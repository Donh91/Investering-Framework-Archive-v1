import { mkdir, readFile, rm, writeFile, copyFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(siteDir, "../..");
const outputDir = resolve(siteDir, "dist");
const dataDir = resolve(outputDir, "data");

const POINTER_PATH = resolve(repoRoot, "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json");
const PUBLIC_SITE_FILES = [
  "index.html",
  "styles.css",
  "motion.css",
  "app.js",
  "motion.js"
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
      "rotation_ladder",
      "altseason_countdown",
      "uncertainties",
      "publication_status"
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

async function main() {
  const pointer = await readJson(POINTER_PATH);
  const weekDir = String(pointer.week_dir || "");
  if (!weekDir.startsWith("05_CYCLE_NAVIGATOR/weekly/") || weekDir.includes("..")) {
    throw new Error("Refusing to build from an invalid Cycle Navigator week_dir");
  }

  const packagePath = resolve(repoRoot, weekDir, "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json");
  const pkg = await readJson(packagePath);

  const publicSnapshot = {
    schema_version: "CYCLE_NAVIGATOR_PUBLIC_SNAPSHOT_V1",
    generated_at_utc: new Date().toISOString(),
    pointer: sanitizePointer(pointer),
    package: sanitizePackage(pkg)
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
