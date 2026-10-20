/**
 * Premium browser acceptance, no npm dependencies, no workflow/runner creation.
 * Uses the Chrome preinstalled on GitHub-hosted Ubuntu (or CHROME_BIN).
 * Tests the actual built dist/index.html on loopback HTTP and first-party feeds,
 * with true CDP mobile emulation, never pretending to be Apple Safari/VoiceOver.
 * The producer may be stale: ABSTAIN and neutral PATH are valid outputs.
 */
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {createServer} from 'node:http';
import {existsSync,readFileSync,mkdtempSync,rmSync} from 'node:fs';
import {resolve,dirname,extname,join,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {tmpdir} from 'node:os';
import {setTimeout as delay} from 'node:timers/promises';

const dist=resolve(dirname(fileURLToPath(import.meta.url)),'../dist');
const candidates=[process.env.CHROME_BIN,'/usr/bin/google-chrome','/usr/bin/chromium','/usr/bin/chromium-browser'];
const chrome=candidates.find(x=>x&&existsSync(x));
assert.ok(chrome,'PREMIUM_MOBILE_NO_CHROME: Ubuntu runner needs preinstalled Google Chrome');
assert.ok(existsSync(join(dist,'index.html')),'Build public bundle before browser acceptance');

const mime={'.html':'text/html','.mjs':'text/javascript','.js':'text/javascript','.json':'application/json',
 '.css':'text/css','.svg':'image/svg+xml','.png':'image/png','.woff2':'font/woff2','.txt':'text/plain'};
const server=createServer((req,res)=>{
 let parsed;try{parsed=decodeURIComponent(new URL(req.url,'http://localhost').pathname)}catch{res.writeHead(400).end();return}
 const full=resolve(dist,'.'+(parsed==='/'?'/index.html':parsed));
 if(full!==dist&&!full.startsWith(dist+sep)){res.writeHead(403).end();return}
 try{const bytes=readFileSync(full);res.setHeader('Content-Type',mime[extname(full)]||'application/octet-stream');
 res.setHeader('Cache-Control','no-store');res.writeHead(200).end(bytes)}
 catch{res.writeHead(404).end('Not found')}
});
await new Promise((accept,reject)=>server.once('error',reject).listen(0,'127.0.0.1',accept));
const url='http://127.0.0.1:'+server.address().port+'/';
const profile=mkdtempSync(join(tmpdir(),'cn-premium-browser-'));
const browser=spawn(chrome,['--headless=new','--no-sandbox','--disable-gpu','--disable-dev-shm-usage',
 '--no-first-run','--no-default-browser-check','--no-zygote',
 '--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'],{stdio:'ignore'});
let socket;
try{
 let debugPort;
 for(let i=0;i<130;i++){
  if(browser.exitCode!==null)throw Error('Chrome exited '+browser.exitCode);
  try{debugPort=Number(readFileSync(join(profile,'DevToolsActivePort'),'utf8').split('\n')[0]);if(debugPort>0)break}catch{}
  await delay(100);
 }
 assert.ok(debugPort,'NO_CHROME_DEVTOOLS_PORT');
 const pages=await (await fetch('http://127.0.0.1:'+debugPort+'/json')).json();
 const page=pages.find(x=>x.type==='page');
 assert.ok(page?.webSocketDebuggerUrl,'NO_PAGE_CDP');
 socket=new WebSocket(page.webSocketDebuggerUrl);
 await new Promise((accept,reject)=>{socket.onopen=accept;socket.onerror=reject});
 const pending=new Map();let serial=0;const exceptions=[];
 socket.onmessage=evt=>{
  const m=JSON.parse(evt.data);
  if(m.method==='Runtime.exceptionThrown')exceptions.push(m.params?.exceptionDetails?.text||'UNKNOWN_JS_EXCEPTION');
  if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);
   m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result)}
 };
 function send(method,params={}){
  return new Promise((accept,reject)=>{
   const id=++serial;pending.set(id,{resolve:accept,reject});
   socket.send(JSON.stringify({id,method,params}));
   const deadline=setTimeout(()=>{if(pending.has(id)){pending.delete(id);reject(Error('CDP_TIMEOUT '+method))}},10000);
   deadline.unref();
  });
 }
 async function evaluate(fn){
  const out=await send('Runtime.evaluate',{expression:'('+fn.toString()+')()',
   returnByValue:true,awaitPromise:true});
  if(out.exceptionDetails)throw Error('BROWSER_EVAL '+JSON.stringify(out.exceptionDetails));
  return out.result.value;
 }
 await send('Page.enable');await send('Runtime.enable');
 await send('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]});
 const reports=[];
 for(const [width,height] of [[390,844],[430,932]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:true});
  await send('Page.navigate',{url});
  let ready=false;
  for(let i=0;i<90;i++){
   await delay(100);
   const state=await evaluate(()=>({
    loaded:document.readyState==='complete',
    status:document.querySelector('#source-status')?.textContent||'',
    prompt:document.querySelector('#premium-proof-prompt')?.value||''
   }));
   if(state.loaded&&state.prompt.includes('scorebook-index.json')&&
      state.status&&!state.status.includes('Kontrollerer')){ready=true;break}
  }
  assert.ok(ready,'PREMIUM_BROWSER_NOT_READY at '+width+'px');
  const report=await evaluate(async()=>{
   const check=condition=>!!condition, $=s=>document.querySelector(s);
   const safeOverflow=()=>Math.max(document.documentElement.scrollWidth,document.body.scrollWidth)-window.innerWidth;
   const overflow=[safeOverflow()];
   const tabIds=['overview','compass','path','results'];
   const views={};
   for(const id of tabIds){$('[data-tab="'+id+'"]').click();
    views[id]={visible:!$('#view-'+id).hidden,
     exclusive:tabIds.every(key=>$('#view-'+key).hidden===(key!==id)),overflow:safeOverflow()};
    overflow.push(views[id].overflow)}
   $('[data-tab="compass"]').click();
   const before=$('#premium-now-action').textContent;
   const lens={};
   for(const id of ['holder','active','micro']){$('[data-investor-lens="'+id+'"]').click();
    lens[id]={active:$('[data-investor-lens="'+id+'"]').getAttribute('aria-pressed'),
      action:$('#premium-now-action').textContent};
   }
   const five=$('#premium-risk-steps').children.length;
   $('[data-tab="path"]').click();const phases=$('#premium-path-rail').children.length;
   $('[data-tab="results"]').click();
   const en=$('[data-lang="en"]');en.click();
   const enText=$('#tab-results [data-t="tabResults"]').textContent;
   const enPath=$('[data-exp-t="pathPage"]').textContent;
   $('[data-lang="da"]').click();
   const daText=$('#tab-results [data-t="tabResults"]').textContent;
   const daPath=$('[data-exp-t="pathPage"]').textContent;
   const prompt=$('#premium-proof-prompt').value;
   // A deterministic mocked clipboard validates the product click-handler and
   // exact copied original-source audit text, NOT the native iOS clipboard API.
   let copiedText=null;
   Object.defineProperty(navigator,'clipboard',{configurable:true,value:{
    writeText:async text=>{copiedText=text;}
   }});
   $('#premium-proof-copy').click();
   await new Promise(resolve=>setTimeout(resolve,35));
   const proofCopied=!!copiedText&&copiedText===prompt&&
    $('#premium-copy-status').textContent.includes('kopieret');
   const ownerSource=await (await fetch('/data/compass.json',{cache:'no-store'})).json();
   const expiry=ownerSource?.full_stack?.official_freshness?.valid_until_utc;
   const sourceExpired=typeof expiry==='string'&&Number.isFinite(Date.parse(expiry))&&
     Date.now()>=Date.parse(expiry);
   const sourceExpiryShown=sourceExpired?
     $('#source-status').textContent.includes('udløbet')&&
     $('#source-clock').textContent.includes('Kompas gyldigt til'):true;
   const sourceClockText=$('#source-clock').textContent;
   const sourceClock=$('#source-clock').getBoundingClientRect();
   // Only measure touch targets when their owning tab is actually visible.
   // A hidden tab's DOM elements correctly report 0x0, not a 0px product bug.
   const sizes=els=>Array.from(els).map(e=>{
    const q=e.getBoundingClientRect();return {label:e.textContent.trim().slice(0,24),width:q.width,height:q.height}
   });
   const checks=sizes(document.querySelectorAll('.tabs button,.languages button,#premium-proof-copy'));
   $('[data-tab="compass"]').click();
   checks.push(...sizes(document.querySelectorAll('[data-investor-lens],.product-more>summary')));
   $('[data-tab="overview"]').click();
   $('[data-nav-to="path"]').focus();$('[data-nav-to="path"]').click();
   const pathJumpFocus=document.activeElement?.id==='tab-path'&&!$('#view-path').hidden;
   $('[data-tab="overview"]').click();
   const chartButtons=Array.from(document.querySelectorAll('[data-fw-asset]'));
   const chartSource=await (await fetch('/data/latest.json',{cache:'no-store'})).json();
   const model=window.CNWeekChart;
   const eligibleModels=typeof model?.model==='function'&&
     model.model(chartSource,'BTC')!==null&&model.model(chartSource,'ETH')!==null;
   let chart='ABSTAIN_NO_ELIGIBLE_CHART_SOURCE';
   if(typeof model?.model!=='function')chart='FAIL_CHART_LIBRARY_MISSING';
   else if(eligibleModels&&chartButtons.length!==2)chart='FAIL_ELIGIBLE_CHART_CONTROLS_MISSING';
   else if(eligibleModels&&chartButtons.length===2){
    $('[data-fw-asset="ETH"]').click();
    const eth=$('[data-fw-asset="ETH"]').getAttribute('aria-pressed')==='true';
    $('[data-fw-asset="BTC"]').click();
    const btc=$('[data-fw-asset="BTC"]').getAttribute('aria-pressed')==='true';
    chart=eth&&btc?'PASS':'FAIL';
   }
   overflow.push(safeOverflow());
   return {width:innerWidth,overflow:Math.max(...overflow),views,lens,before,five,phases,
    enText,enPath,daText,daPath,promptHasProof:prompt.includes('scorebook-index.json')&&
      prompt.includes('SHA-256')&&prompt.includes('source_commit'),
    scorePrice:$('#premium-proof-price-status').textContent,
    scoreDirection:$('#premium-proof-direction-status').textContent,
    scorePullback:$('#premium-proof-pullback-status').textContent,
    proofCopied,sourceExpiryShown,pathJumpFocus,
    clockRight:sourceClock.right,clockLeft:sourceClock.left,clockWidth:sourceClock.width,
    clockHeight:sourceClock.height,clockText:sourceClockText,buttons:checks,chart,
    reducedMotion:getComputedStyle(document.documentElement).scrollBehavior};
  });
  reports.push(report);
  assert.equal(report.width,width,'Wrong CDP viewport');
  assert.ok(report.overflow<=2,'Horizontal page overflow on '+width+'px '+JSON.stringify(report));
  assert.ok(report.clockText&&report.clockText!=='—'&&
     /Kompas gyldigt til|Sidste levering/.test(report.clockText)&&
     report.clockWidth>0&&report.clockHeight>0,'Source clock missing or placeholder '+width);
  assert.ok(report.clockRight<=width+2&&report.clockLeft>=-2,'Source expiry outside viewport '+width);
  assert.ok(Object.values(report.views).every(q=>q.visible&&q.exclusive&&q.overflow<=2),
   'Multiple panels visible or one of four tabs clipped at '+width);
  assert.equal(report.five,5,'Five official ordinal risk categories must be visible');
  assert.equal(report.phases,10,'Full PATH must have ten stages, even when expired');
  assert.ok(Object.values(report.lens).every(q=>q.active==='true'&&q.action===report.before),
   'Investor lens changed official action');
  assert.equal(report.enText,'Results','English tab content switch missing');
  assert.equal(report.daText,'Resultater','Danish tab restoration missing');
  assert.equal(report.enPath,'The market cycle','English PATH translation missing');
  assert.equal(report.daPath,'Markeds­cyklussen','Danish PATH restoration missing');
  assert.ok(report.promptHasProof,'Proof AI prompt lacks original source/hash anchors');
  assert.ok(report.proofCopied,'AI verification copy button omitted or changed the original public audit prompt');
  assert.ok(report.sourceExpiryShown,'Expired Official Compass not disclosed in served homepage status');
  assert.ok(report.pathJumpFocus,'Overview-to-PATH anchor lost keyboard focus in hidden panel');
  assert.ok([report.scorePrice,report.scoreDirection,report.scorePullback].every(x=>
     typeof x==='string'&&x.trim()!==''&&x.trim()!=='—'&&x.trim()!=='UNAVAILABLE'),
    'One of the three public Proof families missing or a placeholder');
  assert.ok(report.scoreDirection.includes('Ingen verificeret')&&
    report.scorePullback.includes('Ingen verificeret'),'Edge claim escaped unverified source policy');
  assert.ok(report.buttons.every(x=>x.width>=44&&x.height>=44),
   'Mobile touch target smaller than 44px '+JSON.stringify(report.buttons.filter(x=>x.width<44||x.height<44)));

  assert.ok(!report.chart.startsWith('FAIL'),'BTC/ETH chart controls failed or valid chart source was dropped: '+report.chart);
  assert.equal(report.reducedMotion,'auto','Reduced-motion page scrolling is not disabled');
 }
 assert.deepEqual(exceptions,[],'Unexpected browser JavaScript exception');
 console.log('PASS real Chrome mobile 390x844 and 430x932; tabs, languages, PATH, source-clock, risk, proof, chart '+JSON.stringify(reports));
} finally {
 try{socket?.close()}catch{}
 browser.kill('SIGTERM');
 await Promise.race([new Promise(accept=>browser.once('close',accept)),delay(1500)]);
 if(browser.exitCode===null)browser.kill('SIGKILL');
 server.close();
 await delay(150);
 try{rmSync(profile,{recursive:true,force:true})}catch{}
}
