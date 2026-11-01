/**
 * Kompas PRO: bounded source-reader ONLY. Never issues a forecast, risk stage,
 * trading permission, day-by-day path or portfolio recommendation.
 * All narrative is already published public prose, translated by exact match.
 */
export const VIEWS = Object.freeze([
  {id:'NEXT_1_3D',da:'1–3 dage',en:'1–3 days'},
  {id:'NEXT_5_7D',da:'5–7 dage',en:'5–7 days'},
  {id:'NEXT_2_3W',da:'2–3 uger',en:'2–3 weeks'},
  {id:'CYCLE_ALTCOINS_3_8W',da:'3–8 uger',en:'3–8 weeks'}
]);
const DIRECTION={
  UP:['Stigende','Rising'],DOWN:['Faldende','Falling'],
  MIXED:['Blandet','Mixed'],SIDEWAYS:['Sideværts','Sideways'],
  LEAN_BEARISH:['Hældning mod fald','Leaning bearish'],
  LEAN_BULLISH:['Hældning mod stigning','Leaning bullish'],
  NO_EDGE:['Ingen dokumenteret fordel','No proven edge'],
  UNAVAILABLE:['Ingen sikker vurdering','No supported outlook']
};
const POSTURE={
  WAIT:['Afvent','Wait'],HOLD_WAIT:['Afvent','Wait'],
  HOLD:['Behold / afvent','Hold / wait'],
  NO_EDGE:['Ingen handlefordel','No trading edge'],
  ABSTAIN:['Ingen ny handling','No new action'],
  UNAVAILABLE:['Ikke fastlagt','Not established']
};
const tr=(da,en,lang)=>lang==='en'?en:da;
const label=(dict,key,lang,fallback)=>dict[key]?.[lang==='en'?1:0]||fallback;
const isPlain=s=>typeof s==='string'&&s.length>=6&&s.length<=900&&!/[\u0000-\u001f<>]/.test(s);
const cleanSentence=s=>s.length<=380?s:s.slice(0,377).replace(/\s+\S*$/,'')+'…';
// Replace only machine vocabulary inside the already-issued public sentence.
// No inference, changed price, probability, trading authority or time horizon.
const readableSource=(text,lang)=>cleanSentence(text)
  .replace(/\bUNAVAILABLE\b/g,lang==='en'?'not established':'ikke fastlagt')
  .replace(/\bMIXED\b/g,lang==='en'?'mixed':'blandet')
  .replace(/\bNO_EDGE\b/g,lang==='en'?'no proven edge':'ingen påvist fordel')
  .replace(/\bHOLD_WAIT\b/g,lang==='en'?'wait':'afvent');


/**
 * Presentation only. Confirm the original Official expiry without reviving
 * an invalid or mismatched source as a CURRENT decision.
 */
export function expiredOfficial({compass,view,now=Date.now()}){
 const until=Date.parse(compass?.full_stack?.official_freshness?.valid_until_utc);
 const issued=Date.parse(compass?.issued_at_utc);
 return !!(compass?.contract==='PUBLIC_COMPASS_PROJECTION_v1'&&
  compass?.data_status==='OK'&&
  typeof compass.compass_id==='string'&&compass.compass_id&&
  view?.compass?.compass_id===compass.compass_id&&
  compass?.weekly_context?.status==='ALIGNED'&&
  compass.weekly_context.forecast_week===view?.weekly?.forecast_week&&
  Number.isFinite(until)&&until<=now&&
  Number.isFinite(issued)&&issued<=until&&issued<=now);
}

export function currentCompass({compass,view,now=Date.now()}){
  const until=Date.parse(compass?.full_stack?.official_freshness?.valid_until_utc);
  const issued=Date.parse(compass?.issued_at_utc);
  return !!(
    view?.compass?.state==='FRESH'&&view.compass.permit_path_live_gates===true&&
    view.compass.compass_id===compass?.compass_id&&
    compass?.contract==='PUBLIC_COMPASS_PROJECTION_v1'&&compass.data_status==='OK'&&
    compass.weekly_context?.status==='ALIGNED'&&
    compass.weekly_context.forecast_week===view?.weekly?.forecast_week&&
    Number.isFinite(until)&&until>now&&
    Number.isFinite(issued)&&issued<=now
  );
}

export function sourceTranslation(sentence,latest,lang){
  if(!isPlain(sentence))return {text:'',translated:false};
  if(lang==='en')return {text:readableSource(sentence,lang),translated:true};
  const pair=Array.isArray(latest?.presentation_translations)?
    latest.presentation_translations.find(x=>x?.en===sentence&&isPlain(x?.da)):null;
  // Only an exact, authored source-to-source translation is allowed.
  if(pair)return {text:readableSource(pair.da,lang),translated:true};
  // This is the exact translation of a known public sentence, not a new call.
  if(sentence==='Short-horizon state is cross-checked against the current weekly regime; transmission must improve before risk moves down-cap.'){
    return {text:'Den korte vurdering holdes op mod ugens marked. Bredere deltagelse skal forbedres, før risiko flyttes til mindre kryptovalutaer.',translated:true};
  }
  return {text:readableSource(sentence,lang),translated:false};
}

export function readHorizon({latest,compass,view,lang='da',id='NEXT_1_3D',now=Date.now()}){
  const selected=VIEWS.find(x=>x.id===id)||VIEWS[0];
  const current=currentCompass({compass,view,now});
  const source=current?compass.horizons?.[selected.id]:null;
  const rawDirection=source?.expected_direction;
  const rawPosture=source?.action_posture;
  const direction=current?label(DIRECTION,rawDirection,lang,tr('Ikke fastlagt','Not established',lang)):
    tr('Afventer nye data','Awaiting updated data',lang);
  const posture=current?label(POSTURE,rawPosture,lang,tr('Ikke fastlagt','Not established',lang)):
    tr('Ingen aktuel handling','No current action',lang);
  const hasDirection=current&&rawDirection!=='UNAVAILABLE'&&rawDirection!=='UNKNOWN'&&
    Object.hasOwn(DIRECTION,rawDirection);
  const src=sourceTranslation(source?.expected_path,latest,lang);
  const description=current&&src.text?src.text:
    tr('Ingen aktuel, dokumenteret fortolkning.','No current documented interpretation.',lang);
  return {
    current,selected,hasDirection,direction,posture,description,
    translated:current?src.translated:true,
    publishedAt:current?compass.issued_at_utc:null,
    week:current?compass.weekly_context.forecast_week:null,
    sourceAction:current?compass.action_now:null,
    sourcePosture:current?rawPosture:null,
    sourceDirection:current?rawDirection:null,
    reviewWindow:current&&selected.id==='NEXT_1_3D'&&
      /^(?:24-72h|24–72h|1-3d)$/.test(source?.eta||'')?'24–72h':null
  };
}

export function lensContext(reading,lens='swing',lang='da'){
  if(!reading.current)return tr(
    'Ingen beslutning på gamle eller manglende data. Afvent en ny verificeret vurdering.',
    'Do not act on old or missing data. Await a new verified reading.',lang);
  const caution=['WAIT','HOLD_WAIT','NO_EDGE','ABSTAIN','UNAVAILABLE'].includes(
    reading.sourcePosture);
  if(lens==='swing')return caution?tr(
    'Kortsigtet: afvent et selvstændigt bekræftet signal, før du overvejer en ny swing-position.',
    'Short term: await a separately confirmed signal before considering a new swing position.',lang):
    tr('Kortsigtet: se den officielle handling. Retning alene er ikke et købs- eller salgssignal.',
       'Short term: see the official action. Direction alone is not a buy/sell signal.',lang);
  return tr(
    'Langsigtet: følg regimeskift og risikobekræftelse. Ugeudsigten giver ikke i sig selv tilladelse til at købe eller sælge.',
    'Long term: watch for regime and risk confirmation. The outlook alone does not authorize buying or selling.',lang);
}


/**
 * Explain *why WAIT* in the selected horizon. WAIT is not a prediction of
 * sideways prices, a 50/50 probability, or a recommendation to sell holdings.
 * This layer has no authority to issue or promote any market or trade signal.
 */
export function explainPosture(reading,lang='da'){
 const trc=(da,en)=>tr(da,en,lang);
 if(!reading.current)return trc(
  'Ingen aktuel kildevurdering. Tidligere signaler er ikke en handleanvisning.',
  'No current source assessment. Prior signals are not trading instructions.');
 const posture=reading.sourcePosture,dir=reading.sourceDirection;
 if(posture==='WAIT'||posture==='HOLD_WAIT'||posture==='ABSTAIN'){
  if(dir==='MIXED')return trc(
    'Afvent = signalerne peger begge veje. Intet nyt køb eller salg er bekræftet for perioden.',
    'Wait = evidence points both ways. No new buy or sell is confirmed for this horizon.');
  if(dir==='UP'||dir==='LEAN_BULLISH')return trc(
    'Afvent = udsynet peger op, men nyt køb er ikke bekræftet.',
    'Wait = the outlook leans up, but a new buy is not confirmed.');
  if(dir==='DOWN'||dir==='LEAN_BEARISH')return trc(
    'Afvent = udsynet peger ned, men det er ikke et selvstændigt salgssignal.',
    'Wait = the outlook leans down, but this is not an independent sell signal.');
  return trc('Afvent = intet nyt handelssignal er bekræftet i perioden.',
             'Wait = no new trading signal is confirmed for this horizon.');
 }
 if(posture==='HOLD')return trc(
  'HOLD = behold eksisterende vurdering; det er ikke et signal om at købe mere.',
  'HOLD = maintain the current stance; this is not a signal to buy more.');
 if(posture==='NO_EDGE'||posture==='UNAVAILABLE'||dir==='UNAVAILABLE')
  return trc('Intet dokumenteret handlingssignal for perioden.',
             'No supported action signal for this horizon.');
 return trc('Retning og handling vurderes separat. Se den officielle handling før en beslutning.',
            'Direction and action are separate. Check the official action before deciding.');
}

/**
 * One concise adaptive sentence *under the original current-action verdict*.
 * Never present review ETA as a forecasted event time or replace source action.
 */
export function explainCurrentAction({latest,compass,view,lang='da',now=Date.now()}){
 const reading=readHorizon({latest,compass,view,lang,id:'NEXT_1_3D',now});
 if(!reading.current)return tr('Ingen gyldige aktuelle data. Afvent ny kildevurdering.',
   'No current valid data. Await an updated source assessment.',lang);
 const action=compass.action_now;
 if(!['HOLD_WAIT','WAIT','HOLD','ABSTAIN'].includes(action))return null;
 const horizon=reading.sourceDirection;
 const wait=action==='HOLD_WAIT'||action==='WAIT'||action==='ABSTAIN';
 const start=lang==='en'?'1–3 days: ':'1–3 dage: ';
 let detail;
 if(wait&&horizon==='MIXED')detail=tr(
   'blandede signaler; ingen ny handel bekræftet.',
   'mixed evidence; no new trade confirmed.',lang);
 else if(wait&&(horizon==='DOWN'||horizon==='LEAN_BEARISH'))detail=tr(
   'svagt udsyn, men intet selvstændigt salgssignal.',
   'weak outlook, but no independent sell signal.',lang);
 else if(wait&&(horizon==='UP'||horizon==='LEAN_BULLISH'))detail=tr(
   'positivt udsyn, men intet nyt køb bekræftet.',
   'positive outlook, but no new buy confirmed.',lang);
 else if(wait)detail=tr('ingen ny handel bekræftet.','no new trade confirmed.',lang);
 else detail=tr('behold aktuel vurdering; intet nyt købssignal.',
                 'maintain current stance; no new buy signal.',lang);
 const review=reading.reviewWindow?tr(' Revurdering: 24–72 timer.',
   ' Review window: 24–72 hours.',lang):'';
 return start+detail+review;
}

/**
 * Optional source-owned condition to watch. It is neither a threshold nor a
 * mechanical trigger, and can never change the official action.
 */
export function sourceWatch({latest,compass,view,lang='da',now=Date.now()}){
 if(!currentCompass({compass,view,now}))return null;
 const p=compass?.protection_tracker,c=p?.public_explanation;
 if(c?.contract!=='CN_PUBLIC_PROTECTION_COPY_v1'||c.action_authority!==false||
    c.risk_state!==p?.pullback_risk_state||
    c.forecast_week!==compass.weekly_context.forecast_week||
    !isPlain(c.watch_for)||c.watch_for.length>220)return null;
 const t=sourceTranslation(c.watch_for,latest,lang);
 return t.text?{text:t.text,translated:t.translated}:null;
}
