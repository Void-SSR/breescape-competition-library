import {chromium} from '/Users/voidengine/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const dir=fileURLToPath(new URL('.',import.meta.url));
const browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1500,height:1050},acceptDownloads:true});
const errors=[];page.on('pageerror',e=>errors.push(e.message));
try{
 await page.goto('http://127.0.0.1:8766/#overview/shilucheng');await page.locator('.brand-report h1').waitFor();
 assert.equal(await page.locator('.report-chapter-heading').count(),6);
 assert.equal(await page.locator('.report-stale').count(),0);
 const price=page.locator('.report-evidence').filter({hasText:'同款床单的尺寸与套装价格'}).first();
 assert.match(await price.innerText(),/单人床三件套/);assert.doesNotMatch(await price.innerText(),/Twin \/ 3PC/);
 const term=price.locator('[data-term=queen]').first();await term.click();assert.match(await page.locator('.reading-dialog').innerText(),/双人床/);await page.keyboard.press('Escape');assert.equal(await page.locator('.reading-dialog[open]').count(),0);
 await term.focus();await page.keyboard.press('Enter');assert.equal(await page.locator('.reading-dialog[open]').count(),1);await page.getByRole('button',{name:'关闭',exact:true}).click();
 const matrix=page.locator('.report-topic .comparison-table').first();assert.equal(await matrix.locator('thead th').count(),4);assert.equal(await matrix.locator('tbody tr').count(),8);assert.equal(await matrix.locator('thead a[href^="https://shop.tiktok.com/"]').count(),3);
 assert.match(await matrix.innerText(),/64.49／件数未核实/);await matrix.scrollIntoViewIfNeeded();await matrix.screenshot({path:path.join(dir,'竞争对照_桌面.png')});
 const social=page.locator('.report-evidence').filter({hasText:'官网关联的Instagram'}).first();for(const host of ['instagram.com','facebook.com','youtube.com','pinterest.com'])assert.equal(await social.locator(`a[href*="${host}"]`).count(),1);
 const videos=[];
 for(let id=56;id<=60;id++){
  await page.locator(`.report-topic a[data-library-video="${id}"]`).first().click();await page.waitForFunction(()=>{const v=document.querySelector('.reading-dialog video');return v&&v.readyState>=1;});
  const actual=await page.locator('.reading-dialog video').evaluate(async v=>{v.muted=true;await v.play();return {duration:v.duration,paused:v.paused};});assert.ok(actual.duration>7);assert.equal(actual.paused,false);videos.push({id,...actual});
  if(id===56)await page.locator('.reading-dialog').screenshot({path:path.join(dir,'已保存视频_播放.png')});
  await page.keyboard.press('Escape');await page.waitForFunction(()=>!document.querySelector('.reading-dialog').open&&!document.querySelector('.reading-dialog video')?.getAttribute('src'));
 }
 // Evidence links in table cells must still work after term annotation.
 assert.ok(await page.locator('.report-evidence a.review-citation').count()>5);
 await page.setViewportSize({width:390,height:844});await matrix.scrollIntoViewIfNeeded();
 const width=await page.evaluate(()=>({page:document.documentElement.scrollWidth,viewport:innerWidth}));assert.ok(width.page<=width.viewport+1,JSON.stringify(width));
 await price.locator('[data-term=twin]').click();assert.ok((await page.locator('.reading-dialog').boundingBox()).width<390);await page.keyboard.press('Escape');await matrix.scrollIntoViewIfNeeded();await page.screenshot({path:path.join(dir,'竞争对照_手机.png')});
 await page.setViewportSize({width:1500,height:1050});const downloadPromise=page.waitForEvent('download',{timeout:60000});await page.locator('#report-package').click();
 const download=await downloadPromise;assert.equal(await download.failure(),null);await download.saveAs(path.join(dir,'完整报告验收.zip'));
 assert.deepEqual(errors,[]);await fs.writeFile(path.join(dir,'ui_result.json'),JSON.stringify({video_playback:videos,page_errors:errors,mobile_width:width,export:download.suggestedFilename()},null,2));console.log(JSON.stringify({passed:true,videos:videos.length,export:download.suggestedFilename()}));
}finally{await browser.close();}
