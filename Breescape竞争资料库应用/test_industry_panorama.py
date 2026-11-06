"""Acceptance boundaries from the user's approved industry plan."""
import copy,json,sqlite3,unittest
from pathlib import Path
import industry

CONTENT=Path('协作/行业全景补回_20261106/01_核定内容.json')

class PanoramaTest(unittest.TestCase):
 def setUp(self):
  self.d=json.loads(CONTENT.read_text())
  self.c=sqlite3.connect(':memory:')
  with sqlite3.connect('file:data/library.sqlite3?mode=ro',uri=True) as src:src.backup(self.c)
 def tearDown(self):self.c.close()
 def test_import_is_idempotent_and_preserves_competitor_research(self):
  names=['brands','products','reviews','records','observations','brand_reports','material_links']
  before={t:self.c.execute('select * from '+t+' order by rowid').fetchall() for t in names}
  industry.import_document(self.c,self.d,'2099-01-01')
  count=self.c.execute('select count(*) from materials').fetchone()[0]
  industry.import_document(self.c,self.d,'2099-01-02')
  self.assertEqual(count,self.c.execute('select count(*) from materials').fetchone()[0])
  self.assertEqual(before,{t:self.c.execute('select * from '+t+' order by rowid').fetchall() for t in names})
  self.assertEqual(industry.document(self.c),self.d)
 def test_regressions_are_rejected_before_writing(self):
  mutations=[
   lambda d:d['sections'].reverse(),
   lambda d:d['sections'].append({'id':'growth','title':'增长记录'}),
   lambda d:d['market'].update(share_chart=d['materials']['share_chart']),
   lambda d:d['market'].pop('total'),
   lambda d:d['product_view']['categories'][1].update(growth_ids=[]),
   lambda d:d['growth']['cards'][0].update(category='sheets'),
   lambda d:d['product_view']['categories'][0]['groups'][0]['product_ids'].append('rest'),
   lambda d:d['needs']['models'].pop(),
   lambda d:d['needs']['models'][0]['clusters'][0]['items'][0].update(need_id='not-a-need'),
   lambda d:d['mindmap']['lanes'][0].update(scope='unknown')]
  for change in mutations:
   with self.subTest(change=change):
    d=copy.deepcopy(self.d);change(d);before=self.c.total_changes
    with self.assertRaises(ValueError):industry.import_document(self.c,d,'2099')
    self.assertEqual(before,self.c.total_changes)
 def test_publication_matches_required_scope(self):
  self.assertEqual(self.d['title'],'凉感床品行业全景')
  self.assertEqual([s['id'] for s in self.d['sections']],['market','products','materials','needs','mindmap'])
  self.assertEqual(len(self.d['products']),11)
  self.assertEqual([m['id'] for m in self.d['needs']['models']],['all','covers','sheets'])
  self.assertNotIn('share_chart',self.d['market'])
  self.assertIn('第三方模型',self.d['market']['segments'][0]['kind'])
  self.assertTrue(all('暂无' in s['share'] for s in self.d['market']['segments']))
 def test_each_need_can_be_traced_to_a_source(self):
  source_keys={s['key'] for s in self.d['sources']}
  for n in self.d['needs']['need_pool']:
   self.assertTrue(n['evidence']);self.assertTrue(n['refs']);self.assertTrue(set(n['refs'])<=source_keys)
   for rid in n['review_ids']:
    row=self.c.execute('select product_id from reviews where id=?',(rid,)).fetchone()
    self.assertEqual(row[0],'sheets')
 def test_sources_of_nested_growth_case_are_linked_to_products(self):
  industry.import_document(self.c,self.d,'2099')
  url=next(s['url'] for s in self.d['sources'] if s['key']=='rest-growth')
  self.assertTrue(self.c.execute('select 1 from industry_materials im join materials m on im.material_id=m.id where m.url=? and im.category=?',(url,'products')).fetchone())

if __name__=='__main__':unittest.main()
