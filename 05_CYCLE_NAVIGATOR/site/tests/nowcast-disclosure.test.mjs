import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';

const source=await readFile(new URL('../compass-product-v5.js',import.meta.url),'utf8');
const da=JSON.parse(await readFile(new URL('../i18n-da.json',import.meta.url),'utf8'));
async function render(compass){
  const root={innerHTML:''};
  const document={readyState:'complete',getElementById:id=>id==='productNow'?root:null,addEventListener:()=>{}};
  const context={document,window:{CNI18n:{language:'en'}},Intl,Date,console,
    setTimeout:fn=>fn(),setInterval:()=>{},
    fetch:async url=>({ok:true,json:async()=>url.includes('compass-event')?{}:compass})};
  vm.runInNewContext(source,context);
  await new Promise(resolve=>setImmediate(resolve));
  return root.innerHTML;
}
const fresh={contract:'PUBLIC_COMPASS_PROJECTION_v1',data_status:'OK',issued_at_utc:'2026-10-28T12:00:00Z',
 market_now:{directional_state:'BULLISH'},action_now:'HOLD_WAIT',
 horizons:{NEXT_12H:{expected_direction:'DOWN',expected_path:'FORGED FUTURE PATH'},NEXT_1_3D:{},NEXT_5_7D:{}}};
const html=await render(fresh);
assert.match(html,/CURRENT MOMENTUM<\/span><p>BULLISH/);
assert.match(html,/not a validated 12-hour forecast/);
assert.doesNotMatch(html,/FORGED FUTURE PATH|NEXT 12 HOURS|next-compass-countdown|08:17 \/ 20:17/);
const missing=structuredClone(fresh);delete missing.market_now;
assert.match(await render(missing),/CURRENT MOMENTUM<\/span><p>UNAVAILABLE/);
const stale=structuredClone(fresh);stale.data_status='DEGRADED';
const staleHtml=await render(stale);
assert.doesNotMatch(staleHtml,/CURRENT MOMENTUM|BULLISH|FORGED FUTURE PATH/);
assert.match(staleHtml,/fresh navigation is temporarily unavailable/);
const dict=da.translations||da;
assert.ok(JSON.stringify(dict).includes('Aktuel retningsindikator, ikke en valideret 12-timersprognose.'));
console.log('PASS nowcast source, missing/stale fail-closed, cadence and DA disclosure');
