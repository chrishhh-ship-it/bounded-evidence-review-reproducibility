# IPM Major Revision v3 Reproducibility Pack

## Scope

This folder supports the v3 major-revision analyses. It reproduces preserved-output evaluation, paired query statistics, deterministic release-gate decisions, human-study reanalysis, the limited claim-support audit summary, external bibliography verification, threshold sensitivity, and the schema-matched single-agent baseline.

It does **not** claim byte-identical regeneration of historical API outputs. The provider did not expose immutable model snapshot identifiers. The authors confirmed that the same `deepseek-chat` alias was used; aliases, dates, decoding parameters, per-query prompt hashes, evidence sidecars, and generated outputs are preserved.

## Canonical commands

Run from the project root with Python 3.10:

```powershell
python scripts/analyze_ipm_major_revision_v3.py
python scripts/verify_ipm_out_of_boundary_refs.py
python scripts/build_title_match_blind_validation.py --n 320 --seed 20260724
python scripts/analyze_schema_baseline_v3.py
```

The paid/API-dependent schema baseline was generated with:

```powershell
python scripts/run_schema_matched_single_agent.py `
  --provider deepseek `
  --model deepseek-chat `
  --output-dir data/expanded_outputs/schema_single_agent_v1 `
  --start 1 --end 251
```

Do not rerun the paid command unless the author explicitly authorises cost and model-snapshot drift is accepted.

Compile the revised manuscript:

```powershell
cd data/reports
latexmk -xelatex -interaction=nonstopmode -halt-on-error `
  Research_Intelligence_Assistant_IPM_rev_major_v3_20260724.tex
```

## Principal outputs

- `major_revision_v3_results.json`: integrated machine-readable summary.
- `per_query_metrics.csv`: M1/M2a/M2b/M2c query-level metrics.
- `paired_query_tests.csv`: paired Wilcoxon, BCa confidence intervals, BH-FDR.
- `deterministic_release_gate.csv`: release decisions and rejection reasons.
- `schema_single_agent_per_query.csv`: B0 query-level structural metrics and cost.
- `schema_single_agent_run_summary.json`: B0 model alias, parameters, prompt hashes, pass rate, timing.
- `out_of_boundary_external_verification.csv`: registry audit of unique boundary-rejected entries.
- `human_stimulus_metrics.csv`: structural metrics linked to the 30 user-study stimuli.
- `title_match_blind_validation/`: blinded 320-pair packet; **human labels are pending**.
- `artifact_manifest_sha256.json`: file sizes and SHA-256 checksums.

## Evidence boundaries

1. ICP/ECP and the gate measure structural resolution and evidence-boundary membership.
2. The 50-pair audit is a limited pooled semantic check, not a population CSC estimate.
3. Registry resolution outside \(E_q\) establishes probable publication existence, not claim support.
4. Human ratings do not show a statistically reliable method advantage.
5. The 0.72 title threshold remains heuristic until the blinded packet receives two independent human label sets.
