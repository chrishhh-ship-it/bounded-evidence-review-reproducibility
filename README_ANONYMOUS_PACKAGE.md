# Anonymous reproducibility package

Version: 2026-08-14 review snapshot

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
- SHA-256 and byte-size manifest for every deposited file other than the
  manifest itself.

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

The principal reproducibility claim is analysis reproducibility from the
preserved outputs. Provider-backed scripts are included for protocol
inspection and prospective reruns, but they require users' own API credentials
and may not reproduce historical generations byte for byte.

## Setup and path note

Install the analysis dependencies with:

```bash
python -m pip install -r requirements.txt
```

`requirements-lock.txt` records the exact dependency versions used for the
clean-room verification run. It is an environment snapshot rather than a
promise that hosted model endpoints remain unchanged.

On Windows, clone or extract the repository to a short path such as
`C:\ipmrep`. Deeply nested checkout paths can exceed legacy Windows path
limits. Paths stored inside preserved JSON records use the neutral
`<USER_ROOT>` placeholder and are not required by the analysis scripts.

## Licence and upstream data

The code licence and the boundaries for third-party data are documented in
`LICENSE` and `DATA_SOURCES_AND_LICENSES.md`. The code licence does not grant
new rights over third-party bibliographic records or benchmark data.

## Access boundary

This repository is prepared for double-blind peer review. Local account names,
absolute workstation paths, credentials, and contributor-role identifiers have
been removed. Scholarly bibliographic metadata is retained as research data and
may contain author names already present in the underlying publications. Raw
proprietary-source exports, provider credentials, and immutable provider-side
snapshot identifiers are not included.
