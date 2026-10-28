/**
 * Premium browser acceptance, no npm dependencies, no workflow/runner creation.
 * Uses the Chrome preinstalled on GitHub-hosted Ubuntu (or CHROME_BIN).
 * Tests the actual built dist/index.html on loopback HTTP and first-party feeds,
 * with true CDP mobile emulation, never pretending to be Apple Safari/VoiceOver.
 * The producer may be stale: ABSTAIN and neutral PATH are valid outputs.
 */
import assert from 'node:assert/strict';
import {assertExactMobileViewport} from './viewport-metrics.mjs';
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
// Chrome may intermittently fail to initialize on a busy GitHub-hosted runner.
// A single failed Chrome bootstrap must NOT bypass any browser assertions or
// permanently block the Pages release. A second *fresh* isolated profile is
// allowed only for the startup handshake; both failures still fail the job.
let profile=null,browser=null,socket;
try{
 let debugPort;
 const startupFailures=[];
 for(let attempt=1;attempt<=2&&!debugPort;attempt++){
  profile=mkdtempSync(join(tmpdir(),'cn-premium-browser-'));
  const flags=['--headless=new','--no-sandbox','--disable-gpu',
    '--disable-dev-shm-usage','--no-first-run','--no-default-browser-check',
    ...(attempt===1?['--no-zygote']:[]),
    '--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'];
  browser=spawn(chrome,flags,{stdio:['ignore','ignore','pipe']});
  let startupError='',startupStderr='';
  browser.on('error',e=>{startupError=String(e.message||e)});
  browser.stderr?.on('data',chunk=>{startupStderr=(startupStderr+chunk.toString()).slice(-4000)});
  for(let i=0;i<120;i++){
   if(startupError||browser.exitCode!==null||browser.signalCode!==null)break;
   try{
    const port=Number(readFileSync(join(profile,'DevToolsActivePort'),'utf8').split('\n')[0]);
    if(Number.isInteger(port)&&port>0){debugPort=port;break}
   }catch{}
   await delay(100);
  }
  if(debugPort)break;
  startupFailures.push({attempt,exitCode:browser.exitCode,signal:browser.signalCode,
    error:startupError,stderr:startupStderr.slice(-1800)});
  // Ensure no stale browser/profile is reused by the second attempt.
  if(browser.exitCode===null&&browser.signalCode===null){
   browser.kill('SIGTERM');
   await Promise.race([new Promise(resolve=>browser.once('close',resolve)),delay(1000)]);
   if(browser.exitCode===null&&browser.signalCode===null)browser.kill('SIGKILL');
  }
  try{rmSync(profile,{recursive:true,force:true})}catch{}
  profile=null;browser=null;
  if(attempt===1)await delay(400);
 }
 assert.ok(debugPort,'NO_CHROME_DEVTOOLS_PORT '+JSON.stringify(startupFailures));
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
  // Before any tab or language clicks, record whether CDP mobile emulation
  // already produced a larger layout viewport. Never override the observation.
  const beforeViewport=await evaluate(()=>({
   width:innerWidth,height:innerHeight,
   documentClientWidth:document.documentElement.clientWidth,
   documentScrollWidth:document.documentElement.scrollWidth,
   bodyScrollWidth:document.body?.scrollWidth??null,
   visualViewportWidth:window.visualViewport?.width??null,
   screenWidth:screen.width,
   viewportMeta:document.querySelector('meta[name="viewport"]')?.content??null
  }));
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
   const sourceActionCode=$('#premium-action-code')?.textContent||'';
   const sourceActionMeaning=$('#premium-action-meaning')?.textContent||'';
   const actionReconciled=sourceActionCode.includes('OFFICIAL · HOLD_WAIT')?
     before==='AFVENT'&&sourceActionMeaning.includes('afventsignal'):
     !sourceActionCode.includes('OFFICIAL · HOLD_WAIT')&&before.length>0;

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
   const enChart=$('#view-overview .cn-chart-jump')?.textContent;
   const enPath=$('[data-exp-t="pathPage"]').textContent;
   $('[data-lang="da"]').click();
   const daText=$('#tab-results [data-t="tabResults"]').textContent;
   const daChart=$('#view-overview .cn-chart-jump')?.textContent;
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
     $('#source-clock').textContent.includes('Kompas udløb'):true;
   const sourceClockText=$('#source-clock').textContent;
   const priceBanner=$('#price-source-warning');
   const publicLive=(await (await fetch('/data/latest.json',{cache:'no-store'})).json())?.public_live_precision;
   const ageCutoff=publicLive?.hourly_price_path?.observed_through_utc;
   const priceAge=Date.parse(ageCutoff);
   const ageSla=Number(publicLive?.freshness_sla_minutes)*60000;
   const priceIsStale=Number.isFinite(priceAge)&&ageSla>0&&Date.now()-priceAge>ageSla;
   const priceStatusIndependent=!!priceBanner&&
     (priceIsStale?
       (!priceBanner.hidden&&priceBanner.textContent.includes('Kursgraf forældet')&&
        priceBanner.textContent.includes('Kompas vurderes separat')):
       (priceBanner.hidden||priceBanner.textContent.includes('uden verificerede timepriser')));
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
   // Hallmark-inspired adverse text test: simulate official source expiry
   // without changing original source data or browser fixtures. The previous
   // iPhone screenshot showed UNAVAILABLE split onto a dangling final letter.
   const actionNode=$('#action'), originalAction=actionNode.textContent;
   actionNode.textContent='UNAVAILABLE';
   const adverseRange=document.createRange();
   adverseRange.selectNodeContents(actionNode);
   const actionPieces=Array.from(adverseRange.getClientRects()).filter(q=>q.width>0);
   const actionCard=actionNode.closest('.decision-main').getBoundingClientRect();
   const unavailableOneLine=actionPieces.length===1&&
     actionPieces[0].left>=actionCard.left+1&&
     actionPieces[0].right<=actionCard.right-1;
   actionNode.textContent=originalAction;
   // Real Chrome test: the approved chart must be easily discoverable on mobile,
   // not buried below unrelated PATH/risk cards despite valid data in the DOM.
   const graphLink=$('#view-overview .cn-chart-jump');
   const graphHost=$('#official-path-chart');
   // Video QA, verify real root, not AppDeploy synthetic visual reference.
   const rootBStyle=!!graphHost?.classList.contains('frozen-week-chart')&&
     getComputedStyle(graphHost).backgroundColor==='rgb(10, 23, 41)'&&
     getComputedStyle($('.fw-quote')).backgroundColor==='rgb(10, 23, 41)'&&
     getComputedStyle($('.fw-quote strong')).color==='rgb(247, 251, 255)';
   const approvedBFrame=document.querySelector('.chart-area[data-approved-design="B"]');
   const approvedBProbe={
     outer:!!approvedBFrame,
     frameBg:approvedBFrame?getComputedStyle(approvedBFrame).backgroundColor:null,
     chart:!!approvedBFrame?.querySelector('#official-path-chart.frozen-week-chart'),
     title:approvedBFrame?.querySelector('.chart-b-title')?.textContent?.trim()||null,
     eyebrow:approvedBFrame?.querySelector('.chart-b-eyebrow')?.textContent?.trim()||null,
     quoteBg:approvedBFrame?.querySelector('.fw-quote')?
       getComputedStyle(approvedBFrame.querySelector('.fw-quote')).backgroundColor:null,
     inlineStyle:approvedBFrame?.getAttribute('style'),
     matchesApproved:approvedBFrame?.matches('.chart-area[data-approved-design="B"]'),
     matchingBackgroundRules:[...document.styleSheets].flatMap(sheet=>{
       let rules=[];try{rules=[...sheet.cssRules]}catch{}
       return rules.filter(rule=>rule.selectorText&&approvedBFrame?.matches(rule.selectorText)&&
         (rule.style?.getPropertyValue('background')||rule.style?.getPropertyValue('background-color'))).
         map(rule=>({href:sheet.href,selector:rule.selectorText,bg:rule.style.getPropertyValue('background'),
            color:rule.style.getPropertyValue('background-color'),
            important:rule.style.getPropertyPriority('background')})).slice(-12);
     }),
     styles:[...document.styleSheets].map(sheet=>{
       let rules=[];try{rules=[...sheet.cssRules]}catch{}
       return {href:sheet.href,ruleCount:rules.length,approvedBRule:rules.some(rule=>rule.selectorText?.includes('chart-area[data-approved-design'))};
     })
   };
   const approvedBVisual=approvedBProbe.outer&&
     approvedBProbe.frameBg==='rgb(255, 255, 255)'&&
     approvedBProbe.chart&&
     approvedBProbe.title==='Weekly Outlook · B'&&
     /FROSSEN PROGNOSE|FROZEN FORECAST/.test(approvedBProbe.eyebrow)&&
     approvedBProbe.quoteBg==='rgb(10, 23, 41)';
   const bOuterControls=document.querySelectorAll('.chart-b-assets [data-b-asset]').length===2 &&
     !!document.querySelector('#chart-b-scrub-range') &&
     document.querySelector('.chart-area[data-approved-design="B"] .fw-horizons')!==null;
   const rootIsNotDemo=!document.querySelector('.cn-forward-demo a[href*="appdeploy.ai"]');
   const pathRail=$('#premium-path-rail');
   const contiguousPath=!!pathRail&&getComputedStyle(pathRail).display==='block'&&
     pathRail.querySelectorAll('.path-node').length===10&&
     getComputedStyle(pathRail,'::before').content!=='none';
   const sourceRef=pathRail?.querySelectorAll('.path-node[data-kind="reference"]').length??0;
   const sourceSafePhases=sourceRef<=1;
   const liveBoxes=Array.from(document.querySelectorAll('#proof-live-windows .proof-live-window'));
   const liveStatus=document.querySelector('#proof-live-status')?.textContent||'';
   const liveProofSafe=liveBoxes.length===3?
     liveBoxes.every(b=>b.querySelector('.proof-live-window-score')?.textContent?.trim()&&
       b.querySelector('.proof-live-window-hours')?.textContent?.trim()):
     liveBoxes.length===0&&/mangler|unavailable/i.test(liveStatus);
   const proofSimple=!!document.querySelector('.proof-primer')&&
     !!document.querySelector('.proof-journey')&&
     document.querySelector('.proof-window-details')?.open===false&&
     !!document.querySelector('#premium-proof-copy');
   const ring=$('#premium-balance-dial');
   const compassGraphic=!!ring&&['verified','unavailable'].includes(ring.dataset.state)&&
     ring.getAttribute('aria-label')?.length>12;
   const officialBull=Number($('#premium-bull')?.textContent||NaN);
   const compassAngle=ring?.style.getPropertyValue('--dial-needle-angle')?.trim();
   const evidenceNeedle=ring?.dataset.state==='verified'&&Number.isInteger(officialBull)?
     compassAngle===String((officialBull-5)*14)+'deg':
     compassAngle==='0deg';
   const graphTop=graphHost?.getBoundingClientRect().top-
      $('#view-overview').getBoundingClientRect().top;
   const pathBeforeGraphJump=location.pathname;
   graphLink?.click();
   const graphClickSafe=location.pathname===pathBeforeGraphJump&&
     !location.pathname.endsWith('/vnext/')&&document.activeElement===graphHost&&
     !$('#view-overview').hidden;
   const graphQuickAccess=!!graphLink&&graphLink.getAttribute('href')==='../#official-path-chart'&&
     graphHost?.tabIndex===-1&&Number.isFinite(graphTop)&&graphTop<740&&
     graphLink.textContent.includes('Se grafen')&&graphClickSafe;
   checks.push(...sizes(graphLink?[graphLink]:[]));
   const chartButtons=Array.from(document.querySelectorAll('[data-fw-asset]'));
   const chartSource=await (await fetch('/data/latest.json',{cache:'no-store'})).json();
   const model=window.CNWeekChart;
   const hourlySource=chartSource.public_live_precision?.hourly_price_path;
   const actualModel=model?.model?.(chartSource,'BTC');
   // Both languages must tell a screen reader that the observed source is
   // STALE, not silently describe an old green curve as a live quote.
   const previousChartLanguage=window.CNI18n?.language||'da';
   let staleChartAccessible=false;
   if(actualModel&&typeof model.graphDescription==='function'){
     window.CNI18n={language:'da'};
     const daStale=model.graphDescription({...actualModel,stale:true});
     const daFresh=model.graphDescription({...actualModel,stale:false});
     window.CNI18n={language:'en'};
     const enStale=model.graphDescription({...actualModel,stale:true});
     const enFresh=model.graphDescription({...actualModel,stale:false});
     window.CNI18n={language:previousChartLanguage};
     staleChartAccessible=daStale.startsWith('FORÆLDET OBSERVATION.')&&
       enStale.startsWith('STALE OBSERVATION.')&&
       !daFresh.startsWith('FORÆLDET OBSERVATION.')&&
       !enFresh.startsWith('STALE OBSERVATION.')&&
       daStale.includes('Grøn fuldt optrukken linje')&&
       enStale.includes('Green solid line');
   }
   const actualPlan=actualModel?model.linePlan(actualModel):null;
   // Source-exact original low/high edges, never a fabricated seven-day close.
   const ranges=actualModel?model.rangePlan(actualModel):[];
   const originalRangesValid=!!actualModel&&
     (actualModel.daily.length===7?ranges.length===0:
       ranges.length===3&&ranges.every((r,i)=>{
         const first=i===0?0:i===1?2:4,last=i===0?1:i===1?3:6;
         const source=actualModel.rows[i];
         return r.low.length===2&&r.high.length===2&&
           r.low[0].time===actualModel.days[first].time&&
           r.low[1].time===actualModel.days[last].closeTime&&
           r.high[0].time===r.low[0].time&&
           r.high[1].time===r.low[1].time&&
           r.low.every(p=>p.value===source.forecast_low)&&
           r.high.every(p=>p.value===source.forecast_high);
       }));
   const hourlyPublished=hourlySource?.contract==='CN_PUBLIC_HOURLY_PRICE_PATH_v1'&&
      Array.isArray(hourlySource.BTC)&&hourlySource.BTC.length>0;
   const hourlyCurveProof=!hourlyPublished?true:!!actualModel&&
     actualModel.hourly.length===hourlySource.BTC.length&&
     actualPlan.actualRuns.reduce((sum,run)=>sum+run.length,0)===hourlySource.BTC.length&&
     (actualModel.daily.length===7?actualPlan.forecast.length===7:actualPlan.forecast.length===0);
   const actualPointCount=actualPlan?.actualRuns.reduce((sum,run)=>sum+run.length,0)??0;
   const hourlyPointCount=hourlySource?.BTC?.length??0;
   const forecastPointCount=actualPlan?.forecast.length??0;
   // Original B is two curves ONLY if the forecast issuer published daily
   // expected closes; show the source-denial banner otherwise, in both assets.
   const issuerDenied=!!actualModel&&actualModel.daily.length!==7;
   const missingForecastBanner=document.querySelector('#official-path-chart .fw-forecast-not-issued');

   const actualStatus=document.querySelector('.fw-progress-actual')?.textContent||'';
   const forecastStatus=document.querySelector('.fw-progress-forecast')?.textContent||'';
   const eligibleModels=typeof model?.model==='function'&&
     model.model(chartSource,'BTC')!==null&&model.model(chartSource,'ETH')!==null;
   const graphBSourceHonesty=!eligibleModels||!issuerDenied||
      !!missingForecastBanner?.textContent.includes('BLÅ PROGNOSEKURVE IKKE UDSTEDT');
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
   // On the real Premium site, 7/14/21 are functional buttons, not
   // separate AppDeploy links. The 14/21 extension is a TIME AXIS only.
   let forwardButtons='ABSTAIN_NO_ELIGIBLE_CHART_SOURCE';
   if(eligibleModels){
     const buttons=Array.from(document.querySelectorAll('[data-fw-horizon]'));
     if(buttons.length!==3)forwardButtons='FAIL_MISSING_HORIZON_BUTTONS';
     else{
       const hit=n=>{
         const btn=document.querySelector('[data-fw-horizon="'+n+'"]');
         btn.click();
         const chosen=document.querySelector('[data-fw-horizon="'+n+'"]');
         const notice=document.querySelector('.fw-horizon-availability')?.textContent||'';
         return chosen?.getAttribute('aria-pressed')==='true'&&
           (n===7?/seven.day frozen range|syv originale forventede|original seven.day expected/i.test(notice)||/kun originale syvdagesintervaller/i.test(notice):notice.includes('8–'+n));
       };
       const all=hit(14)&&hit(21)&&hit(7);
       forwardButtons=all?'PASS':'FAIL_HORIZON_TOGGLE_OR_SOURCE_DISCLOSURE';
       checks.push(...sizes(document.querySelectorAll('[data-fw-horizon]')));
     }
   }
   overflow.push(safeOverflow());
   return {width:innerWidth,height:innerHeight,
    documentClientWidth:document.documentElement.clientWidth,
    documentScrollWidth:document.documentElement.scrollWidth,
    visualViewportWidth:window.visualViewport?.width??null,
    viewportMeta:document.querySelector('meta[name="viewport"]')?.content??null,
    overflow:Math.max(...overflow),views,lens,before,five,phases,
    enText,enPath,daText,daPath,enChart,daChart,graphQuickAccess,graphTop,promptHasProof:prompt.includes('scorebook-index.json')&&
      prompt.includes('SHA-256')&&prompt.includes('source_commit'),
    unavailableOneLine,staleChartAccessible,rootBStyle,approvedBVisual,bOuterControls,approvedBProbe,rootIsNotDemo,contiguousPath,sourceSafePhases,proofSimple,liveProofSafe,compassGraphic,evidenceNeedle,
    scorePrice:$('#premium-proof-price-status').textContent,
    scoreDirection:$('#premium-proof-direction-status').textContent,
    scorePullback:$('#premium-proof-pullback-status').textContent,
    proofCopied,sourceExpiryShown,priceStatusIndependent,actionReconciled,pathJumpFocus,
    clockRight:sourceClock.right,clockLeft:sourceClock.left,clockWidth:sourceClock.width,
    clockHeight:sourceClock.height,clockText:sourceClockText,buttons:checks,chart,forwardButtons,
    hourlyCurveProof,originalRangesValid,graphBSourceHonesty,hourlyPointCount,actualPointCount,forecastPointCount,actualStatus,forecastStatus,
    reducedMotion:getComputedStyle(document.documentElement).scrollBehavior};
  });
  reports.push(report);
  if(beforeViewport.documentScrollWidth>width){
   const offenders=await evaluate(()=>[...document.querySelectorAll('body *')].map(el=>({id:el.id,cls:String(el.className?.baseVal||el.className||'').slice(0,40),left:Math.round(el.getBoundingClientRect().left),right:Math.round(el.getBoundingClientRect().right)})).filter(q=>q.right>390+8||q.left<-8).sort((a,b)=>b.right-a.right).slice(0,20));
   console.log('WIDTH_DEBUG',width,JSON.stringify(offenders));
  }
  assertExactMobileViewport(report,width,height,beforeViewport);
  assert.ok(report.overflow<=2,'Horizontal page overflow on '+width+'px '+JSON.stringify(report));
  assert.ok(report.clockText&&report.clockText!=='—'&&
     /Kompas gyldigt til|Kompas udløb|Sidste levering/.test(report.clockText)&&
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
   assert.equal(report.enChart,'View chart · BTC / ETH ↓','English chart shortcut missing');
   assert.equal(report.daChart,'Se grafen · BTC / ETH ↓','Danish chart shortcut missing');
   assert.ok(report.graphQuickAccess,'Approved B graph must be discoverable near overview top: '+report.graphTop);
  assert.ok(report.rootBStyle,'Official CN chart must be navy from quote to plot');
  assert.ok(report.approvedBVisual,'Approved B white editorial card / navy source chart mismatch at '+width+': '+JSON.stringify(report.approvedBProbe));
  assert.ok(report.bOuterControls,'Real B must have external source-bound BTC/ETH selector, scrubber and 7/14/21 controls');
  assert.ok(report.rootIsNotDemo,'Public product should not link to competing synthetic demo');
  assert.ok(report.contiguousPath&&report.sourceSafePhases,'PATH should be one source-honest dotted sequence');
  assert.ok(report.proofSimple,'Proof explanation and progressive detail not rendered');
  assert.ok(report.liveProofSafe,'Current-week source-joined D1–2/D3–4/D5–7 proof sequencing missing or fake');
  assert.ok(report.compassGraphic,'Official evidence dial missing or not source-labelled');
  assert.ok(report.evidenceNeedle,'Dial needle should match verified 0–10 Bull/Bear evidence, not a hardcoded angle');
  assert.equal(report.enPath,'The market cycle','English PATH translation missing');
  assert.equal(report.daPath,'Markeds­cyklussen','Danish PATH restoration missing');
  assert.ok(report.promptHasProof,'Proof AI prompt lacks original source/hash anchors');
  assert.ok(report.proofCopied,'AI verification copy button omitted or changed the original public audit prompt');
  assert.ok(report.sourceExpiryShown,'Expired Official Compass not disclosed in served homepage status');
  assert.ok(report.actionReconciled,'Official Compass readable action must preserve original verified code without creating BUY/SELL');
  assert.ok(report.priceStatusIndependent,'Public hourly source freshness must be disclosed separately from Compass');
  assert.ok(report.pathJumpFocus,'Overview-to-PATH anchor lost keyboard focus in hidden panel');
  assert.ok([report.scorePrice,report.scoreDirection,report.scorePullback].every(x=>
     typeof x==='string'&&x.trim()!==''&&x.trim()!=='—'&&x.trim()!=='UNAVAILABLE'),
    'One of the three public Proof families missing or a placeholder');
  assert.ok(report.scoreDirection.includes('Ingen verificeret')&&
    report.scorePullback.includes('Ingen verificeret'),'Edge claim escaped unverified source policy');
  assert.ok(report.buttons.every(x=>x.width>=44&&x.height>=44),
   'Mobile touch target smaller than 44px '+JSON.stringify(report.buttons.filter(x=>x.width<44||x.height<44)));

  assert.ok(!report.chart.startsWith('FAIL'),'BTC/ETH chart controls failed or valid chart source was dropped: '+report.chart);
  assert.ok(!report.forwardButtons.startsWith('FAIL'),'Approved B 7/14/21 horizon controls failed: '+report.forwardButtons);
  assert.ok(report.unavailableOneLine,'The source-unavailable action must not split or clip on narrow mobile');
  assert.ok(report.staleChartAccessible,'Stale public observed prices need explicit DA/EN screen-reader warning');
  assert.ok(report.hourlyCurveProof,'Verified hourly actual source dropped / gaps fabricated / forecast filled');
  assert.ok(report.graphBSourceHonesty,'Approved Graph B must visibly acknowledge absence of source-issued blue expected-close curve');
  assert.ok(report.originalRangesValid,'Three frozen source windows must form six exact low/high edges');
  if(report.hourlyPointCount>0){
    assert.equal(report.actualPointCount,report.hourlyPointCount,'Actual line must contain exactly each source-valid hour');
    assert.ok(report.actualStatus.includes('timesluk')&&report.forecastStatus,'Progress display must explain observed vs forecast');
  }
  assert.equal(report.reducedMotion,'auto','Reduced-motion page scrolling is not disabled');
 }
 assert.deepEqual(exceptions,[],'Unexpected browser JavaScript exception');
 console.log('PASS real Chrome mobile 390x844 and 430x932; tabs, languages, PATH, source-clock, risk, proof, chart '+JSON.stringify(reports));
} finally {
 try{socket?.close()}catch{}
 if(browser){
  if(browser.exitCode===null&&browser.signalCode===null){
   browser.kill('SIGTERM');
   await Promise.race([new Promise(resolve=>browser.once('close',resolve)),delay(1500)]);
  }
  if(browser.exitCode===null&&browser.signalCode===null)browser.kill('SIGKILL');
 }
 server.close();
 await delay(150);
 if(profile)try{rmSync(profile,{recursive:true,force:true})}catch{}
}
