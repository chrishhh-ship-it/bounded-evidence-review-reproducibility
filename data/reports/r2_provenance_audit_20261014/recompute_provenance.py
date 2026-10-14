# -*- coding: utf-8 -*-
"""Independent recomputation of the post-09-28 numbers (read-only; no API calls).

Inputs: archived expanded outputs (latest per query, Q01-Q251) for M1, M2a, M2b, M2c,
the frozen 3,011-record corpus, and the B0 outputs.
"""
import json, re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts")); sys.path.insert(0, str(ROOT / "historical_generation_protocols")); sys.path.insert(0, str(ROOT))
import evaluate_metrics as em
from run_expanded_benchmark import retrieve_from_corpus

corpus = json.loads((ROOT / "data" / "frozen_corpus_multidomain_v1.json").read_text(encoding="utf-8"))
qids = {f"Q{i:02d}" for i in range(1, 252)} | {f"Q{i}" for i in range(1, 252)}
DIRS = {"M1": "method1", "M2a": "method2a", "M2b": "method2b", "M2c": "method2d"}

def latest(dirpath):
    files = sorted(Path(dirpath).glob("*.md"))
    files = [f for f in files if not any(f.name.lower().endswith(s) for s in (".outline.md", ".raw.md", ".nocheck.md"))]
    sel = em._select_latest_per_query(files)
    out = {}
    for key, path in sel.items():
        parsed = em._parse_result_stem(path.stem)
        if not parsed: continue
        qid = em._canonical_query_id("Q", re.sub(r"\D", "", parsed[0])) if hasattr(em, "_canonical_query_id") else parsed[0]
        n = int(re.sub(r"\D", "", parsed[0]))
        if 1 <= n <= 251:
            out[n] = path
    return out

def line_of(p):
    return f"{p.get('title', 'N/A')}. {p.get('journal', '') or p.get('source', '')}. {p.get('year', '')}."

def norm(s):
    s = s.lower()
    s = re.sub(r"[\*\_`]", "", s)
    s = re.sub(r"[^\w\u4e00-\u9fff]+", " ", s)
    return " ".join(s.split())

def gate(body_cites, bib, pool_titles):
    reasons = []
    if not bib: reasons.append("no_bib")
    unresolved = [c for c in body_cites if c not in bib or not em._match_title(bib[c], pool_titles, threshold=0.72)]
    if unresolved: reasons.append("unresolved")
    if bib and any(k not in set(body_cites) for k in bib): reasons.append("uncited")
    if bib and any(not em._match_title(v, pool_titles, threshold=0.72) for v in bib.values()): reasons.append("outside")
    return reasons

tot_entries = tot_verbatim = 0
reports = reports_eight = 0
arch_unmatched = arch_unmatched_verbatim = 0
res = {}
for lab, d in DIRS.items():
    files = latest(ROOT / "data" / "expanded_outputs" / d)
    assert len(files) == 251, (lab, len(files))
    pool_pass = arch_pass = 0
    m_unmatched = m_unmatched_rank915 = m_unmatched_verbatim = m_unmatched_title15 = 0
    ref_indep_block = {"uncited": 0, "no_bib": 0, "any": 0}
    for n, path in sorted(files.items()):
        side = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
        cands = retrieve_from_corpus(side["query"], corpus, domain_id=side.get("domain_id"), top_k=15)
        top8_ids = [em._paper_id(p) for p in side["top_papers"]]
        assert [em._paper_id(p) for p in cands[:8]] == top8_ids, (lab, n)   # A_c,q = pre-screen top 8
        pool_titles = [p.get("title", "") for p in cands]
        a_titles = [p.get("title", "") for p in cands[:8]]
        lines = {line_of(p).strip(): i for i, p in enumerate(cands)}
        nlines = {norm(line_of(p)): i for i, p in enumerate(cands)}
        content = path.read_text(encoding="utf-8")
        body, bibtxt = em._split_body_bib(content)
        bib = em._parse_bib_entries(bibtxt)
        cites = em._extract_citations_from_text(body)
        reports += 1
        hit_idx = set()
        for k, v in bib.items():
            tot_entries += 1
            v = v.strip()
            verb = v in lines
            tot_verbatim += verb
            j = nlines.get(norm(v))
            if j is not None: hit_idx.add(j)
            if not em._match_title(v, a_titles, threshold=0.72):
                arch_unmatched += 1; arch_unmatched_verbatim += verb
                m_unmatched += 1; m_unmatched_verbatim += verb
                t15 = [i for i, p in enumerate(cands) if p.get("title") and norm(p["title"]) in norm(v)]
                if t15: m_unmatched_title15 += 1
                if verb and lines[v] >= 8: m_unmatched_rank915 += 1
        if len(hit_idx) == 8 and len(bib) >= 8: reports_eight += 1
        if not gate(cites, bib, pool_titles): pool_pass += 1
        if not gate(cites, bib, a_titles): arch_pass += 1
        r = []
        if not bib: r.append("no_bib")
        if bib and any(k not in set(cites) for k in bib): r.append("uncited")
        if any(c not in bib for c in cites): r.append("unresolved_tag")
        if r: ref_indep_block["any"] += 1
        if "uncited" in r: ref_indep_block["uncited"] += 1
        if "no_bib" in r: ref_indep_block["no_bib"] += 1
    res[lab] = dict(pool_pass=pool_pass, arch_pass=arch_pass, archive_unmatched=m_unmatched,
                    unmatched_verbatim=m_unmatched_verbatim, unmatched_verbatim_rank9_15=m_unmatched_rank915,
                    unmatched_with_15cand_title=m_unmatched_title15, ref_indep_block=ref_indep_block)
for k, v in res.items():
    print(k, v)
print("total entries", tot_entries, "verbatim", tot_verbatim, f"{100*tot_verbatim/tot_entries:.1f}%")
print("reports", reports, "with eight distinct normalised lines", reports_eight, f"{100*reports_eight/reports:.1f}%")
print("archive-unmatched entries", arch_unmatched, "of which verbatim", arch_unmatched_verbatim)
