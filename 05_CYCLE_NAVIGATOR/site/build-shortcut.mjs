import { copyFile, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteDir = dirname(fileURLToPath(import.meta.url));
const output = resolve(siteDir, "dist/index.html");
let html = await readFile(output, "utf8");

function requireAnchor(anchor, label) {
  if (!html.includes(anchor)) throw new Error(`${label} changed; refusing silent shortcut drift`);
}

const headAnchor = '</head>';
requireAnchor(headAnchor, 'Production head');
html = html.replace(headAnchor, '  <link rel="stylesheet" href="./shortcut.css" />\n</head>');

const rightNowAnchor = '      <section class="section">\n        <div class="section-head"><div><div class="eyebrow" data-icon="signal">Right now</div><h2>What matters.</h2></div><p class="section-intro">A curated read of the official weekly state. LIVE prices add context, but never rewrite the official Cycle Navigator call.</p></div>';
requireAnchor(rightNowAnchor, 'Right-now section');
const shortcut = `      <section class="shortcut-section" id="shortcut" aria-labelledby="shortcut-title">\n        <div class="shortcut-head"><div><div class="eyebrow">30-second read</div><h2 id="shortcut-title">The cycle at a glance.</h2></div><p>NOW → NEXT DAYS → THIS WEEK → 2–3 WEEKS → NEXT GATE → SCORE. Everything is taken from OFFICIAL CN data or clearly marked unavailable.</p></div>\n        <div class="shortcut-grid">\n          <article class="shortcut-card primary"><span class="shortcut-label">Now</span><strong id="shortcutNow">—</strong><small id="shortcutNowNote">Loading official state.</small></article>\n          <article class="shortcut-card muted"><span class="shortcut-label">Next days</span><strong id="shortcutDays">NOT PUBLISHED</strong><small id="shortcutDaysNote">No OFFICIAL 24–72h feed. LIVE prices do not create a signal.</small></article>\n          <article class="shortcut-card"><span class="shortcut-label">This week</span><strong id="shortcutWeek">—</strong><small id="shortcutWeekNote">Loading 7-day base case.</small></article>\n          <article class="shortcut-card"><span class="shortcut-label">Next 2–3 weeks</span><strong id="shortcutForward">—</strong><small id="shortcutForwardNote">Loading forward view.</small></article>\n          <article class="shortcut-card primary"><span class="shortcut-label">Next phase</span><strong id="shortcutGate">—</strong><small id="shortcutGateNote">Loading confirmation window.</small></article>\n          <article class="shortcut-card"><span class="shortcut-label">Precision</span><strong id="shortcutScore">—</strong><small id="shortcutScoreNote">Loading verified track record.</small></article>\n        </div>\n        <article class="panel view-change" aria-label="What changes the Cycle Navigator view">\n          <div><b>What unlocks the next phase</b><p id="viewUnlock">Waiting for OFFICIAL confirmation conditions.</p></div>\n          <div><b>If confirmation fails</b><p id="viewIfNot">The current OFFICIAL state remains in force until a new Cycle Navigator closes the evidence.</p></div>\n        </article>\n      </section>\n\n`;
html = html.replace(rightNowAnchor, `${shortcut}${rightNowAnchor}`);

const oldTimelineHead = '        <div class="section-head"><div><div class="eyebrow" data-icon="route">Cycle journey</div><h2>Where capital goes next.</h2></div><p class="section-intro">The timeline is intentionally conditional. Calendar time never overrides confirmation — the sequence advances only when market breadth and relative leadership transmit.</p></div>';
requireAnchor(oldTimelineHead, 'Cycle journey heading');
const newTimelineHead = '        <div class="section-head"><div><div class="eyebrow" data-icon="route">Altcoin season countdown</div><h2>Path to Mania.</h2></div><p class="section-intro">A confirmation-gated sequence from the current regime to broad altseason, Mania and eventually distribution. Calendar labels never override evidence.</p></div>';
html = html.replace(oldTimelineHead, newTimelineHead);

const clockAnchor = '        <div class="clock-grid" id="cycleClocks" aria-label="Cycle timing clocks"></div>';
requireAnchor(clockAnchor, 'Cycle clocks');
const mania = `        <div class="mania-summary-grid">\n          <article class="mania-summary"><span>Current phase</span><strong id="maniaCurrent">—</strong><small id="maniaCurrentNote">Loading current stage.</small></article>\n          <article class="mania-summary"><span>Next unlock</span><strong id="maniaNext">—</strong><small id="maniaNextNote">Loading next confirmation gate.</small></article>\n          <article class="mania-summary"><span>Path to Mania</span><strong id="maniaGates">—</strong><small id="maniaGatesNote">Calendar ETA stays locked until the required phases confirm.</small></article>\n        </div>\n        <div class="panel mania-path-panel"><div class="mania-path" id="maniaPath"></div></div>\n        ${clockAnchor}\n        <div class="official-phase-caption">OFFICIAL CN phase detail</div>`;
html = html.replace(clockAnchor, mania);

const bodyAnchor = '</body>';
requireAnchor(bodyAnchor, 'Production body');
html = html.replace(bodyAnchor, '  <script src="./shortcut.js" defer></script>\n</body>');

await writeFile(output, html, "utf8");
await copyFile(resolve(siteDir, "shortcut.css"), resolve(siteDir, "dist/shortcut.css"));
await copyFile(resolve(siteDir, "shortcut.js"), resolve(siteDir, "dist/shortcut.js"));
console.log("Added CN shortcut horizon board and Path to Mania layer");
