import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';

const premium=await readFile(new URL('../market-compass-premium.js',import.meta.url),'utf8');
const header=await readFile(new URL('../public-product.js',import.meta.url),'utf8');
const builder=await readFile(new URL('../build-public.mjs',import.meta.url),'utf8');
const start=premium.indexOf('function officialReadingState(');
const end=premium.indexOf('\nfunction renderPremium(',start);
assert.ok(start>=0&&end>start,'Freshness owner function must exist');
const sandbox={window:{},Date};
vm.createContext(sandbox);
vm.runInContext(premium.slice(start,end)+'\nglobalThis.getReadingState=officialReadingState;',sandbox);
const state=sandbox.getReadingState;
const stamp='2026-10-16T09:30:00Z';
const source='2026-10-16T09:00:00Z';
const expiry='2026-10-16T12:00:00Z';
const clock=t=>Date.parse('2026-10-16T'+t+'Z');
const verified={contract:'PUBLIC_COMPASS_PROJECTION_v1',data_status:'OK',issued_at_utc:stamp,action_now:'HOLD_WAIT',
 full_stack:{source_status:{official:'VERIFIED'},official_freshness:{
  contract:'OFFICIAL_COMPASS_SOURCE_FRESHNESS_READBACK_v1',
  status:'VERIFIED_OWNER_POLICY',source_asof_utc:source,valid_until_utc:expiry}}};
assert.equal(state(verified,clock('10:00:00')),'CURRENT');
assert.equal(state(verified,clock('12:00:00')),'CURRENT');
assert.equal(state(verified,clock('12:00:00.001')),'LAST_VERIFIED');
assert.equal(state(verified,clock('15:00:00')),'LAST_VERIFIED');
assert.equal(state({...verified,data_status:'DEGRADED'},clock('10:00:00')),'UNAVAILABLE');
assert.equal(state({...verified,contract:'UNTRUSTED'},clock('10:00:00')),'UNAVAILABLE');
assert.equal(state({...verified,issued_at_utc:'2099-01-01T00:00:00Z'},clock('10:00:00')),'UNAVAILABLE');
assert.equal(state({...verified,full_stack:{source_status:{official:'UNVERIFIED'},official_freshness:verified.full_stack.official_freshness}},clock('10:00:00')),'UNAVAILABLE');
assert.equal(state({...verified,full_stack:{source_status:{official:'VERIFIED'},official_freshness:{status:'UNAVAILABLE'}}},clock('10:00:00')),'UNAVAILABLE');
assert.equal(state({...verified,full_stack:{source_status:{official:'VERIFIED'},official_freshness:{...verified.full_stack.official_freshness,source_asof_utc:'2026-10-17T00:00:00Z'}}},clock('10:00:00')),'UNAVAILABLE');
assert.match(builder,/source_bindings\?\.auto_market_state\?\.freshness/,'Use the original verified owner policy');
assert.match(builder,/official_freshness:officialValid\?officialFreshness/,'Projected owner policy');
assert.match(header,/window\.CNOfficialReadingState\?\.\(officialCompass\)/,'Header must share state function');
assert.match(premium,/LAST VERIFIED ACTION · NOT CURRENT/,'Stale must be explicitly historical');
assert.match(premium,/dataOk \? '<div class="premium-action-window"/,'Only CURRENT shows APPLIES NOW window');
assert.match(premium,/scheduleFreshnessExpiry\(snapshot,compass,event\)/,'Expiration schedules in-place rerender');
console.log('OFFICIAL_COMPASS_FRESHNESS_3STATE_PASS');
