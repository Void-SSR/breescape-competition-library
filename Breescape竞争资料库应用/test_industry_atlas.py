import copy,json,sqlite3,unittest
from pathlib import Path
import industry

class AtlasTest(unittest.TestCase):
 def setUp(self):
  self.c=sqlite3.connect(':memory:');src=sqlite3.connect('file:data/library.sqlite3?mode=ro',uri=True);src.backup(self.c);src.close()
  self.d=json.loads(Path('协作/行业全景升级_20261105/01_核定内容.json').read_text())
 def tearDown(self): self.c.close()
 def test_import_preserves_research_and_old_documents(self):
  tables=['brands','products','reviews','records','observations','brand_reports','material_links']
  before={t:self.c.execute('select * from '+t).fetchall() for t in tables};docs=self.c.execute('select count(*) from industry_documents').fetchone()[0]
  industry.import_document(self.c,self.d,'2099-01-01');n=self.c.execute('select count(*) from materials').fetchone()[0];industry.import_document(self.c,self.d,'2099-01-02')
  self.assertEqual(n,self.c.execute('select count(*) from materials').fetchone()[0]);self.assertEqual(docs,self.c.execute('select count(*) from industry_documents').fetchone()[0])
  self.assertEqual(before,{t:self.c.execute('select * from '+t).fetchall() for t in tables});self.assertEqual(industry.document(self.c),self.d)
 def test_bad_references_leave_database_unchanged(self):
  changes=[lambda d:d['needs']['need_pool'][0]['refs'].append('missing'),lambda d:d['mindmap']['lanes'][0]['brands'][0].update(product_id='missing'),lambda d:d['products'][0].update(price_observation_id=17),lambda d:d['sources'][0].update(local_path='../private')]
  before=self.c.execute('select count(*) from materials').fetchone()[0]
  for f in changes:
   d=copy.deepcopy(self.d);f(d)
   with self.assertRaises(ValueError):industry.import_document(self.c,d,'2099-01-01')
   self.assertEqual(before,self.c.execute('select count(*) from materials').fetchone()[0])
 def test_new_material_stays_out_of_document(self):
  before=industry.document(self.c)
  for category in ['market','products','growth','materials','needs','mindmap']:
   result=industry.add_material(self.c,{'url':'https://example.org/'+category,'category':category},'2099')
   self.assertEqual('待核实',self.c.execute('select status from industry_materials where material_id=?',(result['id'],)).fetchone()[0])
  self.assertEqual(before,industry.document(self.c))
 def test_case_and_need_identity_integrity(self):
  changes=[lambda d:d['growth']['cards'].append(copy.deepcopy(d['growth']['cards'][0])),lambda d:d['needs']['groups'][0]['need_ids'].append('n1'),lambda d:d['needs']['need_pool'].append(copy.deepcopy(d['needs']['need_pool'][0])),lambda d:d['growth']['cards'][0].pop('sections')]
  for f in changes:
   d=copy.deepcopy(self.d);f(d)
   with self.assertRaises(ValueError):industry.import_document(self.c,d,'2099-01-01')
if __name__=='__main__':unittest.main()
