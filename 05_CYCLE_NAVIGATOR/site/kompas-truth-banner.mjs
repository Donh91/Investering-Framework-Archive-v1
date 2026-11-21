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
  const mins=known?Math.floor((nowMs-obs)/60000):null;
  const timing=mins===null?'':(en?' · Data age ':' · Dataalder ')+mins+' min';
  if(!valid||source.inherited!==true)return {state,text:labels[state]+timing};
  const p=source.origin;
  const origin=weeklyAligned&&positiveInt(p?.public_issue_number)&&/^\d{4}-\d{2}-\d{2}$/.test(p?.issued_date_utc)?
    (en?'issue #':'udgave #')+p.public_issue_number+' ('+p.issued_date_utc+' UTC)':
    (en?'a prior issue (origin unverified)':'en tidligere udgave (ophav ukendt)');
  const risk=en?'Risk assessment carried forward from '+origin:'Risikovurdering nedarvet fra '+origin;
  return {state,text:risk+' · '+labels[state]+timing};
}
