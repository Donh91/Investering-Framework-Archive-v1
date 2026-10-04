(() => {
'use strict';

const esc=v=>String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#039;');
const short=(v,n=240)=>{const s=String(v??'').trim();return s.length>n?`${s.slice(0,n-1).trim()}…`:s};
const mean=a=>a.length?a.reduce((x,y)=>x+y,0)/a.length:null;
const pct=v=>Number.isFinite(v)?`${Math.round(v)}%`:'—';
const clamp=n=>Math.max(0,Math.min(100,Number(n)||0));
const state=v=>{const s=String(v||'').toUpperCase();if(/PAUSED|INACTIVE|DEFENSIVE/.test(s))return'pause';if(/ACTIVE WATCH|RELATIVE RESILIENCE|ON WATCH|WATCH/.test(s))return'watch';if(/MAJOR LIQUIDITY ANCHOR|NO CONFIRMED MARKET BREAKDOWN|HOLD/.test(s))return'hold';if(/UNCONFIRMED|SELECTIVE PARTICIPATION|WAIT/.test(s))return'wait';if(/ACTIVE|CONFIRMED/.test(s))return'active';return'unknown'};
const statusLabel=v=>({active:'ACTIVE',hold:'HOLD',watch:'WATCH',wait:'WAIT',pause:'WAIT',unknown:'PENDING'}[state(v)]||'PENDING');
const actionCopy=v=>({active:'Risk can stay active here while confirmation holds.',hold:'Hold existing exposure. Do not add from this segment alone.',watch:'Watch closely. Prepare, but wait for confirmation.',wait:'Do not broaden risk here yet.',pause:'Wait for the preceding rotation to confirm before adding here.',unknown:'Awaiting enough evidence for a public call.'}[state(v)]||'Awaiting evidence.');
const actionTitle=s=>({HOLD:'HOLD',WAIT:'WAIT',PREPARE:'PREPARE',SELECTIVE:'ADD SELECTIVELY','PROTECT CAPITAL':'REDUCE RISK','BROADER DEPLOYMENT':'ADD BROADLY'}[String(s||'').toUpperCase()]||'WAIT');
const cleanPhase=v=>String(v||'').replace(/^\d+\.\s*/,'').replace(/\s[—–-]\s(ACTIVE WATCH|ACTIVE|UNCONFIRMED|INACTIVE|PAUSED).*$/i,'').trim();

function investorText(raw){
  let s=String(raw||'').trim();
  if(!s)return'';
  s=s.replace(/HANDLEKOMPAS/gi,'Market Compass').replace(/\bW\d+\b/g,'This week')
    .replace(/MASTER MONDAY/gi,'weekly review')
    .replace(/FROZEN CYCLE NAVIGATOR/gi,'weekly outlook')
    .replace(/CANONICAL CONFIRMATION/gi,'confirmed signal')
    .replace(/CANONICAL/gi,'confirmed')
    .replace(/NATIVE STATE/gi,'market evidence')
    .replace(/SOURCE HEALTH/gi,'signal confidence')
    .replace(/DATA HEALTH/gi,'signal confidence')
    .replace(/ETHBTC/gi,'Ethereum vs Bitcoin')
    .replace(/ETH\/BTC/gi,'Ethereum vs Bitcoin')
    .replace(/BREADTH/gi,'market participation')
    .replace(/NO ROTATION/gi,'no broad altcoin rotation')
    .replace(/SELECTIVE REPAIR/gi,'selective market repair')
    .replace(/FRAGILE TRANSLATION/gi,'fragile follow-through')
    .replace(/_/g,' ')
    .replace(/\bGTE\b/gi,'at least')
    .replace(/\bLT\b/gi,'below')
    .replace(/\s+/g,' ')
    .trim();
  return s;
}

function gate(raw,type='confirm'){
  const s=String(raw||'').trim();
  if(!s)return type==='confirm'?'Wait for stronger Ethereum leadership and broader market participation.':'Renewed weakness would delay the next rotation.';
  if(/ETHBTC_STRENGTH.*BREADTH/i.test(s))return'Ethereum strengthens relative to Bitcoin while participation broadens across the market.';
  if(/BREADTH_LT|ETHBTC_WEAKENS/i.test(s))return'Ethereum loses relative strength while participation across the market weakens.';
  if(/HEALTH|DEGRADED|SOURCE/i.test(s))return type==='confirm'?'Signal confidence returns to normal alongside stronger market confirmation.':'Signal confidence becomes too limited to support a new risk call.';
  return investorText(s);
}

function phaseCopy(raw){
  const s=String(raw||'');
  if(/VOLATILE.*CONSOLIDATION|PULLBACK RISK/i.test(s))return'Volatile consolidation';
  if(/SELECTIVE REPAIR|FRAGILE/i.test(s))return'Fragile market repair';
  if(/EARLY ROTATION/i.test(s))return'Early rotation watch';
  if(/BROAD.*EXPANSION|ALTSEASON/i.test(s))return'Broad risk expansion';
  return investorText(cleanPhase(s))||'Market transition';
}

function stageName(raw,index){
  const s=String(raw||'').toLowerCase();
  if(/volatile|consolidation|pullback/.test(s))return'Consolidation / transition';
  if(/eth-relative stabilization|ethereum.*stabil/.test(s))return'Ethereum stabilises vs Bitcoin';
  if(/selective.*eth|large-cap leadership|large cap leadership/.test(s))return'Ethereum + large caps strengthen';
  if(/mid-cap|midcap/.test(s))return'Mid-cap participation broadens';
  if(/small.*micro|small-cap|microcap/.test(s))return'Small & micro caps expand';
  if(/broad altseason|mania|high-risk/.test(s))return'Broad risk expansion';
  if(/bitcoin|btc/.test(s))return'Bitcoin leadership';
  if(/breadth|broad|altcoin/.test(s))return'Broad altcoin participation';
  return phaseCopy(raw)||`Stage ${index+1}`;
}

function parseRangeScore(text){
  const s=String(text||'').trim();if(!s)return null;
  const combined=s.match(/Combined\s+(\d+(?:\.\d+)?)/i);if(combined)return Number(combined[1]);
  const labelled=[...s.matchAll(/\b(?:BTC|ETH)\s+(\d+(?:\.\d+)?)/gi)].map(m=>Number(m[1])).filter(Number.isFinite);
  if(labelled.length)return mean(labelled);
  const exact=s.match(/^\s*(\d+(?:\.\d+)?)\s*$/);return exact?Number(exact[1]):null;
}

function parseComponentScores(text){
  const s=String(text||'').trim();if(!s)return[];
  const values=[];
  for(const m of s.matchAll(/(\d+(?:\.\d+)?)\s*\/\s*(\d+(?:\.\d+)?)/g)){const a=Number(m[1]),b=Number(m[2]);if(Number.isFinite(a)&&Number.isFinite(b)&&b>0)values.push(a/b*100);}
  const noRatios=s.replace(/\d+(?:\.\d+)?\s*\/\s*\d+(?:\.\d+)?/g,' ');
  const labelled=[...noRatios.matchAll(/\b(?:BTC|ETH|Cycle|Regime|Rotation|Breadth|Structural|Structure|Leadership|Direction|Timing|Phase)\s+(\d+(?:\.\d+)?)/gi)].map(m=>Number(m[1])).filter(Number.isFinite);
  values.push(...labelled);
  if(!labelled.length&&/^\s*\d+(?:\.\d+)?\s*$/.test(noRatios))values.push(Number(noRatios.trim()));
  const hits=(s.match(/\bHIT\b/gi)||[]).length,misses=(s.match(/\bMISS\b/gi)||[]).length;
  for(let i=0;i<hits;i++)values.push(100);for(let i=0;i<misses;i++)values.push(0);
  return values.filter(v=>Number.isFinite(v)&&v>=0&&v<=100);
}

function publicScores(record){
  const price=parseRangeScore(record.range_display);
  const separatedMarket=['LEGACY_PRE_V2','MARKET_STRUCTURE_V2'].includes(String(record?.structure_method||''));
  const marketValues=separatedMarket?parseComponentScores(record.structure_display):[...parseComponentScores(record.intraday_display),...parseComponentScores(record.structure_display)];
  const market=mean(marketValues);
  const archived=Number.isFinite(record.overall)?Number(record.overall):null;
  const explicitDerive = record?.allow_derived_overall;
  const mayDerive = explicitDerive === true || (explicitDerive == null && !['AUTOMATED_CANONICAL','DUAL_TRACK_CANONICAL','PRICE_PRECISION_PLUS_STRUCTURE_ANALYSIS'].includes(String(record?.era||'')));
  const weekly=archived??(mayDerive?mean([price,market].filter(Number.isFinite)):null);
  return{weekly,price,market,archived,derived:archived==null&&Number.isFinite(weekly)};
}

function sparkline(records){
  const rows=records.map(r=>({cn:r.cn,...publicScores(r)}));
  const w=760,h=220,pad=22,x=i=>pad+(w-pad*2)*(i/Math.max(1,rows.length-1)),y=v=>h-pad-(h-pad*2)*(clamp(v)/100);
  const points=key=>rows.filter(r=>Number.isFinite(r[key])).map(r=>`${x(rows.indexOf(r)).toFixed(1)},${y(r[key]).toFixed(1)}`).join(' ');
  return `<svg class="score-spark" viewBox="0 0 ${w} ${h}" role="img" aria-label="Historical Cycle Navigator scores"><line x1="${pad}" y1="${y(100)}" x2="${w-pad}" y2="${y(100)}"/><line x1="${pad}" y1="${y(75)}" x2="${w-pad}" y2="${y(75)}"/><line x1="${pad}" y1="${y(50)}" x2="${w-pad}" y2="${y(50)}"/><polyline class="series weekly" points="${points('weekly')}"/><polyline class="series price" points="${points('price')}"/><polyline class="series market" points="${points('market')}"/></svg>`;
}

let snapshot=null,refreshTimer=null;

function shell(){
  const main=document.querySelector('main');if(!main)return;
  let root=document.getElementById('publicProduct');
  if(!root){
    root=document.createElement('section');root.id='publicProduct';root.className='public-product';
    root.innerHTML='<nav class="product-tabs" aria-label="Cycle Navigator"><button class="active" data-tab="now">NOW</button><button data-tab="path">PATH</button><button data-tab="proof">PROOF</button></nav><div id="productNow" class="product-view active"></div><div id="productPath" class="product-view"></div><div id="productProof" class="product-view"></div>';
    main.prepend(root);
    root.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{root.querySelectorAll('[data-tab]').forEach(x=>x.classList.toggle('active',x===b));root.querySelectorAll('.product-view').forEach(x=>x.classList.toggle('active',x.id===`product${b.dataset.tab[0].toUpperCase()}${b.dataset.tab.slice(1)}`));window.scrollTo({top:Math.max(0,root.offsetTop-8),behavior:'smooth'});});
  }
  main.querySelectorAll(':scope > section:not(#publicProduct)').forEach(x=>x.classList.add('legacy-detail'));
  document.querySelector('.journey-nav-wrap')?.classList.add('legacy-detail');
}

async function json(u){const r=await fetch(`${u}?v=${Date.now()}`,{cache:'no-store'});if(!r.ok)throw Error(r.status);return r.json();}
async function jsonOptional(u){try{return await json(u);}catch{return null;}}
async function prices(){try{const r=await fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd',{cache:'no-store'}),d=await r.json(),b=+d.bitcoin?.usd,e=+d.ethereum?.usd;return b&&e?`BTC $${Math.round(b).toLocaleString()} · ETH $${Math.round(e).toLocaleString()} · ETH/BTC ${(e/b).toFixed(5)}`:null;}catch{return null;}}

function freshness(){
  const h=document.getElementById('productFreshness');if(!h||!snapshot)return;
  const a=snapshot.live_observation?.current_action||{},p=snapshot.package||{},d=a.generated_at?new Date(a.generated_at):p.generated_unix?new Date(+p.generated_unix*1000):null,n=new Date();
  const age=d?n-d:null,next=new Date(n),ownerMinute=12;next.setUTCSeconds(0,0);if(next.getUTCMinutes()<ownerMinute)next.setUTCMinutes(ownerMinute);else{next.setUTCHours(next.getUTCHours()+1);next.setUTCMinutes(ownerMinute);}
  const mins=x=>{const m=Math.max(0,Math.ceil(x/60000));return m>=60?`${Math.floor(m/60)}h ${m%60}m`:`${m} min`;};
  const stale=age!=null&&age>90*60*1000;
  const publicIssue=snapshot?.public_series?.current_public_projection?.public_issue_number;
  h.innerHTML=`<div><span>${stale?'LAST VERIFIED COMPASS':'MARKET COMPASS UPDATED'}</span><strong>${d?d.toLocaleString([],{day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'}):'Awaiting fresh data'}</strong><small>${age!=null?`${mins(age)} ago`:'No verified live timestamp'}</small></div><div><span>NEXT UPDATE</span><strong>${mins(next-n)}</strong><small>Expected after the next market-data cycle</small></div><div><span>CURRENT WEEKLY OUTLOOK</span><strong>CN #${esc(publicIssue??p.issue_number??'—')}</strong><small>Public-series numbering, unchanged by live updates</small></div>`;
}

function rotationEta(item){
  const explicit=item?.eta||item?.window||item?.timing;if(explicit)return investorText(explicit);
  return({active:'Now',hold:'Now · reassess on the next update',watch:'Next confirmation',wait:'No reliable estimate yet',pause:'No ETA until conditions improve',unknown:'No reliable estimate yet'})[state(item?.status)]||'No reliable estimate yet';
}

function structuralRotation(rows){
  rows=Array.isArray(rows)&&rows.length?rows:[];
  if(!rows.length)return '';
  return '<div class="capital-line structural-context-rail">'+rows.map((r,i)=>'<div class="capital-step"><div class="capital-node">'+esc(i+1)+'</div><div class="capital-copy"><div class="capital-title"><strong>'+esc(r.segment||'Segment')+'</strong><b>WEEKLY CONTEXT</b></div><p>'+esc(investorText(r.status||'No structural context published.'))+'</p></div></div>').join('')+'</div>';
}

function precisionLite(data){
  const live=data?.public_live_precision;
  if(live?.contract!=='CN_PUBLIC_LIVE_PRICE_PRECISION_v1')return '';
  const n=live.running_price_precision_pct===null||live.running_price_precision_pct===undefined?null:Number(live.running_price_precision_pct);
  const score=Number.isFinite(n)?n.toFixed(2).replace(/\.?0+$/,'')+'%':'—';
  const d=live.live_as_of_utc?new Date(live.live_as_of_utc):null;
  const ageMs=d&&Number.isFinite(d.getTime())?Date.now()-d.getTime():null;
  const sla=Math.max(30,Number(live.freshness_sla_minutes||90));
  const stale=ageMs===null||ageMs>sla*60*1000;
  const mins=ageMs===null?null:Math.max(0,Math.floor(ageMs/60000));
  const age=mins===null?'unknown age':mins>=60?Math.floor(mins/60)+'h '+(mins%60)+'m old':mins+' min old';
  const phase=!Number.isFinite(n)?'AWAITING':stale?'STALE':'LIVE';
  const stamp=v=>{const x=v?new Date(v):null;return x&&Number.isFinite(x.getTime())?x.toLocaleString('en-GB',{timeZone:'UTC',day:'2-digit',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit',hour12:false}).replace(',','')+' UTC':'—';};
  return '<section id="publicLiveAccountabilityLite" class="pa-lite'+(stale?' stale':'')+'">'
    +'<div class="pa-lite-mark"><i></i><span>WEEKLY TRACK RECORD · '+esc(phase)+'</span></div>'
    +'<div class="pa-lite-score"><strong>'+esc(score)+'</strong><small>provisional Price Range Precision</small></div>'
    +'<div class="pa-lite-meta"><span>CN #'+esc(live.public_issue_number)+' · '+esc(live.forecast_week)+'</span><b>Frozen '+esc(stamp(live.frozen_at_utc))+'</b><small>'+(stale?'Last complete observation ':'Live as of ')+esc(stamp(live.live_as_of_utc))+' · '+esc(age)+' · '+esc(live.completed_rows??0)+' settled / '+esc(live.live_rows??0)+' live</small></div>'
    +'<button type="button" data-pa-proof-native>View full scorecard →</button>'
    +'</section>';
}

function renderNow(data,px){
  const p=data.package||{},live=data.live_observation||{},a=live.current_action||{},st=String(a.stance||'WAIT').toUpperCase(),available=!!a.generated_at,limited=/DATA_DEGRADED/i.test(String(a.current||''));
  const marketPhase=phaseCopy(p.market_state||'');
  const next=investorText(a.next_days)||(`Stay ${actionTitle(st).toLowerCase()} while the next market confirmation develops.`);
  const confirm=gate(a.confirmation,'confirm'),risk=gate(a.invalidation,'risk');
  const headline=!available?'Fresh evidence is temporarily unavailable. No new risk call is inferred from price alone.':limited?'Signal confidence is temporarily limited. Keep risk contained until the evidence improves.':({HOLD:'Keep current positioning. Do not add broad market risk yet.',WAIT:'Stay patient. A broader risk-on move is not confirmed yet.',PREPARE:'Prepare for a possible shift, but wait for confirmation before adding broadly.',SELECTIVE:'Add selectively only. Broad market risk is not confirmed yet.','PROTECT CAPITAL':'Reduce risk and protect capital until conditions improve.','BROADER DEPLOYMENT':'Broader participation is confirmed enough to add risk across the market.'}[st]||'Keep the current stance until the evidence changes.');
  document.getElementById('productNow').innerHTML=`<div id="productFreshness" class="freshness-strip"></div><section class="action-hero"><div class="action-label">MARKET COMPASS</div><div class="action-word">${esc(available?actionTitle(st):'WAIT')}</div><p>${esc(headline)}</p><div class="hero-lines"><div><span>MARKET PHASE</span><strong>${esc(marketPhase)}</strong></div><div><span>NEXT 1–3 DAYS</span><strong>${esc(short(next,180))}</strong></div><div><span>NEXT CONFIRMATION</span><strong>${esc(short(confirm,180))}</strong></div><div class="risk-line"><span>RISK</span><strong>${esc(short(risk,170))}</strong></div></div></section><section class="context-row"><article><span>LIVE MARKET</span><strong>${esc(px||'Live prices temporarily unavailable')}</strong><small>Market context only. Prices cannot rewrite the weekly outlook.</small></article><article><span>THIS WEEK</span><strong>${esc(short(investorText(p.base_case_this_week||p.market_state)||'No public weekly summary available.',220))}</strong><small>Plain-English translation of the current weekly outlook.</small></article></section>${precisionLite(data)}`;
  freshness();
}

function pathEta(value){
  const s=investorText(value).trim();
  if(!s||/UNAVAILABLE|UNKNOWN|NO FIXED ETA|NO SUPPORTED ETA/i.test(s))return'NO SUPPORTED ETA';
  return s;
}
function pathStatus(value){
  const s=String(value||'').toUpperCase();
  const hit=s.match(/ACTIVE WATCH|NOT CONFIRMED|UNCONFIRMED|INACTIVE|PAUSED|HARD_WAIT|HARD WAIT|BUILDING|ELEVATED|WARNING|CONFIRMED|UNAVAILABLE|UNKNOWN|ACTIVE|WAIT|HOLD|HIGH|NORMAL|NONE/);
  return hit?hit[0].replace('_',' '):'PENDING';
}
function pathTone(value){
  const s=String(value||'').toUpperCase();
  if(/INACTIVE|UNAVAILABLE|UNKNOWN|PAUSED/.test(s))return'unknown';
  if(/NOT CONFIRMED|UNCONFIRMED|HARD_WAIT|HARD WAIT|WAIT|ELEVATED|HIGH/.test(s))return'wait';
  if(/ACTIVE WATCH|BUILDING|WATCH|WARNING/.test(s))return'watch';
  if(/HOLD|NORMAL|NONE/.test(s))return'hold';
  if(/CONFIRMED|ACTIVE/.test(s))return'active';
  return'unknown';
}
function adaptiveStageTitle(raw,index){
  const s=String(raw||'').toLowerCase();
  if(/short-horizon alt participation/.test(s))return'Short-horizon alt participation';
  if(/eth-relative stabilization/.test(s))return'Ethereum stabilises vs Bitcoin';
  if(/large-cap and midcap transmission/.test(s))return'Large + mid-cap transmission';
  if(/small- and microcap transmission/.test(s))return'Small + micro-cap transmission';
  if(/broad, multi-horizon altseason|broad.*altseason/.test(s))return'Broad altseason confirmation';
  return stageName(raw,index);
}
function utcLabel(value){
  if(!value)return'—';
  const d=new Date(value);if(!Number.isFinite(d.getTime()))return'—';
  return d.toLocaleString('en-GB',{timeZone:'UTC',day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit',hour12:false}).replace(',','')+' UTC';
}
function compassSegment(compass,segment){
  return (Array.isArray(compass?.capitalization_ladder)?compass.capitalization_ladder:[]).find(x=>x?.segment===segment)||null;
}
function liveGateItem(label,status,eta,reason){
  return {label,status:pathStatus(status),tone:pathTone(status),eta:pathEta(eta),reason:investorText(reason)||'No additional governed explanation is published.'};
}
function adaptiveGateRows(compass,index){
  if(compass?.contract!=='PUBLIC_COMPASS_PROJECTION_v1'){
    return [liveGateItem('OFFICIAL COMPASS','UNAVAILABLE',null,'A fresh Official Compass is required before the live gate can update.')];
  }
  const h=compass.horizons||{};
  const seg=s=>compassSegment(compass,s);
  if(index===0){
    const x=h.NEXT_1_3D||{};
    return [liveGateItem('1–3D MARKET',x.action_posture||x.state,x.eta,x.expected_path)];
  }
  if(index===1){
    const x=seg('ETH')||{};
    return [liveGateItem('ETH',x.status||x.action,x.eta,x.reason)];
  }
  if(index===2){
    return ['LARGE_CAPS','MID_CAPS'].map(s=>{const x=seg(s)||{};return liveGateItem(s.replace('_',' '),x.status||x.action,x.eta,x.reason);});
  }
  if(index===3){
    return ['SMALL_CAPS','MICROCAPS'].map(s=>{const x=seg(s)||{};return liveGateItem(s.replace('_',' '),x.status||x.action,x.eta,x.reason);});
  }
  const x=h.CYCLE_ALTCOINS_3_8W||{};
  return [liveGateItem('BROAD ALTCOINS',x.action_posture||x.state,x.eta,x.expected_path)];
}
function adaptiveRotationTimeline(pkg,compass){
  const raw=Array.isArray(pkg?.altseason_countdown)?pkg.altseason_countdown:[];
  if(!raw.length)return '<section class="adaptive-path empty"><span>CYCLE PATH · ADAPTIVE TIMELINE</span><strong>No frozen Monday path is published.</strong><p>The site will not create a countdown without a governed baseline.</p></section>';
  const frozenCurrent=raw.findIndex(x=>/ACTIVE WATCH|\bACTIVE\b/i.test(String(x?.phase||'')));
  const compassStatus=compass?.data_status||'UNAVAILABLE';
  const cards=raw.map((x,i)=>{
    const gates=adaptiveGateRows(compass,i);
    const gateHtml=gates.map(g=>'<div class="adaptive-live-row tone-'+esc(g.tone)+'"><div><span>'+esc(g.label)+'</span><b>'+esc(g.status)+'</b></div><strong>'+esc(g.eta)+'</strong></div>').join('');
    const gateReasons=gates.map(g=>'<div class="adaptive-detail-row"><b>'+esc(g.label)+'</b><p>'+esc(short(g.reason,220))+'</p></div>').join('');
    const current=frozenCurrent>=0&&i===frozenCurrent;
    return '<article class="adaptive-stage'+(current?' baseline-current':'')+'">'
      +'<header><i>'+esc(i+1)+'</i><div><span>'+(current?'MONDAY · YOU ARE HERE':'MONDAY BASELINE')+'</span><strong>'+esc(adaptiveStageTitle(x.phase,i))+'</strong></div><b class="baseline-tone tone-'+esc(pathTone(x.phase))+'">'+esc(pathStatus(x.phase))+'</b></header>'
      +'<div class="adaptive-window"><span>MONDAY WINDOW</span><strong>'+esc(pathEta(x.window))+'</strong></div>'
      +'<div class="adaptive-live"><span class="adaptive-live-title">LIVE GATE</span>'+gateHtml+'</div>'
      +'<details><summary>What moves this stage?</summary><div class="adaptive-detail-row"><b>MONDAY BASELINE</b><p>'+esc(short(investorText(x.phase),260))+'</p></div>'+gateReasons+'</details>'
      +'</article>';
  }).join('');
  return '<section class="adaptive-path" data-contract="CN_ADAPTIVE_PATH_PRESENTATION_v1">'
    +'<header class="adaptive-head"><div><span>CYCLE PATH · ADAPTIVE TIMELINE</span><h3>Frozen Monday. Adaptive live gates.</h3><p>The Monday path never moves. Live gates refresh from the Official Compass and may tighten, delay or lose an ETA as evidence changes.</p></div>'
    +'<aside><span>LIVE OWNER</span><strong>'+esc(compassStatus)+'</strong><small>'+esc(utcLabel(compass?.issued_at_utc))+'</small></aside></header>'
    +'<div class="adaptive-legend"><span><i class="frozen"></i>Monday baseline</span><span><i class="live"></i>Official Compass live gate</span><b>ETA windows only · no client-side countdown synthesis</b></div>'
    +'<div class="adaptive-stage-grid">'+cards+'</div>'
    +'</section>';
}
function exitRiskClock(compass){
  const p=compass?.protection_tracker||{},sell=compass?.sell_assessment||{};
  const valid=compass?.contract==='PUBLIC_COMPASS_PROJECTION_v1';
  const rows=[
    {label:'PULLBACK / RETEST',status:valid?p.pullback_risk_state:'UNAVAILABLE',eta:valid?p.eta_window:null,reason:valid?p.pullback_class:'A fresh Official Compass is required.'},
    {label:'DISTRIBUTION',status:valid?p.distribution_risk:'UNAVAILABLE',eta:null,reason:valid?(Array.isArray(p.decisive_public_drivers)&&p.decisive_public_drivers.length?p.decisive_public_drivers[0]:'No governed distribution explanation is published.'):'A fresh Official Compass is required.'},
    {label:'EXIT WINDOW',status:valid?sell.state:'UNAVAILABLE',eta:valid?sell.eta:null,reason:valid?sell.reason:'A governed sell/trim owner is unavailable.'}
  ];
  return '<section class="exit-clock">'
    +'<header><div><span>EXIT RISK CLOCK</span><h3>Protection can accelerate independently of altseason.</h3><p>Distribution does not wait for every rotation stage to complete. This lane is owned by the existing protection and sell-assessment contracts.</p></div><b>NO FRONTEND SELL RULE</b></header>'
    +'<div class="exit-rail">'+rows.map((r,i)=>'<article class="tone-'+esc(pathTone(r.status))+'"><i>'+esc(i+1)+'</i><div><span>'+esc(r.label)+'</span><strong>'+esc(pathStatus(r.status))+'</strong><b>ETA · '+esc(pathEta(r.eta))+'</b><p>'+esc(short(investorText(r.reason),190))+'</p></div></article>').join('')+'</div>'
    +'<footer><span>Re-entry</span><strong>'+esc(pathStatus(valid?p.reentry_state:'UNAVAILABLE'))+'</strong><p>'+esc(short(investorText(valid?p.reentry_message:'Re-entry review is unavailable.'),180))+'</p></footer>'
    +'</section>';
}
function renderPath(data,compass){
  const p=data.package||{};
  document.getElementById('productPath').innerHTML='<header class="product-head"><small>CONDITIONAL MARKET PATH</small><h2>Where capital could rotate next — and when protection starts to matter.</h2><p>Cycle Navigator freezes the weekly route. The Official Compass updates the live gates. ETA is shown only where a governed source already supports a window.</p></header>'
    +adaptiveRotationTimeline(p,compass)
    +exitRiskClock(compass)
    +'<section class="horizon-grid"><article><span>NEXT 2–3 WEEKS</span><p>'+esc(short(investorText(p.base_case_2_3_weeks)||'No supported 2–3 week view is published.',270))+'</p></article><article><span>NEXT 4–8 WEEKS</span><p>'+esc(short(investorText(p.base_case_4_8_weeks||p.compass_4_8_weeks)||'No supported 4–8 week view is published.',270))+'</p></article></section>'
    +'<section class="now-section structural-rotation"><div class="section-title"><div><small>WEEKLY STRUCTURAL ROTATION CONTEXT</small><h2>Bitcoin → microcaps</h2></div><p>Frozen Cycle Navigator context only. Live actions are owned by the Market Compass on NOW.</p></div>'+structuralRotation(p.rotation_ladder)+'</section>'
    +sinceLastBlock(data)+whyThisCallBlock(data);
}

function showProof(){document.querySelector('[data-tab="proof"]')?.click();}
function trustStrip(data,history){
  const coverage=history?.coverage||{},current=data?.public_series?.current_public_projection||{};
  const completed=Number(coverage.completed_issues),audited=Number(coverage.rows_with_published_or_canonical_score_evidence);
  const currentIssue=Number(current.public_issue_number),coverageOpen=Number(coverage.latest_open_issue),open=Number.isInteger(currentIssue)?currentIssue:coverageOpen;
  if(!Number.isInteger(completed)||completed<1||audited!==completed||!Number.isInteger(open))return '';
  return '<button class="cn-trust-strip" type="button" data-proof-link><span>'+esc(audited+' / '+completed+' completed forecasts with score evidence')+'</span><i aria-hidden="true">·</i><span>CN #'+esc(open)+' open</span><i aria-hidden="true">·</i><strong>Forecast locked before outcome</strong><small>View proof →</small></button>';
}
function sinceLastBlock(data){
  const x=data?.since_last_cn;
  if(x?.contract!=='CN_PUBLIC_SINCE_LAST_V1')return '';
  if(x.comparison_method!=='EXACT_GOVERNED_FIELD_EQUALITY')return '';
  const changed=Array.isArray(x.changed)?x.changed.filter(v=>v?.label&&v?.current&&v?.previous).slice(0,2):[],still=Array.isArray(x.still_true)?x.still_true.filter(v=>v?.label&&v?.current).slice(0,2):[];
  if(!changed.length&&!still.length)return '';
  const section=(label,rows)=>rows.length?'<div><span>'+esc(label)+'</span>'+rows.map(v=>'<p><b>'+esc(v.label)+'</b>'+esc(v.current)+(label==='CHANGED'?'<small>Previous: '+esc(v.previous)+'</small>':'')+'</p>').join('')+'</div>':'';
  return '<section class="cn-since-last"><header><small>SINCE LAST CN</small><strong>CN #'+esc(x.previous_public_issue)+' → CN #'+esc(x.current_public_issue)+'</strong></header><div class="cn-since-grid">'+section('CHANGED',changed)+section('STILL TRUE',still)+'</div></section>';
}
function whyThisCallBlock(data){
  const analysis=data?.public_market_structure_analysis,dims=Array.isArray(analysis?.dimensions)?analysis.dimensions:[];
  if(analysis?.contract!=='CN_PUBLIC_MARKET_STRUCTURE_PRESENTATION_v1'||!String(analysis?.source||'').startsWith('CYCLE_NAVIGATOR_FORECAST_FREEZE.market_structure_')||dims.length!==5)return '';
  return '<section class="cn-why-call"><header><div><small>WHY THIS CALL</small><h2>Five lenses, one disciplined read.</h2></div><p>Analysis only · not an accuracy score</p></header><ol>'+dims.map(x=>'<li><b>'+esc(x.label||x.id||'Dimension')+'</b><span>'+esc(short(x.analysis||'',200))+'</span></li>').join('')+'</ol></section>';
}
let nowObserver=null;
function installNowRefinements(data,history){
  nowObserver?.disconnect();
  const root=document.getElementById('productNow');if(!root)return;
  const apply=()=>{
    if(root.querySelector('.cn-now-refinements'))return true;
    const anchor=root.querySelector('.action-hero,.fail-card');if(!anchor)return false;
    const wrap=document.createElement('div');wrap.className='cn-now-refinements';
    wrap.innerHTML=trustStrip(data,history);
    if(!wrap.innerHTML.trim())return true;
    anchor.after(wrap);
    wrap.querySelector('[data-proof-link]')?.addEventListener('click',showProof);
    return true;
  };
  nowObserver=new MutationObserver(()=>queueMicrotask(()=>{if(!root.querySelector('.cn-now-refinements'))apply();}));
  nowObserver.observe(root,{childList:true,subtree:true});
  apply();
}
function preciseScorePct(value){
  if(value===null||value===undefined||value==='')return '—';
  const n=Number(value);if(!Number.isFinite(n))return '—';
  return n.toFixed(2).replace(/\.?0+$/,'')+'%';
}
function completedForecastReceipt(data){
  const x=data?.latest_completed_forecast;
  if(x?.contract!=='CN_PUBLIC_COMPLETED_FORECAST_RECEIPT_v1')return '';
  const list=(title,rows,fallback)=>'<div><span>'+esc(title)+'</span><ul>'+(rows.length?rows.map(v=>'<li>'+esc(short(v,190))+'</li>').join(''):'<li>'+esc(fallback)+'</li>')+'</ul></div>';
  const held=Array.isArray(x.held_up)?x.held_up:[],missed=Array.isArray(x.missed)?x.missed:[];
  return '<section class="completed-receipt"><header><div><small>LAST COMPLETED FORECAST</small><h3>CN #'+esc(x.public_issue_number)+' · '+esc(x.forecast_week)+' · FINAL</h3></div><strong>Price Range '+esc(preciseScorePct(x.price_range_score))+'</strong></header><div class="completed-grid">'+list('HELD UP',held,'Structured outcome detail is not available in this public receipt.')+list('MISSED',missed,'Structured outcome detail is not available in this public receipt.')+'</div><button type="button" data-ledger-link="'+esc(x.exact_ledger_issue)+'">View full archived record →</button></section>';
}

function marketStructureAnalysisBlock(data){
  const analysis=data?.public_market_structure_analysis;
  const dims=Array.isArray(analysis?.dimensions)?analysis.dimensions:[];
  if(analysis?.contract!=='CN_PUBLIC_MARKET_STRUCTURE_PRESENTATION_v1'||!String(analysis?.source||'').startsWith('CYCLE_NAVIGATOR_FORECAST_FREEZE.market_structure_')||dims.length!==5)return '';
  const rows=dims.map((x,i)=>(i+1)+'. <b>'+esc(x.label||x.id||'Dimension')+'</b> — '+esc(short(x.analysis||'',190))).join('<br>');
  return '<section class="live-score"><span>MARKET STRUCTURE · ANALYSIS ONLY</span><strong>No accuracy score from CN #27 onward</strong><p>'+rows+'</p></section>';
}

function renderProof(data,history){
  const root=document.getElementById('productProof'),records=history.records||[],scores=records.map(r=>({record:r,...publicScores(r)}));
  const live=data.live_observation||{},meas=Number(live.provisional_coverage?.measurable||0),total=Number(live.provisional_coverage?.total||live.claims_due_this_week||0),liveScore=Number(live.provisional_score);
  const liveTitle=meas>0&&Number.isFinite(liveScore)?`${Math.round(liveScore)}% so far`:'Waiting for evidence';
  const liveCopy=meas>0?`${meas} of ${total||meas} weekly calls are ready to be evaluated. This remains provisional until the week is complete.`:`0 of ${total||0} weekly calls are ready to be evaluated. No percentage is shown until at least one call is genuinely scoreable.`;
  const rows=[...scores].reverse().map(x=>{const analysisOnly=String(x.record?.structure_method||'')==='ANALYSIS_ONLY_NOT_SCORED';return `<details id="cn-record-${x.record.cn}" class="ledger-row"><summary><span><strong>CN #${x.record.cn}</strong><small>${x.derived?'component rollup':analysisOnly?'price score + structure analysis':'published overall preserved'}</small></span><b>${pct(x.weekly)}</b><span>${pct(x.price)}<small>PRICE</small></span><span>${analysisOnly?'—':pct(x.market)}<small>MARKET / STRUCTURE</small></span></summary><div class="ledger-detail"><p><b>Archived price evidence:</b> ${esc(x.record.range_display||'No numerical price-range score published for this issue.')}</p>${analysisOnly?'<p><b>Market / Structure:</b> Analysis only — no public accuracy score for this issue.</p>':`<p><b>Archived market evidence:</b> ${esc([x.record.intraday_display,x.record.structure_display].filter(Boolean).join(' · ')||'No additional numerical component published.')}</p>`}</div></details>`}).join('');
  const process=[
    ['1','COLLECT & VERIFY','Market observations are gathered continuously, timestamped and checked for freshness, conflicts and missing inputs before they can influence the public view.'],
    ['2','ANALYSE INDEPENDENTLY','Different analytical lenses assess trend, relative strength, participation, liquidity, positioning, risk and rotation instead of relying on one indicator.'],
    ['3','CHALLENGE THE EVIDENCE','Contradictory or weak signals reduce confidence. The system is designed to prefer “not enough evidence” over forcing a clean answer.'],
    ['4','SYNTHESISE WEEKLY','Once a week, the evidence is combined into one public market outlook: current phase, expected path, risk conditions and price expectations where the data supports them.'],
    ['5','LOCK BEFORE THE OUTCOME','The weekly forecast is fixed before the market outcome is known. Later live data can change the current action, but it cannot rewrite the original forecast.'],
    ['6','MONITOR LIVE','Between weekly publications, a separate live layer checks whether the investor posture should remain hold, prepare, selective, defensive or broader risk-on.'],
    ['7','SCORE & LEARN','When outcomes mature, prospectively frozen price ranges are scored. Market Structure remains an analytical layer, while archived legacy structure scores stay visible as historical records.']
  ];
  root.innerHTML=`<header class="product-head"><small>PROOF</small><h2>Track record, method and accountability.</h2><p>The public record is translated into three investor-friendly measures while the original archived scores remain untouched.</p></header><section class="proof-metrics"><article class="proof-coverage"><span>COMPLETED FORECAST COVERAGE</span><strong>${history.coverage?.completed_issues||records.length} / ${history.coverage?.rows_with_published_or_canonical_score_evidence||records.length}</strong><small>completed CN issues audited · no cross-era aggregate</small></article><article><span>LATEST COMPLETED</span><strong>CN #${data?.public_series?.latest_completed_score?.public_issue_number??"—"}</strong><small>${esc(data?.public_series?.latest_completed_score?.forecast_week||"Published lineage unavailable")} · FINAL</small></article><article><span>CURRENT FORECAST</span><strong>CN #${data?.public_series?.current_public_projection?.public_issue_number??"—"}</strong><small>OPEN · forecast locked before outcome</small></article></section>${completedForecastReceipt(data)}<section class="live-score"><span>LIVE EVIDENCE · NON-FINAL</span><strong>${esc(liveTitle)}</strong><p>${esc(liveCopy)}</p></section><section class="chart-wrap"><div class="chart-head"><div><small>ARCHIVED SCORE FAMILIES</small><h3>Records remain in their original methods</h3></div><div class="legend"><i class="weekly"></i>Archived overall <i class="price"></i>Price <i class="market"></i>Legacy structure</div></div>${sparkline(records)}</section><section class="score-method"><p><b>Forecast first. Outcome later. Historical methods are never rewritten.</b> Score families remain separate; this page intentionally does not create a lifetime accuracy number across eras.</p><p><b>Price Range Accuracy</b> remains the active public precision score. Historical Market / Structure entries remain visible in their original method. From CN #27 onward, Market Structure is analysis only, while the Bull/Bear scale remains a forward evidence balance—not an accuracy score.</p></section><section class="ledger"><div class="section-title"><div><small>ALL COMPLETED ISSUES</small><h2>CN #1 → #${records.at(-1)?.cn??records.length}</h2></div><p>Tap any row for the archived components behind the public rollup.</p></div>${rows}</section><section class="how-editorial"><header><small>HOW IT WORKS</small><h2>What the system actually watches.</h2><p>Cycle Navigator combines market structure, liquidity, positioning, participation, macro conditions and cross-asset behaviour to estimate where crypto sits in the cycle and what is most likely to matter next.</p></header><div class="data-families"><article><strong>PRICE & STRUCTURE</strong><p>Trend, momentum, volatility, Bitcoin and Ethereum behaviour, Ethereum vs Bitcoin, Bitcoin dominance and historical price structure.</p></article><article><strong>PARTICIPATION & ROTATION</strong><p>Market breadth, relative strength, altcoin participation and the movement of capital from Bitcoin into Ethereum, large caps and progressively smaller assets.</p></article><article><strong>LIQUIDITY & POSITIONING</strong><p>Stablecoin liquidity, ETF and institutional flows, derivatives positioning, leverage, funding, open interest and broader market liquidity.</p></article><article><strong>MACRO & NETWORK CONTEXT</strong><p>Macro liquidity, rates, risk appetite, selected on-chain activity and historical pattern comparisons used as context rather than as single-point signals.</p></article></div><div class="method-flow">${process.map(x=>`<article><span>${x[0]}</span><div><strong>${x[1]}</strong><p>${x[2]}</p></div></article>`).join('')}</div><p class="method-note">The exact providers, thresholds, weights, prompts, fallback routes and decision recipe remain private. The public layer explains what is analysed and how accountability works without exposing a copyable implementation.</p></section>`;
}

async function render(){
  shell();
  try{
    const [s,h,p,compass]=await Promise.all([json('./data/latest.json'),json('./history-scoreboard.json'),prices(),jsonOptional('./data/compass.json')]);snapshot=s;renderNow(s,p);document.querySelector('[data-pa-proof-native]')?.addEventListener('click',showProof);renderPath(s,compass);renderProof(s,h);installNowRefinements(s,h);document.querySelectorAll("[data-ledger-link]").forEach(b=>b.onclick=()=>{const row=document.getElementById(`cn-record-${b.dataset.ledgerLink}`);if(row){row.open=true;row.scrollIntoView({behavior:"smooth",block:"start"});}});clearInterval(refreshTimer);refreshTimer=setInterval(freshness,30000);
  }catch(e){console.warn('Cycle Navigator unavailable',e);const n=document.getElementById('productNow');if(n)n.innerHTML='<section class="fail-card"><small>MARKET DATA TEMPORARILY UNAVAILABLE</small><h1>WAIT</h1><p>No new action is inferred while verified evidence is unavailable.</p></section>';}
}

render();setInterval(render,5*60*1000);
})();
