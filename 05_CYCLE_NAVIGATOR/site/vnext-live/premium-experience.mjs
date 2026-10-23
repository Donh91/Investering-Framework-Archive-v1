/* Cycle Navigator Premium product alignment, read-only presentation.
 * Official source, week join, source expiry and score authority remain upstream.
 * Never infer a trading action, pullback probability, phase ETA or proof seal.
 */
import {officialBullBear} from './official-bullbear.mjs';
import {officialPullbackStage} from './official-pullback-stage.mjs';
import {officialPathView} from './official-path.mjs';

const RISK=['NORMAL','BUILDING','ELEVATED','HIGH','CONFIRMED'];
const STAGE_LABELS={
 da:['Normal','Opbygning','Forhøjet','Høj','Bekræftet'],
 en:['Normal','Building','Elevated','High','Confirmed']
};
export function riskStageLabel(stage,lang='da'){
 const index=RISK.indexOf(stage);return index<0?'UNAVAILABLE':STAGE_LABELS[lang==='en'?'en':'da'][index];
}
const TXT={
 da:{
  unavailable:'UTILGÆNGELIG',action:'Handling nu',direction:'0–12t · observeret retning',bull:'Bull',bear:'Bear',
  balance:'Officiel evidensbalance, ikke sandsynlighed eller handelssignal',
  risk:'Pullback · officiel risikoklasse',severity:'Trin i fem kategorier, ikke procent eller sandsynlighed',
  sell:'SELL / TRIM',distribution:'Distribution',window:'Muligt kildevindue',quality:'Evidenskvalitet',
  impact:'Påvirkning på BTC, ETH, large, mid, small, micro og memes er ikke individuelt verificeret',
  noSell:'Pullback er ikke en selvstændig salgstilladelse',
  holder:'HODL / beskyttelse',active:'Aktiv / swing',micro:'Micro / meme',
  holderNote:'Følg officiel SELL-vurdering, distribution og pullback. En watch-status er ikke automatisk exit.',
  activeNote:'Adskil 0–12 timers observeret retning fra officiel handling. Kontrollér kildevindue og ugyldiggørelse før positionering.',
  microNote:'Høj beta kræver særskilt aktivering. Microcaps kan aldrig give MEMES en handelstilladelse; afvent egne kildesignalers status.',
  info:'Visningsfokus ændrer kun forklaring, ikke signal, risikomodel eller kilde.',
  pathNow:'Aktuelt checkpoint',pathNext:'Næste bekræftelse',pathWatch:'Altseason-watch',
  pathUnavailable:'Aktuel cyklusfase ikke verificeret',pathNote:'Blå: kun kildeunderbygget reference. Rav: ubekræftet næste gate. Grå: ingen dokumenteret progression.',
  pathGate:'Næste kildebetingelse',pathNoEta:'Ingen verificeret ETA',pathFrozen:'Frossen ugereference, ikke bekræftet faseovergang',
  rotation:'Denne uges kapitalrotation',wait:'Ikke bekræftet',source:'Kilde',
  rangeFamily:'Price Range · kildescore',directionFamily:'Direction / Flow / Rotation',pullbackFamily:'Pullback Edge',rangeEligible:'Officielt scorecard · ikke uafhængigt forseglet',rangeUnavailable:'Ingen færdig kildekontrolleret score',edgeUnavailable:'Ingen verificeret offentlig Edge-score',
  proofTitle:'Få en uafhængig AI-gennemgang',proofInfo:'Læsere kan lade deres egen AI kontrollere originale prognoser, hashbindinger, observationer og scores. Dette er ikke en AI-certificering eller en ny modelvurdering.',
  proofButton:'Kopiér auditinstruks',proofCopied:'Auditinstruks kopieret',proofFailure:'Markér og kopiér teksten nedenfor',
  proofStatus:'Uafhængig ex-ante-forsegling afventer dokumentation. Price Range ≠ Direction/Rotation/Pullback Edge.',
  proofOpen:'Åbn ChatGPT',proofArchive:'Åbn offentligt proof-arkiv',
  proofRangeMeaning:'Scoren gælder kun de seks afsluttede BTC/ETH-prisvinduer efter den eksisterende 70/30-metode. Den er ikke en score for køb/sælg, markedsretning eller kommende uger.',
  proofCoverageMeaning:'Datadækning tæller observerede timer, ikke korrekte forudsigelser. 168/168 er derfor ikke 100 % prognosepræcision.',
  proofFirstKnown:'Før udfald',proofFirstCopy:'Original prognose og udstedelsestid skal være fastlåst',
  proofOngoing:'Undervejs',proofOngoingCopy:'Kun kildeverificerede faktiske observationer tæller',
  proofAfter:'Efter udløb',proofAfterCopy:'Kun modne og godkendelige resultater får score',
  proofSix:'Vis de seks historiske vinduer og deres oprindelige værdier',
  proofLiveEyebrow:'DENNE UGE · KILDEBUNDET',proofLiveTitle:'Løbende kontrol af prisvinduer',
  proofLiveExplainer:'Dag 1–2, 3–4 og 5–7. Samme 70/30-metode som den afsluttede uge. Foreløbige tal er ikke en godkendt slutscore.',
  proofLiveMissing:'Denne uges kvalificerede timeopgørelse mangler. Ingen løbende score vises.',
  proofLiveStale:'Sidste prisobservation er forældet. Løbende scoring vises først med friske verificerede data.',
  proofLiveFresh:'Oprindeligt fastlåst · verificerede observationer',
  proofLivePending:'Afventer',proofLiveClosed:'Vindue lukket · foreløbig',proofLiveTracking:'Under observation · foreløbig',
  proofLiveDegraded:'Mangelfuld datadækning',proofLiveWindow:'Dag',proofLiveHours:'timer observeret',proofLiveNoScore:'Ingen kvalificeret score endnu',
  pathPage:'Markeds­cyklussen',pathIntro:'Cyklusrejsen og kapitalrotationen. Ingen selvstændige handlesignaler eller opdigtede datoer.',pathStepsTitle:'10 trin. Én sammenhængende rejse.',pathConditional:'Et observationsvindue er ikke en bekræftet dato.',rotationCaveat:'Et HOLD er ikke en bekræftet fase. Memes kræver særskilt kilde.',altNote:'Kun et betinget observationsmål, aldrig en automatisk nedtælling.',interpretation:'Min fortolkning · ugegrundlag og kilder',protection:'Pullback, beskyttelse & re-entry',contextNote:'Master Monday og forskning er baggrund, ikke officielle køb/sælg-signaler.',
  proofPrompt:'Uafhængig kildeaudit af Cycle Navigator: Åbn følgende OFFENTLIGE arkiver. Læs README, v2/scorebook-index.json og latest_readback. For hver påstand: hent ORIGINAL prognose ved præcist source_commit, kontroller offentlig CN-identitet, forecast_week, offentliggørelsestid før outcome, byte-eksakt SHA-256, gældende 70/30-metode, 168-timers dækning og seks frosne BTC/ETH-vinduer. Skeln Price Range-præcision fra Direction/Flow/Rotation og Pullback Edge, som kan være ABSTAIN/PENDING. Kontroller censur, fejl, datamangler og baseline. Kræv uafhængigt verificeret timestamp og immutable release før VERIFIED. Rapporter PASS/FAIL/UNVERIFIED med konkrete kilde-URL\'er; gæt aldrig manglende data.'
 },
 en:{
  unavailable:'UNAVAILABLE',action:'Official action now',direction:'0–12h · observed direction',bull:'Bull',bear:'Bear',
  balance:'Official evidence balance, not probability or trading permission',
  risk:'Pullback · official risk class',severity:'Five ordinal categories, not a percent or event probability',
  sell:'SELL / TRIM',distribution:'Distribution',window:'Possible source window',quality:'Evidence quality',
  impact:'Tier-by-tier impact on BTC, ETH, large, mid, small, micro and memes is not independently verified',
  noSell:'A pullback watch never independently authorizes selling',
  holder:'HODL / protect',active:'Active / swing',micro:'Micro / meme',
  holderNote:'Watch the official sell assessment, distribution and pullback. Watch status does not automatically mean exit.',
  activeNote:'Separate observed 0–12h direction from official action. Verify the source window and invalidation before positioning.',
  microNote:'High beta needs its own confirmation. Microcap status never authorizes MEMES; await dedicated source confirmation.',
  info:'This lens changes presentation only, never action, source authority or risk classification.',
  pathNow:'Current checkpoint',pathNext:'Next confirmation',pathWatch:'Altseason watch',
  pathUnavailable:'Current cycle phase unverified',pathNote:'Blue: sourced reference only. Amber: unconfirmed next gate. Grey: no documented progression.',
  pathGate:'Next source condition',pathNoEta:'No verified ETA',pathFrozen:'Frozen weekly reference, not a confirmed phase transition',
  rotation:'This week’s capital rotation',wait:'Unconfirmed',source:'Source',
  rangeFamily:'Price Range · source score',directionFamily:'Direction / Flow / Rotation',pullbackFamily:'Pullback Edge',rangeEligible:'Official scorecard · not independently sealed',rangeUnavailable:'No eligible completed source score',edgeUnavailable:'No verified public Edge score',
  proofTitle:'Ask an independent AI to audit',proofInfo:'Readers can use their own AI to examine original forecasts, source hashes, observations and scores. This is not AI certification or a new performance claim.',
  proofButton:'Copy audit instructions',proofCopied:'Audit instructions copied',proofFailure:'Select and copy the prompt below',
  proofStatus:'Independent ex-ante sealing remains unproven. Price Range ≠ Direction/Rotation/Pullback Edge.',
  proofOpen:'Open ChatGPT',proofArchive:'Open public proof archive',
  proofRangeMeaning:'The score covers only the six completed BTC/ETH price windows under the existing 70/30 method. It does not rate buy/sell calls, direction or future weeks.',
  proofCoverageMeaning:'Coverage counts observed hours, not correct predictions. 168/168 does not mean 100% forecast accuracy.',
  proofFirstKnown:'Before outcome',proofFirstCopy:'Original forecast and issue time must be frozen',
  proofOngoing:'During week',proofOngoingCopy:'Only source-verified real observations count',
  proofAfter:'After maturity',proofAfterCopy:'Only mature eligible outcomes receive a score',
  proofSix:'View six historical windows and original source values',
  proofLiveEyebrow:'THIS WEEK · SOURCE-BOUND',proofLiveTitle:'Live price-window accountability',
  proofLiveExplainer:'Days 1–2, 3–4 and 5–7. The same 70/30 method as the settled week. Running values are not final settled scores.',
  proofLiveMissing:'Eligible current-week hourly evidence is unavailable. No running score is shown.',
  proofLiveStale:'Last price observation is stale. Running scores require fresh verified evidence.',
  proofLiveFresh:'Originally frozen · verified observations',
  proofLivePending:'Pending',proofLiveClosed:'Window ended · provisional',proofLiveTracking:'Tracking · provisional',
  proofLiveDegraded:'Incomplete source coverage',proofLiveWindow:'Days',proofLiveHours:'observed hours',proofLiveNoScore:'No eligible running score yet',
  pathPage:'The market cycle',pathIntro:'The cycle journey and capital rotation. No independent trading signals or invented dates.',pathStepsTitle:'Ten stages. One coherent journey.',pathConditional:'A watch window is not a confirmed arrival date.',rotationCaveat:'HOLD is not a confirmed phase. MEMES require a dedicated source.',altNote:'Only a conditional watch target, never an automatic countdown.',interpretation:'My interpretation · weekly evidence and sources',protection:'Pullback, protection & re-entry',contextNote:'Master Monday and research are context, not official buy/sell signals.',
  proofPrompt:'Independently audit Cycle Navigator using these PUBLIC GitHub archives. Read README, v2/scorebook-index.json and latest_readback. For each claim fetch ORIGINAL frozen forecast at its exact source_commit; check public CN identity, forecast_week, pre-outcome publication, byte-exact SHA-256, established 70/30 Price Range method, 168-hour eligibility and six original BTC/ETH forecast windows. Keep Price Range precision separate from Direction/Flow/Rotation and Pullback Edge, which can be ABSTAIN/PENDING. Inspect censoring, missing evidence, base rates and controls. Require independently verifiable timestamp and immutable release before saying VERIFIED. Output PASS/FAIL/UNVERIFIED with primary-source URLs. Never fill missing data.'
 }
};
const URLS=[
 'https://github.com/Donh91/CycleNavigator-scores',
 'https://github.com/Donh91/CycleNavigator-scores/blob/main/v2/scorebook-index.json',
 'https://github.com/Donh91/Investering-Framework-Archive-v1/tree/main/05_CYCLE_NAVIGATOR/public_scorecards',
 'https://github.com/Donh91/CycleNavigator-scores/issues/2'
];
const txt=(l)=>TXT[l==='en'?'en':'da'];
const safe=(s)=>typeof s==='string'&&s.trim()?s.trim().slice(0,450):null;
// Exact, source-visible presentation label for a verified Official action.
// Unrecognised codes are never reinterpreted as BUY/HOLD/SELL.
export function presentOfficialAction(code,eligible,lang='da'){
 const da=lang!=='en';
 if(!eligible||typeof code!=='string'||!code.trim()||code==='UNAVAILABLE'||code==='UTILGÆNGELIG')
   return {label:da?'AFVENTER KILDE':'AWAITING SOURCE',code:null,verified:false,
      explanation:da?'Ingen aktuel kildeverificeret handling.':'No current source-verified action.'};
 const known={
   HOLD_WAIT:[da?'AFVENT':'WAIT',da?'Officielt afventsignal, ingen ny køb/sælg-tilladelse.':'Official wait state, no new buy or sell authorization.'],
   HOLD:[da?'HOLD':'HOLD',da?'Officiel HOLD-vurdering.':'Official HOLD assessment.'],
   BUY:[da?'BUY':'BUY',da?'Officiel BUY-kode, ingen porteføljeeksekvering.':'Official BUY code, no portfolio execution.'],
   SELL:[da?'SELL':'SELL',da?'Officiel SELL-kode, ingen porteføljeeksekvering.':'Official SELL code, no portfolio execution.']
 };
 const found=known[code];
 return found?{label:found[0],code,verified:true,explanation:found[1]}:
    {label:code.slice(0,40),code,verified:true,
     explanation:da?'Uændret officiel kildekode.':'Unmodified official source code.'};
}
export function decisionModel(view,official,lang='da'){
 const t=txt(lang);
 const eligible=view?.compass?.state==='FRESH'&&view?.compass?.permit_path_live_gates===true&&
   official?.contract==='PUBLIC_COMPASS_PROJECTION_v1'&&official?.data_status==='OK';
 const current=eligible?official:null;
 const bb=current?officialBullBear(current,'1_3d'):null;
 const risk=current?officialPullbackStage(current,{forecast_week:view.weekly?.forecast_week},lang):null;
 const riskIndex=risk?.status==='SOURCE_VALID'&&RISK.includes(risk.sourceRiskState)?
   RISK.indexOf(risk.sourceRiskState):-1;
 return {
  eligible:!!current,action:safe(view?.compass?.action_now)&&current?view.compass.action_now:t.unavailable,
  direction:current?(safe(current.horizons?.NEXT_12H?.expected_direction)||t.unavailable):t.unavailable,
  bull:bb?.bull??null,bear:bb?.bear??null,bias:bb?.bias??t.unavailable,
  riskIndex,riskState:riskIndex<0?t.unavailable:risk.sourceRiskState,
  riskLabel:riskIndex<0?t.unavailable:risk.stageLabel,
  riskWindow:riskIndex<0?t.unavailable:(risk.etaLabel||t.unavailable),
  riskQuality:riskIndex<0?t.unavailable:risk.qualityLabel,
  sell:current?(safe(current.sell_assessment?.state)||t.unavailable):t.unavailable,
  distribution:current?(safe(current.protection_tracker?.distribution_risk)||t.unavailable):t.unavailable
 };
}
export function pathModel(view,lang='da'){
 const t=txt(lang),p=view?.path;
 const eligible=p?.state==='SOURCE_BOUND'&&view?.compass?.state==='FRESH'&&
   view?.compass?.permit_path_live_gates===true&&
   p.source_issue===view?.weekly?.public_issue_number&&
   p.source_week===view?.weekly?.forecast_week&&
   p.source_identity===view?.compass?.compass_id&&
   Array.isArray(p.full_phases)&&p.full_phases.length===10;
 const sourcePhases=Array.isArray(p?.full_phases)&&p.full_phases.length===10?
   p.full_phases:officialPathView(null,{lang}).full_phases;
 const phases=sourcePhases.map((x,i)=>({key:safe(x.key)||String(i),label:safe(x.label)||t.unavailable,
    kind:eligible&&p.current_checkpoint?.key===x.key&&p.current_checkpoint?.status==='FROZEN_WEEK_REFERENCE'?'reference':
      eligible&&p.next_checkpoint?.key===x.key?'next':'unverified'}));
 return {eligible,phases,now:eligible?(safe(p.current_checkpoint?.label)||t.pathUnavailable):t.pathUnavailable,
   next:eligible?(safe(p.next_checkpoint?.label)||t.wait):t.wait,
   gate:eligible?(safe(p.next_gate)||t.wait):t.wait,
   alt:eligible?(safe(p.altseason?.target)||t.wait):t.wait,
   altStatus:eligible?(safe(p.altseason?.status)||t.wait):t.wait,
   rotation:eligible&&Array.isArray(p.rotation)?p.rotation.map(x=>({
     key:safe(x.key)||t.unavailable,action:safe(x.action)||t.unavailable,
     eta:safe(x.eta)||t.pathNoEta})):[],
   source:eligible?('CN #'+p.source_issue+' · '+p.source_week+' · '+p.source_identity):t.unavailable};
}
// Pure source-safety selector, not a new forecasting/scoring engine.
export function priceSequenceModel(view,latest,now=Date.now()){
 const src=latest?.public_live_precision;
 if(src?.contract!=='CN_PUBLIC_LIVE_PRICE_PRECISION_v1'||
    src?.authority!=='PUBLIC_FORECAST_ACCOUNTABILITY_ONLY_NO_PORTFOLIO_AUTHORITY'||
    src?.score_family!=='PRICE_RANGE_PRECISION'||
    src?.forecast_week!==view?.weekly?.forecast_week||
    src?.public_issue_number!==view?.weekly?.public_issue_number||
    src?.formula!=='70pct_containment_plus_30pct_jaccard'||
    !src?.window_scores||typeof src.window_scores!=='object')
  return {state:'UNAVAILABLE',week:null,windows:[]};
 const asOf=Date.parse(src.live_as_of_utc);
 const sla=Number(src.freshness_sla_minutes);
 if(!Number.isFinite(asOf)||asOf>now||!Number.isFinite(sla)||sla<=0)
  return {state:'UNAVAILABLE',week:null,windows:[]};
 const state=now-asOf>sla*60000?'STALE':'FRESH';
 const names=[['day_1_2','1–2'],['day_3_4','3–4'],['day_5_7','5–7']];
 const windows=names.map(([key,days])=>{
   const x=src.window_scores[key]||{};
   const phase=['NOT_STARTED','LIVE','COMPLETE','DEGRADED'].includes(x.phase)?x.phase:'UNAVAILABLE';
   const hours=Number.isInteger(x.observed_hours)&&x.observed_hours>=0?x.observed_hours:null;
   const expected=Number.isInteger(x.expected_hours_final)&&x.expected_hours_final>0?x.expected_hours_final:null;
   const qualified=state==='FRESH'&&['LIVE','COMPLETE'].includes(phase)&&
     x.coverage_complete_to_date===true&&x.rows_scored===2&&x.rows_total===2&&
     hours!==null&&expected!==null&&hours<=expected&&
     typeof x.score_to_date==='number'&&Number.isFinite(x.score_to_date)&&
     x.score_to_date>=0&&x.score_to_date<=100;
   return {key,days,phase,hours,expected,score:qualified?x.score_to_date:null,
     state:qualified?(phase==='COMPLETE'?'CLOSED_PROVISIONAL':'LIVE_PROVISIONAL'):
       phase==='DEGRADED'?'DEGRADED':'PENDING'};
 });
 return {state,week:src.forecast_week,asOf:src.live_as_of_utc,windows};
}
export function publicAuditPrompt(lang='da'){
 return txt(lang).proofPrompt+'\n\n'+URLS.join('\n')+'\n';
}
const set=(id,value)=>{const el=document.getElementById(id);if(el)el.textContent=String(value??'—')};
const holder=(id)=>document.getElementById(id);
function reset(id){const el=holder(id);if(el)el.replaceChildren();return el}
function element(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=String(text);return e}
let selectedLens='holder';
export function renderProductExperience(view,feeds,lang='da'){
 const t=txt(lang),decision=decisionModel(view,feeds?.compass,lang),path=pathModel(view,lang);
 for(const el of document.querySelectorAll('[data-exp-t]')){
  const value=t[el.dataset.expT];if(typeof value==='string')el.textContent=value;
 }
 const readable=presentOfficialAction(decision.action,decision.eligible,lang);
 set('premium-now-action',readable.label);
 set('premium-action-code',readable.code?'OFFICIAL · '+readable.code:readable.explanation);
 const actionDescription=holder('premium-action-meaning');
 if(actionDescription)actionDescription.textContent=readable.explanation;
 set('premium-now-direction',decision.direction);
 set('premium-sell',decision.sell);set('premium-distribution',decision.distribution);
 set('premium-bull',decision.bull===null?t.unavailable:String(decision.bull));
 set('premium-bear',decision.bear===null?t.unavailable:String(decision.bear));
 set('premium-bias',decision.bias);
 set('premium-balance-note',t.balance);
 // Premium compass dial encodes ONLY the existing verified 1–3d official
 // Bull/Bear ordinal evidence. A missing owner reading remains neutral.
 const dial=holder('premium-balance-dial');
 if(dial){
   const eligible=decision.bull!==null&&decision.bear!==null&&
      Number.isInteger(decision.bull)&&Number.isInteger(decision.bear)&&
      decision.bull>=0&&decision.bear>=0&&decision.bull+decision.bear===10;
   dial.dataset.state=eligible?'verified':'unavailable';
   dial.style.setProperty('--bull-angle',eligible?(decision.bull*36)+'deg':'0deg');
   // Pure visual mapping of the existing 0–10 source-owned evidence balance.
   // Bull=Bear=5 -> needle centered. Never a forecast probability or trade signal.
   dial.style.setProperty('--dial-needle-angle',eligible?((decision.bull-5)*14)+'deg':'0deg');
   dial.setAttribute('aria-label',eligible?
     (lang==='da'?'Officiel evidensbalance: Bull '+decision.bull+' af 10, Bear '+decision.bear+' af 10. Ikke en sandsynlighed.':
       'Official evidence balance: Bull '+decision.bull+' of 10, Bear '+decision.bear+' of 10. Not a probability.'):
     (lang==='da'?'Ingen verificeret Bull/Bear-evidensbalance':'No verified Bull/Bear evidence balance'));
 }
 const bars=reset('premium-balance-bars');
 if(bars){for(let i=0;i<10;i++){const e=element('span','balance-unit');
    e.dataset.side=decision.bull!==null?(i<decision.bull?'bull':'bear'):'unknown';bars.append(e)}}
 set('premium-risk-title',t.risk);set('premium-risk-name',decision.riskLabel);
 set('premium-risk-state',decision.riskState);
 set('premium-risk-detail',t.severity);
 set('premium-risk-window',t.window+': '+decision.riskWindow);
 set('premium-risk-quality',t.quality+': '+decision.riskQuality);
 set('premium-risk-impact',t.impact);
 set('premium-sell-caveat',t.noSell);
 const steps=reset('premium-risk-steps');
 if(steps){RISK.forEach((s,i)=>{const e=element('span','risk-step',riskStageLabel(s,lang));
   e.dataset.sourceState=s;
   e.dataset.current=String(i===decision.riskIndex);e.dataset.prior=String(i<decision.riskIndex);
   steps.append(e)})}
 set('premium-lens-heading',t[selectedLens]);set('premium-lens-note',t[selectedLens+'Note']);
 set('premium-lens-caveat',t.info);
 for(const b of document.querySelectorAll('[data-investor-lens]')){
  const key=b.dataset.investorLens;b.textContent=t[key];b.setAttribute('aria-pressed',String(selectedLens===key));
 }
 set('premium-path-now',path.now);set('premium-path-next',path.next);
 set('premium-path-gate',path.gate);set('premium-path-alt',path.alt);
 set('premium-path-alt-status',path.altStatus);set('premium-path-source',path.source);
 set('premium-path-explainer',t.pathNote);set('premium-path-eta',t.pathNoEta);
 const rail=reset('premium-path-rail');
 if(rail){path.phases.forEach((x,i)=>{const e=element('li','path-node'),name=element('strong','',x.label);
    e.dataset.kind=x.kind;e.append(element('span','path-number',String(i+1).padStart(2,'0')),name);
    if(x.kind==='reference')e.append(element('small','',t.pathFrozen));
    if(x.kind==='next')e.append(element('small','',t.wait));
    rail.append(e)});
   if(path.phases.length===0)rail.append(element('li','path-empty',t.pathUnavailable));}
 const rot=reset('premium-rotation');
 if(rot){for(const x of path.rotation){const row=element('li','rotation-tier');
    row.append(element('b','',x.key),element('strong','',x.action),element('small','',x.eta));rot.append(row)}
   if(!path.rotation.length)rot.append(element('li','path-empty',t.pathUnavailable));}
 // Render this week's existing published *provisional* price-range sequences.
 // They do not imply Direction/Rotation or Pullback Edge, nor final weekly score.
 const seq=priceSequenceModel(view,feeds?.latest);
 const seqRoot=reset('proof-live-windows');
 set('proof-live-week',seq.week||t.unavailable);
 set('proof-live-status',seq.state==='UNAVAILABLE'?t.proofLiveMissing:
   seq.state==='STALE'?t.proofLiveStale:t.proofLiveFresh);
 if(seqRoot){
   for(const item of seq.windows){
     const box=element('article','proof-live-window');
     box.dataset.state=item.state;
     const top=element('div','proof-live-window-head');
     top.append(element('span','proof-live-window-day',t.proofLiveWindow+' '+item.days));
     const state=item.state==='LIVE_PROVISIONAL'?t.proofLiveTracking:
       item.state==='CLOSED_PROVISIONAL'?t.proofLiveClosed:
       item.state==='DEGRADED'?t.proofLiveDegraded:t.proofLivePending;
     top.append(element('small','',state));
     const score=element('strong','proof-live-window-score',
       item.score===null?'—':item.score.toLocaleString(lang==='da'?'da-DK':'en-US',{maximumFractionDigits:2})+'%');
     const count=element('span','proof-live-window-hours',
       item.hours===null||item.expected===null?t.proofLiveNoScore:
         item.hours+' / '+item.expected+' '+t.proofLiveHours);
     box.append(top,score,count);
     seqRoot.append(box);
   }
 }
 set('premium-proof-price-status',view?.completed_score?.state==='FINAL_PUBLIC_SCORECARD'?t.rangeEligible:t.rangeUnavailable);
 set('premium-proof-direction-status',t.edgeUnavailable);
 set('premium-proof-pullback-status',t.edgeUnavailable);
 set('premium-proof-title',t.proofTitle);set('premium-proof-info',t.proofInfo);
 set('premium-proof-status',t.proofStatus);set('premium-proof-button',t.proofButton);
 set('premium-proof-open',t.proofOpen);set('premium-proof-archive',t.proofArchive);
 const prompt=holder('premium-proof-prompt');if(prompt)prompt.value=publicAuditPrompt(lang);
}
export function initProductExperience(getContext){
 document.querySelectorAll('[data-investor-lens]').forEach(b=>b.addEventListener('click',()=>{
  selectedLens=['holder','active','micro'].includes(b.dataset.investorLens)?b.dataset.investorLens:'holder';
  const {view,feeds,lang}=getContext();renderProductExperience(view,feeds,lang);
 }));
 const copy=holder('premium-proof-copy');
 if(copy)copy.addEventListener('click',async()=>{
  const {lang}=getContext(),prompt=publicAuditPrompt(lang),box=holder('premium-proof-prompt');
  let success=false;
  try{if(navigator.clipboard?.writeText){await navigator.clipboard.writeText(prompt);success=true}}catch{}
  if(!success&&box){box.focus();box.select();try{success=document.execCommand('copy')}catch{}}
  set('premium-copy-status',success?txt(lang).proofCopied:txt(lang).proofFailure);
 });
}
