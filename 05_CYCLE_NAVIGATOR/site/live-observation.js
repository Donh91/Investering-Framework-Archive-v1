(() => {
  'use strict';
  const DATA_URL = './data/latest.json';
  const esc = (value) => String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
  const numeric = (value) => value != null && value !== '' && Number.isFinite(Number(value));

  function statusCounts(tests) {
    const counts = { ON_TRACK: 0, MIXED: 0, OFF_TRACK: 0, OPEN: 0 };
    for (const test of Array.isArray(tests) ? tests : []) {
      const key = String(test?.status || 'OPEN').toUpperCase();
      counts[key] = (counts[key] || 0) + 1;
    }
    return counts;
  }

  function renderShortcut(snapshot) {
    const live = snapshot?.live_observation;
    if (!live) return;
    const score = document.getElementById('shortcutScore');
    const note = document.getElementById('shortcutScoreNote');
    const verified = snapshot?.weekly_score_bundle;
    const held = String(live.maturity_state || '').toUpperCase() === 'HELD';
    const current = numeric(live.provisional_score);
    const measured = Number(live.evaluable_count || 0);
    const total = Number(live.frozen_claim_count || 0);

    if (score) score.textContent = current ? `${Math.round(Number(live.provisional_score))}% ${held ? 'HELD' : 'LIVE'}` : 'CALIBRATING';
    if (note) {
      const coverage = `${measured}/${total || '—'} frozen calls measurable`;
      const last = numeric(verified?.structural_score)
        ? `Last verified: CN #${verified.issue_scored} ${Math.round(Number(verified.structural_score))}%`
        : 'Verified history pending';
      note.textContent = current ? `${coverage} · provisional · ${last}` : `${coverage} · ${last}`;
    }
  }

  function renderCurrentScoring(snapshot) {
    const live = snapshot?.live_observation;
    if (!live) return;
    const section = document.getElementById('current-scoring');
    if (section) {
      const heading = section.querySelector('h2');
      const intro = section.querySelector('.section-intro');
      if (heading) heading.textContent = 'Live until the week closes.';
      if (intro) intro.textContent = 'Frozen Monday calls are checked against new observations through the week. Only the next verified CN score enters the permanent track record.';
    }
    const state = document.getElementById('currentScoreState');
    if (!state) return;
    const held = String(live.maturity_state || '').toUpperCase() === 'HELD';
    state.textContent = numeric(live.provisional_score)
      ? `${Math.round(Number(live.provisional_score))}% ${held ? 'HELD' : 'LIVE'} · ${live.evaluable_count}/${live.frozen_claim_count}`
      : `CALIBRATING · ${live.evaluable_count || 0}/${live.frozen_claim_count || 0}`;
  }

  function panelMarkup(snapshot) {
    const live = snapshot?.live_observation || {};
    const verified = snapshot?.weekly_score_bundle || {};
    const tests = Array.isArray(live.tests) ? live.tests : [];
    const counts = statusCounts(tests);
    const ranges = Array.isArray(live.frozen_numeric_ranges) ? live.frozen_numeric_ranges : [];
    const hasLiveScore = numeric(live.provisional_score);
    const hasPriceScore = numeric(live.price_tracking_score);
    const held = String(live.maturity_state || '').toUpperCase() === 'HELD';
    const main = hasLiveScore ? `${Math.round(Number(live.provisional_score))}%` : 'Calibrating';
    const badge = held ? 'WEEK HELD' : hasLiveScore ? 'LIVE · PROVISIONAL' : 'WEEK IN PROGRESS';
    const verifiedCopy = numeric(verified.structural_score)
      ? `CN #${verified.issue_scored} · ${Math.round(Number(verified.structural_score))}%`
      : 'Not available yet';
    const priceMain = ranges.length ? (hasPriceScore ? `${Math.round(Number(live.price_tracking_score))}% LIVE` : 'Tracking') : 'Not published';
    const priceNote = ranges.length
      ? ranges.map((row) => `${row.asset} ${row.status === 'BREACHED' ? 'outside range' : row.status === 'IN_RANGE_SO_FAR' ? 'inside range so far' : 'open'}`).join(' · ')
      : 'No frozen BTC/ETH price range this week.';
    const updated = live.observation_through_utc
      ? new Date(live.observation_through_utc).toLocaleString([], { weekday: 'short', hour: '2-digit', minute: '2-digit' })
      : 'Waiting for first measurable observation';

    return `
      <div class="panel">
        <div class="cal-panel-intro">
          <div>
            <span class="kicker">Live precision</span>
            <h3>${esc(main)}${hasLiveScore ? '<span style="font-size:.48em;vertical-align:top;margin-left:.2em">*</span>' : ''}</h3>
            <p>${esc(live.note || 'Frozen Monday calls are tracked through the week without changing the official forecast.')}</p>
          </div>
          <span class="cal-method-badge">${esc(badge)}</span>
        </div>
        <div class="cal-summary-grid">
          <article class="cal-summary-card">
            <span class="cal-summary-label">Measured now</span>
            <strong class="cal-summary-value">${esc(live.evaluable_count ?? 0)}/${esc(live.frozen_claim_count ?? 0)}</strong>
            <small class="cal-summary-note">Only directly measurable frozen calls enter the live percentage.</small>
          </article>
          <article class="cal-summary-card">
            <span class="cal-summary-label">Call status</span>
            <strong class="cal-summary-value">${esc(counts.ON_TRACK)} on track</strong>
            <small class="cal-summary-note">${esc(counts.MIXED)} mixed · ${esc(counts.OFF_TRACK)} off track · ${esc(counts.OPEN)} open</small>
          </article>
          <article class="cal-summary-card">
            <span class="cal-summary-label">Last verified</span>
            <strong class="cal-summary-value">${esc(verifiedCopy)}</strong>
            <small class="cal-summary-note">Locked weekly result after the prior issue closed.</small>
          </article>
          <article class="cal-summary-card">
            <span class="cal-summary-label">Price tracking</span>
            <strong class="cal-summary-value">${esc(priceMain)}</strong>
            <small class="cal-summary-note">${esc(priceNote)}</small>
          </article>
        </div>
        <div class="score-history" style="margin-top:1rem">
          ${tests.map((test) => `<div class="score-row ${test.status === 'OPEN' ? 'na' : ''}">
            <div class="score-row-meta"><strong>Call ${esc(test.test_id)}</strong><small>${esc(test.family || 'weekly')}</small></div>
            <div class="score-track" aria-label="${esc(test.status)}">${numeric(test.score) ? `<div class="score-fill" style="--score-width:${Math.max(0, Math.min(100, Number(test.score)))}%"></div>` : ''}</div>
            <div class="score-row-value">${esc(test.status === 'ON_TRACK' ? 'ON TRACK' : test.status === 'OFF_TRACK' ? 'OFF TRACK' : test.status === 'MIXED' ? 'MIXED' : 'OPEN')}</div>
          </div>`).join('')}
        </div>
        <small class="cal-summary-note" style="display:block;margin-top:1rem">Updated through ${esc(updated)}. *Live percentage is provisional and automatically stops at the weekly horizon; only the next verified CN score enters the permanent track record.</small>
      </div>`;
  }

  function renderPanel(snapshot) {
    const live = snapshot?.live_observation;
    if (!live) return;
    let section = document.getElementById('livePrecisionObservation');
    if (!section) {
      section = document.createElement('section');
      section.id = 'livePrecisionObservation';
      section.className = 'section-block';
      section.setAttribute('aria-label', 'Live provisional Cycle Navigator precision');
      const weekly = document.getElementById('weeklyCanonicalScorecard');
      if (weekly?.parentNode) weekly.parentNode.insertBefore(section, weekly);
      else {
        const calibration = document.querySelector('.calibration-center') || document.getElementById('calibration');
        if (calibration?.parentNode) calibration.parentNode.insertBefore(section, calibration);
        else document.querySelector('main')?.appendChild(section);
      }
    }
    section.innerHTML = panelMarkup(snapshot);
  }

  function render(snapshot) {
    renderPanel(snapshot);
    renderShortcut(snapshot);
    renderCurrentScoring(snapshot);
  }

  async function load() {
    try {
      const response = await fetch(`${DATA_URL}?live-observation=${Date.now()}`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`Live observation snapshot HTTP ${response.status}`);
      render(await response.json());
    } catch (error) {
      console.warn('Live precision temporarily unavailable', error);
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load, { once: true });
  else load();
  setInterval(load, 5 * 60 * 1000);
})();
