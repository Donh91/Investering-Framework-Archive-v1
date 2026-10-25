import './styles.css';

type Variant = 'b' | 'c';
type Asset = 'BTC' | 'ETH';
type Language = 'da' | 'en';
interface Point {
  t: number;
  forecast: number;
  low: number;
  high: number;
  actual: number;
}

let variant: Variant = 'b';
let asset: Asset = 'BTC';
let language: Language = 'da';
let hour = 63;
let sourceMissing = false;
let playing: number | undefined;

const i18n: Record<Language, Record<string, string>> = {
  da: {
    headerState: 'DESIGNTEST',
    overview: 'Overblik',
    results: 'Resultater',
    warning: 'ISOLERET DESIGNPREVIEW · KUN EKSEMPELDATA',
    heroEyebrow: 'CYCLE NAVIGATOR / GRAPH STUDIO',
    heroTitle: 'Ugens kursrejse.',
    heroIntro:
      'To linjer. Det forventede forløb og markedets faktiske bevægelse, uden tabeller eller visuel støj.',
    choiceLabel: 'VÆLG DESIGN',
    originalA: 'Se original A ↗',
    cardEyebrow: 'FROSSEN PROGNOSE / UGENS BEVÆGELSE',
    cardDesc: 'Kursretning, forventede udsving og faktiske observationer.',
    observed: 'Simuleret observeret kurs',
    freeze: 'Illustrativ prognose · låst for hele ugen',
    blueLegend: 'Forventet kurs',
    greenLegend: 'Faktisk kurs',
    rangeLegend: 'Forventet low / high',
    demoFoot: 'VISUEL SIMULATION, IKKE EN PUBLICERET PROGNOSE',
    missingFoot: 'MANGLENDE ORIGINAL KILDE · INGEN FORECAST-KURVE',
    hourLabel: 'Spol gennem ugen',
    monday: 'Mandag',
    sunday: 'Søndag',
    play: 'Afspil uge',
    pause: 'Stop',
    missing: 'Test uden prognose',
    restore: 'Vis forecast-design',
    underA: 'Frys forventningen',
    underAText:
      'Prognoselinjen og low/high-båndet ændrer sig ikke, når den faktiske kurve vokser.',
    underB: 'Vis bevægelsen',
    underBText:
      'Forventningen har egne udsving. Ikke blot en flad linje med tre range-intervaller.',
    underC: 'Bevar troværdigheden',
    underCText:
      'Manglende original kilde betyder ingen officiel prognoselinje. Scores hører til Resultater.',
    disclaimerTitle: 'Datagrænse',
    disclaimerBody:
      'Begge designs bruger kunstigt genererede kurver udelukkende til visuel godkendelse. Den faktiske W43-prognose mangler en verificeret daglig prognosesti. Den færdige graf må kun vise en fremadrettet kildefrosset forventning med dokumenterede datapunkter.',
    footer: 'Ingen ændringer på live-sitet',
  },
  en: {
    headerState: 'DESIGN TEST',
    overview: 'Overview',
    results: 'Results',
    warning: 'ISOLATED DESIGN PREVIEW · EXAMPLE DATA ONLY',
    heroEyebrow: 'CYCLE NAVIGATOR / GRAPH STUDIO',
    heroTitle: 'The weekly journey.',
    heroIntro:
      'Two lines. Expected direction against observed market movement, with no tables or visual clutter.',
    choiceLabel: 'SELECT DESIGN',
    originalA: 'View original A ↗',
    cardEyebrow: 'FROZEN FORECAST / WEEKLY MOVEMENT',
    cardDesc: 'Price direction, expected swings and actual observations.',
    observed: 'Simulated observed price',
    freeze: 'Illustrative forecast · frozen for the whole week',
    blueLegend: 'Forecast path',
    greenLegend: 'Actual path',
    rangeLegend: 'Expected low / high',
    demoFoot: 'VISUAL SIMULATION, NOT A PUBLISHED FORECAST',
    missingFoot: 'ORIGINAL SOURCE MISSING · NO FORECAST PATH',
    hourLabel: 'Move through the week',
    monday: 'Monday',
    sunday: 'Sunday',
    play: 'Play week',
    pause: 'Pause',
    missing: 'Test without forecast',
    restore: 'Restore forecast design',
    underA: 'Keep the forecast frozen',
    underAText:
      'The forecast line and low/high band never change while actual observations arrive.',
    underB: 'Show expected movement',
    underBText:
      'Forecast has genuine illustrated swings, not just a flat line across three range windows.',
    underC: 'Keep the evidence honest',
    underCText:
      'An absent original source means no official forecast line. Scoring belongs in Results.',
    disclaimerTitle: 'Data boundary',
    disclaimerBody:
      'Both options use synthetic curves for visual approval only. The actual W43 forecast has no source-verified daily price path. Production can draw a forward forecast only using documented original pre-outcome points.',
    footer: 'Live website remains unchanged',
  },
};

const dayNames: Record<Language, string[]> = {
  da: ['Man', 'Tir', 'Ons', 'Tor', 'Fre', 'Lør', 'Søn'],
  en: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
};
const longDays: Record<Language, string[]> = {
  da: ['Mandag', 'Tirsdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lørdag', 'Søndag'],
  en: [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday',
  ],
};
const byId = (id: string): HTMLElement => {
  const target = document.getElementById(id);
  if (!target) throw new Error('MISSING_' + id);
  return target;
};
const svgElement = (name: string) =>
  document.createElementNS('http://www.w3.org/2000/svg', name);
function points(which: Asset): Point[] {
  const base = which === 'BTC' ? 82400 : 2425;
  const amp = which === 'BTC' ? 465 : 31;
  const series: Point[] = [];
  // Fixed deterministic visual fixtures. Absolutely not sourced predictions.
  // Both the forecast curve AND envelope are unchanged as the time cursor moves.
  for (let i = 0; i < 168; i++) {
    const phase = i / 167;
    const f =
      0.92 * Math.sin(i / 17 - 0.52) +
      0.3 * Math.sin(i / 4.7) +
      0.13 * Math.sin(i / 2.7 + 1.1) +
      0.16 * Math.sin(i / 1.75) +
      1.05 * Math.sin(phase * Math.PI * 2.12 - 0.53) +
      1.45 * phase;
    const diff =
      0.98 * Math.sin(i / 16 - 1.05) +
      0.41 * Math.sin(i / 5.0 + 1.4) +
      0.38 * Math.sin(i * 0.94) +
      0.23 * Math.sin(i * 1.81 + 0.3) +
      0.7 * Math.sin(phase * 7.5 - 0.9) +
      1.52 * phase -
      0.12;
    const spread =
      0.5 +
      0.13 * Math.sin(i / 9 + 0.2) ** 2 +
      0.24 * Math.abs(Math.sin(i / 5.6));
    series.push({
      t: i,
      forecast: base + amp * f,
      low: base + amp * (f - spread),
      high: base + amp * (f + spread),
      actual: base + amp * diff,
    });
  }
  return series;
}
const data: Record<Asset, Point[]> = { BTC: points('BTC'), ETH: points('ETH') };
function number(n: number) {
  return Math.round(n).toLocaleString(language === 'da' ? 'da-DK' : 'en-US');
}
function movePath(pts: { x: number; y: number }[]) {
  return pts
    .map(
      (p, i) => (i === 0 ? 'M' : 'L') + p.x.toFixed(2) + ',' + p.y.toFixed(2)
    )
    .join(' ');
}
function put(id: string, text: string) {
  byId(id).textContent = text;
}
function attribute(id: string, name: string, value: string) {
  byId(id).setAttribute(name, value);
}
function updateGraph() {
  const arr = data[asset];
  const all = arr.flatMap(p => [p.low, p.high, p.actual]);
  const min = Math.min(...all),
    max = Math.max(...all);
  const pad = (max - min) * 0.06;
  const lower = min - pad,
    upper = max + pad;
  const x = (t: number) => 14 + (t / 167) * 972;
  const y = (price: number) => 28 + ((upper - price) / (upper - lower)) * 344;
  const f = arr.map(p => ({ x: x(p.t), y: y(p.forecast) }));
  const lo = arr.map(p => ({ x: x(p.t), y: y(p.low) }));
  const hi = arr.map(p => ({ x: x(p.t), y: y(p.high) }));
  const actualPoints = arr
    .slice(0, hour + 1)
    .map(p => ({ x: x(p.t), y: y(p.actual) }));
  const polygon =
    movePath(hi) +
    ' ' +
    movePath(lo.slice().reverse()).replace(/^M/, 'L') +
    ' Z';
  attribute('range-band', 'd', sourceMissing ? '' : polygon);
  attribute('range-lower', 'd', sourceMissing ? '' : movePath(lo));
  attribute('range-upper', 'd', sourceMissing ? '' : movePath(hi));
  attribute('forecast', 'd', sourceMissing ? '' : movePath(f));
  attribute('actual', 'd', movePath(actualPoints));
  const last = arr[hour],
    endX = x(last.t),
    endY = y(last.actual);
  ['endpoint', 'endpoint-halo'].forEach(id => {
    attribute(id, 'cx', String(endX));
    attribute(id, 'cy', String(endY));
  });
  attribute('playhead', 'x1', String(endX));
  attribute('playhead', 'x2', String(endX));
  const grid = byId('grid');
  grid.replaceChildren();
  for (let i = 0; i < 5; i++) {
    const line = svgElement('line');
    const py = 28 + (344 / 4) * i;
    line.setAttribute('x1', '14');
    line.setAttribute('x2', '986');
    line.setAttribute('y1', String(py));
    line.setAttribute('y2', String(py));
    line.setAttribute('stroke', 'var(--grid)');
    line.setAttribute('stroke-opacity', variant === 'b' ? '.17' : '.24');
    line.setAttribute('stroke-width', '1');
    grid.append(line);
  }
  for (let i = 1; i < 7; i++) {
    const line = svgElement('line');
    const px = x(i * 24);
    line.setAttribute('x1', String(px));
    line.setAttribute('x2', String(px));
    line.setAttribute('y1', '28');
    line.setAttribute('y2', '372');
    line.setAttribute('stroke', 'var(--grid)');
    line.setAttribute('stroke-opacity', '.16');
    line.setAttribute('stroke-dasharray', '3 7');
    grid.append(line);
  }
  const labels = byId('price-axis');
  labels.replaceChildren();
  for (let i = 0; i < 5; i++) {
    const span = document.createElement('span');
    span.textContent = number(upper - ((upper - lower) * i) / 4);
    span.style.top = (100 * (28 + (344 * i) / 4)) / 405 + '%';
    labels.append(span);
  }
  const day = Math.min(6, Math.floor(hour / 24)),
    h = hour % 24;
  const hours = String(h).padStart(2, '0') + ':00 UTC';
  put('pair', asset + ' / USD');
  put('observed-value', number(last.actual));
  put('time-label', dayNames[language][day] + ' · ' + hours);
  put('timeline-label', longDays[language][day] + ' ' + hours);
  put(
    'source-state',
    i18n[language][sourceMissing ? 'missingFoot' : 'demoFoot']
  );
  byId('variant-panel').dataset.source = sourceMissing
    ? 'missing'
    : 'illustrative';
  document
    .querySelectorAll<HTMLElement>('[data-asset]')
    .forEach(b =>
      b.setAttribute('aria-pressed', String(b.dataset.asset === asset))
    );
}
function updateVariant() {
  const panel = byId('variant-panel');
  panel.dataset.variant = variant;
  put('card-heading', 'Weekly Outlook ' + (variant === 'b' ? '· B' : '· C'));
  document.querySelectorAll<HTMLElement>('[data-variant]').forEach(b => {
    if (b.tagName === 'BUTTON')
      b.setAttribute('aria-pressed', String(b.dataset.variant === variant));
  });
  try {
    history.replaceState(null, '', '#' + variant);
  } catch {}
  updateGraph();
}
function translate() {
  document.documentElement.lang = language;
  document.querySelectorAll<HTMLElement>('[data-t]').forEach(e => {
    const key = e.dataset.t || '';
    if (i18n[language][key]) e.textContent = i18n[language][key];
  });
  document.querySelectorAll<HTMLElement>('[data-day]').forEach(e => {
    const i = Number(e.dataset.day);
    e.textContent = dayNames[language][i].toUpperCase();
  });
  document
    .querySelectorAll<HTMLElement>('[data-lang]')
    .forEach(e =>
      e.setAttribute('aria-pressed', String(e.dataset.lang === language))
    );
  put('missing', i18n[language][sourceMissing ? 'restore' : 'missing']);
  updatePlayCaption();
  updateGraph();
}
function updatePlayCaption() {
  put('play-symbol', playing === undefined ? '▶' : 'Ⅱ');
  put('play-text', i18n[language][playing === undefined ? 'play' : 'pause']);
}
function stopPlaying() {
  if (playing !== undefined) {
    window.clearInterval(playing);
    playing = undefined;
  }
  updatePlayCaption();
}
document
  .querySelectorAll<HTMLButtonElement>('[data-variant]')
  .forEach(button => {
    button.addEventListener('click', () => {
      variant = button.dataset.variant as Variant;
      updateVariant();
    });
  });
document.querySelectorAll<HTMLButtonElement>('[data-asset]').forEach(button => {
  button.addEventListener('click', () => {
    asset = button.dataset.asset as Asset;
    updateGraph();
  });
});
document.querySelectorAll<HTMLButtonElement>('[data-lang]').forEach(button => {
  button.addEventListener('click', () => {
    language = button.dataset.lang as Language;
    translate();
  });
});
(byId('hour-slider') as HTMLInputElement).addEventListener('input', event => {
  stopPlaying();
  hour = Number((event.currentTarget as HTMLInputElement).value);
  updateGraph();
});
byId('play').addEventListener('click', () => {
  if (playing !== undefined) {
    stopPlaying();
    return;
  }
  if (hour === 167) hour = 0;
  (byId('hour-slider') as HTMLInputElement).value = String(hour);
  playing = window.setInterval(() => {
    hour = Math.min(167, hour + 1);
    (byId('hour-slider') as HTMLInputElement).value = String(hour);
    updateGraph();
    if (hour === 167) stopPlaying();
  }, 135);
  updatePlayCaption();
});
byId('missing').addEventListener('click', () => {
  sourceMissing = !sourceMissing;
  byId('missing').setAttribute('aria-pressed', String(sourceMissing));
  put('missing', i18n[language][sourceMissing ? 'restore' : 'missing']);
  updateGraph();
});
window.addEventListener('visibilitychange', () => {
  if (document.hidden) stopPlaying();
});
const initial = location.hash.slice(1).toLowerCase();
if (initial === 'c') variant = 'c';
translate();
updateVariant();
