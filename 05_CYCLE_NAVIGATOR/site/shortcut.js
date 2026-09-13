(() => {
  'use strict';
  const DATA_URL = './data/latest.json';
  const $ = (id) => document.getElementById(id);
  const esc = (value) => String(value ?? '')
    .replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;').replaceAll("'", '&#039;');

  function cleanPhase(text) {
    return String(text || '')
      .replace(/^\d+\.\s*/, '')
      .replace(/\s[—–-]\s(ACTIVE WATCH|ACTIVE|UNCONFIRMED|INACTIVE|PAUSED).*$/i, '')
      .trim();
  }

  function phaseState(text) {
    const match = String(text || '').match(/(?:—|-)\s*(ACTIVE WATCH|ACTIVE|UNCONFIRMED|INACTIVE|PAUSED)/i);
    return match ? match[1].toUpperCase() : 'UNKNOWN';
  }

  function firstSentence(text) {
    const source = String(text || '').trim();
    if (!source) return '';
    const match = source.match(/^.*?[.!?](?:\s|$)/);
    return (match ? match[0] : source).trim();
  }

  function sentenceMatching(text, pattern) {
    return String(text || '').split(/(?<=[.!?])\s+/).map((part) => part.trim()).find((part) => pattern.test(part)) || '';
  }

  function latestVerified(track) {
    return (Array.isArray(track) ? track : [])
      .filter((row) => String(row?.score_status || '').toUpperCase() === 'REPRODUCIBLE' && Number.isFinite(Number(row?.structural_score)))
      .at(-1) || null;
  }

  function conciseNow(pkg) {
    const state = String(pkg?.market_state || '');
    if (/volatile transition/i.test(state)) return 'VOLATILE TRANSITION';
    if (/broad altseason/i.test(state) && /active/i.test(state)) return 'BROAD ALTSEASON';
    const first = firstSentence(state).replace(/[.!?]+$/, '');
    return first ? first.slice(0, 64).toUpperCase() : 'OFFICIAL STATE';
  }

  function weekLabel(text) {
    const source = String(text || '');
    if (/volatile transition/i.test(source) && /selective/i.test(source)) return 'VOLATILE / SELECTIVE';
    if (/broad alt/i.test(source) && /inactive|not active|unconfirmed/i.test(source)) return 'NO BROAD EXPANSION';
    return '7-DAY BASE CASE';
  }

  function forwardLabel(text) {
    const source = String(text || '');
    if (/ETH/i.test(source) && /large-cap/i.test(source)) return 'ETH → LARGE-CAP TEST';
    if (/broad alt/i.test(source) && /expansion/i.test(source)) return 'BROADENING WATCH';
    return 'FORWARD VIEW';
  }

  function renderShortcut(data) {
    const pkg = data?.package || {};
    const pointer = data?.pointer || {};
    const track = data?.calibration?.track_record?.rows || [];
    const phases = Array.isArray(pkg.altseason_countdown) ? pkg.altseason_countdown : [];
    const active = [...phases].reverse().find((item) => ['ACTIVE', 'ACTIVE WATCH'].includes(phaseState(item.phase)));
    const next = phases.find((item) => phaseState(item.phase) === 'UNCONFIRMED') || phases.find((item) => phaseState(item.phase) === 'ACTIVE WATCH');
    const verified = latestVerified(track);
    const openCount = Number(data?.calibration?.current?.frozen_test_count ?? pkg?.forecast_freeze?.structural_calls?.length ?? 0);

    if ($('shortcutNow')) $('shortcutNow').textContent = conciseNow(pkg);
    if ($('shortcutNowNote')) $('shortcutNowNote').textContent = active ? `${cleanPhase(active.phase)} · ${phaseState(active.phase)}` : firstSentence(pkg.market_state) || 'Official state unavailable.';
    if ($('shortcutDays')) $('shortcutDays').textContent = 'NOT PUBLISHED';
    if ($('shortcutDaysNote')) $('shortcutDaysNote').textContent = 'No OFFICIAL 24–72h feed yet. LIVE prices are context only and never create a short-horizon call.';
    if ($('shortcutWeek')) $('shortcutWeek').textContent = weekLabel(pkg.base_case_this_week);
    if ($('shortcutWeekNote')) $('shortcutWeekNote').textContent = firstSentence(pkg.base_case_this_week) || 'No 7-day base case published.';
    if ($('shortcutForward')) $('shortcutForward').textContent = forwardLabel(pkg.base_case_2_3_weeks);
    if ($('shortcutForwardNote')) $('shortcutForwardNote').textContent = firstSentence(pkg.base_case_2_3_weeks) || 'No 2–3 week view published.';
    if ($('shortcutGate')) $('shortcutGate').textContent = next?.window ? String(next.window).toUpperCase() : 'CONDITIONAL';
    if ($('shortcutGateNote')) $('shortcutGateNote').textContent = next ? cleanPhase(next.phase) : 'No publishable next-stage window.';
    if ($('shortcutScore')) $('shortcutScore').textContent = verified ? `${Math.round(Number(verified.structural_score))}%` : 'N/A';
    if ($('shortcutScoreNote')) $('shortcutScoreNote').textContent = verified
      ? `Last verified: CN #${verified.issue_scored}. Current CN #${pkg.issue_number ?? pointer.issue_number ?? '—'}: ${openCount || 'all'} frozen tests still open.`
      : `No reproducible numerical score yet. Current CN #${pkg.issue_number ?? pointer.issue_number ?? '—'} remains open.`;

    const unlock = sentenceMatching(pkg.base_case_2_3_weeks, /requires|only if|progress|transmission/i)
      || pkg?.forecast_freeze?.breadth_condition
      || 'The next phase requires the OFFICIAL confirmation conditions to close.';
    const ifNot = sentenceMatching(pkg.base_case_2_3_weeks, /without|if not|otherwise/i)
      || 'Until confirmation closes, the current OFFICIAL state remains the working map.';
    if ($('viewUnlock')) $('viewUnlock').textContent = unlock;
    if ($('viewIfNot')) $('viewIfNot').textContent = ifNot;
  }

  function renderManiaPath(data) {
    const pkg = data?.package || {};
    const history = data?.public_history || {};
    const root = $('maniaPath');
    if (!root) return;
    const phases = Array.isArray(pkg.altseason_countdown) ? pkg.altseason_countdown : [];
    const official = phases.map((item, index) => ({ index: index + 1, title: cleanPhase(item.phase), state: phaseState(item.phase), window: item.window || 'No calendar window', source: 'OFFICIAL CN' }));
    const activeIndexes = official.map((item, index) => ['ACTIVE', 'ACTIVE WATCH'].includes(item.state) ? index : -1).filter((index) => index >= 0);
    const currentIndex = activeIndexes.length ? Math.max(...activeIndexes) : 0;
    const current = official[currentIndex] || official[0] || null;
    const next = official.find((item) => item.state === 'UNCONFIRMED') || official.find((item, index) => index > currentIndex && item.state !== 'ACTIVE');
    const gatesToMania = Math.max(1, official.length - currentIndex);
    const historical = history?.historical_mania_reference;
    const maniaWindow = pkg.altseason_mania_window || 'Only after broad altseason credibly confirms';
    const maniaNote = historical?.window ? `${maniaWindow}. Historical CN #${historical.issue}: ${historical.window} — superseded, not a current ETA.` : `${maniaWindow}. No current calendar ETA.`;
    const path = [
      ...official,
      { index: official.length + 1, title: 'Mania phase', state: 'LOCKED', window: maniaNote, source: 'SEQUENCE REFERENCE' },
      { index: official.length + 2, title: 'Distribution / exit window', state: 'LOCKED', window: 'Only after Mania matures. No current calendar ETA or automatic exit signal.', source: 'SEQUENCE REFERENCE' }
    ];

    if ($('maniaCurrent')) $('maniaCurrent').textContent = current?.title || 'Awaiting official phase';
    if ($('maniaCurrentNote')) $('maniaCurrentNote').textContent = current ? `${current.state} · ${current.window}` : 'No official phase available.';
    if ($('maniaNext')) $('maniaNext').textContent = next?.title || 'Confirmation gated';
    if ($('maniaNextNote')) $('maniaNextNote').textContent = next?.window || 'No calendar ETA.';
    if ($('maniaGates')) $('maniaGates').textContent = `${gatesToMania} GATES`;
    if ($('maniaGatesNote')) $('maniaGatesNote').textContent = 'Sequence distance, not a time forecast. Mania calendar ETA remains locked until broad altseason confirms.';
    root.innerHTML = path.map((item) => `<div class="mania-stage" data-state="${esc(item.state)}"><div class="mania-stage-index">${item.index}</div><div><div class="mania-stage-title">${esc(item.title)}<span class="mania-source">${esc(item.source)}</span></div><div class="mania-stage-window">${esc(item.window)}</div></div><div class="mania-stage-state">${esc(item.state)}</div></div>`).join('');
  }

  async function load() {
    try {
      const response = await fetch(`${DATA_URL}?shortcut=${Date.now()}`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`Shortcut snapshot HTTP ${response.status}`);
      const data = await response.json();
      renderShortcut(data);
      renderManiaPath(data);
    } catch (error) {
      console.warn('Cycle Navigator shortcut layer unavailable', error);
    }
  }

  load();
  setInterval(load, 5 * 60 * 1000);
})();
