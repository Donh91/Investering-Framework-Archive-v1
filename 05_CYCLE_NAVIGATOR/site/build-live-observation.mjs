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
const productSource = resolve(siteDir, "public-product.js");
const productDist = resolve(distDir, "public-product.js");
const productCssSource = resolve(siteDir, "public-product.css");
const productCssDist = resolve(distDir, "public-product.css");
const entrySignalPath = resolve(repoRoot, "04_MARKET_LEARNING/entry_signals/LATEST.json");
const handlekompasPath = resolve(repoRoot, "04_MARKET_LEARNING/handlekompas/LATEST.json");

const readJson = async (path, fallback = null) => { try { return JSON.parse(await readFile(path, "utf8")); } catch { return fallback; } };
const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");
const numeric = (value) => value != null && value !== "" && Number.isFinite(Number(value));
const clean = (value) => typeof value === "string" && value.trim() ? value.trim() : null;

function safeWeekDir(pointer) {
  const weekDir = String(pointer?.week_dir || "");
  if (!weekDir.startsWith("05_CYCLE_NAVIGATOR/weekly/") || weekDir.includes("..")) throw new Error("Refusing LIVE observation from invalid week_dir");
  return weekDir;
}

function rangeRows(freeze) {
  return [["BTC", freeze?.btc_range_low, freeze?.btc_range_high],["ETH", freeze?.eth_range_low, freeze?.eth_range_high]]
    .filter(([, low, high]) => numeric(low) && numeric(high))
    .map(([asset, low, high]) => ({ asset, low: Number(low), high: Number(high), status: "FROZEN_RANGE_AVAILABLE" }));
}

function publicAction(source) {
  if (!source || typeof source !== "object") return null;
  const lanes = source.lanes || {};
  const near = lanes.lane1 || lanes.near_term || {};
  const next = lanes.lane2 || lanes.five_to_seven_day || {};
  const longer = lanes.lane3 || lanes.altcoin_market || {};
  const raw = clean(near.action || near.posture || source.current_action || source.action) || "WAIT";
  const upper = raw.toUpperCase();
  let stance = "WAIT";
  if (/PROTECT|DE-RISK|REDUCE|EXIT|STOP NEW/.test(upper)) stance = "PROTECT CAPITAL";
  else if (/BROAD/.test(upper) && /DEPLOY|BUY|TOP/.test(upper)) stance = "BROADER DEPLOYMENT";
  else if (/SELECTIVE|TOP-UP/.test(upper)) stance = "SELECTIVE";
  else if (/PREPARE/.test(upper)) stance = "PREPARE";
  else if (/HOLD/.test(upper)) stance = "HOLD";
  return {
    stance,
    current: raw,
    next_days: clean(next.action || next.posture || next.summary),
    longer: clean(longer.action || longer.posture || longer.summary),
    confirmation: clean(near.confirmation_gate || near.confirmation || source.confirmation_gate),
    invalidation: clean(near.invalidation_gate || near.invalidation || source.invalidation_gate),
    generated_at: source.generated_at || source.generated_utc || null
  };
}

function evaluateClaims(uniqueClaims, entrySignal) {
  const rows = uniqueClaims.map((claim) => ({ claim_id: claim.claim_id, label: claim.label, state: "OPEN", reason: "No eligible in-week evidence yet." }));
  if (entrySignal?.measurement_validity?.canonical_compatible !== true) return rows;
  const signals = entrySignal.signals || {};
  const breadth = String(signals?.breadth?.status || signals?.breadth_status || signals?.proxy_breadth?.status || "").toUpperCase();
  if (!breadth) return rows;
  for (const row of rows) {
    const label = String(row.label || "").toLowerCase();
    if (!label.includes("breadth")) continue;
    if (label.includes("weak")) row.state = /WEAK|NARROW|LOW/.test(breadth) ? "ON_TRACK" : /BROAD|STRONG|EXPAND/.test(breadth) ? "OFF_TRACK" : "MIXED";
    else if (label.includes("broad")) row.state = /BROAD|STRONG|EXPAND/.test(breadth) ? "ON_TRACK" : /WEAK|NARROW|LOW/.test(breadth) ? "OFF_TRACK" : "MIXED";
    else continue;
    row.reason = "Current canonical-compatible breadth evidence is mechanically comparable with this frozen claim.";
  }
  return rows;
}

async function main() {
  const pointer = await readJson(pointerPath);
  const weekDir = safeWeekDir(pointer);
  const root = resolve(repoRoot, weekDir);
  const publicFreezePath = resolve(root, "CYCLE_NAVIGATOR_FORECAST_FREEZE.json");
  const internalFreezePath = resolve(root, "CYCLE_NAVIGATOR_INTERNAL_PRECISION_FREEZE.json");
  const publicFreezeBytes = await readFile(publicFreezePath);
  const publicFreezeHash = sha256(publicFreezeBytes);
  if (publicFreezeHash !== String(pointer.forecast_freeze_sha256 || "")) throw new Error("LIVE observation refused: public forecast-freeze hash mismatch");
  const publicFreeze = JSON.parse(publicFreezeBytes.toString("utf8"));
  const internalFreeze = await readJson(internalFreezePath);
  if (String(internalFreeze.source_public_freeze_sha256 || "") !== publicFreezeHash) throw new Error("LIVE observation refused: internal precision freeze is not bound to current public freeze");
  if (Number(internalFreeze.issue_number) !== Number(pointer.issue_number)) throw new Error("LIVE observation refused: frozen-claim issue mismatch");

  const claims = Array.isArray(internalFreeze.claims) ? internalFreeze.claims : [];
  const uniqueClaims = claims.filter((claim) => !claim?.alias_of);
  const dueThisWeek = uniqueClaims.filter((claim) => Number(claim?.maturity_iso_year) === Number(pointer.iso_year) && Number(claim?.maturity_iso_week) === Number(pointer.iso_week));
  const ranges = rangeRows(publicFreeze);
  const entrySignal = await readJson(entrySignalPath);
  const claimStates = evaluateClaims(uniqueClaims, entrySignal);
  const measurable = claimStates.filter((row) => row.state !== "OPEN");
  const points = measurable.reduce((sum, row) => sum + (row.state === "ON_TRACK" ? 1 : row.state === "MIXED" ? 0.5 : 0), 0);
  const provisionalScore = measurable.length ? Math.round(points / measurable.length * 1000) / 10 : null;
  const action = publicAction(await readJson(handlekompasPath));

  const snapshot = await readJson(snapshotPath, {});
  snapshot.live_observation = {
    contract: "CYCLE_NAVIGATOR_PUBLIC_LIVE_OBSERVATION_v2",
    authority: "NON_AUTHORITATIVE_OBSERVATION_ONLY",
    issue_number: Number(pointer.issue_number), iso_year: Number(pointer.iso_year), iso_week: Number(pointer.iso_week),
    frozen_claim_count: uniqueClaims.length, claims_due_this_week: dueThisWeek.length,
    provisional_score: provisionalScore,
    provisional_score_status: measurable.length ? "PROVISIONAL_PARTIAL" : "AWAITING_ELIGIBLE_CANONICAL_OUTCOME_EVIDENCE",
    provisional_coverage: { measurable: measurable.length, total: uniqueClaims.length, label: `${measurable.length}/${uniqueClaims.length} measurable` },
    claim_states: claimStates,
    frozen_numeric_ranges: ranges, live_price_scoring_allowed: ranges.length > 0,
    current_action: action,
    official_weekly_scores_mutable: false, forecast_mutable: false,
    note: measurable.length ? "Provisional only. OPEN claims are excluded from the denominator and the Monday score remains immutable." : "No frozen claim has eligible in-week evidence yet, so no provisional percentage is shown."
  };

  await writeFile(snapshotPath, `${JSON.stringify(snapshot, null, 2)}\n`, "utf8");
  await copyFile(widgetSource, widgetDist); await copyFile(copySource, copyDist); await copyFile(productSource, productDist); await copyFile(productCssSource, productCssDist);
  let index = await readFile(indexPath, "utf8");
  if (!index.includes("./public-product.css")) index = index.replace("</head>", '  <link rel="stylesheet" href="./public-product.css" />\n</head>');
  for (const script of ["./live-observation.js", "./public-copy.js", "./public-product.js"]) if (!index.includes(script)) index = index.replace("</body>", `  <script src="${script}" defer></script>\n</body>`);
  await writeFile(indexPath, index, "utf8");
  console.log(JSON.stringify({ status: "PASS", issue_number: pointer.issue_number, frozen_claim_count: uniqueClaims.length, measurable_claims: measurable.length, provisional_score: provisionalScore, frozen_numeric_range_count: ranges.length }));
}

main().catch((error) => { console.error(error); process.exit(1); });
