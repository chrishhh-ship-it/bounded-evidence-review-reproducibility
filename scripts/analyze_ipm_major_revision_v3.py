from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import bootstrap, norm, pearsonr, spearmanr, wilcoxon


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import evaluate_metrics as em  # noqa: E402


CORPUS_PATH = PROJECT_ROOT / "data" / "frozen_corpus_multidomain_v1.json"
USER_STUDY_PATH = PROJECT_ROOT / "data" / "user_study" / "analysis_responses_n30.csv"
ANSWER_KEY_PATH = PROJECT_ROOT / "data" / "user_study" / "answer_key.json"
ANNOTATION_DIR = PROJECT_ROOT / "data" / "annotation"

CONFIGS = {
    "M1": ("method1", "method1"),
    "M2a": ("method2a", "method2"),
    "M2b": ("method2b", "method2_same_model"),
    "M2c": ("method2d", "method2c"),
}

SYSTEMS = {
    "A": ("M1", "method1", "method1"),
    "B": ("M2b", "method2b", "method2_same_model"),
    "C": ("M2a", "method2a", "method2"),
}


def _load_corpus() -> dict[str, dict[str, Any]]:
    corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    return {em._paper_id(row): row for row in corpus}


def _latest_rows(
    dirname: str,
    tag: str,
    frozen_by_id: dict[str, dict[str, Any]],
    threshold: float = 0.72,
) -> dict[str, dict[str, Any]]:
    directory = PROJECT_ROOT / "data" / "expanded_outputs" / dirname
    latest = em._select_latest_per_query(list(directory.glob("*.md")))
    rows: dict[str, dict[str, Any]] = {}
    for path in latest.values():
        parsed = em._parse_result_stem(path.stem)
        if not parsed:
            continue
        qid = parsed[0]
        row = em.evaluate_file(path, tag, frozen_by_id, match_threshold=threshold)
        row["qid"] = qid
        row["path"] = str(path.relative_to(PROJECT_ROOT))
        rows[qid] = row
    return rows


def _bh_adjust(p_values: list[float]) -> list[float]:
    n = len(p_values)
    order = sorted(range(n), key=lambda idx: p_values[idx])
    adjusted = [1.0] * n
    running = 1.0
    for rank_from_end, idx in enumerate(reversed(order), start=1):
        rank = n - rank_from_end + 1
        value = min(1.0, p_values[idx] * n / rank)
        running = min(running, value)
        adjusted[idx] = running
    return adjusted


def _bca_mean_ci(diff: np.ndarray) -> tuple[float, float]:
    if diff.size < 2 or np.allclose(diff, diff[0]):
        return float(np.mean(diff)), float(np.mean(diff))
    result = bootstrap(
        (diff,),
        np.mean,
        method="BCa",
        confidence_level=0.95,
        n_resamples=10_000,
        random_state=np.random.default_rng(20260724),
    )
    return float(result.confidence_interval.low), float(result.confidence_interval.high)


def paired_query_analysis(
    rows_by_config: dict[str, dict[str, dict[str, Any]]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    per_query: list[dict[str, Any]] = []
    for config, rows in rows_by_config.items():
        for qid, row in rows.items():
            per_query.append(
                {
                    "config": config,
                    "qid": qid,
                    "citation_precision": row["citation_precision"],
                    "bibliography_match_rate": row["bibliography_match_rate"],
                    "orphan_rate": row["orphan_rate"],
                    "total_citations": row["total_citations"],
                    "bibliography_entries": row["bibliography_entries"],
                    "candidate_pool_size": row["candidate_pool_size"],
                    "path": row["path"],
                }
            )

    comparisons: list[dict[str, Any]] = []
    metrics = ("citation_precision", "bibliography_match_rate", "orphan_rate")
    for challenger in ("M2a", "M2b", "M2c"):
        common = sorted(set(rows_by_config["M1"]) & set(rows_by_config[challenger]))
        for metric in metrics:
            x = np.array(
                [float(rows_by_config["M1"][qid][metric] or 0.0) for qid in common],
                dtype=float,
            )
            y = np.array(
                [float(rows_by_config[challenger][qid][metric] or 0.0) for qid in common],
                dtype=float,
            )
            diff = y - x
            if np.allclose(diff, 0):
                statistic, p_value = 0.0, 1.0
            else:
                test = wilcoxon(diff, zero_method="pratt", alternative="two-sided")
                statistic, p_value = float(test.statistic), float(test.pvalue)
            ci_low, ci_high = _bca_mean_ci(diff)
            comparisons.append(
                {
                    "comparison": f"{challenger}-M1",
                    "metric": metric,
                    "n_pairs": len(common),
                    "mean_M1": float(np.mean(x)),
                    "mean_challenger": float(np.mean(y)),
                    "mean_difference": float(np.mean(diff)),
                    "median_difference": float(np.median(diff)),
                    "bca95_low": ci_low,
                    "bca95_high": ci_high,
                    "wilcoxon_statistic": statistic,
                    "p_raw": p_value,
                }
            )
    adjusted = _bh_adjust([row["p_raw"] for row in comparisons])
    for row, p_adj in zip(comparisons, adjusted):
        row["p_bh_fdr"] = p_adj
    return per_query, comparisons


def deterministic_release_gate(
    rows_by_config: dict[str, dict[str, dict[str, Any]]]
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for config, rows in rows_by_config.items():
        for qid, row in rows.items():
            reasons: list[str] = []
            if not row["has_bibliography"]:
                reasons.append("missing_bibliography")
            if row["text_orphans"] > 0:
                reasons.append("unresolved_in_text_citation")
            if row["uncited_bibliography_entries"] > 0:
                reasons.append("uncited_bibliography_entry")
            if row["bibliography_match_rate"] < 1:
                reasons.append("bibliography_outside_query_evidence")
            results.append(
                {
                    "config": config,
                    "qid": qid,
                    "release": "pass" if not reasons else "block",
                    "reasons": "|".join(reasons),
                    "text_orphans": row["text_orphans"],
                    "uncited_bibliography_entries": row["uncited_bibliography_entries"],
                    "bibliography_match_rate": row["bibliography_match_rate"],
                    "path": row["path"],
                }
            )
    return results


def threshold_sensitivity(
    frozen_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for threshold in (0.60, 0.72, 0.80, 0.90, 1.00):
        for config, (dirname, tag) in CONFIGS.items():
            rows = _latest_rows(dirname, tag, frozen_by_id, threshold=threshold)
            cp = [float(row["citation_precision"] or 0.0) for row in rows.values()]
            bmr = [float(row["bibliography_match_rate"]) for row in rows.values()]
            orphan = [float(row["orphan_rate"]) for row in rows.values()]
            result.append(
                {
                    "threshold": threshold,
                    "config": config,
                    "n": len(rows),
                    "citation_precision_mean": float(np.mean(cp)),
                    "bibliography_match_rate_mean": float(np.mean(bmr)),
                    "orphan_rate_mean": float(np.mean(orphan)),
                }
            )
    return result


def _normal_two_sided_p(z_value: float) -> float:
    return float(2 * norm.sf(abs(z_value)))


def human_study_analysis(
    frozen_by_id: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    import statsmodels.api as sm

    responses = pd.read_csv(USER_STUDY_PATH)
    answer_key = json.loads(ANSWER_KEY_PATH.read_text(encoding="utf-8"))
    long = responses.melt(
        id_vars=["participant", "qno"],
        value_vars=["score_A", "score_B", "score_C"],
        var_name="system",
        value_name="score",
    )
    long["system"] = long["system"].str[-1]
    exog = pd.DataFrame(
        {
            "sys_B": (long["system"] == "B").astype(int),
            "sys_C": (long["system"] == "C").astype(int),
        }
    )
    question_dummies = pd.get_dummies(
        long["qno"].astype(str), prefix="q", drop_first=True, dtype=int
    )
    exog = pd.concat(
        [exog.reset_index(drop=True), question_dummies.reset_index(drop=True)],
        axis=1,
    )
    model = sm.OrdinalGEE(
        long["score"].astype(int),
        exog,
        long["participant"],
        cov_struct=sm.cov_struct.Exchangeable(),
    )
    fitted = model.fit(maxiter=200)
    params = fitted.params
    covariance = fitted.cov_params()

    contrasts: list[dict[str, Any]] = []
    for label, left, right in (
        ("B vs A", "sys_B", None),
        ("C vs A", "sys_C", None),
        ("C vs B", "sys_C", "sys_B"),
    ):
        if right is None:
            estimate = float(params[left])
            variance = float(covariance.loc[left, left])
        else:
            estimate = float(params[left] - params[right])
            variance = float(
                covariance.loc[left, left]
                + covariance.loc[right, right]
                - 2 * covariance.loc[left, right]
            )
        se = math.sqrt(max(variance, 0.0))
        z_value = estimate / se if se else 0.0
        contrasts.append(
            {
                "contrast": label,
                "log_odds": estimate,
                "odds_ratio": math.exp(estimate),
                "se": se,
                "z": z_value,
                "p": _normal_two_sided_p(z_value),
                "ci95_low": math.exp(estimate - 1.96 * se),
                "ci95_high": math.exp(estimate + 1.96 * se),
            }
        )

    descriptive: dict[str, Any] = {}
    for system in ("A", "B", "C"):
        values = responses[f"score_{system}"].astype(float)
        descriptive[system] = {
            "label": SYSTEMS[system][0],
            "mean": float(values.mean()),
            "sd": float(values.std(ddof=1)),
            "rank_first_n": int((responses["rank_1st_system"] == system).sum()),
            "rank_first_pct": float((responses["rank_1st_system"] == system).mean()),
            "most_suspicious_n": int((responses["suspicious_system"] == system).sum()),
            "most_suspicious_pct": float(
                (responses["suspicious_system"] == system).mean()
            ),
        }

    stimulus_rows: list[dict[str, Any]] = []
    for qno, qid in enumerate(answer_key["sampled_qids"], start=1):
        for system, (paper_label, dirname, tag) in SYSTEMS.items():
            files = sorted(
                (
                    PROJECT_ROOT
                    / "data"
                    / "expanded_outputs"
                    / dirname
                ).glob(f"{qid}_*.md")
            )
            if not files:
                continue
            path = files[-1]
            metric = em.evaluate_file(path, tag, frozen_by_id)
            source_text = path.read_text(encoding="utf-8")
            stimulus_rows.append(
                {
                    "qno": qno,
                    "qid": qid,
                    "system": system,
                    "paper_label": paper_label,
                    "source_file": str(path.relative_to(PROJECT_ROOT)),
                    "citation_precision": metric["citation_precision"],
                    "bibliography_match_rate": metric["bibliography_match_rate"],
                    "orphan_rate": metric["orphan_rate"],
                    "total_citations": metric["total_citations"],
                    "bibliography_entries": metric["bibliography_entries"],
                    "source_length_chars": len(source_text),
                    "mean_credibility": float(
                        responses.loc[
                            responses["qno"] == qno, f"score_{system}"
                        ].mean()
                    ),
                    "rank_first_pct": float(
                        (
                            responses.loc[
                                responses["qno"] == qno, "rank_1st_system"
                            ]
                            == system
                        ).mean()
                    ),
                }
            )
    stimuli = pd.DataFrame(stimulus_rows)
    correlations: dict[str, Any] = {}
    for field in (
        "citation_precision",
        "bibliography_match_rate",
        "orphan_rate",
        "source_length_chars",
    ):
        rho, p_s = spearmanr(stimuli[field], stimuli["mean_credibility"])
        r_value, p_p = pearsonr(stimuli[field], stimuli["mean_credibility"])
        correlations[field] = {
            "spearman_rho": float(rho),
            "spearman_p": float(p_s),
            "pearson_r": float(r_value),
            "pearson_p": float(p_p),
        }

    summary = {
        "n_participants": int(responses["participant"].nunique()),
        "n_questions": int(responses["qno"].nunique()),
        "n_response_rows": int(len(responses)),
        "n_ordinal_observations": int(len(long)),
        "model": (
            "Ordinal GEE with participant clusters, exchangeable within-participant "
            "correlation, and question fixed effects"
        ),
        "descriptive": descriptive,
        "ordinal_gee_contrasts": contrasts,
        "stimulus_metric_correlations": correlations,
    }
    return summary, stimulus_rows


def claim_support_audit() -> dict[str, Any]:
    annotator_files = {
        "coder_a": ANNOTATION_DIR / "annotation_sample_50_coder_a.csv",
        "coder_b": ANNOTATION_DIR / "annotation_sample_50_coder_b.csv",
        "coder_c": ANNOTATION_DIR / "annotation_sample_50_coder_c.csv",
    }
    rows_by_annotator: dict[str, list[dict[str, str]]] = {}
    for name, path in annotator_files.items():
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows_by_annotator[name] = list(csv.DictReader(handle))
    ids = [
        [row["pair_id"] for row in rows]
        for rows in rows_by_annotator.values()
    ]
    if any(candidate != ids[0] for candidate in ids[1:]):
        raise RuntimeError("Claim-support annotation files are not row-aligned.")

    base = next(iter(rows_by_annotator.values()))
    majority_labels: list[str] = []
    for index in range(len(base)):
        labels = [
            rows[index]["your_label"].strip().upper()
            for rows in rows_by_annotator.values()
        ]
        majority_labels.append(Counter(labels).most_common(1)[0][0])

    by_method: dict[str, Any] = {}
    for method in sorted({row["method_tag"] for row in base}):
        indices = [
            idx for idx, row in enumerate(base) if row["method_tag"] == method
        ]
        distribution = Counter(majority_labels[idx] for idx in indices)
        by_method[method] = {
            "n": len(indices),
            "majority_label_distribution": dict(distribution),
            "entailed_rate": distribution.get("E", 0) / len(indices),
        }

    kappa = json.loads(
        (ANNOTATION_DIR / "kappa_results.json").read_text(encoding="utf-8")
    )
    return {
        "scope": (
            "Stratified 50-pair audit of citation-bearing claims from M1 and M2a; "
            "not a prevalence estimate and not a CSC audit."
        ),
        "n_pairs": len(base),
        "methods": by_method,
        "majority_distribution": dict(Counter(majority_labels)),
        "fleiss_kappa_3": kappa["fleiss_kappa_3"],
        "pairwise_kappa": kappa["pairwise_kappa"],
        "kappa_majority_vs_auto": kappa["kappa_majority_vs_auto"],
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reanalyse preserved IPM major-revision artifacts without model calls."
    )
    parser.add_argument(
        "--out-dir",
        default=str(
            PROJECT_ROOT
            / "data"
            / "reports"
            / "ipm_major_revision_20260721"
            / "repro"
            / "v3"
        ),
    )
    parser.add_argument(
        "--skip-threshold-sensitivity",
        action="store_true",
        help="Skip the relatively slow 20-cell threshold sensitivity rerun.",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    frozen_by_id = _load_corpus()
    rows_by_config = {
        config: _latest_rows(dirname, tag, frozen_by_id)
        for config, (dirname, tag) in CONFIGS.items()
    }

    per_query, comparisons = paired_query_analysis(rows_by_config)
    release_gate = deterministic_release_gate(rows_by_config)
    human_summary, stimulus_rows = human_study_analysis(frozen_by_id)
    support_summary = claim_support_audit()
    sensitivity = (
        json.loads((out_dir / "major_revision_v3_results.json").read_text(encoding="utf-8")).get(
            "threshold_sensitivity", []
        )
        if args.skip_threshold_sensitivity
        and (out_dir / "major_revision_v3_results.json").exists()
        else threshold_sensitivity(frozen_by_id)
    )

    schema_summary_path = out_dir / "schema_single_agent_run_summary.json"
    schema_summary = (
        json.loads(schema_summary_path.read_text(encoding="utf-8"))
        if schema_summary_path.exists()
        else None
    )
    external_summary_path = out_dir / "out_of_boundary_external_verification_summary.json"
    external_summary = (
        json.loads(external_summary_path.read_text(encoding="utf-8"))
        if external_summary_path.exists()
        else None
    )
    blind_packet_path = out_dir / "title_match_blind_validation" / "README.json"
    blind_packet = (
        json.loads(blind_packet_path.read_text(encoding="utf-8"))
        if blind_packet_path.exists()
        else None
    )

    gate_summary: dict[str, Any] = {}
    for config in CONFIGS:
        subset = [row for row in release_gate if row["config"] == config]
        pass_n = sum(row["release"] == "pass" for row in subset)
        gate_summary[config] = {
            "n": len(subset),
            "pass_n": pass_n,
            "pass_rate": pass_n / len(subset) if subset else None,
            "block_n": len(subset) - pass_n,
        }

    summary = {
        "analysis_version": "2026-07-24-v3",
        "corpus": str(CORPUS_PATH.relative_to(PROJECT_ROOT)),
        "corpus_records": len(frozen_by_id),
        "canonical_queries_per_config": {
            config: len(rows) for config, rows in rows_by_config.items()
        },
        "paired_query_comparisons": comparisons,
        "deterministic_release_gate_summary": gate_summary,
        "human_study": human_summary,
        "claim_support_audit": support_summary,
        "threshold_sensitivity": sensitivity,
        "schema_matched_single_agent": schema_summary,
        "external_bibliography_verification": external_summary,
        "title_match_blind_validation_packet": blind_packet,
        "limitations": [
            "The deterministic release gate is applied to final archived reports; pre-revision LLM reviewer item-level flags were not preserved.",
            "The 50-pair claim-support audit covers M1 and M2a only and does not estimate claim-support coverage.",
            "The 320-pair blinded match/non-match packet has been prepared, but its independent human coding is still pending.",
            "The provider did not expose immutable model snapshot identifiers; alias continuity was confirmed by the authors and the alias, decoding parameters, prompt hashes, and dates were preserved.",
        ],
    }

    _write_csv(out_dir / "per_query_metrics.csv", per_query)
    _write_csv(out_dir / "paired_query_tests.csv", comparisons)
    _write_csv(out_dir / "deterministic_release_gate.csv", release_gate)
    _write_csv(out_dir / "human_stimulus_metrics.csv", stimulus_rows)
    _write_csv(out_dir / "threshold_sensitivity.csv", sensitivity)
    (out_dir / "major_revision_v3_results.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
