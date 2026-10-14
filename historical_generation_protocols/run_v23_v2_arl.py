"""v2.3 V2: role-separated ARL (Reviewer -> Reviser), starting from the SAME
B1 draft as V1. Same model, same temperature=0.0, same token budget as V1
(protocol-frozen fairness requirement). Reviewer checks evidence availability
explicitly before judging support (see protocol freeze doc); Reviser only
applies directives, never introduces new claims or citations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

B1_DIR = PROJECT_ROOT / "data" / "expanded_outputs" / "semantic_v23_b1"
OUTPUT_DIR = PROJECT_ROOT / "data" / "expanded_outputs" / "semantic_v23_v2_arl"
PRINT_LOCK = threading.Lock()

TEMPERATURE = 0.0
REVIEW_MAX_TOKENS = 24000
REVISE_MAX_TOKENS = 24000


def _reviewer_prompt(draft: str, papers: list[dict[str, Any]]) -> str:
    evidence_blocks = []
    for i, p in enumerate(papers, start=1):
        abstract = (p.get("abstract") or "").strip()
        ev_text = f"Abstract: {abstract}" if abstract else "Abstract: [NO ABSTRACT AVAILABLE]"
        evidence_blocks.append(f"[{i}] {p.get('title','')} ({p.get('year','')})\n{ev_text}")
    return (
        "You are a semantic citation auditor. You did not write the draft "
        "below and must not rewrite it. Find every sentence carrying a [N] "
        "citation and classify it using exactly one of five labels:\n\n"
        "EVIDENCE_UNAVAILABLE -- the cited record's abstract is marked "
        "'[NO ABSTRACT AVAILABLE]'. Use this whenever true, regardless of how "
        "plausible the claim sounds; never guess in place of missing text.\n"
        "SUPPORTED -- an abstract is available and directly backs the claim.\n"
        "PARTIAL -- an abstract is available and topically related but does "
        "not fully back the specific wording.\n"
        "INSUFFICIENT -- an abstract is available but insufficient to judge.\n"
        "CONTRADICTED -- an abstract is available and conflicts with the claim.\n\n"
        'For each citation-bearing sentence output one JSON object with fields: '
        '"sentence" (verbatim substring from the draft), "cited" (list of '
        'integers), "verdict" (one of the five labels above), "directive" '
        '(one of KEEP, NARROW, REMOVE, HEDGE_UNAVAILABLE), and "reason" (one '
        "short clause).\n"
        "Directive rules: SUPPORTED->KEEP. PARTIAL->NARROW. "
        "INSUFFICIENT->REMOVE. CONTRADICTED->REMOVE. "
        "EVIDENCE_UNAVAILABLE->HEDGE_UNAVAILABLE (never REMOVE and never KEEP "
        "unchanged for this verdict).\n\n"
        "Return only a JSON array of these objects, nothing else.\n\n"
        "Draft:\n" + draft + "\n\n"
        "Evidence records:\n" + "\n\n".join(evidence_blocks)
    )


def _reviser_prompt(draft: str, verdicts: list[dict[str, Any]]) -> str:
    directives = json.dumps(verdicts, ensure_ascii=False, indent=2)
    return (
        "You are a semantic repair agent. Apply the Reviewer's directives "
        "exactly. You may not introduce any new claim, citation, or evidence "
        "beyond what the draft already cites.\n\n"
        "Rules:\n"
        "- REMOVE: delete that exact sentence from the draft.\n"
        "- NARROW: rewrite that exact sentence so its claim is hedged to "
        "match only what the cited evidence supports. Keep the same citation "
        "tag(s).\n"
        "- KEEP: leave the sentence unchanged.\n"
        "- HEDGE_UNAVAILABLE: keep the sentence, but append this exact "
        "parenthetical immediately after it: "
        "（注：本主张所引证据在当前语料中缺失可用的摘要文本，"
        "无法核实该主张，需在后续补齐证据后复核。）\n"
        "- Do not touch sentences not listed in the directives.\n"
        "- Remove a bibliography entry only if every sentence citing it was "
        "removed.\n"
        "- Preserve section structure.\n\n"
        "Reviewer directives (JSON array):\n" + directives + "\n\n"
        "Original draft:\n" + draft + "\n\n"
        "Output only the final revised report, nothing else."
    )


def _parse_json_array(text: str) -> list[dict[str, Any]]:
    text = text.strip()
    m = re.search(r"\[.*\]", text, re.S)
    candidate = m.group(0) if m else text
    try:
        data = json.loads(candidate)
        return data if isinstance(data, list) else []
    except Exception:
        pass
    objs: list[dict[str, Any]] = []
    depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    objs.append(json.loads(text[start:i + 1]))
                except Exception:
                    pass
                start = None
    return objs


def _run_one(qid: str, provider: str, model: str, provider_key: str,
             overwrite: bool) -> dict[str, Any]:
    from modules.ai_provider import call_ai

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    existing = sorted(OUTPUT_DIR.glob(f"{qid}_v23v2_*_final.md"))
    if existing and not overwrite:
        return {"qid": qid, "status": "skipped", "file": str(existing[-1])}

    b1_md = B1_DIR / f"{qid}_semantic_v23_b1.md"
    b1_json = B1_DIR / f"{qid}_semantic_v23_b1.json"
    if not b1_md.exists():
        return {"qid": qid, "status": "failed", "error": "no B1 source"}
    draft = b1_md.read_text(encoding="utf-8")
    meta_b1 = json.loads(b1_json.read_text(encoding="utf-8"))
    papers = meta_b1.get("top_papers") or []

    started = time.time()
    review_prompt = _reviewer_prompt(draft, papers)
    review_response = call_ai(
        prompt=review_prompt,
        system="You are a strict semantic auditor. Output JSON only. Never "
               "guess when the abstract is marked unavailable.",
        provider=provider, api_key=provider_key, model=model or None,
        task_type="analysis", max_tokens=REVIEW_MAX_TOKENS, temperature=TEMPERATURE,
        timeout=180,
    )
    verdicts = _parse_json_array(review_response)
    review_elapsed = time.time() - started

    revise_started = time.time()
    if verdicts:
        revise_prompt = _reviser_prompt(draft, verdicts)
        final_text = call_ai(
            prompt=revise_prompt,
            system="You are a constrained semantic repair agent. Apply directives only.",
            provider=provider, api_key=provider_key, model=model or None,
            task_type="analysis", max_tokens=REVISE_MAX_TOKENS, temperature=TEMPERATURE,
            timeout=180,
        )
    else:
        final_text = draft
    revise_elapsed = time.time() - revise_started

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"{qid}_v23v2_{stamp}"
    review_json_path = OUTPUT_DIR / f"{stem}_review.json"
    final_md_path = OUTPUT_DIR / f"{stem}_final.md"
    final_json_path = OUTPUT_DIR / f"{stem}_final.json"

    review_json_path.write_text(
        json.dumps({"verdicts": verdicts, "raw_response": review_response},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    final_md_path.write_text(final_text, encoding="utf-8")
    meta = {
        "condition": "V2_arl",
        "protocol": "semantic_arl_v2_3",
        "qid": qid,
        "source_b1": str(b1_md.relative_to(PROJECT_ROOT)),
        "provider": provider,
        "model": model,
        "top_papers": papers,
        "n_verdicts": len(verdicts),
        "verdict_counts": {
            v: sum(1 for d in verdicts if d.get("verdict") == v)
            for v in ("SUPPORTED", "PARTIAL", "CONTRADICTED", "INSUFFICIENT", "EVIDENCE_UNAVAILABLE")
        },
        "temperature": TEMPERATURE,
        "review_max_tokens": REVIEW_MAX_TOKENS,
        "revise_max_tokens": REVISE_MAX_TOKENS,
        "reviewer_prompt_sha256": hashlib.sha256(review_prompt.encode("utf-8")).hexdigest(),
        "review_elapsed_seconds": round(review_elapsed, 3),
        "revise_elapsed_seconds": round(revise_elapsed, 3),
        "review_json": str(review_json_path.relative_to(PROJECT_ROOT)),
        "output_markdown": str(final_md_path.relative_to(PROJECT_ROOT)),
    }
    final_json_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"qid": qid, "status": "completed", "file": str(final_md_path),
            "n_verdicts": len(verdicts),
            "elapsed_seconds": round(review_elapsed + revise_elapsed, 3)}


def main() -> None:
    from modules.searcher import _load_saved_search_config

    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="deepseek")
    ap.add_argument("--model", default="deepseek-v4-pro")
    ap.add_argument("--start", type=int, default=31)
    ap.add_argument("--end", type=int, default=60)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    config = _load_saved_search_config()
    provider_key = config.get(f"{args.provider}_api_key", "") or ""
    if not provider_key:
        raise SystemExit(f"Missing API key for provider={args.provider}")

    qids = [f"Q{n:02d}" for n in range(args.start, args.end + 1)]
    results = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
        futs = {ex.submit(_run_one, qid, args.provider, args.model, provider_key,
                           args.overwrite): qid for qid in qids}
        for fut in as_completed(futs):
            qid = futs[fut]
            try:
                r = fut.result()
            except Exception as exc:
                r = {"qid": qid, "status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            results.append(r)
            with PRINT_LOCK:
                print(json.dumps(r, ensure_ascii=False))

    print(json.dumps({"summary": results}, ensure_ascii=False))


if __name__ == "__main__":
    main()
