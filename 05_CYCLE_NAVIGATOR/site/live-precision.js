(() => {
  'use strict';
  const DATA_URL = './data/latest.json';
  const $ = (id) => document.getElementById(id);
  const esc = (value) => String(value ?? '')
    .replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;').replaceAll("'", '&#039;');

  function statusView(status) {
    const value = String(status || 'WAITING_FOR_EVIDENCE').toUpperCase();
    const map = {
      CURRENTLY_ON_TRACK: ['On track now', 'positive'],
      CURRENTLY_OFF_TRACK: ['Off track now', 'negative'],
      PROXY_ONLY: ['Proxy only', 'proxy'],
      WAITING_FOR_WEEK_CLOSE: ['Week still open', 'waiting'],
      WAITING_FOR_EVIDENCE: ['Awaiting evidence', 'waiting'],
      STALE: ['Awaiting refresh', 'waiting']
    };
    return map[value] || ['Open', 'waiting'];
  }

  function qualityView(raw) {
    const value = String(raw || '').toUpperCase();
    if (value === 'DEGRADED') return {
      label: 'LIMITED COVERAGE',
      title: 'The official weekly package has limited evidence coverage. Unavailable inputs stay unpublished rather than being inferred.'
    };
    if (['PASS', 'READY', 'COMPLETE', 'OK'].includes(value)) return {
      label: 'FULL COVERAGE',
      title: 'The official weekly package passed its current coverage state.'
    };
    return { label: 'OFFICIAL MAP', title: 'Official frozen Cycle Navigator state.' };
  }

  function readableTime(value) {
    const date = new Date(String(value || ''));
    if (!Number.isFinite(date.getTime())) return 'awaiting fresh evidence';
    return date.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' });
  }

  function renderQuality(snapshot) {
    const pill = $('qualityPill');
    if (!pill) return;
    const view = qualityView(snapshot?.package?.status || snapshot?.pointer?.status);
    if (pill.textContent !== view.label) pill.textContent = view.label;
    pill.title = view.title;
    pill.setAttribute('aria-label', `${view.label}. ${view.title}`);
  }

  function renderTests(live) {
    const root = $('livePrecisionTests');
    if (!root) return;
    const tests = Array.isArray(live?.tests) ? live.tests : [];
    if (!tests.length) {
      root.innerHTML = '<div class="live-empty">Current frozen tests are awaiting the immutable precision freeze.</div>';
      return;
    }
    root.innerHTML = tests.map((test) => {
      const [label, cls] = statusView(test.status);
      return `<article class="live-test ${esc(cls)}">
        <div class="live-test-head"><strong>${esc(test.label || test.family || 'Current test')}</strong><span class="live-test-status">${esc(label)}</span></div>
        <p>${esc(test.evidence || 'Evidence remains open.')}</p>
      </article>`;
    }).join('');
  }

  function render(snapshot) {
    const live = snapshot?.calibration?.current?.live_precision || null;
    renderQuality(snapshot);
    const panel = $('livePrecisionPanel');
    if (!panel) return;

    if (!live) {
      if ($('livePrecisionTitle')) $('livePrecisionTitle').textContent = 'Awaiting current evidence';
      if ($('livePrecisionCount')) $('livePrecisionCount').textContent = '—';
      if ($('livePrecisionCountLabel')) $('livePrecisionCountLabel').textContent = 'observation unavailable';
      return;
    }

    const issue = live.issue_number ?? snapshot?.package?.issue_number ?? '—';
    const observed = Number(live.observed_count || 0);
    const total = Number(live.total_count || 0);
    const direct = Number(live.direct_check_count || 0);
    const limited = live.package_coverage === 'LIMITED_COVERAGE';

    if ($('livePrecisionTitle')) $('livePrecisionTitle').textContent = `CN #${issue} · current evidence check`;
    if ($('livePrecisionCount')) $('livePrecisionCount').textContent = `${observed}/${total || '—'}`;
    if ($('livePrecisionCountLabel')) $('livePrecisionCountLabel').textContent = 'observable now';
    if ($('livePrecisionMethod')) $('livePrecisionMethod').textContent = 'Observation only · no synthetic current-week percentage';
    if ($('livePrecisionAsOf')) $('livePrecisionAsOf').textContent = `Evidence as of ${readableTime(live.as_of_utc || live.generated_at_utc)}`;
    if ($('livePrecisionCoverage')) $('livePrecisionCoverage').textContent = limited
      ? 'Official weekly package: limited coverage. Missing inputs remain unpublished.'
      : 'Official weekly package: standard coverage.';
    if ($('livePrecisionAuthority')) $('livePrecisionAuthority').textContent = direct
      ? `${direct} direct market check${direct === 1 ? '' : 's'} · remaining observations stay open until the week closes.`
      : 'No direct current-week check is safely evaluable yet; frozen calls remain open.';
    renderTests(live);

    const shortcutNote = $('shortcutScoreNote');
    if (shortcutNote && !shortcutNote.dataset.liveAugmented) {
      const directTest = (live.tests || []).find((test) => ['CURRENTLY_ON_TRACK', 'CURRENTLY_OFF_TRACK'].includes(test.status));
      const suffix = directTest
        ? ` Live check: ${directTest.label} ${statusView(directTest.status)[0].toLowerCase()} · ${observed}/${total} observable.`
        : ` Live check: ${observed}/${total || '—'} observable · no synthetic score.`;
      shortcutNote.textContent = `${shortcutNote.textContent}${suffix}`;
      shortcutNote.dataset.liveAugmented = 'true';
    }
  }

  async function load() {
    try {
      const response = await fetch(`${DATA_URL}?live-precision=${Date.now()}`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`Live precision snapshot HTTP ${response.status}`);
      const snapshot = await response.json();
      render(snapshot);

      const pill = $('qualityPill');
      if (pill) {
        const expected = qualityView(snapshot?.package?.status || snapshot?.pointer?.status).label;
        const observer = new MutationObserver(() => {
          if (pill.textContent !== expected) renderQuality(snapshot);
        });
        observer.observe(pill, { childList: true, characterData: true, subtree: true });
        setTimeout(() => observer.disconnect(), 10000);
      }
    } catch (error) {
      console.warn('Live precision observation unavailable', error);
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load, { once: true });
  else load();
  setInterval(load, 5 * 60 * 1000);
})();
