import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {buildKompasProPublic} from './kompas-pro-public-v1.mjs';
const nowMs=Date.parse('2026-11-24T10:00:00Z');
const bytes=x=>Buffer.from(JSON.stringify(x)+'\n');
test('wrong contracts suppress all current values, exact byte bindings',()=>{
 const a=bytes({schema:'WRONG'}),b=bytes({contract:'WRONG',action_now:'BUY'});
 const p=buildKompasProPublic(a,b,{nowMs});
 assert.equal(p.state,'INVALID');assert.equal(p.action,null);assert.equal(p.bull_bear,null);
 assert.equal(p.risk,null);assert.equal(p.momentum.direction,null);
 assert.equal(p.horizons.length,4);assert.equal(p.horizon_status.length,14);
 assert.ok(p.horizons.every(h=>h.action===null&&h.direction===null));
 assert.equal(p.source_shas.latest_json,createHash('sha256').update(a).digest('hex'));
 assert.notEqual(p.source_shas.latest_json,buildKompasProPublic(Buffer.from(a.toString().trim()),b,{nowMs}).source_shas.latest_json);
});
test('expired owner deadline never creates current action',()=>{
 const a=bytes({schema:'CN_PUBLIC_SNAPSHOT_V2',generated_at:'2026-11-24T09:00:00Z'});
 const b=bytes({contract:'PUBLIC_COMPASS_PROJECTION_v1',issued_at_utc:'2026-11-24T08:00:00Z',action_now:'BUY',full_stack:{official_freshness:{valid_until_utc:'2026-11-24T09:30:00Z'}}});
 const p=buildKompasProPublic(a,b,{nowMs});assert.equal(p.state,'STALE');assert.equal(p.action,null);assert.equal(p.valid_until,'2026-11-24T09:30:00.000Z');
});
test('invalid clock rejected',()=>assert.throws(()=>buildKompasProPublic(bytes({}),bytes({}),{nowMs:NaN})));
