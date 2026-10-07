(() => {
'use strict';

window.CN_PREMIUM_COMPASS_OWNER = true;
// Legacy release-gate wording only, never rendered: RECOMMENDATION · APPLIES NOW · NEXT GOVERNED REVIEW

const COMPASS_URL = './data/compass.json';
const SNAPSHOT_URL = './data/latest.json';
const HORIZONS = [
  { scale: '1_3d', lane: 'NEXT_1_3D', label: '1–3 DAYS', title: 'Near term' },
  { scale: '5_7d', lane: 'NEXT_5_7D', label: '5–7 DAYS', title: 'This week' },
  { scale: '2_3w', lane: 'NEXT_2_3W', label: '2–3 WEEKS', title: 'Forward view' }
];

const esc = (value) => String(value ?? '')
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#039;');

const words = (value) => String(value || '').replaceAll('_', ' ').replace(/\s+/g, ' ').trim();
const clean = (value) => typeof value === 'string' && value.trim() ? value.trim() : null;
const publicState = (value) => {
  const s = words(value).toUpperCase();
  if (s === 'UNAVAILABLE') return 'NOT READY';
  if (s === 'UNKNOWN') return 'UNCLEAR';
  if (s === 'UNCHANGED NO NEW OBSERVATION') return 'NO NEW READING';
  if (s === 'HARD WAIT') return 'WAIT';
  if (s === 'INACTIVE' || s === 'LOCKED') return 'NOT ACTIVE';
  return s || 'WAITING';
};
const publicDataStatus = (value) => {
  const s = words(value).toUpperCase();
  if (s === 'OK' || s === 'PASS') return 'UP TO DATE';
  if (/DEGRADED|STALE/.test(s)) return 'LIMITED';
  return s === 'UNAVAILABLE' || !s ? 'WAITING' : s;
};
const publicCompassText = (value) => {
  let s = words(value)
    .replace(/\bW(\d+)\b/g, 'week $1')
    .replace(/MASTER MONDAY/gi, 'weekly review')
    .replace(/\bgoverned\b/gi, 'verified')
    .replace(/\bcanonical\b/gi, 'confirmed')
    .replace(/\bframework\b/gi, 'research process')
    .replace(/\bdecision owner\b/gi, 'signal source')
    .replace(/\bowner\b/gi, 'signal source')
    .replace(/\bETHBTC\b/gi, 'Ethereum vs Bitcoin')
    .replace(/\bETH\/BTC\b/gi, 'Ethereum vs Bitcoin')
    .replace(/\bETH-relative\b/gi, 'Ethereum-relative')
    .replace(/\bbreadth\b/gi, 'market participation')
    .replace(/\bmicrostructure\b/gi, 'market structure')
    .replace(/\baction posture\b/gi, 'current action')
    .replace(/\bALTCOIN_SEASON\b/gi, 'altcoin-season')
    .replace(/\b30d shadow source\b/gi, '30-day altcoin participation reading')
    .replace(/\bbroad transmission\b/gi, 'broad participation')
    .replace(/\bcapital transmission\b/gi, 'capital rotation')
    .replace(/\s+/g, ' ')
    .trim();
  const exact = [
    [/The 30-day altcoin participation reading ended at 78 with an altcoin-season label, but 90d was 55 and 365d was 37; the shorter-window label varied during This week\.?/i,
      'The 30-day altcoin participation reading was strong, while the 90-day and one-year readings were materially weaker. Shorter-term participation also moved around during the week.'],
    [/Five settled sessions totaled \+82\.9 in reported BTC ETF units versus [−-]118\.0 in ETH ETF units; final weekly review describes mixed market structure and no confirmed broad participation\.?/i,
      'Recent settled ETF flows favoured Bitcoin over Ethereum, while market structure remained mixed and broad altcoin participation was not confirmed.'],
    [/Meme risk is a separate rung and requires a verified meme-specific signal source\. No such signal source is currently bound, so MICROCAPS cannot be used as a proxy\.?/i,
      'Meme risk needs its own confirmed signal. No meme-specific signal is active yet, so microcaps are not used as a substitute.']
  ];
  for (const [pattern, replacement] of exact) s = s.replace(pattern, replacement);
  return s;
};

function officialScale(compass) {
  const scale = compass?.bull_bear_scale;
  if (scale?.contract !== 'OFFICIAL_COMPASS_BULL_BEAR_DISPLAY_v1') return null;
  if (scale?.semantics !== 'EVIDENCE_BALANCE_NOT_PROBABILITY') return null;
  if (scale?.owner !== 'OFFICIAL_COMPASS') return null;
  if (scale?.source_of_truth_contract !== 'MARKET_WEATHER_SOURCE_OF_TRUTH_v1') return null;
  if (scale?.authority?.site_synthesis_allowed !== false) return null;
  return scale;
}

function scoreRow(scale, key) {
  const row = scale?.horizons?.[key] || {};
  const bull = Number(row.bull);
  const bear = Number(row.bear);
  const ok = row.status === 'OK'
    && Number.isInteger(bull)
    && Number.isInteger(bear)
    && bull >= 0 && bull <= 10
    && bear >= 0 && bear <= 10
    && bull + bear === 10;
  return { ...row, bull: ok ? bull : null, bear: ok ? bear : null, ok };
}

function publicAction(raw) {
  const value = String(raw || '').toUpperCase();
  if (/GRADUATED_TOPUP_ACTIVE|BROAD.*DEPLOY|BROAD.*TOPUP/.test(value)) return 'ADD BROADLY';
  if (/PREPARE/.test(value)) return 'PREPARE';
  if (/HOLD_DEFENSIVE|PROTECT|DE_RISK|REDUCE|EXIT/.test(value)) return 'PROTECT CAPITAL';
  if (/SELECTIVE|TOPUP/.test(value)) return 'ADD SELECTIVELY';
  if (/HOLD/.test(value)) return 'HOLD';
  return 'WAIT';
}

function recommendation(raw) {
  const action = publicAction(raw);
  const map = {
    'ADD BROADLY': 'Broader participation is confirmed enough to add risk, while keeping the published invalidation conditions in view.',
    'ADD SELECTIVELY': 'Add selectively only. Broader market risk is not yet confirmed across the full rotation ladder.',
    'PREPARE': 'Prepare for a possible shift, but wait for confirmation before broadening exposure.',
    'PROTECT CAPITAL': 'Keep risk contained and protect capital until the Market Compass confirms that conditions have repaired.',
    'HOLD': 'Keep current positioning. Do not broaden risk from this reading alone.',
    'WAIT': 'Stay patient. Do not infer a new risk-on call until the Market Compass publishes enough evidence.'
  };
  return { action, copy: map[action] || map.WAIT };
}

function cnConclusion(snapshot) {
  const pkg = snapshot?.package || {};
  return publicCompassText(clean(pkg.base_case_this_week)
    || clean(pkg.market_state)
    || 'The current weekly Cycle Navigator conclusion is not available.');
}

function twoThreeWeekContext(snapshot) {
  const pkg = snapshot?.package || {};
  return publicCompassText(clean(pkg.base_case_2_3_weeks) || 'No separate 2–3 week Cycle Navigator context is published.');
}

function statusTone(row) {
  const bias = String(row?.bias || '').toUpperCase();
  if (!row?.ok) return 'pending';
  if (/BULL|UP/.test(bias)) return 'bull';
  if (/BEAR|DOWN/.test(bias)) return 'bear';
  return 'neutral';
}

function actionFromLane(lane) {
  const p = String(lane?.action_posture || '').toUpperCase();
  if (/PREPARE|ADD|DEPLOY|TOPUP|BUY/.test(p)) return 'PREPARE';
  if (/HOLD/.test(p)) return 'HOLD';
  return 'WAIT';
}

function capSummary(compass) {
  const rows = Array.isArray(compass?.capitalization_ladder) ? compass.capitalization_ladder : [];
  if (!rows.length) return 'Risk-rotation evidence is not available.';
  return rows.slice(0, 6).map((row) => words(row.segment) + ' ' + publicState(row.status)).join(' · ');
}

function riskSummary(compass) {
  const protection = compass?.protection_tracker || {};
  const pullback = publicState(protection.pullback_risk_state || 'UNAVAILABLE');
  return 'Pullback ' + pullback;
}

function decisionMeta(compass) {
  const market = compass?.market_now || {};
  const near = compass?.horizons?.NEXT_12H || {};
  const weekly = compass?.horizons?.NEXT_5_7D || {};
  const protection = compass?.protection_tracker || {};
  return {
    live: publicState(market.directional_state || market.regime || near.label || near.expected_direction || 'UNAVAILABLE'),
    liveEta: clean(near.eta) || clean(compass?.next_meaningful_change_eta) || 'No fixed ETA',
    weekly: publicState(weekly.label || weekly.expected_direction || 'UNAVAILABLE'),
    weeklyEta: clean(weekly.eta) || '5–7d',
    risk: riskSummary(compass),
    riskEta: clean(protection.eta_window) || 'No supported risk window',
    distribution: publicState(protection.distribution_risk || 'UNKNOWN')
  };
}

function recommendationWindow(compass) {
  const explicit = clean(compass?.next_meaningful_change_eta);
  const near = clean(compass?.horizons?.NEXT_12H?.eta);
  const fallback = clean(compass?.horizons?.NEXT_1_3D?.eta);
  return explicit || near || fallback || 'Next Compass update';
}

function decisionDetail(compass, rec, meta) {
  const protection = compass?.protection_tracker || {};
  const invalidation = publicCompassText(clean(protection.invalidation) || 'No public invalidation condition is currently available.');
  const issued = clean(compass?.issued_at_utc);
  const issuedLabel = issued ? new Date(issued).toLocaleString('en-GB',{timeZone:'Europe/Copenhagen',day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit',hour12:false}).replace(',','') + ' CPH' : 'timestamp unavailable';
  const investor = rec.action === 'HOLD'
    ? 'Keep existing positioning. The bearish 0–12h pressure reading is tactical, not the 5–7 day base case. Do not broaden high-beta exposure from this signal alone.'
    : rec.copy;
  const swing = 'Treat ' + meta.live + ' over ' + meta.liveEta + ' as short-horizon pressure, while the 5–7 day outlook remains ' + meta.weekly + '. ' + meta.risk + ' means a retest deserves attention, but it is not a confirmed sell, short or distribution signal.';
  return '<details id="liveDecisionDetail" class="premium-decision-detail">'
    + '<summary><span>DECISION DETAIL</span><b>Investor + swing trader context</b></summary>'
    + '<div class="premium-decision-body">'
    + '<div class="premium-decision-strip"><div><span>NEAR-TERM PRESSURE</span><strong>'+esc(meta.live)+'</strong><small>'+esc(meta.liveEta)+'</small></div><div><span>WEEKLY OUTLOOK</span><strong>'+esc(meta.weekly)+'</strong><small>'+esc(meta.weeklyEta)+'</small></div><div><span>RISK WINDOW</span><strong>'+esc(meta.risk)+'</strong><small>'+esc(meta.riskEta)+'</small></div></div>'
    + '<div class="premium-audience-grid"><article><span>FOR AN INVESTOR</span><p>'+esc(investor)+'</p></article><article><span>FOR A SWING TRADER</span><p>'+esc(swing)+'</p></article></div>'
    + '<div class="premium-risk-detail"><span>WHAT TO WATCH</span><strong>'+esc(meta.risk)+' · Distribution '+esc(meta.distribution)+'</strong><p><b>When:</b> '+esc(meta.riskEta)+'</p><p><b>Risk weakens if:</b> '+esc(invalidation)+'</p><small>Risk context is not a sell instruction. Market Compass updated '+esc(issuedLabel)+'.</small></div>'
    + '</div></details>';
}

function hourlyMonitor(snapshot) {
  const live = snapshot?.live_observation;
  const action = live?.current_action || {};
  if (live?.contract !== 'CYCLE_NAVIGATOR_PUBLIC_LIVE_OBSERVATION_v2' || !clean(action.generated_at)) {
    return '<div class="premium-live-monitor unavailable"><span>HOURLY MONITOR</span><strong>AWAITING VERIFIED UPDATE</strong><small>Context only. Current action comes from the verified Market Compass.</small></div>';
  }
  const d = new Date(action.generated_at);
  const ageMinutes = Number.isFinite(d.getTime()) ? Math.max(0, Math.floor((Date.now() - d.getTime()) / 60000)) : null;
  const age = ageMinutes === null ? 'unknown age' : ageMinutes >= 60 ? Math.floor(ageMinutes / 60) + 'h ' + (ageMinutes % 60) + 'm ago' : ageMinutes + 'm ago';
  const raw = String(action.current || '').toUpperCase();
  const stale = ageMinutes === null || ageMinutes > 90;
  const degraded = /DATA_DEGRADED/.test(raw);
  const health = stale ? 'STALE' : degraded ? 'DEGRADED' : 'LIVE';
  const cls = stale ? ' stale' : degraded ? ' degraded' : '';
  return '<div class="premium-live-monitor' + cls + '"><span>HOURLY MONITOR</span><strong>' + esc(publicAction(action.stance || action.current)) + ' · ' + esc(health) + '</strong><small>Updated ' + esc(age) + ' · context only. Current action comes from the verified Market Compass.</small></div>';
}

function soWhat(row, lane) {
  if (!row?.ok) return 'No verified edge yet — wait for a fresh reading.';
  const action = actionFromLane(lane);
  const tone = statusTone(row);
  if (action === 'PREPARE' && tone === 'bull') return 'Prepare selectively — confirmation still comes before broad risk.';
  if (action === 'PREPARE') return 'Prepare, but keep deployment conditional on confirmation.';
  if (action === 'HOLD') return 'Stay positioned — do not chase high-beta from this horizon alone.';
  if (tone === 'bull') return 'Bullish pressure is visible, but the current action still says wait.';
  if (tone === 'bear') return 'Downside pressure dominates — keep new high-beta risk contained.';
  return 'No broad edge — keep high-beta risk contained.';
}

function ladderTone(status) {
  const s = String(status || '').toUpperCase();
  if (/DEPLOY|ACTIVE|ELIGIBLE/.test(s)) return 'active';
  if (/PREPARE|WATCH/.test(s)) return 'watch';
  if (/HOLD/.test(s)) return 'hold';
  if (/WAIT/.test(s)) return 'wait';
  return 'pending';
}

function riskCurve(compass) {
  const rows = Array.isArray(compass?.capitalization_ladder) ? compass.capitalization_ladder : [];
  const ordered = ['BTC','ETH','LARGE_CAPS','MID_CAPS','SMALL_CAPS','MICROCAPS','MEMES'];
  const bySegment = new Map(rows.map((row) => [String(row?.segment || '').toUpperCase(), row]));
  const resolved = ordered.map((segment) => bySegment.get(segment) || { segment, status: 'UNAVAILABLE', action: 'UNAVAILABLE', reason: 'No verified public reading is available.' });
  const meme = resolved.find((row) => String(row.segment).toUpperCase() === 'MEMES') || {};
  const rail = resolved.map((row, index) => {
    const label = words(row.segment).replace('LARGE CAPS','LARGE').replace('MID CAPS','MID').replace('SMALL CAPS','SMALL').replace('MICROCAPS','MICRO');
    return '<div class="premium-rung tone-' + esc(ladderTone(row.status)) + '"><i>' + esc(index + 1) + '</i><span>' + esc(label) + '</span><strong>' + esc(publicState(row.status || row.action || 'UNAVAILABLE')) + '</strong></div>';
  }).join('');
  return '<section class="premium-risk-curve">'
    + '<header><div><span class="premium-kicker">RISK CURVE · NOW</span><h3>Bitcoin → memes</h3></div><p>How far out on the risk curve the verified evidence currently supports going.</p></header>'
    + '<div class="premium-rung-grid">' + rail + '</div>'
    + '<div class="premium-meme-focus"><span>MEME RISK</span><strong>' + esc(publicState(meme.status || meme.action || 'UNAVAILABLE')) + '</strong><p>' + esc(publicCompassText(clean(meme.reason) || 'No verified meme-specific signal is available yet.')) + '</p><small>ETA · ' + esc(clean(meme.eta) || 'No fixed ETA') + '</small></div>'
    + '</section>';
}

function evidenceDrivers(compass) {
  const rows = Array.isArray(compass?.protection_tracker?.decisive_public_drivers)
    ? compass.protection_tracker.decisive_public_drivers.filter(Boolean).slice(0, 4)
    : [];
  return rows.map((x) => publicCompassText(x));
}

function scoreFormula(row) {
  if (!row.ok) {
    return '<div class="premium-formula pending"><span>OFFICIAL BALANCE</span><strong>AWAITING VERIFIED READ</strong><small>No Bull/Bear number is reconstructed by the website.</small></div>';
  }
  return '<div class="premium-formula"><span>OFFICIAL BALANCE</span><strong>BULL ' + esc(row.bull) + ' + BEAR ' + esc(row.bear) + ' = 10</strong><small>Evidence balance, not probability. Published by the Market Compass.</small></div>';
}

function evidenceFamily(label, copy) {
  return '<article><span>' + esc(label) + '</span><p>' + esc(copy) + '</p></article>';
}

function detailsPanel(snapshot, compass, row, lane, horizon) {
  const drivers = evidenceDrivers(compass);
  const context23 = horizon.scale === '2_3w' && !row.ok
    ? '<div class="premium-cn-context"><span>CYCLE NAVIGATOR CONTEXT · NOT A LIVE SCORE</span><p>' + esc(twoThreeWeekContext(snapshot)) + '</p></div>'
    : '';
  const driverBlock = drivers.length
    ? '<div class="premium-drivers"><span>CURRENT PUBLIC EVIDENCE</span><ul>' + drivers.map((x) => '<li>' + esc(x) + '</li>').join('') + '</ul></div>'
    : '<div class="premium-drivers"><span>CURRENT PUBLIC EVIDENCE</span><p>No decisive public drivers are published for this Compass state.</p></div>';

  return '<details class="premium-breakdown">'
    + '<summary><span>HOW THIS READING IS BUILT</span><b>View inputs & method</b></summary>'
    + '<div class="premium-breakdown-body">'
    + scoreFormula(row)
    + '<div class="premium-call"><div><span>DIRECTION</span><strong>' + esc(publicState(lane?.expected_direction || row?.bias || 'UNAVAILABLE')) + '</strong></div><div><span>ACTION</span><strong>' + esc(actionFromLane(lane)) + '</strong></div><div><span>WINDOW</span><strong>' + esc(lane?.eta || horizon.label) + '</strong></div></div>'
    + '<div class="premium-families">'
    + evidenceFamily('PRICE & STRUCTURE', 'BTC and ETH price behaviour, relative trend and the horizon-specific market path.')
    + evidenceFamily('PARTICIPATION & ROTATION', 'Market participation, Ethereum vs Bitcoin, Bitcoin dominance and capital movement across size tiers.')
    + evidenceFamily('LIQUIDITY & POSITIONING', 'Settled ETF flows, stablecoin liquidity, open interest, funding and leverage context when eligible.')
    + evidenceFamily('SENTIMENT & CYCLE', 'Market sentiment, risk conditions and the weekly Cycle Navigator context for the relevant horizon.')
    + '</div>'
    + driverBlock
    + context23
    + '<p class="premium-method-note"><b>Important:</b> the website displays the published score exactly as issued. It does not recalculate or reverse-engineer private thresholds, weights, prompts or fallback routes. Contradictory or stale evidence reduces confidence or leaves the horizon unavailable.</p>'
    + '</div></details>';
}

function horizonCard(snapshot, compass, scale, horizon) {
  const row = scoreRow(scale, horizon.scale);
  const lane = compass?.horizons?.[horizon.lane] || {};
  const tone = statusTone(row);
  const score = row.ok
    ? '<div class="premium-score"><strong>' + esc(row.bull) + '</strong><span>BULL</span><i>vs</i><strong>' + esc(row.bear) + '</strong><span>BEAR</span></div>'
    : '<div class="premium-score unavailable"><strong>—</strong><span>AWAITING</span></div>';
  const meter = row.ok
    ? '<div class="premium-meter" style="--bull:' + esc(row.bull * 10) + '%"><div class="premium-bear-zone"></div><i aria-hidden="true"></i><div class="premium-bull-zone"></div></div>'
    : '<div class="premium-meter unavailable"><div></div></div>';
  const call = row.ok ? words(row.bias || 'NEUTRAL') : 'AWAITING COMPASS';
  const summary = publicCompassText(clean(row.summary) || clean(lane.expected_path) || 'No verified reading is published for this horizon.');
  const takeaway = soWhat(row, lane);
  return '<article class="premium-horizon tone-' + esc(tone) + '">'
    + '<header><div><span class="premium-horizon-label">' + esc(horizon.label) + '</span><small>' + esc(horizon.title) + '</small></div><b>' + esc(call) + '</b></header>'
    + score
    + meter
    + '<p>' + esc(summary) + '</p>'
    + '<div class="premium-so-what"><span>SO WHAT?</span><strong>' + esc(takeaway) + '</strong></div>'
    + '<div class="premium-horizon-meta"><span>' + esc(actionFromLane(lane)) + '</span><span>' + esc(lane?.eta || 'No fixed ETA') + '</span></div>'
    + detailsPanel(snapshot, compass, row, lane, horizon)
    + '</article>';
}

function pullbackCard(compass) {
  const valid=compass?.contract==='PUBLIC_COMPASS_PROJECTION_v1'&&compass?.data_status==='OK';
  const p=valid&&compass?.protection_tracker?.contract==='COMPASS_PROTECTION_TRACKER_v1'?compass.protection_tracker:{};
  const sell=valid&&compass?.sell_assessment?.contract==='COMPASS_SELL_ASSESSMENT_v1'?compass.sell_assessment:{};
  const state=String(p.pullback_risk_state||'UNAVAILABLE').toUpperCase();
  const classification=clean(p.pullback_class),ordinary=!!classification&&/ORDINARY|RETEST|DIP/i.test(classification)&&!/MAJOR|SEVERE|DEEP/i.test(classification);
  const title=state==='UNAVAILABLE'?'Risk assessment unavailable':state==='NORMAL'?'No major pullback signal':ordinary?'Ordinary dip watch':'Pullback watch';
  const status=state==='BUILDING'?'DEVELOPING · UNCONFIRMED':state==='NORMAL'?'NO ACTIVE WARNING':publicState(state);
  const rawCopy=p.public_explanation,copy=rawCopy?.contract==='CN_PUBLIC_PROTECTION_COPY_v1'&&rawCopy.action_authority===false&&rawCopy.risk_state===state&&rawCopy.risk_class===classification.toUpperCase()&&rawCopy.forecast_week===compass?.weekly_context?.forecast_week?rawCopy:null;
  const safeCopy=v=>typeof v==='string'&&v.length<=180&&!/\d|%|\b(?:buy|sell|short|rebuy|guaranteed|probability|internal|shadow|data_ping)\b/i.test(v)?v:null;
  let start=Date.parse(copy?.onset_start_utc),end=Date.parse(copy?.onset_end_utc);
  // Legacy date formatting changes no alert or action: only an explicit owner's Day N–N window.
  if(!Number.isFinite(start)||!Number.isFinite(end)){
    const week=String(compass?.weekly_context?.forecast_week||'').match(/^(\d{4})-W(\d{2})$/),days=String(p.eta_window||'').match(/\bDay\s+([1-7])\s*[–-]\s*([1-7])\b/i);
    if(week&&days&&Number(days[1])<=Number(days[2])){
      const jan4=new Date(Date.UTC(Number(week[1]),0,4)),monday=jan4.getTime()-((jan4.getUTCDay()+6)%7)*86400000+(Number(week[2])-1)*7*86400000;
      start=monday+(Number(days[1])-1)*86400000;end=monday+Number(days[2])*86400000;
    }
  }
  const date=v=>new Date(v).toLocaleDateString('en-GB',{day:'numeric',month:'short',timeZone:'UTC'});
  const timing=Number.isFinite(start)&&Number.isFinite(end)&&end>start?(Date.now()>=end?'Prior watch window · ':Date.now()>=start?'Window open · ':'Possible onset · ')+date(start)+'–'+date(end-1)+' · UTC':'Possible onset date not established';
  const explanation=safeCopy(copy?.summary)||(ordinary?'A routine retest is possible. A large decline is not confirmed.':state==='NORMAL'?'The current signal does not establish a material pullback.':'The evidence does not establish a confirmed decline.');
  const edge=!!sell.state&&!['UNAVAILABLE','UNKNOWN','INACTIVE','NONE'].includes(sell.state);
  const rec=recommendation(valid?compass.action_now:'WAIT');
  return '<details id="pullbackWatch" class="premium-pullback" data-contract="CN_PULLBACK_WATCH_v1"><summary><div><span>RISK WATCH · DIP / PULLBACK</span><h3>'+esc(title)+'</h3><p class="pullback-window">'+esc(timing)+'</p><p>'+esc(explanation)+'</p></div><div class="pullback-summary-state"><strong>'+esc(status)+'</strong><small>EVIDENCE QUALITY · '+esc(publicState(p.confidence_quality||'UNAVAILABLE'))+'</small><b>'+esc(edge?'SELL / TRIM · '+publicState(sell.state):'Sell / rebuy edge: NOT ESTABLISHED')+'</b><span>Investor details ↓</span></div></summary><div class="pullback-body">'
    +'<div class="pullback-facts"><article><span>ACTION NOW · COMPASS</span><strong>'+esc(rec.action)+'</strong><p>'+esc(rec.copy)+'</p></article><article><span>DEPTH + DURATION</span><strong>Not quantified</strong><p>Dates describe possible onset, not the length or size of a decline.</p></article><article><span>SELL / TRIM</span><strong>'+esc(publicState(sell.state||'UNAVAILABLE'))+'</strong><p>'+esc(edge?'A separate verified assessment is available in the current Compass.':'This watch does not establish a reason to sell and buy back lower.')+'</p></article><article><span>RE-ENTRY</span><strong>'+esc(publicState(p.reentry_state||'UNAVAILABLE'))+'</strong><p>'+esc(publicCompassText(p.reentry_message||'No verified re-entry assessment available.'))+'</p></article></div>'
    +'<div class="pullback-impact"><span>BTC / ETH / ALTCOINS</span><p>'+esc(ordinary?'A routine dip does not imply a major BTC or ETH decline. Small caps and memes still require their own risk and liquidity confirmation.':'The current classification and segment permissions govern risk. A price-range miss alone does not establish distribution or a sell signal.')+'</p></div>'
    +'<div class="pullback-evidence"><span>WATCH FOR</span><p>'+esc(safeCopy(copy?.watch_for)||'A fresh verified risk update before changing the current action.')+'</p><span>WHAT WOULD WEAKEN IT</span><p>'+esc(safeCopy(copy?.weakens_if)||'The warning must be downgraded by the next verified protection assessment.')+'</p></div>'
    +'<p class="pullback-note">Evidence quality is qualitative, not a probability. Possible onset dates can pass without confirmation. Risk warnings and trading permissions remain separate.</p></div></details>';
}
function renderPremium(snapshot, compass) {
  const root = document.getElementById('productNow');
  if (!root) return false;
  const expanded = [...root.querySelectorAll('#premiumMarketCompass details[open][id]')].map(d=>d.id);
  const scale = officialScale(compass);
  const rec = recommendation(compass?.action_now || snapshot?.live_observation?.current_action?.stance);
  const meta = decisionMeta(compass);
  const dataOk = compass?.data_status === 'OK';
  const section = document.createElement('section');
  section.id = 'premiumMarketCompass';
  section.className = 'premium-market-compass';
  section.innerHTML =
    '<div class="premium-overview">'
    + '<div class="premium-overview-copy"><span class="premium-kicker">CYCLE NAVIGATOR · CONCLUSION</span><h2>' + esc(dataOk ? 'One market. Three decision windows.' : 'Fresh market evidence is still loading.') + '</h2><p>' + esc(cnConclusion(snapshot)) + '</p><div class="premium-hero-meta"><a href="#liveDecisionDetail" data-live-detail><span>NEAR-TERM PRESSURE · 0–12H</span><strong>' + esc(meta.live) + '</strong>' + (meta.live.includes('MIXED') ? '<p class="mixed-explanation">Conflicting signals · no clear near-term direction.</p>' : meta.live==='NO NEW READING' ? '<p class="mixed-explanation">Current action unchanged · awaiting a fresh near-term reading.</p>' : '') + '<small>' + esc(meta.liveEta) + ' · not the weekly outlook</small></a><a href="#liveDecisionDetail" data-live-detail><span>WEEKLY OUTLOOK · 5–7D</span><strong>' + esc(meta.weekly) + '</strong>' + (meta.weekly.includes('MIXED') ? '<p class="mixed-explanation">Mixed weekly evidence · no clear directional edge.</p>' : '') + '<small>' + esc(meta.weeklyEta) + ' · current weekly view</small></a></div></div>'
    + '<aside><span>CURRENT ACTION</span><strong>' + esc(rec.action) + '</strong><div class="premium-action-window"><span>APPLIES NOW</span><b>NEXT REVIEW · ' + esc(recommendationWindow(compass)) + '</b><small>This is the reassessment window, not a promise that the action changes.</small></div><p>' + esc(rec.copy) + '</p>' + hourlyMonitor(snapshot) + '<small>Current action · near-term pressure and weekly outlook remain separate signals.</small></aside>'
    + '</div>'
    + decisionDetail(compass, rec, meta)
    + pullbackCard(compass)
    + '<div class="premium-compass-head"><div><span class="premium-kicker">MARKET COMPASS</span><h2>Directional pressure by horizon.</h2></div><p>Each Bull/Bear balance is an official evidence reading. Tap a horizon to see the public inputs, current drivers and method behind the call.</p></div>'
    + '<div class="premium-horizon-grid">' + HORIZONS.map((h) => horizonCard(snapshot, compass, scale, h)).join('') + '</div>'
    + riskCurve(compass)
    + '<div class="premium-footline"><span>DATA STATUS · <b>' + esc(publicDataStatus(compass?.data_status || 'UNAVAILABLE')) + '</b></span><span>RISK ROTATION · ' + esc(capSummary(compass)) + '</span><span>Evidence balance · not probability</span></div>';

  expanded.forEach(id=>{const d=section.querySelector('#'+id);if(d)d.open=true;});
  root.querySelector('#premiumMarketCompass')?.remove();
  root.classList.add('premium-compass-installed');
  const anchor = root.querySelector('.action-hero,.fail-card');
  if (anchor) anchor.after(section);
  else root.prepend(section);
  section.querySelectorAll('[data-live-detail]').forEach((link) => link.addEventListener('click', (event) => {
    event.preventDefault();
    const detail = section.querySelector('#liveDecisionDetail');
    if (!detail) return;
    detail.open = true;
    requestAnimationFrame(() => detail.scrollIntoView({ behavior: 'smooth', block: 'start' }));
  }));
  return true;
}

let latestSnapshot = null;
let latestCompass = null;
let observer = null;

function install() {
  if (!latestSnapshot || !latestCompass) return;
  const root = document.getElementById('productNow');
  if (!root) return;
  if (!observer) {
    observer = new MutationObserver(() => {
      if (!document.getElementById('premiumMarketCompass')) queueMicrotask(() => renderPremium(latestSnapshot, latestCompass));
    });
    observer.observe(root, { childList: true, subtree: false });
  }
  renderPremium(latestSnapshot, latestCompass);
}

async function load() {
  try {
    const stamp = Date.now();
    const [s, c] = await Promise.all([
      fetch(SNAPSHOT_URL + '?premium=' + stamp, { cache: 'no-store' }),
      fetch(COMPASS_URL + '?premium=' + stamp, { cache: 'no-store' })
    ]);
    if (!s.ok || !c.ok) throw new Error('Premium Compass source unavailable');
    latestSnapshot = await s.json();
    latestCompass = await c.json();
    install();
  } catch (error) {
    console.warn('Premium Market Compass unavailable', error);
  }
}

function boot() {
  load();
  setInterval(load, 5 * 60 * 1000);
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, { once: true });
else boot();
})();
