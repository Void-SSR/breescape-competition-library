import json
from pathlib import Path
W=Path(__file__).parent;before=json.loads((W/'before.json').read_text());doc=json.loads(next(r['document'] for r in before['brand_reports'] if r['brand_id']=='shilucheng'));feedback=json.loads((W/'feedback.json').read_text())
materials={m['id']:m for m in before['materials']};url=lambda i:materials[i]['url'];link=lambda name,i:f'[{name}]({url(i)})'
def q(id,title,answer='',**kw):return dict(id=id,title=title,answer=answer,**kw)
def pt(title,detail='',evidence=''):return dict(title=title,detail=detail,evidence=evidence)
def table(rid,mode='table',purpose='core',**kw):return dict(record_id=rid,mode=mode,purpose=purpose,**kw)
def topic(s,i,questions,lead=''):
 t=doc['sections'][s-1]['topics'][i];t['questions']=questions;t['finding']=lead;t['bullets']=[];t['featured']=[];t['figures']=[];return t

doc['summary']='Shilucheng以“价格负担得起、睡着舒服”介绍床品，已进入多个线上渠道。重点床单获得了明确的柔软认可，也有使用后再次购买的案例。对Breescape最值得研究的是：凉感怎样吸引下单，真实体验怎样支撑继续购买，以及哪些体验落差能形成有价值的换购需求。'
# 1. Brand overview, not product mechanism.
doc['sections'][0].update(headline='多品类、多渠道经营；竹混纺床单在已观察的四款商品中累计销量最高',summary='官网覆盖床单、褥垫、毯和枕头等产品，已有独立站、Amazon、TikTok及Walmart入口。品牌总收入与各渠道占比仍未取得。')
topic(1,0,[
 q('brand-position','品牌希望消费者记住什么？','价格负担得起，床品睡着舒服。官网围绕材料和舒适睡眠表达价值，面向希望改善床品、又在意价格的家庭。',record_ids=[50,1,3],evidence='这是品牌的对外主张；实际消费者构成与品牌认知尚未完成验证。'),
 q('brand-history','品牌什么时候成立，发展背景是什么？','品牌成立年份尚未查实。Amazon卖家自述公司成立于2003年；美国商标于2016年申请、2017年注册。两者都不能直接替代品牌创立年份。',record_ids=[2,28,44],evidence='商标现登记在苏州SHUOTANG公司名下；网站与平台出现的经营主体名称尚未全部对齐。'),
 q('brand-business','主营业务和产品范围是什么？','以家纺床品为主，公开目录还包括窗帘、地毯和浴室垫。不同材料与规格共同组成产品线。',record_ids=[1,34]),
 q('brand-distinction','品牌有什么差异化？','“舒适、价格可负担”是清楚的品牌主张；目前尚无充分证据证明消费者认为它独有，或愿意因此优先选择Shilucheng。',record_ids=[3,50])])
topic(1,1,[
 q('sales-channels','品牌通过哪些渠道销售？','已确认四类线上销售入口。各入口的销售额不能用粉丝数、评论数或累计售出数相互替代。',record_ids=[29,35],tables=[table(29)]),
 q('sales-scale','品牌销售规模、增长及渠道占比是多少？','尚未取得可核验的品牌总销售额、增长序列和同期间分渠道销售额。',record_ids=[4,30,49],evidence='公开第三方线索缺少店铺身份或统计口径核对，保留为查证线索，未用来估算品牌规模。'),
 q('sales-main','哪个渠道是销售主力，哪个增长最快？','目前无法排序。TikTok有可见的累计成交积累，但缺少其他渠道的同期数据。',record_ids=[4,35])])
# add missing evidence record49 to topic references; topics must be complete and traceable.
if 49 not in doc['sections'][0]['topics'][1]['record_ids']:doc['sections'][0]['topics'][1]['record_ids'].append(49)
topic(1,2,[
 q('product-matrix','产品覆盖哪些品类和价格带？','公开目录覆盖多类家纺；床单套装展示价约30—170美元，不同材质、尺寸和件数共同形成这个范围。',record_ids=[5,31,32],tables=[table(31)],figures=[{'material_id':47,'source_id':6,'caption':'官网产品陈列：床单、褥垫与毯共同出现。'}],note='目录及价格采集于2026年11月4日；按网站品牌标签整理，部分链接归属尚待核实。'),
 q('product-contribution','哪些产品卖得多，贡献了多少销售？','同一TikTok店铺已观察的四款商品中，本款床单累计售出约43.55万件，明显高于另三款。品牌销售贡献占比仍未知。',record_ids=[33,6],tables=[table(33)],note='这是2026年11月4日的四款商品累计展示，不是全店完整排行，也不是同期间销售额。'),
 q('product-dependence','依赖单一爆款，还是多品类发展？','可以确认多品类有售；尚不能判断收入是否依赖单一爆款。需要完整的同期间产品销售额。',record_ids=[5,6])])
# 2. Specific product, then feedback, then causal analysis.
doc['sections'][1].update(headline='柔软获得广泛的样本内认可；凉感和价格影响部分顾客下单',summary='消费者“为什么买”和“买后为什么继续用或再买”需要分开理解。现有证据支持具体购买理由与体验价值，尚未完成对总销量的因果分解。')
topic(2,0,[
 q('product-identity','研究的是哪款产品，价格和销量如何？',link('Shilucheng竹混纺凉感床单套装',3)+'，在TikTok美国站销售。2026年11月4日页面累计售出约43.55万件，评分4.4；当晚插件记录评价46,170条。销售额和期间销量未取得。',record_ids=[7,36,38],tables=[table(36)],figures=[{'material_id':48,'source_id':3,'caption':'商品首页：深灰色单人床三件套（Twin）；顶部为达人精灵数据区。'}],note='销量、评分及评价数汇总同一商品链接下的多个规格；截图与价格保留实际观察日期。'),
 q('product-concept','它给消费者的核心购买理由是什么？','柔软、凉爽、睡得舒服，同时价格可接受。商家用竹源材料和酒店感解释体验价值，并强调床笠包覆和洗护便利。',record_ids=[8,9,39],evidence='商家标注60%竹源人造丝＋40%聚酯；宣传中的性能尚不等于实测效果。'),
 q('product-comparison','同类产品之间，价格、设计和体验有什么差别？','本款四件套报价高于LDC同规格；另有多两个枕套的六件套选项。CGK采用100%竹源人造丝；三款都宣传柔软、凉感和较深床笠。',record_ids=[10,37,51],tables=[table(51,layout='comparison')],note='比较表用于看清差别；“更凉、更耐用、值得多付钱”仍需同条件使用证据。')])
t=topic(2,1,[
 q('feedback-overall','消费者整体表达了怎样的评价？','柔软是最常被具体称赞的体验；不满主要集中在触感、温度和适配。',type='feedback-summary',record_ids=[12]),
 q('feedback-positive','消费者认可什么？','柔软是本款最清楚的已获认可价值；凉感、贴合和配色也获得反馈。Breescape研究凉感升级时，应同时守住顾客在意的触感。',type='feedback-positive',record_ids=[12],evidence='柔软获得397条明确认可；R580因手感再次下单。这里说明体验价值，尚未证明优于其他品牌。'),
 q('feedback-negative','消费者不认可什么？','粗糙、不够凉和适配不满，是本样本中最常见的具体问题。它们提示产品体验和宣传承诺需要一起核查，单纯提高竹源材料比例并不能保证解决。',type='feedback-negative',record_ids=[12,13],evidence='适配不满38条与滑脱35条接近，优先级不宜只由这3条差距决定；还需考虑严重程度及是否导致退货。'),
 q('feedback-needs','真实购买理由与未满足需求是什么？',record_ids=[13,52],points=[
  pt('为凉感而买，实际还要接受手感。','怕热是明确的购买触发，但收到后能否接受触感，会影响继续使用。','R452、R917明确为凉感买；R619无法接受粗糙；R718虽未感到预期凉感，仍因舒适继续用。'),
  pt('价格与促销影响下单时机。','有的顾客原本想试，遇到合适价格才购买；这不同于产品长期比对手便宜。','R475因价格合适下单；R1389等待促销后购买。'),
  pt('材料、套装和宣传需要与顾客理解一致。','值得关注的是“买到的是否正是想买的”，包括混纺／纯竹源理解，以及套装内容。','R453若早知含聚酯便不买；R535原想买纯竹版本而退货。')])])
t['feedback']=feedback
# Central requested three questions. Prior tables now serve the specific conclusion or stay in evidence.
topic(2,2,[
 q('success-buy','消费者为什么购买它？','已找到两类明确触发：想改善怕热睡感，以及价格／促销合适。视频和评论也参与了部分顾客的期待形成。',record_ids=[14,54,66],evidence='R452、R917为凉感买；R475看到合适价格后下单。R1409谈视频带来的软凉期待，R1618提及评论影响选择。'),
 q('success-advantage','相比同类产品，真正领先在哪里？','目前能确认较高累计成交与部分顾客的体验认可；尚未证明它在价格、技术或成品性能上领先同类。',record_ids=[65,67,68],points=[
  pt('本组对照中，本款不是最低报价。','白色双人床四件套为$42.37，高于LDC的$30.99；两款价格观察日相同。'),
  pt('柔软、凉感和深床笠已有竞品供给。','本款的认可是真实研究证据，但“有人认可”尚不能证明“比对手更好”。'),
  pt('六件套提供了另一种购买组合。','同尺寸深灰色六件套比四件套多两个枕套、贵$3；这是商品设计差别，未证实为独家或主要销量来源。')],links=[{'target':'product-comparison','label':'查看三款产品的完整对照'}],tables=[table(65,purpose='support',caption='核对同日、同尺寸的价格与销量展示')]),
 q('success-drivers','销量背后的主要驱动因素是什么？','当前最值得重视的，是以下三项相互衔接的作用。',record_ids=[67,68,69],ordered=True,points=[
  pt('柔软体验支持继续使用和再次购买。','这是目前最扎实的产品价值证据：不仅有人称赞，还有人明确因手感再次下单。','397条近期评论肯定柔软；R580因触感两次下单，R499试用后追加五套。'),
  pt('凉感购买理由与合适价格共同推动尝试。','凉感回应了部分买家的具体需要；价格和促销让已经感兴趣的人决定下单。','R452、R917为凉感购买；R475因价格合适下单。当前报价高于LDC，不能解释为长期最低价。'),
  pt('达人把“换掉不舒服的旧床单”拍成具体场景。','这类表达给出明确换购理由，再连接产品展示和优惠，是已有内容中值得研究的促购方式。','已确认的五条素材中，Ben三条采用相近结构，均有佣金标识；尚无作品级订单归因。')],note='排序表示本轮研究对解释力与商业重要性的判断，不是各因素的销量贡献排名。推广投入、上架时长、促销净收益等尚未分解；先发、独有技术和品牌溢价暂无充分依据。',links=[{'target':'channel-top5','label':'查看五条视频及表达方式'}],tables=[table(67,'analysis','support',caption='展开：十种销量解释的证据与反证')])])
# 3. Channel execution; preserve approved video identity and playable files.
doc['sections'][2].update(headline='高点赞素材把旧床单的不满转成换购理由',summary='五条已选视频中，三条先批评旧床单、再展示替换和优惠；两条直接展示铺床与配色。可借鉴表达结构，实际销售效果尚无订单数据验证。')
topic(3,0,[
 q('channel-accounts','有哪些渠道账号，规模与更新频率如何？',link('TikTok @shiluchenghome',20)+'主页于11月4日展示3.32万粉丝、12.17万获赞；'+link('Shilucheng Home店铺',4)+'展示累计售出68.76万件。其他官网关联账号见下表。',record_ids=[15,41,46],tables=[table(46)],figures=[{'material_id':24,'source_id':4,'caption':'TikTok店铺公开页面：全店累计售出与单款床单销量分别记录。'}],note='已找到的入口不等于完整账号矩阵；内容发布频率尚未统计。店铺1,093个视频的口径不明，不当作自营发帖数。'),
 q('channel-sales-mix','达人、自营、直播与短视频如何分工？','已确认存在达人佣金推广；各方式的销售占比尚未取得。自营账号与店铺的后台管理关系也未核实。',record_ids=[16,42])])
topic(3,1,[
 q('channel-top5','这五条高点赞视频分别讲什么？','三条通过批评旧床单引出换购，两条直接展示柔软、铺床和配色。点击视频名称可播放已保存素材。',record_ids=[17,43,55],tables=[table(55)],figures=[{'material_id':61,'source_id':3,'caption':'V03关键帧：旧床单不适 → 展示包装与新产品 → 优惠引导。'}],note='采用已确认的商品页关联视频前五条；点赞为2026年11月4日展示，不能称作全品牌或全平台完整TOP5。'),
 q('channel-attraction','这些内容为什么可能吸引消费者？','把“为什么要换”讲得具体：先呈现旧床单的不适，再用铺床、触摸和颜色展示替换后的想象，优惠提供即时行动理由。',record_ids=[55],evidence='这是对内容说服方式的研究判断；Ben三条来自同一作者、结构相近，不能当作三种独立验证成功的策略。'),
 q('channel-conversion','是否形成实际销售转化？','尚未取得视频对应的播放量、点击、订单与销售额。高点赞只能证明互动，不能单独说明带货效率。',record_ids=[17,55,76],note='发布时间、评论／分享量和独立原帖链接仍缺；五条原文件及画面证据已保留。音轨已自动转写，尚未人工听辨。')])
topic(3,2,[
 q('channel-message','品牌正在通过内容建立什么认知？','更柔软、凉爽、像酒店床品的睡眠体验，是已见内容的主要表达。部分达人使用“全天然竹床单”，与商品的60/40混纺说明不一致。',record_ids=[18,56,70],evidence='这说明内容希望建立的认知；尚未证明多数消费者已经形成同样印象。'),
 q('channel-borrow','哪些内容形式值得借鉴？','针对一种具体不满，展示换购后的真实改善；再把材料、适配规格和优惠讲清楚。',record_ids=[18,56,70],evidence='可借鉴展示方式；皮肤改善、抗菌及纯材料等未经证实的说法不宜照搬。R1409也显示宣传期待可能在收货后落空。')])
# 4. Historical facts remain discrete and linked.
doc['sections'][3].update(headline='已有商标与推广记录，增长拐点仍未确定',summary='公开记录能说明品牌在不同时点做过什么；缺少动作前后的销售和投入数据，尚无法判定哪次动作推动了快速增长。')
topic(4,0,[
 q('history-events','从成立到现在，哪些发展节点可以核实？','已核实商标申请、注册与转让，以及若干官网材料文章和床单推广。产品首发、重要渠道进入及战略调整时间仍不完整。',record_ids=[19,45,47,71],tables=[table(19)],evidence=link('2023年黑五推广原帖',44)+'与'+link('2025年竹凉感床单文章',34)+'可查；文章日期不自动等于产品上市日。')])
topic(4,1,[
 q('history-growth','哪些动作推动了快速增长？','尚未找到能把某项动作与增长变化可靠对应的证据。材料内容、促销和达人推广均已出现，但不能据此排出增长贡献。',record_ids=[20,57]),
 q('history-change','早期到现在，增长方式发生了什么变化？','现有材料显示不同时期都有产品价值和促销表达；尚不足以判定从哪种增长方式转向哪种方式。',record_ids=[20,57],evidence='仍需同期渠道收入、流量、推广费用与动作时间线。零散公开记录不能还原完整经营演变。')])
# 5. Whole-brand mechanism, not repeating single-product testimonials.
doc['sections'][4].update(headline='已看到产品认可；品牌溢价与长期壁垒尚未证明',summary='多品类、多渠道和达人合作已经存在。是否形成难以复制的能力，需要进一步看跨产品成功、品质稳定、获客费用和持续盈利。')
topic(5,0,[
 q('brand-choice','消费者选择的是品牌，还是具体产品？','现有直接证据主要指向具体床单的手感和使用价值。跨产品的品牌偏好仍缺充分证明。',record_ids=[21,58],evidence='R580、R499明确再次购买；这些评论没有证明顾客因品牌名而购买其他品类。'),
 q('brand-premium','独特价值是否形成品牌心智，能否支撑更高价格？','尚不能确认。“舒适、可负担”是品牌表达；较高页面报价也不能独立证明消费者愿意为品牌多付钱。',record_ids=[21,58])])
topic(5,1,[
 q('brand-capabilities','品牌成功背后依靠哪些能力？','已观察到产品组合、多个销售入口和达人推广的运作。它们是已存在的经营活动；具体研发、供应链和组织效率尚未核实。',record_ids=[22,59,72]),
 q('brand-moat','哪些优势难以复制，能否支撑持续增长？','目前未确认独有技术、成本或品牌壁垒。能否持续增长，还取决于体验能否稳定、获客是否经济，以及成功能否延伸到更多产品。',record_ids=[22,59,72],evidence='官网Lab页面目前提供制造自述，未取得可核验的设备、产能、专利或检测报告；缺少证明不等于这些能力不存在。')])
# 6. Concise implications, avoid forcing every observation into a new opportunity.
doc['sections'][5].update(headline='值得验证的是：什么实际改善，能让已有凉感床单的顾客愿意换购',summary='竞品已有柔软认可，也存在凉感、触感与预期落差。Breescape的机会需要落到具体改善和付费选择；产品组合、价值展示和小批量测试已在客户资料中提出，不再当作新增发现。')
topic(6,0,[q('implication-product','哪些产品创新值得借鉴或进一步研究？','保留柔软触感，同时分别验证凉感、洗后稳定和贴合。多两个枕套的组合也是已有商品设计线索，但其新增需求和利润尚未证明。',record_ids=[60,73])])
topic(6,1,[q('implication-content','哪些营销及渠道动作值得学习？','用明确的使用不满引出换购，再展示真实改善。此次新增价值是具体的视频结构、顾客原文及落差反例；“把触感拍出来”本身已是客户方向。',record_ids=[61])])
topic(6,2,[q('implication-gaps','竞争对手有哪些不足，我方有机会做得更好吗？','达人材料表述与商品成分不一致，容易造成误解；部分评论还报告粗糙、不够凉和不同购买之间的体验差别。是否能转为我方优势，须验证我方确实改善了这些问题。',record_ids=[62])])
topic(6,3,[q('implication-opportunity','哪些潜在机会值得优先验证？','优先研究已买同类凉感床单、关键体验仍不满意且愿为改善换购的人。它与已有供给直接竞争，需要同时成立的条件见下。',record_ids=[63,74],ordered=True,points=[
 pt('需求反复存在，且规模值得做。','不能由少数投诉直接推算市场大小；需要确认人群数量、场景和问题严重程度。'),
 pt('Breescape确实提供了可感知的改善。','已有凉感与检测展示是比较起点，仍要与具体竞品在同条件下验证。'),
 pt('顾客愿意付费，经营上能够盈利。','换购意愿、可接受价格，以及推广和退货后的利润，目前尚未取得。')],note='这是待验证的商业机会，不是已确定的收入来源。家庭多床与追加购买保留为次级线索。')])
topic(6,4,[q('implication-decision','这些发现如何指导Breescape的增长决策？','产品规划围绕具体体验改善；产品开发验证实际差别；品牌和内容讲清值得换购的理由；渠道用订单及退货后的收益判断效果。',record_ids=[64,75],note='客户已提出组合、价值展示和小批量测试；本次补充的是具体竞争证据、顾客选择差别，以及需要成立的商业条件。')])
# Build an auditable coverage list from the questions, without adding implementation language to the report.
coverage=[]
for s in doc['sections']:
 for t in s['topics']:
  for item in t.get('questions',[]):
   assert set(item.get('record_ids',[]))<=set(t['record_ids']),(item['id'],item.get('record_ids'),t['record_ids'])
   coverage.append({'section':s['number'],'topic':t['topic'],'question':item['title'],'question_id':item['id'],'record_ids':item.get('record_ids',[]),'has_answer':bool(item['answer'] or item.get('points') or item.get('type'))})
assert len({r['question_id'] for r in coverage})==len(coverage)
(W/'report_candidate.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2));(W/'framework_coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2));print('questions',len(coverage),'all grounded',all(r['record_ids'] and r['has_answer'] for r in coverage))
