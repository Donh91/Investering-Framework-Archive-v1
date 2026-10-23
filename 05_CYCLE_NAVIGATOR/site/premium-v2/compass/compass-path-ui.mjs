/**
 * Minimal Official Compass & PATH: source-only UI on isolated NEXT candidate.
 * Never an action issuer or market phase estimator.
 */
import {readOfficialCompassPath} from './official-compass-path.mjs';
const $=id=>document.getElementById(id);
const dataUrl=new URL('../../data/compass.json',import.meta.url);
const latestUrl=new URL('../../data/latest.json',import.meta.url);
const lang=(da,en)=>document.documentElement.lang==='en'?en:da;
let currentModel=null,sourceCompass=null,sourceLatest=null,expiryTimer=null;
function make(tag,cls,text){const el=document.createElement(tag);if(cls)el.className=cls;
 if(text!==undefined)el.textContent=String(text);return el}
function clearUnissued(){
 $('official-pilot-status').textContent=lang('KILDE MANGLER','SOURCE UNAVAILABLE');
 $('official-pilot-action').textContent='—';$('official-pilot-action-note').textContent=
  lang('Ingen verificeret officiel handling.','No verified Official action.');
 $('official-pilot-horizons').replaceChildren();
 $('official-pilot-rotation').replaceChildren();
 $('official-pilot-path').replaceChildren();
 $('official-pilot-phase-note').textContent=lang('Ingen verificeret aktuel PATH-position.',
  'No verified current PATH position.');
 $('official-pilot-gate').textContent='';
}

function localizeCompass(){
 const en=document.documentElement.lang==='en';
 const heading=document.querySelector('.official-pilot-head h2');
 if(heading)heading.textContent=en?'Decision compass.':'Handlingskompas.';
 const subtitle=document.querySelector('.official-pilot-head p');
 if(subtitle)subtitle.textContent=en?'Official source only. No new action inference.':
  'Official-first. Ingen nye køb-/salgsbeslutninger fra denne visning.';
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
 $('official-pilot-status').textContent=now?
  lang('OFFICIEL KILDE · AKTUEL','OFFICIAL SOURCE · CURRENT'):
  lang('UDLØBET · HISTORIK','EXPIRED · HISTORY');
 const code=model.official_action;
 const da={HOLD_WAIT:'AFVENT',HARD_WAIT:'AFVENT',HOLD:'HOLD',WAIT:'AFVENT',
  BUY:'KØB',SELL:'SÆLG',UNAVAILABLE:'UTILGÆNGELIG'};
 const en={HOLD_WAIT:'WAIT',HARD_WAIT:'WAIT',HOLD:'HOLD',WAIT:'WAIT',
  BUY:'BUY',SELL:'SELL',UNAVAILABLE:'UNAVAILABLE'};
 $('official-pilot-action').textContent=now?(lang(da[code]||code,en[code]||code)):'—';
 $('official-pilot-action-note').textContent=now?
  lang('Original officiel handling: '+code+'. Kilde '+model.issued_at_utc,
  'Original Official action: '+code+'. Issued '+model.issued_at_utc):
  lang('Historisk '+code+' (IKKE aktuelt). Gyldig til '+model.valid_until_utc,
       'Historical '+code+' (NOT current). Valid until '+model.valid_until_utc);
 const g=model.bull_bear?.['1_3d'];
 $('official-pilot-bias').textContent=g?
  g.bull+' / '+g.bear:'—';
 $('official-pilot-bias-note').textContent=lang(
  'BULL / BEAR, kildeudstedt evidensbalance, ikke sandsynlighed.',
  'BULL / BEAR, source-issued evidence balance, not probability.');
 const h=$('official-pilot-horizons');h.replaceChildren();
 const translations={NEXT_12H:'12H',NEXT_1_3D:'1–3D',NEXT_5_7D:'5–7D',
 NEXT_2_3W:'2–3U',CYCLE_ALTCOINS_3_8W:'3–8U'};
 for(const w of model.horizons){
  const c=make('article','official-pilot-horizon');
  c.append(make('span','',translations[w.id]||w.id));
  c.append(make('strong','',w.direction||'UNAVAILABLE'));
  c.append(make('small','',w.action_posture||'—'));h.append(c);
 }
 const rotation=$('official-pilot-rotation');rotation.replaceChildren();
 for(const segment of model.capitalization_ladder){
  const item=make('div','official-pilot-tier');
  const labels={LARGE_CAPS:'LARGE',MID_CAPS:'MID',SMALL_CAPS:'SMALL',MICROCAPS:'MICRO'};
  item.append(make('strong','',labels[segment.segment]||segment.segment));
  item.append(make('small','',segment.status||'—'));
  rotation.append(item);
 }
 const steps=$('official-pilot-path');steps.replaceChildren();
 for(const phrase of model.path_phases){
  const el=make('li','',phrase);
  if(model.path_current_phase===phrase)el.setAttribute('aria-current','step');
  steps.append(el);
 }
 $('official-pilot-phase-note').textContent=model.rotation_confirmed?
  lang('Kildebekræftet fase: '+model.path_current_phase,'Source-confirmed phase: '+model.path_current_phase):
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
async function init(){
 clearUnissued();
 if(expiryTimer!==null){clearTimeout(expiryTimer);expiryTimer=null;}
 try{
  const [compass,latest]=await Promise.all([fetchJson(dataUrl),fetchJson(latestUrl)]);
  sourceCompass=compass;sourceLatest=latest;
  currentModel=readOfficialCompassPath(compass,latest,{now_utc:new Date().toISOString()});
  paint(currentModel);
  if(currentModel.status==='SOURCE_CURRENT'){
   const ms=Date.parse(currentModel.valid_until_utc)-Date.now()+150;
   if(ms>0&&ms<2147483000)expiryTimer=setTimeout(()=>{
     currentModel=readOfficialCompassPath(sourceCompass,sourceLatest,{now_utc:new Date().toISOString()});
     paint(currentModel);
   },ms);
  }
 }catch{clearUnissued()}
}
init();

document.addEventListener('cn:languagechange',()=>{if(currentModel)paint(currentModel);else localizeCompass()});
document.addEventListener('visibilitychange',()=>{if(!document.hidden)init()});
