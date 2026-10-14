"""n=100 variant of score_scifact_cross_vs_same_model.py. Reuses its
accuracy()/macro_f1()/mcnemar() functions unmodified; only the input/output
paths differ, per SCIFACT_N100_EXPANSION_PREREGISTRATION_20260727.md.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from score_scifact_cross_vs_same_model import accuracy, macro_f1, mcnemar  # noqa: E402

SAME = PROJECT_ROOT / "data/external_benchmarks/scifact_semantic_pilot_n100/scifact_semantic_pilot_outputs.json"
CROSS = PROJECT_ROOT / "data/external_benchmarks/scifact_cross_model_pilot_n100/scifact_cross_model_pilot_outputs.json"
OUT = PROJECT_ROOT / "data/external_benchmarks/scifact_cross_vs_same_model_n100/comparison.json"


def benjamini_hochberg(p_values: dict[str, float], q: float = 0.05) -> dict[str, dict]:
    items = sorted(p_values.items(), key=lambda kv: kv[1])
    m = len(items)
    max_rank_pass = 0
    for rank, (_key, p) in enumerate(items, start=1):
        if p <= q * rank / m:
            max_rank_pass = rank
    out = {}
    for rank, (key, p) in enumerate(items, start=1):
        out[key] = {"p": p, "rank": rank, "bh_critical": q * rank / m, "significant_after_fdr": rank <= max_rank_pass}
    return out


def main() -> None:
    same = json.loads(SAME.read_text(encoding="utf-8"))
    cross = json.loads(CROSS.read_text(encoding="utf-8"))
    same_by_id = {r["id"]: r for r in same}
    cross_by_id = {r["id"]: r for r in cross}
    common_ids = sorted(set(same_by_id) & set(cross_by_id))
    print(f"common claims: {len(common_ids)}")

    v0_identical = all(same_by_id[i]["draft"] == cross_by_id[i]["draft"] for i in common_ids)
    print(f"V0 drafts identical across both pilots: {v0_identical}")

    same_rows = [same_by_id[i] for i in common_ids]
    cross_rows = [cross_by_id[i] for i in common_ids]

    results = {
        "n": len(common_ids),
        "v0_drafts_identical_across_pilots": v0_identical,
        "v0": {"accuracy": accuracy(same_rows, "v0_label"), "macro_f1": macro_f1(same_rows, "v0_label")},
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

    p_values = {}
    for key in ("mcnemar_v0_vs_same_model_final", "mcnemar_v0_vs_cross_model_final", "mcnemar_same_model_final_vs_cross_model_final"):
        p = results[key].get("p_value_exact_binomial")
        if p is not None:
            p_values[key] = p
    if p_values:
        fdr = benjamini_hochberg(p_values, q=0.05)
        for key, info in fdr.items():
            results[key]["bh_fdr"] = info
        results["_fdr_summary"] = {"family_size": len(p_values), "q_threshold": 0.05,
                                     "any_significant_after_fdr": any(v["significant_after_fdr"] for v in fdr.values())}

    per_claim = []
    for i in common_ids:
        s, c = same_by_id[i], cross_by_id[i]
        per_claim.append({
            "id": i, "gold": s["gold"], "v0": s["v0_label"],
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
