# v2.3 semantic condition summary

Date: 2026-08-06

## Source and interpretation

This summary uses the user-adjudicated reference labels in `v23_csp_adjudicated_gold_20260806.csv`, joined to the frozen V0/V1/V2 condition mapping. The labels are human support judgments for generated claim--evidence pairs. They are not model self-verdicts and are not, by themselves, an accuracy measure.

## Descriptive results

| Condition | Anchors | Assessed | Removed | Supported | Partial | Contradicted | Insufficient | Supported / assessed | Supported+Partial / assessed | Supported / all anchors | Supported+Partial / all anchors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V0 | 60 | 60 | 0 | 19 | 37 | 1 | 3 | 0.3167 | 0.9333 | 0.3167 | 0.9333 |
| V1 | 60 | 55 | 5 | 37 | 18 | 0 | 0 | 0.6727 | 1.0000 | 0.6167 | 0.9167 |
| V2 | 60 | 58 | 2 | 38 | 19 | 1 | 0 | 0.6552 | 0.9828 | 0.6333 | 0.9500 |

## Boundary

The results are descriptive because the conditions do not have identical claim-retention patterns: V1 has five removed items and V2 has two. Excluding removed items can make a condition look better by changing the denominator; therefore both assessed-denominator and all-anchor rates are reported. No causal or statistically significant ARL claim should be made from this table alone.
