from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

SOURCE = (
    PROJECT_ROOT
    / "data/reports/ipm_major_revision_20260721/repro/v3/"
    / "title_match_single_vs_arl_20260730/final_gold_v1_20260730/"
    / "title_match_final_gold_v1.csv"
)
OUT_DIR = (
    PROJECT_ROOT
    / "data/reports/ipm_major_revision_20260721/repro/v3/"
    / "title_match_single_vs_arl_20260730/threshold_sensitivity_20260730"
)
THRESHOLDS = (0.60, 0.65, 0.70, 0.72, 0.75, 0.80, 0.85, 0.90, 0.95)


def _score(reference: str, candidate: str) -> float:
    import evaluate_metrics as em

    reference_norm = em._normalize_title(reference)
    candidate_norm = em._normalize_title(candidate)
    if not reference_norm or not candidate_norm:
        return 0.0
    if candidate_norm in reference_norm or reference_norm in candidate_norm:
        return 1.0
    reference_tokens = set(em._title_tokens(reference))
    candidate_tokens = set(em._title_tokens(candidate))
    token_ratio = len(reference_tokens & candidate_tokens) / max(
        1, min(len(reference_tokens), len(candidate_tokens))
    )
    sequence_ratio = SequenceMatcher(
        None, reference_norm, candidate_norm
    ).ratio()
    return max(token_ratio, sequence_ratio)


def _language(row: dict[str, str]) -> str:
    text = f"{row.get('reference_string', '')} {row.get('candidate_evidence_title', '')}"
    return "Chinese-present" if re.search(r"[\u4e00-\u9fff]", text) else "English/Latin"


def _metrics(rows: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
    tp = fp = fn = tn = 0
    for row in rows:
        predicted = row["score"] >= threshold
        actual = row["final_gold_label"] == "match"
        if predicted and actual:
            tp += 1
        elif predicted and not actual:
            fp += 1
        elif not predicted and actual:
            fn += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / len(rows) if rows else 0.0
    return {
        "n": len(rows),
        "threshold": threshold,
        "predicted_match": tp + fp,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": accuracy,
    }


def main() -> None:
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 320:
        raise RuntimeError(f"Expected 320 gold pairs, found {len(rows)}")
    for row in rows:
        row["score"] = _score(
            row["reference_string"], row["candidate_evidence_title"]
        )
        row["language_group"] = _language(row)
        row["collision_flag"] = (
            "high-score nonmatch" if row["score"] >= 0.90 and row["final_gold_label"] == "nonmatch" else ""
        )

    overall = [_metrics(rows, threshold) for threshold in THRESHOLDS]
    grouped: list[dict[str, Any]] = []
    group_values = sorted({row["language_group"] for row in rows})
    group_values += sorted({row["domain"] for row in rows})
    for group_name in group_values:
        group_rows = [
            row
            for row in rows
            if row["language_group"] == group_name or row["domain"] == group_name
        ]
        group_type = "language" if group_name in {row["language_group"] for row in rows} else "domain"
        for threshold in THRESHOLDS:
            result = _metrics(group_rows, threshold)
            result.update({"group_type": group_type, "group": group_name})
            grouped.append(result)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pair_fields = [
        "pair_id", "query_id", "domain", "language_group", "reference_string",
        "candidate_evidence_title", "final_gold_label", "score", "collision_flag",
    ]
    with (OUT_DIR / "title_match_pair_scores_20260730.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=pair_fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in pair_fields})

    metric_fields = [
        "group_type", "group", "threshold", "n", "predicted_match", "tp", "fp",
        "fn", "tn", "precision", "recall", "f1", "accuracy",
    ]
    with (OUT_DIR / "title_match_threshold_metrics_20260730.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=metric_fields)
        writer.writeheader()
        for result in overall:
            writer.writerow({"group_type": "overall", "group": "all", **result})
        writer.writerows(grouped)

    collisions = [
        {
            "pair_id": row["pair_id"],
            "domain": row["domain"],
            "score": row["score"],
            "reference_string": row["reference_string"],
            "candidate_evidence_title": row["candidate_evidence_title"],
        }
        for row in rows
        if row["collision_flag"]
    ]
    report = {
        "source": str(SOURCE),
        "n_pairs": len(rows),
        "gold_distribution": dict(Counter(row["final_gold_label"] for row in rows)),
        "thresholds": list(THRESHOLDS),
        "overall": overall,
        "grouped": grouped,
        "high_score_nonmatch_count": len(collisions),
        "high_score_nonmatches": collisions,
        "interpretation": {
            "threshold_role": "A screening cutoff on a title-similarity score, not a proof of bibliographic identity.",
            "metadata_boundary": "High-score nonmatches remain when generic or ambiguous titles collide; a threshold alone cannot resolve missing author, journal, year, or DOI metadata.",
            "historical_results": "The frozen historical single-agent and ARL estimates are unchanged. This is a calibration and sensitivity analysis, not a retroactive relabeling of those outputs.",
        },
    }
    (OUT_DIR / "TITLE_MATCH_THRESHOLD_SENSITIVITY_20260730.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# Title-match threshold sensitivity analysis (2026-07-30)",
        "",
        f"Source: `{SOURCE}`",
        "Unit: 320 final human-gold reference/candidate pairs.",
        "",
        "## Overall results",
        "",
        "| threshold | predicted match | TP | FP | FN | TN | precision | recall | F1 | accuracy |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for result in overall:
        lines.append(
            f"| {result['threshold']:.2f} | {result['predicted_match']} | {result['tp']} | {result['fp']} | {result['fn']} | {result['tn']} | {result['precision']:.3f} | {result['recall']:.3f} | {result['f1']:.3f} | {result['accuracy']:.3f} |"
        )
    lines += [
        "",
        "## What this resolves",
        "",
        "The analysis shows how the cutoff trades false positives against recall. On this set, the tested positive pairs retain recall through 0.85, while precision improves as the cutoff becomes stricter.",
        "",
        "## What a threshold cannot resolve",
        "",
        f"There are {len(collisions)} high-score nonmatches (score >= 0.90). These are identity collisions involving generic or ambiguous titles. Because the candidate field contains only a title, no numeric cutoff can infer which author, journal, year, or DOI the record denotes.",
        "The protocol therefore keeps 0.72 as the frozen historical screening cutoff, reports this sensitivity analysis, and changes the future rule to: DOI/stable identifier first; title plus bibliographic metadata second; fuzzy title score only as a fallback. The analysis does not retroactively change the historical ARL or single-agent estimates.",
        "",
        "## Boundary",
        "",
        "This 320-pair set supports a sensitivity audit, not a universal optimum claim. A genuinely validated threshold would require a prespecified held-out calibration set or nested validation across new domains and languages.",
    ]
    (OUT_DIR / "TITLE_MATCH_THRESHOLD_SENSITIVITY_20260730.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print(OUT_DIR)
    print(json.dumps({"overall": overall, "collisions": len(collisions)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
