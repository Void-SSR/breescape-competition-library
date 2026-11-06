from pathlib import Path
import sys,sqlite3,json,datetime,csv
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import reports,report_framework as F
from zoneinfo import ZoneInfo
P=Path(__file__).parent
D=json.loads((P/'候选报告.json').read_text())
c=sqlite3.connect(ROOT/'data/library.sqlite3');c.row_factory=sqlite3.Row
now=datetime.datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
# 保存同一篇研究的现行表述；修改前数据库和报告已单独备份。
t=next(t for t in D['shilucheng']['sections'][1]['topics'] if t['topic'].startswith('6.') and t['product_id']=='sheets')
body=[]
for q in t['questions']:
 body.extend([q['title'],q.get('answer','')])
 for i,p in enumerate(q.get('points',[]),1):body.extend([f'{i}. '+p['title'],p.get('detail',''),p.get('evidence','')])
 if q.get('note'):body.append(q['note'])
c.execute('update records set title=?,body=?,updated_at=? where id=68',('销量驱动与相对竞争优势：两项问题的研究结论','\n\n'.join(x for x in body if x),now))
rows=[]
for bid,d in D.items():
 F.validate_document(d)
 d['updated_at']=now
 for s in d['sections']:
  s['updated_at']=now;s['reviewed_revision']=reports.section_revision(c,bid,s['number'])
  d['reviewed_revisions'][str(s['number'])]=s['reviewed_revision']
  for t in s['topics']:
   for q in t['questions']:
    if not q.get('framework_key'):continue
    for rid in q['record_ids']:
     r=c.execute('select * from records where id=?',(rid,)).fetchone()
     assert r and r['brand_id']==bid and r['section']==s['number']
     if s['number']==2:assert r['product_id']==t['product_id']
    rows.append({'品牌':bid,'产品':t.get('product_id') or t.get('scope_product_id') or '品牌整体','板块':s['number'],'研究项':t['display_title'],'问题':q['title'],'回答':q.get('answer') or '；'.join(p['title'] for p in q.get('points',[])) or '已呈现完整分项表','证据记录':','.join(map(str,q['record_ids'])),'状态':q['answer_status'],'页面定位':'http://127.0.0.1:8766/#overview/'+bid,'问题锚点':'question-'+q['id']})
 c.execute('update brand_reports set document=?,updated_at=? where brand_id=?',(json.dumps(d,ensure_ascii=False),now,bid))
c.commit()
with (P/'01_逐题覆盖与依据.csv').open('w',encoding='utf-8-sig',newline='') as out:
 w=csv.DictWriter(out,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(P/'已发布报告.json').write_text(json.dumps(D,ensure_ascii=False,indent=2))
print('已发布',len(D),'品牌；框架回答位置',len(rows))
