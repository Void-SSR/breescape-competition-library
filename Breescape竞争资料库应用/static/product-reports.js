'use strict';
// A single research record feeds both the brand directory and its product report.
function productReportRoute(pid=product,present=false){return '#product-report/'+pid+(present?'/present':'');}
function productReportData(pid){return brandReport()?.product_reports?.[pid]||{};}
function merchantReason(meta,compact=false){
 const r=meta.merchant_reason;
 if(!r)return '<p class="question-note">商家主推的购买理由尚未核实。</p>';
 return `<div class="merchant-reason ${compact?'compact':''}"><span>商家主推的购买理由</span><${compact?'h4':'h2'}>${esc(r.headline)}</${compact?'h4':'h2'}><p>${esc(r.structure)}${r.detail?' · '+esc(r.detail):''}</p>${compact?'':`<details class="merchant-source"><summary>查看商家表达与判断依据</summary><p>${esc(r.basis||'依据商品标题、主图及商家详情归纳；不等同于消费者实际购买原因或已证实的产品效果。')}</p>${reportCitations(r.record_ids||[])}</details>`}</div>`;
}
function productFacts(meta){return `<dl class="product-report-facts">${(meta.key_facts||[]).map(f=>`<div><dt>${esc(f.label)}</dt><dd>${esc(f.value)}</dd>${f.detail?`<small>${esc(f.detail)}</small>`:''}</div>`).join('')}</dl>`;}
function productReportCard(p){
 const meta=productReportData(p.id);
 return `<article class="product-report-card"><h3><a href="${productReportRoute(p.id,reportPresent)}">${esc(p.name)}</a></h3>${merchantReason(meta,true)}${productFacts(meta)}${meta.summary?`<p class="product-card-summary">${esc(meta.summary)}</p>`:''}<div class="product-card-links"><a href="${productReportRoute(p.id,reportPresent)}">打开本款产品报告 →</a><a href="${esc(safeURL(p.url))}" target="_blank" rel="noopener">${esc(p.channel)}商品原页 ↗</a></div></article>`;
}
function productReportSections(pid){
 return brandReport().sections.map(s=>({...s,topics:s.topics.filter(t=>s.number===2?t.product_id===pid:t.scope_product_id===pid)})).filter(s=>s.topics.length);
}
function productReport(){
 const p=current(),meta=productReportData(p.id),sections=productReportSections(p.id),basic=sections.find(s=>s.number===2);
 const firstFigure=meta.cover_figure||basic?.topics.flatMap(t=>(t.questions||[]).flatMap(q=>q.figures||[]))[0];
 const readingTopic=(t,n)=>reportTopic({...t,questions:(t.questions||[]).map(q=>({...q,figures:(q.figures||[]).filter(f=>f.material_id!==firstFigure?.material_id)}))},n);
 const sectionsHtml=sections.map(s=>s.number===2?s.topics.map(t=>`<section class="report-section product-chapter">${readingTopic(t,2)}</section>`).join(''):`<section class="report-section" id="product-section-${s.number}"><div class="report-chapter-heading"><h2>${s.number===3?'本款的渠道内容与传播':'本款对Breescape的启示与机会'}</h2></div>${s.topics.map(t=>readingTopic(t,s.number)).join('')}</section>`).join('');
 const navigation=(basic?.topics||[]).map(t=>({id:topicAnchor(t,2),label:t.display_title||t.topic}));
 sections.filter(s=>s.number!==2).forEach(s=>navigation.push({id:'product-section-'+s.number,label:s.number===3?'渠道内容与传播':'启示与机会'}));
 return `<div class="report-toolbar"><label class="report-brand-picker">产品<select id="product-select" aria-label="选择产品">${productOptions()}</select></label><div class="actions"><button id="report-mode" class="${reportPresent?'primary':''}">${reportPresent?'返回工作视图':'进入汇报视图'}</button><button id="report-export">导出报告</button>${p.id==='sheets'?'<button id="report-package">导出报告与证据</button>':''}</div></div><div class="brand-report product-report" data-report-product="${esc(p.id)}"><div class="report-cover"><p class="product-report-breadcrumb"><a href="${reportRoute(p.brand_id,reportPresent)}">${esc(brand(p))} 品牌总览</a><span> / 产品研究报告</span></p><h1>${esc(brand(p))} ${esc(p.name)}</h1>${merchantReason(meta)}<div class="report-cover-grid ${firstFigure?'has-figure':''}"><div>${productFacts(meta)}${meta.summary?`<p class="product-report-intro">${esc(meta.summary)}</p>`:''}<a class="product-page-link" href="${esc(safeURL(p.url))}" target="_blank" rel="noopener">${esc(p.channel)} · ${esc(p.market)} · 打开本款商品 ↗</a></div>${reportFigure(firstFigure,true)}</div></div><nav class="report-jumpbar" aria-label="产品研究目录">${navigation.map(n=>`<button data-question-scroll="${esc(n.id)}">${esc(n.label)}</button>`).join('')}</nav><div class="report-content">${sectionsHtml}</div><details class="report-research-log"><summary>本款来源、研究进度与待补事项</summary><p class="question-note">商品ID：${esc(p.external_id)} · 本款独立评论 ${p.review_count.toLocaleString()} 条。品牌背景、经营规模与发展历程见品牌总览。</p>${meta.pending?.length?`<ul>${meta.pending.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`:''}${sections.map(reportAudit).join('')}</details>${reviewAppendix()}<div class="report-end">Breescape 竞争资料库 · 竞品品牌研究框架 V1.0 · ${esc(p.name)}</div></div>`;
}
