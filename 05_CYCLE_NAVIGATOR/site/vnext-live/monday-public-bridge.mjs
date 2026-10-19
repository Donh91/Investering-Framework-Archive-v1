/* vNext Monday context: presentation-only consumer of existing verified
 * SITE public full-stack output. NEVER computes an action or accesses private
 * machine packages. This output is WEEKLY HISTORICAL context, not live NOW. */
const CONTRACT='PUBLIC_MASTER_MONDAY_WEEKLY_CONTEXT_READBACK_v1';
const AUTHORITY='WEEKLY_CONTEXT_ONLY_NO_CURRENT_ACTION';
const ANALYTICS=new Set(['COMPLETE','PARTIAL_ANALYTICS','CONFLICTING_ANALYTICS']);
const PRIORITY=Object.freeze({
  COMPLETE:'COMPLETE',PARTIAL_ANALYTICS:'PARTIAL_ANALYTICS',
  CONFLICTING_ANALYTICS:'CONFLICTING_ANALYTICS',UNVERIFIED:'UNVERIFIED'
});
const fallback=()=>({
  contract:'CN_PREMIUM_MONDAY_PRESENTATION_v1',source_state:'UNVERIFIED',
  completed_week:null,analytics_status:'UNVERIFIED',
  api_analysis_status:'UNAVAILABLE',scorecard_status:'UNAVAILABLE',
  operational_translation_status:'UNAVAILABLE',current_action_authority:false
});
const cleanState=v=>typeof v==='string'&&/^[A-Z_]{2,65}$/.test(v)?v:'UNAVAILABLE';
const weekInfo=x=>{
  if(typeof x!=='string')return null;
  const m=/^(20\d{2})-W(0[1-9]|[1-4]\d|5[0-3])$/.exec(x);
  return m?{year:Number(m[1]),week:Number(m[2])}:null;
};
/** Verified public readback only. Prefer FAIL CLOSED to guessing a week or
 * promoting a successful API transport into substantive analysis. */
export function mondayContext(latest,compass,parsed){
  const result=fallback();
  if(latest?.schema!=='CN_PUBLIC_SNAPSHOT_V2'||
     compass?.contract!=='PUBLIC_COMPASS_PROJECTION_v1'||
     compass.full_stack?.contract!=='PUBLIC_COMPASS_FULL_STACK_READBACK_v1')return result;
  const mon=compass.full_stack.master_monday;
  const source=compass.full_stack.source_status;
  const completed=weekInfo(mon?.completed_week);
  const currentWeek=latest?.public_series?.current_public_projection?.forecast_week;
  const current=weekInfo(currentWeek);
  const completedNumber=latest?.pointer?.completed_source_week;
  const iso=latest?.pointer?.iso_year;
  const matching=Boolean(
    completed&&current&&Number.isInteger(completedNumber)&&
    completed.week===completedNumber&&Number.isInteger(iso)&&
    completed.year<=iso&&completed.year>=iso-1&&
    mon.completed_week!==currentWeek
  );
  const allowedAnalytics=ANALYTICS.has(mon?.analytics_status);
  const crossStatus=source?.master_monday_analysis===mon?.analytics_status;
  const weeklySafe=['OK','DEGRADED'].includes(parsed?.weekly?.state)&&
    parsed?.weekly?.forecast_week===currentWeek&&
    parsed?.weekly?.public_issue_number===latest?.public_series?.current_public_projection?.public_issue_number;
  const verified=Boolean(
    weeklySafe&&parsed?.delivery_health==='FRESH'&&matching&&
    mon?.contract===CONTRACT&&mon?.authority===AUTHORITY&&
    mon?.status==='SOURCE_ALIGNED'&&source?.master_monday==='SOURCE_ALIGNED'&&
    allowedAnalytics&&crossStatus
  );
  if(!verified)return result;
  result.source_state='SOURCE_ALIGNED';
  result.completed_week=mon.completed_week;
  result.analytics_status=PRIORITY[mon.analytics_status];
  result.api_analysis_status=mon.api_analysis_status==='AVAILABLE_SHADOW_ONLY'?'AVAILABLE_SHADOW_ONLY':'UNAVAILABLE';
  result.scorecard_status=cleanState(mon.scorecard_status);
  result.operational_translation_status=cleanState(mon.operational_translation_status);
  return result;
}
export function mondayLabels(v,lang='da'){
  const da=lang!=='en',al=v?.analytics_status;
  if(v?.source_state!=='SOURCE_ALIGNED')return {
    title:da?'Ikke kildeverificeret':'Source not verified',
    evidence:da?'Mandagsgrundlaget kan ikke bekræftes fra den aktuelle offentlige udgivelse.':'Monday context cannot be confirmed from the current public publication.',
    severity:'neutral'
  };
  const title=al==='COMPLETE'
    ?(da?'Analysegrundlag komplet':'Analytical context complete')
    :al==='CONFLICTING_ANALYTICS'
      ?(da?'Modstridende analysegrundlag':'Conflicting analytical context')
      :(da?'Analysegrundlag delvist':'Analytical context partial');
  const evidence=al==='COMPLETE'
    ?(da?'Verificeret ugegrundlag. Dette er ikke en aktuel køb/sælg-handling.':'Verified completed-week context. Not a current buy/sell action.')
    :al==='CONFLICTING_ANALYTICS'
      ?(da?'Kildernes analyse-status er modstridende. Ingen samlet analysebekræftelse.':'Conflicting analytical source status. No complete analysis confirmation.')
      :(da?'Leveringen er verificeret, men dele af analysen mangler eller er uafklarede.':'Delivery is verified, but parts of the analysis are missing or unresolved.');
  return {title,evidence,severity:al==='COMPLETE'?'normal':al==='CONFLICTING_ANALYTICS'?'warning':'neutral'};
}
