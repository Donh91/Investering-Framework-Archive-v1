/**
 * Display-only original Official Compass source-age readback.
 * Original issuer's source observation age is distinct from the age of a newly
 * assembled Auto Market State wrapper, both measured AT FORECAST ISSUANCE.
 * This is NOT the current candle's live age, provider first-known timestamp,
 * investor delivery confirmation, scientific PIT gate, or a trading threshold.
 */
const validAge=n=>Number.isSafeInteger(n)&&n>=0&&n<=30*86400;
const safeIso=s=>typeof s==='string'&&/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(s)&&
  Number.isFinite(Date.parse(s))&&new Date(Date.parse(s)).toISOString()===s.replace('Z','.000Z');

function lane(freshness,name){
  const matches=Array.isArray(freshness?.checks)?freshness.checks.filter(c=>c?.lane===name):[];
  return Array.isArray(matches)&&matches.length===1&&validAge(matches[0]?.age_seconds)?
    matches[0]:null;
}

/** From a hash-verified immutable INTERNAL Official record, NOT a loose feed. */
export function originalSourceAgeAtIssue(internal,projection){
  const base={
    contract:'CN_OFFICIAL_ORIGINAL_SOURCE_AGE_READBACK_v1',
    status:'UNKNOWN',observation_age_seconds_at_issue:null,
    packet_age_seconds_at_issue:null,issued_at_utc:null,compass_id:null,
    observation_clock_status:'UNKNOWN',packet_clock_status:'UNKNOWN',
    provider_first_published_at_utc:null,first_investor_delivery_at_utc:null,
    authority:'PRESENTATION_ONLY_NO_GATE_OR_SIGNAL'
  };
  // Only the actually issued v1 original contract has verified clock semantics.
  // Do not accept hypothetical future revisions by a version-number regex.
  if(internal?.contract!=='OFFICIAL_DAILY_COMPASS_v1')return base;
  if(!projection||typeof internal.compass_id!=='string'||!internal.compass_id||
     internal.compass_id!==projection.compass_id||!safeIso(internal.issued_at_utc)||
     internal.issued_at_utc!==projection.issued_at_utc)return base;
  const freshness=internal.source_bindings?.auto_market_state?.freshness;
  // The recorded ages must be independently consistent with their ORIGINAL
  // observation timestamps and the issuer's evaluation clock. A hash verifies
  // file identity, not the semantic truth of contradictory clock fields.
  if(!safeIso(freshness?.evaluated_at_utc)||
     freshness.evaluated_at_utc!==internal.issued_at_utc)return base;
  const obs=lane(freshness,'source_observation_freshness');
  const packet=lane(freshness,'auto_market_state_packet');
  const issuedMs=Date.parse(internal.issued_at_utc);
  const clockMatches=check=>safeIso(check?.timestamp)&&
    Date.parse(check.timestamp)<=issuedMs&&
    (issuedMs-Date.parse(check.timestamp))/1000===check.age_seconds;
  if(!obs||!packet||!clockMatches(obs)||!clockMatches(packet))return base;
  if(obs.age_seconds<packet.age_seconds)return base; // newer source than its wrapper would be contradictory
  return {...base,status:'ORIGINAL_ISSUANCE_CLOCKS_ONLY',
    observation_age_seconds_at_issue:obs.age_seconds,
    packet_age_seconds_at_issue:packet.age_seconds,
    issued_at_utc:internal.issued_at_utc,compass_id:internal.compass_id,
    observation_clock_status:typeof obs.status==='string'?obs.status:'UNKNOWN',
    packet_clock_status:typeof packet.status==='string'?packet.status:'UNKNOWN'};
}

/** Safe UI copy, only for the current hash-bound public Official projection. */
export function originalSourceAgeLabel(compass,{lang='da',valid=false}={}){
  const x=compass?.original_source_age_at_issue,da=lang!=='en';
  if(!valid)return '';
  if(x?.contract!=='CN_OFFICIAL_ORIGINAL_SOURCE_AGE_READBACK_v1'||
     x?.status!=='ORIGINAL_ISSUANCE_CLOCKS_ONLY'||
     x?.issued_at_utc!==compass?.issued_at_utc||
     typeof x?.compass_id!=='string'||!x.compass_id||
     x.compass_id!==compass?.compass_id||
     !validAge(x?.observation_age_seconds_at_issue)||
     !validAge(x?.packet_age_seconds_at_issue)||
     x?.observation_age_seconds_at_issue<x?.packet_age_seconds_at_issue)return da?
       ' · Kildealder ved udstedelse: ukendt':' · Source age at issuance: unknown';
  const minutes=n=>n<60?'<1':String(Math.ceil(n/60));
  return da?
    ' · Ved udstedelse: markedsdata '+minutes(x.observation_age_seconds_at_issue)+
    ' min, kildepakke '+minutes(x.packet_age_seconds_at_issue)+' min':
    ' · At issuance: market data '+minutes(x.observation_age_seconds_at_issue)+
    ' min, source packet '+minutes(x.packet_age_seconds_at_issue)+' min';
}
