(() => {
  'use strict';
  const DATA_URL = './data/latest.json';
  const esc = (value) => String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

  function insertPanel(snapshot) {
    if (document.getElementById('livePrecisionObservation')) return;
    const live = snapshot?.live_observation;
    if (!live) return;

    const section = document.createElement('section');
    section.id = 'livePrecisionObservation';
    section.className = 'section-block';
    section.setAttribute('aria-label', 'Live provisional Cycle Navigator observation');

    const hasScore = Number.isFinite(Number(live.provisional_score));
    const ranges = Array.isArray(live.frozen_numeric_ranges) ? live.frozen_numeric_ranges : [];
    const statusLabel = hasScore ? `${Math.round(Number(live.provisional_score))}% provisional` : 'Tracking';
    const rangeCopy = ranges.length
      ? `${ranges.length} frozen numerical range${ranges.length === 1 ? '' : 's'} eligible for live observation.`
      : 'No numerical price range was published for this issue, so live prices are not scored.';

    section.innerHTML = `
      <div class="panel">
        <div class="cal-panel-intro">
          <div>
            <span class="kicker">Live observation</span>
            <h3>${esc(statusLabel)}</h3>
            <p>${esc(live.note || 'Current frozen claims are tracked without changing the official weekly forecast or Monday score.')}</p>
          </div>
          <span class="cal-method-badge">Observation only</span>
        </div>
        <div class="cal-summary-grid">
          <article class="cal-summary-card">
            <span class="cal-summary-label">Frozen claims</span>
            <strong class="cal-summary-value">${esc(live.frozen_claim_count ?? 0)}</strong>
            <small class="cal-summary-note">Immutable current-issue claims</small>
          </article>
          <article class="cal-summary-card">
            <span class="cal-summary-label">Due this week</span>
            <strong class="cal-summary-value">${esc(live.claims_due_this_week ?? 0)}</strong>
            <small class="cal-summary-note">Still requires eligible outcome evidence</small>
          </article>
          <article class="cal-summary-card">
            <span class="cal-summary-label">Provisional precision</span>
            <strong class="cal-summary-value">${hasScore ? `${Math.round(Number(live.provisional_score))}%` : 'Pending'}</strong>
            <small class="cal-summary-note">Never substitutes for the verified Monday score</small>
          </article>
          <article class="cal-summary-card">
            <span class="cal-summary-label">Live price scoring</span>
            <strong class="cal-summary-value">${ranges.length ? 'Available' : 'Off'}</strong>
            <small class="cal-summary-note">${esc(rangeCopy)}</small>
          </article>
        </div>
      </div>`;

    const weekly = document.getElementById('weeklyCanonicalScorecard');
    if (weekly?.parentNode) {
      weekly.parentNode.insertBefore(section, weekly);
      return;
    }
    const calibration = document.querySelector('.calibration-center');
    if (calibration?.parentNode) calibration.parentNode.insertBefore(section, calibration.nextSibling);
  }

  async function load() {
    try {
      const response = await fetch(`${DATA_URL}?live-observation=${Date.now()}`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`Live observation snapshot HTTP ${response.status}`);
      const snapshot = await response.json();
      const attempt = () => insertPanel(snapshot);
      attempt();
      if (!document.getElementById('livePrecisionObservation')) {
        const observer = new MutationObserver(() => {
          attempt();
          if (document.getElementById('livePrecisionObservation')) observer.disconnect();
        });
        observer.observe(document.body, { childList: true, subtree: true });
        setTimeout(() => observer.disconnect(), 5000);
      }
    } catch (error) {
      console.warn('Live observation unavailable', error);
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load, { once: true });
  else load();
})();
