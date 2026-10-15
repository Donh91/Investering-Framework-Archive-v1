// Chromium CDP-based read-only QA for the single-file source-locked preview.
// No external browser service, npm QA package, AppDeploy, or production deployment.
import assert from 'node:assert/strict';
import {spawn,execFileSync} from 'node:child_process';
import {mkdirSync,mkdtempSync,rmSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {setTimeout as wait} from 'node:timers/promises';
assert.equal(process.argv.length,4,'Usage: browser-preview-qa.mjs <offline.html> <qa-dir>');
const source=resolve(process.argv[2]),out=resolve(process.argv[3]);mkdirSync(out,{recursive:true});
const browser=['google-chrome','google-chrome-stable','chromium'].find(name=>{
  try{execFileSync('which',[name],{stdio:'ignore'});return true;}catch{return false;}
});
assert.ok(browser,'Existing Chromium is required');
const profile=mkdtempSync(join(tmpdir(),'cn-cdp-qa-'));
const child=spawn(browser,['--headless=new','--no-sandbox','--disable-gpu',
  '--disable-dev-shm-usage','--no-first-run','--no-default-browser-check',
  '--disable-extensions','--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'],
  {stdio:['ignore','ignore','pipe']});
let wsUrl='',startupLog='';
child.stderr.on('data',chunk=>{
  startupLog=(startupLog+chunk.toString()).slice(-6000);
  const m=chunk.toString().match(/DevTools listening on (ws:\/\/\S+)/);
  if(m)wsUrl=m[1];
});
try{
  for(let i=0;i<350&&!wsUrl;i++){
    if(child.exitCode!==null)throw Error('Chrome exited '+child.exitCode);
    await wait(100);
  }
  assert.ok(wsUrl,'Chrome debug websocket unavailable after 35s: '+startupLog);
  const ws=new WebSocket(wsUrl),pending=new Map();let id=0;
  await new Promise((ok,bad)=>{
    ws.addEventListener('open',ok,{once:true});
    ws.addEventListener('error',bad,{once:true});
  });
  const runtimeErrors=[];
  ws.addEventListener('message',event=>{
    const e=JSON.parse(event.data);
    if(e.method==='Runtime.exceptionThrown')runtimeErrors.push(e.params?.exceptionDetails?.text??'unknown');
    if(e.id&&pending.has(e.id)){
      const {ok,bad}=pending.get(e.id);pending.delete(e.id);
      e.error?bad(Error(JSON.stringify(e.error))):ok(e.result??{});
    }
  });
  const call=(method,params={},sessionId)=>new Promise((ok,bad)=>{
    const req={id:++id,method,params};
    if(sessionId)req.sessionId=sessionId;
    pending.set(req.id,{ok,bad});ws.send(JSON.stringify(req));
  });
  const {targetId}=await call('Target.createTarget',{url:'about:blank'});
  const {sessionId}=await call('Target.attachToTarget',{targetId,flatten:true});
  await call('Runtime.enable',{},sessionId);
  await call('Page.enable',{},sessionId);
  async function evaluate(expression){
    const response=await call('Runtime.evaluate',{
      expression,returnByValue:true,awaitPromise:true
    },sessionId);
    if(response.exceptionDetails)throw Error('Browser evaluation failure '+JSON.stringify(response.exceptionDetails));
    return response.result?.value;
  }
  const readPaths = [
    '(()=>{',
    "const svg=document.querySelector('#range-visualization svg');",
    "const forecast=svg?.querySelector('.cn-chart-forecast-midpoint');",
    "const actual=svg?.querySelector('.cn-chart-close-path');",
    "const p=[forecast,actual];",
    'return {',
    'inner:innerWidth,scrollWidth:document.documentElement.scrollWidth,',
    'route:location.hash,lang:document.documentElement.lang,',
    "asset:document.querySelector('[data-asset].selected')?.dataset.asset,",
    "hasSource:document.body.textContent.includes('W40'),",
    "forecastNote:document.querySelector('.cn-path-week .range-summary')?.textContent?.trim(),",
    "forecastLegend:document.querySelector('.cn-path-week .cn-legend-forecast')?.textContent?.trim(),",
    "heading:document.querySelector('#cn-path-week-title')?.textContent?.trim(),",
    "mondayClose:document.querySelector('#cn-path-daily-table tbody tr:first-child td:last-child')?.textContent?.trim(),",
    "freezeDisclosure:document.querySelector('#cn-path-freeze-status')?.textContent?.trim(),",
    "weekdays:[...svg.querySelectorAll('.cn-chart-weekday')].map(x=>x.textContent),",
    "axisTicks:[...svg.querySelectorAll('.cn-chart-tick')].map(x=>x.textContent),",
    "revealPhase:document.querySelector('.range-compare-panel')?.dataset.revealPhase,",
    "paths:p.map(x=>Boolean(x&&x.getAttribute('d')?.includes(' C ')&&",
    "x.getBBox().width>100&&getComputedStyle(x).display!=='none'&&getComputedStyle(x).opacity!=='0')),",
    "viewBox:svg?.getAttribute('viewBox')",
    '};})()'
  ].join('');
  // Real browser bounding boxes, not approximate CSS declaration checks.
  // All *visible* buttons on the active route must have 44px targets on phone.
  const inspectMobileTapTargets = `(()=>{
    const visible=[...document.querySelectorAll('button')].filter(el=>{
      const r=el.getBoundingClientRect();
      return r.width>0&&r.height>0&&getComputedStyle(el).visibility!=='hidden';
    });
    return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,
      undersized:visible.filter(el=>{
        const r=el.getBoundingClientRect();
        return r.width<44||r.height<44;
      }).map(el=>{
        const r=el.getBoundingClientRect();
        return {text:el.textContent.trim().slice(0,30),
          width:Math.round(r.width),height:Math.round(r.height)};
      })};
  })()`;
  // Evidence labels are essential, not decorative metadata. Test their
  // computed contrast in Chrome, with exact white/card and canvas backdrops.
  const inspectPathContrast = `(()=>{
    const samples=[
      ['.cn-path-week .section-aside','rgb(246,247,248)','color'],
      ['.cn-path-week .cn-chart-tick','rgb(255,255,255)','fill'],
      ['.cn-path-week .cn-chart-weekday','rgb(255,255,255)','fill'],
      ['.cn-path-week .cn-chart-week','rgb(255,255,255)','fill'],
      ['.cn-path-week .chart-legend small','rgb(255,255,255)','color'],
      ['.cn-path-week .range-summary','rgb(255,255,255)','color'],
      ['.cn-path-week .range-summary span:last-child','rgb(255,255,255)','color']
    ];
    const channels=s=>String(s).match(/[0-9.]+/g)?.slice(0,3).map(Number);
    const l=s=>{
      const rgb=channels(s);
      if(!rgb||rgb.length!==3)return NaN;
      const c=rgb.map(v=>{
        const x=v/255;
        return x<=0.04045?x/12.92:((x+0.055)/1.055)**2.4;
      });
      return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2];
    };
    return samples.map(([selector,background,property])=>{
      const node=document.querySelector(selector);
      const foreground=node&&getComputedStyle(node)[property];
      const a=l(foreground),b=l(background);
      const contrast=(Math.max(a,b)+0.05)/(Math.min(a,b)+0.05);
      return {selector,foreground,contrast:Number(contrast.toFixed(2))};
    });
  })()`;
  for(const width of [390,430]){
    await call('Emulation.setDeviceMetricsOverride',{
      width,height:844,mobile:true,deviceScaleFactor:1
    },sessionId);
    const nav=await call('Page.navigate',{
      url:pathToFileURL(source).href+'#cn-path-week'
    },sessionId);
    assert.ok(!nav.errorText,'File navigation failed: '+nav.errorText);
    let ready=false;
    for(let i=0;i<125;i++){
      ready=await evaluate("Boolean(document.querySelector('#range-visualization .cn-chart-forecast-midpoint')&&document.querySelector('#range-visualization .cn-chart-close-path'))");
      if(ready)break;await wait(100);
    }
    assert.ok(ready,'Both chart paths must render at '+width);
    const mobileTap=await evaluate(inspectMobileTapTargets);
    assert.ok(mobileTap.scrollWidth<=width+1&&mobileTap.undersized.length===0,
      'Phone tap/overflow regression at '+width+'px '+JSON.stringify(mobileTap));
    const contrast=await evaluate(inspectPathContrast);
    assert.ok(contrast.every(x=>Number.isFinite(x.contrast)&&x.contrast>=4.5),
      'Evidence-bearing PATH labels must meet WCAG AA small-text contrast '+JSON.stringify(contrast));
    console.log('PASS PATH source-caption AA contrast '+width+'px '+JSON.stringify(contrast));
    for(const lang of ['da','en']){
      await evaluate("document.querySelector('[data-lang="+JSON.stringify(lang)+"]').click()");
      await wait(200);
      for(const asset of ['BTC','ETH']){
        await evaluate("document.querySelector('[data-asset="+JSON.stringify(asset)+"]').click()");
        await wait(180);
        const proof=await evaluate(readPaths);
        assert.ok(proof.inner===width&&proof.scrollWidth<=width+1&&
          proof.route==='#cn-path-week'&&proof.lang===lang&&proof.asset===asset&&
          proof.hasSource&&proof.paths.every(Boolean)&&proof.revealPhase==='score'&&
          proof.axisTicks?.includes(asset==='BTC'
            ?(lang==='en'?'$85,000':'$85.000')
            :(lang==='en'?'$2,700':'$2.700'))&&
          proof.mondayClose===(asset==='BTC'
            ?(lang==='en'?'$83,500.01':'$83.500,01')
            :(lang==='en'?'$2,688.71':'$2.688,71'))&&
          proof.freezeDisclosure?.startsWith(lang==='en'?'FREEZE':'FRYSNING')&&
          (lang==='en'?
            proof.forecastNote?.includes('derived midpoint line')&&
            proof.forecastNote?.includes('three frozen price ranges')&&
            proof.forecastLegend?.includes('(derived)')&&
            proof.heading?.includes('The frozen week')&&
            proof.weekdays?.join(',')==='Mon,Tue,Wed,Thu,Fri,Sat,Sun':
            proof.forecastNote?.includes('afledt midtlinje')&&
            proof.forecastLegend?.includes('(afledt)')&&
            proof.weekdays?.join(',')==='Man,Tir,Ons,Tor,Fre,Lør,Søn'),
          'Browser QA '+width+' '+lang+' '+asset+' '+JSON.stringify(proof));
        console.log('PASS '+width+' '+lang+' '+asset+' '+JSON.stringify(proof));
        if(lang==='da'&&asset==='BTC'){
          await evaluate("document.querySelector('#range-visualization').scrollIntoView({behavior:'instant',block:'center'})");
          await wait(350);
          const shot=await call('Page.captureScreenshot',{
            format:'png',captureBeyondViewport:false,fromSurface:true
          },sessionId);
          const bytes=Buffer.from(shot.data,'base64');
          const filepath=join(out,'PATH_CHROME_'+width+'.png');
          writeFileSync(filepath,bytes);
          assert.ok(bytes.length>12000,'Blank/tiny Chrome screenshot '+bytes.length+'B '+filepath);
          // The chart-centered shot intentionally excludes the long heading.
          // Also capture the actual hash destination to confirm the sticky
          // header never hides the page's title on an iPhone-sized screen.
          await evaluate("document.getElementById('cn-path-week').scrollIntoView({behavior:'instant',block:'start'})");
          await wait(250);
          const top=await evaluate("Math.round(document.querySelector('#cn-path-week-title').getBoundingClientRect().top)");
          assert.ok(top>=60&&top<260,'PATH heading obscured or offscreen at '+width+'px: '+top);
          const sectionShot=await call('Page.captureScreenshot',{
            format:'png',captureBeyondViewport:false,fromSurface:true
          },sessionId);
          const sectionBytes=Buffer.from(sectionShot.data,'base64');
          writeFileSync(join(out,'PATH_SECTION_'+width+'.png'),sectionBytes);
          assert.ok(sectionBytes.length>12000,'Blank/tiny PATH heading screenshot');
        }
      }
    }
  }
  // 320/360/375px compact iPhones and the 580px breakpoint are separate
  // regression widths: no false acceptance from just modern 390px devices.
  for(const width of [320,360,375,580]){
    await call('Emulation.setDeviceMetricsOverride',{
      width,height:844,mobile:true,deviceScaleFactor:1
    },sessionId);
    const nav=await call('Page.navigate',{
      url:pathToFileURL(source).href+'#cn-path-week'
    },sessionId);
    assert.ok(!nav.errorText,'Compact source navigation failed: '+nav.errorText);
    let ready=false;
    for(let i=0;i<125;i++){
      ready=await evaluate("Boolean(document.querySelector('.cn-chart-close-path'))");
      if(ready)break;
      await wait(100);
    }
    assert.ok(ready,'Compact chart source unavailable at '+width);
    const tap=await evaluate(inspectMobileTapTargets);
    assert.ok(tap.width===width&&tap.scrollWidth<=width+1&&tap.undersized.length===0,
      'Compact iPhone touch/overflow FAIL at '+width+'px '+JSON.stringify(tap));
    console.log('PASS compact mobile '+width+'px, min target 44x44, no overflow');
  }
  // The explicit replay must complete, not leave the solid ACTUAL curve
  // hidden after user interaction. This is deliberately not autoplay.
  await evaluate("document.querySelector('[data-lang=da]').click()");
  await evaluate("document.querySelector('[data-asset=BTC]').click()");
  await evaluate("document.querySelector('#range-replay').click()");
  await wait(2700);
  const replayState=await evaluate("(()=>({phase:document.querySelector('.range-compare-panel')?.dataset.revealPhase,label:document.querySelector('#cn-replay-day')?.textContent,visible:getComputedStyle(document.querySelector('.cn-chart-close-path')).opacity}))()");
  assert.ok(replayState.phase==='score'&&replayState.label?.includes('alle syv')&&replayState.visible==='1',
    'Actual path must fully return after explicit 7-day replay: '+JSON.stringify(replayState));
  // Intermediate tablet widths are easy to miss: the desktop nav used to
  // push the header's trailing buttons outside the viewport at 801–925px.
  // Assert real layout bounds, not merely a successful CSS compilation.
  for(const width of [801,820,900,940]){
    await call('Emulation.setDeviceMetricsOverride',{
      width,height:844,mobile:false,deviceScaleFactor:1
    },sessionId);
    await call('Page.navigate',{url:pathToFileURL(source).href+'#cn-path-week'},sessionId);
    let ready=false;
    for(let i=0;i<125;i++){
      ready=await evaluate("Boolean(document.querySelector('.cn-chart-close-path'))");
      if(ready)break;
      await wait(100);
    }
    assert.ok(ready,'Tablet preview failed to render at '+width);
    await evaluate("document.querySelector('.cn-path-range-details').open=true");
    const state=await evaluate("(()=>{const mast=document.querySelector('.masthead-inner');const end=document.querySelector('.header-actions');return {viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,headerRight:Math.round(end.getBoundingClientRect().right),navVisible:getComputedStyle(document.querySelector('.desktop-nav')).display!=='none',tableVisible:!!document.querySelector('#cn-path-daily-table tbody tr'),chartPresent:!!document.querySelector('.cn-chart-close-path')}})()");
    assert.ok(state.viewport===width&&state.scrollWidth<=width+1&&state.headerRight<=width+1&&
      state.navVisible&&state.tableVisible&&state.chartPresent,
      'Tablet header/forecast must fit at '+width+'px '+JSON.stringify(state));
    console.log('PASS tablet '+width+'px '+JSON.stringify(state));
    if(width===820){
      await evaluate("document.querySelector('.cn-path-range-details').open=false");
      await evaluate("document.getElementById('cn-path-week').scrollIntoView({behavior:'instant',block:'start'})");
      await wait(300);
      const shot=await call('Page.captureScreenshot',{
        format:'png',captureBeyondViewport:false,fromSurface:true
      },sessionId);
      const bytes=Buffer.from(shot.data,'base64');
      writeFileSync(join(out,'PATH_TABLET_820.png'),bytes);
      assert.ok(bytes.length>12000,'Blank tablet screenshot');
    }
  }
  // Desktop first-impression gate: show the *source-owned* action and
  // direction within a standard 900px-high first screen. A beautiful gauge
  // which hides the decision until the next scroll is not a premium UX.
  for(const width of [1024,1280,1440]){
    await call('Emulation.setDeviceMetricsOverride',{
      width,height:900,mobile:false,deviceScaleFactor:1
    },sessionId);
    await call('Page.navigate',{
      url:pathToFileURL(source).href+'#overblik'
    },sessionId);
    let ready=false;
    for(let i=0;i<125;i++){
      ready=await evaluate("Boolean(document.querySelector('#cn-gauge-action')?.textContent.includes('HOLD'))");
      if(ready)break;
      await wait(100);
    }
    assert.ok(ready,'Desktop source action did not load at '+width);
    const desktop=await evaluate("(()=>{const card=document.querySelector('.cn-instrument');const footer=document.querySelector('.cn-instrument-footer');const rect=footer.getBoundingClientRect();const strip=document.querySelector('.preview-ribbon')?.textContent;return {inner:innerWidth,overflow:document.documentElement.scrollWidth,top:Math.round(rect.top),bottom:Math.round(rect.bottom),action:document.querySelector('#cn-gauge-action')?.textContent?.trim(),direction:document.querySelector('#cn-gauge-direction')?.textContent?.trim(),snapshotCaveat:strip?.includes('KILDEFAST SNAPSHOT'),gaugeWidth:Math.round(card.getBoundingClientRect().width)}})()");
    assert.ok(desktop.inner===width&&desktop.overflow<=width+1&&
      desktop.top>=0&&desktop.bottom<=900&&desktop.gaugeWidth<=650&&
      desktop.action?.includes('HOLD')&&desktop.direction?.includes('BULLISH')&&
      desktop.snapshotCaveat,
      'Decision hidden under desktop first-screen fold '+width+'px '+JSON.stringify(desktop));
    console.log('PASS desktop first-screen decision '+width+'px '+JSON.stringify(desktop));
    if(width===1440){
      await wait(230);
      const shot=await call('Page.captureScreenshot',{
        format:'png',captureBeyondViewport:false,fromSurface:true
      },sessionId);
      const bytes=Buffer.from(shot.data,'base64');
      writeFileSync(join(out,'OVERVIEW_DESKTOP_1440.png'),bytes);
      assert.ok(bytes.length>16000,'Blank desktop Overview screenshot');
    }
  }
  assert.deepEqual(runtimeErrors.filter(Boolean),[],'No JavaScript exceptions');
  console.log('PASS all: two lines, 390/430 mobile, 801/820/900/940 desktop-tablet, DA/EN, BTC/ETH, source, hash, scroll-width, real screenshots');
  ws.close();
}finally{
  // Chrome writes profile files asynchronously. Cleanup must never obscure a
  // genuine browser assertion/connection failure with a secondary ENOTEMPTY.
  child.kill('SIGTERM');
  await Promise.race([
    new Promise(done=>child.once('exit',done)),
    wait(2500)
  ]);
  try { rmSync(profile,{recursive:true,force:true,maxRetries:20,retryDelay:150}); }
  catch(err) { console.warn('Non-blocking temporary Chromium profile cleanup:',err.code); }
}
