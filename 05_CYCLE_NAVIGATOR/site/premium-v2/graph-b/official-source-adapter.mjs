/**
 * Premium v2.1 / Graph B · SOURCE-ONLY domain adapter.
 * Development-only; NOT wired to Pages root/build-public.
 * Mirrors canonical source gates in site/frozen-week-chart.js instead of
 * deriving market predictions from graphic geometry.
 * No I/O, remote providers, mutable scores, Math.sin or synthetic sample data.
 */
const DAY=86400000;
const HOUR=3600000;
const NUM=x=>typeof x==='number'&&Number.isFinite(x)&&x>0;
const date=t=>typeof t==='string'?Date.parse(t):NaN;
const empty=(asset,reason)=>({
 contract:'CN_PREMIUM_V2_GRAPH_B_PRESENTATION_v1',
 asset,source_status:'UNAVAILABLE',source_reason:reason,
 forecast_status:'UNAVAILABLE',forecast:[],bands:[],
 actual_segments:[],hourly_observations:[],last_observed_at_utc:null,
 live_freshness:'UNAVAILABLE',is_current_quote:false,
 proof_authority:false,score_authority:false
});
function runs(points){
 const out=[];let current=[];
 for(const p of points){
   if(current.length&&p.time-current.at(-1).time!==HOUR/1000){
     out.push(current);current=[];
   }
   current.push(p);
 }
 if(current.length)out.push(current);
 return out;
}
export function readOfficialGraphB(snapshot,asset,{now_utc,publication_lineage=null}={}){
 const bad=reason=>empty(asset,reason);
 if(asset!=='BTC'&&asset!=='ETH')return bad('UNSUPPORTED_ASSET');
 const now=date(now_utc);
 if(!Number.isFinite(now))return bad('NOW_CLOCK_UNVERIFIED');
 if(snapshot?.schema!=='CN_PUBLIC_SNAPSHOT_V2')return bad('SNAPSHOT_CONTRACT_MISMATCH');
 const pub=snapshot?.public_series?.current_public_projection||{},m=snapshot?.public_live_precision;
 if(m?.contract!=='CN_PUBLIC_LIVE_PRICE_PRECISION_v1'||
    m.public_issue_number!==pub.public_issue_number||
    m.forecast_week!==pub.forecast_week||
    !/^\d{4}-W\d{2}$/.test(String(m.forecast_week||'')))return bad('PUBLIC_WEEK_OR_ISSUE_MISMATCH');
 const a=m?.window_scores?.day_1_2,b=m?.window_scores?.day_5_7;
 const start=date(a?.window_start_utc),end=date(b?.window_end_utc);
 if(!Number.isFinite(start)||end-start!==7*DAY)return bad('FROZEN_WEEK_BOUNDS_INVALID');
 const keys=['day_1_2','day_3_4','day_5_7'];
 const rows=keys.map(w=>(m.rows||[]).find(x=>x.asset===asset&&x.window===w));
 if(rows.some(r=>!r||!NUM(r.forecast_low)||!NUM(r.forecast_high)||r.forecast_low>=r.forecast_high))
   return bad('ORIGINAL_RANGE_EVIDENCE_INVALID');
 const obs=m?.daily_observations;
 const cutoff=date(obs?.observed_through_utc||m.live_as_of_utc);
 if(obs?.contract!=='CN_PUBLIC_DAILY_OBSERVATIONS_v1'||
    !Number.isFinite(cutoff)||cutoff>now||cutoff>end)return bad('OBSERVATION_CUTOFF_INVALID');
 const h=m.hourly_price_path;
 if(h?.contract!=='CN_PUBLIC_HOURLY_PRICE_PATH_v1'||
    h.source!=='HOURLY_SPOT_PASS_ONLY'||
    h.semantics!=='OBSERVED_HOURLY_CLOSE_NOT_A_PROSPECTIVE_FORECAST'||
    h.forecast_week!==m.forecast_week||
    h.public_issue_number!==m.public_issue_number||
    h.observed_through_utc!==obs.observed_through_utc)return bad('HOURLY_SOURCE_PROVENANCE_INVALID');
 const raw=h[asset];
 if(!Array.isArray(raw)||raw.length>168)return bad('HOURLY_ROWS_INVALID');
 let prev=start,valid=true;
 const points=raw.map(p=>{
   const t=date(p?.observed_at_utc);
   if(!/^\d{4}-\d{2}-\d{2}T\d{2}:00:00Z$/.test(String(p?.observed_at_utc||''))||
      !NUM(p?.close)||!Number.isFinite(t)||t<=prev||
      t>cutoff||t>now||t>end||(t-start)%HOUR!==0)valid=false;
   prev=t;
   return {time:t/1000,value:p?.close,observed_at_utc:p?.observed_at_utc};
 });
 if(!valid)return bad('HOURLY_SAMPLES_UNVERIFIED');
 const lowHigh=rows.map((r,i)=>({id:keys[i],forecast_low:r.forecast_low,forecast_high:r.forecast_high,
   window_start_utc:m.window_scores[keys[i]]?.window_start_utc,
   window_end_utc:m.window_scores[keys[i]]?.window_end_utc}));
 const freeze=m.daily_price_path,block=freeze?.[asset];
 let forecast=[],forecastStatus='UNAVAILABLE';
 if(freeze?.contract==='CN_FROZEN_DAILY_PRICE_PATH_v1'&&freeze.forecast_week===m.forecast_week&&block?.status==='PUBLISHED'){
   const issued=date(m.frozen_at_utc),values=block.points;
   const firstEligible=date(m.scoring_valid_from_utc||a?.scoring_start_utc);
   const good=Number.isFinite(issued)&&Number.isFinite(firstEligible)&&firstEligible>=start&&firstEligible<end&&
      issued<=now&&issued<firstEligible&&Array.isArray(values)&&values.length===7&&
      values.every((p,i)=>p?.day===i+1&&NUM(p?.expected_close)&&NUM(p?.low)&&NUM(p?.high)&&
      p.low<p.high&&p.low<=p.expected_close&&p.expected_close<=p.high);
   if(good){
     forecast=values.map((p,i)=>({day:i+1,time:(start+(i+1)*DAY)/1000,
       expected_close:p.expected_close,low:p.low,high:p.high}));
     forecastStatus='SOURCE_ISSUED';
   }else forecastStatus='PUBLISHED_INVALID_FAIL_CLOSED';
 }
 const age=now-cutoff;
 const stale=age>Math.max(30,Number(m.freshness_sla_minutes)||90)*60000;
 const lineageOK=!publication_lineage||(
   publication_lineage.contract==='CN_PUBLICATION_LINEAGE_RELEASE_RECEIPT_v1'&&
   publication_lineage.forecast_week===m.forecast_week&&
   publication_lineage.public_issue_number===m.public_issue_number&&
   publication_lineage.source_to_public_equality==='PASS'&&
   publication_lineage.last_observed_close_utc===h.observed_through_utc
 );
 if(!lineageOK)return bad('PUBLIC_RELEASE_LINEAGE_MISMATCH');
 return {
   contract:'CN_PREMIUM_V2_GRAPH_B_PRESENTATION_v1',
   asset,public_issue_number:m.public_issue_number,forecast_week:m.forecast_week,
   source_status:'SOURCE_BOUNDED',source_reason:null,
   forecast_status:forecastStatus,forecast,bands:lowHigh,
   hourly_observations:points,actual_segments:runs(points),
   last_observed_at_utc:h.observed_through_utc,
   live_freshness:stale?'STALE':'FRESH',
   source_freshness_sla_minutes:Math.max(30,Number(m.freshness_sla_minutes)||90),
   is_current_quote:!stale&&points.length>0,
   first_known_frozen_at_utc:m.frozen_at_utc||null,
   publication_lineage_status:publication_lineage?'MATCHED':'NOT_PROVIDED',
   proof_authority:false,score_authority:false
 };
}
/**
 * Only eligible actual observations at or before a selected original UTC hour.
 * No extrapolation, synthetic interpolation or recomputation of frozen forecast.
 */
export function replayObservedUntil(model,utc_hour){
 if(model?.contract!=='CN_PREMIUM_V2_GRAPH_B_PRESENTATION_v1'||
   !Array.isArray(model.hourly_observations))return [];
 const until=date(utc_hour);
 if(!Number.isFinite(until))return [];
 return runs(model.hourly_observations.filter(p=>p.time*1000<=until));
}
