/**
 * Real Chrome/CDP acceptance of the existing GitHub Pages HTML, CSS and
 * TradingView 5.2 original renderer. No independent canvas implementation.
 */
import assert from "node:assert/strict";
import {createServer} from "node:http";
import {spawn} from "node:child_process";
import {readFileSync,existsSync,mkdtempSync,rmSync} from "node:fs";
import {dirname,resolve,join,extname,sep} from "node:path";
import {fileURLToPath} from "node:url";
import {tmpdir} from "node:os";
import {setTimeout as delay} from "node:timers/promises";

const dist=resolve(dirname(fileURLToPath(import.meta.url)),"../../dist");
const base="/Investering-Framework-Archive-v1/";
const path=base+"kompas-pro-test/alternativer/";
const chrome=[process.env.CHROME_BIN,"/usr/bin/google-chrome","/usr/bin/chromium","/usr/bin/chromium-browser"].find(x=>x&&existsSync(x));
assert.ok(chrome,"NO_CHROME_FOR_NATIVE_ALTERNATIVES");
const files=[
 "kompas-pro-test/alternativer/index.html","kompas-pro-test/alternativer/app.mjs",
 "kompas-pro-test/alternativer/styles.css","kompas-pro-test/alternativer/full-week-fixture.mjs",
 "frozen-week-chart.js","vendor/lightweight-charts-5.2.0.js"];
for(const name of files)assert.ok(existsSync(resolve(dist,name)),"MISSING_BUILD_ASSET "+name);
const mime={".html":"text/html",".css":"text/css",".mjs":"text/javascript",".js":"text/javascript"};
const srv=createServer((req,res)=>{
 let pathname;
 try{pathname=decodeURIComponent(new URL(req.url,"http://localhost").pathname)}catch{res.writeHead(400).end();return}
 if(!pathname.startsWith(base)){res.writeHead(404).end();return}
 let rel=pathname.slice(base.length);
 if(!rel||rel.endsWith("/"))rel+="index.html";
 const filepath=resolve(dist,rel);
 if(!filepath.startsWith(dist+sep)){res.writeHead(403).end();return}
 try{res.writeHead(200,{"Content-Type":mime[extname(filepath)]||"application/octet-stream","Cache-Control":"no-store"}).end(readFileSync(filepath))}
 catch{res.writeHead(404).end("Not found")}
});
await new Promise((ok,fail)=>srv.once("error",fail).listen(0,"127.0.0.1",ok));
let browser=null,profile=null,socket=null;
const errors=[];
try{
 let port,boot="";
 for(let attempt=1;attempt<=2&&!port;attempt++){
  profile=mkdtempSync(join(tmpdir(),"kompas-alt-browser-"));
  browser=spawn(chrome,["--headless=new","--no-sandbox","--disable-gpu","--disable-dev-shm-usage",
    ...(attempt===1?["--no-zygote"]:[]),"--remote-debugging-port=0",
    "--user-data-dir="+profile,"about:blank"],{stdio:["ignore","ignore","pipe"]});
  browser.stderr?.on("data",v=>{boot=(boot+v.toString()).slice(-1800)});
  for(let i=0;i<120;i++){
   if(browser.exitCode!==null||browser.signalCode!==null)break;
   try{const v=Number(readFileSync(join(profile,"DevToolsActivePort"),"utf8").split("\n")[0]);
     if(v>0){port=v;break}}catch{}
   await delay(100);
  }
  if(port)break;
  if(browser.exitCode===null)browser.kill("SIGTERM");
  await delay(250);
  try{rmSync(profile,{recursive:true,force:true})}catch{}
 }
 assert.ok(port,"ALTERNATIVES_CHROME_BOOT_FAILED "+boot);
 const tabs=await(await fetch("http://127.0.0.1:"+port+"/json")).json();
 const tab=tabs.find(p=>p.type==="page");
 assert.ok(tab?.webSocketDebuggerUrl,"CHROME_CDP_TAB_MISSING");
 socket=new WebSocket(tab.webSocketDebuggerUrl);
 await new Promise((ok,fail)=>{socket.onopen=ok;socket.onerror=fail});
 let serial=0;const pending=new Map();
 socket.onmessage=e=>{
  const v=JSON.parse(e.data);
  if(v.method==="Runtime.exceptionThrown")errors.push(String(v.params?.exceptionDetails?.exception?.description||v.params?.exceptionDetails?.text));
  if(v.id&&pending.has(v.id)){const p=pending.get(v.id);pending.delete(v.id);v.error?p.fail(Error(JSON.stringify(v.error))):p.ok(v.result)}
 };
 function send(method,params={}){
  return new Promise((ok,fail)=>{
   const id=++serial;pending.set(id,{ok,fail});
   socket.send(JSON.stringify({id,method,params}));
   const t=setTimeout(()=>{if(pending.has(id)){pending.delete(id);fail(Error("CDP_TIMEOUT "+method))}},10000);
   t.unref();
  });
 }
 async function evaluate(expression){
  const v=await send("Runtime.evaluate",{expression,returnByValue:true,awaitPromise:true});
  if(v.exceptionDetails)throw Error("BROWSER_EVAL "+JSON.stringify(v.exceptionDetails));
  return v.result?.value;
 }
 await send("Page.enable");await send("Runtime.enable");await send("Network.enable");
 const checked=[];
 for(const width of [390,430,1360]){
  await send("Emulation.setDeviceMetricsOverride",{width,height:width===390?844:width===430?932:900,deviceScaleFactor:1,mobile:width<600});
  await send("Page.navigate",{url:"http://127.0.0.1:"+srv.address().port+path+"?design=nordic&hours=168"});
  let ready=false;
  for(let i=0;i<100;i++){
   await delay(100);
   ready=await evaluate('Boolean(document.querySelector("#native-chart .fw-canvas canvas") && document.querySelectorAll("#daily-rows tr").length===7 && document.querySelector("#observed-hours")?.textContent==="168 / 168")');
   if(ready)break;
  }
  assert.ok(ready,"GITHUB_NATIVE_CHART_NOT_READY_"+width);
  const colors=[];
  for(const design of ["nordic","atelier","signal"]){
   await evaluate('document.querySelector("[data-concept-choice='+design+']").click();true');
   await delay(140);
   const report=await evaluate('(()=>{const rows=[...document.querySelectorAll("#daily-rows tr")];return {design:document.body.dataset.concept,chartDesign:document.querySelector(".chart-area")?.getAttribute("data-kompas-alternative"),color:getComputedStyle(document.querySelector(".fw-canvas")).backgroundColor,canvases:document.querySelectorAll("#native-chart .fw-canvas canvas").length,rows:rows.length,actual:rows.filter(r=>!r.cells[4]?.textContent?.includes("Afventer")).length,observed:document.querySelector("#observed-hours")?.textContent,error:!document.querySelector("#graph-error").hidden,overflow:document.documentElement.scrollWidth>innerWidth+2,forecast:document.querySelector(".fw-progress-forecast")?.textContent,dayFoldOpen:document.querySelector("#daily-values-fold")?.open,rangeExplanationDisplay:getComputedStyle(document.querySelector("#nordic-range-explanation")).display}})()');
   assert.equal(report.design,design,JSON.stringify(report));
   assert.equal(report.chartDesign,design,JSON.stringify(report));
   assert.ok(report.canvases>=1,JSON.stringify(report));
   assert.equal(report.rows,7,JSON.stringify(report));
   assert.equal(report.actual,7,JSON.stringify(report));
   assert.equal(report.observed,"168 / 168",JSON.stringify(report));
   assert.equal(report.error,false,JSON.stringify(report));
   assert.equal(report.overflow,false,JSON.stringify(report));
   assert.match(report.forecast||"",/7/);
   if(design==="nordic"){
     assert.equal(report.dayFoldOpen,false,"NORDIC_DAY_TABLE_MUST_BE_COLLAPSED_BY_DEFAULT");
     assert.notEqual(report.rangeExplanationDisplay,"none","NORDIC_RANGE_EXPLANATION_REQUIRED");
   }else{
     assert.equal(report.dayFoldOpen,true,"OTHER_DESIGNS_KEEP_EXISTING_TABLES");
     assert.equal(report.rangeExplanationDisplay,"none","NORDIC_HINT_NOT_VISIBLE_IN_OTHER_DESIGNS");
   }
   colors.push(report.color);
  }
  assert.equal(new Set(colors).size,3,"THREE_LIGHT_CHART_BACKGROUNDS_NOT_DIFFERENT "+JSON.stringify(colors));
  const frozen=await evaluate('[...document.querySelectorAll("#daily-rows tr")].map(r=>r.cells[1].textContent)');
  await evaluate('document.querySelector("[data-stage]").click();true');
  const monday=await evaluate('(()=>({prices:[...document.querySelectorAll("#daily-rows tr")].map(r=>r.cells[1].textContent),observed:document.querySelector("#observed-hours").textContent,actual:[...document.querySelectorAll("#daily-rows tr")].filter(r=>!r.cells[4].textContent.includes("Afventer")).length,chart:document.querySelectorAll("#native-chart .fw-canvas canvas").length,error:!document.querySelector("#graph-error").hidden}))()');
  assert.equal(JSON.stringify(monday.prices),JSON.stringify(frozen),"FROZEN_FORECAST_MUTATED");
  assert.equal(monday.observed,"16 / 168");
  assert.equal(monday.actual,0);
  assert.ok(monday.chart>=1&&!monday.error,"MONDAY_NATIVE_CHART_FAILED");
  checked.push({width,colors,week:"168h",monday:"16h",native:true});
 }
 assert.deepEqual(errors,[],"JS_RUNTIME_ERRORS_IN_ORIGINAL_GITHUB_CHART");
 console.log("GITHUB_ONLY_FULL_WEEK_THREE_DESIGNS_BROWSER_PASS "+JSON.stringify(checked));
}finally{
 try{socket?.close()}catch{}
 if(browser&&browser.exitCode===null&&browser.signalCode===null){browser.kill("SIGTERM");await delay(350);if(browser.exitCode===null)browser.kill("SIGKILL")}
 if(profile)try{rmSync(profile,{recursive:true,force:true})}catch{}
 await new Promise(ok=>srv.close(ok));
}
