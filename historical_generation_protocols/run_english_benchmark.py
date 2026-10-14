# -*- coding: utf-8 -*-
"""
run_english_benchmark.py
-------------------------
Run the three core methods (M1 / M2a / M2b) on the 50 English queries and
compute ICP / ECP / Orphan metrics.  Results are written to:
  data/english_benchmark/
    results_method1/   (EN01_method1_exp_*.md  *.json)
    results_method2a/
    results_method2b/
    english_benchmark_metrics.csv
    english_benchmark_summary.json

Usage:
  python scripts/run_english_benchmark.py --methods method1 method2a method2b
  python scripts/run_english_benchmark.py --dry-run
  python scripts/run_english_benchmark.py --eval-only   (skip pipeline, recompute metrics)
"""

from __future__ import annotations
import argparse, io, json, os, re, sys, time, unicodedata
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── Encoding fix ──────────────────────────────────────────────────────────────
if "PYTEST_CURRENT_TEST" not in os.environ:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "buffer"):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

BENCHMARK_FILE  = PROJECT_ROOT / "data" / "benchmarks" / "english_queries_benchmark.json"
CORPUS_FILE     = PROJECT_ROOT / "data" / "frozen_corpus_multidomain_v1.json"
OUT_BASE        = PROJECT_ROOT / "data" / "english_benchmark"
METRICS_CSV     = OUT_BASE / "english_benchmark_metrics.csv"
SUMMARY_JSON    = OUT_BASE / "english_benchmark_summary.json"

METHOD_CONFIGS = {
    "method1": {
        "tag": "method1_exp",
        "mode": "pipeline",
        "writer_provider":   "deepseek",
        "writer_model":      "deepseek-chat",
        "reviewer_provider": None,
        "reviewer_model":    None,
        "reviser_provider":  None,
        "reviser_model":     None,
    },
    "method2a": {
        "tag": "method2a_exp",
        "mode": "arl",
        "writer_provider":   "deepseek",
        "writer_model":      "deepseek-chat",
        "reviewer_provider": "kimi",
        "reviewer_model":    "moonshot-v1-32k",
        "reviser_provider":  "deepseek",
        "reviser_model":     "deepseek-chat",
    },
    "method2b": {
        "tag": "method2b_exp",
        "mode": "arl",
        "writer_provider":   "deepseek",
        "writer_model":      "deepseek-chat",
        "reviewer_provider": "deepseek",
        "reviewer_model":    "deepseek-chat",
        "reviser_provider":  "deepseek",
        "reviser_model":     "deepseek-chat",
    },
}

# ── Metric helpers (adapted from evaluate_metrics.py) ────────────────────────
_BIB_HDR_RE       = re.compile(r"^\s*#{1,3}\s*(参考文献|References)\s*$", re.I | re.M)
_BRACKET_BLOCK_RE = re.compile(r"\[([0-9,\-\s]+)\]")
_BIB_ENTRY_RE     = re.compile(r"^\s*\[(\d+)\]\s+(.*)", re.M)


def _normalize_title(text: str) -> str:
    text = unicodedata.normalize("NFKC", (text or "").lower()).strip()
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"doi[:\s]*\S+", " ", text)
    text = re.sub(r"[^\w\u4e00-\u9fff]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _title_overlap(a: str, b: str, threshold: float = 0.72) -> bool:
    na, nb = _normalize_title(a), _normalize_title(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    toks_a = set(na.split())
    toks_b = set(nb.split())
    if len(toks_a) >= 4 and len(toks_b) >= 4:
        jaccard = len(toks_a & toks_b) / len(toks_a | toks_b)
        if jaccard >= threshold:
            return True
    ratio = SequenceMatcher(None, na, nb).ratio()
    return ratio >= threshold


def _parse_intext_indices(md_body: str) -> set[int]:
    """Return all integer citation indices found in the non-bibliography body."""
    bib_match = _BIB_HDR_RE.search(md_body)
    body = md_body[:bib_match.start()] if bib_match else md_body
    indices: set[int] = set()
    for block in _BRACKET_BLOCK_RE.finditer(body):
        raw = block.group(1)
        for part in re.split(r"[,\s]+", raw):
            part = part.strip()
            if re.match(r"^\d+$", part):
                indices.add(int(part))
            elif "-" in part or "\u2013" in part:
                sep = "-" if "-" in part else "\u2013"
                lo, _, hi = part.partition(sep)
                try:
                    for i in range(int(lo.strip()), int(hi.strip()) + 1):
                        indices.add(i)
                except ValueError:
                    pass
    return indices


def _parse_bib_entries(md: str) -> Dict[int, str]:
    """Return {idx: title_text} for all reference-list entries."""
    bib_match = _BIB_HDR_RE.search(md)
    if not bib_match:
        return {}
    bib_section = md[bib_match.start():]
    return {int(m.group(1)): m.group(2) for m in _BIB_ENTRY_RE.finditer(bib_section)}


def compute_metrics(md_text: str, corpus: List[Dict[str, Any]],
                    top_papers: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Returns ICP, ECP, Orphan.
    corpus_titles: titles/abstracts available for ECP matching.
    """
    intext = _parse_intext_indices(md_text)
    bib    = _parse_bib_entries(md_text)

    if not intext:
        return {"icp": 0.0, "ecp": 0.0, "orphan": 0.0, "n_intext": 0, "n_bib": 0}

    # ICP: fraction of in-text indices that have a bib entry
    matched_in_bib = {i for i in intext if i in bib}
    icp = len(matched_in_bib) / len(intext)

    # ECP: fraction of in-text indices where bib entry matches a corpus paper
    corpus_titles = [p.get("title", "") for p in corpus if p.get("title")]
    ecp_matches = 0
    for i in matched_in_bib:
        bib_title = bib[i]
        for ct in corpus_titles:
            if _title_overlap(bib_title, ct):
                ecp_matches += 1
                break
    ecp = ecp_matches / len(intext)

    orphan = 1.0 - icp

    return {
        "icp":      round(icp   * 100, 1),
        "ecp":      round(ecp   * 100, 1),
        "orphan":   round(orphan * 100, 1),
        "n_intext": len(intext),
        "n_bib":    len(bib),
    }


# ── Corpus & pipeline helpers ─────────────────────────────────────────────────
def _tokenize(text: str) -> List[str]:
    text = unicodedata.normalize("NFKC", (text or "").lower())
    text = re.sub(r"[^\w\u4e00-\u9fff]+", " ", text)
    return [t for t in text.split() if len(t) >= 2]


def retrieve_from_corpus(query: str, corpus: List[Dict], domain_id: str,
                         top_k: int = 15) -> List[Dict]:
    q_tokens = set(_tokenize(query))
    scored = []
    for p in corpus:
        title    = p.get("title", "") or ""
        abstract = p.get("abstract", "") or ""
        t_tok = set(_tokenize(title))
        b_tok = set(_tokenize(f"{title} {abstract}"))
        score = len(q_tokens & b_tok) + 2 * len(q_tokens & t_tok)
        score += min((p.get("citations") or 0) / 500, 0.3)
        if p.get("domain_id") == domain_id:
            score += 0.5
        scored.append((score, p))
    scored.sort(key=lambda x: -x[0])
    return [p for _, p in scored[:top_k]]


def run_query_method1(qid, query, domain_id, corpus, cfg, out_dir, dry_run=False) -> Optional[str]:
    from batch_run_method1 import role2_screening, role3_evidence, role4_synthesis, _compact
    from modules.searcher import _load_saved_search_config

    saved = _load_saved_search_config()
    provider = cfg["writer_provider"]
    api_key  = saved.get(f"{provider}_api_key", "") or ""
    model    = cfg["writer_model"]

    candidates = retrieve_from_corpus(query, corpus, domain_id, top_k=15)
    papers_raw = [_compact(p) for p in candidates]

    if dry_run:
        print(f"  [DRY] {qid} | {len(papers_raw)} candidates | provider={provider}")
        return None

    screened  = role2_screening(query, papers_raw, top_k=8,
                                provider=provider, provider_key=api_key, model=model)
    enriched  = role3_evidence(query, screened,
                               provider=provider, provider_key=api_key, model=model)
    report_md = role4_synthesis(query, enriched,
                                provider=provider, provider_key=api_key, model=model)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    tag = cfg["tag"]
    stem = f"{qid}_{tag}_{ts}"
    (out_dir / f"{stem}.md").write_text(report_md, encoding="utf-8")
    meta = {
        "query_id": qid, "query": query, "domain_id": domain_id,
        "provider": provider, "model": model, "n_candidates": len(candidates),
        "top_papers": candidates[:8], "timestamp": ts,
    }
    (out_dir / f"{stem}.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  -> {stem}.md")
    return report_md


def run_query_method2(qid, query, domain_id, corpus, cfg, out_dir,
                      review_rounds=2, dry_run=False) -> Optional[str]:
    from batch_run_method1 import role2_screening, role3_evidence, role4_synthesis, _compact
    from batch_run_method2 import review_draft, revise_draft, _build_evidence_blocks
    from modules.searcher import _load_saved_search_config

    saved = _load_saved_search_config()
    w_key  = saved.get(f"{cfg['writer_provider']}_api_key",   "") or ""
    rv_key = saved.get(f"{cfg['reviewer_provider']}_api_key", "") or ""
    rs_key = saved.get(f"{cfg['reviser_provider']}_api_key",  "") or ""

    candidates = retrieve_from_corpus(query, corpus, domain_id, top_k=15)
    papers_raw = [_compact(p) for p in candidates]

    if dry_run:
        print(f"  [DRY] {qid} | {len(papers_raw)} candidates | "
              f"writer={cfg['writer_provider']} reviewer={cfg['reviewer_provider']}")
        return None

    w_model  = cfg["writer_model"]
    rv_model = cfg["reviewer_model"]
    rs_model = cfg["reviser_model"]

    screened  = role2_screening(query, papers_raw, top_k=8,
                                provider=cfg["writer_provider"],
                                provider_key=w_key, model=w_model)
    enriched  = role3_evidence(query, screened,
                               provider=cfg["writer_provider"],
                               provider_key=w_key, model=w_model)
    report_md = role4_synthesis(query, enriched,
                                provider=cfg["writer_provider"],
                                provider_key=w_key, model=w_model)

    evidence_block, bib_lines = _build_evidence_blocks(enriched)
    current_draft = report_md

    for rnd in range(1, review_rounds + 1):
        try:
            review_json = review_draft(
                query=query,
                draft=current_draft,
                evidence_block=evidence_block,
                review_provider=cfg["reviewer_provider"],
                review_provider_key=rv_key,
                review_model=rv_model,
                reviewer_model=rv_model,
            )
        except Exception as e:
            print(f"    ARL round {rnd}: review parse error ({e}), stopping")
            break
        if review_json.get("accept_without_revision", False):
            print(f"    ARL round {rnd}: accepted without revision")
            break
        revised = revise_draft(
            query=query,
            draft=current_draft,
            evidence_block=evidence_block,
            bib_lines=bib_lines,
            review_json=review_json,
            revise_provider=cfg["reviser_provider"],
            revise_provider_key=rs_key,
            revise_model=rs_model,
            reviser_model=rs_model,
        )
        if revised and revised.strip():
            current_draft = revised
        print(f"    ARL round {rnd} done")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    tag = cfg["tag"]
    stem = f"{qid}_{tag}_{ts}"
    (out_dir / f"{stem}.md").write_text(current_draft, encoding="utf-8")
    meta = {
        "query_id": qid, "query": query, "domain_id": domain_id,
        "writer_provider": cfg["writer_provider"], "writer_model": w_model,
        "reviewer_provider": cfg["reviewer_provider"], "reviewer_model": rv_model,
        "n_candidates": len(candidates), "top_papers": candidates[:8],
        "timestamp": ts,
    }
    (out_dir / f"{stem}.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  -> {stem}.md")
    return current_draft


# ── Collect & evaluate all outputs ───────────────────────────────────────────
def evaluate_outputs(methods: List[str], out_base: Path,
                     corpus: List[Dict]) -> Dict[str, Any]:
    results = {}  # {method: {qid: metrics}}
    for method in methods:
        method_dir = out_base / f"results_{method}"
        tag = METHOD_CONFIGS[method]["tag"]
        results[method] = {}

        # Group by qid, take latest
        by_qid: Dict[str, Path] = {}
        for md_path in method_dir.glob("EN*_*.md"):
            stem = md_path.stem
            parts = stem.split("_")
            qid = parts[0]
            ts  = "_".join(parts[-2:]) if len(parts) >= 3 else ""
            if qid not in by_qid or ts > "_".join(by_qid[qid].stem.split("_")[-2:]):
                by_qid[qid] = md_path

        for qid, md_path in sorted(by_qid.items()):
            md_text = md_path.read_text(encoding="utf-8")
            # Load top_papers from JSON for ECP
            json_path = md_path.with_suffix(".json")
            top_papers = []
            if json_path.exists():
                try:
                    meta = json.loads(json_path.read_text(encoding="utf-8"))
                    top_papers = meta.get("top_papers", [])
                except Exception:
                    pass
            m = compute_metrics(md_text, corpus, top_papers)
            results[method][qid] = m

        n = len(results[method])
        print(f"[eval] {method}: {n} outputs evaluated")
    return results


def summarise(results: Dict[str, Any]) -> Dict[str, Any]:
    summary = {}
    for method, qdata in results.items():
        if not qdata:
            continue
        icps    = [v["icp"]    for v in qdata.values()]
        ecps    = [v["ecp"]    for v in qdata.values()]
        orphans = [v["orphan"] for v in qdata.values()]
        summary[method] = {
            "n": len(qdata),
            "icp_mean":    round(sum(icps)    / len(icps),    1),
            "ecp_mean":    round(sum(ecps)    / len(ecps),    1),
            "orphan_mean": round(sum(orphans) / len(orphans), 1),
        }
    return summary


def write_csv(results: Dict[str, Any], path: Path) -> None:
    rows = ["qid,method,icp,ecp,orphan,n_intext,n_bib"]
    for method, qdata in results.items():
        for qid, m in sorted(qdata.items()):
            rows.append(f"{qid},{method},{m['icp']},{m['ecp']},{m['orphan']},"
                        f"{m['n_intext']},{m['n_bib']}")
    path.write_text("\n".join(rows), encoding="utf-8")
    print(f"[ok] CSV written: {path}")


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--methods",   nargs="+",
                    default=["method1", "method2a", "method2b"],
                    choices=list(METHOD_CONFIGS.keys()))
    ap.add_argument("--dry-run",   action="store_true")
    ap.add_argument("--eval-only", action="store_true",
                    help="Skip pipeline runs; just recompute metrics on existing outputs")
    ap.add_argument("--sleep",     type=float, default=8.0)
    ap.add_argument("--review-rounds", type=int, default=2)
    args = ap.parse_args()

    OUT_BASE.mkdir(parents=True, exist_ok=True)

    queries = json.loads(BENCHMARK_FILE.read_text(encoding="utf-8"))
    corpus  = json.loads(CORPUS_FILE.read_text(encoding="utf-8"))
    print(f"[info] {len(queries)} English queries | corpus {len(corpus)} papers")

    # ── Pipeline runs ─────────────────────────────────────────────────────────
    if not args.eval_only:
        for method in args.methods:
            cfg = METHOD_CONFIGS[method]
            out_dir = OUT_BASE / f"results_{method}"
            out_dir.mkdir(parents=True, exist_ok=True)
            tag = cfg["tag"]

            print(f"\n{'='*55}\nMethod: {method}  ({len(queries)} English queries)\n{'='*55}")

            for row in queries:
                qid   = row["id"]
                query = row["query"]
                dom   = row.get("domain_id", "")

                # Skip if already done
                existing = list(out_dir.glob(f"{qid}_{tag}_*.md"))
                if existing:
                    print(f"[{qid}] already done, skipping")
                    continue

                print(f"\n[{qid}] {query[:65]}...")
                try:
                    if cfg["mode"] == "pipeline":
                        run_query_method1(qid, query, dom, corpus, cfg,
                                          out_dir, dry_run=args.dry_run)
                    else:
                        run_query_method2(qid, query, dom, corpus, cfg,
                                          out_dir, review_rounds=args.review_rounds,
                                          dry_run=args.dry_run)
                    if not args.dry_run:
                        time.sleep(args.sleep)
                except Exception as e:
                    print(f"  [ERROR] {qid}: {e}")
                    err_path = out_dir / "errors.jsonl"
                    with open(err_path, "a", encoding="utf-8") as fp:
                        fp.write(json.dumps({"qid": qid, "error": str(e),
                                             "ts": datetime.now().isoformat()}) + "\n")

    # ── Evaluate ──────────────────────────────────────────────────────────────
    if not args.dry_run:
        print("\n[eval] Computing ICP / ECP / Orphan metrics …")
        results = evaluate_outputs(args.methods, OUT_BASE, corpus)
        summary = summarise(results)

        write_csv(results, METRICS_CSV)
        SUMMARY_JSON.write_text(
            json.dumps({"summary": summary, "detail": results},
                       ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        print("\n" + "="*55)
        print(f"{'Method':<18} {'n':>4} {'ICP':>7} {'ECP':>7} {'Orphan':>8}")
        print("-"*55)
        for method, s in summary.items():
            print(f"{method:<18} {s['n']:>4} {s['icp_mean']:>6.1f}% "
                  f"{s['ecp_mean']:>6.1f}% {s['orphan_mean']:>7.1f}%")
        print("="*55)
        print(f"\n[done] Results in {OUT_BASE}")


if __name__ == "__main__":
    main()
