import sys,pathlib,json
W=pathlib.Path(__file__).parent;ROOT=W.parents[1];sys.path.insert(0,str(ROOT));import server,reports
p=json.loads((W/'published.json').read_text());rr=p['record_keys'];ms=p['source_keys'];now=server.now()
with server.conn() as c:
 r=c.execute('SELECT body FROM records WHERE id=?',(rr['cozy_matrix'],)).fetchone()[0]
 row='| [泡泡仿毛皮盖毯（灰色扎染）](https://cozybliss.com/products/bubble-faux-fur-throw-blanket) | $69–139 |'
 r=r.replace('\n\n2026年11月5日','\n'+row+'\n\n2026年11月5日');c.execute('UPDATE records SET body=?,updated_at=? WHERE id=?',(r,now,rr['cozy_matrix']))
 mid=c.execute('INSERT INTO materials(title,url,source_type,publisher,published_at,retrieved_at,summary,local_path,access_note) VALUES(?,?,?,?,?,?,?,?,?)',('截图｜Shilucheng褥垫商品与选中规格',None,'页面截图','TikTok / Shilucheng','',now,'灰色 / Queen / 2英寸：$41.90、70.8K累计售出与9,008条全球评价。','attachments/topper_20261105.png','原始页面见对应商品资料。')).lastrowid
 c.execute('INSERT INTO material_links(material_id,brand_id,product_id,section,topic) VALUES(?,?,?,?,?)',(mid,'shilucheng','topper',2,server.TOPICS[2][0]))
 summaries={
 'cozy-bliss':['Cozy Bliss的产品覆盖毯、被、床单与枕；官网、Amazon和TikTok均有销售入口，品牌整体销售规模尚未公开。','本款为Amazon灰蓝Queen凉感被，面料标注90%尼龙与10%氨纶，当前页面价为69.99美元。官网近似款保持独立，不混用评价和材料数据。','已确认TikTok、Instagram和Facebook账号，并收录官网促销与服务信息；达人销售和视频转化数据仍缺。','目前可追溯到品牌自述的2018年起点、2020年加拿大商标申请及2025年集团快闪公告，尚无相应销售增量证明。'],
 'sheex':['SHEEX从运动服面料的触感与性能出发开发床品，目前官网覆盖多个床单系列及被、枕、睡衣等产品。品牌总销售额与渠道份额尚未公开。','本款为Original Performance经典性能床单。亮白Queen四件套当前页面价194.35美元，面料为87%聚酯纤维与13%氨纶。','官网关联多个社交账号，另有公开联盟推广规则、睡眠主题活动和历史广告案例；这些记录不能代替渠道成交占比。','创始故事、2020年Midnight Label合作与2026年Sleep Week均有官方材料。历史广告案例另外保留统计边界，不用来代表当前品牌增长。']}
 for bid in ['cozy-bliss','sheex','shilucheng']:
  d=json.loads(c.execute('SELECT document FROM brand_reports WHERE brand_id=?',(bid,)).fetchone()[0])
  if bid in summaries:
   for s,summary in zip(d['sections'][:4],summaries[bid]):s['summary']=summary
  else:
   t=next(t for t in d['sections'][1]['topics'] if t['product_id']=='topper' and t['topic']==server.TOPICS[2][0]);t['questions'][0]['figures']=[dict(material_id=mid,source_id=ms['topper'],caption='TikTok褥垫页面：选中灰色、双人床（Queen）、2英寸厚规格。')]
  if bid=='sheex':
   t=d['sections'][1]['topics'][0];t['questions'][0]['figures'][0]['caption']='SHEEX经典床单：亮白色Queen规格，页面价194.35美元。'
  for s in d['sections']:
   s['reviewed_revision']=reports.section_revision(c,bid,s['number']);s['updated_at']=now
  d['reviewed_revisions']={str(s['number']):s['reviewed_revision'] for s in d['sections']};d['updated_at']=now
  c.execute('UPDATE brand_reports SET document=?,updated_at=? WHERE brand_id=?',(json.dumps(d,ensure_ascii=False),now,bid))
 p['source_keys']['topper_shot']=mid;p['finalized_at']=now
(W/'published.json').write_text(json.dumps(p,ensure_ascii=False,indent=2))
print('reports summaries and product screenshots verified')
