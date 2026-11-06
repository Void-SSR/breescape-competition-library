const {chromium}=require('/Users/voidengine/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path'),assert=require('assert');
const out=__dirname,base='http://127.0.0.1:8766/';
(async()=>{
 const b=await chromium.launch({headless:true});const p=await b.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
 const errors=[],result={routes:[],interactions:[],exports:[]};p.on('pageerror',e=>errors.push(e.message));
 const data=await(await p.request.get(base+'api/bootstrap')).json();
 const go=async hash=>{await p.goto(base+hash);await p.locator('.brand-report').waitFor();await p.waitForFunction(()=>document.fonts.status==='loaded');};
 const shot=async(sel,name)=>{await p.locator(sel).evaluate(el=>window.scrollTo(0,el.getBoundingClientRect().top+window.scrollY-22));await p.waitForTimeout(120);await p.locator(sel).evaluate(async el=>{await Promise.all([...el.querySelectorAll('img')].filter(x=>x.getBoundingClientRect().top<innerHeight).map(x=>x.decode().catch(()=>{})))});await p.screenshot({path:path.join(out,name+'.png')});};
 for(const bid of ['shilucheng','cozy-bliss','sheex']){
  await go('#overview/'+bid);const doc=data.reports.find(d=>d.brand_id===bid);const expected=doc.sections.flatMap(s=>s.topics.flatMap(t=>t.questions)).map(q=>q.id);
  const actual=await p.locator('.report-question').evaluateAll(es=>es.map(x=>x.id.replace('question-','')));assert.deepStrictEqual(actual,expected);
  assert.equal(await p.locator('.report-section').count(),6);assert.equal(await p.locator('.report-research-log[open]').count(),0);
  const broken=await p.locator('.brand-report a[href^="#question-"]').evaluateAll(es=>es.filter(a=>!document.getElementById(a.hash.slice(1))).map(a=>a.hash));assert.deepStrictEqual(broken,[]);
  result.routes.push({route:'#overview/'+bid,questions:actual.length,chapters:6,overflow:await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth)});
  await p.screenshot({path:path.join(out,bid+'-首页.png')});
  if(bid==='shilucheng'){
   for(let n=1;n<=6;n++)await shot('#report-section-'+n,'shilucheng-板块'+n);
   assert.equal(await p.locator('[data-brand-product="topper"] details').first().getAttribute('open'),null);
   await p.locator('[data-brand-product="topper"]>.brand-product-study>summary').click();assert(await p.locator('#question-shilucheng-topper-4-identity').isVisible());
   await shot('[data-brand-product="topper"]','topper-独立研究');
   await p.locator('#question-shilucheng-sheets-6-drivers [data-question-jump]').click();assert(await p.locator('#question-shilucheng-brand-8-samples').isVisible());result.interactions.push('销量驱动跳转对应视频');
   await p.locator('#question-shilucheng-sheets-4-difference [data-term="queen"]:visible').first().click();assert(await p.locator('.reading-dialog[open]').isVisible());await p.locator('.reading-dialog button').click();result.interactions.push('术语解释');
   await p.locator('#question-shilucheng-brand-8-samples a[data-library-video]').first().click();await p.locator('.reading-dialog video[src]').waitFor();result.interactions.push('关联视频加载');await p.locator('.reading-dialog button').click();
   await p.locator('#question-shilucheng-sheets-6-drivers').locator('xpath=..').locator('[data-open-evidence]').click();assert(await p.locator('.report-research-log[open]').count());result.interactions.push('来源查验展开');
   const downloadPromise=p.waitForEvent('download');await p.locator('#report-export').click();const dl=await downloadPromise;const name=path.join(out,'Shilucheng品牌总览.html');await dl.saveAs(name);result.exports.push({file:name,bytes:fs.statSync(name).size});
   const packPromise=p.waitForEvent('download');await p.locator('#report-package').click();const pack=await packPromise;const zip=path.join(out,'Shilucheng报告与证据.zip');await pack.saveAs(zip);result.exports.push({file:zip,bytes:fs.statSync(zip).size});
  }
 }
 for(const pid of ['sheets','topper','cozy-comforter','sheex-sheets']){
  await go('#product-report/'+pid);assert.equal(await p.locator('[data-report-product]').getAttribute('data-report-product'),pid);
  const questions=await p.locator('.product-chapter .report-question').evaluateAll(es=>es.map(e=>e.id));assert(questions.every(x=>x.includes('-'+pid+'-')));
  result.routes.push({route:'#product-report/'+pid,coreQuestions:questions.length,overflow:await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth)});
  await p.screenshot({path:path.join(out,pid+'-产品首页.png')});
 }
 await go('#overview/shilucheng/present');assert(await p.locator('body.presenting').count());await shot('#report-section-1','汇报视图-事实字段');
 await shot('#question-shilucheng-sheets-5-overview','汇报视图-评论总览');await shot('#question-shilucheng-sheets-6-drivers','汇报视图-销量驱动');
 result.interactions.push('汇报视图');
 await p.setViewportSize({width:390,height:844});await go('#overview/shilucheng');assert(!(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth)));
 await shot('#report-section-1','手机-事实字段');await shot('#question-shilucheng-sheets-6-drivers','手机-销量驱动');
 result.routes.push({route:'390px/overview/shilucheng',overflow:false});
 const offline=await b.newPage({viewport:{width:1440,height:1000}});offline.on('pageerror',e=>errors.push(e.message));
 await offline.goto('file://'+path.join(out,'Shilucheng品牌总览.html'));assert.equal(await offline.locator('.report-question').count(),58);assert.equal(await offline.locator('.brand-product-study[open]').count(),2);await offline.locator('.report-question [data-term]:visible').first().click();assert(await offline.locator('.reading-dialog[open]').count());await offline.locator('.reading-dialog button').click();result.interactions.push('离线报告包含两款产品及术语解释');
 await offline.evaluate(async()=>Promise.all([...document.images].map(i=>i.decode().catch(()=>{}))));await offline.pdf({path:path.join(out,'Shilucheng品牌总览.pdf'),format:'A4',printBackground:true,margin:{top:'12mm',right:'10mm',bottom:'12mm',left:'10mm'}});result.interactions.push('完整报告打印');
 result.errors=errors;assert.deepStrictEqual(errors,[]);fs.writeFileSync(path.join(out,'浏览器核验结果.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));await b.close();
})().catch(e=>{console.error(e);process.exit(1)});
