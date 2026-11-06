"""Ordered report migration. Apply one research section at a time; idempotent source inserts."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server,reports
ROOT=server.ROOT

def material(c,title,path,section,topic,source,summary,pid=None):
 row=c.execute('SELECT id FROM materials WHERE local_path=?',(path,)).fetchone()
 if row:return row[0]
 mid=c.execute('INSERT INTO materials(title,source_type,publisher,retrieved_at,summary,local_path,access_note) VALUES (?,?,?,?,?,?,?)',(title,'页面截图','Shilucheng / TikTok',server.now(),summary,path,'原始页面：'+source)).lastrowid
 c.execute('INSERT INTO material_links(material_id,brand_id,product_id,section,topic) VALUES (?,?,?,?,?)',(mid,'shilucheng',pid,section,topic))
 return mid

def add_refs(c,rid,mids):
 r=c.execute('SELECT evidence FROM records WHERE id=?',(rid,)).fetchone();ids=list(dict.fromkeys(json.loads(r[0])+mids))
 c.execute('UPDATE records SET evidence=?,updated_at=? WHERE id=?',(json.dumps(ids),server.now(),rid))

def topic(t,bullets,coverage,gap,impact,kind='事实概括',figures=None):
 t.update(bullets=bullets,coverage=coverage,gap=gap,impact=impact,answer_type=kind)
 if figures is not None:t['figures']=figures

def figure(mid,source_id,caption):return {'material_id':mid,'source_id':source_id,'caption':caption}

with server.conn() as c:
 doc=json.loads(c.execute("SELECT document FROM brand_reports WHERE brand_id='shilucheng'").fetchone()[0])
 step=int(sys.argv[1]);s=doc['sections'][step-1]
 if step==1:
  home=material(c,'截图｜官网首屏：场景与促销表达','attachments/Shilucheng_官网首屏_20261104_2318.png',1,server.TOPICS[1][0],'https://shilucheng.com/','完整加载后的首页首屏；展示品牌导航、居家睡眠场景与促销表达。')
  matrix=material(c,'截图｜官网首页：床单、褥垫与毯类陈列','attachments/Shilucheng_官网产品陈列_20261104_2319.png',1,server.TOPICS[1][2],'https://shilucheng.com/','首页商品陈列局部，浏览器中文翻译；展示多个品类，非销量排行或同规格价格比较。')
  add_refs(c,1,[home]);add_refs(c,5,[matrix])
  doc['cover_figure']=figure(home,6,'官网首页｜亚麻床单的睡眠场景与材料表达。截图经过浏览器中文翻译；不作为材料性能验证。')
  doc['summary']='Shilucheng以舒适、材料选择和可负担性表达品牌价值，公开产品布局覆盖床单、褥垫、凉被、枕头及其他家居品类。已确认独立站、Amazon、TikTok和Walmart入口；本次以TikTok美国站竹混纺床单为单品研究切口。'
  doc['summary_record_ids']=[1,3,5,29,7]
  doc['profile']=[
   {'label':'卖什么','value':'床品延伸至家居','detail':'床单、褥垫、凉被、枕头，以及毯、窗帘和地毯等；目录布局不代表收入贡献。','record_ids':[5,31]},
   {'label':'面向谁','value':'追求舒适与可负担性','detail':'这是品牌希望传递的价值；床单商品另明确面向怕热及夜间出汗人群。','record_ids':[3,9]},
   {'label':'在哪里卖','value':'4类已确认渠道入口','detail':'独立站、Amazon、TikTok、Walmart；各渠道销售占比未知。','record_ids':[29]},
   {'label':'先研究什么','value':'TikTok竹混纺床单','detail':'商品ID 1729438233542234865。其他平台同名商品不自动视为同款。','record_ids':[7]}]
  s['headline']='床品为主、家居延伸；舒适与可负担性是主要价值表达'
  s['summary']='网站按品类和材料组织商品，床单、褥垫、毯等共同陈列。多渠道入口和多品类布局已经可见；经营收入集中在哪个渠道、哪个品类，仍需同口径销售数据。'
  s['images']=[]
  t=s['topics'][0]
  t['finding']='品牌希望消费者记住舒适睡眠、材料选择和可负担性。成立年份与经营主体仍需区分核实。'
  t['record_ids']=[1,2,3,28,34,44,48];t['featured']=[]
  topic(t,['品牌自述：希望消费者获得舒适、自然感与可负担的床品；尚无实际消费者画像数据。','美国商标于2017年注册，当前登记持有人为SUZHOU SHUOTANG；这不是品牌成立日期。','卖家自述“公司成立于2003年”；网站、平台和商标主体之间的关系尚未完全对齐。'],'部分回答','品牌创立背景、主体关系、实际消费者画像及消费者认知尚缺可靠依据。','影响品牌沿革、定位有效性与品牌差异化判断。')
  t=s['topics'][1];t['finding']='四类渠道已有公开入口，尚不能按入口数量或商品累计销量判断品牌的收入结构。'
  topic(t,[],'部分回答','品牌总收入、同期间渠道销售额与增长率尚无可靠数据。','不能计算渠道份额或判断最大、增长最快的渠道。')
  t=s['topics'][2];t['finding']='网站目录覆盖多个品类；在已观察的同店商品中，目标床单的累计售出展示高于列出的褥垫与毯类链接。'
  t['record_ids']=[5,31,32,33,6];t['featured']=[{'record_id':31,'mode':'table'},{'record_id':33,'mode':'table'}]
  topic(t,['目录共30个产品条目，其中25个品牌标签为Shilucheng；其中3个链接含其他品牌名称，归属待核实。','床单有竹混纺、竹源粘胶及亚麻等材料路线；不同材料和规格的价格不直接用于判断溢价。'],'部分回答','同期间单品收入和品牌总收入缺失；网站部分条目的品牌归属待核实。','不能由多品类在售推出均衡增长，也不能计算单品贡献与爆款依赖。',figures=[figure(matrix,6,'首页产品陈列局部：床单、褥垫与毯共同出现。截图经过浏览器中文翻译；展示价不作同规格比较。')])
 elif step==2:
  shot=material(c,'截图｜竹混纺床单商品首屏及达人精灵速览','attachments/Shilucheng_床单商品首屏_20261104.png',2,server.TOPICS[2][0],'https://shop.tiktok.com/us/pdp/1729438233542234865','2026-11-04 Chrome已登录页面；选中Bamboo-Dark Grey / Twin / 3PC。插件与平台指标分开标注。','sheets')
  add_refs(c,7,[shot]);add_refs(c,38,[shot])
  c.execute('UPDATE records SET body=body || ?,updated_at=? WHERE id=38 AND body NOT LIKE ?',('\n\n2026-11-04晚间复核：平台首屏仍展示4.4/5、435.5K累计售出和46.2K评价摘要；达人精灵商品速览显示435,492累计销量、46,170评价。插件数值另存为该来源的观察，保留前次平台46,166条的历史读数。',server.now(),'%晚间复核%'))
  for metric,value,unit in [('插件累计销量','435492','件'),('插件评价数','46170','条')]:
   if not c.execute('select 1 from observations where product_id=? and metric=? and value=?',('sheets',metric,value)).fetchone():
    c.execute('INSERT INTO observations(product_id,metric,value,unit,variant,scope,observed_at,retrieved_at,source_url,source_type,availability,note) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',('sheets',metric,value,unit,'商品链接全部规格','达人精灵商品速览；累计口径，非月销','2026-11-04 晚间',server.now(),'https://shop.tiktok.com/us/pdp/1729438233542234865','第三方插件页面展示','页面已核实','截图保存；尚未核实插件底层统计规则'))
  s['summary']='目标链接已有435.5K累计售出展示，商家以柔滑、凉爽透气、深口袋和可负担的酒店感组织购买理由。库内1,628条有效文本可用于后续主题分析；采样包含一星补充，不能代表总体意见比例。'
  t=s['topics'][0]
  t['finding']='竹源人造丝与聚酯混纺，以材料、体感与床垫适配共同组织购买理由；目前尚未证明这些构成竞争优势。'
  topic(t,['商品描述：60%竹源人造丝＋40%聚酯；14英寸口袋可拉伸适配至16英寸床垫，属于商家参数。','平台首屏：4.4/5、累计售出435.5K；达人精灵另显示435,492件和46,170条评价，保留各自来源。','同色同日比价：Twin/3PC $32.37，Queen/4PC $42.37，Queen/6PC $45.37；是页面价，非最终结算价。'],'部分回答','同规格竞争对照、实物/检测依据与织法描述冲突尚未解决。','只能说明购买理由设计，不能认定比竞争产品更凉、更好或有溢价。',figures=[figure(shot,3,'商品首屏｜Bamboo-Dark Grey / Twin / 3PC，展示价$32.37。顶部为达人精灵，商品区为TikTok平台；截图经过浏览器中文翻译。')])
  t=s['topics'][1];t['featured']=[{'record_id':40,'mode':'table'}]
  t['finding']='评论语料已准备好，认可点、痛点和购买理由仍需逐条编码。当前先说明样本从哪里来、能回答什么。'
  topic(t,['样本1,628条，评论日期覆盖2025-08-20至2026-11-04；规范化文本无重复。','共820条一星评论，包含专门补采批次；后续主题占比必须注明分母与采样范围。','购买前的选择理由与购买后的使用体验将分别标注；缺少购买前表述时不倒推动机。'],'部分回答','主题TOP3、购买动机与未满足需求尚未完成编码。','无法报告认可/不认可主题占比，也不能据此判断总体差评率。')
  topic(s['topics'][2],[],'等待前置研究','评论主题、同规格竞争对照与内容转化证据尚缺。','尚不能确定成交主要由产品、价格、品牌还是营销驱动。','研究问题')
  for t in s['topics'][3:]:topic(t,[],'尚未研究','该产品尚未进入本轮研究。','不与床单样本混合。','研究问题')
 elif step==3:
  c.execute('UPDATE materials SET title=? WHERE id=27',('候选清单｜床单关联视频19条（前五条已选入研究）',))
  shot=material(c,'截图｜用户已确认的商品关联视频TOP5','attachments/Shilucheng_关联视频TOP5_20261104.png',3,server.TOPICS[3][1],'https://shop.tiktok.com/us/pdp/1729438233542234865','页面展示前五条；心形图标旁为点赞量，均有创作者获得佣金标识。不是全平台或销售排行。','sheets')
  body='用户已确认采用目标床单商品页关联视频区的前五条（V01—V05）作为研究对象。2026-11-04复核展示顺序，点赞数依次下降；平台完整排序算法未核实。\n\n| 编号 | 作者 | 点赞展示 | 画面/文案线索 |\n| --- | --- | --- | --- |\n| V01 | Alyssa🍓 | 185.1K | 铺床画面；凉爽与柔软 |\n| V02 | Kat Kag ☕️✨ | 144.5K | 柔软竹床单、秋季颜色与促销 |\n| V03 | Ben | 140.1K | 缎面床单不舒适；换用竹床单 |\n| V04 | Ben | 133.7K | 缎面触感类比、竹床单与售罄提示 |\n| V05 | Ben | 125.6K | 对缎面床单的否定；换用竹床单 |\n\n五条均有创作者获得佣金标识。此表只记录可见画面与文案，不代表已完成完整视频解读。独立作品链接、发布时间、播放/评论/分享和销售转化待核实；当前以商品页链接、编号、作者、截图及原候选表回溯。'
  c.execute('UPDATE records SET title=?,body=?,kind=?,status=?,evidence=?,updated_at=? WHERE id=17',('商品页关联视频TOP5：对象已确认',body,'事实','已核实页面信息',json.dumps([3,27,shot]),server.now()))
  r=c.execute('select body from records where id=43').fetchone()[0]
  r=r.replace('19条均为待确认候选，未评定爆款TOP5。','用户现已选定V01—V05作为商品页关联视频TOP5；其余14条保留为候选备查。')
  c.execute('UPDATE records SET body=?,updated_at=? WHERE id=43',(r,server.now()))
  c.execute('UPDATE records SET body=?,updated_at=? WHERE id=18',('TOP5对象已确认，已记录封面画面、文案与点赞展示；等待完整视频研究和转化资料后再判断传播策略、消费者认知及可模仿形式。',server.now()))
  s['headline']='商品关联视频前五条已确定，3条来自同一作者'
  s['summary']='五条均有佣金合作标识。可见画面与文案覆盖铺床体验、柔软凉感，以及从缎面床单转向竹床单的替换表达。它们是内容研究样本，尚不能说明品牌整体投放策略或销售转化。'
  s['boundary']='选样范围是这一个商品页展示的前五条，不是全平台销量TOP5。点赞不等于播放或成交；当前素材观察不替代完整视频分析。'
  t=s['topics'][0]
  topic(t,[],'部分回答','发布频率、完整账号矩阵、自营/达人及直播/短视频销售占比缺失。','不能比较渠道效率或销售构成。',figures=[figure(24,4,'TikTok店铺公开页面；累计售出为全店口径，不能当作目标床单销量。')])
  t=s['topics'][1];t['finding']='按已确认口径选入V01—V05；其中Ben占3条。先固定研究对象，再补完整内容与效果资料。';t['featured']=[{'record_id':17,'mode':'table'}]
  topic(t,[],'部分回答','独立作品链接、发布时间、完整视频解读及播放/互动/转化数据待补。','能描述选样与表层表达，尚不能解释为什么爆或证明能带货。',figures=[figure(shot,3,'商品页关联视频TOP5（页面展示前五条）。从左至右为V01—V05；数字为点赞量。')])
  t=s['topics'][2];t['finding']='待完整视频研究后，再归纳值得模仿的表达形式及适用条件。'
  topic(t,[],'等待前置研究','完整内容研究及可验证的效果证据尚未齐备。','暂不将高点赞或重复作者直接当作营销成功机制。','研究问题')
  s['images']=[41,42]
 elif step==4:
  t=s['topics'][0]
  topic(t,[],'部分回答','重要产品首发、渠道进入、定位变更的明确日期及背景仍缺。','现有时间线能核查事件，尚不能还原完整发展阶段。')
  t=s['topics'][1]
  topic(t,[],'等待前置研究','动作前后的销售变化与投放、渠道资料缺失。','事件发生不等于事件推动增长。','研究问题')
 elif step==5:
  for t in s['topics']:
   topic(t,[],'等待前置研究','消费者购买动机、竞争比较及品牌能力证据尚未齐备。','现阶段不认定品牌心智、溢价或长期壁垒。','研究问题')
 elif step==6:
  c.execute('UPDATE records SET body=?,updated_at=? WHERE id=24',('TOP5已按目标商品页展示前五条确认。完整内容、转化效果及对Breescape的适用条件待研究；目前不输出确定模仿建议。',server.now()))
  s['topics'][1]['finding']='TOP5已确定；待完整内容、转化效果与我方适用条件核实后，再提出营销借鉴。'
  gaps=['同规格竞品比较与消费者主题编码','完整视频、转化效果与我方适用条件','消费者体验或实物/检测证据','需求规模、竞争强度、支付意愿与我方能力','前五板块的充分证据与优先级比较']
  for t,gap in zip(s['topics'],gaps):topic(t,[],'等待前置研究',gap+'待补。','仅保留研究问题，尚不作为正式建议。','研究问题')
 else:raise SystemExit('该板块迁移尚未配置')
 s['reviewed_revision']=reports.section_revision(c,'shilucheng',step);s['updated_at']=server.now();doc['updated_at']=server.now()
 doc['reviewed_revisions']={str(n):reports.section_revision(c,'shilucheng',n) for n in range(1,7)}
 c.execute('UPDATE brand_reports SET document=?,updated_at=? WHERE brand_id=?',(json.dumps(doc,ensure_ascii=False),server.now(),'shilucheng'))
 c.execute('INSERT INTO events(action,detail,created_at) VALUES (?,?,?)',('总览图文升级',f'按顺序整理第{step}板块；保留原始评论与历史指标',server.now()))
 print('完成板块',step)
