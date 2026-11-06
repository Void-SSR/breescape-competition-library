# coding: utf-8
"""Apply explicitly authored adjudications, never classify from text or stars."""
from pathlib import Path
import json,copy
P=Path(__file__).resolve().parent
S={r['id']:r for r in json.loads((P/'00_source_snapshot.json').read_text())}
rows=[json.loads(x) for x in (P/'02_first_pass_annotations.jsonl').read_text().splitlines()];D={r['review_id']:r for r in rows};log=[]
def edit(i,reason,fn):
 before=copy.deepcopy(D[i]);fn(D[i]);log.append(dict(review_id=i,reason=reason,before=before,after=copy.deepcopy(D[i])))
def remove(code,val=None):
 return lambda r:r.update(annotations=[a for a in r['annotations'] if not(a['code']==code and (val is None or a['valence']==val))])
def add(i,code,val,quote,**kw):
 a=dict(dimension='theme',code=code,valence=val,quote=quote,note='人工复核补充',subject='target_same_product',experience_phase='unspecified',component='unspecified_product_or_set',relation='absolute_or_unspecified',primary_count_eligible=code.startswith('T') and val in ['positive','negative'],count_unit_key=f'{i}|{code}|{val}',quote_start=S[i]['body'].index(quote),quote_end=S[i]['body'].index(quote)+len(quote));a.update(kw);return lambda r:r['annotations'].append(a)
def change(old_code,**kw):
 def f(r):
  for a in r['annotations']:
   if a['code']==old_code:a.update(kw)
 return f
edit(105,'盲复读：睡眠改善与感谢不单独构成总体推荐。',remove('G00'))
edit(1,'盲复读：Material & Comfort后pretty good为总体舒适感。',add(1,'G02','positive','Pretty good actually'))
edit(377,'盲复读：满意专指不脱角，不重复另计总体评价。',remove('G00'))
edit(151,'盲复读：none of them feel like this在赞扬语境中是一般触感满意，非额外柔软。',add(151,'G02','positive','none of them feel like this'))
edit(577,'盲复读：更舒服地入睡未明确睡眠改善，保留一般舒适。',remove('T30'))
edit(242,'盲复读：nice sheets是独立总体肯定。',add(242,'G00','positive','nice'))
edit(519,'盲复读：No complaints为总体无抱怨。',add(519,'G00','positive','No complaints'))
edit(1289,'盲复读：Save your money是明确价值否定。',add(1289,'T29','negative','Save your money'))
edit(375,'盲复读：ok与nothing special分别保留中性和相对总体不满。',add(375,'G00','negative','They are nothing special.'))
edit(37,'先前仅明确向同店购买，未足证同款，复购降为店铺层面。',change('repeat_reported_prior_and_current',code='repeat_brand_reported'))
edit(557,'had to order more为过去追加订购自述，按已下单而非到货；与其他ordered口径一致。',change('repeat_intent',code='repeat_actual',note='自述追加下单，不代表交易被独立验证或已收货'))
for i in [1124,1548]:edit(i,'品牌身份争议不混入材料成分落差。',change('T18',code='T52',count_unit_key=f'{i}|T52|negative'))
edit(253,'仅能透视材料，没有明确态度；与thin中性规则一致。',change('T06',valence='neutral',primary_count_eligible=False,count_unit_key='253|T06|neutral',note='仅透视描述，不据星级推不满'))
for i in [714,1374,1464,1586]:edit(i,'get what you pay for可指低价低质吻合，不独立推断不值钱；保留廉价感。',change('T29',valence='neutral',primary_count_eligible=False,count_unit_key=f'{i}|T29|neutral',note='低价低质对应，不足独立否定性价比'))

for i in [621,661]:edit(i,'仅称买过多套，没有不同订单的时间顺序，不能计明确复购。',change('repeat_actual',code='multiple_sets_timing_unknown'))
def signal(i,code,quote):
 def f(r):
  pos=S[i]['body'].index(quote)
  r['annotations'].append(dict(dimension='purchase_signal',code=code,valence='not_applicable',quote=quote,note='人工复核：明确复购触发自述，非总体因果贡献',subject='target_same_product',experience_phase='unspecified',component='unspecified_product_or_set',relation='absolute_or_unspecified',primary_count_eligible=False,count_unit_key='',quote_start=pos,quote_end=pos+len(quote)))
 return f
for i,q in [(221,'We loved them so much that we actually went back and ordered a SECOND set!'),(298,'I LOVED them so much, I have bought them for gifts as well as for myself!'),(499,'fell in love with it since then, I’ve gotten 5 more.'),(557,'there so comfy I had to order more'),(580,'I’ve now ordered twice because I absolutely love the feel of these sheets.')]:
 edit(i,'复购理由与单纯复购行为分开，补记明确前次体验触发。',signal(i,'prior_experience_repeat',q))

# Attribute manifestations manually adjudicated across all original readings.
for i,meaning in [(27,'temperature_regulation_unspecified'),(110,'warmth_appreciated'),(468,'warmth_appreciated'),(642,'insufficient_warmth'),(764,'temperature_regulation_unspecified')]:
 edit(i,'温度维度含保暖/调温，不全部改写成凉感。',change('T03',thermal_meaning=meaning))
# Normalise derived keys after explicit edits only.
for r in rows:
 for a in r['annotations']:
  if a['dimension']=='theme':
   a['primary_count_eligible']=a['code'].startswith('T') and a['subject']=='target_same_product' and a['valence'] in ('positive','negative')
   a['count_unit_key']=f"{r['review_id']}|{a['code']}|{a['valence']}"
 r['rule_version']='1.1'
(P/'02_annotations.jsonl').write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in sorted(rows,key=lambda r:r['review_id']))+'\n')
(P/'03_adjudication_log.json').write_text(json.dumps(log,ensure_ascii=False,indent=2))
print('Applied',len(log),'explicit adjudications; all original annotations retained in first-pass snapshot.')
