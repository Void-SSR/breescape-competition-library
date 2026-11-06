from pathlib import Path
import json,re,html,sqlite3,csv,collections,shutil
R=Path(__file__).resolve().parent;B=R.parents[1];c=sqlite3.connect(B/'data/library.sqlite3')
raw=json.loads((R/'cozy_cells.json').read_text())[1:];rows=[]
for r in raw:
 d={re.sub(r'\d+','',k):v for k,v in r.items()};u=d.get('L','');m=re.search(r'customer-reviews/([^/?]+)',u);eid=m[1] if m else u
 body=html.unescape(re.sub(r'<[^>]+>',' ',d.get('F',''))).strip();norm=' '.join(body.lower().split())
 if not body or not eid:continue
 old=c.execute('select id from reviews where product_id=? and (external_id=? or normalized=?)',('cozy-comforter',eid,norm)).fetchone()
 if old:rid=old[0]
 else:rid=c.execute('insert into reviews(product_id,external_id,body,normalized,rating,date,sku,region,raw_json) values(?,?,?,?,?,?,?,?,?)',('cozy-comforter',eid,body,norm,int(d['H']),d.get('M',''),d.get('A',''),'US',json.dumps(d,ensure_ascii=False))).lastrowid
 rows.append(dict(duplicate_body=bool(old),id=rid,external_id=eid,title=d.get('D',''),body=body,translation=d.get('G',''),rating=int(d['H']),date=d.get('M',''),sku=d.get('A',''),vine=d.get('C',''),verified=d.get('B',''),url=u,asin=(re.search(r'ASIN=([^&]+)',u).group(1) if 'ASIN=' in u else '')))
c.commit();c.close();(R/'cozy_reviews.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
with (R/'CozyBliss_B0BVQMTD8W_系列评论_1483条.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(len(rows),min(r['id'] for r in rows),max(r['id'] for r in rows),collections.Counter(r['rating'] for r in rows));print('verified',collections.Counter(r['verified'] for r in rows),'vine',collections.Counter(r['vine'] for r in rows))
