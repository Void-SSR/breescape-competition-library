import {chromium} from '/Users/voidengine/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';import fs from 'node:fs/promises';import path from 'node:path';import {fileURLToPath,pathToFileURL} from 'node:url';
const dir=fileURLToPath(new URL('.',import.meta.url));const report=path.join(dir,'offline_check/Shilucheng_品牌研究总览_问题导向版_2026-11-05/报告.html');
const browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1400,height:1000}});let errors=[];page.on('pageerror',e=>errors.push(e.message));
try{
 await page.goto(pathToFileURL(report).href);assert.equal(await page.locator('.report-chapter-heading').count(),6);assert.equal(await page.locator('.report-question').count(),39);assert.equal(await page.locator('tr[data-feedback-code]').count(),83);await page.locator('#question-success-advantage .report-support>summary').click();assert.equal(await page.locator('#question-success-advantage .report-support').getAttribute('open'),'');await page.locator('[data-question-jump="question-product-comparison"]').click();assert.ok(Math.abs((await page.locator('#question-product-comparison').boundingBox()).y)<120);
 await page.locator('.report-topic [data-term=queen]').first().click();assert.match(await page.locator('.reading-dialog').innerText(),/双人床/);await page.keyboard.press('Escape');
 const missing=[];const refs=await page.locator('a[href]').evaluateAll(as=>as.map(a=>a.getAttribute('href')));
 for(const ref of new Set(refs)){if(/^(?:https?:|data:|#)/.test(ref))continue;const target=fileURLToPath(new URL(ref,pathToFileURL(report)));try{await fs.access(target);}catch{missing.push(ref);}}assert.deepEqual(missing,[]);
 const videos=[];for(let id=56;id<=60;id++){
  await page.locator(`.report-topic [data-library-video="${id}"]`).first().click();await page.waitForFunction(()=>document.querySelector('.reading-dialog video')?.readyState>=1);
  const result=await page.locator('.reading-dialog video').evaluate(async v=>{v.muted=true;await v.play();return {duration:v.duration,playing:!v.paused};});assert.equal(result.playing,true);videos.push({id,...result});await page.keyboard.press('Escape');await page.waitForFunction(()=>!document.querySelector('.reading-dialog').open&&!document.querySelector('.reading-dialog video')?.getAttribute('src'));
 }
 await page.locator('.report-topic a[href="#review-proof-718"]').first().click();assert.equal(await page.locator('#review-proof-718').getAttribute('open'),'');assert.equal(await page.locator('.report-review-appendix').getAttribute('open'),'');
 assert.deepEqual(errors,[]);await fs.writeFile(path.join(dir,'offline_result.json'),JSON.stringify({passed:true,missing_local_links:missing,page_errors:errors,videos},null,2));console.log(JSON.stringify({passed:true,local_links:new Set(refs).size,videos:videos.length}));
}finally{await browser.close();}
