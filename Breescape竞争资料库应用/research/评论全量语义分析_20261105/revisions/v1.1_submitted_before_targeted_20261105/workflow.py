"""Storage/validation only. Labels and evidence choices are supplied by the analyst."""
from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parent
SOURCE={r['id']:r for r in json.loads((ROOT/'00_source_snapshot.json').read_text())}
def coded():
 p=ROOT/'02_annotations.jsonl'
 return {r['review_id']:r for r in (json.loads(x) for x in p.read_text().splitlines())} if p.exists() else {}
def pending(start=1,n=50):
 done=coded();rows=[r for i,r in SOURCE.items() if i>=start and i not in done][:n]
 for r in rows:print(str(r['id'])+' '+json.dumps(r['body'],ensure_ascii=False))
 return [r['id'] for r in rows]
def save(rows,batch_name):
 done=coded();assert len({r['review_id'] for r in rows})==len(rows)
 for r in rows:
  i=r['review_id'];assert i not in done and i in SOURCE
  for a in r['annotations']:
   assert a['quote'] in SOURCE[i]['body'],(i,a)
   a['quote_start']=SOURCE[i]['body'].index(a['quote']);a['quote_end']=a['quote_start']+len(a['quote'])
  r.update(rule_version='1.0',batch=batch_name,source_group=SOURCE[i]['source_group'],disposition=r.get('disposition','retain'),denominator_included=r.get('denominator_included',True),operator='same_analyst_read_original')
 (ROOT/'batches').mkdir(exist_ok=True)
 p=ROOT/'batches'/f'{batch_name}.json';assert not p.exists();p.write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 with (ROOT/'02_annotations.jsonl').open('a') as f:
  for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')
 (ROOT/'progress.json').write_text(json.dumps({'stage':'逐条全量编码','full_scope':len(SOURCE),'encoded':len(done)+len(rows),'last_batch':batch_name,'remaining':len(SOURCE)-len(done)-len(rows),'scope':'独立底稿，应用未改'},ensure_ascii=False,indent=2))
 print('saved',batch_name,len(rows),'total',len(done)+len(rows))
def manual(entries,batch_name):
 """An entry is [id, explicit analyst labels...]. No text-dependent labels are inferred.
 T03-@pillowcase~relative|literal quote ; absent quote = full short review (<=260 chars).
 Other dimensions: G00+, M01?, R.choice, B.repeat_actual, C.washing, X.unresolved.
 Subject @prior / @other / @unclear; component @pillowcase / @sheet / @set;
 phase @current; relation ~relative / ~expectation; |quote|note.
 """
 out=[]
 for row in entries:
  i=row[0];body=SOURCE[i]['body'];ann=[];notes=[]
  for raw in row[1:]:
   if raw.startswith('NOTE:'):notes.append(raw[5:]);continue
   bits=raw.split('|',2);head=bits[0];quote=bits[1] if len(bits)>1 else body;note=bits[2] if len(bits)>2 else ''
   if len(bits)==1:assert len(body)<=260,(i,'choose a specific evidence quote for long review')
   subject='target_same_product';phase='unspecified';component='unspecified_product_or_set';relation='absolute_or_unspecified'
   if '~' in head:head,relation=head.split('~',1)
   atoms=head.split('@');head=atoms[0]
   for x in atoms[1:]:
    if x=='prior':phase='prior_same_product'
    elif x in ('other','unclear'):subject=x
    elif x=='current':phase='current_reference'
    else:component=x
   valence='not_applicable'
   if head[-1:] in '+-?=':valence={'+':'positive','-':'negative','?':'uncertain','=':'neutral'}[head[-1]];head=head[:-1]
   if head.startswith(('T','G','M')) and '.' not in head:
    import re
    assert re.fullmatch(r'[TGM]\d{2}',head) and valence!='not_applicable',(i,raw)
    dimension='theme'
   else:dimension={'R':'purchase_signal','B':'behavior','C':'context','X':'noncoded'}[head.split('.')[0]];head=head.split('.',1)[1]
   eligible=dimension=='theme' and head.startswith('T') and valence in ('positive','negative') and subject=='target_same_product'
   ann.append(dict(dimension=dimension,code=head,valence=valence,quote=quote,note=note,subject=subject,experience_phase=phase,component=component,relation=relation,primary_count_eligible=eligible,count_unit_key=f'{i}|{head}|{valence}' if dimension=='theme' else ''))
  out.append({'review_id':i,'annotations':ann,'notes':notes})
 save(out,batch_name)
if __name__=='__main__':
 import sys
 pending(int(sys.argv[1]) if len(sys.argv)>1 else 1,int(sys.argv[2]) if len(sys.argv)>2 else 50)
