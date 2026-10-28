/**
 * SITE #1578 · Single-root Kompas PRO readback, not a new action issuer.
 * Reuses existing source-verification and PRO rendering from /vnext-live/.
 * No separate model, new forecast, execution, market authority or API.
 */
import '../vnext-live/premium-experience.css';
import {inspectOfficialPublicFeeds} from '../vnext-live/official-feed-parity.mjs';
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
function paint(){
 const lang=document.documentElement.lang==='en'?'en':'da';
 try{view=feeds?inspectOfficialPublicFeeds(feeds.latest,feeds.compass,{lang}):null}
 catch{view=null}
 // Official source gate remains upstream. An expired issuer can never be
 // refreshed via a newer Pages bundle timestamp or cached prior DOM text.
 renderProductExperience(view,feeds,lang);
 horizons();
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
initProductExperience(()=>({view,feeds,lang:document.documentElement.lang==='en'?'en':'da'}));
document.addEventListener('cn:languagechange',paint);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)load()});
window.addEventListener('focus',()=>{if(!document.hidden)load()});
const clock=setInterval(paint,CLOCK_RECHECK_MS);
const refresh=setInterval(()=>{if(!document.hidden)load()},SOURCE_RECHECK_MS);
window.addEventListener('pagehide',()=>{clearInterval(clock);clearInterval(refresh)});
paint();
load();
