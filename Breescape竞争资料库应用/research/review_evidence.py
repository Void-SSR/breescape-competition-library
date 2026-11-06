"""Reproducible theme index. Mentions are NOT sentiment, prevalence or purchase motivation."""
import sqlite3,json,re,csv
from pathlib import Path
root=Path(__file__).resolve().parents[1]
c=sqlite3.connect(root/'data/library.sqlite3');c.row_factory=sqlite3.Row
rows=list(c.execute('select * from reviews where product_id="sheets" order by id'))
patterns={
'触感/舒适':r'\b(soft\w*|silk\w*|smooth\w*|comfort\w*|rough\w*|scratch\w*|itch\w*)\b|suav\w*|c[oó]mod\w*',
'凉感/热/汗':r'\b(cool\w*|hot|hotter|heat\w*|warm\w*|sweat\w*|breathab\w*|temperature)\b|fresc\w*|calor',
'尺寸/固定':r'\b(fit\w*|pocket\w*|slip\w*|pop\w* off|stay\w* on|stays? in place|corners?|elastic)\b|too small|too big',
'耐久/洗护':r'\b(wash\w*|pill\w*|ripp\w*|torn|tear\w*|stitch\w*|durab\w*|last\w*|shrink\w*)\b',
'成分/材料':r'\b(bamboo|polyester|microfiber|blend\w*|cotton)\b',
'价格/价值':r'\b(price\w*|cheap\w*|expensive|money|worth|afford\w*|sale)\b',
'颜色/外观':r'\b(colou?r\w*|pretty|beautiful|picture\w*|look\w*)\b',
'物流/售后':r'\b(deliver\w*|receiv\w*|shipping|refund\w*|return\w*|package\w*)\b'}
counts={k:{'近期全星级':0,'一星补充':0,'推荐样本':0} for k in patterns};out=[]
for r in rows:
 raw=json.loads(r['raw_json']);scope=raw.get('采样范围','');cohort='近期全星级' if '全部星级' in scope else ('一星补充' if '一星评论补充' in scope else '推荐样本')
 tags=[];hits=[]
 for theme,p in patterns.items():
  ms=list(re.finditer(p,r['body'],re.I))
  if ms:tags.append(theme);counts[theme][cohort]+=1;hits.append(theme+':'+','.join(dict.fromkeys(m.group() for m in ms)))
 out.append({'本库评论ID':r['id'],'平台评论ID':r['external_id'],'商品ID':'1729438233542234865','样本组':cohort,'原采样范围':scope,'发表日期':r['date'],'星级':r['rating'],'关键词提及主题':'；'.join(tags),'命中词':'；'.join(hits),'评论原文':r['body']})
a=root/'data/attachments';p=a/'Shilucheng_床单评论_关键词索引_2026-11-05.csv'
with p.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=out[0].keys());w.writeheader();w.writerows(out)
summary={'方法':'全量原文的确定性关键词检索；多标签、每条每主题至多计1次。没有自动判定褒贬或购买动机，不是语义TOP3。','局限':'英文与部分西语词干检索，存在语义漏检或歧义；不能作为需求发生率、满意度或市场规模。','分组':{'近期全星级':928,'一星补充':687,'推荐样本':13},'样本数':len(rows),'计数':counts,'规则':patterns}
(a/'Shilucheng_床单评论_关键词索引说明_2026-11-05.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print(json.dumps(summary,ensure_ascii=False,indent=2))
