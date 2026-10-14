from pathlib import Path
import json,csv,collections,statistics,sys,numpy as np
from sklearn.metrics import accuracy_score,f1_score,cohen_kappa_score
from scipy.stats import binomtest,wilcoxon
P=Path(r'D:\文献\研究情报助手');O=Path(__file__).resolve().parent;V=P/'data/reports/ipm_major_revision_20260721/repro/v3'
def rd(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
r=rd(V/'title_match_single_vs_arl_20260730/first_independent_coding_20260730/TITLE_MATCH_FIRST_INDEPENDENT_BASELINE_20260730.csv');gold=[x['independent_human_label'] for x in r];res={'title':{}}
for c in ['single_agent_label','arl_label']:
 y=[x[c] for x in r];res['title'][c]={'n':len(r),'correct':sum(a==b for a,b in zip(gold,y)),'accuracy':accuracy_score(gold,y),'macro_f1':f1_score(gold,y,average='macro'),'kappa':cohen_kappa_score(gold,y)}
b=sum(x['arl_label']==x['independent_human_label'] and x['single_agent_label']!=x['independent_human_label'] for x in r);c=sum(x['arl_label']!=x['independent_human_label'] and x['single_agent_label']==x['independent_human_label'] for x in r);res['title']['mcnemar']={'b':b,'c':c,'p':binomtest(b,b+c,.5).pvalue}
keys={x['item_id']:x for x in rd(V/'semantic_arl_v2_3/v23_csp_gold_key_do_not_share.csv')};g=rd(V/'semantic_arl_v2_3/v23_csp_adjudicated_gold_20260806.csv');res['semantic']={}
for condition in ['V0','V1','V2']:
 rr=[x for x in g if keys[x['item_id']]['condition'].upper()==condition];res['semantic'][condition]={'n':len(rr),'labels':dict(collections.Counter(x['adjudicated_verdict'] for x in rr))}
valid=[x for x in g if x['coder_A_verdict'] in ['SUPPORTED','PARTIAL','CONTRADICTED','INSUFFICIENT'] and x['coder_B_verdict'] in ['SUPPORTED','PARTIAL','CONTRADICTED','INSUFFICIENT']];res['semantic']['reliability']={'n':len(valid),'agree':sum(x['coder_A_verdict']==x['coder_B_verdict'] for x in valid),'kappa':cohen_kappa_score([x['coder_A_verdict'] for x in valid],[x['coder_B_verdict'] for x in valid])}
sys.path.insert(0,str(P/'scripts/external_benchmark'));from score_alce_official_pilot import citation_diagnostics
raw=json.loads((P/'data/external_benchmarks/alce_official_pilot_n40_structural/alce_official_pilot_outputs.json').read_text(encoding='utf8'));res['alce']={}
for ds in ['asqa','qampari']:
 by={};[by.setdefault(x.get('sample_id') or x.get('id'),{}).update({x['condition']:x}) for x in raw if x['dataset']==ds]
 for metric in ['citation_index_validity','sentence_citation_coverage']:
  a=np.array([citation_diagnostics(v['v0'])[metric] for v in by.values()]);b=np.array([citation_diagnostics(v['v2'])[metric] for v in by.values()]);d=b-a
  res['alce'][ds+'_'+metric]={'n':len(a),'v0':a.mean(),'v2':b.mean(),'difference':d.mean(),'up':int(sum(d>1e-9)),'down':int(sum(d<-1e-9)),'same':int(sum(abs(d)<1e-9)),'p':float(wilcoxon(a,b).pvalue) if any(d) else None}
nli=json.loads((P/'data/reports/ipm_major_revision_20260721/completion_5678_20260726/external_semantic_completion.json').read_text(encoding='utf8'))['alce_full_local_nli'];print('NLI FIELDS',list(nli['pair_scores'][0]),'CONDITIONS',str(nli['conditions'])[:1500]);res['nli_stored_summary']=nli['conditions']
(O/'additional_results.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in res.items() if k!='nli_stored_summary'},indent=2))

