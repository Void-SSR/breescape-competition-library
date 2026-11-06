"""Publish only the approved section-three transcript evidence and status correction."""
from pathlib import Path
import hashlib
import json
import shutil
import sqlite3
import sys
import zipfile
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import reports

WORK = Path(__file__).parent
SOURCE = ROOT / 'research/TOP5视频文字转写_VAI_20261105'
TARGET = ROOT / 'data/attachments/TOP5音轨转写_20261105'
BEFORE = json.loads((WORK / 'before.json').read_text())
STAMP = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')

assert not TARGET.exists(), '附件目录已存在，请先核对而非重复写入'
TARGET.mkdir()
for name in ['转写核验说明.md', '逐视频转写与分歧.txt']:
    shutil.copy2(SOURCE / name, TARGET / name)
with zipfile.ZipFile(TARGET / '原始转写与核验文件.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(SOURCE.iterdir()):
        if p.is_file():
            z.write(p, p.name)

c = sqlite3.connect(ROOT / 'data/library.sqlite3')
c.row_factory = sqlite3.Row
with c:
    c.execute('BEGIN IMMEDIATE')
    # Protect edits made since the write-before snapshot.
    for table, old in BEFORE.items():
        current = [dict(r) for r in c.execute('SELECT * FROM ' + table + ' ORDER BY rowid')]
        assert current == old, '数据库已变化，请重新核对：' + table
    old_revision = reports.section_revision(c, 'shilucheng', 3)
    mids = []
    for title, filename, summary in [
        ('TOP5音轨自动转写｜核验说明与使用边界', '转写核验说明.md', '五条既有视频的本地自动转写已完成；未人工听辨，未得到可靠的新产品口播主张。'),
        ('TOP5音轨自动转写｜逐视频文字与分歧', '逐视频转写与分歧.txt', '保留V01/V04分歧、V02秋季语境及V03/V05疑似歌词；时间仅属于对应识别结果。'),
        ('TOP5音轨自动转写｜原始JSON、SRT与校验包', '原始转写与核验文件.zip', '包含全部28个原始结果及说明文件；保留空输出、分歧和原视频哈希，不覆盖原件。'),
    ]:
        mid = c.execute('''INSERT INTO materials(title,url,source_type,publisher,retrieved_at,summary,local_path,access_note)
            VALUES (?,NULL,?,?,?,?,?,?)''', (title, '本地自动转写证据', 'VAI 本地识别', STAMP, summary,
            'attachments/TOP5音轨转写_20261105/' + filename,
            '自动识别结果不等于人工回听或商品事实。空输出不等于无声音；具体方法与分歧见核验说明。')).lastrowid
        mids.append(mid)
        for topic in ['8. TOP5爆款内容分析', '9. 渠道内容总结']:
            c.execute('''INSERT INTO material_links(material_id,brand_id,product_id,section,topic)
                VALUES (?,'shilucheng','sheets',3,?)''', (mid, topic))

    replacements = {
        18: ('音乐与口播尚未听辨／转录；',
             '五条音轨已完成本地自动转写；目前没有新增可靠的产品口播主张，V02仅补充印证已有秋季语境。未人工听辨，V01/V04的识别分歧和音乐、语气等听感未知仍保留；'),
        55: ('未转录音乐或口播，不宣称完成音轨研究。',
             '另已完成五条音轨的本地自动转写，尚未人工听辨；转写及分歧见音轨补充记录。以下产品宣称仍以可见画面与字幕为依据，不改写为已在声音中验证。'),
    }
    for rid, (old, new) in replacements.items():
        row = c.execute('SELECT * FROM records WHERE id=?', (rid,)).fetchone()
        assert row['body'].count(old) == 1
        body = row['body'].replace(old, new)
        evidence = list(dict.fromkeys(json.loads(row['evidence']) + mids))
        c.execute('UPDATE records SET body=?,evidence=?,updated_at=? WHERE id=?',
                  (body, json.dumps(evidence), STAMP, rid))

    body = '''本轮仅补充既有V01—V05的自动转写文字与证据状态，不重新筛选视频。五条音轨合计74.434秒；没有获得可靠的新产品口播主张，现有两类内容结构和畅销机制判断不因此升级。

| 视频 | 自动转写得到的线索 | 当前可支持的内容与限制 |
| --- | --- | --- |
| V01 | 两次全音轨识别不一致，分段识别无正文 | 尚无可稳定引用的完整句；不能断言没有人声 |
| V02 | 两模型均识别“I am an autumn.” | 结合原有棕色床品与秋季字幕，仅补充印证原有秋季语境；不是材质、凉感或优惠证据 |
| V03 | 两模型全音轨文字高度相近，呈疑似歌词，末尾截断 | 未得到新的可靠产品主张；不据此确认音乐策略或转化作用 |
| V04 | 一模型识别到与V03/V05重合的疑似歌词，另一模型无正文 | 单模型及尾句不确定，不作为可靠口播引用；空输出不等于无声音 |
| V05 | 两模型全音轨文字高度相近，呈疑似歌词 | 未得到新的可靠产品主张；不能从文字判断节奏、语气、音效或销量作用 |

时间与方法：V02的Whisper分段为0.000—2.760秒；Qwen分段分别为0.360—1.160秒和2.240—2.880秒，不混合为同一时间轴。Qwen全音轨结果没有逐句时间，不能借用另一次分段的时间点。五条完整原始JSON/SRT、空输出和分歧均在附件中保留；原视频入口按V01—V05对应。

本地自动转写不等于人工回听，两模型一致也不等于商品宣称已经验证。语气、音乐节奏、音效及混音未核验；这些未知目前不影响已有画面研究继续使用，不作为整个研究推进的门槛。只有后续判断确实依赖某句原话或听感时，再针对性补证。'''
    rid = c.execute('''INSERT INTO records(brand_id,product_id,section,topic,title,body,kind,status,evidence,updated_at)
        VALUES ('shilucheng','sheets',3,'8. TOP5爆款内容分析',?,?,'分析','研究草稿',?,?)''',
        ('TOP5音轨文字补充：自动转写与证据边界', body, json.dumps(mids + [56, 57, 58, 59, 60]), STAMP)).lastrowid

    doc = json.loads(c.execute("SELECT document FROM brand_reports WHERE brand_id='shilucheng'").fetchone()[0])
    section = doc['sections'][2]
    section['boundary'] = '研究范围为用户于2026-11-04 23:07（北京时间）确认的商品页前五条。已完成画面与字幕的逐秒抽帧核对，并补充音轨自动转写；未人工听辨，部分识别仍有分歧。现有产品宣称判断来自画面与字幕；作品级播放和成交尚无可核数据。'
    topic = next(t for t in section['topics'] if t['topic'] == '8. TOP5爆款内容分析')
    topic['record_ids'] = topic['record_ids'] + [rid]
    assert topic['bullets'][2] == '本轮核对了五条完整时长的逐秒画面与字幕；音轨未转录，点赞不能替代播放或成交。'
    topic['bullets'][2] = '画面与字幕是上述产品宣称的依据；补充自动转写未提供可靠的新产品口播。点赞不能替代播放或成交。'
    topic['gap'] = '音轨自动转写已完成，V01/V04仍有识别分歧，尚未人工听辨；这些未知不阻塞已有画面研究。独立作品链接、发布时间和作品级转化数据尚未取得，不以点赞推断销售。'
    new_revision = reports.section_revision(c, 'shilucheng', 3)
    if section.get('reviewed_revision') == old_revision:
        section['reviewed_revision'] = new_revision
    if section.get('current_revision') == old_revision:
        section['current_revision'] = new_revision
    if doc.get('reviewed_revisions', {}).get('3') == old_revision:
        doc['reviewed_revisions']['3'] = new_revision
    section['updated_at'] = STAMP
    doc['updated_at'] = STAMP
    c.execute("UPDATE brand_reports SET document=?,updated_at=? WHERE brand_id='shilucheng'",
              (json.dumps(doc, ensure_ascii=False), STAMP))
    c.execute('INSERT INTO events(action,detail,created_at) VALUES (?,?,?)',
              ('TOP5转写状态同步', f'第三板块记录18、55更新转写状态，新增记录{rid}和材料{mids}；核心解释与其他板块不变。', STAMP))

result = {'updated_at': STAMP, 'updated_records': [18, 55], 'new_record': rid, 'new_materials': mids,
          'updated_report_section': 3, 'copied_evidence_directory': str(TARGET), 'core_findings_changed': False}
(WORK / 'publication.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps(result, ensure_ascii=False))
