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
let view=null,links=[],step='freeze';
const label={
 freeze:['Oprindelig udstedelse og fastlåste intervaller.','Original freeze and unchanged source ranges.'],
 observed:['Efterfølgende observeret dækning, aldrig bagudkonstrueret.','Later observation coverage, never hindsight reconstruction.'],
 assess:['Kun kildeberegnede Price Range-resultater til dato.','Only source-reported Price Range scores to date.']
};
const local=(da,en)=>document.documentElement.lang==='en'?en:da;
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
  const r=w.original_ranges.map(x=>x.asset+' '+x.low+'–'+x.high).join(' / ');
  return w.window+': '+r;
 }).join(' · ');
 if(step==='observed')text+=' '+rows.map(w=>
  w.window+': '+w.observed_hours+'/'+w.expected_hours_final+
  'h ('+w.state+')').join(' · ');
 if(step==='assess')text+=' '+rows.map(w=>
  w.window+' '+score(w.source_reported_score_to_date)+' · '+
  (w.observed_complete?'WINDOW COMPLETE':'PROVISIONAL')).join(' / ')+
  '. '+local('Ingen af tallene er uafhængigt Proof-seglet.',
             'None of these readings is independently proof-sealed.');
 host.textContent=text;
}
function renderWindows(){
 const host=$('proof-windows');host.replaceChildren();
 if(view?.status!=='PROVISIONAL_SOURCE_READBACK')return;
 const map={'day_1_2':'D1–2','day_3_4':'D3–4','day_5_7':'D5–7'};
 for(const w of view.window_items){
  const card=node('article','proof-window');card.dataset.status=w.observed_complete?'complete':'live';
  card.append(node('span','proof-kicker',map[w.window]+' · '+(w.observed_complete?'CLOSED':'PROVISIONAL')));
  card.append(node('strong','proof-score',score(w.source_reported_score_to_date)));
  card.append(node('p','',w.observed_hours+'/'+w.expected_hours_final+'h · '+
    local('observeret kildedækning','observed source coverage')));
  card.append(node('p','',w.state));
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
function display(){
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
async function initialize(){
 try{
  const latestJson=await json(latest);
  view=sourceOnlyPriceRangeProof(latestJson,{now_utc:new Date().toISOString()});
 }catch{view={status:'UNAVAILABLE'};}
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
initialize();
