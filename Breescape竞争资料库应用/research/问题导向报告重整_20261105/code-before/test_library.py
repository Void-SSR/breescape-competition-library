import tempfile,os,sys,json,unittest,threading,urllib.request,urllib.error,sqlite3,csv,io
from pathlib import Path
TEMP=tempfile.TemporaryDirectory();os.environ['BREESCAPE_DATA_DIR']=TEMP.name
import server
server.bootstrap();http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);threading.Thread(target=http.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{http.server_port}'
def get(path):return json.load(urllib.request.urlopen(BASE+path))
def post(path,data,token=server.TOKEN):
 req=urllib.request.Request(BASE+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json','X-Library-Token':token})
 with urllib.request.urlopen(req) as r:return json.load(r)
class Acceptance(unittest.TestCase):
 def test_01_seed(self):
  data=get('/api/bootstrap');self.assertEqual(sum(p['review_count'] for p in data['products']),1628);self.assertEqual(len(data['products']),4)
  self.assertFalse(any(r['kind']=='分析' and r['status']=='已核实页面信息' for r in data['records']))
 def test_02_idempotent_import(self):
  f=next(server.LEGACY.glob('*竹混纺*已整理.csv'));r=post('/api/import-reviews',{'product_id':'sheets','filename':f.name,'text':f.read_text(encoding='utf-8-sig')});self.assertEqual(r['added'],0)
 def test_03_wrong_product_atomic(self):
  text='商品ID,评论原文,星级\n1729438233542234865,Specific test review,5\nWRONG,other review,4\n'
  with self.assertRaises(urllib.error.HTTPError):post('/api/import-reviews',{'product_id':'sheets','text':text})
  self.assertEqual(get('/api/reviews?product=sheets')['total'],1628)
 def test_04_material_dedup_and_persistence(self):
  d={'url':'https://example.org/research-test','title':'验收测试材料','product_id':'sheets','section':1,'topic':'1. 品牌信息'};a=post('/api/material',d);b=post('/api/material',d);self.assertEqual(a['id'],b['id']);self.assertTrue(b['duplicate'])
  with server.conn() as c:self.assertEqual(c.execute('SELECT count(*) FROM materials WHERE url=?',(d['url'],)).fetchone()[0],1)
 def test_05_analysis_gate(self):
  d={'product_id':'sheets','section':5,'topic':'13. 品牌能力与竞争壁垒','kind':'分析','title':'未经支持的壁垒','status':'已核实页面信息','evidence':[1]}
  with self.assertRaises(urllib.error.HTTPError):post('/api/record',d)
 def test_06_observation_history(self):
  d={'product_id':'sheets','metric':'test-price','value':'10','unit':'USD','variant':'Queen','scope':'测试标价','observed_at':'2026-11-04','source_url':'https://example.org/test'};post('/api/observation',d);d['value']='12';post('/api/observation',d)
  with server.conn() as c:self.assertEqual([r[0] for r in c.execute("SELECT value FROM observations WHERE metric='test-price' ORDER BY id")],['10','12'])
 def test_07_filter_and_export(self):
  d=get('/api/reviews?product=sheets&rating=1&q=soft');self.assertTrue(all(r['rating']==1 and 'soft' in (r['body']+' '+r['sku']).lower() for r in d['items']))
  text=urllib.request.urlopen(BASE+'/api/export?product=sheets').read().decode('utf-8-sig');self.assertEqual(len(list(csv.DictReader(io.StringIO(text)))),1628)
 def test_08_security(self):
  with self.assertRaises(urllib.error.HTTPError):post('/api/material',{'url':'https://example.org'},'invalid')
  with self.assertRaises(urllib.error.HTTPError):post('/api/material',{'url':'javascript:alert(1)'})
 def test_09_backup(self):
  d=post('/api/backup',{});self.assertTrue(Path(d['path']).exists())
  with sqlite3.connect(d['path']) as c:self.assertEqual(c.execute('SELECT count(*) FROM reviews').fetchone()[0],1628)
 def test_10_new_product(self):
  r=post('/api/product',{'name':'测试产品','brand':'测试品牌','url':'https://example.org/new-product','external_id':'test001','channel':'独立站','market':'美国'});self.assertTrue(any(p['id']==r['id'] for p in get('/api/bootstrap')['products']))
 def test_11_brand_report_isolation(self):
  data=get('/api/bootstrap');reports=data['reports'];self.assertEqual(len(reports),len(data['brands']))
  other=next(r for r in reports if r['brand_id']=='cozy-bliss')
  self.assertEqual(len(other['sections']),6);self.assertEqual(other['summary'],'')
  self.assertTrue(all(not t['record_ids'] for s in other['sections'] for t in s['topics']))
 def test_12_report_evidence_change_requires_review(self):
  r=next(r for r in get('/api/bootstrap')['reports'] if r['brand_id']=='shilucheng');s=r['sections'][0]
  s['topics'][0].update(finding='测试：品牌信息的阶段性概括',record_ids=[1])
  post('/api/report',{'brand_id':'shilucheng','section':1,'headline':'测试标题','summary':'测试小结','boundary':'仅用于测试','topics':s['topics'],'expected_revision':s['current_revision']})
  current=lambda:next(r for r in get('/api/bootstrap')['reports'] if r['brand_id']=='shilucheng')['sections'][0]
  self.assertFalse(current()['stale'])
  with server.conn() as c:c.execute("UPDATE records SET body=body||' 新证据' WHERE id=1")
  self.assertTrue(current()['stale']);self.assertEqual(current()['summary'],'测试小结')
  with self.assertRaises(urllib.error.HTTPError):post('/api/report',{'brand_id':'shilucheng','section':1,'summary':'过时保存','topics':s['topics'],'expected_revision':s['current_revision']})
 def test_13_report_rejects_cross_brand_and_cross_product(self):
  with self.assertRaises(urllib.error.HTTPError):post('/api/report',{'brand_id':'cozy-bliss','section':0,'title':'测试','summary':'错误引用','summary_record_ids':[1]})
  r=next(r for r in get('/api/bootstrap')['reports'] if r['brand_id']=='shilucheng');s=r['sections'][1]
  next(t for t in s['topics'] if t['product_id']=='topper').update(finding='混入床单',record_ids=[7])
  with self.assertRaises(urllib.error.HTTPError):post('/api/report',{'brand_id':'shilucheng','section':2,'summary':'混用产品','topics':s['topics']})
 def test_14_report_export_and_new_brand_outline(self):
  data=get('/api/export-library');bid=next(b['id'] for b in data['brands'] if b['name']=='测试品牌')
  r=next(r for r in data['reports'] if r['brand_id']==bid)
  self.assertEqual(len(r['sections']),6);self.assertEqual(len(r['sections'][1]['topics']),3)
  self.assertNotIn('token',data)
 def test_15_report_summary_requires_evidence(self):
  with self.assertRaises(urllib.error.HTTPError):post('/api/report',{'brand_id':'sheex','section':0,'title':'未经支持的小结','summary':'不能凭空认定优势','summary_record_ids':[]})
 def test_16_report_feature_must_use_linked_fact(self):
  r=next(r for r in get('/api/bootstrap')['reports'] if r['brand_id']=='shilucheng');s=r['sections'][0]
  s['topics'][0]['featured']=[{'record_id':7,'mode':'table'}]
  with self.assertRaises(urllib.error.HTTPError):post('/api/report',{'brand_id':'shilucheng','section':1,'topics':s['topics']})
 def test_17_report_screenshot_scope(self):
  with server.conn() as c:
   mid=c.execute("INSERT INTO materials(title,local_path) VALUES ('测试截图','test.png')").lastrowid
   c.execute('INSERT INTO material_links(material_id,brand_id,section,topic) VALUES (?,?,?,?)',(mid,'shilucheng',1,'1. 品牌信息'))
  r=next(r for r in get('/api/bootstrap')['reports'] if r['brand_id']=='cozy-bliss')
  with self.assertRaises(urllib.error.HTTPError):post('/api/report',{'brand_id':'cozy-bliss','section':1,'topics':r['sections'][0]['topics'],'images':[mid]})
 def test_18_overall_summary_rejects_stale_save(self):
  r=next(r for r in get('/api/bootstrap')['reports'] if r['brand_id']=='shilucheng')
  revisions={str(s['number']):s['current_revision'] for s in r['sections']}
  with server.conn() as c:c.execute("UPDATE records SET body=body||' 又有新证据' WHERE id=1")
  with self.assertRaises(urllib.error.HTTPError):post('/api/report',{'brand_id':'shilucheng','section':0,'title':'测试','summary':'测试','summary_record_ids':[1],'expected_revisions':revisions})
 def test_19_report_topic_figure_product_scope(self):
  with server.conn() as c:
   mid=c.execute("INSERT INTO materials(title,local_path) VALUES ('床单测试图','sheets.png')").lastrowid
   c.execute('INSERT INTO material_links(material_id,brand_id,product_id,section,topic) VALUES (?,?,?,?,?)',(mid,'shilucheng','sheets',2,'4. 核心产品基本信息'))
  r=next(r for r in get('/api/bootstrap')['reports'] if r['brand_id']=='shilucheng');s=r['sections'][1]
  t=next(t for t in s['topics'] if t['product_id']=='topper');t['figures']=[{'material_id':mid,'caption':'误配图'}]
  with self.assertRaises(urllib.error.HTTPError):post('/api/report',{'brand_id':'shilucheng','section':2,'topics':s['topics']})
 def test_20_report_answer_requires_evidence(self):
  r=next(r for r in get('/api/bootstrap')['reports'] if r['brand_id']=='sheex');s=r['sections'][0]
  s['topics'][0]['coverage']='已回答'
  with self.assertRaises(urllib.error.HTTPError):post('/api/report',{'brand_id':'sheex','section':1,'topics':s['topics']})
 def test_21_report_visual_roundtrip(self):
  r=next(r for r in get('/api/bootstrap')['reports'] if r['brand_id']=='shilucheng');s=r['sections'][0]
  t=s['topics'][0];t.update(bullets=['可核实的测试要点'],coverage='部分回答',gap='仍缺主体信息',impact='不能认定品牌沿革',answer_type='事实概括')
  post('/api/report',{'brand_id':'shilucheng','section':1,'topics':s['topics']})
  now=next(r for r in get('/api/bootstrap')['reports'] if r['brand_id']=='shilucheng')['sections'][0]['topics'][0]
  self.assertEqual(now['bullets'],['可核实的测试要点']);self.assertEqual(now['coverage'],'部分回答');self.assertEqual(now['gap'],'仍缺主体信息')
  # Older clients may omit new fields; saving must not erase them.
  for key in ('bullets','coverage','gap','impact','answer_type'):t.pop(key,None)
  post('/api/report',{'brand_id':'shilucheng','section':1,'topics':s['topics']})
  now=next(r for r in get('/api/bootstrap')['reports'] if r['brand_id']=='shilucheng')['sections'][0]['topics'][0]
  self.assertEqual(now['bullets'],['可核实的测试要点'])
 def test_22_analysis_presentation_remains_distinct_from_facts(self):
  with server.conn() as c:
   rid=c.execute("INSERT INTO records(brand_id,product_id,section,topic,title,body,kind,status,evidence,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",('shilucheng','sheets',2,'6. 产品卖得好的原因','机制验证','| 解释 | 证据 |\n| --- | --- |\n| 体验 | 个案 |','分析','研究草稿','[1]',server.now())).lastrowid
  r=next(r for r in get('/api/bootstrap')['reports'] if r['brand_id']=='shilucheng');s=r['sections'][1]
  t=next(t for t in s['topics'] if t['topic']=='6. 产品卖得好的原因' and t['product_id']=='sheets')
  t.update(finding='有来源的阶段性解释',record_ids=[rid],featured=[{'record_id':rid,'mode':'analysis'}])
  post('/api/report',{'brand_id':'shilucheng','section':2,'topics':s['topics']})
  t['featured'][0]['mode']='table'
  with self.assertRaises(urllib.error.HTTPError):post('/api/report',{'brand_id':'shilucheng','section':2,'topics':s['topics']})
  t['featured'][0]['mode']='analysis'
  with server.conn() as c:c.execute("UPDATE records SET evidence='[]' WHERE id=?",(rid,))
  with self.assertRaises(urllib.error.HTTPError):post('/api/report',{'brand_id':'shilucheng','section':2,'topics':s['topics']})
 def test_23_portable_evidence_includes_only_brand_attachments(self):
  import hashlib,zipfile,reports,review_package
  data=Path(TEMP.name)
  (data/'test-fixed.txt').write_text('immutable evidence')
  (data/'test-video.mp4').write_bytes(b'video test fixture')
  with server.conn() as c:
   old=c.execute('SELECT value FROM meta WHERE key=?',(review_package.KEY,)).fetchone()
   m={'brand_id':'shilucheng','files':[{'local_path':'test-fixed.txt','filename':'fixed.txt','sha256':hashlib.sha256((data/'test-fixed.txt').read_bytes()).hexdigest()}]}
   c.execute('INSERT OR REPLACE INTO meta VALUES (?,?)',(review_package.KEY,json.dumps(m)))
   mid=c.execute("INSERT INTO materials(title,local_path) VALUES ('测试视频','test-video.mp4')").lastrowid
   c.execute('INSERT INTO material_links(material_id,brand_id,section) VALUES (?,?,?)',(mid,'shilucheng',3))
   other=c.execute("INSERT INTO materials(title,local_path) VALUES ('另一品牌','test-video.mp4')").lastrowid
   c.execute('INSERT INTO material_links(material_id,brand_id,section) VALUES (?,?,?)',(other,'sheex',3))
   bad=c.execute("INSERT INTO materials(title,local_path) VALUES ('越界附件','../outside.txt')").lastrowid
   c.execute('INSERT INTO material_links(material_id,brand_id,section) VALUES (?,?,?)',(bad,'shilucheng',3))
   payload={'brand_id':'shilucheng','html':'<!doctype html><p>报告</p>','document_updated_at':c.execute("SELECT updated_at FROM brand_reports WHERE brand_id='shilucheng'").fetchone()[0],'revisions':{str(n):reports.section_revision(c,'shilucheng',n) for n in range(1,7)},'attachment_ids':[mid,mid]}
   content,name=review_package.package(c,data,payload)
   with zipfile.ZipFile(io.BytesIO(content)) as z:
    videos=[n for n in z.namelist() if n.endswith('.mp4')]
    self.assertEqual(len(videos),1);self.assertEqual(z.read(videos[0]),b'video test fixture')
    self.assertTrue(any(n.endswith('/证据 v1.2/fixed.txt') for n in z.namelist()))
   for ids in [[other],[bad],['1'],[True]]:
    with self.assertRaises(ValueError):review_package.package(c,data,{**payload,'attachment_ids':ids})
   if old:c.execute('UPDATE meta SET value=? WHERE key=?',(old[0],review_package.KEY))
   else:c.execute('DELETE FROM meta WHERE key=?',(review_package.KEY,))
if __name__=='__main__':
 try:unittest.main(exit=False)
 finally:http.shutdown();http.server_close();TEMP.cleanup()
