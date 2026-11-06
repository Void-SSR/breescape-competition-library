from pathlib import Path
import csv,json,re,sqlite3,hashlib,collections,datetime,shutil
R=Path(__file__).resolve().parent;B=R.parents[1]
SRC=Path('/Users/voidengine/Documents/Codex/2026-11-06/https-www-sheex-com-products-original/outputs')
raw=list(csv.DictReader((SRC/'SHEEX_Original_Performance_评论.csv').open(encoding='utf-8-sig')))
shutil.copy2(SRC/'SHEEX_Original_Performance_评论.csv',R/'SHEEX_原始513条.csv')
shutil.copy2(SRC/'采集说明.md',R/'SHEEX_原采集说明.md')
excluded={140:'订单变更请求，无产品使用内容',218:'无实质内容 g g',373:'仅标点',493:'无实质内容 N/Am',227:'单独枕套购买，非目标套装',465:'竹源粘胶枕套，非Original套装',504:'Studio Tech系列，非Original套装'}
# 全文阅读后逐条指定负面主题；避免把低星当差评、把旧产品不满误算到本款。
neg={9:'service',14:'fit',15:'quality soft contents',20:'cool',23:'cool soft',27:'fit',31:'quality',35:'service',52:'service',61:'cool general',66:'fit cool service',73:'closure value',76:'soft',83:'closure',86:'service',88:'quality',90:'quality',91:'quality soft',92:'service',93:'contents',106:'fit',107:'soft',109:'color',117:'slip closure',127:'slip',139:'service',162:'quality',164:'closure',170:'slip',184:'quality',198:'soft',205:'closure',216:'service',223:'quality soft',243:'color',271:'color',275:'value',278:'general',281:'fit service',283:'soft',286:'slip',287:'color',301:'quality value',307:'cool care',319:'soft',321:'slip',334:'value',354:'contents',375:'closure cool',379:'choice',390:'cool',392:'fit',421:'color',425:'cool',434:'slip cool',441:'choice',444:'value soft color',451:'fit',486:'choice',490:'fit closure'}
P={
 'soft':('柔软、丝滑与舒适触感',r'soft|silky|smooth|comfort|comfy|柔软|柔滑|丝滑|舒适|舒服|手感|触感'),
 'fit':('弹力、贴合与不脱角',r'fit|stretch|stay.{0,15}(?:place|put|on)|弹|贴合|不.{0,8}(?:脱落|滑落|移位)|合身|适合.{0,15}床|包裹.{0,8}床垫'),
 'cool':('凉爽、透气与少出汗',r'cool|breath|wick|凉|透气|排汗|排湿|不.{0,8}(?:热|汗)|没有.{0,8}(?:热|汗)'),
 'quality':('做工与耐用',r'quality|durab|last(?:ed|ing|s)?|well.made|质量|品质|耐用|经久|用了.{0,6}年|使用了.{0,6}年|保持.{0,8}状态'),
 'care':('洗护方便、洗后状态好',r'wash|dryer|wrinkle|洗|烘干|抗皱|不起皱'),
 'sleep':('睡得更好',r'sleep.{0,12}(?:better|well|great)|slept.{0,12}(?:better|well|great)|best.{0,8}sleep|睡.{0,12}(?:更好|香|安稳|踏实|很好)|睡眠质量|更好的睡眠'),
 'color':('颜色与外观',r'colou?r|look|颜色|色彩|漂亮|美丽|外观'),
 'value':('值得购买、价格与价值',r'worth|value|good.{0,8}price|值得|物有所值|一分钱一分货|实惠|划算'),
 'service':('送货与服务',r'fast.{0,8}(?:ship|delivery)|quick.{0,8}deliver|great.{0,8}service|快速.{0,8}(?:到货|送达)|服务.{0,8}(?:好|棒)|发货.{0,8}快'),
 'ease':('铺床省力、容易整理',r'easy.{0,15}(?:put|make|change)|easier.{0,15}(?:make|put|bed)|容易.{0,10}(?:铺|套|整理)|轻松.{0,10}(?:铺|套|整理)|方便.{0,8}铺|铺床.{0,8}(?:容易|轻松|方便)')}
labels={k:v[0] for k,v in P.items()}|{'closure':'枕套开口与固定','slip':'上层床单或被子滑落','contents':'套装件数与交付内容','choice':'缺少单买或规格选择','general':'笼统认可或不满'}
# 实际已经拥有/购买多套，排除仅说将再购买；也包含复购后的负面评论。
repeat=set(map(int,'''2 7 11 13 19 21 24 25 28 31 34 40 41 42 44 48 55 56 57 66 69 70 71 79 84 85 86 87 88 90 91 92 95 96 97 98 100 104 105 108 109 110 114 115 116 119 122 129 132 135 136 141 142 148 152 154 156 157 158 159 166 168 172 174 179 180 183 184 188 192 195 201 207 210 211 212 213 216 225 236 239 240 242 244 252 255 256 258 260 261 264 265 266 267 268 269 274 276 278 279 280 281 284 285 286 287 291 299 302 303 305 307 310 311 318 325 326 327 331 336 337 344 351 355 360 361 365 367 370 371 377 380 381 383 387 388 394 395 398 399 403 407 408 411 412 414 415 417 419 421 427 428 429 435 436 440 447 453 459 466 479 481 483 487 489 500 507 508 511'''.split()))
experience=set(map(int,'51 56 87 124 176 191 192 207 224 232 240 252 258 302 318 351 355 360 370 403 411 416 417 438 448 488 491 513'.split()))
fit_purchase=set(map(int,'151 170 177 222 237 244 340 441 442 456'.split()))
c=sqlite3.connect(B/'data/library.sqlite3');rows=[];seen={};ex=[]
for d in raw:
 n=int(d['序号']);body=d['正文（页面显示）'].strip();norm=' '.join(body.casefold().split())
 if n in excluded:ex.append(dict(sequence=n,reason=excluded[n],raw=d));continue
 if norm in seen:ex.append(dict(sequence=n,reason='正文相同，分析保守去重；不等于确认同一消费者',retained=seen[norm],raw=d));continue
 seen[norm]=n
 date=d['评论日期'];m=re.fullmatch(r'(\d{4})年(\d+)月(\d+)日',date)
 if m:date=f'{m[1]}-{int(m[2]):02d}-{int(m[3]):02d}'
 else:
  try:date=datetime.datetime.strptime(date,'%m/%d/%y').date().isoformat()
  except ValueError:pass
 eid='local-'+hashlib.sha256((d['评论者']+date+d['标题（页面显示）']+body).encode()).hexdigest()[:20]
 old=c.execute('select id from reviews where product_id=? and normalized=?',('sheex-sheets',norm)).fetchone()
 rid=old[0] if old else c.execute('insert into reviews(product_id,external_id,body,normalized,rating,date,sku,region,raw_json) values(?,?,?,?,?,?,?,?,?)',('sheex-sheets',eid,body,norm,int(d['评分（5分制）']),date,'Original Performance，具体规格未标注','US',json.dumps(d,ensure_ascii=False))).lastrowid
 txt=d['标题（页面显示）']+'. '+body;parts=re.split(r'[.!?。！？；;\n]+|\bbut\b|但是|但',txt,flags=re.I)
 pos=set();ev={}
 for s in parts:
  if re.search(r'not|never|don.t|doesn.t|isn.t|wasn.t|wish|hope|不|没|希望|想要|期待|以前|previous|used to|old ones',s,re.I):continue
  for k,(label,pat) in P.items():
   if re.search(pat,s,re.I):pos.add(k);ev.setdefault(k,[]).append(s.strip())
 if re.search(r'love|great|best|recommend|excellent|perfect|喜欢|好评|推荐|很棒|完美|最好的|爱',txt,re.I):pos.add('general')
 # Mixed reviews may praise one topic and criticize another; audit overrides below resolve sentence context.
 rows.append(dict(sequence=n,id=rid,title=d['标题（页面显示）'],body=body,rating=int(d['评分（5分制）']),date=date,url=d['产品及来源链接'],positive=sorted(pos),negative=neg.get(n,'').split(),evidence=ev,actual_repeat=n in repeat,experience_recommendation=n in experience,explicit_fit_purchase=n in fit_purchase))
c.commit();c.close()
# Context overrides based on reading full original displayed text; preserve genuine mixed feedback.
ov={15:['general'],20:['soft','general'],23:[],31:['general'],35:['general'],61:[],66:['general'],73:['soft','general'],76:['soft','general'],83:['soft','general'],86:['soft','general'],88:[],90:[],91:[],93:['soft','general'],107:['general'],117:['soft','general'],127:['soft','cool','general'],139:[],162:['soft','fit','general'],170:['soft','fit','cool','general'],184:['general'],198:[],205:['fit','soft','general'],216:['soft','general'],223:['general'],243:['general'],264:['soft','general'],271:['soft','general'],275:['soft','fit','general'],281:['soft','general'],283:['general'],286:['fit','soft','cool','general'],287:['soft','general'],301:['soft','general'],307:['soft','general'],319:['general'],321:['soft','general'],354:['soft','general'],375:['soft','fit','general'],390:['cool','general'],392:['soft','general'],425:['soft','general'],426:['quality','general'],434:['soft','general'],444:[],451:['soft','general'],490:['soft','fit','general']}
for r in rows:
 if r['sequence'] in ov:r['positive']=ov[r['sequence']]
# 二次逐条复核：补回否定旧问题的正面表述，并剔除仅意向/跨品类的再购误计。
adds={4:'general',13:'odor general',17:'general',26:'color general',30:'cool',54:'soft cool',65:'cool',68:'general',71:'general',79:'general',81:'general',83:'fit cool',96:'fit soft',107:'soft',110:'cool',117:'fit',126:'cool',129:'quality general',133:'fit',134:'general',136:'fit',143:'general',147:'general',160:'soft general',162:'cool',168:'general',177:'fit ease general',181:'general',184:'cool',188:'cool',193:'cool general',196:'cool',197:'general',198:'soft quality',210:'quality general',226:'cool',233:'general',236:'soft fit',243:'soft quality color',244:'fit ease',248:'cool general',259:'fit',261:'cool',264:'cool',266:'general',273:'fit sleep general',278:'fit',282:'fit',284:'soft care general',287:'fit',301:'cool',305:'general',309:'cool',311:'cool',318:'general',319:'soft cool',326:'cool',329:'general',352:'general',355:'soft cool care',363:'fit',370:'fit soft',375:'cool',381:'general',385:'sleep general',390:'soft',393:'general',407:'quality general',408:'general',414:'soft',426:'soft',429:'cool',434:'fit color',436:'cool',438:'general',446:'fit',451:'fit ease',452:'soft',455:'general',469:'general',477:'fit general',478:'cool general',483:'cool',492:'general',494:'fit cool general',500:'fit cool soft care',502:'soft care ease',506:'fit',507:'general',508:'general'}
removes={127:'cool soft',170:'cool soft',201:'cool',286:'cool soft',319:'fit',426:'cool'}
more_neg={109:'value',110:'cool',136:'value',156:'value',198:'fit',207:'value',237:'value',258:'value',264:'value',274:'value',331:'value',436:'value',506:'value'}
labels['odor']='不易残留体味'
adds[150]='service value'
adds[386]='cool'
adds[481]='fit'
for r in rows:
 n=r['sequence'];r['positive']=sorted((set(r['positive'])|set(adds.get(n,'').split()))-set(removes.get(n,'').split()))
 r['negative']=sorted(set(r['negative'])|set(more_neg.get(n,'').split()))
 if n in {286,310,355,377,408,417,483,511}:r['actual_repeat']=False
 # 长期使用不等于已经再次购买，单独保留未知。
N=len(rows);pc=sum(bool(r['positive']) for r in rows);nc=sum(bool(r['negative']) for r in rows);bc=sum(bool(r['positive']) and bool(r['negative']) for r in rows)
summary=dict(total=N,positive=pc,negative=nc,mixed=bc,unclassified=N-pc-nc+bc,positive_only=pc-bc,negative_only=nc-bc,positive_percent=round(pc/N*100,1),negative_percent=round(nc/N*100,1))
st=[]
for v,den in [('positive',pc),('negative',nc)]:
 rank=0
 for k,num in collections.Counter(k for r in rows for k in r[v]).most_common():
  if k!='general':rank+=1
  st.append(dict(code=k,label=({'value':'价格偏高、购买预算受限','soft':'触感不适、黏肤或新旧手感落差','cool':'仍然闷热、凉爽程度未达预期','service':'配送、售后与退换问题','fit':'尺寸或贴合不合适','quality':'耐用、起球与新旧质量落差','color':'颜色选择或配套不足','care':'洗后变色等洗护问题'}.get(k,labels[k]) if v=='negative' else labels[k]),valence=v,count=num,percent_group=round(num/den*100,1),percent_all=round(num/N*100,1),general=k=='general',rank=rank if k!='general' else None,ids=[r['id'] for r in rows if k in r[v]]))
beh={k:dict(count=sum(r[k] for r in rows),ids=[r['id'] for r in rows if r[k]],sequences=[r['sequence'] for r in rows if r[k]]) for k in ['actual_repeat','experience_recommendation','explicit_fit_purchase']}
(R/'sheex_reviews.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));(R/'sheex_excluded.json').write_text(json.dumps(ex,ensure_ascii=False,indent=2));(R/'sheex_statistics.json').write_text(json.dumps(dict(summary=summary,rows=st,behavior=beh),ensure_ascii=False,indent=2))
with (R/'SHEEX_逐条主题编码.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['原序号','评论ID','日期','星级','认可主题','不认可主题','明确已购买或拥有多套','体验或推荐线索','明确适配购买理由','标题','页面显示正文（部分中文翻译）','原商品链接'])
 for r in rows:w.writerow([r['sequence'],r['id'],r['date'],r['rating'],'；'.join(labels[k] for k in r['positive']),'；'.join(labels[k] for k in r['negative']),r['actual_repeat'],r['experience_recommendation'],r['explicit_fit_purchase'],r['title'],r['body'],r['url']])
print(summary);print('excluded',len(ex));print([(x['valence'],x['label'],x['count']) for x in st]);print({k:v['count'] for k,v in beh.items()})
