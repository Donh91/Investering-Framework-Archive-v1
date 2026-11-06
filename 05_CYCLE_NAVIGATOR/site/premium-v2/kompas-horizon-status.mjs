/**
 * Kompas PRO v2 · optional disclosure-only 14-horizon presentation map.
 * No forecasts, prices, trades, independent source issuance or authority.
 * The OFFICIAL current-direction gate is inherited from the existing site
 * verifier. Unknown/missing source never becomes an affirmative direction.
 */
export const KOMPAS_HORIZONS=Object.freeze([
  ['NOW','Nu','Now','OBSERVED'],
  ['H0_12H','0–12 timer','0–12 hours','OBSERVED'],
  ['H24H','24 timer','24 hours','PENDING'],
  ['H1_3D','1–3 dage','1–3 days','OFFICIAL','NEXT_1_3D'],
  ['H5_7D','5–7 dage','5–7 days','OFFICIAL','NEXT_5_7D'],
  ['H8_14D','8–14 dage','8–14 days','RESEARCH'],
  ['H15_21D','15–21 dage','15–21 days','RESEARCH'],
  ['H2_3W','2–3 uger','2–3 weeks','OFFICIAL','NEXT_2_3W'],
  ['H21_30D','21–30 dage','21–30 days','STRATEGIC'],
  ['H4_8W','4–8 uger','4–8 weeks','RESEARCH'],
  ['H1_3M','1–3 måneder','1–3 months','SCENARIO'],
  ['H3_6M','3–6 måneder','3–6 months','SCENARIO'],
  ['H6_9M','6–9 måneder','6–9 months','SCENARIO'],
  ['H9_12M','9–12 måneder','9–12 months','SCENARIO']
]);
const directions={
  UP:['Stigende','Rising','up'],DOWN:['Faldende','Falling','down'],
  MIXED:['Blandet','Mixed','mixed'],SIDEWAYS:['Sideværts','Sideways','mixed'],
  LEAN_BULLISH:['Forsigtigt stigende','Cautiously rising','up'],
  LEAN_BEARISH:['Forsigtigt faldende','Cautiously falling','down'],
  BULLISH:['Stigende måling','Rising observation','up'],
  BEARISH:['Faldende måling','Falling observation','down'],
  NEUTRAL:['Neutral måling','Neutral observation','mixed'],
  NO_EDGE:['Ingen påvist edge','No proven edge','missing']
};
const tr=(lang,da,en)=>lang==='en'?en:da;
function validOfficial(compass,view){
  return view?.compass?.state==='FRESH'&&
    view.compass.permit_path_live_gates===true&&
    compass?.contract==='PUBLIC_COMPASS_PROJECTION_v1'&&
    compass?.data_status==='OK'&&typeof compass.compass_id==='string'&&
    compass.compass_id===view.compass.compass_id;
}
function emptyStatus(lang){
  return {label:tr(lang,'Afventer gyldig kilde','Awaiting verified source'),tone:'missing',status:'SOURCE_UNAVAILABLE'};
}
// Strategic context has its OWN source clock and weekly lineage. A current
// Official decision is neither required nor sufficient for that NONBINDING
// context, but a caller-supplied outlook alone is never sufficient proof.
function trustedStrategicContext(trace,strategic){
  const lane=trace?.long_horizons?.find(x=>x.id==='21_30d');
  return trace?.contract==='CN_PREMIUM_SOURCE_TRACE_v1'&&
    ['COMPLETE','PARTIAL_OR_DEGRADED'].includes(trace.status)&&
    trace.sources?.some(x=>x.id==='strategic'&&x.status==='BOUND_WEEKLY_ANCHOR')&&
    lane?.owner==='CYCLE_NAVIGATOR_STRATEGIC_CONTEXT'&&
    lane.direction!=='UNAVAILABLE'&&
    strategic?.contract==='CN_PUBLIC_FORWARD_OUTLOOK_v1'&&
    strategic.status==='FROZEN_CONTEXT_ONLY'&&
    strategic.strategic?.available===true;
}
export function kompasHorizonStatusRows({compass,view,lang='da',observationCurrent=false,strategic=null,trace=null}={}){
  const verified=validOfficial(compass,view);
  const out=KOMPAS_HORIZONS.map(([id,da,en,kind,officialId])=>{
    const row={id,label:tr(lang,da,en),kind,sourceStatus:'NOT_ISSUED_IN_THIS_VIEW',
      // Never invent a numerical terminal close, interval, forecast or ETA.
      priceLabel:tr(lang,'Ingen separat verificeret kursprognose her','No separate verified price forecast here'),
      ...emptyStatus(lang),value:tr(lang,'Afventer gyldig kilde','Awaiting verified source'),
      label:tr(lang,da,en)};
    // Static knowledge of what is NOT issued must never disappear merely
    // because the separate Official daily decision has expired.
    if(kind==='PENDING'||kind==='RESEARCH'||kind==='SCENARIO'){
      const c={
        PENDING:['Ikke udstedt','Not issued','PENDING',
          'Ingen officiel prognose udstedt','No official forecast issued'],
        RESEARCH:['Research, ikke udstedt','Research, not issued','RESEARCH_ONLY',
          'Forskningshorisont · ikke prognose','Research horizon · not a forecast'],
        SCENARIO:['Scenarie ikke udstedt','Scenario not issued','SCENARIO_ONLY',
          'Muligt betinget researchscenarie','Potential conditional research scenario']
      }[kind];
      return {...row,status:c[2],tone:'missing',value:tr(lang,c[0],c[1]),
        sourceLabel:tr(lang,c[3],c[4])};
    }
    // A valid separately source-bound strategic anchor can still be shown as
    // FROZEN / NONBINDING after the daily Official decision expires.
    if(kind==='STRATEGIC'&&trustedStrategicContext(trace,strategic)){
      const info=directions[strategic.strategic.btc_direction];
      if(info&&['UP','DOWN','MIXED','SIDEWAYS','NO_EDGE'].includes(strategic.strategic.btc_direction))
        return {...row,status:'VERIFIED_STRATEGIC_CONTEXT_ONLY',
          tone:info[2],sourceStatus:'STRATEGIC_SOURCE_NONBINDING',
          value:tr(lang,info[0],info[1]),
          sourceLabel:tr(lang,'Tidligere udstedt strategisk kontekst · ikke-bindende',
            'Previously issued strategic context · nonbinding'),
          priceLabel:tr(lang,'BTC-retning · ikke kursmål','BTC direction · not a price target')};
    }
    if(!verified)return row;
    if(kind==='OFFICIAL'){
      const h=compass.horizons?.[officialId];
      const info=directions[h?.expected_direction];
      if(!info||!['UP','DOWN','MIXED','SIDEWAYS','LEAN_BULLISH','LEAN_BEARISH'].includes(h.expected_direction))
        return row;
      return {...row,label:tr(lang,da,en),kind,status:'OFFICIAL_DIRECTION_ONLY',
        tone:info[2],sourceStatus:'OFFICIAL_SOURCE_DIRECTION_ONLY',
        value:tr(lang,info[0],info[1]),
        sourceLabel:tr(lang,'Officiel retningsvurdering','Official direction'),
        // A direction is never an independently issued BTC price target.
        priceLabel:tr(lang,'Retning, ikke kursmål','Direction, not a price target')};
    }
    if(kind==='OBSERVED'){
      const info=observationCurrent?directions[compass.market_now?.directional_state]:null;
      const v=info?tr(lang,info[0],info[1]):
        tr(lang,'Måling ikke frisk','Observation not current');
      return {...row,status:info?'CURRENT_OBSERVATION':'OBSERVATION_UNAVAILABLE',
        tone:info?info[2]:'missing',value:v,
        sourceLabel:tr(lang,'Observeret momentum, ikke prognose','Observed momentum, not a forecast'),
        priceLabel:tr(lang,'Ingen fremadrettet kursprognose','No forward price forecast')};
    }
    // No source-verified strategic anchor. A type label is not an issued
    // direction, much less a numerical price forecast.
    const categories={
      STRATEGIC:['Strategisk kontekst afventer','Strategic context pending','NONBINDING_CONTEXT']
    };
    const c=categories[kind];
    return {...row,status:c[2],tone:'missing',value:tr(lang,c[0],c[1]),
      sourceLabel:tr(lang,'Ingen officiel retningsudstedelse her','No official direction issued here')};
  });
  return {contract:'CN_KOMPAS_PRO_14_HORIZON_PRESENTATION_v1',
    officialSourceCurrent:verified,rows:out};
}
