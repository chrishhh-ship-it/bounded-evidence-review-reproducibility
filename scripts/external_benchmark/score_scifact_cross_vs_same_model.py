"""Compare same-model (deepseek reviews deepseek) vs cross-model (kimi reviews
deepseek) SciFact ARL pilots on the SAME 40 claims (identical V0 drafts,
reused across both pilots). Answers: is the accuracy decline seen in the
same-model pilot a same-model artifact, or does it persist cross-model?

McNemar's test on paired binary correctness (V0-correct vs Final-correct)
because the same 40 claims are evaluated in both settings.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAME = PROJECT_ROOT / "data/external_benchmarks/scifact_semantic_pilot_n40/scifact_semantic_pilot_outputs.json"
CROSS = PROJECT_ROOT / "data/external_benchmarks/scifact_cross_model_pilot_n40/scifact_cross_model_pilot_outputs.json"
OUT = PROJECT_ROOT / "data/external_benchmarks/scifact_cross_vs_same_model_n40/comparison.json"


def accuracy(rows: list[dict], field: str) -> float:
    correct = sum(1 for r in rows if r[field] == r["gold"])
    return correct / len(rows)


def macro_f1(rows: list[dict], field: str) -> float:
    labels = {"SUPPORT", "CONTRADICT", "NEI"}
    f1s = []
    for lab in labels:
        tp = sum(1 for r in rows if r[field] == lab and r["gold"] == lab)
        fp = sum(1 for r in rows if r[field] == lab and r["gold"] != lab)
        fn = sum(1 for r in rows if r[field] != lab and r["gold"] == lab)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        f1s.append(f1)
    return sum(f1s) / len(f1s)


def mcnemar(a_correct: list[bool], b_correct: list[bool]) -> dict:
    # b01: A correct, B wrong. b10: A wrong, B correct.
    b01 = sum(1 for a, b in zip(a_correct, b_correct) if a and not b)
    b10 = sum(1 for a, b in zip(a_correct, b_correct) if not a and b)
    n = b01 + b10
    if n == 0:
        return {"b01": b01, "b10": b10, "statistic": None, "p_value": None,
                "note": "no discordant pairs"}
    # exact binomial two-sided test on the discordant pairs (small-n safe,
    # equivalent to exact McNemar)
    from math import comb
    k = min(b01, b10)
    p_value = 0.0
    for i in range(0, k + 1):
        p_value += comb(n, i) * (0.5 ** n)
    p_value = min(1.0, 2 * p_value)
    return {"b01": b01, "b10": b10, "n_discordant": n, "p_value_exact_binomial": p_value}


def main() -> None:
    same = json.loads(SAME.read_text(encoding="utf-8"))
    cross = json.loads(CROSS.read_text(encoding="utf-8"))
    same_by_id = {r["id"]: r for r in same}
    cross_by_id = {r["id"]: r for r in cross}
    common_ids = sorted(set(same_by_id) & set(cross_by_id))
    print(f"common claims: {len(common_ids)}")

    # sanity: confirm V0 drafts are IDENTICAL between the two pilots (reused)
    v0_identical = all(same_by_id[i]["draft"] == cross_by_id[i]["draft"] for i in common_ids)
    print(f"V0 drafts identical across both pilots: {v0_identical}")

    same_rows = [same_by_id[i] for i in common_ids]
    cross_rows = [cross_by_id[i] for i in common_ids]

    results = {
        "n": len(common_ids),
        "v0_drafts_identical_across_pilots": v0_identical,
        "v0": {
            "accuracy": accuracy(same_rows, "v0_label"),
            "macro_f1": macro_f1(same_rows, "v0_label"),
        },
        "same_model_final": {
            "reviewer_model": "deepseek-v4-pro",
            "accuracy": accuracy(same_rows, "v2_final_label"),
            "macro_f1": macro_f1(same_rows, "v2_final_label"),
        },
        "cross_model_final": {
            "reviewer_model": "kimi (moonshot-v1-32k)",
            "accuracy": accuracy(cross_rows, "cross_final_label"),
            "macro_f1": macro_f1(cross_rows, "cross_final_label"),
        },
    }

    v0_correct = [same_by_id[i]["v0_label"] == same_by_id[i]["gold"] for i in common_ids]
    same_final_correct = [same_by_id[i]["v2_final_label"] == same_by_id[i]["gold"] for i in common_ids]
    cross_final_correct = [cross_by_id[i]["cross_final_label"] == cross_by_id[i]["gold"] for i in common_ids]

    results["mcnemar_v0_vs_same_model_final"] = mcnemar(v0_correct, same_final_correct)
    results["mcnemar_v0_vs_cross_model_final"] = mcnemar(v0_correct, cross_final_correct)
    results["mcnemar_same_model_final_vs_cross_model_final"] = mcnemar(same_final_correct, cross_final_correct)

    # per-claim detail for auditability
    per_claim = []
    for i in common_ids:
        s, c = same_by_id[i], cross_by_id[i]
        per_claim.append({
            "id": i, "gold": s["gold"],
            "v0": s["v0_label"],
            "same_model_reviewer": s["v2_reviewer_label"], "same_model_final": s["v2_final_label"],
            "cross_model_reviewer_kimi": c["cross_reviewer_label"], "cross_model_final": c["cross_final_label"],
        })
    results["per_claim"] = per_claim

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in results.items() if k != "per_claim"}, ensure_ascii=False, indent=2))
    print(f"\nwrote: {OUT}")


if __name__ == "__main__":
    main()
