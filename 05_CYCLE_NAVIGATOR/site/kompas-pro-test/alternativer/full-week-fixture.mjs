/**
 * GitHub-only, isolated complete-week Kompas PRO visual QA.
 * SYNTHETIC PRICES ONLY. Never sourced by public market/data producers.
 * Reuses the unchanged canonical CNWeekChart model and forecast coordinates.
 */
export const WEEK="2026-W46";
export const MONDAY="2026-11-09T00:00:00Z";
export const ASSETS=Object.freeze({
 BTC:Object.freeze({
   close:Object.freeze([101850,102700,102350,103900,104450,104050,105580]),
   low:Object.freeze([100900,101200,101550,102650,103150,102880,104100]),
   high:Object.freeze([102650,103650,103100,104800,105300,105200,106650]),
   observed:Object.freeze([101430,101820,103110,102860,104090,103480,105020,104870]),
   ripple:245
 }),
 ETH:Object.freeze({
   close:Object.freeze([3520,3575,3548,3624,3658,3635,3710]),
   low:Object.freeze([3455,3490,3480,3550,3580,3565,3630]),
   high:Object.freeze([3590,3630,3620,3690,3730,3720,3790]),
   observed:Object.freeze([3500,3512,3585,3558,3626,3598,3693,3680]),
   ripple:13
 })
});
const HOUR=3600000;
const DAY=24*HOUR;
const START=Date.parse(MONDAY);
const UTC=ms=>new Date(ms).toISOString().replace(".000Z","Z");
const clone=v=>JSON.parse(JSON.stringify(v));
export function frozenSource(){
 const dailyPath={contract:"CN_FROZEN_DAILY_PRICE_PATH_v1",forecast_week:WEEK};
 const dailyRanges={contract:"CN_FROZEN_DAILY_RANGE_PLAN_v1",forecast_week:WEEK};
 const windows=[["day_1_2",0,2],["day_3_4",2,4],["day_5_7",4,7]];
 const windowScores={};
 const rows=[];
 for(const [id,first,end] of windows){
   windowScores[id]={window_start_utc:UTC(START+first*DAY),window_end_utc:UTC(START+end*DAY),scoring_start_utc:"2026-11-09T08:00:00Z"};
   for(const [asset,a] of Object.entries(ASSETS)){
     rows.push({asset,window:id,forecast_low:Math.min(...a.low.slice(first,end)),forecast_high:Math.max(...a.high.slice(first,end))});
   }
 }
 for(const [asset,a] of Object.entries(ASSETS)){
   const points=a.close.map((expected_close,i)=>({day:i+1,expected_close,low:a.low[i],high:a.high[i]}));
   dailyPath[asset]={status:"PUBLISHED",points};
   dailyRanges[asset]={status:"PUBLISHED",points:points.map(p=>({
     day:p.day,low:p.low,high:p.high,why:"Fiktiv individuel dagsrange, alene til grafens visuelle accept.",
     invalidate_if:"Kun rigtige, originalt udstedte og kildevaliderede data må publiceres."
   }))};
 }
 return {dailyPath,dailyRanges,windowScores,rows};
}
const FROZEN=frozenSource();
const FULL_HOURLY=Object.fromEntries(Object.entries(ASSETS).map(([asset,a])=>{
 const rows=[];
 for(let h=1;h<=168;h++){
   const day=Math.floor((h-1)/24), progress=(h-day*24)/24;
   const core=a.observed[day]+(a.observed[day+1]-a.observed[day])*progress;
   const ripple=a.ripple*(.56*Math.sin(h*.53)+.24*Math.sin(h*.17)+.17*Math.cos(h*.91));
   rows.push({observed_at_utc:UTC(START+h*HOUR),close:Math.round((core+ripple)*100)/100});
 }
 return [asset,Object.freeze(rows)];
}));
export function buildWeek({hours=168,quote="USDT",missing=false}={}){
 if(!Number.isInteger(hours)||hours<1||hours>168)throw Error("QA_HOURS_MUST_BE_1_TO_168");
 const asOf=UTC(START+hours*HOUR);
 const now=UTC(START+hours*HOUR+60000);
 const hourly={
   contract:"CN_PUBLIC_HOURLY_PRICE_PATH_v1",source:"HOURLY_SPOT_PASS_ONLY",
   semantics:"OBSERVED_HOURLY_CLOSE_NOT_A_PROSPECTIVE_FORECAST",forecast_week:WEEK,
   public_issue_number:46,observed_through_utc:asOf
 };
 const observations={contract:"CN_PUBLIC_DAILY_OBSERVATIONS_v1",timezone:"UTC",observed_through_utc:asOf};
 for(const asset of ["BTC","ETH"]){
   const rows=FULL_HOURLY[asset].slice(0,hours);
   hourly[asset]=rows;
   observations[asset]=[];
   for(let d=0;d<7;d++){
     if(hours<(d+1)*24)continue;
     const daily=rows.slice(d*24,(d+1)*24);
     const prices=daily.map(p=>p.close);
     observations[asset].push({
       day:d+1,date:UTC(START+d*DAY).slice(0,10),
       as_of_utc:UTC(START+(d+1)*DAY),coverage_complete_to_date:true,status:"COMPLETE",
       observed_hours:24,low:Math.min(...prices),high:Math.max(...prices),close:prices.at(-1)
     });
   }
 }
 const path=missing?
  {contract:"CN_FROZEN_DAILY_PRICE_PATH_v1",forecast_week:WEEK,
    BTC:{status:"UNAVAILABLE",points:[]},ETH:{status:"UNAVAILABLE",points:[]}}
  :clone(FROZEN.dailyPath);
 const live={
   contract:"CN_PUBLIC_LIVE_PRICE_PRECISION_v1",public_issue_number:46,forecast_week:WEEK,
   frozen_at_utc:"2026-11-09T07:00:00Z",scoring_valid_from_utc:"2026-11-09T08:00:00Z",
   freshness_sla_minutes:90,live_as_of_utc:asOf,
   price_quote_labels:{
     contract:"CN_PUBLIC_PRICE_QUOTE_LABELS_v1",actual_native_spot:{BTC:"USDT",ETH:"USDT"},
     forecast_model_declared:{BTC:quote,ETH:quote},conversion_applied:false
   },
   window_scores:clone(FROZEN.windowScores),rows:clone(FROZEN.rows),
   daily_price_path:path,daily_range_plan:clone(FROZEN.dailyRanges),
   hourly_price_path:hourly,daily_observations:observations
 };
 return {test_only:true,week:WEEK,hours,nowUtc:now,observedThroughUtc:asOf,
   data:{public_series:{current_public_projection:{forecast_week:WEEK,public_issue_number:46}},public_live_precision:live}};
}
export function forecastFingerprint(){
 return JSON.stringify({week:WEEK,price_quote:"USDT",issued_at_utc:"2026-11-09T07:00:00Z",
  daily_price_path:FROZEN.dailyPath,daily_range_plan:FROZEN.dailyRanges});
}
export function expectedDaily(asset="BTC"){
 return clone(FROZEN.dailyPath[asset].points);
}
