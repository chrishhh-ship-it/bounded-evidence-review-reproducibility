# Human-study analysis data

`analysis_responses_n30.csv` is the anonymized, analysis-ready table used by
the deposited scripts. It contains 300 rows: 30 pseudonymous participants
(`P01`-`P30`) by 10 evaluation questions.

## Deposited fields

| Field | Meaning |
|---|---|
| `participant` | Pseudonymous participant identifier. |
| `qno` | Evaluation-question number (1-10). |
| `rank_systems` | Complete system ordering, for example `A>C>B`. |
| `rank_1st_system` | System ranked first. |
| `rank_2nd_system` | System ranked second. |
| `rank_3rd_system` | System ranked third. |
| `suspicious_system` | System judged most suspicious. |
| `score_A` | Likert score for system A. |
| `score_B` | Likert score for system B. |
| `score_C` | Likert score for system C. |

The system-to-method mapping is defined in `scripts/analyze_user_study.py` and
`answer_key.json`.

## Sanitization boundary

The local source extraction included questionnaire file names and redundant
display-form fields. Some historical exports also contained irreversible
character-encoding damage in those non-analytic fields. They are not deposited
because file names can disclose direct identifiers and the raw display fields
are not used by any reported analysis. The clean normalized ranking, suspicion,
and score fields were unaffected and are preserved in full here.

`imputation_log.json` records the three documented cleaning decisions. No
additional values were reconstructed for this public snapshot.
