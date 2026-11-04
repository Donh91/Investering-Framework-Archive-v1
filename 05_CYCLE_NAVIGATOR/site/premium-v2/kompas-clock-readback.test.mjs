import test from 'node:test';
import assert from 'node:assert/strict';
import {kompasSourceClockReadback} from './kompas-clock-readback.mjs';

const now=Date.parse('2026-11-04T12:00:00Z');
const compass={
 contract:'PUBLIC_COMPASS_PROJECTION_v1',
 data_status:'OK',compass_id:'CMP-1',
 issued_at_utc:'2026-11-04T11:00:00Z',
 weekly_context:{status:'ALIGNED',forecast_week:'2026-W45'},
 full_stack:{official_freshness:{valid_until_utc:'2026-11-04T13:00:00Z'}},
 market_now:{market_observation_open_utc:'2026-11-04T11:00:00Z',
   predecessor_market_observation_open_utc:'2026-11-04T10:00:00Z',
   new_price_observation:true,directional_state:'BULLISH'}
};
const view={compass:{state:'FRESH',permit_path_live_gates:true,compass_id:'CMP-1'},
 weekly:{forecast_week:'2026-W45'}};
const read=(extra={})=>kompasSourceClockReadback({compass,view,now,...extra});

test('separates original Official validity from completed hourly market observation',()=>{
 const r=read();
 assert.equal(r.contract,'CN_KOMPAS_PRO_DUAL_SOURCE_CLOCK_v2');
 assert.equal(r.official.status,'CURRENT');
 assert.equal(r.observation.status,'CURRENT');
 assert.match(r.official.label,/gælder til/);
 assert.match(r.observation.label,/Kompas-måling afsluttet/);
 assert.ok(!r.official.label.includes('timekurs'));
});

test('expiry never revives official decision and hourly remains independent',()=>{
 const expired=read({now:Date.parse('2026-11-04T15:00:00Z'),
   view:{...view,compass:{...view.compass,state:'EXPIRED'}}});
 assert.equal(expired.official.status,'EXPIRED');
 assert.equal(expired.observation.status,'DELAYED');
 assert.equal(expired.official.tone,'warning');
});

test('missing and mismatched provenance suppresses both clocks',()=>{
 for(const v of [
  {...view,compass:{...view.compass,compass_id:'FAKE'}},
  {...view,weekly:{forecast_week:'2026-W44'}}
 ]){
  const r=read({view:v});
  assert.equal(r.official.status,'UNAVAILABLE');
  assert.equal(r.observation.status,'UNAVAILABLE');
 }
 const forged=read({compass:{...compass,contract:'FORGED'}});
 assert.equal(forged.observation.status,'UNAVAILABLE');
});

test('no-new-hour, stale-hour and future-hour fail closed separately',()=>{
 const noNew=read({compass:{...compass,market_now:{...compass.market_now,new_price_observation:false}}});
 assert.equal(noNew.observation.status,'NO_NEW_OBSERVATION');
 const late=read({now:Date.parse('2026-11-04T13:40:00Z')});
 assert.equal(late.observation.status,'DELAYED');
 const future=read({compass:{...compass,market_now:{...compass.market_now,
  market_observation_open_utc:'2026-11-04T13:00:00Z'}}});
 assert.equal(future.observation.status,'UNAVAILABLE');
});

test('English labels never convert a measured hour to predictive 12-hour forecast',()=>{
 const r=read({lang:'en'});
 assert.match(r.official.label,/valid until/);
 assert.match(r.observation.label,/Compass price observation completed/);
 assert.doesNotMatch(r.observation.label,/forecast|predictive/i);
});

test('valid Official can have delayed basis without being a live price',()=>{
 const c={...compass,market_now:{...compass.market_now,
  market_observation_open_utc:'2026-11-04T08:00:00Z',
  predecessor_market_observation_open_utc:'2026-11-04T07:00:00Z'}};
 const x=read({compass:c});
 assert.equal(x.official.status,'CURRENT');
 assert.equal(x.observation.status,'DELAYED');
 assert.equal(x.tone,'qualified');
 assert.match(x.context,/ældre end 90 min/);
 assert.match(x.explanation,/ikke en livekurs/);
});
test('verified newer Hourly window never refreshes Official',()=>{
 const c={...compass,market_now:{...compass.market_now,
  market_observation_open_utc:'2026-11-04T08:00:00Z',
  predecessor_market_observation_open_utc:'2026-11-04T07:00:00Z'},
  public_data_health:{contract:'CN_PUBLIC_DATA_HEALTH_v1',
   hourly_status:'COMPLETE',native_data_health:'PASS',
   latest_complete_market_hour_utc:'2026-11-04T11:00:00Z',
   hourly_retrieved_at_utc:'2026-11-04T11:10:00Z'}};
 const x=read({compass:c});
 assert.equal(x.hourlyStatus,'NEWER_HOURLY_UNBOUND');
 assert.equal(x.official.status,'CURRENT');
 assert.match(x.explanation,/ændrer ikke/);
 const bad={...c,public_data_health:{...c.public_data_health,
   latest_complete_market_hour_utc:'2026-11-04T14:00:00Z'}};
 assert.equal(read({compass:bad}).hourlyStatus,'UNAVAILABLE');
});
test('single coherent English copy is not a forecast',()=>{
 const x=read({lang:'en'});
 assert.match(x.headline,/valid until/);
 assert.match(x.context,/Price evidence from/);
 assert.doesNotMatch(x.headline+' '+x.context,/probability|forecast/i);
});
