/** Navigator One M3: a versioned, read-only projection of exact public CN bytes.
 * No forecasts, permissions, providers, timers or private inputs.
 * Hashes bind bytes, not trust in the hosting origin; consumers must recheck expiry.
 */
import {createHash} from 'node:crypto';
import {inspectOfficialPublicFeeds} from '../vnext-live/official-feed-parity.mjs';
import {officialBullBear} from '../vnext-live/official-bullbear.mjs';
import {observedMarketClock} from './compass-overview.mjs';
import {kompasHorizonStatusRows} from './kompas-horizon-status.mjs';
import {sourceTrace} from '../vnext-live/source-trace.mjs';
import {forwardOutlook} from '../vnext-live/forward-outlook.mjs';
export const CONTRACT='CN_KOMPAS_PRO_PUBLIC_v1';
const actions=['HOLD_WAIT','HOLD','WAIT','HARD_WAIT','ABSTAIN','NO_EDGE','WATCH','PREPARE','BUY','SELL','REDUCE','PREPARE_BUY','PREPARE_SELL'];
const directions=['UP','DOWN','MIXED','SIDEWAYS','LEAN_BEARISH','LEAN_BULLISH','NO_EDGE'];
const observations=['BULLISH','BEARISH','NEUTRAL','MIXED','UP','DOWN','SIDEWAYS'];
const riskClasses=['NORMAL','BUILDING','ELEVATED','HIGH','CONFIRMED'];
const horizonIds=['NEXT_1_3D','NEXT_5_7D','NEXT_2_3W','CYCLE_ALTCOINS_3_8W'];
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const iso=n=>Number.isFinite(n)?new Date(n).toISOString():null;
const timestamp=s=>typeof s==='string'&&/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z$/.test(s)&&Number.isFinite(Date.parse(s))?Date.parse(s):NaN;
const known=(a,v)=>a.includes(v)?v:null;
export function buildKompasProPublic(latestBytes,compassBytes,{nowMs=Date.now()}={}){
 if(!Number.isFinite(nowMs))throw Error('INVALID_PUBLIC_BUILD_CLOCK');
 const source_shas={latest_json:hash(latestBytes),compass_json:hash(compassBytes)};
 const latest=JSON.parse(latestBytes),compass=JSON.parse(compassBytes);
 const view=inspectOfficialPublicFeeds(latest,compass,{nowUtc:iso(nowMs)});
 const expiry=timestamp(compass?.full_stack?.official_freshness?.valid_until_utc);
 const issued=timestamp(compass?.issued_at_utc),delivered=timestamp(latest?.generated_at);
 const validUntil=Math.min(expiry,issued+86400000,delivered+86400000);
 const current=view.compass.state==='FRESH'&&view.compass.permit_path_live_gates===true&&
  Number.isFinite(validUntil)&&nowMs<validUntil;
 const action=current?known(actions,view.compass.action_now):null;
 const clock=current?observedMarketClock({compass,now:nowMs}):{state:'SOURCE_UNAVAILABLE'};
 const momentumDirection=clock.state==='FRESH_OBSERVATION'?known(observations,compass.market_now?.directional_state):null;
 const momentumUntil=momentumDirection?Math.min(validUntil,timestamp(compass.market_now.market_observation_open_utc)+9000000):NaN;
 const risk=current?view.compass.pullback_stage:null;
 const riskClass=known(riskClasses,risk?.source_risk_state);
 const balance=current?officialBullBear(compass,'1_3d'):null;
 const horizons=horizonIds.map(id=>({id,direction:current?known(directions,compass.horizons?.[id]?.expected_direction):null,
  action:current?known(actions,compass.horizons?.[id]?.action_posture):null}));
 let trace=null,strategic=null;try{trace=sourceTrace(latest,compass,view);strategic=forwardOutlook(latest,compass,trace)}catch{}
 const matrix=kompasHorizonStatusRows({compass,view,lang:'da',observationCurrent:!!momentumDirection,trace,strategic});
 const reason=!current?'OFFICIAL_SOURCE_NOT_CURRENT':!action?'ACTION_UNRECOGNIZED':!balance||!riskClass||!momentumDirection||horizons.some(h=>!h.direction)?'PARTIAL_CARD_EVIDENCE':null;
 const state=!current?(Number.isFinite(validUntil)&&nowMs>=validUntil?'STALE':'INVALID'):reason?'DEGRADED':'OK';
 return {contract:CONTRACT,version:1,authority:'READ_ONLY_PRESENTATION',state,reasons:reason?[reason]:[],
  generated_at:iso(nowMs),issued_at:iso(issued),valid_until:iso(validUntil),source_shas,
  compass_id:current?compass.compass_id:null,forecast_week:view.weekly.forecast_week,
  action,momentum:{state:momentumDirection?'FRESH_OBSERVATION':clock.state==='FRESH_OBSERVATION'?'UNKNOWN_DIRECTION':clock.state,
    direction:momentumDirection,valid_until:iso(momentumUntil)},
  bull_bear:balance,risk:riskClass?{class:riskClass,ordinal:riskClasses.indexOf(riskClass)+1}:null,
  horizons,horizon_status:matrix.rows.map(({id,kind,status,tone})=>({id,kind,status,tone}))};
}
