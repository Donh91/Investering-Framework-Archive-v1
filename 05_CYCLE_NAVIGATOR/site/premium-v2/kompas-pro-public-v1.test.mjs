import test from 'node:test';
import {mkdtemp,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {finalizeKompasPublic,verifyKompasPublicBinding} from './finalize-kompas-public.mjs';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {buildKompasProPublic} from './kompas-pro-public-v1.mjs';
import {forwardOutlook} from '../vnext-live/forward-outlook.mjs';
import {fixture,bytes,nowMs} from './kompas-pro-public-fixture.mjs';
const run=(f,now=nowMs)=>buildKompasProPublic(bytes(f.latest),bytes(f.compass),bytes(f.lineage),{nowMs:now});
test('qualified positive source and exact three final byte bindings',()=>{
 const f=fixture(),p=run(f);assert.equal(p.state,'OK');assert.equal(p.action,'HOLD_WAIT');
 assert.deepEqual(p.bull_bear,{bull:6,bear:4,bias:'LEAN_BULLISH'});
 assert.deepEqual(p.risk,{class:'ELEVATED',ordinal:3,quality:'LOW'});
 assert.equal(p.momentum.direction,'BULLISH');assert.equal(p.momentum.valid_until,'2026-11-24T10:30:00.000Z');
 assert.equal(p.valid_until,'2026-11-24T12:00:00.000Z');assert.equal(p.horizons.length,4);assert.equal(p.horizon_status.length,14);
 assert.equal(p.protection.sell_state,'NONE');assert.deepEqual(p.frozen_week.btc,{low:60000,high:70000});
 for(const [key,name] of [['latest_json','latest'],['compass_json','compass'],['publication_lineage_json','lineage']])assert.equal(p.source_shas[key],createHash('sha256').update(bytes(f[name])).digest('hex'));
});
test('one-byte append on final latest changes its digest',()=>{const f=fixture(),a=bytes(f.latest),b=bytes(f.compass),c=bytes(f.lineage);assert.notEqual(buildKompasProPublic(a,b,c,{nowMs}).source_shas.latest_json,buildKompasProPublic(Buffer.concat([a,Buffer.from(' ')]),b,c,{nowMs}).source_shas.latest_json)});
test('owner deadline inclusive expiry removes all live values',()=>{const p=run(fixture(),Date.parse('2026-11-24T12:00:00Z'));assert.equal(p.state,'STALE');assert.equal(p.action,null);assert.equal(p.risk,null);assert.equal(p.momentum.direction,null);assert.ok(p.horizons.every(h=>h.action===null&&h.direction===null&&h.bull_bear===null));assert.ok(p.horizon_status.every(h=>!['CURRENT_OBSERVATION','OFFICIAL_DIRECTION_ONLY'].includes(h.status)))});
test('momentum has independent expiry',()=>{const p=run(fixture(),Date.parse('2026-11-24T10:31:00Z'));assert.equal(p.state,'DEGRADED');assert.equal(p.momentum.direction,null);assert.equal(p.action,'HOLD_WAIT')});
test('lineage mismatch blocks live values despite fresh Compass',()=>{const f=fixture();f.lineage.public_issue_number++;const p=run(f);assert.equal(p.state,'INVALID');assert.equal(p.action,null);assert.equal(p.frozen_week,null);assert.ok(p.horizon_status.every(h=>!['CURRENT_OBSERVATION','OFFICIAL_DIRECTION_ONLY'].includes(h.status)))});
test('future issue and unknown direction never promote momentum',()=>{const f=fixture();f.compass.issued_at_utc='2026-11-24T10:01:00Z';f.latest.generated_at='2026-11-24T10:02:00Z';assert.equal(run(f).action,null);const g=fixture();g.compass.market_now.directional_state='UNKNOWN';assert.equal(run(g).momentum.direction,null)});
test('bad balance and risk authority are suppressed',()=>{const f=fixture();f.compass.bull_bear_scale.horizons['1_3d'].bull=9;f.compass.protection_tracker.authority.portfolio_execution=true;const p=run(f);assert.equal(p.state,'DEGRADED');assert.equal(p.risk,null);assert.equal(p.bull_bear,null)});
test('invalid evaluation clock rejected',()=>assert.throws(()=>run(fixture(),NaN)));

test('final binding rejects altered values despite original source digests',async()=>{
 const dir=await mkdtemp(join(tmpdir(),'cn-kompas-binding-'));
 try{
  const f=fixture();
  for(const [name,key] of [['latest.json','latest'],['compass.json','compass'],['publication-lineage.json','lineage']])await writeFile(join(dir,name),bytes(f[key]));
  const original=await finalizeKompasPublic(dir,{nowMs});
  assert.deepEqual(await verifyKompasPublicBinding(dir),original);
  const target=join(dir,'kompas-pro.v1.json');
  for(const mutate of [
   p=>{p.action='BUY'},p=>{p.momentum.direction='BEARISH'},p=>{p.risk.ordinal=5},
   p=>{p.horizons[0].direction='DOWN'},p=>{p.generated_at='2026-02-30T10:00:00.000Z'},
   p=>{p.unreviewed_field=true}
  ]){
   const forged=JSON.parse(JSON.stringify(original));mutate(forged);
   await writeFile(target,JSON.stringify(forged,null,2)+'\n');
   await assert.rejects(verifyKompasPublicBinding(dir),/KOMPAS_PRO_FINAL_(PROJECTION_MISMATCH|BUILD_CLOCK_INVALID)/);
  }
  await writeFile(target,JSON.stringify(original,null,2)+'\n');
  await writeFile(join(dir,'latest.json'),Buffer.concat([bytes(f.latest),Buffer.from(' ')]));
  await assert.rejects(verifyKompasPublicBinding(dir),/KOMPAS_PRO_FINAL_BYTE_BINDING_MISMATCH/);
 }finally{await rm(dir,{recursive:true,force:true})}
});

test('strategic context is evaluated at the supplied build clock, never later wall time',()=>{
 const f=fixture(),issued='2026-11-24T11:00:00Z';
 f.compass.full_stack={...f.compass.full_stack,contract:'PUBLIC_COMPASS_FULL_STACK_READBACK_v1',
  source_status:{strategic:'BOUND_WEEKLY_ANCHOR'},strategic:{status:'BOUND_WEEKLY_ANCHOR',
   authority:'CYCLE_NAVIGATOR_OWNED_NOT_NEW_SITE_FORECAST',issued_at_utc:issued,
   horizon_21_30d:{btc_direction:'UP',eth_direction:'UP',confidence:'LOW'}}};
 const trace={contract:'CN_PREMIUM_SOURCE_TRACE_v1',status:'VERIFIED',long_horizons:[{id:'21_30d',owner:'CYCLE_NAVIGATOR_STRATEGIC_CONTEXT',direction:'UP'}]};
 const runAt=nowMs=>forwardOutlook(f.latest,f.compass,trace,{nowMs}).strategic.available;
 assert.equal(runAt(nowMs),false);
 assert.equal(runAt(Date.parse(issued)-1),false);
 assert.equal(runAt(Date.parse(issued)),true);
 assert.equal(runAt(NaN),false);
});

test('weekly mismatch preserves independently verified closed-candle momentum only',()=>{
 const f=fixture();f.compass.weekly_context.status='MISMATCH';
 const p=run(f);assert.equal(p.state,'DEGRADED');assert.equal(p.action,null);assert.equal(p.risk,null);
 assert.equal(p.momentum.direction,'BULLISH');assert.equal(p.momentum.valid_until,'2026-11-24T10:30:00.000Z');
 assert.ok(p.horizons.every(x=>x.action===null&&x.direction===null&&x.bull_bear===null));
 assert.equal(p.horizon_status.filter(x=>x.status==='CURRENT_OBSERVATION').length,2);
 assert.ok(p.horizon_status.every(x=>x.status!=='OFFICIAL_DIRECTION_ONLY'));
 assert.equal(run(f,Date.parse('2026-11-24T10:30:00Z')).momentum.direction,null);
 for(const mutate of [
  f=>{f.compass.compass_id=''},f=>{f.compass.market_now.new_price_observation=false},
  f=>{f.compass.full_stack.official_freshness.valid_until_utc='2026-11-24T10:00:00Z'},
  f=>{f.latest.generated_at='2026-11-24T10:01:00Z'},
  f=>{f.lineage.public_issue_number++}
 ]){
  const g=fixture();g.compass.weekly_context.status='MISMATCH';mutate(g);
  const q=run(g);assert.equal(q.momentum.direction,null);assert.equal(q.action,null);
  assert.ok(q.horizon_status.every(x=>x.status!=='CURRENT_OBSERVATION'));
 }
});
