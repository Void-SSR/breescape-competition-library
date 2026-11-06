from pathlib import Path
import sqlite3,json,shutil,datetime,sys
BASE=Path(__file__).resolve().parents[2]; ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE));import reports,report_framework
c=sqlite3.connect(BASE/'data/library.sqlite3');c.row_factory=sqlite3.Row
now=datetime.datetime.now().astimezone().isoformat(timespec='seconds')
doc=json.loads((ROOT/'shilucheng_before.json').read_text())
ATT=BASE/'data/attachments/Shilucheng深入重研_20261106';ATT.mkdir(parents=True,exist_ok=True)
S='https://shop.tiktok.com/us/pdp/bamboo-sheets-set-by-shilucheng-4-6-pc-cooling-deep-pocket-silky-soft/1729438233542234865'
T='https://shop.tiktok.com/us/pdp/cooling-mattress-topper-by-shilucheng-extra-down-alternative-fill/1729439070512124657'
urls={
'ldc':'https://shop.tiktok.com/us/pdp/solid-bed-sheets-by-ldc-lux-decor-4-pc-brushed-microfiber-set/1729590912873370233',
'lux':'https://shop.tiktok.com/us/pdp/sheet-set-by-luxclub-6pc-deep-pocket-eco-friendly-silky-soft-wrinkle-free/1729385256317981042',
'dec':'https://shop.tiktok.com/us/pdp/organic-viscose-sheets-by-decolure-twin-size-17-deep-pockets-hypoallergenic/1729916842555707699',
'mel':'https://shop.tiktok.com/us/pdp/mellanni-iconic-4-pc-bed-sheets-set-soft-breathable-cooling/1729408552029229334',
'we':'https://shop.tiktok.com/us/pdp/mattress-topper-by-brand-name-extra-1000-gsm-cooling-plush-pad/1729457680158658805',
'sweet':'https://shop.tiktok.com/us/pdp/mattress-topper-by-sweetcrispy-memory-foam-cooling-ergonomic-design/1729707309447090914',
'bed':'https://shop.tiktok.com/us/pdp/california-king-bamboo-viscose-mattress-topper-deep-pocket-easy-care/1731362585480434000',
'niag':'https://shop.tiktok.com/us/pdp/ultra-soft-twin-mattress-topper-bamboo-viscose-cool-comfort/1732318179776369433'}
mid={};rid={}
def material(key,title,file=None,url=None,source='平台公开页面',summary=''):
 local=''
 if file:
  shutil.copy2(ROOT/file,ATT/file);local=str((ATT/file).relative_to(BASE/'data'))
 # Dedicated capture URL is kept local; exact source URL is in access_note.
 old=c.execute('select id from materials where title=?',(title,)).fetchone()
 if old:return old[0]
 i=c.execute('INSERT INTO materials(title,url,source_type,publisher,retrieved_at,summary,local_path,access_note) VALUES(?,?,?,?,?,?,?,?)',(title,None,source,'TikTok Shop' if source=='平台公开页面' else '研究整理',now,summary,local,('原始网址：'+url if url else '本次研究生成；保留原文与计算依据'))).lastrowid
 mid[key]=i;return i
captures=[('sheet','Shilucheng 床单页面与当前经营信号','sheets_visible_20261106.txt',S),('top','Shilucheng 褥垫页面与当前经营信号','topper_full.txt',T),('search','Cooling Sheets 关键词页：一次排序观察','cooling_sheets_search.txt','https://shop.tiktok.com/us/k/cooling-sheets'),('ldc','LDC 微纤维白色双人床四件套','ldc_microfiber_queen.txt',urls['ldc']),('lux','LuxClub 白色双人床四件套','luxclub_queen.txt',urls['lux']),('dec','DECOLURE 白色双人床六件套','decolure_queen6.txt',urls['dec']),('mel','Mellanni 白色双人床四件套','mellanni_queen.txt',urls['mel']),('we','WeCharmer 白色双人床1000克每平方米褥垫','wecharmer_queen1000.txt',urls['we']),('sweet','Sweetcrispy 双人床2英寸记忆棉加垫','sweetcrispy_queen2.txt',urls['sweet']),('bed','BEDLORE 白色双人床褥垫','bedlore_queen.txt',urls['bed']),('niag','Niagara 白色双人床褥垫','niagara_queen.txt',urls['niag'])]
for k,title,f,u in captures:mid[k]=material(k,title+'｜2026-11-06',f,u)
mid['searchpic']=material('searchpic','凉感床单关键词页截图｜2026-11-06','cooling_sheets_search.png','https://shop.tiktok.com/us/k/cooling-sheets')
for k,f,title in [('code','topper_逐条编码.csv','褥垫1000条评论｜原文、分项与编码'),('stats','topper_statistics.json','褥垫评论｜分项统计与原评论编号'),('rules','code_topper.py','褥垫评论｜可复查的编码规则与修订'),('raw','topper_reviews.json','褥垫1000条评论｜独立原始底稿')]:mid[k]=material(k,title+'｜2026-11-06',f,source='研究计算')

def topic(n,pid=None):return next(t for s in doc['sections'] for t in s['topics'] if report_framework.topic_number(t['topic'])==n and t.get('product_id')==pid)
def question(n,key,pid=None):return next(q for q in topic(n,pid)['questions'] if q.get('framework_key')==key)
def put(n,key,answer='',points=None,pid=None,kind=None,evidence='',note=''):
 q=question(n,key,pid);q['answer']=answer;q['points']=[dict(zip(('title','detail','evidence'),list(x)+['']*(3-len(x)))) for x in (points or [])];q['ordered']=bool(points);q['evidence']=evidence;q['note']=note;q['answer_status']='已回答';q['presentation']=kind or ('answer' if points or len(answer)>110 else 'fact')
 q.pop('links',None)
 if n>=5 and key!='accounts':q.pop('tables',None)
 return q

def record(key,n,title,body,evidence,pid=None,kind='分析'):
 t=topic(n,pid);sec=next(s['number'] for s in doc['sections'] if t in s['topics'])
 old=c.execute('select id from records where brand_id=? and title=?',('shilucheng',title)).fetchone()
 vals=('shilucheng',pid,sec,t['topic'],title,body,kind,'已复核' if kind=='分析' else '已核实页面信息',json.dumps(list(dict.fromkeys(evidence))),now)
 if old:
  i=old[0];c.execute('UPDATE records SET brand_id=?,product_id=?,section=?,topic=?,title=?,body=?,kind=?,status=?,evidence=?,updated_at=? WHERE id=?',(*vals,i))
 else:i=c.execute('INSERT INTO records(brand_id,product_id,section,topic,title,body,kind,status,evidence,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)',vals).lastrowid
 rid[key]=i
 for m in evidence:
  if not c.execute('select 1 from material_links where material_id=? and brand_id=? and product_id IS ? and section=? and topic=?',(m,'shilucheng',pid,sec,t['topic'])).fetchone():c.execute('INSERT INTO material_links(material_id,brand_id,product_id,section,topic) VALUES(?,?,?,?,?)',(m,'shilucheng',pid,sec,t['topic']))
 if i not in t['record_ids']:t['record_ids'].append(i)
 return i

def table(q,r,caption,support=False,comparison=False):q['tables']=[dict(record_id=r,mode='analysis',caption=caption,purpose='support' if support else 'core',**({'layout':'comparison'} if comparison else {}))]

# I. Brand facts and channel economics.
put(1,'difference','Shilucheng希望把“舒适、看起来有品质的床品，也可以负担得起”作为品牌印象。它经营的是大众床品升级，而非已证实拥有独家凉感技术的专业品牌。',kind='answer')
put(2,'main','Amazon与TikTok是已有规模证据的两大销售渠道；现有估算中Amazon较大，TikTok是更突出的内容获客渠道。不能把TikTok单款的高累计销量等同于全品牌销售第一。',kind='answer')
put(2,'growth','目前不能可靠评出增长最快的渠道。能确认的增长信号来自Amazon两组床单：2026年10月估算销售额合计48.42万美元，较9月增长241.3%；这是两个产品系列的变化，不能扩大为全渠道增长率。',evidence='卖家精灵历史估算已保存。TikTok缺少同月份销售序列；Amazon历史低谷还可能受缺货、链接变更及监测覆盖影响。',kind='answer')
put(3,'structure','多品类经营，但TikTok店铺的成交积累明显集中于床单。竹混纺床单约43.59万件，指定褥垫约7.08万件，另一款褥垫另行统计；Amazon同时有棉、亚麻、竹源材料等系列，不能据此判断全品牌只靠一个爆款。',kind='answer')
put(3,'contribution','竹混纺床单是所查TikTok店铺最重要的已观察单品。按页面累计件数与店铺累计件数粗比，约相当于六成，指定褥垫约一成；这反映成交集中度，不能当作品牌收入贡献。',evidence='商品与店铺统计可能包含多规格、跨地区与历史变化；售价不同，累计件数不是销售额。详见商品销量表。',kind='answer')
# II-A. Sheet comparison: competitive alternatives, not cherry-picked weak sellers.
rows=[
['产品',f'[Shilucheng竹混纺凉感床单（本款）]({S})',f'[LDC微纤维床单]({urls["ldc"]})',f'[LuxClub床单]({urls["lux"]})',f'[DECOLURE竹源粘胶床单]({urls["dec"]})',f'[Mellanni Iconic床单]({urls["mel"]})'],
['核心购买理由','竹源材料的柔滑与凉爽，价格可以接受','用较低价格换一套柔软、易护理的床单','柔软、透气、深包边；居家酒店感','100%竹源粘胶、凉感排湿及六件组合','柔软透气、耐用易护理的日常床单'],
['TikTok累计售出','约43.59万件','约19.32万件','约14.10万件','约2.85万件','约2.71万件'],
['评分／评分数','4.4／约4.62万','4.4／约2.49万','4.4／约1.20万','4.8／约2500','4.5／约2100'],
['白色双人床（Queen）价格','42.89美元／四件（11月5日）','24.99美元／四件（11月6日）','69.98美元／四件（11月6日）','114.99美元／六件（11月6日）','80.16美元／四件（11月6日）'],
['面料标注','60%竹源人造丝＋40%聚酯','刷毛微纤维','当前选项标注微纤维','100%竹源粘胶','双面刷毛微纤维'],
['套装组合','床单＋床笠＋2枕套；另有六件套','床单＋床笠＋2枕套','当前页面为四件；历史URL带六件，勿混用','床单＋床笠＋4枕套','床单＋床笠＋2枕套'],
['包覆与固定','侧深约36厘米，可拉伸适配约41厘米床垫','标题与参数存在36／41厘米差异','宣称约46厘米，360度松紧包边','宣称约43厘米，双缝线','宣称约41厘米'],
['已见内容信号','前五相关视频约12.6万—18.5万赞','相关视频可见约2.84万赞','相关视频最高可见约43.38万赞','样本定位为高价竹源材料替代品','样本定位为高价日常舒适替代品'],
['期间增长量','未取得同周期数据','未取得同周期数据','未取得同周期数据','未取得同周期数据','未取得同周期数据']]
def mdtable(rows):return '\n'.join(['| '+' | '.join(row)+' |' for row in [rows[0],['---']*len(rows[0]),*rows[1:]]])
scomp=record('scomp',4,'五款床单竞争对照｜高销量替代品与价格带',mdtable(rows)+'\n\n选样：本款＋四款已核实的同平台竞争样本；不是全平台TOP5排名。LDC、LuxClub是高销量日常舒适替代，DECOLURE补充纯竹源材料路线，Mellanni补充品牌与设计路线。累计售出均为商品链接的多规格历史展示，不是当月或所选白色Queen销量。价格不含个性化券与运费；本款新会话颜色选项存在标签不一致，保留11月5日已核实报价。LuxClub历史链接／视频的版本不一定等于当前四件套。未取得同条件性能测试，不按材料名判优劣。',[mid[x] for x in ['sheet','ldc','lux','dec','mel']]+[88,132,133],pid='sheets')
q=put(4,'difference','本款最突出的差别，是以中低预算提供“竹源材料＋柔软凉爽”的升级感，并已积累更大的成交与评价规模。尚未发现能单独解释销量优势的独有技术。',[
('价格处在廉价微纤维与高价竹源材料之间。','它比已查LDC微纤维四件套贵约72%，但低于本次LuxClub、Mellanni四件套报价；DECOLURE为六件套，只作价位参考。更便宜的LDC竹混纺四件套也存在，因此“竹混纺”本身不构成稀缺。'),
('竹源材料为升级体验提供解释，但材料比例不是性能优势的证明。','60%竹源人造丝与40%聚酯混纺，把竹材料故事带入较低预算。是否比微纤维更凉、更耐用，仍需同条件测试；不能由纤维名称直接推定。'),
('规格与配色提高选择便利，属于商品组合优势。','四／六件套、多个床型和颜色可覆盖换色、备用、多房间需求；其他品牌也提供丰富选择，不能写成独有设计。'),
('更大的成交与评价积累，有利于降低陌生品牌的购买顾虑。','约43.59万件累计成交，约为LDC四件套的2.3倍、LuxClub的3.1倍。优势仍明显，但不是与所有主流替代品相差几十倍。')],pid='sheets')
table(q,scomp,'本款与四款竞争产品：购买理由、销量、价格和设计',comparison=True)
put(4,'concept','主购买理由可概括为“花一笔可接受的钱，把旧床单换成更柔软、凉爽、有品质感的床单”。商品页并列多个卖点；在达人内容中，换掉闷、不舒服的旧床单是更清楚的购买触发。',pid='sheets',kind='answer',evidence='这是对商品页与已观看视频的研究归纳，不是品牌明确公布的唯一定位；“天然”“抗菌”等达人说法不能替代60/40混纺标注或性能检测。')
put(4,'performance','TikTok页面累计售出约43.59万件，评分4.4，约4.62万条评分。它领先本次四个比较样本；尚未取得可比的月销量、销售额和上市时长，不能据此计算市占率或销售增速。',pid='sheets',kind='answer')
put(5,'purchase','购买前，消费者需要一个换掉现有床单的理由；购买后，柔软与舒适才决定这笔钱是否花得值。',[
('改善怕热、闷汗与旧床单不舒服的问题。','凉感是明确的下单动机之一；“换一套就能睡得更舒服”比解释纤维参数更接近消费者的选择。','R452、R917明确提到为凉感购买；达人视频把不舒服的缎面旧床单设为替换对象。'),
('在心动与价格合适同时出现时下单。','优惠、可接受的总价与整套购买共同降低尝试门槛。不能把页面五折视为实际长期让利50%，也不能把本款称为市场最低价。','R475提到价格合适，R1389提到等到促销；同平台存在更低价的替代品。'),
('借助视频与已有评价，判断陌生品牌是否值得试。','内容负责把舒适感变得可想象，成交与评价积累提供选择依据；这是当前较有支持的获客与信任机制。','R1409提到视频、R1618提到评论；它们证明路径存在，不用于估算全体买家的动机比例。')],pid='sheets')
put(5,'unmet','最值得抓住的需求，是“买前说得清、买后摸得到，而且多次购买保持一致”。',[
('柔软与凉感需要同时兑现。','部分买家认可舒适却没有得到预期凉感；也有人因粗糙而不接受产品。升级款不能只提高瞬时凉感而牺牲触感。'),
('材料与套装要符合消费者购买时的理解。','竹源混纺与100%竹源材料、四件与六件应清楚区分；内容中笼统的“天然竹”会放大期待落差。'),
('厚床垫包覆与不同颜色的体验一致性仍有改善空间。','尺寸、滑脱与复购后触感变化均已出现。它们是具体改进方向，不能凭单条反馈认定所有批次有缺陷。')],pid='sheets')
put(6,'drivers','最有解释力的判断是：本款把常见的舒适卖点做成容易想象、容易购买的床单升级方案，再通过达人内容和长期成交积累放大。当前证据不支持“靠最低价”或“靠独家凉感技术”解释领先。',[
('把“换掉旧床单”变成当下值得做的一笔小额升级。','视频先唤起对旧缎面闷、滑、不舒服的反感，再给出柔软凉爽的替代。消费者不必先掌握技术知识，就能理解为什么要换、换了会有什么感觉。','商品页、五条已观看视频与购买前动机相互印证，共同指向旧品替换带来的舒适升级动机。'),
('达人推广让同一购买理由反复触达，商品页接住这些需求。','已确认多名佣金达人、多个相关内容样本，以及一次Cooling Sheets关键词页首位展示。内容和搜索入口共同扩大可见度，较能解释功能相近时仍产生的销量差距。','尚未独立核实4,740名达人的统计范围；没有广告后台证据，不能把首位展示写成购买关键词，也不能把佣金合作等同大量固定广告费。'),
('促销与中间价格带降低尝试门槛，而非绝对最低价取胜。','对比高价竹源材料或品牌床单，本款容易被理解为较低成本升级；与廉价微纤维和LDC竹混纺相比又不便宜。顾客购买的是可感知的组合价值。','同平台白色Queen价格已核实；历史成交价、优惠券和投流成本未取得，不能倒推长期利润或价格弹性。'),
('累计成交、评价与部分正向体验让销售更容易延续。','大量既有购买记录降低选择顾虑，柔软体验和配色选择还能支持后续购置。它是销售积累后的放大因素，不能反过来当作最初起量原因。','928条主样本397条认可柔软；13条明确再次下单，其中有复购后不满的反例。13条是提及再次购买的评论数，不能当作复购率。')],pid='sheets')
put(6,'advantage','本款已体现的强项是“把升级价值卖出去并积累成交”，而不是已证实在面料、凉感或价格上全面胜出。',[
('最大的可观察优势，是成交与评价积累。','对比本次高销量替代样本，本款有更大的历史成交规模。这能支持购买信任，但上市更早、历史售价更低也可能参与形成差距。'),
('购买理由完整：旧床单不舒服 → 柔软凉爽的替换 → 价格值得试。','这条表达路径比孤立材料参数更便于短视频传播。但同类也在说软与凉，因此优势在持续执行和触达，不能写成独占心智。'),
('产品本身提供足够多被认可的舒适体验，但尚无独有性能领先证据。','柔软认可强于凉感反馈，是产品接住营销期待的重要基础。更深包边、纯竹源材料和更低售价都能在对手中找到，BS仅增加这些参数未必能胜出。')],pid='sheets',evidence='反证：LuxClub可见相关视频最高约43.38万赞，高于本款前五视频，但累计销量较低。单条爆款点赞不是销售领先的充分解释。')
# II-B. Topper: independent product and consumer analysis.
trows=[['产品',f'[Shilucheng仿羽绒褥垫（本款）]({T})',f'[WeCharmer纤维褥垫]({urls["we"]})',f'[Sweetcrispy记忆棉加垫]({urls["sweet"]})',f'[BEDLORE竹源混纺褥垫]({urls["bed"]})',f'[Niagara竹源材料褥垫]({urls["niag"]})'],['核心购买理由','较低投入给旧／硬床垫加软，兼顾凉感','加厚蓬松、为床垫增加缓冲','记忆棉贴合、压力分散与凝胶凉感','竹源混纺、舒适与深包边','竹源材料、云朵般柔软与透气'],['TikTok累计售出','约7.08万件','约12.25万件','约3.63万件','约1.03万件','约5400件'],['评分／评分数','4.3／9013','4.4／约1.43万','4.7／约4500','4.4／约1400','4.5／915'],['双人床（Queen）页面价','41.90美元／灰色2英寸','58.99美元／白色1000克每平方米','53.37美元／2英寸','69.19美元／白色','92.99美元／白色'],['结构与选项','纤维填充；2／3英寸，未披露填充克重','500／1000克每平方米；纤维填充','凝胶记忆棉；2／3／4英寸','表层宣称40%竹源粘胶＋60%聚酯','表层宣称竹源粘胶，完整比例未核实'],['适配厚度','约20—53厘米床垫','约20—53厘米床垫','直接铺于床垫上的泡棉','约15—46厘米床垫','约20—51厘米床垫'],['主要比较边界','标题Bamboo Top与Cotton参数不一致；不同颜色／版本不可混说','1000克选项与本款不同，不能只按厚度比较填充','属于解决同一问题的结构替代品，不是同材质褥垫','宣称与实际凉感仍需验证','宣称与实际凉感仍需验证'],['期间增长量','未取得同周期数据','未取得同周期数据','未取得同周期数据','未取得同周期数据','未取得同周期数据']]
tcomp=record('tcomp',4,'五款床垫加垫竞争对照｜舒适升级的不同路线',mdtable(trows)+'\n\n2026年11月6日页面观察。价格为所选规格，不含个性化券、运费；累计销量不是该规格销量。WeCharmer为本次观察中更高销量的同类竞争者，不能称本款为类别第一。泡棉与纤维填充承担的支撑任务不同，厚度数字不能直接代表同等舒适或承托。',[mid[x] for x in ['top','we','sweet','bed','niag']],pid='topper')
put(4,'identity',f'[Shilucheng仿羽绒凉感褥垫]({T})，研究商品ID为1729439070512124657。灰色双人床（Queen）、标称厚约5厘米（2英寸）页面价41.90美元，另有约7.6厘米（3英寸）版本。它是铺在床垫上的加垫，不能替代独立床垫。',pid='topper',kind='answer')
put(4,'performance','页面累计售出约7.08万件，评分4.3／9013条评分。具有成交规模，但低于本次WeCharmer同类链接的约12.25万件；不能套用床单的“销量领先”判断。',pid='topper',kind='answer')
put(4,'concept','主购买理由是“少花钱，让现有床垫更柔软、更舒服，暂时不必更换整张床垫”。凉感与透气是加分项，真实使用反馈更集中在加软与舒适。',pid='topper',kind='answer',evidence='商品页强调加厚、蓬松与旧床垫升级；消费者有明确的硬床垫、宿舍床、客房床及暂缓换床垫情境。标题中的Bamboo Top与Cotton参数存在冲突，暂不写确定的表层成分比例。')
q=put(4,'difference','它以较低页面总价提供纤维填充的加软方案；差异主要来自预算与软感路线，而非已证明的独家凉感技术。',[
('在本次已选规格中价格最低。','41.90美元低于WeCharmer的1000克版本及其余三个比较样本；但WeCharmer还有500克版本，不能外推为全市场最低价。'),
('主要改变表层软感，不等于泡棉的承托与压力分散。','对不想换床垫、又不喜欢厚泡棉陷入感的人有吸引力。是否合适取决于原床垫与个人偏好。'),
('深包边和多个厚度提供适配选择，但供应普遍存在。','WeCharmer等也有深包边；本款未公布统一可比的填充克重，宣传的“加倍填充”暂不能用于认定更厚或更耐压。')],pid='topper')
table(q,tcomp,'本款与四款床垫加垫：销量、价格、材料和使用任务',comparison=True)
stat=json.loads((ROOT/'topper_statistics.json').read_text());fb=topic(5,'topper');fb['feedback']={**stat,'material_id':mid['code'],'method_material_id':mid['rules'],'calculation_material_id':mid['stats'],'sample_label':'已收录的1000条混合来源评论','method_paragraphs':[
'对象：商品1729439070512124657，1000条既有评论，日期2025年8月20日至2026年11月4日；来自推荐排序导出与后续采集，不是随机抽样。584条带平台评论ID，416条原来源未提供ID；保留原文和来源，不补造身份。',
'采用全量规则辅助编码，并对未判定、混合评价、温度表述和关键归因逐条复核。按评论文字识别，不用星级替代；同一条可同时认可与不认可、提到多个主题。语义较隐含的表达可能遗漏，统计用于识别主题，不代表客户满意率、故障率或市场发生率。',
'样本含230条一星评论（23%），平台页面一星约10.1%，表明样本结构与全体评价不同。不得用本样本的70.1%或45.0%推断全体买家；也不能直接与床单近期样本横向比较满意度。',
'身体不适改善是消费者自述，不构成医疗效果证明；图片不符与厚度不满可能来自同一条评论，不能相加。完整原文、编码与计算规则可下载复核。']}
fb['questions'].insert(0,{'id':'shilucheng-topper-5-overview','title':'评论反馈全貌','framework_key':None,'type':'feedback-summary','presentation':'plain','answer':'','record_ids':[],'answer_status':'已回答'})
put(5,'positive','主要认可集中在柔软、舒适和适配；凉感不是这批评论里最强的体验信号。',pid='topper',kind='answer')['type']='feedback-positive'
put(5,'negative','最突出的不满是“没有视频里那么厚、那么蓬松”，其次是与展示不符及软感未达预期。需要优先解决购买承诺与实际加软效果之间的落差。',pid='topper',kind='answer')['type']='feedback-negative'
put(5,'purchase','核心需求是给现有床垫补一层舒适，而不是单纯购买一项凉感技术。',[
('暂缓更换床垫，用较小投入改善硬、旧或不舒服的床。','宿舍、客房、房车及家中现有床垫都出现这一使用场景。它争夺的不仅是其他褥垫预算，也包括“继续忍着”与“直接换床垫”的选择。','原评论R2230、R2524明确先尝试加垫再决定换床垫；R2074明确为增加缓冲购买。'),
('追求看得见的蓬松与酒店床感。','短视频和商品图片把柔软放大成直观的床面改造，消费者很容易想象睡上去的感觉；大量厚度落差反馈也反向证明这种展示影响了期待。','R1846、R1877、R2172、R2504等直接描述看过视频后的期待；其中有关AI、夸大的说法属于消费者看法，未作为事实认定。'),
('部分人明确为降温购买，另一些人重视优惠与试错成本。','R2131、R2297明确提到凉感购买动机；R2055描述活动价。两类需求应区分，不能把全部加软订单归因于凉感。')],pid='topper')
put(5,'unmet','真正的改进机会，是“加软效果可信、拆包即用更省事、洗后依然稳定”。',[
('展示真实厚度与受压后的表现。','不能只拍悬空抖动的蓬松效果。应说明它是加垫、适用什么床垫，以及能改善什么、不能替代什么。'),
('减少恢复蓬松与日常洗护的负担。','有人通过烘干改善，也有人按说明处理仍无效，还有大尺寸难放进家用烘干机的反馈。改善填充与包装，比一味要求用户继续蓬松处理更有价值。'),
('同时考虑怕热、偏好承托与退换成本。','更厚更软不一定更凉，也不一定适合每个人。页面提示退货运费可能由买家承担；体积大、难重新打包会放大试错负担。')],pid='topper')
put(6,'drivers','本款卖得动，最合理的解释是“低门槛床垫升级”有明确需求，视觉化的蓬松表达促成尝试，部分消费者实际感受到加软效果；其成功不等于凉感性能领先。',[
('用几十美元的加垫，替代马上更换床垫的大决定。','把问题从“买新床垫”转为“先改善表面软感”，显著降低消费者需要投入的预算和决策精力。这是比单独“凉感”更有解释力的购买任务。'),
('蓬松画面将舒适升级变成容易理解的商品利益。','消费者不必理解填充技术，就能被“床变厚、变软”的画面吸引。评论中反复出现视频厚度期待，说明视觉宣传参与了购买；但也带来过度承诺的风险。'),
('较低页面总价与已有店铺成交积累降低陌生产品的尝试障碍。','本次所选规格价格低于四个参照样本，且已有数万件成交和数千评分。它不需要技术独占，也能在可接受的价格上获得订单。'),
('真实舒适改善支撑口碑与少量再次购买，不能掩盖蓬松度短板。','全量评论中柔软舒适是最常见的明确认可；同时，厚度与恢复蓬松是最集中的问题。增长能否延续，取决于承诺和体验能否保持一致。','R1915、R1977、R2149、R2343、R2372、R2381、R2523、R2617等有实际再次购置信息；未将未来购买意愿当作已发生复购。')],pid='topper')
put(6,'advantage','它已形成的是有销量支撑的入门加软方案；尚未形成同类领先地位或不可替代的技术优势。',[
('所选规格总价较低，购买任务直接。','对只想给硬床垫增加软感的人，比直接换床垫更容易尝试；但价格优势的比较范围仅限已核规格。'),
('舒适加层与深包边获得明确认可。','部分消费者能在保留原床垫承托的同时得到表层软感；这也解释了为何有人偏好纤维加垫而不喜欢记忆棉陷入感。'),
('主要短板是蓬松承诺与体验稳定性，竞争者也已达到更大销量。','WeCharmer约12.25万件，高于本款约7.08万件；本款不能以“品牌床单卖得好”代替褥垫竞争力证明。')],pid='topper')
# III. Channel operations and consumer psychology.
put(7,'accounts','在已核实的官方关联账号中，TikTok明显是主要内容经营阵地；Instagram、Facebook与YouTube的公开受众规模很小，暂看不到相同强度的内容积累。',[
('TikTok同时具备内容分发与即时购买入口。','@shiluchenghome约3.32万粉丝；店铺与商品页连接佣金达人视频，内容可直接引向商品。账号粉丝不等于达人总覆盖。'),
('其他关联社交账号目前更接近基础展示。','Instagram约17位粉丝／30帖，Facebook约2位粉丝，YouTube约29位订阅者／26个视频。这个判断限已核实账号，不代表不存在其他账号或广告投放。')],evidence='账号截面为11月4日；未连续记录发布时间，不用累计帖子数代替发布频率。',kind='answer')
put(7,'affiliate','达人分销是明确存在的主要内容获客方式之一，品牌自营承担店铺承接与基础沟通。',[
('商品相关视频显示佣金合作，购买理由由不同创作者反复表达。','已见19条相关视频，去重约11名创作者；其中有同一作者的多个相近版本，视频数与去重后的创作者人数分别统计。'),
('尚不能把达人规模直接等同于推广预算。','用户提供的4,740名达人线索尚未独立核实统计对象、时间与去重口径；佣金合作、寄样、固定付费与广告加热应分别研究。')],kind='answer')
put(7,'format','已确认短视频参与带货，尚未取得直播、短视频、商城自然成交的销售构成。当前可把短视频视为重要获客方式，不能给出未经验证的销售占比。',kind='fact')
video_rows=[['视频／点赞量','抓住的心理与购买触发','为什么具有传播潜力'],
['[V01 Alyssa：粉色床单](/attachment/56)／约18.51万赞','把清爽、柔软与好看的卧室连在一起；买的是可想象的生活改善','完整铺床画面让消费者迅速代入自己的卧室，低理解成本；“软与凉”直接对应身体感受'],
['[V02 Kat Kag：秋季棕色床品](/attachment/57)／约14.45万赞','借换季换色给购买找理由，再用柔软和优惠推动下单','季节审美让非刚需的更换变得合理；柔软视觉与促销缩短犹豫'],
['[V03 Ben：缎面床单不舒服](/attachment/58)／约14.01万赞','戳破“看起来丝滑就一定舒服”的期待，提供替换选择','先说出已有使用者的不满，再让本款成为解决办法；对旧品的判断比材料参数更容易引起共鸣'],
['[V04 Ben：垃圾袋类比旧床单](/attachment/59)／约13.37万赞','用夸张类比强化闷、滑、不舒适的反感','容易记住、容易形成评论争论，随后用新品与优惠承接；夸张能吸引注意，但不是性能证据'],
['[V05 Ben：换成竹源床单](/attachment/60)／约12.56万赞','让竹材料与酒店式舒适成为旧品升级的解释','先否定旧选择，再给购买新床单一个看似清楚的理由；“天然、抗菌”等说法仍需与成分和测试区分']]
vtable=record('video',8,'五条高点赞视频：消费者心理与购买触发',mdtable(video_rows)+'\n\n按用户认可的商品相关视频前五选择，点赞数为11月4日截面。五条来自三名创作者，不是五种独立打法。已保存视频可点击观看；未取得原作品永久链接，来源为本款商品页。没有各视频的可核实播放量、订单或GMV，不用点赞代替转化率。',[56,57,58,59,60,61,80,81,82],kind='分析')
q=put(8,'samples','这五条内容的共同点，是把“换床单”讲成可立即获得的舒适与卧室升级；其中三条来自Ben，集中使用对旧缎面床单的不满。',kind='answer');table(q,vtable,'TOP5样本：视频链接、受众心理与购买触发')
put(8,'message','最值得学习的是让消费者先产生“现在这套该换了”的理由，再介绍新品。',[
('激活已有不满：旧床单看着光滑，睡起来却不舒服。','这种表达把潜在问题拉到注意力中心，促使观众重新评价现有产品；对已经不满意的人尤其直接。'),
('给替换以具体想象：更软、更凉、卧室更好看。','铺床、触摸和成套配色让收益可视化。它卖的是换过之后的感受，不是让消费者先研究材料科学。'),
('用材料故事与优惠完成最后解释。','竹源材料让升级显得有依据，促销让当下尝试显得划算。若材料与性能说得过满，同一机制也会造成落差和差评。')],kind='answer')
put(8,'conversion','综合商品挂链、佣金合作、评论中的视频购买线索与成交规模，判断这类内容参与促进了销售，有合理依据。当前不能把订单分配到每条视频，也不能断言前五视频全部具有同等转化能力。',[
('高点赞代表注意力，不自动等于高成交。','LuxClub可见相关视频点赞高于本款，但累计成交低于本款；说明需要同时看触达量、挂链承接、价格、受众与持续发布。'),
('销售判断要落到整套路径，而不是只夸一个爆款。','从对旧床单不满，到相信新产品，再到点击购买，这条路径有多种证据互相支持；推广费用和净利润仍未公开。')],kind='answer')
put(9,'strategy','核心传播策略是“替换旧床单”，以舒适体验推动升级，再用达人分销和促销扩大成交。',[
('以旧品不满为开场，而不是堆叠新品参数。','闷、滑、看着好但睡不好，为消费者建立更换理由。'),
('重复少数容易理解的利益点。','软、凉、好看、价格值得试，被不同达人和场景反复表达。'),
('允许相近内容反复传播，但不把重复误称为系统性投放实验。','同一创作者的多个相似视频说明内容可以复用；未取得投放记录，不能认定品牌做过严格的测试或广告放量。')],kind='answer')
put(9,'perception','它试图建立的是“比旧床单更舒服、价格又够得着的竹源床单”认知。消费者反馈对柔软舒适的支持较强；对全品牌独占“凉感”的心智，现有材料仍不足。',kind='answer')
put(9,'learn','可借鉴的是表达结构与场景选择，不能直接照搬未经验证的性能宣称。',[
('从真实的旧品痛点切入。','让怕热、粗糙、滑脱等不同人群看到自己的问题。'),
('拍出替换前后的真实差别。','用相同条件展示接触、铺床、固定与洗后表现，避免只有看起来蓬松或丝滑。'),
('把优惠放在价值解释之后。','先让人知道为什么值得换，再用价格促成行动；不能只复制大折扣。')],kind='answer')
# IV. History, preserving chronology and causal limits.
put(11,'actions','当前最值得重视的增长动作，是把成熟床品做成适合短视频销售的升级方案，并在多个产品上重复使用。',[
('用达人内容把模糊的舒适需求变成明确的换购理由。','床单替换旧缎面，褥垫改善旧／硬床垫；两款都在降低消费者理解产品价值的难度。'),
('让内容、活动价、商品选择和评价承接形成连续的购买过程。','单独的卖点不稀缺，但看到内容后能马上挑尺寸、颜色和套装并下单，有利于把兴趣变成订单。'),
('在同一店铺向相邻舒适需求扩展。','床单之外，指定褥垫已形成约7万件成交，另一款褥垫另有积累。说明店铺有跨产品经营的结果；不能据此断言是床单买家交叉购买，或所有新品都能复制成功。')],kind='answer',evidence='以上为现有经营方式与结果的综合判断，各动作的独立销量贡献及增长拐点仍需历史序列检验。')
put(11,'change','能确认的是：2023年已有竹床单促销传播，现在已观察到TikTok达人带货与多品类成交。尚未取得连续的历史渠道份额、投放和销售数据，不能写成“从Amazon转向TikTok”或某年完成增长模式转型。',kind='fact')
# V. Brand mechanism.
put(12,'perception','目前更强的是商品层面的“软、舒服、可接受的价格”，而不是已经证实的跨品类品牌信仰。',[
('床单承接柔软凉爽与换购期待，褥垫承接床垫加软期待。','两者共同指向用不太高的预算改善睡眠环境。'),
('品牌正在把分散的产品体验汇成“舒适升级”印象。','同店多产品、达人展示与评价积累支持这个方向；它是否已成为消费者主动点名选择的品牌，仍需品牌搜索与选择调查确认。')],kind='answer')
put(12,'value','它提供的商业价值，是把消费者熟悉的舒适需求变成容易理解、购买与尝试的商品组合。这个价值不要求每一种材料都独有。',[
('从消费者的问题出发包装成熟供给。','旧床单不舒服、床垫太硬等问题，比混纺比例更容易形成购买理由。'),
('在产品选择、内容表达与销售承接上减少购买阻力。','尺寸、颜色、套件、活动价和评价让顾客更容易完成选择。竞争优势可能来自这些环节共同执行，而非某个孤立功能。')],kind='answer')
put(12,'pay','消费者愿意多付一点，可能是为更确定的选择和更具体的舒适期待；目前不能把全部价差认定为Shilucheng品牌溢价。',[
('相对廉价替代品，内容和购买积累可以提高信任。','本款床单并不比LDC廉价款更便宜，却有更多成交，说明价格不是唯一决策因素；历史促销与上架时长也可能解释部分差距。'),
('使用体验能让部分顾客继续买，但尚不能推出整体品牌忠诚。','床单有明确再次下单，褥垫也有为家人或其他床购置的记录。没有对照调查，不能量化消费者只为品牌名称愿意多付多少。')],kind='answer')
put(12,'mind','较有支持的是“商品与舒适升级场景形成联系”，尚不能认定品牌已独占凉感床品心智。高成交、搜索可见度、复购个案与品牌主动联想是不同层次，不能互相替代。',kind='answer')
put(13,'factor','最关键的能力，是把成熟床品的舒适利益做成可规模传播、可即时购买的商品。床单的成交领先，比独家面料或最低价更能指向这一商业执行能力。',kind='answer')
put(13,'capability','从已观察结果看，三项能力最值得BS研究。',[
('找到容易让人行动的商品概念。','床单讲换掉旧的不舒服，褥垫讲先改善现有床垫；都把价值落在具体使用问题上。'),
('组织可持续的内容与分销。','多位佣金创作者、重复的内容结构与商品挂链，表明经营不只依靠一个品牌账号的自然粉丝。实际团队规模、达人总数和投流效率仍未取得。'),
('把流量转为可选购的商品供给。','规格、颜色、套装与相邻品类扩展支撑不同需求。跨款出现成交是经营能力的结果信号，但不能据此推定研发、成本或供应链全面领先。')],kind='answer')
put(13,'barrier','较难快速复制的是长期积累的商品评价、成交记录、有效内容和合作关系；材料名称、降价、套装及单条视频形式都容易被复制。',[
('积累优势比独家技术壁垒更符合现有证据。','新进入者即使做出近似产品，也需要时间建立相同的购买信任和内容覆盖。'),
('这种优势可被竞争削弱，不能理解为永久护城河。','其他品牌已经有高销量或更高点赞内容；平台流量规则、获客成本和体验问题都会影响持续性。')],kind='answer')
put(13,'sustain','具备继续扩张的商业基础，但持续增长取决于能否在放大销售时控制体验落差与获客成本。',[
('最直接的风险，是营销承诺超过可稳定交付的体验。','床单的凉感／材料期待，褥垫的厚度／蓬松期待，是已经出现的具体问题。'),
('成交规模需要进一步转化为可持续利润。','佣金、广告、促销、退货与履约都会影响实际利润；现有销量不能证明低成本获客或高盈利。'),
('复制时应保留需求逻辑，而非把同一套夸张卖点套到所有产品。','床单和褥垫购买任务不同，后者还有更重的体积、洗护和退换负担。')],kind='answer')
# VI. Incremental business implications, tied to BS existing work.
put(14,'innovation','优先开发能在“替换现有床品”中明显改善体验的产品，而不是只增加一个凉感参数。',[
('床单：把凉感、柔软、固定和洗后稳定性组合成可感知的升级。','选择真实畅销的竹混纺与微纤维对手做同条件比较，突出一至两个顾客确实在意的改善。'),
('褥垫：如果进入，应把真实加软效果和恢复蓬松放在前面。','先判断填充结构、压缩包装、洗护与大件退换能否经济地做好；不能仅换表层材料就称为升级。')],kind='answer')
put(15,'marketing','最值得借鉴的是“说清旧品哪里不够好，再证明换后有什么改善”。',[
('把换购人群分开表达。','怕热者、嫌旧床单粗糙者、厚床垫滑脱者，各有不同的购买触发。'),
('把可复用内容做成可验证的对比。','真实使用与洗后对比，比抽象的“高科技、极致凉感”更容易解释价差；达人推广需要统一可证实的表述。')],kind='answer')
put(16,'weakness','最有竞争价值的弱点，是内容承诺与实际体验之间存在可识别的落差。',[
('床单：竹源材料容易被理解成纯竹，凉感也不被所有人认可。','BS有机会用清楚的材料说明与真实体验证明争取换购，而非攻击某种纤维。'),
('褥垫：厚度、填充均匀性和拆包恢复反复引发不满。','若产品做不到稳定蓬松，放大云朵画面会同时放大投诉和退换负担。')],kind='answer')
put(17,'opportunity','优先机会是争取“已经买过基础凉感床品、愿意为更稳定体验升级”的消费者；褥垫是另一个需要单独核算的相邻机会。',[
('优先：承接大众凉感床单的升级需求。','需求已有数十万件级平台商品成交支持；竞争来自成熟竹混纺和微纤维品牌。BS应证明某项高频体验显著更好，并验证顾客是否愿意支付差价，不能只把更高技术参数当作溢价依据。'),
('第二：让内容与商品组合共同服务具体的换购场景。','客户已经考虑套装、视觉表达与凉感开发；新增判断是把“为什么要换现有产品”作为内容与产品测试的共同标准，并把竞品对照和净收益带入决策。'),
('条件性：为旧／硬床垫提供可信的舒适升级。','本款和WeCharmer的成交证明有人购买这个任务；BS能否进入取决于加软效果、凉感取舍、包装恢复及退换后的利润。先验证能力与经济性，不把投诉多直接等同于蓝海。')],kind='answer')
put(18,'implication','BS要争取的不是多写几个卖点，而是用更可靠的产品体验，拿下一个顾客愿意换、愿意付钱的理由。',[
('产品判断：先选值得赢的体验，再选材料和技术。','不要只与低销量对手比较；以真实畅销替代品检验升级是否明显。'),
('增长判断：同时算购买理由、触达能力与退换后的利润。','更强产品不自动带来销量；更多达人也不自动带来盈利。'),
('品牌判断：把一次次可信改善积累成稳定认知。','在尚未建立心智时，具体的“为什么换你”比空泛的品牌愿景更能指导产品与传播。')],kind='answer')
# Compile each edited item into an auditable current research record.
source_by={1:[6,15,48],2:[180,181,182,183,184],3:[15,16,4,mid['sheet'],mid['top']],7:[20,25,37,38,39,40,mid['sheet']],8:[56,57,58,59,60,61,80,81,82,mid['lux']],9:[56,57,58,59,60,76,mid['sheet']],10:[44,72],11:[44,72,56,57,58,mid['sheet'],mid['top']],12:[73,74,76,mid['sheet'],mid['code']],13:[73,76,mid['sheet'],mid['top'],mid['code']],14:[87,85,86,mid['code']],15:[87,56,57,58],16:[76,mid['code'],mid['top']],17:[87,85,86,mid['sheet'],mid['top'],mid['we']],18:[87,85,86,mid['sheet'],mid['top']]}
for s in doc['sections']:
 for t in s['topics']:
  n=report_framework.topic_number(t['topic']);pid=t.get('product_id')
  if n==10:continue # preserve verified historical facts
  src=source_by.get(n,[])
  if pid=='sheets':src=([mid[k] for k in ['sheet','search','ldc','lux','dec','mel']]+[56,57,58,59,60,73,74,76,87])
  if pid=='topper':src=([mid[k] for k in ['top','we','sweet','bed','niag','code','stats','rules','raw']])
  body='\n\n'.join('## '+q['title']+'\n'+q.get('answer','')+'\n'+'\n'.join(f'{i+1}. {p["title"]}\n{p.get("detail","")}\n{p.get("evidence","")}' for i,p in enumerate(q.get('points',[])))+ ('\n'+q.get('evidence','') if q.get('evidence') else '') for q in t['questions'])
  key=f'current-{pid or "brand"}-{n}';rr=record(key,n,('床单' if pid=='sheets' else '褥垫' if pid=='topper' else '品牌')+'｜'+t['topic']+'｜深入重研20261106',body,src,pid)
  t['coverage']='部分回答' if n in [1,2,3,7,8,11,12,13] else '已回答';t['answer_type']='分析判断' if n not in [1,2,3,4] else '事实概括';t['finding']='';t['gap']='';t['impact']=''
  for q in t['questions']:
   q['record_ids']=list(dict.fromkeys(q.get('record_ids',[])+[rr]));q['answer_status']='已回答' if q.get('answer') or q.get('type') else '部分回答'
  # Remove superseded analytical clutter from the displayed evidence list.
  kept=[]
  for oldid in t['record_ids']:
   row=c.execute('select kind,title from records where id=?',(oldid,)).fetchone()
   if row and (row['kind']!='分析' or oldid in rid.values()):kept.append(oldid)
  t['record_ids']=list(dict.fromkeys(kept+[rr]))
  for q in t['questions']:q['record_ids']=[x for x in q['record_ids'] if x in t['record_ids']]
  if pid=='topper' and n==5:
   t['feedback']['material_id']=mid['code'];t['feedback']['method_material_id']=mid['rules']
# Main conclusions have priority; evidence remains available below.
heads=[
'以可负担的舒适升级经营床品，Amazon与TikTok分别承担重要销售与内容角色',
'床单靠完整的换购理由积累领先；褥垫靠低门槛改善现有床垫获得订单',
'用达人内容激发“旧床品该换了”，再由价格、规格与评价接住购买',
'已有持续销售与促销记录；增长动作可分析，历史拐点不能补造',
'更强的能力是把成熟床品卖出去，长期优势取决于信任与体验能否持续',
'BS的机会是争取有明确升级理由的人群，并把真实改善转化为愿付价差']
for i,s in enumerate(doc['sections']):s['headline']=heads[i];s['summary']='';s['updated_at']=now
# Keep raw data boundaries away from the reading flow.
doc['summary']='Shilucheng的核心竞争力，更像是把成熟床品做成易理解、易尝试的舒适升级方案，再通过达人内容、促销和成交积累扩大销售。床单的销量优势明显，褥垫也已形成规模；两款均未显示独家凉感技术优势，且存在不同的体验落差。对BS而言，机会在于用更稳定、可感知的改善争取升级购买，而不是仅复制材料名或大折扣。'
doc['title']='Shilucheng 品牌研究总览'
doc['scope']='按竞品品牌研究框架V1.0及已确认的第6项调整。品牌经营、床单、褥垫分别研究；事实、区间估算、商业推断分开。新增竞争页面于2026年11月6日读取，旧事实保留原采集日。统计范围与缺口见各项依据。'
doc['summary_record_ids']=[rid['current-brand-2'],rid['current-sheets-6'],rid['current-topper-6'],rid['current-brand-13'],rid['current-brand-17']]
doc['profile']=[{'label':'核心经营方式','value':'可负担的舒适升级','detail':'成熟产品＋明确换购理由＋内容分销','record_ids':[rid['current-brand-13']]},{'label':'床单累计售出','value':'约43.59万件','detail':'TikTok商品链接，全部规格累计','record_ids':[rid['scomp']]},{'label':'褥垫累计售出','value':'约7.08万件','detail':'同类样本中另有更高销量产品','record_ids':[rid['tcomp']]},{'label':'对BS的优先机会','value':'有证据的体验升级','detail':'争取愿意为稳定凉感与舒适换购的人群','record_ids':[rid['current-brand-17']]}]
for pid in ['sheets','topper']:
 pr=doc['product_reports'][pid]
 pr['summary']=question(6,'drivers',pid)['answer'];pr['merchant_reason']['headline']=question(4,'concept',pid)['answer'];pr['merchant_reason']['headline']='换掉旧床单，以可接受价格获得柔软凉爽' if pid=='sheets' else '给旧／硬床垫加软，暂时不必换整张床垫';pr['merchant_reason']['structure']='商品页与内容主张的研究归纳';pr['merchant_reason']['record_ids']=[rid[f'current-{pid}-4']]
 pr['pending']=['可比月度销量、历史成交价及推广成本未取得；不影响已观察事实，但限制销售贡献和利润估算。']
 if pid=='topper':pr['pending'].append('独立褥垫TOP5视频尚待确认；本轮未套用床单视频。')
 pr['key_facts'][1]['value']='约43.59万件' if pid=='sheets' else '约7.08万件';pr['key_facts'][1]['detail']='11月6日商品页累计展示，全部规格'
# The new search image is shown with the relevant finding and attached correctly.
q=question(6,'drivers','sheets');q['figures']=[{'material_id':mid['searchpic'],'source_id':mid['search'],'caption':'一次关键词页观察：本款出现在Cooling Sheets商品列表首位。页面未见广告标记，不据此认定付费竞价。'}]
c.execute('INSERT INTO material_links(material_id,brand_id,product_id,section,topic) VALUES(?,?,?,?,?)',(mid['searchpic'],'shilucheng','sheets',2,topic(6,'sheets')['topic']))
for s in doc['sections']:
 s['reviewed_revision']=reports.section_revision(c,'shilucheng',s['number'])
doc['reviewed_revisions']={str(s['number']):s['reviewed_revision'] for s in doc['sections']};doc['updated_at']=now
report_framework.validate_document(doc,['sheets','topper'])
# All referenced material IDs must exist; this catches source typos before publishing.
for t in [t for s in doc['sections'] for t in s['topics']]:
 for i in t['record_ids']:
  r=c.execute('select * from records where id=?',(i,)).fetchone();assert r and r['brand_id']=='shilucheng'
  for m in json.loads(r['evidence']):assert c.execute('select 1 from materials where id=?',(m,)).fetchone(),m
c.execute('UPDATE brand_reports SET document=?,updated_at=? WHERE brand_id=?',(json.dumps(doc,ensure_ascii=False),now,'shilucheng'))
c.commit();(ROOT/'shilucheng_published.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2));(ROOT/'published_ids.json').write_text(json.dumps({'materials':mid,'records':rid},ensure_ascii=False,indent=2))
print('已发布Shilucheng',len(rid),'条研究记录；',len(mid),'项新证据；全部框架问题通过检查')
