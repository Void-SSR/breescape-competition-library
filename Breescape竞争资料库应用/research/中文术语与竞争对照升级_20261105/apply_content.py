import json,sqlite3,sys
from pathlib import Path
from datetime import datetime
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));import reports
C=sqlite3.connect(ROOT/'data/library.sqlite3');C.row_factory=sqlite3.Row
BEFORE=json.loads((Path(__file__).parent/'before.json').read_text())
NOW=datetime.now().astimezone().isoformat(timespec='seconds')
# Refuse to overwrite intervening work.
for table,rows in BEFORE.items():
 assert [dict(r) for r in C.execute(f'SELECT * FROM {table} ORDER BY rowid')]==rows,table+' changed since snapshot'
M={m['id']:m for m in BEFORE['materials']};R={r['id']:r for r in BEFORE['records']}
url=lambda mid:M[mid]['url']
link=lambda name,mid:f'[{name}]({url(mid)})'
changes={}
def edit(rid,body=None,title=None,extra=()):
 r=dict(R[rid]);r.update(changes.get(rid,{}))
 if body is not None:r['body']=body
 if title is not None:r['title']=title
 r['evidence']=json.dumps(list(dict.fromkeys(json.loads(r['evidence'])+list(extra))),ensure_ascii=False);r['updated_at']=NOW;changes[rid]=r
# 1. Brand / channel entry points.
b=R[29]['body']
for old,name,mid in [('shilucheng.com','Shilucheng官网',6),('Shilucheng Home，店铺ID 7495541840241986289','Shilucheng Home店铺',4),('shilucheng，卖家ID AHKCVOX33TXTW','shilucheng卖家主页',18),('Shilucheng品牌页','Shilucheng品牌页',11)]:b=b.replace(old,link(name,mid))
edit(29,b)
# 2. Product facts and comparison, maintaining historical observation dates.
edit(36,'''2026年11月4日直接选择深灰色规格核实，价格单位为美元。均为商品页展示活动价，不含税费或个性化优惠券，未结算。

| 尺寸与件数 | 展示活动价 | 页面划线价 | 可售状态 |
| --- | --- | --- | --- |
| 单人床三件套（Twin） | $32.37 | $64.74 | 当时可下单 |
| 双人床四件套（Queen） | $42.37 | $85.77 | 当时可下单 |
| 双人床六件套（Queen） | $45.37 | $90.97 | 当时可下单 |

划线价只是商家展示的比较价格，未验证为曾经实际成交价。不能拿单人床三件套的价格与竞品双人床套装比较。''','同款床单的尺寸与套装价格｜美元，2026年11月4日')
edit(37,'''页面有20种颜色选项。尺寸标签包括单人床（Twin）、加长单人床（Twin XL）、小双人床（Full）、双人床（Queen）、加大双人床（King）、加长双人床（California King）、分体双人床（Split King）。中文为便于阅读的说明，实际适配以商品尺寸表为准。

| 套装 | 商家列出的内容 | 适用的页面尺寸标签 |
| --- | --- | --- |
| 四件套 | 1张平床单、1张床笠、2个枕套 | Full、Queen、King、California King |
| 六件套 | 1张平床单、1张床笠、4个枕套 | Full、Queen、King、California King |

页面另有三件套与分体双人床五件套标签，具体组合尚未逐一核实。尺寸、颜色和件数并非任意组合都可售，不将选项数相乘当作可售规格数。''')
headers=[link('Shilucheng 竹混纺凉感床单（本款）',3),link('LDC Lux Decor 竹混纺床单',55),link('CGK Linens 100%竹源人造丝床单',54)]
body='''对比TikTok美国站三个具体商品。价格采用2026年11月5日已保存的同日选规格记录；材料、结构及洗护来自商品标题和商家描述。页面自动生成的AI摘要不作为产品证据。

| 对比维度 | '''+' | '.join(headers)+''' |
| --- | --- | --- | --- |
| 白色双人床（Queen）页面价 | $42.37／四件套 | $30.99／四件套 | $64.49／件数未核实 |
| 套装内容 | 1张平床单＋1张床笠＋2个枕套 | 1张平床单＋1张床笠＋2个枕套 | 此链接的具体件数与组合待核实 |
| 面料成分 | 60%竹源人造丝＋40%聚酯 | 竹混纺；未披露比例 | 100%竹源人造丝 |
| 床笠包覆与固定 | 松紧包边；侧深约36厘米，可拉伸适配最厚约41厘米床垫 | 深包边，标称适配最厚约41厘米床垫 | 弹性包边，标称适配最厚约41厘米床垫 |
| 套装选择 | 双人床可选四件或六件套；六件套多2个枕套，深灰色价差$3 | 已核实的双人床组合为四件套 | 件数未核实，暂不比较 |
| 洗护要求 | 冷水轻柔机洗、低温烘干；避免柔顺剂和漂白剂 | 标称可机洗；具体水温、烘干条件待核实 | 标称可机洗；具体水温、烘干条件待核实 |
| 商家重点宣传 | 柔软、凉感、吸湿；面向怕热与夜间出汗人群 | 柔软丝滑、凉感透气、抗皱防褪色 | 柔软、凉感排湿；提及夜间出汗和热潮红 |
| 已有使用证据 | 928条近期评论中，397条肯定柔软，92条不满触感；不能据此与另外两款排名 | 尚未完成可比的评论分析及实测 | 尚未完成可比的评论分析及实测 |

床垫厚度为商家标称值，16英寸约40.6厘米；本款床笠侧深14英寸约35.6厘米。以上换算取整便于阅读，未经实物适配测试。深灰色四／六件套价差来自11月4日同色同尺寸记录，不与11月5日白色价格混算。

三页均展示免费配送和30天免费退货入口，实际适用条件以平台结算及退货规则为准，不作为本款独有优势。织法或闭合方式的参数栏存在混杂表述，不能由“拉链”等泛化标签断定有独特结构。没有同条件成品测试，暂不判断谁更凉、更耐洗、更耐用。'''
edit(51,body,'三款床单对照：价格、套装、材料、设计与使用证据',extra=[64,65,66,78,79])
edit(10,'''能确认的差异不止材料。2026年11月5日，同为白色双人床（Queen）四件套，本款页面价$42.37，比LDC的$30.99高$11.38，约高36.7%；因此不能在这组对照中把本款解释为最低价选择。CGK虽标价$64.49，但件数未核实，暂不能比较整套性价比。

本款还有双人床六件套选项，比四件套多两个枕套；11月4日深灰色同尺寸页面价只高$3。它给需要更多枕套的人提供了另一种组合，但尚未查全竞品其他链接，不能称为独家设计；也没有证据证明六件套是销量高的主要原因。

材料上，本款为60%竹源人造丝＋40%聚酯；LDC为比例未披露的竹混纺，CGK为100%竹源人造丝。三者都宣传柔软、凉感，并标称适配最厚约41厘米的床垫，因此这些表述不能直接构成本款独有优势。

目前只有本款完成系统评论分析，三款缺少同条件使用与洗涤对照。可确认的是价格、成分和组合的差别；更凉、更耐用、让顾客愿意多付钱，仍需另外验证。''',extra=[78,79])
edit(65,R[65]['body'].replace('白色和Queen','白色和双人床（Queen）').replace('白色 Queen 页面价','白色双人床（Queen）页面价').replace('同系列Queen四件套','同系列双人床（Queen）四件套'))
# 3. Channel accounts and the already confirmed video sample.
edit(15,R[15]['body'].replace('Shilucheng Home店铺（ID 7495541840241986289）',link('Shilucheng Home店铺',4)+'（ID 7495541840241986289）'))
edit(41,R[41]['body'].replace('@shiluchenghome',link('@shiluchenghome',20)))
b=R[46]['body']
for old,name,mid in [('Instagram @shilucheng_sheet','Instagram @shilucheng_sheet',37),('Facebook Shilucheng，ID 61550502788661','Facebook Shilucheng',38),('YouTube @shilucheng','YouTube @shilucheng',39),('Pinterest Shilucheng_sheet','Pinterest Shilucheng_sheet',40)]:b=b.replace(old,link(name,mid))
edit(46,b.replace('账号当前展示总数','2026年11月4日展示总数').replace('主页当前展示总数','2026年11月4日主页展示').replace('频道当前展示总数','2026年11月4日频道展示'))
for rid in [17,43,55,76]:
 b=R[rid]['body']
 for i in range(1,6):
  vid=f'V{i:02d}';b=b.replace(f'| {vid} |',f'| [{vid} 已保存视频](/attachment/{55+i}) |')
  for author in ['Alyssa','Kat Kag','Ben']:
   b=b.replace(f'| {vid} {author} /',f'| [{vid} {author} 已保存视频](/attachment/{55+i}) /')
 b+='\n\n视频入口：V01—V05可点击播放已保存文件；它们对应此次确认的五条素材。尚未取得这些作者的可靠账号主页和独立原帖链接，不按显示名称猜测账号。'
 if rid==43:b+='其余14条仅保留候选记录，原作品入口待补。'
 if rid==17:b=b.replace('当前以商品页链接、编号、作者、截图及原候选表回溯','当前可播放已保存视频，并以商品页、编号、作者、截图及原候选表回溯')
 edit(rid,b,extra=[56,57,58,59,60])
# 4. Link the historical post to the observed original.
edit(47,R[47]['body'].replace('Instagram账号的一条帖子',link('Instagram黑五促销帖',44)).replace('官网关联Facebook主页',link('官网关联Facebook主页',38)))
# 5-6. Confirm nothing in the extended comparison proves a moat, willingness to pay or market size.
# Existing cautious brand/strategic conclusions remain applicable and unchanged.
notes='''# 三款床单规格与设计复核｜2026年11月5日

复核对象：TikTok美国站三个具体商品链接，不将其他平台同系列自动并为同一规格。

'''
for name,mid in [('Shilucheng',3),('LDC',55),('CGK',54)]:notes+=f'- {name}：{url(mid)}\n'
notes+='''
本次通过网页读取商品标题和商家Product description，排除AI Highlights、Introduction及自动问答。商品页可能提供缓存内容，未将默认规格价格写成新的实时报价。价格比较继续采用已保存的11月5日白色Queen页面截图（材料64—66）；本款六件与四件的价差来自11月4日深灰色历史选规格记录。

核对结果：
- Shilucheng：60%竹源人造丝、40%聚酯；床笠侧深14英寸、可适配16英寸；冷水轻柔机洗、低温烘干，避柔顺剂和漂白剂。Full/Queen/King/California King四件套为平床单、床笠、两枕套；六件套增加两枕套。描述称斜纹，参数有缎纹／平织，实际织法未确认。
- LDC：仅写竹混纺、比例未披露；可适配16英寸床垫；Queen为平床单、床笠、两枕套；标称机洗及抗皱防褪色，未取得同条件实测。描述中的Queen平床单为90×102英寸、床笠60×80英寸、枕套20×30英寸，不能把该尺寸套用于Shilucheng。
- CGK：标题为100% rayon from bamboo；弹性包边适配16英寸床垫，宣传凉感排湿、夜间出汗／热潮红需要，标称可机洗。此TikTok链接Queen件数及具体洗护温度仍未核实；不拿Target同系列四件套替代。
- 参数栏出现Zipper、Envelope、Elastic等表述，但具体部位和对应规格不明确，未认定独特拉链设计。
- 未取得三款同条件使用、洗涤与耐久实测。已有评论统计只属于Shilucheng，不能与另外两款未经系统采集的评论直接排名。

计算核对：42.37−30.99＝11.38美元；11.38÷30.99≈36.7%；45.37−42.37＝3美元。14英寸＝35.56厘米，16英寸＝40.64厘米。汇报表取整为约36／41厘米，不是精确适配保证。

新观察只支持规格、价格和材料差异，不证明主要销量原因、独有竞争壁垒、真实成交溢价或机会市场规模。
'''
path=ROOT/'data/attachments/三款床单规格与设计复核_2026-11-05.md';assert not path.exists();path.write_text(notes)
with C:
 mid=C.execute('INSERT INTO materials(title,source_type,publisher,retrieved_at,summary,local_path,access_note) VALUES (?,?,?,?,?,?,?)',('三款床单规格、设计及价格口径复核｜2026年11月5日','本地核查记录','公开商品页与既有页面证据',NOW,'补充套装、包覆设计、洗护要求；材料与宣传不等同于实测优势。',str(path.relative_to(ROOT/'data')),'保留三条原始商品链接及证据口径；CGK件数和同条件实测仍缺。')).lastrowid
 C.execute('INSERT INTO material_links(material_id,brand_id,product_id,section,topic) VALUES (?,?,?,?,?)',(mid,'shilucheng','sheets',2,'4. 核心产品基本信息'))
 for rid in [10,37,51]:
  r=changes[rid];r['evidence']=json.dumps(json.loads(r['evidence'])+[mid])
 for rid,r in changes.items():C.execute('UPDATE records SET title=?,body=?,evidence=?,updated_at=? WHERE id=?',(r['title'],r['body'],r['evidence'],NOW,rid))
 for rid in [17,43]:
  for vid in range(56,61):
   if not C.execute('SELECT 1 FROM material_links WHERE material_id=? AND brand_id=? AND section=3',(vid,'shilucheng')).fetchone():C.execute('INSERT INTO material_links(material_id,brand_id,product_id,section,topic) VALUES (?,?,?,?,?)',(vid,'shilucheng','sheets',3,'8. TOP5爆款内容分析'))
 for vid in [27,56,57,58,59,60]:
  m=M[vid];summary=m['summary'].replace('音轨未转录','音轨已自动转写，尚未人工听辨');access=m['access_note'].replace('声音听辨／转录尚未完成','音轨已自动转写，尚未人工听辨；分歧与原始转写见材料80—82').replace('音轨未转录','音轨已自动转写，尚未人工听辨')
  C.execute('UPDATE materials SET summary=?,access_note=? WHERE id=?',(summary,access,vid))
 d=json.loads(BEFORE['brand_reports'][0]['document'])
 assert d['brand_id']=='shilucheng'
 t=d['sections'][1]['topics'][0]
 t['finding']='本款提供四件与六件组合；同尺寸四件套比LDC贵，凉感和柔软也不是独有卖点。'
 t['bullets'][1]='深灰色双人床（Queen）四件套为$42.37、六件套为$45.37；六件套多两个枕套、贵$3。价格为2026年11月4日页面记录。'
 t['figures'][0]['caption']='目标商品首页：深灰色单人床三件套（Twin），页面价$32.37；顶部为达人精灵数据区。'
 for f in t['featured']:
  if f['record_id']==51:f['layout']='comparison'
 t['gap']='CGK的TikTok套装件数、三款同条件的使用与洗涤表现尚未核实；材料、套装差别不能直接认定为销量或溢价原因。'
 for s in d['sections']:
  # Only presentation text; preserve underlying original observations and review text.
  for t in s['topics']:
   t['bullets']=[x.replace('白色Queen四件套','白色双人床（Queen）四件套') for x in t.get('bullets',[])]
  s['current_revision']=s['reviewed_revision']=reports.section_revision(C,'shilucheng',s['number']);s['stale']=False
  if s['number'] in [1,2,3,4]:s['updated_at']=NOW
 d['reviewed_revisions']={str(s['number']):s['current_revision'] for s in d['sections']};d['summary_stale']=False;d['updated_at']=NOW
 C.execute('UPDATE brand_reports SET document=?,updated_at=? WHERE brand_id=?',(json.dumps(d,ensure_ascii=False),NOW,'shilucheng'))
result={'changed_records':list(changes),'new_material_id':mid,'updated_at':NOW,'reviewed_sections':[1,2,3,4,5,6],'preserved_raw_tables':['reviews','observations','products','brands']}
(Path(__file__).parent/'content_changes.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
