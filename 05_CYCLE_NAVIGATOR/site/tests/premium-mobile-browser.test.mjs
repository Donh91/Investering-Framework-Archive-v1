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
    views[id]={visible:!$('#view-'+id).hidden,overflow:safeOverflow()};
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
   const sourceClock=$('#source-clock').getBoundingClientRect();
   const checks=Array.from(document.querySelectorAll('.tabs button,.languages button,[data-investor-lens],#premium-proof-copy,.product-more>summary')).map(e=>{
    const q=e.getBoundingClientRect();return {label:e.textContent.trim().slice(0,24),width:q.width,height:q.height}
   });
   $('[data-tab="overview"]').click();
   const chartButtons=Array.from(document.querySelectorAll('[data-fw-asset]'));
   let chart='ABSTAIN_NO_ELIGIBLE_CHART_CONTROLS';
   if(chartButtons.length===2){$('[data-fw-asset="ETH"]').click();
    const eth=$('[data-fw-asset="ETH"]').getAttribute('aria-pressed')==='true';
    $('[data-fw-asset="BTC"]').click();
    const btc=$('[data-fw-asset="BTC"]').getAttribute('aria-pressed')==='true';
    chart=eth&&btc?'PASS':'FAIL'}
   overflow.push(safeOverflow());
   return {width:innerWidth,overflow:Math.max(...overflow),views,lens,before,five,phases,
    enText,enPath,daText,daPath,promptHasProof:prompt.includes('scorebook-index.json')&&
      prompt.includes('SHA-256')&&prompt.includes('source_commit'),
    scorePrice:$('#premium-proof-price-status').textContent,
    scoreDirection:$('#premium-proof-direction-status').textContent,
    scorePullback:$('#premium-proof-pullback-status').textContent,
    clockRight:sourceClock.right,clockLeft:sourceClock.left,buttons:checks,chart,
    reducedMotion:getComputedStyle(document.documentElement).scrollBehavior};
  });
  reports.push(report);
  assert.equal(report.width,width,'Wrong CDP viewport');
  assert.ok(report.overflow<=2,'Horizontal page overflow on '+width+'px '+JSON.stringify(report));
  assert.ok(report.clockRight<=width+2&&report.clockLeft>=-2,'Source expiry outside viewport '+width);
  assert.ok(Object.values(report.views).every(q=>q.visible&&q.overflow<=2),'One of four tabs clipped at '+width);
  assert.equal(report.five,5,'Five official ordinal risk categories must be visible');
  assert.equal(report.phases,10,'Full PATH must have ten stages, even when expired');
  assert.ok(Object.values(report.lens).every(q=>q.active==='true'&&q.action===report.before),
   'Investor lens changed official action');
  assert.equal(report.enText,'Results','English tab content switch missing');
  assert.equal(report.daText,'Resultater','Danish tab restoration missing');
  assert.equal(report.enPath,'The market cycle','English PATH translation missing');
  assert.equal(report.daPath,'Markeds­cyklussen','Danish PATH restoration missing');
  assert.ok(report.promptHasProof,'Proof AI prompt lacks original source/hash anchors');
  assert.ok(report.scoreDirection&&report.scorePullback,'Edge status must never be a fabricated number');
  assert.ok(report.buttons.every(x=>x.width>=43&&x.height>=43),'Mobile touch target smaller than 44px');
  assert.ok(report.chart!=='FAIL','BTC/ETH chart asset toggling failed');
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
