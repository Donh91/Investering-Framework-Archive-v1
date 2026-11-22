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
     // Capture first-visit Compass before switching views; the graph tab is
     // intentionally hidden on the genuine default homepage.
     const initial='compass-default-'+width+'.png';
     await page.screenshot({path:join(out,initial),fullPage:true,animations:'disabled'});
     screenshots.push(initial);
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
     const btc=page.locator('[data-asset="BTC"]'),eth=page.locator('[data-asset="ETH"]');
     assert.ok(await btc.count()>0&&await eth.count()>0,'ASSET_CONTROLS_MISSING');
     await eth.first().click();
     await btc.first().click();
     if(width===390||width===1280){
       const file='graph-'+width+'.png';
       await page.locator('#variant-panel').screenshot({path:join(out,file),animations:'disabled'});
       screenshots.push(file);
     }
     const file='page-'+width+'.png';
     await page.screenshot({path:join(out,file),fullPage:true,animations:'disabled'});
     screenshots.push(file);
     await page.addScriptTag({content:axe.source});
     const audit=await page.evaluate(async()=>{
       const result=await window.axe.run(document,{runOnly:{type:'tag',
         values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
       return {passes:result.passes.length,incomplete:result.incomplete.length,
         violations:result.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length,
           examples:v.nodes.slice(0,3).map(n=>n.target.join(' '))}))};
     });
     accessibility.push({width,...audit});
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
 const a11y=accessibility.length===4?(violationCount===0?'NO_AUTOMATED_VIOLATIONS':'NEEDS_REMEDIATION'):'NOT_VERIFIED';
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
