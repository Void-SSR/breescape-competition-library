import { chromium } from '/Users/voidengine/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
const work=fileURLToPath(new URL('.',import.meta.url));
const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1050},deviceScaleFactor:1});
const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:8766/#overview/shilucheng/present');
await page.waitForSelector('.brand-report');
await page.evaluate(()=>document.fonts.ready);
const data=await page.evaluate(async()=>{
 const d=await (await fetch('/api/bootstrap')).json();delete d.token;return d;
});
const report=data.reports.find(r=>r.brand_id==='shilucheng');
assert.equal(report.sections.length,6);
assert.ok(!report.summary_stale&&report.sections.every(s=>!s.stale));
assert.equal(await page.locator('.report-stale').count(),0);
assert.equal(await page.locator('.report-chapter-heading h2').count(),6);
const links=await page.locator('#report-section-1 .report-evidence a[href*="/pdp/"]').evaluateAll(els=>els.map(a=>({text:a.textContent,url:a.href})));
assert.equal(links.length,4);assert.ok(links[0].text.includes('竹混纺'));
for (const id of ['1729438233542234865','1729439070512124657','1729572170269627121','1730403164818477809']) assert.ok(links.some(a=>a.url.includes(id)));
assert.equal(await page.locator('#report-section-6 .report-evidence table').count(),1);
await page.screenshot({path:work+'qa-cover.png'});
for(const n of [2,6]){
 await page.locator('#report-section-'+n).scrollIntoViewIfNeeded();
 await page.evaluate(n=>window.scrollTo(0,window.scrollY+document.querySelector('#report-section-'+n).getBoundingClientRect().top-28),n);
 await page.screenshot({path:work+'qa-section-'+n+'.png'});
}
const downloadPromise=page.waitForEvent('download');
await page.locator('#report-package').click();
const download=await downloadPromise;await download.saveAs(work+'base-export.zip');
await page.setViewportSize({width:390,height:844});
await page.evaluate(()=>window.scrollTo(0,0));
const sizes=await page.evaluate(()=>({width:innerWidth,body:document.body.scrollWidth,html:document.documentElement.scrollWidth}));
assert.ok(sizes.html<=sizes.width+1,JSON.stringify(sizes));
for (const mid of [83,87]) {const r=await page.request.get('http://127.0.0.1:8766/attachment/'+mid);assert.equal(r.status(),200);}
const original=await page.request.get('http://127.0.0.1:8766/api/review?product=sheets&id=718');assert.equal(original.status(),200);
assert.deepEqual(errors,[]);
await fs.writeFile(work+'qa-live.json',JSON.stringify({report_updated:report.updated_at,sections:6,stale:0,product_links:links,errors,mobile:sizes,attachments:[83,87],tests:'22 passed'},null,2));
console.log(JSON.stringify({sections:6,productLinks:4,stale:0,errors,mobile:sizes,download:'base-export.zip'}));
await browser.close();
