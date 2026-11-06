'use strict';
let visualEditing=false,visualImage=null,visualRange=null,visualRoot=null;
const draftKey=()=> 'breescape-layout-'+reportBrand;
function bindVisualEditor(){
 const doc=db.reports.find(r=>r.brand_id===reportBrand),root=document.querySelector('.brand-report');if(!doc||!root)return;
 visualRoot=root;visualEditing=false;
 if(doc.manual_layout?.html)root.innerHTML=doc.manual_layout.html;
 const bar=document.querySelector('.report-toolbar .actions');
 bar.insertAdjacentHTML('afterbegin','<button id="visual-edit" class="primary">编辑总览</button>');
 document.getElementById('visual-edit').onclick=()=>startVisualEdit(doc);
 if(doc.manual_layout){bar.insertAdjacentHTML('beforeend','<button id="visual-reset">恢复研究原稿</button>');document.getElementById('visual-reset').onclick=async()=>{if(confirm('恢复研究原稿？当前排版会保留，可用“撤回上次保存”找回。'))await persistVisual('reset');};}
 if(doc.layout_history?.length){bar.insertAdjacentHTML('beforeend','<button id="visual-undo-save">撤回上次保存</button>');document.getElementById('visual-undo-save').onclick=()=>{if(confirm('恢复到上一次保存前的展示稿？'))persistVisual('undo');};}
 if(doc.manual_layout?.research_updated_at!==doc.updated_at&&doc.manual_layout)bar.insertAdjacentHTML('afterend','<p class="muted">研究内容有更新；当前展示的是你保存的编辑版，可恢复研究原稿后重新调整。</p>');
}
function startVisualEdit(doc){
 if(visualEditing)return;
 document.querySelectorAll('.report-toolbar button,.report-toolbar select').forEach(e=>e.disabled=true);
 visualEditing=true;visualImage=null;visualRange=null;
 const draft=localStorage.getItem(draftKey());if(draft&&confirm('发现未保存的编辑草稿，是否继续？'))visualRoot.innerHTML=draft;
 visualRoot.querySelectorAll('.brand-product-study').forEach(e=>e.open=true);
 visualRoot.contentEditable='true';visualRoot.classList.add('visual-editing');
 document.querySelector('.report-toolbar').insertAdjacentHTML('afterend',`<div class="visual-toolbar" contenteditable="false"><div class="visual-drag"><b>总览编辑</b><small>拖动移动</small></div><div class="visual-compact"><button data-panel="text" aria-expanded="false">文字</button><button data-panel="image" aria-expanded="false">图片</button><button id="visual-save" class="primary">保存</button><button id="visual-cancel">退出</button></div><div class="visual-panel" data-tools="text" hidden><button data-cmd="bold"><b>加粗</b></button><button data-cmd="italic"><i>斜体</i></button><button data-cmd="underline">下划线</button><button data-cmd="insertOrderedList">编号列表</button><button data-cmd="insertUnorderedList">项目列表</button><button data-cmd="justifyLeft">左对齐</button><button data-cmd="justifyCenter">居中</button><select id="visual-size" aria-label="字号"><option value="">字号</option><option value="3">正文</option><option value="4">小标题</option><option value="5">大标题</option><option value="2">小字说明</option></select><button data-cmd="removeFormat">清除格式</button><button data-cmd="undo">撤销</button><button data-cmd="redo">重做</button><button id="visual-link">添加链接</button></div><div class="visual-panel" data-tools="image" hidden><button id="visual-add-image">插入图片</button><button id="visual-image-url">引用网络图片</button><button id="visual-replace-image">替换选中图片</button><select id="visual-image-size" aria-label="图片宽度"><option value="">图片宽度</option><option value="30%">小</option><option value="60%">中</option><option value="100%">通栏</option></select><button id="visual-remove-image">删除选中图片</button><small>点击图片后调整；图片下方可输入说明。来源链接保留。</small><input type="file" id="visual-file" accept="image/png,image/jpeg,image/webp" hidden></div><span id="visual-status">点击正文编辑 · 草稿暂存本机</span></div>`);
 const toolbar=document.querySelector('.visual-toolbar');
 toolbar.querySelectorAll('[data-panel]').forEach(b=>{b.onmousedown=e=>e.preventDefault();b.onclick=()=>{const opening=b.getAttribute('aria-expanded')!=='true';toolbar.querySelectorAll('[data-panel]').forEach(x=>x.setAttribute('aria-expanded',String(opening&&x===b)));toolbar.querySelectorAll('[data-tools]').forEach(x=>x.hidden=!(opening&&x.dataset.tools===b.dataset.panel));};});
 const drag=toolbar.querySelector('.visual-drag');let move=null;
 drag.onpointerdown=e=>{if(e.button!==0)return;const r=toolbar.getBoundingClientRect();move={x:e.clientX-r.left,y:e.clientY-r.top};toolbar.style.left=r.left+'px';toolbar.style.top=r.top+'px';toolbar.style.right='auto';toolbar.style.bottom='auto';drag.setPointerCapture(e.pointerId);e.preventDefault();};
 drag.onpointermove=e=>{if(!move)return;toolbar.style.left=Math.max(8,Math.min(innerWidth-toolbar.offsetWidth-8,e.clientX-move.x))+'px';toolbar.style.top=Math.max(8,Math.min(innerHeight-toolbar.offsetHeight-8,e.clientY-move.y))+'px';};
 drag.onpointerup=()=>move=null;drag.onpointercancel=()=>move=null;

 const remember=()=>{let s=getSelection();if(s.rangeCount&&visualRoot.contains(s.anchorNode))visualRange=s.getRangeAt(0).cloneRange();};
 visualRoot.onkeyup=remember;visualRoot.onmouseup=remember;
 visualRoot.oninput=stashVisual;
 visualRoot.onclick=e=>{if(e.target.closest('a,button'))e.preventDefault();if(e.target.tagName==='IMG'){visualImage?.classList.remove('visual-selected');visualImage=e.target;visualImage.classList.add('visual-selected');}remember();};
 toolbar.querySelectorAll('[data-cmd]').forEach(b=>{b.onmousedown=e=>e.preventDefault();b.onclick=()=>{restoreVisualSelection();document.execCommand(b.dataset.cmd);stashVisual();};});
 document.getElementById('visual-size').onchange=e=>{restoreVisualSelection();document.execCommand('fontSize',false,e.target.value);stashVisual();};
 document.getElementById('visual-link').onclick=()=>{let u=prompt('输入完整网页链接（https://…）');if(!u)return;if(!/^https?:\/\//i.test(u)){toast('请输入 http 或 https 链接');return;}restoreVisualSelection();document.execCommand('createLink',false,u);stashVisual();};
 document.getElementById('visual-image-url').onclick=()=>{const u=prompt('粘贴图片的完整网址（https://…）');if(!u)return;if(!/^https?:\/\//i.test(u))return toast('请输入 http 或 https 图片链接');restoreVisualSelection();document.execCommand('insertHTML',false,'<figure><img src="'+esc(u)+'" alt="网络图片" style="width:60%;height:auto"><figcaption>图片说明</figcaption></figure><p><br></p>');stashVisual();};
 let replacing=false;const file=document.getElementById('visual-file');
 document.getElementById('visual-add-image').onclick=()=>{replacing=false;file.click();};
 document.getElementById('visual-replace-image').onclick=()=>{if(!visualImage)return toast('请先点击一张图片');replacing=true;file.click();};
 file.onchange=()=>{const f=file.files[0];if(!f)return;if(!['image/png','image/jpeg','image/webp'].includes(f.type)||f.size>4e6)return toast('请选择4MB以内的PNG、JPG或WebP图片');const reader=new FileReader();reader.onload=()=>{if(replacing&&visualImage){visualImage.src=reader.result;visualImage.alt=f.name;const a=visualImage.closest('a');if(a)a.replaceWith(visualImage);}else{restoreVisualSelection();document.execCommand('insertHTML',false,'<figure><img src="'+reader.result+'" alt="'+esc(f.name)+'" style="width:60%;height:auto"><figcaption>图片说明</figcaption></figure><p><br></p>');}stashVisual();file.value='';};reader.readAsDataURL(f);};
 document.getElementById('visual-image-size').onchange=e=>{if(!visualImage)return toast('请先点击一张图片');visualImage.style.width=e.target.value;visualImage.style.height='auto';stashVisual();};
 document.getElementById('visual-remove-image').onclick=()=>{if(!visualImage)return toast('请先点击一张图片');visualImage.remove();visualImage=null;stashVisual();};
 document.getElementById('visual-save').onclick=()=>persistVisual('save');
 document.getElementById('visual-cancel').onclick=()=>{if(confirm('放弃这次未保存的修改？')){visualEditing=false;localStorage.removeItem(draftKey());render();}};
 visualRoot.focus();
}
function restoreVisualSelection(){visualRoot.focus();if(visualRange&&visualRoot.contains(visualRange.commonAncestorContainer)){const s=getSelection();s.removeAllRanges();s.addRange(visualRange);}else{const r=document.createRange();r.selectNodeContents(visualRoot);r.collapse(false);getSelection().removeAllRanges();getSelection().addRange(r);}}
function visualHTML(){const clone=visualRoot.cloneNode(true);clone.querySelectorAll('.visual-selected').forEach(e=>e.classList.remove('visual-selected'));return clone.innerHTML;}
function stashVisual(){try{localStorage.setItem(draftKey(),visualHTML());document.getElementById('visual-status').textContent='草稿已暂存 · 尚未保存到总览';}catch(e){document.getElementById('visual-status').textContent='图片较大，请点击保存以免丢失';}}
async function persistVisual(action){try{const html=action==='save'?visualHTML():'';await api('/api/report-layout',{brand_id:reportBrand,action,html});visualEditing=false;localStorage.removeItem(draftKey());await refresh();render();toast('总览已保存');}catch(e){toast(e.message);}}
window.addEventListener('beforeunload',e=>{if(visualEditing){e.preventDefault();e.returnValue='';}});
document.addEventListener('click',e=>{if(!visualEditing)return;const a=e.target.closest('a');if(a&&!visualRoot.contains(a)&&!confirm('离开编辑？草稿已暂存在本机，但尚未保存到总览。')){e.preventDefault();e.stopImmediatePropagation();}},true);
