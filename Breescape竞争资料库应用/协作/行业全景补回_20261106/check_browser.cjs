const {chromium}=require('/Users/voidengine/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');const path=require('path');const assert=require('assert');
(async()=>{
 const browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1500,height:1050}});const errors=[];const results=[];
 page.on('pageerror',e=>errors.push(e.message));
 const root='http://127.0.0.1:8766/';
 async function go(route){await page.goto(root+'#industry/'+route);await page.locator('.atlas-v3').waitFor();}
 await go('market');assert.strictEqual(await page.locator('h1').innerText(),'凉感床品行业全景');assert.strictEqual(await page.locator('.atlas-tabs a').count(),5);assert.strictEqual(await page.locator('.pan-market-total').count(),1);assert.strictEqual(await page.locator('.pan-market-table tbody tr').count(),4);assert.strictEqual(await page.locator('.atlas-share').count(),0);results.push('原行业入口：五板块、总体在前、四类规模、无材料占比');
 await page.locator('a[href="#industry/products/sheets"]').first().click();await page.locator('[data-category="sheets"]').waitFor();assert.strictEqual(await page.locator('[data-product-row]').count(),7);assert.strictEqual(await page.locator('[data-growth-case]').count(),0);
 await page.locator('[data-atlas-filter="covers"]').click();await page.locator('[data-category="covers"]').waitFor();assert.strictEqual(await page.locator('[data-product-row]').count(),3);assert.strictEqual(await page.locator('[data-growth-case]').count(),1);
 await page.locator('[data-atlas-filter="all"]').click();await page.locator('[data-product-row]').nth(10).waitFor();assert.strictEqual(await page.locator('[data-category]').count(),3);assert.strictEqual(await page.locator('[data-growth-case]').count(),1);results.push('产品分类与筛选：7款床单、3款凉感被、1款薄毯；REST案例只归属凉感被');
 await go('growth');assert.strictEqual(new URL(page.url()).hash,'#industry/products/covers');assert.strictEqual(await page.locator('[data-growth-case]').count(),1);results.push('旧增长入口：转入凉感被品类');
 await go('materials');assert.strictEqual(await page.locator('.atlas-share').count(),1);assert.strictEqual(await page.locator('.atlas-material-table tbody tr').count(),8);await page.locator('[data-atlas-term="qmax"]').click();await page.locator('#modal[open]').waitFor();assert.match(await page.locator('#modal').innerText(),/热流/);await page.locator('#cancel').click();results.push('材料页：8条路线、材料结构、术语弹窗');
 for(const scope of ['all','covers','sheets']){
  await go('needs/'+scope);assert.strictEqual(await page.locator('[data-need-scope="'+scope+'"]').count(),1);await page.locator('a[href="#industry/mindmap/'+scope+'"]').click();await page.locator('[data-map-scope="'+scope+'"]').waitFor();
  await page.locator('[data-atlas-brand]').first().click();await page.locator('#modal[open]').waitFor();assert(await page.locator('#modal a[target="_blank"]').count()>0);await page.locator('#cancel').click();
  await page.locator('a[href="#industry/needs/'+scope+'"]').click();await page.locator('[data-need-scope="'+scope+'"]').waitFor();
 }
 await go('needs/sheets');await page.locator('[data-atlas-need="n1"]').first().click();await page.locator('#modal[open]').waitFor();await page.locator('#modal [data-atlas-review="619"]').click();await page.waitForFunction(()=>document.querySelector('#modal')?.innerText.includes('sand paper'));await page.locator('#cancel').click();results.push('三种需求与心智范围互跳；品牌详情及R619原评论可打开');
 await go('print');assert.strictEqual(await page.locator('.atlas-print-section').count(),5);assert.strictEqual(await page.locator('[data-need-scope]').count(),3);assert.strictEqual(await page.locator('[data-map-scope]').count(),3);assert.strictEqual(await page.locator('[data-product-row]').count(),11);assert.strictEqual(await page.locator('[data-growth-case]').count(),1);
 await page.locator('.atlas img').evaluateAll(a=>a.forEach(i=>i.loading='eager'));await page.waitForTimeout(4000);
 await page.pdf({path:path.join(__dirname,'行业全景_验收打印.pdf'),format:'A4',printBackground:true,preferCSSPageSize:true});results.push('打印版：五板块、11款产品、三种需求范围、三种心智范围齐全');
 for(const width of [1500,1024,768,390]){
  await page.setViewportSize({width,height:1000});await go('needs/covers');assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
 }
 results.push('需求页在1500、1024、768、390宽度无整页横向溢出');
 await page.setViewportSize({width:1500,height:1050});
 for(const [route,name] of [['market','market'],['products/covers','covers'],['materials','materials'],['needs/all','needs_all'],['needs/covers','needs_covers'],['needs/sheets','needs_sheets'],['mindmap/all','mindmap_all'],['mindmap/covers','mindmap_covers'],['mindmap/sheets','mindmap_sheets']]){
  await go(route);await page.locator('.atlas img').evaluateAll(a=>a.forEach(i=>i.loading='eager'));if(route.startsWith('products'))await page.waitForTimeout(4000);await page.screenshot({path:path.join(__dirname,name+'.png'),fullPage:true});
 }
 assert.deepStrictEqual(errors,[]);fs.writeFileSync(path.join(__dirname,'浏览器验收.json'),JSON.stringify({results,errors},null,2));console.log(JSON.stringify({results,errors},null,2));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
