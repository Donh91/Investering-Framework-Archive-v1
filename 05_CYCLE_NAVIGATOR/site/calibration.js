(() => {
  'use strict';

  const DATA_URL = './data/latest.json';
  let countdownTimer = null;

  const esc = (value) => String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

  const numeric = (value) => value != null && value !== '' && Number.isFinite(Number(value));
  const fmtScore = (value) => numeric(value) ? `${Math.round(Number(value))}%` : 'N/A';
  const mean = (values) => {
    const nums = values.filter(numeric).map(Number);
    return nums.length ? nums.reduce((sum, value) => sum + value, 0) / nums.length : null;
  };

  function isoWeekEndUtc(year, week) {
    const y = Number(year);
    const w = Number(week);
    if (!Number.isInteger(y) || !Number.isInteger(w)) return null;
    const jan4 = new Date(Date.UTC(y, 0, 4));
    const jan4Day = jan4.getUTCDay() || 7;
    const monday = new Date(jan4);
    monday.setUTCDate(jan4.getUTCDate() - jan4Day + 1 + (w - 1) * 7);
    const nextMonday = new Date(monday);
    nextMonday.setUTCDate(monday.getUTCDate() + 7);
    return nextMonday;
  }

  function duration(ms) {
    const minutes = Math.max(0, Math.floor(ms / 60000));
    const days = Math.floor(minutes / 1440);
    const hours = Math.floor((minutes % 1440) / 60);
    const mins = minutes % 60;
    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h ${mins}m`;
    return `${mins}m`;
  }

  function ensureShell() {
    if (document.getElementById('calibration-heading')) return true;
    const hero = document.querySelector('main .hero');
    const navWrap = document.querySelector('.journey-nav-wrap');
    const nav = document.querySelector('.journey-nav');
    if (!hero || !navWrap || !nav) return false;

    if (!document.querySelector('a[href="#calibration-heading"]')) {
      const scoreLink = document.createElement('a');
      scoreLink.href = '#calibration-heading';
      scoreLink.textContent = 'Score';
      nav.insertBefore(scoreLink, nav.querySelector('a[href="#public-edition-heading"]') || null);
    }

    if (!document.getElementById('calibrationChip')) {
      const chip = document.createElement('a');
      chip.id = 'calibrationChip';
      chip.className = 'calibration-chip';
      chip.href = '#calibration-heading';
      chip.setAttribute('aria-label', 'Open verified Cycle Navigator calibration');
      chip.innerHTML = '<span>Verified</span><strong id="calibrationChipScore">—</strong>';
      navWrap.appendChild(chip);
    }

    const section = document.createElement('section');
    section.className = 'section-block calibration-center';
    section.setAttribute('aria-labelledby', 'calibration-heading');
    section.innerHTML = `
      <div class="calibration-head">
        <div>
          <span class="kicker">Calibration Center</span>
          <h2 id="calibration-heading">How accurate has Cycle Navigator been?</h2>
          <p>Machine-valid scores start only where the GitHub track record is reproducible. Current-week scoring stays open until the frozen tests can be judged against completed evidence.</p>
        </div>
        <span class="calibration-freshness" id="calibrationFreshness">Syncing track record…</span>
      </div>
      <div class="cal-summary-grid">
        <article class="cal-summary-card primary">
          <span class="cal-summary-label">Latest verified</span>
          <strong class="cal-summary-value" id="latestVerifiedScore">—</strong>
          <small class="cal-summary-note" id="latestVerifiedNote">Waiting for the reproducible track record.</small>
        </article>
        <article class="cal-summary-card">
          <span class="cal-summary-label">Verified rolling mean</span>
          <strong class="cal-summary-value" id="verifiedMean">—</strong>
          <small class="cal-summary-note" id="verifiedMeanNote">Only machine-valid rows count.</small>
        </article>
        <article class="cal-summary-card">
          <span class="cal-summary-label">Current CN scoring</span>
          <strong class="cal-summary-value" id="currentScoreState">OPEN</strong>
          <small class="cal-summary-note" id="currentScoreNote">Frozen tests are awaiting completed evidence.</small>
        </article>
      </div>
      <div class="panel cal-tabs-shell">
        <div class="cal-tabs" role="tablist" aria-label="Calibration views">
          <button class="cal-tab active" type="button" role="tab" aria-selected="true" data-cal-tab="verified">Verified track record</button>
          <button class="cal-tab" type="button" role="tab" aria-selected="false" data-cal-tab="current">Current scoring</button>
          <button class="cal-tab" type="button" role="tab" aria-selected="false" data-cal-tab="xrecord">Public X record</button>
        </div>
        <div class="cal-panel active" data-cal-panel="verified">
          <div class="cal-panel-intro">
            <div><h3>Reproducible GitHub ledger</h3><p>The curve begins only when a frozen forecast can be scored against completed evidence. Legacy public claims are excluded.</p></div>
            <span class="cal-method-badge">Machine-valid only</span>
          </div>
          <div class="score-history" id="verifiedScoreHistory"></div>
          <div class="cal-caveat">Older CN issues may contain public score claims, but they do not enter this verified line unless the current contract can reproduce them.</div>
        </div>
        <div class="cal-panel" data-cal-panel="current">
          <div class="cal-panel-intro">
            <div><h3>Current issue · scoring in progress</h3><p>A live percentage appears only if a valid interim scoring artifact exists. Otherwise the open confirmation tests are shown instead of manufacturing precision.</p></div>
            <span class="cal-method-badge" id="currentIssueBadge">OPEN</span>
          </div>
          <div class="current-score-grid">
            <article class="current-score-status">
              <span class="cal-summary-label">Next verification checkpoint</span>
              <strong id="currentIssueLabel">Current CN</strong>
              <small id="currentIssueStatus">Waiting for completed-week evidence and the official scoring pass.</small>
              <div class="score-countdown" id="scoreCountdown">Calculating week close…</div>
            </article>
            <div class="frozen-test-list" id="currentFrozenTests"></div>
          </div>
        </div>
        <div class="cal-panel" data-cal-panel="xrecord">
          <div class="cal-panel-intro">
            <div><h3>What the published X posts claimed</h3><p>A separate history of published precision numbers. Useful for continuity, but never merged into the machine-valid series.</p></div>
            <span class="cal-method-badge">Legacy public record</span>
          </div>
          <div class="x-record-summary">
            <article class="x-aggregate">
              <span class="cal-summary-label">Claimed average</span>
              <strong id="xClaimMean">—</strong>
              <small id="xClaimMeanNote">Across archived X posts with an explicit overall precision number.</small>
            </article>
            <div class="x-claims" id="xClaims"></div>
          </div>
          <div class="cal-caveat">Public X precision used an older presentation/scoring approach. It is shown for transparency, not as scientific calibration and not as a directly comparable series to the current structural score.</div>
        </div>
      </div>`;

    hero.parentNode.insertBefore(section, hero.nextSibling);
    section.querySelectorAll('[data-cal-tab]').forEach((button) => {
      button.addEventListener('click', () => {
        const target = button.dataset.calTab;
        section.querySelectorAll('[data-cal-tab]').forEach((tab) => {
          const active = tab === button;
          tab.classList.toggle('active', active);
          tab.setAttribute('aria-selected', String(active));
        });
        section.querySelectorAll('[data-cal-panel]').forEach((panel) => panel.classList.toggle('active', panel.dataset.calPanel === target));
      });
    });
    return true;
  }

  function renderVerified(track) {
    const rows = Array.isArray(track?.rows) ? track.rows : [];
    const scored = rows.filter((row) => numeric(row.structural_score) && String(row.score_status).toUpperCase() === 'REPRODUCIBLE');
    const latest = scored.at(-1);
    const rolling = mean(scored.map((row) => row.structural_score));

    document.getElementById('latestVerifiedScore').textContent = latest ? fmtScore(latest.structural_score) : 'N/A';
    document.getElementById('calibrationChipScore').textContent = latest ? fmtScore(latest.structural_score) : 'N/A';
    document.getElementById('latestVerifiedNote').textContent = latest
      ? `CN #${latest.issue_scored} · completed W${latest.completed_iso_week} · ${latest.score_status}`
      : 'No reproducible numerical score has been logged yet.';
    document.getElementById('verifiedMean').textContent = rolling == null ? 'N/A' : fmtScore(rolling);
    document.getElementById('verifiedMeanNote').textContent = scored.length
      ? `${scored.length} reproducible numerical ${scored.length === 1 ? 'week' : 'weeks'} in the current ledger.`
      : 'No reproducible numerical weeks yet.';

    const root = document.getElementById('verifiedScoreHistory');
    if (!rows.length) {
      root.innerHTML = '<div class="cal-caveat">Track record unavailable in the public snapshot.</div>';
      return;
    }
    root.innerHTML = rows.map((row) => {
      const valid = numeric(row.structural_score) && String(row.score_status).toUpperCase() === 'REPRODUCIBLE';
      const score = valid ? Math.max(0, Math.min(100, Number(row.structural_score))) : null;
      return `<div class="score-row ${valid ? '' : 'na'}">
        <div class="score-row-meta"><strong>CN #${esc(row.issue_scored ?? '—')}</strong><small>W${esc(row.completed_iso_week ?? '—')} · ${esc(row.score_status ?? 'UNKNOWN')}</small></div>
        <div class="score-track" aria-label="${valid ? `Structural score ${score}%` : 'No reproducible numerical score'}">${valid ? `<div class="score-fill" style="--score-width:${score}%"></div>` : ''}</div>
        <div class="score-row-value">${valid ? fmtScore(score) : 'N/A'}</div>
      </div>`;
    }).join('');
  }

  function renderCurrent(snapshot) {
    const pkg = snapshot?.package || {};
    const pointer = snapshot?.pointer || {};
    const scoring = snapshot?.calibration?.current || {};
    const tests = Array.isArray(pkg.forecast_freeze?.structural_calls) ? pkg.forecast_freeze.structural_calls : [];
    const hasProvisional = numeric(scoring.provisional_score);

    document.getElementById('currentScoreState').textContent = hasProvisional ? fmtScore(scoring.provisional_score) : 'OPEN';
    document.getElementById('currentScoreNote').textContent = hasProvisional
      ? `Provisional only · ${scoring.provisional_status || 'not final'}`
      : `${tests.length} frozen confirmation ${tests.length === 1 ? 'test' : 'tests'} awaiting completed evidence.`;
    document.getElementById('currentIssueLabel').textContent = `CN #${pkg.issue_number ?? pointer.issue_number ?? '—'} · W${pointer.iso_week ?? '—'}`;
    document.getElementById('currentIssueBadge').textContent = hasProvisional ? 'PROVISIONAL' : 'OPEN';
    document.getElementById('currentIssueStatus').textContent = hasProvisional
      ? 'An interim scoring artifact exists. It remains non-final until the official completed-week scoring pass.'
      : 'No valid interim numerical score is published. Open calls receive no precision credit before the outcome is known.';

    document.getElementById('currentFrozenTests').innerHTML = tests.length ? tests.map((test, index) => `
      <article class="frozen-test"><span class="frozen-test-index">${index + 1}</span><p>${esc(test)}</p><span class="test-open">Open</span></article>`).join('')
      : '<div class="cal-caveat">No frozen structural tests are present in the current public package.</div>';

    if (countdownTimer) clearInterval(countdownTimer);
    const close = isoWeekEndUtc(pointer.iso_year, pointer.iso_week);
    const updateCountdown = () => {
      const node = document.getElementById('scoreCountdown');
      if (!node) return;
      if (!close) return void (node.textContent = 'Next checkpoint follows the official completed-week scoring pass.');
      const remaining = close.getTime() - Date.now();
      node.textContent = remaining > 0
        ? `ISO week closes in ${duration(remaining)} · verification follows completed evidence`
        : 'ISO week closed · awaiting official verified score';
    };
    updateCountdown();
    countdownTimer = setInterval(updateCountdown, 60_000);
  }

  function renderXRecord(history) {
    const claims = Array.isArray(history?.x_precision_claims) ? history.x_precision_claims : [];
    const avg = mean(claims.map((claim) => claim.overall_precision));
    document.getElementById('xClaimMean').textContent = avg == null ? 'N/A' : fmtScore(avg);
    document.getElementById('xClaimMeanNote').textContent = claims.length
      ? `Across ${claims.length} archived X ${claims.length === 1 ? 'claim' : 'claims'} with an explicit overall precision number.`
      : 'No archived X post with an explicit overall precision number was found.';
    document.getElementById('xClaims').innerHTML = claims.length ? claims.map((claim) => `
      <article class="x-claim"><div><strong>CN #${esc(claim.scored_issue ?? '—')}</strong><small>Published in CN #${esc(claim.publication_issue ?? '—')} · ${esc(claim.date ?? '')}</small></div><span class="x-claim-score">${fmtScore(claim.overall_precision)}</span></article>`).join('')
      : '<div class="cal-caveat">No public precision claims found.</div>';
  }

  function render(snapshot) {
    if (!ensureShell()) return;
    renderVerified(snapshot?.calibration?.track_record || {});
    renderCurrent(snapshot);
    renderXRecord(snapshot?.public_history || {});
    const generated = snapshot?.generated_at_utc ? new Date(snapshot.generated_at_utc) : null;
    document.getElementById('calibrationFreshness').textContent = generated && !Number.isNaN(generated.getTime())
      ? `Public calibration snapshot · ${generated.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}`
      : 'Public calibration snapshot';
  }

  async function load() {
    try {
      const response = await fetch(`${DATA_URL}?calibration=${Date.now()}`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`Calibration snapshot HTTP ${response.status}`);
      render(await response.json());
    } catch (error) {
      console.warn('Cycle Navigator calibration unavailable', error);
      ensureShell();
      const freshness = document.getElementById('calibrationFreshness');
      if (freshness) freshness.textContent = 'Calibration feed unavailable';
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load, { once: true });
  else load();
  setInterval(load, 5 * 60_000);
})();
