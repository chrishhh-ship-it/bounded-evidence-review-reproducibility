"""Information-flow check of historical expanded bibliographies (read-only; no model calls).

In run_expanded_benchmark.py the Writer prompt (batch_run_method1.role4_synthesis) contains only the
screened/enriched records, each rendered by code as "[i] {title}. {journal or source}. {year}.", and the
M2 Reviewer/Reviser receive evidence blocks and bibliography lines built from the same screened records.
The seven unscreened top-15 candidates are never shown to any generation role. A bibliography entry that
reproduces the exact code-rendered line of a candidate therefore records that candidate as part of the
actual generation input. This script measures how many entries reproduce such lines.
"""
from pathlib import Path
from collections import Counter
import json
import re
import sys
import unicodedata

P = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(P / "scripts")); sys.path.insert(0, str(P / "historical_generation_protocols"))
sys.path.insert(0, str(P))
import evaluate_metrics as em  # noqa: E402
import run_expanded_benchmark as reb  # noqa: E402

corpus = json.loads((P / "data/frozen_corpus_multidomain_v1.json").read_text(encoding="utf-8-sig"))
queries = json.loads((P / "data/benchmarks/benchmark_all_queries.json").read_text(encoding="utf-8-sig"))
queries = queries if isinstance(queries, list) else queries.get("queries")
qmap = {int((q.get("id") or q.get("query_id"))[1:]): q for q in queries}


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def code_line(p):
    """Exactly the bibliography line role4_synthesis puts in the Writer prompt (without the [i] prefix)."""
    venue = p.get("journal", "") or p.get("source", "")
    return f"{p.get('title', 'N/A')}. {venue}. {p.get('year', '')}."


def strip_md(s):
    return re.sub(r"[*_`]", "", s)


out = {}
for name, folder in [("M1", "method1"), ("M2a", "method2a"), ("M2b", "method2b"), ("M2c", "method2d")]:
    files = em._filter_result_files(list((P / "data/expanded_outputs" / folder).glob("*.md")), None,
                                    em._parse_query_ids("Q01-Q251"))
    c = Counter()
    ranks = Counter()
    per_report_sizes = Counter()
    examples = []
    for _, path in sorted(em._select_latest_per_query(files).items()):
        qid = em._parse_result_stem(path.stem)[0]
        side = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
        q = qmap[int(qid[1:])]
        cands = reb.retrieve_from_corpus(q.get("query") or q.get("text"), corpus,
                                         domain_id=q.get("domain_id") or side.get("domain_id"), top_k=15)
        lines = {norm(code_line(p)): i for i, p in enumerate(cands, 1)}
        lines_nomd = {norm(strip_md(k)): v for k, v in lines.items()}
        titles = [(norm(p.get("title", "")), i) for i, p in enumerate(cands, 1)]
        _, bib = em._split_body_bib(path.read_text(encoding="utf-8"))
        entries = em._parse_bib_entries(bib)
        per_report_sizes[len(entries)] += 1
        matched = set()
        for num, ref in entries.items():
            r = norm(ref)
            r = re.sub(r"^\[\d+\]\s*", "", r)
            c["entries"] += 1
            if r in lines:
                c["exact_code_line"] += 1
                ranks[lines[r]] += 1
                matched.add(lines[r])
            elif norm(strip_md(r)) in lines_nomd:
                c["code_line_after_markdown_strip"] += 1
                ranks[lines_nomd[norm(strip_md(r))]] += 1
                matched.add(lines_nomd[norm(strip_md(r))])
            else:
                hit = next((i for t, i in titles if t and r.startswith(t)), None)
                if hit:
                    c["title_prefix_other_venue_or_year"] += 1
                    ranks[hit] += 1
                    matched.add(hit)
                    if len(examples) < 6:
                        examples.append({"qid": qid, "entry": ref[:180], "expected": code_line(cands[hit - 1])[:180]})
                else:
                    c["other"] += 1
                    if len(examples) < 12:
                        examples.append({"qid": qid, "entry": ref[:180]})
        c["reports"] += 1
        c["distinct_candidates_cited_total"] += len(matched)
        c["reports_all_entries_exact_or_md"] += int(all(
            norm(re.sub(r"^\[\d+\]\s*", "", norm(ref))) in lines or
            norm(strip_md(re.sub(r"^\[\d+\]\s*", "", norm(ref)))) in lines_nomd for ref in entries.values()) and bool(entries))
    out[name] = {"counts": dict(c), "matched_rank_distribution": dict(sorted(ranks.items())),
                 "bibliography_sizes": dict(sorted(per_report_sizes.items())), "examples": examples}
    print(name, json.dumps(dict(c), ensure_ascii=False))
    print("   ranks:", dict(sorted(ranks.items())))
    print("   bib sizes:", dict(sorted(per_report_sizes.items())))
(Path(__file__).resolve().parent / "bib_line_provenance_check.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
