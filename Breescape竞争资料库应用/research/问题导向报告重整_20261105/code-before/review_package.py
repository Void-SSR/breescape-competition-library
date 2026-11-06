"""Read-only access to the fixed, reviewed sheets analysis and portable evidence."""
import csv
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

KEY = 'review_analysis:sheets:v1.2'


def manifest(c):
    row = c.execute('SELECT value FROM meta WHERE key=?', (KEY,)).fetchone()
    return json.loads(row[0]) if row else None


def fixed_path(data, item):
    path = (data / item['local_path']).resolve()
    if data.resolve() not in path.parents:
        raise ValueError('证据路径无效')
    if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
        raise ValueError('固定v1.2证据校验不符，请复核附件')
    return path


def analysis_rows(c, data):
    m = manifest(c)
    if not m:
        return {}
    item = next(f for f in m['files'] if f['key'] == 'reviews')
    with fixed_path(data, item).open(encoding='utf-8-sig', newline='') as f:
        return {int(r['review_id']): r for r in csv.DictReader(f)}


def review(c, data, product_id, rid, index=None):
    if not re.fullmatch(r'[1-9][0-9]*', str(rid)):
        raise ValueError('评论编号须为正整数')
    if int(rid) > 9223372036854775807:
        raise ValueError('评论编号超出有效范围')
    if not product_id:
        raise ValueError('请指定产品')
    row = c.execute('SELECT * FROM reviews WHERE product_id=? AND id=?',
                    (product_id, int(rid))).fetchone()
    if not row:
        return None
    result = dict(row)
    raw = json.loads(result.pop('raw_json'))
    result.pop('normalized', None)
    result['source_group'] = '未纳入v1.2分析'
    result['sample_scope'] = raw.get('采样范围', '')
    result['source_files'] = raw.get('来源文件', '')
    result['collected_at'] = raw.get('采集日期', '')
    m = manifest(c)
    if m and product_id == m['product_id']:
        item = (index if index is not None else analysis_rows(c, data)).get(int(rid))
        if item:
            if item['body'] != row['body'] or item['external_review_id'] != row['external_id']:
                raise ValueError('原评论与固定v1.2证据不一致，请复核')
            result['source_group'] = item['source_group']
            result['source_files'] = item['source_files']
    p = c.execute('SELECT url,external_id,name FROM products WHERE id=?', (product_id,)).fetchone()
    result.update(product_url=p['url'], external_product_id=p['external_id'], product_name=p['name'])
    return result


def publication(c, data):
    m = manifest(c)
    if not m:
        return None
    out = dict(m)
    index = analysis_rows(c, data)
    out['reviews'] = []
    for rid in m['review_ids']:
        r = review(c, data, m['product_id'], rid, index)
        if not r:
            raise ValueError('固定研究的原评论不存在')
        out['reviews'].append(r)
    return out


def package(c, data, payload):
    """Package the same client-rendered report with immutable evidence copies."""
    import reports
    m = manifest(c)
    if not m or payload.get('brand_id') != m['brand_id']:
        raise ValueError('该品牌没有对应的v1.2证据包')
    doc = c.execute('SELECT updated_at FROM brand_reports WHERE brand_id=?', (m['brand_id'],)).fetchone()
    if payload.get('document_updated_at') != doc[0]:
        raise ValueError('报告已更新，请刷新后导出')
    expected = payload.get('revisions', {})
    if any(expected.get(str(n)) != reports.section_revision(c, m['brand_id'], n) for n in range(1, 7)):
        raise ValueError('研究依据已更新，请刷新并复核后导出')
    html = payload.get('html', '')
    if not isinstance(html, str) or not html.startswith('<!doctype html>'):
        raise ValueError('报告内容无效')
    attachment_ids = payload.get('attachment_ids', [])
    if not isinstance(attachment_ids, list) or len(attachment_ids) > 150 or any(type(x) is not int or x <= 0 for x in attachment_ids):
        raise ValueError('附件清单无效')
    allowed = {r[0] for r in c.execute('SELECT material_id FROM material_links WHERE brand_id=?', (m['brand_id'],))}
    for row in c.execute('SELECT evidence FROM records WHERE brand_id=?', (m['brand_id'],)):
        allowed.update(json.loads(row[0] or '[]'))
    attachments = []
    for mid in dict.fromkeys(attachment_ids):
        if mid not in allowed:
            raise ValueError('附件须属于当前品牌的研究依据')
        item = c.execute('SELECT title,local_path FROM materials WHERE id=?', (mid,)).fetchone()
        if not item or not item['local_path']:
            raise ValueError('附件不存在')
        path = (data / item['local_path']).resolve()
        if data.resolve() not in path.parents or not path.is_file():
            raise ValueError('附件文件不可用')
        name = f"{mid}_{Path(item['local_path']).name}"
        attachments.append((mid, item['title'], path, name))
    folder = 'Shilucheng_品牌研究总览_完整证据_2026-11-05'
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(folder + '/报告.html', html)
        for item in m['files']:
            archive.write(fixed_path(data, item), folder + '/证据 v1.2/' + item['filename'])
        archive.writestr(folder + '/证据 v1.2/文件校验.json', json.dumps(m, ensure_ascii=False, indent=2))
        for mid, title, path, name in attachments:
            archive.write(path, folder + '/附件/' + name)
        archive.writestr(folder + '/附件校验.json', json.dumps([
            {'material_id': mid, 'title': title, 'filename': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
            for mid, title, path, name in attachments], ensure_ascii=False, indent=2))
        archive.writestr(folder + '/阅读说明.txt',
            '双击“报告.html”。请保留它与“证据 v1.2”“附件”文件夹的相对位置，并整体分享。\n'
            '正文、统计表、截图、术语解释及关键原评论可离线阅读；保存的视频可点击播放。随附CSV/JSON/Markdown可下载、搜索和核验。\n'
            '完整评论编号、主题分子和原文见随附证据；外部商品与来源网站仍需联网。\n'
            '研究限于既有样本，不代表消费者总体、复购率或销量因果。\n')
    return stream.getvalue(), folder + '.zip'
