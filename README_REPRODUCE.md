# Reproducibility Guide

Updated: 2026-08-15

This guide lists the copy-paste commands used to reproduce the reported
structural metrics from preserved system outputs. `scripts/evaluate_metrics.py`
requires an explicit `--corpus` argument so that pilot and expanded benchmark
corpora cannot be mixed silently.

## Environment and scope

From the repository root, install the minimum analysis dependencies:

```bash
python -m pip install -r requirements.txt
```

For the exact versions used in the verification run, see
`requirements-lock.txt`.

The commands below reproduce analyses from preserved outputs. They do not
promise byte-identical regeneration of hosted-model responses. Scripts that
call model providers require the user's own credentials and may be affected by
provider-side model updates.

**Windows checkout note.** Several files under `data/reports/.../repro/v3/`
have long nested paths. Git for Windows disables long-path support by default,
so a plain `git clone` can silently fail to check out some of these files
(you may see `Filename too long` errors during clone, or a later
`build_manifest.py --verify-only` failure that looks like a missing file but
is actually a failed local checkout). Before cloning on Windows, run:

```bash
git config --global core.longpaths true
```

Using a short checkout path such as `C:\ipmrep` further reduces the risk but
is not a substitute for the setting above, since the long segments live
inside the repository's own directory structure, not just in the checkout
root.

## Required Files

Core corpora:

- Pilot MAS corpus: `data/topic_runs/multi_agent_intel_service_20260410_114059/retrieved_papers_wave3.json`
- Expanded multi-domain corpus: `data/frozen_corpus_multidomain_v1.json`

Benchmark query definitions:

- Expanded 251-query benchmark: `data/benchmarks/benchmark_all_queries.json`
- Independent 50-query English stress test (EN01--EN50): `data/benchmarks/english_queries_benchmark.json`

The English file is a separate, purpose-built 50-query English stress-test set
that is not part of the 251-query expanded benchmark. It has no exact
query-string overlap with `benchmark_all_queries.json` and is not an English
subset of that benchmark.

Run manifest and checksums:

- `data/manifests/run_manifest.json`
- `data/topic_runs/multi_agent_intel_service_20260410_114059/retrieved_papers_wave3.json.sha256`
- `data/frozen_corpus_multidomain_v1.json.sha256`

Human pilot:

- `data/user_study/analysis_responses_n30.csv`
- `data/user_study/README.md`
- `data/user_study/imputation_log.json`
- `scripts/analyze_user_study.py`

## P0 Commands: Expanded Multi-Domain Benchmark

These commands reproduce the main expanded benchmark table over 251 queries and
the 3,011-paper frozen corpus.

### Method 1

```bash
python scripts/evaluate_metrics.py --corpus data/frozen_corpus_multidomain_v1.json --dir data/expanded_outputs/method1 --tag method1 --query-ids Q01-Q251
```

Expected: `n=251`, `CP=61.8%`, `BMR=61.9%`, `CUR/Orphan=38.6%`, `AbsCov=94.9%`.

### Method 2a: Cross-Model ARL

```bash
python scripts/evaluate_metrics.py --corpus data/frozen_corpus_multidomain_v1.json --dir data/expanded_outputs/method2a --tag method2 --query-ids Q01-Q251
```

Expected: `n=251`, `CP=62.4%`, `BMR=62.4%`, `CUR/Orphan=37.7%`, `AbsCov=94.9%`.

### Method 2b: Same-Model ARL

```bash
python scripts/evaluate_metrics.py --corpus data/frozen_corpus_multidomain_v1.json --dir data/expanded_outputs/method2b --tag method2_same_model --query-ids Q01-Q251
```

Expected: `n=251`, `CP=62.7%`, `BMR=62.6%`, `CUR/Orphan=37.9%`, `AbsCov=94.9%`.

### Method 2c: Weak-Capacity Reviewer

```bash
python scripts/evaluate_metrics.py --corpus data/frozen_corpus_multidomain_v1.json --dir data/expanded_outputs/method2d --tag method2c --query-ids Q01-Q251
```

Expected: `n=251`, `CP=61.5%`, `BMR=61.4%`, `CUR/Orphan=72.0%`, `AbsCov=94.9%`.

## Pilot Commands

Pilot and extended MAS-domain runs use the 513-paper wave3 corpus.

### Baseline A

```bash
python scripts/evaluate_metrics.py --corpus data/topic_runs/multi_agent_intel_service_20260410_114059/retrieved_papers_wave3.json --dir data/baselines --tag baseline_a --query-ids Q01-Q30
```

### Baseline B

```bash
python scripts/evaluate_metrics.py --corpus data/topic_runs/multi_agent_intel_service_20260410_114059/retrieved_papers_wave3.json --dir data/baselines --tag baseline_b --query-ids Q01-Q30
```

### Method 1 Pilot/Extended Outputs

```bash
python scripts/evaluate_metrics.py --corpus data/topic_runs/multi_agent_intel_service_20260410_114059/retrieved_papers_wave3.json --dir data/method1_outputs --tag method1 --query-ids Q01-Q30
```

### Method 2a Pilot/Extended Outputs

```bash
python scripts/evaluate_metrics.py --corpus data/topic_runs/multi_agent_intel_service_20260410_114059/retrieved_papers_wave3.json --dir data/method2_outputs --tag method2 --query-ids Q01-Q30
```

### Method 2b Pilot/Extended Outputs

```bash
python scripts/evaluate_metrics.py --corpus data/topic_runs/multi_agent_intel_service_20260410_114059/retrieved_papers_wave3.json --dir data/method2_same_model_outputs --tag method2_same_model --query-ids Q01-Q30
```

### Self-Critique Control

```bash
python scripts/evaluate_metrics.py --corpus data/topic_runs/multi_agent_intel_service_20260410_114059/retrieved_papers_wave3.json --dir data/method3_outputs --tag method3 --query-ids Q01-Q60
```

### CoT Verification Control

```bash
python scripts/evaluate_metrics.py --corpus data/topic_runs/multi_agent_intel_service_20260410_114059/retrieved_papers_wave3.json --dir data/method4_outputs --tag method4 --query-ids Q01-Q60
```

## AutoSurvey Comparison

### Controlled AutoSurvey

```bash
python scripts/evaluate_metrics.py --corpus data/topic_runs/multi_agent_intel_service_20260410_114059/retrieved_papers_wave3.json --dir data/autosurvey_outputs --tag autosurvey --query-ids Q01-Q30
```

### Native AutoSurvey With CHECK_CITATION

```bash
python scripts/evaluate_metrics.py --corpus data/topic_runs/multi_agent_intel_service_20260410_114059/retrieved_papers_wave3.json --dir data/autosurvey_native_outputs --tag autosurvey_native --query-ids Q01-Q30
```

### Native AutoSurvey Without CHECK_CITATION

```bash
python scripts/evaluate_metrics.py --corpus data/topic_runs/multi_agent_intel_service_20260410_114059/retrieved_papers_wave3.json --dir data/autosurvey_native_outputs --tag autosurvey_native_nocheck --query-ids Q01-Q05
```

## Per-Category and Per-Domain Breakdowns

These commands reproduce the secondary breakdown tables. Both rely on
``scripts/evaluate_metrics.py`` and only call its public entry points.

### Per-Category Pilot Breakdown (Table 7, n=30 MAS pilot)

```bash
python scripts/analyze_pilot_per_category.py
```

Expected (M1 ICP / Orphan, M2a ICP / Orphan per category):

- competitive_intel. (n=2): M1 `43.8% / 56.2%`, M2a `100.0% / 0.0%`
- cost_efficiency (n=2): M1 `100.0% / 6.2%`, M2a `100.0% / 0.0%`
- evaluation (n=4): M1 `0.0% / 100.0%`, M2a `100.0% / 0.0%`
- full_text (n=3): M1 `37.5% / 62.5%`, M2a `100.0% / 0.0%`
- retrieval (n=4): M1 `40.6% / 59.4%`, M2a `100.0% / 0.0%`
- benchmark (n=4): M1 `100.0% / 0.0%`, M2a `100.0% / 0.0%`
- knowledge_service (n=2): M1 `0.0% / 50.0%`, M2a `100.0% / 0.0%`
- writing (n=5): M1 `80.0% / 20.0%`, M2a `100.0% / 2.5%`
- agent_roles (n=4): M1 `75.0% / 25.0%`, M2a `100.0% / 0.0%`

### Per-Domain Expanded Breakdown (Table 12, n=251 expanded benchmark)

```bash
python scripts/analyze_expanded_breakdown.py --benchmark data/benchmarks/benchmark_all_queries.json --corpus data/frozen_corpus_multidomain_v1.json --out data/reports/expanded_domain_breakdown_20260416.json
```

Expected: per-domain CP for M1/M2a/M2b/M2d (= paper M2c) reproduces the four
corresponding rows of Table 12 (e.g., M1 MAS `65.9%`, DH `61.4%`, Bio `57.9%`,
Climate `56.9%`).

## Human Pilot

The anonymized, analysis-ready 30-participant file is
`data/user_study/analysis_responses_n30.csv`. Direct identifiers, source-file
names, and redundant raw display fields are not deposited. The retained fields
are the exact inputs used by the analysis scripts; see
`data/user_study/README.md` for the data dictionary and sanitization boundary.
The analysis entrypoint is read-only by default.

```bash
python scripts/analyze_user_study.py
```

Expected descriptive values:

- M2a: rank-first `41.7%`, average rank `1.86`, mean score `4.27`, SD `1.40`, most suspicious `26.7%`
- M1: rank-first `29.7%`, average rank `2.10`, mean score `3.94`, SD `1.40`, most suspicious `39.3%`
- M2b: rank-first `28.7%`, average rank `2.04`, mean score `4.12`, SD `1.44`, most suspicious `34.0%`

## Notes

- `SC` / section completeness is parser-sensitive and is retained only as a
  secondary descriptive signal. The main reproducible structural claims should
  rely on `CP`, `BMR`, `CUR/Orphan`, and `AbsCov`.
- End-to-end API regeneration is not expected to be byte-identical because the
  LLM calls were not seeded. The preserved markdown/JSON outputs are the
  reproducible evaluation objects.

## Verify the deposited snapshot without modifying it

```bash
python scripts/build_manifest.py --verify-only
```

The repository enforces LF line endings through `.gitattributes`, so the same
byte-level manifest can be verified on Windows, macOS, and Linux checkouts.
