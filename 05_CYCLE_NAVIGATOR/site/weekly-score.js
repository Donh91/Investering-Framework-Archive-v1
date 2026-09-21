(() => {
  'use strict';

  const DATA_URL = './data/latest.json';
  const numeric = (value) => value != null && value !== '' && Number.isFinite(Number(value));
  const fmt = (value) => numeric(value) ? `${Math.round(Number(value))}%` : 'N/A';
  const esc = (value) => String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

  const weekNumber = (value) => {
    const match = String(value || '').match(/W(\d{1,2})$/i);
    return match ? Number(match[1]) : null;
  };

  function latestRangeScore(snapshot, bundle) {
    const range = snapshot?.range_score;
    if (!range || !numeric(range.price_range_score) || !numeric(range.issue_scored)) return null;
    const rangeWeek = weekNumber(range.forecast_week);
    const bundleWeek = numeric(bundle?.completed_iso_week) ? Number(bundle.completed_iso_week) : null;
    const newerThanBundle = rangeWeek != null && (bundleWeek == null || rangeWeek > bundleWeek);
    const fillsMissingSameWeek = rangeWeek != null
      && bundleWeek != null
      && rangeWeek === bundleWeek
      && !numeric(bundle?.price_range_score);
    return newerThanBundle || fillsMissingSameWeek ? { ...range, completed_iso_week: rangeWeek } : null;
  }

  function rangeScoreCards(range) {
    const windows = range?.intraday_window_scores || {};
    const intraday = [
      numeric(windows.day_1_2) ? `D1–2 ${Math.round(Number(windows.day_1_2))}%` : null,
      numeric(windows.day_3_4) ? `D3–4 ${Math.round(Number(windows.day_3_4))}%` : null,
      numeric(windows.day_5_7) ? `D5–7 ${Math.round(Number(windows.day_5_7))}%` : null
    ].filter(Boolean).join(' · ') || 'N/A';
    return `
      <article class="cal-summary-card">
        <span class="cal-summary-label">Price range precision</span>
        <strong class="cal-summary-value">${fmt(range.price_range_score)}</strong>
        <small class="cal-summary-note">Final reconciled completed-week score</small>
      </article>
      <article class="cal-summary-card">
        <span class="cal-summary-label">BTC ranges</span>
        <strong class="cal-summary-value">${fmt(range.btc_score)}</strong>
        <small class="cal-summary-note">Prospective ranges vs completed actuals</small>
      </article>
      <article class="cal-summary-card">
        <span class="cal-summary-label">ETH ranges</span>
        <strong class="cal-summary-value">${fmt(range.eth_score)}</strong>
        <small class="cal-summary-note">Prospective ranges vs completed actuals</small>
      </article>
      <article class="cal-summary-card">
        <span class="cal-summary-label">Intraday windows</span>
        <strong class="cal-summary-value" style="font-size:1rem">${esc(intraday)}</strong>
        <small class="cal-summary-note">Completed D1–2, D3–4 and D5–7 windows</small>
      </article>`;
  }

  function scoreCards(bundle) {
    const rows = [
      ['Structural', bundle.structural_score],
      ['Price ranges', bundle.price_range_score],
      ['Decision utility', bundle.decision_utility_score],
      ['Public continuity', bundle.public_continuity_score]
    ];
    return rows.map(([label, value]) => `
      <article class="cal-summary-card">
        <span class="cal-summary-label">${esc(label)}</span>
        <strong class="cal-summary-value">${fmt(value)}</strong>
        <small class="cal-summary-note">${numeric(value) ? 'Verified weekly score' : 'Not scored / unavailable'}</small>
      </article>`).join('');
  }

  function parameterRows(bundle) {
    const rows = Array.isArray(bundle.parameter_scores) ? bundle.parameter_scores : [];
    if (!rows.length) return '';
    return `
      <div class="score-history" style="margin-top:1rem">
        ${rows.map((row) => {
          const valid = numeric(row.score);
          const score = valid ? Math.max(0, Math.min(100, Number(row.score))) : null;
          return `<div class="score-row ${valid ? '' : 'na'}">
            <div class="score-row-meta"><strong>${esc(row.parameter_id || 'parameter')}</strong><small>${esc(row.status || 'UNKNOWN')}</small></div>
            <div class="score-track" aria-label="${valid ? `Score ${score}%` : 'Not evaluable'}">${valid ? `<div class="score-fill" style="--score-width:${score}%"></div>` : ''}</div>
            <div class="score-row-value">${valid ? fmt(score) : 'N/A'}</div>
          </div>`;
        }).join('')}
      </div>`;
  }

  function insertPanel(snapshot) {
    if (document.getElementById('weeklyCanonicalScorecard')) return;
    const bundle = snapshot?.weekly_score_bundle;
    const range = latestRangeScore(snapshot, bundle);
    if (!bundle && !range) return;

    const section = document.createElement('section');
    section.id = 'weeklyCanonicalScorecard';
    section.className = 'section-block';
    section.setAttribute('aria-label', 'Weekly verified Cycle Navigator scorecard');
    if (range) {
      section.innerHTML = `
        <div class="panel">
          <div class="cal-panel-intro">
            <div>
              <span class="kicker">Latest completed precision</span>
              <h3>CN #${esc(range.issue_scored ?? '—')} · completed W${esc(range.completed_iso_week ?? '—')}</h3>
              <p>Final reconciled range precision from the prospectively published forecast and 168/168 completed-week hourly actuals. No synthetic overall score is shown.</p>
            </div>
            <span class="cal-method-badge">${esc(range.status || 'FINAL')}</span>
          </div>
          <div class="cal-summary-grid">${rangeScoreCards(range)}</div>
        </div>`;
    } else {
      section.innerHTML = `
        <div class="panel">
          <div class="cal-panel-intro">
            <div>
              <span class="kicker">Weekly verified scorecard</span>
              <h3>CN #${esc(bundle.issue_scored ?? '—')} · completed W${esc(bundle.completed_iso_week ?? '—')}</h3>
              <p>Direct from the canonical weekly CN scorecard generated after final Master Monday. X is downstream publication only and is never a score source for this site.</p>
            </div>
            <span class="cal-method-badge">${esc(bundle.score_status || 'UNKNOWN')}</span>
          </div>
          <div class="cal-summary-grid">${scoreCards(bundle)}</div>
          ${parameterRows(bundle)}
        </div>`;
    }

    const calibration = document.querySelector('.calibration-center');
    if (calibration?.parentNode) {
      calibration.parentNode.insertBefore(section, calibration.nextSibling);
      return;
    }
    const hero = document.querySelector('main .hero');
    if (hero?.parentNode) hero.parentNode.insertBefore(section, hero.nextSibling);
  }

  async function load() {
    try {
      const response = await fetch(`${DATA_URL}?weekly-score=${Date.now()}`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`Weekly score snapshot HTTP ${response.status}`);
      const snapshot = await response.json();
      const tryInsert = () => insertPanel(snapshot);
      tryInsert();
      if (!document.getElementById('weeklyCanonicalScorecard')) {
        const observer = new MutationObserver(() => {
          tryInsert();
          if (document.getElementById('weeklyCanonicalScorecard')) observer.disconnect();
        });
        observer.observe(document.body, { childList: true, subtree: true });
        setTimeout(() => observer.disconnect(), 5000);
      }
    } catch (error) {
      console.warn('Weekly canonical scorecard unavailable', error);
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load, { once: true });
  else load();
})();
