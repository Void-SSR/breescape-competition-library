"""Persisted editorial summaries, with references to the existing evidence store."""
import hashlib
import json

COVERAGE = ('已回答', '部分回答', '尚未研究', '资料待补', '待你确认', '等待前置研究')
ANSWER_TYPES = ('事实概括', '分析判断', '研究问题')


def init(c):
    c.execute('''CREATE TABLE IF NOT EXISTS brand_reports(
      brand_id TEXT PRIMARY KEY REFERENCES brands(id), document TEXT NOT NULL,
      updated_at TEXT NOT NULL)''')


def section_revision(c, brand_id, section):
    records = [dict(r) for r in c.execute(
        'SELECT * FROM records WHERE brand_id=? AND section=? ORDER BY id', (brand_id, section))]
    materials = [dict(r) for r in c.execute('''SELECT DISTINCT m.* FROM materials m
      JOIN material_links l ON m.id=l.material_id WHERE l.brand_id=? AND l.section=? ORDER BY m.id''', (brand_id, section))]
    extra = []
    if section == 2:
        extra = [dict(r) for r in c.execute('''SELECT o.* FROM observations o JOIN products p
          ON p.id=o.product_id WHERE p.brand_id=? ORDER BY o.id''', (brand_id,))]
        extra += [dict(r) for r in c.execute('''SELECT p.id,p.name,count(r.id) review_count,max(r.id) last_review
          FROM products p LEFT JOIN reviews r ON r.product_id=p.id WHERE p.brand_id=? GROUP BY p.id ORDER BY p.id''', (brand_id,))]
    raw = json.dumps([records, materials, extra], ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def empty_document(c, brand, topics):
    products = [dict(r) for r in c.execute('SELECT id,name FROM products WHERE brand_id=? ORDER BY rowid', (brand['id'],))]
    sections = []
    for section in range(1, 7):
        rows = []
        scopes = [p['id'] for p in products] if section == 2 else [None]
        for pid in scopes:
            for topic in topics[section]:
                rows.append({'topic': topic, 'product_id': pid, 'finding': '', 'record_ids': [], 'featured': [],
                             'bullets': [], 'coverage': '尚未研究', 'answer_type': '研究问题', 'gap': '', 'impact': '', 'figures': []})
        sections.append({'number': section, 'headline': '', 'summary': '', 'boundary': '',
                         'topics': rows, 'images': [], 'reviewed_revision': '', 'updated_at': ''})
    return {'title': brand['name'] + ' 品牌研究总览', 'summary': '', 'scope': '',
            'summary_record_ids': [], 'profile': [], 'cover_figure': None, 'updated_at': '', 'reviewed_revisions': {}, 'sections': sections}


def documents(c, topics):
    output = []
    for brand in c.execute('SELECT * FROM brands ORDER BY rowid').fetchall():
        row = c.execute('SELECT document FROM brand_reports WHERE brand_id=?', (brand['id'],)).fetchone()
        doc = json.loads(row[0]) if row else empty_document(c, brand, topics)
        doc['brand_id'] = brand['id']
        # New products automatically receive their own empty research outline.
        defaults = empty_document(c, brand, topics)
        for s in doc['sections']:
            known = {(t['topic'], t.get('product_id')) for t in s['topics']}
            for t in defaults['sections'][s['number'] - 1]['topics']:
                if (t['topic'], t.get('product_id')) not in known:
                    s['topics'].append(t)
            s['current_revision'] = section_revision(c, brand['id'], s['number'])
            s['stale'] = bool(s['reviewed_revision'] and s['reviewed_revision'] != s['current_revision'])
        doc['summary_stale'] = bool(doc.get('summary')) and any(
            doc.get('reviewed_revisions', {}).get(str(s['number'])) != s['current_revision'] for s in doc['sections'])
        output.append(doc)
    return output


def save(c, data, topics, timestamp):
    bid = data.get('brand_id')
    doc = next((x for x in documents(c, topics) if x['brand_id'] == bid), None)
    if not doc:
        raise ValueError('请选择已有品牌')
    section = int(data.get('section', 0))
    if section not in range(7):
        raise ValueError('报告板块无效')

    def text(key, limit=6000):
        value = str(data.get(key, '')).strip()
        if len(value) > limit:
            raise ValueError('内容过长，请保留关键信息')
        return value

    def references(ids, number=None, topic=None, pid=None):
        if not isinstance(ids, list):
            raise ValueError('引用格式无效')
        for rid in ids:
            r = c.execute('SELECT * FROM records WHERE id=?', (int(rid),)).fetchone()
            if not r or r['brand_id'] != bid or (number and r['section'] != number):
                raise ValueError('引用须属于当前品牌及对应板块')
            if topic and r['topic'] != topic:
                raise ValueError('引用须对应当前框架问题')
            if number == 2 and r['product_id'] != pid:
                raise ValueError('单品论据不能混用其他产品')
        return list(dict.fromkeys(int(x) for x in ids))

    def figures(items, number, topic=None, pid=None):
        if not isinstance(items, list) or len(items) > 8:
            raise ValueError('每个问题最多展示8张截图')
        result = []
        for item in items:
            mid = int(item.get('material_id', 0))
            rows = c.execute('''SELECT m.local_path,l.topic,l.product_id FROM materials m
              JOIN material_links l ON m.id=l.material_id WHERE m.id=? AND l.brand_id=? AND l.section=?''',
                             (mid, bid, number)).fetchall()
            if not any(r['local_path'].lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
                       and (not topic or r['topic'] == topic)
                       and (number != 2 or r['product_id'] == pid) for r in rows):
                raise ValueError('配图须属于当前品牌、板块、问题和产品')
            sid = item.get('source_id')
            if sid and not c.execute('SELECT 1 FROM material_links WHERE material_id=? AND brand_id=?', (int(sid), bid)).fetchone():
                raise ValueError('配图原始来源须属于当前品牌')
            caption = str(item.get('caption', '')).strip()
            if len(caption) > 1000:
                raise ValueError('图片说明过长')
            result.append({'material_id': mid, 'source_id': int(sid) if sid else None, 'caption': caption})
        return result

    if section == 0:
        expected = data.get('expected_revisions')
        if expected and any(expected.get(str(s['number'])) != s['current_revision'] for s in doc['sections']):
            raise ValueError('资料刚刚发生变化，请刷新后复核整体小结')
        doc.update(title=text('title', 160), summary=text('summary'), scope=text('scope', 1000),
                   summary_record_ids=references(data.get('summary_record_ids', [])))
        if not doc['title']:
            raise ValueError('请填写报告标题')
        if doc['summary'] and not doc['summary_record_ids']:
            raise ValueError('整体小结需要关联研究依据')
        if 'profile' in data:
            if not isinstance(data['profile'], list) or len(data['profile']) > 6:
                raise ValueError('品牌速览最多6项')
            profile = []
            for card in data['profile']:
                clean = {k: str(card.get(k, '')).strip() for k in ('label', 'value', 'detail')}
                if any(len(v) > 1000 for v in clean.values()):
                    raise ValueError('品牌速览内容过长')
                clean['record_ids'] = references(card.get('record_ids', []))
                if (clean['value'] or clean['detail']) and not clean['record_ids']:
                    raise ValueError('品牌速览需要关联依据')
                profile.append(clean)
            doc['profile'] = profile
        if 'cover_figure' in data:
            doc['cover_figure'] = figures([data['cover_figure']], 1)[0] if data['cover_figure'] else None
        doc['reviewed_revisions'] = {str(s['number']): s['current_revision'] for s in doc['sections']}
    else:
        s = doc['sections'][section - 1]
        revision = data.get('expected_revision')
        if revision and revision != s['current_revision']:
            raise ValueError('资料刚刚发生变化，请刷新后复核再保存小结')
        s.update(headline=text('headline', 240), summary=text('summary'), boundary=text('boundary', 2000))
        submitted = data.get('topics', [])
        expected = {(t['topic'], t.get('product_id')) for t in s['topics']}
        if len(submitted) != len(expected) or {(t['topic'], t.get('product_id')) for t in submitted} != expected:
            raise ValueError('请保留框架全部问题及产品范围')
        for old, t in [(next(x for x in s['topics'] if (x['topic'], x.get('product_id')) ==
                         (t['topic'], t.get('product_id'))), t) for t in submitted]:
            ids = references(t.get('record_ids', []), section, t['topic'], t.get('product_id'))
            finding = str(t.get('finding', '')).strip()
            if len(finding) > 6000:
                raise ValueError('小结过长')
            if finding and not ids:
                raise ValueError('有内容的小结需要关联事实或缺口依据')
            old.update(finding=finding, record_ids=ids)
            features = t.get('featured', [f for f in old.get('featured', []) if f['record_id'] in ids])
            for f in features:
                if f.get('record_id') not in ids or f.get('mode') not in ('table', 'lead'):
                    raise ValueError('展示论据须从已关联的研究条目中选择')
                source = c.execute('SELECT status FROM records WHERE id=?', (f['record_id'],)).fetchone()
                if source['status'] not in ('已核实页面信息', '品牌自述'):
                    raise ValueError('待核实或分析条目不能作为事实论据展示')
            old['featured'] = features
            coverage = t.get('coverage', old.get('coverage', '尚未研究'))
            kind = t.get('answer_type', old.get('answer_type', '研究问题'))
            bullets = t.get('bullets', old.get('bullets', []))
            if coverage not in COVERAGE or kind not in ANSWER_TYPES:
                raise ValueError('请选择有效的问题状态与内容类型')
            if not isinstance(bullets, list) or len(bullets) > 6 or any(not isinstance(x, str) or len(x) > 2000 for x in bullets):
                raise ValueError('关键事实最多6条，请保持简练')
            if (bullets or coverage == '已回答') and (not finding or not ids):
                raise ValueError('关键事实或已回答问题需要小结及关联依据')
            gap, impact = str(t.get('gap', old.get('gap', ''))).strip(), str(t.get('impact', old.get('impact', ''))).strip()
            if len(gap) > 2000 or len(impact) > 2000:
                raise ValueError('缺口说明过长')
            old.update(coverage=coverage, answer_type=kind, bullets=bullets, gap=gap, impact=impact)
            if 'figures' in t:
                old['figures'] = figures(t['figures'], section, t['topic'], t.get('product_id'))
        images = data.get('images', s.get('images', []))
        for mid in images:
            m = c.execute('''SELECT m.local_path FROM materials m JOIN material_links l ON m.id=l.material_id
              WHERE m.id=? AND l.brand_id=? AND l.section=?''', (int(mid), bid, section)).fetchone()
            if not m or not m['local_path'].lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                raise ValueError('截图须属于当前品牌和板块')
        s['images'] = list(dict.fromkeys(int(x) for x in images))
        if s['summary'] and not any(t['record_ids'] for t in s['topics']):
            raise ValueError('板块小结需要关联研究依据')
        s['reviewed_revision'] = s['current_revision']
        s['updated_at'] = timestamp
    doc['updated_at'] = timestamp
    c.execute('INSERT INTO brand_reports VALUES (?,?,?) ON CONFLICT(brand_id) DO UPDATE SET document=excluded.document,updated_at=excluded.updated_at',
              (bid, json.dumps(doc, ensure_ascii=False), timestamp))
    return {'message': '报告已保存；引用资料和原始评论保持独立', 'brand_id': bid}
