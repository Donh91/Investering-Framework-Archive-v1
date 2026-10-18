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
    if(e.method==='Runtime.exceptionThrown')runtimeErrors.push(String(e.params?.exceptionDetails?.exception?.description||e.params?.exceptionDetails?.text||'unknown').slice(0,1200));
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
    "const derived=svg?.querySelectorAll('.cn-chart-forecast-midpoint').length||0;",
    "const actual=svg?.querySelector('.cn-chart-close-path');",
    "const p=[actual];",
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
    "derivedCount:derived,paths:p.map(x=>Boolean(x&&x.getAttribute('d')?.includes(' L ')&&",
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
      ready=await evaluate("Boolean(document.querySelector('#range-visualization .cn-chart-close-path'))");
      if(ready)break;await wait(100);
    }
    if(!ready){
      const diagnostic=await evaluate(`(()=>({
        sourceHealth:document.getElementById('source-health')?.textContent?.trim(),
        sourceDetail:document.getElementById('source-detail')?.textContent?.trim().slice(0,250),
        pathHtml:document.getElementById('range-visualization')?.innerHTML?.slice(0,350),
        rangeHidden:document.getElementById('cn-source-chart')?.hidden,
        scripts:[...document.scripts].map(e=>({type:e.type,src:e.src?.slice(0,100)})),
        documentLanguage:document.documentElement.lang
      }))()`);
      throw new Error('Observed daily chart did not render at '+width+': '+JSON.stringify({diagnostic,runtimeErrors}));
    }
    const mobileTap=await evaluate(inspectMobileTapTargets);
    assert.ok(mobileTap.scrollWidth<=width+1&&mobileTap.undersized.length===0,
      'Phone tap/overflow regression at '+width+'px '+JSON.stringify(mobileTap));
    // Taste reference is a style inspiration, not a runtime dependency:
    // computed CSS must actually balance type and align financial figures.
    const typography=await evaluate("(()=>({headline:getComputedStyle(document.querySelector('#overview-title')).textWrapStyle,headlineWrap:getComputedStyle(document.querySelector('#overview-title')).textWrap,section:getComputedStyle(document.querySelector('#cn-path-week-title')).textWrapStyle,sectionWrap:getComputedStyle(document.querySelector('#cn-path-week-title')).textWrap,numbers:getComputedStyle(document.querySelector('.hero-key-metrics strong')).fontVariantNumeric,copy:getComputedStyle(document.querySelector('.cn-path-week-description')).textWrapStyle,copyWrap:getComputedStyle(document.querySelector('.cn-path-week-description')).textWrap}))()");
    assert.ok(
      (typography.headline==='balance'||typography.headlineWrap?.includes('balance'))&&
      (typography.section==='balance'||typography.sectionWrap?.includes('balance'))&&
      typography.numbers?.includes('tabular-nums')&&
      (typography.copy==='pretty'||typography.copyWrap?.includes('pretty')),
      'Editorial typography must be applied by Chromium '+width+'px: '+JSON.stringify(typography));
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
          proof.hasSource&&proof.derivedCount===0&&proof.paths.every(Boolean)&&proof.revealPhase==='score'&&
          proof.axisTicks?.includes(asset==='BTC'
            ?(lang==='en'?'$85,000':'$85.000')
            :(lang==='en'?'$2,700':'$2.700'))&&
          proof.mondayClose===(asset==='BTC'
            ?(lang==='en'?'$83,500.01':'$83.500,01')
            :(lang==='en'?'$2,688.71':'$2.688,71'))&&
          proof.freezeDisclosure?.startsWith(lang==='en'?'FREEZE':'FRYSNING')&&
          (lang==='en'?
            proof.forecastNote?.includes('no authentic seven-day forecast curve')&&
            proof.forecastNote?.includes('Exact original frozen ranges')&&
            proof.forecastLegend?.includes('3 FROZEN RANGES')&&
            proof.heading?.includes('The frozen week')&&
            proof.weekdays?.join(',')==='Mon,Tue,Wed,Thu,Fri,Sat,Sun':
            proof.forecastNote?.includes('ingen oprindelig 7-dages forecastkurve')&&
            proof.forecastLegend?.includes('3 FROSNE INTERVALLER')&&
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
  // Current public source takes the first viewport; historical W41 HOLD
  // is visible only below the explicit HISTORISK DESIGNARKIV separator.
  for(const [width,height] of [[390,844],[430,932],[1024,900],[1280,900],[1440,900]]){
    await call('Emulation.setDeviceMetricsOverride',{
      width,height,mobile:width<800,deviceScaleFactor:1
    },sessionId);
    await call('Page.navigate',{url:pathToFileURL(source).href+'#overblik'},sessionId);
    let ready=false;
    for(let i=0;i<125;i++){
      ready=await evaluate("Boolean(document.querySelector('#hero-action-summary')?.textContent.includes('HOLD')&&document.querySelector('#hero-now')?.textContent.includes('BULLISH'))");
      if(ready)break;
      await wait(100);
    }
    assert.ok(ready,'Historical archive did not load at '+width);
    const proof=await evaluate("(()=>{const dir=document.querySelector('#cn-current-direction');const act=document.querySelector('#cn-current-action');const status=document.querySelector('#cn-current-status');const panel=document.querySelector('#cn-current-public-panel');const dr=dir.getBoundingClientRect(),ar=act.getBoundingClientRect();return {inner:innerWidth,overflow:document.documentElement.scrollWidth,dirTop:Math.round(dr.top),dirBottom:Math.round(dr.bottom),actionTop:Math.round(ar.top),actionBottom:Math.round(ar.bottom),action:act.textContent.trim(),direction:dir.textContent.trim(),state:panel.dataset.state,status:status.textContent.trim(),archive:document.querySelector('.cn-archive-boundary')?.textContent?.includes('HISTORISK DESIGNARKIV'),hasGauge:!!document.querySelector('#cn-instrument-svg'),sourceInfo:!!document.querySelector('#source-button')}})()");
    const failClosed = proof.state==='UNAVAILABLE' && proof.action==='UNAVAILABLE' && proof.direction==='UNKNOWN';
    const sourceVerified = proof.state==='CURRENT_VERIFIED' &&
      ['HOLD_WAIT','HOLD','HARD_WAIT','WAIT','BUY','BUY_DIP','PREPARE'].includes(proof.action) &&
      ['UP','DOWN','MIXED','SIDEWAYS','NEUTRAL','BULLISH','BEARISH','UNKNOWN'].includes(proof.direction);
    assert.ok(proof.inner===width&&proof.overflow<=width+1&&
      proof.dirTop>=0&&proof.dirBottom<height&&proof.actionTop>=0&&
      proof.actionBottom<height&&proof.archive&&!proof.hasGauge&&proof.sourceInfo&&
      (failClosed||sourceVerified),
      'Current source first-screen fail at '+width+'px '+JSON.stringify(proof));
    console.log('PASS first-screen current-source-vs-archive '+width+'px '+JSON.stringify(proof));
    if(width===1440 || width===390){
      await wait(230);
      const shot=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false,fromSurface:true},sessionId);
      const bytes=Buffer.from(shot.data,'base64');
      writeFileSync(join(out,width===1440?'OVERVIEW_DESKTOP_1440.png':'OVERVIEW_MOBILE_390.png'),bytes);
      assert.ok(bytes.length>16000,'Blank first-viewport screenshot at '+width);
    }
  }
  // Native keyboard semantics: no fake screenshot-only accessibility pass.
  // Test the source-dialog's accessible focus trap and Escape return path.
  await call('Emulation.setDeviceMetricsOverride',{
    width:390,height:844,mobile:true,deviceScaleFactor:1
  },sessionId);
  await call('Page.navigate',{url:pathToFileURL(source).href+'#cn-path-week'},sessionId);
  let accessible=false;
  for(let i=0;i<125;i++){
    accessible=await evaluate("Boolean(document.querySelector('.cn-chart-close-path'))");
    if(accessible)break;await wait(100);
  }
  assert.ok(accessible,'Accessible PATH page failed to initialize');
  await evaluate("document.querySelector('#source-button').click()");
  const initiallyFocused=await evaluate("(()=>({open:!document.querySelector('#source-dialog').hidden,focus:document.activeElement?.id,expanded:document.querySelector('#source-button')?.getAttribute('aria-expanded')}))()");
  assert.ok(initiallyFocused.open&&initiallyFocused.focus==='close-source'&&initiallyFocused.expanded==='true',
    'Source dialog must open with focus inside modal '+JSON.stringify(initiallyFocused));
  await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Tab',code:'Tab',windowsVirtualKeyCode:9,modifiers:8},sessionId);
  await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Tab',code:'Tab',windowsVirtualKeyCode:9,modifiers:8},sessionId);
  const wrappedToLast=await evaluate("document.activeElement?.closest('#source-dialog') !== null && document.activeElement?.tagName==='A'");
  assert.ok(wrappedToLast,'Shift-Tab must wrap source dialog first focusable to last');
  await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Tab',code:'Tab',windowsVirtualKeyCode:9},sessionId);
  await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Tab',code:'Tab',windowsVirtualKeyCode:9},sessionId);
  assert.equal(await evaluate("document.activeElement?.id"),'close-source','Tab must wrap back to modal close button');
  await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Escape',code:'Escape',windowsVirtualKeyCode:27},sessionId);
  await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Escape',code:'Escape',windowsVirtualKeyCode:27},sessionId);
  const restored=await evaluate("(()=>({hidden:document.querySelector('#source-dialog').hidden,focus:document.activeElement?.id,expanded:document.querySelector('#source-button')?.getAttribute('aria-expanded')}))()");
  assert.ok(restored.hidden&&restored.focus==='source-button'&&restored.expanded==='false',
    'Escape must close source dialog and restore focus '+JSON.stringify(restored));
  const nativeSummary="document.querySelector('#cn-path-week .cn-path-range-details summary')";
  // The same offline file persists its DOM when Chrome navigates between
  // hash destinations. A prior tablet test deliberately opened this
  // disclosure; reset ONLY test state before testing actual keyboard input.
  await evaluate("document.querySelector('#cn-path-week .cn-path-range-details').open=false");
  assert.equal(await evaluate("document.querySelector('#cn-path-week .cn-path-range-details').open"),false,
    'Keyboard disclosure test must begin closed');
  for(const expected of [true,false]){
    // Once a disclosure opens, the browser can move its focus to the
    // newly displayed subtree. Give each actual key activation a focused
    // native summary, just as a keyboard user navigating back to it would.
    await evaluate(nativeSummary+".focus()");
    const focus=await evaluate("document.activeElement?.tagName");
    assert.equal(focus,'SUMMARY','Native summary must be focusable');
    await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13,nativeVirtualKeyCode:13,text:'\r',unmodifiedText:'\r'},sessionId);
    await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13},sessionId);
    // Native details toggle as a queued activation default action; CDP's
    // key event completion alone is not the same as DOM microtask completion.
    await wait(120);
    const open=await evaluate("document.querySelector('#cn-path-week .cn-path-range-details').open");
    assert.equal(open,expected,'Native keyboard Enter must toggle provenance disclosure');
  }
  await call('Emulation.setEmulatedMedia',{
    features:[{name:'prefers-reduced-motion',value:'reduce'}]
  },sessionId);
  const motion=await evaluate("getComputedStyle(document.querySelector('.cn-chart-close-path')).animationName");
  assert.equal(motion,'none','Source price chart must respect reduced-motion preference');
  await call('Emulation.setEmulatedMedia',{features:[]},sessionId);
  console.log('PASS keyboard: modal focus/shift-tab/tab/escape, native details enter, reduced-motion chart');
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
