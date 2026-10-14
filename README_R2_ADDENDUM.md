# R2 addendum (2026-10-14, package v4)

This version extends the v3 package (2026-08-13) with the generation scripts, outputs and audit files cited in the second revision. The GitHub deposit incorporates the supplied v4 archive with the public-repository adaptations described below. `MANIFEST_SHA256.csv` covers the deposited files except itself.

## Added in v4

1. **Prompts and role instructions**: `PROTOCOL_PROMPTS.md` lists every prompt referred to in Sections 3.1–3.2 and the script that contains it, including the structural protocol instructions and the instructions of the archived M2 runs.
2. **Generation scripts** (`historical_generation_protocols/`): the expanded-benchmark runner, the M3/M4 controls, Baselines A/B, the query generator, the AutoSurvey runners, the public-corpus, English and bilingual checks, the title-identity audit, the semantic V0–V2 audit, the reviewer-versus-gate run and the human-study material builder.
3. **Analysis scripts** (`scripts/`): title-threshold sensitivity, the local NLI audit, ALCE scoring and significance tests, and SciFact scoring.
4. **Outputs**: `data/alce_outputs/` (public-corpus check), `data/english_benchmark/`, `data/bilingual_exp/`, and the benchmark query files.
5. **Numeric audit** (`data/reports/r2_numeric_audit_20260928/`): per-report rows for every condition, the numeric-cell ledger for the tables, the corrected NLI grouping, full-text availability checks and runtime records.
6. **Provenance audit** (`data/reports/r2_provenance_audit_20261014/`), replacing the files previously described as available on request:
   - `pools_and_gate_reasons.json`: for each of the 1,004 expanded reports, the reconstructed 15-candidate pool, the archived set A_{c,q}, and gate reasons against A_{c,q}, against the 15-candidate pool, and for the reference-set-independent checks (export script included);
   - `bib_line_provenance_check.*`, `all_entries_title_check.*`, `provenance_title_detail.*`: the Writer-prompt-line and title-level traces of all 7,984 bibliography entries;
   - `screened_recover.*`: identification of the eight screened records from each report's bibliography (875 of 1,004 reports);
   - `recompute_provenance.py`: an independent recomputation of the provenance and gate counts reported in Section 3.

## Reproducing the R2 counts

From the package root, with the v3 requirements installed:

```
python data/reports/r2_provenance_audit_20261014/export_pools_and_gate_reasons.py
python data/reports/r2_provenance_audit_20261014/bib_line_provenance_check.py
python data/reports/r2_provenance_audit_20261014/screened_recover.py screened_recover_rerun.json
```

Expected values: gate pass against A_{c,q} 15/20/17/0 and against the 15-candidate pool 244/247/242/14 (M1/M2a/M2b/M2c); reference-set-independent blocks for M1 7; 7,984 bibliography entries, 7,815 exact code-rendered lines after Unicode and whitespace normalisation; 875 reports with all eight screened records identified.

API-backed generation is not expected to reproduce byte-identical text; the analyses run on the preserved outputs.

## Anonymisation in v4

Coder file names and a contact string in a request header were replaced by neutral labels in the supplied archive. The source-package summary, including its `redacted_in_v4` list, is retained under `provenance/source_package_v4/`. Author lists of retrieved literature records in the frozen corpora are bibliographic data and are unchanged.

## Public repository adaptations

The original ZIP is identified by its SHA-256 in
`provenance/IMPORT_V4_R2_20261014.json`. Its original checksum manifest and
summary are retained under `provenance/source_package_v4/`; they describe the
supplied archive, not the adapted GitHub checkout.

The public deposit keeps the existing repository licenses, helper modules and
anonymous human-study table. `raw_responses_n30.csv` is an alias of
`analysis_responses_n30.csv`: all 300 rows and all 10 analysis fields match the
supplied archive exactly. Original questionnaire file names and unused display
fields are excluded. Workstation path prefixes and coder names use neutral
labels. Git preserves deposited line endings, and the root manifest is regenerated
for these deposited bytes. No analysis values are changed by these adaptations.

Run `python scripts/build_manifest.py --verify-only` on a fresh checkout before
recomputing outputs. The first two R2 commands above write their JSON results
beside the scripts; the third writes to the specified output path. Use a copy of
the checkout when retaining the deposited files unchanged is necessary.

## Scope of executable reproduction

The three R2 provenance commands above recompute the archived counts locally
using Python's standard library and require no API credentials.

The scripts in `data/reports/r2_numeric_audit_20260928/` are historical audit
snapshots. Several refer to the original audit workspace, manuscript
`source/main.tex`, annotation files, or full-text files that are not included in
this deposit. Their archived JSON/CSV results and numeric-cell ledger are
included; those scripts are not standalone reproduction entrypoints here.
The complete historical `scripts/analyze_ipm_major_revision_v3.py` run also
requires the original annotation files, which are not included in this deposit.
The title-identity generation scripts likewise refer to an external verified
coding file. Historical generation also depends on provider access and other
original workflow components. These limitations do not apply to the local R2
provenance commands above or the preserved-output structural evaluator.
