(() => {
  'use strict';

  const DATA_URL = './data/latest.json';
  let refreshTimer = null;

  const esc = (value) => String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

  function stateOf(text) {
    const t = String(text || '').toUpperCase();
    if (t.includes('ACTIVE WATCH') || t.includes('UNCONFIRMED')) return 'watch';
    if (t.includes('ACTIVE') && !t.includes('INACTIVE')) return 'active';
    return 'locked';
  }

  function stateLabel(text) {
    const t = String(text || '').toUpperCase();
    if (t.includes('ACTIVE WATCH')) return 'Active watch';
    if (t.includes('ACTIVE') && !t.includes('INACTIVE')) return 'Active';
    if (t.includes('UNCONFIRMED')) return 'Unconfirmed';
    if (t.includes('PAUSED')) return 'Paused';
    if (t.includes('INACTIVE')) return 'Inactive';
    return 'Watching';
  }

  function cleanPhase(text) {
    return String(text || '')
      .replace(/^\d+\.\s*/, '')
      .replace(/\s[—–-]\s(ACTIVE WATCH|ACTIVE|UNCONFIRMED|INACTIVE|PAUSED).*$/i, '')
      .trim();
  }

  function parseWindowDays(windowText) {
    const source = String(windowText || '').toLowerCase().replaceAll('–', '-').replaceAll('—', '-');
    let match = source.match(/(\d+)\s*-\s*(\d+)\s*weeks?/);
    if (match) return { min: Number(match[1]) * 7, max: Number(match[2]) * 7 };
    match = source.match(/(\d+)\s*-\s*(\d+)\s*days?/);
    if (match) return { min: Number(match[1]), max: Number(match[2]) };
    match = source.match(/(?:~|approximately\s*)?(\d+)\s*weeks?/);
    if (match) {
      const days = Number(match[1]) * 7;
      return { min: days, max: days };
    }
    return null;
  }

  function fmtDuration(ms) {
    const minutes = Math.max(0, Math.floor(ms / 60000));
    const days = Math.floor(minutes / 1440);
    const hours = Math.floor((minutes % 1440) / 60);
    const mins = minutes % 60;
    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h ${mins}m`;
    return `${mins}m`;
  }

  function clockFor(baseUnix, windowText) {
    const parsed = parseWindowDays(windowText);
    const base = Number(baseUnix) * 1000;
    if (!parsed || !Number.isFinite(base) || base <= 0) return null;

    const start = base + parsed.min * 86400000;
    const end = base + parsed.max * 86400000;
    const now = Date.now();

    if (now < start) {
      return {
        mode: 'countdown',
        value: fmtDuration(start - now),
        subtitle: 'until earliest working window',
        note: windowText
      };
    }
    if (now <= end) {
      return {
        mode: 'open',
        value: 'WINDOW OPEN',
        subtitle: parsed.max > parsed.min ? `${fmtDuration(end - now)} left in window` : 'working window active',
        note: windowText
      };
    }
    return {
      mode: 'paused',
      value: 'AWAIT NEW CN',
      subtitle: 'working window has matured',
      note: 'No automatic promotion. The next OFFICIAL Cycle Navigator must confirm the phase.'
    };
  }

  function clockCard(label, title, clock, fallback = {}) {
    const mode = clock?.mode || fallback.mode || 'locked';
    const value = clock?.value || fallback.value || 'PAUSED';
    const subtitle = clock?.subtitle || fallback.subtitle || title;
    const note = clock?.note || fallback.note || 'No active calendar ETA.';
    return `
      <article class="cycle-clock" data-mode="${esc(mode)}">
        <div class="clock-label"><span>${esc(label)}</span><i class="clock-dot"></i></div>
        <div class="clock-value">${esc(value)}</div>
        <div class="clock-title">${esc(subtitle)}</div>
        <small class="clock-note">${esc(note)}</small>
      </article>`;
  }

  function nextTimedStage(items) {
    return (items || []).find((item) => stateOf(item.phase) !== 'active' && parseWindowDays(item.window));
  }

  function broadStage(items) {
    return (items || []).find((item) => /broad altseason/i.test(String(item.phase || '')));
  }

  function actionPosture(item) {
    const segment = String(item?.segment || '').toUpperCase();
    const status = String(item?.status || '').toUpperCase();

    if (status.includes('INACTIVE')) {
      return segment.includes('MID') ? { label: 'WAIT / PREPARE', cls: 'wait' } : { label: 'WAIT', cls: 'wait' };
    }
    if (status.includes('SELECTIVE')) return { label: 'SELECTIVE', cls: 'active' };
    if (status.includes('LEADERSHIP') || status.includes('ATTEMPT')) return { label: 'WATCH / SELECTIVE', cls: 'active' };
    if (status.includes('ANCHOR') && status.includes('CONFLICT')) return { label: 'HOLD / NO CHASE', cls: '' };
    if (status.includes('PROTECT') || status.includes('DISTRIBUT')) return { label: 'PROTECT / DE-RISK', cls: 'protect' };
    return { label: 'WATCH', cls: '' };
  }

  function ensureShell() {
    if (document.getElementById('cycle-journey-heading')) return true;
    const rotation = document.getElementById('rotation-heading')?.closest('section');
    if (!rotation) return false;

    const journey = document.createElement('section');
    journey.className = 'section-block cycle-journey';
    journey.setAttribute('aria-labelledby', 'cycle-journey-heading');
    journey.innerHTML = `
      <div class="journey-hero-grid">
        <article class="panel journey-intro">
          <span class="kicker">Cycle Journey</span>
          <h2 id="cycle-journey-heading">Where capital moves next.</h2>
          <p id="journeySummary">Loading the OFFICIAL cycle route...</p>
          <span class="journey-question" id="journeyQuestion">Mapping the next confirmation gate</span>
        </article>
        <div class="clock-grid" id="cycleClocks" aria-label="Cycle timing clocks"></div>
      </div>
      <div class="panel phase-map">
        <div class="phase-map-head">
          <strong>Altcoin cycle timeline</strong>
          <small>Scenario windows, not automatic phase promotions.</small>
        </div>
        <div class="phase-track" id="journeyPhaseTrack"></div>
      </div>`;
    rotation.parentNode.insertBefore(journey, rotation);

    const compass = document.createElement('section');
    compass.className = 'section-block action-compass';
    compass.setAttribute('aria-labelledby', 'action-compass-heading');
    compass.innerHTML = `
      <div class="section-heading">
        <div>
          <span class="kicker">Cycle Action Compass</span>
          <h2 id="action-compass-heading">Hold, select, prepare — or protect?</h2>
        </div>
        <span class="section-note">Navigation shorthand · not portfolio execution authority</span>
      </div>
      <div class="action-grid" id="actionGrid"></div>
      <div class="compass-horizons">
        <article class="panel horizon-card">
          <span class="horizon-label">🔭 2–3 weeks</span>
          <h3 id="horizon23Posture">Current compass</h3>
          <p id="horizon23Copy">Loading...</p>
        </article>
        <article class="panel horizon-card">
          <span class="horizon-label">🛰️ 4–8 weeks</span>
          <h3 id="horizon48Posture">Longer cycle compass</h3>
          <p id="horizon48Copy">Loading...</p>
        </article>
      </div>
      <p class="compass-disclaimer">BUY / TOP-UP / SELL language is intentionally translated into public Cycle Navigator posture: HOLD, PREPARE, SELECTIVE DEPLOYMENT, BROADER DEPLOYMENT or PROTECT CAPITAL. The website never creates portfolio execution authority.</p>`;
    rotation.parentNode.insertBefore(compass, rotation.nextSibling);

    const audit = document.getElementById('report-heading')?.closest('section');
    if (audit) {
      const edition = document.createElement('section');
      edition.className = 'section-block public-edition';
      edition.setAttribute('aria-labelledby', 'public-edition-heading');
      edition.innerHTML = `
        <article class="panel public-edition-card">
          <div class="public-edition-head">
            <div>
              <span class="kicker">Public edition</span>
              <h2 id="public-edition-heading">The X version — without losing the live story.</h2>
              <p>Current CN narrative plus the latest confirmed public post, kept separate from LIVE prices.</p>
            </div>
            <span class="public-status" id="publicEditionStatus">SYNCING</span>
          </div>
          <details class="x-ready-details">
            <summary>Current X-ready Cycle Navigator</summary>
            <div class="x-ready-copy" id="xReadyCopy">Loading...</div>
          </details>
          <details class="x-ready-details">
            <summary id="latestPublishedSummary">Latest confirmed X publication</summary>
            <div class="x-ready-copy" id="latestPublishedCopy">Loading...</div>
          </details>
        </article>`;
      audit.parentNode.insertBefore(edition, audit);
    }
    return true;
  }

  function renderTimeline(pkg) {
    const root = document.getElementById('journeyPhaseTrack');
    if (!root) return;
    const official = Array.isArray(pkg.altseason_countdown) ? pkg.altseason_countdown : [];
    const extra = [
      { phase: '7. Altseason mania — LOCKED', window: 'Only after broad altseason; no active OFFICIAL ETA' },
      { phase: '8. Parabolic advance → distribution — LOCKED', window: 'Endgame phase; protect capital / de-risk if reached' }
    ];
    const items = [...official, ...extra];
    root.style.setProperty('--phase-count', items.length);
    root.innerHTML = items.map((item) => {
      const state = stateOf(item.phase);
      return `
        <article class="phase-node ${state}">
          <strong>${esc(cleanPhase(item.phase))}</strong>
          <small>${esc(item.window || 'No calendar ETA')}</small>
          <span class="phase-state">${esc(stateLabel(item.phase))}</span>
        </article>`;
    }).join('');
  }

  function renderClocks(pkg, history) {
    const root = document.getElementById('cycleClocks');
    if (!root) return;
    const stages = pkg.altseason_countdown || [];
    const next = nextTimedStage(stages);
    const broad = broadStage(stages);
    const nextClock = next ? clockFor(pkg.generated_unix, next.window) : null;
    const broadClock = broad ? clockFor(pkg.generated_unix, broad.window) : null;
    const maniaCurrent = pkg.altseason_mania_window ? clockFor(pkg.generated_unix, pkg.altseason_mania_window) : null;
    const histMania = history?.historical_mania_reference;

    root.innerHTML = [
      clockCard('Next phase', cleanPhase(next?.phase || 'Next confirmation'), nextClock, {
        mode: 'locked', value: 'EVIDENCE FIRST', subtitle: cleanPhase(next?.phase || 'Next confirmation'), note: next?.window || 'No active timed next-stage window.'
      }),
      clockCard('Broad altseason', 'Broad altseason', broadClock, {
        mode: 'paused', value: 'PAUSED', subtitle: 'No calendar ETA', note: broad?.window || 'Waiting for broad, persistent alt/BTC outperformance.'
      }),
      clockCard('Altseason mania', 'Altseason mania', maniaCurrent, {
        mode: 'locked', value: 'LOCKED', subtitle: 'No active mania ETA', note: histMania?.window
          ? `Historical CN #${histMania.issue}: ${histMania.window}. Superseded by the current paused state.`
          : 'Only becomes timeable after broad altseason is credibly active.'
      })
    ].join('');
  }

  function renderCompass(pkg) {
    const root = document.getElementById('actionGrid');
    if (!root) return;
    root.innerHTML = (pkg.rotation_ladder || []).map((item) => {
      const posture = actionPosture(item);
      return `
        <article class="action-tile">
          <strong>${esc(item.segment)}</strong>
          <span class="action-posture ${esc(posture.cls)}">${esc(posture.label)}</span>
          <p>${esc(item.status)}</p>
        </article>`;
    }).join('');

    const copy23 = pkg.base_case_2_3_weeks || 'UNAVAILABLE in the current OFFICIAL issue.';
    const copy48 = pkg.base_case_4_8_weeks || pkg.compass_4_8_weeks || 'UNAVAILABLE in the current OFFICIAL issue. Future CN issues are required to publish this when evidence permits.';
    document.getElementById('horizon23Copy').textContent = copy23;
    document.getElementById('horizon48Copy').textContent = copy48;

    const upper = copy23.toUpperCase();
    document.getElementById('horizon23Posture').textContent = upper.includes('BROAD') && upper.includes('CONFIRM')
      ? 'Prepare for broader deployment only on confirmation'
      : 'Selective / prepare';
    document.getElementById('horizon48Posture').textContent = copy48.startsWith('UNAVAILABLE') ? 'UNAVAILABLE — no invented view' : 'Cycle direction / capital protection';
  }

  function renderEdition(pkg, pointer, history) {
    const status = pointer?.publication_status || pkg.publication_status || 'UNKNOWN';
    const badge = document.getElementById('publicEditionStatus');
    if (badge) badge.textContent = String(status).replaceAll('_', ' ');

    const xReady = document.getElementById('xReadyCopy');
    if (xReady) xReady.textContent = pkg.x_ready_markdown || 'No X-ready copy is included in this public snapshot.';

    const latest = history?.latest_published_x;
    const summary = document.getElementById('latestPublishedSummary');
    const copy = document.getElementById('latestPublishedCopy');
    if (summary) summary.textContent = latest?.issue ? `Latest confirmed X publication · CN #${latest.issue}` : 'Latest confirmed X publication';
    if (copy) copy.textContent = latest?.text || 'No confirmed published X copy is bundled.';
  }

  function render(snapshot) {
    if (!ensureShell()) return;
    const pkg = snapshot?.package || {};
    const pointer = snapshot?.pointer || {};
    const history = snapshot?.public_history || {};
    const stages = pkg.altseason_countdown || [];
    const next = nextTimedStage(stages);

    document.getElementById('journeySummary').textContent = pkg.market_state || 'Cycle state unavailable.';
    document.getElementById('journeyQuestion').textContent = next
      ? `Next gate: ${cleanPhase(next.phase)} · ${next.window}`
      : 'Next gate: evidence must define the next phase';

    renderClocks(pkg, history);
    renderTimeline(pkg);
    renderCompass(pkg);
    renderEdition(pkg, pointer, history);
  }

  async function load() {
    try {
      const response = await fetch(`${DATA_URL}?journey=${Date.now()}`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`Journey snapshot HTTP ${response.status}`);
      render(await response.json());
    } catch (error) {
      console.warn('Cycle Journey snapshot unavailable', error);
    }
  }

  function start() {
    ensureShell();
    load();
    clearInterval(refreshTimer);
    refreshTimer = setInterval(load, 5 * 60_000);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
  else start();
})();
