/* Cycle Navigator — source-bound interactive preview. Read-only. No signal ownership. */
import { initializeLanguage, translateInterface, selectLanguage, currentLanguage } from './premium-i18n.js';
import { officialPullbackDisplay } from './official-pullback-eta.mjs';
import { officialPullbackStage } from './official-pullback-stage.mjs';
import { officialPullbackInvestorView } from './official-pullback-investor-view.mjs';
import { officialBullBear } from './official-bullbear.mjs';
import { officialPathView } from './official-path.mjs';
'use strict';

const SOURCE_FILE = './seed.json';
const routes = ['overblik', 'kompas', 'dokumentation'];
const $ = (id) => document.getElementById(id);
let data = null;
let selectedAsset = 'BTC';
let toastTimer = null;

const clean = (s, fallback = 'Ukendt') => typeof s === 'string' && s.trim() ? s.trim() : fallback;
const safeNumber = (n) => typeof n === 'number' && Number.isFinite(n);
function completePriceRows(score, asset) {
  const rows = score?.price_range_precision?.rows;
  if (!Array.isArray(rows)) return [];
  return rows.filter((r) =>
    r.asset === asset && ['forecast_low', 'forecast_high', 'actual_low', 'actual_high'].every((key) => safeNumber(r[key])) &&
    r.forecast_high > r.forecast_low && r.actual_high >= r.actual_low
  );
}
const formatPct = (n) => safeNumber(n) ? n.toLocaleString('da-DK', { minimumFractionDigits: 0, maximumFractionDigits: 2 }) + ' %' : 'Ikke scoret';
const formatUSD = (n) => safeNumber(n) ? '$' + n.toLocaleString(currentLanguage()==='en'?'en-US':'da-DK', { maximumFractionDigits: 2 }) : '—';
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
  for (const button of document.querySelectorAll('[data-open-path]')) {
    button.classList.remove('is-active');
    button.removeAttribute('aria-current');
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

// PATH is a discoverable deep-link within the same Overblik page. Preserve
// the existing canonical pages, score owner and source; navigation only.
function openPathGraph({ updateHash = true } = {}) {
  navigate('overblik', { updateHash: false });
  for (const button of document.querySelectorAll('[data-open-path]')) {
    button.classList.add('is-active');
    if (button.classList.contains('nav-link') || button.classList.contains('dock-link')) {
      button.setAttribute('aria-current','page');
    }
  }
  for (const button of document.querySelectorAll('[data-route="overblik"]')) {
    button.classList.remove('is-active');
    button.removeAttribute('aria-current');
  }
  if (updateHash && location.hash !== '#cn-path-week') {
    history.replaceState(null, '', '#cn-path-week');
  }
  requestAnimationFrame(() => {
    const target = document.getElementById('cn-path-week');
    if (target) target.scrollIntoView({ behavior:'instant', block:'start' });
  });
}
function bindNavigation() {
  document.querySelectorAll('[data-route]').forEach((button) => {
    button.addEventListener('click', () => navigate(button.dataset.route));
  });
  document.querySelectorAll('[data-go]').forEach((button) => {
    button.addEventListener('click', () => navigate(button.dataset.go));
  });
  document.querySelectorAll('[data-open-path]').forEach((button) => {
    button.addEventListener('click', () => openPathGraph());
  });
  window.addEventListener('hashchange', () => {
    const route = location.hash.slice(1);
    if (route === 'cn-path-week') openPathGraph({ updateHash:false });
    else if (routes.includes(route)) navigate(route, { updateHash: false });
  });
  const initial = location.hash.slice(1);
  if (initial === 'cn-path-week') openPathGraph({ updateHash:false });
  else if (routes.includes(initial)) navigate(initial, { updateHash: false });
}

// Presentation-only score reveal. No price interpolation, market prediction or scorer logic.
let rangeRevealTimers = [];
function cancelRangeReveal({ complete = true } = {}) {
  rangeRevealTimers.forEach(clearTimeout);
  rangeRevealTimers = [];
  const panel = document.querySelector('.range-compare-panel');
  if (panel && complete) panel.dataset.revealPhase = 'score';
}
function setRangeRevealPhase(phase) {
  const panel = document.querySelector('.range-compare-panel');
  if (!panel) return;
  panel.dataset.revealPhase = phase;
  for (const step of document.querySelectorAll('[data-motion-step]')) {
    step.classList.toggle('is-current', step.dataset.motionStep === phase);
  }
}
// User-visible animation is seven discrete verified UTC observations,
// never fabricated intraday interpolations.
function revealActualThrough(dayIndex) {
  const clip = $('cn-path-actual-clip-rect');
  if (!clip) return;
  const {left,right}=rangeChartGeometry();
  const width=dayIndex<0?0:(right-left)*(Math.min(6,dayIndex)/6)+24;
  clip.setAttribute('width',String(width));
  if (dayIndex < 0) setText('cn-replay-day','01 · Frosne intervalvinduer');
  else setText('cn-replay-day', (dayIndex+1)+'/7 · '+(currentLanguage()==='en'
    ?['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    :['Mandag','Tirsdag','Onsdag','Torsdag','Fredag','Lørdag','Søndag'])[dayIndex]+
    ' · '+ selectedAsset+' '+formatUSD(data.completed_score.daily_observations_w40.days[dayIndex][selectedAsset].close));
}
function playRangeComparison() {
  cancelRangeReveal();
  const available = Boolean(completeDailyHistory(data?.completed_score,selectedAsset));
  const button = $('range-replay');
  if (button) button.disabled = !available;
  if (!available) {
    setRangeRevealPhase('score');
    return;
  }
  const reduce = typeof window.matchMedia === 'function' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) {
    setRangeRevealPhase('score');
    revealActualThrough(6);
    return;
  }
  setRangeRevealPhase('frozen');
  revealActualThrough(-1);
  for (let i=0;i<7;i++) {
    rangeRevealTimers.push(setTimeout(()=>{
      setRangeRevealPhase('actual');
      revealActualThrough(i);
    }, 420+i*260));
  }
  rangeRevealTimers.push(setTimeout(()=>{
    setRangeRevealPhase('score');
    revealActualThrough(6);
    setText('cn-replay-day',currentLanguage()==='en'
      ?'Observed week · all seven verified daily closes'
      :'Faktisk uge · alle syv verificerede dagslukninger');
  },2350));
}


const overviewHorizonKeys = new Set(['NEXT_12H','NEXT_1_3D','NEXT_5_7D','NEXT_2_3W','CYCLE_ALTCOINS_3_8W']);
let overviewHorizon = 'NEXT_5_7D';
function paintOverviewSnapshot(c) {
  const da = currentLanguage() !== 'en';
  const horizon = overviewHorizonKeys.has(overviewHorizon) ? overviewHorizon : 'NEXT_5_7D';
  for (const b of document.querySelectorAll('[data-overview-horizon]')) {
    const selected = b.dataset.overviewHorizon === horizon;
    b.classList.toggle('is-selected',selected);
    b.setAttribute('aria-pressed',String(selected));
  }
  const item = c?.horizons?.[horizon], direction = directionView(item?.expected_direction).text;
  const action = actionView(item?.action_posture).text;
  const label = ({ NEXT_12H:'12T', NEXT_1_3D:'1–3D', NEXT_5_7D:'5–7D', NEXT_2_3W:'2–3U', CYCLE_ALTCOINS_3_8W:'4–8U' })[horizon];
  setText('cn-overview-horizon-state', label + ' · ' + (da?'Retning: ':'Direction: ') + direction);
  setText('cn-overview-horizon-action', (da?'Handling: ':'Action: ') + action);
  const body = $('cn-overview-market-body'); clear(body);
  const names = [['BTC','Bitcoin'],['ETH','Ethereum'],['LARGE_CAPS','Large caps'],['MID_CAPS','Mid caps'],
    ['SMALL_CAPS','Small caps'],['MICROCAPS','Microcaps'],['MEMES','Memes']];
  for (const [segment,label] of names) {
    const sourceRow = c?.capitalization_ladder?.find((row) => row.segment === segment);
    const tr = make('tr'); tr.append(make('th',null,label));
    const status = String(sourceRow?.status || 'UNAVAILABLE').toUpperCase();
    const action = String(sourceRow?.action || 'UNAVAILABLE').toUpperCase();
    const normalize = (word) => ({
      'UNAVAILABLE':da?'Utilgængelig':'Unavailable',
      'HARD_WAIT':da?'Afvent':'Wait', 'WAIT':da?'Afvent':'Wait',
      'HOLD': 'HOLD','BUY':'BUY','SELL':'SELL'
    }[word] || word);
    const stateTd=make('td');
    const dot=make('i','cn-segment-indicator');
    dot.dataset.status=status;
    dot.setAttribute('aria-hidden','true');
    stateTd.append(dot,make('span',null,normalize(status)));
    tr.append(stateTd,make('td',null,normalize(action)));body?.append(tr);
  }
}

function bindPanels() {
  document.querySelectorAll('[data-overview-horizon]').forEach((button) => button.addEventListener('click', () => {
    overviewHorizon = button.dataset.overviewHorizon;
    if (data) paintOverviewSnapshot(data.compass);
  }));
  // PATH uses one native <details>/<summary> disclosure; no custom click state.
  // Kompas explanations now use native <details>/<summary> for accessible disclosure.
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
    // The primary chart is a side-by-side comparison, not an autoplay
    // sequence. BTC/ETH changes must show BOTH lines immediately. Replay
    // starts only from the explicit user action below.
    cancelRangeReveal();
    renderRangeChart();
    setRangeRevealPhase('score');
    setText('cn-replay-day',currentLanguage()==='en'
      ?'Observed week · all seven verified daily closes'
      :'Faktisk uge · alle syv verificerede dagslukninger');
    translateInterface();
  }));
  $('range-replay')?.addEventListener('click', playRangeComparison);
  $('cn-path-week-open')?.addEventListener('click', () => openPathGraph());
  $('edge-open-comparison')?.addEventListener('click', () => {
    // The modern Edge chapter links to a genuine, older frozen comparison.
    // It is not promoted into a new scored outcome.
    if (data) playRangeComparison();
    const panel = document.querySelector('.range-compare-panel');
    if (panel) {
      const reduce = typeof window.matchMedia === 'function' &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      panel.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' });
    }
  });

  // Historical chart now lives outside the collapsed legacy archive.
  // Keep legacy disclosure independent from chart playback.
  void document.querySelector('.edge-legacy-fold');

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
    if (dialog.hidden) return;
    if (event.key === 'Escape') { closeDialog(); return; }
    if (event.key !== 'Tab') return;
    const focusable = [...dialog.querySelectorAll('button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])')]
      .filter((element) => !element.hidden && element.getAttribute('aria-hidden') !== 'true');
    if (!focusable.length) { event.preventDefault(); dialog.focus(); return; }
    const first = focusable[0], last = focusable[focusable.length - 1];
    if (event.shiftKey && (document.activeElement === first || !dialog.contains(document.activeElement))) {
      event.preventDefault(); last.focus();
    } else if (!event.shiftKey && (document.activeElement === last || !dialog.contains(document.activeElement))) {
      event.preventDefault(); first.focus();
    }
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
  if (compass.data_status !== 'OK' || compass.compass_id !== 'CMP-20261011-7d14a9ee5914' || compass.issued_at_utc !== '2026-10-11T13:15:27Z') throw new Error('Compass source does not match the archived W41 preview identity');
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
  return line;
}

// Danish editorial translations are locked to this exact archived source identity.
// If the public Compass changes, present its original source text instead.
const previewDa = {
  NEXT_12H: 'Kortfristet fortsættelse er udgangspunktet, medmindre den officielle bekræftelses- eller forværringsbetingelse ændrer status.',
  NEXT_1_3D: 'Det korte markedssignal er blandet og vurderes op imod ugens struktur. Bredere kapitalrotation skal bekræftes, før risiko kan flyttes længere ned i aktivklasserne.',
  NEXT_5_7D: 'Uge 41 begyndte med en BTC-ledet dollarstigning og uafklaret rotation. Både fortsættelse og senere retest blev vurderet som mulige. Svag relativ ETH-styrke og blandede flows begrænsede overbevisningen. Hverken distribution eller bred altseason var bekræftet.',
  NEXT_2_3W: 'Selektiv og volatil deltagelse uden bekræftet bred alt-rotation eller tydelig faldretning. BTC kan forblive relativt stærk, men ETH/BTC, 30-dages deltagelse gennem pullbacks og 90/365-dages bredde skal styrkes.',
  CYCLE_ALTCOINS_3_8W: 'Ingen evidensstøttet 4–8-ugers retning eller handletilladelse. Et betinget 21–30-dages scenarie kan ikke erstatte den manglende længere bekræftelse.'
};
function localizedHorizon(c, key) {
  const original = clean(c.horizons?.[key]?.expected_path);
  if (data?.weekly?.forecast_week === '2026-W41' &&
      c.compass_id === 'CMP-20261011-7d14a9ee5914' &&
      previewDa[key]) return previewDa[key];
  return original;
}
function localizedPulse(c) {
  if (data?.weekly?.forecast_week === '2026-W41' &&
      c.compass_id === 'CMP-20261011-7d14a9ee5914') {
    return 'BTC og ETH steg i det seneste officielle sammenligningsvindue. Retning og handletilladelse er separate signaler.';
  }
  return clean(c.market_now?.summary);
}

function paintPullbackEscalator(stage, language) {
  const ruler = $('pullback-stage-ruler');
  if (!ruler) return;
  const active = stage.status === 'SOURCE_VALID' ? stage.sourceRiskState : null;
  ruler.dataset.risk = active || 'UNAVAILABLE';
  const label = language === 'en'
    ? 'Official source risk category: ' + (active || 'unavailable') + '. Not a probability, timeline or SELL permission.'
    : 'Officiel kildebaseret risikoklasse: ' + (active || 'utilgængelig') + '. Ikke sandsynlighed, tidslinje eller SELL-tilladelse.';
  ruler.setAttribute('aria-label', label);
  for (const segment of ruler.querySelectorAll('[data-risk-stage]')) {
    segment.classList.toggle('is-current', !!active && segment.dataset.riskStage === active);
  }
}

function paintPullbackInvestorFacts(d, language) {
  const root = $('pullback-investor-facts');
  if (!root) return;
  const facts = officialPullbackInvestorView(d.compass, d.weekly, language);
  clear(root);
  for (const entry of facts.rows) {
    const div = make('div', 'pullback-fact');
    div.dataset.source = entry.source;
    div.dataset.fact = entry.id;
    div.append(make('span', null, entry.label), make('p', null, entry.value));
    root.append(div);
  }
}

function paintPullback(d, lang = 'da') {
  // Independent governed risk-state and week/ETA readback, never an in-browser
  // early warning, synthetic time forecast, or authorization to SELL.
  const p = officialPullbackDisplay(d.compass, d.weekly, lang);
  const stage = officialPullbackStage(d.compass, d.weekly, lang);
  paintPullbackEscalator(stage, lang);
  paintPullbackInvestorFacts(d, lang);
  setText('overview-risk', stage.sourceRiskState);
  setText('overview-risk-stage', stage.stageLabel);
  setText('compass-risk-stage', stage.stageLabel);
  setText('overview-risk-window', p.headline);
  setText('compass-risk-window', p.headline);
  setText('overview-risk-desc', p.note + ' · ' + stage.proximityLabel);
  setText('risk-main-copy', stage.stageLabel + ' · ' + stage.etaLabel + ' · ' + stage.proximityLabel);
  const qualityEl = $('risk-evidence-quality');
  if (qualityEl) {
    const prefix = lang === 'en' ? 'Evidence quality (not probability): ' : 'Evidenskvalitet (ikke sandsynlighed): ';
    qualityEl.replaceChildren(make('strong', null, prefix), document.createTextNode(stage.qualityLabel));
  }
  for (const id of ['overview-risk-window','compass-risk-window']) {
    const el = $(id);
    if (el) el.dataset.windowKind = p.windowKind;
  }
}

function paintPath(d, lang = 'da') {
  const view = officialPathView(d, { lang, mode:'archived' });
  const isDA = lang !== 'en';
  const route = $('path-route');
  const full = $('path-all-phases');
  const rotation = $('path-rotation-rail');
  clear(route);
  clear(full);
  clear(rotation);
  const pill = $('path-source-pill');
  if (pill) {
    pill.dataset.sourceHealth = view.source_health;
    pill.textContent = view.status === 'SOURCE_BOUND'
      ? (isDA ? 'ARKIV · IKKE LIVE' : 'ARCHIVE · NOT LIVE') + ' · ' + view.source_health
      : (isDA ? 'KILDE UTILGÆNGELIG' : 'SOURCE UNAVAILABLE');
  }
  setText('path-source-intro', view.status === 'SOURCE_BOUND'
    ? view.source_label
    : (isDA ? 'Kildeintegritet ikke verificeret. Faser kan ikke aflæses.' :
      'Source integrity not verified. Cycle stages unavailable.'));
  const current = view.current_checkpoint;
  const next = view.next_checkpoint;
  setText('path-lead', view.status === 'SOURCE_BOUND'
    ? (current ? (isDA ? 'BTC-lederskab er senest dokumenteret.' :
       'BTC leadership was last documented.') :
       (isDA ? 'Aktuel cyklusfase er ikke bekræftet.' : 'Current cycle phase is unconfirmed.'))
    : (isDA ? 'Cyklusaflæsning utilgængelig.' : 'Cycle reading unavailable.'));
  setText('path-current', current?.label || (isDA ? 'Ikke verificeret' : 'Unverified'));
  setText('path-current-context', current
    ? (isDA ? 'Afsluttet kildeuge · ikke en livefase' : 'Completed source week · not a live phase')
    : (isDA ? 'Ingen verificeret aktuel fase' : 'No confirmed current phase'));
  setText('path-next', next?.label || (isDA ? 'Ikke verificeret' : 'Unverified'));
  setText('path-next-gate', view.next_gate);
  setText('path-eta', view.phase_eta);
  setText('path-alt-status', view.status === 'SOURCE_BOUND'
    ? (isDA ? 'Altseason ikke bekræftet' : 'Altseason unconfirmed') :
      (isDA ? 'Ikke tilgængeligt' : 'Unavailable'));
  setText('path-alt-evidence', view.altseason.detail);

  for (const phase of view.concise_phases) {
    const item = make('li','path-phase');
    item.dataset.phase = phase.key;
    item.dataset.status = phase.status;
    const pin=make('span','path-pin', String(phase.index + 1).padStart(2,'0'));
    pin.setAttribute('aria-hidden','true');
    const text=make('span','path-phase-content');
    const state=phase.is_reference
      ? (isDA?'Senest dokumenteret':'Last documented')
      : phase.key === next?.key
        ? (isDA?'Næste bekræftelse mangler':'Next confirmation pending')
        : (isDA?'Ikke bekræftet':'Unconfirmed');
    text.append(make('strong',null,phase.label),make('small',null,state));
    item.append(pin,text);
    route?.append(item);
  }

  for (const phase of view.full_phases) {
    const item=make('li','path-full-phase');
    item.dataset.status=phase.status;
    const label=make('span','path-full-number',String(phase.index+1).padStart(2,'0'));
    const group=make('span','path-full-label');
    group.append(make('strong',null,phase.label),
      make('small',null, phase.is_reference
        ? (isDA?'Senest dokumenteret i arkiv':'Last documented in archive')
        : phase.status==='SOURCE_RISK_CONDITION_NOT_CYCLE_CONFIRMATION'
          ? (isDA?'Risikokontekst · ikke bekræftet cyklusfase':'Risk context · not a confirmed phase')
          : (isDA?'Betinget etape · ingen ETA':'Conditional stage · no ETA')));
    item.append(label,group);
    full?.append(item);
  }

  for (const tier of view.rotation) {
    const row=make('div','path-rotation-tier');
    row.dataset.segment=tier.key;
    row.dataset.action=tier.action;
    row.setAttribute('role','listitem');
    row.append(make('span','path-tier-label',tier.label),
      make('strong',null,tier.action === 'WAIT'
        ? (isDA ? 'AFVENT' : 'WAIT')
        : tier.action === 'UNAVAILABLE'
          ? (isDA ? 'INGEN DATA' : 'NO DATA')
          : tier.action));
    rotation?.append(row);
  }
  setText('path-gate-detail', view.status === 'SOURCE_BOUND'
    ? view.next_source_caveat + (view.source_window
        ? ' · ' + (isDA?'Betinget kildevindue: ':'Conditional source window: ') + view.source_window
        : '')
    : (isDA?'Afventer verificeret kilde':'Awaiting verified source'));
  setText('path-2-3w', view.structural_long.weeks_2_3);
  setText('path-4-8w', view.structural_long.weeks_4_8);
  setText('path-protection', view.status === 'SOURCE_BOUND'
    ? (isDA?'Pullback: ':'Pullback: ')+view.protection
      + ' · '+ (isDA?'Distribution: ':'Distribution: ')+(d.compass?.protection_tracker?.distribution_risk || 'UNKNOWN')
      + ' · '+ (isDA?'SELL: ':'SELL: ')+view.sell
      + ' · '+ (isDA?'Re-entry: ':'Re-entry: ')+view.reentry
    : (isDA?'Uverificeret':'Unverified'));
  setText('path-caveat', view.source_caveat || (isDA?'Ingen verificeret ETA':'No verified ETA'));
}


function paintSourceInstrument(c) {
  const marker = $('cn-gauge-needle');
  const action = String(c?.action_now ?? 'UNAVAILABLE').toUpperCase();
  // Only explicit governed action maps to a segment. Mixed HOLD_WAIT is
  // shown at the neutral HOLD/WAIT boundary, NEVER as new BUY permission.
  const degrees = { WAIT:-22, HARD_WAIT:-34, HOLD_WAIT:0, HOLD:21 };
  const known = c?.data_status === 'OK' && Object.prototype.hasOwnProperty.call(degrees, action);
  if (marker) {
    marker.hidden = !known;
    if (known) marker.setAttribute('transform','rotate('+degrees[action]+' 340 276)');
    marker.setAttribute('aria-hidden','true');
  }
  setText('cn-gauge-action',known?actionView(action).text:'UNAVAILABLE');
  setText('cn-gauge-direction',directionView(c?.horizons?.NEXT_12H?.expected_direction).text);
  const instrument = $('cn-instrument-svg');
  if (instrument) instrument.setAttribute('aria-label', known ?
    'Arkiveret officiel handling '+actionView(action).text+'. Retning og handletilladelse er adskilt. Illustrationen viser ingen sandsynlighed.' :
    'Ingen understøttet nåleposition. Handletilladelse ikke verificeret.');
}

function paintTop(d) {
  const { weekly: w, compass: c } = d;
  setText('header-issue', 'CN #' + w.public_issue_number + ' · ' + w.forecast_week);
  setText('edition-number', 'NO. ' + w.public_issue_number);
  setText('hero-horizon', 'NÆSTE 12 TIMER');
  setText('source-health', 'WEEKLY: ' + String(w.status ?? 'UNAVAILABLE'));
  setText('source-time', 'KILDEFAST SNAPSHOT · ' + c.issued_at_utc.slice(0, 16).replace('T', ' ') + ' UTC');
  const direction = directionView(c.horizons?.NEXT_12H?.expected_direction).text;
  const next = directionView(c.horizons?.NEXT_1_3D?.expected_direction).text;
  setText('hero-now', direction + ' · 12T');
  setText('hero-forward', next + ' · 1–3D');
  const currentDirection = String(c.horizons?.NEXT_12H?.expected_direction || 'UNAVAILABLE').toUpperCase();
  if ($('hero-now')) $('hero-now').dataset.direction = currentDirection;
  setText('hero-action-summary', actionView(c.action_now).text);
  paintSourceInstrument(c);
  paintOverviewSnapshot(c);
  setText('hero-deck', localizedPulse(c));
  paintPullback(d, currentLanguage());
  setText('compass-updated', 'KILDEFAST SNAPSHOT · ' + c.issued_at_utc.slice(0, 16).replace('T', ' ') + ' UTC');
  setText('compass-primary-action', actionView(c.action_now).text);
  setText('compass-primary-direction', direction);
  const riskState = clean(c.protection_tracker?.pullback_risk_state, 'UNAVAILABLE');
  const sellState = clean(c.sell_assessment?.state, 'UNAVAILABLE');
  setText('compass-risk-inline', riskState);
  setText('compass-sell-inline', sellState);
  setText('compass-distribution-inline', clean(c.protection_tracker?.distribution_risk, 'UNKNOWN'));
  if ($('compass-risk-inline')) $('compass-risk-inline').dataset.state = String(riskState).toUpperCase();
  if ($('compass-sell-inline')) $('compass-sell-inline').dataset.state = String(sellState).toUpperCase();
}

// Official Market Weather display only. Never infer Bull/Bear from a UI
// direction, risk warnings, price action, or any browser-side estimate.
function paintBullBear(c) {
  const main = officialBullBear(c, '1_3d');
  const panel = $('compass-bullbear');
  setText('bullbear-bull', main?.bull ?? '—');
  setText('bullbear-bear', main?.bear ?? '—');
  setText('bullbear-bias', main?.bias ?? 'UTILGÆNGELIG');
  if (panel) {
    panel.dataset.state = main?.bias || 'UNAVAILABLE';
    // Static translated group label + visible Bull/Bear values remain accessible.
    // Never mutate language-dependent aria copy from a market data refresh.
  }
  const meter = $('bullbear-track');
  if (meter) meter.hidden = !main;
  for (const [key, value] of [['bullbear-bear-fill', main?.bear], ['bullbear-bull-fill', main?.bull]]) {
    const segment = $(key);
    if (segment) segment.style.width = Number.isInteger(value) ? value * 10 + '%' : '0%';
  }
  const extra = $('bullbear-other-horizons');
  clear(extra);
  for (const [key, name] of [['5_7d', 'Bull/Bear · 5–7 dage'], ['2_3w', 'Bull/Bear · 2–3 uger']]) {
    const row = officialBullBear(c, key);
    strongText(extra, name, row ?
      'BULL ' + row.bull + ' / BEAR ' + row.bear + ' · ' + row.bias :
      'UTILGÆNGELIG');
  }
}

function paintCompass(d) {
  const { compass: c } = d;
  paintBullBear(c);
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

  setText('interpretation-copy', localizedHorizon(c, 'NEXT_1_3D'));
  const details = $('interpret-details'); clear(details);
  strongText(details, 'Næste 12 timer', localizedHorizon(c, 'NEXT_12H'));
  strongText(details, 'Næste 5–7 dage', localizedHorizon(c, 'NEXT_5_7D'));
  strongText(details, 'Næste 2–3 uger', localizedHorizon(c, 'NEXT_2_3W'));
  strongText(details, '4–8 uger', localizedHorizon(c, 'CYCLE_ALTCOINS_3_8W'));

  const risk = c.protection_tracker ?? {};
  setText('risk-large', clean(risk.pullback_risk_state, 'UNAVAILABLE'));
  const stage = officialPullbackStage(c, d.weekly, currentLanguage());
  setText('risk-main-copy', stage.stageLabel + ' · ' + stage.etaLabel + ' · ' + stage.proximityLabel);
  setText('distribution-label', clean(risk.distribution_risk));
  setText('sell-label', clean(c.sell_assessment?.state));
  setText('reentry-label', clean(risk.reentry_state));
  const riskDetails = $('risk-details'); clear(riskDetails);
  strongText(riskDetails, 'Evidenskvalitet (ikke sandsynlighed)', stage.qualityLabel).id = 'risk-evidence-quality';
  strongText(riskDetails, 'SELL-adskillelse', clean(c.sell_assessment?.reason));
  strongText(riskDetails, 'Re-entry', clean(risk.reentry_message));
  strongText(riskDetails, 'Hvad svækker risikovurderingen', clean(risk.invalidation));
  if (Array.isArray(risk.decisive_public_drivers)) {
    const list = make('ul');
    risk.decisive_public_drivers.slice(0, 4).forEach((str) => list.append(make('li', null, str)));
    riskDetails.append(list);
  }
}


/*
 * Archived W40 research chart. Data owner: original frozen 3-window CN27
 * scorecard + independently captured 168 hourly OHLC (UTC). Daily ACTUAL
 * close is observed. Forecast exists ONLY for 1-2,3-4,5-7 day windows.
 * No derived day-level forecasts; no false daily probability or rescore.
 */
function completeDailyHistory(score, asset) {
  const pack = score?.daily_observations_w40;
  const rows = completePriceRows(score, asset);
  if (!pack || pack.contract !== 'CN_W40_OBSERVED_DAILY_OHLC_READBACK_v1' ||
      pack.observed_hours !== 168 || pack.basis !== 'UTC_ISO_WEEK' ||
      !Array.isArray(pack.days) || pack.days.length !== 7 || rows.length !== 3 ||
      !['BTC', 'ETH'].includes(asset)) return null;
  const expected = ['2026-09-28','2026-09-29','2026-09-30','2026-10-01','2026-10-02','2026-10-03','2026-10-04'];
  const order = ['day_1_2','day_3_4','day_5_7'];
  if (rows.some((r,i) => r.window !== order[i])) return null;
  for (let i = 0; i < 7; i++) {
    const day = pack.days[i], point = day?.[asset];
    if (day?.date !== expected[i] || day.observed_hours !== 24 ||
        !point || ![point.low,point.high,point.close].every((n) => safeNumber(n) && n > 0) ||
        point.high < point.low || point.close < point.low || point.close > point.high) return null;
  }
  for (const [index, start, end] of [[0,0,2],[1,2,4],[2,4,7]]) {
    const observed = pack.days.slice(start,end).map((d) => d[asset]);
    const low = Math.min(...observed.map((d) => d.low));
    const high = Math.max(...observed.map((d) => d.high));
    if (Math.abs(rows[index].actual_low-low) > .011 ||
        Math.abs(rows[index].actual_high-high) > .011) return null;
  }
  return { days: pack.days, windows: rows };
}

const SVG_NS = 'http://www.w3.org/2000/svg';
function chartElement(tag, attributes = {}, content) {
  const node = document.createElementNS(SVG_NS, tag);
  for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, String(value));
  if (content != null) node.textContent = String(content);
  return node;
}
// Shape-preserving Hermite handles. The rendering is a guide connecting
// observed DAILY CLOSES; it never claims to reproduce intraday ticks.
function monotoneClosePath(points) {
  if (points.length < 2) return '';
  if (points.some((p,i) => !Number.isFinite(p.x) || !Number.isFinite(p.y) ||
    (i > 0 && p.x === points[i-1].x) ||
    (i > 1 && (p.x-points[i-1].x)*(points[i-1].x-points[i-2].x) <= 0))) return '';
  // A closed corridor needs the upper curve left-to-right AND the lower
  // curve right-to-left. Both monotonic x directions must be supported.
  // Fritsch-Carlson / PCHIP shape-preserving tangents for UNEVEN x-spacings.
  // Prevent spurious peaks when the frozen source has only 3 window centers.
  const h=points.slice(1).map((p,i)=>p.x-points[i].x);
  const d=h.map((width,i)=>(points[i+1].y-points[i].y)/width);
  const m=points.map((_,i)=>{
    if (i===0 || i===points.length-1) return 0;
    if (d[i-1]===0 || d[i]===0 || d[i-1]*d[i]<0) return 0;
    const w1=2*h[i]+h[i-1],w2=h[i]+2*h[i-1];
    return (w1+w2)/(w1/d[i-1]+w2/d[i]);
  });
  return points.reduce((str,p,i)=>{
    if(!i) return 'M '+p.x.toFixed(2)+' '+p.y.toFixed(2);
    const before=points[i-1],dx=h[i-1]/3;
    return str+' C '+(before.x+dx).toFixed(2)+' '+(before.y+m[i-1]*dx).toFixed(2)+
      ' '+(p.x-dx).toFixed(2)+' '+(p.y-m[i]*dx).toFixed(2)+
      ' '+p.x.toFixed(2)+' '+p.y.toFixed(2);
  },'');
}
// Give the iPhone chart its own legible coordinate system instead of
// reducing an 820px desktop SVG to unreadably small 5px price labels.
function rangeChartGeometry() {
  const compact = typeof window.matchMedia === 'function' &&
    window.matchMedia('(max-width: 580px)').matches;
  return compact
    ? { width:480, height:380, top:24, left:76, right:424, bottom:320, weekX:458 }
    : { width:820, height:396, top:35, left:87, right:706, bottom:336, weekX:774 };
}
function renderRangeChart() {
  const root = $('range-visualization'); clear(root);
  const parsed = completeDailyHistory(data?.completed_score, selectedAsset);
  if (!parsed) {
    root.append(make('p','method-disclaimer','Daglige observationer er ikke tilstrækkeligt verificeret. Ingen konstrueret kursgraf vises.'));
    setText('range-method', 'Daglig evidens mangler · intet score- eller forecast-skøn');
    return;
  }
  const { days, windows } = parsed;
  // Focus the visual Y-domain on directly comparable daily observations
  // and the derived midpoint. Full frozen ranges remain source-exact below,
  // rather than compressing the actual price path into a giant uncertain band.
  const rangeValues = [
    ...windows.map(r => (r.forecast_low+r.forecast_high)/2),
    ...days.flatMap(d => [d[selectedAsset].low,d[selectedAsset].high])
  ];
  const step = selectedAsset === 'BTC' ? 1000 : 100;
  const floor = Math.floor(Math.min(...rangeValues)/step)*step;
  const ceiling = Math.ceil(Math.max(...rangeValues)/step)*step;
  const yMin = floor-step, yMax=ceiling+step;
  const english=currentLanguage()==='en';
  const weekAbbr=english?['Mon','Tue','Wed','Thu','Fri','Sat','Sun']:['Man','Tir','Ons','Tor','Fre','Lør','Søn'];
  const weekFull=english?['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']:
    ['Mandag','Tirsdag','Onsdag','Torsdag','Fredag','Lørdag','Søndag'];
  const {width:chartW,height:chartH,top,left,right,bottom,weekX}=rangeChartGeometry();
  const h=bottom-top;
  const Y = (n) => bottom-(n-yMin)/(yMax-yMin)*h;
  const X = (i) => left+(right-left)*(i/6);
  const svg=chartElement('svg',{viewBox:'0 0 '+chartW+' '+chartH,class:'cn-history-chart',role:'img',
    'aria-label':english
      ?selectedAsset+' W40: dashed DERIVED midpoint from 3 frozen range windows versus solid blue observed daily close from Monday to Sunday'
      :selectedAsset+' W40: lys stiplet AFLEDT forecastmidte fra tre frosne intervalvinduer mod blå faktisk dagslukning mandag til søndag'});
  svg.append(chartElement('title',{},english
    ?selectedAsset+' week 40: derived range midpoint versus seven actual daily closes'
    :selectedAsset+' uge 40: afledt intervalmidte og syv faktiske dagslukninger'));
  svg.append(chartElement('desc',{},english
    ?'Actual daily closes from 168 source observations. The three original forecast windows were frozen Monday 05:53 UTC. No seven original daily predicted closing prices exist.'
    :'Syv faktiske dagslukninger fra 168 timeobservationer. De tre frosne intervalvinduer blev frosset mandag 05:53 UTC. Der findes ikke syv originale forudsagte dagslukningspriser.'));
  for(let val=yMin;val<=yMax;val+=step){
    const y=Y(val);
    svg.append(chartElement('line',{x1:left-8,x2:right,y1:y,y2:y,class:'cn-chart-grid'}));
    svg.append(chartElement('text',{x:left-14,y:y+4,'text-anchor':'end',class:'cn-chart-tick'},'$'+Math.round(val).toLocaleString(currentLanguage()==='en'?'en-US':'da-DK')));
  }
  // Forecast has ONLY three originally frozen 2/2/3-day windows. The
  // smooth corridor interpolates between their numeric boundaries for
  // presentation, it is NOT a recorded daily forecast or an actual price path.
  const forecastCenters=[.5,2.5,5];
  // Only three authoritative forecast RANGE windows exist. Extrapolate the
  // three frozen centers flat to week endpoints and interpolate visually
  // between them. The trajectory is an indicative RANGE MIDPOINT GUIDE,
  // never a recorded daily closing-price forecast.
  const guide = (field) => {
    const values=windows.map(w=>field==='midpoint'?(w.forecast_high+w.forecast_low)/2:w[field]);
    return [0,...forecastCenters,6].map((day,i)=>({
      x:X(day),y:Y(i===0?values[0]:i===4?values[2]:values[i-1])
    }));
  };
  // The three full forecast LOW/HIGH boundaries belong to the exact-value
  // details below. Do not disguise an interpolated weekly range as daily data.
  const midpointGuide=guide('midpoint');
  svg.append(chartElement('path',{d:monotoneClosePath(midpointGuide),class:'cn-chart-forecast-midpoint','vector-effect':'non-scaling-stroke'}));
  // Only three pale markers are shown, one per original frozen window.
  for(let i=0;i<3;i++){
    const p=midpointGuide[i+1];
    svg.append(chartElement('circle',{cx:p.x,cy:p.y,r:5,class:'cn-chart-midpoint-anchor'}));
  }
  const pathPoints=days.map((d,i)=>({x:X(i),y:Y(d[selectedAsset].close)}));
  const defs=chartElement('defs'),clip=chartElement('clipPath',{id:'cn-path-actual-clip'});
  clip.append(chartElement('rect',{x:left-12,y:0,width:right-left+24,height:chartH,id:'cn-path-actual-clip-rect'}));
  defs.append(clip);svg.append(defs);
  const actualGroup=chartElement('g',{'clip-path':'url(#cn-path-actual-clip)'});
  days.forEach((d,i)=>{
    const p=d[selectedAsset],x=X(i);
    actualGroup.append(chartElement('line',{x1:x,x2:x,y1:Y(p.high),y2:Y(p.low),class:'cn-chart-actual-range'}));
    svg.append(chartElement('text',{x,y:bottom+27,'text-anchor':'middle',class:'cn-chart-weekday'},weekAbbr[i]));
  });
  // W40 is already labeled at the chart's upper edge. No second W40
  // beside Sunday: it clashes with the seventh weekday at iPhone width.
  actualGroup.append(chartElement('path',{d:monotoneClosePath(pathPoints),class:'cn-chart-close-path','vector-effect':'non-scaling-stroke'}));
  pathPoints.forEach((p,i)=>{
    const point=chartElement('circle',{cx:p.x,cy:p.y,r:4.8,class:'cn-chart-point'});
    point.append(chartElement('title',{},days[i].date+' · '+selectedAsset+' dagsluk '+formatUSD(days[i][selectedAsset].close)));
    actualGroup.append(point);
  });
  svg.append(actualGroup);
  const badge=chartElement('text',{x:right,y:20,'text-anchor':'end',class:'cn-chart-week'},'2026 · W40 · UTC');
  svg.append(badge);root.append(svg);
  // Keep exactly one short, source-honest forecast footnote below the chart.
  // Its owner is the pre-existing .range-summary, not a duplicated caption.
  const tableWrap=make('div','cn-chart-table-scroll'),table=make('table','cn-chart-table');
  const head=make('thead'),headrow=make('tr');
  for(const label of english?['Day','Frozen range (window)','Observed low–high','Close']:
    ['Dag','Frosset interval (periode)','Faktisk lav–høj','Luk']) headrow.append(make('th',null,label));
  head.append(headrow);table.append(head);
  const tbody=make('tbody');days.forEach((d,i)=>{
    const row=windows[i<2?0:i<4?1:2],tr=make('tr');
    tr.append(make('td',null,weekAbbr[i]));
    tr.append(make('td',null,formatUSD(row.forecast_low)+' – '+formatUSD(row.forecast_high)));
    tr.append(make('td',null,formatUSD(d[selectedAsset].low)+' – '+formatUSD(d[selectedAsset].high)));
    tr.append(make('td','cn-chart-close-value',formatUSD(d[selectedAsset].close)));
    tbody.append(tr);
  });
  table.append(tbody);tableWrap.append(table);
  const cards=$('cn-range-official-scorecards');clear(cards);
  for (let i=0;i<3;i++) {
    const r=windows[i],card=make('div','cn-score-card');
    card.append(make('span',null,['Dag 1–2','Dag 3–4','Dag 5–7'][i]));
    card.append(make('strong',null,formatPct(r.score)));
    card.append(make('small',null, '70 % containment + 30 % Jaccard'));
    cards?.append(card);
  }
  const windowRoot=$('cn-path-window-table');clear(windowRoot);
  const windowTable=make('table','cn-chart-table cn-window-table');
  const wh=make('thead'),whr=make('tr');
  for (const label of english?['Frozen window','Frozen range low–high','Observed low–high']:
    ['Frosset vindue','Frosset prisinterval','Faktisk interval lav–høj']) whr.append(make('th',null,label));
  wh.append(whr);windowTable.append(wh);
  const wb=make('tbody');
  windows.forEach((w,i)=>{
    const tr=make('tr');
    tr.append(make('th',null,(english?['Days 1–2','Days 3–4','Days 5–7']:
      ['Dag 1–2','Dag 3–4','Dag 5–7'])[i]));
    tr.append(make('td',null,formatUSD(w.forecast_low)+' – '+formatUSD(w.forecast_high)));
    tr.append(make('td',null,formatUSD(w.actual_low)+' – '+formatUSD(w.actual_high)));
    wb.append(tr);
  });
  windowTable.append(wb);
  const frozen=data.completed_score.frozen_weekly_expectation_w40;
  const frozenRoot=$('cn-path-frozen-expectations');clear(frozenRoot);
  const freezeValid = frozen?.contract === 'CN_W40_ORIGINAL_FROZEN_INTRADAY_PATH_CONTEXT_v1' &&
    frozen.forecast_week === '2026-W40' && frozen.public_issue_number === 27 &&
    frozen.frozen_at_utc === '2026-09-28T05:53:37Z' &&
    frozen.source_git_blob_sha === '4f867d594c355c31ede8a3718638c6e72249a5a8' &&
    ['day_1_2','day_3_4','day_5_7'].every((key)=>typeof frozen.intraday_map?.[key] === 'string' &&
      frozen.intraday_map[key].length > 90);
  if (freezeValid) {
    frozenRoot?.append(make('h4','cn-chart-table-title',english?'What did the frozen forecast say?':'Hvad var den frosne forventning?'));
    const descriptions={
      da:['Mulig stabilisering eller fortsættelse, men svag ETH-styrke og markedsstruktur gav risiko for afvisning.',
        'Større opmærksomhed på retest. Et brud på prisintervallet er en prognosefejl, ikke automatisk et breakdown.',
        'Bredere interval for enten dybere retest eller genopretning. Ingen forudsigelse af ekstra volatilitet sidst på ugen.'],
      en:['Stabilization or a continuation attempt was possible, with rejection risk from ETH weakness and microstructure.',
        'Retest watch increased. A range breach was a forecast miss, not automatic evidence of market breakdown.',
        'Wider band allowed a deeper retest or recovery, without predicting late-week volatility expansion.']
    };
    const collection=make('div','cn-frozen-context');
    ['day_1_2','day_3_4','day_5_7'].forEach((key,i)=>{
      const card=make('div','cn-frozen-context-item');
      card.append(make('strong',null,(english?['Days 1–2','Days 3–4','Days 5–7']:['Dag 1–2','Dag 3–4','Dag 5–7'])[i]),
        make('span',null,descriptions[currentLanguage()==='en'?'en':'da'][i]));
      card.dataset.frozenSource = key;
      card.setAttribute('title','2026-W40 · frozen source, Monday 05:53 UTC');
      collection.append(card);
    });
    frozenRoot?.append(collection);
    setText('cn-path-freeze-status',english
      ?'FREEZE · MON 28 SEP 2026 AT 05:53 UTC. Monday observed lows/highs also include hours BEFORE the freeze, so this is not an entirely ex-ante midnight comparison.'
      :'FRYSNING · MAN 28 SEP 2026 KL. 05:53 UTC. Mandagens faktiske low/high omfatter også timer FØR frysetidspunktet. Historisk visning er ikke fuldt ex ante fra midnat.');
  } else {
    frozenRoot?.append(make('p','method-disclaimer','Frossen ugeforventning kan ikke verificeres ud fra kilden.'));
    setText('cn-path-freeze-status','Frysetid ikke kildeverificeret. Ingen ex-ante påstand.');
  }
  const rangeHeading=make('h4','cn-chart-table-title',
    (english?'Original frozen ranges · ':'Originale frosne intervaller · ')+selectedAsset);
  const windowScroll=make('div','cn-chart-table-scroll');
  windowScroll.append(windowTable);windowRoot?.append(rangeHeading,windowScroll);
  const dayRoot=$('cn-path-daily-table');clear(dayRoot);
  const title=make('h4','cn-chart-table-title',english?'Observed prices · Monday to Sunday':'Faktiske priser · mandag til søndag');
  dayRoot?.append(title,tableWrap);
  setText('range-method','W40 · 3 frosne perioder · 7 observerede dage');
  setText('cn-replay-day','Faktisk uge · alle syv verificerede dagslukninger');
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
  initializeLanguage();
  document.querySelectorAll('[data-lang]').forEach((button) => {
    button.addEventListener('click', () => {
      // Translate static content first. The source-owned ETA text is dynamic
      // and must be painted LAST; i18n keeps the original text node baseline.
      selectLanguage(button.dataset.lang);
      if (data) {
        paintPullback(data, button.dataset.lang);
        paintPath(data, button.dataset.lang);
        paintOverviewSnapshot(data.compass);
        cancelRangeReveal();
        renderRangeChart();
        setRangeRevealPhase('score');
        translateInterface();
      }
    });
  });
  bindNavigation();
  bindPanels();
  if (typeof window.matchMedia === 'function') {
    window.matchMedia('(max-width: 580px)').addEventListener?.('change', () => {
      // Recreate paths and clip geometry only when crossing the real breakpoint.
      // Avoid stale desktop coordinates after iPhone landscape rotation.
      if (data) {
        cancelRangeReveal();
        renderRangeChart();
        setRangeRevealPhase('score');
      }
    });
  }
  try {
    const response = await fetch(SOURCE_FILE, { cache: 'no-store' });
    if (!response.ok) throw new Error('Source HTTP ' + response.status);
    const raw = await response.json();
    data = getTrustedSeed(raw);
    paintTop(data);
    paintPath(data, currentLanguage());
    paintCompass(data);
    renderRangeChart();
    setRangeRevealPhase('score');
    paintHistory(data);
    paintSource(data);
    // Dynamic source rendering can shift the page after the initial hash
    // navigation, so honor a shared PATH deep link after source paint too.
    if (location.hash === '#cn-path-week') {
      requestAnimationFrame(() => document.getElementById('cn-path-week')
        ?.scrollIntoView({ behavior:'instant', block:'start' }));
    }
  } catch (err) {
    console.error('Preview source validation failed:', err);
    setText('source-health', 'DATASOURCE: UNAVAILABLE');
    setText('source-time', 'Kildeintegritet ikke bekræftet');
    setText('hero-deck', 'Previewen kan ikke verificere datakilden. Ingen aktuelle markedskonklusioner kan udledes.');
    setText('hero-now', '— / UNAVAILABLE');
    setText('hero-forward', '— / UNAVAILABLE');
    setText('hero-action-summary', 'UTILGÆNGELIG');
    setText('overview-risk', 'UTILGÆNGELIG');
    setText('overview-risk-window', 'ETA ikke tilgængelig');
    setText('compass-risk-window', 'ETA ikke tilgængelig');
    setText('overview-risk-stage', 'Stadie ikke tilgængeligt');
    setText('compass-risk-stage', 'Stadie ikke tilgængeligt');
    setText('overview-risk-desc', 'Ingen verificeret kilde eller start/slut.');
    setText('compass-primary-direction', 'UKENDT');
    setText('compass-primary-action', 'UTILGÆNGELIG');
    setText('bullbear-bull', '—');
    setText('bullbear-bear', '—');
    setText('bullbear-bias', 'UTILGÆNGELIG');
    if ($('bullbear-track')) $('bullbear-track').hidden = true;
    setText('compass-risk-inline', 'UTILGÆNGELIG');
    setText('compass-sell-inline', 'UTILGÆNGELIG');
    setText('compass-distribution-inline', 'UTILGÆNGELIG');
    $('horizon-body')?.replaceChildren(make('tr'));
    $('asset-body')?.replaceChildren(make('tr'));
    $('range-visualization')?.replaceChildren(make('p', 'method-disclaimer', 'Ingen verificeret kilde tilgængelig.'));
    // Never show pre-filled demo numbers after source validation fails.
    for (const target of document.querySelectorAll('.hero-grid, .path-panel, .forecast-grid, .teaser-shell, .compass-summary, .compass-weather, .compass-urgent, .compass-table-block, .compass-disclosure-group, .table-frame, .proof-summary-grid, .range-compare-panel, .history-panel')) {
      target.hidden = true;
    }
    setText('source-detail', 'Kilden kunne ikke indlæses eller bestod ikke integritetskontrollen. Der vises ingen markeds- eller scorepåstande.');
    showToast('Kildedata kunne ikke indlæses.');
  } finally {
    translateInterface();
  }
}

initialize();
