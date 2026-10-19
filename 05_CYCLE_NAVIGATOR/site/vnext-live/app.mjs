
/* Premium candidate only. Same-origin read-only official public data.
 * Never synthesize a market action, forecast, score or hidden source. */
import {inspectOfficialPublicFeeds} from './official-feed-parity.mjs';
const $=id=>document.getElementById(id),keys=['overview','compass','results'];
const H=[['NEXT_12H','0–12h'],['NEXT_1_3D','1–3d'],['NEXT_5_7D','5–7d'],['NEXT_2_3W','2–3u'],['CYCLE_ALTCOINS_3_8W','3–8u']];
const T=['BTC','ETH','LARGE_CAPS','MID_CAPS','SMALL_CAPS','MICROCAPS','MEMES'];
const dict={
da:{tabOverview:'Overblik',tabCompass:'Kompas',tabResults:'Resultater',overviewEyebrow:'MARKEDSBILLEDE / LIGE NU',heroOne:'Forstå',heroTwo:'retningen.',heroIntro:'Én tydelig læsning. Én officiel handling. Ægte markedsdata.',weeklyState:'UGENS MARKEDSSTATUS',actionLabel:'OFFICIEL HANDLING · NU',proxyLabel:'RETNINGSPROXY · 0–12 TIMER',proxyCaveat:'Observeret bevægelse, ikke selvstændigt valideret prognose.',riskLabel:'PULLBACK-RISIKO',distributionLabel:'DISTRIBUTION',nextGateLabel:'NÆSTE BEKRÆFTELSE',cycleHeading:'Hvor i cyklussen?',noEta:'Ingen udokumenteret ETA',forecastHeading:'Prognose møder virkelighed.',frozenRange:'Oprindeligt fastlåst interval',chartTitle:'Frossen prognose / faktiske priser',chartTrust:'Grafen viser kun frosne kildepunkter og gyldige observationer. Manglende dagsprognoser tegnes ikke.',compassHeading:'Tydeligere beslutninger.',compassSub:'Markedsretning, handling og tid adskilles. Ingen nye handelssignaler skabes her.',horizonsHeading:'Tidshorisonter',ownerOfficial:'Kun officielt Kompas',time:'Tid',direction:'Retning',actionShort:'Handling',tiersHeading:'Kapitalrotation',asset:'Aktiv',state:'Status',protectionHeading:'Beskyttelse og re-entry',pullback:'PULLBACK',resultsHeading:'Beviser frem for hype.',resultsSub:'Den senest afsluttede uge, dens reelle dækning og seks frosne intervaller. Ikke en opdigtet samlet præcision.',completedPrecision:'SENEST AFSLUTTEDE PRISPRÆCISION',coverage:'KILDEDÆKNING',hours:'Kvalificerede observationstimer',weeklyScoreTable:'Frossent interval vs. faktisk',sixWindows:'BTC / ETH · 3 vinduer',assetWindow:'Aktiv / vindue',frozenForecast:'Frossen prognose',observed:'Observeret',precision:'Præcision',methodHeading:'Hvad er egentlig verificeret?',methodText:'Prisintervaller måles med 70/30-metoden. Strukturanalyse scores ikke i procent efter CN #26. Uafhængig forsegling må ikke påstås uden bevis.',openScoreRepo:'Åbn offentligt kildearkiv ↗',previewOnly:'Ikke standardforsiden',legacySite:'Åbn eksisterende site ↗'},
en:{tabOverview:'Overview',tabCompass:'Compass',tabResults:'Results',overviewEyebrow:'MARKET OVERVIEW / RIGHT NOW',heroOne:'Read',heroTwo:'the shift.',heroIntro:'One clear reading. One official action. Real market evidence.',weeklyState:'THIS WEEK’S MARKET STATUS',actionLabel:'OFFICIAL ACTION · NOW',proxyLabel:'DIRECTION PROXY · 0–12 HOURS',proxyCaveat:'Observed continuation, not an independently validated forecast.',riskLabel:'PULLBACK RISK',distributionLabel:'DISTRIBUTION',nextGateLabel:'NEXT CONFIRMATION',cycleHeading:'Where are we in the cycle?',noEta:'No unsupported ETA',forecastHeading:'Forecast meets reality.',frozenRange:'Originally frozen weekly range',chartTitle:'Frozen forecast / actual prices',chartTrust:'Only original frozen points and eligible observations are shown. Missing daily forecasts are not drawn.',compassHeading:'Clearer decisions.',compassSub:'Direction, action and timing remain separate. No new trading signals are created here.',horizonsHeading:'Time horizons',ownerOfficial:'Official Compass only',time:'Horizon',direction:'Direction',actionShort:'Action',tiersHeading:'Capital rotation',asset:'Asset',state:'Status',protectionHeading:'Protection and re-entry',pullback:'PULLBACK',resultsHeading:'Receipts, not hype.',resultsSub:'Last completed week, real evidence coverage and six original frozen windows. No invented overall accuracy.',completedPrecision:'LATEST COMPLETED PRICE PRECISION',coverage:'SOURCE COVERAGE',hours:'Eligible observation hours',weeklyScoreTable:'Frozen range vs actual',sixWindows:'BTC / ETH · 3 windows',assetWindow:'Asset / window',frozenForecast:'Frozen forecast',observed:'Observed',precision:'Precision',methodHeading:'What is actually verified?',methodText:'Price ranges use the established 70/30 method. Structure analysis has no percentage score after CN #26. No claim of independent sealing without proof.',openScoreRepo:'Open public source archive ↗',previewOnly:'Not the default homepage',legacySite:'Open existing site ↗'}};
let lang='da',tab='overview',feeds=null,view=null,error=false,lastChartFeed=null,lastChartLang=null;
const tr=(da,en)=>lang==='da'?da:en, val=x=>typeof x==='string'&&x.trim()?x.trim().slice(0,600):null;
const num=x=>typeof x==='number'&&Number.isFinite(x);
const show=(id,s)=>{const e=$(id);if(e)e.textContent=String(s??'—')};
const money=x=>num(x)?'$'+x.toLocaleString(lang==='da'?'da-DK':'en-US',{maximumFractionDigits:2}):'—';
const pct=x=>num(x)?x.toLocaleString(lang==='da'?'da-DK':'en-US',{maximumFractionDigits:2})+'%':'—';
const range=(low,high)=>num(low)&&num(high)&&low<high?money(low)+' – '+money(high):'—';
const stamp=x=>x&&!Number.isNaN(Date.parse(x))?new Date(x).toLocaleString(lang==='da'?'da-DK':'en-GB',{timeZone:'UTC',day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'})+' UTC':'—';
const clear=id=>{const el=$(id);el.replaceChildren();return el};
function row(id,values){const tr=document.createElement('tr');for(const value of values){const td=document.createElement('td');td.textContent=String(value??'—');tr.append(td)}$(id).append(tr)}
function missing(id,n=3){clear(id);const tr=document.createElement('tr'),td=document.createElement('td');td.colSpan=n;td.textContent=trText('Ingen godkendelige officielle data','No eligible official data');tr.append(td);$(id).append(tr)}
function trText(da,en){return tr(da,en)}
function drawStatus(){
 const fresh=view?.compass?.state==='FRESH',valid=view?.weekly?.state==='OK'||view?.weekly?.state==='DEGRADED';
 $('source-dot').className='statusdot '+(fresh?'good':valid?'warn':'bad');
 show('source-status',error?tr('Indlæsning af offentlige kilder fejlede','Public source loading failed'):fresh?tr('Kildekontrolleret · officielt Kompas aktuelt','Source verified · Official Compass current'):valid?tr('Ugen frosset · aktuelle handlinger afventer','Week frozen · current actions unavailable'):tr('Ingen aktuel kildeverificeret handling','No current source-verified action'));
 show('source-clock',stamp(feeds?.latest?.generated_at));
}
function drawOverview(){
 const w=view?.weekly||{},c=view?.compass||{},p=view?.path||{},verified=c.state==='FRESH'&&c.permit_path_live_gates===true,official=verified?feeds.compass:null;
 show('headline',w.state==='DEGRADED'?tr('Begrænset dækning','Limited coverage'):w.state==='OK'?tr('Kildebundet','Source bound'):tr('Kilde afventer','Awaiting source'));
 show('week-label','CN #'+(w.public_issue_number??'—')+' · '+(w.forecast_week||'—'));
 show('action',official?(val(c.action_now)||'UNAVAILABLE'):'UNAVAILABLE');
 show('action-note',official?tr('Udstedt','Issued')+' '+stamp(official.issued_at_utc):tr('Ingen verificeret aktuel handling','No verified current action'));
 show('direction',official?(val(official.horizons?.NEXT_12H?.expected_direction)||'UNKNOWN'):'UNKNOWN');
 show('risk',official?(val(c.pullback_risk_state)||'UNKNOWN'):'UNKNOWN');
 show('risk-2',official?(val(c.pullback_risk_state)||'UNKNOWN'):'UNKNOWN');
 show('distribution',official?(val(official.protection_tracker?.distribution_risk)||'UNKNOWN'):'UNKNOWN');
 const next=typeof p.next_gate==='string'?p.next_gate:p.next_checkpoint?.label;
 show('next-gate',official&&p.state==='SOURCE_BOUND'?(val(next)||'UNAVAILABLE'):'UNAVAILABLE');
 show('cycle-summary',official&&p.state==='SOURCE_BOUND'?(val(official.market_now?.summary)||tr('Cyklusfase afventer bekræftelse','Cycle phase awaiting confirmation')):tr('Aktuel cyklusfase er ikke kildeverificeret. Det frosne ugeinterval vises nedenfor.','Current cycle phase is not source verified. The frozen weekly range remains below.'));
 clear('cycle-steps');
 const names=lang==='da'?['BTC-ledelse','ETH-ledelse','Large + mid','Altseason','Exit / beskyttelse']:['BTC leadership','ETH leadership','Large + mid','Altseason','Exit / protection'];
 const phaseKeys=['BTC','ETH','LARGE_MID','ALT_IGNITION','PROTECTION'];
 names.forEach((x,i)=>{const el=document.createElement('div'),s=document.createElement('strong');el.className='cycle-step';
  const sourceReference=verified&&p.state==='SOURCE_BOUND'&&
    p.current_checkpoint?.key===phaseKeys[i]&&p.current_checkpoint?.status==='FROZEN_WEEK_REFERENCE';
  el.dataset.reference=String(sourceReference);
  s.textContent=x;el.append(s);
  if(sourceReference){const note=document.createElement('small');note.textContent=tr('Frossen reference','Frozen reference');el.append(note)}
  $('cycle-steps').append(el)});
 show('btc-range',w.state==='OK'||w.state==='DEGRADED'?range(w.btc_range?.low,w.btc_range?.high):'—');
 show('eth-range',w.state==='OK'||w.state==='DEGRADED'?range(w.eth_range?.low,w.eth_range?.high):'—');
 show('freeze-identity',(w.forecast_week||'—')+' · CN #'+(w.public_issue_number??'—'));
 const path=feeds?.latest?.public_live_precision?.daily_price_path;
 const hasDaily=['BTC','ETH'].some(k=>path?.[k]?.status==='PUBLISHED'&&path?.[k]?.points?.length===7);
 show('chart-evidence',hasDaily?tr('Oprindelige dagsprognoser','Original daily forecasts'):tr('Ingen original dagskurve','No original daily curve'));
 window.CNI18n={language:lang};const host=$('official-path-chart');
 const chartData=feeds?.latest?.public_live_precision&&window.CNWeekChart?.mount&&window.LightweightCharts?feeds.latest:null;
 if(chartData){
   if(lastChartFeed!==chartData||lastChartLang!==lang)window.CNWeekChart.mount(host,chartData);
   lastChartFeed=chartData;lastChartLang=lang;
 }else{
   lastChartFeed=null;lastChartLang=lang;
   host.textContent=tr('Daglige kildeobservationer afventer. Frosne ugeintervaller står ovenfor.','Daily sourced observations pending. Original frozen weekly ranges are shown above.');
 }
}
function drawCompass(){
 const verified=view?.compass?.state==='FRESH'&&view.compass.permit_path_live_gates===true,official=verified?feeds.compass:null;
 if(!official){missing('horizon-body');missing('tier-body')}
 else{
  clear('horizon-body');for(const [key,label] of H){const v=official.horizons?.[key]||{};row('horizon-body',[label,val(v.expected_direction)||'UNAVAILABLE',val(v.action_posture)||'UNAVAILABLE'])}
  clear('tier-body');for(const key of T){const r=official.capitalization_ladder?.find(x=>x.segment===key);row('tier-body',[key,val(r?.status)||'UNAVAILABLE',val(r?.action)||'UNAVAILABLE'])}
 }
 show('sell-state',official?.sell_assessment?.state||'UNAVAILABLE');
 show('reentry-state',official?.protection_tracker?.reentry_state||'UNAVAILABLE');
 show('sell-note',official?.sell_assessment?.reason||tr('Pullback-risiko er ikke en salgstilladelse. Ingen ny handelsautoritet.','Pullback risk is not permission to sell. No new trading authority.'));
}
function drawResults(){
 const score=view?.completed_score||{},available=score.state==='FINAL_PUBLIC_SCORECARD';
 show('score-value',available?pct(score.price_range_precision):'—');
 show('score-identity',available?'CN #'+score.public_issue_number+' · '+score.forecast_week:tr('Senest afsluttede score er ikke verificeret','Latest completed score not verified'));
 const hours=available?feeds?.latest?.public_scorecard?.price_range_precision?.actuals_hourly_coverage:null;
 show('coverage-value',num(hours)?String(hours)+'/168':'—');
 show('score-proof',available?tr('Original metode og resultater matcher officiel offentlig score. Uafhængig forsegling er ikke dokumenteret.','Original method and results match the official public score. Independent sealing remains unproven.'):tr('Ingen score vises uden kilde- og observationsbevis.','No score is shown without source and observation proof.'));
 if(!available){missing('score-body',4);return}
 clear('score-body');
 for(const x of score.rows)row('score-body',[x.asset+' / '+x.window,range(x.forecast_low,x.forecast_high),range(x.actual_low,x.actual_high),pct(x.score)]);
}
function selectTab(id){
 if(!keys.includes(id))return;tab=id;
 for(const key of keys){$('view-'+key).hidden=key!==tab;const b=document.querySelector('[data-tab="'+key+'"]');b.setAttribute('aria-selected',String(key===tab));b.tabIndex=key===tab?0:-1}
 try{history.replaceState(null,'','#'+id)}catch{}
}
function refresh(){
 if(feeds){try{view=inspectOfficialPublicFeeds(feeds.latest,feeds.compass)}catch{view=null}}else view=null;
 document.documentElement.lang=lang;
 document.querySelectorAll('[data-t]').forEach(e=>{if(dict[lang][e.dataset.t])e.textContent=dict[lang][e.dataset.t]});
 document.querySelectorAll('[data-lang]').forEach(e=>e.setAttribute('aria-pressed',String(e.dataset.lang===lang)));
 drawStatus();drawOverview();drawCompass();drawResults();
}
let loading=false;
async function load(){
 if(loading)return;
 loading=true;
 const controller=new AbortController();
 const deadline=setTimeout(()=>controller.abort(),10000);
 try{
  const files=['../data/latest.json','../data/compass.json'];
  const [latest,compass]=await Promise.all(files.map(async path=>{const r=await fetch(path,{cache:'no-store',redirect:'error',signal:controller.signal});if(!r.ok)throw Error('OFFICIAL_PUBLIC_SOURCE_UNAVAILABLE');return r.json()}));
  feeds={latest,compass};error=false;
 }catch{feeds=null;error=true}
 finally{clearTimeout(deadline);loading=false;refresh()}
}
document.querySelectorAll('[data-tab]').forEach(b=>{
 b.addEventListener('click',()=>selectTab(b.dataset.tab));
 b.addEventListener('keydown',event=>{
  const at=keys.indexOf(b.dataset.tab);let index=null;
  if(event.key==='ArrowRight')index=(at+1)%keys.length;
  else if(event.key==='ArrowLeft')index=(at+keys.length-1)%keys.length;
  else if(event.key==='Home')index=0;
  else if(event.key==='End')index=keys.length-1;
  if(index!==null){event.preventDefault();selectTab(keys[index]);document.querySelector('[data-tab="'+keys[index]+'"]').focus()}
 });
});
document.querySelectorAll('[data-lang]').forEach(b=>b.addEventListener('click',()=>{lang=b.dataset.lang;try{localStorage.setItem('cnPremiumLanguage',lang)}catch{}refresh()}));
try{const stored=localStorage.getItem('cnPremiumLanguage');if(stored==='da'||stored==='en')lang=stored}catch{}
const initial=location.hash.slice(1);selectTab(keys.includes(initial)?initial:'overview');refresh();load();
document.addEventListener('visibilitychange',()=>{if(!document.hidden)load()});
window.addEventListener('focus',()=>{if(!document.hidden)load()});
setInterval(refresh,60000); // Cached source-owner expiry check (no HTTP).
setInterval(()=>{if(!document.hidden)load()},300000); // One first-party re-fetch / 5 minutes, visible tabs only.
