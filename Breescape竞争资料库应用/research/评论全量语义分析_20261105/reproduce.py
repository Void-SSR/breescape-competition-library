# coding: utf-8
"""Deterministic aggregation of analyst-authored annotations. No text/star classifiers."""
from pathlib import Path
import json,csv,collections,hashlib
P=Path(__file__).resolve().parent
URL='https://shop.tiktok.com/us/pdp/bamboo-sheets-set-by-shilucheng-4-6-pc-cooling-deep-pocket-silky-soft/1729438233542234865'
S={r['id']:r for r in json.loads((P/'00_source_snapshot.json').read_text())}
A=[json.loads(x) for x in (P/'02_annotations.jsonl').read_text().splitlines()]
BOOK=json.loads((P/'01_theme_rules_v1.2.json').read_text());labels={r['code']:r['label'] for r in BOOK}
def dump(name,data):(P/name).write_text(json.dumps(data,ensure_ascii=False,indent=2))
def csvout(name,data):
 assert data
 with (P/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in data for k in r)));w.writeheader();w.writerows(data)
def valid(a):return a['dimension']=='theme' and a['subject']=='target_same_product' and a['valence'] in ('positive','negative')
def ids(rows,code,val,predicate=lambda a:True):return sorted({r['review_id'] for r in rows if any(valid(a) and a['code']==code and a['valence']==val and predicate(a) for a in r['annotations'])})
assert len(A)==len(S)==1628 and len({r['review_id'] for r in A})==1628 and {r['review_id'] for r in A}==set(S)
for r in A:
 assert r['source_group']==S[r['review_id']]['source_group']
 for a in r['annotations']:
  assert S[r['review_id']]['body'][a['quote_start']:a['quote_end']]==a['quote'],(r['review_id'],a)
  if a['dimension']=='theme':
   assert a['code'] in labels
   assert a['count_unit_key']==f"{r['review_id']}|{a['code']}|{a['valence']}"
   assert a['primary_count_eligible']==(valid(a) and a['code'].startswith('T'))
flat=[];reviewrows=[];stats=[];summary={}
for group in ['main_recent','extra_one_star','recommended']:
 rows=[r for r in A if r['source_group']==group and r['denominator_included']];n=len(rows)
 gs={'denominator':n,'date_min':min(S[r['review_id']]['date'] for r in rows),'date_max':max(S[r['review_id']]['date'] for r in rows),'rating_distribution':dict(collections.Counter(S[r['review_id']]['rating'] for r in rows)),'positive':[],'negative':[],'general':{}}
 for c in sorted(labels):
  if not c.startswith(('T','G')):continue
  for v in ['positive','negative']:
   found=ids(rows,c,v)
   if not found:continue
   item={'code':c,'label':labels[c],'count':len(found),'denominator':n,'percent':round(len(found)/n*100,2),'review_ids':found}
   stats.append({'source_group':group,'theme_type':'具体主题' if c.startswith('T') else '一般评价','valence':v,**{k:v for k,v in item.items() if k!='review_ids'},'review_ids':';'.join(map(str,found))})
   if c.startswith('T'):gs[v].append(item)
   else:gs['general'].setdefault(v,[]).append(item)
 for v in ['positive','negative']:gs[v].sort(key=lambda t:(-t['count'],t['code']))
 summary[group]=gs
for r in A:
 s=S[r['review_id']];themes=sorted({f"{a['code']}:{a['valence']}:{a['subject']}" for a in r['annotations'] if a['dimension']=='theme'})
 reviewrows.append(dict(review_id=r['review_id'],product_id=s['product_id'],product_url=URL,external_review_id=s['external_id'],date=s['date'],rating=s['rating'],sku=s['sku'],source_group=r['source_group'],source_files=s['source_files'],sample_scope=s['sample_scope'],overlap_one_star=s['overlap_one_star'],denominator_included=r['denominator_included'],body=s['body'],themes=';'.join(themes),purchase_signals=';'.join(a['code'] for a in r['annotations'] if a['dimension']=='purchase_signal'),behavior=';'.join(a['code'] for a in r['annotations'] if a['dimension']=='behavior'),notes=';'.join(r['notes'])))
 for a in r['annotations']:flat.append({'review_id':r['review_id'],'source_group':r['source_group'],'external_review_id':s['external_id'],'review_date':s['date'],'product_url':URL,**a})
csvout('04_逐条评论与编码.csv',reviewrows);csvout('04_全部证据标注.csv',flat);csvout('05_分来源主题统计.csv',stats);dump('05_statistics.json',summary)
main=[r for r in A if r['source_group']=='main_recent']
sens={}
for name,pred in [('primary',lambda a:True),('excluding_explicit_prior',lambda a:a['experience_phase']!='prior_same_product'),('explicit_current_only',lambda a:a['experience_phase']=='current_reference'),('excluding_relative_comparisons',lambda a:a['relation']!='relative')]:
 sens[name]={v:sorted([{'code':c,'n':len(ids(main,c,v,pred))} for c in labels if c.startswith('T')],key=lambda x:(-x['n'],x['code']))[:6] for v in ['positive','negative']}
sens['explicit_current_only']={'status':'not_identifiable_as_a_current_batch','recorded_explicit_current_theme_count':sum(1 for r in main for a in r['annotations'] if valid(a) and a['experience_phase']=='current_reference'),'reason':'主样本未普遍明确前次/本次对照；多数为未限定阶段，不应输出0作为当前产品体验结果，也不能据评论日期判定生产批次。'}
sens['current_only_warning']='current_reference仅记录明确前后对象对照时的本次指代，标注稀少且不代表同一生产批次；不能拿此小子集估计当前产品满意度。excluding_explicit_prior只表示剔除明确历史，并不证明剩余全是当前批次。'
sens['ambiguity_ceiling']={v:[{'code':c,'clear':len(ids(main,c,v)),'upper_if_every_uncertain_assigned_this_valence':len(set(ids(main,c,v))|{r['review_id'] for r in main if any(a['code']==c and a['valence']=='uncertain' and a['subject']=='target_same_product' for a in r['annotations'])})} for c in ['T01','T03','T07','T09','T08','T06']] for v in ['positive','negative']}
groups={'触感':['T01','T02','T16'],'热湿':['T03','T04','T32'],'适配与固定':['T07','T08','T38','T39'],'颜色':['T09','T10','T41','T45'],'价格价值':['T28','T29'],'使用稳定性与缝制':['T11','T12','T13','T14','T15','T46']}
sens['broader_categories']={v:sorted([{'group':g,'codes':codes,'count':len({r['review_id'] for r in main if any(valid(a) and a['valence']==v and a['code'] in codes for a in r['annotations'])})} for g,codes in groups.items()],key=lambda x:-x['count']) for v in ['positive','negative']}
knownpairs=[[50,51],[640,641],[698,699],[855,856],[1027,1028],[1055,1056],[1141,1143],[1205,1206],[1525,1526]]
sens['known_similar_text_pairs']=[{'review_ids':pair,'external_ids':[S[i]['external_id'] for i in pair],'decision':'不同平台ID，未删除；相似文字不足证明重复或独立买家'} for pair in knownpairs]
exact=collections.defaultdict(list)
for s in S.values():exact[' '.join(s['body'].casefold().split())].append(s['id'])
sens['exact_text_clusters']=[v for v in exact.values() if len(v)>1]
# Hypothetical collapse of known near-text groups: not data deletion.
drop={pair[1] for pair in knownpairs};dedup=[r for r in main if r['review_id'] not in drop]
sens['known_similar_text_pair_collapse_sensitivity']={'denominator':len(dedup),'top':{v:sorted([{'code':c,'count':len(ids(dedup,c,v))} for c in labels if c.startswith('T')],key=lambda x:(-x['count'],x['code']))[:4] for v in ['positive','negative']},'warning':'仅演示，非声称已证重复；正式分母不变。'}
# Positive temperature manifestations manually reviewed, temperature is not identical to cooling.
sens['thermal_breakdown']={}
for group in summary:
 rows=[r for r in A if r['source_group']==group]
 for v in ['positive','negative']:
  themes=[(r['review_id'],a) for r in rows for a in r['annotations'] if valid(a) and a['code']=='T03' and a['valence']==v]
  buckets=collections.defaultdict(set)
  for i,a in themes:buckets[a.get('thermal_meaning','cooling_or_heat_sweat_experience')].add(i)
  sens['thermal_breakdown'][group+'_'+v]={k:{'count':len(vv),'review_ids':sorted(vv)} for k,vv in buckets.items()}
dump('05_sensitivity.json',sens)
# Behavior groups are explicit code mappings, not natural-language extraction.
bgroups={'self_report_repeat':['repeat_actual','repeat_reported_prior_and_current'],'possible_repeat_sequence_uncertain':['repeat_sequence_uncertain'],'repeat_intent':['repeat_intent','color_expansion_intent','household_replace_intent','additional_sizes_intent','family_purchase_intent','repeat_conditional_price','repeat_conditional_stock'],'multiple_sets_without_order_sequence':['multiple_sets_timing_unknown','multiple_colors_timing_unknown','multiple_sets_purchased','multiple_sets_owned','multiple_colors_purchased'],'store_repeat_only':['repeat_brand_reported'],'store_multiple_sequence_uncertain':['store_multiple_sequence_uncertain']}
behavior={}
for group in summary:
 rows=[r for r in A if r['source_group']==group];behavior[group]={}
 for name,codes in bgroups.items():
  found=sorted({r['review_id'] for r in rows if any(a['dimension']=='behavior' and a['code'] in codes for a in r['annotations'])});behavior[group][name]={'count':len(found),'review_ids':found,'codes':codes}
dump('05_behavior_counts.json',behavior)
csvout('04_购买线索.csv',[x for x in flat if x['dimension']=='purchase_signal']);csvout('04_行为与使用情境.csv',[x for x in flat if x['dimension'] in ('behavior','context')])
# Versioned rulebooks are inputs; never overwrite historical v1.1.
with (P/'01_主题规则表.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['代码','主题','类型','纳入条件','排除条件'])
 for r in BOOK:w.writerow([r['code'],r['label'],r['role'],r['include'],r['exclude']])
# Provenance and integrity checks.
nonempty=[s['external_id'] for s in S.values() if s['external_id']]
assert len(nonempty)==len(set(nonempty))
manifest=json.loads((P/'00_protection_manifest.json').read_text());base=P.parent.parent;changed=[];missing=[]
for rel,digest in manifest.items():
 f=base/rel
 if not f.exists():missing.append(rel)
 elif hashlib.sha256(f.read_bytes()).hexdigest()!=digest:changed.append(rel)
blind=json.loads((P/'03_blind_labels_part1.json').read_text())+json.loads((P/'03_blind_labels_part2.json').read_text())
assert {i for i,_ in blind}==set(json.loads((P/'03_blind_sample_ids.json').read_text()))
diffs=json.loads((P/'03_blind_differences.json').read_text())
validation={'reviews':len(A),'annotation_rows':len(flat),'all_quotes_exact':True,'all_review_ids_present_once':True,'nonempty_external_ids':len(nonempty),'distinct_nonempty_external_ids':len(set(nonempty)),'missing_external_ids':len(S)-len(nonempty),'changed_protected_files':changed,'missing_protected_files':missing,'blind_reread_reviews':len(blind),'first_vs_second_theme_set_disagreements':len(diffs),'disclaimer':'同一分析者二读，不是独立编码者一致性，也不是准确率；第二轮先隐藏旧标签，但无法排除记忆影响。','blind_reread_scope':'v1.1既有163条通用二读；v1.2仅做已批准的定向复核，无重复抽样','analysis_versions':{'rule':'1.2','source_snapshot_sha256':hashlib.sha256((P/'00_source_snapshot.json').read_bytes()).hexdigest(),'annotation_sha256':hashlib.sha256((P/'02_annotations.jsonl').read_bytes()).hexdigest()}}
dump('06_validation.json',validation)
print(json.dumps({g:{'n':d['denominator'],'positive':[(x['code'],x['count'],x['percent']) for x in d['positive'][:4]],'negative':[(x['code'],x['count'],x['percent']) for x in d['negative'][:4]],'general':{v:[(x['code'],x['count']) for x in ls] for v,ls in d['general'].items()}} for g,d in summary.items()},ensure_ascii=False,indent=2))
print('BEHAVIOR',json.dumps(behavior,ensure_ascii=False));print('VALIDATION',json.dumps(validation,ensure_ascii=False));print('BROADER',json.dumps(sens['broader_categories'],ensure_ascii=False));print('THERMAL', {k:{kk:vv['count'] for kk,vv in v.items()} for k,v in sens['thermal_breakdown'].items()})
