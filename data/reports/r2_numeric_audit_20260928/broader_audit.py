from pathlib import Path
import sys,json,statistics,csv,hashlib,collections
import numpy as np
P=Path(r'D:\文献\研究情报助手');O=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'scripts'))
import final_revision_analyses_20260812 as f
f.OUT_DIR=O/'broader_recompute';f.OUT_DIR.mkdir(exist_ok=True)
res={}
for name,fn in [('title_threshold',f.analyze_title_thresholds),('distributions',f.analyze_deduplicated_outputs),('human',f.analyze_human_sensitivity)]:
 print('START',name,flush=True);res[name]=fn();print('DONE',name,flush=True)
import run_english_benchmark as en
corpus=json.loads((P/'data/frozen_corpus_multidomain_v1.json').read_text(encoding='utf8'))
x=en.evaluate_outputs(['method1','method2a','method2b'],P/'data/english_benchmark',corpus);res['english']=en.summarise(x)
import run_alce_validation as wiki
wr=wiki.score_all_outputs();res['wiki']={k:{'n':len(v),**{m:statistics.mean(r[m] for r in v) for m in ['icp','ecp','orphan'] if m in v[0]}} for k,v in wr.items()}
import analyze_ipm_major_revision_v3 as major
res['claim_support']=major.claim_support_audit()
(O/'broader_results.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf8');print('DONE ALL',flush=True)
