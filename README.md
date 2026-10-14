# Anonymous reproducibility package

Version: 2026-10-14 (v4, R2)

This repository contains the anonymized code, benchmark data, preserved outputs,
and analysis records for a manuscript under double-anonymized review. It now
includes the R2 generation protocols, prompt inventory, public-corpus and
English/bilingual outputs, numeric-audit records, and provenance checks for the
1,004 expanded reports.

Start with [the R2 addendum](README_R2_ADDENDUM.md) for the new materials and
commands, [the prompt inventory](PROTOCOL_PROMPTS.md) for prompt provenance,
and [the reproduction guide](README_REPRODUCE.md) for the earlier analyses.
[The package overview](README_ANONYMOUS_PACKAGE.md) describes the deposit scope;
[data sources and licenses](DATA_SOURCES_AND_LICENSES.md) describes reuse terms.

## Verify and reproduce

Use Python 3.10 or newer. Verify the downloaded files before running analyses:

```bash
python scripts/build_manifest.py --verify-only
```

For analyses requiring scientific Python packages:

```bash
python -m pip install -r requirements-analysis.txt
```

The R2 provenance checks use only the standard library:

```bash
python data/reports/r2_provenance_audit_20261014/export_pools_and_gate_reasons.py
python data/reports/r2_provenance_audit_20261014/bib_line_provenance_check.py
python data/reports/r2_provenance_audit_20261014/screened_recover.py screened_recover_rerun.json
```

Expected results include 1,004 reports, 7,984 bibliography entries, 7,815 exact
code-rendered lines after Unicode/whitespace normalization, and 875 reports with
all eight screened records identified. The addendum gives the gate counts and
explains which commands write output files.

## Reproduction scope and source provenance

The supplied ZIP is recorded in
[the import record](provenance/IMPORT_V4_R2_20261014.json), including its SHA-256.
Its original manifest and summary are retained under `provenance/source_package_v4/`.
The root manifest covers this GitHub deposit after anonymous-data handling and
preservation of deposited line endings. The public human-study CSV retains all 300 rows
and all 10 analysis fields while excluding questionnaire filenames and other
identifying fields.

The analyses operate on preserved outputs. API-backed generation requires the
user's own credentials and is not expected to regenerate byte-identical text.
Historical generation and numeric-audit scripts may require external workflow
components or manuscript/full-text inputs; see the R2 addendum for limitations.
No new provider calls are required for the R2 provenance checks.
