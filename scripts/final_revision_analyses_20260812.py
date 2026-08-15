from __future__ import annotations

import csv
import json
import math
import re
import sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import norm, pearsonr, spearmanr


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import evaluate_metrics as em  # noqa: E402


OUT_DIR = (
    PROJECT_ROOT
    / "data/reports/ipm_major_revision_20260721/repro/final_revision_20260812"
)
TITLE_GOLD = (
    PROJECT_ROOT
    / "data/reports/ipm_major_revision_20260721/repro/v3/"
    / "title_match_single_vs_arl_20260730/first_independent_coding_20260730/"
    / "TITLE_MATCH_FIRST_INDEPENDENT_BASELINE_20260730.csv"
)
TITLE_DETAILS = (
    PROJECT_ROOT
    / "data/reports/ipm_major_revision_20260721/repro/v3/"
    / "title_match_single_vs_arl_20260730/full_20260730_034303/"
    / "title_match_single_vs_arl_results.csv"
)
CORPUS_PATH = PROJECT_ROOT / "data/frozen_corpus_multidomain_v1.json"
USER_STUDY_PATH = PROJECT_ROOT / "data/user_study/analysis_responses_n30.csv"
ANSWER_KEY_PATH = PROJECT_ROOT / "data/user_study/answer_key.json"
THRESHOLDS = (0.60, 0.65, 0.70, 0.72, 0.75, 0.80, 0.85, 0.90, 0.95)
CONFIGS = {
    "M1": ("method1", "method1"),
    "M2a": ("method2a", "method2"),
    "M2b": ("method2b", "method2_same_model"),
    "M2c": ("method2d", "method2c"),
}
SYSTEM_LABELS = {"A": "M1", "B": "M2b", "C": "M2a"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def title_score(reference: str, candidate: str) -> float:
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
    sequence_ratio = SequenceMatcher(None, reference_norm, candidate_norm).ratio()
    return max(token_ratio, sequence_ratio)


def title_metrics(rows: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
    tp = fp = fn = tn = 0
    for row in rows:
        predicted = row["score"] >= threshold
        actual = row["gold_label"] == "match"
        if predicted and actual:
            tp += 1
        elif predicted:
            fp += 1
        elif actual:
            fn += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "threshold": threshold,
        "n": len(rows),
        "predicted_match": tp + fp,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": (tp + tn) / len(rows),
    }


def analyze_title_thresholds() -> dict[str, Any]:
    gold = {row["pair_id"]: row for row in read_csv(TITLE_GOLD)}
    details = {row["pair_id"]: row for row in read_csv(TITLE_DETAILS)}
    if len(gold) != 320 or set(gold) != set(details):
        raise RuntimeError("Title-gold and title-detail pair sets do not align")
    rows: list[dict[str, Any]] = []
    for pair_id in sorted(gold):
        detail = details[pair_id]
        text = f"{detail['reference_string']} {detail['candidate_evidence_title']}"
        rows.append(
            {
                "pair_id": pair_id,
                "query_id": detail["query_id"],
                "domain": detail["domain"],
                "language_group": (
                    "Chinese-present" if re.search(r"[\u4e00-\u9fff]", text) else "English/Latin"
                ),
                "reference_string": detail["reference_string"],
                "candidate_evidence_title": detail["candidate_evidence_title"],
                "gold_label": gold[pair_id]["independent_human_label"],
                "single_agent_label": gold[pair_id]["single_agent_label"],
                "arl_label": gold[pair_id]["arl_label"],
                "score": title_score(
                    detail["reference_string"], detail["candidate_evidence_title"]
                ),
            }
        )
    overall = [title_metrics(rows, threshold) for threshold in THRESHOLDS]
    grouped: list[dict[str, Any]] = []
    for group_type, key in (("language", "language_group"), ("domain", "domain")):
        for group in sorted({row[key] for row in rows}):
            subset = [row for row in rows if row[key] == group]
            for threshold in THRESHOLDS:
                grouped.append(
                    {
                        "group_type": group_type,
                        "group": group,
                        **title_metrics(subset, threshold),
                    }
                )
    write_csv(OUT_DIR / "title_threshold_pair_scores.csv", rows)
    write_csv(
        OUT_DIR / "title_threshold_metrics.csv",
        [{"group_type": "overall", "group": "all", **row} for row in overall]
        + grouped,
    )
    result = {
        "source_gold": str(TITLE_GOLD.relative_to(PROJECT_ROOT)),
        "source_details": str(TITLE_DETAILS.relative_to(PROJECT_ROOT)),
        "n": len(rows),
        "gold_distribution": dict(Counter(row["gold_label"] for row in rows)),
        "overall": overall,
        "high_score_nonmatches": sum(
            row["score"] >= 0.90 and row["gold_label"] == "nonmatch" for row in rows
        ),
        "boundary": (
            "Sensitivity analysis on the final independent human benchmark; it does not "
            "establish a universal optimal threshold."
        ),
    }
    return result


def percentile_summary(values: list[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    return {
        "mean": float(np.mean(array)),
        "sd": float(np.std(array, ddof=1)) if len(array) > 1 else 0.0,
        "median": float(np.median(array)),
        "q1": float(np.quantile(array, 0.25)),
        "q3": float(np.quantile(array, 0.75)),
        "min": float(np.min(array)),
        "max": float(np.max(array)),
    }


def citation_occurrence_count(body: str) -> int:
    """Count citation mentions, preserving repeated citations and expanded ranges."""
    count = 0
    for match in em._BRACKET_BLOCK_RE.finditer(body):
        count += len(em._expand_citation_block(match.group(1)))
    count += sum(1 for _ in em._WENXIAN_CITE_RE.finditer(body))
    return count


def analyze_deduplicated_outputs() -> dict[str, Any]:
    corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    frozen_by_id = {em._paper_id(row): row for row in corpus}
    summaries: list[dict[str, Any]] = []
    selected_rows: list[dict[str, Any]] = []
    for config, (dirname, tag) in CONFIGS.items():
        directory = PROJECT_ROOT / "data/expanded_outputs" / dirname
        all_files = list(directory.glob("*.md"))
        selected = em._select_latest_per_query(all_files)
        metrics: list[dict[str, Any]] = []
        for path in selected.values():
            parsed = em._parse_result_stem(path.stem)
            if not parsed:
                continue
            row = em.evaluate_file(path, tag, frozen_by_id)
            text = path.read_text(encoding="utf-8")
            body, _ = em._split_body_bib(text)
            occurrence_count = citation_occurrence_count(body)
            bibliography_entries = row["bibliography_entries"]
            row.update(
                {
                    "config": config,
                    "query_id": parsed[0],
                    "file": str(path.relative_to(PROJECT_ROOT)),
                    "output_length_chars": len(body),
                    "citation_occurrences": occurrence_count,
                    "citation_density_per_bib": (
                        occurrence_count / bibliography_entries
                        if bibliography_entries
                        else None
                    ),
                }
            )
            metrics.append(row)
            selected_rows.append(row)
        summaries.append(
            {
                "config": config,
                "raw_files": len(all_files),
                "deduplicated_queries": len(metrics),
                "bibliography_entries": percentile_summary(
                    [row["bibliography_entries"] for row in metrics]
                ),
                "citations_per_output": percentile_summary(
                    [row["citation_occurrences"] for row in metrics]
                ),
                "output_length_chars": percentile_summary(
                    [row["output_length_chars"] for row in metrics]
                ),
                "citation_density_per_bib": percentile_summary(
                    [
                        row["citation_density_per_bib"]
                        for row in metrics
                        if row["citation_density_per_bib"] is not None
                    ]
                ),
            }
        )
    write_csv(OUT_DIR / "deduplicated_output_rows.csv", selected_rows)
    flat_rows: list[dict[str, Any]] = []
    for summary in summaries:
        row: dict[str, Any] = {
            "config": summary["config"],
            "raw_files": summary["raw_files"],
            "deduplicated_queries": summary["deduplicated_queries"],
        }
        for metric in (
            "bibliography_entries",
            "citations_per_output",
            "output_length_chars",
            "citation_density_per_bib",
        ):
            for statistic, value in summary[metric].items():
                row[f"{metric}_{statistic}"] = value
        flat_rows.append(row)
    write_csv(OUT_DIR / "deduplicated_output_summary.csv", flat_rows)
    return {
        "selection_rule": (
            "For each query/configuration, retain the latest timestamped preserved Markdown "
            "output; retry and regeneration files remain archived but are not independent rows."
        ),
        "summaries": summaries,
    }


def p_two_sided(z_value: float) -> float:
    return float(2 * norm.sf(abs(z_value)))


def fit_ordinal_gee(responses: pd.DataFrame) -> dict[str, Any]:
    import statsmodels.api as sm

    long = responses.melt(
        id_vars=["participant", "qno"],
        value_vars=["score_A", "score_B", "score_C"],
        var_name="system",
        value_name="score",
    ).dropna(subset=["score"])
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
    exog = pd.concat([exog.reset_index(drop=True), question_dummies.reset_index(drop=True)], axis=1)
    model = sm.OrdinalGEE(
        long["score"].astype(int),
        exog,
        long["participant"],
        cov_struct=sm.cov_struct.Exchangeable(),
    )
    fitted = model.fit(maxiter=200)
    covariance = fitted.cov_params()
    contrasts: list[dict[str, Any]] = []
    for label, left, right in (
        ("M2b vs M1", "sys_B", None),
        ("M2a vs M1", "sys_C", None),
        ("M2a vs M2b", "sys_C", "sys_B"),
    ):
        if right is None:
            estimate = float(fitted.params[left])
            variance = float(covariance.loc[left, left])
        else:
            estimate = float(fitted.params[left] - fitted.params[right])
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
                "p": p_two_sided(z_value),
                "ci95_low": math.exp(estimate - 1.96 * se),
                "ci95_high": math.exp(estimate + 1.96 * se),
            }
        )
    descriptive = {
        SYSTEM_LABELS[system]: {
            "n": int(responses[f"score_{system}"].notna().sum()),
            "mean": float(responses[f"score_{system}"].mean()),
            "sd": float(responses[f"score_{system}"].std(ddof=1)),
        }
        for system in ("A", "B", "C")
    }
    return {
        "n_response_rows": int(len(responses)),
        "n_ordinal_observations": int(len(long)),
        "n_participants": int(responses["participant"].nunique()),
        "descriptive": descriptive,
        "contrasts": contrasts,
    }


def stimulus_correlations(responses: pd.DataFrame) -> dict[str, Any]:
    answer_key = json.loads(ANSWER_KEY_PATH.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    directory_map = {
        "A": ("method1", "method1"),
        "B": ("method2b", "method2_same_model"),
        "C": ("method2a", "method2"),
    }
    corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    frozen_by_id = {em._paper_id(row): row for row in corpus}
    for qno, qid in enumerate(answer_key["sampled_qids"], start=1):
        for system, (dirname, tag) in directory_map.items():
            files = sorted((PROJECT_ROOT / "data/expanded_outputs" / dirname).glob(f"{qid}_*.md"))
            if not files:
                continue
            path = files[-1]
            metric = em.evaluate_file(path, tag, frozen_by_id)
            rows.append(
                {
                    "citation_precision": metric["citation_precision"],
                    "orphan_rate": metric["orphan_rate"],
                    "source_length_chars": len(path.read_text(encoding="utf-8")),
                    "mean_credibility": float(
                        responses.loc[responses["qno"] == qno, f"score_{system}"].mean()
                    ),
                }
            )
    frame = pd.DataFrame(rows)
    result: dict[str, Any] = {"n_stimuli": int(len(frame))}
    for field in ("citation_precision", "orphan_rate", "source_length_chars"):
        rho, p_s = spearmanr(frame[field], frame["mean_credibility"])
        r_value, p_p = pearsonr(frame[field], frame["mean_credibility"])
        result[field] = {
            "spearman_rho": float(rho),
            "spearman_p": float(p_s),
            "pearson_r": float(r_value),
            "pearson_p": float(p_p),
        }
    return result


def analyze_human_sensitivity() -> dict[str, Any]:
    imputed = pd.read_csv(USER_STUDY_PATH)
    excluded = {("P10", 8), ("P26", 8)}
    complete = imputed[
        ~imputed.apply(lambda row: (row["participant"], int(row["qno"])) in excluded, axis=1)
    ].copy()
    if len(complete) != 298:
        raise RuntimeError(f"Expected 298 complete-case rows, found {len(complete)}")
    result = {
        "primary_complete_case": {
            **fit_ordinal_gee(complete),
            "stimulus_metric_correlations": stimulus_correlations(complete),
        },
        "sensitivity_imputed": {
            **fit_ordinal_gee(imputed),
            "stimulus_metric_correlations": stimulus_correlations(imputed),
        },
        "excluded_rows": ["P10_Q08", "P26_Q08"],
        "interpretation": (
            "Complete-case results are primary; prespecified participant-mean imputation is "
            "reported only as a sensitivity analysis."
        ),
    }
    comparison_rows: list[dict[str, Any]] = []
    for label, analysis in (
        ("complete_case_primary", result["primary_complete_case"]),
        ("imputed_sensitivity", result["sensitivity_imputed"]),
    ):
        for contrast in analysis["contrasts"]:
            comparison_rows.append(
                {
                    "analysis": label,
                    "n_response_rows": analysis["n_response_rows"],
                    "n_ordinal_observations": analysis["n_ordinal_observations"],
                    **contrast,
                }
            )
    write_csv(OUT_DIR / "human_complete_case_vs_imputed.csv", comparison_rows)
    return result


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "title_threshold": analyze_title_thresholds(),
        "deduplicated_output_distributions": analyze_deduplicated_outputs(),
        "human_study_sensitivity": analyze_human_sensitivity(),
    }
    (OUT_DIR / "FINAL_REVISION_ANALYSES_20260812.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
