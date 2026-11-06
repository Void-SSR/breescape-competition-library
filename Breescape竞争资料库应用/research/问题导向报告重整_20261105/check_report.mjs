import {chromium} from '/Users/voidengine/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';import fs from 'node:fs/promises';import path from 'node:path';import {fileURLToPath} from 'node:url';
const dir=fileURLToPath(new URL('.',import.meta.url)),data=JSON.parse(await fs.readFile(path.join(dir,'feedback.json'),'utf8'));
const browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1500,height:1050},acceptDownloads:true});const errors=[];page.on('pageerror',e=>errors.push(e.message));
try{
 await page.goto('http://127.0.0.1:8766/#overview/shilucheng');await page.locator('.brand-report h1').waitFor();
 assert.equal(await page.locator('.report-chapter-heading').count(),6);assert.equal(await page.locator('.report-question').count(),39);assert.equal(await page.locator('.report-stale').count(),0);
 assert.equal(await page.locator('.feedback-list.positive tbody tr').count(),37);assert.equal(await page.locator('.feedback-list.negative tbody tr').count(),46);assert.equal(await page.locator('.feedback-rank').count(),6);
 for(const r of data.rows){const row=page.locator(`tr[data-feedback-code="${r.code}"][data-feedback-valence="${r.valence}"]`);assert.equal((await row.locator('td').nth(0).innerText()).trim(),String(r.count));assert.equal((await row.locator('td').nth(1).innerText()).trim(),r.percent_group.toFixed(1)+'%');}
 const overview=await page.locator('.feedback-overview').innerText();assert.match(overview,/79.1%/);assert.match(overview,/33.8%/);assert.equal(await page.locator('.feedback-method').getAttribute('open'),null);
 assert.ok((await page.locator('.feedback-method').boundingBox()).y>(await page.locator('#question-feedback-negative').boundingBox()).y);
 assert.equal(await page.locator('#question-success-drivers ol>li').count(),3);assert.equal(await page.locator('#question-success-buy').count(),1);assert.equal(await page.locator('#question-success-advantage').count(),1);
 assert.equal(await page.locator('#question-success-advantage .report-support').getAttribute('open'),null);assert.equal(await page.locator('#question-success-drivers .report-support').getAttribute('open'),null);
 const hierarchy=await page.locator('#question-success-drivers').evaluate(el=>({title:parseFloat(getComputedStyle(el.querySelector('.finding-title')).fontSize),evidence:parseFloat(getComputedStyle(el.querySelector('.finding-evidence')).fontSize)}));assert.ok(hierarchy.title>hierarchy.evidence);
 await page.locator('#question-feedback-overall').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(dir,'评论全貌与认可_桌面.png')});
 await page.locator('#question-feedback-negative').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(dir,'不认可完整分项_桌面.png')});
 await page.locator('#question-success-drivers').screenshot({path:path.join(dir,'畅销原因_桌面.png')});
 await page.locator('#question-brand-position').screenshot({path:path.join(dir,'问题式阅读_桌面.png')});
 // Jump to the comparison instead of appending an unrelated table to the cause section.
 await page.locator('[data-question-jump="question-product-comparison"]').click();await page.waitForTimeout(450);assert.equal(new URL(page.url()).hash,'#overview/shilucheng');
 assert.equal(await page.locator('#question-product-comparison .comparison-table thead a').count(),3);
 const social=page.locator('#question-channel-accounts');for(const host of ['instagram.com','facebook.com','youtube.com','pinterest.com'])assert.ok(await social.locator(`a[href*="${host}"]`).count());
 await page.locator('#question-product-identity [data-term=queen]').first().click();assert.equal(await page.locator('.reading-dialog[open]').count(),1);await page.keyboard.press('Escape');
 assert.equal(await page.locator('#question-channel-top5 [data-library-video]').count(),5);
 await page.locator('#question-channel-top5 [data-library-video="56"]').click();await page.waitForFunction(()=>document.querySelector('.reading-dialog video')?.readyState>=1);assert.ok(await page.locator('.reading-dialog video').evaluate(v=>v.duration>7));await page.keyboard.press('Escape');
 // Verify that the current editor exposes the new answers without saving to the live DB.
 await page.locator('#report-audit-2>summary').click();await page.locator('[data-edit-report="2"]').click();assert.ok(await page.locator('#modal input[name^="question_title_"]').count()>6);assert.equal(await page.locator('#modal textarea[name="question_answer_2_0"]').inputValue(),await page.locator('#question-success-buy .question-answer').innerText());await page.keyboard.press('Escape');
 await page.setViewportSize({width:390,height:844});await page.locator('#question-feedback-overall').scrollIntoViewIfNeeded();assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await page.screenshot({path:path.join(dir,'评论全貌_手机.png')});
 await page.locator('#question-success-drivers').screenshot({path:path.join(dir,'畅销原因_手机.png')});
 await page.setViewportSize({width:1500,height:1050});const dp=page.waitForEvent('download',{timeout:60000});await page.locator('#report-package').click();const download=await dp;assert.equal(await download.failure(),null);await download.saveAs(path.join(dir,'报告验收.zip'));
 assert.deepEqual(errors,[]);await fs.writeFile(path.join(dir,'ui_result.json'),JSON.stringify({passed:true,questions:39,feedback_rows:83,top_marks:6,hierarchy,errors,download:download.suggestedFilename()},null,2));console.log(JSON.stringify({passed:true,questions:39,feedback_rows:83,export:download.suggestedFilename()}));
}finally{await browser.close();}
