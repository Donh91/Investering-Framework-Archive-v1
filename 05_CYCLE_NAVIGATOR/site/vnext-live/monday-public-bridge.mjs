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
  const sourceYear=latest?.pointer?.completed_source_year;
  const iso=latest?.pointer?.iso_year;
  const isoWeek=latest?.pointer?.iso_week;
  // Never accept a year-old "W42" just because its week number matches.
  // completed_source_year is preserved from the SAME verified weekly pointer
  // used by the SITE producer. There is no local calendar inference.
  const matching=Boolean(
    completed&&current&&Number.isInteger(completedNumber)&&
    Number.isInteger(sourceYear)&&Number.isInteger(iso)&&Number.isInteger(isoWeek)&&
    current.year===iso&&current.week===isoWeek&&
    completed.week===completedNumber&&completed.year===sourceYear&&
    ((current.week>1&&sourceYear===current.year&&completed.week===current.week-1)||
      (current.week===1&&sourceYear===current.year-1&&[52,53].includes(completed.week)))
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
  result.c5_context=projectC5Context(mon.c5_context);
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

// Strict derived-only projection. No source rows, hashes, paths or arbitrary source text.
const C5_AUTH='CONTEXT_ONLY_NOT_DECISION_OR_SCORING';
const C5_REASONS=new Set(['C5_PREREG_NOT_FROZEN','C5_CONTEXT_UNVERIFIED','C5_ADAPTER_UNAVAILABLE','C5_NOT_ISSUED','FRED_NOT_SCHEDULED','FRED_CAPTURE_FAILED','FRED_RECEIPT_MISSING_OR_AMBIGUOUS','FRED_RECEIPT_SCOPE_INVALID','FRED_RECEIPT_HASH_MISMATCH','FRED_ARTIFACT_UNVERIFIED','FRED_SOURCE_BINDING_INVALID','FRED_SOURCE_IDENTITY_INVALID','FRED_CAPTURE_UNVERIFIED','FRED_C5_CAPTURE_NOT_AVAILABLE','FRED_CONTEXT_INTEGRITY_INVALID','FRED_CONTEXT_BINDING_INVALID','FRED_CAPTURE_STALE','FRED_CONTEXT_UNVERIFIED','FRED_MATCHED_SESSION_GAP','FRED_INPUT_INVALID','FRED_CAPTURE_CLOCK_INVALID_OR_STALE','OKX_CAPTURE_CLOCK_INVALID_OR_STALE','OKX_LATEST_RUN_BINDING_INVALID','OKX_LATEST_ASSET_CAPTURE_FAILED','OKX_CAPTURE_COVERAGE_GAP','OKX_CAPTURE_UNVERIFIED','OKX_BASELINE_INCOMPLETE_OR_ZERO']);
const c5reason=v=>C5_REASONS.has(v)?v:'C5_CONTEXT_UNVERIFIED';
const clock=v=>typeof v==='string'&&/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|\+00:00)$/.test(v)&&Number.isFinite(Date.parse(v))?v:null;
export function projectC5Context(v){
 const out={contract:'C5_MM_CONTEXT_v1',authority:C5_AUTH,scoring_allowed:false,status:'UNAVAILABLE',reason:'C5_NOT_ISSUED'};
 if(!v)return out;
 if(v.contract!==out.contract||v.authority!==C5_AUTH||v.scoring_allowed!==false||!clock(v.as_of_utc))return {...out,reason:'C5_CONTEXT_UNVERIFIED'};
 out.as_of_utc=clock(v.as_of_utc);out.reason=c5reason(v.reason);
 const m=v.macro,d=v.realized_liquidations;
 const macroGood=m?.status==='AVAILABLE'&&['INVERTED','FLAT','CONTANGO'].includes(m.term_structure_class)&&clock(m.as_of_utc)&&Date.parse(m.as_of_utc)<=Date.parse(out.as_of_utc);
 out.macro=macroGood?{status:'AVAILABLE',term_structure_class:m.term_structure_class,as_of_utc:clock(m.as_of_utc)}:{status:'UNAVAILABLE',reason:c5reason(m?.reason||v.reason)};
 out.realized_liquidations={status:'UNAVAILABLE',reason:c5reason(d?.reason||v.reason),assets:{}};
 let any=false;
 if(d?.status==='AVAILABLE_LOWER_BOUND'&&clock(d.as_of_utc)&&Date.parse(d.as_of_utc)<=Date.parse(out.as_of_utc)){
  for(const asset of ['BTC','ETH']){const row=d.assets?.[asset];out.realized_liquidations.assets[asset]={};
   for(const win of ['24h','7d']){const x=row?.[win];const valid=x?.status==='AVAILABLE_LOWER_BOUND'&&['HIGH','LOW','NORMAL','UNAVAILABLE'].includes(x.pressure_class)&&[x.long_notional_usd,x.short_notional_usd].every(n=>Number.isFinite(n)&&n>=0);
    out.realized_liquidations.assets[asset][win]=valid?{status:'AVAILABLE_LOWER_BOUND',pressure_class:x.pressure_class,long_notional_usd:x.long_notional_usd,short_notional_usd:x.short_notional_usd,pressure_reason:c5reason(x.pressure_reason)}:{status:'UNAVAILABLE',reason:c5reason(x?.reason||row?.reason)};any ||= valid;
   }}
  if(any){out.realized_liquidations.status='AVAILABLE_LOWER_BOUND';out.realized_liquidations.as_of_utc=clock(d.as_of_utc);}
 }
 out.status=macroGood&&any?'AVAILABLE':macroGood||any?'PARTIAL':'UNAVAILABLE';
 return out;
}
export function c5ContextLabel(v,lang='da'){
 const da=lang!=='en',x=projectC5Context(v),parts=[];
 const m=x.macro,d=x.realized_liquidations;
 if(m?.status==='AVAILABLE')parts.push('VIX: '+m.term_structure_class+' · '+m.as_of_utc);
 else parts.push('VIX: UNAVAILABLE ('+(m?.reason||x.reason)+')');
 for(const a of ['BTC','ETH'])for(const w of ['24h','7d']){const r=d?.assets?.[a]?.[w];parts.push(a+' '+w+': '+(r?.status==='AVAILABLE_LOWER_BOUND'?r.pressure_class+' · '+(da?'observeret minimum':'observed lower bound')+(r.pressure_class==='UNAVAILABLE'?' ('+r.pressure_reason+')':''):'UNAVAILABLE ('+(r?.reason||d?.reason||x.reason)+')'));}
 if(d?.as_of_utc)parts.push('OKX: '+d.as_of_utc);
 return parts.join(' | ');
}
export function renderC5Context(doc, value, lang='da'){
 const anchor=doc.getElementById('monday-translation');if(!anchor)return;
 let row=doc.getElementById('monday-c5-context');
 if(!row){row=doc.createElement('p');row.id='monday-c5-context';row.className='small';const parent=anchor.closest('section')||anchor.parentElement;parent.appendChild(row);}
 row.textContent=(lang==='en'?'Macro and derivatives context (non-scoring)':'Makro- og derivatkontekst (ikke-scorende)')+': '+c5ContextLabel(value,lang);
}
