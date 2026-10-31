/**
 * Publish a MINIMAL research-only Pullback Radar accountability receipt to Pages.
 * No market classifier, live warning, implied probability or trading authority.
 * Runs after existing build-public.mjs. Does not touch the existing Compass API.
 */
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {resolve, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';

export const CONTRACT='CN_PUBLIC_PULLBACK_RESEARCH_READBACK_v1';
const SOURCE='KOMPAS_ROLLING_14D_HISTORICAL_ACCOUNTABILITY_v1';
const RESEARCH='PULLBACK_RADAR_TIMEBOX_SHADOW_v1';
const REPORT_BASE='04_MARKET_LEARNING/handlekompas/research/rolling_14d/daily';
const HORIZONS=['12h','24h','72h'];
const HASH=/^[a-f0-9]{64}$/;

function localDay(timestamp){
 const parts=Object.fromEntries(new Intl.DateTimeFormat('en-GB',{
  timeZone:'Europe/Copenhagen',year:'numeric',month:'2-digit',day:'2-digit'
 }).formatToParts(timestamp).filter(p=>p.type!=='literal').map(p=>[p.type,p.value]));
 return parts.year+'-'+parts.month+'-'+parts.day;
}
function sourceRel(day){
 if(!/^\d{4}-\d{2}-\d{2}$/.test(day))throw new Error('INVALID_DATE');
 const [y,m,d]=day.split('-');
 return REPORT_BASE+'/'+y+'/'+m+'/'+d+'/'+day+'_ROLLING14.json';
}
function counter(x){return Number.isSafeInteger(x)&&x>=0;}
function unavailable(reason,now){
 return {contract:CONTRACT,status:'UNAVAILABLE',reason,asof_utc:now.toISOString(),
  source_date:null,source_sha256:null,source_report_generated_at_utc:null,
  all_issuances:null,source_state_counts:null,new_warning_events:null,horizons:null,
  scientific_edge_status:'NOT_PROVEN',first_known_publication_verified:false,
  risk_state_is_not_new_warning:true,authority:{
    research_only:true,live_warning:false,portfolio_execution:false,automatic_promotion:false}};
}
export function projectPullbackReport(bytes,{now=new Date(),expectedDay}={}){
 const empty=reason=>unavailable(reason,now);
 if(!(bytes instanceof Uint8Array)||bytes.length===0||bytes.length>8_000_000)
  return empty('REPORT_BYTES_MISSING_OR_OVERSIZE');
 let r;
 try{r=JSON.parse(Buffer.from(bytes).toString('utf8'));}catch{return empty('INVALID_REPORT_JSON');}
 if(!r||r.contract!==SOURCE||r.scope!=='rolling14'||r.research_only!==true||
    r.automatic_model_reweighting!==false||r.trade_permission!=='NONE'||
    r.first_known_publication_verified!==false||r.frozen_forecasts_unchanged!==true||
    !r.pullback_warning_timebox_shadow||
    r.pullback_warning_timebox_shadow.contract!==RESEARCH)
  return empty('UNQUALIFIED_RESEARCH_SOURCE');
 const x=r.pullback_warning_timebox_shadow,issued=Date.parse(r.generated_at_utc);
 const age=now.valueOf()-issued;
 if(!Number.isFinite(issued)||age < -120000||age>36*3600*1000||
    r.copenhagen_date!==expectedDay||localDay(new Date(issued))!==expectedDay)
  return empty('STALE_OR_CONTRADICTORY_REPORT_CLOCK');
 const total=r.all_issuances?.forecasts;
 const n=x.new_warning_or_escalation_events;
 if(!counter(total)||!counter(n)||n>total||
    x.first_known_publication_verified!==false||
    x.prospective_holdout_completed!==false||
    x.automatic_model_reweighting!==false||x.trade_permission!=='NONE'||
    x.repeated_elevated_count_is_not_warning_success!==true||
    x.expired_alert_cannot_be_credited_from_later_drop!==true||
    x.false_negative_recall_unknown_without_matched_no_alert_grid!==true||
    x.economically_executable_edge!==null||x.calibrated_probability!==null)
  return empty('INVALID_SHADOW_AUTHORITY_OR_DENOMINATOR');
 const out={};
 for(const h of HORIZONS){
  const v=x.horizons?.[h];
  if(!v||!['matured_n','hit_n','false_alarm_n','pending_n','unknown_n','new_warning_or_escalation_n'].every(k=>counter(v[k]))||
    v.new_warning_or_escalation_n!==n||
    v.matured_n!==v.hit_n+v.false_alarm_n||
    v.matured_n+v.pending_n+v.unknown_n!==n||
    v.warning_skill_or_edge!==null)
    return empty('INVALID_HORIZON_COUNTS');
  out[h]={events:n,matured:v.matured_n,hits:v.hit_n,
   false_alarms:v.false_alarm_n,pending:v.pending_n,unknown:v.unknown_n,
   hit_rate_descriptive:null}; // No raw hit rate without prospective PIT proof.
 }
 const counts=x.warning_state_counts||{};
 if(Object.keys(counts).length>16||!Object.values(counts).every(counter)||
    Object.values(counts).reduce((a,b)=>a+b,0)!==total)
  return empty('INVALID_STATE_COUNTS');
 const accepted=['REPEAT_STATE_NOT_NEW_WARNING','RETRIGGER_WITHIN_OPEN_WINDOW_NOT_SCORED',
  'EXPIRED_NO_FRESH_WARNING','LEFT_CENSORED_NO_TRANSITION_PROOF',
  'SOURCE_UNAVAILABLE_OR_UNQUALIFIED','INVALID_REFERENCE_CLOCK_OR_PRICE',
  'NEW_WARNING','ESCALATION','NO_WARNING'];
 if(Object.keys(counts).some(k=>!accepted.includes(k)))return empty('UNEXPECTED_INTERNAL_STATE');
 const sha=createHash('sha256').update(bytes).digest('hex');
 if(!HASH.test(sha))return empty('INVALID_SOURCE_HASH');
 return {contract:CONTRACT,status:'RESEARCH_ONLY',reason:null,
  asof_utc:now.toISOString(),source_date:expectedDay,source_sha256:sha,
  source_report_generated_at_utc:r.generated_at_utc,
  all_issuances:total,
  source_state_counts:{
   repeated:(counts.REPEAT_STATE_NOT_NEW_WARNING||0)+(counts.RETRIGGER_WITHIN_OPEN_WINDOW_NOT_SCORED||0),
   initial_censored:counts.LEFT_CENSORED_NO_TRANSITION_PROOF||0,
   unavailable:(counts.SOURCE_UNAVAILABLE_OR_UNQUALIFIED||0)+(counts.INVALID_REFERENCE_CLOCK_OR_PRICE||0)
  },
  new_warning_events:n,horizons:out,scientific_edge_status:'NOT_PROVEN',
  first_known_publication_verified:false,risk_state_is_not_new_warning:true,
  authority:{research_only:true,live_warning:false,portfolio_execution:false,
   automatic_promotion:false}};
}
export async function buildPublicPullback({repoRoot,output,now=new Date()}){
 let found=null,day=null,bytes=null;
 for(let daysAgo=0;daysAgo<=2;daysAgo++){
  const d=localDay(new Date(now.valueOf()-daysAgo*86400000));
  try{bytes=await readFile(resolve(repoRoot,sourceRel(d)));day=d;found=true;break;}
  catch(err){if(err.code!=='ENOENT')throw err;}
 }
 const result=found?projectPullbackReport(bytes,{now,expectedDay:day}):
   unavailable('AWAITING_FIRST_QUALIFIED_RESEARCH_REPORT',now);
 await mkdir(dirname(output),{recursive:true});
 await writeFile(output,JSON.stringify(result,null,2)+'\n');
 return result;
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const site=dirname(fileURLToPath(import.meta.url));
 const repoRoot=resolve(site,'../..');
 const output=resolve(site,'dist/data/pullback-research.json');
 const result=await buildPublicPullback({repoRoot,output});
 console.log(JSON.stringify({contract:result.contract,status:result.status,
  reason:result.reason,date:result.source_date,events:result.new_warning_events,
  source_sha256:result.source_sha256,trade_permission:'NONE'}));
}
