/**
 * Real NEXT artifact smoke on the exact GitHub Pages repository prefix.
 * Bounded headless Chrome/CDP test, no npm browser dependencies.
 * Emulates 390 and 430 CSS px; NOT physical iPhone Safari approval.
 */
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {spawn} from 'node:child_process';
import {existsSync,readFileSync,mkdtempSync,rmSync} from 'node:fs';
import {resolve,dirname,extname,join,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {tmpdir} from 'node:os';
import {setTimeout as delay} from 'node:timers/promises';

const here=dirname(fileURLToPath(import.meta.url));
const dist=resolve(here,'../dist');
const base='/Investering-Framework-Archive-v1/';
const rootMode=process.argv.includes('--root');
const chrome=[process.env.CHROME_BIN,'/usr/bin/google-chrome','/usr/bin/chromium','/usr/bin/chromium-browser']
 .find(path=>path&&existsSync(path));
assert.ok(chrome,'NEXT_BROWSER_NO_CHROME');
assert.ok(existsSync(resolve(dist,'next/index.html')),'NEXT_BROWSER_NO_REAL_VITE_ROOT');
assert.ok(existsSync(resolve(dist,'next/graph-b/source-graph-b.html')),'NEXT_BROWSER_NO_B_ENTRY');
if(rootMode)assert.ok(existsSync(resolve(dist,'index.html')),'ROOT_BROWSER_MISSING_OFFICIAL_ENTRY');

const types={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript',
 '.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png'};
const server=createServer((req,res)=>{
 let path;
 try{path=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname)}
 catch{res.writeHead(400).end();return;}
 if(!path.startsWith(base)){res.writeHead(404).end();return;}
 let rel=path.slice(base.length);
 if(!rel||rel.endsWith('/'))rel+='index.html';
 const file=resolve(dist,rel);
 if(!file.startsWith(dist+sep)){res.writeHead(403).end();return;}
 try{
  const bytes=readFileSync(file);
  res.writeHead(200,{'Content-Type':types[extname(file)]||'application/octet-stream',
   'Cache-Control':'no-store'}).end(bytes);
 }catch{res.writeHead(404).end('Not found');}
});
await new Promise((ok,bad)=>server.once('error',bad).listen(0,'127.0.0.1',ok));
const origin='http://127.0.0.1:'+server.address().port+base;
const errors=[],responses=[];
let profile=null,browser=null,socket=null;
try{
 // One fresh retry mirrors the canonical Chrome gate and never bypasses
 // browser assertions or the release when both startup attempts fail.
 const failures=[];
 let port=null;
 for(let attempt=1;attempt<=2&&!port;attempt++){
  profile=mkdtempSync(join(tmpdir(),'cn-next-browser-'));
  browser=spawn(chrome,['--headless=new','--no-sandbox','--disable-gpu',
   '--disable-dev-shm-usage',...(attempt===1?['--no-zygote']:[]),
   '--no-first-run','--no-default-browser-check',
   '--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'],
   {stdio:['ignore','ignore','pipe']});
  let stderr='',startupError='';
  browser.on('error',err=>{startupError=String(err.message||err)});
  browser.stderr?.on('data',data=>{stderr=(stderr+data.toString()).slice(-2400)});
  for(let i=0;i<120;i++){
   if(startupError||browser.exitCode!==null||browser.signalCode!==null)break;
   try{
    const p=Number(readFileSync(join(profile,'DevToolsActivePort'),'utf8').split('\n')[0]);
    if(Number.isInteger(p)&&p>0){port=p;break}
   }catch{}
   await delay(100);
  }
  if(port)break;
  failures.push({attempt,exitCode:browser.exitCode,signal:browser.signalCode,
   error:startupError,stderr:stderr.slice(-700)});
  if(browser.exitCode===null&&browser.signalCode===null){
   browser.kill('SIGTERM');
   await Promise.race([new Promise(ok=>browser.once('close',ok)),delay(1000)]);
   if(browser.exitCode===null&&browser.signalCode===null)browser.kill('SIGKILL');
  }
  try{rmSync(profile,{recursive:true,force:true})}catch{}
  profile=null;browser=null;
  if(attempt===1)await delay(400);
 }
 assert.ok(port,'NEXT_CHROME_BOTH_STARTUPS_FAILED:'+JSON.stringify(failures));
 const pages=await (await fetch('http://127.0.0.1:'+port+'/json')).json();
 const page=pages.find(p=>p.type==='page');
 assert.ok(page?.webSocketDebuggerUrl,'NEXT_NO_CDP_TARGET');
 socket=new WebSocket(page.webSocketDebuggerUrl);
 await new Promise((ok,bad)=>{socket.onopen=ok;socket.onerror=bad});
 const pending=new Map();
 let id=0;
 socket.onmessage=e=>{
  const msg=JSON.parse(e.data);
  if(msg.method==='Runtime.exceptionThrown'){
   errors.push(String(msg.params?.exceptionDetails?.text||'RUNTIME_EXCEPTION'));
  }
  if(msg.method==='Network.responseReceived'){
   const response=msg.params?.response||{};
   if(response.status>=400&&/\.(?:html|js|css|json|svg)(?:$|\?)/.test(response.url||''))
    responses.push({url:response.url,status:response.status});
  }
  if(msg.id&&pending.has(msg.id)){
   const entry=pending.get(msg.id);pending.delete(msg.id);
   msg.error?entry.reject(Error(JSON.stringify(msg.error))):entry.resolve(msg.result);
  }
 };
 function send(method,params={}){
  return new Promise((ok,bad)=>{
   const serial=++id;
   pending.set(serial,{resolve:ok,reject:bad});
   socket.send(JSON.stringify({id:serial,method,params}));
   const timeout=setTimeout(()=>{
    if(pending.has(serial)){pending.delete(serial);bad(Error('NEXT_CDP_TIMEOUT:'+method))}
   },10000);
   timeout.unref();
  });
 }
 async function evaluate(fn){
  const result=await send('Runtime.evaluate',{expression:'('+fn.toString()+')()',
   returnByValue:true,awaitPromise:true});
  if(result.exceptionDetails)throw Error('NEXT_BROWSER_EVALUATION:'+JSON.stringify(result.exceptionDetails));
  return result.result?.value;
 }
 await send('Page.enable');
 await send('Runtime.enable');
 await send('Network.enable');
 const results=[];
 // 320 CSS-px reflow is an additional automated narrow-viewport proxy.
 // This is NOT a physical iPhone Safari/VoiceOver/200% zoom certification.
 for(const width of [390,430,1440,320]){
  await send('Emulation.setDeviceMetricsOverride',{width,height:width===390?844:width===430?932:width===320?700:1000,
   deviceScaleFactor:1,mobile:width<600});
  await send('Page.navigate',{url:origin+(rootMode?'':'next/')});
  let ready=false;
  for(let attempt=0;attempt<100;attempt++){
   await delay(100);
   ready=await evaluate(()=>document.readyState==='complete'&&
    !!document.getElementById('official-pilot-path')&&
    (document.getElementById('feed-status')?.textContent||'')!=='Kontrollerer kanonisk, offentligt CN-datasæt. Ingen demo-priser.');
   if(ready)break;
  }
  assert.ok(ready,'NEXT_SOURCE_APP_NOT_READY:'+width);
  const report=await evaluate(()=>{
   const $=q=>document.querySelector(q);
   const ids=['variant-panel','chart','proof-explorer','official-product-pilot','official-pilot-path'];
   const present=ids.every(id=>!!document.getElementById(id));
   const logo=$('.dev-brand img');
   const label=$('[data-asset="BTC"]');
   const alternate=$('[data-asset="ETH"]');
   const touch=[...document.querySelectorAll('[data-asset],[data-lang]')].map(b=>{
    const r=b.getBoundingClientRect();return {w:r.width,h:r.height};
   });
   const horizonCards=[...document.querySelectorAll('.official-pilot-horizon')];
   const horizonSourceState=$('#official-product-pilot')?.dataset.sourceState||'unavailable';
   const horizonsPresent=horizonCards.length===5;
   const horizonSemantics=horizonCards.every(card=>{
    const posture=card.querySelector('.official-pilot-horizon-posture');
    return !!card.querySelector('.official-pilot-horizon-direction')&&!!posture&&
     card.dataset.sourceState===horizonSourceState&&
     (horizonSourceState!=='expired'||(posture.textContent==='UDLØBET'||posture.textContent==='EXPIRED'));
   });
   const pathStageCount=document.querySelectorAll('#official-pilot-path li').length;
   const bounds=el=>{if(!el)return null;const r=el.getBoundingClientRect();
    return {top:r.top,bottom:r.bottom,left:r.left,right:r.right,height:r.height};};
   const decisionFold={
    summary:bounds($('.premium-decision-summary')),
    action:bounds($('.premium-decision-summary .official-pilot-action')),
    gate:bounds($('.premium-decision-summary #official-pilot-gate')),
    graph:bounds($('#variant-panel')),
    detail:bounds($('.premium-compass-detail')),
    gateCount:document.querySelectorAll('#official-pilot-gate').length,
    gateWithinSummary:$('.premium-decision-summary')?.contains($('#official-pilot-gate'))===true,
    actionCount:document.querySelectorAll('#official-pilot-action').length,
    headingCount:document.querySelectorAll('#official-product-pilot').length,
    viewportHeight:innerHeight
   };
   const before=$('.premium-entry-navigation [data-premium-nav="compass"]')?.textContent||'';
   $('[data-lang="en"]')?.click();
   const english=$('.premium-entry-navigation [data-premium-nav="compass"]')?.textContent||'';
   $('[data-lang="da"]')?.click();
   const danish=$('.premium-entry-navigation [data-premium-nav="compass"]')?.textContent||'';
   alternate?.click();
   return {width:innerWidth,overflow:Math.max(document.body.scrollWidth,document.documentElement.scrollWidth)-innerWidth,
    present,logo:!!logo?.complete&&logo.naturalWidth>0,
    originalB:!!$('#chart[viewBox="0 0 1000 405"]'),links:[...document.querySelectorAll('.premium-entry-navigation a')].map(a=>a.getAttribute('href')),
    before,english,danish,touch,horizonsPresent,horizonSemantics,horizonSourceState,pathStageCount,
    sourceState:$('#source-state')?.textContent||'',
    sourceStatus:$('#feed-status')?.textContent||'',decisionFold,
    btc:!!label,eth:!!alternate,rootPath:location.pathname,
    officialHome:document.body.classList.contains('premium-home'),
    noindex:!!document.querySelector('meta[name="robots"][content*="noindex"]'),
    priorLink:$('.premium-entry-canonical')?.getAttribute('href'),
    dataLinks:[...document.querySelectorAll('.premium-meta-links a')].map(a=>a.getAttribute('href')),
    title:$('h1[data-premium-copy="title"]')?.textContent||''};
  });
  await delay(400);
  const selection=await evaluate(()=>({
   ethSelected:document.querySelector('[data-asset="ETH"]')?.getAttribute('aria-pressed')==='true',
   pair:document.getElementById('pair')?.textContent
  }));
  assert.equal(report.width,width,'NEXT_WRONG_VIEWPORT');
  assert.ok(report.present&&report.originalB,'NEXT_MISSING_REAL_PREMIUM_MARKUP:'+width);
  assert.ok(report.logo,'NEXT_REAL_CN_LOGO_NOT_LOADED:'+width);
  const fold=report.decisionFold;
  assert.ok(fold.summary&&fold.action&&fold.graph&&fold.detail&&fold.gate,
    'NEXT_DECISION_FIRST_MARKUP_MISSING:'+width);
  assert.equal(fold.actionCount,1,'NEXT_ACTION_ISSUER_DUPLICATED:'+width);
  assert.equal(fold.headingCount,1,'NEXT_COMPASS_ISSUER_DUPLICATED:'+width);
  assert.equal(fold.gateCount,1,'NEXT_SOURCE_GATE_DUPLICATED:'+width);
  assert.ok(fold.summary.top>=0&&fold.summary.top<fold.viewportHeight,
    'NEXT_FIRST_FOLD_SUMMARY_NOT_VISIBLE:'+width+':'+JSON.stringify(fold));
  assert.ok(fold.action.top>=fold.summary.top&&
    fold.action.bottom<=fold.summary.bottom+3,
    'NEXT_ACTION_NOT_IN_SUMMARY:'+width);
  assert.ok(fold.gateWithinSummary,
    'NEXT_SOURCE_GATE_MUST_BELONG_TO_DECISION_SUMMARY:'+width);
  // UNAVAILABLE or expired data may deliberately hide the source gate.
  // A display:none element has a zero rectangle and must not fail geometry.
  if(fold.gate.height>0)assert.ok(fold.gate.top>=fold.summary.top&&
    fold.gate.bottom<=fold.summary.bottom+3,
    'NEXT_VISIBLE_GATE_NOT_IN_SUMMARY:'+width);
  assert.ok(fold.summary.bottom<=fold.graph.top+2&&fold.graph.bottom<=fold.detail.top+2,
    'NEXT_WRONG_DECISION_GRAPH_DETAIL_ORDER:'+width);
  if(width===390||width===430){
   assert.ok(fold.action.bottom<=fold.viewportHeight,
    'NEXT_MOBILE_ACTION_BELOW_FIRST_FOLD:'+width+':'+JSON.stringify(fold));
   assert.ok(fold.gate.height===0||fold.gate.bottom<=fold.viewportHeight,
    'NEXT_MOBILE_SOURCE_CONFIRMATION_BELOW_FIRST_FOLD:'+width+':'+JSON.stringify(fold));
   assert.ok(fold.graph.top<fold.viewportHeight,
    'NEXT_MOBILE_APPROVED_GRAPH_B_BELOW_FIRST_FOLD:'+width+':'+JSON.stringify(fold));
  }
  assert.ok(report.overflow<=2,'NEXT_HORIZONTAL_OVERFLOW:'+width+':'+report.overflow);
  assert.equal(report.english,'Compass','NEXT_LANGUAGE_EN');
  assert.equal(report.danish,'Kompas','NEXT_LANGUAGE_DA');
  assert.ok(report.links.includes('#proof-explorer')&&report.links.includes('#official-pilot-path'),
   'NEXT_MISSING_SECTION_NAV');
  assert.ok(report.touch.every(x=>x.w>=44&&x.h>=44),'NEXT_TOUCH_TARGET_TOO_SMALL');
  assert.ok(report.horizonSemantics,'NEXT_COMPASS_HORIZON_MARKUP_OR_EXPIRED_ACTION');
  assert.ok(report.horizonSourceState==='unavailable'||
    (report.horizonsPresent&&report.pathStageCount===10),
   'NEXT_HORIZON_SOURCE_OR_PATH_COUNT_MISMATCH');
  assert.ok(selection.ethSelected&&selection.pair==='ETH / USD','NEXT_BTC_ETH_NOT_INTERACTIVE');
  assert.ok(report.rootPath.endsWith(rootMode?base:base+'next/'),'NEXT_WRONG_BASEPATH');
  if(rootMode){
   assert.ok(report.officialHome&&!report.noindex,'ROOT_NOT_OFFICIAL_OR_NOINDEX');
   assert.equal(report.priorLink,'./vnext/','ROOT_PRIOR_VERSION_LINK');
   assert.deepEqual(report.dataLinks,['./data/latest.json','./data/compass.json'],'ROOT_DATA_LINKS');
  }
  assert.equal(errors.length,0,'NEXT_BROWSER_JS_EXCEPTIONS:'+JSON.stringify(errors));
  assert.equal(responses.length,0,'NEXT_BROWSER_FAILED_ASSETS:'+JSON.stringify(responses));
  results.push({width,overflow:report.overflow,originalB:true,logo:true,
   officialInputsPresent:report.present,daEn:true,ethSelected:true,failClosed:!!report.sourceStatus,
   decisionFirst:true,actionVisibleInFirstFold:fold.action.top<fold.viewportHeight,
   firstFoldMetrics:{viewportHeight:fold.viewportHeight,summaryTop:Math.round(fold.summary.top),
    summaryBottom:Math.round(fold.summary.bottom),actionTop:Math.round(fold.action.top),
    actionBottom:Math.round(fold.action.bottom),gateTop:Math.round(fold.gate.top),
    gateBottom:Math.round(fold.gate.bottom),graphTop:Math.round(fold.graph.top)}});
  if(width===430){
   // Adversarial live refresh failure, not merely an adapter unit assertion:
   // a previously rendered Official action must not reappear on language switch.
   await evaluate(()=>{
    window.fetch=async()=>{throw Error('INTENTIONAL_TEST_ONLY_OFFLINE')};
    Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});
    document.dispatchEvent(new Event('visibilitychange'));
    return true;
   });
   await delay(450);
   const staleAction=await evaluate(()=>{
    document.querySelector('[data-lang="en"]')?.click();
    const status=document.getElementById('official-pilot-status')?.textContent||'';
    const action=document.getElementById('official-pilot-action')?.textContent||'';
    const bias=document.getElementById('official-pilot-bias')?.textContent||'';
    const biasNote=document.getElementById('official-pilot-bias-note')?.textContent||'';
    document.querySelector('[data-asset="BTC"]')?.click();
    document.querySelector('[data-lang="da"]')?.click();
    const quote=document.getElementById('observed-value')?.textContent||'';
    const pair=document.getElementById('pair')?.textContent||'';
    return {status,action,quote,pair,bias,biasNote};
   });
   assert.equal(staleAction.status,'SOURCE UNAVAILABLE','NEXT_OFFLINE_RESURRECTED_CURRENT_COMPASS');
   assert.equal(staleAction.action,'—','NEXT_OFFLINE_RESTORED_CURRENT_ACTION');
   assert.equal(staleAction.bias,'—','NEXT_OFFLINE_RETAINED_BULL_BEAR');
   assert.match(staleAction.biasNote,/No verified Bull\/Bear/,'NEXT_OFFLINE_RETAINED_BIAS_VALIDITY');
   assert.equal(staleAction.quote,'—','NEXT_ASSET_SWITCH_BORROWED_PRIOR_PRICE');
   assert.equal(staleAction.pair,'BTC / USD','NEXT_ASSET_SWITCH_WRONG_SELECTED_PAIR');
  }
 }
 await send('Page.navigate',{url:origin+'next/graph-b/source-graph-b.html'});
 let nested=false;
 for(let i=0;i<40;i++){
  await delay(100);
  nested=await evaluate(()=>document.readyState==='complete'&&!!document.getElementById('chart'));
  if(nested)break;
 }
 assert.ok(nested,'NEXT_NESTED_B_ENTRY_NOT_AVAILABLE');
 assert.deepEqual(responses,[],'NEXT_NESTED_ASSET_MISSING');
 assert.deepEqual(errors,[],'NEXT_NESTED_RUNTIME_EXCEPTION');
 console.log((rootMode?'ROOT':'NEXT')+'_VITE_BROWSER_REAL_CDP_PASS '+JSON.stringify({
  base,engine:'CHROME_HEADLESS_CDP_NOT_SAFARI',results,nested_graph_b:true,
  http_asset_errors:responses.length,js_exceptions:errors.length
 }));
}finally{
 try{socket?.close()}catch{}
 if(browser&&browser.exitCode===null)browser.kill('SIGTERM');
 try{rmSync(profile,{recursive:true,force:true})}catch{}
 await new Promise(resolve=>server.close(resolve));
}
