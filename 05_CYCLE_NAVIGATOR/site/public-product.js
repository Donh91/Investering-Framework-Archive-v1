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
  const marketValues=[...parseComponentScores(record.intraday_display),...parseComponentScores(record.structure_display)];
  const market=mean(marketValues);
  const archived=Number.isFinite(record.overall)?Number(record.overall):null;
  const mayDerive = record?.allow_derived_overall === true || !['AUTOMATED_CANONICAL','DUAL_TRACK_CANONICAL'].includes(String(record?.era||''));
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
async function prices(){try{const r=await fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd',{cache:'no-store'}),d=await r.json(),b=+d.bitcoin?.usd,e=+d.ethereum?.usd;return b&&e?`BTC $${Math.round(b).toLocaleString()} · ETH $${Math.round(e).toLocaleString()} · ETH/BTC ${(e/b).toFixed(5)}`:null;}catch{return null;}}

function freshness(){
  const h=document.getElementById('productFreshness');if(!h||!snapshot)return;
  const a=snapshot.live_observation?.current_action||{},p=snapshot.package||{},d=a.generated_at?new Date(a.generated_at):p.generated_unix?new Date(+p.generated_unix*1000):null,n=new Date();
  const age=d?n-d:null,next=new Date(n);next.setUTCSeconds(0,0);if(next.getUTCMinutes()<5)next.setUTCMinutes(5);else{next.setUTCHours(next.getUTCHours()+1);next.setUTCMinutes(5);}
  const mins=x=>{const m=Math.max(0,Math.ceil(x/60000));return m>=60?`${Math.floor(m/60)}h ${m%60}m`:`${m} min`;};
  const stale=age!=null&&age>90*60*1000;
  const publicIssue=snapshot?.public_series?.current_public_projection?.public_issue_number;
  h.innerHTML=`<div><span>${stale?'LAST VERIFIED COMPASS':'MARKET COMPASS UPDATED'}</span><strong>${d?d.toLocaleString([],{day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'}):'Awaiting fresh data'}</strong><small>${age!=null?`${mins(age)} ago`:'No verified live timestamp'}</small></div><div><span>NEXT UPDATE</span><strong>${mins(next-n)}</strong><small>Expected after the next market-data cycle</small></div><div><span>CURRENT WEEKLY OUTLOOK</span><strong>CN #${esc(publicIssue??p.issue_number??'—')}</strong><small>Public-series numbering, unchanged by live updates</small></div>`;
}

function rotationEta(item){
  const explicit=item?.eta||item?.window||item?.timing;if(explicit)return investorText(explicit);
  return({active:'Now',hold:'Now · reassess on the next update',watch:'Next confirmation',wait:'No reliable estimate yet',pause:'No ETA until conditions improve',unknown:'No reliable estimate yet'})[state(item?.status)]||'No reliable estimate yet';
}

function capitalRail(rows){
  rows=Array.isArray(rows)&&rows.length?rows:[{segment:'Bitcoin'},{segment:'Ethereum'},{segment:'Large caps'},{segment:'Mid caps'},{segment:'Small caps'},{segment:'Microcaps'}];
  return `<div class="capital-line">${rows.map((r,i)=>`<div class="capital-step state-${state(r.status)}"><div class="capital-node">${i+1}</div><div class="capital-copy"><div class="capital-title"><strong>${esc(r.segment||'Segment')}</strong><b>${statusLabel(r.status)}</b></div><p>${esc(actionCopy(r.status))}</p><small>ETA · ${esc(rotationEta(r))}</small></div></div>`).join('')}</div>`;
}

function renderNow(data,px){
  const p=data.package||{},live=data.live_observation||{},a=live.current_action||{},st=String(a.stance||'WAIT').toUpperCase(),available=!!a.generated_at,limited=/DATA_DEGRADED/i.test(String(a.current||''));
  const marketPhase=phaseCopy(p.market_state||'');
  const next=investorText(a.next_days)||(`Stay ${actionTitle(st).toLowerCase()} while the next market confirmation develops.`);
  const confirm=gate(a.confirmation,'confirm'),risk=gate(a.invalidation,'risk');
  const headline=!available?'Fresh evidence is temporarily unavailable. No new risk call is inferred from price alone.':limited?'Signal confidence is temporarily limited. Keep risk contained until the evidence improves.':({HOLD:'Keep current positioning. Do not add broad market risk yet.',WAIT:'Stay patient. A broader risk-on move is not confirmed yet.',PREPARE:'Prepare for a possible shift, but wait for confirmation before adding broadly.',SELECTIVE:'Add selectively only. Broad market risk is not confirmed yet.','PROTECT CAPITAL':'Reduce risk and protect capital until conditions improve.','BROADER DEPLOYMENT':'Broader participation is confirmed enough to add risk across the market.'}[st]||'Keep the current stance until the evidence changes.');
  document.getElementById('productNow').innerHTML=`<div id="productFreshness" class="freshness-strip"></div><section class="action-hero"><div class="action-label">MARKET COMPASS</div><div class="action-word">${esc(available?actionTitle(st):'WAIT')}</div><p>${esc(headline)}</p><div class="hero-lines"><div><span>MARKET PHASE</span><strong>${esc(marketPhase)}</strong></div><div><span>NEXT 1–3 DAYS</span><strong>${esc(short(next,180))}</strong></div><div><span>NEXT CONFIRMATION</span><strong>${esc(short(confirm,180))}</strong></div><div class="risk-line"><span>RISK</span><strong>${esc(short(risk,170))}</strong></div></div></section><section class="now-section"><div class="section-title"><div><small>CAPITAL ROTATION · HERE AND NOW</small><h2>Bitcoin → microcaps</h2></div><p>How far out on the risk curve the current evidence supports going right now.</p></div>${capitalRail(p.rotation_ladder)}</section><section class="context-row"><article><span>LIVE MARKET</span><strong>${esc(px||'Live prices temporarily unavailable')}</strong><small>Market context only. Prices cannot rewrite the weekly outlook.</small></article><article><span>THIS WEEK</span><strong>${esc(short(investorText(p.base_case_this_week||p.market_state)||'No public weekly summary available.',220))}</strong><small>Plain-English translation of the current weekly outlook.</small></article></section>`;
  freshness();
}

function renderPath(data){
  const p=data.package||{},raw=Array.isArray(p.altseason_countdown)?p.altseason_countdown:[];
  const stages=raw.length?raw:[{phase:'Bitcoin leadership',window:'No reliable estimate yet'},{phase:'Consolidation / transition',window:'No reliable estimate yet'},{phase:'Ethereum + large caps strengthen',window:'No reliable estimate yet'},{phase:'Broad altcoin participation',window:'No reliable estimate yet'},{phase:'High-risk expansion',window:'No reliable estimate yet'}];
  let current=stages.findIndex(x=>['active','watch','hold'].includes(state(x.phase)));if(current<0)current=0;
  const rail=stages.map((x,i)=>{
    const future=i>current,where=i===current?'YOU ARE HERE':i<current?'EARLIER':'NEXT IF CONFIRMED';
    const explanation=i===current?'Current market phase. The investor action can still remain more defensive than the phase itself.':i===current+1?'What moves us here: stronger Ethereum leadership and broader participation.':future?'What moves us here: the preceding stage must confirm and participation must broaden further.':'This stage helped define the path into the current market state.';
    const delay=future?'What delays it: renewed relative weakness or narrowing participation.':'';
    return `<article class="cycle-step ${future?'future':''} state-${state(x.phase)}"><span>${i+1}</span><div><em>${where}</em><strong>${esc(stageName(x.phase,i))}</strong><p>${esc(explanation)}</p>${delay?`<p class="delay">${esc(delay)}</p>`:''}<small>ETA · ${esc(investorText(x.window)||'No reliable estimate yet')}</small></div></article>`;
  }).join('');
  document.getElementById('productPath').innerHTML=`<header class="product-head"><small>CONDITIONAL MARKET PATH</small><h2>Where capital could rotate next.</h2><p>This is a sequence of confirmations, not a promise of altseason. Market phase and investor action are shown separately so a developing rotation never automatically becomes a buy signal.</p></header><div class="cycle-line">${rail}</div><section class="horizon-grid"><article><span>NEXT 2–3 WEEKS</span><p>${esc(short(investorText(p.base_case_2_3_weeks)||'No supported 2–3 week view is published.',270))}</p></article><article><span>NEXT 4–8 WEEKS</span><p>${esc(short(investorText(p.base_case_4_8_weeks||p.compass_4_8_weeks)||'No supported 4–8 week view is published.',270))}</p></article></section>`;
}

function renderProof(data,history){
  const root=document.getElementById('productProof'),records=history.records||[],scores=records.map(r=>({record:r,...publicScores(r)}));
  const weekly=mean(scores.map(x=>x.weekly).filter(Number.isFinite)),price=mean(scores.map(x=>x.price).filter(Number.isFinite)),market=mean(scores.map(x=>x.market).filter(Number.isFinite));
  const live=data.live_observation||{},meas=Number(live.provisional_coverage?.measurable||0),total=Number(live.provisional_coverage?.total||live.claims_due_this_week||0),liveScore=Number(live.provisional_score);
  const liveTitle=meas>0&&Number.isFinite(liveScore)?`${Math.round(liveScore)}% so far`:'Waiting for evidence';
  const liveCopy=meas>0?`${meas} of ${total||meas} weekly calls are ready to be evaluated. This remains provisional until the week is complete.`:`0 of ${total||0} weekly calls are ready to be evaluated. No percentage is shown until at least one call is genuinely scoreable.`;
  const rows=[...scores].reverse().map(x=>`<details class="ledger-row"><summary><span><strong>CN #${x.record.cn}</strong><small>${x.derived?'component rollup':'published overall preserved'}</small></span><b>${pct(x.weekly)}</b><span>${pct(x.price)}<small>PRICE</small></span><span>${pct(x.market)}<small>MARKET / CYCLE</small></span></summary><div class="ledger-detail"><p><b>Archived price evidence:</b> ${esc(x.record.range_display||'No numerical price-range score published for this issue.')}</p><p><b>Archived market evidence:</b> ${esc([x.record.intraday_display,x.record.structure_display].filter(Boolean).join(' · ')||'No additional numerical component published.')}</p></div></details>`).join('');
  const process=[
    ['1','COLLECT & VERIFY','Market observations are gathered continuously, timestamped and checked for freshness, conflicts and missing inputs before they can influence the public view.'],
    ['2','ANALYSE INDEPENDENTLY','Different analytical lenses assess trend, relative strength, participation, liquidity, positioning, risk and rotation instead of relying on one indicator.'],
    ['3','CHALLENGE THE EVIDENCE','Contradictory or weak signals reduce confidence. The system is designed to prefer “not enough evidence” over forcing a clean answer.'],
    ['4','SYNTHESISE WEEKLY','Once a week, the evidence is combined into one public market outlook: current phase, expected path, risk conditions and price expectations where the data supports them.'],
    ['5','LOCK BEFORE THE OUTCOME','The weekly forecast is fixed before the market outcome is known. Later live data can change the current action, but it cannot rewrite the original forecast.'],
    ['6','MONITOR LIVE','Between weekly publications, a separate live layer checks whether the investor posture should remain hold, prepare, selective, defensive or broader risk-on.'],
    ['7','SCORE & LEARN','When outcomes mature, the archived call is compared with the market. Price accuracy and market/cycle understanding are tracked separately, and misses feed future learning rather than changing the past.']
  ];
  root.innerHTML=`<header class="product-head"><small>PROOF</small><h2>Track record, method and accountability.</h2><p>The public record is translated into three investor-friendly measures while the original archived scores remain untouched.</p></header><section class="proof-metrics"><article><span>HISTORICAL WEEKLY AVERAGE</span><strong>${pct(weekly)}</strong><small>${records.length} completed Cycle Navigators</small></article><article><span>PRICE RANGE ACCURACY</span><strong>${pct(price)}</strong><small>${scores.filter(x=>Number.isFinite(x.price)).length}/${records.length} issues with published numerical range evidence</small></article><article><span>MARKET & CYCLE UNDERSTANDING</span><strong>${pct(market)}</strong><small>${scores.filter(x=>Number.isFinite(x.market)).length}/${records.length} issues with published non-price evidence</small></article></section><section class="live-score"><span>THIS WEEK</span><strong>${esc(liveTitle)}</strong><p>${esc(liveCopy)}</p></section><section class="chart-wrap"><div class="chart-head"><div><small>HISTORICAL CONSISTENCY</small><h3>Weekly · Price · Market/Cycle</h3></div><div class="legend"><i class="weekly"></i>Weekly <i class="price"></i>Price <i class="market"></i>Market/Cycle</div></div>${sparkline(records)}</section><section class="score-method"><p><b>Weekly score</b> preserves the archived overall when one was published. For older issues without a single overall number, the public rollup uses only that issue's published Price and Market/Cycle components. <b>Price Range Accuracy</b> gives each Cycle Navigator one vote, even if both BTC and ETH were scored. <b>Market & Cycle Understanding</b> combines the published non-price components such as direction, regime, rotation, breadth, relative strength and intraday path.</p><p>Scoring methodology evolved over time. These presentation averages intentionally span those eras, as a simple public track-record summary, while the underlying historical records remain unchanged.</p></section><section class="ledger"><div class="section-title"><div><small>ALL COMPLETED ISSUES</small><h2>CN #1 → #${records.at(-1)?.cn??records.length}</h2></div><p>Tap any row for the archived components behind the public rollup.</p></div>${rows}</section><section class="how-editorial"><header><small>HOW IT WORKS</small><h2>What the system actually watches.</h2><p>Cycle Navigator combines market structure, liquidity, positioning, participation, macro conditions and cross-asset behaviour to estimate where crypto sits in the cycle and what is most likely to matter next.</p></header><div class="data-families"><article><strong>PRICE & STRUCTURE</strong><p>Trend, momentum, volatility, Bitcoin and Ethereum behaviour, Ethereum vs Bitcoin, Bitcoin dominance and historical price structure.</p></article><article><strong>PARTICIPATION & ROTATION</strong><p>Market breadth, relative strength, altcoin participation and the movement of capital from Bitcoin into Ethereum, large caps and progressively smaller assets.</p></article><article><strong>LIQUIDITY & POSITIONING</strong><p>Stablecoin liquidity, ETF and institutional flows, derivatives positioning, leverage, funding, open interest and broader market liquidity.</p></article><article><strong>MACRO & NETWORK CONTEXT</strong><p>Macro liquidity, rates, risk appetite, selected on-chain activity and historical pattern comparisons used as context rather than as single-point signals.</p></article></div><div class="method-flow">${process.map(x=>`<article><span>${x[0]}</span><div><strong>${x[1]}</strong><p>${x[2]}</p></div></article>`).join('')}</div><p class="method-note">The exact providers, thresholds, weights, prompts, fallback routes and decision recipe remain private. The public layer explains what is analysed and how accountability works without exposing a copyable implementation.</p></section>`;
}

async function render(){
  shell();
  try{
    const [s,h,p]=await Promise.all([json('./data/latest.json'),json('./history-scoreboard.json'),prices()]);snapshot=s;renderNow(s,p);renderPath(s);renderProof(s,h);clearInterval(refreshTimer);refreshTimer=setInterval(freshness,30000);
  }catch(e){console.warn('Cycle Navigator unavailable',e);const n=document.getElementById('productNow');if(n)n.innerHTML='<section class="fail-card"><small>MARKET DATA TEMPORARILY UNAVAILABLE</small><h1>WAIT</h1><p>No new action is inferred while verified evidence is unavailable.</p></section>';}
}

render();setInterval(render,5*60*1000);
})();
