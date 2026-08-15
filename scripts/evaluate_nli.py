#!/usr/bin/env python3
"""
evaluate_nli.py — Citation Faithfulness Score (CFS) evaluation.

For every markdown output in a directory, samples (claim_sentence, cited_abstract)
pairs and uses an LLM NLI judge to decide if each claim is faithfully supported by
the cited paper's abstract.

  CFS = n_faithful / n_evaluated   (higher is better)

This metric is independent of the candidate-pool circularity issue: it directly
tests whether the CONTENT of cited abstracts supports the CLAIMS written.
It is adapted from the NLI_PROMPT in the original AutoSurvey codebase
(AutoSurveys/AutoSurvey src/prompt.py) so the evaluation methodology is fair to
all systems compared.

Handles bilingual outputs: Chinese claim sentences + English abstracts are both
supported by the judge prompt.

Usage (single directory):
    python scripts/evaluate_nli.py \\
        --dir data/autosurvey_native_outputs \\
        --provider deepseek --model deepseek-chat \\
        --max-pairs 20 \\
        --out-json data/benchmarks/cfs_autosurvey_native.json

Usage (multiple directories at once for paper table):
    python scripts/evaluate_nli.py \\
        --dirs data/autosurvey_native_outputs data/autosurvey_outputs data/expanded_outputs/method2a \\
        --provider deepseek --model deepseek-chat \\
        --max-pairs 20 \\
        --out-json data/benchmarks/cfs_all_systems.json
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules.ai_provider import call_ai  # noqa: E402
from modules.searcher import _load_saved_search_config  # noqa: E402

FROZEN_CORPUS_PATH = (
    PROJECT_ROOT
    / "data"
    / "topic_runs"
    / "multi_agent_intel_service_20260410_114059"
    / "retrieved_papers_wave3.json"
)

# ── regexes ──────────────────────────────────────────────────────────────────
_BIB_HDR_RE = re.compile(r"^\s*#{1,3}\s*(参考文献|References)\s*$", re.I | re.M)
_BIB_ENTRY_RE = re.compile(r"^\s*\[(\d+)\]\s+(.{5,})", re.M)
_CITE_IN_TEXT_RE = re.compile(r"\[(\d+)\]")
_HEADING_RE = re.compile(r"^#{1,4}\s+.+$", re.M)
_INTERMEDIATE_SUFFIXES = (".outline.md", ".raw.md", ".nocheck.md")

# ── NLI judge prompt (bilingual, adapted from AutoSurvey NLI_PROMPT) ─────────
NLI_PROMPT = """\
You are a strict NLI (Natural Language Inference) judge for academic citations.

Claim (may be in Chinese or English):
---
{claim}
---

Source abstract (may be in English or Chinese):
---
{source}
---

Task: Does the Source abstract contain information that directly supports the \
core assertion in the Claim?
- Answer 'Yes' if the core part of the Claim is explicitly stated or clearly \
implied by the Source.
- Answer 'No' if the Source does not support the Claim, or the Claim relies on \
information absent from the Source.

Reply with ONLY the single word 'Yes' or 'No':"""


# ── helper functions (self-contained; no imports from evaluate_metrics) ───────

def _paper_id(paper: Dict[str, Any]) -> str:
    doi = (paper.get("doi") or "").strip().lower()
    if doi:
        return f"doi:{doi}"
    title = " ".join((paper.get("title") or "").lower().split())
    year = str(paper.get("year") or "").strip()
    return f"title:{title}|{year}"


def _normalize_title(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "").lower().strip()
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"doi[:\s]*\S+", " ", text)
    text = re.sub(r"[^\w\u4e00-\u9fff]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _title_tokens(text: str) -> List[str]:
    return [t for t in _normalize_title(text).split() if len(t) >= 2]


def _match_title(
    ref_text: str,
    candidate_titles: List[str],
    threshold: float = 0.72,
) -> Optional[str]:
    ref_norm = _normalize_title(ref_text)
    ref_tokens = set(_title_tokens(ref_text))
    if not ref_norm:
        return None
    best: Optional[Tuple[float, str]] = None
    for cand in candidate_titles:
        cand_norm = _normalize_title(cand)
        if not cand_norm:
            continue
        if cand_norm in ref_norm or ref_norm in cand_norm:
            score = 1.0
        else:
            cand_tokens = set(_title_tokens(cand))
            overlap = len(ref_tokens & cand_tokens)
            token_ratio = overlap / max(1, min(len(ref_tokens), len(cand_tokens)))
            seq_ratio = SequenceMatcher(None, ref_norm, cand_norm).ratio()
            score = max(seq_ratio, token_ratio)
        if score >= threshold and (best is None or score > best[0]):
            best = (score, cand)
    return best[1] if best else None


def _load_frozen_corpus(path: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    target = path if path is not None else FROZEN_CORPUS_PATH
    corpus = json.loads(target.read_text(encoding="utf-8"))
    by_id: Dict[str, Dict[str, Any]] = {}
    for row in corpus:
        by_id[_paper_id(row)] = row
    return by_id


# ── document parsing ──────────────────────────────────────────────────────────

def _split_body_bib(content: str) -> Tuple[str, str]:
    parts = _BIB_HDR_RE.split(content, maxsplit=1)
    if len(parts) >= 3:
        return parts[0], parts[-1]
    return content, ""


def _parse_bib(bib_text: str) -> Dict[int, str]:
    """Parse bibliography section → {citation_num: title_or_first_line}."""
    entries: Dict[int, str] = {}
    for m in _BIB_ENTRY_RE.finditer(bib_text):
        num = int(m.group(1))
        raw = m.group(2).strip()
        # strip trailing DOI / URL so we only keep the title
        raw = re.sub(r"\s+DOI:.*$", "", raw, flags=re.I).strip()
        raw = re.sub(r"\s+https?://\S+.*$", "", raw).strip()
        # strip trailing venue/year "(Journal, 2020.)" style
        raw = re.sub(r"\.\s+[\w\s,]+\.\s*\d{4}\.?$", ".", raw).strip()
        entries[num] = raw
    return entries


def _sentences_from_text(text: str) -> List[str]:
    """Split text into sentences (Chinese 。！？ and Latin . ! ? endings)."""
    parts = re.split(r"(?<=[。！？.!?])\s*", text)
    return [p.strip() for p in parts if p.strip() and len(p.strip()) > 20]


def _extract_claim_pairs(body: str, bib: Dict[int, str]) -> List[Tuple[str, int]]:
    """
    Return (claim_sentence, citation_num) pairs.
    One entry per (sentence, citation_number) combination; deduped.
    """
    pairs: List[Tuple[str, int]] = []
    seen: set[Tuple[str, int]] = set()

    # remove headings so they don't confuse sentence splitting
    clean_body = _HEADING_RE.sub("", body)
    paragraphs = re.split(r"\n{2,}", clean_body)

    for para in paragraphs:
        sentences = _sentences_from_text(para)
        for sent in sentences:
            nums = [int(m.group(1)) for m in _CITE_IN_TEXT_RE.finditer(sent)]
            for num in nums:
                if num not in bib:
                    continue
                key = (sent[:70], num)
                if key in seen:
                    continue
                seen.add(key)
                pairs.append((sent, num))
    return pairs


def _get_abstract(
    title_text: str,
    frozen_by_id: Dict[str, Dict[str, Any]],
    all_titles: List[str],
    threshold: float = 0.72,
) -> Optional[str]:
    matched = _match_title(title_text, all_titles, threshold=threshold)
    if not matched:
        return None
    for row in frozen_by_id.values():
        if row.get("title", "") == matched:
            abstract = (row.get("abstract", "") or "").strip()
            # require a reasonably informative abstract
            return abstract if len(abstract) >= 80 else None
    return None


# ── NLI LLM call ─────────────────────────────────────────────────────────────

def _call_nli(
    claim: str,
    abstract: str,
    provider: str,
    api_key: str,
    model: str,
) -> str:
    prompt = NLI_PROMPT.format(
        claim=claim.strip()[:500],
        source=abstract.strip()[:800],
    )
    for attempt in range(3):
        try:
            raw = call_ai(
                prompt=prompt,
                system="You are a strict NLI judge. Reply only with 'Yes' or 'No'.",
                provider=provider,
                api_key=api_key,
                model=model,
                task_type="analysis",
                max_tokens=8,
                temperature=0.0,
                timeout=30,
            ).strip().lower()
            if raw.startswith("yes"):
                return "yes"
            if raw.startswith("no"):
                return "no"
            return "no"  # treat ambiguous response as unfaithful
        except Exception as exc:
            if attempt == 2:
                return "error"
            time.sleep([5, 15][attempt])
    return "error"


# ── per-file evaluation ───────────────────────────────────────────────────────

def evaluate_nli_file(
    md_path: Path,
    frozen_by_id: Dict[str, Dict[str, Any]],
    all_titles: List[str],
    provider: str,
    api_key: str,
    model: str,
    max_pairs: int = 20,
    seed: int = 42,
) -> Dict[str, Any]:
    content = md_path.read_text(encoding="utf-8")
    body, bib_text = _split_body_bib(content)
    bib = _parse_bib(bib_text)

    if not bib:
        return {
            "file": md_path.name,
            "error": "no_bibliography",
            "cfs": None,
            "cfs_pct": None,
            "n_evaluated": 0,
        }

    all_pairs = _extract_claim_pairs(body, bib)
    if not all_pairs:
        return {
            "file": md_path.name,
            "error": "no_claim_pairs_extracted",
            "cfs": None,
            "cfs_pct": None,
            "n_evaluated": 0,
        }

    rng = random.Random(seed)
    sampled = rng.sample(all_pairs, min(max_pairs, len(all_pairs)))

    records: List[Dict[str, Any]] = []
    for claim, num in sampled:
        title_text = bib[num]
        abstract = _get_abstract(title_text, frozen_by_id, all_titles)
        if not abstract:
            records.append({
                "citation_num": num,
                "claim": claim[:200],
                "bib_title": title_text[:120],
                "abstract_found": False,
                "verdict": "skipped",
            })
            continue
        verdict = _call_nli(claim, abstract, provider, api_key, model)
        records.append({
            "citation_num": num,
            "claim": claim[:200],
            "bib_title": title_text[:120],
            "abstract_found": True,
            "verdict": verdict,
        })
        time.sleep(0.4)  # gentle rate-limiting

    evaluated = [r for r in records if r["verdict"] not in ("skipped", "error")]
    n_yes = sum(1 for r in evaluated if r["verdict"] == "yes")
    n_total = len(evaluated)
    cfs = round(n_yes / n_total, 4) if n_total > 0 else None

    return {
        "file": md_path.name,
        "cfs": cfs,
        "cfs_pct": round(cfs * 100, 1) if cfs is not None else None,
        "n_evaluated": n_total,
        "n_faithful": n_yes,
        "n_skipped": len(records) - n_total,
        "records": records,
    }


# ── directory-level helpers ───────────────────────────────────────────────────

def _collect_md_files(directory: Path) -> List[Path]:
    files = [
        f for f in sorted(directory.glob("*.md"))
        if not any(f.name.lower().endswith(s) for s in _INTERMEDIATE_SUFFIXES)
    ]
    return files


def _print_summary(tag: str, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    valid = [r for r in rows if r.get("cfs") is not None]
    if not valid:
        print(f"\n=== {tag.upper()} | no valid results ===")
        return {"config": tag, "n": 0, "mean_cfs_pct": None}
    mean_cfs = sum(r["cfs"] for r in valid) / len(valid)
    print(f"\n=== {tag.upper()} | n={len(valid)} ===")
    print(f"  Citation Faithfulness Score (CFS): {mean_cfs * 100:.1f}%")
    print(f"  Total pairs evaluated              : {sum(r['n_evaluated'] for r in valid)}")
    print(f"  Faithful pairs                     : {sum(r['n_faithful'] for r in valid)}")
    return {
        "config": tag,
        "n": len(valid),
        "mean_cfs_pct": round(mean_cfs * 100, 1),
        "total_pairs_evaluated": sum(r["n_evaluated"] for r in valid),
        "total_faithful": sum(r["n_faithful"] for r in valid),
        "files": rows,
    }


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Citation Faithfulness Score (NLI-based) evaluation for survey outputs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    # accept either --dir (single) or --dirs (multiple)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dir", default=None, help="Single directory containing markdown outputs.")
    group.add_argument(
        "--dirs",
        nargs="+",
        default=None,
        help="Multiple directories (one per system) to evaluate together.",
    )
    parser.add_argument("--provider", default="deepseek", help="AI provider.")
    parser.add_argument("--model", default="deepseek-chat", help="Model name.")
    parser.add_argument(
        "--max-pairs",
        type=int,
        default=20,
        help="Max (claim, citation) pairs to evaluate per file (default: 20).",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for sampling.")
    parser.add_argument("--out-json", default=None, help="Save aggregate results to this JSON path.")
    parser.add_argument(
        "--frozen-corpus",
        default=None,
        help=(
            "Path to frozen corpus JSON (list of paper dicts). "
            f"Defaults to the AutoSurvey wave3 corpus at {FROZEN_CORPUS_PATH}. "
            "Use data/frozen_corpus_multidomain_v1.json for CDMA+ARL method outputs."
        ),
    )
    args = parser.parse_args()

    # Build directory list
    if args.dir:
        dirs = [Path(args.dir)]
    else:
        dirs = [Path(d) for d in args.dirs]

    for d in dirs:
        if not d.exists():
            raise SystemExit(f"Directory not found: {d}")

    # Load API key
    cfg = _load_saved_search_config()
    api_key = cfg.get(f"{args.provider}_api_key", "") or ""
    if not api_key:
        raise SystemExit(f"{args.provider}_api_key not configured in saved search config.")

    # Load corpus
    corpus_path = Path(args.frozen_corpus) if args.frozen_corpus else FROZEN_CORPUS_PATH
    if not corpus_path.exists():
        raise SystemExit(f"Frozen corpus not found: {corpus_path}")
    print(f"Loading frozen corpus from {corpus_path.name}...")
    frozen_by_id = _load_frozen_corpus(corpus_path)
    all_titles = [row.get("title", "") for row in frozen_by_id.values()]
    print(f"  {len(frozen_by_id)} papers loaded.\n{'-' * 60}")

    all_summaries: List[Dict[str, Any]] = []

    for directory in dirs:
        tag = directory.name
        md_files = _collect_md_files(directory)
        print(f"\n[{tag}] Found {len(md_files)} output files.")

        dir_results: List[Dict[str, Any]] = []
        for md_path in md_files:
            print(f"  Evaluating {md_path.name} ...", flush=True)
            result = evaluate_nli_file(
                md_path,
                frozen_by_id,
                all_titles,
                provider=args.provider,
                api_key=api_key,
                model=args.model,
                max_pairs=args.max_pairs,
                seed=args.seed,
            )
            dir_results.append(result)
            if result.get("error"):
                print(f"    SKIP ({result['error']})")
            else:
                print(
                    f"    CFS={result['cfs_pct']}%  "
                    f"({result['n_faithful']}/{result['n_evaluated']} faithful, "
                    f"{result['n_skipped']} skipped)"
                )

        summary = _print_summary(tag, dir_results)
        all_summaries.append(summary)

    if args.out_json:
        out_path = Path(args.out_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(all_summaries, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nSaved results to {out_path}")


if __name__ == "__main__":
    main()
