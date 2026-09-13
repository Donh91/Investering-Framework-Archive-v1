import { mkdir, readFile, readdir, rm, writeFile, copyFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(siteDir, "../..");
const outputDir = resolve(siteDir, "dist");
const dataDir = resolve(outputDir, "data");

const POINTER_PATH = resolve(repoRoot, "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json");
const PUBLISHED_ROOT = resolve(repoRoot, "05_CYCLE_NAVIGATOR/published");
const PUBLIC_SITE_FILES = [
  "index.html",
  "styles.css",
  "motion.css",
  "journey.css",
  "vibe.css",
  "app.js",
  "motion.js",
  "journey.js",
  "live-context.js"
];

function pick(obj, keys) {
  return Object.fromEntries(keys.filter((key) => Object.prototype.hasOwnProperty.call(obj || {}, key)).map((key) => [key, obj[key]]));
}

function sanitizePointer(pointer) {
  return pick(pointer, [
    "iso_year",
    "iso_week",
    "completed_source_week",
    "issue_number",
    "publication_status",
    "status"
  ]);
}

function sanitizePackage(pkg) {
  return {
    ...pick(pkg, [
      "issue_number",
      "previous_issue_number",
      "generated_unix",
      "status",
      "market_state",
      "base_case_this_week",
      "base_case_2_3_weeks",
      "base_case_4_8_weeks",
      "compass_4_8_weeks",
      "rotation_ladder",
      "altseason_countdown",
      "altseason_mania_window",
      "uncertainties",
      "publication_status",
      "x_ready_markdown"
    ]),
    evaluation: pkg?.evaluation ? pick(pkg.evaluation, [
      "structural_score",
      "score_status",
      "strengths",
      "misses"
    ]) : {},
    forecast_freeze: pkg?.forecast_freeze ? pick(pkg.forecast_freeze, [
      "breadth_condition",
      "btc_range_low",
      "btc_range_high",
      "eth_range_low",
      "eth_range_high",
      "structural_calls"
    ]) : {}
  };
}

async function readJson(path) {
  return JSON.parse(await readFile(path, "utf8"));
}

function publicationMeta(filename) {
  const match = filename.match(/CYCLE_NAVIGATOR_(\d+)_X_PUBLISHED_(\d{4}-\d{2}-\d{2})\.md$/);
  if (!match) return null;
  return { issue: Number(match[1]), date: match[2], filename };
}

function extractManiaWindow(text) {
  const table = String(text).match(/Broad altseason mania\s*\|\s*([^|\n]+)\|/i);
  if (table) return table[1].trim();
  const prose = String(text).match(/altseason mania[^\n.]*?(~?\d+\s*[–—-]\s*\d+\s*weeks[^\n.]*)/i);
  return prose ? prose[1].trim() : null;
}

async function publicHistory() {
  const candidates = [];
  try {
    const yearDirs = await readdir(PUBLISHED_ROOT, { withFileTypes: true });
    for (const year of yearDirs.filter((entry) => entry.isDirectory())) {
      const yearPath = resolve(PUBLISHED_ROOT, year.name);
      const files = await readdir(yearPath);
      for (const filename of files) {
        const meta = publicationMeta(filename);
        if (meta) candidates.push({ ...meta, path: resolve(yearPath, filename) });
      }
    }
  } catch {
    return {};
  }

  candidates.sort((a, b) => `${b.date}-${String(b.issue).padStart(4, "0")}`.localeCompare(`${a.date}-${String(a.issue).padStart(4, "0")}`));
  if (!candidates.length) return {};

  const latest = candidates[0];
  const latestText = await readFile(latest.path, "utf8");
  let historicalMania = null;

  for (const candidate of candidates) {
    const text = candidate.path === latest.path ? latestText : await readFile(candidate.path, "utf8");
    const window = extractManiaWindow(text);
    if (window) {
      historicalMania = {
        issue: candidate.issue,
        date: candidate.date,
        window
      };
      break;
    }
  }

  return {
    latest_published_x: {
      issue: latest.issue,
      date: latest.date,
      text: latestText
    },
    historical_mania_reference: historicalMania
  };
}

async function main() {
  const pointer = await readJson(POINTER_PATH);
  const weekDir = String(pointer.week_dir || "");
  if (!weekDir.startsWith("05_CYCLE_NAVIGATOR/weekly/") || weekDir.includes("..")) {
    throw new Error("Refusing to build from an invalid Cycle Navigator week_dir");
  }

  const packagePath = resolve(repoRoot, weekDir, "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json");
  const pkg = await readJson(packagePath);
  const history = await publicHistory();

  const publicSnapshot = {
    schema_version: "CYCLE_NAVIGATOR_PUBLIC_SNAPSHOT_V2",
    generated_at_utc: new Date().toISOString(),
    pointer: sanitizePointer(pointer),
    package: sanitizePackage(pkg),
    public_history: history
  };

  await rm(outputDir, { recursive: true, force: true });
  await mkdir(dataDir, { recursive: true });

  for (const file of PUBLIC_SITE_FILES) {
    await copyFile(resolve(siteDir, file), resolve(outputDir, file));
  }

  await writeFile(resolve(dataDir, "latest.json"), `${JSON.stringify(publicSnapshot, null, 2)}\n`, "utf8");
  console.log(`Built privacy-safe Cycle Navigator public bundle at ${outputDir}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
