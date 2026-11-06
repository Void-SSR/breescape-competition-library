'use strict';
let reportBrand='shilucheng', reportPresent=false;
const factualRecord=r=>['已核实页面信息','品牌自述'].includes(r.status);
function brandReport(){return db.reports.find(r=>r.brand_id===reportBrand);}
function reportProducts(){return db.products.filter(p=>p.brand_id===reportBrand);}
function reportRecords(n){return db.records.filter(r=>r.brand_id===reportBrand&&(!n||r.section===n));}
function representativeProduct(bid=reportBrand){return db.products.find(p=>p.brand_id===bid)?.id||product;}
function reportRoute(bid=reportBrand,present=reportPresent){return '#overview/'+bid+(present?'/present':'');}
function recordRoute(r){return '#research/'+(r.product_id||representativeProduct(r.brand_id))+'/'+r.section+'/record-'+r.id;}
function openReport(bid=reportBrand,present=false){location.hash=reportRoute(bid,present);}
function reportProgress(n){
 const rs=reportRecords(n),facts=rs.filter(factualRecord).length;
 return {facts,total:rs.length,label:rs.some(r=>r.status==='待你确认')?'候选待确认':facts?'已有事实 · 研究未完':rs.length?'等待前置证据':'尚未研究'};
}
function reportSources(ids){
 const mids=[...new Set(ids.flatMap(id=>JSON.parse(db.records.find(r=>r.id===id)?.evidence||'[]')))];
 return mids.map(id=>db.materials.find(m=>m.id===id)).filter(Boolean);
}
function reportCitations(ids){return `<div class="report-citations"><span>资料来源</span>${reportSources(ids).map(m=>`<a href="${esc(materialHref(m))}" target="_blank" rel="noopener" title="${esc(m.publisher+' · '+m.retrieved_at)}">${esc(m.title)} ↗</a>`).join('')||'<span>尚无可引用材料</span>'}</div>`;}
function featuredEvidence(f){
 const r=db.records.find(x=>x.id===f.record_id);if(!r)return '';
 if(!factualRecord(r))return `<p class="report-boundary">原引用「${esc(r.title)}」已变为${esc(r.status)}，请复核小结。</p>`;
 const blocks=r.body.split(/\n\s*\n/),body=f.mode==='table'?r.body:blocks.find(b=>!b.trim().startsWith('|'));
 return body?`<div class="report-evidence"><div class="evidence-caption">${esc(r.kind)}依据 · ${esc(r.title)}</div>${formatBody(body)}</div>`:'';
}
function reportTopic(t,n){
 const ids=t.record_ids||[],rs=ids.map(id=>db.records.find(r=>r.id===id)).filter(Boolean);
 const available=reportRecords(n).filter(r=>r.topic===t.topic&&(n!==2||r.product_id===t.product_id));
 const showIds=ids.length?ids:available.map(r=>r.id);
 const pending=!t.finding;
 return `<div class="report-topic ${pending?'unwritten':''}"><h4>${esc(t.topic)}</h4><p class="topic-finding">${esc(t.finding||(available.length?'已收录材料，尚未归纳为报告小结。':'该问题尚未开展研究。'))}</p>${(t.featured||[]).map(featuredEvidence).join('')}${showIds.length?reportCitations(showIds):''}${showIds.length?`<details class="report-proof work-only"><summary>查验研究条目（${showIds.length}）</summary>${showIds.map(id=>{const r=db.records.find(x=>x.id===id);return r?`<div class="proof-row">${pill(r.status)}<a href="${recordRoute(r)}">${esc(r.title)} →</a><small>${r.product_id?esc(db.products.find(p=>p.id===r.product_id)?.name):'品牌级'} · ${esc(r.updated_at.slice(0,10))}</small></div>`:'';}).join('')}</details>`:''}</div>`;
}
function reportSection(s){
 const progress=reportProgress(s.number),hasText=Boolean(s.summary),pid=representativeProduct();
 let topics='';
 if(s.number===2){
  topics=reportProducts().map(p=>{
   const rows=s.topics.filter(t=>t.product_id===p.id),written=rows.some(t=>t.finding);
   return `<div class="report-product"><div class="report-product-heading"><div><small>${esc(p.channel)} · ${esc(p.market)} · 商品ID ${esc(p.external_id)}</small><h3>${esc(p.name)}</h3></div><a class="work-only" href="#research/${p.id}/2">产品研究 →</a></div>${written?rows.map(t=>reportTopic(t,2)).join(''):`<p class="report-empty-line">尚未形成该产品的研究小结。${p.review_count?`已接入 ${p.review_count.toLocaleString()} 条评论，分析状态以产品档案为准。`:''}</p><div class="unwritten-topics">${rows.map(t=>`<span>${esc(t.topic)}</span>`).join('')}</div>`}</div>`;
  }).join('');
 }else topics=!hasText&&!reportRecords(s.number).length?`<div class="unwritten-topics">${s.topics.map(t=>`<span>${esc(t.topic)}</span>`).join('')}</div>`:s.topics.map(t=>reportTopic(t,s.number)).join('');
 const images=(s.images||[]).map(id=>db.materials.find(m=>m.id===id)).filter(m=>m&&evidenceImage(m));
 return `<section class="report-section ${hasText?'':'report-section-empty'}" id="report-section-${s.number}"><div class="report-section-kicker"><span>0${s.number} / ${esc(db.sections[s.number-1])}</span><span class="work-only">${pill(progress.label)}<button class="report-edit" data-edit-report="${s.number}">编辑本节</button></span></div><h2>${esc(s.headline||(progress.facts?'已有资料，等待形成阶段性小结':'尚未形成研究小结'))}</h2><p class="report-section-summary">${esc(s.summary||(progress.total?'材料与研究状态已保留，需核对证据后撰写小结。':'按V1.0保留研究目录，目前没有足够资料形成结论。'))}</p>${s.stale?'<div class="report-stale">本节依据已发生变化，小结待复核。汇报前请核对最新资料。</div>':''}<div class="report-topics">${topics}</div>${images.length?`<details class="report-visuals"><summary>页面证据 · ${images.length} 张截图</summary><div class="evidence-grid">${images.map(evidencePreview).join('')}</div></details>`:''}${s.boundary?`<div class="report-boundary"><strong>判断边界</strong><p>${esc(s.boundary)}</p></div>`:''}<div class="report-section-footer work-only"><span>${s.updated_at?'小结更新 '+esc(s.updated_at.slice(0,10)):'尚未撰写小结'}</span><a href="#research/${pid}/${s.number}">查看完整板块 →</a></div></section>`;
}
function overview(){
 const b=db.brands.find(x=>x.id===reportBrand)||db.brands[0];reportBrand=b.id;
 const report=brandReport();if(!report)return '<p>正在准备品牌报告…</p>';
 const rs=reportRecords(),facts=rs.filter(factualRecord).length,ps=reportProducts(),written=report.sections.filter(s=>s.summary).length;
 const lastSource=rs.map(r=>r.updated_at.slice(0,10)).sort().at(-1)||'尚未收录';
 return `<div class="report-toolbar"><label class="report-brand-picker">品牌<select id="report-brand" aria-label="选择报告品牌">${db.brands.map(x=>`<option value="${esc(x.id)}" ${x.id===b.id?'selected':''}>${esc(x.name)}</option>`).join('')}</select></label><div class="actions"><button id="report-mode" class="${reportPresent?'primary':''}">${reportPresent?'返回工作视图':'进入汇报视图'}</button><button id="report-export">导出报告</button></div></div><div class="brand-report"><div class="report-cover"><div class="report-eyebrow">BREESCAPE · COMPETITOR RESEARCH / V1.0</div><div class="report-heading"><h1>${esc(report.title)}</h1><span class="report-phase">${written?'阶段性研究报告':'待研究 · 目录已建立'}</span></div><div class="report-date">小结更新 ${esc(report.updated_at?.slice(0,10)||'—')}<span>资料条目最近更新 ${esc(lastSource)}</span><button class="report-edit work-only" data-edit-report="0">编辑整体小结</button></div><div class="report-lead"><span class="report-label">整体小结</span><p>${esc(report.summary||'目前已建立品牌与产品档案，尚未形成有证据支持的整体判断。后续按六大板块逐步补入事实、论据与小结。')}</p></div>${report.summary_record_ids.length?reportCitations(report.summary_record_ids):''}<p class="report-scope"><b>研究范围</b> ${esc(report.scope||'现有产品：'+ps.map(p=>p.name).join('、')+'。具体产品信息和研究结论待核实。')}</p>${report.summary_stale?'<div class="report-stale">资料已有变化，整体小结待复核。下文保留各板块的独立复核状态。</div>':''}</div><div class="report-layout"><div class="report-content">${report.sections.map(reportSection).join('')}</div><div class="report-side work-only"><div class="report-contents"><h3>目录与研究进度</h3><p>事实已收录，不代表研究完成</p>${db.sections.map((t,i)=>{let p=reportProgress(i+1);return `<button data-report-scroll="${i+1}"><span class="toc-number">0${i+1}</span><span>${esc(t)}<small>${esc(p.label)} · ${p.facts} 条事实/自述</small></span></button>`;}).join('')}<div class="report-coverage"><b>本品牌资料</b><span>${ps.length} 个产品档案 · ${facts} 条事实/自述</span><span>${ps.reduce((a,p)=>a+p.review_count,0).toLocaleString()} 条评论已接入</span></div><div class="report-legend">事实、自述和分析分开呈现。缺失资料保留边界；候选确认后再开展内容研究。</div></div></div></div><div class="report-end">Breescape 竞争资料库 · 竞品品牌研究框架 V1.0 · 报告中的事实按标注日期与范围解读</div></div>`;
}
function reportEditor(number){
 const r=brandReport(),s=number?r.sections[number-1]:null;
 const refSelect=(name,available,chosen)=>`<label>关联研究条目（可多选，Mac 按住⌘）<select multiple name="${name}">${available.map(x=>`<option value="${x.id}" ${chosen.includes(x.id)?'selected':''}>${esc(x.title+' · '+x.status)}</option>`).join('')}</select></label>`;
 let fields=number?field('本节核心标题','headline',s.headline)+textarea('先读的小结','summary',s.summary)+textarea('判断边界 / 仍缺的证据','boundary',s.boundary):field('报告标题','title',r.title)+textarea('整体小结','summary',r.summary)+textarea('研究范围与资料日期','scope',r.scope)+refSelect('summary_record_ids',reportRecords(),r.summary_record_ids);
 if(number){
  fields+=s.topics.map((t,i)=>{
   const pname=t.product_id?db.products.find(p=>p.id===t.product_id)?.name:'';
   const available=reportRecords(number).filter(x=>x.topic===t.topic&&(number!==2||x.product_id===t.product_id));
   const chosen=t.featured?.[0],value=chosen?chosen.record_id+':'+chosen.mode:'';
   const options=available.filter(factualRecord).flatMap(x=>[{value:x.id+':lead',label:x.title+' · 首段事实'},...(/(^|\n)\|/.test(x.body)?[{value:x.id+':table',label:x.title+' · 表格及完整口径'}]:[])]);
   return `<div class="report-editor-topic"><h3>${esc((pname?pname+' / ':'')+t.topic)}</h3>${textarea('关键信息与阶段性认识','finding_'+i,t.finding)}${refSelect('refs_'+i,available,t.record_ids)}<label>在报告中展示的重点论据<select name="featured_${i}"><option value="">仅展示小结与来源</option>${options.map(o=>`<option value="${o.value}" ${o.value===value?'selected':''}>${esc(o.label)}</option>`).join('')}</select><small>请同时在上方关联该研究条目。表格保留原记录的规格、时间和口径说明。</small></label></div>`;
  }).join('');
  const images=db.materials.filter(m=>evidenceImage(m)&&db.links.some(l=>l.material_id===m.id&&l.brand_id===reportBrand&&l.section===number));
  fields+=`<label>本节截图（可多选，Mac 按住⌘）<select multiple name="report_images">${images.map(m=>`<option value="${m.id}" ${s.images.includes(m.id)?'selected':''}>${esc(m.title)}</option>`).join('')}</select><small>${images.length?'引用本节已收录的截图。':'本节暂未收录截图；添加材料后可以在此选用。'}</small></label>`;
 }
 openModal(number?'编辑第 '+number+' 板块小结':'编辑品牌整体小结',`<p class="muted">先概括，再关联依据。材料不足时保留缺口；不会改动原始条目。保存表示已复核当前资料。</p>`+fields,d=>{
  const selected=name=>Array.from($('#fields [name="'+name+'"]').selectedOptions).map(o=>+o.value);
  const payload={brand_id:reportBrand,section:number,...d};
  if(number){
   payload.expected_revision=s.current_revision;payload.images=selected('report_images');
   payload.topics=s.topics.map((t,i)=>{const f=(d['featured_'+i]||'').split(':');return {topic:t.topic,product_id:t.product_id,finding:d['finding_'+i],record_ids:selected('refs_'+i),featured:f[0]?[{record_id:+f[0],mode:f[1]}]:[]};});
  }else{
   payload.summary_record_ids=selected('summary_record_ids');
   payload.expected_revisions=Object.fromEntries(r.sections.map(s=>[s.number,s.current_revision]));
  }
  return api('/api/report',payload);
 });
}
async function exportBrandReport(){
 const button=$('#report-export');button.disabled=true;button.textContent='正在导出…';
 try{
  const clone=$('.brand-report').cloneNode(true);
  clone.querySelectorAll('.work-only').forEach(x=>x.remove());
  clone.querySelectorAll('details').forEach(x=>x.open=true);
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
  const url=URL.createObjectURL(new Blob([html],{type:'text/html;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download=title.replace(/[\\/:*?"<>|]/g,'_')+'_'+new Date().toISOString().slice(0,10)+'.html';a.click();setTimeout(()=>URL.revokeObjectURL(url),5000);
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
 document.querySelectorAll('[data-report-scroll]').forEach(b=>b.onclick=()=>$('#report-section-'+b.dataset.reportScroll).scrollIntoView({behavior:'smooth',block:'start'}));
}
