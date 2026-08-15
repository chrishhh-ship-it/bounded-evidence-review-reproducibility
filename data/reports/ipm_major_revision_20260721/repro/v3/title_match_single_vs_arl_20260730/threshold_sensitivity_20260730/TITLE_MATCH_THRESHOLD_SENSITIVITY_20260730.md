# Title-match threshold sensitivity analysis (2026-07-30)

Source: `data/reports/ipm_major_revision_20260721/repro/v3/title_match_single_vs_arl_20260730/final_gold_v1_20260730/title_match_final_gold_v1.csv`
Unit: 320 final human-gold reference/candidate pairs.

## Overall results

| threshold | predicted match | TP | FP | FN | TN | precision | recall | F1 | accuracy |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.60 | 263 | 152 | 111 | 0 | 57 | 0.578 | 1.000 | 0.733 | 0.653 |
| 0.65 | 231 | 152 | 79 | 0 | 89 | 0.658 | 1.000 | 0.794 | 0.753 |
| 0.70 | 203 | 152 | 51 | 0 | 117 | 0.749 | 1.000 | 0.856 | 0.841 |
| 0.72 | 197 | 152 | 45 | 0 | 123 | 0.772 | 1.000 | 0.871 | 0.859 |
| 0.75 | 197 | 152 | 45 | 0 | 123 | 0.772 | 1.000 | 0.871 | 0.859 |
| 0.80 | 180 | 152 | 28 | 0 | 140 | 0.844 | 1.000 | 0.916 | 0.912 |
| 0.85 | 164 | 152 | 12 | 0 | 156 | 0.927 | 1.000 | 0.962 | 0.963 |
| 0.90 | 160 | 151 | 9 | 1 | 159 | 0.944 | 0.993 | 0.968 | 0.969 |
| 0.95 | 160 | 151 | 9 | 1 | 159 | 0.944 | 0.993 | 0.968 | 0.969 |

## What this resolves

The analysis shows how the cutoff trades false positives against recall. On this set, the tested positive pairs retain recall through 0.85, while precision improves as the cutoff becomes stricter.

## What a threshold cannot resolve

There are 9 high-score nonmatches (score >= 0.90). These are identity collisions involving generic or ambiguous titles. Because the candidate field contains only a title, no numeric cutoff can infer which author, journal, year, or DOI the record denotes.
The protocol therefore keeps 0.72 as the frozen historical screening cutoff, reports this sensitivity analysis, and changes the future rule to: DOI/stable identifier first; title plus bibliographic metadata second; fuzzy title score only as a fallback. The analysis does not retroactively change the historical ARL or single-agent estimates.

## Boundary

This 320-pair set supports a sensitivity audit, not a universal optimum claim. A genuinely validated threshold would require a prespecified held-out calibration set or nested validation across new domains and languages.
