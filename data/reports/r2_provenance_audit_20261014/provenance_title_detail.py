"""Title-level detail for the 3,004 archive-unmatched bibliography entries (read-only).

For each expanded condition, rebuilds the 15 retrieval candidates and classifies
every bibliography entry that does not match the saved first-eight set:
cited or uncited in the body; whether its normalised string contains a
candidate's complete normalised title (verbatim) or matches only through the
0.72 similarity rule; and the length of the contained candidate title. It also
counts cited keys that have no bibliography entry.
"""
from pathlib import Path
from collections import Counter
import json
import statistics
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

res = {}
short_examples = []
similarity_only_examples = []
for name, folder in [("M1", "method1"), ("M2a", "method2a"), ("M2b", "method2b"), ("M2c", "method2d")]:
    files = em._filter_result_files(list((P / "data/expanded_outputs" / folder).glob("*.md")), None,
                                    em._parse_query_ids("Q01-Q251"))
    selected = em._select_latest_per_query(files)
    c = Counter()
    lengths = []
    unresolved_reports = 0
    for _, path in sorted(selected.items()):
        qid = em._parse_result_stem(path.stem)[0]
        side = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
        q = qmap[int(qid[1:])]
        cands = reb.retrieve_from_corpus(q.get("query") or q.get("text"), corpus,
                                         domain_id=q.get("domain_id") or side.get("domain_id"), top_k=15)
        saved = [x.get("title") for x in side.get("top_papers", [])]
        pool = [x.get("title") for x in cands]
        pool_norm = [(t, em._normalize_title(t)) for t in pool if em._normalize_title(t)]
        body, bib = em._split_body_bib(path.read_text(encoding="utf-8"))
        entries = em._parse_bib_entries(bib)
        keys = set(em._extract_citations_from_text(body))
        unresolved = [k for k in keys if k not in entries]
        c["unresolved_cited_keys"] += len(unresolved)
        unresolved_reports += bool(unresolved)
        for num, ref in entries.items():
            if em._match_title(ref, saved, threshold=0.72):
                continue
            c["archive_unmatched"] += 1
            c["cited" if num in keys else "uncited"] += 1
            if not em._match_title(ref, pool, threshold=0.72):
                c["outside_top15"] += 1
                continue
            ref_norm = em._normalize_title(ref)
            contained = [(t, n) for t, n in pool_norm if n in ref_norm]
            if contained:
                c["verbatim_title"] += 1
                longest = max(contained, key=lambda x: len(x[1].split()))
                n_tok = len(longest[1].split()) if not any('\u4e00' <= ch <= '\u9fff' for ch in longest[1]) else len(longest[1])
                lengths.append(n_tok)
                if n_tok < 4 and len(short_examples) < 8:
                    short_examples.append([name, qid, longest[0], ref[:120]])
            else:
                c["similarity_only"] += 1
                if len(similarity_only_examples) < 8:
                    similarity_only_examples.append([name, qid, ref[:140]])
    d = dict(c)
    d["reports_with_unresolved_keys"] = unresolved_reports
    d["contained_title_length_min"] = min(lengths) if lengths else None
    d["contained_title_length_median"] = statistics.median(lengths) if lengths else None
    d["contained_titles_under_4_tokens"] = sum(1 for x in lengths if x < 4)
    res[name] = d
    print(name, d)
res["short_title_examples"] = short_examples
res["similarity_only_examples"] = similarity_only_examples
out = Path(__file__).resolve().parent / "provenance_title_detail.json"
out.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
print("short examples:", json.dumps(short_examples, ensure_ascii=False)[:1500])
print("similarity-only examples:", json.dumps(similarity_only_examples, ensure_ascii=False)[:1500])
