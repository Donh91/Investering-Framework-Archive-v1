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
    if (!bundle) return;

    const section = document.createElement('section');
    section.id = 'weeklyCanonicalScorecard';
    section.className = 'section-block';
    section.setAttribute('aria-label', 'Weekly verified Cycle Navigator scorecard');
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
