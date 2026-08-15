# Review snapshot repair log

This update follows an independent audit of public commit
`5753face6a9d2d0cd4a3fc573537f914928e657c` on 2026-08-15. It does not alter
the preserved manuscript or response letter.

## Repairs

- added `.gitattributes` so text files retain LF line endings across Windows,
  macOS, and Linux checkouts;
- added `--verify-only` to `scripts/build_manifest.py`, allowing reviewers and
  CI to verify the existing manifest without rewriting it;
- replaced a historical human-study CSV containing encoding-damaged,
  non-analytic fields with `analysis_responses_n30.csv`, an anonymized table
  containing exactly the normalized fields consumed by the analysis scripts;
- documented the human-study field dictionary, sanitization boundary, and
  imputation record;
- added a minimal GitHub Actions workflow for manifest, source, JSON, and
  human-study checks;
- regenerated the complete SHA-256 manifest after these changes.
- regenerated the manifest from the committed LF-normalized object set and
  verified it from a fresh Windows checkout.

## Scope

The repaired human-study deposit preserves all variables used in the reported
statistics. It intentionally excludes local questionnaire file names, direct
identifiers, and redundant raw display fields. No reported result was changed.
