/**
 * Proof 2.1 · read-only SOURCE UI. No score calculations, AI attestation,
 * synthetic prices, "VERIFIED" promotion, or immutable source rewrites.
 */
import {sourceOnlyPriceRangeProof} from './price-range-proof.mjs';
import {sourceReadbackProofRows} from './public-source-links.mjs';
const $=id=>document.getElementById(id);
const HOME='https://raw.githubusercontent.com/Donh91/CycleNavigator-scores/main/';
const latest=new URL('../../data/latest.json',import.meta.url);
const INDEX=HOME+'v2/scorebook-index.json';
const RECEIPT=HOME+'v2/source-receipts/2026/2026-10-20_PUBLIC_READBACK.json';
let view=null,sourceSnapshot=null,expiryTimer=null,links=[],step='freeze',requestGeneration=0;
const SOURCE_RECHECK_MS=5*60*1000;
const label={
 freeze:['Oprindelig udstedelse og fastlåste intervaller.','Original freeze and unchanged source ranges.'],
 observed:['Efterfølgende observeret dækning, aldrig bagudkonstrueret.','Later observation coverage, never hindsight reconstruction.'],
 assess:['Kun kildeberegnede Price Range-resultater til dato.','Only source-reported Price Range scores to date.']
};
const local=(da,en)=>document.documentElement.lang==='en'?en:da;
const windowName={day_1_2:'D1–2',day_3_4:'D3–4',day_5_7:'D5–7'};
const integer=n=>Number(n).toLocaleString(document.documentElement.lang==='en'?'en-GB':'da-DK');
function node(tag,cls,text){const n=document.createElement(tag);if(cls)n.className=cls;
 if(text!==undefined)n.textContent=String(text);return n}
function score(n){return typeof n==='number'&&Number.isFinite(n)?n.toLocaleString(
 document.documentElement.lang==='en'?'en-GB':'da-DK',{maximumFractionDigits:2})+' %':'—'}
async function json(url){
 const response=await fetch(url,{credentials:'omit',cache:'no-store',redirect:'error',
   signal:AbortSignal.timeout(12000)});
 if(!response.ok)throw Error('SOURCE_HTTP_'+response.status);
 return response.json();
}
function focus(){
 const host=$('proof-focus');host.replaceChildren();
 if(view?.status!=='PROVISIONAL_SOURCE_READBACK'){
  host.textContent=local('Ingen verificerbar Price Range-kilde, derfor ingen præcisionsvisning.',
   'Price Range source unavailable; accuracy is not displayed.');
  return;
 }
 const rows=view.window_items;
 let text=local(...label[step]);
 if(step==='freeze')text+=' '+rows.map(w=>{
  const r=w.original_ranges.map(x=>x.asset+' '+integer(x.low)+'–'+integer(x.high)+' USD').join(' / ');
  return windowName[w.window]+': '+r;
 }).join(' · ');
 if(step==='observed')text+=' '+rows.map(w=>
  windowName[w.window]+': '+w.observed_hours+'/'+w.expected_hours_final+
  'h').join(' · ');
 if(step==='assess')text+=' '+rows.map(w=>
  windowName[w.window]+' '+score(w.source_reported_score_to_date)+' · '+
  (w.observed_complete?local('afsluttet','closed'):local('foreløbig','provisional'))).join(' / ')+
  '. '+local('Ingen af tallene er uafhængigt Proof-seglet.',
             'None of these readings is independently proof-sealed.');
 host.textContent=text;
}
function renderWindows(){
 const host=$('proof-windows');host.replaceChildren();
 if(view?.status!=='PROVISIONAL_SOURCE_READBACK')return;
 for(const w of view.window_items){
  const card=node('article','proof-window');card.dataset.status=w.observed_complete?'complete':'live';
  card.setAttribute('title',w.state);
  card.append(node('span','proof-kicker',windowName[w.window]+' · '+(w.observed_complete?
   local('AFSLUTTET','CLOSED'):local('FORELØBIG','PROVISIONAL'))));
  card.append(node('strong','proof-score',score(w.source_reported_score_to_date)));
  card.append(node('p','',w.observed_hours+'/'+w.expected_hours_final+'h · '+
    local('observeret kildedækning','observed source coverage')));
  card.append(node('p','',w.observed_complete?
   local('Kildedækning afsluttet','Source coverage complete'):
   local('Observation fortsætter','Observation ongoing')));
  host.append(card);
 }
}
function renderSources(){
 const host=$('proof-sources');host.replaceChildren();
 const intro=node('p','',local(
  'GitHub-commits er navigations- og byte-referencer. Uden uafhængigt tidsvidne er disse forecast-mirrors foreløbige, ikke VERIFIED.',
  'GitHub commit SHAs identify bytes, not independent pre-outcome attestation. These mirrors remain provisional.'));
 host.append(intro);
 if(!links.length){host.append(node('p','',local('Ingen godkendt præcis kildebinding.','No eligible exact source binding.')));return}
 const body=node('div','proof-source-list');
 for(const r of links){
  const row=node('div','proof-source-row'),info=node('div','');
  info.append(node('strong','', 'CN #'+r.public_issue_number+' · '+r.forecast_week));
  info.append(node('small','', r.total_claims+' '+local('oprindelige udsagn','original claims')+
   ' · '+r.abstained_claims+' ABSTAIN · '+r.independent_proof_status));
  const a=node('a','',local('Original ↗','Original ↗'));
  a.href=r.source_url;a.target='_blank';a.rel='noopener noreferrer';
  row.append(info,a);body.append(row);
 }
 host.append(body);
}

function localizeProof(){
 const en=document.documentElement.lang==='en';
 const eyebrow=document.querySelector('.proof-eyebrow');if(eyebrow)eyebrow.textContent=en?
  'RESULTS / ORIGINAL → OBSERVED → SCORE':'RESULTATER / ORIGINAL → OBSERVERET → SCORE';
 const steps=document.querySelector('.proof-steps');if(steps)steps.setAttribute('aria-label',en?'Proof steps':'Proof-trin');
 $('proof-windows').setAttribute('aria-label',en?'Three weekly price windows':'Tre ugentlige prisvinduer');
 const heading=$('proof-title');if(heading)heading.textContent=en?
  'Proof. Check what was actually forecast.':'Proof. Se hvad der faktisk blev forudsagt.';
 const sub=document.querySelector('.proof-head p');if(sub)sub.textContent=en?
  'Frozen original source, observed outcomes, and an inspectable method. No rewriting.':
  'Frosne kilder, observerede udfald, åben metode. Ingen omskrivning.';
 const map={freeze:en?'Original freeze':'Frossen kilde',
 observed:en?'Observed':'Observation',assess:en?'Score & source':'Score & kilde'};
 for(const button of document.querySelectorAll('[data-proof-step]')){
  const key=button.dataset.proofStep,id=key==='freeze'?'01':key==='observed'?'02':'03';
  button.replaceChildren(node('span','',id),document.createTextNode(map[key]||key));
 }
 const summary=document.querySelector('.proof-source-details summary');
 if(summary)summary.textContent=en?'Original GitHub sources and method':'Originale GitHub-kilder og metode';
 const link=document.querySelector('.proof-foot a');if(link)link.textContent=en?
  'Open public Proof archive ↗':'Åbn offentligt Proof-arkiv ↗';
 const copy=$('proof-copy-audit');if(copy)copy.textContent=en?'Copy audit prompt':'Kopiér auditinstruktion';
}

function display(){
 // Re-derive freshness on every repaint, including language/tab interactions.
 if(sourceSnapshot)view=sourceOnlyPriceRangeProof(sourceSnapshot,{now_utc:new Date().toISOString()});
 if(expiryTimer!==null){clearTimeout(expiryTimer);expiryTimer=null;}
 if(view?.status==='PROVISIONAL_SOURCE_READBACK'&&!view.source_stale){
  const ms=Date.parse(view.source_valid_until_utc)-Date.now()+1;
  if(ms>0&&ms<2147483000)expiryTimer=setTimeout(display,ms);
 }
 localizeProof();
 const available=view?.status==='PROVISIONAL_SOURCE_READBACK';
 const freshness=$('proof-freshness');
 freshness.dataset.freshness=available?(view.source_stale?'stale':'current'):'unavailable';
 freshness.textContent=available?
  (view.source_stale?'STALE':'CURRENT')+' · '+local('Observation','Observed')+' '+view.live_as_of_utc+
  ' · '+local('Friskhedsgrænse','Freshness limit')+' '+view.source_freshness_sla_minutes+
  ' min · '+local('gyldig til','valid until')+' '+view.source_valid_until_utc:
  local('Observationstid og kildefriskhed utilgængelig.','Observation time and source freshness unavailable.');
 $('proof-status').textContent=view?.status==='PROVISIONAL_SOURCE_READBACK'?
  local('FORELØBIG · '+view.forecast_week,'PROVISIONAL · '+view.forecast_week):
  local('KILDE MANGLER','SOURCE MISSING');
 $('proof-method').textContent=local(
  'Price Range 70 % containment + 30 % Jaccard. D1–2/D3–4/D5–7 er kildeberegnede tal til dato; Direction/Edge forbliver en separat ABSTAIN-/Proof-familie. Ingen afkastgaranti.',
  'Price Range: 70% containment + 30% Jaccard. D1–2/D3–4/D5–7 are source-reported interim readings; Direction/Edge is a separate ABSTAIN/Proof family. Not a return prediction.'
 );
 document.querySelectorAll('[data-proof-step]').forEach(button=>{
  button.setAttribute('aria-pressed',String(button.dataset.proofStep===step));
 });
 renderWindows();focus();renderSources();
}
async function refreshLatest(){
 const request=++requestGeneration;
 try{
  const next=await json(latest);
  if(request!==requestGeneration)return;
  sourceSnapshot=next;
 }catch{
  if(request!==requestGeneration)return;
  sourceSnapshot=null;view={status:'UNAVAILABLE'};
 }
 // Render and arm expiry before optional external Proof links finish loading.
 display();
}
async function initialize(){
 await refreshLatest();
 try{
  const [index,receipt]=await Promise.all([json(INDEX),json(RECEIPT)]);
  links=sourceReadbackProofRows(index,receipt);
 }catch{links=[];}
 display();
}
document.querySelectorAll('[data-proof-step]').forEach(button=>
 button.addEventListener('click',()=>{step=button.dataset.proofStep;display()}));
$('proof-copy-audit')?.addEventListener('click',async()=>{
 const prompt=[
 'Audit Cycle Navigator PROOF from the original PUBLIC frozen source, never from this UI alone.',
 'Score family: PRICE_RANGE_PRECISION is separate from binary EDGE and investment returns.',
 'Forecast week: '+(view?.forecast_week||'UNAVAILABLE'),
 'Public CN issue: '+(view?.public_issue_number||'UNAVAILABLE'),
 'Source freeze timestamp: '+(view?.freeze_issued_at_utc||'UNAVAILABLE'),
 'Public sources: '+links.map(x=>x.source_url+' SHA256 '+x.source_sha256).join(' ; '),
 'Verify source issue, source_commit, bytes, pre-window publication evidence, hourly coverage, method (70/30), mature outcomes, source hash and independent timestamp anchor.',
 'Mark PROVISIONAL or ABSTAIN unless independently sealed. Do not reconstruct missing future expected closes.'
 ].join('\n');
 try{await navigator.clipboard.writeText(prompt);
  $('proof-copy-status').textContent=local('Kopieret','Copied');
 }catch{$('proof-copy-status').textContent=local('Kopiér manuelt fra kildeoversigten','Use sources above manually')}
});
document.addEventListener('cn:languagechange',()=>display());
document.addEventListener('visibilitychange',()=>{if(!document.hidden)refreshLatest()});
window.addEventListener('pageshow',()=>{refreshLatest()});
const sourceRecheck=setInterval(()=>{if(!document.hidden)refreshLatest()},SOURCE_RECHECK_MS);
window.addEventListener('pagehide',()=>clearInterval(sourceRecheck));
initialize();
