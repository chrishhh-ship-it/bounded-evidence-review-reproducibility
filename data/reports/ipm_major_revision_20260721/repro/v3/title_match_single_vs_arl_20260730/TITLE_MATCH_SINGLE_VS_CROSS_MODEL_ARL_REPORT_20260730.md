# Title-match single agent vs cross-model ARL

Date: 2026-07-30

## Experimental question

Does a role-separated, cross-model audit pipeline improve title-match decisions over a single-agent DeepSeek baseline when both systems receive the same 320 title pairs and are evaluated against the same human reference key?

## Frozen design

- Human reference: `title_match_verified_key_20260730.csv`, with the author's two adjudications applied: `TM077 = match`, `TM189 = nonmatch`.
- Gold balance: 160 `match`, 160 `nonmatch`.
- Single-agent baseline: DeepSeek `deepseek-v4-pro`.
- ARL analyst: DeepSeek `deepseek-v4-pro`.
- ARL critic: Kimi `moonshot-v1-32k`.
- ARL final adjudicator: DeepSeek `deepseek-v4-pro`.
- Temperature: 0.0 for all calls.
- All 320 items completed; no failed items.

The Kimi stage was executed as an independent adversarial review, not as a second copy of the DeepSeek model. Raw outputs for all roles are retained in the per-item JSON files.

## Results

| System | Accuracy | Macro-F1 | Errors |
|---|---:|---:|---:|
| Single-agent DeepSeek | 99.375% | 0.9938 | 2 |
| Cross-model ARL | 96.563% | 0.9656 | 11 |
| ARL minus single agent | -2.8125 pp | -0.0282 | +9 |

Paired comparison:

- ARL correct / single wrong: 0
- Single correct / ARL wrong: 9
- Exact paired McNemar p = 0.00390625

Thus, this implementation of cross-model ARL is significantly worse than the single-agent baseline on this title-match task. It cannot be reported as evidence that ARL improves title matching.

## Diagnostic finding

The nine ARL regressions are all cases where the single agent said `match`, the DeepSeek analyst said `match`, but the Kimi critic said `nonmatch` and the DeepSeek adjudicator followed the critic. The dominant failure mode was an overly strict requirement that a candidate title must also include author, journal, and year metadata.

That rule is inconsistent with the human title-match protocol used here. Several cases have an exact candidate title but omit metadata; the human key treats the title identity as sufficient. The ARL critic therefore converted correct exact-title matches into false negatives. This is a calibration and task-definition failure in the present ARL prompt, not proof that cross-model review is intrinsically inferior.

One additional case, `TM240`, shows the opposite direction: the single agent and final ARL both returned `match`, while the human key is `nonmatch` because the candidate title omits the distinctive modifier `Automated`. This indicates that the title protocol must distinguish essential title modifiers from optional shortened-title wording before claiming semantic superiority.

## What the result supports

The experiment supports only the following claims:

1. A real DeepSeek-Kimi-DeepSeek ARL pipeline was executed on all 320 items.
2. Under the first frozen prompt version, the pipeline was more conservative and produced more false negatives than the single-agent baseline.
3. The Kimi critic introduced a systematic metadata-completeness bias.
4. The result is diagnostic evidence for recalibrating the ARL task specification; it is not positive evidence for ARL improvement.

## What must not be claimed

- Do not claim that cross-model ARL improves title-match accuracy.
- Do not claim that Kimi is intrinsically worse than DeepSeek from this single task.
- Do not treat the model outputs as a replacement for the two human coding records.
- Do not silently change the human key or prompt after seeing these results and then report a new result as if it were the original confirmatory test.

## Recommended next experiment

If ARL is to be tested again, preserve this run as the preregistered diagnostic result and create a clearly labeled recalibration run. The revised critic and adjudicator prompts should state:

- This is a title-identity task, not a full-record metadata-completeness task.
- An exact candidate title is a match even when the candidate extract omits authors, venue, or year, unless the reference title is known to be ambiguous and the candidate contains conflicting information.
- Distinctive modifiers such as `automated`, `LLM-based`, a population, or a specific method cannot be dropped when their omission changes the work's scope.
- General topical overlap and shared words remain insufficient.

The recalibration run should use the same 320 items, same gold key, same providers, same temperature, and a new versioned output directory. Only after that independent run should the two versions be compared. If the recalibrated ARL still loses, ARL should be retained as an auditability/traceability architecture rather than an accuracy-improvement claim.

## Reproducibility files

- Metrics: `TITLE_MATCH_SINGLE_VS_ARL_METRICS.json`
- Compact decisions: `title_match_single_vs_arl_results.csv`
- Full raw role outputs: `title_match_single_vs_arl_raw.jsonl`
- Per-item raw outputs: `items\\TM001.json` through `items\\TM320.json`
- Run manifest: `run_manifest.json`
- Script: `<USER_ROOT>\\文献\\研究情报助手\\scripts\\run_title_match_single_vs_arl.py`
