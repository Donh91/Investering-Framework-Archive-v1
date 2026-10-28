/**
 * SITE #1578 · Single-root Kompas PRO readback, not a new action issuer.
 * Reuses existing source-verification and PRO rendering from /vnext-live/.
 * No separate model, new forecast, execution, market authority or API.
 */
import '../vnext-live/premium-experience.css';
import {inspectOfficialPublicFeeds} from '../vnext-live/official-feed-parity.mjs';
import {sourceTrace} from '../vnext-live/source-trace.mjs';
import {mondayContext,mondayLabels} from '../vnext-live/monday-public-bridge.mjs';
import {forwardOutlook} from '../vnext-live/forward-outlook.mjs';
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
  cell(r,eligible?safe(key==='NEXT_12H'?feeds.compass.market_now?.directional_state:v?.expected_direction):'—');
  cell(r,eligible?safe(v?.action_posture):'—');
  body.append(r);
 }
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
  row('long-horizon-body',[periods[item.id]||safe(item.id),safe(item.direction),owner]);
 }
 for(const item of (trace?.sources||[]))row('source-trace-body',[safe(item.name),safe(item.status)]);
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
 set('monday-reading',labels?.title||'UNAVAILABLE');
 set('monday-explanation',labels?.evidence||t('Ugens kildegrundlag mangler','Weekly source unavailable'));
 set('monday-week',valid?m.completed_week:'—');
 set('monday-source',valid?t('Verificeret ugegrundlag','Verified weekly source'):
   t('Ugegrundlag ikke verificeret','Weekly source unverified'));
 set('monday-source-explanation',t('Ugeanalyse er kontekst, ikke en ny handelstilladelse.',
   'Weekly analysis is context, not new trade permission.'));
 set('monday-scorecard',valid?m.scorecard_status:'UNAVAILABLE');
 set('monday-translation',valid?m.operational_translation_status:'UNAVAILABLE');
 set('monday-api',valid&&m.api_analysis_status==='AVAILABLE_SHADOW_ONLY'?
  t('Research tilgængelig · ikke-bindende','Research available · nonbinding'):'UNAVAILABLE');
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
 horizons();
 renderForward();
 renderReentry();
 sourceRows();
 mondayReadback();
 const c=view?.compass,w=view?.weekly;
 const fresh=c?.state==='FRESH'&&c?.permit_path_live_gates===true;
 const weekly=w?.state==='DEGRADED'?t(' · UGEKILDE: BEGRÆNSET DÆKNING',' · WEEKLY SOURCE: LIMITED COVERAGE'):
   w?.state==='OK'?'':t(' · UGEKILDE UTILGÆNGELIG',' · WEEKLY SOURCE UNAVAILABLE');
 const expires=feeds?.compass?.full_stack?.official_freshness?.valid_until_utc;
 const deadline=Date.parse(expires);
 const validUntil=Number.isFinite(deadline)?time(expires):'—';
 const last=feeds?.compass?.issued_at_utc;
 set('pro-source-status',failed?t('Indlæsning mislykkedes · ingen aktuel handling','Source fetch failed · no current action'):
   fresh?t('Kildeverificeret handling · udstedt ','Source-verified action · issued ')+time(last)+
         t(' · gyldig til ',' · valid until ')+validUntil+weekly:
   t('Ingen gyldig aktuel handling · kilde udløbet, mangler eller matcher ikke uge','No eligible current action · source expired, missing or wrong week')+weekly);
 const gate=fresh&&view?.path?.state==='SOURCE_BOUND'?safe(view.path.next_gate):'UNAVAILABLE';
 set('pro-next-gate',t('Næste bekræftelse: ','Next confirmation: ')+(gate==='UNAVAILABLE'?
   t('Afventer kildeverificeret betingelse','Awaiting source-verified condition'):gate));
 const root=$('compass-pro');if(root){
  root.dataset.sourceCurrent=fresh?'true':'false';
  root.dataset.weeklyHealth=w?.state||'UNAVAILABLE';
 }
 const proNav=document.querySelector('[data-premium-nav="compass"]');
 if(proNav)proNav.textContent=lang==='en'?'Compass PRO':'Kompas PRO';
 // Only neutral presentation labels; all action, SELL, risk, state, price and
 // source-provenance labels remain produced by existing PRO/source modules.
 const copy=lang==='en'?{
  risk:'Risk, protection and trader view',
  horizon:'Time horizons',
  owner:'Official Compass only',
  time:'Horizon',direction:'Direction',action:'Source posture'
 }:{
  risk:'Risiko, beskyttelse og trader-visning',
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
document.addEventListener('cn:languagechange',paint);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)load()});
window.addEventListener('focus',()=>{if(!document.hidden)load()});
const clock=setInterval(paint,CLOCK_RECHECK_MS);
const refresh=setInterval(()=>{if(!document.hidden)load()},SOURCE_RECHECK_MS);
window.addEventListener('pagehide',()=>{clearInterval(clock);clearInterval(refresh)});
paint();
load();
