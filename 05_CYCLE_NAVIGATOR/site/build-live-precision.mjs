import { readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(siteDir, "../..");
const snapshotPath = resolve(siteDir, "dist/data/latest.json");
const pointerPath = resolve(repoRoot, "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json");
const hourlyPointerPath = resolve(repoRoot, "03_DAILY_CAPTURE_LOGS/hourly/LATEST.json");
const breadthPath = resolve(repoRoot, "03_DAILY_CAPTURE_LOGS/breadth_rich/LATEST.json");

const AUTHORITY = "OBSERVATION_ONLY_NO_FORECAST_OR_SCORE_AUTHORITY";
const CONTRACT = "CYCLE_NAVIGATOR_LIVE_PRECISION_OBSERVATION_v1";
const ALLOWED_TEST_STATUS = new Set([
  "CURRENTLY_ON_TRACK",
  "CURRENTLY_OFF_TRACK",
  "PROXY_ONLY",
  "WAITING_FOR_WEEK_CLOSE",
  "WAITING_FOR_EVIDENCE",
  "STALE"
]);

async function readJson(path) {
  return JSON.parse(await readFile(path, "utf8"));
}

async function readJsonOptional(path) {
  try {
    return await readJson(path);
  } catch {
    return null;
  }
}

function isoWeekStartUtc(year, week) {
  const jan4 = new Date(Date.UTC(year, 0, 4));
  const jan4Day = jan4.getUTCDay() || 7;
  const monday = new Date(jan4);
  monday.setUTCDate(jan4.getUTCDate() - jan4Day + 1 + (week - 1) * 7);
  monday.setUTCHours(0, 0, 0, 0);
  return monday;
}

function isoDate(date) {
  return date.toISOString().slice(0, 10);
}

function csvRows(text) {
  const lines = String(text || "").trim().split(/\r?\n/).filter(Boolean);
  if (lines.length < 2) return [];
  const header = lines[0].split(",");
  return lines.slice(1).map((line) => {
    const values = line.split(",");
    return Object.fromEntries(header.map((key, index) => [key, values[index] ?? ""]));
  });
}

function spotPointerComplete(pointer) {
  if (!pointer || typeof pointer !== "object") return false;
  if (pointer.status === "COMPLETE") return true;
  if (pointer.status !== "PARTIAL") return false;
  const requested = pointer.requested_hours;
  const complete = pointer.spot_complete_hours;
  return Number.isInteger(requested) && requested > 0 && Number.isInteger(complete) && requested === complete;
}

async function weeklySpotRows(year, week, hourlyPointer) {
  if (!spotPointerComplete(hourlyPointer)) return { rows: [], reason: "hourly spot owner is incomplete" };
  const boundary = new Date(String(hourlyPointer.window_end_utc || ""));
  if (!Number.isFinite(boundary.getTime())) return { rows: [], reason: "hourly spot owner has no valid window end" };
  const start = isoWeekStartUtc(year, week);
  if (boundary <= start) return { rows: [], reason: "hourly spot owner has not reached this ISO week" };

  const rows = [];
  for (let cursor = new Date(start); cursor < boundary; cursor = new Date(cursor.getTime() + 86400000)) {
    const day = isoDate(cursor);
    const [yyyy, mm] = day.split("-");
    const path = resolve(repoRoot, `03_DAILY_CAPTURE_LOGS/hourly/${yyyy}/${mm}/${day}.csv`);
    try {
      const text = await readFile(path, "utf8");
      for (const row of csvRows(text)) {
        if (row.spot_status !== "PASS") continue;
        const ts = new Date(row.timestamp_utc);
        if (!Number.isFinite(ts.getTime()) || ts < start || ts >= boundary) continue;
        if (!row.ethbtc_open || !row.ethbtc_close) continue;
        rows.push(row);
      }
    } catch {
      // Missing day remains fail-closed below. No synthetic backfill.
    }
  }
  rows.sort((a, b) => new Date(a.timestamp_utc) - new Date(b.timestamp_utc));
  return { rows, reason: rows.length ? null : "no complete direct ETH/BTC spot rows in the current ISO week" };
}

function pctChange(open, close) {
  const a = Number(open);
  const b = Number(close);
  if (!Number.isFinite(a) || !Number.isFinite(b) || a <= 0) return null;
  return ((b / a) - 1) * 100;
}

function fmtRatio(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n.toFixed(5) : "—";
}

function fmtSigned(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return "—";
  return `${n >= 0 ? "+" : ""}${n.toFixed(2)}%`;
}

function labelForFamily(family) {
  return ({
    ethbtc: "ETH/BTC",
    breadth: "Breadth",
    regime: "Regime",
    leadership: "Leadership",
    rotation: "Rotation",
    altseason: "Altseason"
  })[family] || String(family || "Current test");
}

function publicTest(claim) {
  return {
    claim_id: String(claim.claim_id || ""),
    family: String(claim.family || ""),
    label: labelForFamily(claim.family),
    horizon: String(claim.horizon || "WEEKLY"),
    status: "WAITING_FOR_WEEK_CLOSE",
    evidence: "Frozen weekly call remains open until completed evidence closes the week."
  };
}

function breadthObservation(breadth, buildNow) {
  if (!breadth || breadth.contract !== "RICH_BREADTH_CHECKPOINT_v1") return null;
  if (breadth?.evidence_semantics?.evidence_role !== "PROXY_ONLY") return null;
  if (breadth?.authority?.binding !== false || breadth?.authority?.canonical_acceptance !== false) return null;
  const observed = new Date(String(breadth.retrieved_at_utc || breadth?.observation?.retrieval_timestamp_utc || ""));
  if (!Number.isFinite(observed.getTime())) return null;
  const ageHours = (buildNow.getTime() - observed.getTime()) / 3600000;
  if (ageHours < -0.25 || ageHours > 12) return { stale: true, observed_at_utc: observed.toISOString() };
  const aggregate = breadth.aggregate || {};
  const n = Number(aggregate.constituent_count);
  const adv = Number(aggregate.advancer_pct);
  const btc = Number(aggregate.outperforming_btc_count);
  const eth = Number(aggregate.outperforming_eth_count);
  if (![n, adv, btc, eth].every(Number.isFinite) || n <= 0) return null;
  return {
    stale: false,
    observed_at_utc: observed.toISOString(),
    constituent_count: n,
    advancer_pct: adv,
    outperforming_btc_count: btc,
    outperforming_eth_count: eth,
    canonical_broad_alt_breadth: String(breadth?.evidence_semantics?.canonical_broad_alt_breadth || "UNCONFIRMED")
  };
}

function emptyObservation(issue, reason, publicStatus) {
  return {
    contract: CONTRACT,
    authority: AUTHORITY,
    issue_number: issue,
    status: "OBSERVATION_UNAVAILABLE",
    generated_at_utc: new Date().toISOString(),
    provisional_score: null,
    observed_count: 0,
    direct_check_count: 0,
    total_count: 0,
    observation_coverage_pct: null,
    tests: [],
    package_coverage: publicStatus === "DEGRADED" ? "LIMITED_COVERAGE" : "STANDARD",
    source_note: reason,
    method_note: "Observation only. No live evidence can rewrite the frozen Cycle Navigator or the verified weekly score."
  };
}

async function main() {
  const snapshot = await readJson(snapshotPath);
  const pointer = await readJson(pointerPath);
  const issue = Number(pointer.issue_number || snapshot?.package?.issue_number || 0) || null;
  const weekDir = String(pointer.week_dir || "");
  if (!weekDir.startsWith("05_CYCLE_NAVIGATOR/weekly/") || weekDir.includes("..")) {
    throw new Error("Refusing live observation from invalid Cycle Navigator week_dir");
  }

  const freezePath = resolve(repoRoot, weekDir, "CYCLE_NAVIGATOR_INTERNAL_PRECISION_FREEZE.json");
  const freeze = await readJsonOptional(freezePath);
  if (!freeze || freeze.contract !== "CYCLE_NAVIGATOR_INTERNAL_PRECISION_FREEZE_v2" || Number(freeze.issue_number) !== issue) {
    snapshot.calibration ||= {};
    snapshot.calibration.current ||= {};
    snapshot.calibration.current.live_precision = emptyObservation(issue, "Current immutable precision freeze is not available yet; live checking remains closed.", snapshot?.package?.status);
    await writeFile(snapshotPath, `${JSON.stringify(snapshot, null, 2)}\n`, "utf8");
    console.log("Live precision observer: awaiting current immutable freeze");
    return;
  }

  const headlineWeeklyClaims = (Array.isArray(freeze.claims) ? freeze.claims : [])
    .filter((claim) => claim?.horizon === "WEEKLY" && !claim?.alias_of);
  const tests = headlineWeeklyClaims.map(publicTest);
  const byFamily = new Map(tests.map((test) => [test.family, test]));
  const buildNow = new Date();

  let observedCount = 0;
  let directCheckCount = 0;
  let asOf = null;

  const hourlyPointer = await readJsonOptional(hourlyPointerPath);
  const spot = await weeklySpotRows(Number(pointer.iso_year), Number(pointer.iso_week), hourlyPointer);
  const ethbtc = byFamily.get("ethbtc");
  if (ethbtc && spot.rows.length) {
    const expectedStart = isoWeekStartUtc(Number(pointer.iso_year), Number(pointer.iso_week)).toISOString();
    const openRow = spot.rows.find((row) => row.timestamp_utc === expectedStart);
    const latest = spot.rows.at(-1);
    const boundary = new Date(String(hourlyPointer?.window_end_utc || ""));
    const ageHours = Number.isFinite(boundary.getTime()) ? (buildNow.getTime() - boundary.getTime()) / 3600000 : Infinity;
    if (openRow && latest && ageHours >= -0.25 && ageHours <= 8) {
      const change = pctChange(openRow.ethbtc_open, latest.ethbtc_close);
      if (change != null) {
        ethbtc.status = change >= 0 ? "CURRENTLY_ON_TRACK" : "CURRENTLY_OFF_TRACK";
        ethbtc.evidence = `ETH/BTC is ${fmtSigned(change)} from the W${pointer.iso_week} open (${fmtRatio(openRow.ethbtc_open)} → ${fmtRatio(latest.ethbtc_close)}). This is a live directional check, not a settled weekly score.`;
        ethbtc.observed_at_utc = boundary.toISOString();
        observedCount += 1;
        directCheckCount += 1;
        asOf = boundary.toISOString();
      }
    } else if (ageHours > 8) {
      ethbtc.status = "STALE";
      ethbtc.evidence = "Direct ETH/BTC owner data is stale; no current directional check is published.";
    } else if (!openRow) {
      ethbtc.status = "WAITING_FOR_EVIDENCE";
      ethbtc.evidence = "The exact ISO-week opening ETH/BTC candle is unavailable, so no open-to-now comparison is inferred.";
    }
  } else if (ethbtc && spot.reason) {
    ethbtc.status = "WAITING_FOR_EVIDENCE";
    ethbtc.evidence = spot.reason;
  }

  const breadth = breadthObservation(await readJsonOptional(breadthPath), buildNow);
  const breadthTest = byFamily.get("breadth");
  if (breadthTest && breadth && !breadth.stale) {
    breadthTest.status = "PROXY_ONLY";
    breadthTest.evidence = `${Math.round(breadth.advancer_pct)}% advancers; ${breadth.outperforming_btc_count}/${breadth.constituent_count} outperform BTC and ${breadth.outperforming_eth_count}/${breadth.constituent_count} outperform ETH over the source-reported 24h window. Owner semantics remain proxy-only and canonical broad-alt breadth is ${breadth.canonical_broad_alt_breadth}.`;
    breadthTest.observed_at_utc = breadth.observed_at_utc;
    observedCount += 1;
    if (!asOf || breadth.observed_at_utc > asOf) asOf = breadth.observed_at_utc;
  } else if (breadthTest && breadth?.stale) {
    breadthTest.status = "STALE";
    breadthTest.evidence = "Proxy breadth capture is stale; no current breadth observation is published.";
  } else if (breadthTest) {
    breadthTest.status = "WAITING_FOR_EVIDENCE";
    breadthTest.evidence = "No fresh, provenance-bounded proxy breadth observation is available.";
  }

  for (const test of tests) {
    if (!ALLOWED_TEST_STATUS.has(test.status)) throw new Error(`Unexpected live observation status: ${test.status}`);
  }

  const totalCount = tests.length;
  const observation = {
    contract: CONTRACT,
    authority: AUTHORITY,
    issue_number: issue,
    iso_year: Number(pointer.iso_year),
    iso_week: Number(pointer.iso_week),
    status: observedCount ? "OBSERVING" : "OBSERVATION_UNAVAILABLE",
    generated_at_utc: buildNow.toISOString(),
    as_of_utc: asOf,
    provisional_score: null,
    observed_count: observedCount,
    direct_check_count: directCheckCount,
    total_count: totalCount,
    observation_coverage_pct: totalCount ? Math.round((10000 * observedCount) / totalCount) / 100 : null,
    package_coverage: snapshot?.package?.status === "DEGRADED" ? "LIMITED_COVERAGE" : "STANDARD",
    tests,
    source_note: "Direct hourly ETH/BTC owner data plus proxy-only rich breadth. No hidden substitution, no live portfolio authority, and no browser-created market call.",
    method_note: "Current-week observations remain provisional and unscored. Aliases are excluded, proxy breadth cannot create a rotation vote, and only completed-week evidence can produce the verified weekly score."
  };

  snapshot.calibration ||= {};
  snapshot.calibration.current ||= {};
  snapshot.calibration.current.live_precision = observation;
  // Preserve the official current-week score as null. The live layer is not a score authority.
  snapshot.calibration.current.provisional_score = null;
  await writeFile(snapshotPath, `${JSON.stringify(snapshot, null, 2)}\n`, "utf8");
  console.log(`Live precision observer: CN #${issue}, ${observedCount}/${totalCount} observable, ${directCheckCount} direct check(s)`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
