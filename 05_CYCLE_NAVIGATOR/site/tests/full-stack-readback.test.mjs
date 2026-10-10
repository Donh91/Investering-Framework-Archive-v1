import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve,relative} from 'node:path';
const source=await readFile(new URL('../build-public.mjs',import.meta.url),'utf8');
const premium=await readFile(new URL('../market-compass-premium.js',import.meta.url),'utf8');
const hash=s=>createHash('sha256').update(s).digest('hex');
const sort=x=>Array.isArray(x)?x.map(sort):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,sort(x[k])])):x;
const signed=(x,key)=>{const digest=hash(JSON.stringify(sort(x)));return {hash:digest,raw:JSON.stringify(sort({...x,[key]:digest}))};};
function fixture(){
 const root='/fixture',now=new Date().toISOString(),files=new Map(),pointers=new Map();
 const autoPath='04_MARKET_LEARNING/entry_signals/auto_market_state/runs/current.json';
 const auto=signed({contract:'AUTO_MARKET_STATE_PACKET_v1',packet_generated_at_utc:now},'packet_sha256');
 files.set(resolve(root,autoPath),auto.raw);
 const weeklyRaw=JSON.stringify({issue_number:29});
 const weeklyPath='05_CYCLE_NAVIGATOR/weekly/2026/W41/CYCLE_NAVIGATOR_MACHINE_PACKAGE.json';
 files.set(resolve(root,weeklyPath),weeklyRaw);
 const wp={week_dir:'05_CYCLE_NAVIGATOR/weekly/2026/W41',iso_year:2026,iso_week:41,issue_number:29,machine_package_sha256:hash(weeklyRaw)};
 const officialPath='04_MARKET_LEARNING/handlekompas/official/daily/c.json';
 const official={contract:'OFFICIAL_DAILY_COMPASS_v1',compass_id:'c',issued_at_utc:now,data_status:'OK',source_bindings:{auto_market_state:{packet_sha256:auto.hash}}};
 const officialRaw=JSON.stringify(official);files.set(resolve(root,officialPath),officialRaw);
 pointers.set('official',{contract:'OFFICIAL_DAILY_COMPASS_LATEST_POINTER_v1',compass_path:officialPath,compass_id:'c',issued_at_utc:now,data_status:'OK',compass_content_sha256:hash(officialRaw),source_packet_sha256:auto.hash});
 pointers.set('auto',{packet_path:autoPath,packet_sha256:auto.hash,packet_generated_at_utc:now});
 const forecastPath='04_MARKET_LEARNING/handlekompas/shadow_v2/forecasts/f.json';
 const forecast={contract:'SHADOW_COMPASS_V2_FORECAST_v1',forecast_id:'f',issued_at_utc:now,source_fingerprint:'fp',authority:{automatic_promotion:false},source_bindings:{auto_market_state:{packet_path:autoPath,packet_sha256:auto.hash,packet_generated_at_utc:now},cycle_navigator:{iso_year:2026,iso_week:41,issue_number:29,machine_package_sha256:wp.machine_package_sha256}},model_output:{horizons:{'12h':{direction:'UP'}}}};
 const installForecast=()=>{const f=signed(forecast,'forecast_sha256');files.set(resolve(root,forecastPath),f.raw);pointers.set('shadow',{contract:'SHADOW_COMPASS_V2_LATEST_POINTER_v1',forecast_path:forecastPath,forecast_sha256:f.hash,forecast_id:'f',source_fingerprint:'fp'});};installForecast();
 const context={resolve,relative,createHash,Date,repoRoot:root,INTERNAL_COMPASS_POINTER_PATH:'official',AUTO_MARKET_STATE_POINTER_PATH:'auto',NATIVE_COMPASS_POINTER_PATH:'native',SHADOW_COMPASS_V2_POINTER_PATH:'shadow',STRATEGIC_COMPASS_POINTER_PATH:'strategic',MASTER_MONDAY_HANDOFF_PATH:'handoff',readJson:async p=>pointers.get(p),readFile:async(p,encoding)=>{if(!files.has(p))throw Error('missing');return encoding?files.get(p):Buffer.from(files.get(p));}};
 vm.createContext(context);vm.runInContext(source.slice(source.indexOf('function verifiedRelative'),source.indexOf('\nasync function buildCompassEventSnapshot'))+';globalThis.run=buildFullStackReadback;globalThis.digest=verifiedRawDigest;',context);
 return {root,files,pointers,forecast,installForecast,autoPath,officialPath,weeklyPath,context,run:()=>context.run({compass_id:'c',data_status:'OK',action_now:'HOLD'},wp,{issue_number:29})};
}
let f=fixture();assert.equal((await f.run()).shadow.status,'ALIGNED_RESEARCH');
f=fixture();f.pointers.get('official').source_packet_sha256='a'.repeat(64);let result=await f.run();assert.equal(result.source_status.official,'DEGRADED');assert.notEqual(result.shadow.status,'ALIGNED_RESEARCH');
f=fixture();f.pointers.get('auto').packet_generated_at_utc='2099-01-01T00:00:00Z';result=await f.run();assert.equal(result.source_status.auto_market_state,'UNVERIFIED');assert.notEqual(result.shadow.status,'ALIGNED_RESEARCH');
f=fixture();f.files.delete(resolve(f.root,f.officialPath));assert.equal((await f.run()).source_status.official,'DEGRADED');
f=fixture();f.files.set(resolve(f.root,f.officialPath),'{}');assert.equal((await f.run()).source_status.official,'DEGRADED');
for(const mode of ['missing','tampered','wrong-issue','valid']){
 f=fixture();const oldRaw=JSON.stringify({issue_number:28});f.forecast.source_bindings.cycle_navigator={iso_year:2026,iso_week:40,issue_number:28,machine_package_sha256:hash(oldRaw)};
 const path=resolve(f.root,'05_CYCLE_NAVIGATOR/weekly/2026/W40/CYCLE_NAVIGATOR_MACHINE_PACKAGE.json');
 if(mode==='valid')f.files.set(path,oldRaw);
 if(mode==='tampered')f.files.set(path,JSON.stringify({issue_number:28,changed:true}));
 if(mode==='wrong-issue'){f.files.set(path,JSON.stringify({issue_number:27}));f.forecast.source_bindings.cycle_navigator.machine_package_sha256=hash(f.files.get(path));}
 f.installForecast();result=await f.run();assert.equal(result.shadow.status,mode==='valid'?'STALE_RESEARCH':'UNVERIFIED');
 assert.equal(result.shadow.horizons['12h']?.direction,mode==='valid'?'UP':undefined);
}
// Native metadata must come from the hash-verified target, not a mutable pointer.
for(const mode of ['valid','health','time']){
 f=fixture();const auto=f.pointers.get('auto');const path='04_MARKET_LEARNING/handlekompas/runs/n.json';
 const run={contract:'NATIVE_HANDLEKOMPAS_v1',action:{NOW:'HOLD_WAIT'},source:{packet_sha256:auto.packet_sha256},DATA_HEALTH:'PASS',generated_at_utc:auto.packet_generated_at_utc};const n=signed(run,'handlekompas_sha256');
 f.files.set(resolve(f.root,path),n.raw);f.pointers.set('native',{handlekompas_path:path,handlekompas_sha256:n.hash,source_packet_sha256:auto.packet_sha256,NOW:'HOLD_WAIT',data_health:mode==='health'?'DEGRADED':'PASS',generated_at_utc:mode==='time'?'2099-01-01T00:00:00Z':run.generated_at_utc});
 result=await f.run();assert.equal(result.source_status.native,mode==='valid'?'SOURCE_ALIGNED':'UNVERIFIED');
}
// Preserve Python integral-float bytes rather than parse/stringify reconstruction.
f=fixture();const raw='{"contract":"FLOAT_TEST","number":1.0}';const digest=hash(raw),withDigest='{"contract":"FLOAT_TEST","number":1.0,"z_sha256":"'+digest+'"}';assert.equal(f.context.digest(withDigest,JSON.parse(withDigest),'z_sha256',digest),true);assert.equal(f.context.digest(withDigest.replace('1.0','2.0'),JSON.parse(withDigest.replace('1.0','2.0')),'z_sha256',digest),false);
function render(status,contract='PUBLIC_COMPASS_PROJECTION_v1'){
 let html='';const root={querySelectorAll:()=>[],querySelector:()=>null,classList:{add:()=>{}},prepend:s=>{html=s.innerHTML}};
 const ctx={document:{getElementById:()=>root,createElement:()=>({querySelector:()=>null,querySelectorAll:()=>[]})},esc:String,HORIZONS:[],officialScale:()=>null,decisionMeta:()=>({live:'UNAVAILABLE',liveEta:'UNKNOWN',weekly:'UNAVAILABLE',weeklyEta:'UNKNOWN'}),cnConclusion:()=>'',recommendationWindow:()=>'',hourlyMonitor:()=>'',decisionDetail:()=>'<p>INVESTOR_DETAIL</p>',compositeIntel:()=>'',pullbackCard:()=>'',riskCurve:()=>'',publicDataStatus:String,capSummary:()=>''};
 vm.createContext(ctx);vm.runInContext(premium.slice(premium.indexOf('function publicAction'),premium.indexOf('\nfunction cnConclusion'))+premium.slice(premium.indexOf('function renderPremium('),premium.indexOf('\nlet latestSnapshot'))+';globalThis.run=renderPremium;',ctx);
 ctx.run({live_observation:{current_action:{stance:'BUY'}}},{contract,data_status:status,action_now:'HOLD_WAIT_DATA_DEGRADED',bull_bear_scale:{}});return html;
}
for(const status of ['DEGRADED','NOT_PUBLISHED','STALE',undefined]){const html=render(status);assert.match(html,/WAIT · DATA DEGRADED/);assert.doesNotMatch(html,/Keep current positioning|INVESTOR_DETAIL|APPLIES NOW/);}
assert.match(render('OK'),/CURRENT ACTION<\/span><strong>HOLD<\/strong>/);assert.match(render('OK'),/INVESTOR_DETAIL/);assert.doesNotMatch(render('OK','WRONG_CONTRACT'),/INVESTOR_DETAIL/);
console.log('FULL_STACK_READBACK_REGRESSION_PASS');
