"""Paired significance test for ALCE citation-structure metrics (V0 vs V2),
reusing the exact citation_diagnostics() function from the project's own
scoring script -- not a reimplementation -- so the numbers are guaranteed
identical to metrics.json. Uses paired Wilcoxon signed-rank (same convention
as the project's other query-level paired comparisons) since
citation_index_validity / sentence_citation_coverage are per-record
proportions, not binary outcomes, so McNemar does not apply here.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "external_benchmark"))
from score_alce_official_pilot import citation_diagnostics  # noqa: E402

try:
    from scipy.stats import wilcoxon
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False

DEFAULT_RUN_DIR = PROJECT_ROOT / "data" / "external_benchmarks" / "alce_official_pilot_n15_expanded"


def benjamini_hochberg(p_values: dict[str, float], q: float = 0.05) -> dict[str, dict]:
    items = sorted(p_values.items(), key=lambda kv: kv[1])
    m = len(items)
    out = {}
    max_rank_pass = 0
    for rank, (_key, p) in enumerate(items, start=1):
        critical = q * rank / m
        if p <= critical:
            max_rank_pass = rank
    for rank, (key, p) in enumerate(items, start=1):
        out[key] = {"p": p, "rank": rank, "bh_critical": q * rank / m, "significant_after_fdr": rank <= max_rank_pass}
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    args = parser.parse_args()
    RUN_DIR = args.run_dir
    records = json.loads((RUN_DIR / "alce_official_pilot_outputs.json").read_text(encoding="utf-8"))
    by_dataset = {}
    for r in records:
        by_dataset.setdefault(r["dataset"], {}).setdefault(r.get("sample_id") or r.get("id"), {})[r["condition"]] = r

    results = {}
    for dataset, by_sample in by_dataset.items():
        v0_validity, v2_validity = [], []
        v0_coverage, v2_coverage = [], []
        for sample_id, conds in by_sample.items():
            if "v0" not in conds or "v2" not in conds:
                continue
            d0 = citation_diagnostics(conds["v0"])
            d2 = citation_diagnostics(conds["v2"])
            v0_validity.append(d0["citation_index_validity"])
            v2_validity.append(d2["citation_index_validity"])
            v0_coverage.append(d0["sentence_citation_coverage"])
            v2_coverage.append(d2["sentence_citation_coverage"])

        n = len(v0_validity)
        entry = {"n_pairs": n}
        for name, a, b in (("citation_index_validity", v0_validity, v2_validity),
                            ("sentence_citation_coverage", v0_coverage, v2_coverage)):
            diffs = [y - x for x, y in zip(a, b)]
            mean_diff = sum(diffs) / len(diffs) if diffs else None
            n_nonzero = sum(1 for d in diffs if d != 0)
            n_improved = sum(1 for d in diffs if d > 0)
            n_worsened = sum(1 for d in diffs if d < 0)
            stat_entry = {
                "mean_v0": sum(a) / len(a) if a else None,
                "mean_v2": sum(b) / len(b) if b else None,
                "mean_diff_v2_minus_v0": mean_diff,
                "n_pairs_improved": n_improved,
                "n_pairs_worsened": n_worsened,
                "n_pairs_unchanged": n - n_nonzero,
            }
            if HAVE_SCIPY and n_nonzero >= 1:
                try:
                    stat, p = wilcoxon(a, b, zero_method="wilcox", alternative="two-sided")
                    stat_entry["wilcoxon_statistic"] = float(stat)
                    stat_entry["wilcoxon_p_two_sided"] = float(p)
                except Exception as exc:
                    stat_entry["wilcoxon_error"] = str(exc)
            else:
                stat_entry["wilcoxon_note"] = "scipy unavailable or all pairs tied; report descriptive only"
            entry[name] = stat_entry
        results[dataset] = entry

    p_values = {}
    for dataset, entry in results.items():
        for metric in ("citation_index_validity", "sentence_citation_coverage"):
            p = entry[metric].get("wilcoxon_p_two_sided")
            if p is not None:
                p_values[f"{dataset}/{metric}"] = p
    if p_values:
        fdr = benjamini_hochberg(p_values, q=0.05)
        for key, info in fdr.items():
            dataset, metric = key.split("/", 1)
            results[dataset][metric]["bh_fdr"] = info
        results["_fdr_summary"] = {
            "family_size": len(p_values),
            "q_threshold": 0.05,
            "any_significant_after_fdr": any(v["significant_after_fdr"] for v in fdr.values()),
        }

    out_path = RUN_DIR / "structural_significance_v0_vs_v2.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\nwrote: {out_path}")


if __name__ == "__main__":
    main()
