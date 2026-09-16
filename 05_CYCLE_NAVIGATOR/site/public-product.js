(() => {
  'use strict';

  const esc = value => String(value ?? '').replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#039;');
  const short = (value, limit = 220) => { const text = String(value ?? '').trim(); return text.length > limit ? `${text.slice(0, limit - 1).trim()}…` : text; };
  const cleanPhase = value => String(value || '').replace(/^\d+\.\s*/, '').replace(/\s[—–-]\s(ACTIVE WATCH|ACTIVE|UNCONFIRMED|INACTIVE|PAUSED).*$/i, '').trim();
  const statusFrom = value => { const text = String(value || '').toUpperCase(); if (text.includes('PAUSED') || text.includes('INACTIVE')) return 'pause'; if (text.includes('ACTIVE WATCH') || text.includes('RELATIVE RESILIENCE') || text.includes('ON WATCH')) return 'watch'; if (text.includes('MAJOR LIQUIDITY ANCHOR') || text.includes('NO CONFIRMED MARKET BREAKDOWN')) return 'hold'; if (text.includes('UNCONFIRMED') || text.includes('SELECTIVE PARTICIPATION')) return 'wait'; if (text.includes('ACTIVE')) return 'active'; return 'unavailable'; };
  const statusLabel = value => ({ active: 'ACTIVE', hold: 'HOLD', watch: 'WATCH', wait: 'WAIT', pause: 'PAUSE', unavailable: 'UNAVAILABLE' }[statusFrom(value)] || 'UNAVAILABLE');
  const postureCopy = value => ({ active: 'Current rotation is active.', hold: 'Hold the current posture. Do not broaden risk from this segment alone.', watch: 'Watch and prepare. Confirmation is still required.', wait: 'Wait. Rotation is not confirmed.', pause: 'Pause new risk here until the framework reopens this stage.', unavailable: 'No public posture is available.' }[statusFrom(value)] || 'No public posture is available.');
  const eraLabel = era => ({ PUBLISHED_MANUAL_AUDIT: 'Published legacy', BRIDGE_PUBLISHED_SCORE: 'Bridge', FROZEN_PROSPECTIVE: 'Frozen prospective', AUTOMATED_CANONICAL: 'Automated canonical' }[era] || 'Published record');
  const stanceTitle = stance => ({ HOLD: 'HOLD / WAIT', WAIT: 'WAIT', PREPARE: 'PREPARE', SELECTIVE: 'SELECTIVE', 'PROTECT CAPITAL': 'PROTECT CAPITAL', 'BROADER DEPLOYMENT': 'BROADER DEPLOYMENT' }[String(stance || '').toUpperCase()] || 'WAIT');
  const stanceCopy = stance => ({ HOLD: 'Hold the current posture. Do not broaden risk until the next confirmation gate is met.', WAIT: 'No new broad deployment is confirmed. Wait for the next valid gate.', PREPARE: 'Prepare for a possible transition, but do not treat it as confirmed yet.', SELECTIVE: 'Keep risk selective. Broad deployment is not confirmed.', 'PROTECT CAPITAL': 'Risk conditions are defensive. Avoid broadening exposure until evidence improves.', 'BROADER DEPLOYMENT': 'Broader participation is confirmed by the current public framework state.' }[String(stance || '').toUpperCase()] || 'No new action is confirmed.');
  const publicGate = raw => {
    const text = String(raw || '').trim();
    if (!text) return 'Await the next published confirmation gate.';
    if (/ETHBTC_STRENGTH.*BREADTH.*HEALTHY/i.test(text)) return 'ETH/BTC strength persists, participation broadens, and source health remains healthy.';
    if (/BREADTH_LT|ETHBTC_WEAKENS|NATIVE_HEALTH_DEGRADES/i.test(text)) return 'Participation weakens, ETH/BTC rolls over, or source health deteriorates.';
    if (/ONLY_EXISTING_ENTRY_SIGNAL|REGISTERED_CANONICAL_CONFIRMATION/i.test(text)) return 'Only a canonical entry signal or registered confirmation may reopen top-up risk.';
    return text.replaceAll('_', ' ').replace(/\bGTE\b/gi, 'at least').replace(/\bLT\b/gi, 'below').replace(/\s+/g, ' ').trim();
  };
  const priceText = prices => prices ? `BTC $${Math.round(prices.btc).toLocaleString()} · ETH $${Math.round(prices.eth).toLocaleString()} · ETH/BTC ${prices.ratio.toFixed(5)}` : 'Live price context temporarily unavailable';

  let currentSnapshot = null;
  let updateTimer = null;

  function ensureShell() {
    const main = document.querySelector('main');
    if (!main) return null;
    let root = document.getElementById('publicProduct');
    if (!root) {
      root = document.createElement('section');
      root.id = 'publicProduct';
      root.className = 'public-product';
      root.innerHTML = '<nav class="product-tabs" role="tablist" aria-label="Cycle Navigator"><button class="active" data-tab="now" role="tab" aria-selected="true">NOW</button><button data-tab="path" role="tab" aria-selected="false">PATH</button><button data-tab="score" role="tab" aria-selected="false">SCORE</button><button data-tab="how" role="tab" aria-selected="false">HOW</button></nav><div id="productNow" class="product-view active" role="tabpanel"></div><div id="productPath" class="product-view" role="tabpanel"></div><div id="productScore" class="product-view" role="tabpanel"></div><div id="productHow" class="product-view" role="tabpanel"></div>';
      main.prepend(root);
      root.querySelectorAll('[data-tab]').forEach(button => button.addEventListener('click', () => {
        const target = button.dataset.tab;
        root.querySelectorAll('[data-tab]').forEach(item => { const selected = item === button; item.classList.toggle('active', selected); item.setAttribute('aria-selected', String(selected)); });
        root.querySelectorAll('.product-view').forEach(view => view.classList.toggle('active', view.id === `product${target[0].toUpperCase()}${target.slice(1)}`));
        window.scrollTo({ top: Math.max(0, root.offsetTop - 10), behavior: 'smooth' });
      }));
    }
    main.querySelectorAll(':scope > section:not(#publicProduct)').forEach(section => section.classList.add('legacy-detail'));
    document.querySelector('.journey-nav-wrap')?.classList.add('legacy-detail');
    return root;
  }

  async function fetchJson(url) {
    const response = await fetch(`${url}${url.includes('?') ? '&' : '?'}v=${Date.now()}`, { cache: 'no-store' });
    if (!response.ok) throw new Error(`${url} HTTP ${response.status}`);
    return response.json();
  }

  async function fetchPrices() {
    try {
      const response = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd', { cache: 'no-store' });
      if (!response.ok) throw new Error(response.status);
      const data = await response.json();
      const btc = Number(data.bitcoin?.usd), eth = Number(data.ethereum?.usd);
      if (!Number.isFinite(btc) || !Number.isFinite(eth)) throw new Error('invalid market context');
      return { btc, eth, ratio: eth / btc };
    } catch {
      return null;
    }
  }

  function parseTime(value) {
    if (!value) return null;
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? null : date;
  }

  function nextHourlySourceCycle(now = new Date()) {
    const next = new Date(now);
    next.setUTCSeconds(0, 0);
    if (next.getUTCMinutes() < 5) next.setUTCMinutes(5);
    else { next.setUTCHours(next.getUTCHours() + 1); next.setUTCMinutes(5); }
    return next;
  }

  function duration(ms) {
    if (!Number.isFinite(ms)) return '—';
    const total = Math.max(0, Math.ceil(ms / 60000));
    const hours = Math.floor(total / 60), minutes = total % 60;
    return hours ? `${hours}h ${minutes}m` : `${minutes}m`;
  }

  function formatUpdated(date) {
    if (!date) return 'Timestamp unavailable';
    return date.toLocaleString([], { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
  }

  function updateFreshness() {
    const host = document.getElementById('productFreshness');
    if (!host || !currentSnapshot) return;
    const action = currentSnapshot.live_observation?.current_action || {};
    const pkg = currentSnapshot.package || {};
    const updated = parseTime(action.generated_at) || (Number(pkg.generated_unix) > 0 ? new Date(Number(pkg.generated_unix) * 1000) : null);
    const now = new Date();
    const ageMs = updated ? now - updated : NaN;
    const stale = Number.isFinite(ageMs) && ageMs > 90 * 60 * 1000;
    const limited = /DATA_DEGRADED/i.test(String(action.current || ''));
    const next = nextHourlySourceCycle(now);
    host.className = `freshness-strip${stale ? ' stale' : ''}${limited ? ' limited' : ''}`;
    host.innerHTML = `<div><span>${stale ? 'LAST VALID HANDLEKOMPAS' : limited ? 'HANDLEKOMPAS · DATA LIMITED' : 'HANDLEKOMPAS UPDATED'}</span><strong>${esc(formatUpdated(updated))}</strong><small>${updated ? `${esc(duration(ageMs))} ago` : 'No LIVE timestamp published'}</small></div><div><span>NEXT HOURLY DATA CYCLE</span><strong>${esc(duration(next - now))}</strong><small>Owner source runs at :05 UTC · publishing may trail by a few minutes</small></div><div><span>WEEKLY AUTHORITY</span><strong>Frozen CN #${esc(pkg.issue_number ?? '—')}</strong><small>LIVE may update posture, never rewrite the weekly forecast</small></div>`;
  }

  function phaseSummary(stages) {
    const active = stages.filter(item => statusFrom(item.phase) === 'active').map(item => cleanPhase(item.phase));
    const watch = stages.filter(item => statusFrom(item.phase) === 'watch').map(item => cleanPhase(item.phase));
    const waiting = stages.filter(item => statusFrom(item.phase) === 'wait').map(item => cleanPhase(item.phase));
    const pieces = [];
    if (active[0]) pieces.push(`${active[0]} active`);
    if (watch[0]) pieces.push(`${watch[0]} on watch`);
    if (waiting[0]) pieces.push(`${waiting[0]} not confirmed`);
    return pieces.join(' · ') || 'Cycle phase awaiting confirmation.';
  }

  function rotationCards(rotation, compact = false) {
    const rows = Array.isArray(rotation) && rotation.length ? rotation : [
      { segment: 'Bitcoin', status: 'UNAVAILABLE' }, { segment: 'Ethereum', status: 'UNAVAILABLE' }, { segment: 'Large caps', status: 'UNAVAILABLE' }, { segment: 'Mid caps', status: 'UNAVAILABLE' }, { segment: 'Small caps', status: 'UNAVAILABLE' }, { segment: 'Microcaps', status: 'UNAVAILABLE' }
    ];
    return `<div class="rotation-compass${compact ? ' compact' : ''}">${rows.map(item => {
      const state = statusFrom(item.status), label = statusLabel(item.status);
      return `<article class="rotation-card state-${state}"><div class="rotation-top"><strong>${esc(item.segment || 'Segment')}</strong><span>${esc(label)}</span></div><p>${esc(postureCopy(item.status))}</p><small>${esc(String(item.status || 'Not published').replaceAll('_', ' '))}</small></article>`;
    }).join('')}</div>`;
  }

  function renderNow(data, prices) {
    const pkg = data.package || {}, live = data.live_observation || {}, action = live.current_action || {};
    const stages = Array.isArray(pkg.altseason_countdown) ? pkg.altseason_countdown : [];
    const stance = String(action.stance || 'WAIT').toUpperCase();
    const gate = publicGate(action.confirmation);
    const invalidation = publicGate(action.invalidation);
    const dataLimited = /DATA_DEGRADED/i.test(String(action.current || ''));
    const nextDays = action.next_days ? short(action.next_days, 180) : dataLimited ? 'Stay HOLD / WAIT until source health and the confirmation gate recover. Recheck on the next hourly cycle.' : `Stay ${stanceTitle(stance)} and reassess on the next hourly Handlekompas cycle; broaden risk only after the confirmation gate.`;
    const whyNow = phaseSummary(stages);
    const liveAvailable = Boolean(action.generated_at);
    const currentText = !liveAvailable ? 'LIVE Handlekompas is unavailable. The public product is failing closed and will not infer a new action from price alone.' : dataLimited ? 'Data quality is currently limited. HOLD / WAIT remains the bounded posture and no broader risk is promoted until healthy evidence returns.' : stanceCopy(stance);
    document.getElementById('productNow').innerHTML = `<section class="action-hero">
        ${dataLimited ? '<div class="data-limited-badge">LIVE DATA LIMITED</div>' : ''}
        <div class="action-label">HANDLEKOMPAS · WHAT SHOULD I DO NOW?</div>
        <div class="action-word">${esc(liveAvailable ? stanceTitle(stance) : 'WAIT')}</div>
        <p>${esc(currentText)}</p>
        <div class="phase-line">${esc(whyNow)}</div>
        <div class="action-grid">
          <article><span>NEXT 1–3 DAYS</span><p>${esc(nextDays)}</p></article>
          <article><span>CONFIRMATION</span><p>${esc(gate)}</p></article>
          <article><span>RISK / INVALIDATION</span><p>${esc(invalidation)}</p></article>
        </div>
      </section>
      <div id="productFreshness" class="freshness-strip"></div>
      <section class="now-section"><div class="section-title"><div><small>RISK LADDER · HERE AND NOW</small><h2>Bitcoin to microcaps</h2></div><p>The weekly rotation map translated into a simple public posture. LIVE Handlekompas controls the top-level stance.</p></div>${rotationCards(pkg.rotation_ladder, true)}</section>
      <section class="context-row"><article><span>MARKET CONTEXT</span><strong id="productPrices">${esc(priceText(prices))}</strong><small>Context only. Price cannot rewrite the frozen call.</small></article><article><span>THIS WEEK · FROZEN</span><strong>${esc(short(pkg.base_case_this_week || 'Not published for this issue.', 190))}</strong><small>Master Monday / Cycle Navigator authority</small></article></section>
      <section class="why-now"><div><small>WHY NOW</small><h2>${esc(whyNow)}</h2></div><p>${esc(short(pkg.market_state || 'Official weekly market state unavailable.', 260))}</p></section>`;
    updateFreshness();
  }

  function renderPath(data) {
    const pkg = data.package || {};
    const stages = Array.isArray(pkg.altseason_countdown) ? pkg.altseason_countdown : [];
    document.getElementById('productPath').innerHTML = `<header class="product-head"><small>CONDITIONAL CYCLE MAP</small><h2>Where capital can rotate next.</h2><p>This is a sequence of gates, not a promise of altseason. ETA is shown only where the frozen package publishes a window.</p></header>
      <section class="path-list">${stages.length ? stages.map((item, index) => `<article class="path-card state-${statusFrom(item.phase)}"><span class="path-index">${index + 1}</span><div><div class="path-name"><strong>${esc(cleanPhase(item.phase))}</strong><span>${esc(statusLabel(item.phase))}</span></div><p>${esc(item.window || 'No verified ETA published')}</p><small>${index === 0 ? 'Current gate.' : index === 1 ? 'Needs persistent ETH relative strength and supporting participation.' : 'Needs broader participation and confirmation through the preceding stage.'}</small></div></article>`).join('') : '<article class="empty-card">No public path is published for this issue.</article>'}</section>
      <section class="now-section"><div class="section-title"><div><small>ROTATION LADDER</small><h2>Large caps → microcaps</h2></div><p>Current weekly confirmation state by market-cap segment.</p></div>${rotationCards(pkg.rotation_ladder)}</section>
      <section class="horizon-grid"><article><span>2–3 WEEKS</span><p>${esc(short(pkg.base_case_2_3_weeks || 'No supported 2–3 week view is published.', 260))}</p></article><article><span>4–8 WEEKS</span><p>${esc(short(pkg.base_case_4_8_weeks || pkg.compass_4_8_weeks || 'No supported 4–8 week view is published.', 260))}</p></article></section>`;
  }

  function renderScore(history) {
    const root = document.getElementById('productScore');
    if (!root) return;
    if (!history?.records?.length) {
      root.innerHTML = '<header class="product-head"><small>PUBLIC ACCOUNTABILITY</small><h2>Score history unavailable.</h2><p>The site will not reconstruct missing scores from outcomes.</p></header>';
      return;
    }
    const coverage = history.coverage || {}, records = history.records;
    const bars = records.map(record => `<div class="score-bar-wrap" title="CN #${record.cn}${record.overall == null ? ' · overall unavailable' : ` · ${record.overall}%`}"><span>${record.overall == null ? '—' : `${record.overall}%`}</span><div class="score-bar ${record.overall == null ? 'missing' : ''}" style="--value:${record.overall == null ? 0 : Math.max(0, Math.min(100, Number(record.overall)))}"></div><small>${record.cn}</small></div>`).join('');
    const rows = [...records].reverse().map(record => `<article class="score-row"><div><strong>CN #${record.cn}</strong><span>${esc(eraLabel(record.era))}</span></div><div class="score-main"><b>${record.overall == null ? '—' : `${record.overall}%`}</b><small>published overall</small></div><p><span>Range</span>${esc(record.range_display || '—')}</p><p><span>Intraday</span>${esc(record.intraday_display || '—')}</p><p><span>Structure</span>${esc(record.structure_display || '—')}</p></article>`).join('');
    root.innerHTML = `<header class="product-head"><small>PUBLIC ACCOUNTABILITY</small><h2>Scoreboard</h2><p>${esc(coverage.completed_issues ?? records.length)} completed issues are preserved in their original scoring semantics. Open CN #${esc(coverage.latest_open_issue ?? '—')} is excluded until its outcome is scoreable.</p></header>
      <section class="score-policy"><article><strong>${esc(coverage.completed_issues ?? records.length)}</strong><span>completed CN issues</span></article><article><strong>LOCKED</strong><span>no retroactive rescoring</span></article><article><strong>NO</strong><span>cross-era synthetic average</span></article></section>
      <section class="score-chart"><div class="score-chart-title"><strong>Published overall score by issue</strong><small>— means that an overall score was not published under that era's method.</small></div><div class="score-bars">${bars}</div></section>
      <section class="score-history"><div class="section-title"><div><small>FULL RECORD</small><h2>CN #1 → #${records.at(-1)?.cn ?? records.length}</h2></div><p>Legacy and automated records are both first-class publication history.</p></div>${rows}</section>
      <p class="score-note">${esc(history.provenance_note || 'Missing components remain unavailable and are never reconstructed from outcomes.')}</p>`;
  }

  function renderHow(data) {
    const pkg = data.package || {};
    const steps = [
      ['1', 'DATA', 'Autonomous market data is materialized and checked before it can feed the public decision layer.'],
      ['2', 'SPECIALIST ANALYSIS', 'Specialist processes evaluate cycle, relative strength, breadth, rotation, risk and supporting evidence.'],
      ['3', 'EVIDENCE & CHALLENGE', 'Conflicts, missing inputs and weak evidence are challenged before a state can advance.'],
      ['4', 'MASTER MONDAY', 'The weekly package becomes the reference point for the new week.'],
      ['5', 'FROZEN CYCLE NAVIGATOR', 'The forecast is frozen before outcomes are known. It cannot be silently rewritten later.'],
      ['6', 'LIVE HANDLEKOMPAS', 'Hourly evidence may update the current public posture between Mondays, but it cannot change the frozen weekly forecast or official historical score.'],
      ['7', 'SCORE & LEARNING', 'After outcomes mature, the published call is scored. Missing evidence stays missing and learning feeds future issues, not the past.']
    ];
    document.getElementById('productHow').innerHTML = `<header class="product-head"><small>HOW IT WORKS</small><h2>Forecast first. Outcome later.</h2><p>Enough transparency to understand the machine without publishing proprietary thresholds, weights, prompts or the complete signal recipe.</p></header>
      <section class="method-flow">${steps.map(step => `<article><span>${step[0]}</span><div><strong>${step[1]}</strong><p>${step[2]}</p></div></article>`).join('')}</section>
      <section class="trust-grid"><article><span>WEEKLY</span><h3>Frozen authority</h3><p>Cycle Navigator #${esc(pkg.issue_number ?? '—')} is the current weekly reference. LIVE context never rewrites it.</p></article><article><span>LIVE</span><h3>Hourly posture</h3><p>Handlekompas follows the autonomous hourly source chain. If LIVE evidence is unavailable or stale, the site shows that instead of inventing a call.</p></article><article><span>HISTORY</span><h3>Immutable public record</h3><p>Previously published scores stay exactly as published under the method used at the time. No hindsight cleanup.</p></article><article><span>FAIL CLOSED</span><h3>Unknown means unknown</h3><p>Missing ranges, ETA or score components are shown as unavailable, never filled with guesses or LIVE prices.</p></article></section>
      <section class="method-foot"><strong>Public architecture</strong><p>DATA → SPECIALIST ANALYSIS → EVIDENCE & CHALLENGE → MASTER MONDAY → FROZEN CYCLE NAVIGATOR → LIVE HANDLEKOMPAS → SCORE & LEARNING</p></section>`;
  }

  async function renderAll() {
    ensureShell();
    try {
      const [snapshot, history, prices] = await Promise.all([fetchJson('./data/latest.json'), fetchJson('./history-scoreboard.json'), fetchPrices()]);
      currentSnapshot = snapshot;
      renderNow(snapshot, prices);
      renderPath(snapshot);
      renderScore(history);
      renderHow(snapshot);
      if (updateTimer) clearInterval(updateTimer);
      updateTimer = setInterval(updateFreshness, 30 * 1000);
    } catch (error) {
      console.warn('Cycle Navigator public product unavailable', error);
      const now = document.getElementById('productNow');
      if (now) now.innerHTML = '<section class="fail-card"><small>PUBLIC FEED UNAVAILABLE</small><h1>WAIT</h1><p>The product is failing closed. No action is inferred from LIVE price alone.</p></section>';
    }
  }

  renderAll();
  setInterval(async () => {
    const prices = await fetchPrices();
    const node = document.getElementById('productPrices');
    if (node) node.textContent = priceText(prices);
  }, 5 * 60 * 1000);
  setInterval(renderAll, 5 * 60 * 1000);
})();
