/**
 * SITE #1578 · Single-root Kompas PRO readback, not a new action issuer.
 * Reuses existing source-verification and PRO rendering from /vnext-live/.
 * No separate model, new forecast, execution, market authority or API.
 */
import '../vnext-live/premium-experience.css';
import {inspectOfficialPublicFeeds} from '../vnext-live/official-feed-parity.mjs';
import {sourceTrace,displayPublicStatus,displayLongDirection} from '../vnext-live/source-trace.mjs';
import {mondayContext,mondayLabels} from '../vnext-live/monday-public-bridge.mjs';
import {forwardOutlook} from '../vnext-live/forward-outlook.mjs';
import {VIEWS,readHorizon,lensContext,explainPosture,explainCurrentAction,sourceWatch,expiredOfficial} from './compass-reader.mjs';
import {publicOverview,directionVisual,readRotation,POSITION_GUIDE,shortVsForward,observedMarketClock} from './compass-overview.mjs';
import {originalSourceAgeLabel} from '../source-age-readback.mjs';
import {
  renderProductExperience,initProductExperience
} from '../vnext-live/premium-experience.mjs';

const SOURCE_RECHECK_MS=5*60*1000;
const CLOCK_RECHECK_MS=60*1000;
const H=[
 ['NEXT_12H','CURRENT MOMENTUM'],['NEXT_1_3D','1–3d'],
 ['NEXT_5_7D','5–7d'],['NEXT_2_3W','2–3w'],
 ['CYCLE_ALTCOINS_3_8W','3–8w']
];
const $=id=>document.getElementById(id);
const safe=s=>typeof s==='string'&&s.trim()?s.trim().slice(0,180):'UNAVAILABLE';
const t=(da,en)=>document.documentElement.lang==='en'?en:da;
let feeds=null,view=null,failed=false,request=0,inflight=false;
let selectedReaderHorizon='NEXT_1_3D',selectedReaderLens='swing';
const assets=[
 new URL('../../data/latest.json',import.meta.url),
 new URL('../../data/compass.json',import.meta.url)
];
function set(id,value){const e=$(id);if(e)e.textContent=String(value??'—')}
function time(utc){
 const ms=Date.parse(utc);
 return Number.isFinite(ms)?new Date(ms).toLocaleString(
    document.documentElement.lang==='en'?'en-GB':'da-DK',
    {timeZone:'UTC',day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'}
 )+' UTC':'—';
}
function cell(parent,value){
 const td=document.createElement('td');td.textContent=value;parent.append(td);
}

// Three independent SOURCE-ISSUED directions. No continuity, 24h forecast,
// or rise-then-fall ordering is inferred between or within the windows.
function renderOverview(){
 const lang=document.documentElement.lang==='en'?'en':'da';
 const en=lang==='en';
 const model=publicOverview({latest:feeds?.latest,compass:feeds?.compass,view,lang});
 const keys=['d13','d57','w23'];
 set('cn-overview-heading',en?'Compass outlook':'Kompasforløb');
 set('cn-overview-subtitle',en?'Three independent forecast windows':'Tre selvstændige prognosehorisonter');
 set('cn-overview-foot',en?
  'Arrows show source-issued direction for each window, not the order of price moves. Bull/Bear are coarse evidence points, not probabilities.':
  'Pilene viser retning pr. periode, ikke rækkefølgen af kursbevægelser. Bull/Bear er grove evidenspoint, ikke sandsynligheder.');
 const contrast=shortVsForward({compass:feeds?.compass,view,lang});
 set('cn-short-meaning',(en?'Now vs 1–3 days: ':'Nu vs. 1–3 dage: ')+contrast.text);
 const contrastEl=$('cn-short-meaning');if(contrastEl){
  contrastEl.dataset.contrastState=contrast.state;
  contrastEl.dataset.sourceBound=String(contrast.sourceBound);
 }
 keys.forEach((key,i)=>{
  const card=model.cards[i];
  set('cn-overview-'+key+'-arrow',card.arrow);
  set('cn-overview-'+key+'-direction',card.direction);
  set('cn-overview-'+key+'-position',card.position);
  set('cn-overview-'+key+'-summary',card.summary.text);
  set('cn-overview-'+key+'-balance',card.evidence?
   (en?'Evidence points: ':'Evidenspoint: ')+'Bull '+card.evidence.bull+' · Bear '+card.evidence.bear:
   (en?'No verified evidence balance':'Ingen verificeret evidensbalance'));
  const bar=$('cn-overview-'+key+'-bar');
  if(bar)bar.style.width=card.evidence?String(card.evidence.bull*10)+'%':'0%';
  const root=document.querySelector('[data-cn-overview="'+key+'"]');
  if(root){
   root.dataset.sourceCurrent=String(model.valid);
   root.dataset.direction=card.sourceDirection;
   root.setAttribute('aria-label',card.title+': '+card.direction+'. '+card.position+
    '. '+(card.evidence?'Bull '+card.evidence.bull+', Bear '+card.evidence.bear+'. ':'')+
    card.summary.text);
  }
 });
 const observationLabel=contrast.state==='OBSERVATION_DELAYED'?
  (en?'Delayed price observation':'Prisobservation forsinket'):
  contrast.state==='SOURCE_INVALID'||contrast.state==='OBSERVATION_CLOCK_INVALID'?
  (en?'Price observation unavailable':'Ingen gyldig prisobservation'):
  (en?'Latest verified price observation':'Seneste verificerede prisobservation');
 set('cn-overview-observed-caption',observationLabel);
 const rotation=readRotation({compass:feeds?.compass,view,lang});
 const list=$('cn-rotation-classes');
 if(list)list.replaceChildren();
 set('cn-rotation-heading',en?'Positioning & rotation':'Positionering og rotation');
 set('cn-rotation-full',en?'Explore the cycle':'Se markedsforløbet');
 set('cn-rotation-disclaimer',en?
  'HOLD applies only to positions already owned. Class labels are not new buy/sell signals.':
  'HOLD gælder kun eksisterende positioner. Klassevisningen er ikke nye køb/salg-signaler.');
 const map=new Map(rotation.rows.map(x=>[x.id,x]));
 const group=(label,ids)=>{
  const rows=ids.map(x=>map.get(x));
  if(rows.some(x=>!x))return null;
  const same=rows.every(x=>x.sourceAction===rows[0].sourceAction);
  return same?{name:label,stance:rows[0].stance,source:rows[0].sourceAction}:
   rows.map(x=>({name:x.name,stance:x.stance,source:x.sourceAction}));
 };
 const groups=rotation.valid?[
  group('BTC / ETH',['BTC','ETH']),
  group(en?'Large / Mid / Small':'Store / Mellem / Små',['LARGE_CAPS','MID_CAPS','SMALL_CAPS']),
  group(en?'Microcaps':'Mikroaktiver',['MICROCAPS']),group('Memes',['MEMES'])
 ].flatMap(x=>Array.isArray(x)?x:x?[x]:[]):[];
 if(list)for(const g of groups){
  const row=document.createElement('div');row.className='cn-rotation-class';
  row.setAttribute('role','listitem');row.dataset.action=g.source;
  const name=document.createElement('strong');name.textContent=g.name;
  const stance=document.createElement('span');stance.textContent=g.stance;
  row.append(name,stance);list.append(row);
 }
 const trustedCore=rotation.valid&&map.get('BTC')?.sourceAction==='HOLD'&&
  map.get('ETH')?.sourceAction==='HOLD';
 const altNotPromoted=rotation.valid&&['LARGE_CAPS','MID_CAPS','SMALL_CAPS','MICROCAPS']
   .every(k=>['WAIT','HARD_WAIT'].includes(map.get(k)?.sourceAction));
 set('cn-rotation-summary',!rotation.valid?
  (en?'Class positioning unavailable until the official source is valid.':
      'Klassevurdering afventer gyldige officielle data.'):
  trustedCore&&altNotPromoted?
   (en?'BTC and ETH: maintain existing exposure; broader altcoin rotation remains conditional.':
       'BTC og ETH: behold eventuel eksisterende eksponering. Bred rotation kræver særskilt bekræftelse.'):
  trustedCore?
   (en?'Existing BTC/ETH positions are retained. Follow each additional class on its own official source.':
       'Eksisterende BTC/ETH-positioner beholdes. Følg hver øvrig klasse efter dens officielle kildevurdering.'):
   (en?'Position by class follows the issued source; there is no assumed upgrade from WAIT to HOLD.':
       'Se kildens vurdering af hver klasse. AFVENT bliver ikke automatisk til HOLD.'));
 set('cn-positions-title',en?
  'What do WAIT, WATCH, PREPARE, HOLD and SELL mean?':
  'Hvad betyder Afvent, Overvåg, Forbered, Hold og Sælg?');
 set('cn-positions-disclaimer',en?
  'Vocabulary only. Not an active or mandatory trading sequence. WAIT never implies a prior purchase.':
  'Kun begreber, ikke aktive signaler eller en automatisk handelskæde. AFVENT betyder ikke, at man allerede har købt.');
 const termRoot=$('cn-position-terms');if(termRoot){
  termRoot.replaceChildren();
  for(const [id,da,daMeaning,eng,enMeaning] of POSITION_GUIDE){
   const dt=document.createElement('dt');dt.textContent=en?eng:da;
   const dd=document.createElement('dd');dd.textContent=en?enMeaning:daMeaning;
   dt.dataset.state=id;termRoot.append(dt,dd);
  }
 }
 set('cn-reader-expand-title',en?
  'Read all horizons, Swing/HODL and source evidence':
  'Uddyb tidshorisonter, Swing/HODL og kildegrundlag');
}

function horizons(){
 const body=$('horizon-body');if(!body)return;
 body.replaceChildren();
 const eligible=view?.compass?.state==='FRESH'&&view?.compass?.permit_path_live_gates===true&&
   feeds?.compass?.contract==='PUBLIC_COMPASS_PROJECTION_v1'&&
   feeds.compass.data_status==='OK';
 const rows=eligible?H:[['UNAVAILABLE',t('Afventer kilde','Awaiting source')]];
 for(const [key,label] of rows){
  const r=document.createElement('tr'),v=eligible?feeds.compass.horizons?.[key]:null;
  cell(r,key==='NEXT_12H'?t('Aktuelt momentum · ikke prognose','Current momentum · not a forecast'):label);
  const rawDirection=key==='NEXT_12H'?feeds?.compass?.market_now?.directional_state:v?.expected_direction;
  const sourcePosture=v?.action_posture;
  const words={WAIT:t('Afvent','Wait'),HOLD:t('Behold eksisterende','Hold existing'),
   HOLD_WAIT:t('Afvent','Wait'),HARD_WAIT:t('Skærpet afvent','Strict wait'),
   NO_EDGE:t('Ingen påvist fordel','No proven edge'),UNAVAILABLE:t('Ingen vurdering','No outlook')};
  cell(r,eligible?directionVisual(rawDirection,document.documentElement.lang).text:'—');
  cell(r,eligible?(words[sourcePosture]||t('Ikke fastlagt','Not established')):'—');
  body.append(r);
 }
}
function renderQuickDecision(){
 const lang=document.documentElement.lang==='en'?'en':'da';
 const eligible=view?.compass?.state==='FRESH'&&
   view?.compass?.permit_path_live_gates===true&&
   feeds?.compass?.contract==='PUBLIC_COMPASS_PROJECTION_v1'&&
   feeds.compass.data_status==='OK'&&
   feeds.compass.compass_id===view.compass.compass_id;
 const h=eligible?feeds.compass.horizons?.NEXT_1_3D:null;
 const direction=safe(h?.expected_direction);
 const posture=safe(h?.action_posture);
 // Presentation-only translations of known official enums: never infer new
 // forward direction, time, permission or source validity.
 const directions={
  UP:['Stigende','Rising'],DOWN:['Faldende','Falling'],
  MIXED:['Blandet','Mixed'],SIDEWAYS:['Sideværts','Sideways'],
  LEAN_BEARISH:['Overvejende svagt','Leaning bearish'],
  LEAN_BULLISH:['Overvejende stærkt','Leaning bullish'],
  NO_EDGE:['Intet pålideligt signal','No reliable signal'],
  UNAVAILABLE:['Ingen aktuel vurdering','No current outlook']
 };
 const postures={
  HOLD:['Behold','Hold'],HOLD_WAIT:['Afvent','Wait'],WAIT:['Afvent','Wait'],
  ABSTAIN:['Ingen ny handling','No new action'],
  NO_EDGE:['Intet pålideligt signal','No reliable signal'],
  UNAVAILABLE:['Ingen aktuel vurdering','No current outlook']
 };
 const readable=(map,value,fallback)=>map[value]?.[lang==='en'?1:0]||fallback;
 const forwardArrow=eligible?directionVisual(direction,lang).arrow:'?';
 set('cn-horizon-13',eligible?
   forwardArrow+' '+readable(directions,direction,lang==='en'?'Not established':'Ikke fastlagt'):
   lang==='en'?'Awaiting updated data':'Afventer nye data');
 set('cn-horizon-13-posture',eligible?
   readable(postures,posture,lang==='en'?'See details':'Se detaljer'):'—');
 set('cn-horizon-13-label',lang==='en'?'Next 1–3 days':'De næste 1–3 dage');
 // Translate descriptive 12h data-time and directional states, without
 // inventing fresh momentum or changing the official action's authority.
 const nowLabels={
  BULLISH:['Stigende','Rising'],BEARISH:['Faldende','Falling'],
  NEUTRAL:['Ingen tydelig retning','No clear direction'],
  MIXED:['Blandet','Mixed'],UP:['Stigende','Rising'],DOWN:['Faldende','Falling'],
  SIDEWAYS:['Sideværts','Sideways'],
  UNCHANGED_NO_NEW_OBSERVATION:['Ingen ny måling','No new observation'],
  NO_NEW_OBSERVATION:['Ingen ny måling','No new observation'],
  OBSERVATION_DELAYED:['Måling forsinket','Observation delayed'],
  OBSERVATION_CLOCK_INVALID:['Ingen gyldig måling','No verified observation'],
  UNAVAILABLE:['Ingen måling','No reading']
 };
 const observed=eligible?observedMarketClock({compass:feeds.compass}):
  {state:'OBSERVATION_CLOCK_INVALID'};
 // The official 1–3d forecast remains source-valid even when the latest
 // completed public market candle has exceeded the independent 90min SLA.
 const nowState=observed.state==='FRESH_OBSERVATION'?
  feeds.compass.market_now?.directional_state:
  observed.state==='NO_NEW_PRICE_OBSERVATION'?'NO_NEW_OBSERVATION':
  observed.state;
 const nowArrow=eligible?directionVisual(nowState,lang).arrow:'?';
 set('premium-now-direction',nowLabels[nowState]?
   (nowArrow==='?'?'':nowArrow+' ')+nowLabels[nowState][lang==='en'?1:0]:
   (lang==='en'?'Awaiting valid data':'Afventer gyldige data'));
 const actionLabels={
  HOLD_WAIT:['Officiel vurdering · afvent','Official outlook · wait'],
  WAIT:['Officiel vurdering · afvent','Official outlook · wait'],
  HOLD:['Officiel vurdering · behold','Official outlook · hold'],
  ABSTAIN:['Ingen ny handling','No new action']
 };
 const officialAction=eligible?feeds.compass.action_now:null;
 set('premium-action-code',actionLabels[officialAction]?.[lang==='en'?1:0]||
   (lang==='en'?'No current verified action':'Ingen aktuel verificeret handling'));
 const adaptive=explainCurrentAction({latest:feeds?.latest,compass:feeds?.compass,view,lang});
 if(adaptive)set('premium-action-meaning',adaptive);
 const twelve=$('premium-now-direction')?.closest('.product-cell')?.querySelector('small');
 if(twelve)twelve.textContent=lang==='en'?
  'Now · latest observed price move':
  'Nu · seneste prisbevægelse';
}
function renderRiskQuick(){
 const en=document.documentElement.lang==='en';
 set('cn-risk-quick-label',en?'RISK OF A FURTHER DECLINE':
   'RISIKO FOR YDERLIGERE FALD');
 set('cn-risk-quick-meaning-label',en?'WHAT DOES IT MEAN?':'HVAD BETYDER DET?');
 set('cn-risk-quick-action-label',en?'HOW TO RESPOND':'SÅDAN FORHOLDER DU DIG');
 // Reuse the existing Official Kompas PRO source-bound result, including
 // its original 1–5 ordinal. This is not a new market classifier.
 const eligible=view?.compass?.state==='FRESH'&&
   view.compass.permit_path_live_gates===true&&
   feeds?.compass?.contract==='PUBLIC_COMPASS_PROJECTION_v1'&&
   feeds.compass.data_status==='OK'&&
   feeds.compass.compass_id===view.compass.compass_id&&
   feeds.compass.weekly_context?.status==='ALIGNED'&&
   feeds.compass.weekly_context?.forecast_week===view?.weekly?.forecast_week;
 const p=eligible?feeds.compass.protection_tracker:null;
 const sourceStage=eligible?$('pro-risk-stage')?.textContent:null;
 const stage=sourceStage&&/^[1-5]\/5 · /.test(sourceStage)?sourceStage:null;
 set('cn-risk-quick-state',stage||
   (en?'— / 5 · awaiting fresh data':'— / 5 · afventer nye data'));
 set('cn-risk-quick-note',en?'Ordinal risk level, not probability':
   'Risikoniveau, ikke sandsynlighed');
 const copy=p?.public_explanation;
 const bounded=copy?.contract==='CN_PUBLIC_PROTECTION_COPY_v1'&&
   copy?.action_authority===false&&copy?.risk_state===p?.pullback_risk_state&&
   copy?.forecast_week===feeds.compass.weekly_context.forecast_week&&
   typeof copy?.summary==='string'&&copy.summary.length<=240;
 // Danish text is a bounded localization of the already verified official
 // ordinal, never a translation of unverified free-form news or a new model.
 const daStage={
  NORMAL:'Ingen aktiv pullback-varsling. Det er ikke et selvstændigt købssignal.',
  BUILDING:'Pullback-risiko er under opbygning. Start og dybde er ikke dokumenteret.',
  ELEVATED:'Forhøjet risiko for et nyt fald. Start og dybde er ikke dokumenteret.',
  HIGH:'Officielt høj pullback-risiko. Gennemgå beredskab, ikke automatisk salg.',
  CONFIRMED:'Bekræftet officiel risikotilstand. Det er ikke en selvstændig salgstilladelse.'
 };
 set('cn-risk-more-title',en?'Evidence, protection and timing':'Forklaring, beskyttelse og timing');
 set('cn-risk-quick-meaning',stage&&bounded?
   (en?copy.summary:daStage[p.pullback_risk_state]):
   (en?'The current risk assessment is unavailable or lacks sufficient evidence.':
    'Der mangler en aktuel, tilstrækkeligt dokumenteret risikovurdering.'));
 set('cn-risk-quick-brief',stage&&bounded?
   (en?copy.summary:daStage[p.pullback_risk_state]):
   (en?'No current evidence-backed pullback classification.':
       'Ingen aktuel kildeverificeret pullback-vurdering.'));
 set('cn-risk-quick-action',stage?($('pro-guidance')?.textContent||
   (en?'Await the next verified decision':'Afvent næste verificerede handling')):
   (en?'Wait for an updated Compass before making a new decision':
    'Afvent opdateret Kompas før nye beslutninger'));
 const quality=stage?$('pro-risk-quality')?.textContent:null;
 const onset=stage?$('pro-onset-eta')?.textContent:null;
 set('cn-risk-quick-quality',(en?'Evidence quality: ':'Evidenskvalitet: ')+
   (quality||(en?'unknown':'ukendt')));
 set('cn-risk-quick-onset',(en?'Possible onset: ':'Mulig start: ')+
   (onset||(en?'not established':'ikke dokumenteret')));
 // Same official five source stages, never inferred from hourly prices.
 const source=$('premium-risk-steps'),target=$('cn-risk-quick-steps');
 if(source&&target){
  target.replaceChildren(...[...source.children].map(el=>{
   const copy=el.cloneNode(true);copy.removeAttribute('id');return copy;
  }));
 }
 const surface=$('compass-pro')?.querySelector('.cn-risk-quick');
 if(surface)surface.dataset.current=stage?'true':'false';
}
function renderReader(){
 const lang=document.documentElement.lang==='en'?'en':'da';
 const en=lang==='en';
 const reading=readHorizon({
   latest:feeds?.latest,compass:feeds?.compass,view,lang,id:selectedReaderHorizon
 });
 set('cn-reader-overline',en?'PUBLISHED MARKET INTERPRETATION':'OFFENTLIG MARKEDSFORTOLKNING');
 set('cn-reader-title',en?'What is Compass seeing ahead?':'Hvad viser Kompas fremad?');
 set('cn-reader-headnote',en?
   'Previously issued source analysis · not a fresh forecast':
   'Allerede udstedt kildeanalyse · ikke en ny prognose');
 for(const v of VIEWS){
   const b=document.querySelector('[data-cn-reader-horizon="'+v.id+'"]');
   if(b){b.textContent=en?v.en:v.da;
     b.setAttribute('aria-pressed',String(v.id===selectedReaderHorizon))}
 }
 set('cn-reader-direction',reading.direction);
 set('cn-reader-posture',reading.posture);
 set('cn-reader-analysis',reading.description);
 set('cn-reader-why',explainPosture(reading,lang));
 const riskHorizon=['NEXT_1_3D','NEXT_5_7D'].includes(selectedReaderHorizon);
 const watch=riskHorizon?sourceWatch({latest:feeds?.latest,compass:feeds?.compass,view,lang}):null;
 const watchAlreadyIntroduced=watch&&/^(?:Hold øje med|Watch\b)/i.test(watch.text);
 set('cn-reader-watch',watch?
   (watchAlreadyIntroduced?'':(en?'Watch for: ':'Hold øje med: '))+watch.text:'');
 set('cn-reader-language',reading.current&&!reading.translated?
   (en?'':'Oprindelig kildetekst på engelsk · ingen verificeret dansk oversættelse'):'');
 for(const lens of ['swing','hodl']){
   const b=document.querySelector('[data-cn-reader-lens="'+lens+'"]');
   if(b)b.setAttribute('aria-pressed',String(selectedReaderLens===lens));
 }
 const periods=$('cn-reader-title')?.closest('.cn-reader')?.querySelector('.cn-reader-periods');
 if(periods)periods.setAttribute('aria-label',en?'Select forecast horizon':'Vælg tidshorisont');
 const lenses=$('cn-reader-title')?.closest('.cn-reader')?.querySelector('.cn-reader-lens-buttons');
 if(lenses)lenses.setAttribute('aria-label',en?'Select investor perspective':'Vælg investeringsperspektiv');
 set('cn-reader-lens-note',lensContext(reading,selectedReaderLens,lang));
 set('cn-reader-source',reading.current?
   (en?'Published ':'Udstedt ')+time(reading.publishedAt)+' · '+reading.week+
   (en?' · checks public updates every 5 min':' · tjekker offentlige opdateringer hvert 5. minut'):
   (en?'No eligible current assessment · awaiting a new verified publication':
       'Ingen gyldig aktuel vurdering · afventer ny verificeret udgivelse'));
 set('cn-reader-glossary-title',en?'Understand the signals · 5 quick definitions':
   'Forstå signalerne · 5 korte forklaringer');
 const entries=en?[
  ['WAIT','No new trade is confirmed yet. Not a prediction of flat prices.'],
  ['MIXED','Evidence points both ways; not a 50/50 probability.'],
  ['HOLD','Wait for a change in the official stance; not a new buy.'],
  ['NO EDGE','No demonstrated predictive advantage.'],
  ['MISSING DATA','No current valid outlook; old signals are not current.']
 ]:[
  ['AFVENT','Nyt køb/salg er ikke bekræftet. Prisen kan stadig bevæge sig.'],
  ['BLANDET','Tegn peger begge veje; ikke en 50/50-sandsynlighed.'],
  ['HOLD','Afvent ændring i officiel vurdering; ikke et nyt køb.'],
  ['INGEN EDGE','Ingen dokumenteret prognosefordel.'],
  ['MANGLER DATA','Ingen gyldig aktuel vurdering; gamle signaler gælder ikke.']
 ];
 entries.forEach(([term,definition],index)=>{
   set('cn-reader-term-'+(index+1),term);
   set('cn-reader-definition-'+(index+1),definition);
 });
}

function renderAltMilestone(){
 const en=document.documentElement.lang==='en';
 const eligible=view?.path?.state==='SOURCE_BOUND'&&
  view?.compass?.state==='FRESH'&&
  view.compass.permit_path_live_gates===true&&
  view.path.source_issue===view?.weekly?.public_issue_number&&
  view.path.source_week===view?.weekly?.forecast_week&&
  view.path.source_identity===view.compass.compass_id;
 const p=eligible?view.path:null;
 set('cn-alt-milestone-title',en?'Altseason ignition':'Altseason begynder');
 set('cn-alt-milestone-subtitle',en?
  'Before small/micro acceleration · independently verified rotation required':
  'Før small/micro-acceleration · kræver verificeret rotation');
 set('cn-alt-milestone-eta-label',en?'Time to phase':'Tid til fase');
 // No structured authoritative future absolute timestamp exists in PATH v3.
 // A prose watch window is not a countdown, date or probability.
 set('cn-alt-milestone-eta',en?'No verified ETA':'Ingen verificeret ETA');
 const state=eligible&&p?.altseason?.status==='WATCH_ONLY'?
   (en?'Conditional watch · not confirmed':'Betinget watch · ikke bekræftet'):
   (en?'Awaiting verified transition':'Afventer verificeret overgang');
 set('cn-alt-milestone-state',state);
 const panel=$('cn-alt-milestone-title')?.closest('.cn-alt-milestone');
 if(panel)panel.dataset.state=eligible&&p.altseason?.status==='WATCH_ONLY'?
   'watch':'unverified';
}
function renderForward(){
 const lang=document.documentElement.lang==='en'?'en':'da';
 const say=(da,en)=>lang==='en'?en:da;
 const direction=value=>
  value==='UP'?say('OP','UP'):
  value==='DOWN'?say('NED','DOWN'):
  value==='MIXED'?say('BLANDET','MIXED'):
  value==='SIDEWAYS'?say('SIDEVÆRTS','SIDEWAYS'):
  value==='NO_EDGE'?say('INGEN PÅVIST EDGE','NO DEMONSTRATED EDGE'):'UNAVAILABLE';
 let out=null;
 try{
   const trace=sourceTrace(feeds?.latest,feeds?.compass,view);
   out=forwardOutlook(feeds?.latest,feeds?.compass,trace);
 }catch{out=null}
 set('cn-forward-source-status',out?.status||'UNAVAILABLE');
 set('cn-forward-week-direction',direction(out?.weekly?.direction));
 set('cn-forward-strategic-direction',direction(out?.strategic?.direction));
 set('cn-forward-week-copy',out?.weekly?.summary||
   say('Ingen kvalificeret 2–3-ugers vurdering udstedt.','No eligible 2–3 week outlook issued.'));
 set('cn-forward-strategic-copy',out?.strategic?.summary||
   say('Ingen kildeverificeret strategisk vurdering.','No source-verified strategic outlook.'));
 set('cn-forward-issued',out?.strategic?.issued_at_utc?time(out.strategic.issued_at_utc):'—');
 set('cn-forward-assets',out?.strategic?.available?
   'BTC '+direction(out.strategic.btc_direction)+' / ETH '+
   direction(out.strategic.eth_direction)+' · '+safe(out.strategic.confidence):'—');
 set('cn-forward-path',out?.strategic?.expected_path||
   say('Ingen understøttet forventet markedssti.','No supported expected market path.'));
 const reset=id=>{const e=$(id);if(e)e.replaceChildren();return e};
 const scenarios=reset('cn-forward-scenarios');
 if(scenarios)for(const item of (out?.strategic?.scenarios||[])){
   const article=document.createElement('article');
   const name=document.createElement('strong');name.textContent=safe(item.label);
   const desc=document.createElement('p');desc.textContent=safe(item.thesis);
   article.append(name,desc);scenarios.append(article);
 }
 const falsifiers=reset('cn-forward-falsifiers');
 if(falsifiers&&(out?.strategic?.falsifiers||[]).length){
   const name=document.createElement('strong');
   name.textContent=say('Hvad kan modbevise vurderingen?','What would falsify this outlook?');
   const list=document.createElement('ul');
   for(const value of out.strategic.falsifiers){
     const li=document.createElement('li');li.textContent=safe(value);list.append(li)
   }
   falsifiers.append(name,list);
 }
 const i18n={
  da:{title:'Længere udsyn · kildevurdering',detail:'Scenarier og kildebevis',
      caveat:'Kun udstedte, kildeverificerede tidshorisonter. Ingen garanteret kurssti.',
      reentry:'Genkøb · officiel status'},
  en:{title:'Longer outlook · source context',detail:'Scenarios and evidence',
      caveat:'Only originally issued, source-verified horizons. No guaranteed price path.',
      reentry:'Re-entry · official status'}
 }[lang];
 const title=$('cn-forward-title');if(title)title.textContent=i18n.title;
 const details=$('compass-pro')?.querySelector('.cn-forward-details summary');
 if(details)details.textContent=i18n.detail;
 const caveat=$('compass-pro')?.querySelector('.cn-forward-disclaimer');
 if(caveat)caveat.textContent=i18n.caveat;
 set('pro-reentry-heading',i18n.reentry);
}
function renderReentry(){
 const eligible=view?.compass?.state==='FRESH'&&
  view?.compass?.permit_path_live_gates===true&&
  feeds?.compass?.contract==='PUBLIC_COMPASS_PROJECTION_v1'&&
  feeds?.compass?.data_status==='OK';
 const source=eligible?feeds.compass.protection_tracker:null;
 set('pro-reentry-state',source?safe(source.reentry_state):'UNAVAILABLE');
 set('pro-reentry-note',source&&typeof source.reentry_message==='string'?
  source.reentry_message:t('Ingen kildeverificeret genkøbsstatus. Risiko er ikke automatisk et købssignal.',
   'No source-verified re-entry status. Risk alone never authorizes buying.'));
}
function sourceRows(){
 let trace=null;
 try{trace=sourceTrace(feeds?.latest,feeds?.compass,view)}catch{trace=null}
 const status=trace?.reason==='OFFICIAL_NOT_CURRENT_CONTEXT_ONLY'?
  t('Officiel handling ikke aktuel · kontekst kan vises','Official action not current · context only'):
  trace?.status==='COMPLETE'?t('Krævede kildeled verificeret','Required sources verified'):
  trace?.status==='PARTIAL_OR_DEGRADED'?t('Delvist dokumenteret grundlag','Partial source evidence'):
  t('Kildestatus utilgængelig','Source status unavailable');
 set('source-trace-status',status);
 const lang=document.documentElement.lang==='en'?'en':'da';
 const row=(target,values)=>{
  const el=$(target);if(!el)return;
  const tr=document.createElement('tr');
  for(const v of values)cell(tr,String(v??'—'));
  el.append(tr);
 };
 const long=$('long-horizon-body');if(long)long.replaceChildren();
 const source=$('source-trace-body');if(source)source.replaceChildren();
 const periods={'2_3w':'2–3w','21_30d':'21–30d','4_8w':'4–8w'};
 for(const item of (trace?.long_horizons||[])){
  const owner=item.owner==='CYCLE_NAVIGATOR_WEEKLY'?
    t('Cycle Navigator · frossen uge','Cycle Navigator · frozen week'):
    item.owner==='CYCLE_NAVIGATOR_STRATEGIC_CONTEXT'?
      t('Cycle Navigator · strategisk kontekst','Cycle Navigator · strategic context'):
      t('Strategisk forskning · ikke-bindende','Strategic research · nonbinding');
  row('long-horizon-body',[periods[item.id]||safe(item.id),displayLongDirection(item,lang),owner]);
 }
 for(const item of (trace?.sources||[]))row('source-trace-body',[safe(item.name),displayPublicStatus(item.status,lang)]);
 const title=$('source-trace-title');
 if(title)title.textContent=lang==='da'?'Længere tidshorisonter · kildekontekst':'Longer horizons · source context';
 const sourceSummary=$('compass-pro')?.querySelector('.source-trace-details > summary');
 if(sourceSummary)sourceSummary.textContent=lang==='da'?
  'Se kildeled og deres status':'Inspect source layers and their status';
}
function mondayReadback(){
 let m=null;
 try{m=mondayContext(feeds?.latest,feeds?.compass,view)}catch{m=null}
 const lang=document.documentElement.lang==='en'?'en':'da';
 let labels=null;try{if(m)labels=mondayLabels(m,lang)}catch{}
 const valid=m?.source_state==='SOURCE_ALIGNED';
 set('monday-reading',labels?.title||displayPublicStatus('UNAVAILABLE',lang));
 set('monday-explanation',labels?.evidence||t('Ugens kildegrundlag mangler','Weekly source unavailable'));
 set('monday-week',valid?m.completed_week:'—');
 set('monday-source',valid?t('Verificeret ugegrundlag','Verified weekly source'):
   t('Ugegrundlag ikke verificeret','Weekly source unverified'));
 set('monday-source-explanation',t('Ugeanalyse er kontekst, ikke en ny handelstilladelse.',
   'Weekly analysis is context, not new trade permission.'));
 set('monday-scorecard',displayPublicStatus(valid?m.scorecard_status:'UNAVAILABLE',lang));
 set('monday-translation',displayPublicStatus(valid?m.operational_translation_status:'UNAVAILABLE',lang));
 set('monday-api',valid&&m.api_analysis_status==='AVAILABLE_SHADOW_ONLY'?
  t('Research tilgængelig · ikke-bindende','Research available · nonbinding'):displayPublicStatus('UNAVAILABLE',lang));
 const title=$('monday-title');
 if(title)title.textContent=t('Mandagens dokumenterede ugegrundlag','Monday’s verified weekly context');
}
function paint(){
 const lang=document.documentElement.lang==='en'?'en':'da';
 try{view=feeds?inspectOfficialPublicFeeds(feeds.latest,feeds.compass,{lang}):null}
 catch{view=null}
 // Official source gate remains upstream. An expired issuer can never be
 // refreshed via a newer Pages bundle timestamp or cached prior DOM text.
 renderProductExperience(view,feeds,lang);
 renderQuickDecision();
 renderRiskQuick();
 renderOverview();
 renderReader();
 renderAltMilestone();
 horizons();
 renderForward();
 renderReentry();
 sourceRows();
 mondayReadback();
 const c=view?.compass,w=view?.weekly;
 const fresh=c?.state==='FRESH'&&c?.permit_path_live_gates===true;
 const weekly=w?.state==='DEGRADED'?t(' · Ugens datagrundlag er ufuldstændigt',' · Weekly data is incomplete'):
   w?.state==='OK'?'':t(' · Ugens data er ikke tilgængelige',' · Weekly data is unavailable');
 const expires=feeds?.compass?.full_stack?.official_freshness?.valid_until_utc;
 const deadline=Date.parse(expires);
 const validUntil=Number.isFinite(deadline)?time(expires):'—';
 const expired=!fresh&&expiredOfficial({compass:feeds?.compass,view});
 const expiredTime=Number.isFinite(deadline)?new Date(deadline).toLocaleString(
   lang==='en'?'en-GB':'da-DK',
   {timeZone:'Europe/Copenhagen',day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'}
 )+(lang==='en'?' (Copenhagen time)':' (dansk tid)'):'—';
 const last=feeds?.compass?.issued_at_utc;
 const sourceAgeAtIssue=originalSourceAgeLabel(feeds?.compass,{lang,valid:fresh});
 set('pro-source-status',failed?t('Indlæsning mislykkedes · ingen aktuel handling','Source fetch failed · no current action'):
   fresh?t('Aktuel vurdering · opdateret ','Current verified outlook · updated ')+time(last)+
         t(' · gyldig til ',' · valid until ')+validUntil+weekly+sourceAgeAtIssue:
   expired?t('Ingen aktuel vurdering: Seneste Kompas-vurdering udløb ','No current outlook: last Compass issue expired ')+expiredTime+
     t('. Ingen aktuel handling. Afventer ny verificeret udgivelse.','. No current action. Awaiting a new verified issue.')+weekly:
   t('Ingen aktuel vurdering: data er for gamle, mangler eller passer ikke til denne uge','No current outlook: data are too old, missing or do not match this week')+weekly);
 const gate=fresh&&view?.path?.state==='SOURCE_BOUND'?safe(view.path.next_gate):'UNAVAILABLE';
 set('pro-next-gate',t('Næste bekræftelse: ','Next confirmation: ')+(gate==='UNAVAILABLE'?
   t('Afventer pålidelige data','Awaiting reliable data'):gate));
 const root=$('compass-pro');if(root){
  root.dataset.sourceCurrent=fresh?'true':'false';
  root.dataset.sourceState=fresh?'FRESH':expired?'EXPIRED':'UNAVAILABLE';
  root.dataset.weeklyHealth=w?.state||'UNAVAILABLE';
 }
 const proNav=document.querySelector('[data-premium-nav="compass"]');
 if(proNav)proNav.textContent=lang==='en'?'Compass PRO':'Kompas PRO';
 const heading=$('pro-heading');if(heading)heading.textContent=lang==='en'?'Compass PRO':'Kompas PRO';
 const intro=$('compass-pro')?.querySelector('.cn-pro-intro > p');
 if(intro)intro.textContent=lang==='en'?
  'Current market direction, risk and what could change the outlook. Missing or outdated data are clearly marked.':
  'Aktuel markedsretning, risiko og hvad der kan ændre udsynet. Manglende eller gamle data vises tydeligt.';
 // Only neutral presentation labels; all action, SELL, risk, state, price and
 // source-provenance labels remain produced by existing PRO/source modules.
 const copy=lang==='en'?{
  risk:'Advanced · detailed risk and sources',
  horizon:'Time horizons',
  owner:'Official Compass only',
  time:'Horizon',direction:'Direction',action:'Source posture'
 }:{
  risk:'Avanceret · detaljer, risici og kilder',
  horizon:'Tidshorisonter',
  owner:'Kun officielt Kompas',
  time:'Tid',direction:'Retning',action:'Kildens position'
 };
 const summary=document.querySelector('#compass-pro .cn-pro-more > summary');
 if(summary)summary.textContent=copy.risk;
 const title=$('pro-horizon-heading');if(title)title.textContent=copy.horizon;
 set('pro-horizon-owner',copy.owner);
 const header=$('pro-horizon-table')?.querySelectorAll('th');
 if(header?.length===3){header[0].textContent=copy.time;header[1].textContent=copy.direction;header[2].textContent=copy.action}
}
async function load(){
 if(inflight)return;
 inflight=true;
 const my=++request;
 const controller=new AbortController();
 const timeout=setTimeout(()=>controller.abort(),10000);
 try{
  const [latest,compass]=await Promise.all(assets.map(async url=>{
   const r=await fetch(url,{cache:'no-store',redirect:'error',credentials:'omit',signal:controller.signal});
   if(!r.ok)throw Error('CN_OFFICIAL_PUBLIC_SOURCE_UNAVAILABLE');
   return r.json();
  }));
  if(my===request){feeds={latest,compass};failed=false}
 }catch{
  if(my===request){feeds=null;failed=true}
 }finally{
  clearTimeout(timeout);inflight=false;paint();
 }
}
// A trader may switch lens BETWEEN periodic clock checks. Re-evaluate the
// official source expiry synchronously on every lens interaction, never
// replay a cached 'FRESH' action after its owner validity deadline.
initProductExperience(()=>{
 const lang=document.documentElement.lang==='en'?'en':'da';
 try{view=feeds?inspectOfficialPublicFeeds(feeds.latest,feeds.compass,{lang}):null}
 catch{view=null}
 return {view,feeds,lang};
});
// Keep headline source banner/gate synchronized on a trader-lens click.
// initProductExperience already evaluates the eligibility for the action;
// this final paint also invalidates the visible SOURCE CURRENT badge and gate.
// The UI changes what is READ, never what the original market owner issues.
document.querySelectorAll('[data-cn-reader-horizon]').forEach(button=>
 button.addEventListener('click',()=>{
   const id=button.getAttribute('data-cn-reader-horizon');
   if(VIEWS.some(v=>v.id===id)){selectedReaderHorizon=id;paint()}
 }));
document.querySelectorAll('[data-cn-reader-lens]').forEach(button=>
 button.addEventListener('click',()=>{
   const lens=button.getAttribute('data-cn-reader-lens');
   if(lens==='swing'||lens==='hodl'){selectedReaderLens=lens;paint()}
 }));
document.querySelectorAll('[data-investor-lens]').forEach(button=>
 button.addEventListener('click',paint));
document.addEventListener('cn:languagechange',paint);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)load()});
window.addEventListener('focus',()=>{if(!document.hidden)load()});
const clock=setInterval(paint,CLOCK_RECHECK_MS);
const refresh=setInterval(()=>{if(!document.hidden)load()},SOURCE_RECHECK_MS);
window.addEventListener('pagehide',()=>{clearInterval(clock);clearInterval(refresh)});
paint();
load();
