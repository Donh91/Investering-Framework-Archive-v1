const OFFICIAL_SNAPSHOT_URL = "./data/latest.json";
const MARKET_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true&include_last_updated_at=true";

const FALLBACK = {
  issue_number: 25,
  previous_issue_number: 24,
  generated_unix: 1788757939,
  status: "DEGRADED",
  market_state: "Unresolved, volatile transition with an active ETH-relative leadership test.",
  base_case_this_week: "An unresolved, volatile transition remains the base case. ETH retains a relative-strength opportunity, but weak proxy breadth and conflicted BTC evidence prevent confirmation of broad expansion.",
  base_case_2_3_weeks: "Selective ETH and large-cap leadership attempts are more likely than immediate broad alt expansion. Progress requires persistent ETH-relative strength, improving breadth and transmission into midcaps.",
  evaluation: {
    structural_score: 75,
    score_status: "REPRODUCIBLE",
    strengths: [
      "The unresolved-transition call held up.",
      "Weak breadth correctly prevented broad-rotation confirmation.",
      "Broad altseason remained inactive.",
      "Midcap, small-cap and microcap transmission remained absent."
    ],
    misses: [
      "The BTC-relative-anchor call was contradicted by ETH outperformance.",
      "The downside-sensitive framing underweighted constructive weekly paths and positive taker flow."
    ]
  },
  rotation_ladder: [
    { segment: "BTC", status: "Major liquidity anchor, but short-term evidence is conflicted" },
    { segment: "ETH", status: "Relative leadership attempt active; broad confirmation absent" },
    { segment: "Large caps", status: "Selective participation only" },
    { segment: "Midcaps", status: "Waiting for sustained breadth transmission" },
    { segment: "Small caps", status: "Inactive" },
    { segment: "Microcaps", status: "Inactive" }
  ],
  altseason_countdown: [
    { phase: "1. Volatile transition and reset - ACTIVE", window: "Now / this week" },
    { phase: "2. ETH-relative stabilization - ACTIVE WATCH", window: "This week" },
    { phase: "3. ETH and large-cap leadership - UNCONFIRMED", window: "1-3 weeks at earliest" },
    { phase: "4. Mid-cap transmission - INACTIVE", window: "Only after breadth confirms leadership" },
    { phase: "5. Small- and microcap expansion - INACTIVE", window: "Later; no reliable calendar window" },
    { phase: "6. Broad altseason - PAUSED", window: "No calendar ETA until broad, persistent alt/BTC outperformance" }
  ],
  forecast_freeze: {
    breadth_condition: "Broad altseason remains inactive unless breadth broadens beyond isolated leaders and survives pullbacks.",
    btc_range_low: null,
    btc_range_high: null,
    eth_range_low: null,
    eth_range_high: null,
    structural_calls: [
      "W37 ends as an unresolved, volatile transition rather than a ratified broad risk-expansion regime.",
      "ETH/BTC records a non-negative return from the W37 open to the W37 close.",
      "ETH-relative strength does not become broadly transmitted leadership during W37 because proxy breadth remains weak.",
      "Rotation remains selective and does not develop into sustained midcap, small-cap and microcap transmission.",
      "Broad altseason remains inactive through the W37 close."
    ]
  },
  uncertainties: [
    "Current BTC and ETH spot prices and volatility inputs were not supplied to the weekly package.",
    "Some supporting market inputs were supplied as conclusions rather than complete underlying time series."
  ],
  publication_status: "X_READY_NOT_CONFIRMED_PUBLISHED"
};

let latestPackage = FALLBACK;
let latestPointer = null;
let canonicalFeedAvailable = false;

function byId(id) {
  return document.getElementById(id);
}

function setText(id, value) {
  const node = byId(id);
  if (node) node.textContent = value ?? "-";
}

function compactState(state) {
  if (!state) return "Cycle state unavailable";
  const first = state.split(". ")[0];
  return first.replace(/\.$/, "");
}

function issueLabel(pointer, data) {
  if (!pointer) return `Cycle Navigator #${data.issue_number ?? "-"}`;
  const week = String(pointer.iso_week ?? "-").padStart(2, "0");
  return `Cycle Navigator #${data.issue_number ?? pointer.issue_number ?? "-"} · ${pointer.iso_year ?? ""}-W${week}`;
}

function qualityClass(status) {
  const s = String(status || "").toUpperCase();
  if (s === "COMPLETE" || s === "OK") return "ok";
  if (s === "DEGRADED" || s === "PARTIAL") return "warn";
  return "bad";
}

function statusFromText(text) {
  const t = String(text || "").toUpperCase();
  if (t.includes("ACTIVE WATCH") || t.includes("UNCONFIRMED") || t.includes("PAUSED")) return "watch";
  if (t.includes("ACTIVE") && !t.includes("INACTIVE")) return "active";
  return "inactive";
}

function cleanPhase(phase) {
  return String(phase || "")
    .replace(/^\d+\.\s*/, "")
    .replace(/\s[-–—]\s(ACTIVE WATCH|ACTIVE|UNCONFIRMED|INACTIVE|PAUSED).*$/i, "")
    .trim();
}

function phaseStatus(phase) {
  const p = String(phase || "").toUpperCase();
  if (p.includes("ACTIVE WATCH")) return "Active watch";
  if (p.includes("ACTIVE") && !p.includes("INACTIVE")) return "Active";
  if (p.includes("UNCONFIRMED")) return "Unconfirmed";
  if (p.includes("PAUSED")) return "Paused";
  if (p.includes("INACTIVE")) return "Inactive";
  return "Watching";
}

function humanStatus(value) {
  return String(value || "unknown").replaceAll("_", " ");
}

function formatOfficialTime(unix) {
  const seconds = Number(unix);
  if (!Number.isFinite(seconds) || seconds <= 0) return "OFFICIAL package time unavailable";
  const date = new Date(seconds * 1000);
  return `OFFICIAL package: ${date.toLocaleString([], {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    timeZoneName: "short"
  })}`;
}

function renderList(id, items, limit = 6) {
  const root = byId(id);
  if (!root) return;
  root.innerHTML = "";
  const safeItems = Array.isArray(items) ? items : [];
  if (!safeItems.length) {
    const li = document.createElement("li");
    li.textContent = "Not available in the current official package.";
    root.appendChild(li);
    return;
  }
  safeItems.slice(0, limit).forEach((text) => {
    const li = document.createElement("li");
    li.textContent = text;
    root.appendChild(li);
  });
}

function renderRotation(items) {
  const root = byId("rotationGrid");
  root.innerHTML = "";
  (items || []).forEach((item) => {
    const card = document.createElement("article");
    const status = statusFromText(item.status);
    card.className = `rotation-item ${status === "active" ? "active-card" : status === "watch" ? "watch-card" : ""}`;

    const dot = document.createElement("i");
    dot.className = `status-dot ${status}`;

    const copy = document.createElement("div");
    const strong = document.createElement("strong");
    strong.textContent = item.segment;
    const p = document.createElement("p");
    p.textContent = item.status;
    copy.append(strong, p);

    card.append(dot, copy);
    root.appendChild(card);
  });
}

function renderCountdownProgress(items) {
  const root = byId("countdownProgress");
  root.innerHTML = "";
  (items || []).forEach((item, index) => {
    const segment = document.createElement("span");
    const state = statusFromText(item.phase);
    segment.className = `progress-segment ${state}`;
    segment.title = `Stage ${index + 1}: ${cleanPhase(item.phase)} - ${phaseStatus(item.phase)}`;
    root.appendChild(segment);
  });
}

function renderCountdown(items) {
  const root = byId("countdown");
  root.innerHTML = "";
  (items || []).forEach((item, index) => {
    const row = document.createElement("div");
    row.className = "timeline-row";

    const button = document.createElement("button");
    button.className = "timeline-button";
    button.type = "button";
    button.setAttribute("aria-expanded", "false");

    const number = document.createElement("span");
    number.className = "timeline-index";
    number.textContent = index + 1;

    const copy = document.createElement("div");
    copy.className = "timeline-copy";
    const strong = document.createElement("strong");
    strong.textContent = cleanPhase(item.phase);
    const small = document.createElement("small");
    small.textContent = item.window || "Window unavailable";
    copy.append(strong, small);

    const badge = document.createElement("span");
    const state = statusFromText(item.phase);
    badge.className = `timeline-status ${state}`;
    badge.textContent = phaseStatus(item.phase);

    const detail = document.createElement("div");
    detail.className = "timeline-detail";
    detail.textContent = `${phaseStatus(item.phase)}. ${item.window || "No calendar window is published."}`;

    button.append(number, copy, badge);
    button.addEventListener("click", () => {
      const expanded = row.classList.toggle("expanded");
      button.setAttribute("aria-expanded", String(expanded));
    });

    row.append(button, detail);
    root.appendChild(row);
  });
  renderCountdownProgress(items);
}

function broadAltseasonState(items) {
  const finalStage = (items || []).find((item) => String(item.phase).toLowerCase().includes("broad altseason"));
  return finalStage ? phaseStatus(finalStage.phase).toUpperCase() : "UNCONFIRMED";
}

function renderRangeState(freeze) {
  const ranges = freeze || {};
  const rangePairs = [
    ["BTC", ranges.btc_range_low, ranges.btc_range_high],
    ["ETH", ranges.eth_range_low, ranges.eth_range_high]
  ];
  const publishable = rangePairs.filter(([, low, high]) => low != null && high != null && Number.isFinite(Number(low)) && Number.isFinite(Number(high)));
  const rangeRow = byId("rangeRow");
  rangeRow.innerHTML = "";

  if (!publishable.length) {
    rangeRow.hidden = true;
    setText("rangeNotice", "Numeric BTC / ETH ranges are intentionally unpublished in this issue because the official machine package freezes those fields as null.");
    return;
  }

  setText("rangeNotice", "Numeric price ranges below are frozen in the OFFICIAL weekly package.");
  publishable.forEach(([asset, low, high]) => {
    const chip = document.createElement("span");
    chip.className = "range-chip";
    chip.textContent = `${asset}: ${price(Number(low))} - ${price(Number(high))}`;
    rangeRow.appendChild(chip);
  });
  rangeRow.hidden = false;
}

function renderChangeSummary(data) {
  const strengths = data.evaluation?.strengths || [];
  const misses = data.evaluation?.misses || [];
  setText("priorIssueLabel", `Compared with Cycle Navigator #${data.previous_issue_number ?? "prior"}`);
  setText("stillHolding", strengths[0] || "No supported prior-issue comparison is available in the current package.");
  setText("changedFromPrior", misses[0] || "No challenged prior-issue call is available in the current package.");
  setText("nextRequirement", data.forecast_freeze?.breadth_condition || data.forecast_freeze?.structural_calls?.[0] || "No explicit next-step condition is available in the current package.");
}

function renderNavigator(data, pointer, options = {}) {
  latestPackage = data;
  latestPointer = pointer;
  canonicalFeedAvailable = Boolean(options.canonical);

  setText("issueLabel", issueLabel(pointer, data));
  setText("marketState", compactState(data.market_state));
  setText("stateSummary", data.market_state);
  setText("weekCase", data.base_case_this_week);
  setText("forwardCase", data.base_case_2_3_weeks);
  setText("reportState", data.market_state);
  setText("altseasonHeadline", broadAltseasonState(data.altseason_countdown));
  setText("officialTimestamp", formatOfficialTime(data.generated_unix));

  const weekText = pointer
    ? `OFFICIAL state: ${pointer.iso_year ?? ""}-W${String(pointer.iso_week ?? "-").padStart(2, "0")}`
    : "OFFICIAL source: embedded fallback snapshot";
  setText("sourceWeekMeta", weekText);

  const score = Number(data.evaluation?.structural_score);
  const hasScore = Number.isFinite(score);
  byId("scoreRing").style.setProperty("--score", hasScore ? Math.max(0, Math.min(100, score)) : 0);
  setText("scoreValue", hasScore ? `${Math.round(score)}%` : "-");
  setText("scoreCaption", hasScore
    ? `${data.evaluation?.score_status || "Scored"} call-level structural audit of Cycle Navigator #${data.previous_issue_number ?? "prior"}.`
    : "No reproducible structural score is available for the prior issue.");

  const quality = data.status || pointer?.status || "UNKNOWN";
  const qualityBadge = byId("qualityBadge");
  qualityBadge.textContent = quality;
  qualityBadge.className = `quality-badge ${qualityClass(quality)}`;

  const dataQualityBadge = byId("dataQualityBadge");
  dataQualityBadge.textContent = quality;
  dataQualityBadge.className = `quality-badge ${qualityClass(quality)}`;
  setText("dataQualityTitle", quality === "DEGRADED" ? "DEGRADED, shown honestly" : "Publication status");

  if (canonicalFeedAvailable) {
    setText("officialStatus", `OFFICIAL signal: ${quality}`);
    setText("feedMode", "Feed mode: canonical public snapshot");
  } else {
    setText("officialStatus", "OFFICIAL feed unavailable");
    setText("feedMode", "Feed mode: embedded fallback snapshot");
  }

  renderRangeState(data.forecast_freeze);
  renderChangeSummary(data);
  renderRotation(data.rotation_ladder);
  renderCountdown(data.altseason_countdown);
  renderList("strengths", data.evaluation?.strengths);
  renderList("misses", data.evaluation?.misses);
  renderList("frozenTests", data.forecast_freeze?.structural_calls);
  renderList("uncertainties", data.uncertainties, 4);

  setText("publicationStatus", `Publication: ${humanStatus(pointer?.publication_status || data.publication_status)}`);
  setText("sourceWeek", pointer
    ? `Source: completed W${pointer.completed_source_week ?? "-"} · current W${pointer.iso_week ?? "-"}`
    : "Source: bounded embedded fallback");
}

async function loadNavigator() {
  try {
    const response = await fetch(`${OFFICIAL_SNAPSHOT_URL}?t=${Date.now()}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`Public snapshot HTTP ${response.status}`);
    const snapshot = await response.json();
    const pointer = snapshot?.pointer;
    const data = snapshot?.package;

    if (!pointer || !data || typeof data !== "object") {
      throw new Error("Public snapshot is missing pointer/package data");
    }

    renderNavigator(data, pointer, { canonical: true });
  } catch (error) {
    console.warn("Cycle Navigator public snapshot unavailable, using bounded embedded fallback", error);
    renderNavigator(FALLBACK, null, { canonical: false });
  }
}

function price(value) {
  if (!Number.isFinite(value)) return "-";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: value >= 1000 ? 0 : 2
  }).format(value);
}

function pct(value) {
  if (!Number.isFinite(value)) return "24h -";
  const sign = value >= 0 ? "+" : "";
  return `24h ${sign}${value.toFixed(2)}%`;
}

function setChange(id, value) {
  const node = byId(id);
  node.textContent = pct(value);
  node.className = Number.isFinite(value) ? (value >= 0 ? "up" : "down") : "";
}

async function loadMarket() {
  try {
    const response = await fetch(`${MARKET_URL}&t=${Date.now()}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`Market HTTP ${response.status}`);
    const data = await response.json();
    const btc = data.bitcoin;
    const eth = data.ethereum;
    const ratio = Number(eth?.usd) / Number(btc?.usd);

    setText("btcPrice", price(Number(btc?.usd)));
    setText("ethPrice", price(Number(eth?.usd)));
    setText("ethBtc", Number.isFinite(ratio) ? ratio.toFixed(5) : "-");
    setChange("btcChange", Number(btc?.usd_24h_change));
    setChange("ethChange", Number(eth?.usd_24h_change));

    const updated = Math.max(Number(btc?.last_updated_at || 0), Number(eth?.last_updated_at || 0));
    const when = updated ? new Date(updated * 1000) : new Date();
    setText("marketTimestamp", `LIVE updated ${when.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}`);
  } catch (error) {
    console.warn("LIVE market feed unavailable", error);
    setText("marketTimestamp", "LIVE feed unavailable, retrying automatically");
  }
}

async function shareSnapshot() {
  const title = `Cycle Navigator #${latestPackage.issue_number ?? ""}`;
  const text = `${compactState(latestPackage.market_state)}. Broad altseason: ${broadAltseasonState(latestPackage.altseason_countdown)}. Scenario map only, not investment advice.`;
  try {
    if (navigator.share) {
      await navigator.share({ title, text, url: location.href });
      return;
    }
    await navigator.clipboard.writeText(`${title}\n${text}\n${location.href}`);
    const button = byId("shareButton");
    const original = button.textContent;
    button.textContent = "Copied";
    setTimeout(() => { button.textContent = original; }, 1500);
  } catch (error) {
    console.warn("Share cancelled or unavailable", error);
  }
}

byId("shareButton").addEventListener("click", shareSnapshot);
renderNavigator(FALLBACK, null, { canonical: false });
loadNavigator();
loadMarket();
setInterval(loadMarket, 60_000);
setInterval(loadNavigator, 5 * 60_000);
