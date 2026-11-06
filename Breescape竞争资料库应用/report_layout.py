"""User-edited presentation, separate from the research source document."""
from html.parser import HTMLParser
from html import escape
import json,re
class Clean(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.out=[];self.block=0
 def handle_starttag(self,t,attrs):
  if t in ('script','style','iframe','object','embed','svg','math'):self.block+=1;return
  if self.block:return
  if t not in 'div span p h1 h2 h3 h4 h5 h6 section article nav header footer figure figcaption img a b strong i em u s br hr ul ol li table thead tbody tr th td details summary small dl dt dd button sup sub font blockquote'.split():return
  safe=[]
  for k,v in attrs:
   v=v or ''
   if k in ('href','src'):
    if not (v.startswith(('https://','http://','#','/attachment/','data:image/png;base64,','data:image/jpeg;base64,','data:image/webp;base64,'))):continue
   elif k=='style':
    allowed={'color','background-color','font-size','font-weight','font-style','text-align','text-decoration','line-height','width','max-width','height','margin','margin-left','margin-right','display'}
    v=';'.join(x for x in v.split(';') if ':' in x and x.split(':')[0].strip().lower() in allowed and not re.search(r'url|expression|javascript|[<>]',x,re.I))
   elif k not in ('class','id','title','alt','colspan','rowspan','open','size','color','face','target','rel','aria-label','role') and not k.startswith('data-'):continue
   safe.append(f' {k}="{escape(v,quote=True)}"')
  self.out.append('<'+t+''.join(safe)+'>')
 def handle_endtag(self,t):
  if t in ('script','style','iframe','object','embed','svg','math'):
   self.block=max(0,self.block-1);return
  if not self.block and t in 'div span p h1 h2 h3 h4 h5 h6 section article nav header footer figure figcaption a b strong i em u s ul ol li table thead tbody tr th td details summary small dl dt dd button sup sub font blockquote'.split():self.out.append('</'+t+'>')
 def handle_data(self,s):
  if not self.block:self.out.append(escape(s))
def save(c,d,now):
 row=c.execute('select document from brand_reports where brand_id=?',(d.get('brand_id'),)).fetchone()
 if not row:raise ValueError('品牌不存在')
 doc=json.loads(row[0]);history=doc.setdefault('layout_history',[])
 if d.get('action')=='undo':
  if not history:raise ValueError('没有可恢复的版本')
  doc['manual_layout']=history.pop()
 else:
  history.append(doc.get('manual_layout'));doc['layout_history']=history[-10:]
  if d.get('action')=='reset':doc['manual_layout']=None
  else:
   raw=d.get('html','')
   if not isinstance(raw,str) or not 1<len(raw)<15_000_000:raise ValueError('内容为空或图片过大，请使用较小图片')
   p=Clean();p.feed(raw)
   doc['manual_layout']={'html':''.join(p.out),'saved_at':now,'research_updated_at':doc.get('updated_at')}
 c.execute('update brand_reports set document=? where brand_id=?',(json.dumps(doc,ensure_ascii=False),d['brand_id']))
 return {'message':'总览排版已保存' if d.get('action') not in ('undo','reset') else '已恢复总览版本'}
