// Source-only view: categorical positions, not elapsed time, price or probability.
const positions=Object.freeze({
 PRE_ROTATION:[85,77],ROTATION:[111,49],BROAD_ALTSEASON:[137,29],
 PARABOLIC_ALTSEASON:[153,24],DISTRIBUTION:[170,24]
});
const names={PRE_ROTATION:'Expansion',ROTATION:'Expansion',BROAD_ALTSEASON:'Expansion',PARABOLIC_ALTSEASON:'Expansion',DISTRIBUTION:'Distribution'};
const tr=(lang,da,en)=>lang==='en'?en:da;
function asOf(pkg,latest){
 const n=pkg?.generated_unix;
 if(!Number.isInteger(n)||n<=0||n>8640000000000)return null;
 const ms=n*1000, delivery=Date.parse(latest?.generated_at||'');
 if(!Number.isFinite(delivery)||ms>delivery)return null;
 return new Date(ms).toISOString();
}
export function cycleMapModel({view,latest,lang='da'}={}){
 const pkg=latest?.package,stamp=asOf(pkg,latest),ctx=pkg?.market_cycle_context;
 const aligned=view?.delivery_health==='FRESH'&&['OK','DEGRADED'].includes(view?.weekly?.state)&&
  view.weekly.public_issue_number===latest?.public_series?.current_public_projection?.public_issue_number&&
  view.weekly.forecast_week===latest?.public_series?.current_public_projection?.forecast_week&&
  view.weekly.machine_issue_number===pkg?.issue_number&&!!stamp;
 const complete=aligned&&view.weekly.state==='OK'&&['OK','PASS'].includes(pkg?.status);
 const code=complete&&typeof ctx?.current_phase==='string'?ctx.current_phase:null;
 const phase=code&&Object.hasOwn(positions,code)?{xy:positions[code],label:names[code],code}:null;
 const path=view?.path,c=view?.compass;
 const joined=complete&&path?.state==='SOURCE_BOUND'&&c?.state==='FRESH'&&c.permit_path_live_gates===true&&
   path.source_identity===c.compass_id&&path.source_issue===view.weekly.public_issue_number&&path.source_week===view.weekly.forecast_week;
 // The current rotation contract only confirms a historical BTC leadership
 // reference. HOLD is not flow, protection is not reset, no other stage guessed.
 const rotation=joined&&path.current_checkpoint?.key==='BTC'&&path.current_checkpoint?.status==='FROZEN_WEEK_REFERENCE'?{x:20,label:'BTC',kind:'FROZEN_WEEK_REFERENCE'}:null;
 const gate=aligned&&typeof ctx?.next_gate==='string'&&ctx.next_gate.trim()?ctx.next_gate.trim():null;
 return {phase,rotation,gate,asOf:aligned?stamp:null,rotationAsOf:rotation?stamp:null,
  weeklyHealth:aligned?view.weekly.state:'UNAVAILABLE',confidence:'UNQUANTIFIED',
  evidence:'HYPOTHESIS',authority:'PRESENTATION_ONLY'};
}
export const cycleMapMarkup=`<section class="cn-cycle-map" id="cn-cycle-map" data-contract="CN_WHERE_ARE_WE_MAP_v1" aria-labelledby="cn-map-title">
 <header><small>HYPOTHESIS · MODEL VIEW</small><h3 id="cn-map-title">Hvor er vi?</h3></header>
 <svg viewBox="0 0 340 140" aria-hidden="true" focusable="false" class="cn-map-wave">
  <rect class="cn-map-bull" x="12" y="16" width="158" height="96" rx="3"/><rect class="cn-map-bear" x="170" y="16" width="158" height="96" rx="3"/>
  <g class="cn-map-engrave"><path d="M20 16V112 M63 16V112 M170 16V112 M277 16V112 M320 16V112"/></g>
  <path class="cn-map-path" d="M20 100 C45 100 63 100 85 77 C96 65 100 59 111 49 C122 39 127 33 137 29 C144 26 149 24 153 24 L170 24 C227 24 250 100 320 100"/>
  <g class="cn-map-label" text-anchor="middle"><text x="91" y="12">BULL</text><text x="249" y="12">BEAR</text>
  <text id="cn-map-acc-label" x="34" y="129">Akkum.</text><text id="cn-map-exp-label" x="111" y="129">Ekspansion</text><text id="cn-map-dist-label" x="192" y="129">Distribution</text><text id="cn-map-con-label" x="282" y="129">Kontraktion</text></g>
  <circle id="cn-map-phase-dot" class="cn-map-dot" cx="0" cy="0" r="5" hidden/>
 </svg>
 <p class="cn-map-state" id="cn-map-phase-text">Aktuel fase ikke dokumenteret.</p>
 <svg viewBox="0 0 340 57" aria-hidden="true" focusable="false" class="cn-map-rotation">
  <path class="cn-map-engrave" d="M20 14H320 M20 7V21 M80 7V21 M150 7V21 M230 7V21 M320 7V21"/>
  <g class="cn-map-label" text-anchor="middle"><text x="20" y="36">BTC</text><text x="80" y="36">ETH</text><text id="cn-map-large-label" x="150" y="36">Store</text><text id="cn-map-alt-label" x="230" y="36">Mellem / små</text><text x="230" y="49">Altseason</text><text id="cn-map-reset-label" x="312" y="36">BTC / stables</text></g>
  <circle id="cn-map-rotation-dot" class="cn-map-dot" cx="0" cy="14" r="5" hidden/>
 </svg>
 <p class="cn-map-state" id="cn-map-rotation-text">Rotation ikke bekræftet.</p>
 <p class="cn-map-caption" id="cn-map-caption">Skematisk forløb, ikke pris, tid eller sandsynlighed.</p>
 <p class="cn-map-next"><strong id="cn-map-next-label">Næste bekræftelse</strong><span id="cn-map-next">Afventer kilde.</span></p>
 <details><summary id="cn-map-evidence">Kilde og evidens</summary><p id="cn-map-facts">FACT · Afventer kilde.</p><p id="cn-map-limits">HYPOTHESIS · Ingen testet faseklassifikation.</p><a href="#premium-path-rail" id="cn-map-link">Detaljeret cyklusforløb</a></details>
 </section>`;
export function renderCycleMap(doc,{view,latest,lang='da'}={}){
 const el=id=>doc.getElementById(id),root=el('cn-cycle-map');if(!root)return;
 const m=cycleMapModel({view,latest,lang}), t=(da,en)=>tr(lang,da,en);
 const set=(id,v)=>{const e=el(id);if(e)e.textContent=v;};
 const dot=(id,xy)=>{const e=el(id);if(!e)return;if(xy){e.setAttribute('cx',String(xy[0]));e.setAttribute('cy',String(xy[1]));e.removeAttribute('hidden');}else e.setAttribute('hidden','');};
 dot('cn-map-phase-dot',m.phase?.xy);dot('cn-map-rotation-dot',m.rotation?[m.rotation.x,14]:null);
 root.dataset.phase=m.phase?.code||'UNAVAILABLE';root.dataset.rotation=m.rotation?.kind||'UNAVAILABLE';
 set('cn-map-title',t('Hvor er vi?','Where are we?'));
 set('cn-map-acc-label',t('Akkum.','Accum.'));
 set('cn-map-exp-label',t('Ekspansion','Expansion'));
 set('cn-map-dist-label','Distribution');set('cn-map-con-label',t('Kontraktion','Contraction'));
 set('cn-map-large-label',t('Store','Large caps'));set('cn-map-alt-label',t('Mellem / små','Mid / small'));set('cn-map-reset-label','BTC / stables');
 const conf=t('sikkerhed ikke kvantificeret','confidence unquantified');
 set('cn-map-phase-text',m.phase?(m.phase.label==='Expansion'?t('Bull / ekspansion','Bull / expansion'):t('Distribution','Distribution'))+' · '+conf+' · '+m.asOf:t('Aktuel fase ikke dokumenteret.','Current phase not established.'));
 set('cn-map-rotation-text',m.rotation?t('BTC · seneste ugereference, ikke live kapitalflow','BTC · previous weekly reference, not live capital flow')+' · '+conf+' · '+m.rotationAsOf:t('Aktuel rotation ikke bekræftet.','Current rotation not confirmed.'));
 set('cn-map-caption',t('Skematisk forløb, ikke pris, tid eller sandsynlighed.','Schematic sequence, not price, time or probability.'));
 set('cn-map-next-label',t('Næste bekræftelse · model view','Next confirmation · model view'));
 set('cn-map-next',m.gate||t('Ikke dokumenteret endnu.','Not documented yet.'));
 set('cn-map-evidence',t('Kilde og evidens','Source and evidence'));
 set('cn-map-facts','FACT · '+(m.asOf?m.weeklyHealth+' · '+m.asOf:t('Kilde utilgængelig','Source unavailable')));
 set('cn-map-limits',t('HYPOTHESIS · Ugeklassifikation og rotationssekvens er ikke testet. Ingen position udledes af HOLD, pris eller en fremtidig prognose.','HYPOTHESIS · Weekly classification and rotation sequence are not tested. No position inferred from HOLD, price or a forward forecast.'));
 set('cn-map-link',t('Detaljeret cyklusforløb','Detailed cycle route'));
}
