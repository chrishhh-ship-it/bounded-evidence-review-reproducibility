# Data sources and reuse boundaries

This repository is an anonymized peer-review snapshot. The MIT licence in
`LICENSE` covers source code only. It does not place third-party data under a
new licence.

## Deposited material

| Material | Purpose | Reuse boundary |
|---|---|---|
| Project-generated query sets, derived metrics, anonymized audit labels, and preserved system outputs | Reproduce the reported analyses | Supplied for scholarly verification; generated text can contain excerpts or bibliographic metadata governed by source terms. |
| Normalized bibliographic records | Freeze the query-specific evidence states | Metadata originated from services identified in each record, including Crossref, OpenAlex, Semantic Scholar, arXiv, PubMed, Google Scholar, Wanfang, and Scopus. No ownership over source metadata is asserted. |
| ALCE-derived ASQA and QAMPARI materials | External citation-structure evaluation | Users must follow the upstream ALCE and underlying dataset licences and citation requirements. |
| SciFact-derived materials | External claim-verification evaluation | Users must follow the upstream SciFact licence and citation requirements. |
| Human-study analysis table | Reproduce aggregate and sensitivity analyses | Only pseudonymous participant IDs and analysis variables are deposited. Direct identifiers, questionnaire file names, and redundant raw display fields are excluded; reuse remains subject to applicable ethics and data-protection requirements. |

## Upstream resources

- ALCE: https://github.com/princeton-nlp/ALCE
- SciFact: https://github.com/allenai/scifact
- Crossref REST API: https://www.crossref.org/documentation/retrieve-metadata/rest-api/
- OpenAlex: https://openalex.org/
- Semantic Scholar API: https://www.semanticscholar.org/product/api
- arXiv: https://arxiv.org/
- PubMed: https://pubmed.ncbi.nlm.nih.gov/

The repository intentionally excludes raw proprietary exports and credentials.
Before redistributing any subset beyond peer review, verify the applicable
upstream licence and terms of service. If a record's reuse status is uncertain,
retain only the derived aggregate statistic or obtain permission from the
source provider.
