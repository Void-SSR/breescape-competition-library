from pathlib import Path
import sqlite3,json,hashlib,shutil,copy,re,sys
ROOT=Path(__file__).resolve().parents[2];P=Path(__file__).resolve().parent
B=ROOT/'data/backups/before_review_sync_v1.2_20261105';SRC=ROOT/'research/评论全量语义分析_20261105'
sys.path.insert(0,str(ROOT));import reports
base={r['id']:r for r in json.loads((B/'records.json').read_text())};docbase=json.loads((B/'shilucheng_report.json').read_text());doc=copy.deepcopy(docbase)
STAMP='2026-11-05T12:00:00+08:00'
from datetime import datetime
from zoneinfo import ZoneInfo
STAMP=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
files=[('statistics','05_分来源主题统计.csv','主样本及补充组主题统计'),('behavior','05_behavior_counts.json','分层购买行为统计'),('rules','01_rules_v1.2.md','语义口径与计数规则'),('reviews','04_逐条评论与编码.csv','逐条原文、来源与编码'),('annotations','04_全部证据标注.csv','全量原文引句与语义标注'),('examples','07_关键证据与反例.md','关键证据与反例'),('conclusion','08_研究结论与机制修订建议.md','评论研究结论与机制建议')]
changes={}
def setr(i,**kw):changes.setdefault(i,{}).update(kw)
def replace(i,old,new):
 body=changes.get(i,{}).get('body',base[i]['body']);assert old in body,(i,old);setr(i,body=body.replace(old,new))
setr(11,body='1,628条既有评论已逐条完成语义编码，未增删原评论。商品ID均对应1729438233542234865；1,615条有平台评论ID且无重复，13条推荐样本缺平台ID。原有地区与来源缺失仍如实保留。\n\n近期全星级928条、额外一星687条、推荐13条分别处理。采集不是随机抽样，也不是连续日期全量；历史“有效”是原采集筛选口径，本轮不借编码重新筛掉泛评、未决或对象不明记录。多标签计评论条数，不计独立消费者或交易数。')
setr(12,kind='分析',status='已复核',body='2026-09-24—11-04的928条近期全星级便利样本。以下为明确提及目标商品具体体验的评论条数及占主样本比例，不代表总体消费者满意率、购买原因占比或销量贡献。\n\n| 具体体验 | 正面评论／占主样本 | 负面评论／占主样本 |\n| --- | --- | --- |\n| 柔软／粗糙／僵硬 | 397／42.8% | 92／9.9% |\n| 温度相关体验 | 176／19.0% | 72／7.8% |\n| 尺寸／深度适配 | 101／10.9% | 38／4.1% |\n\n正面适配101条与颜色94条接近；负面适配38条与滑脱35条接近，第三名不宜强调为稳定优势或首要问题。未决边界情景中滑脱可到38条与适配明确负面持平，不是新增实测结果。\n\n温度正面176条包括172条凉感／少热少汗、2条保暖、2条未细分调温；负面72条含71条不够凉／偏热等和1条怕冷者嫌不够暖（R642）。同条可有多主题、同主题褒贬并存；各项不能相加为人数。R888明确肯定床笠、同时说另一张床单太小，正负分别保留；101条原已含它。')
setr(13,body='凉感进入部分人的明确购买理由（R452、R917），价格或促销触发下单（R475、R1389）；这些是选择线索，不能由所有买后好评反推购买动机。R912因热潮红寻找床品，但未证明症状改善或细分市场规模。\n\n柔软有较广泛的样本内认可，凉感、触感、适配与材料预期仍有落差（R619、R453、R535）。保留也有不同原因：R718不觉得凉而因舒适继续用，R834因急需而保留。主样本13条明确分次／追加下单、21条可能再购且顺序未明；多套和未来意愿独立保留，不计算复购率。\n\n样本内编码与统计已完成；真实驱动的总体权重、未购买者选择、需求规模与付费意愿仍不能从本样本确定。')
setr(40,body='| 来源组 | 条数 | 评论发表时间 | 用途 |\n| --- | --- | --- | --- |\n| 近期全部星级 | 928 | 2026-09-24—11-04 | TOP3分母；便利样本 |\n| 额外一星 | 687 | 2026-05-26—09-24 | 单列失败情境，不估总体风险率 |\n| 推荐展示 | 13 | 2025-08-20—2026-07-10 | 个案例证，缺平台评论ID |\n\n主样本含与一星补采重叠的129条，已经计入928条一次；687条为此外的额外一星。三组时期和筛选方法不同，不能把组间差异解释为近期质量改善或恶化。\n\n额外一星具体负面前三项：温度198／28.8%、触感188／27.4%、材料说明／预期落差98／14.3%。仅描述这687条被筛出的一星评论。原全库星级构成仍为一星820、二星66、三星76、四星77、五星589，不能当商品总体评价分布。')
setr(52,title='评论关键证据：购买、保留、再购与反例',kind='分析',status='已复核',body='以下原文均出自已完成的v1.2逐条语义分析；用于证明具体路径及边界，不把个案频率当销售贡献。R编号可查看完整原文与采集来源。\n\n| 判断 | 支持证据 | 反例或边界 |\n| --- | --- | --- |\n| 凉感可以进入购买决策 | R452、R917明确称因凉感买 | R619期待凉感但无法接受粗糙；不能把买后优点全部倒推为动机 |\n| 保留理由可不同于试购理由 | R718不凉但因舒适继续用 | R834因急需保留，不等于满意 |\n| 部分体验后有追加购买 | R580因触感两次下单；R499试用后追加五套 | R1408后购颜色触感较差；不证明材料或生产改变 |\n| 材料描述影响预期 | R453若早知混纺便不买；R535原想买纯竹版本而退货 | 评论是自述，不是材料检测 |\n| 多套不能自动算复购 | R824第三套且自述比Sam’s便宜舒服 | 套数不是第三次下单；个人参照不是同条件性能排序 |\n\nR1389只说等促销购买后不适配，没有退货自述。R1284同款历史柔软与本次粗糙均保留，但分次下单顺序未明；R888部件褒贬分开。旧22条定性摘记保留为历史选例，不承担正式占比计算。')
replace(53,'评论全量','评论全量') if False else None
setr(53,title='历史检索索引：仅用于找原文，正式统计见v1.2')
replace(53,'框架要求的认可/不认可TOP3及占比尚未完成。','正式认可／不认可TOP3及占比已由v1.2逐条语义分析完成，见研究记录12及其分层统计附件。本条保留历史索引，不作为认可率或主题排名依据。')
setr(14,body='价格、概念／需求、内容、体验、促销、渠道、口碑、规格、再购与先发继续分别检验。新增v1.2评论结果强化了部分试购、保留与追加下单路径；没有解决各因素销售贡献、最初走红、盈利质量及竞品实测领先的问题。')
setr(54,body='竹／凉感升级期待进入部分人的选择，买后柔软／舒适可支持继续使用及追加下单：R452与R917为凉感买；R718不觉得凉仍因舒适继续用；R580与R499明确追加。主样本柔软正面397／928，并非柔软对销量贡献42.8%。\n\nCGK与LDC也使用软、凉、深口袋表达；不能把Shilucheng的认可点称为独占优势。R1408颜色间触感差异、R453与R535材料预期落差显示机制存在中断点。品牌复购率、独立买家人数和客观性能领先均未确定。')
setr(66,body='v1.2已对全部1,628条既有评论逐条编码，分928／687／13三组；本表选例用于连接购买路径，不以选例数量估计驱动权重。早期210条检索候选和47条摘记保留历史版本。\n\n| 环节 | 可追溯原评论 | 支持与边界 |\n| --- | --- | --- |\n| 愿意尝试 | R452、R917因凉感买；R912因热潮红寻找床品 | 凉感进入部分选择；不证明多数人的首要动机或医学效果 |\n| 此时下单 | R475看到合适价格；R1389等促销后买 | 价格与时机有作用；R1389随后不适配不满，未陈述退货 |\n| 信息参与选择 | R1409谈视频引起的软凉期待；R1618因凉感评论买 | 不归因到TOP5某条视频；R1618为推荐样本，只作个案 |\n| 继续使用 | R718不凉但因舒适继续用；R834因急需保留 | 保留不等于凉感兑现，也不必然等于满意 |\n| 购买多件 | R692为赠品买三套；R469买两套 | 不等于多名新客或多次下单；赠品条款不代表当前活动 |\n| 追加购买 | R580因触感两次下单、R499试用后追加；R1408后购颜色粗糙 | 主样本13条明确、21条可能再购；多套／意愿分开；R1284顺序未明 |\n| 竞争参照 | R824称比Sam’s便宜舒服；R773认为比更好竹床单便宜不够多 | 旧床品与零售参照不同，不是同条件性能排序；R824仅第三套 |')
replace(67,'同规格LDC更便宜；另有因体验退货','同规格LDC更便宜；R1389促销后因不适配不满，未说退货')
replace(67,'柔软、贴合、舒适促成部分再购；有人不觉得凉仍认可','柔软正面397／928；R718因舒适继续用，R580因触感追加')
replace(67,'也有人粗糙、脱角、换色后失望','也有粗糙、滑脱、换色后失望；温度正面176不全是凉感成功')
replace(67,'颜色选择、换色、为家人添置；多规格合于一链接','换色及家庭多床线索；主样本13条明确追加、21条可能再购')
replace(67,'一次多件≠持续复购','一次多件≠分次购买，未来意愿≠已发生订单')
replace(68,'体验满意后出现换色、家庭扩展和再购','部分人的柔软／舒适体验支持保留或追加；换色、家庭多床与赠礼另有扩展线索')
replace(68,'| 让人再买 | 触感和适配满足后，换色或给家人添置 | 有已发生复购和相反案例；未测复购率 |','| 让人保留或再买 | R718因舒适继续用；R580、R499明确体验后追加 | 13条明确、21条可能再购；R1408存在反例，不是复购率 |')
replace(10,'仍待消费者主题编码、同条件体验比较及销售归因证据','消费者主题编码与样本内统计已完成；仍待同条件体验比较及销售归因证据')
replace(21,'仍缺完整消费者主题编码、跨产品的品牌认知与选择证据','单品评论已完成分层语义编码；仍缺跨产品的品牌认知与选择证据')
replace(58,'目标床单评论证据摘记','目标床单v1.2分层语义分析')
replace(58,'当前选例没有形成足够证据','现有单品样本仍没有形成足够证据')
replace(59,'部分消费者的产品复购自述','部分消费者明确分次／追加下单的自述（与可能再购、多套和意愿分开）')
replace(72,'此次单品研究显示','此次单品研究及分层评论证据支持一种阶段性解释：')
# Fixed publication copies. No replacement of original files.
folder=ROOT/'data/attachments/评论语义 v1.2_20261105';folder.mkdir(exist_ok=False)
pub=[]
for key,name,title in files:
 shutil.copy2(SRC/name,folder/name);h=hashlib.sha256((folder/name).read_bytes()).hexdigest();assert h==hashlib.sha256((SRC/name).read_bytes()).hexdigest()
 pub.append({'key':key,'filename':name,'title':'床单评论 v1.2｜'+title,'sha256':h,'local_path':str((folder/name).relative_to(ROOT/'data'))})
c=sqlite3.connect(ROOT/'data/library.sqlite3');c.row_factory=sqlite3.Row;c.execute('PRAGMA foreign_keys=ON');c.execute('BEGIN IMMEDIATE')
try:
 for i in changes:assert dict(c.execute('select * from records where id=?',(i,)).fetchone())==base[i],f'研究记录{i}已变化，停止覆盖'
 assert json.loads(c.execute("select document from brand_reports where brand_id='shilucheng'").fetchone()[0])==docbase,'报告已变化，停止覆盖'
 for f in pub:
  mid=c.execute('insert into materials(title,source_type,publisher,published_at,retrieved_at,summary,local_path,access_note) values(?,?,?,?,?,?,?,?)',(f['title'],'本地语义研究','Breescape研究','2026-11-05',STAMP,'固定v1.2发布副本；源于既有1,628条评论。',''+f['local_path'],'样本内研究；非平台统计、总体满意率或销量因果。SHA-256：'+f['sha256'])).lastrowid;f['material_id']=mid
  for sec,topic in [(2,'5. 消费者评论分析'),(2,'6. 产品卖得好的原因')]:
   c.execute('insert into material_links(material_id,brand_id,product_id,section,topic) values(?,?,?,?,?)',(mid,'shilucheng','sheets',sec,topic))
  if f['key'] in ['conclusion','examples']:
   for sec,topic,pid in [(2,'4. 核心产品基本信息','sheets'),(5,'12. 消费者为什么选择品牌',None),(5,'13. 品牌能力与竞争壁垒',None)]:c.execute('insert into material_links(material_id,brand_id,product_id,section,topic) values(?,?,?,?,?)',(mid,'shilucheng',pid,sec,topic))
 mid={f['key']:f['material_id'] for f in pub}
 for i,fields in changes.items():
  e=json.loads(base[i]['evidence']);chosen=['conclusion','examples'] if i in [10,14,21,54,58,59,66,67,68,72] else ['statistics','rules','reviews','annotations','behavior','examples']
  fields['evidence']=json.dumps(list(dict.fromkeys([mid[k] for k in chosen]+e)));fields['updated_at']=STAMP
  c.execute('update records set '+','.join(k+'=?' for k in fields)+' where id=?',tuple(fields.values())+(i,))
 # Field-scoped edits to the existing report.
 doc['scope']='公开事实核查截至2026-11-05，各指标保留观察日期。聚焦TikTok美国竹混纺床单1729438233542234865，其他产品不混样。既有1,628条评论已完成v1.2分层语义编码；便利样本不代表总体，作品级转化与销量因果仍待补。'
 doc['summary']='现有证据更支持一套成交组合：竹／凉感等升级期待、可接受的支出与内容触达帮助部分消费者尝试，买后的柔软与舒适为保留和追加购买提供理由。它在已查竞品中并非最低价；样本内认可不等于独占性能优势，技术、先发、品牌溢价及各因素销量贡献仍未获证明。'
 doc['summary_record_ids']=list(dict.fromkeys(doc['summary_record_ids']+[12,52,66]))
 s=doc['sections'][1];s['headline']='升级期待帮助试购，柔软与舒适支持部分保留和追加购买'
 s['summary']='低价、凉感、柔软都不能单独解释畅销。既有竞争报价、渠道内容和新的分层评论共同支持一条购买路径：愿意尝试、形成订单、实际使用、再作选择；促销、套装、配色和分销仍可能影响成交与件数。'
 s['boundary']='评论统计来自v1.2：928条近期全星级、687条额外一星、13条推荐分别处理。旧210条候选／47条摘记仅留作历史定性材料。当前页面价不等于历史到手价，累计成交不等于同期净销售；本节是阶段性机制解释，不是因果贡献率。'
 t=next(t for t in s['topics'] if t['product_id']=='sheets' and t['topic'].startswith('5.'))
 t.update(finding='柔软是最突出的买后认可点；温度体验既有认可，也有明显落差。',bullets=['2026-09-24—11-04，928条近期全星级便利样本；以下为明确提及具体体验的评论条数，不代表总体消费者满意率或购买原因占比。','温度正面176条含172条凉感／少热少汗、2条保暖、2条未细分调温；负面72条含1条怕冷者嫌不够暖，不能全按凉感成败解释。','正面适配101与颜色94接近；负面适配38与滑脱35接近，未决边界可持平。各主题可重叠、褒贬可并存，不能相加为人数。'],featured=[{'record_id':12,'mode':'analysis'}],record_ids=[12,40,52,11,13,53],gap='样本内语义统计已完成；总体代表性、未购买者选择、各动机权重及需求规模仍无法据此确定。',coverage='部分回答',answer_type='分析判断')
 t=next(t for t in s['topics'] if t['product_id']=='sheets' and t['topic'].startswith('6.'))
 t.update(finding='升级期待帮助部分消费者愿意尝试；买后的柔软与舒适，为保留和追加购买提供理由。',bullets=['凉感、竹材料和可接受的支出进入部分人的选择。R452、R917明确为凉感买；R475看到合适价格后下单。','柔软是最突出的具体认可点；R718没感到预期凉感仍因舒适继续用，R834因急需保留。保留不必然等于满意。','R580因触感两次下单、R499试用后追加；R1408后购颜色触感较差。主样本13条明确再购、21条可能再购且顺序未明，多套和意愿分开，不能算复购率。','同日白色Queen报价中Shilucheng四件套$42.37、LDC四件套$30.99；CGK纯竹源套装$64.49但件数未核。仅是2026-11-05页面价，不证明最低价或品牌溢价。','渠道分销、投放、经营时长、促销及套装仍是未排除的解释；新增评论没有量化各因素贡献，也没有证明普遍更凉或技术独占。'],featured=[{'record_id':65,'mode':'table'},{'record_id':66,'mode':'analysis'}],gap='评论已增强试购、保留和追加购买的证据；仍缺同期销量／流量／价格、投放佣金、退货净利润及实物对照。',record_ids=[14,54,65,66,67,68,69])
 # Revisions are refreshed only for changed sections; unrelated content remains exact.
 for num in [2,5]:
  section=doc['sections'][num-1];section['reviewed_revision']=reports.section_revision(c,'shilucheng',num);section['current_revision']=section['reviewed_revision'];section['stale']=False;section['updated_at']=STAMP
 doc['reviewed_revisions']['2']=doc['sections'][1]['reviewed_revision'];doc['reviewed_revisions']['5']=doc['sections'][4]['reviewed_revision'];doc['updated_at']=STAMP
 c.execute("update brand_reports set document=?,updated_at=? where brand_id='shilucheng'",(json.dumps(doc,ensure_ascii=False),STAMP))
 manifest={'version':'1.2','product_id':'sheets','external_product_id':'1729438233542234865','brand_id':'shilucheng','published_at':STAMP,'files':pub,'review_ids':[int(i) for i in re.findall(r'^## R(\d+)',(SRC/'07_关键证据与反例.md').read_text(),re.M)]+[1409,1618]}
 c.execute('insert into meta(key,value) values(?,?)',('review_analysis:sheets:v1.2',json.dumps(manifest,ensure_ascii=False)))
 c.execute('insert into events(action,detail,created_at) values(?,?,?)',('review-analysis-sync',json.dumps({'version':'1.2','records':sorted(changes)},ensure_ascii=False),STAMP));c.commit()
except:
 c.rollback();raise
log={'backup':str(B),'record_changes':[{'id':i,'fields':fields,'before':{k:base[i][k] for k in fields}} for i,fields in changes.items()],'published_materials':pub,'timestamp':STAMP}
(P/'changes.json').write_text(json.dumps(log,ensure_ascii=False,indent=2));(P/'publication.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('Updated records',sorted(changes));print('Fixed materials',[(f['material_id'],f['filename']) for f in pub])
