# Prompts and role instructions

This file collects the instructions referred to in Sections 3.1–3.2 of the manuscript and states where each one is implemented.

## 1. Archived generation runs (pilot and expanded benchmark)

| Role | Where the exact prompt is | Notes |
|---|---|---|
| Query shortening (pilot only) | `historical_generation_protocols/batch_run_method1.py`, `_derive_search_query` | Applied to long pilot queries before lexical retrieval. |
| Screening | `batch_run_method1.py`, `role2_screening` | Scores the 15 lexical candidates from 0 to 10; the eight highest are retained; lexical order is the fallback. |
| Evidence extraction | `batch_run_method1.py`, `role3_evidence` | Returns key claim, methodology, metrics and limitation from the title and abstract. |
| Writer | `batch_run_method1.py`, `SYNTHESIS_SYSTEM` and `role4_synthesis` | Five-section report; the prompt ends with the code-rendered reference lines (`[i] title. venue or source. year.`). |
| ARL Reviewer (M2a/M2b/M2c) | `historical_generation_protocols/batch_run_method2.py`, `REVIEW_SYSTEM` and `review_draft` | Receives the query, the structured evidence set and the full draft; returns JSON with overall score, major issues, citation issues, revision instructions and an acceptance flag. |
| ARL Reviser (M2a/M2b/M2c) | `batch_run_method2.py`, `REVISE_SYSTEM` and `revise_draft` | Rewrites the draft from the same evidence set and the reviewer JSON; the prompt ends with the same reference lines. |
| Expanded-run configuration | `historical_generation_protocols/run_expanded_benchmark.py` | Models per condition, retrieval over the 3,011-record corpus, up to two review rounds. |
| Self-critique control (M3) | `historical_generation_protocols/batch_run_method3.py` | General quality critique without a check against the evidence list. |
| Chain-of-thought verification control (M4) | `historical_generation_protocols/batch_run_method4.py` | Same agent checks each citation index against the evidence list. |
| Schema-matched single agent (B0) | `scripts/run_schema_matched_single_agent.py` | One call over the archived M1 set; fixed bibliography. |

## 2. Structural protocol (Section 3.2)

The structural ARL protocol is specified by the following instructions. In the public-corpus check (Section 4.13, `historical_generation_protocols/run_alce_validation.py`) the Reviewer comparison is implemented deterministically with the 0.72 title matcher and the Reviser uses an equivalent instruction.

**Reviewer**

> You are a citation audit agent. You will receive (a) a bibliography list and (b) an evidence dictionary. First determine title identity. Treat an exact, distinctive title or an unambiguous translation/variant as a match even when the candidate string omits author, venue, or year. Use metadata to disambiguate generic titles, not to reject an otherwise exact title solely because metadata is absent. Use token overlap ≥ 0.72 only as a screening signal, not as a substitute for identity assessment. Report all unmatched entries as orphaned citations. For each orphan, output: the key [N], the reason for rejection (no match / low overlap / out-of-range key), and a correction directive specifying the closest evidence-dictionary replacement or removal if no suitable match exists. Output in structured JSON format.

**Reviser**

> You are a citation repair agent. Apply the correction directives from the Reviewer. For each orphaned citation: replace it with the evidence-dictionary entry specified in the correction directive, or remove it entirely if the directive specifies removal. Preserve all content that does not involve orphaned citations. Do not introduce any new citations.

## 3. Other experiments

| Experiment | Script |
|---|---|
| Title-identity audit (Section 4.4) | `historical_generation_protocols/run_title_match_single_vs_arl.py`; calibrated recheck `run_title_match_single_vs_arl_v2_calibrated.py`; threshold sensitivity `scripts/analyze_title_match_threshold_sensitivity.py` |
| Matched semantic audit V0–V2 (Section 4.5) | `build_v23_b1.py`, `run_v23_v1_self_critique.py`, `run_v23_v2_arl.py` |
| AutoSurvey comparison (Section 4.7) | `run_autosurvey_controlled.py`, `run_autosurvey_native.py` |
| Bilingual retrieval (Section 4.8) | `run_bilingual_retrieval_exp.py` |
| English stress test (Section 4.9) | `run_english_benchmark.py` |
| ALCE (Section 4.10) | `scripts/external_benchmark/run_official_alce_pilot.py`, `score_alce_official_pilot.py`, `test_alce_structural_significance.py` |
| Reviewer vs gate (Section 4.10.3) | `historical_generation_protocols/run_reviewer_vs_gate_e2_r32.py`, `scripts/analyze_reviewer_vs_gate_e2_r32.py` |
| SciFact (Section 4.11) | `scripts/external_benchmark/run_official_scifact_semantic_pilot.py`, `run_scifact_cross_model_pilot.py`, `score_scifact_cross_vs_same_model*.py`; NLI `scripts/run_complete_semantic_audit.py` |
| Human study materials (Section 4.12) | `historical_generation_protocols/build_user_study_materials.py` |
| Public-corpus check (Section 4.13) | `historical_generation_protocols/run_alce_validation.py` |
