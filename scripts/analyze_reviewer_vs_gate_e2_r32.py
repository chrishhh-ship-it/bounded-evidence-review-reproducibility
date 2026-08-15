"""Analysis for E2/R3-2 gap closure, per
E2_R3-2_REVIEWER_VS_GATE_PREREGISTRATION_20260727.md: compares the fresh
structured LLM Reviewer's overall RELEASE/BLOCK verdict against the
deterministic gate's actual release (pass/block) on all 251 frozen B0
drafts. BLOCK is the positive class.
"""
from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = PROJECT_ROOT / "data/reports/ipm_major_revision_20260721/repro/v3/e2_r32_reviewer_vs_gate/reviewer_vs_gate_results.json"
OUT_PATH = PROJECT_ROOT / "data/reports/ipm_major_revision_20260721/repro/v3/e2_r32_reviewer_vs_gate/reviewer_vs_gate_metrics.json"


def main() -> None:
    rows = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    n = len(rows)

    tp = fp = fn = tn = unparseable = 0
    for r in rows:
        gate_positive = r["gate_release"] == "block"
        reviewer = r["reviewer_overall"]
        if reviewer == "UNPARSEABLE":
            unparseable += 1
            continue
        reviewer_positive = reviewer == "BLOCK"
        if gate_positive and reviewer_positive:
            tp += 1
        elif (not gate_positive) and reviewer_positive:
            fp += 1
        elif gate_positive and (not reviewer_positive):
            fn += 1
        else:
            tn += 1

    scored = tp + fp + fn + tn
    accuracy = (tp + tn) / scored if scored else None
    precision = tp / (tp + fp) if (tp + fp) else None
    recall = tp / (tp + fn) if (tp + fn) else None
    f1 = (2 * precision * recall / (precision + recall)) if precision and recall and (precision + recall) else None

    # reason-level overlap: does reviewer flag orphan citations when gate has text_orphans>0?
    orphan_agree = orphan_total = 0
    uncited_agree = uncited_total = 0
    for r in rows:
        verdict = r["reviewer_verdict"]
        if not isinstance(verdict, dict):
            continue
        gate_has_orphan = r["gate_text_orphans"] > 0
        reviewer_has_orphan = bool(verdict.get("orphan_citation_numbers"))
        orphan_total += 1
        if gate_has_orphan == reviewer_has_orphan:
            orphan_agree += 1

        gate_has_uncited = r["gate_uncited_bibliography_entries"] > 0
        reviewer_has_uncited = bool(verdict.get("uncited_bibliography_numbers"))
        uncited_total += 1
        if gate_has_uncited == reviewer_has_uncited:
            uncited_agree += 1

    results = {
        "n_total": n,
        "n_scored": scored,
        "n_unparseable_reviewer_verdict": unparseable,
        "confusion_matrix": {"TP_block_block": tp, "FP_reviewer_block_gate_pass": fp,
                              "FN_reviewer_release_gate_block": fn, "TN_release_release": tn},
        "accuracy": accuracy,
        "precision_block": precision,
        "recall_block": recall,
        "f1_block": f1,
        "reason_level_agreement": {
            "orphan_citation_flag_agreement_rate": orphan_agree / orphan_total if orphan_total else None,
            "uncited_bibliography_flag_agreement_rate": uncited_agree / uncited_total if uncited_total else None,
        },
        "note": "BLOCK is the positive class; deterministic gate release (pass/block) is treated as the structural-compliance reference standard, not a semantic gold standard.",
    }
    OUT_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\nwrote: {OUT_PATH}")


if __name__ == "__main__":
    main()
