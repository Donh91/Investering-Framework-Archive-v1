
/* Premium candidate only. Same-origin read-only official public data.
 * Never synthesize a market action, forecast, score or hidden source. */
import {inspectOfficialPublicFeeds} from './official-feed-parity.mjs';
import {mondayContext,mondayLabels} from './monday-public-bridge.mjs';
import {sourceTrace} from './source-trace.mjs';
import {chartSourceFingerprint} from './chart-source-key.mjs';
import {renderProductExperience,initProductExperience} from './premium-experience.mjs';
const $=id=>document.getElementById(id),keys=['overview','compass','path','results'];
const H=[['NEXT_12H','0–12h'],['NEXT_1_3D','1–3d'],['NEXT_5_7D','5–7d'],['NEXT_2_3W','2–3u'],['CYCLE_ALTCOINS_3_8W','3–8u']];
const T=['BTC','ETH','LARGE_CAPS','MID_CAPS','SMALL_CAPS','MICROCAPS','MEMES'];
const dict={
da:{tabOverview:'Overblik',tabCompass:'Kompas',tabPath:'PATH',tabResults:'Resultater',overviewEyebrow:'MARKEDSBILLEDE / LIGE NU',heroOne:'Forstå',heroTwo:'retningen.',heroIntro:'Én tydelig læsning. Én officiel handling. Ægte markedsdata.',weeklyState:'UGENS MARKEDSSTATUS',actionLabel:'OFFICIEL HANDLING · NU',proxyLabel:'RETNINGSPROXY · 0–12 TIMER',proxyCaveat:'Observeret bevægelse, ikke selvstændigt valideret prognose.',riskLabel:'PULLBACK-RISIKO',distributionLabel:'DISTRIBUTION',nextGateLabel:'NÆSTE BEKRÆFTELSE',cycleHeading:'Hvor i cyklussen?',noEta:'Ingen udokumenteret ETA',forecastHeading:'Prognose møder virkelighed.',frozenRange:'Oprindeligt fastlåst interval',chartTitle:'Frossen prognose / faktiske priser',chartTrust:'Grafen viser kun frosne kildepunkter og gyldige observationer. Manglende dagsprognoser tegnes ikke.',compassHeading:'Tydeligere beslutninger.',compassSub:'Markedsretning, handling og tid adskilles. Ingen nye handelssignaler skabes her.',forwardNote:'2–3 ugers graf under udvikling. Kun illustrative data, ingen officiel prisprognose.',horizonsHeading:'Tidshorisonter',ownerOfficial:'Kun officielt Kompas',time:'Tid',direction:'Retning',actionShort:'Handling',tiersHeading:'Kapitalrotation',asset:'Aktiv',state:'Status',protectionHeading:'Beskyttelse og re-entry',pullback:'PULLBACK',resultsHeading:'Beviser frem for hype.',resultsSub:'Den senest afsluttede uge, dens reelle dækning og seks frosne intervaller. Ikke en opdigtet samlet præcision.',completedPrecision:'SENEST AFSLUTTEDE PRISPRÆCISION',coverage:'KILDEDÆKNING',hours:'Kvalificerede observationstimer',weeklyScoreTable:'Frossent interval vs. faktisk',sixWindows:'BTC / ETH · 3 vinduer',assetWindow:'Aktiv / vindue',frozenForecast:'Frossen prognose',observed:'Observeret',precision:'Præcision',methodHeading:'Hvad er egentlig verificeret?',methodText:'Prisintervaller måles med 70/30-metoden. Strukturanalyse scores ikke i procent efter CN #26. Uafhængig forsegling må ikke påstås uden bevis.',openScoreRepo:'Åbn offentligt kildearkiv ↗',openPath:'Se den fulde cyklusrejse →',previewOnly:'Ikke standardforsiden',legacySite:'Åbn eksisterende site ↗',mondayTitle:'Hvad viser mandagens grundlag?',mondayAnalytics:'ANALYSEGRUNDLAG',mondayEvidence:'KILDESTATUS · IKKE HANDELSSIGNAL',mondayScore:'SCORECARD',mondayTranslation:'OPERATIONEL ANALYSE',mondayApi:'AI-FORSKNING · SHADOW',mondayBoundary:'Frosset ugegrundlag er historisk kontekst. Kun et friskt, kildeverificeret Official Compass kan eje handlingen NU.'},
en:{tabOverview:'Overview',tabCompass:'Compass',tabPath:'PATH',tabResults:'Results',overviewEyebrow:'MARKET OVERVIEW / RIGHT NOW',heroOne:'Read',heroTwo:'the shift.',heroIntro:'One clear reading. One official action. Real market evidence.',weeklyState:'THIS WEEK’S MARKET STATUS',actionLabel:'OFFICIAL ACTION · NOW',proxyLabel:'DIRECTION PROXY · 0–12 HOURS',proxyCaveat:'Observed continuation, not an independently validated forecast.',riskLabel:'PULLBACK RISK',distributionLabel:'DISTRIBUTION',nextGateLabel:'NEXT CONFIRMATION',cycleHeading:'Where are we in the cycle?',noEta:'No unsupported ETA',forecastHeading:'Forecast meets reality.',frozenRange:'Originally frozen weekly range',chartTitle:'Frozen forecast / actual prices',chartTrust:'Only original frozen points and eligible observations are shown. Missing daily forecasts are not drawn.',compassHeading:'Clearer decisions.',compassSub:'Direction, action and timing remain separate. No new trading signals are created here.',forwardNote:'Two-to-three-week chart in development. Illustrative data only, no official price prediction.',horizonsHeading:'Time horizons',ownerOfficial:'Official Compass only',time:'Horizon',direction:'Direction',actionShort:'Action',tiersHeading:'Capital rotation',asset:'Asset',state:'Status',protectionHeading:'Protection and re-entry',pullback:'PULLBACK',resultsHeading:'Receipts, not hype.',resultsSub:'Last completed week, real evidence coverage and six original frozen windows. No invented overall accuracy.',completedPrecision:'LATEST COMPLETED PRICE PRECISION',coverage:'SOURCE COVERAGE',hours:'Eligible observation hours',weeklyScoreTable:'Frozen range vs actual',sixWindows:'BTC / ETH · 3 windows',assetWindow:'Asset / window',frozenForecast:'Frozen forecast',observed:'Observed',precision:'Precision',methodHeading:'What is actually verified?',methodText:'Price ranges use the established 70/30 method. Structure analysis has no percentage score after CN #26. No claim of independent sealing without proof.',openScoreRepo:'Open public source archive ↗',openPath:'Explore the full market cycle →',previewOnly:'Not the default homepage',legacySite:'Open existing site ↗',mondayTitle:'What does Monday’s evidence show?',mondayAnalytics:'ANALYTICAL CONTEXT',mondayEvidence:'SOURCE STATUS · NOT A TRADE SIGNAL',mondayScore:'SCORECARD',mondayTranslation:'OPERATIONAL ANALYSIS',mondayApi:'AI RESEARCH · SHADOW',mondayBoundary:'Frozen completed-week evidence is historical context. Only a fresh, source-verified Official Compass owns the action NOW.'}};
Object.assign(dict.da,{
 longHorizonEyebrow:'FROSSET / RESEARCH · IKKE HANDLING NU',
 longHorizonTitle:'Længere tidshorisonter',
 longHorizonDisclaimer:'Viser kun kildeudstedt ugentlig og strategisk kontekst, ikke nye køb/sælg-signaler eller bekræftede startdatoer.',
 sourceOwner:'Kildeansvar',sourceStatusSummary:'Se de underliggende kildeled',
 sourceStatusDisclaimer:'Hver datakilde har sin egen status. Shadow og strategi er ikke-bindende og kan aldrig ændre den officielle handling.'
});
Object.assign(dict.en,{
 longHorizonEyebrow:'FROZEN / RESEARCH · NOT CURRENT ACTION',
 longHorizonTitle:'Longer time horizons',
 longHorizonDisclaimer:'Only original weekly and strategic source context, not new buy/sell signals or confirmed start dates.',
 sourceOwner:'Source owner',sourceStatusSummary:'Inspect underlying source layers',
 sourceStatusDisclaimer:'Each owner has an independent status. Shadow and strategic research are nonbinding and cannot change the official action.'
});
let lang='da',tab='overview',feeds=null,view=null,error=false,lastChartFingerprint=null,lastChartLang=null;
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
 // Never present Pages re-publication time as fresh Official market evidence.
 // Use the source owner's exact published validity deadline, not an inferred TTL.
 const freshness=feeds?.compass?.full_stack?.official_freshness;
 const ownerExpiry=freshness?.contract==='OFFICIAL_COMPASS_SOURCE_FRESHNESS_READBACK_v1'&&
   freshness?.status==='VERIFIED_OWNER_POLICY'&&
   freshness?.semantics==='SOURCE_FRESHNESS_EXPIRY_NOT_FORECAST_ETA'?
     freshness.valid_until_utc:null;
 const expiryMs=typeof ownerExpiry==='string'?Date.parse(ownerExpiry):NaN;
 const expired=Number.isFinite(expiryMs)&&Date.now()>=expiryMs;
 $('source-dot').className='statusdot '+(fresh?'good':valid?'warn':'bad');
 show('source-status',error?tr('Indlæsning af offentlige kilder fejlede','Public source loading failed'):
   fresh?tr('Kildekontrolleret · officielt Kompas aktuelt','Source verified · Official Compass current'):
   expired?tr('Officielt Kompas udløbet · ingen aktuel handling','Official Compass expired · no current action'):
   valid?tr('Kompas ikke aktuelt · frossen ugegrundlag vises','Compass not current · frozen weekly context shown'):
   tr('Ingen aktuel kildeverificeret handling','No current source-verified action'));
 show('source-clock',Number.isFinite(expiryMs)?
   tr('Kompas gyldigt til ','Compass valid until ')+stamp(ownerExpiry):
   tr('Sidste levering ','Last delivery ')+stamp(feeds?.latest?.generated_at));
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
 show('btc-range',w.state==='OK'||w.state==='DEGRADED'?range(w.btc_range?.low,w.btc_range?.high):'—');
 show('eth-range',w.state==='OK'||w.state==='DEGRADED'?range(w.eth_range?.low,w.eth_range?.high):'—');
 show('freeze-identity',(w.forecast_week||'—')+' · CN #'+(w.public_issue_number??'—'));
 const path=feeds?.latest?.public_live_precision?.daily_price_path;
 const hasDaily=['BTC','ETH'].some(k=>path?.[k]?.status==='PUBLISHED'&&path?.[k]?.points?.length===7);
 show('chart-evidence',hasDaily?tr('Oprindelige dagsprognoser','Original daily forecasts'):tr('Ingen original dagskurve','No original daily curve'));
 window.CNI18n={language:lang};const host=$('official-path-chart');
 const chartData=feeds?.latest?.public_live_precision&&window.CNWeekChart?.mount&&window.LightweightCharts?feeds.latest:null;
 if(chartData){
   // Parse-object identity changes on every fetch. Source fingerprint excludes
   // unrelated public data and generated_at so an unchanged chart keeps
   // scroll, zoom, selected day and BTC/ETH user interaction intact.
   const fingerprint=chartSourceFingerprint(chartData);
   if(lastChartFingerprint!==fingerprint||lastChartLang!==lang)window.CNWeekChart.mount(host,chartData);
   lastChartFingerprint=fingerprint;lastChartLang=lang;
 }else{
   lastChartFingerprint=null;lastChartLang=lang;
   host.textContent=tr('Daglige kildeobservationer afventer. Frosne ugeintervaller står ovenfor.','Daily sourced observations pending. Original frozen weekly ranges are shown above.');
 }
}
function drawMonday(){
 const m=mondayContext(feeds?.latest,feeds?.compass,view);
 const t=mondayLabels(m,lang),verified=m.source_state==='SOURCE_ALIGNED';
 show('monday-reading',t.title);
 show('monday-explanation',t.evidence);
 show('monday-week',verified?m.completed_week:'—');
 show('monday-source',verified?tr('Verificeret ugegrundlag','Verified completed-week source'):tr('Kilde ikke verificeret','Source unverified'));
 show('monday-source-explanation',tr('Ugentlig kontekst – ingen selvstændig handelstilladelse.','Weekly context only – no independent trade permission.'));
 show('monday-scorecard',verified?m.scorecard_status:'UNAVAILABLE');
 show('monday-translation',verified?m.operational_translation_status:'UNAVAILABLE');
 show('monday-api',verified&&m.api_analysis_status==='AVAILABLE_SHADOW_ONLY'
   ?tr('Tilgængelig · ikke-bindende','Available · nonbinding'):'UNAVAILABLE');
}
function drawSourceTrace(){
 const result=sourceTrace(feeds?.latest,feeds?.compass,view);
 const trust=result.reason==='OFFICIAL_NOT_CURRENT_CONTEXT_ONLY'
   ?tr('Official ikke aktuelt · kun frossen/research-kontekst','Official not current · frozen/research context only')
   :result.status==='COMPLETE'
     ?tr('Alle krævede kilder verificeret','All required sources verified')
     :result.status==='PARTIAL_OR_DEGRADED'
       ?tr('Delvist kildegrundlag','Partial source evidence')
       :tr('Kildestatus utilgængelig','Source status unavailable');
 show('source-trace-status',trust);
 clear('long-horizon-body');
 const labels={'2_3w':'2–3u','21_30d':'21–30d','4_8w':'4–8u'};
 for(const h of result.long_horizons){
   row('long-horizon-body',[labels[h.id]||h.id,h.direction,
     h.owner==='CYCLE_NAVIGATOR_WEEKLY'
       ?tr('Cycle Navigator · frossen uge','Cycle Navigator · frozen week')
       :h.owner==='CYCLE_NAVIGATOR_STRATEGIC_CONTEXT'
         ?tr('Cycle Navigator · strategisk kontekst','Cycle Navigator · strategic context')
         :tr('Strategisk research · ikke-bindende','Strategic research · nonbinding')]);
 }
 clear('source-trace-body');
 const da={
   'Official Compass':'Official Compass','Auto Market State':'Auto Market State',
   'Native Handlekompas':'Native Handlekompas','Shadow research':'Shadow · research',
   'Strategic Compass':'Strategisk Kompas','Master Monday':'Master Monday',
   'Cycle Navigator':'Cycle Navigator'
 };
 for(const item of result.sources)
   row('source-trace-body',[lang==='da'?(da[item.name]||item.name):item.name,item.status]);
}
function drawCompass(){
 drawMonday();
 drawSourceTrace();
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
 try{const url=new URL(location.href);url.hash=id;history.replaceState(null,'',url.href)}catch{}
}
function refresh(){
 if(feeds){try{view=inspectOfficialPublicFeeds(feeds.latest,feeds.compass,{lang})}catch{view=null}}else view=null;
 document.documentElement.lang=lang;
 document.querySelectorAll('[data-t]').forEach(e=>{if(dict[lang][e.dataset.t])e.textContent=dict[lang][e.dataset.t]});
 document.querySelectorAll('[data-lang]').forEach(e=>e.setAttribute('aria-pressed',String(e.dataset.lang===lang)));
 drawStatus();drawOverview();drawCompass();drawResults();renderProductExperience(view,feeds,lang);
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
// The shared document base must not turn the skip link into a page reload.
document.querySelector('.skip').addEventListener('click',event=>{
 event.preventDefault();$('content').focus();
});
initProductExperience(()=>({view,feeds,lang}));
document.querySelectorAll('[data-nav-to]').forEach(a=>a.addEventListener('click',e=>{
 e.preventDefault();
 const target=a.dataset.navTo;
 if(!keys.includes(target))return;
 selectTab(target);
 // The trigger is now in a hidden panel. Move focus to the selected real tab,
 // including for keyboard / VoiceOver navigation.
 document.querySelector('[data-tab="'+target+'"]')?.focus();
}));
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
