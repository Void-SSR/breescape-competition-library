from editorial_upgrade import *
import csv,re
ROOT=Path(__file__).resolve().parents[1]
DAY='2026-11-05'
TOPIC=server.TOPICS[2][2]
shi='https://shop.tiktok.com/us/pdp/bamboo-sheets-set-by-shilucheng-4-6-pc-cooling-deep-pocket-silky-soft/1729438233542234865'
ldc='https://shop.tiktok.com/us/pdp/bamboo-sheet-set-by-ldc-lux-decor-skin-friendly-deep-pockets/1729539387064423033'
cgk='https://shop.tiktok.com/us/pdp/bamboo-sheet-set-by-cgk-linens-100-breathable-moisture-wicking-deep-pocket/1730084277563069132'
# Purposeful cases, read in context. Never treated as a random prevalence sample.
cases={
11:('竞争参照','使用过Bedsure竹床单，觉得本款不一样；不是同规格实测。'),
110:('替换/实际复购','自述比此前Walmart购买的床单舒服，已再购。'),
127:('价格不足以抵消差异','承认便宜很多，仍因不及其他竹床单柔软而退。'),
158:('凉感不是保留的必要条件','认为不凉，仍评价价格合适。'),
221:('实际复购','因柔软、适配厚床垫及凉爽体验而购买第二套。'),
28:('换色/实际复购','前一套使用约六个月后换色购买；不代表总体复购周期。'),
57:('多色/实际复购','明确第三次购买，提及三种颜色。'),
71:('具体使用需求','为触觉敏感的女儿购买，报告接受；不能扩为医疗功效。'),
132:('多色/实际复购','明确第三次购买，认可柔软与凉爽。'),
143:('多件不等于复购','一次买三套含礼物，因床角滑脱不满。'),
344:('价值相对参照','认为比Amazon同价选项好；对手型号未知。'),
369:('价值相对参照','自述此前花更多的钱，体感不及本款；未核实旧款。'),
372:('待探索需求','自述较旧款少沾狗毛；仅个案，未实测、未证明购买前动机。'),
452:('明确购买动机','明确为凉感购买，并认为凉感得到满足。'),
469:('实惠舒适/多件','一次购买两套，认为便宜且舒服符合所求。'),
475:('价格触发试购','此前想试，看到合适价格后下单；未提具体折扣。'),
527:('价值容忍度','不如广告柔软，但认为对得起价格。'),
535:('材料期待','原本想买100%竹源版本，买后退货。'),
549:('感知价值','自述触感像更贵床单；更多颜色是未来意向，不算已发生复购。'),
578:('凉感不是满意的必要条件','凉感不确定，但舒服且认为值。'),
580:('实际复购','明确因手感喜欢已第二次订购。'),
610:('凉感不是意向复购的必要条件','认为不凉、并非预期竹体验，仍认可舒服、颜色、价格且愿再买；非已发生复购。'),
621:('一致性正例','自述多套质量一致、洗后柔软；与颜色差异投诉对照。'),
641:('多床/实际加购','自述已有三套并为女儿买一套；#640高度相似，不当独立佐证重复计算。'),
692:('促销/多件动机','明确称为获赠床垫罩买三套；赠品错码。只能证明买家自述，活动条款未核。'),
713:('新居/客房','明确新买房需要床品，放客房；不代表特定细分市场规模。'),
773:('价值反例','与此前Amazon竹床单相比更粗糙，认为便宜幅度不值得。'),
824:('替换/实际复购','自述第三套，比较Sam’s旧款更便宜且舒服。'),
912:('明确购买动机','因围绝经期热潮红寻找凉床单；效果为自述，非医疗证据。'),
971:('明确购买动机/反例','因降温调温承诺下单，体验比原有性能棉床单更热。'),
984:('达人预期','认为与达人描述不符；不可计算达人订单占比。'),
987:('明确购买动机/反例','因凉感买，认为与普通Walmart床单无差别。'),
1013:('降级保留','自述20美元，觉得普通而改放客房；非全体历史成交均价。'),
1022:('多件/失望','一次购买八套后失望；多件成交不等于多名独立消费者。'),
1203:('认知迁移','原期待像竹睡衣一样弹软；视频与评论带来期待，不是材质实测。'),
1284:('复购反例','前次浅紫柔软，本次粗糙；不能证明普遍批次问题。'),
1289:('材料概念/反例','竹表述吸引注意，后才注意60/40比例；用户当时所见页未核。'),
1354:('竞争参照','使用后准备回到Bedsure；未证明Breescape具体型号领先。'),
1389:('促销改变时机','等待约六个月，看到促销后下单；随后不满适配。'),
1409:('视频触发期待','明确看过视频后期待凉与软；收货后不满。'),
1419:('配色触发多件','明确颜色吸引而买多套；已有高端竹床单参照，最终失望。'),
1464:('低价与信任','对低价质量原有怀疑，仍试购后失望；低价也可能增加风险感。'),
1519:('跨颜色复购反例','因此前白色体验好而买粉色，报告体感不同。'),
1522:('凉感不是保留的必要条件','认为不能整晚保持凉爽，但因舒服而留下。'),
1618:('评论促成试购','明确因评论说凉爽而购买；推荐样本，不能代表总体。'),
1624:('规格需求/审美','分体式King难找到合适床单，认为本套合适且配色提升卧室；推荐样本。'),
1627:('内容与品牌竞争','受影响试购后失望，准备回到旧品牌Bedsure；推荐样本，不作流失率。')}
with server.conn() as c:
 rows=list(c.execute('select * from reviews where product_id="sheets" order by id'))
 p1=r'\b(because|saw|ads?|videos?|influencers?|hype|viral|sale|discount|coupon|cheaper|compared|cariloha|brooklinen|bed.?sure|cozy earth|luxclub|amazon|walmart|tiktok|tik tok)\b'
 p2=r'\b(price|value|expensive|bought.*(sets|gift|daughter|son|mom)|second|third|fourth|my.*set|guest|gift)\b'
 candidate=[r for r in rows if re.search(p1,r['body'],re.I) or re.search(p2,r['body'],re.I)]
 assert len(candidate)==210
 for filename,rs,annotated in [('Shilucheng_畅销原因_210条检索候选.csv',candidate,False),('Shilucheng_畅销原因_47条证据与反例.csv',[r for r in rows if r['id'] in cases],True)]:
  out=[]
  for r in rs:
   raw=json.loads(r['raw_json']);tag,note=cases.get(r['id'],('',''))
   out.append({'本库评论ID':r['id'],'平台评论ID':r['external_id'],'商品ID':'1729438233542234865','商品链接':shi,'日期':r['date'],'星级':r['rating'],'规格':r['sku'],'采样范围':raw.get('采样范围'),'研究分类':tag if annotated else '', '研究摘记':note if annotated else '', '原文':r['body']})
  with (ROOT/'data/attachments'/filename).open('w',encoding='utf-8-sig',newline='') as f:
   w=csv.DictWriter(f,fieldnames=out[0]);w.writeheader();w.writerows(out)
 assert len(cases)==47
 notes=material(c,'畅销原因｜47条购买过程证据与反例','',2,TOPIC,path='attachments/Shilucheng_畅销原因_47条证据与反例.csv',kind='评论定性研究',publisher='Breescape研究',pid='sheets')
 cand=material(c,'畅销原因｜210条检索候选及原文','',2,TOPIC,path='attachments/Shilucheng_畅销原因_210条检索候选.csv',kind='评论研究底稿',publisher='Breescape研究',pid='sheets')
 for mid in [3,19,27,49,51,54,55,56,57,58,59,60,61]:
  c.execute('INSERT INTO material_links(material_id,brand_id,product_id,section,topic) SELECT ?,?,?,?,? WHERE NOT EXISTS (SELECT 1 FROM material_links WHERE material_id=? AND brand_id=? AND product_id=? AND section=? AND topic=?)',(mid,'shilucheng','sheets',2,TOPIC,mid,'shilucheng','sheets',2,TOPIC))
 shots=[]
 for title,path,source in [('Shilucheng｜白色Queen四件套价格核对','Shilucheng_White_Queen价格核对_2026-11-05.png',shi),('LDC｜白色Queen四件套价格核对','LDC_Queen价格核对_2026-11-05.png',ldc),('CGK｜白色Queen套装价格核对','CGK_Queen价格核对_2026-11-05.png',cgk)]:
  shots.append(material(c,title,'',2,TOPIC,'2026-11-05在同一Chrome会话选择规格；页面报价，非结算价。原页：'+source,path='attachments/'+path,kind='商品页截图',publisher='TikTok Shop',pid='sheets'))
 for label,name in [('Shilucheng','shilucheng_white_queen'),('LDC','ldc_queen'),('CGK','cgk_queen')]:
  src=ROOT/'research'/f'{name}_20261105.txt';dst=ROOT/'data/attachments'/src.name;dst.write_bytes(src.read_bytes())
  material(c,label+'｜价格与页面信息观察文本','',2,TOPIC,path='attachments/'+dst.name,kind='页面观察文本',publisher='TikTok Shop',pid='sheets')
 target=material(c,'CGK官方卖家在Target的Queen四件套信息','https://www.target.com/p/-/A-1000038143',2,TOPIC,'辅助确认该品牌纯竹源系列有Queen四件套；未通过GTIN证明与TikTok选中SKU完全一致。',kind='零售商品页',publisher='Target / CGK Unlimited',pid='sheets')
 excluded=material(c,'FindNiche｜周订单榜单（不可用于当前销量归因）','https://findniche.com/zh/tiktok/trending-textiles-and-soft-furnishings-products-us',2,TOPIC,'仅作排除线索：未给完整统计起止日和商品ID；检索与正文日期不同但数值相同。',kind='第三方估算线索',publisher='FindNiche',pid='sheets')
 hist=material(c,'PennLive｜2023年Shilucheng竹床单促销报道','https://www.pennlive.com/shopping/2023/10/prime-day-2023-sleep-better-with-these-deals-on-bedding-mattresses-and-sleep-essentials.html',4,server.TOPICS[4][0],'2023-10-11刊发的联盟购物文章，证明该品牌竹床单已有公开销售表达；不能对应本次TikTok链接上市时间。',kind='历史媒体报道',publisher='PennLive')
 pricebody='''2026-11-05，同一Chrome会话、TikTok美国站，逐一选择白色和Queen；均为页面报价，未领取优惠券、未结算，不含税费。材料为商家描述。

| 商品 | 白色 Queen 页面价 | 材料路线 | 页面链接累计售出 / 评分 |
| --- | --- | --- | --- |
| LDC Lux Decor / 4件套 | $30.99 | 竹混纺，比例未披露 | 14.7K / 4.4 |
| Shilucheng / 4件套 | $42.37 | 60%竹源人造丝＋40%聚酯 | 435.5K / 4.4 |
| CGK / 套装 | $64.49 | 100%竹源人造丝 | 2.6K / 4.7 |

Shilucheng比所选LDC高$11.38（约36.7%），比所选CGK低$22.12（约34.3%）。这是三个已观察报价的关系，不是全市场最低价扫描，也不是成本或支付溢价的证明。LDC和Shilucheng四件套均含平床单、床笠、两枕套；CGK在TikTok的套件数未明确展示，Target官方卖家有同系列Queen四件套，但未用GTIN确认完全同SKU，因此CGK仅作邻近材料路线参照。

三页均展示免费配送及30天免费退货入口，为平台条件下的共同交易服务，不是本品牌独占优势。累计售出跨规格且上架时长未知，不能当作同周期销售速度或份额。Shilucheng当天插件读数435,505、46,174评价，保留旧观察不覆盖；本次不将短间隔差值外推增长率。'''
 price=record(c,2,TOPIC,'价格检验：它不是这组竞品里最便宜的',pricebody,[3,54,55,target]+shots,pid='sheets')
 direct=record(c,2,TOPIC,'购买过程证据：动机、触发、使用评价和加购分别处理','''全库1628条评论按两组可复现词表检索，得到210条候选，逐条阅读候选并留下47条证据摘记。样本是目的性选择，不估计消费者占比，不把一星补采与主样本混为总体。

| 环节 | 原文可追溯个案 | 可支持什么 | 不支持什么 |
| --- | --- | --- | --- |
| 为什么想试 | #452为凉感买且满意；#912为热潮红找床单；#971/#987因凉感买却失望 | 降低夜间热感确实进入部分人的购买决策 | 真实降温性能或凉感是多数人的首要动机 |
| 为什么此时下单 | #475看见合适价格后买；#1389等促销约六个月 | 相对预算和促销可改变购买时机 | 全市场最低价、价格弹性数值 |
| 信息如何影响选择 | #1409看视频后期待软凉；#1618因凉感评论购买 | 内容和用户评价进入实际选择过程 | TOP5某条视频造成了这些订单或达人销售占比 |
| 不凉是否就不值 | #158/#578/#610/#1522不认为明显凉，仍认可舒适、价格或选择留下 | 凉感兑现并非所有消费者保留/满意的必要条件 | 凉感不重要，或投诉用户无需改进 |
| 为什么买多件 | #692为赠品一次买三套；#1419因配色买多套；#143为赠礼买三套 | 件数还受促销、配色和礼物用途影响 | 一件等于一名买家，多件等于复购 |
| 为什么又回来 | #28换色、#57第三次、#580因手感再买、#641给女儿添置；#1284/#1519再买后失望 | 部分产品体验与扩展使用支持再购，同时存在中断点 | 已测得品牌留存率、复购收入占比 |
| 消费者在与谁比 | #110 Walmart、#824 Sam’s；#11/#1354/#1627 Bedsure；#971性能棉床单 | 真实参照横跨旧床品、平价零售和其他竹床单 | 这些对手的同规格客观性能排序 |

#641与#640文本高度相似，不作为两个独立证人。#434讨论褥垫复购，不用作床单复购证据。#1618/#1624/#1627来自推荐排序样本，仅作个案。#692赠品条款未独立核实，不能写成当前活动。''',[notes,cand,19],pid='sheets')
 hypothesis=record(c,2,TOPIC,'十种畅销解释：证据强弱与竞争反证','''下表是质性证据综合，不是销售贡献率或因果实验。较强表示有明确购买过程自述与其他材料相互支持；“未成立”针对当前证据，不等于该因素不存在。

| 候选解释 | 已有证据 | 竞争与反证 | 当前判断 |
| --- | --- | --- | --- |
| 低价取胜 | 顾客说价格合适，存在等促销后下单 | 同规格LDC更便宜；另有因体验退货 | 价格有作用；最低价主因不成立 |
| 概念击中需求 | 凉感、软滑和酒店舒适连接具体使用问题；有明确购买动机 | CGK/LDC也在讲凉感；并非独占概念 | 试购解释较强；优于竞品的说服力未量化 |
| 内容制造替换理由 | 已选素材展示旧缎面不适→换床单→折扣；买家谈视频期待 | 五条为高点赞选例，且三条同作者 | 传播机制清楚；订单贡献未测 |
| 实际体验有价值 | 柔软、贴合、舒适促成部分再购；有人不觉得凉仍认可 | 也有人粗糙、脱角、换色后失望 | 支持部分人的价值感，非性能普遍领先 |
| 命中遗漏需求 | 分体King、触觉偏好、新居/客房有个案 | 怕热与深口袋已有竞品供给；小需求未做供给扫描 | 可探索细分，不称已发现蓝海 |
| 促销和套装增加件数 | 等折扣、为赠品买三套；4件升6件仅多$3（11月4日同色） | 缺活动净增量、套装销售结构与利润 | 有具体行为线索；不推定盈利优势 |
| 达人分销与交易便利 | 佣金标识、视频挂商品、包邮/退货入口 | 竞品也有；广告、直播、货架占比未知 | 明确存在的放大条件，效率待证 |
| 口碑及成交积累 | 46K级评价；有因评论购买的个案 | 历史结果也会反过来影响新客；非随机曝光 | 信任增强有线索，不能用销量解释销量 |
| 多规格与再次购买 | 颜色选择、换色、为家人添置；多规格合于一链接 | 竞品也有多色；一次多件≠持续复购 | 次级增量机制，不是独占壁垒 |
| 先发、品牌或技术 | 品牌竹床单至少2023年已有媒体销售记录 | 本链接上市日、同期竞品、品牌支付意愿和实测缺失 | 暂不能列为已证明主因 |

新增解释改变原先过度集中于“承诺兑现”的结论：要同时解释需求被激活、交易被促成、单位订单件数和后续加购。没有净销量、毛利、退货和获客数据，销量成功不等于盈利成功。''',[3,54,55,notes,27,49,56,57,58,59,60,target,hist]+shots,kind='分析',status='研究草稿',pid='sheets')
 chain=record(c,2,TOPIC,'综合判断：可负担的升级感，经过内容和交易设计形成成交','''在现有公开证据下，解释力较强的组合是：消费者已有床单的热、触感或适配不满被具体化；竹材料与软凉承诺提供升级想象；价格/折扣使试购显得可接受；达人内容和评价提供接触与信任；体验满意后出现换色、家庭扩展和再购。它并不需要在每个维度都是最优，才能在特定消费者的预算与旧产品参照下显得值得换。

| 成交环节 | 这款产品可能起作用的机制 | 证据边界 |
| --- | --- | --- |
| 让人想换 | 把已有床单的不满转成软、凉、贴合的升级期待 | 有明确动机与视频结构；不是独占需求 |
| 让人敢试 | 可接受的到手支出、促销时机、评价及平台服务 | 价格和评论有个案；未证明最低价或转化率领先 |
| 让订单变多 | 套装、配色、赠礼与家庭多床使用 | 存在多件行为；不可等同独立买家增长 |
| 让人再买 | 触感和适配满足后，换色或给家人添置 | 有已发生复购和相反案例；未测复购率 |

最关键的竞争判断：相对消费者旧床单的升级，可以成立于部分人；相对同渠道同类产品的独占优势，尚未证明。当前价格截面中它比LDC更贵、比CGK纯竹源路线更低，适合解释为一个有材料升级想象的中间选择；不能把这个价差直接归为品牌溢价。

优先排查的替代解释是更强/更早的分销与投放：即便商品和价格没有独占优势，大规模或更长时间的曝光也可能造成巨大累计差距。当前数据不足以区分有机传播、付费投放、佣金推动和上架时长贡献。初始突破、当前累计规模和未来增长不能混成一个原因。''',[3,54,55,notes,27,49,56,57,58,59,60]+shots,kind='分析',status='研究草稿',pid='sheets')
 gap=record(c,2,TOPIC,'因果归因还缺什么：会改变判断的证据','''最有区分力的补证顺序：
1. 目标与LDC/CGK各自的上架时间、同期逐日销量/GMV、到手价格、活动及断货记录。判断累计差距是时间积累、曝光规模还是转化能力，不能用商品ID或现有评论最早日期推上市日。
2. 视频/达人/直播/货架的订单和GMV，广告花费、佣金、优惠补贴来源。辨别内容说服力、分销覆盖和付费流量；若付费/补贴占主导，需要修正“可复制低成本获客”的想象。
3. 同规格成交与转化对照：控制流量和日期后比较促销价、概念表达与实际升级证据。没有这些条件，不报“价格贡献X%”。
4. 退货后净收入、毛利、履约/佣金成本；同一顾客首次、多件、再购结构。复购自述不可代替财务贡献。
5. 跨颜色/洗涤后/不同床垫高度的实物对照，与已买同类产品者的盲测。将个人价值感与性能差异分开。

2026-11-05查到FindNiche页面标题写11月1日，但未给七天确切区间或商品ID；其检索摘要日期与页面日期不同而数值相同。该第三方数据不并入当前销量速度与排名。Growi另一纯竹源床单的11%佣金不能套到本目标链接。额外付费权限未购买，以上缺口保留。''',[excluded,3,54,55,notes],kind='缺口',status='资料待补',pid='sheets')
 # Retire the old placeholder without removing history or raw data.
 c.execute('UPDATE records SET body=?,status=?,evidence=?,updated_at=? WHERE id=14',('本问题已完成本轮多维度研究：价格、概念/需求、内容、体验、促销、渠道、口碑、规格、复购与先发逐项检验。综合机制为阶段性解释；因果贡献和盈利质量仍待数据。','研究草稿',json.dumps([3,notes,54,55]),server.now()))
 d=json.loads(c.execute("SELECT document FROM brand_reports WHERE brand_id='shilucheng'").fetchone()[0]);s=d['sections'][1];t=next(t for t in s['topics'] if t['topic']==TOPIC and t['product_id']=='sheets')
 edit(t,'更有解释力的是一套成交组合：用可负担的价格提供升级期待，借内容与促销推动试购，再由部分人的舒适体验带来加购。',[
 '不是最低价：本次白色Queen报价，Shilucheng $42.37，LDC混纺$30.99；CGK纯竹源套装$64.49。价格优势取决于消费者拿谁作比较。',
 '概念抓住的是“换掉不舒服的旧床单”：凉感、软滑和贴合均有买家动机或使用证据；同类竞争者也在提供这些价值。',
 '促销与配色影响的不只是转化，还可能增加件数：已有等促销下单、为赠品买三套、因颜色买多套的明确自述。',
 '满意的底线因人而异：部分用户不觉得明显凉，仍因舒适和价格认可；另一些人把凉感或纯材料视为不能妥协的条件。',
 '累计规模还可能受分销、投放和经营时长放大。没有同期曝光、成交和成本，不能把“卖得多”直接归功于产品更好。'
 ],refs=[14,54,price,direct,hypothesis,chain,gap],kind='分析判断',gap='本轮完成多假设检验与47条证据摘记；尚缺同期销量/流量/价格、投放佣金、退货净利润与实物对照，不能量化各因素贡献。',impact='先解释成交机制，再判断该学产品、内容、商品组合还是渠道；不据累计销量直接立项。')
 t['featured']=[{'record_id':price,'mode':'table'},{'record_id':hypothesis,'mode':'analysis'}]
 s['headline']='畅销更像一套成交组合：升级期待、可接受的支出，以及内容与商品运营'
 s['summary']='低价、凉感或柔软都只能解释一部分。竞争报价与购买过程证据指向同一件事：这款床单让部分消费者觉得“值得换、值得试”，并通过促销、配色和再次购买增加件数。要继续分清产品价值、分销放大与盈利质量。'
 s['boundary']='以上为公开证据支持的阶段性归因。210条检索候选和47条摘记不是代表性比例样本；当前价格不能替代历史到手价，累计成交不能替代同期净销售。'
 save(c,d,2)
 # Dependent findings are revised in order, after the product investigation.
 r3=record(c,3,server.TOPICS[3][2],'内容在成交中的位置：促成试购，而非独自解释销售规模','视频结构与#1409/#1618等评论说明内容和评价参与选择过程。目标不只是传达更凉，而是让人把旧床单的不满与一个可接受价格的替代方案连接。应同时研究点击、订单、折扣和退货；达人佣金标识只能证明存在分销激励，不证明佣金高于对手或获客更便宜。',[3,notes,27,49,56,57,58,59,60],kind='分析',status='研究草稿')
 d['sections'][2]['topics'][2]['record_ids'].append(r3)
 d['sections'][2]['topics'][2]['finding']='值得学习的是替换理由与交易理由相互衔接；传播热度需要用成交结果检验。'
 d['sections'][2]['topics'][2]['bullets']=['旧床品不满→可见的替换体验→价格或行动理由；软、凉、配色可以分别服务不同人。','不能由高点赞推断销售主因，也不能照搬未经验证的材料或健康宣称。']
 save(c,d,3)
 r4=record(c,4,server.TOPICS[4][0],'2023年已有品牌竹床单销售表达，不能证明目标链接先发','PennLive于2023-10-11刊发的促销购物文章列出Shilucheng竹床单，文章带联盟佣金披露。只能证明该品牌该类产品当时已有公开销售记录；没有匹配本次TikTok商品ID，也缺主要竞争者同期进入时间。不把品牌历史等同于本链接先发优势。',[hist],kind='事实',status='已核实页面信息')
 d['sections'][3]['topics'][0]['record_ids'].append(r4)
 d['sections'][3]['topics'][0]['bullets'].append('2023年已有第三方竹床单促销报道；尚未对应本次TikTok链接上市时间，不能证明先发。')
 save(c,d,4)
 r5=record(c,5,server.TOPICS[5][1],'能力判断更新：整合成交要素，仍需证明效率与盈利','此次单品研究显示，需求表达、促销、规格/配色、达人触达、口碑与实际体验可以共同形成成交。品牌层面更值得追问的是能否在多产品复制这种组织能力，而不是从爆款倒推材料技术壁垒。已有商品和内容组合是长处线索；低获客成本、高周转、低退货和持续盈利尚未证实。',[3,15,notes,27,49,54,55],kind='分析',status='研究草稿')
 ss=d['sections'][4];ss['headline']='先研究商品与分销的组织能力，不能从一个爆款倒推品牌或技术壁垒'
 ss['summary']='这款床单的强处更可能来自多项成交要素的协同：材料与舒适表达、价格和促销、规格配色、达人内容及顾客体验。能否低成本复制到其他单品、是否保有利润，才决定它是一次畅销还是可持续的品牌能力。'
 ss['topics'][1]['record_ids'].append(r5);ss['topics'][1]['finding']='可见长处是将商品、内容和交易条件组合起来；组织效率与壁垒仍待验证。'
 ss['topics'][1]['bullets']=['供给、表达与销售入口齐备；本次评论补出了促销和多件、换色与家庭扩展的线索。','跨单品复制能力、达人效率、获客成本及退货后的利润，决定这套组合能否持续。']
 save(c,d,5)
 r6=record(c,6,server.TOPICS[6][0],'产品启示更新：区分升级期待与不可妥协条件','不再将更强凉感当作唯一开发答案。消费者中既有为热感找方案者，也有因软滑、贴合与价格满意者；应分别检验真实任务。对凉感不可妥协者，验证持续热湿体验；对舒适升级者，验证触感、洗后稳定和适配。分体King、触觉偏好或少沾宠物毛只是评论线索，尚无足够规模、竞争和支付依据作为独立机会。',[notes,3,54,55],kind='分析',status='研究草稿')
 r7=record(c,6,server.TOPICS[6][3],'机会判断更新：先检验价值组合，再决定性能突破或商品扩展','两条待验证路径：一是用既有产品和明确价格，给消费者一个比旧床单更值得换的具体理由，降低开发风险；二是验证配色、家庭多床、赠礼和加枕套等商品组合能否提升净贡献。第二条有多件/再购个案，但不得重复计入新客，且须扣除折扣、赠品、退货与履约成本。持续凉感与体验一致性仍是可研究的改进方向，不能因为存在投诉就假定市场大、消费者愿付溢价或我方能实现。竞争报价说明最低价与100%竹源均已有供给，Breescape需要验证的是价值组合在目标价格下是否胜出。',[notes,3,54,55]+shots,kind='分析',status='研究草稿')
 r8=record(c,6,server.TOPICS[6][4],'战略优先级更新：先辨明增长来自哪里，再选择投入','优先把商品价值与获客方式拆开验证：产品在同价对照中是否更好，内容能否让这种好被理解，促销与组合是否仍有净利润。若规模主要来自补贴或高投放，复制卖点不能复制增长；若已有产品能提供升级感，可以先检验表达与商品组合。实测、同周期转化和单位订单经济性未补齐前，不给新品立项、收入或溢价承诺。',[notes,3,54,55,27],kind='分析',status='研究草稿')
 ss=d['sections'][5];ss['headline']='机会从“只改产品”扩展到价值表达、商品组合与真实体验的配合'
 ss['summary']='先判断消费者为什么觉得值得换，再决定改产品还是改表达与交易方案。可先验证已有产品的升级理由，以及配色、家庭多床和套装的净增量；对持续凉感和一致性的改进，仍需市场、竞争、成本与支付意愿支持。'
 ss['topics'][0]['record_ids'].append(r6);ss['topics'][0]['finding']='按购买任务选择改进方向：怕热、触感、适配，不能预设人人都追求最强凉感。';ss['topics'][0]['bullets']=['把可兑现的改善和目标价格一起检验；分体King等小需求先验证规模与竞争。']
 ss['topics'][3]['record_ids'].append(r7);ss['topics'][3]['finding']='两条机会待验证：既有产品的升级表达，以及家庭多床、配色和套装带来的净增量。';ss['topics'][3]['bullets']=['新增材料或性能不是唯一增长路径；也要看内容、到手价和组合是否让现有供给更容易成交。','多件与再购不等于新客；需扣除优惠、退货、佣金和履约后看利润。市场规模、溢价及我方能力仍待验证。']
 ss['topics'][4]['record_ids'].append(r8);ss['topics'][4]['finding']='先分清产品价值、流量来源与交易经济性，再决定开发、营销或渠道投入。'
 save(c,d,6)
 d['summary']='Shilucheng目标床单的畅销，更适合解释为一套成交组合：材料与软凉概念激活升级期待，价格和促销帮助试购，达人与评价增加触达和信任，部分体验再带来换色、家庭扩展与复购。它在已查竞品中并非最低价，技术独占、先发与品牌溢价也未获证明。研究重点转向这套组合如何产生净增长，以及Breescape能在哪个环节做得更好。'
 d['summary_record_ids']=list(dict.fromkeys(d['summary_record_ids']+[chain,hypothesis,price,r5,r7]))
 d['reviewed_revisions']={str(i):reports.section_revision(c,'shilucheng',i) for i in range(1,7)}
 for ss in d['sections']:ss['reviewed_revision']=reports.section_revision(c,'shilucheng',ss['number'])
 c.execute('UPDATE brand_reports SET document=?,updated_at=? WHERE brand_id=?',(json.dumps(d,ensure_ascii=False),server.now(),'shilucheng'))
 print(json.dumps({'notes':notes,'candidates':cand,'price':price,'direct':direct,'matrix':hypothesis,'synthesis':chain,'gap':gap,'dependent':[r3,r4,r5,r6,r7,r8]},ensure_ascii=False))
