(() => {
  'use strict';
  const DATA_URL = './data/latest.json';
  let snapshot = null;

  const $ = (id) => document.getElementById(id);
  const esc = (value) => String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

  function cleanPhase(text) {
    return String(text || '')
      .replace(/^\d+\.\s*/, '')
      .replace(/\s[—–-]\s(ACTIVE WATCH|ACTIVE|UNCONFIRMED|INACTIVE|PAUSED).*$/i, '')
      .trim();
  }

  function phaseState(text) {
    const match = String(text || '').match(/(?:—|- )?\s*(ACTIVE WATCH|ACTIVE|UNCONFIRMED|INACTIVE|PAUSED)/i);
    return match ? match[1].toUpperCase() : 'UNKNOWN';
  }

  function parseWindowDays(text) {
    const source = String(text || '').toLowerCase().replaceAll('–', '-').replaceAll('—', '-');
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
    if (now < start) return { mode: 'countdown', value: fmtDuration(start - now), title: 'until earliest working window', note: windowText };
    if (now <= end) return { mode: 'open', value: 'WINDOW OPEN', title: parsed.max > parsed.min ? `${fmtDuration(end - now)} left in window` : 'working window active', note: windowText };
    return { mode: 'paused', value: 'AWAIT NEW CN', title: 'working window matured', note: 'No automatic promotion. The next OFFICIAL CN must confirm the phase.' };
  }

  function clockCard(label, clock, fallback) {
    const item = clock || fallback;
    return `<article class="cycle-clock" data-mode="${esc(item.mode || 'locked')}"><div class="clock-label"><span>${esc(label)}</span><i class="clock-dot"></i></div><div class="clock-value">${esc(item.value)}</div><div class="clock-title">${esc(item.title)}</div><small class="clock-note">${esc(item.note)}</small></article>`;
  }

  function actionPosture(item) {
    const segment = String(item?.segment || '').toUpperCase();
    const status = String(item?.status || '').toUpperCase();
    if (status.includes('INACTIVE')) return segment.includes('MID') ? { label: 'WAIT / PREPARE', cls: 'wait' } : { label: 'WAIT', cls: 'wait' };
    if (status.includes('SELECTIVE')) return { label: 'SELECTIVE', cls: 'active' };
    if (status.includes('LEADERSHIP') || status.includes('ATTEMPT')) return { label: 'WATCH / SELECTIVE', cls: 'active' };
    if (status.includes('ANCHOR') && status.includes('CONFLICT')) return { label: 'HOLD / NO CHASE', cls: '' };
    if (status.includes('PROTECT') || status.includes('DISTRIBUT')) return { label: 'PROTECT / DE-RISK', cls: 'protect' };
    return { label: 'WATCH', cls: '' };
  }

  function renderClocks(pkg, history) {
    const root = $('cycleClocks');
    if (!root) return;
    const stages = Array.isArray(pkg.altseason_countdown) ? pkg.altseason_countdown : [];
    const next = stages.find((item) => phaseState(item.phase) === 'UNCONFIRMED' && parseWindowDays(item.window))
      || stages.find((item) => phaseState(item.phase) === 'ACTIVE WATCH' && parseWindowDays(item.window));
    const broad = stages.find((item) => /broad altseason/i.test(String(item.phase || '')));
    const nextClock = next ? clockFor(pkg.generated_unix, next.window) : null;
    const broadClock = broad ? clockFor(pkg.generated_unix, broad.window) : null;
    const maniaClock = pkg.altseason_mania_window ? clockFor(pkg.generated_unix, pkg.altseason_mania_window) : null;
    const historical = history?.historical_mania_reference;
    root.innerHTML = [
      clockCard('Next phase', nextClock, { mode: 'locked', value: 'EVIDENCE FIRST', title: cleanPhase(next?.phase || 'Next confirmation'), note: next?.window || 'No active timed next-stage window.' }),
      clockCard('Broad altseason', broadClock, { mode: 'paused', value: 'PAUSED', title: 'No calendar ETA', note: broad?.window || 'Waiting for broad, persistent alt/BTC outperformance.' }),
      clockCard('Altseason mania', maniaClock, { mode: 'locked', value: 'LOCKED', title: 'No active mania ETA', note: historical?.window ? `Historical CN #${historical.issue}: ${historical.window}. Superseded by the current state.` : 'Only timeable after broad altseason is credibly active.' })
    ].join('');
  }

  function render(data) {
    snapshot = data;
    const pkg = data?.package || {};
    const pointer = data?.pointer || {};
    const history = data?.public_history || {};

    if ($('weekCase')) $('weekCase').textContent = pkg.base_case_this_week || 'No official weekly base case is published.';
    if ($('forwardCase')) $('forwardCase').textContent = pkg.base_case_2_3_weeks || 'No official 2–3 week base case is published.';
    renderClocks(pkg, history);

    const ladder = Array.isArray(pkg.rotation_ladder) ? pkg.rotation_ladder : [];
    if ($('actionGrid')) $('actionGrid').innerHTML = ladder.map((item) => {
      const posture = actionPosture(item);
      return `<article class="action-tile"><div class="action-tile-head"><strong>${esc(item.segment)}</strong><span class="action-posture ${esc(posture.cls)}">${esc(posture.label)}</span></div><p>${esc(item.status)}</p></article>`;
    }).join('');

    const copy23 = pkg.base_case_2_3_weeks || 'UNAVAILABLE in the current OFFICIAL issue.';
    const copy48 = pkg.base_case_4_8_weeks || pkg.compass_4_8_weeks || 'UNAVAILABLE in the current OFFICIAL issue. No longer-horizon view is invented.';
    if ($('horizon23Copy')) $('horizon23Copy').textContent = copy23;
    if ($('horizon48Copy')) $('horizon48Copy').textContent = copy48;
    if ($('horizon23Posture')) $('horizon23Posture').textContent = copy23.toUpperCase().includes('BROAD') && copy23.toUpperCase().includes('CONFIRM') ? 'Prepare for broader deployment only on confirmation' : 'Selective / prepare';
    if ($('horizon48Posture')) $('horizon48Posture').textContent = copy48.startsWith('UNAVAILABLE') ? 'UNAVAILABLE — no invented view' : 'Cycle direction / capital protection';

    const tests = Array.isArray(pkg.forecast_freeze?.structural_calls) ? pkg.forecast_freeze.structural_calls : [];
    if ($('currentScoreState')) $('currentScoreState').textContent = data?.calibration?.current?.provisional_score != null ? `${data.calibration.current.provisional_score}%` : 'SCORING IN PROGRESS';
    if ($('frozenTests')) $('frozenTests').innerHTML = tests.length ? tests.map((test, index) => `<div class="frozen-test"><span class="test-index">${index + 1}</span><span>${esc(test)}</span><span class="test-open">Open</span></div>`).join('') : '<div class="frozen-test"><span>—</span><span>No frozen tests published.</span><span class="test-open">N/A</span></div>';

    if ($('publicationStatus')) $('publicationStatus').textContent = String(pointer.publication_status || pkg.publication_status || 'UNKNOWN').replaceAll('_', ' ');
    if ($('xReadyCopy')) $('xReadyCopy').textContent = pkg.x_ready_markdown || 'No X-ready copy is bundled.';
    const latest = history?.latest_published_x;
    if ($('publishedSummary')) $('publishedSummary').textContent = latest?.issue ? `Latest confirmed X publication · CN #${latest.issue}` : 'Latest confirmed X publication';
    if ($('publishedCopy')) $('publishedCopy').textContent = latest?.text || 'No confirmed public X copy is bundled.';

    const strengths = Array.isArray(pkg.evaluation?.strengths) ? pkg.evaluation.strengths : [];
    const misses = Array.isArray(pkg.evaluation?.misses) ? pkg.evaluation.misses : [];
    if ($('strengthList')) $('strengthList').innerHTML = strengths.length ? strengths.map((item) => `<li>${esc(item)}</li>`).join('') : '<li>No scored strengths available.</li>';
    if ($('missList')) $('missList').innerHTML = misses.length ? misses.map((item) => `<li>${esc(item)}</li>`).join('') : '<li>No scored misses available.</li>';
  }

  async function load() {
    try {
      const response = await fetch(`${DATA_URL}?quiet=${Date.now()}`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`Quiet production snapshot HTTP ${response.status}`);
      render(await response.json());
    } catch (error) {
      console.warn('Quiet Precision production layer unavailable', error);
    }
  }

  load();
  setInterval(load, 5 * 60 * 1000);
  setInterval(() => {
    if (snapshot) renderClocks(snapshot.package || {}, snapshot.public_history || {});
  }, 60 * 1000);
})();
