// Run with a Node installation providing Playwright. No network navigation.
const fs=require('fs');
const path=require('path');
const {pathToFileURL}=require('url');
const {chromium}=require(process.env.BOOK_PLAYWRIGHT_MODULE||'playwright');
(async()=>{
 const root=path.resolve(__dirname,'..'),sample=process.argv.includes('--sample');
 const reportDir=path.resolve(process.argv.find(x=>x.startsWith('--reports='))?.slice(10)||path.join(root,'.local-library','book-review'));
 fs.mkdirSync(reportDir,{recursive:true});
 const options={headless:true};
 if(process.env.BOOK_BROWSER_EXECUTABLE)options.executablePath=process.env.BOOK_BROWSER_EXECUTABLE;
 else if(process.platform==='win32')options.executablePath='C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
 const browser=await chromium.launch(options);
 const page=await browser.newPage({viewport:{width:1280,height:1000},deviceScaleFactor:1});
 const errors=[],failed=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure()?.errorText}));
 await page.goto(pathToFileURL(path.join(root,'book','index.html')).href,{waitUntil:'load'});
 await page.locator('#E05').scrollIntoViewIfNeeded();
 await page.locator('#E05').screenshot({path:path.join(reportDir,'hands-sample.png')});
 if(!sample){
   for(const figure of await page.locator('figure.example').all()){
     const id=await figure.getAttribute('id');
     await figure.scrollIntoViewIfNeeded();await figure.screenshot({path:path.join(reportDir,id+'.png')});
   }
 }
 const panel=page.locator('#E05 .player');
 await panel.locator('[data-hand=rh]').click();
 await page.waitForTimeout(200);
 const playing=await panel.locator('output').innerText();
 if(!playing.includes('正在播放右手'))throw new Error('Right-hand player failed: '+playing);
 await panel.locator('.stop').click();
 if(!(await panel.locator('output').innerText()).includes('已停止'))throw new Error('Stop failed');
 await panel.locator('select').selectOption('0.5');await panel.locator('[data-hand=lh]').click();
 const left=await panel.locator('output').innerText();
 if(!left.includes('50%')||!left.includes('左手'))throw new Error('Slow left-hand player failed');
 await panel.locator('.stop').click();
 const images=await page.locator('figure img').evaluateAll(xs=>xs.map(x=>({src:x.getAttribute('src'),loaded:x.complete&&x.naturalWidth>0})));
 // Decode every WAV without playing it. This is a format/access check, not listening.
 const audio=await page.evaluate(async()=>{
   const results=[];
   for(const e of JSON.parse(document.getElementById('exercise-data').textContent)){
     const a=new Audio(`assets/${e.id}.wav`);a.preload='metadata';
     const r=await new Promise(resolve=>{const t=setTimeout(()=>resolve({id:e.id,ok:false,error:'timeout'}),5000);a.onloadedmetadata=()=>{clearTimeout(t);resolve({id:e.id,ok:a.duration>0,seconds:a.duration})};a.onerror=()=>{clearTimeout(t);resolve({id:e.id,ok:false,error:a.error?.message})};a.load()});results.push(r);
   }return results;
 });
 await page.evaluate(()=>document.querySelectorAll('img').forEach(x=>x.loading='eager'));
 await page.waitForTimeout(250);
 const broken=await page.locator('img').evaluateAll(xs=>xs.filter(x=>!x.complete||x.naturalWidth===0).map(x=>x.getAttribute('src')));
 let pdf=null;
 if(!sample){
   await page.emulateMedia({media:'print'});
   pdf=path.join(root,'book','现代流行键盘_初稿.pdf');
   await page.pdf({path:pdf,format:'A4',printBackground:true,preferCSSPageSize:true,
     displayHeaderFooter:true,headerTemplate:'<span></span>',
     footerTemplate:'<div style="font-size:8px;width:100%;text-align:center;color:#647078;">现代流行键盘 · 第一版初稿　<span class="pageNumber"></span> / <span class="totalPages"></span></div>'});
 }
 await page.emulateMedia({media:'screen'});await page.setViewportSize({width:390,height:844});
 await page.locator('#E05').scrollIntoViewIfNeeded();
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);
 await page.screenshot({path:path.join(reportDir,'mobile.png')});
 // Chromium may stop a successful media request after reading its metadata.
 // Retain that evidence separately; an unverified or failed media file is still a failure.
 const verifiedAudio=new Set(audio.filter(x=>x.ok).map(x=>x.id+'.wav'));
 const mediaMetadataAborts=failed.filter(x=>x.error==='net::ERR_ABORTED'&&verifiedAudio.has(x.url.split('/').pop()));
 const unexpectedFailures=failed.filter(x=>!mediaMetadataAborts.includes(x));
 const result={sample,pageErrors:errors,failedRequests:unexpectedFailures,mediaMetadataAborts,brokenImages:broken,scoreImages:images.length,audioFiles:audio,mobileHorizontalOverflow:overflow,player:'right/left/50%-speed/stop checked in browser; audio not listened to',pdf};
 fs.writeFileSync(path.join(reportDir,sample?'sample-browser.json':'browser.json'),JSON.stringify(result,null,2));
 await browser.close();
 console.log(JSON.stringify({errors:errors.length,failedRequests:unexpectedFailures.length,mediaMetadataAborts:mediaMetadataAborts.length,brokenImages:broken.length,audioFiles:audio.length,mobileHorizontalOverflow:overflow,pdf}));
 if(errors.length||unexpectedFailures.length||broken.length||overflow||audio.some(x=>!x.ok))process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
