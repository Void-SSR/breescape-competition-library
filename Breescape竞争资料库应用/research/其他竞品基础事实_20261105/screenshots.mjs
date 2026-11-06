import {chromium} from '/Users/voidengine/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';import path from 'node:path';import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../../',import.meta.url)),w=fileURLToPath(new URL('.',import.meta.url));
const browser=await chromium.launch({headless:true}); const context=await browser.newContext({viewport:{width:1440,height:1000},locale:'en-US'});
const targets=[['cozy_home','https://cozybliss.com/'],['cozy_amazon','https://www.amazon.com/dp/B0BVQMTD8W'],['sheex_home','https://www.sheex.com/'],['sheex_product','https://www.sheex.com/products/original-performance-sheet-set']];
const out=[];for(const [key,url] of targets){const page=await context.newPage();try{await page.goto(url,{waitUntil:'domcontentloaded',timeout:35000});await page.waitForTimeout(2200);const text=await page.locator('body').innerText();await page.screenshot({path:path.join(root,'data/attachments',key+'_20261105.png')});out.push({key,url,title:await page.title(),excerpt:text.slice(0,1600),screenshot:'attachments/'+key+'_20261105.png'});}catch(e){out.push({key,error:String(e)})}finally{await page.close()}console.log(key,JSON.stringify(out.at(-1)).slice(0,350));}
await fs.writeFile(path.join(w,'screenshots.json'),JSON.stringify(out,null,2));await browser.close();
