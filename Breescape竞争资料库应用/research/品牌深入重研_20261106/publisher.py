from pathlib import Path
import sqlite3,json,shutil,datetime,sys
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parents[1]
sys.path.insert(0,str(BASE));import reports,report_framework
def mdtable(rows):return '\n'.join('| '+' | '.join(map(str,row))+' |' for row in [rows[0],['---']*len(rows[0]),*rows[1:]])
class Publisher:
 def __init__(self,bid,pid):
  self.bid=bid;self.pid=pid;self.c=sqlite3.connect(BASE/'data/library.sqlite3');self.c.row_factory=sqlite3.Row
  self.now=datetime.datetime.now().astimezone().isoformat(timespec='seconds');self.doc=json.loads((ROOT/f'{bid}_before.json').read_text());self.mid={};self.rid={};self.ev={}
  self.att=BASE/'data/attachments'/f'{bid}_深入重研_20261106';self.att.mkdir(parents=True,exist_ok=True)
  for s in self.doc['sections']:
   for t in s['topics']:
    t['finding']='';t['bullets']=[];t['featured']=[];t['gap']='';t['impact']=''
    for q in t['questions']:
     for k in ['points','tables','links','evidence','note']:q.pop(k,None)
 def topic(self,n):return next(t for s in self.doc['sections'] for t in s['topics'] if report_framework.topic_number(t['topic'])==n)
 def q(self,n,k):return next(q for q in self.topic(n)['questions'] if q.get('framework_key')==k)
 def put(self,n,key,answer,points=None,kind=None,evidence='',status='已回答'):
  q=self.q(n,key);q.update(answer=answer,points=[dict(zip(('title','detail','evidence'),list(x)+['']*(3-len(x)))) for x in (points or [])],ordered=bool(points),evidence=evidence,answer_status=status,presentation=kind or ('answer' if points else 'fact'),review_product_id=self.pid)
  return q
 def material(self,key,title,file=None,url=None,source='研究整理',summary=''):
  local=''
  if file:
   shutil.copy2(ROOT/file,self.att/file);local=str((self.att/file).relative_to(BASE/'data'))
  old=self.c.execute('select id from materials where title=?',(title,)).fetchone()
  if old:i=old[0]
  else:i=self.c.execute('INSERT INTO materials(title,url,source_type,publisher,retrieved_at,summary,local_path,access_note) VALUES(?,?,?,?,?,?,?,?)',(title,None,source,source,self.now,summary,local,('原始网址：'+url if url else '保留研究原文、处理方法及计算记录'))).lastrowid
  self.mid[key]=i;return i
 def record(self,n,title,body,evidence,kind='分析'):
  t=self.topic(n);s=next(s['number'] for s in self.doc['sections'] if t in s['topics']);pid=t.get('product_id')
  old=self.c.execute('select id from records where brand_id=? and title=?',(self.bid,title)).fetchone()
  args=(self.bid,pid,s,t['topic'],title,body,kind,'已复核',json.dumps(list(dict.fromkeys(evidence))),self.now)
  if old:i=old[0];self.c.execute('UPDATE records SET brand_id=?,product_id=?,section=?,topic=?,title=?,body=?,kind=?,status=?,evidence=?,updated_at=? WHERE id=?',(*args,i))
  else:i=self.c.execute('INSERT INTO records(brand_id,product_id,section,topic,title,body,kind,status,evidence,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)',args).lastrowid
  for m in evidence:
   assert self.c.execute('select 1 from materials where id=?',(m,)).fetchone(),m
   if not self.c.execute('select 1 from material_links where material_id=? and brand_id=? and product_id IS ? and section=? and topic=?',(m,self.bid,pid,s,t['topic'])).fetchone():self.c.execute('INSERT INTO material_links(material_id,brand_id,product_id,section,topic) VALUES(?,?,?,?,?)',(m,self.bid,pid,s,t['topic']))
  if i not in t['record_ids']:t['record_ids'].append(i)
  self.rid[title]=i;return i
 def table(self,n,k,title,rows,evidence,note='',comparison=False):
  i=self.record(n,title,mdtable(rows)+'\n\n'+note,evidence,'分析')
  self.q(n,k).setdefault('tables',[]).append(dict(record_id=i,mode='analysis',purpose='core',caption=title,**({'layout':'comparison'} if comparison else {})));return i
 def feedback(self,filename,code,stats,rules,sample,method):
  t=self.topic(5);t['feedback']={**json.loads((ROOT/filename).read_text()),'material_id':code,'calculation_material_id':stats,'method_material_id':rules,'sample_label':sample,'method_paragraphs':method}
  t['questions']=[q for q in t['questions'] if q.get('type')!='feedback-summary']
  t['questions'].insert(0,dict(id=f'{self.bid}-5-feedback',title='评论反馈全貌',framework_key=None,type='feedback-summary',presentation='plain',answer='',record_ids=[],answer_status='已回答',review_product_id=self.pid))
  self.q(5,'positive')['type']='feedback-positive';self.q(5,'negative')['type']='feedback-negative'
 def finish(self,summary,heads,profile,product_summary,reason,facts,pending):
  d=self.doc;d['summary']=summary;d['scope']='按竞品品牌研究框架V1.0及已确认的第6项调整；事实、商业判断与估算分开。2026年11月6日深化，历史事实保留原采集日期；来源与研究缺口见各项依据。';d['updated_at']=self.now
  current={}
  for s,head in zip(d['sections'],heads):
   s['headline']=head;s['summary']='';s['updated_at']=self.now
   for t in s['topics']:
    n=report_framework.topic_number(t['topic']);body=[]
    for q in t['questions']:
     body.append(q['title']+'\n'+q.get('answer',''))
     for j,x in enumerate(q.get('points',[]),1):body.append(str(j)+'. '+x['title']+' '+x.get('detail','')+' '+x.get('evidence',''))
     if q.get('evidence'):body.append(q['evidence'])
    i=self.record(n,f'{self.bid}｜{t["topic"]}｜2026-11-06深入重研','\n\n'.join(body),self.ev[n]);current[n]=i
    t['record_ids']=list(dict.fromkeys([i]+[z['record_id'] for q in t['questions'] for z in q.get('tables',[])]))
    for q in t['questions']:q['record_ids']=t['record_ids'][:]
    t['coverage']='部分回答' if any(q.get('answer_status')=='待确认' for q in t['questions']) else '已回答';t['answer_type']='分析判断'
   s['reviewed_revision']=reports.section_revision(self.c,self.bid,s['number'])
  d['profile']=[dict(label=a,value=b,detail=c,record_ids=[current[n]]) for a,b,c,n in profile]
  d['summary_record_ids']=[current[n] for n in [2,6,13,17]];d['reviewed_revisions']={str(s['number']):s['reviewed_revision'] for s in d['sections']}
  pr=d['product_reports'][self.pid];pr.update(summary=product_summary,merchant_reason=dict(headline=reason,structure='商品主张与真实需求的研究归纳',detail='',record_ids=[current[4]]),key_facts=facts,pending=pending)
  report_framework.validate_document(d,[self.pid]);self.c.execute('UPDATE brand_reports SET document=?,updated_at=? WHERE brand_id=?',(json.dumps(d,ensure_ascii=False),self.now,self.bid));self.c.commit()
  (ROOT/f'{self.bid}_published.json').write_text(json.dumps(d,ensure_ascii=False,indent=2));(ROOT/f'{self.bid}_published_ids.json').write_text(json.dumps({'materials':self.mid,'records':self.rid},ensure_ascii=False,indent=2));print('已发布',self.bid,len(self.rid),'条研究记录',len(self.mid),'项材料')
