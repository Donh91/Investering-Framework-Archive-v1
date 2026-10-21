/**
 * Investor drilldown for the EXISTING pullback disclosure.
 * Read-only, official-source only; no market classification, event clock,
 * probability, altitude/beta multiplication, wallet access or trade advice.
 */
import { officialPullbackStage } from './official-pullback-stage.mjs';

const LANG={
  da:{
    eta:'Mulig timing',confidence:'Sandsynlighed 1–10',size:'Størrelse · BTC / ETH',
    alts:'Altcoin-påvirkning',duration:'Varighed / re-entry-hastighed',
    weeks:'Struktur · 2–3 uger',cycle:'Cyklus · 4–8 uger',
    regime:'Længere bear-skifte',watch:'Næste bekræftelse',weakens:'Hvad svækker advarslen',
    unavailable:'Ikke vurderbart: officiel kilde mangler',
    notCalibrated:'Ikke kalibreret · ingen valid 1–10 score',
    sizeUnknown:'Ikke kvantificeret · dip vs stort fald ukendt',
    altUnknown:'Ingen valideret størrelse for large/mid/small/micro/memes',
    durationUnknown:'Varighed, trough og re-entry-vindue ikke forudsagt',
    regimeUnknown:'Ikke klassificeret · pullback er ikke automatisk bear',
    horizonUnknown:'Ingen verificeret kildebaseret retning',
    onlyDirection:'Officiel horisontretning, ikke separat SELL/bear-bevis',
    noWatch:'Ingen aktiv varsling',
    sourceMissing:'Ingen verificeret kildebaseret driver'
  },
  en:{
    eta:'Possible timing',confidence:'Likelihood 1–10',size:'Magnitude · BTC / ETH',
    alts:'Altcoin impact',duration:'Duration / re-entry speed',
    weeks:'Structure · 2–3 weeks',cycle:'Cycle · 4–8 weeks',
    regime:'Longer bear transition',watch:'Next confirmation',weakens:'What weakens the warning',
    unavailable:'Unavailable: official source not verified',
    notCalibrated:'Not calibrated · no valid 1–10 score',
    sizeUnknown:'Not quantified · dip vs major pullback unknown',
    altUnknown:'No validated magnitude for large/mid/small/micro/memes',
    durationUnknown:'Duration, trough and re-entry window not predicted',
    regimeUnknown:'Not classified · a pullback does not prove a bear market',
    horizonUnknown:'No verified source-owned direction',
    onlyDirection:'Official horizon direction, not separate SELL/bear proof',
    noWatch:'No active warning',
    sourceMissing:'No verified source-owned driver'
  }
};
const DIRECTIONS=new Set(['UP','DOWN','MIXED','SIDEWAYS','NEUTRAL','NO_EDGE','UNAVAILABLE']);
function sourceDirection(compass,key,loc) {
  const code=compass?.horizons?.[key]?.expected_direction;
  if(typeof code!=='string'||!DIRECTIONS.has(code)||code==='NO_EDGE'||code==='UNAVAILABLE')return loc.horizonUnknown;
  return code+' · '+loc.onlyDirection;
}
function alignedExplanation(compass,weekly,stage) {
  const p=compass?.protection_tracker?.public_explanation;
  if(!p||p.contract!=='CN_PUBLIC_PROTECTION_COPY_v1'||
    p.forecast_week!==weekly?.forecast_week||
    p.risk_state!==stage.sourceRiskState) return null;
  return p;
}
export function officialPullbackInvestorView(compass,weekly,lang='da') {
  const locale=lang==='en'?'en':'da',t=LANG[locale];
  const stage=officialPullbackStage(compass,weekly,locale);
  // Preserve the upstream risk class elsewhere, but no detailed investor
  // ETA/bear-context claims may be displayed if typed timing metadata
  // contradicts the official public risk source.
  const valid=stage.status==='SOURCE_VALID' &&
    !['SOURCE_MISMATCH','INVALID_DATE_PAIR'].includes(stage.windowKind);
  const explanation=valid?alignedExplanation(compass,weekly,stage):null;
  const plain=(value)=>(typeof value==='string'&&value.trim()&&value.length<=1200)?value.trim():null;
  const risk=compass?.protection_tracker;
  const driver=explanation&&plain(explanation.watch_for);
  const weakens=explanation&&plain(explanation.weakens_if);
  const fallbackInvalidation=valid&&plain(risk?.invalidation);
  const eta=valid?stage.etaLabel:t.unavailable;
  const rows=[
    {id:'eta',label:t.eta,value:eta,source:valid?'OFFICIAL_COMPASS':'UNAVAILABLE'},
    {id:'likelihood',label:t.confidence,value:t.notCalibrated,source:'NOT_CALIBRATED'},
    {id:'magnitude',label:t.size,value:t.sizeUnknown,source:'UNQUANTIFIED'},
    {id:'alt_impact',label:t.alts,value:t.altUnknown,source:'UNQUANTIFIED'},
    {id:'duration',label:t.duration,value:t.durationUnknown,source:'UNASSESSED'},
    {id:'weeks_2_3',label:t.weeks,value:valid?sourceDirection(compass,'NEXT_2_3W',t):t.unavailable,source:valid?'OFFICIAL_COMPASS':'UNAVAILABLE'},
    {id:'weeks_4_8',label:t.cycle,value:valid?sourceDirection(compass,'CYCLE_ALTCOINS_3_8W',t):t.unavailable,source:valid?'OFFICIAL_COMPASS':'UNAVAILABLE'},
    {id:'bear_transition',label:t.regime,value:t.regimeUnknown,source:'NOT_CLASSIFIED'},
    {id:'watch_for',label:t.watch,value:valid?(driver||t.sourceMissing):t.unavailable,source:driver?'SOURCE_PUBLIC_EXPLANATION':'UNAVAILABLE'},
    {id:'weakens_if',label:t.weakens,value:valid?(weakens||fallbackInvalidation||t.sourceMissing):t.unavailable,source:(weakens||fallbackInvalidation)?'OFFICIAL_PROTECTION':'UNAVAILABLE'}
  ];
  return {
    contract:'CN_PULLBACK_INVESTOR_DISCLOSURE_v1',
    authority:'SOURCE_ONLY_UI',
    status:valid?'VALID':'UNAVAILABLE',
    source_risk_state:valid?stage.sourceRiskState:'UNAVAILABLE',
    rows
  };
}
