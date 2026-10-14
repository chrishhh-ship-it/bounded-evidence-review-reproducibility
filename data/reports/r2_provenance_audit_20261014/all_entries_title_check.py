"""Title-level check for every bibliography entry in the 1,004 historical expanded reports.

Counts how many entries contain the complete normalised title of one of the
query's 15 retrieved candidates (verbatim), how many match only through the
0.72 similarity rule, and how many match neither; separately for entries that
are cited in the body. Read-only; no model calls.
"""
from pathlib import Path
from collections import Counter
import json
import sys

P = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(P / "scripts")); sys.path.insert(0, str(P / "historical_generation_protocols"))
sys.path.insert(0, str(P))
import evaluate_metrics as em  # noqa: E402
import run_expanded_benchmark as reb  # noqa: E402

corpus = json.loads((P / "data/frozen_corpus_multidomain_v1.json").read_text(encoding="utf-8-sig"))
queries = json.loads((P / "data/benchmarks/benchmark_all_queries.json").read_text(encoding="utf-8-sig"))
queries = queries if isinstance(queries, list) else queries.get("queries")
qmap = {int((q.get("id") or q.get("query_id"))[1:]): q for q in queries}

total = Counter()
res = {}
for name, folder in [("M1", "method1"), ("M2a", "method2a"), ("M2b", "method2b"), ("M2c", "method2d")]:
    files = em._filter_result_files(list((P / "data/expanded_outputs" / folder).glob("*.md")), None,
                                    em._parse_query_ids("Q01-Q251"))
    c = Counter()
    for _, path in sorted(em._select_latest_per_query(files).items()):
        qid = em._parse_result_stem(path.stem)[0]
        side = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
        q = qmap[int(qid[1:])]
        cands = reb.retrieve_from_corpus(q.get("query") or q.get("text"), corpus,
                                         domain_id=q.get("domain_id") or side.get("domain_id"), top_k=15)
        pool = [x.get("title") for x in cands]
        pool_norm = [em._normalize_title(t) for t in pool if em._normalize_title(t)]
        body, bib = em._split_body_bib(path.read_text(encoding="utf-8"))
        entries = em._parse_bib_entries(bib)
        keys = set(em._extract_citations_from_text(body))
        for num, ref in entries.items():
            ref_norm = em._normalize_title(ref)
            cited = num in keys
            if any(n in ref_norm for n in pool_norm):
                kind = "verbatim"
            elif em._match_title(ref, pool, threshold=0.72):
                kind = "similarity_only"
            else:
                kind = "no_match"
            c["entries"] += 1
            c[kind] += 1
            if cited:
                c["cited_entries"] += 1
                c["cited_" + kind] += 1
    res[name] = dict(c)
    total.update(c)
    print(name, dict(c))
res["total"] = dict(total)
print("TOTAL", dict(total))
(Path(__file__).resolve().parent / "all_entries_title_check.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
