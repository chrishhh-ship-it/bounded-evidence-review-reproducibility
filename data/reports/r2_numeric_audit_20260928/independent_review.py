"""Independent R2 review. Reads existing artifacts; writes only this new review folder."""
from pathlib import Path
import csv,json,sys,hashlib,statistics,re
from collections import Counter
import numpy as np
from scipy import stats
P=Path(r'D:\文献\研究情报助手');R=P/'data/reports/IPM_R2_20260928';O=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'scripts'));import evaluate_metrics as em
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
corpus_files={'pilot':P/'data/topic_runs/multi_agent_intel_service_20260410_114059/retrieved_papers_wave3.json','expanded':P/'data/frozen_corpus_multidomain_v1.json'}
corpora={k:json.loads(p.read_text(encoding='utf-8-sig')) for k,p in corpus_files.items()}
allrows={}; provenance={}
specs=[('A','baselines','baseline_a','pilot',30),('B','baselines','baseline_b','pilot',30),('pilot_M1','method1_outputs','method1','pilot',60),('pilot_M2a','method2_outputs','method2','pilot',60),('pilot_M2b','method2_same_model_outputs','method2_same_model','pilot',60),('pilot_M3','method3_outputs','method3','pilot',60),('pilot_M4','method4_outputs','method4','pilot',60)]+[(k,'expanded_outputs/'+f,None,'expanded',251) for k,f in [('M1','method1'),('M2a','method2a'),('M2b','method2b'),('M2c','method2d'),('B0','schema_single_agent_v1')]]
for name,folder,tag,scope,n in specs:
    byid={em._paper_id(r):r for r in corpora[scope]};rows=[];ids=em._parse_query_ids(f'Q01-Q{n}')
    files=em._select_latest_per_query(em._filter_result_files(list((P/'data'/folder).glob('*.md')),tag,ids))
    for f in files.values():
        q,cfg,_=em._parse_result_stem(f.stem);cfg=em._infer_config_tag(f,cfg)
        d=json.loads(f.with_suffix('.json').read_text(encoding='utf8'));r=em.evaluate_file(f,cfg,byid,.72)
        body,bib=em._split_body_bib(f.read_text(encoding='utf8'));entries=em._parse_bib_entries(bib);keys=em._extract_citations_from_text(body)
        pool=em._build_candidate_pool(d,byid)
        # Verify arithmetic from parsed counts, independently of evaluator's aggregation.
        T=sum(k not in entries or em._match_title(entries[k],[v['title'] for v in pool],.72) is None for k in keys)
        U=len(set(entries)-set(keys))
        assert T==r['text_orphans'] and U==r['uncited_bibliography_entries']
        assert abs(r['orphan_rate']-(T+U)/max(len(keys),len(entries),1))<1e-12
        gate=bool(entries) and all(k in entries for k in keys) and U==0 and r['bibliography_match_rate']==1
        r.update(qid=q,mode=d.get('corpus_mode','not_recorded'),gate=gate,
            linkage=(sum(k in entries for k in keys)/len(keys) if keys else None),
            bibliography_unmatched=int(round((1-r['bibliography_match_rate'])*len(entries))),
            pool_ids=sorted(em._paper_id(p) for p in pool),top_ids=sorted(em._paper_id(p) for p in d.get('top_papers',[])),
            md_sha256=sha(f),json_sha256=sha(f.with_suffix('.json')))
        rows.append(r)
        if name=='pilot_M1' and r['mode']=='not_recorded':
            provenance[q]={'file':str(f),'sidecar_keys':list(d),'retrieved_count':d.get('retrieved_count'),
                'top_papers_n':len(d.get('top_papers',[])),'pool_n':len(pool),'sidecar':d}
    assert len(rows)==n,(name,len(rows),n)
    allrows[name]=sorted(rows,key=lambda x:int(x['qid'][1:]));print('evaluated',name,len(rows),flush=True)
    (O/(name+'_rows.json')).write_text(json.dumps(allrows[name],ensure_ascii=False,indent=2),encoding='utf8')
def mean(vals):
    a=[v for v in vals if v is not None];return statistics.fmean(a) if a else None
def summary(rows):
    return {'n':len(rows),'cp_n':sum(r['citation_precision'] is not None for r in rows),
        **{k:mean(r[k] for r in rows) for k in ['citation_precision','bibliography_match_rate','orphan_rate','linkage','gate']},
        'bmr_defined_only':mean(r['bibliography_match_rate'] for r in rows if r['has_bibliography']),
        'gate_n':sum(r['gate'] for r in rows),'has_bib_n':sum(r['has_bibliography'] for r in rows),
        'text_orphans':sum(r['text_orphans'] for r in rows),'uncited':sum(r['uncited_bibliography_entries'] for r in rows),
        'out_of_state_reports':sum(r['bibliography_unmatched']>0 for r in rows),'pool_sizes':dict(Counter(r['candidate_pool_size'] for r in rows))}
summaries={k:summary(v) for k,v in allrows.items()}
for k in [x for x in allrows if x.startswith('pilot_')]:
    for label,test in [('Q01_Q30',lambda r:int(r['qid'][1:])<=30),('Q31_Q60',lambda r:int(r['qid'][1:])>30),('frozen',lambda r:r['mode']=='frozen_topic_run')]:
        rr=[r for r in allrows[k] if test(r)]
        if rr:summaries[k+'_'+label]=summary(rr)
frozen47={r['qid'] for r in allrows['pilot_M1'] if r['mode']=='frozen_topic_run'}
frozen17={q for q in frozen47 if int(q[1:])<=30}
for k in [x for x in allrows if x.startswith('pilot_')]:
    summaries[k+'_matched47']=summary([r for r in allrows[k] if r['qid'] in frozen47])
    summaries[k+'_matched17']=summary([r for r in allrows[k] if r['qid'] in frozen17])
# Same 12-test family, complete pairs for each metric; explicit BH step-up.
tests=[];a={r['qid']:r for r in allrows['M1']}
for name in ['B0','M2a','M2b','M2c']:
    for metric in ['citation_precision','bibliography_match_rate','orphan_rate']:
        pairs=[(a[r['qid']][metric],r[metric]) for r in allrows[name] if a[r['qid']][metric] is not None and r[metric] is not None]
        x,y=np.array(pairs).T;d=y-x;t=stats.wilcoxon(d,zero_method='pratt',alternative='two-sided')
        tests.append({'comparison':name+'-M1','metric':metric,'n':len(d),'mean_difference':float(np.mean(d)),'p':float(t.pvalue),'statistic':float(t.statistic)})
order=sorted(range(len(tests)),key=lambda i:tests[i]['p']);acc=1
for rank in range(len(tests),0,-1):
    i=order[rank-1];acc=min(acc,tests[i]['p']*len(tests)/rank);tests[i]['q']=acc
summary_obj={'evaluator_sha256':sha(Path(em.__file__)),'corpus_sha256':{k:sha(p) for k,p in corpus_files.items()},'summaries':summaries,'paired_tests':tests,'not_frozen_M1_qids':sorted(provenance),'retrieval_sidecar_evidence':provenance}
(O/'independent_results.json').write_text(json.dumps(summary_obj,ensure_ascii=False,indent=2),encoding='utf8')
print('DONE',O/'independent_results.json',flush=True)
