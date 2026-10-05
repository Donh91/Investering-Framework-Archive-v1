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

function publicPathText(raw){
  let s=investorText(raw);
  if(!s)return'';
  s=s
    .replace(/\bsource-owned\b/gi,'published')
    .replace(/\bgoverned\b/gi,'verified')
    .replace(/\blineage\b/gi,'data alignment')
    .replace(/\bfail closed\b/gi,'wait for verified data')
    .replace(/\bfrozen Monday\b/gi,'weekly baseline')
    .replace(/\bmachine package\b/gi,'weekly outlook')
    .replace(/\baction posture\b/gi,'stance')
    .replace(/\bregistered confirmed confirmation\b/gi,'confirmed signal')
    .replace(/\bregistered confirmation\b/gi,'confirmed signal')
    .replace(/\bdecision owner\b/gi,'signal source')
    .replace(/\bowner\b/gi,'signal source')
    .replace(/\bnative\b/gi,'live')
    .replace(/\s+/g,' ')
    .trim();
  const exact=[
    [/First alt-risk tier eligible only after a confirmed signal\.?/i,'Large caps become actionable only after a confirmed rotation signal.'],
    [/Requires durable large-cap transmission under a confirmed signal\.?/i,'Mid caps stay on hold until strength spreads beyond large caps and confirms.'],
    [/Requires confirmed mid-cap participation before deployment\.?/i,'Small caps stay on hold until mid-cap participation confirms.'],
    [/Highest-beta non-meme tier remains late in the rotation sequence\.?/i,'Microcaps remain a late-stage risk tier, so no timing is supported yet.'],
    [/Liquidity anchor; preserve core while the short-horizon gate resolves\.?/i,'Bitcoin remains the liquidity anchor. Hold core exposure while the short-term signal develops.'],
    [/Relative-strength leadership must hold before broader rotation is trusted\.?/i,'Ethereum must keep relative strength before broader altcoin rotation is trusted.'],
    [/Current-state continuation unless the live confirmation or deterioration gate changes state\.?/i,'Near-term momentum can continue, but the view changes if confirmation weakens or deterioration appears.'],
    [/Short-horizon state is cross-checked against the current weekly regime; transmission must improve before risk moves down-cap\.?/i,'Near-term signals are mixed. Broader participation must improve before moving further down the risk curve.'],
    [/No evidence-supported 4[–-]8-week cycle direction or stance\. A conditional 21[–-]30-day scenario does not fill the missing longer-window confirmation\.?/i,'There is not enough long-range evidence yet to call a 4–8 week cycle phase. A shorter 21–30 day scenario is not enough to fill that gap.'],
    [/UNAVAILABLE cycle direction and UNAVAILABLE stance\. The 56-day shadow rotation window has \d+ passing days against \d+ required, and final weekly review does not establish a stable cycle phase\.?/i,'The 4–8 week cycle view is not ready yet. Longer-range evidence has not reached the minimum coverage needed to call a stable cycle phase.'],
    [/Live gate unavailable; the weekly baseline remains visible in details\.?/i,'Live confirmation is unavailable. The weekly baseline remains visible in the details.'],
    [/A fresh aligned Official Compass is required\.?/i,'Fresh verified market data is required.'],
    [/A verified aligned sell\/trim signal source is unavailable\.?/i,'No verified sell or trim signal is currently available.'],
    [/No verified sell\/trim signal source is bound\.?/i,'No verified sell or trim signal is active.'],
    [/Only unlocks after broad altseason is credibly confirmed\.?/i,'This phase only becomes relevant after broad altseason is confirmed.'],
    [/Persistent multi-horizon confirmation\.?/i,'Strength confirmed across multiple timeframes.']
  ];
  for(const [pattern,replacement] of exact)s=s.replace(pattern,replacement);
  return s.replace(/\s+/g,' ').trim();
}

// Legacy release-gate compatibility only; never rendered: Small-cap expansion gate
function publicPathStatus(value){
  const s=pathStatus(value);
  return({
    'HARD WAIT':'WAIT',
    'WAIT FOR RECLAIM':'WAIT',
    'WAIT FOR FLUSH':'WAIT',
    'LOCKED':'NOT ACTIVE',
    'INACTIVE':'NOT ACTIVE',
    'UNAVAILABLE':'NO SIGNAL',
    'UNKNOWN':'UNCLEAR'
  })[s]||s;
}
function publicHorizonState(value){
  const s=horizonStateLabel(value);
  return s==='UNAVAILABLE'?'NOT READY':s;
}
function dataStatusLabel(value){
  const s=String(value||'').toUpperCase();
  if(s==='OK'||s==='PASS')return'UP TO DATE';
  if(/DEGRADED|STALE/.test(s))return'LIMITED';
  return s==='UNAVAILABLE'||!s?'WAITING':'CHECKING';
}
function pathLegend(){
  return '<section class="path-read-guide"><div><span>READ PATH IN 10 SECONDS</span><strong>Blue = what is known now · Amber = next watch · Grey = not confirmed</strong></div><p><b>Watch window</b> means a phase can become actionable inside that range only if confirmation arrives. <b>Review window</b> means the signal is reassessed in that period. Neither is a countdown.</p></section>';
}
function publicCycleSource(source){
  const s=String(source||'');
  if(/21[–-]30D/.test(s))return'Supported by the 21–30 day outlook.';
  if(/4[–-]8W/.test(s))return'Supported by the 4–8 week outlook.';
  return'Long-range evidence is not strong enough to place the cycle yet.';
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
  if(!s||/UNAVAILABLE|UNKNOWN|NO FIXED ETA|NO SUPPORTED ETA|NO CALENDAR ETA|ONLY AFTER|EVIDENCE FIRST/i.test(s))return'NO SUPPORTED ETA';
  return s;
}
function timingWindow(value){
  const eta=pathEta(value);
  if(eta==='NO SUPPORTED ETA')return{supported:false,conditional:false,label:'NOT AVAILABLE YET',note:'No reliable timing window is published yet.'};
  const conditional=/\bCONDITIONAL\b/i.test(eta);
  let label=eta.replace(/\bCONDITIONAL\b/ig,'').replace(/\s+/g,' ').trim();
  label=label
    .replace(/(\d+)\s*[-–]\s*(\d+)\s*d\b/gi,'$1–$2 days')
    .replace(/(\d+)\s*[-–]\s*(\d+)\s*h\b/gi,'$1–$2 hours')
    .replace(/\bNOW\b/i,'NOW');
  return{
    supported:true,
    conditional,
    label,
    note:conditional?'Only if confirmation arrives · not a countdown':'Published timing window'
  };
}
function timingMarkup(value,kind='TIMING'){
  const t=timingWindow(value);
  if(!t.supported)return '<b class="path-timing unsupported">'+esc(kind)+' · '+esc(t.label)+'</b>';
  return '<b class="path-timing'+(t.conditional?' conditional':'')+'">'+esc(t.conditional?'WATCH WINDOW':kind)+' · '+esc(t.label)+'</b>'
    +(t.conditional?'<small class="path-timing-note">'+esc(t.note)+'</small>':'');
}
function timingInline(value){
  const t=timingWindow(value);
  return t.supported?(t.conditional?'Watch window '+t.label+' · only if confirmed':t.label):'No reliable timing yet';
}
function pathStatus(value){
  const s=String(value||'').toUpperCase();
  const hit=s.match(/WAIT_FOR_RECLAIM|WAIT_FOR_FLUSH|PARABOLIC_ALTSEASON|BROAD_ALTSEASON|PRE_ROTATION|ACTIVE WATCH|NOT CONFIRMED|UNCONFIRMED|CONSOLIDATION|DISTRIBUTION|EXIT_RISK|DEFENSIVE|ROTATION|INACTIVE|PAUSED|HARD_WAIT|HARD WAIT|BUILDING|ELEVATED|WARNING|CONFIRMED|UNAVAILABLE|UNCLEAR|UNKNOWN|REVIEW|LOCKED|ACTIVE|WAIT|HOLD|HIGH|NORMAL|NONE/);
  return hit?hit[0].replaceAll('_',' '):'PENDING';
}
function pathTone(value){
  const s=String(value||'').toUpperCase();
  if(/INACTIVE|UNAVAILABLE|UNCLEAR|UNKNOWN|PAUSED|LOCKED/.test(s))return'unknown';
  if(/WAIT_FOR_RECLAIM|WAIT_FOR_FLUSH|REVIEW|NOT CONFIRMED|UNCONFIRMED|HARD_WAIT|HARD WAIT|WAIT|ELEVATED|HIGH/.test(s))return'wait';
  if(/ACTIVE WATCH|BUILDING|WATCH|WARNING/.test(s))return'watch';
  if(/HOLD|NORMAL|NONE/.test(s))return'hold';
  if(/CONFIRMED|ACTIVE/.test(s))return'active';
  return'unknown';
}
function utcLabel(value){
  if(!value)return'—';
  const d=new Date(value);if(!Number.isFinite(d.getTime()))return'—';
  return d.toLocaleString('en-GB',{timeZone:'UTC',day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit',hour12:false}).replace(',','')+' UTC';
}
function compassSegment(compass,segment){
  return (Array.isArray(compass?.capitalization_ladder)?compass.capitalization_ladder:[]).find(x=>x?.segment===segment)||null;
}
function pathWeeklyAlignment(data,compass){
  const current=data?.public_series?.current_public_projection||{},receipt=compass?.weekly_context||{};
  const currentIssue=Number(current.public_issue_number),receiptIssue=Number(receipt.public_issue_number);
  const currentWeek=String(current.forecast_week||''),receiptWeek=String(receipt.forecast_week||'');
  const ok=receipt.contract==='CN_COMPASS_WEEKLY_ALIGNMENT_v1'&&receipt.status==='ALIGNED'&&Number.isInteger(currentIssue)&&Number.isInteger(receiptIssue)&&currentIssue===receiptIssue&&currentWeek!==''&&currentWeek===receiptWeek;
  return {ok,status:ok?'ALIGNED':receipt.status||'UNVERIFIED',currentWeek,receiptWeek};
}
function pathAlignmentNotice(alignment){
  if(alignment.ok)return'';
  return '<section class="path-alignment-warning"><span>LIVE SIGNALS REFRESHING</span><strong>The weekly path stays fixed while live data catches up.</strong><p>Rotation and Altcoin signals temporarily show no live call until the fresh data matches the current weekly outlook.</p></section>';
}
function statusActive(value){
  const s=String(value||'').toUpperCase();
  return !/NOT CONFIRMED|UNCONFIRMED|INACTIVE|UNAVAILABLE|UNKNOWN|HARD_WAIT|HARD WAIT|WAIT|PAUSED|LOCKED/.test(s)&&/(BUY|ACTIVE|CONFIRMED|BROADER DEPLOYMENT)/.test(s);
}
function reentryEngaged(value){
  const s=String(value||'').toUpperCase();
  return ['WAIT_FOR_FLUSH','WAIT_FOR_RECLAIM','REVIEW'].includes(s);
}
function distributionDriver(compass){
  const rows=Array.isArray(compass?.protection_tracker?.decisive_public_drivers)?compass.protection_tracker.decisive_public_drivers:[];
  return rows.find(x=>/distribution/i.test(String(x||'')))||'No public distribution explanation is available.';
}
function mondayAlt(pkg,index){
  const rows=Array.isArray(pkg?.altseason_countdown)?pkg.altseason_countdown:[];
  return rows[index]||{};
}
function cycleDestination(pkg){
  const x=pkg?.decision_projection?.next_21_30d||{};
  const d=String(x.regime_destination||'').toUpperCase();
  const map={EXPANSION:'PRE_ROTATION',CONSOLIDATION:'CONSOLIDATION',DISTRIBUTION:'DISTRIBUTION',CONTRACTION:'DEFENSIVE'};
  return map[d]||null;
}
// Legacy release-gate compatibility only; never rendered: source:'NO STRUCTURED 4–8W PHASE'
function cycleForwardFromSources(pkg){
  const known=['DEFENSIVE','CONSOLIDATION','PRE_ROTATION','ROTATION','BROAD_ALTSEASON','PARABOLIC_ALTSEASON','DISTRIBUTION','EXIT_RISK'];
  const month=pkg?.decision_projection?.next_21_30d||{},monthKey=cycleDestination(pkg);
  if(monthKey&&month.direction&&!/UNAVAILABLE|NO_EDGE/.test(String(month.direction).toUpperCase())){
    return{key:monthKey,source:'STRUCTURED MONDAY 21–30D',eta:'21–30D HORIZON'};
  }
  const weekly=pkg?.decision_projection?.weeks_4_8||{},weeklyKey=String(weekly.state||'').toUpperCase();
  if(known.includes(weeklyKey))return{key:weeklyKey,source:'STRUCTURED MONDAY 4–8W',eta:pathEta(weekly.eta||'4–8W HORIZON')};
  return{key:'UNCLEAR',source:'NO STRUCTURED LONG-CYCLE PHASE',eta:'NO SUPPORTED ETA'};
}
const MARKET_CYCLE=[
  ['DEFENSIVE','Reset / defensive'],
  ['CONSOLIDATION','Transition / consolidation'],
  ['PRE_ROTATION','Pre-rotation / expansion'],
  ['ROTATION','Rotation'],
  ['BROAD_ALTSEASON','Broad altseason'],
  ['PARABOLIC_ALTSEASON','Mania / euphoria'],
  ['DISTRIBUTION','Distribution'],
  ['EXIT_RISK','Exit risk']
];
function cycleEtaFor(key,pkg,compass){
  const forward=cycleForwardFromSources(pkg);
  if(key===forward.key)return forward.eta;
  if(key==='PARABOLIC_ALTSEASON')return pathEta(pkg?.altseason_mania_window);
  if(key==='DISTRIBUTION')return'NO SUPPORTED ETA';
  if(key==='EXIT_RISK')return pathEta(compass?.sell_assessment?.eta);
  return'NO SUPPORTED ETA';
}
function weeklyCycleState(pkg){
  const s=investorText(pkg?.base_case_this_week||pkg?.market_state||'').trim();
  return s?short(publicPathText(s),150):'No public weekly market summary is available.';
}
function weeklySetupLabel(pkg){
  const s=publicPathText(pkg?.base_case_this_week||pkg?.market_state||'').trim();
  if(!s)return'Current setup unavailable';
  let first=(s.split(/[.!?]/)[0]||s).trim()
    .replace(/^This week begins with\s+/i,'')
    .replace(/^Completed This week was\s+/i,'')
    .replace(/^Completed\s+/i,'');
  if(first)first=first[0].toUpperCase()+first.slice(1);
  return short(first,96);
}
function cycleIcon(key){
  return({DEFENSIVE:'↺',CONSOLIDATION:'◐',PRE_ROTATION:'↗',ROTATION:'⇢',BROAD_ALTSEASON:'✦',PARABOLIC_ALTSEASON:'⚡',DISTRIBUTION:'◒',EXIT_RISK:'↓'})[key]||'•';
}
function horizonStateLabel(value){
  const s=String(value||'UNAVAILABLE').toUpperCase().replaceAll('_',' ');
  if(/^(BULLISH|BEARISH|MIXED|NEUTRAL|UNCLEAR|UNAVAILABLE)$/.test(s))return s;
  return pathStatus(value);
}
function horizonCell(compass,key,label){
  const h=compass?.horizons?.[key]||{},stateLabel=publicHorizonState(h.label||h.state||h.expected_direction||'UNAVAILABLE'),eta=timingWindow(h.eta);
  return '<div class="market-horizon-step'+(key==='NEXT_12H'?' now':'')+'"><i></i><span>'+esc(label)+'</span><strong>'+esc(stateLabel)+'</strong><small>'+esc(eta.label)+'</small></div>';
}
function marketCycleTrack(pkg,compass){
  const forward=cycleForwardFromSources(pkg),forwardKnown=forward.key!=='UNCLEAR';
  const h12=compass?.horizons?.NEXT_12H||{},h57=compass?.horizons?.NEXT_5_7D||{},h48=compass?.horizons?.CYCLE_ALTCOINS_3_8W||{};
  const nextStage=forwardKnown?(MARKET_CYCLE.find(x=>x[0]===forward.key)||['','UNRESOLVED'])[1]:'NONE YET';
  const stageNote=forwardKnown?publicCycleSource(forward.source):'Long-range evidence is still too incomplete to place the cycle precisely.';
  const rows=MARKET_CYCLE.map(([key,label])=>{
    const isForward=key===forward.key&&forwardKnown,eta=timingWindow(cycleEtaFor(key,pkg,compass));
    return '<div class="market-cycle-step'+(isForward?' next':'')+'" data-cycle-role="'+(isForward?'forward-destination':'reference')+'"><i>'+esc(cycleIcon(key))+'</i><span>'+esc(label)+'</span>'+(eta.supported?'<b>'+esc(eta.label)+'</b>':'')+'</div>';
  }).join('');
  const horizons=horizonCell(compass,'NEXT_12H','NOW · 0–12H')+horizonCell(compass,'NEXT_1_3D','1–3 DAYS')+horizonCell(compass,'NEXT_5_7D','5–7 DAYS')+horizonCell(compass,'NEXT_2_3W','2–3 WEEKS')+horizonCell(compass,'CYCLE_ALTCOINS_3_8W','4–8 WEEKS');
  const currentPosition='<div class="cycle-position-chip current-context"><i></i><span>HERE NOW · CURRENT SETUP</span><strong>Cycle stage not confirmed</strong><small>'+esc(weeklySetupLabel(pkg))+' · shorter-term direction is known, but the long-cycle stage is deliberately left unassigned.</small></div>';
  const nextPosition=forwardKnown?'<div class="cycle-position-chip next-supported"><i></i><span>NEXT SUPPORTED PHASE</span><strong>'+esc(nextStage)+'</strong><small>'+esc(timingInline(forward.eta))+' · this is a destination, not the current phase.</small></div>':'';
  const positionChip=currentPosition+nextPosition;
  return '<section class="path-track market-cycle-v2" data-path-track="market-cycle">'
    +'<header class="path-track-head"><div><span>1 · MARKET CYCLE</span><h3>The big-picture market cycle.</h3><p>Read the decision windows first, then the full market route. A long-cycle phase is highlighted only when the long-range evidence is strong enough.</p></div><aside><span>LONG-RANGE SIGNAL</span><strong>'+esc(forwardKnown?'NEXT: '+nextStage:'NOT CONFIRMED')+'</strong><small>'+esc(stageNote)+'</small></aside></header>'
    +'<div class="market-cycle-summary"><div><span>NEAR TERM · 0–12H</span><strong>'+esc(publicHorizonState(h12.label||h12.expected_direction||'UNAVAILABLE'))+'</strong><small>'+esc(timingInline(h12.eta))+'</small></div><div><span>WEEK AHEAD · 5–7D</span><strong>'+esc(publicHorizonState(h57.label||h57.expected_direction||'UNAVAILABLE'))+'</strong><small>'+esc(timingInline(h57.eta))+'</small></div><div><span>LONG CYCLE · 4–8W</span><strong>'+esc(publicHorizonState(h48.state||h48.label||'UNCLEAR'))+'</strong><small>'+esc(timingInline(h48.eta))+'</small></div></div>'
    +'<div class="market-cycle-nowline"><span>WEEK-AHEAD CONTEXT</span><p>'+esc(weeklyCycleState(pkg))+'</p></div>'
    +'<div class="market-horizon-title"><span>DECISION WINDOWS</span><small>Blue = NOW · each point keeps its own time horizon</small></div><div class="market-horizon-rail">'+horizons+'</div>'
    +'<div class="market-route-title"><span>FULL CYCLE ROUTE</span><small>'+esc(forwardKnown?'Amber = next supported destination · swipe to follow the route →':'No phase is highlighted until the long-range evidence can support one · swipe →')+'</small></div>'
    +positionChip
    +'<div class="market-cycle-rail">'+rows+'</div>'
    +'<details class="path-track-detail"><summary>Why this cycle view?</summary><p>'+esc(short(publicPathText(pkg?.base_case_2_3_weeks||pkg?.market_state||'No public market-cycle explanation is available.'),420))+'</p></details>'
    +'</section>';
}
const ROTATION_ORDER=[
  ['BTC','Bitcoin'],['ETH','Ethereum'],['LARGE_CAPS','Large caps'],['MID_CAPS','Mid caps'],['SMALL_CAPS','Small caps'],['MICROCAPS','Microcaps'],['MEMES','Memes']
];
function weeklyRotationContext(pkg,segment,label){
  const rows=Array.isArray(pkg?.rotation_ladder)?pkg.rotation_ladder:[];
  const aliases={BTC:['BTC','BITCOIN'],ETH:['ETH','ETHEREUM'],LARGE_CAPS:['LARGE CAPS','LARGE_CAPS'],MID_CAPS:['MIDCAPS','MID CAPS','MID_CAPS'],SMALL_CAPS:['SMALL CAPS','SMALL_CAPS'],MICROCAPS:['MICROCAPS','MICRO CAPS'],MEMES:['MEMES']};
  const keys=aliases[segment]||[label.toUpperCase()];
  return rows.find(r=>keys.some(k=>String(r?.segment||'').toUpperCase()===k))||null;
}
function rotationTrack(pkg,compass){
  const valid=compass?.contract==='PUBLIC_COMPASS_PROJECTION_v1';
  const rows=ROTATION_ORDER.map(([segment,label],i)=>{
    const live=valid?compassSegment(compass,segment):null,weekly=weeklyRotationContext(pkg,segment,label);
    const status=valid?(live?.status||live?.action||'UNAVAILABLE'):'UNAVAILABLE';
    const eta=valid&&live?pathEta(live.eta):'NO SUPPORTED ETA';
    const detail=publicPathText(live?.reason||weekly?.status||'No public rotation explanation is available.');
    return '<article class="rotation-rung-v2 tone-'+esc(pathTone(status))+'"><i>'+esc(i+1)+'</i><div><span>'+esc(label)+'</span><strong>'+esc(publicPathStatus(status))+'</strong></div><div class="rotation-timing">'+timingMarkup(eta,'TIMING')+'</div><details><summary>Why?</summary><p>'+esc(short(investorText(detail),220))+'</p></details></article>';
  }).join('');
  return '<section class="path-track rotation-v2" data-path-track="rotation">'
    +'<header class="path-track-head"><div><span>2 · ROTATION</span><h3>Bitcoin → risk curve.</h3><p>Live map of where capital can move next. A watch window opens only when the required confirmation appears.</p></div><aside><span>DATA STATUS</span><strong>'+esc(dataStatusLabel(compass?.data_status))+'</strong><small>Updated '+esc(utcLabel(compass?.issued_at_utc))+'</small></aside></header>'
    +'<div class="rotation-rail-v2">'+rows+'</div>'
    +'</section>';
}
function conservativeStatus(values){
  const states=values.map(pathStatus);
  const order=['UNAVAILABLE','HARD WAIT','NOT CONFIRMED','UNCONFIRMED','WAIT','REVIEW','BUILDING','ACTIVE WATCH','HOLD','ACTIVE','CONFIRMED'];
  for(const x of order)if(states.includes(x))return x;
  return states[0]||'UNAVAILABLE';
}
function sharedEta(rows){
  const etas=rows.map(x=>pathEta(x?.eta)).filter(Boolean);
  if(!etas.length||etas.some(x=>x==='NO SUPPORTED ETA'))return'NO SUPPORTED ETA';
  return etas.every(x=>x===etas[0])?etas[0]:'NO SUPPORTED ETA';
}
function altcoinCycleStages(pkg,compass){
  const valid=compass?.contract==='PUBLIC_COMPASS_PROJECTION_v1',h=compass?.horizons||{},p=compass?.protection_tracker||{},sell=compass?.sell_assessment||{};
  const seg=s=>valid?compassSegment(compass,s):null;
  const large=seg('LARGE_CAPS')||{},mid=seg('MID_CAPS')||{},small=seg('SMALL_CAPS')||{},micro=seg('MICROCAPS')||{},eth=seg('ETH')||{};
  const cycle=h.CYCLE_ALTCOINS_3_8W||{},cycleState=String(cycle.state||'').toUpperCase();
  const monday=i=>mondayAlt(pkg,i);
  const lmStatus=valid?conservativeStatus([large.status||large.action,mid.status||mid.action]):'UNAVAILABLE';
  const maniaActive=cycleState==='PARABOLIC_ALTSEASON';
  const broadStatus=!valid?'UNAVAILABLE':cycleState==='BROAD_ALTSEASON'?'ACTIVE':['PARABOLIC_ALTSEASON','DISTRIBUTION','EXIT_RISK'].includes(cycleState)?'CONFIRMED':pathStatus(cycle.state||cycle.action_posture||'UNAVAILABLE');
  const unavailableWhy='Live confirmation is unavailable. The weekly baseline remains visible in the details.';
  return [
    {key:'PARTICIPATION',title:'Participation building',status:valid?(h.NEXT_1_3D?.action_posture||h.NEXT_1_3D?.state||'UNAVAILABLE'):'UNAVAILABLE',eta:valid?h.NEXT_1_3D?.eta:null,monday:monday(0).window,why:publicPathText(valid?h.NEXT_1_3D?.expected_path:unavailableWhy)},
    {key:'ETH_UNLOCK',title:'Ethereum leadership',subtitle:'Relative strength must hold',status:valid?(eth.status||eth.action||'UNAVAILABLE'):'UNAVAILABLE',eta:valid?eth.eta:null,monday:monday(1).window,why:publicPathText(valid?eth.reason:unavailableWhy)},
    {key:'LARGE_MID',title:'Large + mid caps join',status:lmStatus,eta:valid?sharedEta([large,mid]):null,monday:monday(2).window,why:publicPathText(valid?[large.reason,mid.reason].filter(Boolean).join(' '):unavailableWhy)},
    {key:'IGNITION',title:'Altseason ignition',subtitle:'Small caps begin to participate',status:valid?(small.status||small.action||'UNAVAILABLE'):'UNAVAILABLE',eta:valid?small.eta:null,monday:monday(3).window,why:publicPathText(valid?small.reason:unavailableWhy)},
    {key:'MICRO',title:'Micro acceleration',status:valid?(micro.status||micro.action||'UNAVAILABLE'):'UNAVAILABLE',eta:valid?micro.eta:null,monday:monday(3).window,why:publicPathText(valid?micro.reason:unavailableWhy)},
    {key:'BROAD',title:'Broad altseason',status:broadStatus,eta:valid?cycle.eta:null,monday:monday(4).window,why:publicPathText(valid?(cycle.expected_path||'No public broad-altseason explanation is available.'):unavailableWhy)},
    {key:'MANIA',title:'Mania / euphoria',status:maniaActive?'ACTIVE':'LOCKED',eta:maniaActive?cycle.eta:null,monday:null,why:publicPathText(maniaActive?cycle.expected_path:'This phase only becomes relevant after broad altseason is confirmed.')},
    {key:'DISTRIBUTION',title:'Distribution',status:valid?p.distribution_risk:'UNAVAILABLE',eta:null,monday:null,why:publicPathText(valid?distributionDriver(compass):'Fresh verified market data is required.')},
    {key:'EXIT',title:'Exit / protection',status:valid?sell.state:'UNAVAILABLE',eta:valid?sell.eta:null,monday:null,why:publicPathText(valid?sell.reason:'No verified sell or trim signal is currently available.')},
    {key:'REENTRY',title:'Cooldown / re-entry',status:valid?p.reentry_state:'UNAVAILABLE',eta:null,monday:null,why:publicPathText(valid?p.reentry_message:'Re-entry review is unavailable.')}
  ];
}
function altcoinTarget(pkg,compass,stages){
  const row=key=>stages.find(x=>x.key===key)||{};
  const small=compassSegment(compass,'SMALL_CAPS')||{},micro=compassSegment(compass,'MICROCAPS')||{};
  const cycle=compass?.horizons?.CYCLE_ALTCOINS_3_8W||{},p=compass?.protection_tracker||{},sell=compass?.sell_assessment||{};
  const sellState=String(sell.state||'').toUpperCase(),dist=String(p.distribution_risk||'').toUpperCase(),cycleState=String(cycle.state||'').toUpperCase(),reentryState=String(p.reentry_state||'').toUpperCase();
  if(reentryEngaged(reentryState))return{key:'REENTRY',mode:'OPPORTUNITY',eyebrow:'NEXT RECOVERY PHASE',title:'Cooldown / re-entry',subtitle:'Re-entry phase after protection',eta:'NO SUPPORTED ETA',status:pathStatus(p.reentry_state)};
  if(sellState&&!/UNAVAILABLE|UNKNOWN|INACTIVE|NONE/.test(sellState))return{key:'EXIT',mode:'PROTECTION',eyebrow:'NEXT DEFENSIVE PHASE',title:'Exit / protection window',subtitle:'Verified sell / trim signal',eta:pathEta(sell.eta),status:pathStatus(sell.state)};
  if(/WARNING|CONFIRMED/.test(dist))return{key:'DISTRIBUTION',mode:'PROTECTION',eyebrow:'NEXT DEFENSIVE PHASE',title:'Distribution watch',subtitle:'Protection takes priority over upside sequencing',eta:'NO SUPPORTED ETA',status:pathStatus(p.distribution_risk)};
  if(cycleState==='PARABOLIC_ALTSEASON')return{key:'DISTRIBUTION',mode:'PROTECTION',eyebrow:'NEXT RISK PHASE',title:'Distribution watch',subtitle:'Mania is active; protection becomes the next thing to watch',eta:'NO SUPPORTED ETA',status:pathStatus(p.distribution_risk)};
  if(cycleState==='BROAD_ALTSEASON')return{key:'MANIA',mode:'OPPORTUNITY',eyebrow:'NEXT HIGH-EXCITEMENT PHASE',title:'Mania / euphoria',subtitle:'After broad altseason confirms',eta:pathEta(pkg?.altseason_mania_window||cycle.eta),status:'LOCKED'};
  if(statusActive(micro.status||micro.action)){const broad=row('BROAD');return{key:'BROAD',mode:'OPPORTUNITY',eyebrow:'NEXT ALTCOIN PHASE',title:'Broad altseason',subtitle:'Strength confirmed across multiple timeframes',eta:pathEta(broad.eta),status:pathStatus(broad.status)};}
  if(statusActive(small.status||small.action)){const next=row('MICRO');return{key:'MICRO',mode:'OPPORTUNITY',eyebrow:'NEXT HIGH-BETA PHASE',title:'Micro acceleration',subtitle:'After small-cap transmission confirms',eta:pathEta(next.eta),status:pathStatus(next.status)};}
  const ignition=row('IGNITION');
  return{key:'IGNITION',mode:'OPPORTUNITY',eyebrow:'NEXT HIGH-BETA PHASE',title:'ALTSEASON IGNITION',subtitle:'Small caps begin to participate',eta:pathEta(ignition.eta),status:pathStatus(ignition.status)};
}
function altcoinCurrentStage(pkg,compass,stages){
  const at=key=>stages.find(x=>x.key===key);
  const liveOrder=['REENTRY','EXIT','DISTRIBUTION','MANIA','BROAD','MICRO','IGNITION','LARGE_MID'];
  for(const key of liveOrder){
    const s=at(key),raw=String(s?.status||'').toUpperCase();
    if(key==='REENTRY'&&reentryEngaged(raw))return{index:stages.indexOf(s),source:'LIVE',certainty:'GOVERNED'};
    if(s&&statusActive(s.status))return{index:stages.indexOf(s),source:'LIVE',certainty:'GOVERNED'};
    if(key==='DISTRIBUTION'&&/WARNING|CONFIRMED/.test(raw))return{index:stages.indexOf(s),source:'LIVE',certainty:'GOVERNED'};
  }
  const eth=compassSegment(compass,'ETH'),ethState=pathStatus(eth?.status||eth?.action);
  if(eth&&/HOLD|ACTIVE|CONFIRMED/.test(ethState)){
    const s=at('ETH_UNLOCK');
    return{index:stages.indexOf(s),source:'LIVE',certainty:'POSITION'};
  }
  const participation=at('PARTICIPATION');
  if(participation&&!/UNAVAILABLE|UNKNOWN/.test(pathStatus(participation.status))){
    return{index:stages.indexOf(participation),source:'LIVE',certainty:'POSITION'};
  }
  const monday=Array.isArray(pkg?.altseason_countdown)?pkg.altseason_countdown:[];
  const active=monday.findIndex(x=>/ACTIVE WATCH|\bACTIVE\b/i.test(String(x?.phase||'')));
  const map=[0,1,2,3,5];
  return active>=0?{index:map[active]??-1,source:'MONDAY',certainty:'REFERENCE'}:{index:-1,source:'NONE',certainty:'NONE'};
}
// Legacy release-gate compatibility only; never rendered: ETA TO TARGET GATE · Conditional gate window · not a guaranteed phase-start date
function targetHeadlineEta(target){
  const eta=pathEta(target?.eta),status=pathStatus(target?.status);
  if(eta==='NO SUPPORTED ETA'||/CONDITIONAL/i.test(eta))return null;
  if(!/ACTIVE|CONFIRMED|HOLD/.test(status))return null;
  return eta;
}
function altcoinCycleTimer(pkg,compass){
  const stages=altcoinCycleStages(pkg,compass),target=altcoinTarget(pkg,compass,stages),current=altcoinCurrentStage(pkg,compass,stages);
  const targetIndex=stages.findIndex(x=>x.key===target.key),currentStage=stages[current.index]||null,headlineEta=targetHeadlineEta(target);
  const rows=stages.map((x,i)=>{
    const isCurrent=i===current.index&&current.source==='LIVE',isTarget=i===targetIndex;
    const t=timingWindow(x.eta),rawStatus=pathStatus(x.status),timingKind=t.supported&&!t.conditional&&/WAIT|NOT CONFIRMED|UNCONFIRMED|REVIEW/.test(rawStatus)?'REVIEW WINDOW':'TIMING';
    return '<article class="alt-cycle-step tone-'+esc(pathTone(x.status))+(isCurrent?' current':'')+(isTarget?' target':'')+'"><i>'+esc(i+1)+'</i><div><span>'+esc(x.title)+'</span>'+(x.subtitle?'<small>'+esc(x.subtitle)+'</small>':'')+'</div><strong>'+esc(publicPathStatus(x.status))+'</strong><div class="alt-step-timing">'+timingMarkup(x.eta,timingKind)+'</div><details><summary>Why?</summary>'+(x.monday?'<p><em>Weekly timing:</em> '+esc(timingInline(x.monday))+'</p>':'')+'<p>'+esc(short(publicPathText(x.why),240))+'</p></details></article>';
  }).join('');
  const nowStrip=currentStage&&current.source==='LIVE'
    ?'<div class="alt-now-strip"><span>NOW POSITION</span><strong>'+esc(currentStage.title)+'</strong><b>'+esc(publicPathStatus(currentStage.status))+' · '+esc(timingInline(currentStage.eta))+'</b><small>Blue = current confirmed position in this sequence. Amber = next watch target. A watch window is conditional, never a countdown.</small></div>'
    :'<div class="alt-now-strip unresolved"><span>NOW POSITION</span><strong>Not confirmed yet</strong><b>Waiting for a fresh live signal</b><small>The weekly baseline remains visible, but the current live stage is not shown until the data can place it reliably.</small></div>';
  const targetPanel=headlineEta
    ?'<div class="alt-countdown '+(target.mode==='PROTECTION'?'protect':'')+'"><span>WATCH WINDOW · NOT CURRENT PHASE</span><strong>'+esc(timingWindow(headlineEta).label)+'</strong><b>'+esc(publicPathStatus(target.status))+'</b><small class="alt-countdown-semantics">'+esc(target.mode==='PROTECTION'?'Review window · not an automatic sell date':'This is the next watch target, not the current market phase or a countdown.')+'</small></div>'
    :'<div class="alt-countdown watch-target '+(target.mode==='PROTECTION'?'protect':'')+'"><span>WATCH TARGET · NOT CURRENT</span><strong>'+esc(publicPathStatus(target.status))+'</strong><b>'+esc(timingInline(target.eta))+'</b><small class="alt-countdown-semantics">'+esc(timingWindow(target.eta).conditional?'This window opens only if confirmation arrives. It is not a countdown to altseason.':'No headline countdown is shown unless the target timing is fully supported.')+'</small></div>';
  return '<section class="path-track altcoin-timer-v2" data-path-track="altcoin-cycle" data-contract="CN_PATH_THREE_TRACK_v2">'
    +'<header class="alt-timer-hero"><div><span>3 · ALTCOIN CYCLE TIMER</span><small>'+esc(target.eyebrow)+' · WATCH TARGET</small><h3>'+esc(target.title)+'</h3><p>'+esc(target.subtitle)+'</p></div>'+targetPanel+'</header>'
    +nowStrip
    +'<div class="alt-timer-note"><span>Blue = current confirmed position. Amber = the next gate worth watching.</span><b>Timing comes from the published market signal · no browser countdown math</b></div>'
    +'<div class="alt-cycle-rail">'+rows+'</div>'
    +'</section>';
}
function rotationFocus(compass){
  const rows=ROTATION_ORDER.map(([segment,label])=>({segment,label,row:compassSegment(compass,segment)}));
  const candidate=rows.find(x=>x.row&&!/HOLD|ACTIVE|CONFIRMED|BUY|BROADER DEPLOYMENT/i.test(String(x.row.status||x.row.action||'')))||rows.find(x=>x.row)||null;
  return candidate?{label:candidate.label,status:pathStatus(candidate.row.status||candidate.row.action),eta:pathEta(candidate.row.eta)}:{label:'UNAVAILABLE',status:'UNAVAILABLE',eta:'NO SUPPORTED ETA'};
}
function pathOverview(pkg,compass){
  const cycle=cycleForwardFromSources(pkg),cycleKnown=cycle.key!=='UNCLEAR',cycleLabel=cycleKnown?(MARKET_CYCLE.find(x=>x[0]===cycle.key)||['','UNRESOLVED'])[1]:'PHASE NOT CONFIRMED';
  const rotation=rotationFocus(compass),stages=altcoinCycleStages(pkg,compass),target=altcoinTarget(pkg,compass,stages),current=altcoinCurrentStage(pkg,compass,stages),currentStage=stages[current.index]||null;
  const nowLabel=currentStage&&current.source==='LIVE'?currentStage.title:'Not confirmed';
  const nowState=currentStage&&current.source==='LIVE'?publicPathStatus(currentStage.status):'WAITING FOR FRESH SIGNAL';
  const rotationTiming=timingWindow(rotation.eta),targetTiming=timingWindow(target.eta);
  return '<section class="path-overview-v2">'
    +'<article><span>MARKET CYCLE · LONG VIEW</span><strong>'+esc(cycleLabel)+'</strong><b>'+esc(cycleKnown?timingInline(cycle.eta):'No reliable 4–8 week phase timing yet')+'</b><small class="overview-note">Short-term momentum is visible, but the site will not guess the long-cycle stage.</small></article>'
    +'<article><span>NEXT ROTATION WATCH</span><strong>'+esc(rotation.label)+'</strong><b>'+esc(publicPathStatus(rotation.status))+'</b><small class="overview-window'+(rotationTiming.conditional?' conditional':'')+'">'+esc(rotationTiming.supported?(rotationTiming.conditional?'WATCH WINDOW · '+rotationTiming.label:'TIMING · '+rotationTiming.label):'TIMING · NOT AVAILABLE YET')+'</small>'+(rotationTiming.conditional?'<em>Only if rotation confirms · not a countdown</em>':'')+'</article>'
    +'<article class="focus"><span>ALTCOIN TIMER · NOW</span><strong>'+esc(nowLabel)+'</strong><b>'+esc(nowState)+'</b><small class="overview-target"><span>NEXT WATCH</span><strong>'+esc(target.title)+'</strong><b>'+esc(targetTiming.supported?(targetTiming.conditional?'WATCH WINDOW · '+targetTiming.label:'TIMING · '+targetTiming.label):'TIMING · NOT AVAILABLE YET')+'</b>'+(targetTiming.conditional?'<em>Only if the target confirms · not a countdown</em>':'')+'</small></article>'
    +'</section>';
}

function pathContext(data){
  const p=data.package||{},extra=sinceLastBlock(data)+whyThisCallBlock(data);
  return '<details class="path-more"><summary>More cycle context</summary><div class="horizon-grid"><article><span>2–3 WEEK OUTLOOK</span><p>'+esc(short(publicPathText(p.base_case_2_3_weeks)||'No reliable 2–3 week view is published.',270))+'</p></article><article><span>4–8 WEEK OUTLOOK</span><p>'+esc(short(publicPathText(p.base_case_4_8_weeks||p.compass_4_8_weeks)||'No reliable 4–8 week view is published.',270))+'</p></article></div>'+extra+'</details>';
}
function renderPath(data,compass){
  const p=data.package||{},alignment=pathWeeklyAlignment(data,compass),liveCompass=alignment.ok?compass:null;
  document.getElementById('productPath').innerHTML='<header class="product-head path-v2-head"><small>PATH</small><h2>Cycle. Rotation. Altcoin timing.</h2><p>Three connected views of the same market: the big cycle, capital rotation and the watch path toward the next high-beta phase — with distribution and exit kept on the same map.</p></header>'
    +pathLegend()
    +pathAlignmentNotice(alignment)
    +pathOverview(p,liveCompass)
    +marketCycleTrack(p,liveCompass)
    +rotationTrack(p,liveCompass)
    +altcoinCycleTimer(p,liveCompass)
    +pathContext(data);
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
  root.innerHTML=`<header class="product-head"><small>PROOF</small><h2>Track record, method and accountability.</h2><p>The public record is translated into three investor-friendly measures while the original archived scores remain untouched.</p></header><section class="proof-metrics"><article class="proof-coverage"><span>COMPLETED FORECAST COVERAGE</span><strong>${history.coverage?.completed_issues||records.length} / ${history.coverage?.rows_with_published_or_canonical_score_evidence||records.length}</strong><small>completed CN issues audited · no cross-era aggregate</small></article><article><span>LATEST COMPLETED</span><strong>CN #${data?.public_series?.latest_completed_score?.public_issue_number??"—"}</strong><small>${esc(data?.public_series?.latest_completed_score?.forecast_week||"Published record unavailable")} · FINAL</small></article><article><span>CURRENT FORECAST</span><strong>CN #${data?.public_series?.current_public_projection?.public_issue_number??"—"}</strong><small>OPEN · forecast locked before outcome</small></article></section>${completedForecastReceipt(data)}<section class="live-score"><span>LIVE EVIDENCE · NON-FINAL</span><strong>${esc(liveTitle)}</strong><p>${esc(liveCopy)}</p></section><section class="chart-wrap"><div class="chart-head"><div><small>ARCHIVED SCORE FAMILIES</small><h3>Records remain in their original methods</h3></div><div class="legend"><i class="weekly"></i>Archived overall <i class="price"></i>Price <i class="market"></i>Legacy structure</div></div>${sparkline(records)}</section><section class="score-method"><p><b>Forecast first. Outcome later. Historical methods are never rewritten.</b> Score families remain separate; this page intentionally does not create a lifetime accuracy number across eras.</p><p><b>Price Range Accuracy</b> remains the active public precision score. Historical Market / Structure entries remain visible in their original method. From CN #27 onward, Market Structure is analysis only, while the Bull/Bear scale remains a forward evidence balance—not an accuracy score.</p></section><section class="ledger"><div class="section-title"><div><small>ALL COMPLETED ISSUES</small><h2>CN #1 → #${records.at(-1)?.cn??records.length}</h2></div><p>Tap any row for the archived components behind the public rollup.</p></div>${rows}</section><section class="how-editorial"><header><small>HOW IT WORKS</small><h2>What the system actually watches.</h2><p>Cycle Navigator combines market structure, liquidity, positioning, participation, macro conditions and cross-asset behaviour to estimate where crypto sits in the cycle and what is most likely to matter next.</p></header><div class="data-families"><article><strong>PRICE & STRUCTURE</strong><p>Trend, momentum, volatility, Bitcoin and Ethereum behaviour, Ethereum vs Bitcoin, Bitcoin dominance and historical price structure.</p></article><article><strong>PARTICIPATION & ROTATION</strong><p>Market breadth, relative strength, altcoin participation and the movement of capital from Bitcoin into Ethereum, large caps and progressively smaller assets.</p></article><article><strong>LIQUIDITY & POSITIONING</strong><p>Stablecoin liquidity, ETF and institutional flows, derivatives positioning, leverage, funding, open interest and broader market liquidity.</p></article><article><strong>MACRO & NETWORK CONTEXT</strong><p>Macro liquidity, rates, risk appetite, selected on-chain activity and historical pattern comparisons used as context rather than as single-point signals.</p></article></div><div class="method-flow">${process.map(x=>`<article><span>${x[0]}</span><div><strong>${x[1]}</strong><p>${x[2]}</p></div></article>`).join('')}</div><p class="method-note">The exact providers, thresholds, weights, prompts, fallback routes and decision recipe remain private. The public layer explains what is analysed and how accountability works without exposing a copyable implementation.</p></section>`;
}

async function render(){
  shell();
  try{
    const [s,h,p,compass]=await Promise.all([json('./data/latest.json'),json('./history-scoreboard.json'),prices(),jsonOptional('./data/compass.json')]);snapshot=s;renderNow(s,p);document.querySelector('[data-pa-proof-native]')?.addEventListener('click',showProof);renderPath(s,compass);renderProof(s,h);installNowRefinements(s,h);document.querySelectorAll("[data-ledger-link]").forEach(b=>b.onclick=()=>{const row=document.getElementById(`cn-record-${b.dataset.ledgerLink}`);if(row){row.open=true;row.scrollIntoView({behavior:"smooth",block:"start"});}});clearInterval(refreshTimer);refreshTimer=setInterval(freshness,30000);
  }catch(e){console.warn('Cycle Navigator unavailable',e);const n=document.getElementById('productNow');if(n)n.innerHTML='<section class="fail-card"><small>MARKET DATA TEMPORARILY UNAVAILABLE</small><h1>WAIT</h1><p>No new action is inferred while verified evidence is unavailable.</p></section>';}
}

render();setInterval(render,5*60*1000);
})();
