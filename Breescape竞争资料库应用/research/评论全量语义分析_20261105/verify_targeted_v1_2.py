# coding: utf-8
"""Independent arithmetic/provenance check over exported CSV; no text classifier.
This verifies reproducibility and audit scope, not semantic accuracy.
"""
from pathlib import Path
import collections
import copy
import csv
import difflib
import hashlib
import json

P = Path(__file__).resolve().parent
B = P / 'revisions/v1.1_submitted_before_targeted_20261105'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(name, data):
    (P / name).write_text(json.dumps(data, ensure_ascii=False, indent=2))


def csvrows(name):
    with (P / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def jsonlines(path):
    return {r['review_id']: r for r in map(json.loads, path.read_text().splitlines())}


source = {r['id']: r for r in read(P / '00_source_snapshot.json')}
base = jsonlines(B / '02_annotations.jsonl')
final = jsonlines(P / '02_annotations.jsonl')
reviews = csvrows('04_逐条评论与编码.csv')
evidence = csvrows('04_全部证据标注.csv')
assert set(base) == set(final) == set(source) == {int(r['review_id']) for r in reviews}
assert len(reviews) == 1628 and len(evidence) == 5150
denominators = collections.Counter(r['source_group'] for r in reviews if r['denominator_included'] == 'True')
assert denominators == {'main_recent': 928, 'extra_one_star': 687, 'recommended': 13}
for r in reviews:
    original = source[int(r['review_id'])]
    for csvkey, sourcekey in [('body', 'body'), ('external_review_id', 'external_id'), ('date', 'date'), ('sku', 'sku'), ('source_group', 'source_group'), ('source_files', 'source_files')]:
        assert r[csvkey] == str(original[sourcekey])
    assert r['product_url'].endswith('/1729438233542234865')
for e in evidence:
    original = source[int(e['review_id'])]
    assert original['body'][int(e['quote_start']):int(e['quote_end'])] == e['quote']
    assert e['source_group'] == original['source_group']
    assert e['external_review_id'] == original['external_id']
    assert e['product_url'].endswith('/1729438233542234865')

# Build sets independently from the flattened export, never invoke reproduce.py.
theme_sets = collections.defaultdict(set)
for e in evidence:
    if e['dimension'] == 'theme' and e['subject'] == 'target_same_product' and e['valence'] in ('positive', 'negative') and e['code'].startswith(('T', 'G')):
        theme_sets[e['source_group'], e['code'], e['valence']].add(int(e['review_id']))
stats = read(P / '05_statistics.json')
reported = {}
for group, s in stats.items():
    assert s['denominator'] == denominators[group]
    for val in ['positive', 'negative']:
        for item in s[val] + s['general'].get(val, []):
            key = group, item['code'], val
            reported[key] = set(item['review_ids'])
            assert item['count'] == len(reported[key])
            assert item['percent'] == round(100 * item['count'] / denominators[group], 2)
assert dict(theme_sets) == reported
csvstats = csvrows('05_分来源主题统计.csv')
assert len(csvstats) == len(reported)
for r in csvstats:
    ids = {int(i) for i in r['review_ids'].split(';')}
    assert ids == reported[r['source_group'], r['code'], r['valence']]
    assert int(r['count']) == len(ids) and int(r['denominator']) == denominators[r['source_group']]

behavior = read(P / '05_behavior_counts.json')
behavior_keys = 0
for group, groups in behavior.items():
    for category, item in groups.items():
        found = {int(e['review_id']) for e in evidence if e['source_group'] == group and e['dimension'] == 'behavior' and e['code'] in item['codes']}
        assert found == set(item['review_ids']) and len(found) == item['count']
        behavior_keys += 1

# Check every per-record audit entry is a continuous before/after chain.
changes = read(P / '09_v1.2_change_log.json')
replayed = copy.deepcopy(base)
for change in changes:
    i = change['review_id']
    assert replayed[i] == change['before'], ('broken before', i)
    replayed[i] = change['after']
for r in replayed.values():
    r['rule_version'] = '1.2'
assert replayed == final
changed_ids = []
for i in base:
    old = {k: v for k, v in base[i].items() if k != 'rule_version'}
    new = {k: v for k, v in final[i].items() if k != 'rule_version'}
    if old != new:
        changed_ids.append(i)
    for key in ['source_group', 'denominator_included', 'disposition']:
        assert old[key] == new[key]
assert set(changed_ids) == {c['review_id'] for c in changes}
assert len(changes) == 47 and len(changed_ids) == 45
scope = read(P / '09_v1.2_scope.json')
allowed = set().union(*(scope[k] for k in ['purchase_candidates', 'T07_negative_candidates', 'component_candidates', 'elastic_candidates']))
assert set(changed_ids) <= allowed
decisions = read(P / '09_v1.2_review_decisions.json')
assert {r['review_id'] for r in decisions['purchase_history']} == set(scope['purchase_candidates'])
assert {r['review_id'] for r in decisions['T07_negative']} == set(scope['T07_negative_candidates'])
assert {r['review_id'] for r in decisions['elastic']} == set(scope['elastic_candidates'])
assert {int(i) for i in decisions['component_updates']} == set(scope['component_candidates'])
assert len(decisions['purchase_history']) == 73 and len(decisions['T07_negative']) == 110

snapshot_manifest = read(B / 'SNAPSHOT_MANIFEST.json')
assert all(sha(B / f) == digest for f, digest in snapshot_manifest.items())
historic = [f for f in snapshot_manifest if f.startswith(('00_', '02_first_pass', '03_', 'batches/')) or f in ['01_rules_v1.0.md', '01_theme_rules_v1.0.json', '01_theme_rules_v1.1.json']]
assert all(sha(P / f) == snapshot_manifest[f] for f in historic)
protection = read(P / '00_protection_manifest.json')
assert len(protection) == 46
assert all(sha(P.parent.parent / f) == digest for f, digest in protection.items())

# Include all changed theme numerators, even if the count remains constant.
oldstats = read(B / '05_statistics.json')
oldsets = {}
for group, s in oldstats.items():
    for val in ['positive', 'negative']:
        for item in s[val] + s['general'].get(val, []):
            oldsets[group, item['code'], val] = set(item['review_ids'])
theme_delta = []
for key in sorted(set(oldsets) | set(reported)):
    before, after = oldsets.get(key, set()), reported.get(key, set())
    if before != after:
        theme_delta.append(dict(source_group=key[0], code=key[1], valence=key[2], before=len(before), after=len(after), removed_ids=sorted(before-after), added_ids=sorted(after-before)))
oldbehavior = read(B / '05_behavior_counts.json')
behavior_delta = []
for group in behavior:
    for category in behavior[group]:
        before = set(oldbehavior[group].get(category, {}).get('review_ids', []))
        after = set(behavior[group][category]['review_ids'])
        if before != after:
            behavior_delta.append(dict(source_group=group, category=category, before=len(before), after=len(after), removed_ids=sorted(before-after), added_ids=sorted(after-before)))
dump('09_v1.2_统计变化.json', dict(theme_changes=theme_delta, behavior_changes=behavior_delta, denominators=dict(denominators)))

diffs = []
for name in ['README.md', '07_关键证据与反例.md', '08_研究结论与机制修订建议.md', 'CURRENT_TASK.md', 'progress.json']:
    diffs.extend(difflib.unified_diff((B/name).read_text().splitlines(keepends=True), (P/name).read_text().splitlines(keepends=True), fromfile='v1.1/'+name, tofile='v1.2/'+name))
(P/'09_v1.2_文字修订.diff').write_text(''.join(diffs))
result = dict(
    rule_version='1.2',
    method='从导出的CSV另建review_id集合，与全部三来源JSON及主题CSV逐项比对；不调用原统计函数。复核逐条变更链、范围与文件哈希。',
    all_source_specific_theme_counts_match=True,
    theme_group_direction_cells_checked=len(reported),
    behavior_group_cells_checked=behavior_keys,
    all_behavior_counts_match=True,
    all_quotes_exact=True,
    annotation_rows=len(evidence),
    reviews=len(reviews),
    denominators_unchanged=dict(denominators),
    logged_edits=len(changes),
    annotation_change_review_ids=sorted(changed_ids),
    distinct_annotation_change_reviews=len(changed_ids),
    outside_scope_changes=[],
    per_record_audit_chain_matches_final=True,
    snapshot_files_unchanged=len(snapshot_manifest),
    historical_files_unchanged=len(historic),
    app_protected_files_unchanged=len(protection),
    source_sha256=sha(P/'00_source_snapshot.json'),
    annotations_sha256=sha(P/'02_annotations.jsonl'),
    semantic_accuracy_claim=False,
    blind_reread='沿用v1.1已完成163条；本轮未重跑，不称独立编码者验证',
)
dump('06_独立复算核验.json', result)
print(json.dumps(result, ensure_ascii=False, indent=2))
