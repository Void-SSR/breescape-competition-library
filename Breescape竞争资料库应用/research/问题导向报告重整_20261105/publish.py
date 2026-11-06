import json,sqlite3,sys,shutil
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));import reports
W=Path(__file__).parent;before=json.loads((W/'before.json').read_text());doc=json.loads((W/'report_candidate.json').read_text());feedback=json.loads((W/'feedback.json').read_text());now=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
c=sqlite3.connect(ROOT/'data/library.sqlite3');c.row_factory=sqlite3.Row
for table,rows in before.items():assert [dict(r) for r in c.execute(f'SELECT * FROM {table} ORDER BY rowid')]==rows,table+' changed since backup'
assets=ROOT/'data/attachments/评论全貌与报告重整_20261105';assert not assets.exists();assets.mkdir()
shutil.copy2(W/'评论全貌与完整分项.csv',assets/'评论全貌与完整分项.csv');shutil.copy2(W/'feedback.json',assets/'计算与逐条编号.json')
method='''# 评论全貌汇总与口径｜2026年11月5日

## 可复算结果
主样本928条，文字中含明确认可734条（79.1%），含明确不认可314条（33.8%）。其中129条同时有认可与不认可；605条仅认可、185条仅不认可，9条未作方向判断。相加605+185+129+9=928。

这不是互斥好评率／差评率，也不是满意率。主体包括目标床单使用及本次购买服务；赠品不适用单列。一般“喜欢”与具体体验分开，TOP3仅按具体反馈条数排名。具体条数不是独立顾客数，各主题可重叠。分项主显示占认可734／不认可314评论的比例；CSV同时保留占全部928条比例。

## 原始输入与复算
复用固定v1.2的逐条评论、全部证据标注、分来源主题统计。82项既有统计的评论ID集合已逐项与证据标注重放核对。额外687条一星、13条推荐展示评论不混入主分母。

仅新增两个总体判断：
- R352原文“I would not purchase these sheets again.”明确不愿再买，补入总体不满。后句balled up含义未决，仍不计入起球或滑脱。
- R692为赠品买三套，但赠品为不适用的Queen规格，单列赠品履约不满，不计床单错发或尺寸适配缺陷。

9条未作正负判断的原评论编号：11、89、155、200、216、253、296、428、476。原因包括文本歧义、残缺、对象不明、仅描述物性或购买行为；不依星级强行归类，也不把未判定当成中性满意。

温度主题正面176中，172凉感／少热少汗、2保暖、2未细分调温；负面72中71不够凉／偏热等、1不够暖。尺寸负面38与固定滑脱35相近，边界判断可能影响第三名，不据3条差距认定经营重要性。

旧v1.2文件及原始评论未改动。本文件、CSV和计算JSON为本轮展示汇总，保留全部编号供核查。
'''
(assets/'口径与补判记录.md').write_text(method)
R={r['id']:r for r in before['records']}
def setrecord(rid,title,body,evidence):c.execute('UPDATE records SET title=?,body=?,evidence=?,updated_at=? WHERE id=?',(title,body,json.dumps(evidence),now,rid))
with c:
 mids=[]
 for filename,title,summary in [('评论全貌与完整分项.csv','消费者反馈全貌｜完整分项与两种占比','734条含认可、314条含不认可，含129条褒贬并存；83项具体或一般反馈。'),('口径与补判记录.md','评论全貌｜计算口径与两条总体补判','原v1.2编码保留；总体正负按评论去重，补判不改变含糊主题归类。'),('计算与逐条编号.json','评论全貌｜全部分项及原评论编号','保留正负集合、混合集合、每项分子、分母与计算结果。')]:
  mid=c.execute('INSERT INTO materials(title,source_type,publisher,retrieved_at,summary,local_path,access_note) VALUES (?,?,?,?,?,?,?)',(title,'本地研究结果','已收录评论的逐条语义标注',now,summary,str((assets/filename).relative_to(ROOT/'data')),'仅主样本928条；另两组保留独立。')).lastrowid;mids.append(mid)
  c.execute('INSERT INTO material_links(material_id,brand_id,product_id,section,topic) VALUES (?,?,?,?,?)',(mid,'shilucheng','sheets',2,'5. 消费者评论分析'))
 tf=doc['sections'][1]['topics'][1];tf['feedback'].update(material_id=mids[0],method_material_id=mids[1],calculation_material_id=mids[2])
 body='柔软是最常被具体称赞的体验；触感、温度和适配是主要具体不满。认可与不认可分开展示，并在研究中分别用于判断已兑现价值与待改善问题。\n\n整体：734条含认可（79.1%），314条含不认可（33.8%）；129条有赞有贬，同时包含于两类，9条未判定。\n\n'
 for valence,label in [('positive','消费者认可的内容'),('negative','消费者不认可的内容')]:
  body+=label+'\n\n| 反馈 | 评论数 | 占本类反馈 | 分类 |\n| --- | --- | --- | --- |\n'
  for r in feedback['rows']:
   if r['valence']!=valence:continue
   marker=f"TOP{r['rank']} · " if r.get('rank',99)<=3 else ''
   body+=f"| {marker}{r['label']} | {r['count']} | {r['percent_group']:.1f}% | {'一般评价' if r['general'] else '具体反馈'} |\n"
  body+='\n'
 body+='统计以928条近期全星级为总分母；分项分别以734条含认可、314条含不认可为分母。同条可多主题，各项不相加。详细日期、统计口径、温度细分、未决编号和两条总体补判见随附记录；不作为全体买家的满意率。'
 setrecord(12,'消费者认可与不认可：整体占比及全部分项',body,list(dict.fromkeys(json.loads(R[12]['evidence'])+mids)))
 newbody='本节分别回答三个问题：消费者为什么购买、相较同类真正领先在哪里、销量背后的主要驱动是什么。\n\n'
 for q in doc['sections'][1]['topics'][2]['questions']:
  newbody+=q['title']+'\n'+q['answer']+'\n\n'
  for i,p in enumerate(q.get('points',[]),1):newbody+=f"{i}. {p['title']}\n{p.get('detail','')}\n"+(p.get('evidence','')+'\n' if p.get('evidence') else '')+'\n'
  if q.get('evidence'):newbody+=q['evidence']+'\n\n'
  if q.get('note'):newbody+=q['note']+'\n\n'
 setrecord(68,'为什么买、哪里领先、哪些因素推动销售',newbody,json.loads(R[68]['evidence']))
 # Purpose determines whether a table is prominent, projected or expandable.
 for s in doc['sections']:
  for t in s['topics']:
   for q in t.get('questions',[]):
    for f in q.get('tables',[]):
     if f['record_id'] in [29,33,46]:f['columns']=[0,1]
     if f['record_id']==31:f['columns']=[0,1,2];f['caption']='各品类与官网展示价格（美元）'
     if f['record_id']==33:f['caption']='四款已观察商品的累计售出（2026年11月4日）'
     if f['record_id']==46:f['caption']='官网关联的社交账号（2026年11月4日）'
    if q['id']=='channel-accounts':q['answer']='已找到5个社交账号入口及1个TikTok店铺，矩阵完整性尚未核实。'+q['answer']
 # Preserve reference numbering and all earlier raw records; only report-purpose projections change.
 for s in doc['sections']:
  s['current_revision']=s['reviewed_revision']=reports.section_revision(c,'shilucheng',s['number']);s['stale']=False;s['updated_at']=now
 doc['reviewed_revisions']={str(s['number']):s['current_revision'] for s in doc['sections']};doc['summary_stale']=False;doc['updated_at']=now
 c.execute("UPDATE brand_reports SET document=?,updated_at=? WHERE brand_id='shilucheng'",(json.dumps(doc,ensure_ascii=False),now))
(W/'published_document.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2));(W/'changes.json').write_text(json.dumps({'material_ids':mids,'records_changed':[12,68],'questions':39,'feedback_rows':83,'time':now},ensure_ascii=False,indent=2));print('published',mids,'39 questions / 83 feedback rows')
