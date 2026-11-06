"""Publish verified public facts; raw evidence remains separate from later analysis."""
import sys,json,sqlite3,pathlib,re,hashlib,csv
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import server,reports
W=pathlib.Path(__file__).parent;NOW=server.now();DATE='2026-11-05'
c=server.conn();sources={};rr={};docs={};added=[]
def source(key,title,url=None,publisher='',typ='官方页面',summary='',published='',local=''):
 meta=W/(key+'.meta.json');m=json.loads(meta.read_text()) if meta.exists() else {}
 u=url or m.get('url');dt=m.get('retrieved_at',NOW)
 old=c.execute('SELECT id FROM materials WHERE url=?',(u,)).fetchone() if u else None
 if old: mid=old[0]
 else:
  mid=c.execute('INSERT INTO materials(title,url,source_type,publisher,published_at,retrieved_at,summary,local_path,access_note) VALUES(?,?,?,?,?,?,?,?,?)',(title,u,typ,publisher,published,dt,summary,local,'本轮基础事实核查；统计口径见对应研究条目。')).lastrowid
 sources[key]=mid;return mid
def link(mid,bid,pid,sec,topic):
 if not c.execute('SELECT 1 FROM material_links WHERE material_id=? AND brand_id=? AND product_id IS ? AND section=? AND topic=?',(mid,bid,pid,sec,topic)).fetchone():c.execute('INSERT INTO material_links(material_id,brand_id,product_id,section,topic) VALUES(?,?,?,?,?)',(mid,bid,pid,sec,topic))
def record(key,bid,pid,sec,ti,title,body,src,kind='事实',status='已核实页面信息'):
 topic=server.TOPICS[sec][ti];ids=[sources[x] for x in src]
 for m in ids:link(m,bid,pid,sec,topic)
 rid=c.execute('INSERT INTO records(brand_id,product_id,section,topic,title,body,kind,status,evidence,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)',(bid,pid,sec,topic,title,body,kind,status,json.dumps(ids),NOW)).lastrowid
 rr[key]=rid;added.append(rid);return rid
def table(cols,rows):return '| '+' | '.join(cols)+' |\n| '+' | '.join(['---']*len(cols))+' |\n'+'\n'.join('| '+' | '.join(str(x) for x in r)+' |' for r in rows)
def url(label,u):return f'[{label}]({u})'
def obs(pid,metric,value,unit,variant,scope,key,note=''):
 m=c.execute('SELECT * FROM materials WHERE id=?',(sources[key],)).fetchone()
 c.execute('INSERT INTO observations(product_id,metric,value,unit,variant,scope,observed_at,retrieved_at,source_url,source_type,availability,note) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(pid,metric,str(value),unit,variant,scope,m['retrieved_at'],m['retrieved_at'],m['url'],m['source_type'],'已读取',note))
def newdoc(bid):
 b=c.execute('SELECT * FROM brands WHERE id=?',(bid,)).fetchone();docs[bid]=reports.empty_document(c,b,server.TOPICS);return docs[bid]
def question(qid,title,answer='',keys=(),tables=(),note='',points=()):
 return dict(id=qid,title=title,answer=answer,record_ids=[rr[k] for k in keys],tables=[dict(record_id=rr[k],mode='table',purpose='core') for k in tables],note=note,points=list(points))
def topic(bid,sec,ti,pid,qs,keys,coverage='部分回答',gap=''):
 t=next(x for x in docs[bid]['sections'][sec-1]['topics'] if x['topic']==server.TOPICS[sec][ti] and x.get('product_id')==pid)
 t.update(questions=qs,record_ids=[rr[k] for k in keys],coverage=coverage,answer_type='事实概括' if coverage in ['已回答','部分回答'] else '研究问题',gap=gap,impact='',finding='',featured=[],bullets=[],figures=[])
 return t

def catalog_record(key,bid,catkey,domain,items):
 cat=json.loads((W/(catkey+'.raw')).read_text())['products'];rows=[]
 for label,handle in items:
  x=next(x for x in cat if x['handle']==handle);v=[float(v['price']) for v in x['variants']];low,high=min(v),max(v)
  price=f'${low:g}' if low==high else f'${low:g}–{high:g}'
  rows.append([url(label,domain+'/products/'+handle),price])
 return record(key,bid,None,1,2,'官网主要产品系列与页面价格带',table(['产品系列','页面价格范围（美元）'],rows)+'\n\n2026年11月5日官网公开商品目录的变体报价，含不同尺寸、颜色及促销；不是同规格横向比较。未把颜色重复链接、礼品与组合套装计为独立产品款数。', [catkey])

# A. Shilucheng mattress topper: reuse existing brand facts.
source('topper','Shilucheng 仿羽绒凉感褥垫｜TikTok美国商品页','https://shop.tiktok.com/us/pdp/cooling-mattress-topper-by-shilucheng-extra-down-alternative-fill/1729439070512124657', 'TikTok / Shilucheng',summary='灰色双人床、2英寸厚；读取2026-11-05。')
source('topper_official','Shilucheng 官网褥垫产品页','https://shilucheng.com/products/bamboo-mattress-topper','Shilucheng')
source('topper_variants','Shilucheng 官网褥垫规格报价','https://shilucheng.com/products/bamboo-mattress-topper.js','Shilucheng',typ='官方商品数据')
legacy=server.LEGACY/'Shilucheng_仿羽绒凉感褥垫_1729439070512124657_有效评论_已整理.csv'
copy=ROOT/'data/attachments/Shilucheng_褥垫_1000条既有评论_20261105.csv';copy.write_bytes(legacy.read_bytes())
source('topper_reviews','Shilucheng 褥垫｜1,000条既有有效评论',publisher='既有评论采集与去重记录',typ='原始评论',summary='原159条与软件导出有效条目、后续补采合并去重；推荐与最新排序混合样本。',local='attachments/'+copy.name)
result=server.import_reviews(c,'topper',legacy.read_text(encoding='utf-8-sig'),str(legacy));assert result.get('added')==1000,result
r=record('topper_identity','shilucheng','topper',2,0,'研究商品与规格',table(['项目','已核实信息'],[
 ['商品',url('Shilucheng 仿羽绒凉感褥垫（本款）','https://shop.tiktok.com/us/pdp/cooling-mattress-topper-by-shilucheng-extra-down-alternative-fill/1729439070512124657')],['商品ID','1729439070512124657'],['本次报价规格','灰色 · 双人床（Queen）· 厚约5厘米（2英寸）'],['垫面尺寸','约152×203厘米（60×80英寸）'],['厚度选项','约5厘米 / 7.6厘米（2 / 3英寸）'],['适配床垫厚度','约20–53厘米（8–21英寸），不是褥垫本身的厚度'],['包装','1件褥垫'],['卖家','Shilucheng Home']]),['topper'])
record('topper_market','shilucheng','topper',2,0,'褥垫价格与平台表现',table(['指标','2026年11月5日页面展示','统计范围'],[['活动价','$41.90','灰色 / Queen / 2英寸；划线价$83.80'],['累计售出','70.8K（约7.08万件）','整个多规格商品链接；非月销量'],['评分','4.3 / 5','商品链接总体评分'],['评价数量','9,008条全球评价','页面总数；不等于本地评论样本数']]),['topper'])
record('topper_material','shilucheng','topper',2,0,'材料标注与产品宣称',table(['项目','商品页面内容','核查说明'],[['表层材料','标题写Bamboo Top；参数写Cotton','表述不一致，成分比例未披露；不能确认竹纤维含量'],['填充','4D超细纤维仿羽绒','商家描述；未核实具体纤维成分及填充克重'],['主推价值','加软、透气、凉感、深床笠包覆','品牌设置的购买理由；并非已证实的消费者体验'],['使用准备','真空包装；建议低温烘约20分钟恢复蓬松','商家使用说明'],['认证','页面出现OEKO-TEX相关宣称','未取得可独立核验的对应证书']]),['topper'],'品牌宣称','品牌自述')
record('topper_cross','shilucheng','topper',2,0,'官网近似规格报价，保留渠道差异',table(['官网规格','报价 / 划线价','备注'],[['深灰 Queen / 2英寸','$41.90 / $83.80','官网变体显示可售'],['深灰 Queen / 3英寸','$51.90 / $103.80','官网变体显示可售'],['Bamboo Queen / 2英寸','$47.90 / $95.80','不同材料/颜色标签；不与TikTok灰色款混为同一规格']])+'\n\n官网产品属于同类褥垫系列；跨渠道精确SKU对应关系尚未取得品牌确认。', ['topper_official','topper_variants'])
record('topper_sample','shilucheng','topper',2,1,'褥垫既有评论已独立入库','已导入1,000条既有有效评论，商品ID均为1729439070512124657。保留原文、日期、星级、规格、地区、原文件与采样方式。推荐排序与最新排序样本混合，不能据此直接计算全体消费者的满意率。本轮未做情绪与主题分析。',['topper_reviews'])
record('topper_causes','shilucheng','topper',2,2,'畅销原因等待评论与竞争研究','尚未完成本款评论主题分析、同规格竞品价格与体验对比、达人覆盖和转化核查，暂不判断畅销原因或领先优势。',['topper','topper_reviews'],'缺口','等待前置证据')
for metric,v,u,scope in [('展示活动价',41.90,'USD','灰色 Queen 2英寸'),('页面累计售出','70.8K','件','商品链接累计约数'),('评分',4.3,'/5','商品链接'),('评价数量',9008,'条','全球评价')]:obs('topper',metric,v,u,'灰色 / Queen / 2英寸',scope,'topper','2026-11-05读取；多规格合并指标不代表单个规格。')

# B. Cozy Bliss brand, then product, channels, history.
for k,title,pub in [('cozy_home','Cozy Bliss 官网首页','Cozy Bliss'),('cozy_story','Cozy Bliss 品牌故事','Cozy Bliss'),('cozy_sunwin','Sunwin旗下Cozy Bliss品牌介绍','Sunwin'),('cozy_catalog','Cozy Bliss 官网产品目录与变体报价','Cozy Bliss'),('cozy_amazon','Cozy Bliss 研究款亚马逊商品页 B0BVQMTD8W','Amazon / Cozy Bliss'),('cozy_product','Cozy Bliss 官网近似凉感被产品页','Cozy Bliss'),('cozy_product_variants','Cozy Bliss 官网近似款规格报价','Cozy Bliss'),('cozy_returns','Cozy Bliss 退货政策','Cozy Bliss'),('cozy_shipping','Cozy Bliss 配送政策','Cozy Bliss'),('cozy_instagram','Cozy Bliss Instagram账号','Instagram'),('cozy_facebook','Cozy Bliss Facebook主页','Facebook'),('cozy_tiktok','Cozy Bliss TikTok官方账号','TikTok'),('cozy_tkproduct','Cozy Bliss TikTok店铺关联商品与店铺信息','TikTok'),('cozy_popup','Sunwin：Cozy in Hudson三品牌快闪公告','Sunwin')]:
 if not (W/(k+'.meta.json')).exists():
  print('MISSING SOURCE KEY',k);raise SystemExit(1)
 source(k,title,publisher=pub,published='2025-11-26' if k=='cozy_popup' else '')
source('cozy_tm','加拿大商标公报｜Cozy Bliss申请记录','https://publications.gc.ca/collections/collection_2021/opic-cipo/RG42-2-68-3488-eng.pdf#page=519','加拿大知识产权局',typ='官方登记公报',summary='公报印刷页519；申请号2,019,692，2020-02-22提交。',published='2021')
record('cozy_brand','cozy-bliss',None,1,0,'品牌背景与希望传达的价值',table(['问题','已查事实与品牌自述'],[['成立背景','官网关联Facebook自述：2018年创于纽约；Sunwin官网把Cozy Bliss列入自有品牌'],['主营业务','毯、被、床单、枕类等居家纺织品；官网另有加热产品与宠物用品'],['品牌定位与核心宣称','围绕柔软触感、放松与舒适的居家生活介绍产品'],['目标消费者','官方凉感被面向睡眠怕热、夜间出汗者；品牌故事也覆盖一般居家舒适需求'],['差异化定位','材料与系列有不同表达；尚无消费者研究证明某种价值已形成品牌独占认知']]),['cozy_home','cozy_story','cozy_facebook','cozy_sunwin'],'品牌宣称','品牌自述')
record('cozy_owner','cozy-bliss',None,1,0,'品牌与Sunwin的可核对关系','Sunwin官网自有品牌目录包含Cozy Bliss。加拿大商标公报中，Cozy Bliss申请号2,019,692的申请人为SHANGHAI SUNWIN INDUSTRY GROUP CO., LTD.，申请日2020年2月22日。这是历史申请记录，不代替当前全球商标权属查询，也不能把Sunwin集团收入当成Cozy Bliss品牌收入。',['cozy_sunwin','cozy_tm'])
cozy_amazon_store='https://www.amazon.com/stores/CozyBliss/page/AA431030-B509-4EF2-82F3-424C35568A06';cozy_tk_store='https://shop.tiktok.com/us/store/cozy-bliss-us/7495792541744990486'
record('cozy_channels','cozy-bliss',None,1,1,'已确认的销售渠道',table(['渠道','已确认入口','公开经营数据'],[['独立站',url('Cozy Bliss官网','https://cozybliss.com/'),'销售额未公开'],['Amazon美国',url('Cozy Bliss品牌店',cozy_amazon_store),'可读取指定商品表现；品牌总销售额未知'],['TikTok美国',url('Cozy Bliss US店铺',cozy_tk_store),'关联商品页展示店铺累计售出5,511件；约3.4K粉丝'],['线下历史活动',url('2025年Hudson快闪店公告','https://www.sunwinglobalco.com/news/sunwin-global-gets-into-the-holiday-spirit-with-its-1st-pop-up-shop'),'临时快闪记录，不代表目前有常设门店']])+'\n\nTikTok店铺指标读取于2026-11-05，覆盖店铺所有商品，不是本款Amazon凉感被销量。', ['cozy_home','cozy_amazon','cozy_tkproduct','cozy_popup'])
record('cozy_scalegap','cozy-bliss',None,1,1,'品牌规模与渠道份额未取得可靠公开数字','已查品牌官网、集团品牌介绍和销售平台；未找到可核验的品牌销售额、增长率、各渠道销售额/占比。当前不能判断最大销售渠道或增长最快渠道。平台单品月购提示与店铺累计件数不可混算。',['cozy_home','cozy_sunwin','cozy_amazon','cozy_tkproduct'],'缺口','已查未找到可靠资料')
catalog_record('cozy_matrix','cozy-bliss','cozy_catalog','https://cozybliss.com',[
 ('Cloud-Like 凉感被','lightweight-cooling-comforter'),('Outlast 调温凉感被','outlast-deep-sleep-cooling-comforter'),('Sorona 华夫格凉感被','waffle-cooling-comforter'),('Tencel 凉感被','luxurious-tencel-lyocell-cooling-comforter'),('凉感床单套装（含平床单）','deep-sleep-cooling-fitted-flat-sheet-with-pillowcase-set'),('双面凉感长抱枕','adjustable-dual-sided-cooling-body-pillow'),('泡泡仿毛皮电热毯（米色）','beige-bubble-faux-fur-electric-blanket')])
record('cozy_matrixgap','cozy-bliss',None,1,2,'产品布局可见，收入集中度未知','官网同时销售床单、被、毯、枕等多个品类。未取得品类销售额与单品贡献，不能由目录丰富直接判断其收入依靠多品类还是单一爆款。',['cozy_catalog'],'缺口','已查未找到可靠资料')
record('cozy_identity','cozy-bliss','cozy-comforter',2,0,'经典双面凉感被：研究对象与材料',table(['项目','页面信息'],[['商品',url('Cozy Bliss 经典双面凉感被（本款）','https://www.amazon.com/dp/B0BVQMTD8W')],['ASIN','B0BVQMTD8W'],['规格','灰/蓝色 · 双人被（Queen）· 约229×229厘米（90×90英寸）'],['套件','1条被；不含枕套'],['面料','90%尼龙＋10%氨纶（商品参数）'],['填充','聚酯仿羽绒'],['清洗','冷水轻柔机洗、低温烘干；不漂白、不熨烫、不干洗'],['卖家 / 发货','Cozy Bliss / Amazon']]),['cozy_amazon'])
record('cozy_performance','cozy-bliss','cozy-comforter',2,0,'亚马逊研究款：价格与平台表现',table(['指标','页面显示','口径'],[['价格','$69.99','灰/蓝 Queen；不含信用卡开卡等条件优惠'],['评分','4.5 / 5','页面综合评分'],['评分数量','2,731','ratings，不能视为2,731条文字评论'],['近一个月购买提示','50+','门槛式提示；不是精确月销量'],['类目排名','#13,802 家居与厨房；#25 被芯及羽绒被','2026-11-05观察时点排名']]),['cozy_amazon'])
record('cozy_claim','cozy-bliss','cozy-comforter',2,0,'商家给出的购买理由','主推睡眠怕热与夜间出汗场景，宣称Q-Max＞0.45、触肤降温2–5℃、双面凉感、丝滑轻薄和机洗。商品页列OEKO-TEX编号22.HCN.14794。以上是页面宣称，未在本研究中做性能或证书有效性验证；不据此认定比竞品更凉。',['cozy_amazon'],'品牌宣称','品牌自述')
record('cozy_identityrisk','cozy-bliss','cozy-comforter',2,0,'官网近似款与本款保持独立',table(['字段','本款：Amazon','官网Cloud-Like近似款'],[['商品入口',url('B0BVQMTD8W','https://www.amazon.com/dp/B0BVQMTD8W'),url('Cloud-Like凉感被','https://cozybliss.com/products/lightweight-cooling-comforter')],['灰/蓝 Queen价格','$69.99','$99；划线价$129'],['材料页面表述','90%尼龙＋10%氨纶；聚酯填充','Material：100% Microfiber'],['凉感宣称','Q-Max＞0.45','Q-Max＞0.46'],['评价口径','2,731个评分','官网显示1,306条评价']])+'\n\n同色同尺寸不足以确认同一SKU。材料表述和指标不同，暂不合并价格、销量、评论或性能。',['cozy_amazon','cozy_product','cozy_product_variants'])
record('cozy_reviewgap','cozy-bliss','cozy-comforter',2,1,'尚未取得可分析的文字评论样本','已保存商品页评分及总评分数；本款文字评论尚未形成去重、可追溯的分析样本。认可/不认可的完整主题与占比、明确购买理由、未满足需求等待评论材料，不能从总评分或商品宣传推导。',['cozy_amazon'],'缺口','需工具或权限')
record('cozy_causegap','cozy-bliss','cozy-comforter',2,2,'畅销原因研究等待前置事实','消费者购买原因、相对竞品的领先之处、销量的主要驱动因素均未完成验证。需先补评论、同规格竞争比较及渠道转化资料。',['cozy_amazon'],'缺口','等待前置证据')
cozy_acc=[['TikTok',url('@cozybliss_usoffical','https://www.tiktok.com/@cozybliss_usoffical'),'3,418粉丝；228个视频；5,637次获赞'],['Instagram',url('@cozybliss_official','https://www.instagram.com/cozybliss_official/'),'5,740粉丝；656篇帖子；705关注'],['Facebook',url('Cozy Bliss','https://www.facebook.com/cozyblissofficial'),'9,390粉丝']]
record('cozy_accounts','cozy-bliss',None,3,0,'官网关联社交账号',table(['渠道','账号链接','公开统计'],cozy_acc)+'\n\n2026-11-05读取平台公开页面元数据；各渠道至少确认一个官方关联账号，不代表品牌所有账号。未取得完整发帖日期序列，发布频率留空；粉丝数不等于销量。',['cozy_home','cozy_tiktok','cozy_instagram','cozy_facebook'])
record('cozy_actions','cozy-bliss',None,3,0,'官网当前促销与服务信息',table(['动作','可核实内容'],[['首页联合展示','2026-11-05首屏展示Cozy Bliss × Heatbloom，并标Coming Soon；不能当成已完成销售'],['组合促销','首页展示订单满$129赠毯（标称价值$59）'],['配送','美国订单满$59免运费；页面列处理时间2–3个工作日'],['退货','官网政策：30天、未使用未清洗并保留包装；列$10退货费用']])+'\n\n官网售后规则不套用到Amazon订单；赠品标称价值不等于消费者实际支付价值。',['cozy_home','cozy_shipping','cozy_returns'])
record('cozy_channelgap','cozy-bliss',None,3,0,'渠道经营构成仍缺数据','达人带货与品牌自营销售占比、直播与短视频销售占比、广告投放金额、视频成交额、持续发布频率均未有足够数据。先保留字段，不从点赞量或粉丝量推算成交。',['cozy_tiktok','cozy_tkproduct'],'缺口','需工具或权限')
record('cozy_top5gap','cozy-bliss',None,3,1,'TOP5视频待选定并确认','下一步应以研究商品相关视频为候选池，展示链接、账号、发布日期和点赞/播放指标后确认TOP5；不把官方账号最新5条或店铺其他商品视频直接当成本款TOP5。',['cozy_tiktok'],'缺口','待你确认')
record('cozy_contentgap','cozy-bliss',None,3,2,'内容总结等待视频样本','尚未完成本款TOP5内容确认与逐条观看，暂不下“内容为何有效”或“建立何种消费者认知”的结论。',['cozy_tiktok'],'缺口','等待前置证据')
record('cozy_timeline','cozy-bliss',None,4,0,'可核实的发展节点',table(['时间','事件','材料性质'],[['2018年','品牌Facebook自述创于纽约','品牌自述，非公司登记核验'],['2020-02-22','Cozy Bliss加拿大商标申请，申请人为SHANGHAI SUNWIN INDUSTRY GROUP CO., LTD.','加拿大商标公报；申请号2,019,692'],['2025-11-26公告','Sunwin宣布Cozy Bliss、Snuggle Sac、Amélie Home联合举办Cozy in Hudson快闪店；计划2025-12-01至2026-01-01，纽约州Hudson 316 Warren St','集团公告；未独立核验实际完整营业周期']]),['cozy_facebook','cozy_tm','cozy_popup'])
record('cozy_growthgap','cozy-bliss',None,4,1,'活动事实不等于增长效果','已收录品牌归属、产品扩展及快闪公告，但未获得事件前后的销售、客群或渠道变化数据，不能确认哪项动作带来品牌快速增长。',['cozy_popup','cozy_catalog'],'缺口','等待前置证据')
for metric,v,u,sc in [('展示价格',69.99,'USD','灰/蓝Queen90×90英寸'),('评分',4.5,'/5','Amazon商品页'),('评分数量',2731,'个','ratings，不等于文字评论'),('近月购买提示','50+','次','页面过去一个月门槛提示，非精确销量')]:obs('cozy-comforter',metric,v,u,'灰/蓝 / Queen / 90×90英寸',sc,'cozy_amazon')

# C. SHEEX
for k,title in [('sheex_home','SHEEX官网首页'),('sheex_company','SHEEX公司与创始故事'),('sheex_catalog','SHEEX官网产品目录与变体报价'),('sheex_product','SHEEX Original Performance床单商品页'),('sheex_variants','SHEEX经典床单规格报价'),('sheex_returns','SHEEX退换与保证政策'),('sheex_shipping','SHEEX配送政策'),('sheex_instagram','SHEEX Instagram账号'),('sheex_facebook','SHEEX Facebook主页'),('sheex_tiktok','SHEEX TikTok账号'),('sheex_youtube','SHEEX YouTube频道'),('sheex_midnight','SHEEX与brrr°合作推出Midnight Label'),('sheex_sleepweek','SHEEX Sleep Week 2026活动'),('sheex_affiliate','SHEEX联盟推广规则')]:source(k,title,publisher='SHEEX / 对应公开平台',published={'sheex_midnight':'2020-09-28','sheex_sleepweek':'2026-03-05'}.get(k,''))
source('sheex_verlo_public','Verlo：SHEEX Elevated Performance销售页','https://verlo.com/national/product/sheex-elevated-performance-sheet-set/','Verlo',summary='本轮通过检索工具读取缓存页面，抓取时间标记为去年；直连SSL失败。不作实时库存或当日报价证明。')
source('sheex_ads','SHEEX与Wpromote：Google Shopping历史投放案例','https://www.wpromote.com/wp-content/uploads/2020/06/Google_Partner-Case-Study-_-SHEEX-2019-1-2.pdf','Wpromote / Google案例',typ='服务商案例',summary='历史案例，正文未披露具体统计期；成效由服务商公布，不是当前品牌总增长数据。')
record('sheex_brand','sheex',None,1,0,'品牌背景、定位与消费者',table(['问题','已查内容'],[['创始背景','Michelle Marciniak与Susan Walvius曾任南卡罗来纳大学篮球教练；官网将创业想法追溯到2007-08-25'],['主营业务','功能性床品与睡衣；官网列床单、被、枕、保护垫及睡眠配件'],['所在地','公司介绍为美国新泽西州企业；官网联系地址为Cherry Hill'],['定位','将运动服面料的柔软、弹性、透气排湿引入床品；品牌称Performance Bedding'],['目标需求','希望改善闷热、出汗与睡眠舒适度；不把运动员形象等同于实际消费者组成'],['差异化主张','运动性能面料、柔软触感、透气排湿；“世界首创”等说法为品牌宣称，尚未独立验证排他性']]),['sheex_company','sheex_home'],'品牌宣称','品牌自述')
record('sheex_channels','sheex',None,1,1,'销售入口与零售渠道证据',table(['渠道','入口 / 已知事实','核查边界'],[['官网独立站',url('SHEEX.com','https://www.sheex.com/'),'当前可读取商品、报价和购买入口'],['Verlo床垫零售商',url('SHEEX Elevated Performance系列','https://verlo.com/national/product/sheex-elevated-performance-sheet-set/'),'检索可读零售商品页；缓存非实时，不能确认今日库存'],['历史零售渠道','官网公司介绍提及Bed Bath & Beyond、百货、床垫与家具零售商','介绍未标更新时间；不将其中所有渠道视作当前仍在售']]),['sheex_home','sheex_company','sheex_verlo_public'])
record('sheex_scalegap','sheex',None,1,1,'品牌规模和渠道销售份额未公开','未取得品牌官方销售总额、同比增长或渠道销售占比。第三方网站营业额区间及站点销售估算口径不一致，未作为已核事实入表。不能由官网评价数量推导品牌收入或最大渠道。',['sheex_home','sheex_company'],'缺口','已查未找到可靠资料')
catalog_record('sheex_matrix','sheex','sheex_catalog','https://www.sheex.com',[
 ('Original Performance经典床单套装','original-performance-sheet-set'),('Active Comfort床单套装','sheex-active-comfort-sheet-set'),('Arctic Aire·MAX床单套装','arctic-aire-max-sheet-set'),('Nightfall床单套装','nightfall-sheet-set'),('Original Performance四季被','sheex-original-performance-all-season-comforter'),('Cool Cloud被','nightfall-cool-cloud-cover'),('VersaCloud可调节枕','versa-cloud-adjustable-hybrid-pillow'),('女式居家短裤','womens-drawstring-pj-short'),('SleepEngine POD睡眠设备','sleep-engine-pod-by-cambridge-sleep-sciences')])
record('sheex_matrixgap','sheex',None,1,2,'多品类布局已确认，销售贡献未知','官网有多系列床单，并延伸至被、枕、睡衣和睡眠设备。目录报价涵盖促销与不同规格；未有各系列销量和收入贡献，不能判断收入是否主要依赖经典床单。',['sheex_catalog'],'缺口','已查未找到可靠资料')
record('sheex_identity','sheex','sheex-sheets',2,0,'经典性能床单：规格、组成与材料',table(['项目','已核实页面信息'],[['商品',url('SHEEX Original Performance经典性能床单套装（本款）','https://www.sheex.com/products/original-performance-sheet-set')],['本次报价规格','亮白色 · 双人床（Queen）· 四件套'],['套件内容','1条平床单＋1条床笠＋2只枕套'],['面料','87%聚酯纤维＋13%氨纶'],['床笠对应床垫','约152×203厘米；页面称可包覆厚约46厘米（18英寸）的床垫'],['床单尺寸','约259×229厘米（102×90英寸）'],['枕套尺寸','约76×51厘米（30×20英寸）'],['产品设计','弹力面料；运动服式弹性包边；多颜色和尺寸']]),['sheex_product'])
record('sheex_price','sheex','sheex-sheets',2,0,'官网经典床单价格与评价',table(['规格 / 指标','2026年11月5日显示','备注'],[['亮白 Queen四件套','$194.35；划线价$299','变体显示可售'],['柠檬黄 Queen四件套','$179.40；划线价$299','不同颜色活动价；显示可售'],['Meridian Blue Queen','$179.40','该颜色规格显示不可售，不作为可购买低价'],['商品评价','6,896条；约4.74 / 5','本商品总体评价，非品牌17,000+总评价'],['销量 / 销售额','未公开','不从评论数倒推销量']]),['sheex_product','sheex_variants'])
record('sheex_claim','sheex','sheex-sheets',2,0,'官网宣称与售后条件','品牌宣称四向弹力、柔软、透气排湿和温度调节；页面列OEKO-TEX编号BJ025254961，未在认证方核验。官网退换专页写购买日起60晚保证，礼品卡、国际订单及Final Sale等有排除条款；运费不退。配送页另留“30天退换”表述，与专页不一致，不能将所有订单直接称为无条件60晚试睡。',['sheex_product','sheex_returns','sheex_shipping'],'品牌宣称','品牌自述')
record('sheex_reviewgap','sheex','sheex-sheets',2,1,'消费者文字评论待独立采集','已取得商品总体评分与评价数量，但尚未建立可追溯、去重后的评论样本。官网自动生成的评论摘要不作为本研究的消费者判断；认可/不认可占比、购买理由及未满足需求等待原文分析。',['sheex_product'],'缺口','待研究')
record('sheex_causegap','sheex','sheex-sheets',2,2,'单品成功原因暂不下结论','功能面料与售后政策是已查产品事实，但尚不足以证明相对竞品的领先、消费者的实际付费理由或销量驱动。需要评论原文、同规格竞争比较及渠道成交资料。',['sheex_product'],'缺口','等待前置证据')
record('sheex_accounts','sheex',None,3,0,'官网关联的社交账号',table(['渠道','账号链接','公开统计'],[['Instagram',url('@SHEEXOfficial','https://www.instagram.com/SHEEXOfficial/'),'约21K粉丝；2,347篇帖子；1,193关注'],['Facebook',url('SHEEX','https://www.facebook.com/SHEEX'),'101,107粉丝'],['TikTok',url('@sheex','https://www.tiktok.com/@SHEEX'),'2,764粉丝；46个视频；1,107次获赞'],['YouTube',url('SHEEX','https://www.youtube.com/user/sheexbedding'),'约2.38K订阅者；88个视频'],['Pinterest',url('SHEEX','https://pinterest.com/SHEEX'),'官网关联入口已确认；未核实统计']])+'\n\n2026-11-05公开页面元数据，账号粉丝和视频数为账号整体，不是本款商品表现。各渠道至少确认一个官方关联账号；未完成完整账号矩阵或持续发布频率统计。',['sheex_home','sheex_instagram','sheex_facebook','sheex_tiktok','sheex_youtube'])
record('sheex_actions','sheex',None,3,0,'可核实的推广动作',table(['动作','公开内容','不可据此推导的结果'],[['联盟推广',url('Partnerize联盟计划','https://www.sheex.com/pages/affiliate')+'；页面列基础佣金8%、15天归因窗口','未披露联盟销售占比及实际合作人数'],['睡眠主题内容',url('Sleep Week 2026','https://www.sheex.com/community/betweenthesheex/what-is-sheex-sleep-week')+'；围绕睡眠知识和习惯发布内容','没有活动新增销量证明'],['Google广告历史案例',url('Wpromote / Google案例PDF','https://www.wpromote.com/wp-content/uploads/2020/06/Google_Partner-Case-Study-_-SHEEX-2019-1-2.pdf')+'；介绍Shopping智能出价与非品牌搜索自动化','案例未列明确统计期；不是当前渠道份额']]),['sheex_affiliate','sheex_sleepweek','sheex_ads'])
record('sheex_channelgap','sheex',None,3,0,'渠道销售构成与内容效果待补','达人与自营销售占比、直播与短视频销售占比、广告投入、逐条视频转化未取得；暂不从账号粉丝数判断渠道重要性。',['sheex_tiktok','sheex_affiliate'],'缺口','需工具或权限')
record('sheex_top5gap','sheex',None,3,1,'TOP5内容待筛选确认','尚未确认本款商品关联视频候选池与排名口径；需要先展示可获得的点赞/播放数据，再确认研究对象。不将任意5条内容叫作品牌全网TOP5。',['sheex_tiktok'],'缺口','待你确认')
record('sheex_contentgap','sheex',None,3,2,'传播策略判断等待内容研究','已收录账号、联盟与活动入口；尚未逐条研究确认的内容样本，暂不推断哪些形式带来成交或值得模仿。',['sheex_tiktok','sheex_sleepweek'],'缺口','等待前置证据')
record('sheex_timeline','sheex',None,4,0,'公开材料支持的发展节点',table(['时间','事件','依据'],[['2007-08-25','两位篮球教练提出把运动服面料用于床单的想法','官方创始故事；不是工商注册日期'],['2020-09-17新闻稿；9月28日官网发布','宣布与brrr°合作推出Midnight Label系列','产品扩展记录；该技术不自动属于本款Original Performance'],['2026-03-05发布','宣布3月8日开展Sleep Week 2026睡眠主题活动','官方活动文章；不推断销售增长']]),['sheex_company','sheex_midnight','sheex_sleepweek'])
record('sheex_growth','sheex',None,4,1,'历史服务商案例：保留成效及适用范围','Wpromote与Google发布的历史案例称，SHEEX Shopping广告利润同比增加1500%，广告投入产出比从2.25升至4.05；非品牌搜索与Shopping转自动化后，某个付费搜索最佳月收入同比增加932.54%。案例未披露具体统计期间、利润定义与完整基数，且属于服务商自述，不能当作当前品牌增长率或独立因果证明。',['sheex_ads'],'品牌宣称','品牌自述')
for metric,v,u,sc in [('展示活动价',194.35,'USD','亮白 Queen四件套'),('页面划线价',299,'USD','亮白 Queen四件套；非历史成交价证据'),('评分',4.735064,'/5','官网商品评价汇总'),('评价数量',6896,'条','该商品评价，非全品牌')]:obs('sheex-sheets',metric,v,u,'亮白 / Queen / 四件套',sc,'sheex_product')

# Build V1.0 fact reports with direct questions; leave later analysis visibly pending.
for bid,pid,prefix in [('cozy-bliss','cozy-comforter','cozy'),('sheex','sheex-sheets','sheex')]:
 d=newdoc(bid)
 for sec in [5,6]:
  for ti,name in enumerate(server.TOPICS[sec]):
   key=prefix+'_pending_'+str(sec)+'_'+str(ti)
   record(key,bid,None,sec,ti,'等待前置研究：'+name,'本轮先补基础事实。品牌心智、竞争壁垒、增长机制与我方机会，需要基于已确认产品比较、消费者评论和渠道内容继续研究；不以品牌宣称代替分析结论。',[], '缺口','等待前置证据')
   topic(bid,sec,ti,None,[question(key,name,'尚未形成可发布的判断。',keys=[key])],[key],'等待前置研究')
 d['scope']='美国市场；基础事实核查截至2026年11月5日。报价对应具体颜色、尺寸和渠道；品牌宣称与分析结论分开保存。'
 d['sections'][0]['headline']='品牌背景、销售入口与产品布局'
 d['sections'][1]['headline']='指定研究产品的价格、规格与平台表现'
 d['sections'][2]['headline']='已确认的账号与公开渠道动作'
 d['sections'][3]['headline']='可追溯的发展节点'
 d['sections'][4]['headline']='品牌竞争力：等待前置研究'
 d['sections'][5]['headline']='对Breescape的机会：等待研究验证'

d=docs['cozy-bliss'];d['summary']='Cozy Bliss经营毯、被、床单和枕等家纺产品，官网、Amazon与TikTok均有销售入口。本轮指定研究对象为Amazon灰蓝双面凉感被；其规格、价格与平台表现已收录，消费者判断和增长原因等待进一步研究。';d['summary_record_ids']=[rr[x] for x in ['cozy_brand','cozy_channels','cozy_identity','cozy_performance']]
d['profile']=[{'label':a,'value':b,'detail':'','record_ids':[rr[k]]} for a,b,k in [('主要产品','毯、被、床单与枕','cozy_brand'),('关联企业','Sunwin','cozy_owner'),('销售入口','官网 / Amazon / TikTok','cozy_channels'),('研究款','灰蓝双面凉感被','cozy_identity')]]
topic('cozy-bliss',1,0,None,[question('cozy-brand','品牌是谁，主要服务什么需求？','品牌以柔软与居家舒适介绍其产品；2018年创于纽约为品牌自述。',keys=['cozy_brand','cozy_owner'],tables=['cozy_brand']),question('cozy-owner','品牌与Sunwin是什么关系？','集团官网将其列为自有品牌；加拿大历史商标申请也可追溯至Sunwin。',keys=['cozy_owner'],note='不把集团成立时间、收入与品牌本身混用。')],['cozy_brand','cozy_owner'])
topic('cozy-bliss',1,1,None,[question('cozy-channels','在哪些渠道销售？',keys=['cozy_channels'],tables=['cozy_channels']),question('cozy-scale','销售规模多大，哪个渠道贡献最大、增长最快？','尚未找到足以回答的可靠公开数字。',keys=['cozy_scalegap'])],['cozy_channels','cozy_scalegap'])
topic('cozy-bliss',1,2,None,[question('cozy-matrix','产品覆盖哪些品类和价格带？','官网可见多条凉感被系列，并销售床单、抱枕和电热毯。',keys=['cozy_matrix'],tables=['cozy_matrix'],note='下表为官网各系列不同规格的报价范围，含促销；不能直接用于同规格比价。'),question('cozy-contribution','依靠单一爆款，还是多品类贡献收入？','产品布局为多品类；各品类与核心单品的销售贡献尚不清楚。',keys=['cozy_matrixgap'])],['cozy_matrix','cozy_matrixgap'])
topic('cozy-bliss',2,0,'cozy-comforter',[question('cozy-product','具体研究哪款产品？',keys=['cozy_identity'],tables=['cozy_identity']),question('cozy-market','卖多少钱，页面显示怎样的市场表现？',keys=['cozy_performance'],tables=['cozy_performance']),question('cozy-value','商品给消费者什么购买理由？','面向怕热、夜间出汗人群，主推双面凉感、丝滑轻薄与可机洗。降温参数和认证表述仍属于商家宣称。',keys=['cozy_claim']),question('cozy-other','官网相似商品能否作为同款合并？','目前不能：材料表述与凉感参数不同，需要保留独立身份。',keys=['cozy_identityrisk'],tables=['cozy_identityrisk'])],['cozy_identity','cozy_performance','cozy_claim','cozy_identityrisk'])
topic('cozy-bliss',2,1,'cozy-comforter',[question('cozy-reviews','消费者认可什么、不认可什么，为什么购买？','尚未取得可分析的文字评论样本。已收录评分及数量，不据此生成主题占比或购买原因。',keys=['cozy_reviewgap'])],['cozy_reviewgap'],'资料待补')
topic('cozy-bliss',2,2,'cozy-comforter',[question('cozy-success',q,'等待评论、竞争比较与渠道成交资料。',keys=['cozy_causegap']) for q in ['产品为什么卖得好，消费者为什么购买？','相比同类产品，真正领先在哪里？','销量背后的主要驱动因素是什么？']],['cozy_causegap'],'等待前置研究')
topic('cozy-bliss',3,0,None,[question('cozy-accounts','有哪些官方关联账号，规模如何？',keys=['cozy_accounts'],tables=['cozy_accounts']),question('cozy-actions','已经能查到哪些具体渠道动作？',keys=['cozy_actions'],tables=['cozy_actions']),question('cozy-channel-mix','达人、自营、直播与短视频各贡献多少？','尚未取得可靠占比与转化数据，发布频率也未完成统计。',keys=['cozy_channelgap'])],['cozy_accounts','cozy_actions','cozy_channelgap'])
topic('cozy-bliss',3,1,None,[question('cozy-top5','本款的TOP5相关内容是哪些？','待形成候选清单并确认后开展研究。',keys=['cozy_top5gap'])],['cozy_top5gap'],'待你确认')
topic('cozy-bliss',3,2,None,[question('cozy-content','内容在建立什么认知，哪些形式值得学习？','等待确认的内容样本与效果资料，暂不下结论。',keys=['cozy_contentgap'])],['cozy_contentgap'],'等待前置研究')
topic('cozy-bliss',4,0,None,[question('cozy-history','有哪些可以核查的重要发展节点？',keys=['cozy_timeline'],tables=['cozy_timeline'])],['cozy_timeline'])
topic('cozy-bliss',4,1,None,[question('cozy-growth','哪些动作推动了增长，增长方式怎样变化？','目前有事件记录，但缺乏事件前后的经营数据，尚不能确认增长效果。',keys=['cozy_growthgap'])],['cozy_growthgap'],'等待前置研究')

d=docs['sheex'];d['summary']='SHEEX将运动服面料的弹性、柔软与透气排湿用于床品，并发展出床单、被、枕和睡衣等系列。本轮以Original Performance经典床单为研究对象，已收录官网规格、现价、评价汇总和公开渠道动作；这些事实尚不等于消费者已认可其溢价。';d['summary_record_ids']=[rr[k] for k in ['sheex_brand','sheex_matrix','sheex_identity','sheex_price']]
d['profile']=[{'label':a,'value':b,'detail':'','record_ids':[rr[k]]} for a,b,k in [('创始背景','两位篮球教练','sheex_brand'),('品牌主张','运动性能面料用于床品','sheex_brand'),('主要品类','床单、被、枕与睡衣','sheex_matrix'),('研究款','Original Performance床单','sheex_identity')]]
topic('sheex',1,0,None,[question('sheex-brand','品牌如何起步，提供什么价值？','官网将品牌想法追溯到2007年：把运动服面料用于床单，围绕舒适睡眠与恢复展开产品设计。',keys=['sheex_brand'],tables=['sheex_brand'])],['sheex_brand'])
topic('sheex',1,1,None,[question('sheex-channels','哪些销售渠道有公开证据？',keys=['sheex_channels'],tables=['sheex_channels']),question('sheex-scale','销售规模、渠道占比和增长情况如何？','未找到可核验的品牌总销售额和渠道份额，不能判断哪个渠道最大或增长最快。',keys=['sheex_scalegap'])],['sheex_channels','sheex_scalegap'])
topic('sheex',1,2,None,[question('sheex-matrix','产品覆盖哪些品类和价格带？',keys=['sheex_matrix'],tables=['sheex_matrix'],note='报价范围含不同规格、颜色和促销，不是同规格横向价格结论。'),question('sheex-contribution','经典床单贡献多少销售？','贡献占比未知；多品类在售不能证明收入均衡。',keys=['sheex_matrixgap'])],['sheex_matrix','sheex_matrixgap'])
topic('sheex',2,0,'sheex-sheets',[question('sheex-product','研究哪一款，套装里有什么？',keys=['sheex_identity'],tables=['sheex_identity']),question('sheex-market','现在多少钱，有多少评价？',keys=['sheex_price'],tables=['sheex_price']),question('sheex-value','产品提供什么设计与服务？','产品采用87%聚酯纤维与13%氨纶，并使用弹力包边。品牌主推柔软、透气排湿与温度调节；功能效果尚未独立验证。',keys=['sheex_claim'],note='退换专页写60晚，配送页仍写30天；Final Sale等有例外。售后表述差异已保留，待品牌进一步确认。')],['sheex_identity','sheex_price','sheex_claim'])
topic('sheex',2,1,'sheex-sheets',[question('sheex-reviews','消费者认可、不认可和真实购买理由是什么？','原文评论样本尚未建立，暂不使用官网自动摘要代替研究。',keys=['sheex_reviewgap'])],['sheex_reviewgap'],'资料待补')
topic('sheex',2,2,'sheex-sheets',[question('sheex-success-'+str(i),q,'等待消费者评论、竞争比较与渠道事实。',keys=['sheex_causegap']) for i,q in enumerate(['产品为什么卖得好，消费者为什么购买？','相比同类产品，真正领先在哪里？','销量背后的主要驱动因素是什么？'])],['sheex_causegap'],'等待前置研究')
topic('sheex',3,0,None,[question('sheex-accounts','有哪些官方账号，公开规模如何？',keys=['sheex_accounts'],tables=['sheex_accounts']),question('sheex-actions','已查到哪些推广与营销动作？',keys=['sheex_actions'],tables=['sheex_actions']),question('sheex-channel-mix','达人、自营、直播与短视频各贡献多少？','销售构成、逐条内容转化和持续发布频率尚未取得。',keys=['sheex_channelgap'])],['sheex_accounts','sheex_actions','sheex_channelgap'])
topic('sheex',3,1,None,[question('sheex-top5','TOP5内容研究对象是哪些？','待形成候选清单并确认。',keys=['sheex_top5gap'])],['sheex_top5gap'],'待你确认')
topic('sheex',3,2,None,[question('sheex-content','内容在建立什么认知，哪些形式有效？','等待完整内容样本与相应效果资料。',keys=['sheex_contentgap'])],['sheex_contentgap'],'等待前置研究')
topic('sheex',4,0,None,[question('sheex-history','哪些发展节点有原始材料支持？',keys=['sheex_timeline'],tables=['sheex_timeline'])],['sheex_timeline'])
topic('sheex',4,1,None,[question('sheex-growth','已有增长案例能说明什么？','历史服务商案例记录了Google Shopping与非品牌搜索的自动化投放，但未披露完整统计期间，不能作为当前品牌增长率。',keys=['sheex_growth'],note='案例自述：Shopping广告投入产出比2.25→4.05；其利润与收入增幅仅适用于案例对应广告范围，不代表品牌整体。')],['sheex_growth'])

# Preserve all existing Shilucheng report content; populate only the topper outline.
docs['shilucheng']=json.loads(c.execute('SELECT document FROM brand_reports WHERE brand_id="shilucheng"').fetchone()[0])
topic('shilucheng',2,0,'topper',[question('topper-product','研究哪款褥垫，厚度和床垫尺寸分别是什么？',keys=['topper_identity'],tables=['topper_identity']),question('topper-market','价格、销量和评分是多少？',keys=['topper_market'],tables=['topper_market']),question('topper-material','材料与卖点已经确认到什么程度？',keys=['topper_material'],tables=['topper_material']),question('topper-cross','官网有没有可对照的规格？',keys=['topper_cross'],tables=['topper_cross'])],['topper_identity','topper_market','topper_material','topper_cross'])
topic('shilucheng',2,1,'topper',[question('topper-reviews','已有多少评论，是否可以开始消费者研究？','本款1,000条既有有效评论已独立入库，可按星级、日期和关键词查找；本轮先收录原文，尚未做主题与购买理由分析。',keys=['topper_sample'],note='样本混合推荐与最新排序，不能直接代表全部消费者。')],['topper_sample'],'部分回答')
topic('shilucheng',2,2,'topper',[question('topper-success-'+str(i),q,'等待本款评论、竞争比较与渠道资料。',keys=['topper_causes']) for i,q in enumerate(['产品为什么卖得好，消费者为什么购买？','相比同类产品，真正领先在哪里？','销量背后的主要驱动因素是什么？'])],['topper_causes'],'等待前置研究')

# Verified screenshots, placed where they help identify the brand/product.
for key,bid,pid,sec,ti,caption in [('cozy_home','cozy-bliss',None,1,0,'Cozy Bliss官网首屏：当前产品展示与促销入口。'),('cozy_amazon','cozy-bliss','cozy-comforter',2,0,'指定Amazon灰蓝Queen款：商品、价格、评分与购买提示。'),('sheex_home','sheex',None,1,0,'SHEEX官网首页：品牌和产品入口。'),('sheex_product','sheex','sheex-sheets',2,0,'SHEEX经典床单商品页；报价以正文核对的颜色与尺寸为准。')]:
 f=ROOT/'data/attachments'/f'{key}_20261105.png'
 if not f.exists():continue
 mid=source(key+'_shot','截图｜'+caption,publisher=bid,typ='页面截图',summary=caption,local='attachments/'+f.name);link(mid,bid,pid,sec,server.TOPICS[sec][ti]);fig=dict(material_id=mid,source_id=sources[key],caption=caption)
 t=next(t for t in docs[bid]['sections'][sec-1]['topics'] if t['topic']==server.TOPICS[sec][ti] and t.get('product_id')==pid)
 t['questions'][0]['figures']=[fig]
 if sec==1:docs[bid]['cover_figure']=fig;t['questions'][0]['figures']=[]

# Finish identity, observations, report references and audit log in one transaction.
c.execute('UPDATE brands SET website=?,note=? WHERE id=?',('https://cozybliss.com','基础事实已收录；品牌规模、消费者研究及增长判断待补','cozy-bliss'))
c.execute('UPDATE brands SET note=? WHERE id=?',('基础事实已收录；历史案例与当前经营分开记录','sheex'))
images={'topper':'https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/190e24cb006a417cb22cdb266ecc0d9f~tplv-fhlh96nyum-crop-webp:800:800.webp?dr=12190&t=555f072d&ps=933b5bde&shp=c940a200&shcp=9b759fb9&idc=useast5&from=3376456192','cozy-comforter':'https://m.media-amazon.com/images/I/71DsyhWMb+L._AC_SX679_.jpg','sheex-sheets':'https://www.sheex.com/cdn/shop/files/SHEEX_PDP_OP-SheetSets-BrightWhite-1.jpg?v=1780599989'}
for pid,img in images.items():c.execute('UPDATE products SET image_url=?,state=? WHERE id=?',(img,'基础事实已收录 · 分析待开展',pid))
for bid,d in docs.items():
 for s in d['sections']:
  rev=reports.section_revision(c,bid,s['number']);s['reviewed_revision']=rev;s['updated_at']=NOW;s.pop('current_revision',None);s.pop('stale',None)
 d['reviewed_revisions']={str(s['number']):s['reviewed_revision'] for s in d['sections']};d['updated_at']=NOW;d.pop('summary_stale',None)
 # every question id must be unique in the report
 qs=[q for s in d['sections'] for t in s['topics'] for q in t.get('questions',[])];seen={}
 for q in qs:
  n=seen.get(q['id'],0);seen[q['id']]=n+1
  if n:q['id']+='-'+str(n)
 c.execute('INSERT INTO brand_reports VALUES(?,?,?) ON CONFLICT(brand_id) DO UPDATE SET document=excluded.document,updated_at=excluded.updated_at',(bid,json.dumps(d,ensure_ascii=False),NOW))
c.execute('INSERT INTO events(action,detail,created_at) VALUES(?,?,?)',('补充其他竞品基础事实',json.dumps({'brands':['cozy-bliss','sheex'],'products':['topper','cozy-comforter','sheex-sheets'],'new_records':len(added),'new_topper_reviews':result,'analysis':'尚未开展；需要确认的TOP5及工具缺口保留'},ensure_ascii=False),NOW))
# Integrity: precise product identity and unchanged old review sample.
assert c.execute('SELECT count(*) FROM reviews WHERE product_id="sheets"').fetchone()[0]==1628
assert c.execute('SELECT count(*) FROM reviews WHERE product_id="topper"').fetchone()[0]==1000
assert not c.execute('PRAGMA foreign_key_check').fetchall()
for rid in added:
 r=c.execute('SELECT * FROM records WHERE id=?',(rid,)).fetchone()
 for mid in json.loads(r['evidence']):assert c.execute('SELECT 1 FROM material_links WHERE material_id=? AND brand_id=? AND section=? AND topic=? AND product_id IS ?',(mid,r['brand_id'],r['section'],r['topic'],r['product_id'])).fetchone()
c.commit()
summary={'published_at':NOW,'records_added':len(added),'source_keys':sources,'record_keys':rr,'review_import':result};(W/'published.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps({'records_added':len(added),'sources':len(sources),'review_import':result},ensure_ascii=False))
