from pathlib import Path
import sys,json,statistics,collections,csv
P=Path(r'D:\文献\研究情报助手');O=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'scripts'));sys.path.insert(0,str(P/'scripts/external_benchmark'))
import score_scifact_cross_vs_same_model as sc
import score_scifact_cross_vs_same_model_n100 as sc100
import analyze_reviewer_vs_gate_e2_r32 as gate
import run_alce_validation as wiki
import evaluate_metrics as em
sc.OUT=O/'scifact_n40.json';sc.main();sc100.OUT=O/'scifact_n100.json';sc100.main();gate.OUT_PATH=O/'reviewer_vs_gate.json';gate.main()
res={'wiki':{}}
# Score only current D-drive copies, retaining the original parser.
for jf in sorted((P/'data/alce_outputs').glob('*.json')):
 d=json.loads(jf.read_text(encoding='utf8'));md=jf.with_suffix('.md')
 if md.exists():res['wiki'].setdefault(d['condition'],[]).append(wiki.compute_metrics(md.read_text(encoding='utf8'),d.get('eq_titles',[])))
res['wiki']={k:{'n':len(v),**{m:statistics.mean(r[m] for r in v) for m in ['icp','ecp','or']}} for k,v in res['wiki'].items()}
corpus=json.loads((P/'data/frozen_corpus_multidomain_v1.json').read_text(encoding='utf8'));byid={em._paper_id(r):r for r in corpus};res['autosurvey']={}
for name,folder,tag,n in [('controlled','autosurvey_outputs','autosurvey',30),('native','autosurvey_native_outputs','autosurvey_native',30),('nocheck','autosurvey_native_outputs','autosurvey_native_nocheck',5)]:
 files=em._select_latest_per_query(em._filter_result_files(list((P/'data'/folder).glob('*.md')),tag,em._parse_query_ids(f'Q01-Q{n:02}')));rows=[em.evaluate_file(p,tag,byid,.72) for p in files.values()]
 assert len(rows)==n,(name,len(rows));res['autosurvey'][name]={'n':len(rows),**{k:statistics.mean(r[k] for r in rows if r[k] is not None) for k in ['citation_precision','bibliography_match_rate','orphan_rate']}};print('autosurvey',name,res['autosurvey'][name],flush=True)
res['corpus_counts']={}
qs=json.loads((P/'data/benchmarks/benchmark_all_queries.json').read_text(encoding='utf8'));ft=json.loads((O/'fulltext_manifest_verification.json').read_text(encoding='utf8'))
for dom in sorted(set(x['domain_id'] for x in corpus)):
 rr=[x for x in corpus if x['domain_id']==dom];res['corpus_counts'][dom]={'papers':len(rr),'abstracts':sum(bool(x.get('abstract')) for x in rr),'queries':sum(x['domain_id']==dom for x in qs),'fulltexts':sum(x['domain']==dom for x in ft)}
(O/'remaining_audit.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf8');print('REMAINING DONE',flush=True)
