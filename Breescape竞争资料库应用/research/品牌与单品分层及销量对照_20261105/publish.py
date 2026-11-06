import sys,pathlib,json,shutil,sqlite3,re
W=pathlib.Path(__file__).parent;ROOT=W.parents[1];sys.path.insert(0,str(ROOT));import server,reports
now=server.now();OUT=W/'published.json'
if OUT.exists():raise SystemExit('Already published; use a targeted revision instead.')
A=ROOT/'data/attachments';facts={};keys={}
for name in ['shilucheng','ldc','cgk']:
 d=json.loads((W/(name+'_data.json')).read_text());p=d['product_info'];m=json.loads((W/(name+'.meta.json')).read_text())
 white=[s for s in p['skus'] if 'Queen' in [v['prop_value'] for v in s['sku_sale_props']] and any('White' in v['prop_value'] for v in s['sku_sale_props'])]
 facts[name]={'url':m['url'],'retrieved_at':m['retrieved_at'],'product_id':p['product_id'],'sold_count':p['sold_count'],'sold_count_note':p['sold_count_note'],'review_header':p.get('review'),'review_summary':d.get('review_info',{}),'white_queen_skus':white,'merchant_description':[b.get('text') or b.get('content') for b in p['desc_blocks'] if b.get('text') or b.get('content')]}
# Save exact selected fields and full originals locally for reproducible checking.
brief={k:{a:v for a,v in d.items() if a!='review_summary'} for k,d in facts.items()}
file='三款TikTok床单_销量规格与商家表达_20261105.json';(A/file).write_text(json.dumps(brief,ensure_ascii=False,indent=2))
notes='''# 三款床单：本次核查口径

2026年11月5日15:20—15:22（北京时间）直接读取三个TikTok美国商品页面及页面公开数据。未登录会话报价，不等于用户账号的券后结算价。来源商品ID与URL见JSON附件。

- Shilucheng：435,716件；白色Queen四件套42.89美元、六件套45.49美元。
- LDC：14,727件；白色Queen四件套30.99美元。
- CGK：2,603件；白色Queen报价64.99美元。商品图展示平床单、床笠、两个枕套，但没有针对Queen单列包装件数。

TikTok对售出量的原文定义：The number of items sold globally since this item was listed on TikTok Shop excluding items that have been returned.
因此这里是多规格链接上架以来的全球累计售出，扣除了退货，不是美国单市场销量，不是本次报价规格的销量，也不是月销量或订单数。

## 历史与增量

此前11月5日的Chrome插件记录分别为435,505、14,715、2,574。本次原生页面值来源不同、采集时点不同，不能当作统一统计周期的增长。没有可靠日/周/月销量序列，不发布增长率。达人精灵完整分析入口要求先在Amazon页面完成插件登录，本次未取得其历史数据。

## 价格与评分差异

此前Chrome登录页面白色Queen报价为42.37 / 30.99 / 64.49美元。本次公开页面为42.89 / 30.99 / 64.99美元。保存两次记录，不将差额认定为普遍涨价；可能涉及时间或会话优惠，具体原因未确认。

CGK商品顶部评分4.7，评论汇总区域4.6，保留冲突，不取平均、不据此做质量排名。三个链接评论总数为46,195 / 1,655 / 299，均为全球商品链接口径。

## 图片补查

CGK商品第1张图主推摆脱夜间出汗，并标100% Bamboo Rayon；第4张图标平床单、床笠、枕套并展示两只枕套；第5张图展示整圈松紧及信封式枕套开口；第6张图写可机洗、低温烘干。图示组合尚不能替代分尺寸装箱清单。

CGK官网近似系列写适配18英寸，而本TikTok链接商家文字写16英寸；不将官网规格直接移植至本链接。官网来源：https://cgk.com/products/new-bamboo-sheet-set 。LDC商品未披露混纺百分比及具体洗涤水温、烘干条件；买家声称的35/65比例未作为商家已核实信息使用。

## 商家主推理由与消费者实际理由

商家理由根据标题、商品图、详情表述概括。Shilucheng多个卖点并列；LDC详情导语面向怕热人群；CGK主图突出夜间出汗和100%竹源人造丝。它们不是实际消费者购买原因或性能验证结论。
'''
(A/'三款床单_本次核查说明_20261105.md').write_text(notes)
with server.conn() as c:
 def material(key,title,local_path='',url=None,summary='',publisher='TikTok / 商家'):
  mid=c.execute('INSERT INTO materials(title,url,source_type,publisher,published_at,retrieved_at,summary,local_path,access_note) VALUES(?,?,?,?,?,?,?,?,?)',(title,url,'页面核查记录',publisher,'',now,summary,local_path,'具体商品、时间和统计范围随材料保留。')).lastrowid
  c.execute('INSERT INTO material_links(material_id,brand_id,product_id,section,topic) VALUES(?,?,?,?,?)',(mid,'shilucheng','sheets',2,server.TOPICS[2][0]));keys[key]=mid;return mid
 mid=material('snapshot','三款床单｜公开页面销量、规格与商家表达','attachments/'+file,summary='三个具体TikTok商品链接；全球累计售出扣退货；本次公开会话报价。')
 memo=material('memo','三款床单｜销量与增长核查说明','attachments/三款床单_本次核查说明_20261105.md',summary='解释销量口径、报价差异、历史不可直接计算增长及图片补查结果。')
 for i in [0,3,4,5]:
  name=f'CGK_TikTok_商品图_{i+1}_20261105.webp';shutil.copyfile(W/f'cgk_image_{i}.webp',A/name)
  material('cgk_image_'+str(i),['CGK主图｜夜间出汗与100%竹源人造丝','CGK套装图｜平床单、床笠与枕套','CGK结构图｜整圈松紧与信封式枕套','CGK洗护图｜机洗与低温烘干'][[0,3,4,5].index(i)],'attachments/'+name,summary='本TikTok商品链接的原始商家图片。')
 def record(title,body,kind='事实',status='已核实页面信息',topic=None,evidence=None):
  return c.execute('INSERT INTO records(brand_id,product_id,section,topic,title,body,kind,status,evidence,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)',('shilucheng','sheets',2,topic or server.TOPICS[2][0],title,body,kind,status,json.dumps(evidence or [mid,memo]),now)).lastrowid
 market=record('三款TikTok床单：全球累计售出、当前报价与历史差异',notes)
 reason=record('三款床单：商家主推的购买理由', '''| 产品 | 商家主推的购买理由 | 主次与依据 |
| --- | --- | --- |
| Shilucheng 竹混纺凉床单 | 柔软丝滑、凉感透气，并强调价格可接受 | 多个卖点并列。详情分别强调可负担的奢华体验、柔软丝滑、调温吸湿、易护理；暂不认定单一核心概念。 |
| LDC Lux Decor 竹混纺床单 | 让怕热的人睡得更凉爽、更舒服 | 详情导语明确面向怕热人群；柔软丝滑、深床笠、抗皱防褪色为辅助宣传。 |
| CGK Linens 100%竹源人造丝床单 | 减少夜间出汗困扰，获得凉爽睡感 | 主图把摆脱夜间出汗放在首位，同时突出100%竹源人造丝，与混纺材料区分。柔软、轻薄、排湿为辅助宣传。 |

以上是对商家购买理由设计的归纳，不等于消费者实际下单原因，也不代表相关性能已经验证。''','品牌宣称','品牌自述',evidence=[mid,keys['cgk_image_0']])
 growth=record('三款床单：期间销量及增长量待取得','未取得同一统计范围、明确起止时间的日/周/月销量序列。此前插件数字与本次原生页面数字不能直接拼接成增长率。达人精灵完整分析入口需要完成插件登录，当前不发布期间销量或增长量。','缺口','需工具或权限')
 old=c.execute('SELECT body,evidence FROM records WHERE id=51').fetchone()
 lines=old['body'].split('\n');header=next(x for x in lines if x.startswith('| 对比维度'))
 table=header+'\n| --- | --- | --- | --- |\n'+'''| 商家主推的购买理由 | 柔软丝滑、凉感透气、价格可接受；多个卖点并列，未见单一主打概念 | 面向怕热人群，主推凉爽、舒适的睡眠 | 主推减少夜间出汗困扰，以100%竹源人造丝区别混纺 |
| TikTok商品链接累计售出（全球，扣除退货） | 435,716件 | 14,727件 | 2,603件 |
| 期间销量／增长量 | 暂无可靠同周期数据 | 暂无可靠同周期数据 | 暂无可靠同周期数据 |
| 白色双人床（Queen）公开页面价 | $42.89／四件套 | $30.99／四件套 | $64.99／商品图示四件组合，分尺寸件数未单列 |
| 套装内容 | 1张平床单＋1张床笠＋2个枕套 | 1张平床单＋1张床笠＋2个枕套 | 商品图展示平床单、床笠和2个枕套；Queen装箱清单未单列 |
| 面料成分 | 60%竹源人造丝＋40%聚酯 | 竹混纺；未披露比例 | 100%竹源人造丝 |
| 标称床笠包覆与固定 | 松紧包边；侧深约36厘米，可拉伸适配最厚约41厘米床垫 | 深包边，标称适配最厚约41厘米床垫 | 整圈松紧；文字标称适配最厚约41厘米床垫 |
| 枕套与其他结构 | 已核实资料不足以认定独特枕套结构 | 未取得明确开口结构说明 | 商品图明确为信封式开口 |
| 套装选择 | 白色双人床可选四件或六件套；六件套多2个枕套，公开报价高$2.60 | 单人床三件套，双人床四件套 | 多尺寸可选；分尺寸件数未单列 |
| 商家洗护要求 | 冷水轻柔机洗、低温烘干；避免柔顺剂和漂白剂 | 可机洗；具体水温、烘干条件未披露 | 可机洗、低温烘干；本链接未写明水温 |
| 页面评分／全球评价数 | 4.4／46,195条 | 4.4／1,655条 | 顶部4.7、评论区4.6，两处不一致／299条 |
| 已有使用证据 | 928条近期评论中397条肯定柔软、92条不满触感 | 尚未完成可比评论分析及实测 | 尚未完成可比评论分析及实测 |
'''
 body='2026年11月5日15:20—15:22，北京时间。三个TikTok美国商品链接，公开页面同色同尺寸报价；未使用AI生成的摘要作为产品事实。\n\n'+table+'\n销量覆盖各链接全部规格，按平台说明为全球累计售出扣退货，不是美国单市场、Queen规格或期间销量。价格来自未登录公开页面，不包含账号券后条件；先前登录会话报价保留在历史证据中，不据此认定普遍涨价。\n\nCGK套件图明确展示两只枕套、平床单和床笠，但没有按Queen单列包装件数；本表保留这一区别。材料、适配、洗护及主推价值均为商家标注，未做成品性能测试。当前没有可比样本，不能凭单款评论或评分认定三款体验优劣。\n\n床垫适配值16英寸约40.6厘米；Shilucheng侧深14英寸约35.6厘米。CGK官网近似款标称18英寸，与本链接16英寸不同，不混用官网尺寸。历史增长来源、价格差异和图片证据见对应核查说明。'
 ev=list(dict.fromkeys(json.loads(old['evidence'])+[mid,memo]+[keys['cgk_image_'+str(i)] for i in [0,3,4,5]]))
 c.execute('UPDATE records SET title=?,body=?,evidence=?,updated_at=? WHERE id=51',('三款床单对照：购买理由、平台销量、价格、材料与设计',body,json.dumps(ev),now))
 sh=facts['shilucheng'];obsvals=[('累计售出','435716','件','商品链接全部规格','全球累计售出，扣除退货，不是美国单市场或期间销量'),('公开页面价','42.89','USD','白色 / Queen / 四件套','未登录公开页面报价，非账号券后结算价'),('公开页面价','45.49','USD','白色 / Queen / 六件套','未登录公开页面报价，非账号券后结算价')]
 for metric,val,unit,variant,scope in obsvals:
  c.execute('INSERT INTO observations(product_id,metric,value,unit,variant,scope,observed_at,retrieved_at,source_url,source_type,availability,note) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',('sheets',metric,val,unit,variant,scope,sh['retrieved_at'],now,sh['url'],'平台公开页面','已核实页面信息','本次核查原始字段及链接见三款床单JSON附件；保留历史观察记录。'))
 # Product-specific prose is referenced rather than duplicated into separate stores.
 for bid in ['shilucheng','cozy-bliss','sheex']:
  d=json.loads(c.execute('SELECT document FROM brand_reports WHERE brand_id=?',(bid,)).fetchone()[0]);s2=d['sections'][1]
  if bid=='shilucheng':
   d['summary']='Shilucheng经营床单、褥垫、毯等家纺，已进入TikTok、Amazon、Walmart与独立站。本库分别研究竹混纺凉床单和仿羽绒凉感褥垫；品牌整体经营判断与各单品的消费者反馈、竞争比较分开呈现。'
   d['scope']='品牌总览覆盖六大板块；单品的规格、评论、畅销原因、关联视频与机会放在独立产品报告。价格和销量各自保留观察时间与口径，两个产品的评论与结论不混用。'
   d['profile'][3]={'label':'已纳入研究的产品','value':'凉床单与凉感褥垫','detail':'两个商品链接各有独立报告、评论和研究记录。','record_ids':[7,77]}
   d['summary_record_ids']=list(dict.fromkeys(d['summary_record_ids']+[77]))
   s2['headline']='床单与褥垫各自研究，消费者体验与增长原因分别判断';s2['summary']='这里先看两款商品的定位与表现；进入单品报告，可查看对应规格、评论、竞争对照和研究结论。'
   d['sections'][2]['headline']='品牌拥有多个社交入口；已完成的内容研究集中在床单'
   d['sections'][2]['summary']='公开账号信息与渠道结构在这里汇总。已确认的五条高点赞素材关联竹混纺床单，其内容研究与视频入口放在床单报告，不能代表褥垫的推广方式。'
   for t in d['sections'][2]['topics'][1:]:t['scope_product_id']='sheets'
   d['sections'][5]['headline']='现有机会线索来自床单研究，尚不外推为整个品牌的增长机制'
   d['sections'][5]['summary']='床单研究提示，可以继续验证柔软、凉感与洗后体验的实际改善，是否足以让已买同类产品的消费者换购。相关竞争条件、反例和机会验证要求保留在床单报告。褥垫尚未形成相应判断。'
   for t in d['sections'][5]['topics']:t['scope_product_id']='sheets'
   for t in s2['topics']:
    if t['product_id']=='sheets' and t['topic']==server.TOPICS[2][0]:
     t['record_ids']=list(dict.fromkeys(t['record_ids']+[market,reason,growth]))
     for q in t.get('questions',[]):
      if q['id']=='product-identity':
       q['answer']='[Shilucheng竹混纺凉床单套装]('+sh['url']+')，TikTok美国站商品链接。11月5日公开页面累计售出435,716件；平台口径为全球累计、扣除退货、覆盖该链接全部规格。'
       for tb in q.get('tables',[]):tb['purpose']='support';tb['caption']='历史选规格价格记录（保留原观察日期）'
      elif q['id']=='product-concept':q['answer']='商家同时强调柔软丝滑、凉感透气、价格可接受及深床笠，暂未见主次清晰的单一核心概念。消费者实际为什么购买，另见评论与畅销原因研究。'
      elif q['id']=='product-comparison':q['answer']='三款链接均主打凉爽与柔软，本款当前累计售出更多，但不是最低报价；CGK强调100%竹源人造丝。本表同时比较购买理由、销量、价格、材料、结构和洗护，不能仅凭卖点判断领先。'
    if t['product_id']=='sheets' and t['topic']==server.TOPICS[2][2]:
     for q in t.get('questions',[]):
      if q['id']=='success-advantage':q['tables']=[dict(record_id=51,mode='table',purpose='support',layout='comparison',caption='核对三款购买理由、全球累计售出与公开报价')]
   d['product_reports']={
    'sheets':{'summary':'柔软是近期评论中最常被具体称赞的体验；凉感与合适的价格触发了部分买家的购买。已有证据能解释部分选择与再次购买，但尚不能解释全部累计销量差距。','merchant_reason':{'headline':'柔软丝滑、凉感透气，价格也能接受','structure':'多个卖点并列，尚未见单一核心概念','detail':'商家同时强调可负担的奢华体验、吸湿和深床笠','basis':'依据商品标题及详情的四组表达：可负担的奢华体验、柔软丝滑、调温吸湿、易护理。这里概括商家的购买理由设计，不等于已验证的消费者动机。','record_ids':[reason]},'key_facts':[{'label':'白色双人床四件套','value':'$42.89','detail':'11月5日公开页面价；非账号券后价'},{'label':'TikTok链接累计售出','value':'435,716件','detail':'全球、全部规格，扣除退货；11月5日'},{'label':'面料标注','value':'60%＋40%','detail':'60%竹源人造丝＋40%聚酯'}],'pending':['同口径期间销量与增长量尚未取得；达人精灵完整分析需插件登录。','已确认的TOP5只代表此商品相关视频的五个研究样本，不能代表全平台带货TOP5。']},
    'topper':{'summary':'这是一款放在床垫上增加柔软度的填充褥垫，可选不同厚度。页面同时宣传凉感与透气，但表层材料表述存在差异，实际体验与竞争优势还需本款评论和同类比较支持。','merchant_reason':{'headline':'给床垫增加蓬松软垫，同时强调透气与凉感','structure':'加软、凉感、透气等多个卖点并列','detail':'尚不认定其中一个已形成独占的产品概念','record_ids':[79]},'key_facts':[{'label':'灰色双人床 · 厚约5厘米','value':'$41.90','detail':'Queen / 2英寸；11月5日页面活动价'},{'label':'TikTok链接累计售出','value':'约7.08万件','detail':'全部规格累计；11月5日页面展示'},{'label':'厚度可选','value':'约5 / 7.6厘米','detail':'2 / 3英寸；不同于适配床垫厚度'}],'pending':['本款1,000条既有评论已独立收录；主题占比和实际购买理由待分析。','本款视频样本尚未确认，不套用床单的五条视频。','同规格竞品比较、畅销原因及机会尚未完成。']}}
  elif bid=='cozy-bliss':
   d['product_reports']={'cozy-comforter':{'summary':'本报告对应Amazon灰蓝色Queen经典凉感被。双面凉感是商家主要概念；价格、材料与评分已核实，实际购买原因和竞争领先程度等待评论与同类比较。','merchant_reason':{'headline':'为怕热、夜间出汗的人提供双面凉感被','structure':'主打双面凉感','detail':'以接触凉感指标、丝滑轻薄和可机洗辅助说明','record_ids':[91]},'key_facts':[{'label':'灰蓝色双人被（Queen）','value':'$69.99','detail':'约229×229厘米；11月5日'},{'label':'Amazon近一个月购买提示','value':'50+','detail':'门槛提示，非精确月销量'},{'label':'页面综合评分','value':'4.5 / 5','detail':'2,731个评分，不等于文字评论数'}],'pending':['消费者评论原文与同条件竞争比较待补。','TOP5研究样本尚未确认，不发布转化或畅销原因。']}}
   s2['headline']='经典双面凉感被：查看独立的产品与消费者研究';s2['summary']='品牌整体产品布局见第一板块，指定Amazon商品的详细研究从下方进入。'
  else:
   d['product_reports']={'sheex-sheets':{'summary':'Original Performance经典性能床单采用聚酯与氨纶面料。商家强调排湿透气和弹力舒适；当前价格可核实，但没有公开销量，不能由评价数倒推经营规模。','merchant_reason':{'headline':'通过透气排湿的性能面料，减少闷热、保持干爽舒适','structure':'主打性能面料带来的睡眠舒适','detail':'柔软、四向弹力与温度调节为辅助表达','record_ids':[107,109]},'key_facts':[{'label':'亮白双人床四件套','value':'$194.35','detail':'Queen；11月5日官网活动价'},{'label':'官网销量','value':'未公开','detail':'不从评价数量推算销量'},{'label':'面料标注','value':'87%＋13%','detail':'87%聚酯＋13%氨纶'}],'pending':['评论样本、真实付费理由及同价位竞争比较待补。','渠道内容研究对象尚未确认。']}}
   s2['headline']='经典性能床单：查看独立的产品与消费者研究';s2['summary']='本款规格、价格与品牌宣传单独呈现，消费者实际购买理由等待原文研究。'
  for s in d['sections']:
   s['reviewed_revision']=reports.section_revision(c,bid,s['number']);s['updated_at']=now
  d['reviewed_revisions']={str(s['number']):s['reviewed_revision'] for s in d['sections']};d['updated_at']=now
  c.execute('UPDATE brand_reports SET document=?,updated_at=? WHERE brand_id=?',(json.dumps(d,ensure_ascii=False),now,bid))
 keys.update(market_record=market,reason_record=reason,growth_record=growth)
OUT.write_text(json.dumps(keys,ensure_ascii=False,indent=2));print(json.dumps(keys,ensure_ascii=False))
