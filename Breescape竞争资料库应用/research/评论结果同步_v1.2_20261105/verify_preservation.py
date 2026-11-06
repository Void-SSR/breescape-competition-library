from pathlib import Path
import sqlite3,json,hashlib
ROOT=Path(__file__).resolve().parents[2];P=Path(__file__).resolve().parent;B=ROOT/'data/backups/before_review_sync_v1.2_20261105'
a=sqlite3.connect('file:'+str(B/'library.sqlite3')+'?mode=ro',uri=True);b=sqlite3.connect('file:'+str(ROOT/'data/library.sqlite3')+'?mode=ro',uri=True)
a.row_factory=b.row_factory=sqlite3.Row
rows=lambda c,t:[dict(r) for r in c.execute('select * from '+t+' order by rowid')]
untouched=['brands','products','reviews','observations','imports'];result={}
for table in untouched:
 assert rows(a,table)==rows(b,table),table;result[table+'_unchanged']=len(rows(b,table))
allowed={10,11,12,13,14,21,40,52,53,54,58,59,66,67,68,72};old={r['id']:r for r in rows(a,'records')};new={r['id']:r for r in rows(b,'records')};assert old.keys()==new.keys()
changes={i:[k for k in old[i] if old[i][k]!=new[i][k]] for i in old if old[i]!=new[i]};assert set(changes)==allowed
for i,fields in changes.items():assert set(fields)<={'title','body','kind','status','evidence','updated_at'},(i,fields)
doc0=json.loads(a.execute("select document from brand_reports where brand_id='shilucheng'").fetchone()[0]);doc1=json.loads(b.execute("select document from brand_reports where brand_id='shilucheng'").fetchone()[0])
for n in [1,3,4,6]:assert doc0['sections'][n-1]==doc1['sections'][n-1],n
for t in doc0['sections'][1]['topics']:
 if t['product_id']!='sheets':assert t in doc1['sections'][1]['topics']
for k,v in doc0['sections'][4].items():
 if k not in ['reviewed_revision','current_revision','stale','updated_at']:assert v==doc1['sections'][4][k],k
for table in ['materials','material_links','meta','events']:
 before=rows(a,table);after=rows(b,table)
 assert all(r in after for r in before),table
for r in rows(a,'brand_reports'):
 if r['brand_id']!='shilucheng':assert r in rows(b,'brand_reports')
protected=json.loads((B/'protected_files.json').read_text());changed_files=[f for f,h in protected.items() if not (ROOT/f).exists() or hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=h];assert not changed_files,changed_files
pub=json.loads((P/'publication.json').read_text());
for f in pub['files']:
 assert hashlib.sha256((ROOT/'data'/f['local_path']).read_bytes()).hexdigest()==f['sha256']
 assert hashlib.sha256((ROOT/'research/评论全量语义分析_20261105'/f['filename']).read_bytes()).hexdigest()==f['sha256']
result.update(record_changed_fields=changes,other_records_unchanged=len(old)-len(changes),old_files_unchanged=len(protected),seven_publication_copies_exact=True,other_brand_reports_unchanged=True,sections_1_3_4_6_unchanged=True,section_5_content_unchanged=True,topper_outline_unchanged=True)
(P/'preservation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
