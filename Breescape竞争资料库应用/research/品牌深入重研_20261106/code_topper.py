"""Conservative, inspectable phrase coding; original reviews are never overwritten."""
import json,re,csv,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parent
rows=json.loads((ROOT/'topper_reviews.json').read_text())
def hit(p,t):return bool(re.search(p,t,re.I))
patterns={
 'soft':('柔软、舒适与贴身触感',r'\b(soft\w*|comf\w*|cozy|cosy|cozz\w*|snuggl\w*|plush\w*)\b|sleeping (on|in) (a |the )?cloud|feels? like.{0,12}(cloud|pillow)|muy c[oó]modo|super comodo'),
 'loft':('蓬松度、厚度与缓冲',r'fluff\w*|puff\w*|poof\w*|plump\w*|inflate\w*|expand\w*|thick\w*|cushion\w*|padding|\bflat\b|\bthin(?:ner|nest)?\b|\binch\w*|lumpy|\blump\b|stuffing|\bfill(?:ed|ing)?\b|esponj|acolchon'),
 'fit':('尺寸适配与包覆',r'\bfit(?:s|ting)?\b|deep pockets?|pockets are (?:very |extra |so )?deep|true to size|wrap\w*.{0,20}mattress|too (?:large|small|big)|wrong size'),
 'fixed':('固定、不滑移',r'stay\w* (?:in place|on|in bed)|slid\w*|slip\w*|move or shift|doesn.t move|doesn.t shift'),
 'temperature':('凉爽、透气与热感',r'cool\w*|\bhot\b|\bheat\b|sweat\w*|breath\w*|fresh|night sweats'),
 'sleep':('睡眠体验',r'sleep\w*|slept|night rest|rested|tossing|wake\w*|waking'),
 'ache':('身体不适与支撑感',r'pain|sore|ach(?:e|es|ing)|sciatica|support\w*|spasm'),
 'value':('价格与价值感',r'price|money|worth|deal|expensive|dollars|\$|cheap\w*|caro'),
 'delivery':('配送与履约',r'ship\w*|deliver\w*|arriv\w*|package|packaging|wrong (?:item|color|size)|never (?:got|received)|didn.t receive|no me.{0,6}llegado|no recib'),
 'service':('客服与退换',r'customer|seller|company|return|refund|send.{0,12}back|ship.{0,12}back|devolv'),
 'care':('洗护与拆包恢复',r'dryer|drying|wash\w*|clean\w*|instructions|fluffing process'),
 'quality':('做工与耐用',r'quality|durab\w*|well made|made very well|\brip(?:ped|s)?\b|torn|tore|tear|fray\w*|seam|damag\w*|stain\w*|burnmarks|\bhole\b|fell apart|fall apart|stitching'),
 'appearance':('外观与颜色',r'color|design|looks? (?:good|great|nice|beautiful)|pretty|beautiful|looks so fluffy'),
 'odor':('气味',r'smell|odor|stink'),
 'expectation':('与图片、视频或描述不符',r'advertis\w*|\bad\b|\badd\b|\bads\b|picture|photo|video|mislead\w*|deceiv\w*|description|described|propaganda|not what I (?:ordered|expected)|false'),
 'wrong_product':('把加垫误认为独立床垫',r'(?:thought|expected|expecting|ordered|ped[ií]|pedi|showed|show me|anuncian|cre[yí]|croyais).{0,70}(?:mattress|matelas|colch[oó]n|colchoneta|bed)|not a mattress|just (?:a|the) (?:cover|topper)|cubre colchon|cubre colch[oó]n')
}
neg=r"\b(?:not|never|no|isn.t|wasn.t|doesn.t|didn.t|won.t|can.t|couldn.t|barely|hardly)\b|disappoint\w*|poor|terrible|horrible|waste|mislead\w*|deceiv\w*|thin\b|flat\b|lumpy|cheaply|rip(?:ped)?\b|torn|damage\w*|stain\w*|scratch\w*|wrong|too (?:hot|small|big|large|soft)|wish|thought.{0,20}(?:thicker|softer|more)|less fluffy|could be (?:thicker|better)|not nearly|not near|uncomfortable|estafa|enga[nñ]\w*|delgad\w*|mala|malo|no sirve"
pos=r'\blove\w*\b|\bgreat\b|\bgood\b|perfect\w*|amazing|wonderful|excellent|nice|happy|recommend|comfortable|comfy|comfy|soft|cozy|cloud|fits?|fluffy|cool|better|best|worth|fast|quick|easy|help|reliev|no (?:pain|aches|smell|odor)|muy c[oó]modo'
coded=[]
for r in rows:
 text=r['body'].replace('’',"'").replace('“','"').replace('”','"')
 # A contrast starts a new claim: e.g. "not thick, but comfortable".
 clauses=[s.strip() for s in re.split(r'[.!?;\n]+|\bbut\b|\bhowever\b|\balthough\b',text,flags=re.I) if s.strip()]
 tags={};evidence={}
 for code,(label,pat) in patterns.items():
  for s in clauses:
   if not hit(pat,s):continue
   n=hit(neg,s);p=hit(pos,s)
   if code in ('soft','loft','fit','temperature','sleep','ache','fixed','care','quality','appearance','odor','value','delivery','service'):
    # Neutral mentions of setup, future use and price are not experiences.
    if code=='soft':
     n=hit(r"not.{0,20}(soft|comf|plush)|isn.t.{0,15}(soft|comf)|uncomfortable|scratch|not (?:add|make).{0,30}(soft|comf)|thought.{0,20}(soft|comf)|wish.{0,20}(soft|comf)|not change|no comfort|comfort: none|doesn.t seem softer|not that comfy",s)
     p=not n and not hit(r'(?:hoping|hope|wanted|expecting|thought).{0,35}(soft|comf|plush)|can.t wait|waiting|looking for|to be (?:fluffy and )?soft',s)
    elif code=='loft':
     n=hit(neg,s) or hit(r"not.{0,40}(inches|inch)|not.{0,25}(fluff|thick)|less than|closer to an inch|could.{0,5}be thicker|thought.{0,30}(thick|fluff)|barely|no padding|need.{0,15}more (?:foam|cushion)",s)
     p=hit(r'fluffy|fluffed.{0,15}(nicely|beautiful|great)|thick|plump|cushion|padding|puff.{0,10}up|fluff.{0,10}up|extra.{0,10}soft',s) and not n and not hit(r'(?:wait|waiting|hope|wish|expect|thought|instructions|recommend|have to|need to).{0,45}(fluff|expand|inflate|thick)|let it (?:sit|expand)|allow',s)
    elif code=='fit':
     n=hit(r"doesn.t fit|didn.t fit|not fit|too (?:small|large|big)|wrong size|ill fitting|not.{0,15}(reach|fit)|smaller than.{0,15}mattress|isn.t.{0,20}fit",s)
     p=not n and hit(r'fits? (?:my|the|our|a|well|perfect|great|very|bed|extremely)|fit: (?:perfect|great)|true to size|deep|wrap|long|fit by|yes.{0,10}fits?',s)
    elif code=='fixed':
     p=hit(r"stay\w*.{0,15}(place|on|bed)|doesn.t (?:move|shift|slip)|no.{0,10}slip|never slipped|don.t.{0,30}coming off|does not.{0,20}slide|doesn.t slip",s);n=not p
    elif code=='temperature':
     n=hit(r"not.{0,35}cool|isn.t.{0,15}cool|don.t.{0,20}cool|no.{0,20}cool|hot|heat|sweat|wish.{0,20}cool|can not tell.{0,35}cool",s)
     p=hit(r"cool|breath|fresh|no.{0,20}sweat|doesn.t.{0,20}hot|does not.{0,20}hot|not hot|doesn.t.{0,20}heat|no.{0,20}heat",s) and not hit(r"not.{0,35}cool|isn.t.{0,15}cool|don.t.{0,20}cool|no.{0,20}cool|wish.{0,20}cool|can not tell.{0,35}cool|haven.t.{0,15}(used|tried)|hope|haven't slept|price|wanted|got on this cooling",s)
     if p and hit(r"no.{0,20}sweat|not hot|does not.{0,20}hot|doesn.t.{0,20}hot|doesn.t.{0,20}heat",s):n=False
     if hit(r'cool color|color.{0,15}cool|coolguy|warm hug',s):p=n=False
    elif code=='sleep':
     p=hit(r'best.{0,20}sleep|sleep.{0,25}(better|great|well|good|sound|peace|amazing)|slept.{0,25}(better|great|well|good|baby|peace)|sleep like|sleep quality|quality.{0,15}sleep|slept fantastic|sleeping soundly|rested|no.{0,20}tossing|not tossing',s) and not hit(r"can.t wait|hope|haven.t|not sure|planning|supposed",s)
     n=hit(r"can.t sleep|sleep.{0,10}(worse|hot)|cannot sleep|not.{0,15}sleep well|trouble sleeping",s) and not hit(r'if you|before|current|used to|had been',s)
    elif code=='ache':
     p=hit(r"no (?:more )?.{0,15}(pain|aches|sore)|pain.{0,12}(gone|ease)|help\w*.{0,20}(pain|hip|back)|reliev|reduc|alleviat|support.{0,10}(great|amazing)|great support|good.{0,15}(support|back)|not sore|not.{0,15}ache|no back|took.{0,10}pain away|back.{0,15}(better|happy|hurt less)|hurts less",s)
     n=hit(r"no support|not.{0,15}support|still.{0,20}(sore|pain|hurt|ache)|not.{0,15}(help|change).{0,15}(pain|back)|cause.{0,15}back|zero (?:support|supper)|no.{0,15}difference",s)
    elif code=='value':
     n=hit(r"not.{0,15}worth|waste|too.{0,10}expensive|way too|ripoff|overpriced|caro|disappoint|could.{0,25}(cheaper|better)|better.{0,20}same price",s)
     p=not n and hit(r'worth|great deal|good deal|happy.{0,20}deal|price.{0,15}(great|good|lower|perfect)|for (?:the|its) price|deal I got|best buy|money well spent|only \$|price isn.t bad|less cheap than a new',s)
    elif code=='delivery':
     n=hit(r'wrong|never got|never received|didn.t receive|delayed|took forever|no me|no recib|damag|torn|flashlights|used|stain|not what.{0,20}ordered',s)
     p=not n and hit(r'fast|quick|on time|timely|prompt|packaged well|packed very well|excellent packaging|within [234] days|in two days|in 2 days|in 3 days|in about 4 days|without issues|no issues',s)
    elif code=='care':
     n=hit(r'not|never|didn.t|doesn.t|no fluff|burn|rip|tough|hard time|does not|almost.{0,15}fire|did not|no change|only reason|disappoint|didn.t like',s)
     p=not n and hit(r'easy.{0,10}(wash|clean|set)|wash.{0,10}well|dryer.{0,25}(worked|difference|fluffy)|fluffed.{0,15}(nicely|beautiful|great)|no complications|safe to wash|very simple',s)
    elif code=='quality':
     n=hit(r'poor|bad|low|cheap|\brip|torn|tore|tear|fray|damag|stain|burn|hole|come apart|fall apart|fell apart|not.{0,15}(great|good)',s)
     p=not n and hit(r'good quality|great quality|excellent quality|quality material|quality bamboo|well made|made very well|durab|high.quality|quality is perfect|quality is very good',s)
    elif code=='odor':
     p=hit(r'no |didn.t have|don.t stink|no fowl|no foul',s);n=not p
    elif code=='appearance':
     p=hit(r'color.{0,12}(perfect|love|match|good|great)|love.{0,20}(color|design|pattern)|looks? (?:good|great|nice|beautiful)|pretty|beautiful|looks so fluffy',s);n=hit(r'wrong color|stain|color.{0,12}(wrong|bad)',s)
    elif code=='service':
     n=hit(r'won.t|denied|difficult|can.t|no clue|never|no response|cost|pay|poor|horrible|blocked|not professional|pack.{0,10}back|how.{0,20}(ship|return)|time and gas|gas|hoops|drag|refund \$8',s)
     p=hit(r'helpful|willing|prompt|quick|friendly|top notch|informative|took care|great customer|excellent|accommodat|resent|proactive',s) and not n
   elif code=='expectation':p=False;n=hit(neg,s) or hit(r'nothing like|not.{0,30}(picture|video|ad|describ)|less than|misleading',s)
   elif code=='wrong_product':
    p=False;n=hit(r'not a mattress|(?:thought|expecting|expected).{0,25}(actual mattress|full bed|mattress)|ped[ií].{0,15}colch|croyais|colch[oó]n plegable|not the floor|showed.{0,25}whole|show me.{0,15}mattress|cubre colchon|cubre colch[oó]n|pedi un colchon',s)
   for v,b in [('positive',p),('negative',n)]:
    if b:tags.setdefault(v,set()).add(code);evidence.setdefault(v+':'+code,[]).append(s)
 # General evaluation only if actually expressed, not inferred from rating.
 for s in clauses:
  if hit(r'\blove (?:it|this|the product)|great product|nice product|amazing product|recommend|excellent product|best purchase|very happy',s) and not hit(r"not|never|don.t|wouldn.t|didn.t|no ",s):tags.setdefault('positive',set()).add('general')
  if hit(r'disappoint|not recommend|don.t recommend|wouldn.t.{0,12}(buy|recommend)|waste|horrible|terrible|garbage|not what.{0,15}expected|estafa|enga[nñ]|mala calidad|not sat|no estoy sati',s):tags.setdefault('negative',set()).add('general')
 coded.append(dict(id=r['id'],rating=r['rating'],date=r['date'],sku=r['sku'],body=r['body'],positive=sorted(tags.get('positive',[])),negative=sorted(tags.get('negative',[])),evidence=evidence))
# Manual overrides follow whole-comment reading: prevent expectations, historical
# experiences, seller allegations and retained products being coded as satisfaction.
overrides={
 1632:{'positive':[],'negative':['loft','general']},1640:{'positive':['general','soft'],'negative':[]},1641:{'positive':['soft'],'negative':[]},1644:{'positive':['service','loft'],'negative':[]},1667:{'positive':[],'negative':['delivery']},1671:{'positive':[],'negative':['delivery']},1672:{'positive':['soft','care'],'negative':[]},1679:{'positive':[],'negative':['fit']},1680:{'positive':['fit'],'negative':[]},1700:{'positive':['general'],'negative':[]},1713:{'positive':[],'negative':['general','value']},1729:{'positive':[],'negative':['loft']},1730:{'positive':[],'negative':['fit']},1733:{'positive':['general'],'negative':[]},1744:{'positive':['general'],'negative':[]},1766:{'positive':[],'negative':['general','loft']},1770:{'positive':[],'negative':['soft']},1771:{'positive':['general'],'negative':['loft']},1772:{'positive':['fit'],'negative':[]},1780:{'positive':[],'negative':['loft','expectation']},1787:{'positive':['sleep'],'negative':[]},1788:{'positive':[],'negative':['delivery','service']},1798:{'positive':['general'],'negative':[]},1814:{'positive':[],'negative':['delivery','service']},1826:{'positive':[],'negative':['quality']},1830:{'positive':[],'negative':['delivery']},1837:{'positive':['general'],'negative':[]},1857:{'positive':['soft'],'negative':[]},1898:{'positive':[],'negative':['loft','general']},1925:{'positive':[],'negative':['loft','expectation']},1977:{'positive':['general'],'negative':[]},1979:{'positive':['soft'],'negative':[]},2005:{'positive':[],'negative':['ache','loft']},2070:{'positive':[],'negative':['loft']},2071:{'positive':[],'negative':['loft','expectation']},2078:{'positive':[],'negative':['quality','value']},2089:{'positive':[],'negative':['delivery']},2092:{'positive':[],'negative':['loft','general']},2109:{'positive':['loft','fit'],'negative':[]},2112:{'positive':[],'negative':['loft','general']},2117:{'positive':[],'negative':['delivery']},2142:{'positive':[],'negative':['fit']},2148:{'positive':['fit'],'negative':['loft','ache','expectation']},2178:{'positive':[],'negative':['delivery']},2216:{'positive':[],'negative':['delivery']},2229:{'positive':['service'],'negative':['loft']},2242:{'positive':[],'negative':['delivery']},2245:{'positive':[],'negative':['loft']},2308:{'positive':['sleep'],'negative':[]},2323:{'positive':['soft'],'negative':[]},2390:{'positive':['general','sleep','ache'],'negative':[]},2434:{'positive':[],'negative':[]},2458:{'positive':[],'negative':['delivery']},2474:{'positive':['fit'],'negative':[]},2512:{'positive':[],'negative':['loft']},2517:{'positive':['general'],'negative':['delivery']},2525:{'positive':['loft','general'],'negative':[]},2532:{'positive':[],'negative':['loft']},2533:{'positive':[],'negative':['expectation']},2536:{'positive':['sleep'],'negative':[]},2561:{'positive':['general','ache','delivery'],'negative':[]},2567:{'positive':['soft'],'negative':['loft']},2590:{'positive':['soft','fit','delivery'],'negative':[]},2601:{'positive':['sleep'],'negative':[]},
 2014:{'positive':[],'negative':['loft','expectation','value']},
 2067:{'positive':[],'negative':['loft','soft']},
 2116:{'positive':[],'negative':['delivery']},
 2210:{'positive':[],'negative':['soft','quality','general']},
 2321:{'positive':[],'negative':[]},
 2455:{'positive':['general'],'negative':[]},
 2482:{'positive':['soft','loft','fit'],'negative':['temperature']},
 2514:{'positive':[],'negative':['delivery']},
 2573:{'positive':['soft','sleep','fit','appearance'],'negative':[]},
 2417:{'positive':['service'],'negative':['delivery']},
 2050:{'positive':['fit'],'negative':['loft','value','expectation','general']},
 1868:{'positive':['care'],'negative':['loft','expectation']},
 2132:{'positive':[],'negative':['loft','service','general']},
 2432:{'positive':['appearance'],'negative':['soft','expectation','general']},
}
for r in coded:
 if r['id'] in overrides:
  r.update(overrides[r['id']]);r['manual_override']=True
 # Temperature statements have all been checked in context; exclude dryer heat,
 # the room/old bedding temperature, buying motives, and "refreshed".
 for v,ids in [('positive',[1725,1731,1746,1757,1764,1776,1796,1799,1817,1832,1874,1890,1916,1918,1934,1935,2088,2095,2102,2127,2137,2151,2165,2187,2209,2225,2241,2247,2258,2261,2262,2283,2285,2296,2318,2336,2349,2379,2388,2401,2456,2557,2607,2613,2618,2628]),('negative',[1634,1655,1807,1819,1829,1864,1871,1983,2036,2123,2131,2291,2326,2327,2335,2364,2410,2427,2482,2508,2555])]:
  r[v]=[x for x in r[v] if x!='temperature']+(['temperature'] if r['id'] in ids else [])
 # Contrasts/old mattresses/"not too much" are not a loft defect.
 if r['id'] in [1692,1736,1856,1961,2010,2065,2102,2123,2129,2145,2233,2384,2409,2412,2422,2483,2487,2491,2593,2595]:r['negative']=[x for x in r['negative'] if x!='loft']
 if r['id'] in [1639,1741,1743,1757,1758,1819,1931,2129,2131,2232,2301,2440,2562,2572]:r['negative']=[x for x in r['negative'] if x!='quality']

out=ROOT/'topper_coding.json';out.write_text(json.dumps(coded,ensure_ascii=False,indent=2))
count=collections.Counter()
for r in coded:
 for v in ('positive','negative'):
  for t in r[v]:count[v,t]+=1
N=len(coded);P=sum(bool(r['positive']) for r in coded);M=sum(bool(r['negative']) for r in coded);B=sum(bool(r['positive']) and bool(r['negative']) for r in coded)
summary=dict(total=N,positive=P,negative=M,mixed=B,unclassified=N-P-M+B,positive_only=P-B,negative_only=M-B,positive_percent=round(100*P/N,1),negative_percent=round(100*M/N,1))
labels={k:v[0] for k,v in patterns.items()}|{'general':'一般性喜欢、不满或推荐'}
stats=[]
for v,base in [('positive',P),('negative',M)]:
 rank=0
 for (vv,t),n in count.most_common():
  if vv!=v:continue
  if t!='general':rank+=1
  stats.append(dict(code=t,label=labels[t],valence=v,count=n,percent_group=round(n/base*100,1),percent_all=round(n/N*100,1),general=t=='general',rank=rank if t!='general' else None,ids=[r['id'] for r in coded if t in r[v]]))
(ROOT/'topper_statistics.json').write_text(json.dumps(dict(summary=summary,rows=stats),ensure_ascii=False,indent=2))
with (ROOT/'topper_逐条编码.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['库内评论ID','星级','日期','规格','认可主题','不认可主题','原文','命中原句','人工修订'])
 for r in coded:w.writerow([r['id'],r['rating'],r['date'],r['sku'],'；'.join(labels[x] for x in r['positive']),'；'.join(labels[x] for x in r['negative']),r['body'],json.dumps(r['evidence'],ensure_ascii=False),r.get('manual_override',False)])
print(summary)
for s in stats:print(s['valence'],s['label'],s['count'],s['percent_group'])
print('UNCLASSIFIED',[(r['id'],r['body']) for r in coded if not r['positive'] and not r['negative']])
