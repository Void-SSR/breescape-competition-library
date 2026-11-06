(function(){
 const base='/breescape-competition-library/';let data;
 const realFetch=window.fetch.bind(window);
 const load=()=>data?Promise.resolve(data):realFetch(base+'snapshot.json').then(r=>{if(!r.ok)throw Error('无法读取公开资料');return r.json()}).then(x=>data=x);
 const response=(v,status=200)=>new Response(JSON.stringify(v),{status,headers:{'Content-Type':'application/json'}});
 function fix(u){let match=String(u).match(/(?:\/breescape-competition-library)?\/attachment\/(\d+)(?=$|[?#])/);return match&&data?.attachments[match[1]]?base+'attachment/'+data.attachments[match[1]]:u}
 window.fetch=async function(url,opts){const s=typeof url==='string'?url:url.url;if(s.includes('/attachment/')){await load();return realFetch(fix(s),opts)}if(!s.startsWith('/api/'))return realFetch(url,opts);if(opts?.method&&opts.method!=='GET')return response({error:'在线分享版为只读，不能修改或保存资料。'},403);const d=await load();let u=new URL(s,location.origin),q=u.searchParams;
 if(u.pathname==='/api/bootstrap')return response(d.snapshot);
 if(u.pathname==='/api/reviews'){let a=d.reviews.filter(r=>r.product_id===(q.get('product')||'sheets'));let query=(q.get('q')||'').toLowerCase();if(query)a=a.filter(r=>(r.body||'').toLowerCase().includes(query)||(r.sku||'').toLowerCase().includes(query));if(q.get('rating'))a=a.filter(r=>String(r.rating)===q.get('rating'));if(q.get('from'))a=a.filter(r=>r.date>=q.get('from'));if(q.get('to'))a=a.filter(r=>r.date<=q.get('to'));if(q.get('order')==='asc')a=[...a].sort((x,y)=>x.date.localeCompare(y.date)||x.id-y.id);let offset=+q.get('offset')||0;return response({total:a.length,items:a.slice(offset,offset+40)});}
 if(u.pathname==='/api/review'){let r=d.reviews.find(x=>x.product_id===q.get('product')&&String(x.id)===q.get('id'));return response(r||{error:'该产品下不存在此评论编号'},r?200:404)}
 return response({error:'该功能在只读分享版中不可用'},403);
 };
 const hide=/^(恢复研究原稿|撤回上次保存|编辑|编辑品牌速览|编辑本节|添加条目|新建产品|记录新数据|导入评论 CSV|收录新资料|添加材料|备份|关闭资料库|保存|导出报告|导出资料与研究记录|导出该产品评论|导出结构化资料)/;
 function refreshNodes(root){if(!data)return;for(const el of [root,...(root.querySelectorAll?.('[src],[href],button')||[])]){if(!el.getAttribute)continue;for(const attr of ['src','href']){let x=el.getAttribute(attr);if(x&&x.includes('/attachment/')){let y=fix(x);if(x!==y)el.setAttribute(attr,y)}if(x&&x.startsWith('/api/export'))el.style.display='none'}if(el.tagName==='BUTTON'&&hide.test(el.textContent.trim()))el.style.display='none';}}
 load().then(()=>{new MutationObserver(ms=>{for(const m of ms)for(const n of m.addedNodes)if(n.nodeType===1)refreshNodes(n)}).observe(document.documentElement,{childList:true,subtree:true});refreshNodes(document.documentElement)});
 document.addEventListener('click',e=>{const b=e.target.closest('button');if(b&&hide.test(b.textContent.trim())){e.preventDefault();e.stopImmediatePropagation();alert('在线分享版为只读快照，请在本地资料库编辑。')}},true);
})();
