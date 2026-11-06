'use strict';
let reportBrand='shilucheng', reportPresent=false;
const factualRecord=r=>['已核实页面信息','品牌自述'].includes(r.status);
const reportStatuses=['已回答','部分回答','尚未研究','资料待补','待你确认','等待前置研究'];
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
 return `<figure class="report-figure ${cover?'report-cover-figure':''}"><a class="figure-zoom" href="/attachment/${m.id}" target="_blank" rel="noopener" aria-label="查看原图：${esc(m.title)}"><img src="/attachment/${m.id}" alt="${esc(m.title)}" ${cover?'':'loading="lazy"'}></a><figcaption><b>${esc(f.caption||m.summary||m.title)}</b><span>${esc(m.source_type)} · 采集 ${esc((m.retrieved_at||'').slice(0,10))}${source?.url?` · <a href="${esc(safeURL(source.url))}" target="_blank" rel="noopener">原始页面 ↗</a>`:''} · 点击图片放大</span></figcaption></figure>`;
}
function featuredEvidence(f){
 const r=db.records.find(x=>x.id===f.record_id);if(!r)return '';
 if(!factualRecord(r))return `<p class="report-boundary">原引用「${esc(r.title)}」已变为${esc(r.status)}，请复核小结。</p>`;
 const blocks=r.body.split(/\n\s*\n/),body=f.mode==='table'?r.body:blocks.find(b=>!b.trim().startsWith('|'));
 return body?`<div class="report-evidence"><div class="evidence-caption">${esc(r.kind)}依据 · ${esc(r.title)}</div>${formatBody(body)}</div>`:'';
}
function reportTopic(t,n){
 const ids=t.record_ids||[],available=reportRecords(n).filter(r=>r.topic===t.topic&&(n!==2||r.product_id===t.product_id));
 const showIds=ids.length?ids:available.map(r=>r.id),pending=t.answer_type==='研究问题'||!t.finding;
 return `<article id="${topicAnchor(t,n)}" class="report-topic ${pending?'unwritten':''}"><div class="topic-heading"><h4>${esc(t.topic)}</h4><span class="topic-kind">${esc(t.answer_type||'事实概括')}</span></div><p class="topic-finding">${esc(t.finding||(available.length?'已收录材料，尚未归纳为报告小结。':'该问题尚未开展研究。'))}</p>${t.bullets?.length?`<ul class="report-key-facts">${t.bullets.map(b=>`<li>${esc(b)}</li>`).join('')}</ul>`:''}${(t.figures||[]).map(f=>reportFigure(f)).join('')}${(t.featured||[]).map(featuredEvidence).join('')}${t.gap?`<div class="topic-gap"><b>尚缺依据</b><span>${esc(t.gap)}</span>${t.impact?`<small>${esc(t.impact)}</small>`:''}</div>`:''}${showIds.length?reportCitations(showIds):''}${showIds.length?`<details class="report-proof work-only"><summary>查验研究条目（${showIds.length}）</summary>${showIds.map(id=>{const r=db.records.find(x=>x.id===id);return r?`<div class="proof-row">${pill(r.status)}<a href="${recordRoute(r)}">${esc(r.title)} →</a><small>${r.product_id?esc(db.products.find(p=>p.id===r.product_id)?.name):'品牌级'} · ${esc(r.updated_at.slice(0,10))}</small></div>`:'';}).join('')}</details>`:''}</article>`;
}
function questionProgress(s){return `<details class="question-progress work-only"><summary>查看本节问题完成情况 · ${reportProgress(s.number).label}</summary><div>${s.topics.map(t=>`<a class="question-row" href="#${topicAnchor(t,s.number)}" data-question-scroll="${topicAnchor(t,s.number)}"><span>${esc(t.topic)}${t.product_id?`<small>${esc(db.products.find(p=>p.id===t.product_id)?.name)}</small>`:''}</span><em>${esc(topicStatus(t))}</em><small>${esc(t.gap||'尚未标注具体缺口')}</small></a>`).join('')}</div></details>`;}
function pendingQuestions(s){return `<div class="pending-questions"><span class="report-label">待研究问题与所需依据</span>${s.topics.map(t=>`<div class="pending-question" id="${topicAnchor(t,s.number)}"><h4>${esc(t.topic)}</h4><p>${esc(t.gap||t.finding||'尚未开展研究。')}</p>${(t.record_ids||[]).length?`<a class="work-only" href="${recordRoute(db.records.find(r=>r.id===t.record_ids[0]))}">查看已有依据 →</a>`:''}</div>`).join('')}</div>`;}
function reportSection(s){
 const p=reportProgress(s.number),pid=representativeProduct();let topics='';
 if(s.number===2){topics=reportProducts().map(product=>{
  const rows=s.topics.filter(t=>t.product_id===product.id),written=rows.some(t=>t.finding);
  return `<div class="report-product"><div class="report-product-heading"><div><small>${esc(product.channel)} · ${esc(product.market)} · 商品ID ${esc(product.external_id)}</small><h3>${esc(product.name)}</h3></div><div><a href="${esc(safeURL(product.url))}" target="_blank" rel="noopener">商品原页 ↗</a><a class="work-only" href="#research/${product.id}/2">产品研究 →</a></div></div>${written?rows.map(t=>reportTopic(t,2)).join(''):`<p class="report-empty-line">尚未开展该产品研究；独立保留档案与问题，不与其他单品混合。</p><div class="unwritten-topics">${rows.map(t=>`<span id="${topicAnchor(t,2)}">${esc(t.topic)}</span>`).join('')}</div>`}</div>`;
 }).join('');}else topics=s.topics.every(t=>(t.answer_type==='研究问题'||!t.finding)&&!t.featured?.length&&!t.figures?.length)?pendingQuestions(s):s.topics.map(t=>reportTopic(t,s.number)).join('');
 const images=(s.images||[]).map(id=>db.materials.find(m=>m.id===id)).filter(m=>m&&evidenceImage(m));
 return `<section class="report-section ${s.summary?'':'report-section-empty'}" id="report-section-${s.number}"><div class="report-section-kicker"><span>0${s.number} / ${esc(db.sections[s.number-1])}</span><span class="work-only"><button class="report-edit" data-edit-report="${s.number}">编辑本节</button></span></div><h2>${esc(s.headline||'尚未形成研究小结')}</h2><p class="report-section-summary">${esc(s.summary||'按V1.0保留研究目录，目前没有足够资料形成结论。')}</p>${s.stale?'<div class="report-stale">本节依据已发生变化，小结待复核。</div>':''}${questionProgress(s)}<div class="report-topics">${topics}</div>${images.length?`<details class="report-visuals"><summary>其他页面证据 · ${images.length} 张截图</summary><div class="evidence-grid">${images.map(evidencePreview).join('')}</div></details>`:''}${s.boundary?`<div class="report-boundary"><strong>判断边界</strong><p>${esc(s.boundary)}</p></div>`:''}<div class="report-section-footer work-only"><span>${s.updated_at?'小结更新 '+esc(s.updated_at.slice(0,10)):'尚未撰写小结'}</span><a href="#research/${pid}/${s.number}">查看完整板块 →</a></div></section>`;
}
function overview(){
 const b=db.brands.find(x=>x.id===reportBrand)||db.brands[0];reportBrand=b.id;
 const report=brandReport();if(!report)return '<p>正在准备品牌报告…</p>';
 const rs=reportRecords(),ps=reportProducts(),written=report.sections.some(s=>s.summary),last=rs.map(r=>r.updated_at.slice(0,10)).sort().at(-1)||'尚未收录';
 return `<div class="report-toolbar"><label class="report-brand-picker">品牌<select id="report-brand" aria-label="选择报告品牌">${db.brands.map(x=>`<option value="${esc(x.id)}" ${x.id===b.id?'selected':''}>${esc(x.name)}</option>`).join('')}</select></label><div class="actions"><button id="report-mode" class="${reportPresent?'primary':''}">${reportPresent?'返回工作视图':'进入汇报视图'}</button><button id="report-export">导出报告</button></div></div><div class="brand-report"><div class="report-cover"><div class="report-eyebrow">BREESCAPE · COMPETITOR RESEARCH / V1.0</div><div class="report-heading"><h1>${esc(report.title)}</h1><span class="report-phase">${written?'阶段性研究报告':'待研究 · 目录已建立'}</span></div><div class="report-date">小结更新 ${esc(report.updated_at?.slice(0,10)||'—')}<span>资料最近更新 ${esc(last)}</span><button class="report-edit work-only" data-edit-report="0">编辑品牌速览</button></div><div class="report-cover-grid ${report.cover_figure?'has-figure':''}"><div><div class="report-lead"><span class="report-label">品牌概貌</span><p>${esc(report.summary||'已建立品牌与产品档案。按六大板块逐步补入事实、论据与小结。')}</p></div>${report.summary_record_ids.length?reportCitations(report.summary_record_ids):''}</div>${reportFigure(report.cover_figure,true)}</div>${report.profile?.length?`<div class="report-profile">${report.profile.map(card=>`<div><span>${esc(card.label)}</span><h3>${esc(card.value)}</h3><p>${esc(card.detail)}</p><details class="profile-source"><summary>查看依据</summary>${reportCitations(card.record_ids)}</details></div>`).join('')}</div>`:''}<p class="report-scope"><b>研究范围</b> ${esc(report.scope||'现有产品：'+ps.map(p=>p.name).join('、')+'。具体产品信息和研究结论待核实。')}</p>${report.summary_stale?'<div class="report-stale">资料已有变化，整体小结待复核。</div>':''}</div><nav class="report-jumpbar" aria-label="报告目录">${db.sections.map((s,i)=>`<button data-report-scroll="${i+1}">0${i+1} ${esc(s)}</button>`).join('')}</nav><div class="report-layout"><div class="report-content">${report.sections.map(reportSection).join('')}</div><div class="report-side work-only"><div class="report-contents"><h3>问题完成情况</h3><p>按研究问题统计，不按材料条数</p>${db.sections.map((t,i)=>`<button data-report-scroll="${i+1}"><span class="toc-number">0${i+1}</span><span>${esc(t)}<small>${esc(reportProgress(i+1).label)}</small></span></button>`).join('')}<div class="report-coverage"><b>本品牌资料</b><span>${ps.length} 个独立产品档案</span><span>${ps.reduce((a,p)=>a+p.review_count,0).toLocaleString()} 条评论已接入</span></div><div class="report-legend">部分回答表示仍有关键缺口。第五、六板块的判断依赖前置研究；进入汇报视图可专注阅读。</div></div></div></div><div class="report-end">Breescape 竞争资料库 · 竞品品牌研究框架 V1.0 · 事实按标注日期与范围解读</div></div>`;
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
   const options=available.filter(factualRecord).flatMap(x=>[{value:x.id+':lead',label:x.title+' · 首段事实'},...(/(^|\n)\|/.test(x.body)?[{value:x.id+':table',label:x.title+' · 表格及完整口径'}]:[])]);
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
   payload.topics=s.topics.map((t,i)=>({topic:t.topic,product_id:t.product_id,finding:d['finding_'+i],record_ids:selected('refs_'+i),coverage:d['coverage_'+i],answer_type:d['answer_type_'+i],bullets:d['bullets_'+i].split('\n').map(x=>x.trim()).filter(Boolean),gap:d['gap_'+i],impact:d['impact_'+i],featured:values('featured_'+i).map(v=>{const [id,mode]=v.split(':');return {record_id:+id,mode};}),figures:selected('figures_'+i).map(mid=>({material_id:mid,source_id:t.figures?.find(f=>f.material_id===mid)?.source_id||null,caption:d['caption_'+i+'_'+mid]}))}));
  }else{
   payload.summary_record_ids=selected('summary_record_ids');payload.expected_revisions=Object.fromEntries(r.sections.map(s=>[s.number,s.current_revision]));
   payload.cover_figure=d.cover_image?{material_id:+d.cover_image,source_id:r.cover_figure?.material_id===+d.cover_image?r.cover_figure.source_id:null,caption:d.cover_caption}:null;
   payload.profile=Array.from({length:r.profile?.length||4},(_,i)=>({label:d['profile_label_'+i],value:d['profile_value_'+i],detail:d['profile_detail_'+i],record_ids:selected('profile_refs_'+i)})).filter(c=>c.label||c.value||c.detail);
  }
  return api('/api/report',payload);
 });
}
async function exportBrandReport(){
 const button=$('#report-export');button.disabled=true;button.textContent='正在导出…';
 try{
  const clone=$('.brand-report').cloneNode(true);
  clone.querySelectorAll('.work-only,.report-jumpbar').forEach(x=>x.remove());
  clone.querySelectorAll('.report-visuals').forEach(x=>x.open=true);
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
   if(href.startsWith('/attachment/')){a.removeAttribute('href');a.textContent+='（附件已收录于本地资料库）';}
   else if(href.startsWith('#')){a.removeAttribute('href');}
  });
  const styles=await Promise.all(['/style.css','/reports.css'].map(async p=>{const r=await fetch(p);if(!r.ok)throw Error('导出样式读取失败');return r.text();}));
  const title=brandReport().title;
  const html='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+'</title><style>'+styles.join('\n')+'\nbody{background:#fff}main{max-width:1200px;margin:auto;padding:32px}.report-layout{display:block}.work-only{display:none!important}</style></head><body class="standalone-report"><main>'+clone.outerHTML+'</main></body></html>';
  const url=URL.createObjectURL(new Blob([html],{type:'text/html;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download=title.replace(/[\\/:*?"<>|]/g,'_')+'_'+new Intl.DateTimeFormat('sv-SE',{timeZone:'Asia/Shanghai'}).format(new Date())+'.html';a.click();setTimeout(()=>URL.revokeObjectURL(url),5000);
  toast('报告已导出；文字和截图可离线查看，原始网络链接按需访问');
 }catch(e){toast(e.message);}finally{button.disabled=false;button.textContent='导出报告';}
}
let reportPrintDetails=[];
window.addEventListener('beforeprint',()=>{
 reportPrintDetails=Array.from(document.querySelectorAll('.report-visuals')).map(el=>({el,open:el.open}));
 reportPrintDetails.forEach(({el})=>el.open=true);
});
window.addEventListener('afterprint',()=>{reportPrintDetails.forEach(({el,open})=>el.open=open);reportPrintDetails=[];});
function bindReport(){
 document.body.classList.toggle('presenting',view==='overview'&&reportPresent);
 if(view!=='overview')return;
 $('#report-brand').onchange=e=>openReport(e.target.value,reportPresent);
 $('#report-mode').onclick=()=>openReport(reportBrand,!reportPresent);
 $('#report-export').onclick=exportBrandReport;
 document.querySelectorAll('[data-edit-report]').forEach(b=>b.onclick=()=>reportEditor(+b.dataset.editReport));
 document.querySelectorAll('[data-question-scroll]').forEach(a=>a.onclick=e=>{e.preventDefault();document.getElementById(a.dataset.questionScroll)?.scrollIntoView({behavior:'smooth',block:'start'});});
 document.querySelectorAll('[data-report-scroll]').forEach(b=>b.onclick=()=>$('#report-section-'+b.dataset.reportScroll).scrollIntoView({behavior:'smooth',block:'start'}));
}
