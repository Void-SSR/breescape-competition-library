import copy,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
d=json.loads((ROOT/'协作/行业全景升级_20261105/01_核定内容.json').read_text())
d.update(package_id='industry-panorama-restored-20261106',layout_version=3,title='凉感床品行业全景',reviewed_at='2026-11-06',subtitle='美国市场 · 市场规模、产品竞争、材料技术与消费者需求')
d['sections']=[{'id':i,'title':t} for i,t in [('market','市场规模与结构'),('products','细分品类与代表产品'),('materials','材料与技术'),('needs','需求金字塔'),('mindmap','心智地图')]]

def source(key,title,url,supports,boundary,kind='消费者公开讨论',publisher='Reddit'):
 d['sources'].append(dict(key=key,title=title,url=url,source_type=kind,publisher=publisher,retrieved_at='2026-11-06',supports=supports,boundary=boundary))

source('comforter-search','消费者原帖｜寻找凉感被时的选择困难','https://www.reddit.com/r/Bedding/comments/1ig3q9m/','发帖者想替换过厚的被子，同时顾虑价格、起球、退货与评论可信度；正文讨论了空调、薄床单和床面送风等替代选择。','个人自述和讨论，不作为市场比例；对其他品牌的投诉转述未独立验证。')
source('blanket-use','消费者原帖｜凉感毯的温度、重量与洗护体验','https://www.reddit.com/r/Costco/comments/1kjp6ui/','不同参与者报告接触凉后仍变热、重量偏大、容易滑落、家庭洗衣机装不下；另有满意反馈。','讨论混有不同商品；只提炼需求，不将这些问题归因于某一个指定型号。')
source('covering-need','消费者原帖｜怕热但仍需要盖被的使用情境','https://www.reddit.com/r/Menopause/comments/1lkmy3l/','有参与者表示不盖东西无法入睡，炎热时改用床单；另有人需要一定被子重量，并使用床面送风。','个人自述，包含不同国家用户；只作为覆盖与重量偏好的线索，不推广为美国人口结论。')
source('sheets-household','消费者原帖｜同床两人的透气、触感与耐用需求','https://www.reddit.com/r/Costco/comments/1w7h432/','发帖者同时提出伴侣怕热、自己对触感敏感、有宠物所以重视强度。','说明同一家庭存在并行要求；不推算这些要求的普及率。')
source('sheets-durability','消费者原帖｜凉感床单使用约一年后破损','https://www.reddit.com/r/Bedding/comments/1xg3avz/','发帖者认可此前使用体验，但因床单破损重新寻找产品，提出耐用与替换成本问题。','单个使用者自述；不能推断该品牌整体寿命或证明破损原因。')
source('comforter-size-audit','IndexBox｜美国凉感被估算复核','https://www.indexbox.io/store/united-states-kw-cooling-comforter-840-market-analysis-forecast-size-trends-and-insights/','页面给出凉感被占比与增长估算，但未找到能复算的产品样本与分类依据；多处图表标注Demo。','不采纳其份额或增速作为美国凉感床品事实。','第三方估算（未采纳）','IndexBox')

m=d['market']
m['title']='市场规模与结构'
m['scope']='美国 · 按产品形态划分'
m['total']={'label':'美国凉感床品市场总额','value':'尚无可核实的统一总额','period':'截至2026年11月6日','note':'统计应覆盖凉感床单、凉感被和凉感毯；其他床品单列。','source_keys':['gmr-sheets','indexbox-audit','comforter-size-audit','indexbox-demo'],'detail':'本轮复查的公开资料没有提供同一年、同一地区、边界一致的完整市场总额。各机构对“凉感”的定义不同，不能把不同估算拼接相加。'}
m['segments']=[
 {'id':'sheets','name':'凉感床单与床笠','definition':'床单套装、床笠及配套枕套','value':'约5.63亿美元','period':'2025年','kind':'第三方模型估算','share':'暂无同口径占比','source_keys':['gmr-sheets'],'detail':m['metrics'][0]['detail']},
 {'id':'covers','name':'有填充凉感被','definition':'被面＋填充，提供覆盖感','value':'暂无可靠规模','period':'—','kind':'未找到可复核数据','share':'暂无同口径占比','source_keys':['comforter-size-audit'],'detail':'公开页面的估算没有可复核的品类样本，不能据此计算份额。'},
 {'id':'blankets','name':'薄凉感毯','definition':'轻薄毯体，部分产品为双面设计','value':'暂无可靠规模','period':'—','kind':'未找到可复核数据','share':'暂无同口径占比','source_keys':['indexbox-demo'],'detail':'已查到的相关图表包含演示数据，未作为市场规模采用。'},
 {'id':'adjacent','name':'其他凉感床品','definition':'独立枕套、被套、枕头、保护垫等','value':'暂无可靠规模','period':'—','kind':'统计边界待补齐','share':'暂无同口径占比','source_keys':[],'detail':'配套枕套若已计入床单套装，不重复计入。床垫与主动控温设备作为相邻市场另列。'}]
m['share_note']='各品类缺少统一总额，暂不绘制市场占比图。'
m['adjacent_note']='床垫、褥垫及主动控温设备另作替代方案研究，不混入上述床单、被、毯数据。'
d['materials']['share_chart']=m.pop('share_chart')
m['excluded'].append({'source_key':'comforter-size-audit','reason':'凉感被占比与增速未找到可复算样本；演示图表不作为市场数据。'})

d['product_view']['title']='细分品类与代表产品'
d['product_view']['intro']='先看产品形态，再看同一品类内的材料与设计路线。'
d['product_view']['categories']=[
 {'id':'sheets','name':'凉感床单与床笠','summary':'铺在身体下方，重点比较触感、热湿感受和床垫贴合。','groups':[
  {'name':'竹源人造丝：混纺与纯纺','product_ids':['sheets','bedsure','cozyearth']},
  {'name':'莱赛尔与棉平纹','product_ids':['sijo','brooklinen']},
  {'name':'弹力排湿与相变调温','product_ids':['sheex-sheets','slumber']}],'growth_ids':[]},
 {'id':'covers','name':'有填充凉感被','summary':'盖在身体上，表层凉感、填充蓄热和覆盖感需要一起比较。','groups':[
  {'name':'接触凉感表层＋填充','product_ids':['cozy-comforter','rest']},
  {'name':'莱赛尔表层＋莱赛尔填充','product_ids':['buffy']}],'growth_ids':['rest-brand-growth']},
 {'id':'blankets','name':'薄凉感毯','summary':'以轻薄覆盖为主，注意双面材料、贴身感和滑落问题。','groups':[
  {'name':'凉感面与棉质面双面设计','product_ids':['elegear']}],'growth_ids':[]}]
d['product_view']['note']='价格和销量保留各自采集日期。跨平台、跨规格的数字不能直接当作销量排名；在售平台不等于销量最大的渠道。'
g=d['growth']['cards'][0]
g.update(name='REST：上线约一年半，品牌年销售额超过3,000万美元',scope='品牌整体，含多个市场及产品',period='历史案例；具体财年未披露',category='covers')
g['metrics']=[{'value':'3,000+','unit':'万美元','label':'品牌年销售额'},{'value':'约1.5','unit':'年','label':'上线至达到上述规模'},{'value':'+10','unit':'%','label':'案例报告的客单价提升'}]
g['sections']=[
 {'label':'','title':'卖给怕热的人','text':'Evercool把凉感和柔软作为主要购买理由，产品延伸至凉感被、床笠和枕套。','source_keys':['rest','rest-channel']},
 {'label':'','title':'让一笔订单买得更多','text':'Shopify案例称：增加支付方式、推荐相关产品和加购页面后，客单价提升10%。','source_keys':['rest-growth']},
 {'label':'','title':'增加销售渠道','text':'2025年3月宣布进入Mattress Firm线上渠道，销售Evercool系列。','source_keys':['rest-channel']}]
g['interpretation']='值得研究的是明确的怕热人群定位，以及围绕同一需求扩展配套产品。客单价提升有案例支持；这些动作各贡献多少销售增长，尚不能分开计算。'
g['caveat']='3,000万美元是品牌年销售额，不是美国凉感被单品销售额；该案例也不是近期同比增长榜。10%来自服务商案例，未披露独立对照。'

# Concrete need evidence is preserved; add cover-specific needs instead of reusing a sheet-only list.
n=d['needs']
def need(id,label,evidence,refs,independence,use):
 n['need_pool'].append(dict(id=id,need=label,role='补充需求线索',evidence=evidence,review_ids=[],review_labels={},independence=independence,use=use,refs=refs))
need('n22','盖住身体，有自己需要的覆盖感','有公开讨论参与者表示不能不盖东西睡觉，天热时仍改用床单覆盖。',['covering-need'],'覆盖感不能用温度代替；裸睡不闷热，仍可能不能满足这个人。','比较薄被、薄毯和床单覆盖，而非只与其他“凉感被”比较。')
need('n23','重量适合自己，不压身或轻得不习惯','凉毯讨论中有人嫌重；另一讨论中有人需要一定的被子重量才能睡。',['blanket-use','covering-need'],'偏轻与偏重是同一重量偏好的不同方向，不重复列为两层，也不认定越轻越好。','按实际重量与使用偏好分组测试，不把克重直接当成购买需求。')
need('n24','翻身时被子不滑落，身体仍能盖住','凉毯讨论中有使用者抱怨被子容易滑下床。',['blanket-use'],'初次能盖住，不代表翻身后仍盖得住；与柔软、凉感分别检查。','检查尺寸、垂坠和表面摩擦的组合效果。')
need('n25','买之前能判断凉感承诺是否可信','寻找凉感被的发帖者难以区分真实体验与广告，并因起球、退货等投诉犹豫。',['comforter-search'],'清楚成分仍可能不知道睡起来如何；可信的效果依据与正确发货不是同一个需求。','检查演示、测试条件与真实使用能否回答同一个效果问题。')
need('n26','同床两人的冷热和触感要求都能照顾到','床单讨论发帖者提出伴侣怕热、自己对触感敏感，必须同时满足。',['sheets-household'],'一个人觉得好用，另一个人仍可能不舒服；家庭选择不能只看单人的平均偏好。','先看是否能同时满足，冲突明显时再研究分侧或分开覆盖。')
n['groups'][0]['need_ids']+=['n22','n23','n24','n26']
n['groups'][-1]['need_ids']+=['n25']
n['title']='需求金字塔'
n['subtitle']='整体、凉感被和凉感床单分别研究；不预设固定层数。'
n['sample_note']='床单依据包括库中928条近期评论及单列的一星补充样本；凉感被补充多条公开讨论。公开讨论不构成代表性抽样，未用于推算需求比例。'
for item in n['need_pool']:
 if item['id']=='n12':
  item['evidence']+=' 凉毯讨论另有人因家中洗衣机装不下而需要送去自助洗衣店。'
  item['refs'].append('blanket-use')
 if item['id']=='n3':
  item['evidence']+=' 另一床单讨论中，有用户称使用约一年后破损，因而重新寻找产品。'
  item['refs'].append('sheets-durability')
 if item['id']=='n5':
  item['evidence']+=' 凉毯讨论也有人明确区分触摸时凉和使用久后变热。'
  item['refs'].append('blanket-use')
n['models']=[
 {'id':'all','name':'凉感床品整体','job':'少受闷热、汗湿和床品不适打扰','summary':'“凉”不是唯一要求：消费者同时考虑热湿感受、触感、日常使用和购买成本。','pyramid':{
  'status':'有条件的前提关系','scenario':'适用于因触感或基本适配问题而拒绝使用的人。',
  'levels':[{'id':'usable','label':'愿意贴身使用、能够正常铺盖','need_ids':['n1','n2','n14','n22']},{'id':'thermal','label':'进一步获得想要的热湿改善','need_ids':['n5','n6']}],
  'link_note':'R619因粗糙放弃凉感期待；R1389因套不上而否定购买。反例R718：凉感不足仍因舒服留下。不能把这一顺序推广给所有买家。','review_ids':[619,1389,718],'source_keys':['material-78','covering-need']},
  'clusters':[{'title':'主要痛点','items':[('n5','睡一段时间又变热'),('n6','出汗后床面湿黏'),('n1','触感粗糙，贴肤不舒服')]},{'title':'使用中的要求','items':[('n3','洗后和用久仍保持状态'),('n12','洗干省事'),('n13','没有难闻气味'),('n26','照顾同床两人的差异')]},{'title':'购买时的取舍','items':[('n8','买得起'),('n20','改善值得这个价钱'),('n25','效果承诺可信'),('n18','不合适能退换')]}],
  'independent_note':'耐用、价格、外观和洗护等需求可以与凉感同时存在，现有证据不支持统一排成高低层。',
  'source_keys':['material-78','cotton-survey','sheets-household','comforter-search']},
 {'id':'covers','name':'凉感被','job':'想盖着被子睡，又不想闷热出汗','summary':'凉感被要解决“盖着也舒服”。重量、覆盖感、滑落和洗护，不能照搬床单的研究维度。','pyramid':{
  'status':'待验证的场景层级','scenario':'适用于“不盖东西就睡不着”的人；不能用于所有怕热者。',
  'levels':[{'id':'cover','label':'保留自己需要的覆盖感','need_ids':['n22','n23']},{'id':'cover-thermal','label':'在盖着的前提下减少闷热与汗湿','need_ids':['n5','n6','n21']}],
  'link_note':'公开自述支持这类人存在，但尚不能证明人群大小。有人选择床单覆盖，有人保留较重被子再加送风；轻薄并非所有人的答案。','review_ids':[],'source_keys':['covering-need','blanket-use']},
  'clusters':[{'title':'覆盖与活动','items':[('n22','身体有覆盖，不必掀被才能凉'),('n23','轻重合适'),('n24','翻身后不滑落'),('n15','不黏身、不拖拽')]},{'title':'温湿感受','items':[('n4','碰上去就凉'),('n5','盖久也少闷热'),('n6','出汗后少湿黏'),('n21','需要时仍有适当暖意')]},{'title':'长期使用与购买','items':[('n12','家里的洗衣机能洗，容易干'),('n3','不因洗用而起球或失去手感'),('n25','能判断凉感效果'),('n8','价格在预算内'),('n18','试用不合适能顺利退换')]}],
  'independent_note':'“摸着凉”与“盖久不热”分开；轻重偏好和洗护条件另行比较，不把它们机械放在更高层。',
  'source_keys':['covering-need','blanket-use','comforter-search','reddit-rest']},
 {'id':'sheets','name':'凉感床单','job':'睡在清爽舒服、铺得稳的床面上','summary':'床单既要贴肤舒服，也要与床垫匹配。套得上和翻身不脱落是两个不同要求。','pyramid':{
  'status':'可检验的使用前提','scenario':'针对床笠的适配与固定；不是完整消费者偏好排名。',
  'levels':[{'id':'fit','label':'先能套住自己的床垫','need_ids':['n2']},{'id':'stay','label':'翻身后仍保持固定和平整','need_ids':['n10']}],
  'link_note':'尺寸不匹配时无法正常固定；能套上仍可能翻身脱落。触感、凉感、耐用是另外几项要求，不能由这两层直接推出。','review_ids':[1389,29,221],'source_keys':['material-78','material-89']},
  'clusters':[{'title':'贴肤与温湿','items':[('n1','柔软、不磨肤'),('n5','睡久不闷热'),('n6','出汗后少湿黏'),('n14','不痒、不刺激'),('n15','翻身不拖拽')]},{'title':'铺床与洗护','items':[('n2','尺寸和床垫厚度合适'),('n10','四角不弹开'),('n11','容易找方向和铺装'),('n12','洗干省事'),('n3','洗后不易破损、起球或变粗糙')]},{'title':'家庭与购买','items':[('n26','伴侣需求也被满足'),('n16','宠物毛易清理'),('n9','配色和外观合适'),('n8','价格可接受'),('n20','比替代品更值'),('n17','材质、套件与订单一致'),('n18','退换顺利'),('n19','按时收到')]}],
  'independent_note':'柔软与凉感可能分别成功或失败；不要把柔软好评直接解释成凉感购买动因。',
  'source_keys':['material-78','material-89','sheets-household','sheets-durability']}]
for model in n['models']:
 for cluster in model['clusters']:
  cluster['items']=[{'need_id':i,'text':text} for i,text in cluster['items']]
n['model_note']='图中只画有依据或明确待验证的局部前提关系。旁边列出并行需求；最终睡眠目标单列，不凑成更高一层。完整人群层级仍需消费者访谈验证。'

# Positioning maps reuse concrete needs, with category choices distinct from brand ownership.
mm=d['mindmap'];old=copy.deepcopy(mm['lanes'])
def lane(id,scope,entry,need_ids,category,alternatives,brands,known,sources):
 return dict(id=id,scope=scope,entry=entry,need_ids=need_ids,category=category,alternatives=alternatives,brands=[dict(product_id=p,concept=c,evidence=e) for p,c,e in brands],known=known,unknown='尚无无提示品牌提及和跨品牌认知调查；不判断谁已占领该心智。',source_keys=sources)
mm['scopes']=[{'id':'all','label':'凉感床品整体','title':'先看消费者把什么当成解决办法','summary':'同一个“睡觉太热”问题，可能先比较换床品、减少覆盖或主动控温，再在所选品类里选品牌。'},{'id':'covers','label':'凉感被','title':'围绕“盖着也不热”的品类选择','summary':'核心竞争不仅是其他凉感被，还包括薄毯、床单覆盖和保留被子后增加送风。'},{'id':'sheets','label':'凉感床单','title':'围绕“清爽、舒服的床面”的选择','summary':'消费者可能按材料名称、触感或调温技术筛选；商家想建立的关联与已被记住的关联需分开。'}]
mm['lanes']=[
 lane('all-cooling','all','整夜少闷热、少湿黏',['n5','n6'],'更换凉感床品',['更薄的普通床品','改变室温或床面送风'],[('sheets','为凉感而购买','consumer'),('rest','怕热者的凉感被','claim')],'床单原评论有明确凉感购买动机；公开讨论也出现先改善房间温度的选择。',['material-78','comforter-search','rest']),
 lane('all-touch','all','触感舒服，也能照顾家人',['n1','n26'],'舒适床品／熟悉的材料',['原品牌床品','不同纤维与织法'],[('cozyearth','柔软丝滑','claim'),('brooklinen','酒店式清爽触感','claim')],'同一家庭可能同时要求透气、平滑与耐用；不能假定单一凉感指标决定购买。',['sheets-household','cozyearth','brooklinen']),
 lane('all-cover','all','有覆盖感，又不想热',['n22','n23','n5'],'薄被／凉感被／凉感毯',['床单覆盖','保留较重被子并送风'],[('rest','凉与软兼顾','claim'),('elegear','双面凉感与棉质面','claim')],'公开讨论出现不愿放弃覆盖感的人，以及重量偏好相反的人。',['covering-need','blanket-use','rest','elegear']),
 lane('cover-touch','covers','盖上先觉得凉，盖久少闷热',['n4','n5'],'接触凉感被',['普通薄被','凉感薄毯'],[('rest','Evercool凉感','claim'),('cozy-comforter','双面凉感','claim')],'两家均明确宣传凉感；现有讨论说明瞬时凉与持久体验需要分别验证。',['rest','material-100','blanket-use']),
 lane('cover-light','covers','不想被厚被裹得闷热',['n5','n23'],'轻薄透气的被子',['空被套','普通薄被／床单覆盖'],[('buffy','莱赛尔表层和填充','claim')],'有消费者把“凉感”解释为替换过厚的原被子；具体材料只是可能的解决手段。',['comforter-search','buffy']),
 lane('cover-flex','covers','保留覆盖感，按冷热调整',['n22','n21','n23'],'可调整的覆盖组合',['薄毯叠盖','床面送风搭配原被子'],[('elegear','双面不同触感','claim')],'存在保留一定覆盖或重量的需求；不因此认定双面设计已解决所有冷热冲突。',['covering-need','reddit-rest','elegear']),
 lane('sheet-soft','sheets','柔软丝滑，又希望清爽',['n1','n5','n6'],'竹源人造丝／莱赛尔床单',['棉床单','原有套装'],[('sheets','为凉感买、因手感再买','consumer'),('bedsure','凉爽丝滑','claim'),('cozyearth','柔软高档体验','claim'),('sijo','轻盈吸湿','claim')],'Shilucheng有购买和再购自述，但尚不能据此判定消费者首先想到哪个品牌。',['material-78','bedsure','cozyearth','sijo']),
 lane('sheet-crisp','sheets','更喜欢清爽、不黏的触感',['n1','n15','n5'],'棉平纹床单',['丝滑型床单'],[('brooklinen','酒店式清爽棉平纹','claim')],'品牌明确使用清爽与透气表达；实际偏好和溢价需要与丝滑型消费者分开研究。',['brooklinen','sheets-household']),
 lane('sheet-fit','sheets','床面贴合，翻身后不松脱',['n2','n10'],'弹力床单／加固床笠',['普通床笠','其他固定结构'],[('sheex-sheets','弹力贴合','claim')],'床单评论确认适配与固定是独立问题；SHEEX主推弹力，但尚未证明消费者已将其与固定优势关联。',['material-114','material-78']),
 lane('sheet-temperature','sheets','少闷热，也不想忽冷忽热',['n5','n21'],'相变调温床单',['普通薄床品','调整室温或覆盖厚度'],[('slumber','吸热与释热调温','claim')],'Slumber Cloud明确宣传温度缓冲；消费者是否把“调温”作为独立品类仍待验证。',['slumber','outlast','reddit-rest'])]
mm.update(title='心智地图',subtitle='需求入口 → 品类及替代选择 → 品牌关联',status='认知线索图',intro='实心节点表示有消费者自述，描边节点表示商家宣传；节点位置不代表品牌排名。',validation_needed='尚缺品牌无提示提及率、第一选择和愿付溢价；本图可用于确定研究方向，不能当成心智占有率或已确认市场空白。')
mm['opportunities_title']='从地图继续验证的方向'
mm['opportunities']=[
 {'scope':'covers','title':'凉感被：保留覆盖感，同时减少闷热','basis':'有些人不能接受不盖或太轻的方案。先比较覆盖、重量与热湿表现的组合。','boundary':'需求已出现，规模、竞品满足程度和愿付价格未验证。','source_keys':['covering-need','blanket-use']},
 {'scope':'sheets','title':'凉感床单：凉爽、触感与长期使用一起兑现','basis':'有消费者同时要求透气、平滑、耐用；新买好用并不等于长期值得。','boundary':'还需比较同价位竞品和实际寿命，不能仅凭投诉宣布机会。','source_keys':['sheets-household','sheets-durability']}]
d['footer']['gaps']=['美国凉感床品统一市场总额与品类占比','各产品同周期销量与跨平台销售拆分','完整消费者需求层级','品牌心智位次与溢价验证']
d['footer']['text']='正文优先显示可用事实与研究结果；来源、未采用数据和待补内容保留在这里。'
(Path(__file__).parent/'01_核定内容.json').write_text(json.dumps(d,ensure_ascii=False,indent=2))
print('content ready:',len(d['products']),'products,',len(n['need_pool'])-1,'needs,',len(d['sources']),'sources')
