import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server,reports

def material(c,title,url,section,topic,summary='',path='',kind='品牌官网',publisher='Shilucheng',pid=None):
 row=c.execute('select id from materials where url=?',(url,)).fetchone() if url else c.execute('select id from materials where local_path=?',(path,)).fetchone()
 if row:mid=row[0]
 else:mid=c.execute('insert into materials(title,url,source_type,publisher,retrieved_at,summary,local_path) values (?,?,?,?,?,?,?)',(title,url or None,kind,publisher,server.now(),summary,path)).lastrowid
 if not c.execute('select 1 from material_links where material_id=? and brand_id=? and section=? and topic=? and product_id is ?',(mid,'shilucheng',section,topic,pid)).fetchone():
  c.execute('insert into material_links(material_id,brand_id,product_id,section,topic) values (?,?,?,?,?)',(mid,'shilucheng',pid,section,topic))
 return mid

def record(c,section,topic,title,body,evidence,kind='事实',status='已核实页面信息',pid=None):
 row=c.execute('select id from records where brand_id=? and title=?',('shilucheng',title)).fetchone()
 vals=('shilucheng',pid,section,topic,title,body,kind,status,json.dumps(evidence),server.now())
 if row:
  c.execute('update records set brand_id=?,product_id=?,section=?,topic=?,title=?,body=?,kind=?,status=?,evidence=?,updated_at=? where id=?',vals+(row[0],));return row[0]
 return c.execute('insert into records(brand_id,product_id,section,topic,title,body,kind,status,evidence,updated_at) values (?,?,?,?,?,?,?,?,?,?)',vals).lastrowid

def edit(t,finding,bullets=None,refs=None,features=None,coverage='部分回答',kind='事实概括',gap='',impact=''):
 t.update(finding=finding,bullets=bullets or [],coverage=coverage,answer_type=kind,gap=gap,impact=impact)
 if refs is not None:t['record_ids']=refs
 if features is not None:t['featured']=[{'record_id':i,'mode':'table'} for i in features]

def save(c,d,n):
 s=d['sections'][n-1];s['reviewed_revision']=reports.section_revision(c,'shilucheng',n);s['updated_at']=server.now();d['updated_at']=server.now()
 d['reviewed_revisions']={str(i):reports.section_revision(c,'shilucheng',i) for i in range(1,7)}
 c.execute('update brand_reports set document=?,updated_at=? where brand_id=?',(json.dumps(d,ensure_ascii=False),server.now(),'shilucheng'))
 c.execute('insert into events(action,detail,created_at) values (?,?,?)',('研究与报告深化',f'按顺序完成本轮第{n}板块研究整理；保留原始记录',server.now()))

if __name__=='__main__':
 with server.conn() as c:
  d=json.loads(c.execute("select document from brand_reports where brand_id='shilucheng'").fetchone()[0]);n=int(sys.argv[1]);s=d['sections'][n-1]
  if n==1:
   m=material(c,'Gloda｜2025年1月家纺店铺周数据（待核验线索）','https://www.gloda.vip/en/content/detail/6817',1,server.TOPICS[1][1],'文章指向2025-01-19至25日，但未列店铺ID；不作为本品牌经营规模。',kind='第三方数据文章',publisher='Gloda')
   record(c,1,server.TOPICS[1][1],'公开经营规模补查：第三方文章不能替代品牌披露','2026-11-04补查：Gloda文章列出2025-01-19至25日同名店铺GMV $129,600、3,413件，未列店铺ID，统计方法无法充分核验。文章在周数据中使用QoQ表达增长，口径不清。暂不并入经营规模、增长率或跨渠道占比；不据此归因。原品牌网站没有披露可用的收入序列。',[m,1,6],kind='缺口',status='已查未找到可靠资料')
   positioning=record(c,1,server.TOPICS[1][0],'品牌表达的商业主线：材料与可负担体验','复核官网About us：材料选择、舒适睡眠与让家庭负担得起的床品是反复出现的价值表达；网站还自述减少中间商成本。结合导航中的微纤维、竹源材料、棉、亚麻等路线，可概括其商品组织方式为“材料分层＋可负担的舒适体验”。这属于对公开表达的研究概括，尚非消费者已形成的品牌认知。',[1,6,15],kind='分析',status='研究草稿')
   s['headline']='用材料与舒适体验组织销售，床单是最值得深挖的成交入口'
   s['summary']='Shilucheng已布局床单、褥垫、毯、枕等品类，并进入多个线上渠道。目标竹混纺床单的累计成交展示，明显高于同店已观察的几款褥垫和毯；本轮应先拆解这款床单怎样把材料与舒适主张变成购买。'
   edit(s['topics'][0],'它向消费者承诺的是：以可负担的价格，获得更舒适的床品。',['材料路线是主要陈列线索：微纤维、竹源材料、棉与亚麻，分别连接不同的触感和睡眠主张。','“减少中间环节”是品牌的价格解释；自有制造、成本领先与研发能力尚未得到独立验证。'],refs=[positioning,1,2,3,28,34,44,48],gap='品牌创立年份与经营主体关系尚未完全核实；公司2003年自述不等同于品牌成立。')
   edit(s['topics'][1],'已确认四类线上渠道；TikTok提供了最清楚的公开成交线索。',refs=[29,35,4,30],features=[29],gap='尚无同期间品牌收入、各渠道销售额及增长率，不能判定最大渠道或渠道份额。')
   edit(s['topics'][2],'多品类布局已经成立，目标床单在已观察商品中有突出的成交积累。',['目标床单累计售出435.5K；另三款已观察商品分别为70.7K、41.9K与29.5K。它值得优先研究，但该列表并非全店销售排行。','官网目录可见多档材料与价格路线；应按规格和材料分别比较，避免把“竹混纺”与“100%竹源粘胶”视为同款。'],refs=[5,31,32,33,6],features=[33,31],gap='尚缺同期间单品收入，不能计算爆款贡献或推断品牌依赖单一爆款。')
   s['boundary']='上述判断限定在已核实的公开入口、目录和商品累计展示；品牌自述与经营成效分别处理。'
   save(c,d,n)
   print('第一板块研究内容已更新')
