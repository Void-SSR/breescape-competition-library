'use strict';
let reportBrand='shilucheng', reportPresent=false;
const readingGlossary={
 twin:{title:'单人床（Twin）',body:'Twin 是美国商品页使用的单人床尺寸名称。三件套中的“件”是套内物品数量，和床的大小分开计算。购买前仍需核对商品尺寸表。'},
 queen:{title:'双人床（Queen）',body:'Queen 是美国商品页使用的一种双人床尺寸名称，不宜直接等同于国内的床号。这里的四件套、六件套表示套内物品数量；具体组合以对应商品为准。'},
 fitted:{title:'床笠',body:'用松紧边包住床垫的床单。页面所说的“深口袋”，是床笠侧边的包覆深度，用来说明能适配多厚的床垫。它不是收纳口袋。'},
 rayon:{title:'竹源人造丝',body:'以竹来源的纤维素加工制成的再生纤维。英文商品页常写 rayon from bamboo，不能把它理解为未经加工的天然竹纤维。混纺比例需看具体商品标注。'},
 polyester:{title:'聚酯（涤纶）',body:'一种常见的合成纤维。材料比例是产品事实；是否更柔软、更凉或更耐用，还要结合织造、加工和实际使用证据判断。'},
 twill:{title:'斜纹',body:'一种织造方式。名称本身不能证明更凉、更柔软或更耐用。若商品描述与参数栏的织法不一致，应先向商家核实。'},
 sateen:{title:'缎纹',body:'一种织造方式，不代表特定纤维成分，也不等同于真丝。仍需分别查看材料成分和实际使用表现。'},
 listprice:{title:'页面划线价',body:'商家在页面上展示的价格比较基准。没有交易历史等证据时，不能把它当作真实的日常成交价，也不能仅凭折扣幅度认定便宜。'}
};
function termInline(value,pid){
 const keys={'（Twin）':'twin','（Queen）':'queen','床笠':'fitted','竹源人造丝':'rayon','聚酯':'polyester','斜纹':'twill','缎纹':'sateen','划线价':'listprice'};
 return String(value??'').split(/(（Twin）|（Queen）|床笠|竹源人造丝|聚酯|斜纹|缎纹|划线价)/g).map(x=>keys[x]?`<button type="button" class="term-help" data-term="${keys[x]}" aria-haspopup="dialog" aria-label="解释：${esc(readingGlossary[keys[x]].title)}">${esc(x)}</button>`:reviewInline(x,pid)).join('');
}
// This function is also embedded in the offline report; keep it independent of app state.
function installReadingTools(){
 let modal=null,objectUrl=null,ticket=0;
 function clean(){ticket++;const v=modal?.querySelector('video');if(v){v.pause();v.removeAttribute('src');v.load();}if(objectUrl){URL.revokeObjectURL(objectUrl);objectUrl=null;}}
 function open(title){
  if(!modal){modal=document.createElement('dialog');modal.className='reading-dialog';modal.setAttribute('aria-labelledby','reading-dialog-title');document.body.append(modal);modal.addEventListener('close',clean);modal.addEventListener('click',e=>{if(e.target===modal){const b=modal.getBoundingClientRect();if(e.clientX<b.left||e.clientX>b.right||e.clientY<b.top||e.clientY>b.bottom)modal.close();}});}
  clean();modal.replaceChildren();const header=document.createElement('div');header.className='reading-dialog-header';const h=document.createElement('h2');h.id='reading-dialog-title';h.textContent=title;const close=document.createElement('button');close.type='button';close.textContent='关闭';close.onclick=()=>modal.close();header.append(h,close);modal.append(header);modal.showModal();return modal;
 }
 document.addEventListener('click',async e=>{
  const term=e.target.closest('[data-term]');if(term){const item=readingGlossary[term.dataset.term];if(!item)return;e.preventDefault();const box=open(item.title),p=document.createElement('p');p.textContent=item.body;box.append(p);return;}
  const a=e.target.closest('a[data-library-video][href]');if(!a)return;
  const url=new URL(a.getAttribute('href'),location.href);
  if(!((url.origin===location.origin&&/^\/attachment\/[1-9][0-9]*$/.test(url.pathname))||(/\.mp4$/i.test(url.pathname)&&['file:','http:','https:'].includes(url.protocol))))return;
  e.preventDefault();const box=open(a.textContent.trim()),v=document.createElement('video');v.controls=true;v.playsInline=true;v.preload='metadata';box.append(v);
  const status=document.createElement('p');status.className='reading-video-note';status.textContent='已保存视频；原作品链接暂未取得。';box.append(status);
  const link=document.createElement('a');link.href=a.href;link.textContent='打开视频文件';link.target='_blank';link.rel='noopener';box.append(link);
  if(a.dataset.videoSource){const source=new URL(a.dataset.videoSource);if(['https:','http:'].includes(source.protocol)){const origin=document.createElement('a');origin.href=source.href;origin.textContent='来源商品页 ↗';origin.target='_blank';origin.rel='noopener';box.append(origin);}}
  const current=ticket;
  try{
   if(/^\/attachment\/[1-9][0-9]*$/.test(url.pathname)){
    const response=await fetch(url);if(!response.ok)throw Error('video unavailable');const bytes=await response.arrayBuffer();if(current!==ticket||!box.open)return;objectUrl=URL.createObjectURL(new Blob([bytes],{type:'video/mp4'}));v.src=objectUrl;
   }else{v.src=url.href;}
   v.addEventListener('error',()=>{status.textContent='视频暂时无法播放，可使用下方“打开视频文件”。原作品链接暂未取得。';},{once:true});
  }catch(error){if(current===ticket)status.textContent='视频读取失败，请稍后重试，或打开视频文件。';}
 });
}
installReadingTools();
const factualRecord=r=>r.kind!=='分析'&&['已核实页面信息','品牌自述'].includes(r.status);
const reportStatuses=['已回答','部分回答','尚未研究','资料待补','待你确认','等待前置研究'];
function reviewGroupLabel(group){return {main_recent:'近期全星级主样本',extra_one_star:'额外一星补充',recommended:'推荐展示样本'}[group]||group;}
function reviewInline(text,pid){
 const value=String(text??'');if(pid!=='sheets'||!db?.review_analysis)return esc(value);
 return value.split(/(\bR[0-9]{1,4}\b)/g).map(part=>/^R[0-9]{1,4}$/.test(part)?`<a class="review-citation" href="#reviews/sheets/2/review-${+part.slice(1)}">${esc(part)}</a>`:esc(part)).join('');
}
function reviewOriginal(r){
 return `<div class="review-source-meta"><span>${esc(reviewGroupLabel(r.source_group))}</span><span>${esc(r.date)} · ${r.rating}星</span><span>${esc(r.sku)}</span></div><p class="review-original">${esc(r.body)}</p><details class="review-origin"><summary>原评论身份与采集来源</summary><p>商品ID：${esc(r.external_product_id)}<br>平台评论ID：${esc(r.external_id||'原始来源未提供，不补造')}<br>采集：${esc(r.collected_at)}<br>来源文件：${esc(r.source_files)}<br>采样口径：${esc(r.sample_scope)}</p><a href="${esc(safeURL(r.product_url))}" target="_blank" rel="noopener">商品原页（非单条评论永久链接） ↗</a></details>`;
}
function reviewAppendix(){
 const m=db.review_analysis;if(!m||m.brand_id!==reportBrand)return '';
 return `<details class="report-review-appendix"><summary>关键原评论与反例 · v1.2</summary><p class="muted">以下是研究引用的个案原文；平台评论ID、日期和来源组随原文保留。完整分子与全部编码见v1.2附件。</p>${m.reviews.map(r=>`<details class="review-proof" id="review-proof-${r.id}"><summary>R${r.id} · ${esc(r.date)} · ${esc(reviewGroupLabel(r.source_group))}</summary>${reviewOriginal(r)}</details>`).join('')}</details>`;
}
function brandReport(){return db.reports.find(r=>r.brand_id===reportBrand);}
function reportProducts(){return db.products.filter(p=>p.brand_id===reportBrand);}
function reportRecords(n){return db.records.filter(r=>r.brand_id===reportBrand&&(!n||r.section===n));}
function representativeProduct(bid=reportBrand){return db.products.find(p=>p.brand_id===bid)?.id||product;}
function reportRoute(bid=reportBrand,present=reportPresent){return '#overview/'+bid+(present?'/present':'');}
function recordRoute(r){return '#research/'+(r.product_id||representativeProduct(r.brand_id))+'/'+r.section+'/record-'+r.id;}
function openReport(bid=reportBrand,present=false){location.hash=reportRoute(bid,present);}
function topicStatus(t){return t.coverage||(t.finding?'部分回答':'尚未研究');}
function topicAnchor(t,n){return 'report-question-'+n+'-'+brandReport().sections[n-1].topics.indexOf(t);}
function reportProgress(n){
 const topics=brandReport().sections[n-1].topics,done=topics.filter(t=>topicStatus(t)==='已回答').length,partial=topics.filter(t=>topicStatus(t)==='部分回答').length;
 return {done,partial,total:topics.length,label:`${done}/${topics.length} 已回答 · ${partial} 部分回答`};
}
function reportSources(ids){
 const mids=[...new Set(ids.flatMap(id=>JSON.parse(db.records.find(r=>r.id===id)?.evidence||'[]')))];
 return mids.map(id=>db.materials.find(m=>m.id===id)).filter(Boolean);
}
function reportSourceLink(m){
 const accessible=m.url||m.local_path;
 return `<span class="report-source-item">${accessible?`<a href="${esc(materialHref(m))}" target="_blank" rel="noopener">${esc(m.title)} ↗</a>`:`<span>${esc(m.title)}（库内原始材料）</span>`}<small>${esc(m.source_type||'来源')} · ${esc((m.retrieved_at||'日期待补').slice(0,10))}</small></span>`;
}
function reportCitations(ids){
 const sources=reportSources(ids),first=sources.slice(0,2),more=sources.slice(2);
 return `<div class="report-citations"><span class="source-label">依据</span>${first.map(reportSourceLink).join('')}${more.length?`<details class="report-more-sources"><summary>另 ${more.length} 项来源</summary><div>${more.map(reportSourceLink).join('')}</div></details>`:''}${sources.length?'':'<span>尚无外部材料；查看研究条目中的缺口说明。</span>'}</div>`;
}
function reportFigure(f,cover=false){
 if(!f)return '';const m=db.materials.find(m=>m.id===f.material_id),source=db.materials.find(m=>m.id===f.source_id);
 if(!m||!evidenceImage(m))return '';
 return `<figure class="report-figure ${cover?'report-cover-figure':''}"><a class="figure-zoom" href="/attachment/${m.id}" target="_blank" rel="noopener" aria-label="查看原图：${esc(m.title)}"><img src="/attachment/${m.id}" alt="${esc(m.title)}" ${cover?'':'loading="lazy"'}></a><figcaption><b>${esc(f.caption||m.summary||m.title)}</b><details class="figure-source"><summary>图片来源</summary><span>${esc(m.source_type)} · 采集 ${esc((m.retrieved_at||'').slice(0,10))}${source?.url?` · <a href="${esc(safeURL(source.url))}" target="_blank" rel="noopener">原始页面 ↗</a>`:''}</span></details></figcaption></figure>`;
}
function featuredEvidence(f){
 const r=db.records.find(x=>x.id===f.record_id);if(!r)return '';
 const analysis=f.mode==='analysis'&&r.kind==='分析'&&['研究草稿','已复核'].includes(r.status)&&JSON.parse(r.evidence||'[]').length;
 if(!analysis&&!factualRecord(r))return `<p class="report-stale">引用「${esc(r.title)}」需复核。</p>`;
 const blocks=r.body.split(/\n\s*\n/),body=(f.mode==='table'||analysis)?blocks.filter(b=>b.trim().startsWith('|')).join('\n\n'):blocks.find(b=>!b.trim().startsWith('|'));
 return body?`<div class="report-evidence"><div class="evidence-caption">${esc(r.title)}${analysis?' · 研究判断':''}</div>${formatBody(body,r.product_id,{comparison:f.layout==='comparison'})}</div>`:'';
}
function reportTopic(t,n){
 const pending=t.answer_type==='研究问题'||!t.finding;
 const voc=t.product_id==='sheets'&&t.topic==='5. 消费者评论分析'&&db.review_analysis;
 const bullets=items=>items?.length?`<ul class="report-key-facts">${items.map(b=>`<li>${reviewInline(b,t.product_id)}</li>`).join('')}</ul>`:'';
 const facts=t.bullets||[];
 return `<article id="${topicAnchor(t,n)}" class="report-topic ${pending?'unwritten':''} ${voc?'report-voc':''}"><h3>${esc(t.topic)}</h3><p class="topic-finding">${esc(t.finding||'尚未开展该问题研究。')}</p>${bullets(voc?facts.slice(0,1):facts)}${(t.figures||[]).map(f=>reportFigure(f)).join('')}${(t.featured||[]).map(featuredEvidence).join('')}${voc?bullets(facts.slice(1)):''}<a class="report-evidence-ref" href="#audit-${topicAnchor(t,n)}" data-open-evidence="audit-${topicAnchor(t,n)}">查看本项依据</a></article>`;
}

function reportAudit(s){
 return `<details class="report-audit" id="report-audit-${s.number}"><summary>依据与研究状态<span>来源、口径、待补事项</span></summary><div class="report-audit-body">${s.boundary?`<p class="audit-boundary">${esc(s.boundary)}</p>`:''}${s.topics.map(t=>{
 const ids=t.record_ids||[],records=ids.map(id=>db.records.find(r=>r.id===id)).filter(Boolean);
 return `<div class="audit-topic" id="audit-${topicAnchor(t,s.number)}"><h4>${esc(t.topic)}${t.product_id?' · '+esc(db.products.find(p=>p.id===t.product_id)?.name):''}</h4><p class="audit-status">${esc(t.answer_type||'研究问题')} · ${esc(topicStatus(t))}</p>${t.gap?`<p><b>待补：</b>${esc(t.gap)}</p>`:''}${t.impact?`<p>${esc(t.impact)}</p>`:''}${reportCitations(ids)}${records.length?`<details class="report-proof"><summary>研究记录与解读边界（${records.length}）</summary>${records.map(r=>`<div class="proof-row"><h5>${esc(r.title)}</h5><small>${esc(r.status)} · ${esc(r.updated_at.slice(0,10))}</small><div>${formatBody(r.body,r.product_id)}</div><a class="work-only" href="${recordRoute(r)}">打开研究条目</a></div>`).join('')}</details>`:''}</div>`;
 }).join('')}${s.images?.length?`<details class="report-visuals"><summary>补充页面截图（${s.images.length}）</summary><div class="evidence-grid">${s.images.map(id=>db.materials.find(m=>m.id===id)).filter(m=>m&&evidenceImage(m)).map(evidencePreview).join('')}</div></details>`:''}<div class="report-section-footer work-only"><span>小结更新 ${esc(s.updated_at?.slice(0,10)||'—')}</span><button class="report-edit" data-edit-report="${s.number}">编辑本节</button><a href="#research/${representativeProduct()}/${s.number}">打开完整板块</a></div></div></details>`;
}
function reportSection(s){
 let topics='';
 if(s.number===2){topics=reportProducts().map(product=>{
  const rows=s.topics.filter(t=>t.product_id===product.id),written=rows.some(t=>t.finding);
  if(!written)return `<details class="report-other-product work-only"><summary>${esc(product.name)} · 尚未研究</summary><p>独立保留档案与框架，不与床单混样。</p><a href="#research/${product.id}/2">打开产品档案</a></details>`;
  return `<div class="report-product"><div class="report-product-heading"><h3>${esc(product.name)}</h3><a href="${esc(safeURL(product.url))}" target="_blank" rel="noopener">${esc(product.channel)} · ${esc(product.market)} · 商品原页 ↗</a></div>${rows.map(t=>reportTopic(t,2)).join('')}</div>`;
 }).join('');}else topics=s.topics.map(t=>reportTopic(t,s.number)).join('');
 return `<section class="report-section ${s.summary?'':'report-section-empty'}" id="report-section-${s.number}"><div class="report-chapter-heading"><span class="chapter-number" aria-hidden="true">${['一','二','三','四','五','六'][s.number-1]}</span><h2>${esc(db.sections[s.number-1])}</h2></div><p class="report-chapter-thesis">${esc(s.headline||'尚未形成研究小结')}</p><p class="report-section-summary">${esc(s.summary||'本板块保留研究目录，尚未形成结论。')}</p>${s.stale?'<p class="report-stale">本节依据已更新，小结待复核。</p>':''}<div class="report-topics">${topics}</div>${reportAudit(s)}</section>`;
}
function overview(){
 const b=db.brands.find(x=>x.id===reportBrand)||db.brands[0];reportBrand=b.id;
 const report=brandReport();if(!report)return '<p>正在准备品牌报告…</p>';
 const rs=reportRecords(),ps=reportProducts(),written=report.sections.some(s=>s.summary);
 return `<div class="report-toolbar"><label class="report-brand-picker">品牌<select id="report-brand" aria-label="选择报告品牌">${db.brands.map(x=>`<option value="${esc(x.id)}" ${x.id===b.id?'selected':''}>${esc(x.name)}</option>`).join('')}</select></label><div class="actions"><button id="report-mode" class="${reportPresent?'primary':''}">${reportPresent?'返回工作视图':'进入汇报视图'}</button><button id="report-export">导出报告</button>${db.review_analysis?.brand_id===b.id?'<button id="report-package">导出报告与证据</button>':''}</div></div><div class="brand-report"><div class="report-cover"><h1>${esc(report.title)}</h1><div class="report-cover-grid ${report.cover_figure?'has-figure':''}"><div><p class="report-lead">${esc(report.summary||'已建立品牌与产品档案，按六大板块逐步研究。')}</p></div>${reportFigure(report.cover_figure,true)}</div>${report.profile?.length?`<div class="report-profile">${report.profile.map(card=>`<div><span>${esc(card.label)}</span><h3>${esc(card.value)}</h3><p>${esc(card.detail)}</p><details class="profile-source"><summary>依据</summary>${reportCitations(card.record_ids)}</details></div>`).join('')}</div>`:''}<details class="report-cover-notes"><summary>报告范围与来源 · ${esc(report.updated_at?.slice(0,10)||'待研究')}</summary><p>${esc(report.scope)}</p>${reportCitations(report.summary_record_ids)}<button class="report-edit work-only" data-edit-report="0">编辑品牌速览</button></details>${report.summary_stale?'<p class="report-stale">资料已有变化，整体小结待复核。</p>':''}</div><nav class="report-jumpbar" aria-label="六大板块目录">${db.sections.map((s,i)=>`<button data-report-scroll="${i+1}"><span>${['一','二','三','四','五','六'][i]}</span>${esc(s)}</button>`).join('')}</nav><div class="report-layout"><div class="report-content">${report.sections.map(reportSection).join('')}</div></div><details class="report-work-summary work-only"><summary>研究进度与资料概况</summary><p>${ps.length}个独立产品档案 · ${ps.reduce((a,p)=>a+p.review_count,0).toLocaleString()}条评论</p>${report.sections.map(s=>`<div><button data-report-scroll="${s.number}">${esc(db.sections[s.number-1])}</button><span>${esc(reportProgress(s.number).label)}</span></div>`).join('')}<p>事实、分析判断、待研究问题分别保留；自动更新尚未启用。</p></details>${reviewAppendix()}<div class="report-end">Breescape 竞争资料库 · 竞品品牌研究框架 V1.0</div></div>`;
}
function reportEditor(number){
 const r=brandReport(),s=number?r.sections[number-1]:null;
 const refSelect=(name,available,chosen)=>`<label>关联研究条目（可多选，Mac 按住⌘）<select multiple name="${name}">${available.map(x=>`<option value="${x.id}" ${chosen.includes(x.id)?'selected':''}>${esc(x.title+' · '+x.status)}</option>`).join('')}</select></label>`;
 const pick=(label,name,options,value)=>`<label>${label}<select name="${name}">${options.map(x=>`<option ${x===value?'selected':''}>${esc(x)}</option>`).join('')}</select></label>`;
 const scopedImages=(n,t)=>db.materials.filter(m=>evidenceImage(m)&&db.links.some(l=>l.material_id===m.id&&l.brand_id===reportBrand&&l.section===n&&(!t||l.topic===t.topic)&&(n!==2||l.product_id===t?.product_id)));
 const imageOptions=(images,chosen)=>images.map(m=>`<option value="${m.id}" ${chosen.includes(m.id)?'selected':''}>${esc(m.title)}</option>`).join('');
 let fields=number?field('本节核心标题','headline',s.headline)+textarea('先读的小结','summary',s.summary)+textarea('判断边界','boundary',s.boundary):field('报告标题','title',r.title)+textarea('整体小结','summary',r.summary)+textarea('研究范围与资料日期','scope',r.scope)+refSelect('summary_record_ids',reportRecords(),r.summary_record_ids);
 if(number){
  fields+=s.topics.map((t,i)=>{
   const pname=t.product_id?db.products.find(p=>p.id===t.product_id)?.name:'',available=reportRecords(number).filter(x=>x.topic===t.topic&&(number!==2||x.product_id===t.product_id));
   const chosen=(t.featured||[]).map(f=>f.record_id+':'+f.mode),images=scopedImages(number,t);
   const options=available.flatMap(x=>factualRecord(x)?[{value:x.id+':lead',label:x.title+' · 首段事实'},...(/(^|\n)\|/.test(x.body)?[{value:x.id+':table',label:x.title+' · 事实表格'}]:[])]:x.kind==='分析'&&['研究草稿','已复核'].includes(x.status)&&JSON.parse(x.evidence||'[]').length&&/(^|\n)\|/.test(x.body)?[{value:x.id+':analysis',label:x.title+' · 研究判断表格（非事实）'}]:[]);
   return `<div class="report-editor-topic"><h3>${esc((pname?pname+' / ':'')+t.topic)}</h3>${pick('问题完成情况','coverage_'+i,reportStatuses,topicStatus(t))}${pick('内容类型','answer_type_'+i,['事实概括','分析判断','研究问题'],t.answer_type||'事实概括')}${textarea('关键信息与阶段性认识','finding_'+i,t.finding)}${textarea('关键事实（每行一条，最多6条）','bullets_'+i,(t.bullets||[]).join('\n'))}${textarea('尚缺依据','gap_'+i,t.gap||'')}${textarea('缺口影响什么判断','impact_'+i,t.impact||'')}${refSelect('refs_'+i,available,t.record_ids)}<label>重点论据（可多选）<select multiple name="featured_${i}">${options.map(o=>`<option value="${o.value}" ${chosen.includes(o.value)?'selected':''}>${esc(o.label)}</option>`).join('')}</select></label><label>随正文展示的配图（可多选）<select multiple name="figures_${i}">${imageOptions(images,(t.figures||[]).map(f=>f.material_id))}</select></label>${images.map(m=>textarea('图片说明：'+m.title,'caption_'+i+'_'+m.id,t.figures?.find(f=>f.material_id===m.id)?.caption||m.summary||'')).join('')}</div>`;
  }).join('');
  fields+=`<label>补充截图（折叠展示）<select multiple name="report_images">${imageOptions(scopedImages(number),s.images||[])}</select></label>`;
 }else{
  const profiles=r.profile?.length?r.profile:Array.from({length:4},()=>({label:'',value:'',detail:'',record_ids:[]}));
  fields+=`<label>封面截图<select name="cover_image"><option value="">暂不展示</option>${imageOptions(scopedImages(1),[r.cover_figure?.material_id])}</select></label>`+textarea('封面图说明','cover_caption',r.cover_figure?.caption||'');
  fields+=profiles.map((card,i)=>`<div class="report-editor-topic"><h3>品牌速览 ${i+1}</h3>${field('栏目','profile_label_'+i,card.label)}${field('关键信息','profile_value_'+i,card.value)}${textarea('补充说明','profile_detail_'+i,card.detail)}${refSelect('profile_refs_'+i,reportRecords(),card.record_ids)}</div>`).join('');
 }
 openModal(number?'编辑第 '+number+' 板块小结':'编辑品牌速览',`<p class="muted">先概括，再关联依据。保存表示已复核当前资料；不改动原始记录。</p>`+fields,d=>{
  const values=name=>Array.from($('#fields [name="'+name+'"]').selectedOptions).map(o=>o.value),selected=name=>values(name).map(Number);
  const payload={brand_id:reportBrand,section:number,...d};
  if(number){
   payload.expected_revision=s.current_revision;payload.images=selected('report_images');
   payload.topics=s.topics.map((t,i)=>({topic:t.topic,product_id:t.product_id,finding:d['finding_'+i],record_ids:selected('refs_'+i),coverage:d['coverage_'+i],answer_type:d['answer_type_'+i],bullets:d['bullets_'+i].split('\n').map(x=>x.trim()).filter(Boolean),gap:d['gap_'+i],impact:d['impact_'+i],featured:values('featured_'+i).map(v=>{const [id,mode]=v.split(':');return {record_id:+id,mode,...(t.featured?.find(f=>f.record_id===+id)?.layout?{layout:t.featured.find(f=>f.record_id===+id).layout}:{})};}),figures:selected('figures_'+i).map(mid=>({material_id:mid,source_id:t.figures?.find(f=>f.material_id===mid)?.source_id||null,caption:d['caption_'+i+'_'+mid]}))}));
  }else{
   payload.summary_record_ids=selected('summary_record_ids');payload.expected_revisions=Object.fromEntries(r.sections.map(s=>[s.number,s.current_revision]));
   payload.cover_figure=d.cover_image?{material_id:+d.cover_image,source_id:r.cover_figure?.material_id===+d.cover_image?r.cover_figure.source_id:null,caption:d.cover_caption}:null;
   payload.profile=Array.from({length:r.profile?.length||4},(_,i)=>({label:d['profile_label_'+i],value:d['profile_value_'+i],detail:d['profile_detail_'+i],record_ids:selected('profile_refs_'+i)})).filter(c=>c.label||c.value||c.detail);
  }
  return api('/api/report',payload);
 });
}
async function exportBrandReport(portable=false){
 const button=$(portable?'#report-package':'#report-export');button.disabled=true;button.textContent='正在导出…';
 try{
  const clone=$('.brand-report').cloneNode(true),attachmentIds=new Set();
  clone.querySelectorAll('.work-only,.report-jumpbar').forEach(x=>x.remove());
  clone.querySelectorAll('.report-proof,.report-visuals').forEach(x=>x.open=false);
  for(const img of clone.querySelectorAll('img')){
   const url=new URL(img.getAttribute('src'),location.href);
   if(url.origin!==location.origin)continue;
   const response=await fetch(url);if(!response.ok)throw Error('截图导出失败，请重试');
   const blob=await response.blob();img.src=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result);reader.onerror=reject;reader.readAsDataURL(blob);});
   img.removeAttribute('loading');
   const a=img.closest('a');if(a)a.href=img.src;
  }
  clone.querySelectorAll('a').forEach(a=>{
   const href=a.getAttribute('href')||'';
   if(href.startsWith('/attachment/')){
    const file=db.review_analysis?.files.find(f=>href==='/attachment/'+f.material_id);
    if(portable&&file){a.href=encodeURIComponent('证据 v1.2')+'/'+encodeURIComponent(file.filename);a.setAttribute('download',file.filename);}
    else if(portable){
     const mid=Number(href.split('/').pop()),material=db.materials.find(m=>m.id===mid);
     if(!material?.local_path)throw Error('附件不存在，请刷新后重试');
     attachmentIds.add(mid);a.href=encodeURIComponent('附件')+'/'+encodeURIComponent(mid+'_'+material.local_path.split('/').pop());
     if(a.dataset.libraryVideo){a.removeAttribute('target');a.removeAttribute('download');}
    }else{a.removeAttribute('href');a.removeAttribute('data-library-video');a.textContent+=file?'（完整附件随“报告与证据”包提供）':'（随“报告与证据”包提供）';}
   }
   else if(/^#reviews\/sheets\/2\/review-\d+$/.test(href)){
    const id=href.split('review-')[1];if(clone.querySelector('#review-proof-'+id))a.href='#review-proof-'+id;else a.removeAttribute('href');
   }
   else if(href.startsWith('#')&&!clone.querySelector('[id="'+CSS.escape(href.slice(1))+'"]')){a.removeAttribute('href');}
  });
  const styles=await Promise.all(['/style.css','/reports.css'].map(async p=>{const r=await fetch(p);if(!r.ok)throw Error('导出样式读取失败');return r.text();}));
  const title=brandReport().title;
  const offlineScript="<script>document.addEventListener('click',function(e){var a=e.target.closest('a[href^=\"#\"]');if(!a)return;var t=document.getElementById(a.getAttribute('href').slice(1));if(!t)return;e.preventDefault();for(var n=t;n;n=n.parentElement)if(n.tagName==='DETAILS')n.open=true;t.scrollIntoView({block:'start'});});</script>";
  const html='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+'</title><style>'+styles.join('\n')+'\nbody{background:#fff}main{max-width:1200px;margin:auto;padding:32px}.report-layout{display:block}.work-only{display:none!important}</style></head><body class="standalone-report"><main>'+clone.outerHTML+'</main>'+offlineScript+'<script>const readingGlossary='+JSON.stringify(readingGlossary).replace(/</g,'\\u003c')+';('+installReadingTools.toString()+')();</script></body></html>';
  let blob=new Blob([html],{type:'text/html;charset=utf-8'}),filename=title.replace(/[\\/:*?"<>|]/g,'_')+'_'+new Intl.DateTimeFormat('sv-SE',{timeZone:'Asia/Shanghai'}).format(new Date())+'.html';
  if(portable){
   const r=await fetch('/api/report-package',{method:'POST',headers:{'Content-Type':'application/json','X-Library-Token':db.token},body:JSON.stringify({html,attachment_ids:[...attachmentIds],brand_id:reportBrand,document_updated_at:brandReport().updated_at,revisions:Object.fromEntries(brandReport().sections.map(s=>[s.number,s.current_revision]))})});
   if(!r.ok)throw Error((await r.json()).error||'证据包导出失败');blob=await r.blob();filename='Shilucheng_品牌研究总览_完整证据_2026-11-05.zip';
  }
  const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),5000);
  toast(portable?'报告与证据已打包；请整体解压、保留相对位置，原始网站仍需联网':'报告已导出；正文、截图与关键原文可离线阅读，完整附件请用“导出报告与证据”');
 }catch(e){toast(e.message);}finally{button.disabled=false;button.textContent=portable?'导出报告与证据':'导出报告';}
}
let reportPrintDetails=[];
window.addEventListener('beforeprint',()=>{
 reportPrintDetails=Array.from(document.querySelectorAll('.report-audit,.report-cover-notes,.report-more-sources,.figure-source')).map(el=>({el,open:el.open}));
 reportPrintDetails.forEach(({el})=>el.open=true);
});
window.addEventListener('afterprint',()=>{reportPrintDetails.forEach(({el,open})=>el.open=open);reportPrintDetails=[];});
function bindReport(){
 document.body.classList.toggle('presenting',view==='overview'&&reportPresent);
 if(view!=='overview')return;
 $('#report-brand').onchange=e=>openReport(e.target.value,reportPresent);
 $('#report-mode').onclick=()=>openReport(reportBrand,!reportPresent);
 $('#report-export').onclick=()=>exportBrandReport(false);
 if($('#report-package'))$('#report-package').onclick=()=>exportBrandReport(true);
 document.querySelectorAll('[data-open-evidence]').forEach(a=>a.onclick=e=>{e.preventDefault();const target=document.getElementById(a.dataset.openEvidence);if(target){target.closest('details').open=true;target.scrollIntoView({behavior:'smooth',block:'start'});}});
 document.querySelectorAll('[data-edit-report]').forEach(b=>b.onclick=()=>reportEditor(+b.dataset.editReport));
 document.querySelectorAll('[data-question-scroll]').forEach(a=>a.onclick=e=>{e.preventDefault();document.getElementById(a.dataset.questionScroll)?.scrollIntoView({behavior:'smooth',block:'start'});});
 document.querySelectorAll('[data-report-scroll]').forEach(b=>b.onclick=()=>$('#report-section-'+b.dataset.reportScroll).scrollIntoView({behavior:'smooth',block:'start'}));
}
