"""Align displayed analysis with the newly verified comparison; preserve earlier observations."""
import json, pathlib, sys
root = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root))
import server, reports

old_price = '白色双人床四件套为$42.37，高于LDC的$30.99；两款价格观察日相同。'
new_price = '11月5日15:20公开页面中，本款白色双人床四件套为$42.89，高于LDC同规格的$30.99；均为页面报价。'
old_set = '同尺寸深灰色六件套比四件套多两个枕套、贵$3；这是商品设计差别，未证实为独家或主要销量来源。'
new_set = '六件套比四件套多两个枕套；11月4日深灰色双人床报价相差$3。这是商品组合差别，未证实为独家或主要销量来源。'
with server.conn() as c:
    now = server.now()
    doc = json.loads(c.execute('SELECT document FROM brand_reports WHERE brand_id=?', ('shilucheng',)).fetchone()[0])
    for topic in doc['sections'][1]['topics']:
        if topic.get('product_id') == 'sheets':
            for question in topic.get('questions', []):
                for point in question.get('points', []):
                    point['detail'] = point.get('detail', '').replace(old_price, new_price).replace(old_set, new_set)
    row = c.execute('SELECT body,evidence FROM records WHERE id=68').fetchone()
    evidence = list(dict.fromkeys(json.loads(row['evidence']) + [132, 133]))
    c.execute('UPDATE records SET body=?,evidence=?,updated_at=? WHERE id=68',
              (row['body'].replace(old_price,new_price).replace(old_set,new_set),json.dumps(evidence),now))
    c.execute('UPDATE records SET title=?,updated_at=? WHERE id=65',
              ('历史报价｜11月5日上午Chrome会话：本款高于LDC，CGK仅供参考',now))
    row = c.execute('SELECT body FROM records WHERE id=67').fetchone()
    c.execute('UPDATE records SET body=?,updated_at=? WHERE id=67',
              (row['body'].replace('本款同色Queen六件套比四件套多$3','11月4日本款深灰色Queen六件套比四件套多$3'),now))
    for mid in [132,133]:
        c.execute('INSERT OR IGNORE INTO material_links(material_id,brand_id,product_id,section,topic) VALUES (?,?,?,?,?)',
                  (mid,'shilucheng','sheets',2,'6. 产品卖得好的原因'))
    section=doc['sections'][1]
    section['reviewed_revision']=reports.section_revision(c,'shilucheng',2)
    section['updated_at']=now
    doc['reviewed_revisions']['2']=section['reviewed_revision']
    doc['updated_at']=now
    c.execute('UPDATE brand_reports SET document=?,updated_at=? WHERE brand_id=?',
              (json.dumps(doc,ensure_ascii=False),now,'shilucheng'))
