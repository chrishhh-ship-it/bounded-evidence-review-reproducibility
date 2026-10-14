from pathlib import Path
import json,statistics,collections,csv,re,sys,ast
P=Path(r'D:\文献\研究情报助手');O=Path(__file__).resolve().parent;queries={int(q['id'][1:]):q for q in json.loads((P/'data/benchmarks/benchmark_all_queries.json').read_text(encoding='utf8'))};res={'domains':{},'sources':{}}
for cfg in ['M1','M2a','M2b','M2c']:
 rows=json.loads((O/f'{cfg}_rows.json').read_text(encoding='utf8'));res['domains'][cfg]={}
 for domain in sorted(set(q['domain_id'] for q in queries.values())):
  rr=[r for r in rows if queries[int(r['qid'][1:])]['domain_id']==domain];cp=[r['citation_precision'] for r in rr if r['citation_precision'] is not None];clr=[r['linkage'] for r in rr if r['linkage'] is not None]
  res['domains'][cfg][domain]={'n':len(rr),'cp_n':len(cp),'cp':statistics.mean(cp),'clr_n':len(clr),'clr':statistics.mean(clr)}
for k,f in [('pilot','data/topic_runs/multi_agent_intel_service_20260410_114059/retrieved_papers_wave3.json'),('expanded','data/frozen_corpus_multidomain_v1.json')]:
 rows=json.loads((P/f).read_text(encoding='utf8'));res['sources'][k]={'n':len(rows),'sources':dict(collections.Counter(r.get('source') for r in rows)),'domains':dict(collections.Counter(r.get('domain_id') for r in rows)),'abstracts':sum(bool(r.get('abstract')) for r in rows)}
V=P/'data/reports/ipm_major_revision_20260721/repro/v3';rr=list(csv.DictReader((V/'out_of_boundary_external_verification.csv').open(encoding='utf-8-sig')));res['registry']={'n':len(rr),'unique':dict(collections.Counter(r['status'] for r in rr)),'occurrences':dict(collections.Counter({k:sum(int(r['occurrences']) for r in rr if r['status']==k) for k in set(r['status'] for r in rr)}))}
sys.path.insert(0,str(P/'scripts'));import evaluate_metrics as em
b0=[]
files=em._select_latest_per_query(em._filter_result_files(list((P/'data/expanded_outputs/schema_single_agent_v1').glob('*.md')),'schema_single_agent',em._parse_query_ids('Q01-Q251')))
for md in files.values():
 p=md.with_suffix('.json')
 d=json.loads(p.read_text(encoding='utf8'))
 if 'elapsed_seconds' in d:b0.append(d['elapsed_seconds'])
res['b0_elapsed']={'n':len(b0),'mean':statistics.mean(b0),'median':statistics.median(b0),'min':min(b0),'max':max(b0)}
# Recompute NLI summaries from saved pair probabilities and raw outputs; never rerun a model.
ns={'re':re};tree=ast.parse((P/'scripts/run_complete_semantic_audit.py').read_text(encoding='utf8'))
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in ['split_claims','cited_pairs']:exec(compile(ast.Module(body=[node],type_ignores=[]),'saved_parser','exec'),ns)
nli=json.loads((P/'data/reports/ipm_major_revision_20260721/completion_5678_20260726/external_semantic_completion.json').read_text(encoding='utf8'))['alce_full_local_nli'];raw=json.loads((P/'data/external_benchmarks/alce_official_pilot_n40_structural/alce_official_pilot_outputs.json').read_text(encoding='utf8'));res['nli']={}
for key,summary in nli['conditions'].items():
 ds,cond=key.split('::');rr=[r for r in nli['pair_scores'] if r['dataset']==ds and r['condition']==cond];items=[x for x in raw if x['dataset']==ds and x['condition']==cond];pairs=[p for x in items for p in ns['cited_pairs'](x)[0]]
 assert [(r['claim'],r['premise']) for r in rr]==[(r['claim'],r['premise']) for r in pairs]
 n_sent=sum(len(ns['split_claims'](x)) for x in items)
 val={'pairs':len(rr),'sentences':n_sent,'cited_sentence_rate':len(pairs)/n_sent,'claim_entailment_rate':statistics.mean(r['entailment_probability']>=.5 for r in rr),'mean_entailment_probability':statistics.mean(r['entailment_probability'] for r in rr)}
 val['summary_comparison']={k: {'recomputed':v,'stored':summary[k],'match':abs(v-summary[k])<1e-10} for k,v in val.items()}
 res['nli'][key]=val
(O/'domain_source_nli_results.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf8');print('M2c effective n',res['domains']['M2c']);print('B0',res['b0_elapsed']);print('NLI pair identity verified; stored summary mismatches are recorded explicitly')



