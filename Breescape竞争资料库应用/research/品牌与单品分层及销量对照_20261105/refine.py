import sys,pathlib,json
W=pathlib.Path(__file__).parent;ROOT=W.parents[1];sys.path.insert(0,str(ROOT));import server,reports
with server.conn() as c:
 d=json.loads(c.execute('SELECT document FROM brand_reports WHERE brand_id="shilucheng"').fetchone()[0]);now=server.now()
 d['summary']='Shilucheng以价格可负担、睡着舒服介绍床品，经营床单、褥垫、毯等家纺，已进入TikTok、Amazon、Walmart与独立站。竹混纺床单与填充褥垫分别从面料触感和床垫加软切入；品牌总收入、渠道贡献和长期竞争壁垒仍缺经营数据验证。'
 d['sections'][1]['headline']='床单强调柔滑凉感，褥垫强调蓬松加软'
 d['sections'][1]['summary']='竹混纺床单通过面料触感与四件、六件套组合提供床面舒适；填充褥垫通过不同厚度增加柔软度，同时宣传凉感和透气。两款商品分别保留价格、平台表现与消费者研究。'
 d['product_reports']['topper']['merchant_reason']['detail']='尚未见主次清晰的单一主打概念'
 d['product_reports']['topper']['key_facts'][1]['detail']='全球、全部规格，扣除退货；11月5日'
 d['product_reports']['sheets']['key_facts'][2]['value']='竹源人造丝混纺'
 for t in d['sections'][1]['topics']:
  for q in t.get('questions',[]):
   for f in q.get('figures',[]):
    if f['material_id']==48:f['caption']='商品页历史截图：11月4日，深灰色单人床三件套；与本次白色双人床报价分开记录。'
 r=c.execute('SELECT body FROM records WHERE id=78').fetchone()[0].replace('整个多规格商品链接；非月销量','全球、整个多规格商品链接，扣除退货；非月销量')
 c.execute('UPDATE records SET body=?,updated_at=? WHERE id=78',(r,now))
 r=c.execute('SELECT body FROM records WHERE id=79').fetchone()[0].replace('标题写Bamboo Top；参数写Cotton','标题写竹源表层（Bamboo Top）；参数写棉（Cotton）')
 c.execute('UPDATE records SET body=?,updated_at=? WHERE id=79',(r,now))
 for rid in [51,133]:
  r=c.execute('SELECT body FROM records WHERE id=?',(rid,)).fetchone()[0].replace('15:20—15:22','15:20');c.execute('UPDATE records SET body=?,updated_at=? WHERE id=?',(r,now,rid))
 for s in d['sections']:
  s['reviewed_revision']=reports.section_revision(c,'shilucheng',s['number']);s['updated_at']=now
 d['reviewed_revisions']={str(s['number']):s['reviewed_revision'] for s in d['sections']};d['updated_at']=now
 c.execute('UPDATE brand_reports SET document=?,updated_at=? WHERE brand_id=?',(json.dumps(d,ensure_ascii=False),now,'shilucheng'))
f=ROOT/'data/attachments/三款床单_本次核查说明_20261105.md';f.write_text(f.read_text().replace('15:20—15:22','15:20'))
