#!/usr/bin/env python3
"""Local-only research library. Python stdlib; no package installation required."""
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlsplit, parse_qs, unquote
from datetime import datetime
from zoneinfo import ZoneInfo
import sqlite3, json, csv, re, unicodedata, hashlib, secrets, os, argparse, base64, mimetypes, io
import reports
import report_layout
import review_package
import industry
ROOT=Path(__file__).resolve().parent
DATA=Path(os.environ.get('BREESCAPE_DATA_DIR',str(ROOT/'data')))
DATA.mkdir(parents=True,exist_ok=True)
DB=DATA/'library.sqlite3'
LEGACY=ROOT.parent/'Breescape竞品资料库'
TOKEN=secrets.token_urlsafe(32)
APP_ID='breescape-library-v1'
SECTIONS=['竞品基础信息','品牌核心产品研究','各渠道的动作','品牌重要发展节点','品牌竞争力与增长机制','对我方的战略启示与机会']
TOPICS={1:['1. 品牌信息','2. 经营规模与渠道结构','3. 产品矩阵与核心产品销量'],2:['4. 核心产品基本信息','5. 消费者评论分析','6. 产品卖得好的原因'],3:['7. 渠道基础信息','8. TOP5爆款内容分析','9. 渠道内容总结'],4:['10. 关键发展历程','11. 关键增长动作'],5:['12. 消费者为什么选择品牌','13. 品牌能力与竞争壁垒'],6:['产品创新','营销与渠道借鉴','竞争短板','潜在市场机会','对我方的战略启示']}
STATUSES=['已核实页面信息','品牌自述','待研究','需工具或权限','待你确认','已查未找到可靠资料','来源暂不可访问','等待前置证据','研究草稿','已复核']
def now():return datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
def conn():
 c=sqlite3.connect(DB,timeout=15);c.row_factory=sqlite3.Row;c.execute('PRAGMA foreign_keys=ON');return c
def rows(c,sql,p=()):return [dict(r) for r in c.execute(sql,p)]
def norm(s):return ' '.join(re.sub(r'[^\w\s]',' ',unicodedata.normalize('NFKC',s).casefold()).split())
def url_ok(s):
 u=urlsplit(s);return u.scheme in ('https','http') and bool(u.hostname) and not u.username and not u.password

def init():
 with conn() as c:
  c.executescript('''
  CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT);
  CREATE TABLE IF NOT EXISTS brands(id TEXT PRIMARY KEY,name TEXT NOT NULL,website TEXT DEFAULT '',note TEXT DEFAULT '');
  CREATE TABLE IF NOT EXISTS products(id TEXT PRIMARY KEY,brand_id TEXT REFERENCES brands(id),name TEXT,channel TEXT,market TEXT,url TEXT,external_id TEXT,image_url TEXT DEFAULT '',state TEXT,legacy_file TEXT DEFAULT '');
  CREATE TABLE IF NOT EXISTS materials(id INTEGER PRIMARY KEY,title TEXT,url TEXT UNIQUE,source_type TEXT,publisher TEXT DEFAULT '',published_at TEXT DEFAULT '',retrieved_at TEXT,summary TEXT DEFAULT '',local_path TEXT DEFAULT '',access_note TEXT DEFAULT '');
  CREATE TABLE IF NOT EXISTS material_links(id INTEGER PRIMARY KEY,material_id INTEGER REFERENCES materials(id),brand_id TEXT REFERENCES brands(id),product_id TEXT REFERENCES products(id),section INTEGER,topic TEXT DEFAULT '',UNIQUE(material_id,product_id,section,topic));
  CREATE TABLE IF NOT EXISTS records(id INTEGER PRIMARY KEY,brand_id TEXT REFERENCES brands(id),product_id TEXT REFERENCES products(id),section INTEGER CHECK(section BETWEEN 1 AND 6),topic TEXT,title TEXT,body TEXT DEFAULT '',kind TEXT,status TEXT,evidence TEXT DEFAULT '[]',updated_at TEXT);
  CREATE TABLE IF NOT EXISTS observations(id INTEGER PRIMARY KEY,product_id TEXT REFERENCES products(id),metric TEXT,value TEXT,unit TEXT,variant TEXT,scope TEXT,observed_at TEXT,retrieved_at TEXT,source_url TEXT,source_type TEXT,availability TEXT,note TEXT DEFAULT '');
  CREATE TABLE IF NOT EXISTS reviews(id INTEGER PRIMARY KEY,product_id TEXT REFERENCES products(id),external_id TEXT,body TEXT,normalized TEXT,rating INTEGER,date TEXT,sku TEXT,region TEXT,raw_json TEXT,UNIQUE(product_id,normalized));
  CREATE UNIQUE INDEX IF NOT EXISTS review_identity ON reviews(product_id,external_id) WHERE external_id!='';
  CREATE TABLE IF NOT EXISTS imports(id INTEGER PRIMARY KEY,product_id TEXT,path TEXT,sha256 TEXT,rows_seen INTEGER,rows_added INTEGER,created_at TEXT,UNIQUE(product_id,sha256));
  CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY,action TEXT,detail TEXT,created_at TEXT);
  CREATE INDEX IF NOT EXISTS review_filter ON reviews(product_id,rating,date);
  ''')
  c.execute('INSERT OR IGNORE INTO meta VALUES (?,?)',('schema_version','1'))
  reports.init(c)
  industry.init(c)

def import_reviews(c,product_id,text,source):
 product=c.execute('SELECT * FROM products WHERE id=?',(product_id,)).fetchone()
 if not product:raise ValueError('请选择已有产品')
 digest=hashlib.sha256(text.encode()).hexdigest()
 if c.execute('SELECT 1 FROM imports WHERE product_id=? AND sha256=?',(product_id,digest)).fetchone():return {'added':0,'duplicate_batch':True}
 reader=csv.DictReader(io.StringIO(text.lstrip('\ufeff')));items=list(reader)
 if not items or not {'商品ID','评论原文','星级'}.issubset(reader.fieldnames or []):raise ValueError('需要包含商品ID、评论原文、星级列的UTF-8 CSV')
 if len(items)>50000:raise ValueError('单批最多50,000行')
 # Reject whole batch before writing if any row belongs to another product.
 if any(r['商品ID']!=product['external_id'] for r in items):raise ValueError('商品ID不一致，整批未导入；请勿混合不同产品')
 added=0;invalid=0
 for r in items:
  body=r['评论原文'];n=norm(body)
  try:rating=int(r['星级'])
  except ValueError:rating=0
  if not n or rating not in range(1,6):invalid+=1;continue
  cur=c.execute('INSERT OR IGNORE INTO reviews(product_id,external_id,body,normalized,rating,date,sku,region,raw_json) VALUES (?,?,?,?,?,?,?,?,?)',(product_id,r.get('评论ID',''),body,n,rating,r.get('发表日期',''),r.get('规格',''),r.get('评论地区',''),json.dumps(r,ensure_ascii=False)))
  added+=cur.rowcount
 c.execute('INSERT INTO imports(product_id,path,sha256,rows_seen,rows_added,created_at) VALUES (?,?,?,?,?,?)',(product_id,source,digest,len(items),added,now()))
 return {'added':added,'duplicates':len(items)-added-invalid,'invalid':invalid,'note':'只做身份、格式和重复检查；新增批次的内容有效性仍需复核。'}

def bootstrap():
 init()
 with conn() as c:
  if c.execute("SELECT 1 FROM meta WHERE key='seeded'").fetchone():return
  seed=json.loads((ROOT/'seed.json').read_text())
  for b in seed['brands']:c.execute('INSERT INTO brands(id,name,website,note) VALUES (:id,:name,:website,:note)',b)
  for p in seed['products']:c.execute('INSERT INTO products(id,brand_id,name,channel,market,url,external_id,image_url,state,legacy_file) VALUES (:id,:brand_id,:name,:channel,:market,:url,:external_id,:image_url,:state,:legacy_file)',p)
  for m in seed['materials']:
   c.execute('INSERT INTO materials(id,title,url,source_type,publisher,retrieved_at,summary,access_note) VALUES (:id,:title,:url,:source_type,:publisher,:retrieved_at,:summary,:access_note)',m)
   c.execute('INSERT INTO material_links(material_id,brand_id,product_id,section,topic) VALUES (?,?,?,?,?)',(m['id'],'shilucheng','sheets',m['section'],m['topic']))
  for r in seed['records']:
   c.execute('INSERT INTO records(brand_id,product_id,section,topic,title,body,kind,status,evidence,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)',('shilucheng',r.get('product_id','sheets'),r['section'],r['topic'],r['title'],r['body'],r['kind'],r['status'],json.dumps(r.get('evidence',[])),now()))
  for o in seed['observations']:
   c.execute('INSERT INTO observations(product_id,metric,value,unit,variant,scope,observed_at,retrieved_at,source_url,source_type,availability,note) VALUES (:product_id,:metric,:value,:unit,:variant,:scope,:observed_at,:retrieved_at,:source_url,:source_type,:availability,:note)',o)
  p=c.execute("SELECT legacy_file FROM products WHERE id='sheets'").fetchone()[0]
  import_reviews(c,'sheets',(LEGACY/p).read_text(encoding='utf-8-sig'),p)
  c.execute('INSERT INTO meta VALUES (?,?)',('seeded',now()))
  c.execute('INSERT INTO events(action,detail,created_at) VALUES (?,?,?)',('初始化','床单样板已接入；研究顺序与缺口已建立；未启用定时任务',now()))

def snapshot(c):
 return {'industry_display':json.loads(c.execute("SELECT document FROM industry_settings WHERE id='display'").fetchone()[0]) if c.execute("SELECT 1 FROM industry_settings WHERE id='display'").fetchone() else {},'industry':industry.document(c),'industry_materials':rows(c,'SELECT im.*,m.title,m.url,m.source_type,m.publisher,m.retrieved_at,m.local_path,m.access_note FROM industry_materials im JOIN materials m ON m.id=im.material_id ORDER BY im.added_at DESC'), 'review_analysis':review_package.publication(c,DATA),'reports':reports.documents(c,TOPICS),'brands':rows(c,'SELECT * FROM brands'),'products':rows(c,'SELECT p.*, (SELECT count(*) FROM reviews r WHERE r.product_id=p.id) review_count FROM products p'),'materials':rows(c,'SELECT * FROM materials ORDER BY id DESC'),'links':rows(c,'SELECT * FROM material_links'),'records':rows(c,'SELECT * FROM records ORDER BY section,id'),'observations':rows(c,'SELECT * FROM observations ORDER BY id DESC'),'imports':rows(c,'SELECT * FROM imports ORDER BY id DESC'),'events':rows(c,'SELECT * FROM events ORDER BY id DESC LIMIT 40'),'sections':SECTIONS,'topics':TOPICS,'statuses':STATUSES,'scheduler':'未启用；价格与销量自动采集器待逐来源接入'}

class Handler(BaseHTTPRequestHandler):
 def log_message(self,fmt,*args):pass
 def send(self,value,code=200,mime='application/json; charset=utf-8',filename=None):
  data=value if isinstance(value,bytes) else json.dumps(value,ensure_ascii=False).encode()
  self.send_response(code);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer')
  if filename:self.send_header('Content-Disposition',"attachment; filename*=UTF-8''"+__import__('urllib.parse',fromlist=['quote']).quote(filename))
  self.end_headers();self.wfile.write(data)
 def valid_host(self):return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}')
 def do_GET(self):
  if not self.valid_host():return self.send({'error':'仅限本机访问'},403)
  u=urlsplit(self.path);q=parse_qs(u.query)
  try:
   with conn() as c:
    if u.path=='/api/health':return self.send({'app':APP_ID,'database':hashlib.sha256(str(DB).encode()).hexdigest()[:12]})
    if u.path=='/api/bootstrap':return self.send({**snapshot(c),'token':TOKEN})
    if u.path=='/api/review':
     r=review_package.review(c,DATA,q.get('product',[''])[0],q.get('id',[''])[0])
     return self.send(r if r else {'error':'该产品下不存在此评论编号'},200 if r else 404)
    if u.path=='/api/reviews':
     pid=q.get('product',['sheets'])[0];search=q.get('q',[''])[0];rating=q.get('rating',[''])[0];offset=max(0,int(q.get('offset',['0'])[0]));where='product_id=?';args=[pid]
     if search:where+=' AND (instr(lower(body),lower(?))>0 OR instr(lower(sku),lower(?))>0)';args.extend([search,search])
     if rating:where+=' AND rating=?';args.append(int(rating))
     for key,op in [('from','>='),('to','<=')]:
      if q.get(key):where+=' AND date'+op+'?';args.append(q[key][0])
     total=c.execute('SELECT count(*) FROM reviews WHERE '+where,args).fetchone()[0]
     order='ASC' if q.get('order',['desc'])[0]=='asc' else 'DESC'
     return self.send({'total':total,'items':rows(c,'SELECT * FROM reviews WHERE '+where+' ORDER BY date '+order+',id LIMIT 40 OFFSET ?',args+[offset])})
    if u.path=='/api/export':
     p=c.execute('SELECT * FROM products WHERE id=?',(q.get('product',['sheets'])[0],)).fetchone()
     if not p:raise ValueError('产品不存在')
     rr=rows(c,'SELECT raw_json FROM reviews WHERE product_id=? ORDER BY date DESC,id',(p['id'],));values=[json.loads(x['raw_json']) for x in rr]
     if not values:raise ValueError('该产品尚未导入评论')
     cols=list(dict.fromkeys(k for x in values for k in x));f=io.StringIO();w=csv.DictWriter(f,cols);w.writeheader();w.writerows(values)
     return self.send(('\ufeff'+f.getvalue()).encode(),mime='text/csv; charset=utf-8',filename=p['name']+'_评论.csv')
    if u.path=='/api/export-industry':
     doc=industry.document(c); refs=[]
     for x in (list((doc or {}).get('product_examples',{}).values())+(doc or {}).get('products',[])):
      refs.extend([x.get('price_observation_id'),x.get('sales_observation_id')])
     data={'document':doc,'display':json.loads(c.execute("SELECT document FROM industry_settings WHERE id='display'").fetchone()[0]),'materials':rows(c,'SELECT im.*,m.* FROM industry_materials im JOIN materials m ON m.id=im.material_id'),'observations':[dict(c.execute('SELECT * FROM observations WHERE id=?',(i,)).fetchone()) for i in set(refs) if i]}
     return self.send(json.dumps(data,ensure_ascii=False,indent=2).encode(),mime='application/json',filename='美国凉感床品_行业全景资料包.json')
    if u.path=='/api/export-library':return self.send(json.dumps(snapshot(c),ensure_ascii=False,indent=2).encode(),mime='application/json',filename='Breescape竞争资料库_资料导出.json')
    if u.path.startswith('/attachment/'):
     m=c.execute('SELECT * FROM materials WHERE id=?',(int(u.path.rsplit('/',1)[1]),)).fetchone()
     if not m or not m['local_path']:raise ValueError('附件不存在')
     p=(DATA/m['local_path']).resolve()
     if DATA.resolve() not in p.parents:raise ValueError('无效文件')
     image_mime={'.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.webp':'image/webp'}.get(p.suffix.lower())
     if image_mime:return self.send(p.read_bytes(),mime=image_mime)
     return self.send(p.read_bytes(),mime='application/octet-stream',filename=p.name)
   target={'/':'index.html','/app.js':'app.js','/style.css':'style.css','/reports.js':'reports.js','/report-editor.js':'report-editor.js','/product-reports.js':'product-reports.js','/reports.css':'reports.css','/industry.js':'industry.js','/industry.css':'industry.css'}.get(u.path)
   if target:return self.send((ROOT/'static'/target).read_bytes(),mime={'index.html':'text/html; charset=utf-8','app.js':'text/javascript; charset=utf-8','style.css':'text/css; charset=utf-8','reports.js':'text/javascript; charset=utf-8','report-editor.js':'text/javascript; charset=utf-8','product-reports.js':'text/javascript; charset=utf-8','reports.css':'text/css; charset=utf-8','industry.js':'text/javascript; charset=utf-8','industry.css':'text/css; charset=utf-8'}[target])
   self.send({'error':'未找到'},404)
  except (ValueError,KeyError) as e:self.send({'error':str(e)},400)
  except Exception:self.send({'error':'读取失败，请检查本地程序日志'},500)
 def do_POST(self):
  if not self.valid_host() or self.headers.get('X-Library-Token')!=TOKEN:return self.send({'error':'请刷新资料库后重试'},403)
  origin=self.headers.get('Origin')
  if origin and origin not in (f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'):return self.send({'error':'请求来源不匹配'},403)
  try:
   size=int(self.headers.get('Content-Length',0))
   if not 0<size<30_000_000:raise ValueError('单次请求需小于30MB')
   d=json.loads(self.rfile.read(size));route=urlsplit(self.path).path
   with conn() as c:
    if route=='/api/report-package':
     content,name=review_package.package(c,DATA,d)
     return self.send(content,mime='application/zip',filename=name)
    if route=='/api/industry-material':
     result=industry.add_material(c,d,now())
    elif route=='/api/material':
     title=str(d.get('title','')).strip();url=str(d.get('url','')).strip();file=d.get('file');local=''
     if not url and not file:raise ValueError('请粘贴链接或选择文件')
     if url and not url_ok(url):raise ValueError('请输入完整的http或https链接')
     pid=d.get('product_id','sheets');p=c.execute('SELECT * FROM products WHERE id=?',(pid,)).fetchone()
     if not p:raise ValueError('产品不存在')
     section=int(d.get('section',1));topic=str(d.get('topic',''))
     if section not in range(1,7):raise ValueError('请选择研究板块')
     existing=c.execute('SELECT id FROM materials WHERE url=?',(url,)).fetchone() if url else None
     duplicate=bool(existing)
     if existing:mid=existing[0]
     else:
      if file:
       content=base64.b64decode(file['data'],validate=True)
       if len(content)>20_000_000:raise ValueError('附件需小于20MB；大材料建议保存网络链接')
       name=Path(file['name']).name;title=title or name;folder=DATA/'attachments';folder.mkdir(exist_ok=True);fname=hashlib.sha256(content).hexdigest()[:20]+Path(name).suffix[:12];(folder/fname).write_bytes(content);local='attachments/'+fname
      title=title or urlsplit(url).hostname or '未命名材料'
      mid=c.execute('INSERT INTO materials(title,url,source_type,publisher,retrieved_at,summary,local_path,access_note) VALUES (?,?,?,?,?,?,?,?)',(title,url or None,d.get('source_type','待核实材料'),d.get('publisher',''),now(),d.get('summary',''),local,'已收录，正文尚未研究')).lastrowid
     c.execute('INSERT OR IGNORE INTO material_links(material_id,brand_id,product_id,section,topic) VALUES (?,?,?,?,?)',(mid,p['brand_id'],pid,section,topic))
     result={'id':mid,'duplicate':duplicate,'message':'已有链接已关联到该板块' if duplicate else '材料已保存；不会自动生成研究结论'}
    elif route=='/api/product':
     for k in ['name','brand','url','external_id']:
      if not str(d.get(k,'')).strip():raise ValueError('请填写品牌、产品名称、商品ID和原链接')
     if not url_ok(d['url']):raise ValueError('请输入完整商品链接')
     if c.execute('SELECT 1 FROM products WHERE url=? OR (external_id=? AND channel=?)',(d['url'],d['external_id'],d.get('channel',''))).fetchone():raise ValueError('该商品已经存在')
     b=c.execute('SELECT id FROM brands WHERE lower(name)=lower(?)',(d['brand'].strip(),)).fetchone()
     bid=b[0] if b else 'brand-'+secrets.token_hex(6)
     if not b:c.execute('INSERT INTO brands(id,name) VALUES (?,?)',(bid,d['brand'].strip()))
     pid='product-'+secrets.token_hex(6)
     img=d.get('image_url','')
     if img and not url_ok(img):raise ValueError('图片链接无效')
     c.execute('INSERT INTO products(id,brand_id,name,channel,market,url,external_id,image_url,state) VALUES (?,?,?,?,?,?,?,?,?)',(pid,bid,d['name'],d.get('channel','待确认'),d.get('market','待确认'),d['url'],d['external_id'],img,'待研究'))
     result={'id':pid,'message':'产品档案已创建；六个研究板块按需收录'}
    elif route=='/api/record':
     rid=d.get('id');old=c.execute('SELECT * FROM records WHERE id=?',(rid,)).fetchone() if rid else None
     pid=d.get('product_id','sheets');p=c.execute('SELECT * FROM products WHERE id=?',(pid,)).fetchone()
     if not p:raise ValueError('请选择产品')
     section=int(d['section']);kind=d.get('kind','事实');status=d.get('status','待研究');evidence=d.get('evidence',[])
     if section not in range(1,7) or status not in STATUSES:raise ValueError('板块或状态无效')
     if not str(d.get('title','')).strip():raise ValueError('请输入条目名称')
     if kind not in ('事实','品牌宣称','分析','缺口'):raise ValueError('条目类型无效')
     for mid in evidence:
      if not c.execute('SELECT 1 FROM materials WHERE id=?',(int(mid),)).fetchone():raise ValueError('引用材料不存在')
     if kind=='分析' and status not in ('等待前置证据','研究草稿','待你确认','待研究','已复核'):raise ValueError('本阶段分析只能保存为草稿或待确认，不能发布为事实结论')
     if status in ('已核实页面信息','品牌自述','已复核') and not evidence:raise ValueError('已核实信息或品牌自述必须关联来源材料')
     values=(p['brand_id'],None if old and old['product_id'] is None and old['brand_id']==p['brand_id'] else pid,section,d.get('topic',''),d['title'].strip(),d.get('body',''),kind,status,json.dumps(evidence),now())
     if rid:
      if not old:raise ValueError('条目不存在')
      c.execute('UPDATE records SET brand_id=?,product_id=?,section=?,topic=?,title=?,body=?,kind=?,status=?,evidence=?,updated_at=? WHERE id=?',values+(rid,))
     else:rid=c.execute('INSERT INTO records(brand_id,product_id,section,topic,title,body,kind,status,evidence,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)',values).lastrowid
     result={'id':rid,'message':'条目已保存'}
    elif route=='/api/report-layout':
     result=report_layout.save(c,d,now())
    elif route=='/api/report':
     result=reports.save(c,d,TOPICS,now())
    elif route=='/api/observation':
     for key in ['product_id','metric','value','unit','variant','scope','observed_at','source_url']:
      if not str(d.get(key,'')).strip():raise ValueError('请填写指标、数值、单位、规格/对象范围、口径、观察时间和来源')
     if not url_ok(d['source_url']):raise ValueError('来源链接无效')
     c.execute('INSERT INTO observations(product_id,metric,value,unit,variant,scope,observed_at,retrieved_at,source_url,source_type,availability,note) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',tuple(d[k] for k in ['product_id','metric','value','unit','variant','scope','observed_at'])+(now(),d['source_url'],d.get('source_type','人工记录'),d.get('availability','手动录入，待复核'),d.get('note','')))
     result={'message':'已追加历史记录，旧数据保持不变'}
    elif route=='/api/import-reviews':result=import_reviews(c,d['product_id'],d['text'],d.get('filename','手动导入.csv'))
    elif route=='/api/shutdown':
     import threading
     threading.Timer(0.3,self.server.shutdown).start()
     result={'message':'资料库即将关闭；数据已保存。点击Mac启动图标即可重新打开。'}
    elif route=='/api/backup':
     folder=DATA/'backups';folder.mkdir(exist_ok=True);path=folder/('library_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.sqlite3')
     with sqlite3.connect(path) as target:c.backup(target)
     result={'message':'已创建完整本地数据库备份','path':str(path)}
    else:raise ValueError('未知操作')
    c.execute('INSERT INTO events(action,detail,created_at) VALUES (?,?,?)',(route,json.dumps(result,ensure_ascii=False),now()))
   self.send(result)
  except (ValueError,KeyError,TypeError,sqlite3.IntegrityError) as e:self.send({'error':str(e)},400)
  except Exception:self.send({'error':'保存失败，请检查本地程序日志；未提交的数据库变更已回滚'},500)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8766);parser.add_argument('--init',action='store_true');a=parser.parse_args();bootstrap()
 if a.init:print(DB);return
 server=ThreadingHTTPServer(('127.0.0.1',a.port),Handler);print(f'Breescape 竞争资料库 http://127.0.0.1:{a.port}',flush=True);server.serve_forever()
if __name__=='__main__':main()
