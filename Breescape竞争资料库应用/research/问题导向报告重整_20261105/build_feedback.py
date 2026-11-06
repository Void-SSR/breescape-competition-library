import csv,json,hashlib
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'data/attachments/评论语义 v1.2_20261105';OUT=Path(__file__).parent
read=lambda f:list(csv.DictReader((BASE/f).open(encoding='utf-8-sig')))
reviews={r['review_id']:r for r in read('04_逐条评论与编码.csv') if r['source_group']=='main_recent'}
annotations=read('04_全部证据标注.csv');stats=[r for r in read('05_分来源主题统计.csv') if r['source_group']=='main_recent'];assert len(reviews)==928
# Replay the published numerator IDs from evidence annotations, not keyword or star counts.
replay=defaultdict(set)
for a in annotations:
 if a['source_group']!='main_recent' or a['dimension']!='theme' or a['valence'] not in ['positive','negative']:continue
 if a['code'].startswith('T') and a['primary_count_eligible']!='True':continue
 if a['code'].startswith('G') and a['subject']!='target_same_product':continue
 replay[(a['code'],a['valence'])].add(a['review_id'])
for row in stats:
 ids=set(row['review_ids'].split(';'));assert ids==replay[(row['code'],row['valence'])],(row['code'],row['valence'],ids^replay[(row['code'],row['valence'])]);assert len(ids)==int(row['count'])
# Only two additional overall judgements; the v1.2 detailed theme coding remains frozen.
# R352 expressly rejects another purchase; its ambiguous 'balled up' is NOT called pilling.
# R692 complains about an unusable gift, a purchase/fulfilment issue, NOT a sheets sizing defect.
manual=[{'review_id':'352','valence':'negative','scope':'general','code':'G00','reason':'明确表示不会再买；具体问题balled up仍未细分，不增加起球或滑脱分子。'}, {'review_id':'692','valence':'negative','scope':'gift','code':'GIFT','reason':'赠品规格不适用，计购买履约不满；不计床单规格错发。'}]
rows=[]
for r in stats:
 rows.append({**r,'ids':sorted(map(int,r['review_ids'].split(';')))})
next(r for r in rows if r['code']=='G00' and r['valence']=='negative')['ids'].append(352)
rows.append({'code':'GIFT','label':'赠品履约','theme_type':'具体主题','valence':'negative','ids':[692]})
sets={v:set().union(*(set(r['ids']) for r in rows if r['valence']==v)) for v in ['positive','negative']}
p,n=sets['positive'],sets['negative'];allids=set(map(int,reviews));mixed=p&n;unknown=allids-(p|n)
assert (len(p),len(n),len(mixed),len(unknown))==(734,314,129,9)
labels={
'T01':('柔软','粗糙、僵硬或不够软'),'T02':('顺滑、丝滑','不够顺滑或丝滑'),'T03':('凉感及温度体验','不够凉、偏热等温度不满'),
'T04':('透气','透气不满意'),'T05':('重量合适、轻盈','重量不满意'),'T06':('厚薄合适','偏薄等厚薄不满'),'T07':('尺寸、包覆厚度合适','尺寸或床垫适配不满意'),
'T08':('床单固定、不易滑脱','滑脱、固定不住'),'T09':('喜欢颜色与搭配','不喜欢颜色或搭配'),'T10':('颜色与展示一致','颜色与展示不一致'),
'T11':('不易起球','起球'),'T12':('褶皱表现满意','褶皱不满'),'T13':('不易破裂','破裂、开线'),'T14':('不易勾丝','勾丝'),
'T16':('不黏身、接触顺畅','黏附衣物／皮肤、摩擦不适'),'T17':('多次／套内体验一致','多次购买或套内体验不一致'),'T18':('材料符合预期','材料与理解或预期不一致'),
'T20':('气味满意、无异味','气味不满'),'T21':('到货清洁','到货清洁或新旧状态不满'),'T22':('发货准确','收到的商品／规格不符'),
'T23':('配送及时','配送时效不满'),'T24':('客服沟通、响应满意','客服沟通、响应不满'),'T25':('补发顺利','补发履约不满'),
'T26':('评价沟通满意','被要求改评的负面自述'),'T27':('包装满意','包装破损等不满'),'T28':('觉得价格较低或合适','觉得价格偏高'),
'T29':('觉得物有所值','觉得不值这个价格'),'T30':('睡眠体验改善','睡眠体验不满'),'T32':('吸湿排湿体验满意','吸湿排湿不满'),
'T33':('套装内容满意','套装件数或内容不符预期'),'T34':('收到完整订单','未收到或少收到套组'),'T35':('退货退款顺利','退货退款过程不满'),
'T36':('方向标记清楚','缺少需要的方向标记'),'T37':('铺展平整','铺展不平整'),'T38':('防滑结构符合说明','防滑结构与理解或说明不符'),
'T39':('铺装方便','铺装不便'),'T40':('不痒、无刺激的使用自述','发痒、刺激的使用自述'),'T41':('颜色保持','使用／洗后颜色变化'),
'T42':('使用环境满意','使用后发现蚂蚁（原因未核）'),'T43':('交付方式满意','投递位置或交付方式不满'),'T45':('颜色选择丰富','颜色选择不足'),
'T46':('缝制做工满意','缝制做工不满'),'T47':('毛发附着较少','毛发附着未达预期'),'T49':('松紧结构满意','松紧带表现不满'),
'G00':('总体喜欢、推荐','总体不认可、不愿再买'),'G01':('笼统肯定质量','笼统不满质量'),'G02':('笼统肯定舒适','笼统不满舒适'),
'G03':('笼统肯定耐用','笼统不满耐用'),'G04':('笼统肯定洗护表现','笼统不满洗护表现'),'G05':('笼统肯定外观','笼统不满外观'),'G06':('展示符合预期','展示触感落差，未细分'),'G07':('总体肯定商家服务','总体不满商家服务'),
'GIFT':('赠品满意','赠品规格不适用')}
for r in rows:
 r['ids']=sorted(set(r['ids']));r['count']=len(r['ids']);r['label']=labels[r['code']][0 if r['valence']=='positive' else 1]
 r['percent_all']=round(r['count']/928*100,1);r['denominator_group']=len(sets[r['valence']]);r['percent_group']=round(r['count']/r['denominator_group']*100,1)
 r['general']=r['theme_type']=='一般评价';r['source']='v1.2逐条编码'+('＋本轮总体态度补判' if r['code']=='G00' and r['valence']=='negative' else '') if r['code']!='GIFT' else '本轮单列赠品履约'
 r.pop('review_ids',None);r.pop('percent',None);r.pop('denominator',None);r.pop('source_group',None)
rows.sort(key=lambda r:(r['valence'],r['general'],-r['count'],r['code']))
for v in ['positive','negative']:
 concrete=[r for r in rows if r['valence']==v and not r['general']]
 for i,r in enumerate(concrete):r['rank']=i+1
summary={'total':928,'positive':len(p),'negative':len(n),'mixed':len(mixed),'positive_only':len(p-n),'negative_only':len(n-p),'unclassified':len(unknown),'positive_percent':round(len(p)/928*100,1),'negative_percent':round(len(n)/928*100,1),'mixed_percent':round(len(mixed)/928*100,1),'unclassified_ids':sorted(unknown),'positive_ids':sorted(p),'negative_ids':sorted(n),'mixed_ids':sorted(mixed)}
result={'summary':summary,'rows':rows,'manual_decisions':manual,'sample_period':'2026-09-24—2026-11-04','method':'同条评论可有认可和不认可；总体按评论去重；分项以各类反馈评论数为分母，一条可提多个主题；不按星级代替语义。'}
(OUT/'feedback.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
with (OUT/'评论全貌与完整分项.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['方向','类别','主题','评论数','占本类反馈比例','占全部928条比例','分母','原评论编号','证据来源'])
 for r in rows:w.writerow(['认可' if r['valence']=='positive' else '不认可','一般评价' if r['general'] else '具体反馈',r['label'],r['count'],r['percent_group'],r['percent_all'],r['denominator_group'],';'.join(map(str,r['ids'])),r['source']])
print(json.dumps({k:v for k,v in summary.items() if not k.endswith('_ids')},ensure_ascii=False));print('all rows',len(rows),'by sign',{v:len([r for r in rows if r['valence']==v]) for v in sets});print('source replay verified',len(stats))
