# coding: utf-8
"""Replay the approved, analyst-authored targeted corrections from sealed v1.1.
No keyword/star classification. All review decisions below were made by reading originals.
"""
from pathlib import Path
import json,copy,hashlib
P=Path(__file__).resolve().parent
B=P/'revisions'/'v1.1_submitted_before_targeted_20261105'
manifest=json.loads((B/'SNAPSHOT_MANIFEST.json').read_text())
assert all(hashlib.sha256((B/f).read_bytes()).hexdigest()==h for f,h in manifest.items())
S={r['id']:r for r in json.loads((B/'00_source_snapshot.json').read_text())}
base=[json.loads(x) for x in (B/'02_annotations.jsonl').read_text().splitlines()]
D={r['review_id']:copy.deepcopy(r) for r in base};changes=[]
def dump(name,obj):(P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2))
def edit(i,rule,reason,fn):
 before=copy.deepcopy(D[i]);fn(D[i]);after=copy.deepcopy(D[i]);assert before!=after,(i,reason)
 changes.append(dict(review_id=i,rule=rule,reason=reason,before=before,after=after))
def recode_behavior(i,old_codes,new_code,reason,quote=None):
 def f(r):
  found=[a for a in r['annotations'] if a['dimension']=='behavior' and a['code'] in old_codes];assert len(found)==1,(i,found)
  a=found[0];a.update(code=new_code,note=reason)
  if quote is not None:
   a['quote']=quote;a['quote_start']=S[i]['body'].index(quote);a['quote_end']=a['quote_start']+len(quote)
 edit(i,'purchase_sequence',reason,f)
def add_ann(i,dimension,code,val,quote,note='',component='unspecified_product_or_set',**kw):
 start=S[i]['body'].index(quote)
 a=dict(dimension=dimension,code=code,valence=val,quote=quote,note=note,subject='target_same_product',experience_phase='unspecified',component=component,relation='absolute_or_unspecified',primary_count_eligible=dimension=='theme' and code.startswith('T') and val in ('positive','negative'),count_unit_key=f'{i}|{code}|{val}' if dimension=='theme' else '',quote_start=start,quote_end=start+len(quote));a.update(kw);return a
# 73 purchase-history candidates: 35 previously classified repeat, 36 multiple-set, 2 store-level.
old_behavior=json.loads((B/'05_behavior_counts.json').read_text())
confirmed_main=[5,28,57,101,110,221,476,499,531,557,580,612,629]
confirmed_extra=[1012,1103,1408,1505,1519,1580]
possible_from_repeat=[45,60,132,298,419,484,620,631,681,685,762,808,824,836,893,1284]
possible_from_multiple=[8,99,206,240,241,337]
specific_reasons={
132:'this is our third order后接pretty soon，可能描述既有第三单，也可能将至；保留可能再购，不计明确已发生。',
298:'喜欢后为自己及赠礼购买是扩展用途线索，未明确这些购买分属不同订单。',
484:'第三套及质量比较能说明多套与差异，未明确下单次数或先使用再追加购买。',
631:'比较1st step i ordered存在措辞笔误及订单/套数组合歧义；不将其确定为不同订单。',
762:'与first set比较可说明不同套体验，但不能排除同单多套后依次使用。',
1284:'明确同款不同颜色的先前体验；但没有明确先使用后再次下单的顺序，历史体验标签保留。'
}
for i in possible_from_repeat:
 reason=specific_reasons.get(i,'仅明确第几套/对或已买套数，不等于第几次购买；不能从套数推订单顺序。')
 recode_behavior(i,{'repeat_actual','repeat_reported_prior_and_current'},'repeat_sequence_uncertain',reason)
for i in possible_from_multiple:
 recode_behavior(i,{'multiple_sets_timing_unknown','multiple_colors_timing_unknown','multiple_sets_purchased','multiple_sets_owned','multiple_colors_purchased'},'repeat_sequence_uncertain','第几套/个是可能再购线索，但缺少分次订单或使用后再下单的明确顺序；不静默丢弃。')
recode_behavior(287,{'repeat_brand_reported'},'store_multiple_sequence_uncertain','只说同店第二套，既不能确认同款，也不能确认两次下单。')
def fix_purchase_signal(r):
 found=[a for a in r['annotations'] if a['dimension']=='purchase_signal' and a['code']=='prior_experience_repeat'];assert len(found)==1
 found[0].update(code='experience_linked_gift_self_purchase',note='喜欢与自用/赠礼购买扩展有关；订单顺序不明，不能当明确分次复购原因。')
edit(298,'purchase_sequence','购买线索同步降为用途扩展，不再以未确认的再购为前提。',fix_purchase_signal)
# Confirmed repeat evidence quotes and rationale; a completed reported action, not verified transactions.
confirmed_quotes={5:'second time ordering',28:'I came back for another color for winter.',57:'My third purchase',101:'I ended up ordering two more sets!',110:'I had to buy a second one',221:'went back and ordered a SECOND set',476:'Bought them twice',499:'I purchased one just to test and fell in love with it since then, I’ve gotten 5 more.',531:'I ordered a 2nd set the next morning.',557:'I had to order more',580:'I’ve now ordered twice',612:'just bought more',629:"This purchase doesn't compare to my 1st order",1012:'I then purchased them in white',1103:'previous purchase',1408:'it was soft so I ordered the dark Grey',1505:'my second Purchase',1519:'I bought these pink sheets because I bought the identical white ones',1580:'So I ordered a different color the second time'}
behavior_review=[]
for group in ['main_recent','extra_one_star']:
 for category in ['self_report_repeat','multiple_sets_without_order_sequence','store_repeat_only']:
  for i in old_behavior[group][category]['review_ids']:
   if i in confirmed_quotes:
    final='explicit_repeat_report';reason='明示购买次数/订单，或已发生的追加购买动作与先前体验相衔接；仍仅自述。';quote=confirmed_quotes[i]
   elif i in possible_from_repeat+possible_from_multiple:
    final='possible_repeat_sequence_uncertain';reason=specific_reasons.get(i,'套数序号不等于购买次数；保留较弱再购线索。');quote=next(a['quote'] for a in D[i]['annotations'] if a['code']=='repeat_sequence_uncertain')
   elif i==37:final='store_repeat_product_uncertain';reason='明确同店以前下单与本次尺寸变化，目标同款身份仍不足。';quote='I had ordered from y’all before'
   elif i==287:final='store_multiple_sequence_uncertain';reason='同店第二套，不足证明目标同款或订单顺序。';quote='second pair of sheets from this company'
   else:final='multiple_sets_only';reason='已买/持有多套或多色，但没有可判定的分次/先后顺序。';quote=S[i]['body']
   assert quote in S[i]['body']
   behavior_review.append(dict(review_id=i,source_group=group,previous_group=category,final_group=final,quote=quote,reason=reason))
assert len(behavior_review)==73 and len({r['review_id'] for r in behavior_review})==73
# 110 explicit-size negative candidates read in full; do not infer fit dimensions from slipping alone.
fit_scope=[r['review_id'] for r in base if any(a['code']=='T07' and a['valence']=='negative' and a['subject']=='target_same_product' for a in r['annotations'])]
assert len(fit_scope)==110
remove_fit={
517:('I thought they were "deep pocketed".','12英寸床垫上滑脱加原先深口袋期待，没有直接描述实际口袋浅或尺寸不合。'),
523:("Doesn’t hold on a deep mattress like advertised.",'说在深床垫上固定不住，未明确尺寸或口袋实际深度不足。'),
559:('it should fit as described','应该按描述适配是规范性期待，明确发生的是固定不住，不倒推尺寸。'),
875:('I measured to make sure they would be “deep enough”','事先测量以确认深度不能证明收到的尺寸不足，明确结果为滑脱。'),
884:('Not good elastic on the fitted sheet','明确松紧带差和滑脱，14英寸仅使用情境，未说太小或口袋浅。'),
1241:('So do not see how it would fit a 16” mattress as claimed.','由12英寸上滑脱质疑16英寸适配，是推测性容量怀疑，非直接尺寸不合体验。')}
for i,(quote,reason) in remove_fit.items():
 def f(r,i=i,quote=quote,reason=reason):
  old=[a for a in r['annotations'] if a['code']=='T07' and a['valence']=='negative'];assert len(old)==1
  r['annotations']=[a for a in r['annotations'] if not(a['code']=='T07' and a['valence']=='negative')]
  r['annotations'].append(add_ann(i,'context','fit_expectation_or_mattress_context','not_applicable',quote,reason))
 edit(i,'fit_not_inferred_from_slip',reason,f)
fit_review=[]
for i in fit_scope:
 original=next(a for a in next(r for r in base if r['review_id']==i)['annotations'] if a['code']=='T07' and a['valence']=='negative')
 reason=remove_fit[i][1] if i in remove_fit else '原文有直接尺寸、深度、贴合或适配结构的负面/预期落差，不只从滑脱推导；保留自述口径。'
 if i in [1205,1206,1293,1369]:reason='明确split king结构与预期不同；保留结构预期落差，不认定实际尺寸太小或发错商品。'
 if i==1176:reason='not fitted为直接但未细分的贴合/结构抱怨；保留笼统适配，不推断具体尺寸或漏发床笠。'
 if i==1080:reason='cal king却fits like a king是明确比较/预期尺寸评价；不认定Cal King所有方向都更大。'
 fit_review.append(dict(review_id=i,source_group=S[i]['source_group'],decision='remove_T07_negative' if i in remove_fit else 'retain_T07_negative',quote=original['quote'],reason=reason))
# Component precision: no extra counting for multiple parts within a review.
component_updates={358:{'positive':('fitted_sheet','explicit','The fitted sheet has a nice deep pocket')},444:{'negative':('flat_sheet','explicit_top_sheet','Top sheet')},579:{'negative':('fitted_sheet','explicit','fitted Sheet')},797:{'negative':('fitted_sheet','explicit','on the fitted')},811:{'negative':('fitted_sheet','explicit','The fitted sheet')},888:{'positive':('fitted_sheet','explicit','fitted sheet is perfect'),'negative':('other_sheet_in_set','inferred_contrast_not_explicitly_flat_sheet','sheet itself is entirely toooooo small')},963:{'negative':('fitted_sheet','explicit','fitted sheet')},1195:{'negative':('set','explicit_multiple_parts','queen bed or pillows')},1558:{'negative':('fitted_sheet','explicit','Fitted sheet')},1571:{'negative':('fitted_sheet','explicit','The fitted sheet')},1598:{'negative':('fitted_sheet','explicit','fitted sheet')}}
for i,updates in component_updates.items():
 def f(r,i=i,updates=updates):
  for a in r['annotations']:
   if a['code']!='T07' or a['valence'] not in updates:continue
   comp,certainty,evidence=updates[a['valence']]
   if i==358 and evidence not in a['quote']:continue
   a.update(component=comp,component_certainty=certainty)
   if i==888 and a['valence']=='negative':a['note']='与明确床笠形成对照，推定套内另一张床单；原文没明确写flat/top，不强断言上床单。'
   if i==1195:a['component_detail']=['bed_sheet_unspecified','pillowcase'];a['note']='床单对床、枕套对枕头均称不合；同方向仍按该评论计一次。'
 edit(i,'component_precision','仅细分部件/指代确定性，不增减同条同方向计数。',f)
# T49 existing theme: fabric extensibility vs elastic-band performance are separate components.
elastic_decisions={
138:('retain_T38_only','预期松紧绑带缺失属于结构与说明不符，没有报告弹性失效。'),
143:('add_T49_band_negative','明确弹性边带固定功能差；不是由仅提滑脱自动生成。'),
884:('add_T49_band_negative','明确评价床笠松紧带not good，失效形式未细分，不虚构弹力实测。'),
1203:('retain_T49_fabric_negative','明确面料无伸展，非松紧带寿命。'),
1222:('retain_T15_only','使用一天stretch out是持续变形，未明示松紧带弹性问题。'),
1252:('add_T49_band_negative','明确口袋深度足够但elastic is crap；保留带结构评价而非尺寸负面。'),
1323:('context_only_for_band_width','要求更宽松紧带是设计期待，未直接评价弹性状态；深度期待与滑脱各保留。'),
1331:('retain_T15_neutral','像其他床单一样几日伸长，未明确弹性褒贬或弹性带失效。'),
1416:('move_specific_failure_G03_to_T49','未持久明确指松紧带；从笼统耐用移至具体结构失效，失效形式未说明，不添加滑脱。'),
1493:('retain_T49_fabric_negative','明确little to no stretch，部件记面料，不推松紧带问题。')}
for i,quote in {143:'The elastic doesnt hold the fitted sheet on very well.',884:'Not good elastic on the fitted sheet',1252:'the elastic is crap',1416:'The elastic on the sheets didn’t last long.'}.items():
 def f(r,i=i,quote=quote):
  if i==1416:r['annotations']=[a for a in r['annotations'] if not(a['code']=='G03' and a['valence']=='negative')]
  r['annotations'].append(add_ann(i,'theme','T49','negative',quote,elastic_decisions[i][1],component='elastic_band',elastic_manifestation='service_life_failure_unspecified' if i==1416 else 'holding_or_quality_complaint_unspecified',component_certainty='explicit'))
 edit(i,'elastic_structure',elastic_decisions[i][1],f)
for i in [1203,1493]:
 def f(r):
  for a in r['annotations']:
   if a['code']=='T49':a.update(component='fabric',component_certainty='explicit_material_context',elastic_manifestation='limited_extensibility')
 edit(i,'elastic_structure',elastic_decisions[i][1],f)
# Preserve sealed v1.1 and all earlier history. Final rule version is metadata, not a claim all labels changed.
for r in D.values():r['rule_version']='1.2'
(P/'02_annotations.jsonl').write_text('\n'.join(json.dumps(D[i],ensure_ascii=False) for i in sorted(D))+'\n')
dump('09_v1.2_change_log.json',changes)
dump('09_v1.2_review_decisions.json',{'purchase_history':behavior_review,'T07_negative':fit_review,'component_updates':component_updates,'elastic':[dict(review_id=i,decision=v[0],reason=v[1],body=S[i]['body']) for i,v in elastic_decisions.items()]})
dump('09_v1.2_scope.json',{'baseline_snapshot':str(B.relative_to(P)),'baseline_annotations_sha256':manifest['02_annotations.jsonl'],'purchase_candidates':sorted(r['review_id'] for r in behavior_review),'T07_negative_candidates':fit_scope,'component_candidates':sorted(component_updates),'elastic_candidates':sorted(elastic_decisions),'protected_original_source_sha256':manifest['00_source_snapshot.json'],'denominators_unchanged':True,'text_corrections':[1389,824]})
book=json.loads((B/'01_theme_rules_v1.1.json').read_text())
for t in book:
 if t['code']=='T07':t.update(include='消费者明确的大小、深度、覆盖、贴合或适配结构评价；结构预期需保留expectation，部件分别标注。',exclude='不能仅由滑脱、床垫厚度、事前测量、广告期待或对容量的推测倒推出实际尺寸不足。错发规格另归履约。')
 if t['code']=='T08':t['exclude']='实际固定表现可由不同原因造成；不自动归因尺寸、深度或松紧带。不同部件不得相互覆盖。'
 if t['code']=='T49':t.update(label='面料伸展／松紧结构表现',include='明确面料可伸展性，或明确松紧带功能、质量、保持寿命的评价；分别标fabric与elastic_band。失效形式未说明即保留未细分。',exclude='仅滑脱不自动推弹性差；永久拉长/缩水归T15；缺失预期绑带归T38；仅要求更宽带不等于弹性失效。')
dump('01_theme_rules_v1.2.json',book)
dump('01_purchase_history_rules_v1.2.json',{
'explicit_repeat_report':'明示购买次数/不同订单，或先前体验与已发生的追加购买动作形成明确叙述；只表示评论者自述，不等于核验交易。',
'possible_repeat_sequence_uncertain':'ordinal set/pair、前后套组比较或扩展用途提示可能再购，但不足区分分次购买、同单多套或未来意图；保留弱线索。',
'multiple_sets_only':'明确已买/持有多套、多色，没有可确认订单顺序；不自动否定可能发生过再购。',
'store_repeat_product_uncertain':'同店先前下单与本次明确，不能确认同款。',
'store_multiple_sequence_uncertain':'同店套数序号，既不能确认同款，也不能确认订单顺序。',
'intentions_and_gifts':'未来意愿、赠礼用途、同单多件独立保留；不计已发生分次购买，可与历史类共存。'})
print('v1.2 applied:',len(changes),'logged edits;',len({x['review_id'] for x in changes}),'distinct annotation-change IDs')
print('IDs',sorted({x['review_id'] for x in changes}))
