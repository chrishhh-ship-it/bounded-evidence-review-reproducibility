# Anonymous reproducibility package

Version: 2026-08-12

This archive reproduces the reported analyses from preserved outputs. It does
not promise byte-identical regeneration of API responses because provider-side
randomness remains possible even at temperature zero and no seed was exposed.

## Included

- frozen normalized corpus and benchmark query sets;
- structural evaluation and statistical-analysis scripts;
- final human title-identity and matched semantic-audit artifacts;
- final threshold, one-output-per-query distribution, and complete-case
  sensitivity analyses;
- external ALCE and SciFact benchmark outputs and analysis artifacts;
- anonymized human-study responses and the formal imputation log;
- anonymized query-construction provenance record;
- SHA-256 and byte-size manifest for every deposited file.

## Excluded

- API keys, browser profiles, account credentials, and local environment files;
- raw proprietary-source exports; only normalized redistributable records are
  included;
- internal model-generated provisional coding keys and abandoned smoke runs;
- coder workbooks containing unnecessary local-document metadata. The final
  machine-readable human results and adjudication records are retained.

## Core commands

Run from the archive root:

```bash
python scripts/evaluate_metrics.py --corpus data/frozen_corpus_multidomain_v1.json --dir PATH_TO_PRESERVED_OUTPUTS --tag method1 --query-ids Q01-Q251
python scripts/final_revision_analyses_20260812.py
```

The complete historical commands and expected values are in
`README_REPRODUCE.md`. The package includes the expanded preserved outputs used
for the reported analyses, their derived per-query evaluation tables, and a
cryptographic manifest. Historical retries remain archived; analyses that
require one row per query use the documented deterministic deduplication rule.

## Access boundary

This repository is prepared for double-blind peer review. Direct identifiers
have been removed from the deposited materials. Raw proprietary-source exports,
provider credentials, and immutable provider-side snapshot identifiers are not
included.
