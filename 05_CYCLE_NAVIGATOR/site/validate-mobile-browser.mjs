// Bounded browser QA for the existing CN release gate. No production writer.
import {createServer} from 'node:http';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,dirname,extname,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';

const site=dirname(fileURLToPath(import.meta.url)),dist=resolve(site,'dist');
const out=resolve(process.env.CN_BROWSER_QA_OUTPUT||'runtime/cn-browser-qa');
const require=createRequire(import.meta.url);
const pw=require(resolve(process.env.CN_BROWSER_QA_NODE_MODULES||'node_modules','playwright'));
const production=process.argv.includes('--production');
const productionUrl='https://donh91.github.io/Investering-Framework-Archive-v1/';
const rows=[],failures=[],versions={};
const sha=b=>createHash('sha256').update(b).digest('hex');
await mkdir(out,{recursive:true});
let server,base;
if(production)base=productionUrl;
else{
 server=createServer(async(req,res)=>{
  try{
   if(req.method!=='GET')throw Error('GET_ONLY');
   const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
   const file=resolve(dist,'.'+(pathname==='/'?'/index.html':pathname));
   const rel=relative(dist,file);
   if(rel.startsWith('..')||rel.split('/').some(x=>x.startsWith('.')))throw Error('OUTSIDE_PUBLIC_BUNDLE');
   const bytes=await readFile(file);
   const type={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.webmanifest':'application/manifest+json'}[extname(file)]||'application/octet-stream';
   res.writeHead(200,{'Content-Type':type,'Cache-Control':'no-store'});res.end(bytes);
  }catch{res.writeHead(404);res.end('Not found');}
 });
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 base=`http://127.0.0.1:${server.address().port}/`;
}
const original=production?null:JSON.parse(await readFile(resolve(dist,'data/compass.json'),'utf8'));
function fixture(state){
 const c=structuredClone(original),now=Date.now();
 c.issued_at_utc=new Date(now-1000).toISOString();c.data_status='OK';c.action_now='HOLD';
 c.full_stack??={};c.full_stack.source_status??={};c.full_stack.source_status.official='VERIFIED';
 c.full_stack.official_freshness={contract:'OFFICIAL_COMPASS_SOURCE_FRESHNESS_READBACK_v1',status:'VERIFIED_OWNER_POLICY',source_asof_utc:new Date(now-60000).toISOString(),valid_until_utc:new Date(now+10740000).toISOString(),semantics:'SOURCE_FRESHNESS_EXPIRY_NOT_FORECAST_ETA'};
 const direction={BULLISH:'BULLISH',BEARISH:'BEARISH',MIXED:'MIXED',SIDEWAYS:'SIDEWAYS',HOLD:'HOLD',NO_EDGE:'NO_EDGE',NO_NEW_READING:'NO_NEW_READING',EXPIRY:'BULLISH'}[state]||'BULLISH';
 c.market_now={...(c.market_now||{}),directional_state:direction};
 c.horizons??={};c.horizons.NEXT_12H={...(c.horizons.NEXT_12H||{}),label:direction,expected_direction:direction==='BULLISH'?'UP':direction==='BEARISH'?'DOWN':direction,summary:'Synthetic consumer-contract fixture; no market result or trading authority.'};
 if(state==='STALE')c.full_stack.official_freshness.valid_until_utc=new Date(now-1).toISOString();
 if(state==='DEGRADED'){c.data_status='DEGRADED';c.full_stack.source_status.official='UNVERIFIED';}
 if(state==='EXPIRY'){
  c.full_stack.official_freshness.source_asof_utc=new Date(now-10792000).toISOString();
  c.full_stack.official_freshness.valid_until_utc=new Date(now+8000).toISOString();
 }
 return c;
}
async function geometry(page){
 return page.evaluate(()=>{
  const width=innerWidth;
  const offenders=[];
  for(const el of document.querySelectorAll('h1,h2,h3,p,strong,button,summary')){
   const r=el.getBoundingClientRect(),s=getComputedStyle(el);
   if(!r.width||!r.height||s.visibility==='hidden'||s.display==='none')continue;
   let scrolling=false;
   for(let p=el.parentElement;p&&p!==document.body;p=p.parentElement){const style=getComputedStyle(p);if(['auto','scroll'].includes(style.overflowX)&&p.scrollWidth>p.clientWidth+2){scrolling=true;break;}}
   if(!scrolling&&(r.left< -3||r.right>width+3))offenders.push({tag:el.tagName,text:el.textContent.trim().slice(0,70),left:Math.round(r.left),right:Math.round(r.right)});
  }
  return {viewport:width,document_width:document.documentElement.scrollWidth,offenders};
 });
}
async function screenshot(page,name){
 const file=name+'.png';await page.screenshot({path:resolve(out,file),fullPage:true});
 return {file,sha256:sha(await readFile(resolve(out,file)))};
}
function check(ok,message){if(!ok)throw Error(message);}
async function runCase(browser,engine,width,language,state){
 const context=await browser.newContext({...pw.devices['iPhone 14'],viewport:{width,height:844},locale:language==='da'?'da-DK':'en-GB',timezoneId:'Europe/Copenhagen',reducedMotion:'reduce'});
 const page=await context.newPage();const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 try{
  if(state!=='REAL')await page.route('**/data/compass.json*',route=>route.fulfill({json:fixture(state)}));
  await page.goto(base,{waitUntil:'domcontentloaded',timeout:30000});
  await page.locator('#premiumMarketCompass').waitFor({state:'visible',timeout:20000});
  await page.locator(`[data-language="${language}"]`).click();
  await page.waitForFunction(lang=>document.documentElement.lang===lang,language);
  if(production)check(await page.evaluate(()=>typeof window.CNOfficialCurrentReading==='function'),'PUBLISHED_REPAIR_NOT_PRESENT');
  const name=`${production?'production':'pr'}-${engine}-${width}-${language}-${state}`;
  const tabs=state==='REAL'?['now','path','proof']:['now'];
  for(const tab of tabs){
   await page.locator(`[data-tab="${tab}"]`).click();
   await page.locator(`#product${tab[0].toUpperCase()+tab.slice(1)}.active`).waitFor();
   const g=await geometry(page);
   const image=await screenshot(page,name+'-'+tab);
   rows.push({engine,width,language,state,tab,synthetic:state!=='REAL',geometry:g,screenshot:image});
   check(g.document_width<=width+3,`HORIZONTAL_DOCUMENT_OVERFLOW ${name} ${tab}: ${g.document_width}`);
   check(g.offenders.length===0,`TEXT_OUTSIDE_VIEWPORT ${name} ${tab}: ${JSON.stringify(g.offenders)}`);
  }
  if(state==='REAL'){
   await page.locator('[data-tab="now"]').click();
   for(const id of ['liveDecisionDetail','pullbackWatch']){
    const detail=page.locator('#'+id);
    if(await detail.count()){
     await detail.locator('summary').click();
     check(await detail.getAttribute('open')!==null,`DETAIL_NOT_OPEN ${id}`);
     const image=await screenshot(page,name+'-'+id);
     const g=await geometry(page);
     rows.push({engine,width,language,state,tab:id,synthetic:false,screenshot:image,geometry:g});
     check(g.document_width<=width+3&&g.offenders.length===0,`EXPANDED_DETAIL_OVERFLOW ${id}: ${JSON.stringify(g)}`);
    }
   }
  }else{
   const text=await page.locator('#premiumMarketCompass').innerText();
   check(!text.includes('The bearish 0–12h pressure reading is'),'HARDCODED_BEARISH_INVESTOR_COPY');
   const disclosure=await page.locator('.premium-hero-meta a').first().innerText();
   check(/12/.test(disclosure)&&/not|ikke|ingen|no /i.test(disclosure),'MISSING_12H_METHOD_LIMITATION');
   if(['STALE','DEGRADED'].includes(state)){
    check(await page.locator('.premium-action-window').count()===0,'UNSUPPORTED_APPLIES_NOW');
    check(await page.locator('#liveDecisionDetail').count()===0,'UNSUPPORTED_CURRENT_DIRECTION_DETAIL');
   }else{
    await page.locator('#liveDecisionDetail summary').click();
    const investor=await page.locator('.premium-audience-grid article').first().innerText();
    check(!/The bearish 0[–-]12h pressure/.test(investor),'BULLISH_BEARISH_CONTRADICTION');
    if(['MIXED','SIDEWAYS'].includes(state))check(/mixed|bland|sideways|sidelæns/i.test(investor),'MIXED_DIRECTION_NOT_EXPLAINED');
    if(['NO_EDGE','NO_NEW_READING','HOLD'].includes(state))check(/no fresh|ingen ny verificeret/i.test(investor),'MISSINGNESS_PRESENTED_AS_DIRECTION');
   }
   if(state==='EXPIRY'){
    check(await page.locator('.premium-action-window').count()===1,'INITIAL_FRESH_READING_MISSING');
    await page.locator('.premium-action-window').waitFor({state:'detached',timeout:15000});
    check(await page.locator('#liveDecisionDetail').count()===0,'EXPIRED_DIRECTION_PERSISTED');
    rows.push({engine,width,language,state:'EXPIRED_WITHOUT_FETCH',synthetic:true,screenshot:await screenshot(page,name+'-expired')});
   }
  }
  check(errors.length===0,`BROWSER_SCRIPT_ERROR ${errors.join('; ')}`);
 }catch(e){
  const image=await screenshot(page,`FAIL-${engine}-${width}-${language}-${state}`).catch(()=>null);
  failures.push({engine,width,language,state,error:e.message,screenshot:image});
 }finally{await context.close();}
}
try{
 for(const engine of ['chromium','webkit']){
  const browser=await pw[engine].launch({headless:true});versions[engine]=browser.version();
  try{
   for(const width of [390,430])for(const language of ['en','da'])await runCase(browser,engine,width,language,'REAL');
   if(!production){
    for(const state of ['BULLISH','BEARISH','MIXED','SIDEWAYS','HOLD','NO_EDGE','STALE','DEGRADED','NO_NEW_READING'])
     for(const width of [390,430])for(const language of ['en','da'])await runCase(browser,engine,width,language,state);
    await runCase(browser,engine,390,'en','EXPIRY');
   }
  }finally{await browser.close();}
 }
}catch(e){failures.push({error:e.message});}
finally{if(server)await new Promise(r=>server.close(r));}
const inputs={};
if(!production)for(const file of ['index.html','market-compass-premium.js','public-product.js','market-compass-premium.css','public-product.css','data/compass.json'])inputs[file]=sha(await readFile(resolve(dist,file)));
const receipt={contract:'CN_REAL_BROWSER_RELEASE_QA_v1',recorded_at_utc:new Date().toISOString(),mode:production?'REAL_PUBLIC_PRODUCTION':'BUILT_PR_AND_DECLARED_SYNTHETIC_CONSUMER_FIXTURES',checkout_sha:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),playwright_version:require(resolve(process.env.CN_BROWSER_QA_NODE_MODULES||'node_modules','playwright/package.json')).version,browser_versions:versions,device_semantics:'Linux Chromium and WebKit iPhone viewport/touch emulation, not real Safari or physical iPhone',production_url:production?productionUrl:null,inputs,rows,failures,status:failures.length?'FAIL':'BROWSER_CHECKS_PASS_MANUAL_SCREENSHOT_REVIEW_REQUIRED',scientific_edge_established:false,fixtures_are_production_evidence:false};
await writeFile(resolve(out,'receipt.json'),JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({status:receipt.status,rendered_views:rows.length,failures},null,2));
if(failures.length)process.exitCode=1;
