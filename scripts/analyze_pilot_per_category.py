"""
Reproduce Table 7 (Per-Category Citation Precision and Orphan Rate, n=30,
MAS pilot benchmark) from the released artifacts.

This script reads the pilot query taxonomy from the benchmark JSON, evaluates
the per-query markdown outputs for each configuration using the public
``evaluate_metrics`` functions, and aggregates ICP / Orphan / BMR by query
category. It does not modify ``evaluate_metrics.py`` and only relies on its
documented entry points.

Default invocation:
    python scripts/analyze_pilot_per_category.py

Output:
    Table-7-shaped per-category breakdown to stdout, plus an optional JSON
    summary via ``--out``.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.evaluate_metrics import (  # noqa: E402
    _infer_config_tag,
    _paper_id,
    _parse_result_stem,
    _select_latest_per_query,
    evaluate_file,
)

# Default 513-paper pilot corpus (MAS seed domain) and 30-query taxonomy.
DEFAULT_CORPUS = (
    PROJECT_ROOT
    / "data"
    / "topic_runs"
    / "multi_agent_intel_service_20260410_114059"
    / "retrieved_papers_wave3.json"
)
DEFAULT_QUERIES = (
    PROJECT_ROOT / "data" / "benchmarks" / "multi_agent_intel_service_queries.json"
)

# Map paper labels (Table 7) to the on-disk output directory + tag pair used by
# ``evaluate_metrics``. The cross-model constrained review (M2a) is the
# canonical choice for the second column of Table 7.
CONFIG_DIRS: Dict[str, Tuple[Path, str]] = {
    "method1": (PROJECT_ROOT / "data" / "method1_outputs", "method1"),
    "method2a": (PROJECT_ROOT / "data" / "method2_outputs", "method2"),
}

# Display order matches Table 7 in the paper.
CATEGORY_ORDER: List[str] = [
    "competitive_intelligence",
    "cost_efficiency",
    "evaluation",
    "full_text",
    "retrieval",
    "benchmark",
    "knowledge_service",
    "writing",
    "agent_roles",
]
# Paper uses an abbreviated label for the first row.
CATEGORY_LABELS: Dict[str, str] = {
    "competitive_intelligence": "competitive_intel.",
}


def _load_corpus(path: Path) -> Dict[str, Dict[str, Any]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {_paper_id(row): row for row in rows}


def _load_query_categories(path: Path) -> Dict[str, str]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {row["id"]: row["category"] for row in rows}


def _evaluate_directory_per_query(
    output_dir: Path,
    target_tag: str,
    frozen_by_id: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """Return ``{query_id: row}`` for the matching markdown files in ``output_dir``."""
    md_files = list(output_dir.glob("*.md"))
    selected = _select_latest_per_query(md_files)
    rows_by_query: Dict[str, Dict[str, Any]] = {}
    for stem_key, path in selected.items():
        parsed = _parse_result_stem(path.stem)
        if not parsed:
            continue
        query_id, parsed_tag, _ = parsed
        config_tag = _infer_config_tag(path, parsed_tag)
        if config_tag != target_tag:
            continue
        rows_by_query[query_id] = evaluate_file(
            path, config_tag, frozen_by_id, match_threshold=0.72
        )
    return rows_by_query


def _category_aggregate(
    rows_by_query: Dict[str, Dict[str, Any]],
    query_categories: Dict[str, str],
) -> Dict[str, Dict[str, float]]:
    bucket: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for qid, row in rows_by_query.items():
        cat = query_categories.get(qid)
        if cat is None:
            continue
        bucket[cat].append(row)
    def _agg_metric(rows: List[Dict[str, Any]], key: str) -> float:
        # Mirror the aggregation rule used by ``evaluate_metrics._agg``: drop
        # rows for which the metric is None (i.e. the markdown contained no
        # in-text citation tag at all) before averaging. This keeps the
        # per-category breakdown numerically comparable to the overall
        # aggregate produced by the manifest commands.
        non_none = [float(r[key]) for r in rows if r.get(key) is not None]
        return sum(non_none) / len(non_none) if non_none else 0.0

    out: Dict[str, Dict[str, float]] = {}
    for cat, rows in bucket.items():
        n = len(rows)
        if n == 0:
            continue
        icp = _agg_metric(rows, "citation_precision") * 100
        orphan = _agg_metric(rows, "orphan_rate") * 100
        bmr = _agg_metric(rows, "bibliography_match_rate") * 100
        out[cat] = {
            "n": n,
            "icp_pct": round(icp, 1),
            "orphan_pct": round(orphan, 1),
            "bmr_pct": round(bmr, 1),
        }
    return out


def _print_table(per_config: Dict[str, Dict[str, Dict[str, float]]]) -> None:
    print(
        f"{'category':25s} {'n':>3s} "
        f"{'M1 ICP':>9s} {'M1 Orph':>9s} "
        f"{'M2a ICP':>9s} {'M2a Orph':>9s}"
    )
    print("-" * 70)
    for cat in CATEGORY_ORDER:
        m1 = per_config.get("method1", {}).get(cat)
        m2a = per_config.get("method2a", {}).get(cat)
        n = (m1 or m2a or {}).get("n", 0)
        label = CATEGORY_LABELS.get(cat, cat)
        m1_icp = f"{m1['icp_pct']:>7.1f}%" if m1 else "       -"
        m1_or = f"{m1['orphan_pct']:>7.1f}%" if m1 else "       -"
        m2a_icp = f"{m2a['icp_pct']:>7.1f}%" if m2a else "       -"
        m2a_or = f"{m2a['orphan_pct']:>7.1f}%" if m2a else "       -"
        print(f"{label:25s} {n:>3d}   {m1_icp}   {m1_or}   {m2a_icp}   {m2a_or}")
    print("-" * 70)
    # The overall (cross-category) aggregate is reported by the manifest's
    # `method1_pilot` / `method2a_pilot` commands and is intentionally not
    # recomputed here from category means, since the row count per category
    # differs and a category-mean of category-means is not the same as a
    # per-query mean. See manifest entries `method1_pilot` and
    # `method2a_pilot` for ICP/Orphan over the full n=30 pilot.


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Reproduce paper Table 7 (Per-Category Citation Precision and "
            "Orphan Rate, n=30 pilot, MAS domain). Aggregates per-query "
            "evaluate_metrics outputs by query category from the benchmark "
            "JSON."
        )
    )
    parser.add_argument(
        "--corpus",
        default=str(DEFAULT_CORPUS),
        help="Path to the 513-paper pilot frozen corpus.",
    )
    parser.add_argument(
        "--queries",
        default=str(DEFAULT_QUERIES),
        help="Pilot 30-query benchmark JSON with category labels.",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Optional JSON path for per-category aggregates.",
    )
    args = parser.parse_args()

    corpus_path = Path(args.corpus)
    queries_path = Path(args.queries)
    if not corpus_path.exists():
        raise SystemExit(f"Corpus not found: {corpus_path}")
    if not queries_path.exists():
        raise SystemExit(f"Queries JSON not found: {queries_path}")

    frozen_by_id = _load_corpus(corpus_path)
    print(f"[Corpus] Loaded {len(frozen_by_id)} papers from {corpus_path.name}")
    query_categories = _load_query_categories(queries_path)

    per_config: Dict[str, Dict[str, Dict[str, float]]] = {}
    for cfg, (out_dir, tag) in CONFIG_DIRS.items():
        if not out_dir.exists():
            print(f"[skip] {cfg}: directory missing -> {out_dir}")
            continue
        rows_by_query = _evaluate_directory_per_query(out_dir, tag, frozen_by_id)
        # Restrict to the 30 queries that have category labels (Q01-Q30).
        rows_by_query = {
            qid: r for qid, r in rows_by_query.items() if qid in query_categories
        }
        per_config[cfg] = _category_aggregate(rows_by_query, query_categories)
        print(f"[{cfg}] evaluated {len(rows_by_query)} queries with category labels")

    print()
    _print_table(per_config)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(per_config, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nSaved per-category breakdown to {out_path}")


if __name__ == "__main__":
    main()
