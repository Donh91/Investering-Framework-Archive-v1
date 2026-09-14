import { createHash } from "node:crypto";
import { copyFile, readFile, readdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(siteDir, "../..");
const distDir = resolve(siteDir, "dist");
const pointerPath = resolve(repoRoot, "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json");
const hourlyPointerPath = resolve(repoRoot, "03_DAILY_CAPTURE_LOGS/hourly/LATEST.json");
const hourlyRoot = resolve(repoRoot, "03_DAILY_CAPTURE_LOGS/hourly");
const capturesRoot = resolve(repoRoot, "03_DAILY_CAPTURE_LOGS/captures");
const snapshotPath = resolve(distDir, "data/latest.json");
const indexPath = resolve(distDir, "index.html");
const widgetSource = resolve(siteDir, "live-observation.js");
const widgetDist = resolve(distDir, "live-observation.js");
const copySource = resolve(siteDir, "public-copy.js");
const copyDist = resolve(distDir, "public-copy.js");

const readJson = async (path) => JSON.parse(await readFile(path, "utf8"));
const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");
const numeric = (value) => value != null && value !== "" && Number.isFinite(Number(value));
const round = (value, digits = 2) => Number(Number(value).toFixed(digits));

function safeWeekDir(pointer) {
  const weekDir = String(pointer?.week_dir || "");
  if (!weekDir.startsWith("05_CYCLE_NAVIGATOR/weekly/") || weekDir.includes("..")) {
    throw new Error("Refusing LIVE observation from invalid week_dir");
  }
  return weekDir;
}

function isoWeekStartUtc(year, week) {
  const jan4 = new Date(Date.UTC(year, 0, 4));
  const jan4MondayOffset = (jan4.getUTCDay() + 6) % 7;
  return Date.UTC(year, 0, 4 - jan4MondayOffset + (week - 1) * 7, 0, 0, 0, 0);
}

function utcDays(startMs, endMs) {
  if (!Number.isFinite(startMs) || !Number.isFinite(endMs) || endMs <= startMs) return [];
  const out = [];
  let cursor = Date.UTC(new Date(startMs).getUTCFullYear(), new Date(startMs).getUTCMonth(), new Date(startMs).getUTCDate());
  const last = endMs - 1;
  while (cursor <= last) {
    const d = new Date(cursor);
    out.push({
      year: String(d.getUTCFullYear()),
      month: String(d.getUTCMonth() + 1).padStart(2, "0"),
      day: String(d.getUTCDate()).padStart(2, "0")
    });
    cursor += 86400000;
  }
  return out;
}

function parseCsv(text) {
  const lines = String(text || "").trim().split(/\r?\n/).filter(Boolean);
  if (lines.length < 2) return [];
  const header = lines[0].split(",");
  return lines.slice(1).map((line) => {
    const values = line.split(",");
    return Object.fromEntries(header.map((key, index) => [key, values[index] ?? ""]));
  });
}

async function readHourlyRows(startMs, endMs) {
  const byTs = new Map();
  for (const day of utcDays(startMs, endMs)) {
    const path = resolve(hourlyRoot, day.year, day.month, `${day.year}-${day.month}-${day.day}.csv`);
    let text;
    try {
      text = await readFile(path, "utf8");
    } catch (error) {
      if (error?.code === "ENOENT") continue;
      throw error;
    }
    for (const row of parseCsv(text)) {
      const ts = Date.parse(String(row.timestamp_utc || ""));
      if (!Number.isFinite(ts) || ts < startMs || ts >= endMs || row.spot_status !== "PASS") continue;
      if (![row.btc_close, row.eth_close, row.ethbtc_close].every(numeric)) continue;
      byTs.set(ts, row);
    }
  }
  return [...byTs.entries()].sort((a, b) => a[0] - b[0]).map(([ts, row]) => ({ ts, ...row }));
}

async function latestEligibleCapture(startMs, endMs) {
  let latest = null;
  for (const day of utcDays(startMs, endMs)) {
    const dir = resolve(capturesRoot, day.year, day.month, day.day);
    let names = [];
    try {
      names = await readdir(dir);
    } catch (error) {
      if (error?.code === "ENOENT") continue;
      throw error;
    }
    for (const name of names.filter((item) => item.endsWith(".json")).sort()) {
      const path = resolve(dir, name);
      let value;
      try {
        value = await readJson(path);
      } catch {
        continue;
      }
      const ts = Date.parse(String(value?.captured_at_utc || ""));
      if (!Number.isFinite(ts) || ts < startMs || ts >= endMs) continue;
      if (!latest || ts > latest.ts) latest = { ts, value };
    }
  }
  return latest;
}

function rangeRows(freeze, hourlyRows) {
  const specs = [
    ["BTC", "btc", freeze?.btc_range_low, freeze?.btc_range_high],
    ["ETH", "eth", freeze?.eth_range_low, freeze?.eth_range_high]
  ].filter(([, , low, high]) => numeric(low) && numeric(high));

  return specs.map(([asset, prefix, low, high]) => {
    const observedLows = hourlyRows.map((row) => Number(row[`${prefix}_low`])).filter(Number.isFinite);
    const observedHighs = hourlyRows.map((row) => Number(row[`${prefix}_high`])).filter(Number.isFinite);
    const observedLow = observedLows.length ? Math.min(...observedLows) : null;
    const observedHigh = observedHighs.length ? Math.max(...observedHighs) : null;
    const breached = observedLow != null && observedHigh != null && (observedLow < Number(low) || observedHigh > Number(high));
    return {
      asset,
      low: Number(low),
      high: Number(high),
      observed_low: observedLow,
      observed_high: observedHigh,
      status: observedLow == null || observedHigh == null ? "OPEN" : breached ? "BREACHED" : "IN_RANGE_SO_FAR",
      score: observedLow == null || observedHigh == null ? null : breached ? 0 : 100
    };
  });
}

function ethbtcEvidence(hourlyRows) {
  if (!hourlyRows.length) return null;
  const first = hourlyRows[0];
  const last = hourlyRows.at(-1);
  const open = numeric(first.ethbtc_open) ? Number(first.ethbtc_open) : Number(first.ethbtc_close);
  const close = Number(last.ethbtc_close);
  if (!Number.isFinite(open) || open <= 0 || !Number.isFinite(close)) return null;
  const changePct = ((close / open) - 1) * 100;
  return {
    status: changePct >= 0 ? "ON_TRACK" : "OFF_TRACK",
    score: changePct >= 0 ? 100 : 0,
    evidence: `ETH/BTC WTD ${changePct >= 0 ? "+" : ""}${round(changePct, 2)}%`,
    source: "DIRECT_HOURLY_SPOT"
  };
}

function altseasonEvidence(capture) {
  const context = capture?.market_metrics?.rotation_context || {};
  const bc = context?.blockchaincenter_altcoin_season;
  const state = String(bc?.horizons?.["90"]?.source_state || "").toUpperCase();
  const reconciliation = String(bc?.horizons?.["90"]?.score_reconciliation || "").toUpperCase();
  if (bc?.status !== "PASS" || reconciliation !== "PASS_EXACT" || !state) return null;
  if (["BITCOIN_SEASON", "BETWEEN_PUBLISHED_THRESHOLDS", "NO_ALTSEASON", "NEUTRAL"].includes(state)) {
    return {
      status: "ON_TRACK",
      score: 100,
      evidence: "Published 90d altseason state remains below broad-altseason confirmation",
      source: "PUBLISHED_ALTSEASON_STATE"
    };
  }
  if (["ALTCOIN_SEASON", "ALTSEASON"].includes(state)) {
    return {
      status: "OFF_TRACK",
      score: 0,
      evidence: "Published 90d altseason state has moved into altseason",
      source: "PUBLISHED_ALTSEASON_STATE"
    };
  }
  return null;
}

function statusForFamily(family, hourlyRows, capture) {
  if (family === "ethbtc") return ethbtcEvidence(hourlyRows);
  if (family === "altseason") return altseasonEvidence(capture);
  return null;
}

function averageScore(rows) {
  const values = rows.map((row) => row.score).filter((value) => Number.isFinite(Number(value))).map(Number);
  return values.length ? round(values.reduce((a, b) => a + b, 0) / values.length, 1) : null;
}

async function main() {
  const pointer = await readJson(pointerPath);
  const weekDir = safeWeekDir(pointer);
  const root = resolve(repoRoot, weekDir);
  const publicFreezePath = resolve(root, "CYCLE_NAVIGATOR_FORECAST_FREEZE.json");
  const internalFreezePath = resolve(root, "CYCLE_NAVIGATOR_INTERNAL_PRECISION_FREEZE.json");

  const publicFreezeBytes = await readFile(publicFreezePath);
  const publicFreezeHash = sha256(publicFreezeBytes);
  if (publicFreezeHash !== String(pointer.forecast_freeze_sha256 || "")) {
    throw new Error("LIVE observation refused: public forecast-freeze hash mismatch");
  }

  const publicFreeze = JSON.parse(publicFreezeBytes.toString("utf8"));
  const internalFreeze = await readJson(internalFreezePath);
  if (String(internalFreeze.source_public_freeze_sha256 || "") !== publicFreezeHash) {
    throw new Error("LIVE observation refused: internal precision freeze is not bound to current public freeze");
  }
  if (Number(internalFreeze.issue_number) !== Number(pointer.issue_number)) {
    throw new Error("LIVE observation refused: frozen-claim issue mismatch");
  }

  const isoYear = Number(pointer.iso_year);
  const isoWeek = Number(pointer.iso_week);
  const weekStartMs = isoWeekStartUtc(isoYear, isoWeek);
  const weekEndMs = weekStartMs + 7 * 86400000;
  const hourlyPointer = await readJson(hourlyPointerPath);
  const rawHourlyEndMs = Date.parse(String(hourlyPointer.window_end_utc || ""));
  const effectiveEndMs = Math.min(Number.isFinite(rawHourlyEndMs) ? rawHourlyEndMs : Date.now(), weekEndMs);
  const readEndMs = Math.max(weekStartMs, effectiveEndMs);
  const hourlyRows = await readHourlyRows(weekStartMs, readEndMs);
  const capture = (await latestEligibleCapture(weekStartMs, Math.max(weekStartMs + 1, readEndMs)))?.value || null;

  const internalClaims = Array.isArray(internalFreeze.claims) ? internalFreeze.claims : [];
  const structuralCalls = Array.isArray(publicFreeze.structural_calls) ? publicFreeze.structural_calls : [];
  const tests = structuralCalls.map((forecast, index) => {
    const sourceParameterId = `structural_call_${index + 1}`;
    const internal = internalClaims.find((claim) => claim?.source_parameter_id === sourceParameterId) || {};
    const observed = statusForFamily(String(internal.family || ""), hourlyRows, capture);
    return {
      test_id: index + 1,
      source_parameter_id: sourceParameterId,
      family: String(internal.family || "structural"),
      forecast,
      status: observed?.status || "OPEN",
      score: observed?.score ?? null,
      evidence: observed?.evidence || "Awaiting a direct eligible observation for this frozen call.",
      source: observed?.source || "NO_DIRECT_OBSERVATION_YET"
    };
  });

  const provisionalScore = averageScore(tests);
  const evaluableCount = tests.filter((test) => Number.isFinite(Number(test.score))).length;
  const ranges = rangeRows(publicFreeze, hourlyRows);
  const priceTrackingScore = averageScore(ranges);
  const nowMs = Date.now();
  const maturityState = nowMs >= weekEndMs ? "HELD" : "LIVE";
  const observationThrough = hourlyRows.length ? new Date(hourlyRows.at(-1).ts).toISOString() : null;
  const lastRowAgeHours = hourlyRows.length ? Math.max(0, (nowMs - hourlyRows.at(-1).ts) / 3600000) : null;
  const freshness = lastRowAgeHours == null ? "WAITING" : lastRowAgeHours <= 12 ? "CURRENT" : "STALE";

  const snapshot = await readJson(snapshotPath);
  snapshot.calibration = snapshot.calibration || {};
  snapshot.calibration.current = {
    status: maturityState,
    provisional_score: provisionalScore,
    evaluable_count: evaluableCount,
    total_count: tests.length,
    frozen_test_count: tests.length,
    issue_number: Number(pointer.issue_number),
    observation_through_utc: observationThrough
  };
  snapshot.live_observation = {
    contract: "CYCLE_NAVIGATOR_PUBLIC_LIVE_OBSERVATION_v2",
    authority: "NON_AUTHORITATIVE_OBSERVATION_ONLY",
    issue_number: Number(pointer.issue_number),
    iso_year: isoYear,
    iso_week: isoWeek,
    maturity_state: maturityState,
    freshness,
    observation_through_utc: observationThrough,
    frozen_claim_count: tests.length,
    evaluable_count: evaluableCount,
    open_count: Math.max(0, tests.length - evaluableCount),
    provisional_score: provisionalScore,
    provisional_score_status: provisionalScore == null ? "CALIBRATING" : maturityState === "HELD" ? "HELD_AT_WEEK_END" : "LIVE_PARTIAL",
    tests,
    frozen_numeric_ranges: ranges,
    live_price_scoring_allowed: ranges.length > 0,
    price_tracking_score: priceTrackingScore,
    official_weekly_scores_mutable: false,
    forecast_mutable: false,
    note: maturityState === "HELD"
      ? "The provisional week view is held at the final eligible observation until a new Cycle Navigator issue starts."
      : provisionalScore == null
        ? "The frozen Monday calls are live, but none has a direct measurable observation yet."
        : `${evaluableCount}/${tests.length} frozen Monday calls are directly measurable so far. The percentage is provisional until the next official weekly score closes the issue.`
  };

  await writeFile(snapshotPath, `${JSON.stringify(snapshot, null, 2)}\n`, "utf8");
  await copyFile(widgetSource, widgetDist);
  await copyFile(copySource, copyDist);

  let index = await readFile(indexPath, "utf8");
  for (const script of ["./live-observation.js", "./public-copy.js"]) {
    if (!index.includes(script)) index = index.replace("</body>", `  <script src="${script}"></script>\n</body>`);
  }
  await writeFile(indexPath, index, "utf8");

  console.log(JSON.stringify({
    status: "PASS",
    issue_number: pointer.issue_number,
    maturity_state: maturityState,
    evaluable_count: evaluableCount,
    frozen_claim_count: tests.length,
    provisional_score: provisionalScore,
    price_tracking_score: priceTrackingScore,
    observation_through_utc: observationThrough,
    authority: "NON_AUTHORITATIVE_OBSERVATION_ONLY"
  }));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});