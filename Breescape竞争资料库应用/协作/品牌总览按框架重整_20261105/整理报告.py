from pathlib import Path
import json,sys,copy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import report_framework as F
BASE=Path(__file__).parent
D=json.loads((BASE/'修改前报告.json').read_text())
OLD=copy.deepcopy(D)
def topic(b,n,pid=None):
 return next(t for s in D[b]['sections'] for t in s['topics'] if F.topic_number(t['topic'])==n and (n not in [4,5,6] or t['product_id']==pid))
def oldq(b,n,qid,pid=None):
 return copy.deepcopy(next(q for s in OLD[b]['sections'] for t in s['topics'] if F.topic_number(t['topic'])==n and (n not in [4,5,6] or t['product_id']==pid) for q in t.get('questions',[]) if q['id']==qid))
def q(b,n,key,answer='',refs=None,pid=None,presentation=None,status='已回答',**kw):
 x={'id':F.question_id(b,pid,n,key),'framework_key':key,'title':dict(F.QUESTIONS[n])[key],'answer':answer,'record_ids':refs or [],'answer_status':status,**kw}
 x['presentation']=presentation or ('fact' if n in [1,2,3,4,7,10] else 'answer')
 if status=='资料不足' and presentation is None:x['presentation']='pending'
 return x
def table(rid,caption=None,purpose='core',**kw):
 return {'record_id':rid,'mode':'table','purpose':purpose,**({'caption':caption} if caption else {}),**kw}
def setqs(b,n,qs,pid=None):
 if n in [4,5,6] and pid is None:pid=next(p for p in D[b]['product_reports'] if qs[0]['id'].startswith(b+'-'+p+'-'+str(n)+'-'))
 t=topic(b,n,pid);t['questions']=qs;t['finding']='';t['featured']=[];t['bullets']=[]
 t['record_ids']=list(dict.fromkeys(t['record_ids']+[r for z in qs for r in z.get('record_ids',[])]))
 t['coverage']='已回答' if all(z.get('answer_status')=='已回答' for z in qs) else '部分回答'
 if all(z.get('answer_status')=='资料不足' for z in qs):t['coverage']='资料待补'
 t['gap']='；'.join(z['title']+'：'+z.get('answer','') for z in qs if z.get('answer_status')=='资料不足')
for b,d in D.items():
 d['framework_version']=F.VERSION
 for s in d['sections']:
  s['summary']=''
  for t in s['topics']: t.pop('scope_product_id',None)
# 第一板块：事实按字段组织；成立时间、定位、目标与差异化不混答。
b='shilucheng'
setqs(b,1,[q(b,1,'background','品牌创立年份未查实。Amazon卖家自述公司成立于2003年；SHILUCHENG美国商标于2016年申请、2017年注册。',[2,28,44],status='部分回答'),q(b,1,'business','床单、褥垫、被、毯、枕等家纺；官网目录还销售窗帘、地毯和浴室垫。',[1,34]),q(b,1,'position','让家庭以负担得起的价格买到舒适床品。官网以材料选择和减少中间商解释这一主张。',[1,50]),q(b,1,'target','面向重视睡眠舒适、同时在意价格的家庭；凉感床单另面向怕热、夜间出汗的人群。实际买家构成未核实。',[3]),q(b,1,'difference','希望消费者记住“舒适而且买得起”。现有资料能确认品牌想传递的价值，尚不能证明消费者认为它比其他品牌更有优势。',[3,50],status='部分回答')])
setqs(b,2,[q(b,2,'scale','尚未取得可靠的品牌总销售额及增长数据。',[4,30,49],status='资料不足'),q(b,2,'channels','已确认官网、TikTok、Amazon、Walmart四类线上入口；各渠道销售额与占比未公开。',[29,4],tables=[table(29,'已确认的销售入口',columns=[0,1])],status='部分回答'),q(b,2,'main','尚无同期间跨渠道销售数据，不能确认销售主力。',[4],status='资料不足'),q(b,2,'growth','尚无可比的渠道销售时间序列，不能确认哪个渠道增长最快。',[4,49],status='资料不足')])
qs=[]
for key,oid in [('matrix','product-matrix'),('contribution','product-contribution'),('structure','product-dependence')]:
 z=oldq(b,3,oid);z.pop('id');z.pop('title');z['answer_status']='部分回答';qs.append(q(b,3,key,**{('refs' if k=='record_ids' else k):v for k,v in z.items()}))
qs[1]['answer']='同一TikTok店铺已观察的四款商品中，竹混纺凉床单的累计售出约43.55万件，最多；它占品牌销售额的比例尚不清楚。'
setqs(b,3,qs)
b='cozy-bliss'
setqs(b,1,[q(b,1,'background','品牌Facebook自述2018年创于纽约。Sunwin官网将Cozy Bliss列为自有品牌；2020年加拿大商标申请人为上海尚佰。',[83,84],status='部分回答'),q(b,1,'business','毯、被、床单、枕等居家纺织品；另有电热产品和宠物用品。',[83]),q(b,1,'position','以柔软触感和居家舒适为主要表达，让使用者放松、感到自在。',[83]),q(b,1,'target','品牌面向居家舒适需求；凉感产品特别面向睡眠怕热、夜间出汗的人群。实际顾客构成未核实。',[83]),q(b,1,'difference','品牌希望与舒适、柔软的居家体验建立联系；尚未查到足以证明其独特消费者认知的材料。',[83],status='部分回答')])
setqs(b,2,[q(b,2,'scale','尚未找到可靠的品牌销售额及增长数据。',[86],status='资料不足'),q(b,2,'channels','官网、Amazon、TikTok有销售入口；另有历史快闪活动。各渠道销售额和占比未取得。',[85,86],tables=[table(85,'销售渠道及已知经营信息')],status='部分回答'),q(b,2,'main','尚无跨渠道销售数据，不能确认销售主力。',[86],status='资料不足'),q(b,2,'growth','尚无同期间渠道增长数据。',[86],status='资料不足')])
setqs(b,3,[q(b,3,'matrix','凉感被分Cloud-Like、Outlast、Sorona和Tencel等系列，并销售凉感床单、抱枕、电热毯和盖毯。',[87],tables=[table(87,'主要系列与官网展示价格（美元）')],note='2026年11月5日；范围包含不同尺寸和颜色，不代表同规格价差。'),q(b,3,'contribution','核心单品的可比销量、销售额和品牌销售贡献尚未取得；指定凉感被的Amazon表现见第二板块。',[88],status='部分回答'),q(b,3,'structure','产品布局覆盖多个品类；缺少收入分布，尚不能判断是否依赖单一爆款。',[88],status='部分回答')])
b='sheex'
setqs(b,1,[q(b,1,'background','官网将创业起点追溯至2007年8月25日：两位篮球教练Michelle Marciniak与Susan Walvius提出把运动服面料用于床单。该日期为品牌故事中的创业起点。',[102]),q(b,1,'business','功能性床品和睡衣，覆盖床单、被、枕、床垫保护用品及睡眠配件。',[102]),q(b,1,'position','把运动服面料的柔软、弹性和透气排湿用于睡眠，品牌称为“性能床品”（Performance Bedding）。',[102]),q(b,1,'target','面向希望改善闷热、出汗及睡眠舒适度的人群；实际顾客中运动员等人群的占比未披露。',[102]),q(b,1,'difference','希望消费者记住运动性能面料带来的睡眠舒适。品牌有明确的概念来源；其排他性及消费者认知仍需竞争与消费者研究。',[102],status='部分回答')])
setqs(b,2,[q(b,2,'scale','尚未取得可靠的品牌销售总额及增长率。',[104],status='资料不足'),q(b,2,'channels','官网独立站和Verlo零售商品页有明确入口；品牌还介绍过百货、床垫和家具渠道，当前完整铺货范围与各渠道份额未核实。',[103,104],tables=[table(103,'销售入口与零售渠道')],status='部分回答'),q(b,2,'main','尚无同期间各渠道销售额，不能确认核心渠道。',[104],status='资料不足'),q(b,2,'growth','历史付费搜索案例提供局部增长记录，但不足以比较当前各渠道增长速度。',[104],status='资料不足')])
setqs(b,3,[q(b,3,'matrix','以多系列床单为基础，延伸至被、枕、睡衣和睡眠设备。',[105],tables=[table(105,'主要系列与官网展示价格（美元）')],note='2026年11月5日；包含不同尺寸、颜色及活动价。'),q(b,3,'contribution','经典床单及其他系列销量、销售额和品牌销售贡献未公开。',[106],status='资料不足'),q(b,3,'structure','已确认多品类在售；收入是否集中于经典床单，尚无销售结构数据。',[106],status='部分回答')])
# 后续板块在资料核对后追加；暂存候选，不写入在线数据库。
(BASE/'候选报告.json').write_text(json.dumps(D,ensure_ascii=False,indent=2))
print('第一板块候选已整理')
# 第二板块：四款产品分别回答同一框架，价格/销量不跨平台或规格拼接。
b='shilucheng';p='sheets'
setqs(b,4,[q(b,4,'identity','[Shilucheng竹混纺凉床单套装](https://shop.tiktok.com/us/pdp/bamboo-sheets-set-by-shilucheng-4-6-pc-cooling-deep-pocket-silky-soft/1729438233542234865)；TikTok美国站。白色双人床（Queen）四件套，2026年11月5日公开报价42.89美元。套内为平床单、床笠和两个枕套。',[7,8,133],pid=p,figures=oldq(b,4,'product-identity',p)['figures'],tables=[table(36,'其他规格的历史报价（11月4日）','support')]),q(b,4,'performance','该链接全球累计售出435,716件（扣除退货），评分4.4/5、全球评价46,195条；均覆盖全部规格。销售额及指定期间销量未公开。',[133,135],pid=p,note='2026年11月5日15:20；不等于美国单市场、双人床规格或月销量。',status='部分回答'),q(b,4,'concept','柔软丝滑、凉感透气，并强调价格可接受。商家多个卖点并列，尚未见明确的单一核心概念。',[9,134],pid=p),q(b,4,'difference','与LDC同为竹混纺，本款公开报价更高；CGK以100%竹源人造丝区分混纺。柔软、凉感和深床笠都是三款的宣传重点，本款尚未证明独有的性能优势。',[51,133,134],pid=p,status='部分回答',tables=[table(51,'三款床单对照：购买理由、销量、价格与产品设计',layout='comparison')],note='价格为2026年11月5日公开页面同色同尺寸报价；销量为各链接全球累计、全部规格、扣除退货。')])
t=topic(b,5,p)
over=oldq(b,5,'feedback-overall',p);over['title']='评论整体情况';over['presentation']='plain';over['answer_status']='已回答';over['id']=F.question_id(b,p,5,'overview')
pos=oldq(b,5,'feedback-positive',p);neg=oldq(b,5,'feedback-negative',p)
for z in [pos,neg]:
 z.pop('id');z.pop('title');z['status']='部分回答';z.pop('links',None)
pos['answer']='柔软是最常被具体称赞的体验，其次是温度感受和尺寸适配。认可集中在日常睡感，不能只用“凉感”概括这款产品的价值。';pos['evidence']='397条肯定柔软；这里统计买后体验，不代表首次购买原因。'
neg['answer']='触感粗糙、不够凉或偏热、尺寸不合，是最常见的具体不满。产品需要同时兑现触感、温度和适配承诺。';neg['evidence']='触感不满92条；温度不满72条；尺寸不满38条，与滑脱35条接近。'
setqs(b,5,[over,q(b,5,'positive',pid=p,**{('refs' if k=='record_ids' else k):v for k,v in pos.items()}),q(b,5,'negative',pid=p,**{('refs' if k=='record_ids' else k):v for k,v in neg.items()}),q(b,5,'purchase','已有明确个案表明：为了凉感而买、在价格合适时下单，以及受到视频或他人评价影响。尚不能确定这些理由在全部买家中的比例。',[13,52],pid=p,status='部分回答',evidence='R452、R917明确为凉感购买；R475提到合适价格；R1409提到视频，R1618提到评论。后两条来自补充样本，只作个案。'),q(b,5,'unmet','需要凉爽，也需要柔软；材料与套装还须符合购买时的理解。评论中的落差包括粗糙、不够凉、床笠滑脱，以及误买混纺版本。',[13,53],pid=p,status='部分回答',evidence='R619期待凉感却不能接受粗糙；R718因舒适继续使用但未得到预期凉感；R453介意40%聚酯，R535因原想买纯竹源版本而退货。')],p)
setqs(b,6,[q(b,6,'drivers',refs=[14,54,66,67,69],pid=p,status='部分回答',ordered=True,points=[{'title':'凉感需求给了部分消费者明确的下单理由。','detail':'怕热者不是泛泛地想换床单，而是希望睡得更凉。视频与其他顾客的评价也会形成这种期待。','evidence':'R452、R917明确说为凉感而买；R1409、R1618分别提到视频和评价的影响。'}, {'title':'柔软体验带来了部分追加购买。','detail':'柔软既是常见的买后认可，也出现了明确的再次下单行为，是产品持续销售的一条已见路径。','evidence':'928条近期评论中397条认可柔软；R580明确因手感两次下单，R499试用后又购买五套。'}, {'title':'合适的价格和促销推动了部分顾客决定购买。','detail':'价格影响下单时机；目前对照中本款高于LDC，不能把销售成绩简单归因于最低价。','evidence':'R475原本想试，看到合适价格后购买；R1389等到促销再买。'}, {'title':'达人提供了具体的换购理由，但其销量贡献尚未测出。','detail':'五条已确认素材中，三条用旧床单的不适引出替换，再展示产品与优惠。它们说明传播方式，尚不能证明带来了多少订单。','evidence':'相关素材带佣金标识；尚无作品级订单归因。'}],note='上述顺序按现有证据与决策价值组织，不是销量贡献排名。广告投入、上架时长、品牌偏好和各因素贡献仍未确定。',tables=[{'record_id':67,'mode':'analysis','purpose':'support','caption':'查看价格、产品、概念、营销、渠道、先发等解释的证据核对'}],links=[{'target':F.question_id(b,None,8,'samples'),'label':'查看相关视频'}]),q(b,6,'advantage','目前尚未证实本款在价格、技术或成品性能上领先同类。累计成交更多是经营结果，不能单独作为优势形成原因。',[65,67,68],pid=p,status='部分回答',points=[{'title':'没有最低价优势。','detail':'11月5日白色双人床四件套，本款42.89美元、LDC 30.99美元。'}, {'title':'柔软、凉感与深床笠已有竞争供给。','detail':'本款获得部分消费者认可，但还缺同条件的竞品体验比较。'}, {'title':'四件与六件套提供不同组合选择。','detail':'六件套多两个枕套；11月5日白色双人床公开报价相差2.60美元。尚未证明这种组合独有或构成主要销量来源。'}],links=[{'target':F.question_id(b,p,4,'difference'),'label':'查看完整产品对照'}])],p)
# 其余三款沿用已有核实信息；明确哪些尚未研究，不移植床单结论。
configs=[('shilucheng','topper',[77,78,79,80],131,92),('cozy-bliss','cozy-comforter',[89,90,91,92],128,100),('sheex','sheex-sheets',[107,108,109],130,114)]
for b,p,rs,img,source in configs:
 identities={'topper':'[Shilucheng仿羽绒凉感褥垫](https://shop.tiktok.com/us/pdp/cooling-mattress-topper-by-shilucheng-extra-down-alternative-fill/1729439070512124657)，灰色双人床（Queen）、厚约5厘米，11月5日活动价41.90美元。','cozy-comforter':'[Cozy Bliss经典双面凉感被](https://www.amazon.com/dp/B0BVQMTD8W)，Amazon美国站，灰蓝色双人被（Queen）、约229×229厘米，11月5日价格69.99美元。','sheex-sheets':'[SHEEX Original Performance经典性能床单](https://www.sheex.com/products/original-performance-sheet-set)，官网亮白色双人床（Queen）四件套，11月5日活动价194.35美元。'}
 concepts={'topper':'给床垫增加蓬松柔软，同时宣传透气、凉感与深床笠包覆；多个卖点并列。表层材料的标题与参数不一致，成分比例尚未核实。','cozy-comforter':'面向怕热、夜间出汗人群，主打双面凉感，并以丝滑轻薄、可机洗作为辅助卖点。商家凉感参数尚未独立验证。','sheex-sheets':'以运动服式性能面料提供柔软、弹力、透气排湿的睡感。面料标注为87%聚酯＋13%氨纶。'}
 differences={'topper':'已知可选不同厚度、深床笠和仿羽绒填充；尚未完成同规格竞品对照，不能把这些常见设计认定为独特优势。','cozy-comforter':'尚未完成同价位竞品比较。官网Cloud-Like近似款与本款材料标注、参数不同，不能直接合并为同一商品。','sheex-sheets':'运动面料概念和弹力结构是明确的产品设计；尚未完成同价位床单的材料、价格、实测和消费者选择比较。'}
 diff_tables=[table(rs[3],'官网近似款核对','support')] if len(rs)>3 else []
 setqs(b,4,[q(b,4,'identity',identities[p],rs[:2],pid=p,tables=[table(rs[0],'产品规格与组成')],figures=[{'material_id':img,'source_id':source,'caption':{'topper':'Shilucheng褥垫商品页（11月5日）','cozy-comforter':'Cozy Bliss研究款Amazon商品页（11月5日）','sheex-sheets':'SHEEX经典床单商品页（11月5日）'}[p]}]),q(b,4,'performance','销售额未公开；下表保留平台实际展示的销量或购买提示、评分与评价数量。',rs[:2],pid=p,status='部分回答',tables=[table(rs[1],'销售表现与评价（2026年11月5日）')]),q(b,4,'concept',concepts[p],rs[2:3],pid=p,status='部分回答' if p=='topper' else '已回答',tables=[table(rs[2],'材料说明与商家宣称','support')] if p=='topper' else []),q(b,4,'difference',differences[p],rs,pid=p,status='资料不足',tables=diff_tables)],p)
 review_ref={'topper':81,'cozy-comforter':93,'sheex-sheets':110}[p]
 text='已收录本款1,000条评论，尚未完成逐条主题编码与统计。' if p=='topper' else '尚未取得可分析、可追溯的文字评论样本。'
 setqs(b,5,[q(b,5,k,text+{'positive':'认可主题、TOP3及占比尚未形成。','negative':'不认可主题、TOP3及占比尚未形成。','purchase':'尚不能判断真实购买动因。','unmet':'尚不能判断未满足需求。'}[k],[review_ref],pid=p,status='资料不足') for k,_ in F.QUESTIONS[5]],p)
 sr={'topper':82,'cozy-comforter':94,'sheex-sheets':111}[p]
 setqs(b,6,[q(b,6,'drivers','尚缺本款购买动因、可比销售及渠道效果证据，暂不能确定主要驱动因素。',[sr],pid=p,status='资料不足'),q(b,6,'advantage','尚未完成同规格竞争比较及消费者验证，暂不能认定领先优势。',[sr],pid=p,status='资料不足')],p)
# 产品报告顶部只保留必要事实；详细结论在对应问题回答。
for b,d in D.items():
 for p,m in d.get('product_reports',{}).items():
  m['summary']=''
  m['merchant_reason']['detail']=''
# 修正品牌层的贡献回答，避免把单款月购提示挪成品牌销量。
topic('cozy-bliss',3)['questions'][1]['answer']='核心单品的可比销量、销售额及品牌销售贡献尚未取得；指定凉感被的Amazon表现见第二板块。'
(BASE/'候选报告.json').write_text(json.dumps(D,ensure_ascii=False,indent=2))
print('第二板块候选已整理')
# 第三板块：账号/运营事实与内容研究分别作答；样本选择沿用用户确认结果。
for b,d in D.items():
 if b=='shilucheng':
  z=oldq(b,7,'channel-accounts');z.pop('id');z.pop('title');z['answer']='已确认5个社交账号入口及1个TikTok店铺。TikTok账号[@shiluchenghome](https://www.tiktok.com/@shiluchenghome)显示约3.32万粉丝、12.17万获赞；其他账号见下表。完整账号数量与持续发布频率尚未核实。'
  setqs(b,7,[q(b,7,'accounts',status='部分回答',**{('refs' if k=='record_ids' else k):v for k,v in z.items()}),q(b,7,'affiliate','已见达人佣金推广，也有品牌关联账号。达人和自营的销售额及占比尚未取得。',[16,42],status='部分回答'),q(b,7,'format','尚未取得直播和短视频分别带来的销售额与占比。',[16,42],status='资料不足')])
  z=oldq(b,8,'channel-top5');z.pop('id');z.pop('title');z['answer']='采用已确认的竹混纺凉床单商品页关联视频前五条。下表视频名称可点击播放；点赞数为11月4日页面展示。';z['note']='原帖链接、播放量、评论数与分享数尚未取得。以下是商品相关内容样本，不代表全品牌或全平台TOP5。'
  setqs(b,8,[q(b,8,'samples',status='部分回答',**{('refs' if k=='record_ids' else k):v for k,v in z.items()}),q(b,8,'message','三条通过旧缎面床单不舒适的表达引出换购；两条直接展示柔软、铺床和颜色。它们把抽象的舒适感转成具体使用场景，是可能吸引消费者的表达方式。',[55],status='部分回答',evidence='三条相近结构来自同一作者；这里分析内容说服方式，尚无转化数据验证。'),q(b,8,'conversion','尚未取得这五条作品对应的点击、订单或销售额，不能由点赞数判断实际带货效果。',[17,55,76],status='资料不足')])
  setqs(b,9,[q(b,9,'strategy','已确认的床单内容主要采用“旧床单不适→换成新床单”的对比，以及触摸、铺床和配色展示，并穿插优惠。',[18,56,70],status='部分回答'),q(b,9,'perception','希望建立“更柔软、更凉爽、像酒店床品”的印象。部分达人把混纺床单称为全天然竹床单，与商品成分标注不一致。',[18,56,70],status='部分回答',note='这是内容的传播方向，尚未证明消费者普遍形成同样认知。'),q(b,9,'learn','从一种具体不适切入，展示更换前后的使用差别；材料、规格和优惠须说清楚。',[18,56,70],status='部分回答')])
 else:
  ids=[95,96,97] if b=='cozy-bliss' else [112,113,114]
  acct='cozy-accounts' if b=='cozy-bliss' else 'sheex-accounts'
  setqs(b,7,[q(b,7,'accounts','已确认'+('3' if b=='cozy-bliss' else '5')+'个官方关联社交入口。下表列已见账号与统计；完整账号矩阵、持续发布频率尚未核实。',[ids[0]],status='部分回答',tables=[table(ids[0],'官方关联账号（2026年11月5日）')]),q(b,7,'affiliate',('有品牌关联账号及TikTok店铺；达人合作规模、自营与达人销售占比未取得。' if b=='cozy-bliss' else '品牌设有联盟推广，页面列基础佣金8%、15天归因窗口；自营与联盟销售占比未披露。'),ids[1:],status='部分回答',tables=[table(ids[1],'已确认的运营动作','support')]),q(b,7,'format','尚未取得直播和短视频分别带来的销售额与占比。',[ids[2]],status='资料不足')])
  tr=98 if b=='cozy-bliss' else 115;cr=99 if b=='cozy-bliss' else 116
  setqs(b,8,[q(b,8,'samples','尚未确认本款TOP5研究样本；视频链接、截图、播放和互动数据待补。',[tr],status='资料不足'),q(b,8,'message','待确认视频样本后，逐条分析内容、卖点和吸引消费者的方式。',[tr],status='资料不足'),q(b,8,'conversion','尚未取得作品级订单和销售额。',[tr],status='资料不足')])
  setqs(b,9,[q(b,9,'strategy','已有账号和活动资料，尚未形成覆盖主要内容的策略判断。',[cr],status='资料不足'),q(b,9,'perception','尚未完成渠道内容研究，暂不能判断传播是否集中于某种品牌认知。',[cr],status='资料不足'),q(b,9,'learn','尚未确认值得借鉴的具体内容形式。',[cr],status='资料不足')])
# 第四板块：时间线直接展示；经营动作与增长效果分开。
for b in D:
 if b=='shilucheng':
  z=oldq(b,10,'history-events');z.pop('id');z.pop('title');z['answer']='已核实的商标与公开推广记录如下。产品首发、战略调整和关键渠道进入时间尚不完整。'
  setqs(b,10,[q(b,10,'timeline',status='部分回答',**{('refs' if k=='record_ids' else k):v for k,v in z.items()})])
  setqs(b,11,[q(b,11,'actions','已见材料内容、促销和达人推广，但缺少动作前后的可比销售数据，尚不能确认哪项推动了快速增长。',[20,57],status='资料不足'),q(b,11,'change','早期和近期均有产品宣传与促销记录；资料不足以还原增长方式的变化。',[20,57],status='资料不足')])
 elif b=='cozy-bliss':
  setqs(b,10,[q(b,10,'timeline','已有品牌背景、商标申请及快闪活动公告；重要产品首发与定位调整时间尚未查全。',[100],status='部分回答',tables=[table(100,'已查发展节点')])])
  setqs(b,11,[q(b,11,'actions','快闪、产品扩展等活动有记录，但缺少相应销售变化，尚不能确认增长贡献。',[101],status='资料不足'),q(b,11,'change','尚无连续的渠道及收入资料，不能判断早期至今的增长方式如何变化。',[101],status='资料不足')])
 else:
  setqs(b,10,[q(b,10,'timeline','从运动服面料的创业想法，到新系列和睡眠主题活动，已有以下公开记录。完整的渠道拓展及战略调整时间仍待补。',[117],status='部分回答',tables=[table(117,'已查发展节点')])])
  setqs(b,11,[q(b,11,'actions','历史案例显示，SHEEX与Wpromote采用Google智能出价和搜索广告自动化，同时扩大付费搜索收入并改善广告回报。',[118],status='部分回答',points=[{'title':'Shopping广告回报提高。','detail':'服务商案例称广告投入产出比由2.25升至4.05，Shopping广告利润同比增加1500%。'},{'title':'付费搜索出现收入增长。','detail':'案例称转向自动化后，最佳月份的付费搜索收入同比增加932.54%。'}],note='来源为Wpromote/Google历史案例；统计期、利润定义与基数未完整披露，不作为当前品牌增长率。'),q(b,11,'change','能确认品牌采用过自动化付费获客；缺少早期与现在的渠道收入结构，尚不能判断整体增长方式的转变。',[118],status='资料不足')])
# 第五板块：四个子问题各自作答，不用“等待前置研究”概括替代。
b='shilucheng'
setqs(b,12,[q(b,12,'perception','现有消费者原文主要认可床单的柔软与舒适；尚不足以确定消费者对整个品牌最核心的认知。',[21,58],status='部分回答',review_product_id='sheets'),q(b,12,'value','品牌主张舒适、价格可负担，但这些价值也有其他品牌提供，尚未验证品牌层面的独特价值。',[21,58],status='部分回答'),q(b,12,'pay','已有因使用感受再次购买床单的案例；还没有充分证据证明消费者愿意仅为Shilucheng品牌支付更高价格。',[21,58],status='部分回答',evidence='R580、R499为产品再购个案，不能外推为跨品类品牌忠诚。',review_product_id='sheets'),q(b,12,'mind','尚不能确认形成了稳定的品牌心智。需要消费者主动联想、品牌选择或跨品类购买证据。',[21,58],status='资料不足')])
setqs(b,13,[q(b,13,'factor','单款床单已有销售积累和购买动因证据，但缺少品牌整体经营资料，尚不能确定品牌成功最关键的因素。',[22,59,72],status='资料不足'),q(b,13,'capability','已观察到产品组合、多渠道销售和达人推广的运作；研发、供应链成本及组织效率尚未核实。',[22,59,72],status='部分回答'),q(b,13,'barrier','尚未确认独有技术、成本或品牌壁垒。官网Lab页面的制造自述不足以证明难复制的能力。',[22,59,72],status='资料不足'),q(b,13,'sustain','尚不能判断持续增长能力。当前缺少稳定的产品体验、获客成本、退货后利润和跨产品复制结果。',[22,59,72],status='资料不足')])
for b,refs in [('cozy-bliss',[119,120]),('sheex',[126,127])]:
 for n,rid in [(12,refs[0]),(13,refs[1])]:
  answers={12:['尚缺品牌层面的消费者研究，不能确定最核心认知。','尚缺竞争与消费者验证，不能认定独特价值。','尚缺真实选择及支付意愿证据，不能解释品牌购买和溢价。','尚缺消费者主动联想和稳定选择证据，不能确认品牌心智。'],13:['尚缺品牌整体经营和消费者证据，不能确定关键成功因素。','已见产品与经营活动，但具体研发、供应链、营销或组织能力尚未验证。','尚无足够证据认定难以复制的竞争壁垒。','尚缺连续经营、获客效率及产品复制结果，不能判断持续增长能力。']}[n]
  setqs(b,n,[q(b,n,k,a,[rid],status='资料不足') for (k,_),a in zip(F.QUESTIONS[n],answers)])
# 第六板块：只保留已有研究支持的启示，研究条件收至简短说明。
b='shilucheng'
imp=[('innovation',60,'尚未发现有充分证据支持、值得直接借鉴的独特产品创新。凉感、柔软与贴合应分别验证，避免改善一项却牺牲另一项。'),('marketing',61,'用旧床单的具体不适引出换购，再展示新产品的触感、铺床和适配，形成容易理解的购买理由。'),('weakness',62,'部分达人对材料的表达与商品成分不一致；评论也存在粗糙、不够凉和不同购买间体验不一致的反馈。'),('opportunity',63,'值得验证的是同类凉感床单的换购需求：让已购买但不满意的人，获得更稳定的柔软、凉爽和贴合体验。'),('implication',64,'Breescape应优先证明具体体验比现有选择改善在哪里，再决定产品、价格与传播；不能仅凭对手累计销量大，就复制材料或营销方式。')]
for n,(key,rid,a) in enumerate(imp,14):
 t=topic(b,n);notes={14:'来自产品对照与使用反馈，尚无独特技术或结构创新的验证。',15:'这是对已观察视频结构的借鉴；实际转化效果尚待验证。',16:'这些是样本中已见的问题；普遍程度及形成原因尚未确认。',17:'机会尚未定案：人群规模、改善幅度、支付意愿及获客后利润仍待验证。',18:'客户已有组合、价值展示和小批量测试方向；本研究补充具体竞争证据与消费者落差。'}
 setqs(b,n,[q(b,n,key,a,t['record_ids'],status='部分回答',presentation='plain',note=notes[n])])
for b in ['cozy-bliss','sheex']:
 for n in range(14,19):
  t=topic(b,n);k=F.QUESTIONS[n][0][0]
  setqs(b,n,[q(b,n,k,'尚无足够证据形成这一方向的建议。',t['record_ids'],status='资料不足',presentation='plain')])
# 每个产品仍可独立打开；共享内容在品牌页可完整阅读，不再只保留跳转链接。
for b,d in D.items():
 p=next(iter(d['product_reports']))
 for s in d['sections']:
  for t in s['topics']:
   n=F.topic_number(t['topic'])
   if n in [8,9] or (b=='shilucheng' and n>=14):t['scope_product_id']=p
   t['display_title']={2:'2. 品牌经营规模及渠道结构',3:'3. 产品矩阵及核心产品销量',6:'6. 产品卖得好的原因总结',12:'12. 消费者为什么选择这个品牌？',13:'13. 它为什么能做成，而竞争对手做不到？',14:'值得学习的产品创新',15:'值得模仿的营销及渠道动作',16:'品牌目前的主要短板',17:'潜在市场机会',18:'对我们的战略启示'}.get(n,t['topic'])
   for z in t['questions']:
    if n==10:z['presentation']='plain'
    z['record_ids']=list(dict.fromkeys(z.get('record_ids',[])+[f['record_id'] for f in z.get('tables',[])]))
   t['record_ids']=list(dict.fromkeys(t['record_ids']+[r for z in t['questions'] for r in z.get('record_ids',[])]))
  s['headline']={
   'shilucheng':['以舒适与可负担价格经营多品类家纺','两款产品分别研究：竹混纺凉床单与仿羽绒褥垫','床单的达人内容围绕柔软、凉爽与换购','','床单的体验认可，尚不足以证明品牌壁垒','从同类床单的体验落差寻找换购机会'],
   'cozy-bliss':['Sunwin旗下家纺品牌，以柔软和居家舒适为主要表达','经典双面凉感被，面向怕热与夜间出汗人群','通过官网、平台店铺和社交账号推广家纺产品','','',''],
   'sheex':['把运动服面料的性能概念用于床品','Original Performance：主打弹力与透气排湿','官网销售配合社交传播与联盟推广','从性能床品创业，到材料合作与睡眠主题活动','','']
  }[b][s['number']-1]
 d['summary']={'shilucheng':'Shilucheng以舒适和可负担价格销售床单、褥垫等多类家纺。竹混纺凉床单在TikTok已有较大累计成交；评论显示柔软体验获得较多认可，凉感和合适价格促成部分购买。品牌整体销售结构与长期优势尚未确定。','cozy-bliss':'Cozy Bliss是Sunwin旗下家纺品牌，围绕柔软与居家舒适布局毯、被、床单和枕。官网、Amazon、TikTok均有销售入口；指定的经典双面凉感被主打怕热与夜间出汗需求。','sheex':'SHEEX从运动服面料切入床品，以柔软、弹力、透气排湿建立性能床品概念，产品延伸至被、枕和睡衣。经典Original Performance床单采用聚酯与氨纶面料；品牌溢价及竞争优势仍待消费者验证。'}[b]
 d['scope']='依据竞品品牌研究框架V1.0及用户确认的第6项两问修订。资料观察日期主要为2026年11月4—5日；基础事实、品牌宣称、研究判断分别记录。各产品独立研究，不混用评论与销量。'
 F.validate_document(d)
(BASE/'候选报告.json').write_text(json.dumps(D,ensure_ascii=False,indent=2))
print('六板块候选通过框架校验；共',sum(len(t['questions']) for d in D.values() for s in d['sections'] for t in s['topics']),'个回答位置')
