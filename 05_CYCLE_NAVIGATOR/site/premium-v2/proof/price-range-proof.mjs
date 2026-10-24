/**
 * Price Range Proof window presenter (read-only, no scoring).
 * Source owner: public CN live_precision only.
 * Edge claims and accuracy are a separate, independent score family.
 */
const WINS=['day_1_2','day_3_4','day_5_7'];
const valid=x=>typeof x==='number'&&Number.isFinite(x)&&x>=0&&x<=100;
const safePos=x=>typeof x==='number'&&Number.isFinite(x)&&x>0;
const parse=x=>typeof x==='string'?Date.parse(x):NaN;
function gone(reason){return{contract:'CN_PREMIUM_V2_PRICE_RANGE_PROOF_v1',
 status:'UNAVAILABLE',reason,window_items:[],price_range_family:null,public_issue_number:null,
 forecast_week:null,score_sealed:false,proof_sealed:false}}
export function sourceOnlyPriceRangeProof(snapshot,{now_utc}={}){
 const bad=reason=>gone(reason),now=parse(now_utc);
 if(!Number.isFinite(now))return bad('CLOCK_UNVERIFIED');
 if(snapshot?.schema!=='CN_PUBLIC_SNAPSHOT_V2')return bad('LATEST_SCHEMA_UNSUPPORTED');
 const m=snapshot.public_live_precision,pub=snapshot.public_series?.current_public_projection;
 if(m?.contract!=='CN_PUBLIC_LIVE_PRICE_PRECISION_v1'||
    m.public_issue_number!==pub?.public_issue_number||
    m.forecast_week!==pub?.forecast_week||
    m.score_family!=='PRICE_RANGE_PRECISION'||
    m.formula!=='70pct_containment_plus_30pct_jaccard')
   return bad('LIVE_SOURCE_OR_SCORE_FAMILY_UNVERIFIED');
 const issued=parse(m.frozen_at_utc),first=parse(m.scoring_valid_from_utc),cutoff=parse(m.live_as_of_utc);
 if(!Number.isFinite(issued)||!Number.isFinite(first)||issued>=first||
    !Number.isFinite(cutoff)||cutoff>now)return bad('ISSUANCE_OR_OBSERVATION_CLOCK_UNVERIFIED');
 const results=[];
 for(const id of WINS){
  const w=m.window_scores?.[id];
  if(!w)return bad('SOURCE_WINDOW_MISSING');
  const beginning=parse(w.window_start_utc),end=parse(w.window_end_utc);
  const scoring=parse(w.scoring_start_utc);
  if(!Number.isFinite(beginning)||!Number.isFinite(end)||end<=beginning||
     !Number.isFinite(scoring)||scoring<beginning||scoring>=end)return bad('WINDOW_TIME_UNVERIFIED');
  // The canonical hourly producer publishes NOT_STARTED before a window opens.
  // Normalize ONLY for display; never manufacture observations or scores.
  const phase=w.phase==='NOT_STARTED'?'PENDING':w.phase;
  if(phase!=='COMPLETE'&&phase!=='LIVE'&&phase!=='PENDING')return bad('WINDOW_PHASE_INVALID');
  const count=Number(w.observed_hours),expected=Number(w.expected_hours_final),
    scored=Number(w.rows_scored),total=Number(w.rows_total);
  if(![count,expected,scored,total].every(Number.isInteger)||
     count<0||expected<=0||count>expected||scored<0||total!==2||
     scored>total)return bad('SOURCE_WINDOW_COVERAGE_INVALID');
  const complete=phase==='COMPLETE'&&count===expected&&w.coverage_complete_to_date===true&&cutoff>=end;
  if(phase==='COMPLETE'&&!complete)return bad('MISLABELED_COMPLETE_WINDOW');
  if(phase==='LIVE'&&!(cutoff<end&&cutoff>=scoring))return bad('MISLABELED_LIVE_WINDOW');
  if(phase==='PENDING'&&(count!==0||scored!==0||valid(w.score_to_date)))return bad('PENDING_HAS_OBSERVATIONS');
  const rows=['BTC','ETH'].map(asset=>(m.rows||[]).find(row=>row.asset===asset&&row.window===id));
  if(rows.some(row=>!row||!safePos(row.forecast_low)||!safePos(row.forecast_high)||
    row.forecast_low>=row.forecast_high))return bad('FROZEN_RANGE_INVALID');
  const recorded=phase!=='PENDING'&&scored===2&&valid(w.score_to_date);
  if(phase==='COMPLETE'&&!recorded)return bad('COMPLETE_SCORE_MISSING');
  results.push({
   window:id,state:complete?'WINDOW_OBSERVED_COMPLETE':phase==='LIVE'?'WINDOW_IN_PROGRESS':'PENDING',
   start_utc:w.window_start_utc,end_utc:w.window_end_utc,
   frozen_sequence_text:typeof w.frozen_sequence_text==='string'?w.frozen_sequence_text:'',
   original_ranges:rows.map(row=>({asset:row.asset,low:row.forecast_low,high:row.forecast_high})),
   observed_hours:count,expected_hours_final:expected,
   coverage_ratio:count/expected,
   observed_complete:complete,
   source_reported_score_to_date:recorded?w.score_to_date:null,
   source_score_status:recorded?'SOURCE_REPORTED_NOT_INDEPENDENTLY_SEALED':'UNAVAILABLE'
  });
 }
 return {
  contract:'CN_PREMIUM_V2_PRICE_RANGE_PROOF_v1',status:'PROVISIONAL_SOURCE_READBACK',
  forecast_week:m.forecast_week,public_issue_number:m.public_issue_number,
  freeze_issued_at_utc:m.frozen_at_utc,scoring_valid_from_utc:m.scoring_valid_from_utc,
  live_as_of_utc:m.live_as_of_utc,
  source_stale:now-cutoff>Math.max(30,Number(m.freshness_sla_minutes)||90)*60000,
  window_items:results,price_range_family:m.score_family,formula:m.formula,
  edge_score:null,score_sealed:false,proof_sealed:false
 };
}
