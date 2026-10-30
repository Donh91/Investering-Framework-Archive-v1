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
  await send('Page.navigate',{url:origin+'next/'});
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
  assert.ok(report.rootPath.endsWith(base+'next/'),'NEXT_WRONG_BASEPATH');
  // Current NEXT pilot is retained for source/rollback coverage; root audited below.
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

 // The third built page must load its REAL bundled PRO/Graph B source modules.
 // A static HTML string test alone cannot detect missing JS/CSS or broken events.
 const unified=[];
 for(const width of [390,430]){
  await send('Emulation.setDeviceMetricsOverride',{
    width,height:width===390?844:932,deviceScaleFactor:1,mobile:true});
  await send('Page.navigate',{url:origin+'next/unified.html'});
  let ready=false;
  for(let attempt=0;attempt<100;attempt++){
   await delay(100);
   ready=await evaluate(()=>document.readyState==='complete'&&
     !!document.getElementById('compass-pro')&&!!document.getElementById('chart')&&
     (document.getElementById('pro-source-status')?.textContent||'')!==
       'Kontrollerer officiel kilde og gyldighed…');
   if(ready)break;
  }
  assert.ok(ready,'UNIFIED_MODULE_BOOT_MISSING:'+width);
  const measured=await evaluate(()=>{
   const id=x=>document.querySelectorAll('[id="'+x+'"]').length;
   const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);
   const pro=document.getElementById('compass-pro'),graph=document.getElementById('variant-panel');
   const source=document.getElementById('pro-source-status')?.textContent||'';
   const nav=document.querySelector('.premium-entry-navigation');
   document.querySelector('[data-lang="en"]')?.click();
   const english=document.getElementById('pro-heading')?.textContent;
   document.querySelector('[data-lang="da"]')?.click();
   const danish=document.getElementById('pro-heading')?.textContent;
   document.querySelector('[data-investor-lens="micro"]')?.click();
   return {
    width:innerWidth,overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,
    source,english,danish,
    micro:document.querySelector('[data-investor-lens="micro"]')?.getAttribute('aria-pressed'),
    uniqueIds:new Set(ids).size===ids.length,
    singleton:['chart','variant-panel','compass-pro','premium-now-action',
      'premium-risk-steps','premium-path-rail','official-path-view','proof-explorer',
      'pro-reentry-state','cn-forward-source-status'].every(x=>id(x)===1),
    noLegacy:!document.getElementById('official-product-pilot'),
    noindex:document.querySelector('meta[name="robots"]')?.content?.includes('noindex'),
    navBeforePro:nav?.getBoundingClientRect().top<pro?.getBoundingClientRect().top,
    proBeforeGraph:!!(pro.compareDocumentPosition(graph)&Node.DOCUMENT_POSITION_FOLLOWING),
    tabMode:document.body.classList.contains('cn-tabbed-ui'),
    tabDefault:!pro.hidden&&graph.hidden,
    tabs:nav?.querySelectorAll('[role="tab"]').length
   };
  });
  assert.equal(measured.width,width,'UNIFIED_WRONG_VIEWPORT');
  assert.ok(measured.overflow<=2,'UNIFIED_OVERFLOW:'+JSON.stringify(measured));
  assert.ok(measured.uniqueIds&&measured.singleton&&measured.noLegacy,
    'UNIFIED_DUPLICATE_OR_MISSING_NODE:'+JSON.stringify(measured));
  assert.ok(measured.noindex&&measured.navBeforePro&&measured.proBeforeGraph&&
    measured.tabMode&&measured.tabDefault&&measured.tabs===4,
    'UNIFIED_PREVIEW_OR_TABS_MISMATCH:'+JSON.stringify(measured));
  const switching=await evaluate(()=>{
    const click=k=>document.querySelector('[data-premium-nav="'+k+'"]')?.click();
    const comp=document.getElementById('compass-pro');
    const graph=document.getElementById('variant-panel');
    const path=document.getElementById('official-path-view');
    const proof=document.getElementById('proof-explorer');
    click('graph'); const graphVisible=!graph.hidden&&comp.hidden&&
      document.getElementById('chart').getBoundingClientRect().width>0;
    click('path'); const pathVisible=!path.hidden&&graph.hidden;
    click('proof'); const proofVisible=!proof.hidden&&path.hidden;
    click('compass'); const returned=!comp.hidden&&proof.hidden;
    return {graphVisible,pathVisible,proofVisible,returned,hash:location.hash};
  });
  assert.ok(switching.graphVisible&&switching.pathVisible&&switching.proofVisible&&
    switching.returned&&switching.hash==='#compass-pro',
    'UNIFIED_TAB_SWITCH_BROKEN:'+JSON.stringify(switching));
  assert.equal(measured.english,'Compass PRO','UNIFIED_EN_LABEL');
  assert.equal(measured.danish,'Kompas PRO','UNIFIED_DA_LABEL');
  assert.equal(measured.micro,'true','UNIFIED_MICRO_LENS_BROKEN');
  assert.ok(measured.source&&measured.source!=='—','UNIFIED_SOURCE_STATUS_MISSING');
  assert.deepEqual(errors,[],'UNIFIED_JS_EXCEPTIONS');
  assert.deepEqual(responses,[],'UNIFIED_HTTP_ASSET_FAILURES');
  unified.push({width,source_status:true,one_graph_one_pro:true,interactive:true});
 }


 if(rootMode){
  const released=[];
  for(const width of [390,430]){
   await send('Emulation.setDeviceMetricsOverride',{width,height:width===390?844:932,
    deviceScaleFactor:1,mobile:true});
   await send('Page.navigate',{url:origin});
   let ready=false;
   for(let attempt=0;attempt<100;attempt++){
    await delay(100);
    ready=await evaluate(()=>document.readyState==='complete'&&
     !!document.getElementById('compass-pro')&&
     (document.getElementById('pro-source-status')?.textContent||'')!==
      'Kontrollerer officiel kilde og gyldighed…');
    if(ready)break;
   }
   assert.ok(ready,'ROOT_UNIFIED_NOT_BOOTED:'+width);
   const report=await evaluate(()=>{
    const id=x=>document.querySelectorAll('[id="'+x+'"]').length;
    const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);
    const graph=document.getElementById('variant-panel');
    const pro=document.getElementById('compass-pro');
    const source=document.getElementById('pro-source-status')?.textContent||'';
    document.querySelector('[data-lang="en"]')?.click();
    const en=document.getElementById('pro-heading')?.textContent;
    document.querySelector('[data-lang="da"]')?.click();
    const da=document.getElementById('pro-heading')?.textContent;
    document.querySelector('[data-investor-lens="micro"]')?.click();
    return {
     width:innerWidth,overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,
     source,en,da,micro:document.querySelector('[data-investor-lens="micro"]')?.getAttribute('aria-pressed'),
     quick13:document.getElementById('cn-horizon-13')?.textContent,
     horizonOverview:[...document.querySelectorAll('.cn-horizon-card')].map(el=>({
      valid:el.dataset.sourceCurrent,
      direction:el.querySelector('.cn-horizon-direction strong')?.textContent,
      arrow:el.querySelector('.cn-horizon-arrow')?.textContent,
      balance:el.querySelector('.cn-evidence small')?.textContent,
      summary:el.querySelector('p')?.textContent
     })),
     riskCollapsed:!document.querySelector('.cn-risk-more')?.open,
     readerCollapsed:!document.querySelector('.cn-reader-expand')?.open,
     positionsCollapsed:!document.querySelector('.cn-position-guide')?.open,
     rotationRows:document.querySelectorAll('#cn-rotation-classes [role="listitem"]').length,
     rotationHasUnknownRaw:[...document.querySelectorAll('#cn-rotation-classes [role="listitem"]')].some(el=>
       /\b(?:HARD_WAIT|UNAVAILABLE|WAIT|HOLD)\b/.test(el.textContent)),
     nowcast:document.getElementById('premium-now-direction')?.textContent,
     actionCode:document.getElementById('premium-action-code')?.textContent,
     actionWhy:document.getElementById('premium-action-meaning')?.textContent||'',
     firstFold:{
      viewport:innerHeight,
      actionTop:Math.round(document.getElementById('premium-now-action')?.getBoundingClientRect().top??9999),
      h12Bottom:Math.round(document.getElementById('premium-now-direction')?.closest('.product-cell')?.getBoundingClientRect().bottom??9999),
      h13Bottom:Math.round(document.getElementById('cn-horizon-13')?.closest('.product-cell')?.getBoundingClientRect().bottom??9999),
      sourceVisible:getComputedStyle(document.getElementById('pro-source-status')).display!=='none',
      navSingleRow:Math.round(document.querySelector('.premium-entry-navigation')?.getBoundingClientRect().height??9999)<=50,
      navFits:document.querySelector('.premium-entry-navigation').scrollWidth<=document.querySelector('.premium-entry-navigation').clientWidth+2,
      archiveA11y:document.querySelector('[data-premium-nav="official"]')?.getAttribute('aria-label')==='Forrige version'
     },
     riskQuick:document.querySelectorAll('#cn-risk-quick-steps .risk-step').length,
     officialRisk:document.querySelectorAll('#premium-risk-steps .risk-step').length,
     futurePath:document.getElementById('cn-alt-milestone-eta')?.textContent,
     pathSteps:document.querySelectorAll('#premium-path-rail .path-node').length,
     hiddenB:getComputedStyle(document.querySelector('#variant-panel .alt-token')).display==='none',
     cleanTitle:!document.title.includes('Graph B'),
     preview:!!document.querySelector('meta[name="robots"][content*="noindex"]'),
     unique:new Set(ids).size===ids.length,
     singleton:['chart','variant-panel','compass-pro','premium-now-action',
      'premium-risk-steps','premium-path-rail','official-path-view',
      'proof-explorer','pro-reentry-state','cn-forward-source-status'].every(x=>id(x)===1),
     old:!!document.getElementById('official-product-pilot'),
     homepage:document.body.classList.contains('premium-home'),
     order:!!(pro.compareDocumentPosition(graph)&Node.DOCUMENT_POSITION_FOLLOWING),
     rollback:document.querySelector('.premium-entry-canonical')?.getAttribute('href'),
     data:[...document.querySelectorAll('.premium-meta-links a')].map(x=>x.getAttribute('href'))
    };
   });
   assert.equal(report.width,width,'ROOT_UNIFIED_VIEWPORT_WRONG');
   assert.ok(report.overflow<=2,'ROOT_UNIFIED_OVERFLOW:'+JSON.stringify(report));
   assert.ok(report.homepage&&!report.preview&&!report.old,'ROOT_PROMOTED_LEGACY_OR_PREVIEW');
   assert.ok(report.unique&&report.singleton&&report.order,'ROOT_UNIFIED_COMPETING_SOURCE');
   assert.equal(report.rollback,'./vnext/','ROOT_NO_PRIOR_VERSION');
   assert.ok(['./data/latest.json','./data/compass.json'].every(x=>report.data.includes(x)),
      'ROOT_SOURCE_DATA_LINKS');
   assert.equal(report.en,'Compass PRO','ROOT_PRO_EN');
   assert.equal(report.da,'Kompas PRO','ROOT_PRO_DA');
   assert.equal(report.micro,'true','ROOT_MICRO_LENS');
   assert.ok(report.horizonOverview.length===3&&
     report.horizonOverview.every(x=>x.direction?.length>1&&x.arrow?.length>0&&x.balance?.length>4)&&
     report.riskCollapsed&&report.readerCollapsed&&report.positionsCollapsed&&
     report.rotationRows>0&&!report.rotationHasUnknownRaw&&
     report.horizonOverview.every(x=>/Evidenspoint|Evidence points|Ingen verificeret evidensbalance|No verified evidence balance/.test(x.balance)),
     'ROOT_SOURCE_BOUND_OVERVIEW_NOT_VISIBLE:'+JSON.stringify(report.horizonOverview));
   assert.ok(report.actionWhy.length>22&&!report.actionWhy.includes('HOLD_WAIT'),
     'ROOT_VERDICT_NO_ADAPTIVE_PLAIN_LANGUAGE_EXPLANATION:'+JSON.stringify(report));
   assert.ok(report.nowcast&&!report.nowcast.includes('_')&&
     report.actionCode&&!report.actionCode.includes('HOLD_WAIT'),
     'ROOT_RAW_INTERNAL_STATE_IN_FIRST_FOLD:'+JSON.stringify({nowcast:report.nowcast,actionCode:report.actionCode}));
   assert.ok(report.firstFold.sourceVisible&&report.firstFold.navSingleRow&&report.firstFold.navFits&&report.firstFold.archiveA11y&&
     report.firstFold.actionTop<report.firstFold.h12Bottom&&
     report.firstFold.h12Bottom<=report.firstFold.viewport-20&&
     report.firstFold.h13Bottom<=report.firstFold.viewport-20,
     'ROOT_FIRSTFOLD_OFFICIAL_ACTION_AND_BOTH_HORIZONS_NOT_VISIBLE:'+JSON.stringify(report.firstFold));
   assert.ok(report.quick13&&report.riskQuick===5&&report.officialRisk===5,
     'ROOT_SOURCE_BOUND_12H_1_3D_AND_FIVE_RISK_STAGES:'+JSON.stringify(report));
   assert.equal(report.pathSteps,10,'ROOT_TEN_CYCLE_STAGES');
   assert.ok(report.futurePath==='Ingen verificeret ETA'||report.futurePath==='No verified ETA',
     'ROOT_INVENTED_ALTSEASON_COUNTDOWN:'+JSON.stringify(report));
   assert.ok(report.hiddenB&&report.cleanTitle,'ROOT_INTERNAL_VARIANT_B_STILL_VISIBLE');
   assert.ok(report.source&&report.source!=='—','ROOT_NO_SOURCE_STATUS');
   assert.deepEqual(errors,[],'ROOT_BROKEN_JS');
   assert.deepEqual(responses,[],'ROOT_BROKEN_ASSET');
   // Source-reader user journey: real DOM interaction at each mobile width.
   // This does not change or mutate the original Official Compass decision.
   const reader=await evaluate(()=>{
    document.querySelector('.cn-reader-expand').open=true;
    const $=id=>document.getElementById(id);
    const select=id=>document.querySelector('[data-cn-reader-horizon="'+id+'"]');
    const periods=[...document.querySelectorAll('[data-cn-reader-horizon]')];
    const actionBefore=$('premium-now-action')?.textContent;
    const tabsBefore=document.querySelectorAll('.premium-entry-navigation [role="tab"]').length;
    const first=select('NEXT_1_3D')?.getAttribute('aria-pressed')==='true';
    select('NEXT_5_7D')?.click();
    const week=select('NEXT_5_7D')?.getAttribute('aria-pressed')==='true';
    select('NEXT_2_3W')?.click();
    const mid=select('NEXT_2_3W')?.getAttribute('aria-pressed')==='true';
    select('CYCLE_ALTCOINS_3_8W')?.click();
    const long=select('CYCLE_ALTCOINS_3_8W')?.getAttribute('aria-pressed')==='true';
    document.querySelector('[data-cn-reader-lens="hodl"]')?.click();
    const hodl=document.querySelector('[data-cn-reader-lens="hodl"]')?.getAttribute('aria-pressed')==='true';
    const guide=$('cn-reader-lens-note')?.textContent||'';
    const glossary=document.querySelector('.cn-reader-glossary');
    glossary.open=true;
    const count=glossary.querySelectorAll('tbody tr').length;
    document.querySelector('[data-lang="en"]')?.click();
    const enTitle=$('cn-reader-title')?.textContent;
    document.querySelector('[data-lang="da"]')?.click();
    const daTitle=$('cn-reader-title')?.textContent;
    select('NEXT_1_3D')?.click();
    return {
      periods:periods.length,first,week,mid,long,hodl,guide,
      count,glossaryOpen:glossary.open,enTitle,daTitle,
      source:$('cn-reader-source')?.textContent||'',
      direction:$('cn-reader-direction')?.textContent||'',
      why:$('cn-reader-why')?.textContent||'',
      watch:$('cn-reader-watch')?.textContent||'',
      originalActionPreserved:actionBefore===$('premium-now-action')?.textContent,
      tabsPreserved:tabsBefore===4&&document.querySelectorAll('.premium-entry-navigation [role="tab"]').length===4,
      overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth
    };
   });
   assert.ok(reader.periods===4&&reader.first&&reader.week&&reader.mid&&reader.long&&
     reader.hodl&&reader.count===5&&reader.glossaryOpen&&
     reader.enTitle==='What is Compass seeing ahead?'&&
     reader.daTitle==='Hvad viser Kompas fremad?'&&
     reader.guide.length>20&&reader.source.length>15&&reader.direction.length>2&&
     reader.why.length>20&&!reader.watch.includes('Hold øje med: Hold øje med')&&
     !reader.watch.includes('Watch for: Watch')&&
     reader.originalActionPreserved&&reader.tabsPreserved&&reader.overflow<=2,
     'ROOT_COMPASS_READER_UX_FAIL:'+JSON.stringify(reader));
   // Visual acceptance of the actual new, active source-reader (not only DOM).
   if(process.env.GITHUB_EVENT_NAME==='pull_request'){
    const locationReady=await evaluate(()=>{
      const panel=document.querySelector('.cn-reader');
      if(!panel)return false;
      document.querySelector('.cn-reader-expand').open=true;
      panel.scrollIntoView({block:'start',behavior:'instant'});
      return getComputedStyle(panel).display!=='none'&&panel.getBoundingClientRect().width>250;
    });
    assert.equal(locationReady,true,'ROOT_COMPASS_READER_VISUAL_NOT_AVAILABLE');
    await delay(120);
    const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
    assert.ok(shot.data?.length>1000,'ROOT_COMPASS_READER_SCREENSHOT_MISSING');
    console.log('CN_READER_SCREENSHOT_'+width+'_BEGIN');
    for(const chunk of shot.data.match(/.{1,8000}/g))
      console.log('CN_READER_SCREENSHOT_'+width+'_PART '+chunk);
    console.log('CN_READER_SCREENSHOT_'+width+'_END');
    await evaluate(()=>{
     document.querySelector('.cn-reader-expand').open=false;
     document.querySelector('.cn-risk-more').open=false;
     window.scrollTo({top:0,behavior:'instant'});
    });
   }
   // Independent first-screen QA: capture BEFORE scrolling to the chart.
   // This specifically guards the owner's request for both short horizons
   // visible next to the live action on a normal 390/430 iPhone viewport.
   if(process.env.GITHUB_EVENT_NAME==='pull_request'){
    const firstFoldShot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
    assert.ok(firstFoldShot.data?.length>1000,'FIRSTFOLD_SCREENSHOT_MISSING');
    console.log('CN_FIRSTFOLD_SCREENSHOT_'+width+'_BEGIN');
    for(const chunk of firstFoldShot.data.match(/.{1,8000}/g))
     console.log('CN_FIRSTFOLD_SCREENSHOT_'+width+'_PART '+chunk);
    console.log('CN_FIRSTFOLD_SCREENSHOT_'+width+'_END');
   }
   // Disclosures remain optional while the real five-class rail stays visible.
   const disclosure=await evaluate(()=>{
    const risk=document.querySelector('.cn-risk-more');
    const legend=document.querySelector('.cn-position-guide');
    const proof=document.querySelector('.cn-reader-expand');
    risk.open=true;legend.open=true;
    const state={
     riskOpen:risk.open,
     legendOpen:legend.open,
     glossaryTerms:legend.querySelectorAll('#cn-position-terms dt').length,
     riskStages:document.querySelectorAll('#cn-risk-quick-steps .risk-step').length,
     rotationRows:document.querySelectorAll('#cn-rotation-classes [role="listitem"]').length,
     action:document.getElementById('premium-now-action')?.textContent,
     legendExplainsNoMandatorySequence:
      /ikke aktive signaler|not an active|mandatory/.test(
       document.getElementById('cn-positions-disclaimer')?.textContent?.toLowerCase()||''),
     readerClosed:!proof.open
    };
    risk.open=false;legend.open=false;
    return state;
   });
   assert.ok(disclosure.riskOpen&&disclosure.legendOpen&&
     disclosure.glossaryTerms===8&&disclosure.riskStages===5&&
     disclosure.rotationRows>0&&disclosure.readerClosed&&
     disclosure.legendExplainsNoMandatorySequence,
     'ROOT_DISCREET_DISCLOSURE_FAILED:'+JSON.stringify(disclosure));
   if(process.env.GITHUB_EVENT_NAME==='pull_request'){
    const visible=await evaluate(()=>{
     const panel=document.querySelector('.cn-risk-quick');
     if(!panel||panel.hidden)return false;
     panel.scrollIntoView({block:'start',behavior:'instant'});
     return panel.getBoundingClientRect().width>280;
    });
    assert.equal(visible,true,'ROOT_PULLBACK_RAIL_VISUAL_MISSING');
    await delay(120);
    const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
    assert.ok(shot.data?.length>1000,'ROOT_PULLBACK_SCREENSHOT_MISSING');
    console.log('CN_OVERVIEW_RISK_SCREENSHOT_'+width+'_BEGIN');
    for(const chunk of shot.data.match(/.{1,8000}/g))
     console.log('CN_OVERVIEW_RISK_SCREENSHOT_'+width+'_PART '+chunk);
    console.log('CN_OVERVIEW_RISK_SCREENSHOT_'+width+'_END');
   }
   // DESIGN GATE: real rendered Chrome pixels of the EXACT staged root.
   // Read via GitHub CI logs before merge; no invented visual QA receipt.
   if(process.env.GITHUB_EVENT_NAME==='pull_request'){
    const position=await evaluate(()=>{
     const box=document.querySelector('#variant-panel');
     if(!box)return false;
     document.querySelector('[data-premium-nav="graph"]')?.click();
     if(box.hidden)return false;
     box.scrollIntoView({block:'start',behavior:'instant'});
     return true;
    });
    assert.equal(position,true,'VISUAL_QA_CHART_NOT_FOUND');
    await delay(150);
    const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
    assert.ok(shot.data?.length>1000,'VISUAL_QA_SCREENSHOT_MISSING');
    console.log('CN_DESIGN_SCREENSHOT_'+width+'_BEGIN');
    for(const chunk of shot.data.match(/.{1,8000}/g))console.log('CN_DESIGN_SCREENSHOT_'+width+'_PART '+chunk);
    console.log('CN_DESIGN_SCREENSHOT_'+width+'_END');
   }
   // Live negative control on the RELEASED root, not only the /next pilot.
   // Deliberately break BOTH public feed requests after initial boot. A stale
   // cached BUY/SELL or next-gate must never survive a failed refresh.
   if(width===430){
    await evaluate(()=>{
     window.fetch=async()=>{throw Error('UNIFIED_ROOT_INTENTIONAL_OFFLINE_TEST')};
     Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});
     document.dispatchEvent(new Event('visibilitychange'));
     return true;
    });
    await delay(500);
    const offline=await evaluate(()=>({
     source:document.getElementById('pro-source-status')?.textContent||'',
     current:document.getElementById('compass-pro')?.dataset.sourceCurrent,
     gate:document.getElementById('pro-next-gate')?.textContent||'',
     reentry:document.getElementById('pro-reentry-state')?.textContent||'',
     action:document.getElementById('premium-now-action')?.textContent||'',
     firstfoldRisk:document.getElementById('cn-risk-quick-state')?.textContent||'',
     firstfoldHorizon:document.getElementById('cn-horizon-13')?.textContent||'',
     cards:[...document.querySelectorAll('.cn-horizon-card')].map(x=>({
      valid:x.dataset.sourceCurrent,bar:x.querySelector('.cn-evidence-rail span')?.style.width,
      balance:x.querySelector('.cn-evidence small')?.textContent
     })),
     rotation:document.querySelectorAll('#cn-rotation-classes [role="listitem"]').length
    }));
    assert.match(offline.source,/Indlæsning mislykkedes|Source fetch failed/,
      'ROOT_FAILED_REFRESH_KEPT_PREVIOUS_SOURCE:'+JSON.stringify(offline));
    assert.equal(offline.current,'false','ROOT_OFFLINE_STILL_CURRENT');
    assert.equal(offline.reentry,'UNAVAILABLE','ROOT_OFFLINE_REENTRY_LEAK');
    // AFVENTER contains the substring "ENTER"; do not mistake the
    // exact fail-closed source-wait state for an ENTER trading instruction.
    assert.equal(offline.action,'AFVENTER KILDE',
      'ROOT_OFFLINE_DID_NOT_FAIL_CLOSED_TO_SOURCE_WAIT:'+JSON.stringify(offline));
    assert.match(offline.firstfoldRisk,/afventer nye data|awaiting fresh data/i,
      'ROOT_OFFLINE_RISK_ORDINAL_WAS_NOT_CLEARED:'+JSON.stringify(offline));
    assert.equal(offline.rotation,0,'ROOT_OFFLINE_ROTATION_STALE_SOURCE');
   assert.ok(offline.cards.length===3&&offline.cards.every(x=>x.valid==='false'&&
     (x.bar==='0%'||!x.bar)&&!x.balance.includes('Bull 5')),
     'ROOT_OFFLINE_HORIZON_EVIDENCE_NOT_CLEARED:'+JSON.stringify(offline.cards));
   assert.match(offline.firstfoldHorizon,/Afventer nye data|Awaiting updated data/,
      'ROOT_OFFLINE_FUTURE_HORIZON_WAS_NOT_CLEARED:'+JSON.stringify(offline));
    assert.match(offline.gate,/Afventer|Awaiting/,'ROOT_OFFLINE_GATE_LEAK');
   }
   released.push({width,oneB:true,onePRO:true,source:true});
  }
  // Desktop pixels complete the same two-gate visual inspection.
  if(process.env.GITHUB_EVENT_NAME==='pull_request'){
   await send('Emulation.setDeviceMetricsOverride',{width:1440,height:960,deviceScaleFactor:1,mobile:false});
   await send('Page.navigate',{url:origin});
   let desktopReady=false;
   for(let attempt=0;attempt<80;attempt++){
    await delay(100);
    desktopReady=await evaluate(()=>document.readyState==='complete'&&
      !!document.querySelector('#variant-panel #chart')&&
      document.getElementById('observed-value')?.textContent!=='—');
    if(desktopReady)break;
   }
   assert.ok(desktopReady,'DESKTOP_VISUAL_SOURCE_NOT_READY');
   const desktopLayout=await evaluate(()=>{
    const tab=document.querySelector('[data-premium-nav="graph"]');
    const panel=document.querySelector('#variant-panel');
    tab?.click();
    if(!panel||panel.hidden)return {error:'GRAPH_TAB_NOT_VISIBLE'};
    panel.scrollIntoView({block:'start',behavior:'instant'});
    return {width:innerWidth,overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,
     graphVisible:panel.getBoundingClientRect().width>0,
     graphSelected:tab?.getAttribute('aria-selected')==='true',
     svgVisible:document.getElementById('chart')?.getBoundingClientRect().width>0};
   });
   assert.ok(desktopLayout.width===1440&&desktopLayout.overflow<=2&&
     desktopLayout.graphVisible&&desktopLayout.graphSelected&&desktopLayout.svgVisible,
     'DESKTOP_VISUAL_GRAPH_TAB_NOT_RENDERED:'+JSON.stringify(desktopLayout));
   await delay(150);
   const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
   assert.ok(shot.data?.length>1000,'DESKTOP_SCREENSHOT_MISSING');
   console.log('CN_DESIGN_SCREENSHOT_1440_BEGIN');
   for(const chunk of shot.data.match(/.{1,8000}/g))console.log('CN_DESIGN_SCREENSHOT_1440_PART '+chunk);
   console.log('CN_DESIGN_SCREENSHOT_1440_END');
  }
  console.log('ROOT_UNIFIED_CHROME_CDP_PASS '+JSON.stringify(released));
 }

 console.log((rootMode?'ROOT':'NEXT')+'_VITE_BROWSER_REAL_CDP_PASS '+JSON.stringify({
  base,engine:'CHROME_HEADLESS_CDP_NOT_SAFARI',results,nested_graph_b:true,unified,
  http_asset_errors:responses.length,js_exceptions:errors.length
 }));
}finally{
 try{socket?.close()}catch{}
 if(browser&&browser.exitCode===null)browser.kill('SIGTERM');
 try{rmSync(profile,{recursive:true,force:true})}catch{}
 await new Promise(resolve=>server.close(resolve));
}
