/* Cycle Navigator — source-bound interactive preview. Read-only. No signal ownership. */
'use strict';

const SOURCE_FILE = './seed.json';
const routes = ['overblik', 'kompas', 'dokumentation'];
const $ = (id) => document.getElementById(id);
let data = null;
let selectedAsset = 'BTC';
let toastTimer = null;

const clean = (s, fallback = 'Ukendt') => typeof s === 'string' && s.trim() ? s.trim() : fallback;
const safeNumber = (n) => typeof n === 'number' && Number.isFinite(n);
const formatPct = (n) => safeNumber(n) ? n.toLocaleString('da-DK', { minimumFractionDigits: 0, maximumFractionDigits: 2 }) + ' %' : 'Ikke scoret';
const formatUSD = (n) => safeNumber(n) ? '$' + n.toLocaleString('da-DK', { maximumFractionDigits: 2 }) : '—';
const setText = (id, value) => { const el = $(id); if (el) el.textContent = String(value ?? '—'); };
const make = (tag, className, text) => {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (text != null) el.textContent = String(text);
  return el;
};
const clear = (el) => { if (el) el.replaceChildren(); };
const showToast = (text) => {
  const el = $('toast');
  if (!el) return;
  el.textContent = text;
  el.classList.add('show');
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('show'), 2800);
};

function navigate(route, { updateHash = true } = {}) {
  if (!routes.includes(route)) return;
  for (const page of document.querySelectorAll('.page')) {
    const active = page.id === 'page-' + route;
    page.classList.toggle('is-active', active);
    page.hidden = !active;
  }
  for (const button of document.querySelectorAll('[data-route]')) {
    const active = button.dataset.route === route;
    button.classList.toggle('is-active', active);
    if (active) button.setAttribute('aria-current', 'page');
    else button.removeAttribute('aria-current');
  }
  if (updateHash && location.hash !== '#' + route) {
    history.replaceState(null, '', '#' + route);
  }
  window.scrollTo({ top: 0, behavior: 'instant' });
  document.title = (route === 'overblik' ? 'Overblik' : route === 'kompas' ? 'Kompas' : 'Resultater') + ' — Cycle Navigator';
}

function bindNavigation() {
  document.querySelectorAll('[data-route]').forEach((button) => {
    button.addEventListener('click', () => navigate(button.dataset.route));
  });
  document.querySelectorAll('[data-go]').forEach((button) => {
    button.addEventListener('click', () => navigate(button.dataset.go));
  });
  window.addEventListener('hashchange', () => {
    const route = location.hash.slice(1);
    if (routes.includes(route)) navigate(route, { updateHash: false });
  });
  const initial = location.hash.slice(1);
  if (routes.includes(initial)) navigate(initial, { updateHash: false });
}

function bindPanels() {
  $('expand-cycle')?.addEventListener('click', (e) => {
    const details = $('cycle-details');
    details.hidden = !details.hidden;
    e.currentTarget.querySelector('span').textContent = details.hidden ? '＋' : '−';
  });
  $('interpret-more')?.addEventListener('click', (e) => {
    const details = $('interpret-details');
    details.hidden = !details.hidden;
    e.currentTarget.setAttribute('aria-expanded', String(!details.hidden));
    e.currentTarget.querySelector('span').textContent = details.hidden ? '＋' : '−';
  });
  $('risk-more')?.addEventListener('click', (e) => {
    const details = $('risk-details');
    details.hidden = !details.hidden;
    e.currentTarget.setAttribute('aria-expanded', String(!details.hidden));
    e.currentTarget.querySelector('span').textContent = details.hidden ? '＋' : '−';
  });
  $('history-toggle')?.addEventListener('click', (e) => {
    const details = $('history-full');
    details.hidden = !details.hidden;
    e.currentTarget.setAttribute('aria-expanded', String(!details.hidden));
    e.currentTarget.querySelector('span').textContent = details.hidden ? '＋' : '−';
  });
  document.querySelectorAll('[data-asset]').forEach((button) => button.addEventListener('click', () => {
    selectedAsset = button.dataset.asset;
    document.querySelectorAll('[data-asset]').forEach((b) => {
      const active = b.dataset.asset === selectedAsset;
      b.classList.toggle('selected', active);
      b.setAttribute('aria-pressed', String(active));
    });
    renderRangeChart();
  }));

  const dialog = $('source-dialog');
  const sourceButton = $('source-button');
  const closeDialog = () => {
    dialog.hidden = true;
    sourceButton.setAttribute('aria-expanded', 'false');
    sourceButton.focus();
  };
  sourceButton?.addEventListener('click', () => {
    dialog.hidden = false;
    sourceButton.setAttribute('aria-expanded', 'true');
    $('close-source')?.focus();
  });
  $('close-source')?.addEventListener('click', closeDialog);
  dialog?.addEventListener('click', (event) => { if (event.target === dialog) closeDialog(); });
  window.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !dialog.hidden) closeDialog();
  });
  $('copy-verification-prompt')?.addEventListener('click', async () => {
    const text = [
      'Kontrollér uafhængigt Cycle Navigator offentlige scores i https://github.com/Donh91/CycleNavigator-scores.',
      'Start med README og PROTOCOL. Sammenkæd offentlig CN-udgave, prognoseuge og oprindeligt frosset forecast.',
      'Bekræft, at prognosen faktisk eksisterede før udfaldsperioden. Kontrollér kildehash, scorerens metodeversion, faktiske observationer og dækningsgrad.',
      'Behandl Price Range, legacy Market/Structure, frozen-claim scores og Bull/Bear som forskellige målinger.',
      'Genberegn scoren, når kilderne muliggør det. Kontrollér uafhængig tidsstempling og immutable release attestation.',
      'Skeln mellem VERIFIED, LEGACY_ATTESTED, PROVISIONAL og UNVERIFIABLE. Ingen retrospektiv opgradering til ex-ante bevis.',
      'Rapportér både støtte og svagheder. X er distributionskanal, ikke krævet sandhedsautoritet.'
    ].join('\n');
    try {
      await navigator.clipboard.writeText(text);
      showToast('AI-auditprompt kopieret');
    } catch {
      showToast('Kopiering er ikke understøttet her. Åbn score-repoet.');
    }
  });
}

function getTrustedSeed(raw) {
  if (!raw || raw.contract !== 'CN_VNEXT_PREVIEW_SOURCE_BUNDLE_v1') throw new Error('Unexpected preview source contract');
  if (raw.source_status !== 'POINT_IN_TIME_PREVIEW_ARCHIVE_NOT_LIVE') throw new Error('The data source is not a certified point-in-time preview');
  const { weekly, compass, completed_score: score, history } = raw;
  if (!weekly || !compass || !score || !history || !Array.isArray(history.records)) throw new Error('Incomplete source');
  if (weekly.public_issue_number !== 28 || weekly.forecast_week !== '2026-W41') throw new Error('Unexpected frozen forecast identity');
  if (score.public_issue_number !== 27 || score.forecast_week !== '2026-W40' || score.market_structure_precision !== null || score.combined_score !== null) throw new Error('Invalid scoring-era contract');
  if (compass.data_status !== 'OK' || !compass.compass_id || !compass.issued_at_utc) throw new Error('Invalid Compass point-in-time source');
  if (history.contract !== 'CN_PUBLIC_HISTORY_SCOREBOARD_V2' || history.policy?.cross_era_aggregate !== false ||
      history.records.length !== 27 || history.records.some((item, i) => item.cn !== i + 1)) throw new Error('Historical score records failed the original-series check');
  return raw;
}

function directionView(code) {
  const raw = String(code ?? '').toUpperCase();
  if (raw === 'UP' || raw === 'BULLISH') return { text: '↗ BULLISH', className: 'dir-up' };
  if (raw === 'DOWN' || raw === 'BEARISH') return { text: '↘ BEARISH', className: 'dir-mixed' };
  if (raw === 'MIXED' || raw === 'SIDEWAYS' || raw === 'NEUTRAL') return { text: '↔ MIXED', className: 'dir-mixed' };
  return { text: '—', className: 'dir-none' };
}
function actionView(code) {
  const raw = String(code ?? '').toUpperCase();
  if (raw === 'HOLD_WAIT') return { text: 'HOLD / AFVENT', className: 'hold' };
  if (raw === 'HOLD') return { text: 'HOLD', className: 'hold' };
  if (raw === 'WAIT') return { text: 'AFVENT', className: '' };
  if (raw === 'HARD_WAIT') return { text: 'HARD WAIT', className: 'hard' };
  if (raw === 'BUY' || raw === 'BUY_DIP') return { text: raw.replace('_', ' '), className: 'hold' };
  if (raw === 'UNAVAILABLE' || raw === 'UNKNOWN') return { text: 'UTILGÆNGELIG', className: '' };
  return { text: raw || 'UKENDT', className: '' };
}
function addTag(tr, code) {
  const cell = make('td');
  const action = actionView(code);
  const tag = make('span', 'action-tag ' + action.className, action.text);
  cell.append(tag); tr.append(cell);
}
function addTd(tr, text, className) { tr.append(make('td', className, text)); }
function strongText(parent, label, text) {
  const line = make('p');
  line.append(make('strong', null, label + ': '), document.createTextNode(text));
  parent.append(line);
}

function paintTop(d) {
  const { weekly: w, compass: c } = d;
  setText('header-issue', 'CN #' + w.public_issue_number + ' · ' + w.forecast_week);
  setText('edition-number', 'NO. ' + w.public_issue_number);
  setText('hero-horizon', 'NÆSTE 12 TIMER');
  setText('source-health', 'WEEKLY: ' + String(w.status ?? 'UNAVAILABLE'));
  setText('source-time', 'KILDESNAPSHOT · ' + new Intl.DateTimeFormat('da-DK', {
    day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC'
  }).format(new Date(c.issued_at_utc)));
  const direction = directionView(c.horizons?.NEXT_12H?.expected_direction).text;
  const next = directionView(c.horizons?.NEXT_1_3D?.expected_direction).text;
  setText('hero-now', direction + ' · 12T');
  setText('hero-forward', next + ' · 1–3D');
  setText('instrument-action', actionView(c.action_now).text);
  setText('instrument-long', directionView(c.horizons?.CYCLE_ALTCOINS_3_8W?.expected_direction).text === '—' ? 'UNCONFIRMED' : directionView(c.horizons?.CYCLE_ALTCOINS_3_8W?.expected_direction).text);
  setText('overview-action', actionView(c.action_now).text);
  setText('overview-action-note', clean(c.market_now?.summary, 'Ingen detaljer fra Official Compass.'));
  setText('overview-risk', clean(c.protection_tracker?.pullback_risk_state, 'UNAVAILABLE'));
  setText('overview-risk-desc', c.protection_tracker?.pullback_risk_state === 'BUILDING' ?
    'Retest-watch under opbygning. Dybde og varighed er ikke kvantificeret. Ikke en SELL-instruktion.' :
    clean(c.protection_tracker?.pullback_class, 'Ingen verificeret risikoklasse.'));
  setText('compass-updated', 'OFFICIAL SNAPSHOT · ' + c.issued_at_utc.slice(0, 16).replace('T', ' ') + ' UTC');
  setText('compass-primary-action', actionView(c.action_now).text);
  setText('compass-primary-direction', direction);
  setText('compass-primary-copy', clean(c.market_now?.summary));
}

function paintCompass(d) {
  const { compass: c } = d;
  const horizonRows = [
    ['0–12 timer', 'NEXT_12H'], ['1–3 dage', 'NEXT_1_3D'], ['5–7 dage', 'NEXT_5_7D'],
    ['2–3 uger', 'NEXT_2_3W'], ['4–8 uger', 'CYCLE_ALTCOINS_3_8W']
  ];
  const horizonBody = $('horizon-body'); clear(horizonBody);
  horizonRows.forEach(([name, key]) => {
    const item = c.horizons?.[key];
    const tr = make('tr');
    addTd(tr, name);
    const direction = directionView(item?.expected_direction);
    addTd(tr, direction.text, direction.className);
    addTag(tr, item?.action_posture);
    horizonBody.append(tr);
  });
  const classRows = [
    ['Bitcoin', 'BTC'], ['Ethereum', 'ETH'], ['Large caps', 'LARGE_CAPS'],
    ['Mid caps', 'MID_CAPS'], ['Small caps', 'SMALL_CAPS'], ['Microcaps', 'MICROCAPS'], ['Memes', 'MEMES']
  ];
  const assetBody = $('asset-body'); clear(assetBody);
  classRows.forEach(([name, key]) => {
    const item = (c.capitalization_ladder ?? []).find((r) => r.segment === key);
    const tr = make('tr');
    addTd(tr, name);
    addTd(tr, clean(item?.status, 'UNAVAILABLE'));
    addTag(tr, item?.action);
    assetBody.append(tr);
  });

  setText('interpretation-copy', clean(c.horizons?.NEXT_1_3D?.expected_path, 'Ingen offentlig fortolkning for denne horisont.'));
  const details = $('interpret-details'); clear(details);
  strongText(details, 'Næste 12 timer', clean(c.horizons?.NEXT_12H?.expected_path));
  strongText(details, 'Næste 5–7 dage', clean(c.horizons?.NEXT_5_7D?.expected_path));
  strongText(details, 'Næste 2–3 uger', clean(c.horizons?.NEXT_2_3W?.expected_path));
  strongText(details, '4–8 uger', clean(c.horizons?.CYCLE_ALTCOINS_3_8W?.expected_path));

  const risk = c.protection_tracker ?? {};
  setText('risk-large', clean(risk.pullback_risk_state, 'UNAVAILABLE') + ' / WATCH');
  setText('risk-main-copy', clean(risk.pullback_class) + ' · ' + clean(risk.eta_window, 'Ingen pålidelig ETA'));
  setText('distribution-label', clean(risk.distribution_risk));
  setText('sell-label', clean(c.sell_assessment?.state));
  setText('reentry-label', clean(risk.reentry_state));
  const riskDetails = $('risk-details'); clear(riskDetails);
  strongText(riskDetails, 'Risikokvalitet', clean(risk.confidence_quality));
  strongText(riskDetails, 'SELL-adskillelse', clean(c.sell_assessment?.reason));
  strongText(riskDetails, 'Re-entry', clean(risk.reentry_message));
  strongText(riskDetails, 'Hvad svækker risikovurderingen', clean(risk.invalidation));
  if (Array.isArray(risk.decisive_public_drivers)) {
    const list = make('ul');
    risk.decisive_public_drivers.slice(0, 4).forEach((str) => list.append(make('li', null, str)));
    riskDetails.append(list);
  }
}

function renderRangeChart() {
  const root = $('range-visualization'); clear(root);
  const rows = data?.completed_score?.price_range_precision?.rows;
  if (!Array.isArray(rows) || !rows.length) {
    root.append(make('p', 'method-disclaimer', 'Ingen fuldførte offentlige målevinduer tilgængelige.'));
    return;
  }
  const eligible = rows.filter((r) =>
    r.asset === selectedAsset &&
    ['forecast_low', 'forecast_high', 'actual_low', 'actual_high'].every((key) => safeNumber(r[key])) &&
    r.forecast_high > r.forecast_low && r.actual_high >= r.actual_low
  );
  if (eligible.length !== 3) {
    root.append(make('p', 'method-disclaimer', 'Det frosne scorekort mangler komplette prisvinduer.'));
    return;
  }
  const min = Math.min(...eligible.map((r) => Math.min(r.actual_low, r.forecast_low)));
  const max = Math.max(...eligible.map((r) => Math.max(r.actual_high, r.forecast_high)));
  const gap = Math.max(1, max - min) * .035;
  const lo = min - gap, hi = max + gap;
  const span = hi - lo;
  const windowLabel = { day_1_2: 'Dag 1–2', day_3_4: 'Dag 3–4', day_5_7: 'Dag 5–7' };
  for (const r of eligible) {
    const line = make('div', 'range-row');
    const meta = make('div', 'range-row-label');
    meta.append(make('strong', null, windowLabel[r.window] || clean(r.window)), make('small', null, selectedAsset));
    line.append(meta);
    const track = make('div', 'range-row-track');
    const bars = [
      ['range-forecast', r.forecast_low, r.forecast_high, 'Frosset forecast: '],
      ['range-observed', r.actual_low, r.actual_high, 'Observeret lav-høj: ']
    ];
    for (const [kind, low, high, label] of bars) {
      const bar = make('div', 'range-bar ' + kind);
      bar.style.setProperty('--l', ((low - lo) / span * 100).toFixed(4) + '%');
      bar.style.setProperty('--w', ((high - low) / span * 100).toFixed(4) + '%');
      bar.setAttribute('role', 'img');
      bar.setAttribute('aria-label', label + formatUSD(low) + ' – ' + formatUSD(high));
      bar.title = label + formatUSD(low) + ' – ' + formatUSD(high);
      track.append(bar);
    }
    line.append(track, make('div', 'range-row-score', formatPct(r.score)));
    root.append(line);
  }
  const axis = make('div', 'range-axis');
  axis.append(make('span', null, formatUSD(min)), make('span', null, formatUSD(max)));
  root.append(axis);
  setText('range-method', '70% containment + 30% Jaccard · ' + selectedAsset);
}

function paintHistory(d) {
  const h = d.history.records;
  const current = h.filter((row) => row.cn >= 25 && row.cn <= 27);
  const bars = $('history-bars'); clear(bars);
  current.forEach((row) => {
    const entry = make('div', 'history-column');
    let parsed = (row.range_display || '').match(/(?:Combined\s+)?(\d{2}\.\d{1,2})/);
    const score = parsed ? Number(parsed[1]) : null;
    if (!safeNumber(score)) return;
    const head = make('div', 'history-top');
    head.append(make('strong', null, formatPct(score)), make('small', null, 'CN #' + row.cn));
    const track = make('div', 'history-bar-track');
    const fill = make('div', 'history-bar-value');
    fill.style.setProperty('--score', String(score) + '%');
    track.append(fill);
    const foot = make('div', 'history-footer', row.cn === 25 ? '2026-W38' : row.cn === 26 ? '2026-W39' : '2026-W40');
    entry.append(head, track, foot);
    bars.append(entry);
  });
  const full = $('history-full'); clear(full);
  h.forEach((r) => {
    const line = make('div', 'history-record');
    line.append(make('strong', null, 'CN #' + r.cn),
      make('span', null, (r.range_display || 'Prisinterval: ikke opgjort') + ' · ' + r.era.replaceAll('_', ' ').toLowerCase()),
      make('small', null, r.overall != null ? 'Legacy ' + r.overall + ' %' : 'Ingen samlet'));
    full.append(line);
  });
}

function paintSource(d) {
  const root = $('source-detail'); clear(root);
  strongText(root, 'Status', 'CN #' + d.weekly.public_issue_number + ' (' + d.weekly.forecast_week + ') er ' + d.weekly.status + '. Eventuelle mangler må ikke skjules af designet.');
  strongText(root, 'Official Compass', 'Kilde ID ' + d.compass.compass_id + ', offentliggjort ' + d.compass.issued_at_utc + '. Ikke en kontinuerlig live-forbindelse i previewen.');
  strongText(root, 'Score', 'CN #' + d.completed_score.public_issue_number + ' / ' + d.completed_score.forecast_week + ', Price Range ' + formatPct(d.completed_score.price_range_precision?.score) + '. Market/Structure er ikke scoret.');
  strongText(root, 'Historisk dokumentation', 'Alle 27 afsluttede scoreudgaver er bevaret, men ældre serier har andre metoder.');
  strongText(root, 'Uafhængig verificering', 'Legacy import og integritetstest er ikke det samme som immutabel release, uafhængigt tidsstempel eller dokumenteret ex-ante edge.');
}

async function initialize() {
  bindNavigation();
  bindPanels();
  try {
    const response = await fetch(SOURCE_FILE, { cache: 'no-store' });
    if (!response.ok) throw new Error('Source HTTP ' + response.status);
    const raw = await response.json();
    data = getTrustedSeed(raw);
    paintTop(data);
    paintCompass(data);
    renderRangeChart();
    paintHistory(data);
    paintSource(data);
  } catch (err) {
    console.error('Preview source validation failed:', err);
    setText('source-health', 'DATASOURCE: UNAVAILABLE');
    setText('source-time', 'Kildeintegritet ikke bekræftet');
    setText('hero-deck', 'Previewen kan ikke verificere datakilden. Ingen aktuelle markedskonklusioner kan udledes.');
    setText('hero-now', '— / UNAVAILABLE');
    setText('hero-forward', '— / UNAVAILABLE');
    setText('overview-action', 'UTILGÆNGELIG');
    setText('overview-risk', 'UTILGÆNGELIG');
    setText('compass-primary-direction', 'UKENDT');
    setText('compass-primary-action', 'UTILGÆNGELIG');
    $('horizon-body')?.replaceChildren(make('tr'));
    $('asset-body')?.replaceChildren(make('tr'));
    $('range-visualization')?.replaceChildren(make('p', 'method-disclaimer', 'Ingen verificeret kilde tilgængelig.'));
    showToast('Kildedata kunne ikke indlæses.');
  }
}

initialize();
