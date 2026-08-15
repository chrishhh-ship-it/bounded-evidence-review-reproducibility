# Reproducibility tree — deposit-facing README (2026-08-09)

This file is the current, authoritative guide to this directory for the
purpose of a public or editor-accessible reproducibility deposit
(reviewer items R1-9, R2-4, R3-10). It supersedes the "Evidence boundaries"
section of `README_MAJOR_REVISION_V3.md`, which was written on 2026-07-24
and is now out of date on one important point: it says the 320-pair
title-matching packet has "human labels ... pending." **That is no longer
true** — the audit was completed on 2026-07-30/2026-08-06 (see below). The
rest of `README_MAJOR_REVISION_V3.md` (canonical commands, principal
outputs) is still accurate and should be kept.

Corresponds to manuscript version
`Research_Intelligence_Assistant_IPM_rev_major_v19_20260809.tex/pdf`.

## What is genuinely human-labeled (safe to present as human evidence)

- `title_match_blind_validation/source_title_coder_A_20260806.xlsx`,
  `source_title_coder_B_20260806.xlsx` — the 320-pair title-identity audit
  underlying the manuscript's 97.50%/99.69% result and exact McNemar test.
  These are the files the corresponding author confirmed were completed by
  two people; do not resubmit or re-derive from the still-blank template
  packets (`title_match_blind_packet_coder_A.csv`/`coder_B.csv`), which were
  an earlier, unused blind-coding attempt and remain empty.
- `semantic_arl_v2_3/source_coder_A_annotated_20260806.csv`,
  `source_coder_B_annotated_20260806.xlsx` — the 173-item matched semantic
  audit (169/173 pre-adjudication agreement, κ=.955), plus
  `v23_csp_adjudicated_gold_20260806.csv` and
  `v23_csp_adjudication_report_20260806.md` documenting the 4 adjudicated
  disagreements.

## What is NOT human-labeled — must not be presented as such

- `model_reference_20260728/` and `provisional_reviewer_reference_keys_20260730/`
  contain **automated, rule-generated** reference labels. Every row's
  `coder_notes` field is stamped `MODEL_REFERENCE_ONLY; ... not a human gold
  label`. These exist only as internal diagnostic scaffolding from an
  earlier stage of the analysis. If this directory is deposited as-is,
  anyone browsing it could mistake these for additional human annotation —
  they should either be excluded from the deposited archive, or kept but
  clearly labeled as automated/diagnostic-only in whatever top-level index
  the deposit uses.

## Housekeeping: empty directories

The following four subdirectories are empty leftovers from abandoned
intermediate analysis attempts and contain no files:
`title_match_verified_20260730/`, `title_match_two_coder_merged_20260730/`,
`title_match_verified_vs_corrected_second_coder_20260730/`,
`title_match_verified_vs_provisional_20260730/`. Exclude them when building
the deposit archive (they add nothing and would read as broken/missing data
to a reviewer browsing the repository).

## Manifest

`MANIFEST_SHA256_20260809.txt` in this directory lists SHA-256 checksums and
byte sizes for all 430 files currently under `repro/v3/` (generated
2026-08-09, this session). This is a full re-hash independent of the older
`artifact_manifest_sha256.json`, which only covers the v3-era subset of
files and predates the later human-coding and semantic-audit source files.
Use `MANIFEST_SHA256_20260809.txt` as the authoritative, complete manifest
for the deposit.

## What still requires the author's decision

Unchanged from `IPM_v13_REPRODUCIBILITY_DEPOSIT_README_20260806.md`:
platform choice (anonymized GitHub, OSF, Zenodo, or editor-only archive),
proprietary-source handling (Scopus/CNKI/Wanfang as IDs/hashes only), and
executing the actual account creation and upload — none of which this
analysis performs autonomously.
