/* Read-only source transparency for staged vNext Compass.
 * The site MAY SHOW owner-issued typed statuses. It MUST NOT derive a new
 * market decision, override Official Compass or turn research into authority.
 * This module never fetches, writes or evaluates prices. */
const SOURCE_CONTRACT='PUBLIC_COMPASS_FULL_STACK_READBACK_v1';
const STATES=Object.freeze([
  ['official','Official Compass'],['auto_market_state','Auto Market State'],
  ['native','Native Handlekompas'],['shadow','Shadow research'],
  ['strategic','Strategic Compass'],['master_monday','Master Monday'],
  ['cycle_navigator','Cycle Navigator']
]);
const ACCEPTED=Object.freeze({
 official:['VERIFIED','DEGRADED'],
 auto_market_state:['HASH_VERIFIED','UNVERIFIED'],
 native:['SOURCE_ALIGNED','VERIFIED_NEWER_OR_DIFFERENT_SOURCE','UNVERIFIED'],
 shadow:['ALIGNED_RESEARCH','STALE_RESEARCH','UNVERIFIED'],
 strategic:['BOUND_WEEKLY_ANCHOR','UNVERIFIED'],
 master_monday:['SOURCE_ALIGNED','UNVERIFIED'],
 cycle_navigator:['WEEKLY_POINTER_ALIGNED','UNVERIFIED']
});
const clean=(id,v)=>ACCEPTED[id]?.includes(v)?v:'UNAVAILABLE';
const validDirection=v=>typeof v==='string'&&/^[A-Z][A-Z_]{1,39}$/.test(v)&&v!=='UNAVAILABLE'?v:'UNAVAILABLE';
const closed=(reason='SOURCE_UNVERIFIED')=>({
  contract:'CN_PREMIUM_SOURCE_TRACE_v1',status:'UNVERIFIED',reason,
  decision_authority:'OFFICIAL_COMPASS_ONLY',official_current:false,
  long_horizons:[
    {id:'2_3w',direction:'UNAVAILABLE',owner:'CYCLE_NAVIGATOR_WEEKLY'},
    {id:'21_30d',direction:'UNAVAILABLE',owner:'STRATEGIC_RESEARCH'},
    {id:'4_8w',direction:'UNAVAILABLE',owner:'CYCLE_NAVIGATOR_STRATEGIC_CONTEXT'}
  ],
  sources:STATES.map(([id,name])=>({id,name,status:'UNAVAILABLE'}))
});
/** Source eligibility is a property of a verified exact PUBLIC pair and its
 * evaluation time. Never treat the old last verified snapshot as current. */
export function sourceTrace(latest,compass,parsed){
  const result=closed();
  const f=compass?.full_stack;
  const cp=latest?.public_series?.current_public_projection;
  const wc=compass?.weekly_context;
  const eligible=latest?.schema==='CN_PUBLIC_SNAPSHOT_V2'&&
    compass?.contract==='PUBLIC_COMPASS_PROJECTION_v1'&&
    f?.contract===SOURCE_CONTRACT&&
    ['COMPLETE','PARTIAL_OR_DEGRADED'].includes(f.status)&&
    parsed?.delivery_health==='FRESH'&&
    ['OK','DEGRADED'].includes(parsed?.weekly?.state)&&
    parsed?.weekly?.forecast_week===cp?.forecast_week&&
    parsed?.weekly?.public_issue_number===cp?.public_issue_number&&
    wc?.forecast_week===cp?.forecast_week&&
    wc?.public_issue_number===cp?.public_issue_number&&
    f.source_status?.official==='VERIFIED';
  if(!eligible)return result;
  const currentOfficial=parsed?.compass?.state==='FRESH'&&
    parsed?.compass?.permit_path_live_gates===true&&
    f.source_status?.official==='VERIFIED';
  // A producer-declared COMPLETE must not coexist with source-owner denial,
  // stale research or incomplete Monday analytics. Reject contradiction,
  // rather than laundering a green site badge through a public object.
  if(f.status==='COMPLETE'&&!(
    f.source_status.official==='VERIFIED'&&
    f.source_status.native==='SOURCE_ALIGNED'&&
    f.source_status.shadow==='ALIGNED_RESEARCH'&&
    f.source_status.strategic==='BOUND_WEEKLY_ANCHOR'&&
    f.source_status.master_monday==='SOURCE_ALIGNED'&&
    f.source_status.master_monday_analysis==='COMPLETE'&&
    f.source_status.cycle_navigator==='WEEKLY_POINTER_ALIGNED'
  ))return closed('CONTRADICTORY_COMPLETE_STATUS');
  // Official authority expires independently of previously verified weekly
  // evidence. Keep only typed, source-aligned NONBINDING research context.
  // Never rebrand the expired Official action as CURRENT.
  result.official_current=currentOfficial;
  result.status=currentOfficial?f.status:'PARTIAL_OR_DEGRADED';
  result.reason=!currentOfficial?'OFFICIAL_NOT_CURRENT_CONTEXT_ONLY':
    f.status==='COMPLETE'?'VERIFIED_ALL_REQUIRED_LAYERS':'SOME_LAYERS_MISSING_OR_DEGRADED';
  result.sources=STATES.map(([id,name])=>({
    id,name,status:id==='official'&&!currentOfficial?'UNAVAILABLE':clean(id,f.source_status?.[id])
  }));
  if(f.source_status?.cycle_navigator==='WEEKLY_POINTER_ALIGNED'&&
     Number.isInteger(f.weekly?.iso_week)&&Number.isInteger(f.weekly?.iso_year)&&
     f.weekly.iso_week===latest.pointer?.iso_week&&f.weekly.iso_year===latest.pointer?.iso_year){
    result.long_horizons[0].direction=validDirection(f.weekly.direction_2_3w);
  }
  if(f.source_status?.strategic==='BOUND_WEEKLY_ANCHOR'&&
     f.strategic?.status==='BOUND_WEEKLY_ANCHOR'&&
     f.strategic?.authority==='CYCLE_NAVIGATOR_OWNED_NOT_NEW_SITE_FORECAST'){
    result.long_horizons[1].direction=validDirection(f.strategic.horizon_21_30d?.direction);
    result.long_horizons[2].direction=validDirection(f.strategic.horizon_4_8w?.direction);
  }
  return result;
}
