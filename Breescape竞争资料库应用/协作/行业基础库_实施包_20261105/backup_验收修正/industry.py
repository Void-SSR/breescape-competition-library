"""Industry document import and material associations."""
import json
from pathlib import Path
from urllib.parse import urlsplit

ALLOWED={'text','table','market_estimate','product_cards','concept_map','term_links','internal_link'}
def init(c):
 c.execute('CREATE TABLE IF NOT EXISTS industry_documents (id TEXT PRIMARY KEY, document TEXT NOT NULL, updated_at TEXT NOT NULL)')
 c.execute('''CREATE TABLE IF NOT EXISTS industry_materials (material_id INTEGER NOT NULL REFERENCES materials(id), category TEXT NOT NULL, question TEXT NOT NULL DEFAULT '', status TEXT NOT NULL, note TEXT NOT NULL DEFAULT '', added_at TEXT NOT NULL, UNIQUE(material_id,category,question))''')
def url_ok(url):
 u=urlsplit(url); return u.scheme in ('http','https') and bool(u.hostname) and not u.username and not u.password
def import_document(c, d, now):
 if d.get('schema_version')!=1: raise ValueError('不支持的行业文档版本')
 sources={s['key']:s for s in d['sources']}
 if len(sources)!=len(d['sources']): raise ValueError('来源标识重复')
 def walk(x):
  if isinstance(x,dict):
   if 'type' in x and x['type'] not in ALLOWED: raise ValueError('未知组件: '+str(x['type']))
   for k,v in x.items():
    if k=='source_keys' and any(i not in sources for i in v): raise ValueError('来源引用不存在')
    if k in ('product_ref','image_product_ref','product_id') and not c.execute('SELECT 1 FROM products WHERE id=?',(v,)).fetchone(): raise ValueError('商品引用不存在: '+str(v))
    if k=='product_refs' and any(not c.execute('SELECT 1 FROM products WHERE id=?',(i,)).fetchone() for i in v): raise ValueError('商品引用不存在')
    if k in ('term',) and v not in d['glossary']: raise ValueError('词条不存在')
    if k=='terms' and any(i not in d['glossary'] for i in v): raise ValueError('词条不存在')
    if k in ('href','internal_link','report_url','brand_url') and isinstance(v,str) and not v.startswith(('#industry','#product-report/','#overview/')): raise ValueError('内部链接无效')
    if k in ('observation_ref','price_observation_id','sales_observation_id') and not c.execute('SELECT 1 FROM observations WHERE id=?',(v,)).fetchone(): raise ValueError('指标引用不存在: '+str(v))
    if k in ('existing_material_id','screenshot_material_id') and not c.execute('SELECT 1 FROM materials WHERE id=?',(v,)).fetchone(): raise ValueError('材料引用不存在: '+str(v))
    if k in ('url',) and v and not url_ok(v): raise ValueError('来源链接无效')
    walk(v)
  elif isinstance(x,list):
   for v in x: walk(v)
 walk(d)
 source_ids={}
 for s in d['sources']:
  mid=s.get('existing_material_id')
  if not mid:
   row=c.execute('SELECT id FROM materials WHERE url=?',(s['url'],)).fetchone()
   mid=row[0] if row else c.execute('INSERT INTO materials(title,url,source_type,publisher,published_at,retrieved_at,summary,access_note) VALUES (?,?,?,?,?,?,?,?)',(s['title'],s['url'],s['source_type'],s.get('publisher',''),s.get('published_at',''),s.get('retrieved_at',''),s.get('supports',''),s.get('boundary',''))).lastrowid
  source_ids[s['key']]=mid
  c.execute('INSERT OR IGNORE INTO industry_materials VALUES (?,?,?,?,?,?)',(mid,'common','', '已用于报告','',now))
 for category in d['categories']:
  for section in category['sections']:
   keys=set()
   for block in section['blocks']:
    keys.update(block.get('source_keys',[]))
    for pid in block.get('product_refs',[]): keys.update(d['product_examples'][pid].get('source_keys',[]))
   for key in keys:c.execute('INSERT OR IGNORE INTO industry_materials VALUES (?,?,?,?,?,?)',(source_ids[key],category['id'],section['id'],'已用于报告','',now))
 c.execute('INSERT INTO industry_documents VALUES (?,?,?) ON CONFLICT(id) DO UPDATE SET document=excluded.document,updated_at=excluded.updated_at',(d['package_id'],json.dumps(d,ensure_ascii=False),now))
def document(c):
 row=c.execute('SELECT document FROM industry_documents ORDER BY updated_at DESC LIMIT 1').fetchone();return json.loads(row[0]) if row else None
def add_material(c,d,now):
 url=str(d.get('url','')).strip();category=d.get('category','common');question=d.get('question','')
 if not url_ok(url):raise ValueError('请输入完整的http或https链接')
 if category not in ('common','sheets','covers') or question not in ('','market','price','products','technology','consumer'):raise ValueError('品类或问题无效')
 row=c.execute('SELECT id FROM materials WHERE url=?',(url,)).fetchone()
 mid=row[0] if row else c.execute('INSERT INTO materials(title,url,source_type,retrieved_at,summary,access_note) VALUES (?,?,?,?,?,?)',(str(d.get('title','')).strip() or urlsplit(url).hostname,url,'待核实材料',now,str(d.get('note','')),'已收录，正文尚未研究')).lastrowid
 c.execute('INSERT OR IGNORE INTO industry_materials VALUES (?,?,?,?,?,?)',(mid,category,question,'待核实',str(d.get('note','')),now))
 return {'id':mid,'message':'已收录为待核实资料；不会自动改写报告。'}
if __name__=='__main__':
 import sys,server
 with server.conn() as c:
  init(c); import_document(c,json.loads(Path(sys.argv[1]).read_text()),server.now())
 print('导入完成')
