import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteDir = dirname(fileURLToPath(import.meta.url));
const snapshotPath = resolve(siteDir, "dist/data/latest.json");
const snapshot = JSON.parse(await readFile(snapshotPath, "utf8"));
const live = snapshot?.calibration?.current?.live_precision;

function fail(message) {
  throw new Error(message);
}

if (!live || live.contract !== "CYCLE_NAVIGATOR_LIVE_PRECISION_OBSERVATION_v1") fail("live precision contract missing");
if (live.authority !== "OBSERVATION_ONLY_NO_FORECAST_OR_SCORE_AUTHORITY") fail("live precision authority firewall failed");
if (live.provisional_score !== null) fail("live precision must never publish a synthetic provisional score");
if (snapshot?.calibration?.current?.provisional_score !== null) fail("official current-week provisional score must remain null");
if (Number(live.issue_number) !== Number(snapshot?.package?.issue_number ?? snapshot?.pointer?.issue_number)) fail("live precision issue lineage mismatch");

const tests = Array.isArray(live.tests) ? live.tests : [];
if (Number(live.total_count) !== tests.length) fail("live precision test count mismatch");
const ids = tests.map((row) => String(row?.claim_id || ""));
if (ids.some((id) => !id) || new Set(ids).size !== ids.length) fail("live precision test ids invalid or duplicated");

const allowed = new Set([
  "CURRENTLY_ON_TRACK",
  "CURRENTLY_OFF_TRACK",
  "PROXY_ONLY",
  "WAITING_FOR_WEEK_CLOSE",
  "WAITING_FOR_EVIDENCE",
  "STALE"
]);
for (const row of tests) {
  if (!allowed.has(String(row?.status || ""))) fail(`invalid live precision status: ${row?.status}`);
  if (Object.prototype.hasOwnProperty.call(row, "score")) fail("live precision rows must not expose settlement scores");
}

const observed = tests.filter((row) => ["CURRENTLY_ON_TRACK", "CURRENTLY_OFF_TRACK", "PROXY_ONLY"].includes(row.status)).length;
if (Number(live.observed_count) !== observed) fail("live precision observed count mismatch");
const direct = tests.filter((row) => ["CURRENTLY_ON_TRACK", "CURRENTLY_OFF_TRACK"].includes(row.status)).length;
if (Number(live.direct_check_count) !== direct) fail("live precision direct-check count mismatch");
if (direct > 1) fail("live precision unexpectedly has multiple direct settlement-like checks");

if (tests.some((row) => row.family === "breadth" && row.status === "PROXY_ONLY" && !/proxy/i.test(String(row.evidence || "")))) {
  fail("proxy breadth must stay explicitly labelled proxy-only");
}

const serialized = JSON.stringify(live).toLowerCase();
for (const forbidden of ["github.com", "raw.githubusercontent.com", "donh91", "investering-framework-archive-v1", "week_dir", "private_key", "api_key", "portfolio_size", "position_size"]) {
  if (serialized.includes(forbidden)) fail(`privacy/firewall leak in live precision: ${forbidden}`);
}

if (live.package_coverage === "LIMITED_COVERAGE" && snapshot?.package?.status !== "DEGRADED") fail("limited-coverage mapping drift");
if (snapshot?.package?.status === "DEGRADED" && live.package_coverage !== "LIMITED_COVERAGE") fail("degraded package must map to public limited coverage");

console.log(JSON.stringify({
  status: "PASS",
  issue_number: live.issue_number,
  live_status: live.status,
  observed_count: live.observed_count,
  total_count: live.total_count,
  direct_check_count: live.direct_check_count,
  provisional_score: live.provisional_score,
  authority: live.authority
}, null, 2));
