from pathlib import Path
from datetime import datetime
from zipfile import ZipFile
import csv, json, re, shutil, sqlite3, sys, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DATA = ROOT / 'data'
ATT = DATA / 'attachments'
NOW = datetime.now().astimezone().isoformat(timespec='seconds')
sys.path.insert(0, str(ROOT))
import reports, report_framework

names = {
 'B0DXCC6P1Z':'埃及棉床单套装', 'B0FWY1TGFK':'凉感床单四件套', 'B0DSZCWGVP':'埃及长绒棉床单四件套',
 'B0DKBW34X4':'纯棉被套', 'B09PYKYCCF':'竹源粘胶床单四件套', 'B0DP8MYZLB':'亚麻被套',
 'B0D8SZWW1P':'法国亚麻床单', 'B0F2TDDFGJ':'加深床笠竹源粘胶床单', 'B0FSS6L11T':'鹅绒羽毛枕双只装',
 'B0GG8R7G4C':'鹅绒被', 'B0G9N5WTXW':'竹源粘胶被套', 'B0FG7NZVYL':'鹅绒枕单只装（Queen）',
 'B0DP8P4KM9':'亚麻装饰枕套', 'B0FFG8RRPD':'羊毛地毯', 'B0G3PS161X':'加深床笠埃及长绒棉床单',
 'B0GHQRBJ2D':'有机棉床单', 'B0D313RMST':'莱赛尔床单', 'B0FG7LZXRM':'鹅绒枕单只装（Standard）',
 'B0DRP1VCCP':'可水洗地毯', 'B0G9LDZ6Y7':'竹源粘胶面料被', 'B0F2H8L1BG':'吉萨棉床单',
 'B0F3HW6TPG':'棉床单六件套', 'B0GKMFX95L':'桑蚕丝床单四件套'
}
rows={}
for f in ['amazon_page1_cards.json','amazon_page2_cards.json','amazon_top_cards.json']:
 for r in json.loads((HERE/f).read_text()):
  m=re.search(r'销售额[：:]\s*\$([\d,]+)',r['text'])
  n=re.search(r'近30天销量\(父体\):\s*([\d,]+)',r['text'])
  if m and n:
   a=r['asin']; rows[a]={'ASIN':a,'产品系列':names.get(a,r.get('title','')),'近30天父体销量_第三方估算':int(n[1].replace(',','')),'销售额美元_插件展示':int(m[1].replace(',','')),'商品链接':'https://www.amazon.com/dp/'+a,'采集时间':NOW,'口径':'父体销量×代表规格展示价的粗估；非后台成交额','原始页面文字':r['text']}
assert len(rows)==23, len(rows)
total=sum(r['销售额美元_插件展示'] for r in rows.values())
assert total==1112904,total
csvpath=ATT/'Shilucheng_Amazon销售估算明细_20261106.csv'
with csvpath.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(next(iter(rows.values()))));w.writeheader();w.writerows(rows.values())

hist={}
for asin in ['B0DXCC6P1Z','B0FWY1TGFK']:
 src=Path('/Users/voidengine/Downloads')/f'US-{asin}-sales-20261106.xlsx'
 dest=ATT/src.name;shutil.copy2(src,dest)
 with ZipFile(src) as z:
  ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
  ss=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml'))] if 'xl/sharedStrings.xml' in z.namelist() else []
  out=[]
  for rr in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('.//m:row',ns):
   vals=[]
   for cell in rr:
    v=cell.find('m:v',ns);x=v.text if v is not None else ''.join(cell.itertext());vals.append(ss[int(x)] if cell.get('t')=='s' else x)
   if vals and re.fullmatch(r'202[56]-\d\d',vals[0]):out.append({'month':vals[0],'units':int(vals[1]),'gmv_usd':int(vals[2])})
  hist[asin]=out
(HERE/'sales_history_parsed.json').write_text(json.dumps(hist,ensure_ascii=False,indent=2))

method='''# Shilucheng：销售规模、渠道结构与增长核查

核查日期：2026年11月6日。范围：美国电商；美元；零售成交额估算，不是公司的财务收入。

## 可以用于业务判断的结果

**Amazon与TikTok是已经找到较大销售规模证据的两个核心渠道。当前模型中Amazon较大；不能据此认定它在所有年份、所有国家都排名第一。**

| 渠道 | 销售规模估算 | 基准情景 | 占两渠道合计的比例 |
| --- | --- | --- | --- |
| [Amazon美国](https://www.amazon.com/s?me=AHKCVOX33TXTW&marketplaceID=ATVPDKIKX0DER) | 近30天约80万—140万美元 | 110万美元 | 约65% |
| [TikTok美国：Shilucheng Home](https://shop.tiktok.com/us/store/shilucheng-home/7495541840241986289) | 按最近约32小时速度折算，约30万—100万美元/月 | 60万美元/月 | 约35% |
| 合计 | 约110万—240万美元/月 | 170万美元/月 | 100% |

两渠道维持该水平12个月，对应约1,320万—2,880万美元的年化量级。**这是当前销售速度的换算，不是2026年全年销售额或未来收入预测。** 季节性、促销和库存会使实际全年结果不同。Amazon覆盖家纺及地毯等产品；TikTok店铺也有少量其他品牌商品，尚未取得其当期成交占比，不能完全等同于Shilucheng品牌净额。全球收入和其他渠道应另加，不能记为零。

## Amazon：已取得销售估算，而不只是评论数量

读取卖家AHKCVOX33TXTW的两页目录，共32个搜索结果。卖家精灵对其中23个系列展示近30天父体销量与销售额，合计1,112,904美元。按搜索结果系列初筛、ASIN去重，没有将同一系列所有颜色和尺寸逐一相加。尚未逐个取得后台父体ID，不能声称已完成完整父体审计。

插件展示额基本等于“父体销量×当前选中的规格价格”。不同尺寸价格、优惠券、历史折扣、父体调整和估算误差都会影响结果。因此采用80万—140万美元的工作区间（约为展示合计上下浮动25%，取整），基准110万美元。**这个范围是研究敏感性区间，不是统计置信区间，也不保证包含真实值。** 未出数的9个结果不按零销量处理；当前仅覆盖该卖家可见目录，不代表品牌在Amazon的全部卖家。

主要系列：埃及棉床单约27.1万美元；凉感床单四件套约10.6万美元；亚麻被套约10.6万美元；法国亚麻床单约8.7万美元。明细CSV保留全部23条记录、商品链接及插件原文。

## TikTok：按直接记录的短期变化估算

同一店铺的两次直接观察：2026-11-04 20:43:29（北京时间）显示累计687.6K；2026-11-06 04:40:07显示688.2K。相隔31.94小时，展示值增加约600件，约451件/天。K位取整使实际差值可能约500—700件；计数刷新、退货调整也会影响差值。

店内畅销床单起价约32美元，褥垫约42—58美元，亚麻产品价格更高。采用每件成交均价35—55美元的假设；45美元为基准，未声称它是实测平均成交价。计算为：600÷31.94×24×30×45≈60.9万美元/月。只考虑取整和均价的范围约39万—87万美元，再放宽为30万—100万美元，以反映短期波动。**不足两天的记录不能代表完整近30天，因此本项可信度低于Amazon。**

[Gloda历史报道](https://www.gloda.vip/en/content/detail/6817)列出2025-01-19至25日同名店铺3,413件、GMV129,600美元，平均37.98美元/件。该报道只用于检查均价假设是否明显偏离历史量级，不当作当前销售额，也不用其含糊的QoQ表述计算增长。

## 各渠道占比：分母必须写清

65%与35%是基准情景中Amazon和TikTok两渠道内部的比例，**不是品牌全渠道占比**。独立取上下界时，Amazon占两渠道合计可落在约44%—82%，这说明精确占比仍很不稳定。

若业务讨论需要暂时考虑其他渠道，可用以下压力测试。其他渠道比例是人为设定的假设，不是已调查出的份额，不能选一个数作为事实发布。

| 假设其他渠道占品牌总额 | Amazon占品牌总额 | TikTok占品牌总额 | 对应品牌月规模（基准两渠道170万美元） |
| --- | --- | --- | --- |
| 0%（仅计算已量化渠道） | 64.7% | 35.3% | 170万美元 |
| 10% | 58.2% | 31.8% | 约189万美元 |
| 20% | 51.8% | 28.2% | 约213万美元 |

不能继续把这个余量无依据地拆成Walmart、官网和线下份额。要拆分，至少需要对应期间的可归属产品销量，或站点访问量、转化率和客单价。

## Walmart与独立站：实际查到什么

[Walmart品牌页](https://www.walmart.com/brand/shilucheng/10006451)确实存在，但其跳转商品出现归属冲突：[微纤维床单](https://www.walmart.com/ip/3692691653)标题保留Shilucheng、品牌链接显示KATOON；[竹源床单](https://www.walmart.com/ip/2838626570)标题和正文已显示KATOON。[褥垫](https://www.walmart.com/ip/3263256486)仍以Shilucheng命名，显示496个评分，未取得可用的期间销量。评分累计不能推成当月成交额。这些渠道归属应核实后再加总，不能因为有品牌入口就算作品牌直营销售。

[独立站](https://shilucheng.com)有产品目录和购买入口，但本轮未取得可复核的月访问量、转化率或订单量。故不能给出有依据的独立站销售额区间。线下及其他国家同样未量化，不按零处理。

## 增长：Amazon主力床单近期回升；最快渠道未定

卖家精灵导出的历史数据：

| Amazon产品系列 | 2026年9月估算销售额 | 2026年10月估算销售额 | 变化 |
| --- | --- | --- | --- |
| [埃及棉床单B0DXCC6P1Z](https://www.amazon.com/dp/B0DXCC6P1Z) | 87,663美元 | 344,127美元 | +292.6% |
| [凉感床单B0FWY1TGFK](https://www.amazon.com/dp/B0FWY1TGFK) | 54,225美元 | 140,121美元 | +158.4% |
| 两个系列合计 | 141,888美元 | 484,248美元 | +241.3% |

两条序列在2026年4—8月有明显低谷，当前只能描述插件记录中的回升；不能认定全部由真实需求增长造成，库存、链接和父体变化或监测缺失尚未排除。11月是未结束月份，不参与月环比。

**业务结论：Amazon应与TikTok一并作为重点竞争渠道；近期增长研究优先核查Amazon主力床单的回升。仍不能把Amazon或TikTok定为品牌增长最快渠道，也没有充分依据给出品牌整体同比增长率。** 这需要两渠道相同期间的月销售序列，而不是累计销量的大小。

## 已排除的误用

- FindNiche的11月榜单仍显示店铺累计284.58K，与10月版数值相同，而平台已显示688.2K；不拿更新的榜单日期冒充最新销量，也不算出虚假的短期增长。
- 不把Amazon卖家累计反馈数当作近12个月反馈数，不用留评数乘一个任意倍数推销售额。
- 不把TikTok累计68.82万件乘当前售价，写成2026年收入。

资料完整性：已获得可量化的两大渠道估算；未获得全渠道财务实绩、完整年度收入和跨渠道同周期增长排名。
'''
methodpath=ATT/'Shilucheng_销售规模与渠道估算_20261106.md';methodpath.write_text(method)

c=sqlite3.connect(DATA/'library.sqlite3');c.row_factory=sqlite3.Row
backup=HERE/'library_before_channels.sqlite3'
if not backup.exists():
 b=sqlite3.connect(backup);c.backup(b);b.close()
doc=json.loads(c.execute("SELECT document FROM brand_reports WHERE brand_id='shilucheng'").fetchone()[0])
(HERE/'brand_report_before.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2))
topic='2. 经营规模与渠道结构'
def material(title,path,source_type,summary,url=None):
 mid=c.execute('INSERT INTO materials(title,url,source_type,publisher,retrieved_at,summary,local_path,access_note) VALUES(?,?,?,?,?,?,?,?)',(title,url,source_type,'Breescape竞争研究 / 原始来源见附件',NOW,summary,'attachments/'+path.name if path else '', '估算、事实及假设在正文中分别标明')).lastrowid
 c.execute('INSERT INTO material_links(material_id,brand_id,product_id,section,topic) VALUES(?,?,NULL,1,?)',(mid,'shilucheng',topic));return mid
mm=material('Shilucheng销售规模与渠道估算｜2026-11-06',methodpath,'研究估算方法与来源','两渠道销售规模、占比、增长核查及未覆盖范围；不是财务营收。')
ma=material('Amazon｜23个系列近30天销售估算明细',csvpath,'第三方工具估算','卖家精灵实时页面读取；32个结果中23条有数，展示合计1,112,904美元。')
mh=[]
for a in hist:mh.append(material('卖家精灵销量历史｜'+names[a],ATT/f'US-{a}-sales-20261106.xlsx','第三方工具原始导出','逐月销量与销售额估算，含未结束月份；不是卖家后台实绩。'))
tkproof=ATT/'Shilucheng_TikTok店铺核查_20261106.txt'
tkproof.write_text('原始页面：https://shop.tiktok.com/us/store/shilucheng-home/7495541840241986289\n采集：2026-11-06T04:40:07+08:00\n'+(HERE/'tiktok_shop_20261106.txt').read_text())
mt=material('TikTok｜店铺累计销量新快照',tkproof,'平台页面记录','2026-11-06 04:40:07直接显示688.2K累计售出；历史快照687.6K见材料4/24。')
def record(title,body,evidence,kind='分析'):
 return c.execute('INSERT INTO records(brand_id,product_id,section,topic,title,body,kind,status,evidence,updated_at) VALUES(?,NULL,1,?,?,?,?,?,?,?)',('shilucheng',topic,title,body,kind,'已复核' if kind=='分析' else '已核实页面信息',json.dumps(evidence),NOW)).lastrowid
ra=record('美国两大渠道销售规模：区间估算而非财务收入','美国Amazon和TikTok两渠道当前销售量级合计约110万—240万美元/月，基准170万美元/月。若维持12个月，年化约1,320万—2,880万美元，不是全年实绩。Amazon约80万—140万美元/近30天，来自23个系列的卖家精灵估算；TikTok约30万—100万美元/月，来自约32小时累计件数变化与每件35—55美元均价假设。两渠道时期与方法不同，不能伪装为同月审计结果。Walmart、独立站、线下、其他国家未量化；TikTok店内少量其他品牌尚未完全剔除。',[mm,ma,mt,4])
rc=record('各渠道销售额与占比｜基准情景', '''| 渠道 | 销售规模估算 | 占已量化两渠道的比例 |
| --- | --- | --- |
| [Amazon美国](https://www.amazon.com/s?me=AHKCVOX33TXTW&marketplaceID=ATVPDKIKX0DER) | 80万—140万美元／近30天；基准110万美元 | 约65% |
| [TikTok美国](https://shop.tiktok.com/us/store/shilucheng-home/7495541840241986289) | 30万—100万美元／月；短期速度折算，基准60万美元 | 约35% |
| [Walmart美国](https://www.walmart.com/brand/shilucheng/10006451) | 部分商品已显示其他品牌，期间销售额未能归属 | 未计入分母，不是0% |
| [独立站](https://shilucheng.com/) | 未取得流量、转化率或订单量，不能据此估计 | 未计入分母，不是0% |
| 线下及其他国家 | 未量化 | 未计入分母，不是0% |

65%和35%只表示两个基准估算的比例，不是品牌全渠道份额。完整区间、均价假设与其他渠道压力测试见方法附件。''',[mm,ma,mt,4,11,6])
rg=record('近期增长：Amazon两组主力床单估算回升', '''| Amazon产品系列 | 9月销售额估算 | 10月销售额估算 | 环比 |
| --- | --- | --- | --- |
| [埃及棉床单](https://www.amazon.com/dp/B0DXCC6P1Z) | 8.77万美元 | 34.41万美元 | +292.6% |
| [凉感床单四件套](https://www.amazon.com/dp/B0FWY1TGFK) | 5.42万美元 | 14.01万美元 | +158.4% |
| 两个系列合计 | 14.19万美元 | 48.42万美元 | +241.3% |

时期为2026年9月和10月。来自卖家精灵历史估算，原始XLSX已保存。两条序列4—8月有异常低谷，尚未排除库存、链接或父体变化及监测缺失；不能推为整个Amazon渠道或品牌的增长率。TikTok未获得同期月度数据，最快渠道不能可靠排名。''',[mm]+mh)
rs=record('核心销售渠道判断','Amazon与TikTok是已有较大销售规模证据的两个核心渠道；当前基准估算中Amazon较大。Amazon在埃及棉、亚麻、竹源粘胶等多个系列都有销售估算，不能从TikTok竹混纺床单的高累计销量推断它是全品牌唯一主力。Walmart归属、官网规模未清，现阶段不将双渠道比例写成品牌全渠道比例。',[mm,ma,mt])

c.execute("UPDATE records SET body=?,updated_at=? WHERE id=4",('2026-11-06更新：已经形成美国Amazon与TikTok两大渠道的销售区间估算和基准占比，详见新研究条目及方法附件。仍未取得全渠道财务收入、各渠道同周期月度序列；不能声称已核实品牌全年收入或最快增长渠道。',NOW))
old=c.execute('SELECT body FROM records WHERE id=29').fetchone()[0]
old=old.replace('有商品展示；是否直营及线下铺货未证实','品牌页存在，但部分跳转商品已显示KATOON；需核对归属后再计收入').replace('以上可确认渠道入口，不能得出各渠道销售占比或哪个渠道增长最快。','入口与归属核查保留于此；新的销售规模估算见本项其他研究记录。')
c.execute('UPDATE records SET body=?,updated_at=? WHERE id=29',(old,NOW))
t=doc['sections'][0]['topics'][1]
t.update(record_ids=list(dict.fromkeys(t['record_ids']+[ra,rc,rg,rs])),answer_type='分析判断',gap='全渠道收入与占比、同周期渠道增长排名仍缺少关键数据；两大渠道已形成可复算区间。')
answers={
 'scale':dict(answer='美国Amazon与TikTok两渠道，当前合计约110万—240万美元/月。若维持12个月，对应约1,320万—2,880万美元的年化量级；这不是品牌全年收入。',record_ids=[ra],note='截至2026年11月6日的工作估算；不含未量化渠道，亦非全球收入。品牌整体同比增长尚不能确认。'),
 'channels':dict(answer='基准情景：Amazon约110万美元/月，TikTok约60万美元/月；两渠道内部占比约65%和35%。',record_ids=[rc,ra],tables=[{'record_id':rc,'mode':'analysis','purpose':'core','caption':'渠道销售规模与两渠道内部占比｜研究估算'}],note='Amazon采用近30天工具估算；TikTok采用约32小时销售速度折算。65%／35%不是全品牌份额；未量化渠道不按零处理。'),
 'main':dict(answer='Amazon与TikTok均为核心销售渠道；当前估算以Amazon较大。',record_ids=[rs],note='这一判断限于已量化的美国渠道。Amazon在多个床品系列有销售积累，TikTok不能仅凭累计销量被认定为全品牌第一渠道。'),
 'growth':dict(answer='已找到Amazon主力床单近期回升的证据；尚不能确认品牌增长最快的渠道。',record_ids=[rg],points=[{'title':'两组主力床单：10月合计估算48.42万美元，比9月增加241.3%。','detail':'这是两个产品系列的工具估算变化，不能扩大成Amazon全店或品牌增速。','evidence':''}],tables=[{'record_id':rg,'mode':'analysis','purpose':'support','caption':'查看9—10月增长数据及商品链接'}],note='历史序列存在低谷，库存及链接变化等原因未排除；TikTok缺少同期月度序列，暂不做跨渠道增速排名。')
}
for q in t['questions']:
 q.update(answers[q['framework_key']]);q.update(answer_status='部分回答',presentation='answer' if q['framework_key'] in ('channels','growth') else 'fact')
 if q['framework_key']!='channels' and q['framework_key']!='growth':q.pop('tables',None)
doc['profile'][2]={'label':'核心销售渠道','value':'Amazon与TikTok','detail':'两渠道当前估算合计110万—240万美元/月；全渠道收入尚未量化。','record_ids':[ra,rs]}
doc['summary']=doc['summary'].replace('品牌整体销售结构与长期优势尚未确定。','Amazon与TikTok均有较大销售规模证据；全渠道收入与长期优势仍需进一步核实。')
doc['summary_record_ids']=list(dict.fromkeys(doc['summary_record_ids']+[ra,rs]))
doc['scope']=doc['scope'].replace('2026年11月4—5日','2026年11月4—6日')
doc['sections'][0]['boundary']='销售规模为工作估算，平台累计件数、近期销售速度和年度收入分别记录；区间假设与完整计算保存在依据中。'
doc['sections'][0]['reviewed_revision']=reports.section_revision(c,'shilucheng',1)
doc['sections'][0]['updated_at']=NOW
doc['reviewed_revisions']['1']=doc['sections'][0]['reviewed_revision']
doc['updated_at']=NOW
report_framework.validate_document(doc,[r['id'] for r in c.execute("SELECT id FROM products WHERE brand_id='shilucheng'")])
c.execute('UPDATE brand_reports SET document=?,updated_at=? WHERE brand_id=?',(json.dumps(doc,ensure_ascii=False),NOW,'shilucheng'))
c.commit()
print(json.dumps({'records':[ra,rc,rg,rs],'materials':[mm,ma,mt]+mh,'amazon_display_sum':total,'method':str(methodpath),'backup':str(backup)},ensure_ascii=False))
