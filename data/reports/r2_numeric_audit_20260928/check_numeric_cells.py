from pathlib import Path
import json,csv,re,statistics,collections,sys
R=Path(__file__).resolve().parents[1];O=R/'audit';P=R.parents[2];s=(R/'source/main.tex').read_text(encoding='utf8');checks=[]
def j(n):return json.loads((O/n).read_text(encoding='utf8'))
def block(label):
 i=s.index('\\label{'+label+'}');return s[s.rfind('\\begin{table}',0,i):s.index('\\end{table}',i)]
def row(label,prefix,vals,kind='raw_record_recomputed'):
 b=block(label);lines=b.splitlines();i=next(i for i,x in enumerate(lines) if x.strip().startswith(prefix));ln=lines[i]
 while '\\\\' not in ln: i+=1;ln+=' '+lines[i]
 cells=ln.split('&')[1:]
 assert len(cells)>=len(vals),(label,prefix,cells)
 for k,(cell,v) in enumerate(zip(cells,vals)):
  if v is None:continue
  st=re.sub(r'\\phantom\{[^}]*\}', '',cell.replace(',',''));m=re.search(r'(?<![A-Za-z])[-+]?(?:\d+(?:\.\d+)?|\.\d+)',st)
  assert m,(label,prefix,cell)
  t=m[0];display=float(t);places=len(t.split('.')[1]) if '.' in t else 0;tol=.5*10**(-places)+1e-9
  good=abs(display-v)<=tol
  checks.append({'table':label,'row':prefix,'cell':k+1,'displayed':display,'recomputed':v,'rounding_tolerance':tol,'pass':good,'basis':kind})
# Corpus and taxonomy.
rem=j('remaining_audit.json');ft=j('fulltext_file_validation.json')
for label,dom in [('Multi-agent','multi_agent_information_services'),('Biomedical','biomedical_evidence_synthesis'),('Digital','digital_humanities'),('Climate','climate_policy_research')]:
 d=rem['corpus_counts'][dom];row('tab:corpus',label,[d['papers'],d['abstracts'],ft['readable_pdf_domains'].get(dom,0),d['queries']])
row('tab:corpus',r'\textbf{Total}',[3011,2582,ft['readable_pdf_n'],251])
rr=j('table19_table20_verified.json');cs=rr['table19']['M1']
for lab,cat in [('Competitive','competitive_intelligence'),('Retrieval','retrieval'),('Evaluation','evaluation'),('Full-Text','full_text'),('Report Writing','writing'),('Agent Roles','agent_roles'),('Cost Efficiency','cost_efficiency'),('Benchmark Design','benchmark'),('Knowledge Service','knowledge_service')]:row('tab:taxonomy',lab,[cs[cat]['n']])
a=j('independent_results.json')['summaries']
for lab,key in [('Core workflow','pilot_M1_Q01_Q30'),('Cross-model','pilot_M2a_Q01_Q30'),('Same-model','pilot_M2b_Q01_Q30')]:row('tab:main_results',lab,[a[key][v]*100 for v in ['citation_precision','bibliography_match_rate','orphan_rate']])
row('tab:main_results','Baseline B',[None,None,a['B']['orphan_rate']*100])
for lab,key in [('Core workflow','pilot_M1'),('Cross-model','pilot_M2a'),('Same-model','pilot_M2b')]:
 raw=j(key+'_rows.json');row('tab:pilot_ext',lab,[a[key][v]*100 for v in ['citation_precision','bibliography_match_rate','orphan_rate']]+[statistics.mean(r['section_completeness'] for r in raw)*100])
for lab,key in [('Core workflow','pilot_M1'),('Self-critique','pilot_M3'),('CoT verification','pilot_M4'),('Same-model','pilot_M2b'),('Cross-model','pilot_M2a')]:row('tab:arch_compare',lab,[a[key]['citation_precision']*100,a[key]['orphan_rate']*100])
for key,lab in [('M1','Method 1'),('M2a','Method 2a'),('M2b','Method 2b'),('M2c','Method 2c')]:
 raw=j(key+'_rows.json');row('tab:expanded_results',lab,[251]+[a[key][v]*100 for v in ['citation_precision','bibliography_match_rate','orphan_rate']]+[statistics.mean(r['abstract_coverage'] for r in raw)*100])
for key in ['B0','M1','M2a','M2b','M2c']:row('tab:matched_reanalysis',key+':',[a[key]['n']]+[a[key][v]*100 for v in ['citation_precision','bibliography_match_rate','orphan_rate','gate']])
# Domain row repeats in two panels; test each separate occurrence.
dn=j('domain_source_nli_results.json')
b=block('tab:expanded_domain_breakdown')
for lab,dom in [('Multi-agent','multi_agent_information_services'),('Digital','digital_humanities'),('Biomedical','biomedical_evidence_synthesis'),('Climate','climate_policy_research')]:
 ls=[x for x in b.splitlines() if x.startswith(lab)]
 for line,metric in zip(ls,['cp','clr']):
  nums=[float(re.search(r'\d+\.\d+',x)[0]) for x in line.split('&')[1:]]
  for k,v in zip(['M1','M2a','M2b','M2c'],nums):checks.append({'table':'tab:expanded_domain_breakdown','row':dom+' '+k+' '+metric,'cell':0,'displayed':v,'recomputed':dn['domains'][k][dom][metric]*100,'rounding_tolerance':.05,'pass':abs(v-dn['domains'][k][dom][metric]*100)<=.050000001,'basis':'raw_record_recomputed'})
add=j('additional_results.json')
for lab,key in [('Single-agent','single_agent_label'),('Cross-model','arl_label')]:
 d=add['title'][key];row('tab:title_identity_audit',lab,[d['accuracy']*100,d['macro_f1'],d['kappa']])
for c in ['V0','V1','V2']:
 d=add['semantic'][c];cnt=d['labels'];row('tab:matched_semantic_audit',c,[60,60-cnt.get('REMOVED',0),cnt.get('REMOVED',0),cnt.get('SUPPORTED',0),cnt.get('PARTIAL',0),cnt.get('INSUFFICIENT',0)+cnt.get('CONTRADICTED',0),cnt.get('SUPPORTED',0)/60*100])
br=j('broader_results.json')
for v in br['title_threshold']['overall']:row('tab:title_threshold_sensitivity',str(v['threshold']),[v[k] for k in ['predicted_match','tp','fp','fn','tn','precision','recall','f1','accuracy']])
for lab,key in [('Method~1','pilot_M1_Q01_Q30'),('\\textbf{CDMA+ARL','pilot_M2a_Q01_Q30')]:row('tab:autosurvey_comparison',lab,[30]+[a[key][v]*100 for v in ['citation_precision','orphan_rate','bibliography_match_rate']])
for lab,key in [('AutoSurvey (controlled','controlled'),('AutoSurvey (native, w/','native'),('AutoSurvey (native, no','nocheck')]:
 d=rem['autosurvey'][key];row('tab:autosurvey_comparison',lab,[d['n']]+[d[k]*100 for k in ['citation_precision','orphan_rate','bibliography_match_rate']])
for lab,key in [('ASQA: index','asqa_citation_index_validity'),('ASQA: sentence','asqa_sentence_citation_coverage'),('QAMPARI: index','qampari_citation_index_validity'),('QAMPARI: sentence','qampari_sentence_citation_coverage')]:
 d=add['alce'][key];row('tab:alce_structural',lab,[d['v0']*100,d['v2']*100,d['difference']*100,d['up'],d['down'],d['same']])
for key,v in dn['nli'].items():
 ds,c=key.split('::');row('tab:local_nli_audit',ds.upper()+' / '+c.upper(),[v['pairs'],v['cited_sentence_rate']*100,v['claim_entailment_rate']*100,v['mean_entailment_probability']])
for lab,cat in [('competitive\\_intel.','competitive_intelligence'),('cost\\_efficiency','cost_efficiency'),('evaluation','evaluation'),('full\\_text','full_text'),('retrieval','retrieval'),('benchmark','benchmark'),('knowledge\\_service','knowledge_service'),('writing','writing'),('agent\\_roles','agent_roles'),('\\textbf{Overall}','Overall')]:
 d=rr['table19']['M1'][cat];e=rr['table19']['M2a'][cat];row('tab:per_category',lab,[d['n'],d['n_cp'],d['cp']*100,d['or']*100,e['cp']*100,e['or']*100])
for lab,key in [('Baseline A','Baseline A'),('Baseline B','Baseline B'),('Core workflow','M1'),('Cross-model review','M2a'),('Same-model review','M2b')]:
 d=rr['table20'][key];row('tab:cost',lab,[d['n_elapsed'],d['median'],d['q1'],d['q3']])
for lab,k in [('Method 1','method1'),('Method 2a','method2a'),('Method 2b','method2b')]:
 d=br['english'][k];row('tab:english_results',lab,[d['icp_mean'],d['ecp_mean'],d['orphan_mean']])
for source in ['OpenAlex','arXiv','CrossRef','Google Scholar','Semantic Scholar','Scopus','PubMed','Wanfang Data']:
 k='万方数据' if source=='Wanfang Data' else source;row('tab:source_provenance',source,[dn['sources'][c]['sources'].get(k,0) for c in ['pilot','expanded']])
# Wiki table uses macros: verify each macro literal.
for macro,key,metric in [('WIKIICPM','m1_vanilla','icp'),('WIKIECPM','m1_vanilla','ecp'),('WIKIOROM','m1_vanilla','or'),('WIKIICPB','m2b_cdma_arl','icp'),('WIKIECPB','m2b_cdma_arl','ecp'),('WIKIOROB','m2b_cdma_arl','or'),('WIKIICPA','m2a_cdma_arl','icp'),('WIKIECPA','m2a_cdma_arl','ecp'),('WIKIORA','m2a_cdma_arl','or')]:
 v=float(re.search(r'\\newcommand\{\\'+macro+r'\}\{([\d.]+)',s)[1]);x=rem['wiki'][key][metric]*100;checks.append({'table':'tab:wiki_validation','row':macro,'cell':0,'displayed':v,'recomputed':x,'rounding_tolerance':.05,'pass':abs(v-x)<.050000001,'basis':'raw_record_recomputed'})

# Human descriptive outcomes: complete-case scores, all available rankings/suspicion.
responses=list(csv.DictReader((P/'data/user_study/raw_responses_n30.csv').open(encoding='utf-8-sig')))
for lab,c,key in [('CDMA+ARL','C','M2a'),('Core CDMA','A','M1'),('Same-model','B','M2b')]:
 ranks=[pos for r in responses for pos,col in enumerate(['rank_1st_system','rank_2nd_system','rank_3rd_system'],1) if r[col]==c];h=br['human']['primary_complete_case']['descriptive'][key]
 row('tab:human_eval',lab,[a['pilot_'+key+'_Q01_Q30']['orphan_rate']*100,sum(r['rank_1st_system']==c for r in responses)/len(responses)*100,statistics.mean(ranks),h['mean'],h['sd'],sum(r['suspicious_system']==c for r in responses)/len(responses)*100])
# Explicitly distinguish archived aggregate agreement from raw reconstruction.
bil=json.loads((P/'data/bilingual_exp/retrieval_metrics_agg.json').read_text(encoding='utf8'))['overall']
for lab,k in [('C1:','zh'),('C2:','en'),('C3:','union')]:
 vals=[bil['size_'+k],bil['acr_'+k]*100,bil['dcr_'+k]*100,bil['src_div_'+k]]
 if k=='union':vals += [bil['bcu_pct'],bil['clg_pct']]
 row('tab:bilingual_retrieval',lab,vals,'archived_aggregate_only_not_raw_recomputed')
# All median/IQR cells of Table 9.
dis=list(csv.DictReader((O/'broader_recompute/deduplicated_output_summary.csv').open(encoding='utf-8-sig')))
for prefix,d in zip(['Method 1','Method 2a','Method 2b','Method 2c'],dis):
 line=next(x for x in block('tab:output_distributions').splitlines() if x.startswith(prefix));cells=line.split('&')[1:]
 groups=[[8,8,8]]+[[float(d[m+'_'+stat]) for stat in ['median','q1','q3']] for m in ['citations_per_output','output_length_chars','citation_density_per_bib']]+[[251]]
 for ci,(cell,values) in enumerate(zip(cells,groups)):
  strings=re.findall(r'\d+(?:\.\d+)?',cell);assert len(strings)==len(values)
  for st,v in zip(strings,values):
   digits=len(st.split('.')[1]) if '.' in st else 0;tol=.5*10**-digits+1e-9;dv=float(st);checks.append({'table':'tab:output_distributions','row':prefix,'cell':ci+1,'displayed':dv,'recomputed':v,'rounding_tolerance':tol,'pass':abs(dv-v)<=tol,'basis':'raw_record_recomputed'})

# Table 14 contains multiple numbers in a single result cell.
reg=dn['registry'];u=reg['unique'];occ=reg['occurrences']
specs=[('External registry, unique entries',[reg['n'],u['verified_genuine_but_unretrieved'],u['probable_genuine_requires_manual_check'],u['unresolved_external']]),
('External registry, occurrences',[sum(occ.values()),occ['verified_genuine_but_unretrieved'],100*occ['verified_genuine_but_unretrieved']/sum(occ.values())])]
for name,key in [('Claim support, M1','M1'),('Claim support, M2a','M2a')]:
 d=br['claim_support']['methods'][key];specs.append((name,[d['n'],d['majority_label_distribution']['E'],100*d['entailed_rate']]))
for name,vals in specs:
 b=block('tab:external_semantic_audits');start=b.index(name);line=b[start:b.index('\\',start)];numeric='&'.join(line.split('&')[1:3]).replace(',','');strings=re.findall(r'\d+(?:\.\d+)?',numeric);assert len(strings)==len(vals),(name,strings)
 for k,(st,v) in enumerate(zip(strings,vals)):
  digits=len(st.split('.')[1]) if '.' in st else 0;tol=.5*10**-digits+1e-9;dv=float(st);checks.append({'table':'tab:external_semantic_audits','row':name,'cell':k+1,'displayed':dv,'recomputed':v,'rounding_tolerance':tol,'pass':abs(dv-v)<=tol,'basis':'raw_record_recomputed'})

with (O/'NUMERIC_CELL_LEDGER.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=checks[0]);w.writeheader();w.writerows(checks)
fail=[x for x in checks if not x['pass']];print('Checked',len(checks),'numeric cells; failures',fail);assert not fail
(O/'numeric_cell_check_summary.json').write_text(json.dumps({'cells':len(checks),'passed':len(checks)-len(fail),'failed':fail,'tables_with_numeric_cell_checks':sorted(set(c['table'] for c in checks))},indent=2),encoding='utf8')
