import json, re, html, sys, urllib.request, signal
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

W = Path(__file__).parent
def fetch(key,url):
    entry={'key':key,'url':url,'retrieved_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')}
    try:
        def deadline(signum,frame): raise TimeoutError('页面读取超过45秒')
        signal.signal(signal.SIGALRM,deadline);signal.alarm(45)
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req,timeout=25) as r:
            data=r.read();entry.update(status=r.status,final_url=r.url,bytes=len(data))
        raw=data.decode('utf-8',errors='replace')
        (W/(key+'.raw')).write_text(raw)
        entry['links']=[{'url':html.unescape(u),'label':html.unescape(re.sub('<[^>]+>',' ',t)).strip()} for u,t in re.findall(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',raw,re.S|re.I)]
        entry['images']=re.findall(r'<meta\b[^>]*(?:property|name)=["\']og:image["\'][^>]*>',raw,re.I)
        text=html.unescape(re.sub('<[^>]+>',' ',re.sub(r'<(script|style)\b[^>]*>.*?</\1>',' ',raw,flags=re.S)))
        (W/(key+'.txt')).write_text(re.sub(r'\s+',' ',text))
    except Exception as e:entry['error']=str(e)
    finally:signal.alarm(0)
    (W/(key+'.meta.json')).write_text(json.dumps(entry,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in entry.items() if k not in ['links','images']},ensure_ascii=False),flush=True)
    return entry
if __name__=='__main__':
    for key,url in json.loads(Path(sys.argv[1]).read_text()).items():fetch(key,url)
