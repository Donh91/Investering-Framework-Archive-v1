/* Actual headless Chrome smoke for the standalone S1 product only.
 * CDP mobile emulation is not a claim about iOS Safari or production CDN.
 */
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { existsSync,readFileSync,mkdtempSync,rmSync } from 'node:fs';
import { resolve,dirname,extname,join,sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { tmpdir } from 'node:os';
import { setTimeout as delay } from 'node:timers/promises';
const dist=dirname(fileURLToPath(import.meta.url));
const mockSuccess=process.env.S1_BROWSER_MODE==='mock';
const MOCK_HEAD='a'.repeat(40),MOCK_MAIN='b'.repeat(40);
const MOCK_PR={number:1996,title:'S1 release control mock exact-head',state:'open',
  draft:false,merged_at:null,changed_files:1,updated_at:'2026-11-07T13:00:00Z',
  user:{login:'Donh91'},head:{sha:MOCK_HEAD},base:{sha:MOCK_MAIN},labels:[]};
const requestLog=[];
function mockGithub(url,method){
  if(method==='OPTIONS')return {code:204,payload:null};
  const u=new URL(url),path=u.pathname;
  if(!path.startsWith('/repos/Donh91/'))return {code:404,payload:{message:'OUTSIDE_SOURCE_BOUNDARY'}};
  const archive=path.startsWith('/repos/Donh91/Investering-Framework-Archive-v1/');
  if(path.endsWith('/branches/main'))return {code:200,payload:{commit:{sha:MOCK_MAIN}}};
  if(path.endsWith('/pulls')&&u.searchParams.has('state'))return {code:200,payload:archive?[MOCK_PR]:[]};
  if(archive&&path.endsWith('/pulls/1996'))return {code:200,payload:MOCK_PR};
  if(archive&&path.endsWith('/pulls/1996/files'))return {code:200,payload:[{filename:'tools/s1-release-control/index.html'}]};
  if(archive&&path.endsWith('/pulls/1996/reviews'))return {code:200,payload:[]};
  if(archive&&path.endsWith('/actions/runs')&&u.searchParams.get('head_sha')===MOCK_HEAD)
    return {code:200,payload:{workflow_runs:[{id:321987654,head_sha:MOCK_HEAD,
      status:'completed',conclusion:'success',name:'S1 Test',event:'pull_request',
      pull_requests:[{number:1996}]}]}};
  return {code:404,payload:{message:'UNMOCKED_SOURCE'}};
}

const chrome=[process.env.CHROME_BIN,'/usr/bin/google-chrome','/usr/bin/chromium','/usr/bin/chromium-browser'].find(x=>x&&existsSync(x));
assert.ok(chrome,'S1_BROWSER_CHROME_UNAVAILABLE');
assert.ok(existsSync(join(dist,'index.html')),'S1_BUNDLE_NOT_STAGED');
const mime={'.html':'text/html','.mjs':'text/javascript','.js':'text/javascript','.json':'application/json','.css':'text/css'};
const server=createServer((req,res)=>{
  let pathname;try{pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname)}catch{res.writeHead(400).end();return}
  const targetPath=pathname.endsWith('/')?pathname+'index.html':pathname;
  const full=resolve(dist,'.'+targetPath);
  if(!full.startsWith(dist+sep)){res.writeHead(403).end();return}
  try{const bytes=readFileSync(full);res.setHeader('Content-Type',mime[extname(full)]||'text/plain');res.setHeader('Cache-Control','no-store');res.writeHead(200).end(bytes)}
  catch(error){if(!res.headersSent){res.writeHead(404).end('missing')}else{res.end();console.error('S1_STATIC_SERVER_POST_HEADER_ERROR',String(error.message||error))}}
});
await new Promise((ok,no)=>server.once('error',no).listen(0,'127.0.0.1',ok));
const pageUrl='http://127.0.0.1:'+server.address().port+'/';
let profile=null,browser=null,ws=null;
try{
  let port=0;
  for(let attempt=1;attempt<=2&&!port;attempt++){
    profile=mkdtempSync(join(tmpdir(),'s1-browser-'));
    browser=spawn(chrome,['--headless=new','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'],{stdio:'ignore'});
    for(let i=0;i<100;i++){
      await delay(100);
      try{port=Number(readFileSync(join(profile,'DevToolsActivePort'),'utf8').split('\n')[0]);if(port>0)break}catch{}
      if(browser.exitCode!==null)break;
    }
    if(port)break;
    browser.kill();try{rmSync(profile,{recursive:true,force:true})}catch{}
  }
  assert.ok(port>0,'S1_NO_CDP_PORT');
  const pages=await(await fetch('http://127.0.0.1:'+port+'/json')).json();
  const target=pages.find(p=>p.type==='page');
  assert.ok(target?.webSocketDebuggerUrl,'S1_NO_BROWSER_PAGE');
  ws=new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((ok,no)=>{ws.onopen=ok;ws.onerror=no;});
  const pending=new Map(),exceptions=[];let serial=0;
  ws.onmessage=event=>{
    const message=JSON.parse(event.data);
    if(message.method==='Runtime.exceptionThrown')exceptions.push(message.params?.exceptionDetails?.text||'UNKNOWN');
    if(message.method==='Fetch.requestPaused'){
      const url=message.params?.request?.url||'',method=message.params?.request?.method||'GET';
      requestLog.push({url,method});
      const fixture=mockGithub(url,method);
      const responseHeaders=[
        {name:'Access-Control-Allow-Origin',value:'*'},
        {name:'Access-Control-Allow-Methods',value:'GET, OPTIONS'},
        {name:'Access-Control-Allow-Headers',value:'Accept, X-GitHub-Api-Version, Content-Type'},
        {name:'Content-Type',value:'application/json'}
      ];
      void send('Fetch.fulfillRequest',{requestId:message.params.requestId,
        responseCode:fixture.code,responseHeaders,
        body:fixture.payload===null?'':Buffer.from(JSON.stringify(fixture.payload)).toString('base64')
      }).catch(error=>exceptions.push('MOCK_FETCH_FAILURE '+String(error.message||error)));
      return;
    }

    if(message.id&&pending.has(message.id)){
      const entry=pending.get(message.id);pending.delete(message.id);
      message.error?entry.reject(Error(JSON.stringify(message.error))):entry.resolve(message.result);
    }
  };
  const send=(method,params={})=>new Promise((ok,no)=>{
    const id=++serial;pending.set(id,{resolve:ok,reject:no});ws.send(JSON.stringify({id,method,params}));
    const clock=setTimeout(()=>{if(pending.has(id)){pending.delete(id);no(Error('S1_CDP_TIMEOUT '+method))}},15000);clock.unref();
  });
  const evaluate=async expression=>{
    const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});
    if(r.exceptionDetails)throw Error('S1_BROWSER_EVALUATION_ERROR '+JSON.stringify(r.exceptionDetails));
    return r.result.value;
  };
  await send('Page.enable');await send('Runtime.enable');await send('Network.enable');
  if(mockSuccess)await send('Fetch.enable',{patterns:[{urlPattern:'https://api.github.com/*',requestStage:'Request'}]});
  else await send('Network.setBlockedURLs',{urls:['https://api.github.com/*']});
  const reports=[];
  for(const [width,height] of [[390,844],[430,932],[1440,900]]){
    await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<800});
    await send('Page.navigate',{url:pageUrl});
    let ready=false;
    for(let n=0;n<75;n++){
      await delay(100);
      const readyExpr=mockSuccess?
        'document.readyState==="complete" && document.getElementById("freshness")?.textContent.startsWith("GitHub readback")':
        'document.readyState==="complete" && !!document.getElementById("m-open") && document.getElementById("m-open").textContent!=="–"';
      if(await evaluate(readyExpr)){ready=true;break}
    }
    if(!ready){
      const debug=await evaluate('({url:location.href,title:document.title,ready:document.readyState,text:document.body?.textContent?.slice(0,350),notice:document.getElementById("sync-notice")?.textContent,open:document.getElementById("m-open")?.textContent})');
      console.error('S1_BROWSER_STARTUP_DIAGNOSTIC',JSON.stringify({width,debug,exceptions}));
    }
    assert.ok(ready,'S1_BROWSER_NOT_READY '+width);
    const report=await evaluate(`(()=>{
      const $=id=>document.getElementById(id);
      $('f-risk').value='HIGH';$('f-risk').dispatchEvent(new Event('change',{bubbles:true}));
      const filtered=$('rows').querySelectorAll('tr').length;
      $('f-risk').value='';$('f-risk').dispatchEvent(new Event('change',{bubbles:true}));
      const first=$('rows').querySelector('tr');if(first)first.click();
      $('q-limit').value='3';$('q-limit').dispatchEvent(new Event('change',{bubbles:true}));
      return {
        width:innerWidth, clientWidth:document.documentElement.clientWidth,
        documentWidth:document.documentElement.scrollWidth, filtered,
        count:Number($('m-open').textContent),
        visibleRows:$('rows').querySelectorAll('tr').length,
        queue:$('m-queue').textContent,
        detailHasSha:$('detail').textContent.includes('SHA40'),
        privateUnavailable:$('repo-list').textContent.includes('PRIVATE · UNOBSERVED'),
        noReleaseAuthority:document.body.textContent.includes('READ-ONLY'),
        fallbackNotLive:$('sync-notice').textContent.includes('IKKE live')||$('freshness').textContent.includes('IKKE live'),
        sourceLabel:$('freshness').textContent,
        exactHeadInDetail:$('detail').textContent.includes('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'),
        exactPrCiCount:Number($('m-ci').textContent)

      };
    })()`);
    assert.equal(report.width,width,'WRONG_VIEWPORT');
    assert.ok(report.documentWidth<=width+2,'HORIZONTAL_PAGE_OVERFLOW '+JSON.stringify(report));
    if(mockSuccess){
      assert.equal(report.count,1,'MOCK_PUBLIC_PR_COUNT');
      assert.equal(report.filtered,0,'MOCK_HIGH_RISK_FILTER_NOT_EMPTY');
      assert.equal(report.exactPrCiCount,1,'MOCK_PR_CI_NOT_OBSERVED');
      assert.equal(report.exactHeadInDetail,true,'MOCK_EXACT_HEAD_MISSING');
      assert.equal(report.fallbackNotLive,false,'MOCK_SOURCE_MISLABELED_AS_STALE');
    }
    assert.ok(report.count>=1,'NO_FALLBACK_PR_ROWS');
    assert.ok(report.visibleRows>=1,'PR_EXPLORER_EMPTY');
    assert.ok(report.detailHasSha,'DETAIL_EVIDENCE_MISSING');
    assert.ok(report.privateUnavailable,'PRIVATE_BOUNDARY_NOT_VISIBLE');
    assert.ok(report.noReleaseAuthority,'READONLY_NOTICE_MISSING');
    if(!mockSuccess)assert.ok(report.fallbackNotLive,'HISTORICAL_FALLBACK_MISLABELED_LIVE');
    assert.match(report.queue,/^\d+\/3$/);
    reports.push(report);
    if(mockSuccess)await evaluate('localStorage.removeItem("s1-release-control-public-v1")');
  }
  assert.deepEqual(exceptions,[],'JS_RUNTIME_EXCEPTIONS');
  if(mockSuccess){
    assert.ok(requestLog.some(r=>r.url.includes('/pulls/1996/files')),'MOCK_FILES_NOT_FETCHED');
    assert.ok(requestLog.some(r=>r.url.includes('/actions/runs')),'MOCK_RUNS_NOT_FETCHED');
    assert.ok(requestLog.every(r=>r.url.startsWith('https://api.github.com/')),'MOCK_CROSSED_PUBLIC_BOUNDARY');
  }
  console.log('S1_CHROME_ACCEPTANCE '+JSON.stringify({mode:mockSuccess?'MOCK_PUBLIC_SUCCESS':'API_DENIED',reports,exceptions,requests:requestLog.length}));
}finally{
  if(ws)try{ws.close()}catch{}
  if(browser&&browser.exitCode===null)browser.kill('SIGTERM');
  if(profile)try{rmSync(profile,{recursive:true,force:true})}catch{}
  await new Promise(ok=>server.close(ok));
}
