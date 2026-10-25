/**
 * Minimal Official Compass & PATH: source-only UI on isolated NEXT candidate.
 * Never an action issuer or market phase estimator.
 */
import {readOfficialCompassPath} from './official-compass-path.mjs';
const $=id=>document.getElementById(id);
const dataUrl=new URL('../../data/compass.json',import.meta.url);
const latestUrl=new URL('../../data/latest.json',import.meta.url);
const lang=(da,en)=>document.documentElement.lang==='en'?en:da;
let currentModel=null,sourceCompass=null,sourceLatest=null,expiryTimer=null,requestGeneration=0;
const SOURCE_RECHECK_MS=5*60*1000;
const DA_PHASES={
 'BTC leadership':'BTC fører',
 'ETH leadership':'ETH fører',
 'Large + Mid rotation':'Large- og midcap-rotation',
 'Altseason ignition':'Altseason starter',
 'Micro acceleration':'Microcaps accelererer',
 'Broad altseason':'Bred altseason',
 'Mania / euphoria':'Mani / eufori',
 'Distribution':'Distribution',
 'Exit / protection':'Exit / beskyttelse',
 'Cooldown / re-entry':'Afkøling / genkøb'
};
const DA_CODES={UP:'OP',DOWN:'NED',MIXED:'BLANDET',UNAVAILABLE:'UTILGÆNGELIG',
 HOLD:'BEHOLD',WAIT:'AFVENT',HARD_WAIT:'STRIKT AFVENT',BUY:'KØB',SELL:'SÆLG'};
const displayCode=code=>document.documentElement.lang==='en'?code:(DA_CODES[code]||code);
function displayUtc(value){
 const date=new Date(value);
 if(!Number.isFinite(date.getTime()))return '—';
 return new Intl.DateTimeFormat(document.documentElement.lang==='en'?'en-GB':'da-DK',{
  timeZone:'UTC',day:'numeric',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'
 }).format(date)+' UTC';
}
function make(tag,cls,text){const el=document.createElement(tag);if(cls)el.className=cls;
 if(text!==undefined)el.textContent=String(text);return el}
function clearUnissued(){
 $('official-product-pilot').dataset.sourceState='unavailable';
 $('official-pilot-status').textContent=lang('KILDE MANGLER','SOURCE UNAVAILABLE');
 $('official-pilot-action').textContent='—';$('official-pilot-action-note').textContent=
  lang('Ingen verificeret officiel handling.','No verified Official action.');
 $('official-pilot-horizons').replaceChildren();
 $('official-pilot-rotation').replaceChildren();
 $('official-pilot-path').replaceChildren();
 $('official-pilot-phase-note').textContent=lang('Ingen verificeret aktuel PATH-position.',
  'No verified current PATH position.');
 $('official-pilot-gate').textContent='';
 $('official-pilot-bias').textContent='—';
 $('official-pilot-bias-note').textContent=lang(
  'Ingen verificeret Bull/Bear-evidens eller gyldighed.',
  'No verified Bull/Bear evidence or validity.');
}

function localizeCompass(){
 const en=document.documentElement.lang==='en';
 for(const [selector,da,english] of [
  ['.official-pilot-eyebrow','KOMPAS / KILDEAUTORITET','COMPASS / SOURCE AUTHORITY'],
  ['.official-pilot-action > span','OFFICIEL HANDLING','OFFICIAL ACTION'],
  ['.official-pilot-state > span','MARKED / BULL · BEAR','MARKET / BULL · BEAR']
 ]){const n=document.querySelector(selector);if(n)n.textContent=en?english:da}
 $('official-product-pilot').setAttribute('aria-label',en?'Official Compass':'Officielt Kompas');
 $('official-pilot-horizons').setAttribute('aria-label',en?'Five Official horizons':'Fem officielle horisonter');
 const heading=document.querySelector('.official-pilot-head h2');
 if(heading)heading.textContent=en?'Decision compass.':'Handlingskompas.';
 const subtitle=document.querySelector('.official-pilot-head p');
 if(subtitle)subtitle.textContent=en?'Source-issued actions and horizons.':
  'Kildeudstedte handlinger og horisonter.';
 const subs=document.querySelectorAll('.official-pilot-subhead');
 if(subs[0]){
  subs[0].querySelector('h3').textContent=en?'Capital rotation':'Kapitalrotation';
  subs[0].querySelector('p').textContent=en?'Seven source-issued tiers, not trading instructions.':
   'Syv kildeudstedte trin, ikke en købsanvisning.';
 }
 if(subs[1])subs[1].querySelector('h3').textContent=en?'PATH · Ten cycle phases':'PATH · Cyklens ti faser';
}

function paint(model){
 localizeCompass();
 if(model.status==='UNAVAILABLE'){clearUnissued();return}
 const now=model.official_action_current;
 $('official-product-pilot').dataset.sourceState=now?'current':'expired';
 $('official-pilot-status').textContent=now?
  lang('OFFICIEL KILDE · AKTUEL','OFFICIAL SOURCE · CURRENT'):
  lang('UDLØBET · HISTORIK','EXPIRED · HISTORY');
 const code=model.official_action;
 const da={HOLD_WAIT:'AFVENT',HARD_WAIT:'AFVENT',HOLD:'HOLD',WAIT:'AFVENT',
  BUY:'KØB',SELL:'SÆLG',UNAVAILABLE:'UTILGÆNGELIG'};
 const en={HOLD_WAIT:'WAIT',HARD_WAIT:'WAIT',HOLD:'HOLD',WAIT:'WAIT',
  BUY:'BUY',SELL:'SELL',UNAVAILABLE:'UNAVAILABLE'};
 $('official-pilot-action').textContent=now&&model.action_allowed_to_display_as_current?
  lang(da[code]||code,en[code]||code):'—';
 $('official-pilot-action-note').textContent=now?
  lang('Kildeudstedt '+displayUtc(model.issued_at_utc)+' · '+code,
  'Source issued '+displayUtc(model.issued_at_utc)+' · '+code):
  lang('Historisk '+code+' · udløb '+displayUtc(model.valid_until_utc),
       'Historical '+code+' · expired '+displayUtc(model.valid_until_utc));
 const g=now?model.bull_bear?.['1_3d']:null;
 $('official-pilot-bias').textContent=g?
  g.bull+' / '+g.bear:'—';
 $('official-pilot-bias-note').textContent=g?lang(
  'Kildeudstedt evidensbalance, ikke sandsynlighed · gyldig til '+displayUtc(model.valid_until_utc),
  'Source-issued evidence balance, not probability · valid until '+displayUtc(model.valid_until_utc)):lang(
  'Ingen aktuel verificeret Bull/Bear-evidens.',
  'No current verified Bull/Bear evidence.');
 const h=$('official-pilot-horizons');h.replaceChildren();
 const translations={NEXT_12H:'12H',NEXT_1_3D:'1–3D',NEXT_5_7D:'5–7D',
 NEXT_2_3W:lang('2–3U','2–3W'),CYCLE_ALTCOINS_3_8W:lang('3–8U','3–8W')};
 for(const w of model.horizons){
  const c=make('article','official-pilot-horizon');
  c.dataset.sourceState=now?'current':'expired';
  c.append(make('span','official-pilot-horizon-label',translations[w.id]||w.id));
  const direction=make('strong','official-pilot-horizon-direction',
   now?displayCode(w.direction||'UNAVAILABLE'):'—');
  direction.title=now?(w.direction||'UNAVAILABLE'):'EXPIRED';
  c.append(direction);
  const action=make('small','official-pilot-horizon-posture',
   now?displayCode(w.action_posture||'UNAVAILABLE'):lang('UDLØBET','EXPIRED'));
  action.title=now?(w.action_posture||'UNAVAILABLE'):'EXPIRED';
  c.append(action);
  // Native disclosure exposes the exact issuer's scenario, not a browser prediction.
  if(now&&typeof w.description==='string'&&w.description.trim()){
   const detail=make('details','official-pilot-horizon-context');
   detail.append(make('summary','',lang('Læs kildegrundlag','Source detail')));
   detail.append(make('p','',w.description));
   c.append(detail);
  }
  h.append(c);
 }
 const rotation=$('official-pilot-rotation');rotation.replaceChildren();
 for(const segment of model.capitalization_ladder){
  const item=make('div','official-pilot-tier');
  const labels={LARGE_CAPS:'LARGE',MID_CAPS:'MID',SMALL_CAPS:'SMALL',MICROCAPS:'MICRO'};
  item.append(make('strong','',labels[segment.segment]||segment.segment));
  const status=make('small','',now?displayCode(segment.status||'—'):'—');
  status.title=now?(segment.status||'—'):'EXPIRED';item.append(status);
  rotation.append(item);
 }
 const steps=$('official-pilot-path');steps.replaceChildren();
 for(const phrase of model.path_phases){
  const el=make('li','',lang(DA_PHASES[phrase]||phrase,phrase));
  if(model.path_current_phase===phrase)el.setAttribute('aria-current','step');
  steps.append(el);
 }
 $('official-pilot-phase-note').textContent=model.rotation_confirmed?
  lang('Kildebekræftet fase: '+model.path_current_phase,'Source-confirmed phase: '+model.path_current_phase):
  model.path_weekly_alignment!=='ALIGNED'?
  lang('Ugentlig kildebinding afventer. Ingen blå positionsmarkør.','Weekly source alignment pending. No blue position marker.'):
  lang('Aktuel fase ikke fastslået. Ingen blå positionsmarkør.','Current phase not established. No blue position marker.');
 $('official-pilot-gate').textContent=model.path_next_gate?
  lang('NÆSTE KILDEGATE · ','NEXT SOURCE GATE · ')+model.path_next_gate:
  lang('Ingen understøttet næste fase eller ETA.','No supported next phase or ETA.');
}
async function fetchJson(url){
 const x=await fetch(url,{cache:'no-store',credentials:'omit',redirect:'error',
 signal:AbortSignal.timeout(12000)});
 if(!x.ok)throw Error('PUBLIC_FEED_HTTP_'+x.status);
 return x.json();
}
function invalidateCompass(){
 currentModel=null;sourceCompass=null;sourceLatest=null;
 if(expiryTimer!==null){clearTimeout(expiryTimer);expiryTimer=null;}
 clearUnissued();
}
function repaintFromCurrentClock(){
 // Always re-derive Official freshness; NEVER reuse a cached current flag.
 if(!sourceCompass||!sourceLatest){invalidateCompass();localizeCompass();return}
 currentModel=readOfficialCompassPath(sourceCompass,sourceLatest,{now_utc:new Date().toISOString()});
 paint(currentModel);
}
async function init({background=false}={}){
 const request=++requestGeneration;
 // Immediately invalidate old actions while new evidence is in flight.
 if(!background)invalidateCompass();
 try{
  const [compass,latest]=await Promise.all([fetchJson(dataUrl),fetchJson(latestUrl)]);
  if(request!==requestGeneration)return; // slower prior request cannot resurrect an old source
  if(expiryTimer!==null){clearTimeout(expiryTimer);expiryTimer=null;}
  sourceCompass=compass;sourceLatest=latest;
  repaintFromCurrentClock();
  if(currentModel?.status==='SOURCE_CURRENT'){
   const ms=Date.parse(currentModel.valid_until_utc)-Date.now()+150;
   if(ms>0&&ms<2147483000)expiryTimer=setTimeout(()=>{
     if(request!==requestGeneration)return;
     repaintFromCurrentClock();
   },ms);
  }
 }catch{
  if(request===requestGeneration)invalidateCompass(); // never retain a previously current model
 }
}
init();

document.addEventListener('cn:languagechange',repaintFromCurrentClock);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)init()});
const sourceRecheck=setInterval(()=>{if(!document.hidden)init({background:true})},SOURCE_RECHECK_MS);
window.addEventListener('pagehide',()=>clearInterval(sourceRecheck));
