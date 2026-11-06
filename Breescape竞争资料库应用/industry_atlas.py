"""Validated, versioned industry atlas. Product references do not mutate brand research."""
import json
from pathlib import Path
from urllib.parse import urlsplit

SECTIONS = {'market','products','growth','materials','needs','mindmap'}
SOURCE_LISTS = {'source_keys','refs','method_sources','principle_sources','event_sources','measurement_sources'}
def import_atlas(c, d, now):
 from industry import url_ok
 sources={s['key']:s for s in d['sources']}
 products={p['id']:p for p in d['products']}
 needs={n['id'] for n in d['needs']['need_pool']}
 if len(sources)!=len(d['sources']) or len(products)!=len(d['products']): raise ValueError('来源或产品标识重复')
 if len(needs)!=len(d['needs']['need_pool']):raise ValueError('需求标识重复')
 groups=d['needs']['groups']
 grouped=[nid for group in groups for nid in group['need_ids']]
 if len({g['id'] for g in groups})!=len(groups) or len(set(grouped))!=len(grouped):raise ValueError('需求分组重复')
 outcome=d['needs'].get('outcome_id')
 if outcome not in needs or set(grouped)!=(needs-{outcome}):raise ValueError('具体需求分组不完整或混入最终目标')
 cases=d['growth']['cards']
 if len({case['id'] for case in cases})!=len(cases):raise ValueError('增长案例标识重复')
 for case in cases:
  for key in ('id','name','case_type','scope','period','metrics','sections','product_ids','source_keys'):
   if not case.get(key):raise ValueError('增长案例字段不完整：'+key)
  for metric in case['metrics']:
   if any(key not in metric for key in ('value','unit','label')):raise ValueError('增长指标字段不完整')
  for section in case['sections']:
   if any(key not in section for key in ('label','title','text','source_keys')):raise ValueError('增长案例板块不完整')
 if d.get('layout_version')==3:
  if [x['id'] for x in d['sections']]!=['market','products','materials','needs','mindmap']:raise ValueError('行业五板块顺序不符合规划')
  categories=d['product_view']['categories']
  grouped_products=[p for cat in categories for group in cat['groups'] for p in group['product_ids']]
  if len(grouped_products)!=len(set(grouped_products)) or set(grouped_products)!=set(products):raise ValueError('产品分类重复或遗漏')
  grouped_cases=[cid for cat in categories for cid in cat['growth_ids']]
  if len(grouped_cases)!=len(set(grouped_cases)) or set(grouped_cases)!={case['id'] for case in cases}:raise ValueError('增长案例必须归入一个品类')
  for cat in categories:
   if any(products[pid]['category']!=cat['id'] for group in cat['groups'] for pid in group['product_ids']):raise ValueError('产品品类归属错误')
   for case in cases:
    if case['id'] in cat['growth_ids'] and (case['category']!=cat['id'] or any(products[pid]['category']!=cat['id'] for pid in case['product_ids'])):raise ValueError('增长案例品类归属错误')
  scopes=['all','covers','sheets']
  if [m['id'] for m in d['needs']['models']]!=scopes:raise ValueError('缺少整体、凉感被或床单需求模型')
  if [m['id'] for m in d['mindmap']['scopes']]!=scopes:raise ValueError('心智地图与需求研究范围不一致')
  for model in d['needs']['models']:
   if not model['clusters'] or not model['pyramid']['levels'] or not model['pyramid']['link_note']:raise ValueError('需求模型缺少内容或前提检验')
  if any(l['scope'] not in scopes for l in d['mindmap']['lanes']) or {l['scope'] for l in d['mindmap']['lanes']}!=set(scopes):raise ValueError('心智地图范围缺失')
  if 'share_chart' in d['market'] or not d['materials'].get('share_chart'):raise ValueError('材料结构必须归入材料板块')
  if not d['market'].get('total') or not d['market'].get('segments'):raise ValueError('市场必须先总体后细分')
 elif {x['id'] for x in d['sections']}!=SECTIONS: raise ValueError('行业六页不完整')
 def check(x):
  if isinstance(x,list):
   for v in x:check(v)
  elif isinstance(x,dict):
   for k,v in x.items():
    if k in SOURCE_LISTS and any(y not in sources for y in v):raise ValueError('来源引用不存在')
    if k=='source_key' and v not in sources:raise ValueError('来源引用不存在')
    if k=='product_id' and v not in products:raise ValueError('行业产品引用不存在')
    if k in ('product_ids','example_ids') and any(y not in products for y in v):raise ValueError('行业产品引用不存在')
    if k=='need_ids' and any(y not in needs for y in v):raise ValueError('需求引用不存在')
    if k=='need_id' and v not in needs:raise ValueError('需求引用不存在')
    if k in ('url','image_url') and v and not url_ok(v):raise ValueError('外部链接无效')
    if k=='report_url' and v and not v.startswith('#product-report/'):raise ValueError('产品报告链接无效')
    if k=='local_path' and v and (Path(v).is_absolute() or '..' in Path(v).parts):raise ValueError('本地附件路径无效')
    if k=='existing_material_id' and not c.execute('SELECT 1 FROM materials WHERE id=?',(v,)).fetchone():raise ValueError('材料不存在')
    check(v)
 check(d)
 for p in d['products']:
  for key in ('price_observation_id','sales_observation_id'):
   if p.get(key):
    row=c.execute('SELECT product_id FROM observations WHERE id=?',(p[key],)).fetchone()
    if not row or row[0]!=p['id']:raise ValueError('产品指标归属不一致')
 source_ids={}
 for s in sources.values():
  mid=s.get('existing_material_id')
  if not mid:
   row=c.execute('SELECT id FROM materials WHERE url=?',(s['url'],)).fetchone() if s.get('url') else c.execute('SELECT id FROM materials WHERE local_path=?',(s.get('local_path',''),)).fetchone()
   mid=row[0] if row else c.execute('INSERT INTO materials(title,url,source_type,publisher,published_at,retrieved_at,summary,access_note,local_path) VALUES (?,?,?,?,?,?,?,?,?)',(s['title'],s.get('url',''),s['source_type'],s.get('publisher',''),s.get('published_at',''),s.get('retrieved_at',''),s.get('supports',''),s.get('boundary',''),s.get('local_path',''))).lastrowid
  source_ids[s['key']]=mid
 def collect(x):
  keys=set()
  if isinstance(x,list):
   for v in x:keys.update(collect(v))
  elif isinstance(x,dict):
   for k,v in x.items():
    if k in SOURCE_LISTS:keys.update(v)
    elif k=='source_key':keys.add(v)
    else:keys.update(collect(v))
  return keys
 for section in d['sections']:
  sid=section['id'];keys=collect(d[sid])
  if sid=='materials':keys.update(collect(d['glossary']))
  if sid=='products':keys.update(collect(d['growth']))
  for key in keys:
   c.execute('INSERT OR IGNORE INTO industry_materials VALUES (?,?,?,?,?,?)',(source_ids[key],sid,'','已用于报告','',now))
 c.execute('INSERT INTO industry_documents VALUES (?,?,?) ON CONFLICT(id) DO UPDATE SET document=excluded.document,updated_at=excluded.updated_at',(d['package_id'],json.dumps(d,ensure_ascii=False),now))
