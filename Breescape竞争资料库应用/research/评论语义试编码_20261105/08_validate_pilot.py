"""Read-only validation of pilot artifacts; does not assign labels or publish rankings."""
from pathlib import Path
import sqlite3,json,hashlib,collections,csv
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
sample=json.loads((P/'00_sample_selection.json').read_text());S={x['id']:x for x in sample}
a=json.loads((P/'01_first_pass_v0.1.json').read_text())['reviews'];b=json.loads((P/'02_calibrated_v0.2.json').read_text())['reviews']
assert len(S)==len(sample)==len(a)==len(b)==60
assert {x['review_id'] for x in a}=={x['review_id'] for x in b}==set(S)
first_hash=(P/'01_first_pass.sha256').read_text().split()[0]
assert hashlib.sha256((P/'01_first_pass_v0.1.json').read_bytes()).hexdigest()==first_hash
c=sqlite3.connect('file:'+str(ROOT/'data/library.sqlite3')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
for i,s in S.items():
 row=dict(c.execute('select * from reviews where id=?',(i,)).fetchone());assert row['product_id']=='sheets'
 for key in ['body','rating','date','sku','external_id']:assert row[key]==s[key],(i,key)
 raw=json.loads(row['raw_json']);assert raw['采样范围']==s['scope'];assert raw['来源文件']==s['source_files']
for version in [a,b]:
 for r in version:
  body=S[r['review_id']]['body']
  for dim in ['themes','motives','behaviors','contexts','noncoded']:
   for x in r.get(dim,[]):assert x['quote'] in body,(r['review_id'],dim,x)
R={r['code']:r for r in json.loads((P/'03_candidate_codebook_v0.2.json').read_text())}
for r in R.values():assert r['example_quote'] in S[r['example_review_id']]['body']
for r in b:
 assert r['disposition']=='retain' and r['denominator_included'] is True
 for t in r['themes']:
  assert t['code'] in R
  assert S[r['review_id']]['body'][t['quote_start']:t['quote_end']]==t['quote']
  assert t['count_unit_key']=='|'.join([str(r['review_id']),t['code'],t['valence']])
  if t['primary_count_eligible']:assert t['role']=='specific_theme' and t['valence'] in ('positive','negative') and t['subject']!='explicit_prior_target_set_or_variant'
  else:assert t['count_exclusion_reason']
# These paired comments have different platform review IDs, not proof of different people.
assert S[640]['external_id'] and S[641]['external_id'] and S[640]['external_id']!=S[641]['external_id']
base=json.loads((P/'00_protection_baseline.json').read_text())
assert all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in base.items())
with (P/'06_semantic_judgments.csv').open(encoding='utf-8-sig') as f:flat=list(csv.DictReader(f))
assert len(flat)==sum(sum(len(r.get(dim,[])) for dim in ['themes','motives','behaviors','contexts','noncoded']) for r in b)
for x in flat:assert S[int(x['review_id'])]['body'][int(x['quote_start']):int(x['quote_end'])]==x['quote']
result={'scope':'60条试编码，未执行全量，未发布TOP3或主题比例','sample_reviews':60,'initial_and_calibrated_ids_match':True,'initial_version_hash_unchanged':True,'raw_text_ids_dates_ratings_and_source_match_database':True,'evidence_quotes_and_offsets_match':True,'rules_examples_match_originals':True,'all_comments_retained_in_source_denominators':True,'source_counts':dict(collections.Counter(x['source_group'] for x in sample)),'source_rating_counts':{group:dict(sorted(collections.Counter(x['rating'] for x in sample if x['source_group']==group).items())) for group in ['main_recent','extra_one_star','recommended']},'main_overlap_reviews':sum(x['overlap']=='yes' for x in sample),'missing_platform_ids_retained':sum(not x['external_id'] for x in sample),'selection_method_counts':dict(collections.Counter(x['selection_type'] for x in sample)),'distinct_review_identity_checked_for_640_641':True,'specific_count_unit':'review_id + theme_code + valence; distinct keys only','judgment_rows_with_exact_quotes':len(flat),'protected_files_unchanged':len(base),'database_hash_unchanged':True,'verification_limit':'自动检查不证明语义判断正确；语义由同一分析者逐条二读，仍待监督者独立审查。'}
print(json.dumps(result,ensure_ascii=False,indent=2))
