const INHERITED='INHERITED_FROM_PRIOR_ISSUE';
const OFFLINE_METHOD='CN_OWNER_AUTHORIZED_API_FREE_SEVEN_DAY_v1';
const CONTRACT='CN_KOMPAS_TRUTH_BANNER_v1';
const positiveInt=n=>Number.isSafeInteger(n)&&n>0;

function inheritsProtection(pkg){
  const basis=pkg?.decision_projection?.protection?.state_basis;
  const method=pkg?.issuer_method;
  return basis?basis===INHERITED:
    method===OFFLINE_METHOD||(!method&&typeof pkg?.readable_markdown==='string'&&
      pkg.readable_markdown.split('\n').includes('Method: '+OFFLINE_METHOD));
}

function sameRisk(a,b){
  const left=a?.decision_projection?.protection,right=b?.decision_projection?.protection;
  return Boolean(left&&right&&['pullback_risk_state','pullback_class','distribution_risk'].every(key=>
    typeof left[key]==='string'&&left[key]===right[key]));
}

/** Resolve the reported original issue, or walk the older hash-bound carry chain. */
export async function inheritedProtectionOrigin(current,readIssue){
  if(!inheritsProtection(current))return null;
  let pkg=current;
  let origin=null;
  for(let count=0;count<12&&inheritsProtection(pkg);count++){
    const explicit=pkg.decision_projection?.protection?.inherited_from_issue_number;
    const prior=explicit??pkg.previous_issue_number;
    if(!positiveInt(prior)||!positiveInt(pkg.issue_number)||prior>=pkg.issue_number)return null;
    origin=await readIssue(prior);
    if(origin?.pkg?.issue_number!==prior||!sameRisk(pkg,origin.pkg)||
       !positiveInt(pkg.generated_unix)||!positiveInt(origin.pkg.generated_unix)||origin.pkg.generated_unix>=pkg.generated_unix)return null;
    pkg=origin.pkg;
  }
  if(!origin||inheritsProtection(pkg)||!positiveInt(origin.publicIssue))return null;
  const ms=pkg.generated_unix*1000;
  if(!Number.isFinite(new Date(ms).getTime()))return null;
  return {public_issue_number:origin.publicIssue,issued_date_utc:new Date(ms).toISOString().slice(0,10)};
}

/** Whitelist only public, observation-clock fields from verified source records. */
export function kompasTruthReadback(internal,projection,{origin=null,officialFreshness}={}){
  const source=projection?.original_source_age_at_issue;
  const age=source?.observation_age_seconds_at_issue;
  const issued=Date.parse(internal?.issued_at_utc);
  const linked=source?.status==='ORIGINAL_ISSUANCE_CLOCKS_ONLY'&&
    source?.contract==='CN_OFFICIAL_ORIGINAL_SOURCE_AGE_READBACK_v1'&&
    source?.observation_clock_status==='PASS'&&source?.packet_clock_status==='PASS'&&
    source?.compass_id===internal?.compass_id&&source?.issued_at_utc===internal?.issued_at_utc&&
    Number.isFinite(issued)&&Number.isSafeInteger(age)&&age>=0&&age<=30*86400;
  const expiry=Date.parse(officialFreshness?.valid_until_utc);
  const expiryVerified=officialFreshness?.status==='VERIFIED_OWNER_POLICY'&&
    officialFreshness?.contract==='OFFICIAL_COMPASS_SOURCE_FRESHNESS_READBACK_v1'&&expiry>=issued;
  const inherited=internal?.cn_protection_state_basis===INHERITED;
  return {contract:CONTRACT,compass_id:internal?.compass_id??null,issued_at_utc:internal?.issued_at_utc??null,
    data_status:internal?.data_status==='OK'?'OK':'DEGRADED',inherited,
    origin:inherited?origin:null,
    observation_at_utc:linked?new Date(issued-age*1000).toISOString():null,
    valid_until_utc:expiryVerified?new Date(expiry).toISOString():null};
}

/** Age increases from the original verified observation, including after a stale page load. */
export function kompasTruthBanner(compass,{nowMs=Date.now(),lang='da',weeklyAligned=false}={}){
  const en=lang==='en';
  const source=compass?.full_stack?.truth_banner;
  const issue=Date.parse(source?.issued_at_utc);
  const obs=Date.parse(source?.observation_at_utc);
  const expiry=Date.parse(source?.valid_until_utc);
  const valid=source?.contract===CONTRACT&&typeof compass?.compass_id==='string'&&
    compass.compass_id===source.compass_id&&compass.issued_at_utc===source.issued_at_utc&&issue<=nowMs;
  const known=valid&&obs<=issue;
  const state=valid&&source.data_status==='DEGRADED'?'DEGRADED':!known?'MISSING':
    !Number.isFinite(expiry)||expiry<issue?'MISSING':expiry<=nowMs?'STALE':'FRESH';
  const labels=en?
    {FRESH:'Current data',STALE:'Stale data',DEGRADED:'Incomplete source data',MISSING:'Source freshness unavailable'}:
    {FRESH:'Aktuelle data',STALE:'Forældede data',DEGRADED:'Ufuldstændige kildedata',MISSING:'Kildens friskhed er ukendt'};
  if(!valid||source.inherited!==true)return {state,text:labels[state]};
  const p=source.origin;
  if(!weeklyAligned||!positiveInt(p?.public_issue_number)||!/^\d{4}-\d{2}-\d{2}$/.test(p?.issued_date_utc))
    return {state,text:labels[state]};
  const date=p.issued_date_utc+' UTC';
  const risk=en?'Risk assessment carried forward from '+date+' (issue #'+p.public_issue_number+'), not refreshed.':
    'Risikovurdering nedarvet fra '+date+' (udgave #'+p.public_issue_number+'), ikke fornyet.';
  return {state,text:risk+' · '+labels[state]};
}

const HOUR_MS=3600000;
const DAY_MS=24*HOUR_MS;
const HOURLY_CONTRACT='CN_PUBLIC_FROZEN_FLOOR_HOURLY_OBSERVATION_v1';
const positivePrice=n=>typeof n==='number'&&Number.isFinite(n)&&n>0;

/** Both inputs come from hash-verified public files. Bind the quote and pre-existing owner clock. */
export function hourlyFloorReadback(auto,freeze,pointer,pkg){
 const year=pointer?.iso_year,week=pointer?.iso_week;
 if(!Number.isInteger(year)||year<2000||year>9999||!Number.isInteger(week)||week<1||week>53)return null;
 const jan4=new Date(Date.UTC(year,0,4));
 const firstMonday=jan4.getTime()-((jan4.getUTCDay()+6)%7)*DAY_MS;
 const weekStart=firstMonday+(week-1)*7*DAY_MS;
 const weekEnd=weekStart+7*DAY_MS;
 if(new Date(weekStart+3*DAY_MS).getUTCFullYear()!==year)return null;
 const weekId=year+'-W'+String(week).padStart(2,'0');
 const path=freeze?.daily_price_path;
 if(path?.contract!=='CN_FROZEN_DAILY_PRICE_PATH_v1'||path.forecast_week!==weekId)return null;
 const live=auto?.normalized_state?.live_market;
 const health=auto?.source_health?.hourly_market;
 const clock=health?.freshness?.source_observation_freshness;
 const open=Date.parse(live?.observation_open_utc);
 const close=open+HOUR_MS;
 const delivered=Date.parse(auto?.packet_generated_at_utc);
 const issued=pkg?.generated_unix*1000;
 if(health?.status!=='PASS'||health.classification!=='GITHUB_POINTER_TARGET_CHAIN_VALID'||
    health.freshness?.status!=='PASS'||clock?.status!=='PASS'||
    !positivePrice(clock.max_age_seconds)||Date.parse(clock.timestamp)!==close||
    live?.observation_semantics!=='COMPLETED_1H_CANDLE_CLOSE_VALUE_ON_CANDLE_OPEN_LABEL'||
    !Number.isFinite(open)||open%HOUR_MS!==0||!Number.isFinite(issued)||open<issued||
    open<weekStart||close>=weekEnd||!Number.isFinite(delivered)||close>delivered||
    delivered-close>clock.max_age_seconds*1000)return null;
 const assets=[];
 for(const asset of ['BTC','ETH']){
  const key=asset.toLowerCase();
  const daily=path[asset]?.points;
  const price=live[key+'_usdt'],floor=freeze[key+'_range_low'];
  if(freeze.price_quote?.[asset]!=='USDT'||!positivePrice(price)||!positivePrice(floor)||
     !Array.isArray(daily)||daily.length!==7||!daily.every(p=>
       Number.isInteger(p?.day)&&p.day>=1&&p.day<=7&&positivePrice(p.low))||
     new Set(daily.map(p=>p.day)).size!==7)continue;
  assets.push({asset,price,weekly_floor:floor});
 }
 if(!assets.length)return null;
 return {contract:HOURLY_CONTRACT,forecast_week:weekId,quote:'USDT',
  closed_at_utc:new Date(close).toISOString(), available_at_utc:new Date(delivered).toISOString(),
  valid_until_utc:new Date(Math.min(weekEnd,close+clock.max_age_seconds*1000)).toISOString(),assets};
}

export function hourlyFloorBanner(compass,{forecastWeek,nowMs=Date.now(),lang='da'}={}){
 const row=compass?.full_stack?.hourly_floor_observation;
 const close=Date.parse(row?.closed_at_utc),delivered=Date.parse(row?.available_at_utc);
 const expiry=Date.parse(row?.valid_until_utc);
 const latestHourly=compass?.public_data_health;
 const knownNewer=latestHourly?.hourly_status==='COMPLETE'&&
   Date.parse(latestHourly.latest_complete_market_hour_utc)>close;
 if(row?.contract!==HOURLY_CONTRACT||row.forecast_week!==forecastWeek||row.quote!=='USDT'||
    knownNewer||!Number.isFinite(close)||!(close<=delivered&&delivered<=nowMs&&nowMs<expiry)||
    !Array.isArray(row.assets))return {age:'',lines:[]};
 const en=lang==='en';
 const age=Math.floor((nowMs-close)/60000);
 const number=new Intl.NumberFormat(en?'en-GB':'da-DK',{minimumFractionDigits:2,maximumFractionDigits:2});
 const utc=new Date(close).toISOString().slice(11,16)+' UTC';
 const lines=row.assets.filter(x=>['BTC','ETH'].includes(x?.asset)&&positivePrice(x?.price)&&
  positivePrice(x?.weekly_floor)&&x.price<x.weekly_floor).map(({asset,price,weekly_floor})=>
  en?asset+': Last hourly close '+number.format(price)+' USDT ('+utc+') is below the frozen weekly floor '+number.format(weekly_floor)+' USDT · observation only':
    asset+': Seneste timelukkekurs '+number.format(price)+' USDT ('+utc+') ligger under prognosens ugebund '+number.format(weekly_floor)+' USDT · beskrivende observation');
 return {age:en?'Data '+age+' min old.':'Data '+age+' min gammel.',lines};
}
