# Review snapshot repair log

This snapshot was rebuilt from repository commit
`fe3f1a3b47807a331208e12f0baf7fd611c9137b` after an independent clean-room
audit.

## Repairs

- restored `modules/searcher.py`, `modules/text_metrics.py`, and
  `modules/generation_history.py`, which are imported by deposited scripts;
- replaced workstation-specific absolute paths in preserved JSON and Markdown
  records with the neutral `<USER_ROOT>` placeholder;
- clarified that the main reproducibility claim concerns analyses from
  preserved outputs, while provider-backed regeneration requires credentials
  and can vary across hosted endpoint versions;
- added Windows short-path guidance and an exact verification-environment
  snapshot;
- added a code licence and third-party data/reuse boundary statement;
- added a deterministic manifest builder and regenerated the complete SHA-256
  manifest without cache or bytecode entries;
- updated the reproduction-guide date and setup instructions.

## Verification

The repaired snapshot passed the following checks:

- all Python files compiled;
- all 3,111 JSON files parsed after path neutralization;
- all four expanded 251-query `evaluate_metrics.py` commands reproduced the
  documented M1, M2a, M2b, and M2c values;
- `analyze_user_study.py` reproduced the documented descriptive values;
- `final_revision_analyses_20260812.py` completed successfully;
- provider-backed command entry points imported successfully and displayed
  their command-line help;
- every deposited file listed in `MANIFEST_SHA256.csv` passed an independent
  size and SHA-256 check.

Hosted-model regeneration was not rerun because it requires private API
credentials and does not promise byte-identical responses.
