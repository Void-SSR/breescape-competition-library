function featuredEvidence(f){
 const r=db.records.find(x=>x.id===f.record_id);if(!r)return '';
 const analysis=f.mode==='analysis'&&r.kind==='分析'&&['研究草稿','已复核'].includes(r.status)&&JSON.parse(r.evidence||'[]').length;
 if(!analysis&&!factualRecord(r))return `<p class="report-stale">引用「${esc(r.title)}」需复核。</p>`;
 const blocks=r.body.split(/\n\s*\n/);let body=(f.mode==='table'||analysis)?blocks.filter(b=>b.trim().startsWith('|')).join('\n\n'):blocks.find(b=>!b.trim().startsWith('|'));
 if(body&&f.columns?.length)body=body.split('\n').map(line=>line.trim().startsWith('|')?'| '+f.columns.map(i=>line.trim().replace(/^\||\|$/g,'').split('|')[i]?.trim()||'').join(' | ')+' |':line).join('\n');
 const caption=f.caption||r.title;
 const content=body?`<div class="report-evidence"><div class="evidence-caption">${esc(caption)}</div>${formatBody(body,r.product_id,{comparison:f.layout==='comparison'})}</div>`:'';
 return f.purpose==='support'&&content?`<details class="report-support"><summary>${esc(caption)}</summary>${content}</details>`:content;
}
function feedbackOverview(t){
 const f=t.feedback?.summary;if(!f)return '';
 return `<div class="feedback-overview"><div><span>含认可反馈</span><strong>${f.positive_percent}%</strong><small>${f.positive} 条评论</small></div><div><span>含不认可反馈</span><strong>${f.negative_percent}%</strong><small>${f.negative} 条评论</small></div></div><p class="feedback-overlap">其中 ${f.mixed} 条有赞有贬，已同时计入两类；另有 ${f.unclassified} 条未作正负判断。</p>`;
}
function feedbackList(t,valence){
 const rows=t.feedback?.rows.filter(r=>r.valence===valence)||[],positive=valence==='positive',label=positive?'认可':'不认可';
 const table=items=>`<div class="table-wrap feedback-table"><table><thead><tr><th scope="col">${label}的内容</th><th scope="col">评论数</th><th scope="col">占${label}反馈</th></tr></thead><tbody>${items.map(r=>`<tr data-feedback-code="${r.code}" data-feedback-valence="${valence}"><th scope="row">${r.rank&&r.rank<=3?`<span class="feedback-rank">TOP ${r.rank}</span>`:''}${esc(r.label)}</th><td>${r.count}</td><td>${r.percent_group.toFixed(1)}%</td></tr>`).join('')}</tbody></table></div>`;
 const concrete=rows.filter(r=>!r.general),general=rows.filter(r=>r.general);
 return `<div class="feedback-list ${positive?'positive':'negative'}">${table(concrete)}${general.length?`<div class="feedback-general"><h5>未细分具体原因的一般评价</h5>${table(general)}</div>`:''}<p class="feedback-table-note">占比以 ${positive?t.feedback.summary.positive:t.feedback.summary.negative} 条含${label}反馈的评论为分母；同一条可以提到多个方面，各项不相加。</p></div>`;
}
function reportQuestion(q,t){
 const inline=value=>bodyInline(value,t.product_id),points=q.points||[];
 const list=points.length?`<${q.ordered?'ol':'ul'} class="report-findings ${q.ordered?'ranked':'unranked'}">${points.map(p=>`<li><div><p class="finding-title">${inline(p.title)}</p>${p.detail?`<p class="finding-detail">${inline(p.detail)}</p>`:''}${p.evidence?`<p class="finding-evidence">${inline(p.evidence)}</p>`:''}</div></li>`).join('')}</${q.ordered?'ol':'ul'}>`:'';
 const specialized=q.type==='feedback-summary'?feedbackOverview(t):q.type==='feedback-positive'?feedbackList(t,'positive'):q.type==='feedback-negative'?feedbackList(t,'negative'):'';
 return `<section class="report-question ${q.type?.startsWith('feedback-')?'feedback-question':''}" id="question-${esc(q.id)}"><h4>${esc(q.title)}</h4>${q.answer?`<p class="question-answer">${inline(q.answer)}</p>`:''}${q.type==='feedback-summary'?specialized:''}${list}${q.evidence?`<p class="finding-evidence">${inline(q.evidence)}</p>`:''}${q.type!=='feedback-summary'?specialized:''}${(q.figures||[]).map(f=>reportFigure(f)).join('')}${(q.tables||[]).map(featuredEvidence).join('')}${q.note?`<p class="question-note">${inline(q.note)}</p>`:''}${q.links?.length?`<p class="question-related">${q.links.map(l=>`<a href="#question-${esc(l.target)}" data-question-jump="question-${esc(l.target)}">${esc(l.label)} →</a>`).join('')}</p>`:''}</section>`;
}
function feedbackMethod(t){
 if(!t.feedback)return '';
 return `<details class="feedback-method"><summary>统计方法与完整明细</summary><p>统计对象为2026年9月24日至11月4日的928条近期全星级评论；额外687条一星与13条推荐展示样本不混入比例。非随机样本，比例不代表全部买家的满意率。</p><p>正负按文字内容和对象判断，不由星级替代。${t.feedback.summary.positive_only}条仅有认可，${t.feedback.summary.negative_only}条仅有不认可，${t.feedback.summary.mixed}条有赞有贬，${t.feedback.summary.unclassified}条未判定。TOP3按具体反馈提及数标注，一般性“喜欢”“质量好”等单列。</p><p>温度认可176条含172条凉感／少热少汗、2条保暖、2条未细分调温；温度不满72条含71条不够凉／偏热等、1条不够暖。尺寸不满与滑脱接近，排名不代表问题严重程度。</p><p>本轮补计R352明确不愿再买的总体不满、R692赠品规格不适用的履约不满；不把含糊的“balled up”认定为起球，也不把赠品错发算作床单尺寸缺陷。原v1.2分项编码与原始评论保留。</p><p><a href="/attachment/${t.feedback.material_id}">下载完整分项、两种分母及对应原评论编号</a> · <a href="/attachment/${t.feedback.method_material_id}">查看计算与补判记录</a></p></details>`;
}
function reportTopic(t,n){
 const pending=t.answer_type==='研究问题'||(!t.finding&&!t.questions?.length);
 if(t.questions?.length)return `<article id="${topicAnchor(t,n)}" class="report-topic question-led ${t.feedback?'report-voc':''}"><h3>${esc(t.topic)}</h3>${t.finding?`<p class="topic-finding">${esc(t.finding)}</p>`:''}${t.questions.map(q=>reportQuestion(q,t)).join('')}${feedbackMethod(t)}<a class="report-evidence-ref" href="#audit-${topicAnchor(t,n)}" data-open-evidence="audit-${topicAnchor(t,n)}">查看本项来源与研究记录</a></article>`;
 const bullets=items=>items?.length?`<ul class="report-key-facts">${items.map(b=>`<li>${reviewInline(b,t.product_id)}</li>`).join('')}</ul>`:'';
 return `<article id="${topicAnchor(t,n)}" class="report-topic ${pending?'unwritten':''}"><h3>${esc(t.topic)}</h3><p class="topic-finding">${esc(t.finding||'尚未开展该问题研究。')}</p>${bullets(t.bullets||[])}${(t.figures||[]).map(f=>reportFigure(f)).join('')}${(t.featured||[]).map(featuredEvidence).join('')}<a class="report-evidence-ref" href="#audit-${topicAnchor(t,n)}" data-open-evidence="audit-${topicAnchor(t,n)}">查看本项依据</a></article>`;
}
