import { createHash } from "node:crypto";
import { copyFile, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(siteDir, "../..");
const distDir = resolve(siteDir, "dist");
const pointerPath = resolve(repoRoot, "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json");
const snapshotPath = resolve(distDir, "data/latest.json");
const indexPath = resolve(distDir, "index.html");
const widgetSource = resolve(siteDir, "live-observation.js");
const widgetDist = resolve(distDir, "live-observation.js");
const copySource = resolve(siteDir, "public-copy.js");
const copyDist = resolve(distDir, "public-copy.js");

const readJson = async (path) => JSON.parse(await readFile(path, "utf8"));
const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");
const numeric = (value) => value != null && value !== "" && Number.isFinite(Number(value));

function safeWeekDir(pointer) {
  const weekDir = String(pointer?.week_dir || "");
  if (!weekDir.startsWith("05_CYCLE_NAVIGATOR/weekly/") || weekDir.includes("..")) {
    throw new Error("Refusing LIVE observation from invalid week_dir");
  }
  return weekDir;
}

function rangeRows(freeze) {
  return [
    ["BTC", freeze?.btc_range_low, freeze?.btc_range_high],
    ["ETH", freeze?.eth_range_low, freeze?.eth_range_high]
  ].filter(([, low, high]) => numeric(low) && numeric(high)).map(([asset, low, high]) => ({
    asset,
    low: Number(low),
    high: Number(high),
    status: "FROZEN_RANGE_AVAILABLE"
  }));
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

  const claims = Array.isArray(internalFreeze.claims) ? internalFreeze.claims : [];
  const uniqueClaims = claims.filter((claim) => !claim?.alias_of);
  const dueThisWeek = uniqueClaims.filter((claim) =>
    Number(claim?.maturity_iso_year) === Number(pointer.iso_year) &&
    Number(claim?.maturity_iso_week) === Number(pointer.iso_week)
  );
  const ranges = rangeRows(publicFreeze);

  const snapshot = await readJson(snapshotPath);
  snapshot.live_observation = {
    contract: "CYCLE_NAVIGATOR_PUBLIC_LIVE_OBSERVATION_v1",
    authority: "NON_AUTHORITATIVE_OBSERVATION_ONLY",
    issue_number: Number(pointer.issue_number),
    iso_year: Number(pointer.iso_year),
    iso_week: Number(pointer.iso_week),
    frozen_claim_count: uniqueClaims.length,
    claims_due_this_week: dueThisWeek.length,
    provisional_score: null,
    provisional_score_status: "AWAITING_ELIGIBLE_CANONICAL_OUTCOME_EVIDENCE",
    frozen_numeric_ranges: ranges,
    live_price_scoring_allowed: ranges.length > 0,
    official_weekly_scores_mutable: false,
    forecast_mutable: false,
    note: ranges.length
      ? "Live prices may be compared with the frozen published ranges as observation only. They cannot rewrite the Monday score or forecast."
      : "Frozen claims are being tracked, but no public provisional percentage is calculated until eligible canonical outcome evidence exists. No numerical price range was published for this issue."
  };

  await writeFile(snapshotPath, `${JSON.stringify(snapshot, null, 2)}\n`, "utf8");
  await copyFile(widgetSource, widgetDist);
  await copyFile(copySource, copyDist);

  let index = await readFile(indexPath, "utf8");
  for (const script of ["./live-observation.js", "./public-copy.js"]) {
    if (!index.includes(script)) {
      index = index.replace("</body>", `  <script src="${script}"></script>\n</body>`);
    }
  }
  await writeFile(indexPath, index, "utf8");

  console.log(JSON.stringify({
    status: "PASS",
    issue_number: pointer.issue_number,
    frozen_claim_count: uniqueClaims.length,
    claims_due_this_week: dueThisWeek.length,
    provisional_score: null,
    frozen_numeric_range_count: ranges.length,
    authority: "NON_AUTHORITATIVE_OBSERVATION_ONLY"
  }));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
