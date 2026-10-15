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
    "paths:p.map(x=>Boolean(x&&x.getAttribute('d')?.includes(' C ')&&",
    "x.getBBox().width>100&&getComputedStyle(x).display!=='none'&&getComputedStyle(x).opacity!=='0')),",
    "viewBox:svg?.getAttribute('viewBox')",
    '};})()'
  ].join('');
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
    for(const lang of ['da','en']){
      await evaluate("document.querySelector('[data-lang="+JSON.stringify(lang)+"]').click()");
      await wait(200);
      for(const asset of ['BTC','ETH']){
        await evaluate("document.querySelector('[data-asset="+JSON.stringify(asset)+"]').click()");
        await wait(180);
        const proof=await evaluate(readPaths);
        assert.ok(proof.inner===width&&proof.scrollWidth<=width+1&&
          proof.route==='#cn-path-week'&&proof.lang===lang&&proof.asset===asset&&
          proof.hasSource&&proof.paths.every(Boolean),
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
        }
      }
    }
  }
  assert.deepEqual(runtimeErrors.filter(Boolean),[],'No JavaScript exceptions');
  console.log('PASS all: two foreground lines, 390/430px, DA/EN, BTC/ETH, source, route, no horizontal overflow, nonblank screenshots');
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
