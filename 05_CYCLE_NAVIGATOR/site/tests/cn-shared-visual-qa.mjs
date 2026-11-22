/**
 * CN shared visual QA: actual promoted Pages root, ephemeral loopback HTTP only.
 * No source authority, no deployment, no private data, no recurring task.
 */
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {existsSync,readFileSync,mkdirSync,writeFileSync,appendFileSync,realpathSync} from 'node:fs';
import {resolve,join,sep,extname} from 'node:path';
import {chromium} from 'playwright';
import axe from 'axe-core';

const site=resolve(import.meta.dirname,'..');
const dist=resolve(site,'dist');
const out=resolve(site,'qa-visual-artifacts');
const prefix='/Investering-Framework-Archive-v1/';
const chrome=[process.env.CHROME_BIN,'/usr/bin/google-chrome','/usr/bin/chromium']
  .find(p=>p&&existsSync(p));
mkdirSync(out,{recursive:true});
const mime={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript',
 '.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png',
 '.woff2':'font/woff2'};
const findings=[],checks=[],accessibility=[],viewports=[],screenshots=[];
let browser,server;
const problem=(type,reason)=>findings.push({type,reason:String(reason).slice(0,500)});
try {
 assert.ok(chrome,'CHROME_NOT_INSTALLED');
 for(const f of ['index.html','data/latest.json','data/compass.json'])
   assert.ok(existsSync(join(dist,f)),'MISSING_PUBLIC_BUNDLE:'+f);
 server=createServer((req,res)=>{
   try{
     const path=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
     if(!path.startsWith(prefix)){res.writeHead(404).end();return;}
     const rel=(path.slice(prefix.length)||'index.html').replace(/\/$/,'/index.html');
     const full=resolve(dist,rel);
     if(!full.startsWith(dist+sep)){res.writeHead(403).end();return;}
     const real=realpathSync(full);
     if(!real.startsWith(dist+sep)){res.writeHead(403).end();return;}
     res.writeHead(200,{'Content-Type':mime[extname(real)]||'application/octet-stream',
       'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}).end(readFileSync(real));
   }catch{res.writeHead(404).end();}
 });
 await new Promise((ok,bad)=>server.once('error',bad).listen(0,'127.0.0.1',ok));
 const origin='http://127.0.0.1:'+server.address().port;
 browser=await chromium.launch({headless:true,executablePath:chrome,
   args:['--no-sandbox','--disable-dev-shm-usage','--disable-background-networking']});
 for(const [width,height] of [[390,844],[430,932],[768,1024],[1280,900]]){
   const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1,
     isMobile:width<600,hasTouch:width<600,reducedMotion:'reduce'});
   const jsErrors=[],httpErrors=[];
   page.on('pageerror',e=>jsErrors.push(String(e.message||e).slice(0,300)));
   page.on('response',r=>{
     if(r.status()>=400&&!r.url().endsWith('/favicon.ico'))
       httpErrors.push({status:r.status(),url:r.url().replace(origin,'').slice(0,120)});
   });
   await page.route('**/*',r=>r.request().url().startsWith(origin+prefix)
     ?r.continue():r.abort('blockedbyclient'));
   let dom={};
   try{
     const resp=await page.goto(origin+prefix,{waitUntil:'domcontentloaded',timeout:30000});
     assert.equal(resp?.status(),200,'NO_PUBLIC_HOME');
     await page.locator('#variant-panel').waitFor({state:'attached',timeout:25000});
     await page.locator('#compass-pro').waitFor({state:'attached',timeout:10000});
     await page.waitForTimeout(650);
     // The first screen is the default Compass view. Audit that view before
     // the real tab system hides it. One axe run per view, not one per page.
     await page.addScriptTag({content:axe.source});
     const auditView=async(view)=>{
       const audit=await page.evaluate(async()=>{
         const result=await window.axe.run(document,{runOnly:{type:'tag',
           values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
         return {passes:result.passes.length,incomplete:result.incomplete.length,
           violations:result.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length,
             examples:v.nodes.slice(0,3).map(n=>n.target.join(' '))}))};
       });
       accessibility.push({width,view,...audit});
     };
     const initial='compass-default-'+width+'.png';
     await page.screenshot({path:join(out,initial),fullPage:true,animations:'disabled'});
     screenshots.push(initial);
     await auditView('compass');
     await page.locator('[data-premium-nav="graph"]').click();
     await page.locator('#variant-panel').waitFor({state:'visible',timeout:12000});
     await page.locator('#chart').waitFor({state:'visible',timeout:12000});
     await page.waitForTimeout(850);
     dom=await page.evaluate(()=>{
       const doc=document.documentElement,body=document.body,graph=document.querySelector('#chart');
       const rect=graph?.getBoundingClientRect();
       return {title:document.title,visibleTextChars:body?.innerText.trim().length||0,
         scrollWidth:Math.max(doc.scrollWidth,body?.scrollWidth||0),clientWidth:doc.clientWidth,
         graphWidth:rect?.width||0,graphHeight:rect?.height||0,
         sourceState:document.querySelector('#compass-pro')?.dataset.sourceState||document.querySelector('#cn-forward-source-status')?.textContent?.trim().slice(0,120)||'NOT_DECLARED',
         feedText:document.querySelector('#feed-status')?.textContent?.trim().slice(0,160)||'NOT_DECLARED'};
     });
     assert.match(dom.title,/Cycle Navigator/i,'WRONG_PRODUCT_TITLE');
     assert.ok(dom.visibleTextChars>250,'EMPTY_PAGE');
     assert.ok(dom.graphWidth>50&&dom.graphHeight>40,'GRAPH_CONTAINER_COLLAPSED');
     assert.ok(dom.scrollWidth<=dom.clientWidth+2,
       'HORIZONTAL_OVERFLOW_'+width+':'+dom.scrollWidth+'>'+dom.clientWidth);
     // More than one DOM node carries data-asset, including non-button,
     // hidden Compass sections. Click only the active visible Graph B controls.
     const btc=page.locator('#variant-panel button[data-asset="BTC"]:visible');
     const eth=page.locator('#variant-panel button[data-asset="ETH"]:visible');
     assert.equal(await btc.count(),1,'BTC_ACTIVE_GRAPH_CONTROL_MISSING_OR_DUPLICATE');
     assert.equal(await eth.count(),1,'ETH_ACTIVE_GRAPH_CONTROL_MISSING_OR_DUPLICATE');
     // Each click launches asynchronous source-bound refresh. Wait for its
     // actual public feed response, then a stable painted state. A missing
     // authenticated source is recorded as UNAVAILABLE, never called fresh.
     const refreshAsset=async(button,name)=>{
       const [response]=await Promise.all([
         page.waitForResponse(r=>r.url().includes('/data/latest.json') && r.status()===200,
           {timeout:16000}),
         button.click({timeout:8000})
       ]);
       assert.equal(response.status(),200,'PUBLIC_FEED_TRANSPORT_'+name);
       await page.waitForFunction(async name=>{
         const buttons=[...document.querySelectorAll('#variant-panel button[data-asset]')];
         const selected=buttons.find(b=>b.dataset.asset===name);
         const pair=document.getElementById('pair')?.textContent||'';
         const feed=document.getElementById('feed-status')?.textContent||'';
         return selected?.getAttribute('aria-pressed')==='true' && pair.startsWith(name+' / ')
           && feed.trim().length>12;
       },name,{timeout:10000});
       // Optional public lineage can settle independently. Wait for a short
       // DOM quiet interval, never a fixed synthetic market value.
       await page.waitForTimeout(220);
       const result=await page.evaluate(()=>({
         asset:document.querySelector('#variant-panel button[aria-pressed="true"][data-asset]')?.dataset.asset||null,
         freshness:document.getElementById('variant-panel')?.dataset.freshness||'NOT_DECLARED',
         source:document.getElementById('source-state')?.textContent?.trim().slice(0,160)||'',
         observed:document.getElementById('observed-value')?.textContent?.trim()||''
       }));
       assert.equal(result.asset,name,'ASSET_REFRESH_MISMATCH');
       assert.ok(['fresh','stale','unavailable'].includes(result.freshness),'UNKNOWN_SOURCE_FRESHNESS');
       assert.ok(result.source.length>0,'UNLABELED_SOURCE_STATE');
       if(result.freshness==='unavailable') assert.ok(result.observed==='—','UNAVAILABLE_HAS_FALSE_QUOTE');
       return result;
     };
     const ethState=await refreshAsset(eth,'ETH');
     const btcState=await refreshAsset(btc,'BTC');
     dom.assetRefresh={ETH:ethState,BTC:btcState};
     if(width===390||width===1280){
       const file='graph-'+width+'.png';
       await page.locator('#variant-panel').screenshot({path:join(out,file),animations:'disabled'});
       screenshots.push(file);
     }
     const file='page-'+width+'.png';
     await page.screenshot({path:join(out,file),fullPage:true,animations:'disabled'});
     screenshots.push(file);
     await auditView('graph');
     for(const view of ['path','proof']){
       await page.locator('[data-premium-nav="'+view+'"]').click();
       const panel=view==='path'?'#official-path-view':'#proof-explorer';
       await page.locator(panel).waitFor({state:'visible',timeout:12000});
       await auditView(view);
     }
     checks.push({width,status:'PASS'});
   }catch(e){
     problem('VISUAL_'+width,e.message||e);
     checks.push({width,status:'FAIL'});
     try{const file='error-'+width+'.png';
       await page.screenshot({path:join(out,file),fullPage:true});
       screenshots.push(file);
     }catch{}
   }
   if(jsErrors.length)problem('JS_'+width,JSON.stringify(jsErrors));
   if(httpErrors.length)problem('HTTP_'+width,JSON.stringify(httpErrors));
   viewports.push({width,height,...dom,jsErrors,httpErrors});
   await page.close();
 }
}catch(e){problem('FATAL',e.message||e)}
finally{
 try{await browser?.close()}catch{}
 try{await new Promise(ok=>{if(server)server.close(ok);else ok()})}catch{}
 const functional=checks.length===4&&!findings.length&&checks.every(c=>c.status==='PASS')?'PASS':'FAIL';
 const violationCount=accessibility.reduce((n,x)=>n+x.violations.length,0);
 const a11y=accessibility.length===16?(violationCount===0?'NO_AUTOMATED_VIOLATIONS':'NEEDS_REMEDIATION'):'NOT_VERIFIED';
 const report={contract:'CN_SHARED_VISUAL_QA_V1',public_only:true,
   native_iphone_safari:false,visual_functional:functional,accessibility:a11y,
   axe_rule_findings:violationCount,viewports,checks,accessibility_results:accessibility,
   findings,screenshots,note:'Automated test only; not evidence of source freshness, investor success or manual WCAG acceptance.'};
 writeFileSync(join(out,'report.json'),JSON.stringify(report,null,2)+'\n');
 console.log('CN_SHARED_VISUAL_QA_V1 '+JSON.stringify({functional,a11y,violationCount}));
 if(violationCount)console.log('::warning::CN WCAG rule findings: '+violationCount+'. See screenshot artifact. Do not claim WCAG PASS.');
 for(const f of findings)console.log('::error::'+f.type+' '+f.reason);
 if(process.env.GITHUB_STEP_SUMMARY)appendFileSync(process.env.GITHUB_STEP_SUMMARY,
   '## CN Visual QA\n\n- Real-browser functional: **'+functional+'**\n- Automated accessibility: **'+a11y+
   '** ('+violationCount+' rule findings)\n- Viewports: 390 / 430 / 768 / 1280\n- Screenshots and evidence: artifact cn-visual-qa (3 days)\n- No deployment, forecast inference or new schedule.\n\n');
 if(functional!=='PASS')process.exitCode=1;
}
