import { mkdir, readFile, readdir, rm, writeFile, copyFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(siteDir, "../..");
const outputDir = resolve(siteDir, "dist");
const dataDir = resolve(outputDir, "data");

const POINTER_PATH = resolve(repoRoot, "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json");
const PUBLISHED_ROOT = resolve(repoRoot, "05_CYCLE_NAVIGATOR/published");
const TRACK_RECORD_PATH = resolve(repoRoot, "05_CYCLE_NAVIGATOR/track_record/CN_TRACK_RECORD_LEDGER.jsonl");
const PUBLIC_SITE_FILES = [
  "index.html",
  "styles.css",
  "motion.css",
  "journey.css",
  "vibe.css",
  "calibration.css",
  "app.js",
  "motion.js",
  "journey.js",
  "live-context.js",
  "calibration.js",
  "favicon.svg",
  "social-card.svg"
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
      "structural_calls",
      "forecast_horizon_days",
      "intraday_map"
    ]) : {}
  };
}

function stripMarkdown(value) {
  return String(value || "")
    .replace(/\*\*/g, "")
    .replace(/`/g, "")
    .trim();
}

function officialShortHorizon(pkg) {
  const issueNumber = Number(pkg?.issue_number || 0) || null;
  const map = pkg?.forecast_freeze?.intraday_map;
  if (map && typeof map === "object") {
    const day12 = stripMarkdown(map.day_1_2);
    const day34 = stripMarkdown(map.day_3_4);
    const day57 = stripMarkdown(map.day_5_7);
    const published = [day12, day34, day57].some((value) => value && value.toUpperCase() !== "UNAVAILABLE");
    return {
      authority: "OFFICIAL_CN",
      issue_number: issueNumber,
      status: published ? "INTRADAY_MAP" : "UNAVAILABLE",
      day_1_2: day12 || "UNAVAILABLE",
      day_3_4: day34 || "UNAVAILABLE",
      day_5_7: day57 || "UNAVAILABLE",
      risk_bias: null,
      note: published
        ? "Frozen OFFICIAL Cycle Navigator intraday map. Missing buckets remain UNAVAILABLE."
        : "The OFFICIAL Cycle Navigator freeze did not publish an evaluable intraday map."
    };
  }

  const source = `${String(pkg?.readable_markdown || "")}\n${String(pkg?.x_ready_markdown || "")}`;
  const riskMatch = source.match(/Near-term\s+risk\s*:\s*\*{0,2}([^\n*]+?)\*{0,2}(?:\s*$|\n)/im);
  if (riskMatch) {
    const riskBias = stripMarkdown(riskMatch[1]).replace(/[.;]+$/, "");
    if (riskBias) {
      return {
        authority: "OFFICIAL_CN",
        issue_number: issueNumber,
        status: "RISK_BIAS_ONLY",
        day_1_2: null,
        day_3_4: null,
        day_5_7: null,
        risk_bias: riskBias,
        note: "Verbatim OFFICIAL Cycle Navigator near-term risk label. This is a risk bias, not a reconstructed 24–72h price forecast."
      };
    }
  }

  return {
    authority: "OFFICIAL_CN",
    issue_number: issueNumber,
    status: "UNAVAILABLE",
    day_1_2: null,
    day_3_4: null,
    day_5_7: null,
    risk_bias: null,
    note: "No OFFICIAL short-horizon map is published for this issue. LIVE prices never create one."
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

function extractXPrecisionClaim(text, publicationIssue, date) {
  const source = String(text || "");
  const scoredIssueMatch = source.match(/WEEKLY\s+PRECISION\s*,?\s*CN\s*#(\d+)/i)
    || source.match(/COMPLETE\s+SCORECARD\s*[—–-]?\s*#(\d+)/i);
  const overallMatch = source.match(/Overall\s+precision\s*:\s*\*{0,2}\s*(\d+(?:\.\d+)?)\s*(?:%|\/\s*100)/i);
  if (!scoredIssueMatch || !overallMatch) return null;

  const components = {};
  const componentPatterns = [
    ["cycle_structure", /Cycle structure\s*:\s*\*{0,2}\s*(\d+(?:\.\d+)?)\s*(?:%|\/\s*100)/i],
    ["ethbtc_transition", /ETH\/BTC transition\s*:\s*\*{0,2}\s*(\d+(?:\.\d+)?)\s*(?:%|\/\s*100)/i],
    ["breadth_participation", /Breadth\s*\/\s*participation\s*:\s*\*{0,2}\s*(\d+(?:\.\d+)?)\s*(?:%|\/\s*100)/i],
    ["rotation_sequencing", /Rotation sequencing\s*:\s*\*{0,2}\s*(\d+(?:\.\d+)?)\s*(?:%|\/\s*100)/i],
    ["altseason_timing", /Altseason timing\s*:\s*\*{0,2}\s*(\d+(?:\.\d+)?)\s*(?:%|\/\s*100)/i],
    ["deployment_sequencing", /Deployment sequencing\s*:\s*\*{0,2}\s*(\d+(?:\.\d+)?)\s*(?:%|\/\s*100)/i],
    ["btc_price_ranges", /BTC price ranges\s*:\s*\*{0,2}\s*(\d+(?:\.\d+)?)\s*(?:%|\/\s*100)/i],
    ["eth_price_ranges", /ETH price ranges\s*:\s*\*{0,2}\s*(\d+(?:\.\d+)?)\s*(?:%|\/\s*100)/i]
  ];
  for (const [key, pattern] of componentPatterns) {
    const match = source.match(pattern);
    if (match) components[key] = Number(match[1]);
  }

  return {
    publication_issue: publicationIssue,
    scored_issue: Number(scoredIssueMatch[1]),
    date,
    overall_precision: Number(overallMatch[1]),
    components
  };
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
  const xPrecisionClaims = [];

  for (const candidate of candidates) {
    const text = candidate.path === latest.path ? latestText : await readFile(candidate.path, "utf8");
    if (!historicalMania) {
      const window = extractManiaWindow(text);
      if (window) {
        historicalMania = {
          issue: candidate.issue,
          date: candidate.date,
          window
        };
      }
    }
    const claim = extractXPrecisionClaim(text, candidate.issue, candidate.date);
    if (claim) xPrecisionClaims.push(claim);
  }

  xPrecisionClaims.sort((a, b) => a.scored_issue - b.scored_issue);

  return {
    latest_published_x: {
      issue: latest.issue,
      date: latest.date,
      text: latestText
    },
    historical_mania_reference: historicalMania,
    x_precision_claims: xPrecisionClaims
  };
}

async function trackRecord() {
  try {
    const raw = await readFile(TRACK_RECORD_PATH, "utf8");
    const rows = raw
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => JSON.parse(line))
      .map((row) => pick(row, [
        "completed_iso_week",
        "issue_scored",
        "next_issue",
        "score_status",
        "structural_score",
        "price_range_score",
        "decision_utility_score",
        "public_continuity_score",
        "score_authority"
      ]))
      .sort((a, b) => Number(a.issue_scored || 0) - Number(b.issue_scored || 0));

    return { rows };
  } catch {
    return { rows: [] };
  }
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
  const track = await trackRecord();

  const publicSnapshot = {
    schema_version: "CYCLE_NAVIGATOR_PUBLIC_SNAPSHOT_V3",
    generated_at_utc: new Date().toISOString(),
    pointer: sanitizePointer(pointer),
    package: sanitizePackage(pkg),
    short_horizon: officialShortHorizon(pkg),
    public_history: history,
    calibration: {
      track_record: track,
      current: {
        issue_number: pkg?.issue_number ?? pointer?.issue_number ?? null,
        provisional_score: null,
        provisional_status: "IN_PROGRESS_UNTIL_COMPLETED_EVIDENCE",
        frozen_test_count: Array.isArray(pkg?.forecast_freeze?.structural_calls) ? pkg.forecast_freeze.structural_calls.length : 0
      }
    }
  };

  await rm(outputDir, { recursive: true, force: true });
  await mkdir(dataDir, { recursive: true });

  for (const file of PUBLIC_SITE_FILES) {
    await copyFile(resolve(siteDir, file), resolve(outputDir, file));
  }

  const socialCardBase64 = (await readFile(resolve(siteDir, "social-card.b64"), "utf8")).trim();
  await writeFile(resolve(outputDir, "social-card.png"), Buffer.from(socialCardBase64, "base64"));
  await writeFile(resolve(dataDir, "latest.json"), `${JSON.stringify(publicSnapshot, null, 2)}\n`, "utf8");
  console.log(`Built privacy-safe Cycle Navigator public bundle at ${outputDir}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
