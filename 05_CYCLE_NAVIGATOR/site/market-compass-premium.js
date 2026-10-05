(() => {
'use strict';

window.CN_PREMIUM_COMPASS_OWNER = true;

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
    'PROTECT CAPITAL': 'Keep risk contained and protect capital until the official Compass confirms that conditions have repaired.',
    'HOLD': 'Keep current positioning. Do not broaden risk from this reading alone.',
    'WAIT': 'Stay patient. Do not infer a new risk-on call until the official Compass publishes enough evidence.'
  };
  return { action, copy: map[action] || map.WAIT };
}

function cnConclusion(snapshot) {
  const pkg = snapshot?.package || {};
  return clean(pkg.base_case_this_week)
    || clean(pkg.market_state)
    || 'The current weekly Cycle Navigator conclusion is not available.';
}

function twoThreeWeekContext(snapshot) {
  const pkg = snapshot?.package || {};
  return clean(pkg.base_case_2_3_weeks) || 'No separate 2–3 week Cycle Navigator context is published.';
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
  if (!rows.length) return 'Capital-transmission evidence is unavailable.';
  return rows.slice(0, 6).map((row) => words(row.segment) + ' ' + words(row.status)).join(' · ');
}

function riskSummary(compass) {
  const protection = compass?.protection_tracker || {};
  const pullback = words(protection.pullback_risk_state || 'UNAVAILABLE');
  return 'Pullback ' + pullback;
}

function decisionMeta(compass) {
  const market = compass?.market_now || {};
  const near = compass?.horizons?.NEXT_12H || {};
  const weekly = compass?.horizons?.NEXT_5_7D || {};
  const protection = compass?.protection_tracker || {};
  return {
    live: words(market.directional_state || market.regime || near.label || near.expected_direction || 'UNAVAILABLE'),
    liveEta: clean(near.eta) || clean(compass?.next_meaningful_change_eta) || 'No fixed ETA',
    weekly: words(weekly.label || weekly.expected_direction || 'UNAVAILABLE'),
    weeklyEta: clean(weekly.eta) || '5–7d',
    risk: riskSummary(compass),
    riskEta: clean(protection.eta_window) || 'No supported risk window',
    distribution: words(protection.distribution_risk || 'UNKNOWN')
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
  const invalidation = clean(protection.invalidation) || 'No governed invalidation text is currently published.';
  const issued = clean(compass?.issued_at_utc);
  const issuedLabel = issued ? new Date(issued).toLocaleString('en-GB',{timeZone:'Europe/Copenhagen',day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit',hour12:false}).replace(',','') + ' CPH' : 'timestamp unavailable';
  const investor = rec.action === 'HOLD'
    ? 'Keep existing positioning. The bearish live-pressure reading is tactical, not the 5–7 day base case. Do not broaden high-beta exposure from this signal alone.'
    : rec.copy;
  const swing = 'Treat ' + meta.live + ' over ' + meta.liveEta + ' as short-horizon pressure, while the 5–7 day outlook remains ' + meta.weekly + '. ' + meta.risk + ' means a retest deserves attention, but it is not a confirmed sell, short or distribution signal.';
  return '<details id="liveDecisionDetail" class="premium-decision-detail">'
    + '<summary><span>LIVE DECISION DETAIL</span><b>Investor + swing trader context</b></summary>'
    + '<div class="premium-decision-body">'
    + '<div class="premium-decision-strip"><div><span>LIVE PRESSURE</span><strong>'+esc(meta.live)+'</strong><small>'+esc(meta.liveEta)+'</small></div><div><span>WEEKLY OUTLOOK</span><strong>'+esc(meta.weekly)+'</strong><small>'+esc(meta.weeklyEta)+'</small></div><div><span>RISK WINDOW</span><strong>'+esc(meta.risk)+'</strong><small>'+esc(meta.riskEta)+'</small></div></div>'
    + '<div class="premium-audience-grid"><article><span>FOR AN INVESTOR</span><p>'+esc(investor)+'</p></article><article><span>FOR A SWING TRADER</span><p>'+esc(swing)+'</p></article></div>'
    + '<div class="premium-risk-detail"><span>WHAT TO WATCH</span><strong>'+esc(meta.risk)+' · Distribution '+esc(meta.distribution)+'</strong><p><b>When:</b> '+esc(meta.riskEta)+'</p><p><b>Risk weakens if:</b> '+esc(invalidation)+'</p><small>Protection context is not execution authority. Official Compass issued '+esc(issuedLabel)+'.</small></div>'
    + '</div></details>';
}

function soWhat(row, lane) {
  if (!row?.ok) return 'No governed edge — wait for a verified read.';
  const action = actionFromLane(lane);
  const tone = statusTone(row);
  if (action === 'PREPARE' && tone === 'bull') return 'Prepare selectively — confirmation still comes before broad risk.';
  if (action === 'PREPARE') return 'Prepare, but keep deployment conditional on confirmation.';
  if (action === 'HOLD') return 'Stay positioned — do not chase high-beta from this horizon alone.';
  if (tone === 'bull') return 'Bullish pressure is visible, but action authority still says wait.';
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
  const resolved = ordered.map((segment) => bySegment.get(segment) || { segment, status: 'UNAVAILABLE', action: 'UNAVAILABLE', reason: 'No governed public reading is available.' });
  const meme = resolved.find((row) => String(row.segment).toUpperCase() === 'MEMES') || {};
  const rail = resolved.map((row, index) => {
    const label = words(row.segment).replace('LARGE CAPS','LARGE').replace('MID CAPS','MID').replace('SMALL CAPS','SMALL').replace('MICROCAPS','MICRO');
    return '<div class="premium-rung tone-' + esc(ladderTone(row.status)) + '"><i>' + esc(index + 1) + '</i><span>' + esc(label) + '</span><strong>' + esc(words(row.status || row.action || 'UNAVAILABLE')) + '</strong></div>';
  }).join('');
  return '<section class="premium-risk-curve">'
    + '<header><div><span class="premium-kicker">RISK CURVE · NOW</span><h3>Bitcoin → memes</h3></div><p>How far out on the risk curve the governed evidence currently supports going.</p></header>'
    + '<div class="premium-rung-grid">' + rail + '</div>'
    + '<div class="premium-meme-focus"><span>MEME RISK</span><strong>' + esc(words(meme.status || meme.action || 'UNAVAILABLE')) + '</strong><p>' + esc(clean(meme.reason) || 'No governed meme-specific reading is currently published.') + '</p><small>ETA · ' + esc(clean(meme.eta) || 'No fixed ETA') + '</small></div>'
    + '</section>';
}

function evidenceDrivers(compass) {
  const rows = Array.isArray(compass?.protection_tracker?.decisive_public_drivers)
    ? compass.protection_tracker.decisive_public_drivers.filter(Boolean).slice(0, 4)
    : [];
  return rows;
}

function scoreFormula(row) {
  if (!row.ok) {
    return '<div class="premium-formula pending"><span>OFFICIAL BALANCE</span><strong>AWAITING GOVERNED READ</strong><small>No Bull/Bear number is reconstructed by the website.</small></div>';
  }
  return '<div class="premium-formula"><span>OFFICIAL BALANCE</span><strong>BULL ' + esc(row.bull) + ' + BEAR ' + esc(row.bear) + ' = 10</strong><small>Evidence balance, not probability. Published upstream by Official Compass.</small></div>';
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
    + '<div class="premium-call"><div><span>DIRECTION</span><strong>' + esc(words(lane?.expected_direction || row?.bias || 'UNAVAILABLE')) + '</strong></div><div><span>ACTION</span><strong>' + esc(actionFromLane(lane)) + '</strong></div><div><span>WINDOW</span><strong>' + esc(lane?.eta || horizon.label) + '</strong></div></div>'
    + '<div class="premium-families">'
    + evidenceFamily('PRICE & STRUCTURE', 'BTC and ETH price behaviour, relative trend and the horizon-specific market path.')
    + evidenceFamily('PARTICIPATION & ROTATION', 'Market participation, Ethereum vs Bitcoin, Bitcoin dominance and capital transmission across size tiers.')
    + evidenceFamily('LIQUIDITY & POSITIONING', 'Settled ETF flows, stablecoin liquidity, open interest, funding and leverage context when eligible.')
    + evidenceFamily('SENTIMENT & CYCLE', 'Market sentiment, risk conditions and the frozen Cycle Navigator context for the relevant horizon.')
    + '</div>'
    + driverBlock
    + context23
    + '<p class="premium-method-note"><b>Important:</b> the website displays the governed score exactly as published. It does not recalculate or reverse-engineer private thresholds, weights, prompts or fallback routes. Contradictory or stale evidence reduces confidence or leaves the horizon unavailable.</p>'
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
  const summary = clean(row.summary) || clean(lane.expected_path) || 'No governed reading is published for this horizon.';
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

function renderPremium(snapshot, compass) {
  const root = document.getElementById('productNow');
  if (!root) return false;
  const scale = officialScale(compass);
  const rec = recommendation(compass?.action_now || snapshot?.live_observation?.current_action?.stance);
  const meta = decisionMeta(compass);
  const dataOk = compass?.data_status === 'OK';
  const section = document.createElement('section');
  section.id = 'premiumMarketCompass';
  section.className = 'premium-market-compass';
  section.innerHTML =
    '<div class="premium-overview">'
    + '<div class="premium-overview-copy"><span class="premium-kicker">CYCLE NAVIGATOR · CONCLUSION</span><h2>' + esc(dataOk ? 'One market. Three decision windows.' : 'The framework is waiting for fresh evidence.') + '</h2><p>' + esc(cnConclusion(snapshot)) + '</p><div class="premium-hero-meta"><a href="#liveDecisionDetail" data-live-detail><span>LIVE PRESSURE · 0–12H</span><strong>' + esc(meta.live) + '</strong><small>' + esc(meta.liveEta) + ' · not the weekly outlook</small></a><a href="#liveDecisionDetail" data-live-detail><span>WEEKLY OUTLOOK · 5–7D</span><strong>' + esc(meta.weekly) + '</strong><small>' + esc(meta.weeklyEta) + ' · current W41 view</small></a><a href="#liveDecisionDetail" data-live-detail><span>RISK WATCH</span><strong>' + esc(meta.risk) + '</strong><small>' + esc(meta.riskEta) + ' · Distribution ' + esc(meta.distribution) + '</small></a></div></div>'
    + '<aside><span>RECOMMENDATION</span><strong>' + esc(rec.action) + '</strong><div class="premium-action-window">APPLIES NOW · NEXT GOVERNED REVIEW ' + esc(recommendationWindow(compass)) + '</div><p>' + esc(rec.copy) + '</p><small>Official action posture · live pressure and weekly outlook are separate signals.</small></aside>'
    + '</div>'
    + decisionDetail(compass, rec, meta)
    + '<div class="premium-compass-head"><div><span class="premium-kicker">MARKET COMPASS</span><h2>Directional pressure by horizon.</h2></div><p>Each Bull/Bear balance is an official evidence reading. Tap a horizon to see the public inputs, current drivers and method behind the call.</p></div>'
    + '<div class="premium-horizon-grid">' + HORIZONS.map((h) => horizonCard(snapshot, compass, scale, h)).join('') + '</div>'
    + riskCurve(compass)
    + '<div class="premium-footline"><span>DATA STATUS · <b>' + esc(words(compass?.data_status || 'UNAVAILABLE')) + '</b></span><span>CAPITAL TRANSMISSION · ' + esc(capSummary(compass)) + '</span><span>Evidence balance · not probability</span></div>';

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