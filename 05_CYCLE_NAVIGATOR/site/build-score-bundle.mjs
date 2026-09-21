import { copyFile, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { isDeepStrictEqual } from "node:util";

const siteDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(siteDir, "../..");
const distDir = resolve(siteDir, "dist");
const pointerPath = resolve(repoRoot, "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json");
const snapshotPath = resolve(distDir, "data/latest.json");
const distIndexPath = resolve(distDir, "index.html");
const sourceWidgetPath = resolve(siteDir, "weekly-score.js");
const distWidgetPath = resolve(distDir, "weekly-score.js");

async function readJson(path) {
  return JSON.parse(await readFile(path, "utf8"));
}

function pick(obj, keys) {
  return Object.fromEntries(
    keys
      .filter((key) => Object.prototype.hasOwnProperty.call(obj || {}, key))
      .map((key) => [key, obj[key]])
  );
}

function sanitizeParameterScores(rows) {
  if (!Array.isArray(rows)) return [];
  return rows
    .filter((row) => row && typeof row === "object")
    .map((row) => pick(row, ["parameter_id", "status", "score", "evidence"]));
}

function sanitizeScorecard(scorecard) {
  return {
    authority: "CYCLE_NAVIGATOR_SCORECARD",
    ...pick(scorecard, [
      "contract",
      "issue_scored",
      "completed_iso_week",
      "score_status",
      "structural_score",
      "price_range_score",
      "decision_utility_score",
      "public_continuity_score",
      "parameter_coverage_pct",
      "method_note",
      "strengths",
      "misses"
    ]),
    parameter_scores: sanitizeParameterScores(scorecard?.parameter_scores)
  };
}

function requireNumberOrNull(value, field) {
  if (value === null || value === undefined) return;
  if (!Number.isFinite(Number(value))) throw new Error(`Invalid numeric score field: ${field}`);
  const n = Number(value);
  if (n < 0 || n > 100) throw new Error(`Out-of-bounds score field: ${field}`);
}

async function main() {
  const pointer = await readJson(pointerPath);
  const weekDir = String(pointer.week_dir || "");
  if (!weekDir.startsWith("05_CYCLE_NAVIGATOR/weekly/") || weekDir.includes("..")) {
    throw new Error("Refusing score bundle from invalid week_dir");
  }

  const weekRoot = resolve(repoRoot, weekDir);
  const scorecard = await readJson(resolve(weekRoot, "CYCLE_NAVIGATOR_SCORECARD.json"));
  const machine = await readJson(resolve(weekRoot, "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json"));
  const snapshot = await readJson(snapshotPath);

  const scorecardEvaluation = Object.fromEntries(
    Object.entries(scorecard).filter(([key]) => !["contract", "issue_scored", "completed_iso_week"].includes(key))
  );
  if (!machine?.evaluation || !isDeepStrictEqual(machine.evaluation, scorecardEvaluation)) {
    throw new Error("CN score authority mismatch: machine evaluation and scorecard evaluation payload differ");
  }
  if (Number(scorecard.issue_scored || 0) !== Number(machine.previous_issue_number || 0)) {
    throw new Error("CN score authority mismatch: scorecard issue_scored does not match previous issue");
  }
  if (Number(scorecard.completed_iso_week || 0) !== Number(pointer.completed_source_week || 0)) {
    throw new Error("CN score authority mismatch: completed week does not match delivery pointer");
  }

  for (const field of ["structural_score", "price_range_score", "decision_utility_score", "public_continuity_score", "parameter_coverage_pct"]) {
    requireNumberOrNull(scorecard[field], field);
  }

  snapshot.weekly_score_bundle = sanitizeScorecard(scorecard);
  snapshot.score_authority_note = "Weekly public scores come directly from the canonical Cycle Navigator scorecard generated after final Master Monday. X is downstream publication only and is never an input to the website score.";
  await writeFile(snapshotPath, `${JSON.stringify(snapshot, null, 2)}\n`, "utf8");

  await copyFile(sourceWidgetPath, distWidgetPath);
  let index = await readFile(distIndexPath, "utf8");
  const tag = '<script src="./weekly-score.js" defer></script>';
  if (!index.includes(tag)) {
    if (!index.includes("</body>")) throw new Error("Cannot inject weekly score widget: </body> missing");
    index = index.replace("</body>", `  ${tag}\n</body>`);
    await writeFile(distIndexPath, index, "utf8");
  }

  console.log(`Bound public snapshot to ${scorecard.contract || "CYCLE_NAVIGATOR_SCORECARD"} for CN #${scorecard.issue_scored ?? "?"}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
