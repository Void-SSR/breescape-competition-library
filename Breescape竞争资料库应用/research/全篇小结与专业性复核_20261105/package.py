from pathlib import Path
import json, sqlite3, shutil, zipfile, html, re, hashlib
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[2]
WORK=Path(__file__).parent
name='Shilucheng_品牌研究总览_全篇复核版_2026-11-05'
out=ROOT/'报告导出'/name
assert not out.exists()
out.mkdir()
with zipfile.ZipFile(WORK/'base-export.zip') as z:
    for entry in z.infolist():
        p=Path(entry.filename)
        assert '..' not in p.parts
        dest=out/Path(*p.parts[1:])
        if entry.is_dir():dest.mkdir(parents=True,exist_ok=True)
        else:
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(z.read(entry))
prior=ROOT/'报告导出/Shilucheng_品牌研究总览_音轨转写补充_2026-11-05'
shutil.copytree(prior/'音轨转写证据',out/'音轨转写证据')
shutil.copytree(ROOT/'data/attachments/全篇查验_20261105',out/'本轮补充查验')
c=sqlite3.connect(ROOT/'data/library.sqlite3');c.row_factory=sqlite3.Row
links={}
for mid in [56,57,58,59,60,80,81,82,83,87]:
    m=c.execute('select * from materials where id=?',(mid,)).fetchone()
    filename=Path(m['local_path']).name
    if mid in [56,57,58,59,60]:rel=Path('音轨转写证据/原视频')/filename
    elif mid in [80,81,82]:rel=Path('音轨转写证据')/filename
    else:rel=Path('本轮补充查验')/filename
    assert (out/rel).is_file(),rel
    links[m['title']+' ↗（附件已收录于本地资料库）']=(m['title']+' ↗',quote(rel.as_posix(),safe='/'))
report=(out/'报告.html').read_text()
hits={k:0 for k in links}
def replace(match):
    attrs,inner=match.group(1),match.group(2)
    text=html.unescape(re.sub('<[^>]+>','',inner))
    if text in links and not re.search(r'\bhref=',attrs):
        title,url=links[text];hits[text]+=1
        return '<a'+attrs+' href="'+html.escape(url,quote=True)+'">'+html.escape(title)+'</a>'
    return match.group(0)
report=re.sub(r'<a\b([^>]*)>(.*?)</a>',replace,report,flags=re.S)
assert all(hits.values()),hits
(out/'报告.html').write_text(report)
(out/'阅读说明.txt').write_text('''Shilucheng品牌研究总览｜全篇复核版｜2026-11-05

解压整个文件夹后，双击“报告.html”阅读。正文和截图、关键原评论、评论统计、五条视频与音轨转写、本轮补查说明可离线访问；原始网站链接需要联网。

本轮按六板块重写小结与关联研究条目，并核对影响结论的材料和原评论。新增“本轮补充查验”说明，区分事实、商家主张、分析和待验证机会。

“证据 v1.2”保留原有评论编码、统计和当时分析文件，不覆写历史。若其中旧的解释措辞与本报告不同，以本次报告及补查说明为最新研究判断；原始评论与统计数没有变化。

“音轨转写证据”保留先前完成的自动识别和原视频；尚未人工回听，不把模型一致视作事实认证。

本轮客户资料核对说明包含内部复盘及访谈摘录和原件定位，适用于项目内部研究与汇报。未打包完整客户访谈。旧版本仍保留在原目录。
''')
manifest={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()}
(WORK/'export-files.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
archive=out.with_suffix('.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(out.rglob('*')):
        if p.is_file():z.write(p,Path(name)/p.relative_to(out))
with zipfile.ZipFile(archive) as z:
    for p,h in manifest.items():assert hashlib.sha256(z.read(name+'/'+p)).hexdigest()==h
result={'folder':str(out),'html':str(out/'报告.html'),'zip':str(archive),'files':len(manifest),'size_bytes':archive.stat().st_size,'relinked':sum(hits.values())}
(WORK/'delivery.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
