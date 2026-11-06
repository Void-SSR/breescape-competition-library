from pathlib import Path
import json,sqlite3
R=Path(__file__).resolve().parent;B=R.parents[1]
negative={'soft':'触感偏硬、粗糙或不够舒服','cool':'不够凉、仍闷热或出汗','temperature':'不够凉、偏热或透气不满意','quality':'开线、勾丝起球或耐用性不满','weight':'厚薄、轻重或包裹感不合适','value':'价格偏高或觉得不值','fit':'尺寸、覆盖或床垫适配不合适','color':'颜色、外观或配套不满意','care':'洗护麻烦或洗后状态不满意','service':'送货、售后或退换问题','contents':'套装件数或内容不符预期','general':'总体不喜欢或不愿推荐','loft':'太薄、不够蓬松或缓冲不足','delivery':'配送、错发漏发等履约不满','fixed':'滑动、固定不住','ache':'支撑不足或身体不适未改善','sleep':'睡眠体验未改善','odor':'异味不满意'}
positive={'general':'总体喜欢或推荐','quality':'做工或耐用性满意','fit':'尺寸、覆盖或床垫适配满意','color':'颜色或外观满意','service':'送货或服务满意','value':'价格合适或物有所值','loft':'蓬松、厚度与缓冲满意','temperature':'凉爽或透气体验满意','delivery':'配送与履约满意','care':'洗护或拆包恢复满意','ache':'身体不适减轻或支撑感改善','odor':'气味满意'}
def change(f,pid):
 for r in f.get('rows',[]):
  if pid=='sheex-sheets' and r['code']!='general':continue
  r['label']=(positive if r['valence']=='positive' else negative).get(r['code'],r['label'])
for pid,fn in [('topper','topper_statistics.json'),('cozy-comforter','cozy_statistics.json'),('sheex-sheets','sheex_statistics.json')]:
 p=R/fn;d=json.loads(p.read_text());change(d,pid);p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
 for dest in (B/'data/attachments').glob('**/'+fn):dest.write_text(p.read_text())
c=sqlite3.connect(B/'data/library.sqlite3')
for bid,raw in c.execute('select brand_id,document from brand_reports').fetchall():
 d=json.loads(raw)
 for s in d['sections']:
  for t in s['topics']:
   if t.get('feedback') and t.get('product_id')!='sheets':change(t['feedback'],t.get('product_id'))
 c.execute('update brand_reports set document=? where brand_id=?',(json.dumps(d,ensure_ascii=False),bid))
 (R/(bid+'_published.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2))
c.commit()
print('分开呈现认可与不认可的具体含义；计数保持不变。')
