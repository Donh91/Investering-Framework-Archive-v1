/**
 * Cycle Navigator vNext PATH · SOURCE-ONLY presentation.
 * Source owners: weekly CN phase/structure, official Compass capital ladder,
 * protection and SELL, not browser-authored phase forecast or ETA.
 * An archived snapshot must never be represented as a current live phase.
 */
export const PATH_CONTRACT = 'CN_PATH_SOURCE_PRESENTATION_v1';

const PHASES = Object.freeze([
  ['BTC','BTC leadership','BTC-lederskab'],
  ['ETH','Ethereum leadership','ETH-lederskab'],
  ['LARGE_MID','Large + mid rotation','Large + mid-rotation'],
  ['ALT_IGNITION','Altseason ignition','Altseason begynder'],
  ['MICRO','Micro acceleration','Micro-acceleration'],
  ['BROAD','Broad altseason','Bred altseason'],
  ['MANIA','Mania / euphoria','Mani / eufori'],
  ['DISTRIBUTION','Distribution','Distribution'],
  ['PROTECTION','Exit / protection','Exit / beskyttelse'],
  ['REENTRY','Cooldown / re-entry','Afkøling / re-entry']
]);
const LABEL = Object.freeze({
  da:{
    noSource:'Kilde utilgængelig',archived:'Arkiv · ikke live',observed:'Dokumenteret reference',
    noPoint:'Aktuel fase ikke verificeret',next:'Næste betingelse',noGate:'Næste gate ikke dokumenteret',
    etaUnknown:'Ingen verificeret ETA',condition:'Betinget kildevindue, ikke nedtælling',
    window:'Kildevindue',watch:'Watch · ikke bekræftet',paused:'Afventer bekræftelse',
    noAlt:'Ingen bekræftet bred altseason',btc:'BTC ledte den senest afsluttede uge',
    eth:'ETH/BTC skal stabiliseres og fastholdes',transmission:'Large/mid deltagelse skal dokumenteres',
    small:'Små selskaber skal deltage vedvarende',long:'90- og 365-dages bredde skal bekræfte',
    wait:'Ingen faseopgradering uden verificerede signaler',
    rotation:'Denne uges rotation',noTransfer:'Kapitaloverførsel til altcoins ikke bekræftet',
    source:'Frosset uge',step:'Strukturel reference',later:'Ikke verificeret',
    unavailable:'UTILGÆNGELIG',notConfirmed:'IKKE BEKRÆFTET',
    hold:'HOLD',waitAction:'AFVENT',hardWait:'HARD WAIT',unavailableAction:'UTILGÆNGELIG',
    altTitle:'Altseason-watch',sourceCaveat:'Tidsrum er observationsvinduer, ikke sikre fase-startdatoer.'
  },
  en:{
    noSource:'Source unavailable',archived:'Archived · not live',observed:'Documented reference',
    noPoint:'Current phase not verified',next:'Next confirmation',noGate:'Next gate not documented',
    etaUnknown:'No verified ETA',condition:'Conditional source window, not a countdown',
    window:'Source window',watch:'Watch · unconfirmed',paused:'Awaiting confirmation',
    noAlt:'No confirmed broad altseason',btc:'BTC led the last completed week',
    eth:'ETH/BTC must stabilize and persist',transmission:'Large/mid participation needs confirmation',
    small:'Sustained small-cap participation required',long:'90- and 365-day breadth need to confirm',
    wait:'Do not promote phases without verified signals',
    rotation:'This week\'s rotation',noTransfer:'Capital transmission to alts unconfirmed',
    source:'Frozen week',step:'Structural reference',later:'Not verified',
    unavailable:'UNAVAILABLE',notConfirmed:'UNCONFIRMED',
    hold:'HOLD',waitAction:'WAIT',hardWait:'HARD WAIT',unavailableAction:'UNAVAILABLE',
    altTitle:'Altseason watch',sourceCaveat:'Time windows are observation watches, not guaranteed phase-start dates.'
  }
});
const ALLOWED_ACTIONS=new Set(['HOLD','WAIT','HARD_WAIT','UNAVAILABLE']);
const TIER=[
  ['BTC','BTC'],
  ['ETH','ETH'],
  ['LARGE_CAPS','LARGE'],
  ['MID_CAPS','MID'],
  ['SMALL_CAPS','SMALL'],
  ['MICROCAPS','MICRO'],
  ['MEMES','MEMES']
];
const validWeek=(x)=>typeof x==='string'&&/^20\d{2}-W(?:0[1-9]|[1-4][0-9]|5[0-3])$/.test(x);
const ss=(x)=>typeof x==='string'&&x.trim()?x.trim():null;

function empty(t){
  return {contract:PATH_CONTRACT,status:'UNAVAILABLE',is_live:false,
    source_issue:null,source_week:null,source_health:'UNAVAILABLE',source_identity:null,
    current_checkpoint:null,next_checkpoint:null,next_gate:t.noGate,phase_eta:t.etaUnknown,
    source_window:null,full_phases:PHASES.map(([key,en,da],i)=>({key,label:t===LABEL.da?da:en,index:i,status:'REFERENCE_ONLY'})),
    concise_phases:[],altseason:{status:'UNAVAILABLE',target:t.altTitle,eta:t.etaUnknown,detail:t.noAlt},
    rotation:[],structural_long:{weeks_2_3:t.noSource,weeks_4_8:t.noSource},
    context:t.noSource,protection:'UNAVAILABLE',sell:'UNAVAILABLE',reentry:'UNAVAILABLE',
    source_label:t.noSource,verified_current:false};
}

/**
 * mode='archived' for pinned, source-authenticated preview; mode='live' is
 * permitted only with independently verified original weekly/Compass join.
 * Caller MUST NOT simply toggle live on an unverified source bundle.
 */
export function officialPathView(bundle,{lang='da',mode='archived',verifiedAlignment=false}={}){
  const t=LABEL[lang==='en'?'en':'da'];
  const out=empty(t);
  const weekly=bundle?.weekly, compass=bundle?.compass;
  if(!weekly||!compass||!validWeek(weekly.forecast_week)||
    !Number.isInteger(weekly.public_issue_number)||weekly.public_issue_number<1||
    !['OK','PASS','DEGRADED'].includes(weekly.status)||
    compass.data_status!=='OK'||!ss(compass.issued_at_utc)||
    !Array.isArray(compass.capitalization_ladder)||
    !Array.isArray(weekly.rotation_ladder)||!Array.isArray(weekly.altseason_countdown))return out;

  const isPreview=bundle.source_status==='POINT_IN_TIME_PREVIEW_ARCHIVE_NOT_LIVE';
  const liveEligible=!isPreview && mode==='live' && verifiedAlignment===true &&
    compass.weekly_context?.forecast_week===weekly.forecast_week &&
    compass.weekly_context?.public_issue_number===weekly.public_issue_number &&
    compass.weekly_context?.status==='ALIGNED';
  // In the archived seed, a known local frozen source joins the exact two
  // W41 authorities; future live must pass verified outside this UI.
  const archiveEligible=isPreview&&mode==='archived'&&
    weekly.public_issue_number===28&&weekly.forecast_week==='2026-W41'&&
    compass.compass_id==='CMP-20261011-7d14a9ee5914'&&
    compass.issued_at_utc==='2026-10-11T13:15:27Z';
  if(!archiveEligible&&!liveEligible)return out;

  // Never promote a held ETH allocation to confirmed ETH leadership.
  // The historical BTC phase is supported by the frozen weekly
  // market-state text plus a separately recorded BTC leadership row.
  const btcEntry=weekly.rotation_ladder.find(x=>x.segment==='BTC');
  const btcEvidence=ss(weekly.market_state)&&/BTC.led|BTC-led/i.test(weekly.market_state)&&
    ss(btcEntry?.status)&&/led|leader|leadership/i.test(btcEntry.status);
  const ethStatus=weekly.rotation_ladder.find(x=>x.segment==='ETH')?.status||'';
  const ethGate=weekly.altseason_countdown.find(x=>/ETH-relative stabiliz/i.test(x.phase||''));
  const tierGate=weekly.altseason_countdown.find(x=>/Large-cap to midcap/i.test(x.phase||''));
  const longGate=weekly.altseason_countdown.find(x=>/Broad, multi-horizon altseason/i.test(x.phase||''));
  const tierMap=new Map(compass.capitalization_ladder.map(x=>[x.segment,x]));
  const rotation=TIER.map(([key,short])=>{
    const original=tierMap.get(key);
    const action=ALLOWED_ACTIONS.has(original?.action)?original.action:
      (ALLOWED_ACTIONS.has(original?.status)?original.status:'UNAVAILABLE');
    const eta=ss(original?.eta);
    return {key,label:short,action,eta:eta||null,
      supported:!!original&&ALLOWED_ACTIONS.has(action)};
  });
  const leading=btcEvidence?'BTC':null;
  const referenceIndex=leading?0:-1;
  const next=referenceIndex===0?'ETH':null;
  const reference=PHASES.map(([key,en,da],i)=>{
    let evidence='UNCONFIRMED';
    if(i===0 && leading==='BTC') evidence='HISTORICALLY_OBSERVED';
    else if(i===7 && compass.protection_tracker?.distribution_risk==='CONFIRMED')evidence='SOURCE_RISK_CONDITION_NOT_CYCLE_CONFIRMATION';
    else if(i===8 && compass.sell_assessment?.state!=='UNAVAILABLE'&&compass.sell_assessment?.state)evidence='SOURCE_SELL_CONTEXT_NOT_CYCLE_CONFIRMATION';
    return {key,label:t===LABEL.da?da:en,index:i,status:evidence,
      is_reference:i===0&&!!leading};
  });
  const current=leading?{key:leading,label:t===LABEL.da?PHASES[0][2]:PHASES[0][1],
    status:'FROZEN_WEEK_REFERENCE',source_note:t.btc}:null;
  const nextObj=next?{key:next,label:t===LABEL.da?PHASES[1][2]:PHASES[1][1],
    status:'UNCONFIRMED',source_note:t.eth}:null;
  const altShadow=weekly.altseason_countdown.find(x=>/30d alt participation/i.test(x.phase||''));
  const altStatus=longGate ? 'WATCH_ONLY' : 'UNAVAILABLE';
  const w23=ss(weekly.decision_projection?.next_2_3w?.summary)||ss(weekly.base_case_2_3_weeks);
  const w48=ss(weekly.decision_projection?.weeks_4_8?.summary)||ss(weekly.base_case_4_8_weeks);
  return {
    contract:PATH_CONTRACT,status:'SOURCE_BOUND',
    is_live:!!liveEligible,source_issue:weekly.public_issue_number,
    source_week:weekly.forecast_week,source_health:weekly.status,
    source_identity:ss(compass.compass_id),source_label:(liveEligible?'OFFICIAL':t.archived)+
      ' · CN #'+weekly.public_issue_number+' · '+weekly.forecast_week,
    verified_current:!!liveEligible,
    current_checkpoint:current,next_checkpoint:nextObj,
    // The original data offers conditional windows, not an independently
    // verified start time. Retain raw source string only for transparent
    // detail, NEVER parse it to calendar dates/ETA.
    next_gate:next?t.eth:t.noGate,
    phase_eta:t.etaUnknown,
    source_window:ss(ethGate?.window)||null,
    full_phases:reference,
    concise_phases:[0,1,2,3,8].map(i=>reference[i]),
    altseason:{status:altStatus,target:t===LABEL.da?PHASES[3][2]:PHASES[3][1],
      eta:t.etaUnknown,
      detail:longGate?t.long:(altShadow?t.watch:t.noAlt),
      watch_source:ss(altShadow?.phase),horizon_evidence:ss(longGate?.phase)},
    rotation,
    structural_long:{weeks_2_3:w23||t.noSource,weeks_4_8:w48||t.noSource},
    context:ss(weekly.market_state)||t.noSource,
    protection:ss(compass.protection_tracker?.pullback_risk_state)||'UNAVAILABLE',
    sell:ss(compass.sell_assessment?.state)||'UNAVAILABLE',
    reentry:ss(compass.protection_tracker?.reentry_state)||'UNAVAILABLE',
    tier_gate:ss(tierGate?.phase)||t.transmission,
    source_caveat:t.sourceCaveat,
    next_source_caveat:ss(ethGate?.phase)||t.eth
  };
}
