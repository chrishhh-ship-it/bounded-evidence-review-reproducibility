"""Read-only: per report, how many distinct top-15 candidates are cited via the exact Writer-prompt line."""
from pathlib import Path
from collections import Counter
import json, re, sys, unicodedata
P = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(P / "scripts")); sys.path.insert(0, str(P / "historical_generation_protocols")); sys.path.insert(0, str(P))
import evaluate_metrics as em
import run_expanded_benchmark as reb
corpus = json.loads((P / "data/frozen_corpus_multidomain_v1.json").read_text(encoding="utf-8-sig"))
queries = json.loads((P / "data/benchmarks/benchmark_all_queries.json").read_text(encoding="utf-8-sig"))
queries = queries if isinstance(queries, list) else queries.get("queries")
qmap = {int((q.get("id") or q.get("query_id"))[1:]): q for q in queries}
norm = lambda s: re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s or "")).strip()
strip_md = lambda s: re.sub(r"[*_`]", "", s)
code_line = lambda p: f"{p.get('title','N/A')}. {p.get('journal','') or p.get('source','')}. {p.get('year','')}."
res = {}
for name, folder in [("M1","method1"),("M2a","method2a"),("M2b","method2b"),("M2c","method2d")]:
    files = em._filter_result_files(list((P/"data/expanded_outputs"/folder).glob("*.md")), None, em._parse_query_ids("Q01-Q251"))
    dist = Counter(); outside8 = Counter(); per = {}
    for _, path in sorted(em._select_latest_per_query(files).items()):
        qid = em._parse_result_stem(path.stem)[0]
        side = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
        q = qmap[int(qid[1:])]
        cands = reb.retrieve_from_corpus(q.get("query") or q.get("text"), corpus, domain_id=q.get("domain_id") or side.get("domain_id"), top_k=15)
        lines = {norm(code_line(p)): i for i, p in enumerate(cands, 1)}
        lines_md = {norm(strip_md(k)): v for k, v in lines.items()}
        _, bib = em._split_body_bib(path.read_text(encoding="utf-8"))
        m = set()
        for ref in em._parse_bib_entries(bib).values():
            r = re.sub(r"^\[\d+\]\s*", "", norm(ref))
            if r in lines: m.add(lines[r])
            elif norm(strip_md(r)) in lines_md: m.add(lines_md[norm(strip_md(r))])
        dist[len(m)] += 1
        outside8[sum(1 for i in m if i > 8)] += 1
        per[qid] = sorted(m)
    res[name] = {"distinct_exact_candidates_per_report": dict(sorted(dist.items())),
                 "n_reports": sum(dist.values()), "reports_with_8": dist[8],
                 "reports_with_ge7": sum(v for k, v in dist.items() if k >= 7),
                 "per_query_candidate_ranks": per}
    print(name, "n=", sum(dist.values()), "dist=", dict(sorted(dist.items())))
Path(sys.argv[1]).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
