from pathlib import Path
import re,json,csv,collections
R=Path(__file__).resolve().parent
rows=list({r['id']:r for r in reversed(json.loads((R/'cozy_reviews.json').read_text()))}.values());rows.sort(key=lambda r:r['id'])
if (R/'cozy_excluded_ids.json').exists():rows=[r for r in rows if r['id'] not in json.loads((R/'cozy_excluded_ids.json').read_text())]
def has(p,s):return bool(re.search(p,s,re.I))
# Explicit phrases, not star-based sentiment; all hit sentences are retained.
P={
'cool':('凉爽、少闷热或少出汗',r'keep\w* (?:me|us|you|him|her|my\s+\w+) (?:\w+\s+){0,3}cool|stays? (?:\w+\s+){0,2}cool|(?:feel\w*|touch|actually|really|very|nice and|so|super|quite|wonderfully|pleasantly|extremely) cool|cool(?:ing)? (?:to the touch|effect|sensation|feeling)|does (?:keep|cool)|no (?:more )?(?:night )?sweat|don.t (?:get hot|sweat)|not (?:too )?hot|without (?:getting |being )?(?:hot|overheat)|less (?:hot|sweat)|stopped sweating|helps?.{0,20}(?:hot flashes|night sweats)|breathable|doesn.t (?:get hot|trap heat)|haven.t.{0,12}sweat'),
'soft':('柔软、丝滑与舒适触感',r'\bsoft\b|\bsilky\b|buttery|comfortable|\bcomfy\b|\bcozy\b|\bsmooth\b'),
'weight':('厚薄、轻重与包裹感',r'perfect (?:weight|thickness)|right (?:weight|amount of weight|thickness)|just (?:enough|the right).{0,20}(?:weight|thick)|lightweight|light weight|weighted.{0,20}(?:feel|feeling)|love.{0,20}(?:weight|heavy)|nice weight|enough weight|not too heavy|not heavy|comfort.{0,15}(?:weight|hug)|fluffy'),
'sleep':('睡得更好或较少醒来',r'sleep(?:ing)? (?:so |much |a lot )?(?:better|well|great|soundly)|slept (?:so |much )?(?:better|well|great|all night)|best.{0,15}sleep|sleep like a baby|no longer.{0,15}wak|not.{0,15}waking|sleep through the night'),
'care':('易洗、洗后保持状态',r'wash(?:es|ed)? (?:up )?(?:well|great|beautiful|nicely)|easy to (?:wash|clean)|held up.{0,20}wash|no (?:shrink|pilling)|not.{0,5}shrink|dryer safe'),
'fit':('尺寸与覆盖范围',r'perfect size|size is perfect|fits? (?:\w+\s+){0,2}(?:perfect|great|well)|big enough|generous (?:size|sizing)|oversized|great size'),
'value':('价格与价值',r'worth (?:every|the|it)|good (?:price|value|deal)|great (?:price|value|deal)|reasonable|affordable|money well spent|less expensive|fraction of the (?:price|cost)'),
'quality':('做工与耐用',r'(?:good|great|excellent|high) quality|well made|well.made|durable|held up well'),
'color':('颜色与外观',r'(?:love|beautiful|gorgeous|great|pretty|nice).{0,18}colou?r|colou?r.{0,18}(?:love|beautiful|gorgeous|great|pretty|nice)|looks? (?:beautiful|great|nice)|beautiful blanket'),
'pet':('宠物毛发易清理',r'pet hair.{0,15}(?:off|not|doesn.t)|doesn.t.{0,20}(?:hair|fur)|hair.{0,15}(?:brush|wipe)|resist.{0,10}(?:pet|hair)'),
'service':('送货与服务',r'fast (?:shipping|delivery)|arrived (?:early|quick|on time)|great customer service|excellent customer service|replaced.{0,15}(?:free|quick)')}
M={
'cool':r'(?:not|isn.t|wasn.t|doesn.t|didn.t|don.t|no|zero|non).{0,24}cool|does not.{0,20}cool|not cooling|gets? (?:too |very |really )?(?:hot|warm)|traps?.{0,10}(?:heat|humidity)|still.{0,15}(?:sweat|hot)|(?:made|makes) me (?:hot|sweat)|hotter|only.{0,15}(?:cool|cold).{0,25}(?:first|minute)|cool.{0,20}(?:goes away|doesn.t last|does not last|at first)|warm.{0,8}quickly',
'soft':r'not.{0,12}(?:soft|comfortable)|scratchy|rough (?:feel|texture)|uncomfortable|stiff',
'weight':r'too (?:heavy|thick|thin|light)|heavier than|thinner than|wish.{0,15}(?:lighter|thicker)|weighs? a ton',
'fit':r'too (?:small|short|narrow)|not (?:large|big|wide|long) enough|doesn.t (?:fit|cover)|not fit|small for|wish.{0,15}(?:bigger|larger)|short on',
'quality':r'loose threads?|thread.{0,15}(?:loose|pull|unravel)|stitch.{0,15}(?:loose|undone|coming|unravel)|pilling|pills\b|snag\w*|ripped|rips\b|torn|tear\w*|falling apart|fell apart|holes?|seam.{0,15}(?:apart|rip|open)|poor quality|cheaply made',
'care':r'(?:wash|dryer|drying).{0,45}(?:ruined|damag|melt|clump|shrink|rip|tear|burn)|(?:ruined|melt|clump|shrink|rip|burn).{0,35}(?:wash|dryer)|hard to (?:wash|dry)|takes.{0,15}(?:forever|hours).{0,12}dry',
'slip':r'slip\w*|slides? (?:off|down|around)|slid off|won.t stay|doesn.t stay on',
'value':r'not worth|waste of money|too expensive|overpriced|return.{0,10}cost',
'color':r'color.{0,20}(?:different|wrong|not|faded)|not.{0,20}(?:color|photo)|not as pictured',
'odor':r'(?:smell|odor|stink).{0,20}(?:bad|chemical|strong)|(?:bad|chemical|strong).{0,20}(?:smell|odor)|stinks',
'service':r'never arrived|wrong (?:item|size|color)|no refund|return.{0,20}(?:denied|difficult)|customer service.{0,20}(?:bad|poor|horrible)'}
labels={k:v[0] for k,v in P.items()}|{'slip':'被子滑落、难固定','odor':'异味','general':'笼统认可或不满','contents':'套装内容与购买预期'}
labels['quality']='做工、勾丝起球与耐用';labels['weight']='厚薄、轻重与包裹感'
result=[]
for r in rows:
 text=(r['title']+'. '+r['body']).replace('’',"'")
 clauses=[s.strip() for s in re.split(r'[.!?;\n]+|\bbut\b|\bhowever\b',text,flags=re.I) if s.strip()]
 tags={'positive':set(),'negative':set()};ev={}
 for s in clauses:
  for k,(lab,p) in P.items():
   if has(p,s) and not has(M.get(k,r'(?!)'),s) and not has(r"(?:wanted|looking for|hoping|supposed|expected|used to|old blanket|previous blanket).{0,50}(?:"+p+")",s):
    if k=='soft' and has(r'cozy bliss',s) and not has(r'\bsoft\b|silky|buttery|comfortable|comfy|smooth',s):continue
    tags['positive'].add(k);ev.setdefault('positive:'+k,[]).append(s)
  for k,p in M.items():
   if has(p,s):
    if k=='quality' and has(r"no pilling|no snags|not.{0,8}(?:pill|snag)|never.{0,8}(?:pill|snag)|resist.{0,10}(?:pill|snag)|without.{0,10}(?:pill|snag)|doesn.t.{0,8}(?:pill|snag)",s):continue
    if k=='slip' and has(r"not.{0,8}slip|doesn.t.{0,8}slip|does not.{0,8}slip|no.{0,8}slip|slippery.{0,20}(?:like|love)",s):continue
    if k=='cool' and has(r"not (?:ice|icy|freezing) cold|not too cool|not too cold|not only|not (?:hot|warm)|no longer.{0,15}(?:hot|sweat)|doesn.t get hot",s):continue
    if k=='weight' and has(r'not too (?:heavy|thin|light|thick)',s):continue
    tags['negative'].add(k);ev.setdefault('negative:'+k,[]).append(s)
  if has(r'\blove (?:it|this|the)|great blanket|great comforter|perfect|highly recommend|very happy|excellent|amazing|best purchase',s) and not has(r"don.t|not|never|wasn.t|isn.t|didn.t|wish",s):tags['positive'].add('general')
  if has(r'disappoint|not recommend|don.t recommend|waste of money|horrible|terrible|not worth|not satisfied|returned it|returning it',s):tags['negative'].add('general')
 result.append(r|{k:sorted(v) for k,v in tags.items()}|{'evidence':ev})
# Overrides are filled only after reading the full review.
ov=R/'cozy_overrides.json'
if ov.exists():
 for r in result:
  if str(r['id']) in json.loads(ov.read_text()):r.update(json.loads(ov.read_text())[str(r['id'])])
N=len(result);pc=sum(bool(r['positive']) for r in result);nc=sum(bool(r['negative']) for r in result);bc=sum(bool(r['positive']) and bool(r['negative']) for r in result)
summ=dict(total=N,positive=pc,negative=nc,mixed=bc,unclassified=N-pc-nc+bc,positive_only=pc-bc,negative_only=nc-bc,positive_percent=round(pc/N*100,1),negative_percent=round(nc/N*100,1));st=[]
for v,den in [('positive',pc),('negative',nc)]:
 rank=0
 for k,n in collections.Counter(k for r in result for k in r[v]).most_common():
  if k!='general':rank+=1
  st.append(dict(code=k,label=labels[k],valence=v,count=n,percent_group=round(n/den*100,1),percent_all=round(n/N*100,1),general=k=='general',rank=rank if k!='general' else None,ids=[r['id'] for r in result if k in r[v]]))
(R/'cozy_coding.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));(R/'cozy_statistics.json').write_text(json.dumps(dict(summary=summ,rows=st),ensure_ascii=False,indent=2))
with (R/'CozyBliss_逐条主题编码.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['评论ID','星级','日期','子ASIN','Vine','认可主题','不认可主题','英文原文','命中原句','来源']);
 for r in result:w.writerow([r['id'],r['rating'],r['date'],r['asin'],r['vine'],'；'.join(labels[k] for k in r['positive']),'；'.join(labels[k] for k in r['negative']),r['body'],json.dumps(r['evidence'],ensure_ascii=False),r['url']])
print(summ)
for r in st:print(r['valence'],r['label'],r['count'],r['percent_all'])
