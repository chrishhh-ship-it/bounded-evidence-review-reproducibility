from pathlib import Path
import json,csv
import numpy as np
from scipy.stats import bootstrap,wilcoxon
O=Path(__file__).resolve().parent
rows={k:{r['qid']:r for r in json.loads((O/(k+'_rows.json')).read_text(encoding='utf8'))} for k in ['M1','M2a','M2b','M2c','B0']}
tests=[]
for k in ['B0','M2a','M2b','M2c']:
    for m in ['citation_precision','bibliography_match_rate','orphan_rate']:
        ids=[q for q in sorted(rows['M1'].keys() & rows[k].keys()) if rows['M1'][q][m] is not None and rows[k][q][m] is not None]
        x=np.array([rows['M1'][q][m] for q in ids]);y=np.array([rows[k][q][m] for q in ids]);d=y-x
        t=wilcoxon(d,zero_method='pratt',alternative='two-sided')
        ci=bootstrap((d,),np.mean,method='BCa',confidence_level=.95,n_resamples=10000,random_state=np.random.default_rng(20260724)).confidence_interval
        tests.append(dict(comparison=k+'-M1',metric=m,n_pairs=len(d),mean_M1=float(x.mean()),mean_challenger=float(y.mean()),mean_difference=float(d.mean()),bca95_low=float(ci.low),bca95_high=float(ci.high),p_raw=float(t.pvalue)))
order=sorted(range(12),key=lambda i:tests[i]['p_raw']);acc=1
for rank in range(12,0,-1):
    i=order[rank-1];acc=min(acc,tests[i]['p_raw']*12/rank);tests[i]['p_bh_fdr']=acc
with (O/'paired_tests_corrected_pratt.csv').open('w',newline='',encoding='utf8') as f:
    w=csv.DictWriter(f,fieldnames=list(tests[0]));w.writeheader();w.writerows(tests)
print(json.dumps(tests,indent=2))
