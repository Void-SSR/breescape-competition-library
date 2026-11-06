from pathlib import Path
import json,sqlite3,datetime,csv
R=Path('research/行业全景与心智地图_20261105'); O=Path('协作/行业全景升级_20261105')
old=json.loads(Path('协作/行业基础库_实施包_20261105/01_核定展示内容.json').read_text())
sources=old['sources'].copy()
def src(key,title,url,kind='品牌官方页面',supports='',boundary='',published=''):
 sources.append(dict(key=key,title=title,url=url,source_type=kind,publisher=title.split('｜')[0],published_at=published,retrieved_at='2026-11-05',supports=supports,boundary=boundary))
src('ries-original','Al Ries｜1972年定位原文','https://www.alries.com/positioning-articles','定位方法原文','消费者按品类建立选择阶梯；销量不等于心智占有。','方法来源，不提供本行业品牌心智排名。','1972')
src('ries-2026','Laura Ries｜定位的定义','https://www.ries.news/p/what-is-positioning','定位方法原文','定位关注品牌在潜在顾客心中形成的概念与关联。','不是本行业消费者调研。','2026-06-03')
src('cotton-survey','Cotton Incorporated｜美国床品消费调查','https://lifestylemonitor.cottoninc.com/wp-content/uploads/2025/03/Bedding-US_download.pdf','调查发布机构','美国床品购买关注点、棉材料偏好。','棉行业机构发布；调查对象是一般床品消费者，非凉感床品专属人群。五国总样本7,163；美国样本数未单列。','2025-03')
src('cozyearth','Cozy Earth｜竹源粘胶床单','https://cozyearth.com/products/bamboo-sheet-set','品牌官方页面','具体产品、材料、商家主张、套装内容。','销量未披露；商家宣传不等于消费者心智。')
src('sijo','SIJO｜AiryWeight莱赛尔床单','https://sijohome.com/products/eucalyptus-sheets','品牌官方页面','材料、套装、护理、宣传及页面评论数。','不同件数的价格不可直接横比；宣传功效未独立实测。')
src('rest','REST｜Evercool凉感被','https://rest.com/products/evercool-comforter','品牌官方页面','具体商品、尺寸、品牌主张和护理。','官网评论数不是销售数量。')
src('rest-retailer','Mattress Firm｜REST Evercool成分','https://www.mattressfirm.com/evercool-comforter/5637554828.p?variantid=5637555608','零售商商品页','表层90%尼龙、10%氨纶。','同系列零售商品标注；不替代到货标签核验。')
src('rest-target','Target｜REST白色双人凉感被','https://www.target.com/p/-/A-1005009737','零售商商品页','TENCEL与Sorona填充及直接盖用设计。','商家标注；填充比例未公开。')
src('buffy','Buffy｜Breeze莱赛尔凉感被','https://buffy.co/products/breeze-comforter?variant=20247576412258','品牌官方页面','双人尺寸、活动价、莱赛尔表层及填充、护理。','测试宣称与实际报告分开；不作为全渠道销量。')
src('slumber','Slumber Cloud｜Performance TENCEL床单','https://slumbercloud.com/products/performance-sheet-set','品牌官方页面','70%莱赛尔、30%Outlast粘胶，白色Queen四件套页面价188.30美元。','官网展示的30K+评价不能认定为单品销量。')
src('brooklinen','Brooklinen｜Classic棉平纹床单','https://www.brooklinen.com/products/classic-core-sheet-set','品牌官方页面','长绒棉平纹路线、套装与酒店式清爽主张。','规格目录价不包含未核实活动优惠。')
src('bedsure','Bedsure｜竹源人造丝床单','https://bedsurehome.com/products/rayon-derived-from-bamboo-sheet-set','品牌官方页面','竹源人造丝路线与具体商品。','该商品不与其他有机竹源款自动合并。')
src('elegear','Elegear｜黑色Arc-Chill 3.0凉感毯','https://www.elegear.com/products/elegear-black-cooling-blanket-arc-chill-3-0-q-max-0-5-multi-size-options','品牌官方页面','双面设计、黑色各规格与Arc-Chill宣传。','该页未明确凉感面完整配比；不从其他型号搬用80/20比例。')
for k in ['cozyearth','sijo','rest','buffy','brooklinen','bedsure','elegear']:
 d=json.loads((R/(k+'_商品公开数据.json')).read_text())
 base=next(s['url'] for s in sources if s['key']==k).split('?')[0]
 src(k+'-variants',k+'｜官网公开规格报价',base+'.js','官方公开商品数据','规格ID、目录报价或活动报价、在售状态及商品图片。','本地保留读取副本；不是税运费及账号优惠后的结算价。')
src('rest-growth','Shopify｜REST增长案例','https://www.shopify.com/case-studies/rest','平台与商家合作案例','案例披露上线约一年半年销售额超过3,000万美元、客单价提升10%。','品牌整体、历史案例；未披露财年和地区拆分，不能当作2026年美国单品销售额。')
src('rest-channel','REST｜进入Mattress Firm','https://www.prnewswire.com/news-releases/rest-partners-with-mattress-firm-to-bring-award-winning-cooling-bedding-to-more-sleepers-302394684.html','品牌新闻稿','2025年3月6日渠道合作事件。','拓渠动作，不是已证实的销量增幅。','2025-03-06')
src('rest-sleep','SLEEP｜凉感床品使用研究摘要','https://doi.org/10.1093/sleep/zsaf090.1386','学术会议摘要','研究报告主观睡眠体验改善，未观察到客观睡眠改善。','组合干预不是单品、单材料测试；摘要不支持医学疗效或品牌心智占有。','2025-05')
src('outlast','Outlast｜相变调温原理','https://www.outlast.com/en/temperature-regulation/faq','技术供应商','相变材料吸收、储存及释放热量；有不同纺织应用。','供应商说明；成品效果取决于含量、位置、结构与环境。')
src('375','37.5｜床品温湿度管理','https://www.thirtysevenfive.com/home-goods/bedding/','技术供应商','以功能颗粒进行温湿度管理的商用路线。','不把37.5当作固定维持37.5°C的承诺。')
src('pe-paper','Nature Sustainability｜工程化聚乙烯织物','https://www.nature.com/articles/s41893-021-00688-5','原始研究论文','工程化PE纱线/织物的导湿、快干及被动散热研究。','研究样品，不证明任一在售PE凉被有相同性能。','2021-03-15')
src('reddit-rest','消费者讨论｜REST床单与凉感被','https://www.reddit.com/r/Bedding/comments/13ohp1p','公开消费者自述','对触感凉、柔软、接触后变暖等有不同体验。','自选择发帖、身份与购买不可核验，不作频率与市场份额统计。','2023-05-22')
src('indexbox-audit','IndexBox｜美国凉感床单范围估算','https://www.indexbox.io/store/united-states-kw-cooling-bedding-sheet-set-840-market-analysis-forecast-size-trends-and-insights/','第三方估算（未采纳）','用于记录与GMR口径冲突。','15–25亿美元估算未披露可复算数据；不可与GMR平均或拼接。')
src('asinsight-audit','ASINSIGHT｜凉感床单关键词样本','https://www.asinsight.com/market-analysis/US/cooling-bed-sheets','第三方估算（未采纳）','记录关键词Top50含褥垫、全套床品的样本污染。','不作为美国凉感床单总体市场或品牌占比。','2026-07')
src('indexbox-demo','IndexBox｜凉毯演示图表','https://www.indexbox.io/store/united-states-cooling-blanket-marketplace-brand-report/','演示数据（排除）','页面图表明确标注Demo。','不能入事实图表。')
# Local algorithm is a supplied method source, never an instruction override.
sources.append(dict(key='user-algorithm',title='用户提供｜百亿爆品算法（升级中）',source_type='用户方法材料',publisher='用户提供',retrieved_at='2026-11-05',url='',local_path=str((R/'百亿爆品算法_原文.md').resolve()),supports='需求组合→需求金字塔→长处→竞争→定位；逐步校验。',boundary='按本次任务适配；不采用无证据的竞争评分。'))
# Product records; this atlas contains reference products, not automatically full brand research objects.
c=sqlite3.connect('data/library.sqlite3');c.row_factory=sqlite3.Row
baseproducts={x['id']:dict(x) for x in c.execute('select * from products')}
products=[]
def prod(id,name,category,route,url,price,spec,pricekind,material,reason,structure,sales,keys,image='',report='',recognition='暂无可判断品牌心智占有的调查。',notes=''):
 products.append(dict(id=id,name=name,category=category,route=route,url=url,price=price,currency='USD',spec=spec,price_kind=pricekind,observed_at='2026-11-05',material=material,merchant_reason=reason,claim_structure=structure,sales=sales,market_share='未取得同口径市场分母',sales_growth='无可比期间序列',verified_channel=('TikTok美国站' if id=='sheets' else 'Amazon美国站' if id=='cozy-comforter' else '美国官网'),best_channel='缺少跨渠道销售拆分，不能确定',source_keys=keys,image_url=image,report_url=report,recognition=recognition,note=notes))
prod('sheets','Shilucheng 竹混纺凉床单','sheets','竹源人造丝混纺',baseproducts['sheets']['url'] if 'url' in baseproducts['sheets'] else 'https://shop.tiktok.com/us/pdp/1729438233542234865',42.89,'白色双人床（Queen）四件套','公开页面价','60%竹源人造丝＋40%聚酯','柔软、凉感、价格可接受','多个卖点并列','43.57万件｜全球累计、全规格、扣除退货',['material-3','material-132','material-89','material-78'],baseproducts['sheets'].get('image_url',''),'#product-report/sheets','已有评论明确为凉感购买，也有因柔软再次下单的自述；不能推及美国整体心智。','销量取观察25，价格取观察26；不把全球累计量当美国销量。')
prod('sheex-sheets','SHEEX Original Performance性能床单','sheets','性能聚酯弹力面料','https://www.sheex.com/products/original-performance-sheet-set',194.35,'亮白双人床（Queen）四件套','展示活动价','87%聚酯＋13%氨纶','透气排湿、弹力贴合','主推性能面料','销量未公开',['material-114','material-115'],baseproducts['sheex-sheets'].get('image_url',''),'#product-report/sheex-sheets')
prod('cozy-comforter','Cozy Bliss 经典双面凉感被','covers','凉感化纤表层＋填充','https://www.amazon.com/dp/B0BVQMTD8W',69.99,'灰/蓝双人款，约229×229厘米','展示价格','尼龙/氨纶表层；聚酯填充','怕热、夜间出汗人群的双面凉感','主推双面凉感','近月购买提示50+｜门槛提示，非精确月销',['material-100'],baseproducts['cozy-comforter'].get('image_url',''),'#product-report/cozy-comforter')
def item(k,title):
 d=json.loads((R/(k+'_商品公开数据.json')).read_text());v=next(v for v in d['variants'] if v['title']==title);return d,v
for k,title,name,cat,route,mat,why,structure,spec,kind,sales in [
('bedsure','White / Queen','Bedsure 竹源人造丝床单','sheets','纯竹源人造丝','100%竹源人造丝','凉爽丝滑、日常易用','凉感与柔软并列','白色双人床（Queen）四件套','官网规格报价','销量未公开'),
('cozyearth','White / Queen','Cozy Earth 竹源粘胶床单','sheets','纯竹源粘胶','100%竹源粘胶','柔软丝滑的高档睡眠体验','主推柔软奢适，兼讲调温','白色双人床（Queen）四件套','官网目录价，未计活动折扣','销量未公开'),
('sijo','Snow / Queen / With a Flat Sheet','SIJO AiryWeight莱赛尔床单','sheets','纯莱赛尔','100%TENCEL莱赛尔','轻盈、柔软、吸湿凉爽','主推轻盈凉爽','白色双人床（Queen）四件套','官网目录价，未计购物车优惠','销量未公开'),
('brooklinen','Solid White / Queen','Brooklinen Classic棉平纹床单','sheets','长绒棉平纹','100%长绒棉；270支数口径为TC','酒店式清爽触感、透气','主推清爽棉平纹','白色双人床（Queen）四件套','官网目录价，未计活动折扣','销量未公开'),
('rest','Arctic White / Full/Queen','REST Evercool凉感被','covers','凉感尼龙表层＋填充','表层90%尼龙＋10%氨纶；TENCEL与Sorona填充，比例未披露','给怕热者的接触凉感与柔软舒适','凉感核心概念明确','白色双人款，约229×229厘米','官网规格活动价','单品销量未公开'),
('buffy','Full/Queen','Buffy Breeze莱赛尔凉感被','covers','莱赛尔表层＋莱赛尔填充','TENCEL莱赛尔表层及填充','用莱赛尔表层和填充减少厚被闷热感','主推莱赛尔凉被','白色双人款，约229×229厘米','页面活动价','销量未公开'),
('elegear','Queen 79"x 86"','Elegear Arc-Chill 3.0双面凉感毯','blankets','凉感面料＋棉双面','凉感面Arc-Chill；另一面标注埃及棉，凉感面配比未明','一面接触凉、一面棉质舒适','主推Arc-Chill接触凉感','黑色约201×218厘米，商品标称Queen','官网规格报价','销量未公开')]:
 d,v=item(k,title);base=next(s['url'] for s in sources if s['key']==k).split('?')[0]
 price=187.50 if k=='buffy' else v['price']/100
 img=d.get('featured_image','');img='https:'+img if img.startswith('//') else img
 keys=[k,k+'-variants']+(['rest-retailer','rest-target'] if k=='rest' else [])
 prod(k,name,cat,route,base+'?variant='+str(v['id']),price,spec,kind,mat,why,structure,sales,keys,img)
prod('slumber','Slumber Cloud Performance TENCEL调温床单','sheets','莱赛尔＋相变粘胶','https://slumbercloud.com/products/performance-sheet-set',188.30,'白色双人床（Queen）四件套','页面活动价','70%TENCEL莱赛尔＋30%Outlast粘胶','吸收、释放热量，缓冲睡眠温度变化','主推相变调温','单品销量未公开',['slumber','outlast'])
# document payload
D=dict(schema_version=2,package_id='industry-atlas-20261105',reviewed_at='2026-11-05',title='美国凉感床品行业全景',subtitle='市场规模 · 品类与产品 · 材料技术 · 消费者需求与心智',navigation_label='行业基础',sources=sources,products=products,glossary=old['glossary'],sections=[{'id':a,'title':b} for a,b in [('market','市场规模与结构'),('products','细分品类与代表产品'),('growth','增长记录'),('materials','材料与技术'),('needs','需求金字塔'),('mindmap','心智地图')]])
D['market']={
 'title':'市场规模与结构','scope':'美国市场｜主动控温设备单列，不计入床单、被子规模',
 'metrics':[{'label':'美国凉感床单','value':'约5.63亿美元','period':'2025年','kind':'第三方模型估算','source_keys':['gmr-sheets'],'note':'包含凉感床单套装、单件及相关组合；不含凉被、床垫、设备。','detail':'GMR按1.369亿户×3.5%年购买率×105美元×1.12推算。3.5%购买率、客单价和12%附加项为模型假设，尚无独立销量验证；不作为计算品牌份额的可靠分母。'},
 {'label':'美国凉感被／凉感毯','value':'暂无可靠总额','period':'截至2026年11月','kind':'公开证据缺口','source_keys':[],'note':'找到的公开资料未提供可复核的统一规模。'},
 {'label':'床单／凉被／凉毯占比','value':'暂不绘制比例','period':'美国全渠道','kind':'缺少统一分母','source_keys':[],'note':'分类先按产品形态；一款商品采用多种技术时不重复计入。'}],
 'share_chart':{'title':'全球凉感床单材料结构参考','scope':'2025年销售额｜第三方模型，非美国占比','values':[{'label':'莱赛尔相关路线','value':34},{'label':'其余材料路线合计','value':66}],'source_keys':['gmr-sheets'],'note':'来源仅公开最大材料组34%；其余66%为100%减去34%，不再拆分。不能据此判定美国材料排序。'},
 'category_rows':[
 ['床单与床笠','直接铺在身体下方；含配套枕套','Shilucheng、Bedsure、SIJO、SHEEX','sheets'],
 ['有填充凉感被','表层与填充共同影响闷热、重量和触感','Cozy Bliss、REST、Buffy','covers'],
 ['薄凉感毯','轻薄覆盖；有双面凉感/棉质设计','Elegear','blankets'],
 ['相邻替代品','褥垫、床垫保护层及主动控温设备','用于理解替代关系；另建统计口径','adjacent']],
 'scope_detail':'Cooling在各机构与平台上并非统一统计品类。全球、美国、关键词样本、品牌全渠道、单链接累计量不能相互代替。市场规模与份额尚未达到用于投资测算的可靠程度。',
 'excluded':[{'source_key':'indexbox-audit','reason':'美国床单估算15–25亿美元，与GMR差异大且无法复算；不取平均。'},{'source_key':'asinsight-audit','reason':'关键词Top50混入床垫加垫、整套床品；不作为纯凉感床单大盘。'},{'source_key':'indexbox-demo','reason':'图表明确标注演示数据；剔除。'}]}
D['product_view']={'title':'细分品类与代表产品','intro':'按产品形态与材料路线查看。价格对应下列具体规格；不是全市场畅销排名。','filters':[{'id':'all','label':'全部'},{'id':'sheets','label':'床单与床笠'},{'id':'covers','label':'有填充凉感被'},{'id':'blankets','label':'薄凉感毯'}],'columns':['产品与路线','商家主推的购买理由','价格与规格','销售记录','已核实在售渠道'],'detail_columns':['材料与设计','消费者认知证据','销售最强平台','市场份额与增长','来源与采集口径'],'note':'官网目录价与活动价已分别标注。渠道列表示已核实在售，不代表该渠道销量最高；缺少销售拆分的商品不写“主销平台”。'}
D['growth']={'title':'增长记录','intro':'已核实的品牌成长与渠道扩展；单品近期增长榜仍缺同口径销售序列。','cards':[{
 'name':'REST｜从怕热人群切入','metric':'年销售额超过3,000万美元','period':'上线约一年半；历史案例，财年未披露','scope':'品牌整体，非美国Evercool单品销售额','source_keys':['rest-growth'],
 'facts':['平台案例披露客单价提升10%。','2025年3月宣布与Mattress Firm合作。'],
 'traits':'以Evercool系列面向怕热者，官网强调凉感与柔软，并逐步扩大销售触点。',
 'interpretation':'明确人群与产品概念值得继续研究；现有证据不能拆出材料、内容、促销和渠道各自的销量贡献。',
 'event_sources':['rest-channel','rest'],
 'product_ids':['rest']}],
 'pending_title':'近期增长产品','pending_text':'尚无通过核对的同款、同平台、同周期销量序列。暂不把新品、评论增加、搜索热度或累计销量写成快速增长。',
 'required_fields':['产品链接／ID','平台及市场','本期与上期日期','销量或销售额','绝对增量与增速','同期价格与促销','数据来源'],
 'analysis_status':'增长原因只有在时间序列与动作对应后才能判断；季节升温与促销需单独核对。'}
D['materials']={'title':'材料与技术','intro':'先看用在哪里、怎样影响热和湿，再看品牌给它起了什么名字。','mechanisms':[
 {'name':'接触时凉','text':'皮肤接触面料时热量较快传走','metric':'接触凉感测试，如q-max','source_keys':['kaken-qmax']},
 {'name':'减少闷热','text':'让热量与水汽更容易离开床品','metric':'透气、热阻、湿阻与整床使用','source_keys':['tencel-fibers','pe-paper']},
 {'name':'缓冲温差','text':'温暖时吸热、降温时释放储存热量','metric':'相变温区、储热量、循环表现','source_keys':['outlast']}],
 'rows':[
 {'name':'竹源人造丝／粘胶','kind':'商用纤维','use':'床单、被面、部分填充','value':'市场主要表达柔软丝滑、吸湿和凉爽','example_ids':['bedsure','cozyearth','sheets'],'tradeoff':'再生纤维素，不等于直接取出的天然竹纤维；纯纺与混纺需分开。','source_keys':['ftc-bamboo','bedsure','cozyearth','material-132']},
 {'name':'莱赛尔（如TENCEL）','kind':'商用纤维','use':'床单、被面和填充','value':'柔滑、吸湿；不同织造与填充量影响最终体验','example_ids':['sijo','buffy'],'tradeoff':'TENCEL是品牌；需核对是莱赛尔还是莫代尔。材料吸湿不等于成品整晚降温。','source_keys':['tencel-fibers','sijo','buffy']},
 {'name':'棉平纹（Percale）','kind':'纤维＋织造','use':'床单、被套','value':'商家以清爽、透气、酒店触感表达凉爽','example_ids':['brooklinen'],'tradeoff':'平纹是织法；不能只凭棉含量或TC判断散热与柔软。','source_keys':['brooklinen']},
 {'name':'聚酯＋氨纶性能面料','kind':'商用混纺','use':'床单与枕套','value':'弹力贴合、排湿与柔软','example_ids':['sheex-sheets'],'tradeoff':'化纤不等于一定闷热；织物结构与整理需看成品测试。','source_keys':['material-114']},
 {'name':'凉感尼龙＋氨纶','kind':'商用混纺','use':'凉感被贴肤表层','value':'品牌主打接触凉与柔滑','example_ids':['rest','cozy-comforter'],'tradeoff':'面料凉不代表填充不蓄热；套被套后接触界面会改变。','source_keys':['rest-retailer','rest','material-100']},
 {'name':'相变材料（PCM）','kind':'商用调温技术','use':'融入纤维、涂层或填充','value':'在相变温区吸收、储存、释放热量','example_ids':['slumber'],'tradeoff':'储热有限；看温区、含量、所在层及洗后表现，不能写成无限制持续制冷。','source_keys':['outlast','slumber']},
 {'name':'37.5功能颗粒','kind':'商用温湿管理技术','use':'织物、填充等','value':'供应商主张帮助调节贴肤温湿度','example_ids':[],'tradeoff':'需验证具体成品；技术名不代表恒温37.5°C，也不是一种独立纤维。','source_keys':['375']},
 {'name':'工程化聚乙烯（PE）织物','kind':'研发参考路线','use':'研究中的纱线与织物','value':'研究已展示导湿、快干及被动散热潜力','example_ids':[],'tradeoff':'论文样品不能替代商业床品实测；耐洗、手感、织造和供应能力仍需具体验证。','source_keys':['pe-paper']}],
 'terms':[
 {'term':'q-max','meaning':'接触瞬间的热流峰值；测试温差、条件一致时才可比较。','source_keys':['kaken-qmax']},
 {'term':'JIS L 1927','meaning':'接触凉感测试方法；不是面料，也不是商家技术名称。','source_keys':['kaken-qmax']},
 {'term':'Arc-Chill／Evercool','meaning':'商家的技术或系列名称；必须继续核对成分、结构与测试证据。','source_keys':['elegear','rest']}],
 'measurement_note':'摸起来凉、整晚少闷热、睡眠改善是三个不同结果。SLEEP发表的REST组合使用研究摘要报告主观体验改善，但未观察到客观睡眠改善。','measurement_sources':['rest-sleep']}
# Consumer evidence precedes the pyramid and positioning hypotheses.
D['needs']={'title':'需求金字塔','subtitle':'怕热、夜间出汗，且正在考虑更换床品的人群｜研究版',
 'survey':{'title':'美国床品消费者的购买关注点','scope':'一般床品消费者，不限凉感床品','items':[{'label':a,'value':b} for a,b in [('柔软',76),('质量',75),('不留异味',72),('弹性',70),('耐洗',68),('使用寿命',65)]],'source_keys':['cotton-survey'],'note':'2024年12月调查，2025年发布；多选，不相加成100%。发布机构为棉行业机构，五国总样本7,163，美国样本数未单列。'},
 'need_pool':[
 {'id':'n1','need':'贴身不扎、不磨皮肤','role':'不能接受的问题','evidence':'床单样本92条不满粗糙或不够软；有买家明确因粗糙无法接受凉感卖点。','refs':['material-89','material-78'],'review_ids':[619]},
 {'id':'n2','need':'尺寸合适、翻身不滑脱','role':'基本使用要求','evidence':'床单样本38条尺寸适配不满、35条固定不住；两项可重叠。','refs':['material-89'],'review_ids':[221,1389]},
 {'id':'n3','need':'洗后仍好用、材料与承诺一致','role':'不能接受的问题','evidence':'美国一般床品调查关注耐洗；床单评论存在材料预期不符与洗后色斑。','refs':['cotton-survey','material-89','material-78'],'review_ids':[917]},
 {'id':'n4','need':'躺上去有凉爽感','role':'直接诉求','evidence':'已有买家明确说为凉感下单。','refs':['material-78'],'review_ids':[452,917]},
 {'id':'n5','need':'睡久也少闷热、少黏湿','role':'核心问题','evidence':'床单样本存在不够凉或偏热反馈；公开讨论区也区分触感凉与睡久变暖。','refs':['material-89','reddit-rest'],'review_ids':[718]},
 {'id':'n6','need':'柔软舒服，同时有喜欢的覆盖感','role':'附加好处／取舍','evidence':'床单397条认可柔软；个别买家未获得凉感仍因舒服继续使用。凉被另需验证覆盖与重量偏好。','refs':['material-89','material-78'],'review_ids':[718,580]},
 {'id':'n7','need':'晚上少因冷热不适反复调整床品','role':'更高期待','evidence':'凉感床品研究中可见主观体验改善；仍不足以承诺客观睡眠改善。','refs':['rest-sleep'],'review_ids':[]},
 {'id':'n8','need':'价格值得、试错损失可接受','role':'购买约束','evidence':'有买家等合适价格才下单，也有人认为与更高品质产品价差不大。','refs':['material-78'],'review_ids':[475,773]},
 {'id':'n9','need':'颜色与卧室搭配','role':'附加好处','evidence':'美国一般床品调查32%为新颜色购买；床单买家有更换冬季颜色的自述。','refs':['cotton-survey','material-78'],'review_ids':[28]}],
 'pyramid':{'title':'从基本可用，到睡眠更少受打扰','layers':[
 {'id':'base','level':1,'label':'基本可用、贴身舒服','items':['不扎皮肤','尺寸固定','耐洗耐用','材料与承诺一致'],'need_ids':['n1','n2','n3'],'evidence_strength':'已有具体反馈支撑'},
 {'id':'core','level':2,'label':'真正解决热与湿的不适','items':['接触时凉爽','睡久少闷热','减少黏湿','保留喜欢的柔软与覆盖感'],'need_ids':['n4','n5','n6'],'evidence_strength':'需求存在；各效果需分别测量'},
 {'id':'outcome','level':3,'label':'整晚舒适，少被冷热打扰','items':['减少反复掀被、找凉处','在偏好温度下稳定休息'],'need_ids':['n7'],'evidence_strength':'期望结果；因果与长期效果待验证'}],
 'side_constraints':['预算与试错成本','清洗便利','颜色风格','材料偏好'],
 'note':'按用户算法梳理的需求递进假设，不是人群普遍固定的先后顺序，也不是销量权重。现有证据中有人愿为柔软保留不够凉的床单，因此不能把层级画成绝对门槛。'},
 'sample_note':'本页床单计数来自Shilucheng的928条近期主样本（2026年9月24日至11月4日）。其余评论组未混入。它支持需求线索，不代表美国需求占比；凉被需求仍需更多品牌的同口径评论验证。',
 'principle_sources':['user-algorithm']}
D['mindmap']={'title':'心智地图','subtitle':'需求入口 → 替代选择 → 品牌认知线索','status':'探索版｜尚未测定品牌心智位次','intro':'从消费者如何理解和选择解决方案出发。图中的品牌表示已经看到的表达或使用关联，不代表已占领某个认知。',
 'center':'睡觉太热／不舒服，换什么能改善',
 'lanes':[
 {'id':'m1','need_ids':['n4','n5'],'entry':'换上就能感觉凉','category':'凉感床单／凉感被／凉毯','alternatives':['原有床单与厚被','其他接触凉感床品'],'brands':[{'product_id':'rest','concept':'怕热者的Evercool凉感被','evidence':'claim'},{'product_id':'elegear','concept':'Arc-Chill接触凉感','evidence':'claim'},{'product_id':'sheets','concept':'为凉感而买','evidence':'consumer'}],'known':'Shilucheng有明确为凉感购买的评论；REST与Elegear主推凉感。','unknown':'谁会被消费者首先想到、各品牌认知覆盖率，尚无调查。','source_keys':['material-78','rest','elegear']},
 {'id':'m2','need_ids':['n5','n6'],'entry':'换一种清爽、舒服的面料','category':'棉平纹／竹源粘胶／莱赛尔床品','alternatives':['熟悉的棉床品','不同纤维与织法的床品'],'brands':[{'product_id':'brooklinen','concept':'酒店式清爽棉平纹','evidence':'claim'},{'product_id':'cozyearth','concept':'柔软丝滑的竹源粘胶','evidence':'claim'},{'product_id':'sijo','concept':'轻盈莱赛尔','evidence':'claim'},{'product_id':'buffy','concept':'莱赛尔表层与填充','evidence':'claim'}],'known':'美国一般床品调查64%偏好棉，说明材料名称已有选择意义；并未测定这些品牌的对应心智。','unknown':'“天然”“竹”“桉树”等词对信任与溢价的实际贡献尚未测定。','source_keys':['cotton-survey','brooklinen','cozyearth','sijo','buffy']},
 {'id':'m3','need_ids':['n5','n7'],'entry':'既怕热，也不想忽冷忽热','category':'调温床品','alternatives':['普通薄被','接触凉感床品'],'brands':[{'product_id':'slumber','concept':'Outlast相变调温','evidence':'claim'}],'known':'Slumber Cloud将吸热和释热作为核心表达。','unknown':'消费者是否将“调温”视为独立品类，以及愿付多少溢价，尚未验证。','source_keys':['slumber','outlast']},
 {'id':'m4','need_ids':['n1','n6','n8'],'entry':'想更柔软舒服，价格也合适','category':'床品舒适升级','alternatives':['原品牌替换款','价格相近的床单套装'],'brands':[{'product_id':'sheets','concept':'柔软与价格的组合','evidence':'consumer'},{'product_id':'sheex-sheets','concept':'弹力、透气的性能面料','evidence':'claim'},{'product_id':'bedsure','concept':'凉爽丝滑、日常易用','evidence':'claim'}],'known':'Shilucheng有因手感再买的自述，也有与Sam’s和Amazon床单比较的具体评论。','unknown':'这类选择是产品层面的理由，不能直接判定品牌忠诚。','source_keys':['material-78','material-114','bedsure']},
 {'id':'m5','need_ids':['n5','n7'],'entry':'不只换布料，直接调节睡眠环境','category':'空调／风扇／主动床面控温','alternatives':['更换床品','减少盖被'],'brands':[],'known':'按“解决同一需求的不同手段互为对手”纳入竞争边界。','unknown':'这是待调查的替代选择范围；尚未量化与凉感床品之间的替代率。','source_keys':['user-algorithm']}],
 'legend':[{'id':'consumer','label':'消费者自述已有线索','style':'solid'},{'id':'claim','label':'品牌正在宣传','style':'outline'}],
 'method':'依据定位系的品类阶梯与品牌关联思路，并结合用户算法先梳理需求与替代方案。没有无提示品牌提及、关联强度及优先选择数据时，不给品牌排心智名次，也不把没有证据的区域称为空白市场。',
 'method_sources':['ries-original','ries-2026','user-algorithm'],
 'opportunities_title':'待验证的机会线索',
 'opportunities':[
 {'title':'把“碰上去凉”与“睡久少闷热”分别兑现','basis':'存在为凉感购买却未获得预期效果的反馈；产品测试与用户表达应覆盖两个不同结果。','boundary':'这是需求落差线索，尚未证明未被竞争者满足。','source_keys':['material-78','reddit-rest','kaken-qmax']},
 {'title':'把凉感与柔软、固定、耐洗一起设计','basis':'已有反馈表明粗糙或尺寸问题会破坏体验；不能只优化凉感参数。','boundary':'先核实跨品牌重复出现的痛点与解决成本，再判断是否值得开发。','source_keys':['material-89','material-78','cotton-survey']}],
 'validation_needed':'品牌心智排名、各认知的人群规模及付费溢价，需要消费者无提示提及、选择对照与价格验证；不以商家宣传或销量代填。'}
D['glossary'].update({'pcm':{'label':'相变材料','text':'在相变温区吸收或释放热量的材料。储热能力有限，不等于持续主动制冷。'},'percale':{'label':'棉平纹','text':'Percale指常见的平纹织造；触感通常被商家描述为清爽。不能仅凭织法确定全部性能。'}})
D['footer']={'title':'来源与待补资料','text':'每项数字保留对象、渠道、规格、时间和来源。待核实链接可以继续收录，未经研究不自动进入正文。','gaps':['美国凉感被/凉毯总规模及统一品类占比','品牌全渠道销售拆分与份额','单品近期可比销量序列','跨品牌同口径评论与消费者心智调查'],'scope_note':'本页为行业基础与研究线索，品牌和单品的深入结论进入各自报告。'}
(O/'01_核定内容.json').write_text(json.dumps(D,ensure_ascii=False,indent=2))
print('核定内容',len(products),'products',len(sources),'sources',len(json.dumps(D,ensure_ascii=False)))
