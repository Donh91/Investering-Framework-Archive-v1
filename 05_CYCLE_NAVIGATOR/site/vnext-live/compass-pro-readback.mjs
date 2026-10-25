/* KOMPAS PRO v1 · presentation-only decision-support readback.
 * No market models, no probabilities, no derived trade permissions,
 * no computed forecast ranges, no new SELL rule.
 * Only source-valid public Official Compass and the existing weekly adapter.
 */
import {officialPullbackStage} from './official-pullback-stage.mjs';

const STAGES=['NORMAL','BUILDING','ELEVATED','HIGH','CONFIRMED'];
const ACTIONS=new Set(['HOLD_WAIT','HOLD','BUY','SELL','UNAVAILABLE']);
const SELL_STATES=new Set(['UNAVAILABLE','NONE','WATCH','PREPARE','REDUCE','SELL','EXIT','CONFIRMED']);
const QUALITY=new Set(['LOW','MEDIUM','HIGH']);
const tr=(lang,da,en)=>lang==='en'?en:da;
const finite=n=>typeof n==='number'&&Number.isFinite(n);
const invalid=(lang)=>({
  contract:'CN_KOMPAS_PRO_PRESENTATION_v1',status:'UNAVAILABLE',severity:null,
  riskLabel:tr(lang,'Utilgængelig','Unavailable'),
  evidenceQuality:tr(lang,'Ukendt','Unknown'),
  eventProbability:tr(lang,'Ikke kalibreret','Not calibrated'),
  onsetEta:tr(lang,'Ikke dokumenteret','Not evidenced'),
  depth:tr(lang,'Ikke udstedt','Not issued'),
  nextReview:tr(lang,'Afventer friske data','Awaiting fresh data'),
  watchWindow:tr(lang,'Ingen kildeverificeret varsling','No source-verified watch'),
  sell:tr(lang,'Ikke tilgængelig','Unavailable'),
  distribution:tr(lang,'Ukendt','Unknown'),
  reentry:tr(lang,'Ikke tilgængelig','Unavailable'),
  guidance:tr(lang,'Afvent friske verificerede data. Undgå nye beslutninger ud fra et udløbet signal.',
                      'Wait for fresh verified data. Do not trade on an expired signal.'),
  guidanceKind:'NONBINDING_PREDEFINED_CHECKLIST',
  scenarioStatus:'NOT_ISSUED',
  forecastRows:['1–3d','5–7d','2–3w','21–30d','4–8w'].map(horizon=>({horizon,btc:null,eth:null,status:'NOT_ISSUED'})),
  sourceWeekly:{status:'UNAVAILABLE',week:null,btc:null,eth:null},
  sourceIdentity:null
});

function weekBounds(iso){
  if(typeof iso!=='string'||!/^20\\d{2}-W(?:0[1-9]|[1-4][0-9]|5[0-3])$/.test(iso))return null;
  const [year,week]=iso.split('-W').map(Number),jan4=new Date(Date.UTC(year,0,4));
  const firstMon=new Date(jan4.getTime()-((jan4.getUTCDay()+6)%7)*86400000);
  const start=new Date(firstMon.getTime()+(week-1)*7*86400000);
  const thursday=new Date(start.getTime()+3*86400000);
  if(thursday.getUTCFullYear()!==year)return null;
  return {from:start.getTime(),until:start.getTime()+7*86400000};
}

function plan(officialAction,risk,lang){
  if(!['HOLD_WAIT','HOLD'].includes(officialAction))
    return tr(lang,
      'Se den særskilte officielle handling. Denne visning udsteder ikke køb, salg eller genkøb.',
      'See the separate official action. This view issues no buy, sell or re-entry.');
  const advice={
    NORMAL:['Behold den aftalte positionering. Der er ingen aktiv pullback-varsling, men det er ikke i sig selv et købsbevis.',
            'Maintain planned exposure. No active pullback watch; that alone is not evidence to buy.'],
    BUILDING:['Behold kernepositioner, undlad at øge spekulativ risiko, og gennemgå din beskyttelsesplan.',
              'Hold core positions, avoid increasing speculative risk, and review your protection plan.'],
    ELEVATED:['Behold kernepositioner. Undlad aggressive nye altcoin-køb. Forbered en konkret trimliste, men sælg ikke alene på pullback-advarslen.',
              'Hold core positions. Avoid aggressive new altcoin buys. Prepare a trim list, but do not sell solely on the pullback watch.'],
    HIGH:['Prioritér kapitalbeskyttelse. Gennemgå hvilke spekulative positioner du eventuelt vil reducere ved yderligere bekræftelse. Intet automatisk SELL.',
          'Prioritize capital protection. Review which speculative positions you might reduce on further confirmation. No automatic SELL.'],
    CONFIRMED:['Gennemgå din på forhånd fastlagte exit- og genkøbsplan. Bekræftet risiko er stadig ikke en selvstændig officiel SELL-tilladelse.',
               'Review your preplanned exit and re-entry rules. Confirmed risk still does not independently authorize SELL.']
  };
  return advice[risk]?.[lang==='en'?1:0]||
    tr(lang,'Afvent flere bekræftede data.','Await further verified evidence.');
}

/** Source-only. Caller must use current site official feed parity. */
export function compassProReadback(view,official,{lang='da',nowUtc=new Date().toISOString()}={}){
  const out=invalid(lang),now=Date.parse(nowUtc);
  if(!Number.isFinite(now)||view?.compass?.state!=='FRESH'||
     view?.compass?.permit_path_live_gates!==true||
     official?.contract!=='PUBLIC_COMPASS_PROJECTION_v1'||official?.data_status!=='OK'||
     !official?.compass_id||view.compass.compass_id!==official.compass_id||
     official.weekly_context?.status!=='ALIGNED'||
     official.weekly_context?.forecast_week!==view?.weekly?.forecast_week||
     official.weekly_context?.public_issue_number!==view.weekly.public_issue_number||
     !ACTIONS.has(official.action_now)||official.action_now!==view.compass.action_now)
    return out;

  out.status='OFFICIAL_SOURCE_BOUND';
  out.sourceIdentity=official.compass_id;
  const raw=official.protection_tracker;
  const risk=officialPullbackStage(official,{forecast_week:view.weekly.forecast_week},lang);
  const ok=risk.status==='SOURCE_VALID'&&STAGES.includes(risk.sourceRiskState);
  const riskState=ok?risk.sourceRiskState:null;
  out.severity=ok?STAGES.indexOf(riskState)+1:null;
  out.riskLabel=ok?risk.stageLabel:out.riskLabel;
  out.evidenceQuality=ok&&QUALITY.has(raw?.confidence_quality)?
      tr(lang,{LOW:'Lav',MEDIUM:'Middel',HIGH:'Høj'}[raw.confidence_quality],
              {LOW:'Low',MEDIUM:'Medium',HIGH:'High'}[raw.confidence_quality]):out.evidenceQuality;
  const wk=weekBounds(view.weekly.forecast_week);
  const windowCurrent=wk&&wk.from<=now&&now<wk.until;
  const typedWindow=ok&&risk.windowKind==='GOVERNED_PROSPECTIVE_WINDOW'&&windowCurrent;
  out.onsetEta=typedWindow?risk.etaLabel:out.onsetEta;
  out.watchWindow=ok&&windowCurrent?risk.etaLabel:
      tr(lang,'Ingen aktuelt verificeret startvindue','No current verified onset window');
  // The only existing typed short-horizon ETA is a decision REVIEW, not pullback onset.
  const review=official.horizons?.NEXT_1_3D?.eta;
  out.nextReview=typeof review==='string'&&/^(?:24-72h|1-3d|24–72h)$/.test(review)?
     tr(lang,'24–72 timer · ny vurdering','24–72 hours · reassess'):out.nextReview;
  // Depth and event probability MUST stay unknown until their respective
  // independently prospectively frozen/validated public source fields exist.
  out.depth=tr(lang,'Ikke kvantificeret','Not quantified');
  out.eventProbability=tr(lang,'Ikke kalibreret','Not calibrated');
  const sell=official.sell_assessment;
  out.sell=sell?.contract==='COMPASS_SELL_ASSESSMENT_v1'&&
     sell?.authority?.portfolio_execution===false&&
     sell?.authority?.protection_is_sell_authority===false&&
     SELL_STATES.has(sell.state)?sell.state:tr(lang,'Ikke tilgængelig','Unavailable');
  out.distribution=typeof raw?.distribution_risk==='string'&&
     ['NONE','WARNING','CONFIRMED','UNKNOWN'].includes(raw.distribution_risk)?
     raw.distribution_risk:out.distribution;
  out.reentry=typeof raw?.reentry_state==='string'&&
     ['INACTIVE','WAIT_FOR_FLUSH','WAIT_FOR_RECLAIM','REVIEW','UNAVAILABLE'].includes(raw.reentry_state)?
     raw.reentry_state:out.reentry;
  out.guidance=ok?plan(official.action_now,riskState,lang):
     tr(lang,'Risikoen er ikke kildeverificeret. Hold beslutningen på pause.',
             'Risk is not source-verified. Pause the decision.');
  if(wk&&view.weekly.state!=='UNAVAILABLE'&&
     Number.isInteger(view.weekly.public_issue_number)){
    const btc=view.weekly.btc_range,eth=view.weekly.eth_range;
    const validRange=x=>finite(x?.low)&&finite(x?.high)&&x.low>0&&x.high>x.low;
    out.sourceWeekly={status:wk.until<=now?'HISTORICAL_FROZEN_WEEK':
       wk.from>now?'FROZEN_FUTURE_WEEK':'FROZEN_CURRENT_WEEK',
      week:view.weekly.forecast_week,
      btc:validRange(btc)?{low:btc.low,high:btc.high}:null,
      eth:validRange(eth)?{low:eth.low,high:eth.high}:null};
  }
  return out;
}
