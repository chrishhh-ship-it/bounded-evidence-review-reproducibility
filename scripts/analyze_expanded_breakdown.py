from __future__ import annotations

import argparse
import os
import json
import re
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.evaluate_metrics import (
    PROJECT_ROOT,
    _build_candidate_pool,
    _extract_citations_from_text,
    _infer_config_tag,
    _paper_id,
    _parse_bib_entries,
    _parse_result_stem,
    _section_map,
    _select_latest_per_query,
    _split_body_bib,
    _match_title,
    evaluate_file,
)


DEFAULT_BENCHMARK = PROJECT_ROOT / "data" / "benchmarks" / "benchmark_all_queries.json"
DEFAULT_CORPUS = PROJECT_ROOT / "data" / "frozen_corpus_multidomain_v1.json"
DEFAULT_OUT = PROJECT_ROOT / "data" / "reports" / "expanded_domain_breakdown_20260416.json"

CONFIG_DIRS: Dict[str, Path] = {
    "method1": PROJECT_ROOT / "data" / "expanded_outputs" / "method1",
    "method2a": PROJECT_ROOT / "data" / "expanded_outputs" / "method2a",
    "method2b": PROJECT_ROOT / "data" / "expanded_outputs" / "method2b",
    "method2d": PROJECT_ROOT / "data" / "expanded_outputs" / "method2d",
}

_WORKER_FROZEN_BY_ID: Optional[Dict[str, Dict[str, Any]]] = None


def _safe_pct(values: Iterable[float]) -> Optional[float]:
    values = list(values)
    if not values:
        return None
    return round(mean(values) * 100, 1)


def _safe_num_mean(values: Iterable[float]) -> Optional[float]:
    values = list(values)
    if not values:
        return None
    return round(mean(values), 2)


def _normalize_qid(raw: str) -> str:
    m = re.search(r"(\d+)", raw or "")
    if not m:
        return raw
    return f"Q{int(m.group(1)):03d}"


def _load_query_meta(path: Path) -> Dict[str, Dict[str, Any]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    meta: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        qid = _normalize_qid(row.get("id", ""))
        meta[qid] = row
    return meta


def _compute_structural_metrics(md_path: Path, frozen_by_id: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    content = md_path.read_text(encoding="utf-8", errors="replace")
    sidecar_path = md_path.with_suffix(".json")
    sidecar: Dict[str, Any] = {}
    if sidecar_path.exists():
        sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))

    body, bib_text = _split_body_bib(content)
    bib_entries = _parse_bib_entries(bib_text)
    cite_nums = _extract_citations_from_text(body)

    total_cites = len(cite_nums)
    structural_valid = sum(1 for num in cite_nums if num in bib_entries)
    structural_orphans = total_cites - structural_valid

    candidate_pool = _build_candidate_pool(sidecar, frozen_by_id)
    candidate_titles = [row.get("title", "") for row in candidate_pool]

    matched_bib = 0
    for _, ref_text in bib_entries.items():
        if _match_title(ref_text, candidate_titles):
            matched_bib += 1

    section_patterns = _section_map(_infer_config_tag(md_path, _parse_result_stem(md_path.stem)[1] if _parse_result_stem(md_path.stem) else None))
    section_hits = sum(1 for pat in section_patterns if pat.search(content))
    section_completeness = section_hits / len(section_patterns) if section_patterns else 0.0

    top_papers = sidecar.get("top_papers", []) or []
    abstract_coverage = (
        sum(1 for paper in top_papers if (paper.get("abstract") or "").strip()) / len(top_papers)
        if top_papers
        else 0.0
    )

    return {
        "total_cites": total_cites,
        "structural_icp": (structural_valid / total_cites) if total_cites else None,
        "structural_orphan": (structural_orphans / total_cites) if total_cites else None,
        "bmr": (matched_bib / len(bib_entries)) if bib_entries else None,
        "n_bib_entries": len(bib_entries),
        "section_completeness": section_completeness,
        "abstract_coverage": abstract_coverage,
    }


def _summarise_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "n_queries": len(rows),
        "structural_icp_pct": _safe_pct(r["structural_icp"] for r in rows if r["structural_icp"] is not None),
        "structural_orphan_pct": _safe_pct(r["structural_orphan"] for r in rows if r["structural_orphan"] is not None),
        "corpus_cp_pct": _safe_pct(r["corpus_cp"] for r in rows if r["corpus_cp"] is not None),
        "bmr_pct": _safe_pct(r["bmr"] for r in rows if r["bmr"] is not None),
        "section_completeness_pct": _safe_pct(r["section_completeness"] for r in rows if r["section_completeness"] is not None),
        "abstract_coverage_pct": _safe_pct(r["abstract_coverage"] for r in rows if r["abstract_coverage"] is not None),
        "avg_bib_entries": _safe_num_mean(r["n_bib_entries"] for r in rows),
        "avg_cite_tags": _safe_num_mean(r["total_cites"] for r in rows),
    }


def _load_corpus_map(corpus_path: Path) -> Dict[str, Dict[str, Any]]:
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    by_id: Dict[str, Dict[str, Any]] = {}
    for row in corpus:
        by_id[_paper_id(row)] = row
    return by_id


def _init_worker(corpus_path_str: str = str(DEFAULT_CORPUS)) -> None:
    global _WORKER_FROZEN_BY_ID
    if _WORKER_FROZEN_BY_ID is None:
        _WORKER_FROZEN_BY_ID = _load_corpus_map(Path(corpus_path_str))


def _evaluate_task(task: Tuple[str, str, str, Dict[str, Any]]) -> Optional[Tuple[str, Dict[str, Any]]]:
    global _WORKER_FROZEN_BY_ID
    if _WORKER_FROZEN_BY_ID is None:
        _init_worker()

    config, md_path_str, parsed_tag, meta = task
    md_path = Path(md_path_str)

    evaluated = evaluate_file(md_path, _infer_config_tag(md_path, parsed_tag), _WORKER_FROZEN_BY_ID or {})
    structural = _compute_structural_metrics(md_path, _WORKER_FROZEN_BY_ID or {})

    row = {
        "query_id": _normalize_qid(meta["id"]),
        "domain_id": meta["domain_id"],
        "domain_name": meta.get("domain_name") or meta.get("domain_label") or meta["domain_id"],
        "category": meta["category"],
        "difficulty": meta.get("difficulty"),
        "corpus_cp": evaluated["citation_precision"],
        "structural_icp": structural["structural_icp"],
        "structural_orphan": structural["structural_orphan"],
        "bmr": structural["bmr"],
        "section_completeness": structural["section_completeness"],
        "abstract_coverage": structural["abstract_coverage"],
        "n_bib_entries": structural["n_bib_entries"],
        "total_cites": structural["total_cites"],
    }
    return config, row


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute expanded benchmark breakdown by domain/config.")
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK))
    parser.add_argument("--corpus", default=str(DEFAULT_CORPUS))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--workers", type=int, default=max(1, min(8, (os.cpu_count() or 2) - 1)))
    args = parser.parse_args()

    query_meta = _load_query_meta(Path(args.benchmark))
    _init_worker(args.corpus)

    result: Dict[str, Any] = {"configs": {}, "deltas_vs_method1": {}}
    tasks: List[Tuple[str, str, str, Dict[str, Any]]] = []

    for config, directory in CONFIG_DIRS.items():
        md_files = sorted(directory.glob("*.md"))
        latest = list(_select_latest_per_query(md_files).values())

        for md_path in latest:
            parsed = _parse_result_stem(md_path.stem)
            if not parsed:
                continue
            query_id, parsed_tag, _ = parsed
            meta = query_meta.get(_normalize_qid(query_id))
            if not meta:
                continue
            tasks.append((config, str(md_path), parsed_tag, meta))

    total_tasks = len(tasks)
    print(f"[Breakdown] Evaluating {total_tasks} canonical reports with {args.workers} workers.")
    rows_by_config: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    if args.workers <= 1:
        for idx, task in enumerate(tasks, start=1):
            item = _evaluate_task(task)
            if item:
                config, row = item
                rows_by_config[config].append(row)
            if idx % 25 == 0 or idx == total_tasks:
                print(f"[Breakdown] {idx}/{total_tasks} completed.")
    else:
        with ProcessPoolExecutor(
            max_workers=args.workers,
            initializer=_init_worker,
            initargs=(args.corpus,),
        ) as executor:
            futures = [executor.submit(_evaluate_task, task) for task in tasks]
            done = 0
            for future in as_completed(futures):
                item = future.result()
                if item:
                    config, row = item
                    rows_by_config[config].append(row)
                done += 1
                if done % 25 == 0 or done == total_tasks:
                    print(f"[Breakdown] {done}/{total_tasks} completed.")

    for config in CONFIG_DIRS:
        per_query = rows_by_config.get(config, [])
        by_domain_rows: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for row in per_query:
            by_domain_rows[row["domain_id"]].append(row)

        by_domain = {
            domain_id: {
                "domain_name": rows[0]["domain_name"],
                **_summarise_rows(rows),
            }
            for domain_id, rows in by_domain_rows.items()
        }

        result["configs"][config] = {
            "overall": _summarise_rows(per_query),
            "by_domain": by_domain,
        }

    method1_domains = result["configs"].get("method1", {}).get("by_domain", {})
    for config in ("method2a", "method2b", "method2d"):
        config_domains = result["configs"].get(config, {}).get("by_domain", {})
        deltas: Dict[str, Dict[str, Optional[float]]] = {}
        for domain_id, m1 in method1_domains.items():
            other = config_domains.get(domain_id, {})
            cp_delta = None
            if m1.get("corpus_cp_pct") is not None and other.get("corpus_cp_pct") is not None:
                cp_delta = round(other["corpus_cp_pct"] - m1["corpus_cp_pct"], 1)
            icp_delta = None
            if m1.get("structural_icp_pct") is not None and other.get("structural_icp_pct") is not None:
                icp_delta = round(other["structural_icp_pct"] - m1["structural_icp_pct"], 1)
            orphan_delta = None
            if m1.get("structural_orphan_pct") is not None and other.get("structural_orphan_pct") is not None:
                orphan_delta = round(other["structural_orphan_pct"] - m1["structural_orphan_pct"], 1)
            deltas[domain_id] = {
                "domain_name": m1.get("domain_name"),
                "delta_structural_icp_pct": icp_delta,
                "delta_corpus_cp_pct": cp_delta,
                "delta_structural_orphan_pct": orphan_delta,
            }
        result["deltas_vs_method1"][config] = deltas

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved expanded breakdown to {out_path}")


if __name__ == "__main__":
    main()
