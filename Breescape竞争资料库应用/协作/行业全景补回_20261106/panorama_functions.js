// REPLACE atlasMarket
function atlasMarket(){
 const m=db.industry.market,t=m.total;
 return `${atlasTitle(m.title,m.scope)}
 <section class="pan-market-total"><div><span class="atlas-eyebrow">整体市场</span><h3>${esc(t.label)}</h3><strong>${esc(t.value)}</strong><p>${esc(t.note)}</p></div><div class="pan-market-outline"><span>凉感床单与床笠</span><span>有填充凉感被</span><span>薄凉感毯</span><span>其他凉感床品</span></div>${atlasDisclosure('范围、来源与核查结果',`<p>${esc(t.period)}。${esc(t.detail)}</p>${atlasSources(t.source_keys)}`)}</section>
 ${atlasTitle('细分品类规模')}
 <div class="pan-table-wrap"><table class="pan-table pan-market-table"><thead><tr><th>品类</th><th>市场规模</th><th>年份与数据性质</th><th>占整体比例</th></tr></thead><tbody>${m.segments.map(s=>`<tr><th>${s.id==='adjacent'?esc(s.name):atlasLink('#industry/products/'+s.id,s.name)}<small>${esc(s.definition)}</small></th><td><strong>${esc(s.value)}</strong></td><td>${esc(s.period)}<small>${esc(s.kind)}</small></td><td>${esc(s.share)}${atlasDisclosure('查看依据',`<p>${esc(s.detail)}</p>${atlasSources(s.source_keys)}`)}</td></tr>`).join('')}</tbody></table></div>
 <p class="atlas-note">${esc(m.share_note)} ${esc(m.adjacent_note)}</p>
 ${atlasDisclosure('估算差异与未采用的数据',`<p>${esc(m.scope_detail)}</p>${m.excluded.map(x=>`<p>${esc(x.reason)}</p>${atlasSources([x.source_key])}`).join('')}`)}`;
}

// REPLACE atlasProductRows
function atlasProductRows(filter='all',ids=null){
 const items=ids?ids.map(atlasProduct):db.industry.products.filter(p=>filter==='all'||p.category===filter);
 return `<div class="atlas-product-table"><div class="atlas-product-head"><span>产品与材料路线</span><span>商家主推的购买理由</span><span>价格与规格</span><span>销售记录 / 在售渠道</span></div>${items.map(p=>`<article class="atlas-product-row" data-product-row="${esc(p.id)}"><div class="atlas-product-main"><div class="atlas-product-name">${atlasPhoto(p)}<div>${atlasLink(p.url,p.name)}<span class="atlas-route">${esc(p.route)}</span></div></div><div class="atlas-buy-reason"><span class="atlas-mobile-label">商家主推购买理由</span><b>${esc(p.merchant_reason)}</b><small>${esc(p.claim_structure)}</small></div><div class="atlas-price-cell">${atlasMoney(p)}</div><div class="atlas-sales"><b>${esc(p.sales)}</b><span>${esc(p.verified_channel)}</span></div></div>${atlasDisclosure('材料、认知证据与来源',atlasProductDetail(p),'atlas-row-detail')}</article>`).join('')}</div>`;
}

// REPLACE atlasProducts
function atlasProducts(print=false){
 const d=db.industry.product_view,categories=d.categories.filter(c=>print||atlasFilter==='all'||c.id===atlasFilter);
 return `${atlasTitle(d.title,d.intro,db.industry.products.length+'款代表产品')}
 <div class="atlas-filter-bar">${d.filters.map(f=>`<button data-atlas-filter="${f.id}" class="${atlasFilter===f.id?'selected':''}">${esc(f.label)} <span>${f.id==='all'?db.industry.products.length:db.industry.products.filter(p=>p.category===f.id).length}</span></button>`).join('')}</div>
 <div id="atlas-product-results">${categories.map(cat=>`<section class="pan-category-section" data-category="${cat.id}"><div class="pan-category-heading"><h3>${esc(cat.name)}</h3><p>${esc(cat.summary)}</p></div>${cat.groups.map(g=>`<div class="pan-product-subgroup"><h4>${esc(g.name)}</h4>${atlasProductRows('all',g.product_ids)}</div>`).join('')}${cat.growth_ids.length?`<div class="pan-category-growth" id="growth-${cat.id}"><h4>增长案例</h4>${cat.growth_ids.map((id,i)=>atlasGrowthCase(db.industry.growth.cards.find(c=>c.id===id),i)).join('')}</div>`:''}</section>`).join('')}</div>
 <p class="atlas-note">${esc(d.note)}</p>${atlasDisclosure('近期增长产品的收录标准',`<p>${esc(db.industry.growth.pending_text)}</p><div class="atlas-chips">${db.industry.growth.required_fields.map(x=>`<span>${esc(x)}</span>`).join('')}</div>`)}`;
}

// REPLACE atlasGrowthCase
function atlasGrowthCase(c,index){
 return `<article class="atlas-growth-case pan-growth-case" data-growth-case="${esc(c.id)}"><h3>${esc(c.name)}</h3>
 <div class="atlas-growth-top">${c.metrics.map(m=>`<div><strong>${esc(m.value)}<span>${esc(m.unit)}</span></strong><p>${esc(m.label)}</p></div>`).join('')}</div>
 <div class="pan-growth-actions">${c.sections.map(s=>`<div><b>${esc(s.title)}</b><p>${esc(s.text)}</p></div>`).join('')}</div>
 <p class="pan-growth-judgment">${esc(c.interpretation)}</p><div class="pan-growth-links">${c.product_ids.map(id=>atlasLink(atlasProduct(id).url,atlasProduct(id).name)).join('')}</div>
 ${atlasDisclosure('案例来源与统计范围',`<p>${esc(c.scope)}；${esc(c.period)}。</p><p>${esc(c.caveat)}</p>${atlasSources([...c.source_keys,...c.sections.flatMap(s=>s.source_keys)])}`)}</article>`;
}

// REPLACE atlasMaterials
function atlasMaterials(){
 const d=db.industry.materials,share=d.share_chart;
 return `${atlasTitle(d.title,d.intro)}<div class="atlas-mechanisms">${d.mechanisms.map((m,i)=>`<article><div class="atlas-mechanism-icon">${['↘','↑','⇄'][i]}</div><div><h3>${esc(m.name)}</h3><p>${esc(m.text)}</p><small>${esc(m.metric)}</small>${atlasSources(m.source_keys)}</div></article>`).join('')}</div>
 <div class="atlas-material-table"><table><thead><tr><th>材料 / 技术</th><th>用途与价值表达</th><th>代表产品</th><th>应用边界</th></tr></thead><tbody>${d.rows.map(r=>`<tr><th scope="row">${esc(r.name)}<small class="${r.kind==='研发参考路线'?'atlas-research-kind':''}">${esc(r.kind)}</small></th><td><b>${esc(r.use)}</b><p>${esc(r.value)}</p></td><td>${r.example_ids.map(id=>{let p=atlasProduct(id);return atlasLink(p.url,p.name)}).join('<br>')||'<span class="atlas-note">具体商业产品待补</span>'}</td><td>${esc(r.tradeoff)}${atlasSources(r.source_keys)}</td></tr>`).join('')}</tbody></table></div>
 <div class="atlas-term-strip"><span>常用概念</span>${['bamboo-rayon','tencel','percale','qmax','jis-l1927','pcm'].map(atlasTerm).join('')}</div>
 <div class="atlas-panel atlas-share">${atlasTitle(share.title,share.scope)}<div class="atlas-stacked" role="img" aria-label="全球凉感床单材料结构模型估算，莱赛尔相关34%，其余66%">${share.values.map((x,i)=>`<div class="share-${i}" style="width:${x.value}%"><b>${x.value}%</b><span>${esc(x.label)}</span></div>`).join('')}</div><p class="atlas-note">${esc(share.note)}</p>${atlasSources(share.source_keys)}</div>
 <div class="atlas-note-box"><p>${esc(d.measurement_note)}</p>${atlasSources(d.measurement_sources)}</div>${atlasDisclosure('材料、商标与测试指标的区别',d.terms.map(t=>`<p><b>${esc(t.term)}</b>：${esc(t.meaning)}</p>${atlasSources(t.source_keys)}`).join(''))}`;
}

// REPLACE atlasNeeds
function atlasNeeds(print=false){
 const n=db.industry.needs,scope=location.hash.split('/')[2]||'all',models=print?n.models:n.models.filter(m=>m.id===(n.models.some(x=>x.id===scope)?scope:'all'));
 return `${atlasTitle(n.title,n.subtitle)}${print?'':panScopeNav('needs',n.models.map(m=>({id:m.id,label:m.name})),scope)}
 ${models.map(model=>panNeedModel(model)).join('')}
 ${atlasDisclosure('全部具体需求与原始依据',`<div class="atlas-need-list">${atlasNeedsList()}</div>`,'pan-all-needs')}
 ${atlasDisclosure('需求金字塔的判断标准与样本范围',`<p>${esc(n.model_note)}</p><p>${esc(n.sample_note)}</p>${n.pyramid.method_checks.map(c=>`<p><b>${esc(c.label)}</b>：${esc(c.text)}</p>`).join('')}${atlasSources(n.principle_sources)}`)}
 ${atlasDisclosure('美国一般床品调查：补充参考',`<p>${esc(n.survey.scope)}</p><div class="atlas-bars">${n.survey.items.map(x=>`<div class="atlas-bar-row"><span>${esc(x.label)}</span><div class="atlas-bar-track"><i style="width:${x.value}%"></i></div><b>${x.value}%</b></div>`).join('')}</div><p class="atlas-note">${esc(n.survey.note)} 比例不代表凉感床品需求份额或金字塔层级。</p>${atlasSources(n.survey.source_keys)}`)}`;
}
function panScopeNav(page,scopes,selected){return `<nav class="pan-scope-nav" aria-label="研究范围">${scopes.map(s=>`<a href="#industry/${page}/${s.id}" class="${s.id===selected?'selected':''}" ${s.id===selected?'aria-current="page"':''}>${esc(s.label)}</a>`).join('')}</nav>`;}
function panNeedModel(m){
 const p=m.pyramid;
 return `<section class="pan-need-model" data-need-scope="${m.id}"><div class="pan-need-heading"><h3>${esc(m.name)}</h3><p>${esc(m.summary)}</p></div>
 <div class="pan-need-goal"><span>消费者要解决的问题</span><strong>${esc(m.job)}</strong></div>
 <div class="pan-pyramid-panel"><div class="pan-pyramid-side"><h4>需求金字塔 · 局部关系</h4><span class="atlas-tag">${esc(p.status)}</span><p>${esc(p.scenario)}</p><small>下方是使用前提，上方是进一步要求。其他独立需求列在图下。</small></div>
 <div class="pan-pyramid" role="group" aria-label="${esc(m.name)}需求层级">${[...p.levels].reverse().map((level,i)=>`<div class="pan-pyramid-level" style="--level-width:${72+i/(Math.max(p.levels.length-1,1))*28}%"><strong>${esc(level.label)}</strong><div>${level.need_ids.map(id=>`<button data-atlas-need="${id}">${esc(db.industry.needs.need_pool.find(n=>n.id===id).need)}</button>`).join('')}</div></div>`).join('')}<span class="pan-pyramid-direction">前提关系 ↑</span></div>
 ${atlasDisclosure('关系依据与反例',`<p>${esc(p.link_note)}</p>${atlasReviewButtons(p.review_ids)}${atlasSources(p.source_keys)}`)}</div>
 <div class="pan-need-clusters">${m.clusters.map(c=>`<section><h4>${esc(c.title)}</h4><ul>${c.items.map(x=>`<li><button data-atlas-need="${x.need_id}">${esc(x.text)}<span>↗</span></button></li>`).join('')}</ul></section>`).join('')}</div><p class="atlas-note">${esc(m.independent_note)}</p>
 <div class="pan-model-foot">${atlasSources(m.source_keys)}${atlasLink('#industry/mindmap/'+m.id,'查看对应心智地图')}</div></section>`;
}

// REPLACE atlasMap
function atlasMap(print=false){
 const m=db.industry.mindmap,selected=location.hash.split('/')[2]||'all',scopes=print?m.scopes:m.scopes.filter(s=>s.id===(m.scopes.some(x=>x.id===selected)?selected:'all'));
 return `${atlasTitle(m.title,m.subtitle,m.status)}${print?'':panScopeNav('mindmap',m.scopes,selected)}
 <div class="atlas-map-legend">${m.legend.map(x=>`<span><i class="${x.style}"></i>${esc(x.label)}</span>`).join('')}<small>不代表品牌心智排名</small></div>
 ${scopes.map(scope=>`<section class="pan-map-scope" data-map-scope="${scope.id}"><div class="pan-need-heading"><h3>${esc(scope.title)}</h3><p>${esc(scope.summary)}</p></div><div class="atlas-map-labels"><span>需求入口</span><span>品类及替代选择</span><span>品牌关联 · 可点击查看</span></div><div class="atlas-mindmap">${m.lanes.filter(l=>l.scope===scope.id).map((l,i)=>`<article class="atlas-map-lane"><div class="atlas-map-entry"><span class="atlas-lane-num">0${i+1}</span><h3>${esc(l.entry)}</h3></div><div class="atlas-map-choice"><strong>${esc(l.category)}</strong><small>替代选择：${esc(l.alternatives.join('、'))}</small></div><div class="atlas-map-brands">${l.brands.map(b=>`<button class="atlas-brand-node ${b.evidence}" data-atlas-brand="${b.product_id}" data-atlas-lane="${l.id}"><b>${esc(atlasBrand(atlasProduct(b.product_id)))}</b><span>${esc(b.concept)}</span></button>`).join('')}</div><div class="atlas-lane-evidence">${atlasDisclosure('认知依据',`<p>${esc(l.known)}</p><p>${esc(l.unknown)}</p><p>${l.need_ids.map(id=>`<button class="atlas-text-button" data-atlas-need="${id}">${esc(db.industry.needs.need_pool.find(n=>n.id===id).need)} ↗</button>`).join('')}</p>${atlasSources(l.source_keys)}`)}</div></article>`).join('')}</div><div class="pan-model-foot">${atlasLink('#industry/needs/'+scope.id,'查看对应需求研究')}</div></section>`).join('')}
 ${atlasTitle(m.opportunities_title)}<div class="atlas-two-cols">${m.opportunities.filter(o=>print||scopes[0].id==='all'||o.scope===scopes[0].id).map(o=>`<article class="atlas-opportunity"><h3>${esc(o.title)}</h3><p>${esc(o.basis)}</p><small>${esc(o.boundary)}</small>${atlasSources(o.source_keys)}</article>`).join('')}</div>
 ${atlasDisclosure('定位方法与证据边界',`<p>${esc(m.method)}</p><p>${esc(m.validation_needed)}</p>${atlasSources(m.method_sources)}`)}`;
}

// REPLACE industryPage
function industryPage(){
 const d=db.industry;if(!d||d.schema_version!==2||d.layout_version!==3)return '<p>行业全景内容需要更新，请重新载入资料库。</p>';
 const parts=location.hash.split('/');let page=parts[1]||'market';
 if(page==='growth'){history.replaceState(null,'','#industry/products/covers');page='products';atlasFilter='covers';}
 else if(['sheets','covers','blankets'].includes(page)){atlasFilter=page;page='products';}
 else if(page==='products')atlasFilter=d.product_view.filters.some(f=>f.id===parts[2])?parts[2]:'all';
 if(!['print',...d.sections.map(x=>x.id)].includes(page))page='market';
 const print=page==='print',fn={market:atlasMarket,products:atlasProducts,materials:atlasMaterials,needs:atlasNeeds,mindmap:atlasMap};
 document.body.classList.toggle('atlas-print-view',print);
 return `<div class="atlas atlas-v3"><div class="atlas-header"><div><span class="atlas-eyebrow">行业基础 <span>/</span> 美国市场</span><h1>${esc(d.title)}</h1><p>${esc(d.subtitle)}</p></div><div class="atlas-actions">${print?'<button id="atlas-print-now">打印 / 保存PDF</button><a href="#industry/market">返回浏览</a>':'<a class="atlas-action-link" href="#industry/print">汇报打印版 ↗</a><button id="atlas-add-top">＋ 添加资料</button>'}</div></div>
 <nav class="atlas-tabs" aria-label="行业基础板块">${d.sections.map((s,i)=>`<a href="#industry/${s.id}" class="${page===s.id?'active':''}" ${page===s.id?'aria-current="page"':''}><span>0${i+1}</span>${esc(s.title)}</a>`).join('')}</nav>
 ${print?d.sections.map(s=>`<section class="atlas-print-section" id="atlas-section-${s.id}">${fn[s.id](true)}</section>`).join('')+atlasAppendix():`<div class="atlas-content">${fn[page]()}</div>`}${print?'':atlasWorkbench()}<div class="atlas-footer"><span>Breescape 竞争资料库 · 行业基础</span><span>资料核对：${esc(d.reviewed_at)}</span></div></div>`;
}
