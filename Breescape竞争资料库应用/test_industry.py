import unittest,sqlite3,json,copy
from pathlib import Path
import industry
P=Path('协作/行业基础库_实施包_20261105/01_核定展示内容.json')
class IndustryTest(unittest.TestCase):
 def setUp(self):
  self.c=sqlite3.connect(':memory:');src=sqlite3.connect('file:data/library.sqlite3?mode=ro',uri=True);src.backup(self.c);src.close();self.d=json.loads(P.read_text());industry.init(self.c)
 def tearDown(self):self.c.close()
 def test_import_idempotent(self):
  industry.import_document(self.c,self.d,'2099-01-01');n=self.c.execute('select count(*) from materials').fetchone()[0];industry.import_document(self.c,self.d,'2099-01-01');self.assertEqual(n,self.c.execute('select count(*) from materials').fetchone()[0]);self.assertEqual(industry.document(self.c),self.d)
 def test_bad_reference_or_component(self):
  for typ in ('reference','component'):
   d=copy.deepcopy(self.d)
   if typ=='reference':d['categories'][0]['sections'][0]['blocks'][1]['rows'][0][1]['product_ref']='missing'
   else:d['categories'][0]['sections'][0]['blocks'][0]['type']='bad'
   with self.assertRaises(ValueError):industry.import_document(self.c,d,'2026')
 def test_invalid_product_configuration_and_metric_are_atomic(self):
  cases=[]
  d=copy.deepcopy(self.d);d['categories'][0]['sections'][0]['blocks'][2]['metric_id']='missing';cases.append(d)
  d=copy.deepcopy(self.d);del d['product_examples']['sheets'];cases.append(d)
  d=copy.deepcopy(self.d);d['product_examples']['sheets']['price_observation_id']=17;cases.append(d)
  before=self.c.execute('select count(*) from industry_materials').fetchone()[0]
  for bad in cases:
   with self.assertRaises(ValueError): industry.import_document(self.c,bad,'2026')
   self.assertEqual(before,self.c.execute('select count(*) from industry_materials').fetchone()[0])
 def test_material_isolation_dedup(self):
  before=self.c.execute('select count(*) from material_links').fetchone()[0];d={'url':'https://example.org/industry-test','category':'sheets','question':'price'};a=industry.add_material(self.c,d,'2026');b=industry.add_material(self.c,{**d,'question':'market'},'2026');self.assertEqual(a['id'],b['id']);self.assertEqual(before,self.c.execute('select count(*) from material_links').fetchone()[0]);self.assertEqual(2,self.c.execute('select count(*) from industry_materials where material_id=?',(a['id'],)).fetchone()[0]);self.assertEqual(self.c.execute('select status from industry_materials where material_id=?',(a['id'],)).fetchone()[0],'待核实')
if __name__=='__main__':unittest.main()
