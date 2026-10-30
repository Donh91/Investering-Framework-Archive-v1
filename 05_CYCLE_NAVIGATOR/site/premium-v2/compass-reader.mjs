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
  if(lang==='en')return {text:cleanSentence(sentence),translated:true};
  const pair=Array.isArray(latest?.presentation_translations)?
    latest.presentation_translations.find(x=>x?.en===sentence&&isPlain(x?.da)):null;
  // Only an exact, authored source-to-source translation is allowed.
  if(pair)return {text:cleanSentence(pair.da),translated:true};
  // This is the exact translation of a known public sentence, not a new call.
  if(sentence==='Short-horizon state is cross-checked against the current weekly regime; transmission must improve before risk moves down-cap.'){
    return {text:'Den korte vurdering holdes op mod ugens marked. Bredere deltagelse skal forbedres, før risiko flyttes til mindre kryptovalutaer.',translated:true};
  }
  return {text:cleanSentence(sentence),translated:false};
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
    sourcePosture:current?rawPosture:null
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
