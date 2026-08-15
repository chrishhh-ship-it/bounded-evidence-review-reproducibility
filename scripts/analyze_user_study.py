from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "user_study" / "analysis_responses_n30.csv"

SYSTEM_LABELS = {
    "A": "Core CDMA without ARL (M1)",
    "B": "Same-model ARL (M2b)",
    "C": "Cross-model CDMA+ARL (M2a)",
}


def _load_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Input CSV not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit(f"Input CSV is empty: {path}")
    return rows


def _float_values(rows: list[dict[str, str]], field: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        raw = row.get(field, "")
        if raw == "":
            continue
        values.append(float(raw))
    return values


def _rank_positions(rows: list[dict[str, str]]) -> dict[str, list[int]]:
    positions: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        for pos, field in (
            (1, "rank_1st_system"),
            (2, "rank_2nd_system"),
            (3, "rank_3rd_system"),
        ):
            system = row.get(field)
            if system in SYSTEM_LABELS:
                positions[system].append(pos)
    return positions


def summarize(rows: list[dict[str, str]]) -> dict[str, Any]:
    n_records = len(rows)
    participants = sorted({row.get("participant", "") for row in rows})
    questions = sorted({row.get("qno", "") for row in rows})

    rank1_counts = Counter(
        row.get("rank_1st_system") for row in rows if row.get("rank_1st_system") in SYSTEM_LABELS
    )
    suspicious_counts = Counter(
        row.get("suspicious_system") for row in rows if row.get("suspicious_system") in SYSTEM_LABELS
    )
    rank_positions = _rank_positions(rows)

    systems: dict[str, Any] = {}
    for system in ("A", "B", "C"):
        scores = _float_values(rows, f"score_{system}")
        ranks = rank_positions.get(system, [])
        systems[system] = {
            "label": SYSTEM_LABELS[system],
            "rank_1st_count": rank1_counts.get(system, 0),
            "rank_1st_pct": round(rank1_counts.get(system, 0) / n_records * 100, 1),
            "avg_rank": round(statistics.mean(ranks), 2) if ranks else None,
            "mean_score": round(statistics.mean(scores), 2) if scores else None,
            "score_sd": round(statistics.stdev(scores), 2) if len(scores) > 1 else None,
            "most_suspicious_count": suspicious_counts.get(system, 0),
            "most_suspicious_pct": round(suspicious_counts.get(system, 0) / n_records * 100, 1),
            "n_scores": len(scores),
            "n_ranks": len(ranks),
        }

    return {
        "input_records": n_records,
        "n_participants": len(participants),
        "n_questions": len(questions),
        "participants": participants,
        "systems": systems,
        "rank_1st_counts": dict(rank1_counts),
        "most_suspicious_counts": dict(suspicious_counts),
    }


def print_summary(summary: dict[str, Any]) -> None:
    print(f"[input] records={summary['input_records']}, participants={summary['n_participants']}, questions={summary['n_questions']}")
    print()
    print("System-level descriptive statistics")
    for system in ("C", "A", "B"):
        stats = summary["systems"][system]
        print(
            f"  {system} ({stats['label']}): "
            f"rank_1st={stats['rank_1st_pct']:.1f}%, "
            f"avg_rank={stats['avg_rank']:.2f}, "
            f"mean={stats['mean_score']:.2f}, "
            f"sd={stats['score_sd']:.2f}, "
            f"most_suspicious={stats['most_suspicious_pct']:.1f}%"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze the cleaned 30-participant user-study CSV. This script is "
            "read-only by default and never overwrites the deposited analysis table."
        )
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Anonymized analysis-ready CSV (default: data/user_study/analysis_responses_n30.csv).",
    )
    parser.add_argument(
        "--summary-json",
        default=None,
        help="Optional path where the computed descriptive summary should be written as JSON.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    rows = _load_rows(input_path)
    summary = summarize(rows)
    print_summary(summary)

    if args.summary_json:
        out_path = Path(args.summary_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n[ok] summary JSON written: {out_path}")


if __name__ == "__main__":
    main()
