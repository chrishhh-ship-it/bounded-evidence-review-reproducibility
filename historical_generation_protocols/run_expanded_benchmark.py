"""
run_expanded_benchmark.py
--------------------------
One-stop launcher for the expanded multi-domain benchmark.

Corpus : data/frozen_corpus_multidomain_v1.json  (3011 papers, 4 domains)
Queries: data/benchmarks/benchmark_all_queries.json  (251 queries, 4 domains)
         -- or pass --benchmark to use a different file

Supported methods:
  method1   : Pipeline multi-agent  (no ARL)
  method2a  : Cross-model ARL       (writer=deepseek, reviewer=kimi)
  method2b  : Same-model ARL        (all deepseek)
  method2c  : Reverse-model ARL     (writer=kimi, reviewer=deepseek)  [new]
  method2d  : GPT-4o-mini ARL       (writer=openai, reviewer=openai)  [new]

Usage examples:
  # Run Method 1, all 251 queries
  python scripts/run_expanded_benchmark.py --method method1

  # Run Method 2a, queries Q031-Q060 only
  python scripts/run_expanded_benchmark.py --method method2a --start 31 --end 60

  # Run Method 2d (GPT-4o-mini) for a single query
  python scripts/run_expanded_benchmark.py --method method2d --query-id Q045

  # Custom benchmark subset
  python scripts/run_expanded_benchmark.py --method method1 \\
      --benchmark data/benchmarks/multi_domain_benchmark_queries_v1.json

  # Dry run (print what would run, don't call APIs)
  python scripts/run_expanded_benchmark.py --method method1 --dry-run
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Fix encoding for Windows GBK console / log-file redirection.
# Skip this during pytest imports because replacing the capture streams
# can break test teardown.
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

# ── Paths ────────────────────────────────────────────────────────────────────
DEFAULT_CORPUS   = PROJECT_ROOT / "data" / "frozen_corpus_multidomain_v1.json"
DEFAULT_BENCHMARK = PROJECT_ROOT / "data" / "benchmarks" / "benchmark_all_queries.json"
OUTPUT_BASE      = PROJECT_ROOT / "data" / "expanded_outputs"

# ── Method configs ────────────────────────────────────────────────────────────
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
    "method2c": {
        "tag": "method2c_exp",
        "mode": "arl",
        "writer_provider":   "kimi",
        "writer_model":      "moonshot-v1-32k",
        "reviewer_provider": "deepseek",
        "reviewer_model":    "deepseek-chat",
        "reviser_provider":  "kimi",
        "reviser_model":     "moonshot-v1-32k",
    },
    "method2d": {
        "tag": "method2d_exp",
        "mode": "arl",
        "writer_provider":   "openai",
        "writer_model":      "gpt-4o-mini",
        "reviewer_provider": "openai",
        "reviewer_model":    "gpt-4o-mini",
        "reviser_provider":  "openai",
        "reviser_model":     "gpt-4o-mini",
    },
}

# ── Corpus loader ─────────────────────────────────────────────────────────────
def load_corpus(corpus_path: Path) -> List[Dict[str, Any]]:
    papers = json.loads(corpus_path.read_text(encoding="utf-8"))
    print(f"[Corpus] {len(papers)} papers loaded from {corpus_path.name}")
    with_abstract = sum(1 for p in papers if p.get("abstract", "").strip())
    from collections import Counter
    by_domain = Counter(p.get("domain_id", "unknown") for p in papers)
    print(f"[Corpus] {with_abstract} with abstracts | domains: {dict(by_domain)}")
    return papers


def _extract_completed_query_ids(output_dir: Path, tag: str) -> set[str]:
    done: set[str] = set()
    pattern = re.compile(rf"^(Q\d+|MD\d+)_{re.escape(tag)}_")
    for path in output_dir.glob("*.json"):
        match = pattern.match(path.name)
        if match:
            done.add(match.group(1))
    return done


# ── Retrieve papers for a query from the multi-domain frozen corpus ───────────
def _tokenize(text: str) -> List[str]:
    import re, unicodedata
    text = unicodedata.normalize("NFKC", (text or "").lower())
    text = re.sub(r"[^\w\u4e00-\u9fff]+", " ", text)
    return [t for t in text.split() if len(t) >= 2]


def _rank_paper(query_tokens: List[str], paper: Dict[str, Any]) -> float:
    title   = paper.get("title", "") or ""
    abstract = paper.get("abstract", "") or ""
    text_tokens = set(_tokenize(f"{title} {abstract}"))
    title_tokens = set(_tokenize(title))
    q_set = set(query_tokens)
    overlap_body  = len(q_set & text_tokens)
    overlap_title = len(q_set & title_tokens)
    cite_bonus = min((paper.get("citations") or 0) / 500, 0.3)
    domain_bonus = 0.2 if paper.get("domain_id") else 0.0
    return overlap_body + 2 * overlap_title + cite_bonus + domain_bonus


def retrieve_from_corpus(
    query: str,
    corpus: List[Dict[str, Any]],
    domain_id: Optional[str] = None,
    top_k: int = 15,
) -> List[Dict[str, Any]]:
    """Retrieve top_k papers from frozen multi-domain corpus.

    If domain_id is provided, first tries within-domain, then falls back to global.
    """
    q_tokens = _tokenize(query)

    # Domain-prioritized retrieval: score domain papers with a boost
    scored = []
    for p in corpus:
        score = _rank_paper(q_tokens, p)
        if domain_id and p.get("domain_id") == domain_id:
            score += 0.5  # domain relevance boost
        scored.append((score, p))

    scored.sort(key=lambda x: -x[0])
    return [p for _, p in scored[:top_k]]


# ── Adapted pipeline roles using multi-domain corpus ─────────────────────────
def run_method1_expanded(
    query: str,
    qid: str,
    query_meta: Dict[str, Any],
    corpus: List[Dict[str, Any]],
    provider: str,
    model: str,
    output_dir: Path,
    tag: str,
    dry_run: bool = False,
) -> None:
    from batch_run_method1 import (
        role2_screening,
        role3_evidence,
        role4_synthesis,
        _compact,
    )
    from modules.searcher import _load_saved_search_config

    cfg = _load_saved_search_config()
    provider_key = cfg.get(f"{provider}_api_key", "") or ""
    domain_id = query_meta.get("domain_id")

    # Role 1: retrieve from frozen multi-domain corpus
    candidates = retrieve_from_corpus(query, corpus, domain_id=domain_id, top_k=15)
    papers_raw = [_compact(p) for p in candidates]

    if dry_run:
        print(f"  [DRY] {qid} | {len(papers_raw)} candidates from domain={domain_id}")
        return

    model_arg = model or None

    # Roles 2-4 same as original
    screened   = role2_screening(query, papers_raw, top_k=8,
                                  provider=provider, provider_key=provider_key, model=model_arg)
    enriched   = role3_evidence(query, screened,
                                provider=provider, provider_key=provider_key, model=model_arg)
    report_md  = role4_synthesis(query, enriched,
                                 provider=provider, provider_key=provider_key, model=model_arg)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"{qid}_{tag}_{ts}"
    md_path   = output_dir / f"{stem}.md"
    json_path = output_dir / f"{stem}.json"

    md_path.write_text(report_md, encoding="utf-8")
    json_path.write_text(json.dumps({
        "query_id": qid, "query": query,
        "domain_id": domain_id,
        "provider": provider, "model": model,
        "n_candidates": len(candidates),
        "top_papers": candidates[:8],
        "timestamp": ts,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  -> {md_path.name}")


def run_method2_expanded(
    query: str,
    qid: str,
    query_meta: Dict[str, Any],
    corpus: List[Dict[str, Any]],
    cfg_method: Dict[str, Any],
    output_dir: Path,
    tag: str,
    review_rounds: int = 2,
    dry_run: bool = False,
) -> None:
    from batch_run_method1 import (
        role2_screening,
        role3_evidence,
        role4_synthesis,
        _compact,
    )
    from batch_run_method2 import review_draft, revise_draft, _build_evidence_blocks
    from modules.searcher import _load_saved_search_config

    cfg = _load_saved_search_config()
    domain_id = query_meta.get("domain_id")

    writer_key   = cfg.get(f"{cfg_method['writer_provider']}_api_key", "") or ""
    reviewer_key = cfg.get(f"{cfg_method['reviewer_provider']}_api_key", "") or ""
    reviser_key  = cfg.get(f"{cfg_method['reviser_provider']}_api_key", "") or ""

    candidates = retrieve_from_corpus(query, corpus, domain_id=domain_id, top_k=15)
    papers_raw = [_compact(p) for p in candidates]

    if dry_run:
        print(f"  [DRY] {qid} | {len(papers_raw)} candidates | "
              f"writer={cfg_method['writer_provider']} "
              f"reviewer={cfg_method['reviewer_provider']}")
        return

    w_model = cfg_method["writer_model"] or None
    rv_model = cfg_method["reviewer_model"] or None
    rs_model = cfg_method["reviser_model"] or None

    screened  = role2_screening(query, papers_raw, top_k=8,
                                provider=cfg_method["writer_provider"],
                                provider_key=writer_key, model=w_model)
    enriched  = role3_evidence(query, screened,
                               provider=cfg_method["writer_provider"],
                               provider_key=writer_key, model=w_model)
    report_md = role4_synthesis(query, enriched,
                                provider=cfg_method["writer_provider"],
                                provider_key=writer_key, model=w_model)

    evidence_block, bib_lines = _build_evidence_blocks(enriched)

    # ARL loop
    for rnd in range(review_rounds):
        try:
            review_json = review_draft(
                query=query,
                draft=report_md,
                evidence_block=evidence_block,
                review_provider=cfg_method["reviewer_provider"],
                review_provider_key=reviewer_key,
                review_model=rv_model,
                reviewer_model=rv_model,
            )
        except Exception as e:
            print(f"  [ARL] Round {rnd+1}: review parse error ({e}), stopping loop")
            break
        if review_json.get("accept_without_revision", False):
            print(f"  [ARL] Round {rnd+1}: accepted")
            break
        report_md = revise_draft(
            query=query,
            draft=report_md,
            evidence_block=evidence_block,
            bib_lines=bib_lines,
            review_json=review_json,
            revise_provider=cfg_method["reviser_provider"],
            revise_provider_key=reviser_key,
            revise_model=rs_model,
            reviser_model=rs_model,
        )
        print(f"  [ARL] Round {rnd+1}: revised")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"{qid}_{tag}_{ts}"
    md_path   = output_dir / f"{stem}.md"
    json_path = output_dir / f"{stem}.json"

    md_path.write_text(report_md, encoding="utf-8")
    json_path.write_text(json.dumps({
        "query_id": qid, "query": query,
        "domain_id": domain_id,
        "writer_provider":   cfg_method["writer_provider"],
        "writer_model":      cfg_method["writer_model"],
        "reviewer_provider": cfg_method["reviewer_provider"],
        "reviewer_model":    cfg_method["reviewer_model"],
        "reviser_provider":  cfg_method["reviser_provider"],
        "reviser_model":     cfg_method["reviser_model"],
        "n_candidates": len(candidates),
        "top_papers": candidates[:8],
        "timestamp": ts,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  -> {md_path.name}")


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser(description="Expanded multi-domain benchmark runner.")
    ap.add_argument("--method",    required=True,
                    choices=list(METHOD_CONFIGS.keys()),
                    help="Which method to run")
    ap.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK),
                    help="Path to benchmark JSON (default: benchmark_all_queries.json, 251 queries)")
    ap.add_argument("--corpus",    default=str(DEFAULT_CORPUS),
                    help="Path to frozen corpus JSON (default: frozen_corpus_multidomain_v1.json)")
    ap.add_argument("--output-dir", default=None,
                    help="Override output directory")
    ap.add_argument("--start",  type=int, default=1,
                    help="Start query index (inclusive)")
    ap.add_argument("--end",    type=int, default=9999,
                    help="End query index (inclusive)")
    ap.add_argument("--domain", default=None,
                    help="Filter to a single domain_id, e.g. digital_humanities")
    ap.add_argument("--query-id", default=None,
                    help="Run a single query by ID, e.g. Q045 or MD023")
    ap.add_argument("--missing-only", action="store_true",
                    help="Run only queries that do not yet have saved outputs in the target directory")
    ap.add_argument("--sleep",  type=float, default=8.0,
                    help="Seconds to sleep between queries (default 8)")
    ap.add_argument("--review-rounds", type=int, default=2,
                    help="ARL review rounds for method2* (default 2)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print what would run without calling any APIs")
    args = ap.parse_args()

    cfg_method = METHOD_CONFIGS[args.method]
    tag = cfg_method["tag"]

    output_dir = Path(args.output_dir) if args.output_dir else (OUTPUT_BASE / args.method)
    output_dir.mkdir(parents=True, exist_ok=True)
    err_path = output_dir / "errors.jsonl"

    corpus    = load_corpus(Path(args.corpus))
    queries   = json.loads(Path(args.benchmark).read_text(encoding="utf-8"))

    # Filter queries
    if args.domain:
        queries = [q for q in queries if q.get("domain_id") == args.domain]
    if args.query_id:
        queries = [q for q in queries if q["id"] == args.query_id]
    if args.missing_only and not args.query_id:
        completed = _extract_completed_query_ids(output_dir, tag)
        queries = [q for q in queries if q["id"] not in completed]

    print(f"\n{'='*60}")
    print(f"Method      : {args.method}  (tag={tag})")
    print(f"Benchmark   : {Path(args.benchmark).name}  ({len(queries)} queries to run)")
    print(f"Corpus      : {Path(args.corpus).name}  ({len(corpus)} papers)")
    print(f"Output dir  : {output_dir}")
    if cfg_method["mode"] == "arl":
        print(f"Writer      : {cfg_method['writer_provider']} / {cfg_method['writer_model']}")
        print(f"Reviewer    : {cfg_method['reviewer_provider']} / {cfg_method['reviewer_model']}")
        print(f"Reviser     : {cfg_method['reviser_provider']} / {cfg_method['reviser_model']}")
    else:
        print(f"Provider    : {cfg_method['writer_provider']} / {cfg_method['writer_model']}")
    print(f"Range       : {args.start}–{args.end}  |  sleep={args.sleep}s")
    if args.dry_run:
        print("*** DRY RUN — no API calls will be made ***")
    print(f"{'='*60}\n")

    success = failed = skipped = 0

    for row in queries:
        qid = row["id"]
        # extract numeric part for range filtering
        num_str = "".join(c for c in qid if c.isdigit())
        idx = int(num_str) if num_str else 0

        if not args.query_id and not (args.start <= idx <= args.end):
            continue

        # Skip if already done
        existing = list(output_dir.glob(f"{qid}_{tag}_*.md"))
        if existing:
            print(f"[{qid}] Already exists, skipping.")
            skipped += 1
            continue

        query_text = row["query"]
        domain_id  = row.get("domain_id", "")
        print(f"\n[{qid}] ({domain_id}) {query_text[:70]}...")

        try:
            if cfg_method["mode"] == "pipeline":
                run_method1_expanded(
                    query=query_text, qid=qid, query_meta=row,
                    corpus=corpus,
                    provider=cfg_method["writer_provider"],
                    model=cfg_method["writer_model"],
                    output_dir=output_dir, tag=tag,
                    dry_run=args.dry_run,
                )
            else:
                run_method2_expanded(
                    query=query_text, qid=qid, query_meta=row,
                    corpus=corpus, cfg_method=cfg_method,
                    output_dir=output_dir, tag=tag,
                    review_rounds=args.review_rounds,
                    dry_run=args.dry_run,
                )
            success += 1
        except Exception as exc:
            import traceback
            print(f"  ERROR: {exc}")
            traceback.print_exc()
            with open(err_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps({
                    "method": args.method, "query_id": qid,
                    "query": query_text, "error": str(exc),
                    "timestamp": datetime.now().isoformat(),
                }, ensure_ascii=False) + "\n")
            failed += 1

        if not args.dry_run:
            print(f"  Sleeping {args.sleep}s...")
            time.sleep(args.sleep)

    print(f"\n{'='*60}")
    print(f"Done.  Success: {success}  Failed: {failed}  Skipped: {skipped}")
    if not args.dry_run:
        print(f"\nNext step — score results:")
        print(f"  python scripts/evaluate_metrics.py --dir {output_dir}")
        print(f"  python scripts/compute_cee.py --dir {output_dir} --tag {tag}")


if __name__ == "__main__":
    main()
