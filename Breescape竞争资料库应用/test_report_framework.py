"""Protect the approved research questions against real editing failure modes."""
import copy,json,unittest
from pathlib import Path
import report_framework as F
BASE=Path(__file__).parent/'协作/品牌总览按框架重整_20261105'
class FrameworkAcceptance(unittest.TestCase):
 def setUp(self):
  self.docs=json.loads((BASE/'候选报告.json').read_text())
  self.d=self.docs['shilucheng']
 def check(self):return F.validate_document(self.d,['sheets','topper'])
 def test_published_brands_cover_the_approved_framework(self):
  for d in self.docs.values():self.assertTrue(F.validate_document(d,list(d['product_reports'])))
 def test_missing_research_topic_is_rejected(self):
  self.d['sections'][0]['topics'].pop(1)
  with self.assertRaises(ValueError):self.check()
 def test_chapter_reorder_is_rejected(self):
  self.d['sections'][3],self.d['sections'][4]=self.d['sections'][4],self.d['sections'][3]
  with self.assertRaises(ValueError):self.check()
 def test_question_omission_or_renaming_is_rejected(self):
  for mode in ['omit','rename','reorder']:
   d=copy.deepcopy(self.d);qs=d['sections'][0]['topics'][0]['questions']
   if mode=='omit':qs.pop()
   elif mode=='rename':qs[0]['title']='另选一个想回答的问题'
   else:qs[0],qs[1]=qs[1],qs[0]
   with self.assertRaises(ValueError):F.validate_document(d)
 def test_whole_product_cannot_disappear(self):
  s=self.d['sections'][1];s['topics']=[t for t in s['topics'] if t['product_id']!='topper']
  with self.assertRaises(ValueError):self.check()
 def test_two_products_cannot_be_interleaved(self):
  ts=self.d['sections'][1]['topics'];ts[1],ts[3]=ts[3],ts[1]
  with self.assertRaises(ValueError):self.check()
 def test_evidence_must_belong_to_current_topic(self):
  self.d['sections'][0]['topics'][0]['questions'][0]['record_ids']=[999999]
  with self.assertRaises(ValueError):self.check()
 def test_sales_reason_has_only_two_approved_questions(self):
  topics=[t for d in self.docs.values() for t in d['sections'][1]['topics'] if F.topic_number(t['topic'])==6]
  for t in topics:self.assertEqual([q['title'] for q in t['questions']],['产品销量背后的主要驱动因素是什么？','相比同类产品，真正领先的地方是什么？'])
 def test_all_original_feedback_categories_preserved(self):
  old=json.loads((BASE/'修改前报告.json').read_text())['shilucheng']
  get=lambda d:next(t['feedback'] for t in d['sections'][1]['topics'] if t.get('feedback'))
  self.assertEqual(get(old),get(self.d));self.assertEqual(len(get(self.d)['rows']),83)
if __name__=='__main__':unittest.main()
