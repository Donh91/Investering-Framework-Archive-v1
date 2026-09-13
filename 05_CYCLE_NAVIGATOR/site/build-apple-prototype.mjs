import { copyFile, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteDir = dirname(fileURLToPath(import.meta.url));
const sourcePath = resolve(siteDir, "apple-prototype.html");
const prototypeOutput = resolve(siteDir, "dist/apple-prototype.html");
const productionOutput = resolve(siteDir, "dist/index.html");
let html = await readFile(sourcePath, "utf8");

function requireAnchor(source, anchor, label) {
  if (!source.includes(anchor)) throw new Error(`${label} changed; refusing silent production drift`);
}

// Shared prototype polish: stronger CN identity and shorter hero hierarchy.
const heroAnchor = '<div>\n          <div class="eyebrow" id="heroEyebrow"></div>';
requireAnchor(html, heroAnchor, "Apple prototype hero anchor");
html = html.replace(
  heroAnchor,
  '<div>\n          <img class="hero-logo" src="./favicon.svg" alt="" aria-hidden="true" />\n          <div class="eyebrow" id="heroEyebrow"></div>'
);

const oldHeroCopy = "$('heroSub').textContent=pkg.base_case_this_week||pkg.market_state||'Official state unavailable.';";
requireAnchor(html, oldHeroCopy, "Apple prototype hero copy binding");
html = html.replace(
  oldHeroCopy,
  "$('heroSub').textContent=pkg.market_state||pkg.base_case_this_week||'Official state unavailable.';"
);

const styleAnchor = "    @media (prefers-reduced-motion:reduce){";
requireAnchor(html, styleAnchor, "Apple prototype style anchor");
const brandPolish = `    .hero-logo{display:block;width:88px;height:88px;margin:0 0 28px;border-radius:22px;filter:drop-shadow(0 16px 34px rgba(25,45,78,.10))}\n    body[data-variant="instrument"] .hero-logo{width:72px;height:72px;margin-bottom:22px;filter:drop-shadow(0 18px 34px rgba(0,0,0,.18))}\n    body[data-variant="editorial"] .hero-logo{width:104px;height:104px;margin-bottom:34px}\n    @media (max-width:900px){.hero-logo{width:76px;height:76px;margin-bottom:22px}body[data-variant="instrument"] .hero-logo{width:66px;height:66px}body[data-variant="editorial"] .hero-logo{width:88px;height:88px;margin-bottom:26px}}\n`;
html = html.replace(styleAnchor, `${brandPolish}${styleAnchor}`);

// Preserve the full design picker as a hidden study route.
await writeFile(prototypeOutput, html, "utf8");

// Promote Quiet Precision to production without exposing the picker.
let production = html;
production = production.replace('<title>Cycle Navigator · Design Study</title>', `<title>Cycle Navigator</title>\n  <meta name="description" content="Cycle Navigator — a live crypto cycle map for market phase, capital rotation, altseason timing and public forecast accountability." />\n  <meta name="format-detection" content="telephone=no" />\n  <meta name="apple-mobile-web-app-capable" content="yes" />\n  <meta name="apple-mobile-web-app-status-bar-style" content="default" />\n  <meta property="og:type" content="website" />\n  <meta property="og:site_name" content="Cycle Navigator" />\n  <meta property="og:title" content="Cycle Navigator — Market Cycles. With Edge." />\n  <meta property="og:description" content="A live crypto cycle map for market phase, capital rotation, altseason timing and public forecast accountability." />\n  <meta property="og:image" content="https://donh91.github.io/Investering-Framework-Archive-v1/social-card.png" />\n  <meta property="og:image:width" content="1200" />\n  <meta property="og:image:height" content="630" />\n  <meta name="twitter:card" content="summary_large_image" />\n  <meta name="twitter:title" content="Cycle Navigator — Market Cycles. With Edge." />\n  <meta name="twitter:description" content="Market phase · capital rotation · altseason timing · forecast accountability." />\n  <meta name="twitter:image" content="https://donh91.github.io/Investering-Framework-Archive-v1/social-card.png" />\n  <link rel="icon" href="./favicon.svg" type="image/svg+xml" />\n  <link rel="preconnect" href="https://api.coingecko.com" />\n  <link rel="stylesheet" href="./quiet-production.css" />`);

const pickerBlock = /\n  <div class="variant-note" id="variantNote">[\s\S]*?<\/nav>\n/;
if (!pickerBlock.test(production)) throw new Error("Prototype picker markup changed; refusing silent production drift");
production = production.replace(pickerBlock, "\n");

const notesLine = "      const notes={quiet:'Quiet Precision · minimal / white space',instrument:'CN Instrument · financial / focused',editorial:'Editorial Navigator · narrative / spacious'};\n";
requireAnchor(production, notesLine, "Prototype variant notes");
production = production.replace(notesLine, "");

const variantLogic = /\n      function setVariant\(v\)\{[\s\S]*?setVariant\(new URL\(location\.href\)\.searchParams\.get\('v'\)\|\|'quiet'\);\n/;
if (!variantLogic.test(production)) throw new Error("Prototype variant switching logic changed; refusing silent production drift");
production = production.replace(variantLogic, "\n");

const timelineAnchor = '      <section class="section" id="timeline">';
requireAnchor(production, timelineAnchor, "Quiet timeline section");
const forecastSection = `      <section class="section" id="forecast">\n        <div class="section-head"><div><div class="eyebrow" data-icon="signal">Forecast</div><h2>The working map.</h2></div><p class="section-intro">The weekly map is deliberately conditional. It shows what the framework expects next without pretending the future is already confirmed.</p></div>\n        <div class="grid forecast-grid">\n          <article class="panel forecast-card"><div class="panel-title">This week</div><h3>Base case</h3><p id="weekCase">—</p></article>\n          <article class="panel forecast-card"><div class="panel-title">Next 2–3 weeks</div><h3>Forward view</h3><p id="forwardCase">—</p></article>\n        </div>\n      </section>\n\n`;
production = production.replace(timelineAnchor, `${forecastSection}${timelineAnchor}`);

const phasePanelAnchor = '        <div class="panel"><div class="timeline" id="phaseTimeline"></div></div>';
requireAnchor(production, phasePanelAnchor, "Quiet phase timeline panel");
production = production.replace(phasePanelAnchor, '        <div class="clock-grid" id="cycleClocks" aria-label="Cycle timing clocks"></div>\n        <div class="panel"><div class="timeline" id="phaseTimeline"></div></div>');

const calibrationAnchor = '      <section class="section" id="calibration">';
requireAnchor(production, calibrationAnchor, "Quiet calibration section");
const actionSection = `      <section class="section" id="compass">\n        <div class="section-head"><div><div class="eyebrow" data-icon="compass">Action compass</div><h2>What the map says to do.</h2></div><p class="section-intro">Public navigation shorthand, not portfolio execution authority. The site never invents a trade signal beyond the OFFICIAL Cycle Navigator state.</p></div>\n        <div class="action-grid" id="actionGrid"></div>\n        <div class="grid horizon-grid">\n          <article class="panel horizon-card"><div class="panel-title">2–3 weeks</div><h3 id="horizon23Posture">Current compass</h3><p id="horizon23Copy">—</p></article>\n          <article class="panel horizon-card"><div class="panel-title">4–8 weeks</div><h3 id="horizon48Posture">Longer cycle compass</h3><p id="horizon48Copy">—</p></article>\n        </div>\n        <p class="nav-disclaimer">BUY / TOP-UP / SELL language is translated into public CN posture: HOLD, PREPARE, SELECTIVE DEPLOYMENT, BROADER DEPLOYMENT or PROTECT CAPITAL.</p>\n      </section>\n\n`;
production = production.replace(calibrationAnchor, `${actionSection}${calibrationAnchor}`);

const footerAnchor = '      <footer class="footer"><strong>Cycle Navigator</strong><span>Scenario map only, not investment advice.</span></footer>';
requireAnchor(production, footerAnchor, "Quiet footer");
const productionTail = `      <section class="section" id="current-scoring">\n        <div class="section-head"><div><div class="eyebrow" data-icon="check">Current scoring</div><h2>Open until the evidence closes.</h2></div><p class="section-intro">The current week never receives a synthetic precision percentage. Frozen tests stay visibly open until completed evidence can score them.</p></div>\n        <article class="panel current-score-strip">\n          <div class="current-score-state"><small>Current week</small><span id="currentScoreState">SCORING IN PROGRESS</span></div>\n          <div><div class="panel-title">Frozen confirmation tests</div><div class="frozen-tests" id="frozenTests"></div></div>\n        </article>\n      </section>\n\n      <section class="section" id="public-edition">\n        <div class="section-head"><div><div class="eyebrow" data-icon="chart">Public edition</div><h2>The published story.</h2></div><p class="section-intro">The curated public X narrative stays separate from machine-valid scoring and LIVE prices, but remains one tap away.</p></div>\n        <article class="panel public-card">\n          <div class="panel-title">Publication state <span class="public-status" id="publicationStatus">—</span></div>\n          <details><summary>Current X-ready Cycle Navigator</summary><div class="public-copy" id="xReadyCopy">—</div></details>\n          <details><summary id="publishedSummary">Latest confirmed X publication</summary><div class="public-copy" id="publishedCopy">—</div></details>\n          <details><summary>Audit notes · strengths, misses and open tests</summary><div class="audit-grid"><div><h4>What held</h4><ul id="strengthList"></ul></div><div><h4>What was challenged</h4><ul id="missList"></ul></div></div></details>\n        </article>\n      </section>\n\n${footerAnchor}`;
production = production.replace(footerAnchor, productionTail);

const bodyEnd = '</body>';
requireAnchor(production, bodyEnd, "Quiet body end");
production = production.replace(bodyEnd, '  <script src="./quiet-production.js" defer></script>\n</body>');

await writeFile(productionOutput, production, "utf8");
await copyFile(resolve(siteDir, "quiet-production.css"), resolve(siteDir, "dist/quiet-production.css"));
await copyFile(resolve(siteDir, "quiet-production.js"), resolve(siteDir, "dist/quiet-production.js"));
console.log("Built hidden design study and promoted Quiet Precision to production");
