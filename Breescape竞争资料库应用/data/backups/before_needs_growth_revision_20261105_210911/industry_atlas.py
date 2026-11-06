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
 if {x['id'] for x in d['sections']}!=SECTIONS: raise ValueError('行业六页不完整')
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
  for key in keys:
   c.execute('INSERT OR IGNORE INTO industry_materials VALUES (?,?,?,?,?,?)',(source_ids[key],sid,'','已用于报告','',now))
 c.execute('INSERT INTO industry_documents VALUES (?,?,?) ON CONFLICT(id) DO UPDATE SET document=excluded.document,updated_at=excluded.updated_at',(d['package_id'],json.dumps(d,ensure_ascii=False),now))
