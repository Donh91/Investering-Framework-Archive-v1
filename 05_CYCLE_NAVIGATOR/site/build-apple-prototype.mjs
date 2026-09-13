import { readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteDir = dirname(fileURLToPath(import.meta.url));
const sourcePath = resolve(siteDir, "apple-prototype.html");
const outputPath = resolve(siteDir, "dist/apple-prototype.html");
let html = await readFile(sourcePath, "utf8");

const heroAnchor = '<div>\n          <div class="eyebrow" id="heroEyebrow"></div>';
if (!html.includes(heroAnchor)) throw new Error("Apple prototype hero anchor changed; refusing silent polish drift");
html = html.replace(
  heroAnchor,
  '<div>\n          <img class="hero-logo" src="./favicon.svg" alt="" aria-hidden="true" />\n          <div class="eyebrow" id="heroEyebrow"></div>'
);

const oldHeroCopy = "$('heroSub').textContent=pkg.base_case_this_week||pkg.market_state||'Official state unavailable.';";
if (!html.includes(oldHeroCopy)) throw new Error("Apple prototype hero copy binding changed; refusing silent polish drift");
html = html.replace(
  oldHeroCopy,
  "$('heroSub').textContent=pkg.market_state||pkg.base_case_this_week||'Official state unavailable.';"
);

const styleAnchor = "    @media (prefers-reduced-motion:reduce){";
if (!html.includes(styleAnchor)) throw new Error("Apple prototype style anchor changed; refusing silent polish drift");
const brandPolish = `    .hero-logo{display:block;width:88px;height:88px;margin:0 0 28px;border-radius:22px;filter:drop-shadow(0 16px 34px rgba(25,45,78,.10))}\n    body[data-variant="instrument"] .hero-logo{width:72px;height:72px;margin-bottom:22px;filter:drop-shadow(0 18px 34px rgba(0,0,0,.18))}\n    body[data-variant="editorial"] .hero-logo{width:104px;height:104px;margin-bottom:34px}\n    @media (max-width:900px){.hero-logo{width:76px;height:76px;margin-bottom:22px}body[data-variant="instrument"] .hero-logo{width:66px;height:66px}body[data-variant="editorial"] .hero-logo{width:88px;height:88px;margin-bottom:26px}}\n`;
html = html.replace(styleAnchor, `${brandPolish}${styleAnchor}`);

await writeFile(outputPath, html, "utf8");
console.log("Added polished hidden Apple-level Cycle Navigator design prototype to public bundle");
