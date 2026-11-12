import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {importantStatusLine,btcNextDays,extraHorizonRows} from './kompas-owner-brief.mjs';

const now=Date.parse('2026-11-10T09:10:00Z');
function feeds(over={}){
 const compass={
  contract:'PUBLIC_COMPASS_PROJECTION_v1',data_status:'OK',compass_id:'CMP-1',
  issued_at_utc:'2026-11-10T08:24:34Z',action_now:'HOLD_WAIT',
  weekly_context:{status:'ALIGNED',forecast_week:'2026-W46'},
  full_stack:{contract:'PUBLIC_COMPASS_FULL_STACK_READBACK_v1',
   official_freshness:{valid_until_utc:'2026-11-10T11:00:00.000Z'},
   native:{now:'HOLD_WAIT',data_health:'PASS',checked_at_utc:'2026-11-10T08:53:30Z',official_source_aligned:false}},
  ...over};
 const view={compass:{state:'FRESH',permit_path_live_gates:true,compass_id:'CMP-1'},
  weekly:{state:'DEGRADED',forecast_week:'2026-W46',btc_range:{low:71289.02,high:76967.74}}};
 return {compass,view};
}

test('important status states official issue and the newer native check, never a new action',()=>{
 const {compass,view}=feeds();
 const s=importantStatusLine({compass,view,lang:'da',now});
 assert.equal(s.text,'Officiel udgave 09.24: Afvent. Nyere kontrol 09.53: Afvent, ikke afstemt med officiel udgave. Kun den officielle vurdering styrer handlingen.');
 assert.equal(s.tone,'warning');
 const en=importantStatusLine({compass,view,lang:'en',now});
 assert.match(en.text,/^Official issue 09:24: Wait\. Newer check 09:53: Wait, not aligned/);
});

test('degraded native check is labelled from its typed enum only',()=>{
 const base=feeds();
 const {compass,view}=feeds({full_stack:{...base.compass.full_stack,
  native:{now:'HOLD_WAIT_DATA_DEGRADED',data_health:'DEGRADED',checked_at_utc:'2026-11-10T08:48:00Z',official_source_aligned:true}}});
 const s=importantStatusLine({compass,view,lang:'da',now});
 assert.match(s.text,/Nyere kontrol 09\.48: Afvent · datakvalitet forringet\./);
 assert.equal(s.tone,'warning');
});

test('no status line when the official issue is not current or the action is unknown',()=>{
 const {compass,view}=feeds();
 assert.equal(importantStatusLine({compass,view,now:Date.parse('2026-11-10T11:30:00Z')}),null);
 assert.equal(importantStatusLine({compass:{...compass,action_now:'BUY'},view,now}),null);
 const older=feeds({full_stack:{...compass.full_stack,native:{...compass.full_stack.native,checked_at_utc:'2026-11-10T08:00:00Z'}}});
 const s=importantStatusLine({...older,now});
 assert.equal(s.text,'Officiel udgave 09.24: Afvent. Kun den officielle vurdering styrer handlingen.');
 assert.equal(s.tone,'ok');
});

const daily=[[73710.46,75323.22,74516.84],[73380.59,75129.64,74255.12],[73478.41,75363.75,74421.08],
 [73196.41,75218.03,74207.22],[73554.76,75712.67,74633.72],[73796.41,76090.61,74943.51],[73584.69,76015.18,74799.94]]
 .map(([low,high,expected_close],i)=>({day:i+1,low,high,expected_close}));
const readback={status:'SOURCE_ISSUED_BOTH',quote:'USDT',forecast_week:'2026-W46',BTC:{original_daily:daily}};

test('BTC next three days are the original frozen points, starting today (UTC day)',()=>{
 const {view}=feeds();
 const r=btcNextDays({readback,view,nowUtc:'2026-11-10T09:10:00Z',lang:'da'});
 assert.deepEqual(r.rows.map(x=>x.day),[2,3,4]);
 assert.equal(r.rows[0].range,'73.381–75.130 USDT');
 assert.equal(r.rows[0].close,'forventet luk 74.255');
 assert.match(r.rows[0].label,/^I dag · /);
 assert.equal(r.weekRange,'71.289–76.968 USDT');
 assert.match(r.caption,/Oprindeligt frosset 2026-W46/);
 const sunday=btcNextDays({readback,view,nowUtc:'2026-11-15T20:00:00Z'});
 assert.deepEqual(sunday.rows.map(x=>x.day),[7]);
 assert.equal(btcNextDays({readback,view,nowUtc:'2026-11-16T01:00:00Z'}),null,'next week: no stale rows');
});

test('BTC days fail closed without a verified original readback or with a foreign week range',()=>{
 const {view}=feeds();
 assert.equal(btcNextDays({readback:{...readback,status:'UNAVAILABLE'},view,nowUtc:'2026-11-10T09:00:00Z'}),null);
 assert.equal(btcNextDays({readback:{...readback,quote:'USD'},view,nowUtc:'2026-11-10T09:00:00Z'}),null);
 const r=btcNextDays({readback,view:{weekly:{...view.weekly,forecast_week:'2026-W45'}},nowUtc:'2026-11-10T09:00:00Z'});
 assert.equal(r.weekRange,null);
});

test('extra horizon rows only copy already-verified readbacks',()=>{
 const matrix={rows:[{id:'H0_12H',value:'Måling ikke frisk',sourceLabel:'Observeret momentum, ikke prognose',tone:'missing'}]};
 const x=extraHorizonRows({matrix,reading:{direction:'Ingen sikker vurdering',posture:'Ikke fastlagt',hasDirection:false},lang:'da'});
 assert.deepEqual(x.h12,{direction:'Måling ikke frisk',position:'Måling, ikke prognose',tone:'missing'});
 assert.deepEqual(x.c38,{direction:'Ingen sikker vurdering',position:'Ikke fastlagt',tone:'missing'});
 const none=extraHorizonRows({matrix:null,reading:null});
 assert.equal(none.c38.direction,'Afventer gyldig kilde');
});

test('the owner-brief module never fetches, scores or computes probabilities',async()=>{
 const raw=await readFile(new URL('./kompas-owner-brief.mjs',import.meta.url),'utf8');
 const src=raw.replace(/\/\*[\s\S]*?\*\//g,'').replace(/\/\/.*$/gm,'');
 assert.doesNotMatch(src,/fetch\(|probabilit|Math\.random/);
});

test('the altcoin lane is labelled 4–8 weeks after the owner decision; no conflict note remains',async()=>{
 const root=await readFile(new URL('./unified-root.mjs',import.meta.url),'utf8');
 const reader=await readFile(new URL('./compass-reader.mjs',import.meta.url),'utf8');
 assert.match(root,/4–8 uger · altcoins/);
 assert.match(root,/data-cn-reader-horizon="CYCLE_ALTCOINS_3_8W" aria-pressed="false">4–8 uger</);
 assert.match(reader,/CYCLE_ALTCOINS_3_8W',da:'4–8 uger',en:'4–8 weeks'/);
 assert.doesNotMatch(root+reader,/3–8 uger|cn-overview-c38-note/);
});
