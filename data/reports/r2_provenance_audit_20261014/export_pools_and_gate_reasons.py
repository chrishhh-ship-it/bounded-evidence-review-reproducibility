# -*- coding: utf-8 -*-
"""Export, for every expanded report (M1, M2a, M2b, M2c; Q01-Q251), the reconstructed 15-candidate retrieval pool,
the archived reference set A_{c,q} (pre-screen top 8), and gate verdicts with reasons against A_{c,q}, against the
15-candidate pool, and for the reference-set-independent checks. Read-only; no model calls."""
import json, re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts")); sys.path.insert(0, str(ROOT / "historical_generation_protocols")); sys.path.insert(0, str(ROOT))
import evaluate_metrics as em
from run_expanded_benchmark import retrieve_from_corpus

corpus = json.loads((ROOT / "data" / "frozen_corpus_multidomain_v1.json").read_text(encoding="utf-8"))
DIRS = {"M1": "method1", "M2a": "method2a", "M2b": "method2b", "M2c": "method2d"}

def reasons(cites, bib, titles):
    r = []
    if not bib: r.append("missing_bibliography")
    if any(c not in bib or not em._match_title(bib[c], titles, threshold=0.72) for c in cites): r.append("unresolved_in_text_citation")
    if bib and any(k not in set(cites) for k in bib): r.append("uncited_bibliography_entry")
    if bib and any(not em._match_title(v, titles, threshold=0.72) for v in bib.values()): r.append("bibliography_outside_reference_set")
    return r

out = []
for lab, d in DIRS.items():
    files = em._filter_result_files(list((ROOT / "data" / "expanded_outputs" / d).glob("*.md")), None, em._parse_query_ids("Q01-Q251"))
    for _, path in sorted(em._select_latest_per_query(files).items()):
        qid = em._parse_result_stem(path.stem)[0]
        side = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
        cands = retrieve_from_corpus(side["query"], corpus, domain_id=side.get("domain_id"), top_k=15)
        body, bibtxt = em._split_body_bib(path.read_text(encoding="utf-8"))
        bib = em._parse_bib_entries(bibtxt); cites = em._extract_citations_from_text(body)
        indep = []
        if not bib: indep.append("missing_bibliography")
        if any(c not in bib for c in cites): indep.append("unresolved_in_text_citation")
        if bib and any(k not in set(cites) for k in bib): indep.append("uncited_bibliography_entry")
        out.append({
            "condition": lab, "query_id": qid, "report": path.name,
            "pool_15_ids": [em._paper_id(p) for p in cands],
            "archived_set_A_ids": [em._paper_id(p) for p in side["top_papers"]],
            "gate_vs_archived_set": reasons(cites, bib, [p.get("title", "") for p in cands[:8]]),
            "gate_vs_15_pool": reasons(cites, bib, [p.get("title", "") for p in cands]),
            "reference_set_independent": indep,
        })
dst = Path(__file__).resolve().parent / "pools_and_gate_reasons.json"
dst.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
from collections import Counter
for lab in DIRS:
    rows = [r for r in out if r["condition"] == lab]
    print(lab, len(rows), "pass vs A:", sum(not r["gate_vs_archived_set"] for r in rows),
          "pass vs pool:", sum(not r["gate_vs_15_pool"] for r in rows),
          "indep blocks:", sum(bool(r["reference_set_independent"]) for r in rows))
