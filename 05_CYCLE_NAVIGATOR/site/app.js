const RAW_BASE = "https://raw.githubusercontent.com/Donh91/Investering-Framework-Archive-v1/main/";
const POINTER_PATH = "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json";
const MARKET_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true&include_last_updated_at=true";

const FALLBACK = {
  issue_number: 25,
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
  publication_status: "X_READY_NOT_CONFIRMED_PUBLISHED"
};

let latestPackage = FALLBACK;
let latestPointer = null;

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
  return s === "COMPLETE" || s === "OK" ? "ok" : "warn";
}

function statusFromText(text) {
  const t = String(text || "").toUpperCase();
  if (t.includes("ACTIVE") && !t.includes("INACTIVE")) return "active";
  if (t.includes("WATCH") || t.includes("UNCONFIRMED") || t.includes("PAUSED")) return "watch";
  return "inactive";
}

function cleanPhase(phase) {
  return String(phase || "")
    .replace(/^\d+\.\s*/, "")
    .replace(/\s[-–]\s(ACTIVE WATCH|ACTIVE|UNCONFIRMED|INACTIVE|PAUSED).*$/i, "")
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

function renderList(id, items) {
  const root = byId(id);
  root.innerHTML = "";
  (items || []).slice(0, 6).forEach((text) => {
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
    card.className = "rotation-item";

    const dot = document.createElement("i");
    const status = statusFromText(item.status);
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

function renderCountdown(items) {
  const root = byId("countdown");
  root.innerHTML = "";
  (items || []).forEach((item, index) => {
    const row = document.createElement("div");
    row.className = "timeline-row";

    const number = document.createElement("span");
    number.className = "timeline-index";
    number.textContent = index + 1;

    const copy = document.createElement("div");
    copy.className = "timeline-copy";
    const strong = document.createElement("strong");
    strong.textContent = cleanPhase(item.phase);
    const small = document.createElement("small");
    small.textContent = item.window || "";
    copy.append(strong, small);

    const badge = document.createElement("span");
    const state = statusFromText(item.phase);
    badge.className = `timeline-status ${state}`;
    badge.textContent = phaseStatus(item.phase);

    row.append(number, copy, badge);
    root.appendChild(row);
  });
}

function broadAltseasonState(items) {
  const finalStage = (items || []).find((item) => String(item.phase).toLowerCase().includes("broad altseason"));
  return finalStage ? phaseStatus(finalStage.phase).toUpperCase() : "UNCONFIRMED";
}

function renderNavigator(data, pointer) {
  latestPackage = data;
  latestPointer = pointer;

  setText("issueLabel", issueLabel(pointer, data));
  setText("marketState", compactState(data.market_state));
  setText("stateSummary", data.market_state);
  setText("weekCase", data.base_case_this_week);
  setText("forwardCase", data.base_case_2_3_weeks);
  setText("reportState", data.market_state);
  setText("altseasonHeadline", broadAltseasonState(data.altseason_countdown));
  setText("altseasonSubline", "official weekly state");

  const score = Number(data.evaluation?.structural_score);
  const hasScore = Number.isFinite(score);
  byId("scoreRing").style.setProperty("--score", hasScore ? Math.max(0, Math.min(100, score)) : 0);
  setText("scoreValue", hasScore ? `${Math.round(score)}%` : "-");
  setText("scoreCaption", hasScore
    ? `${data.evaluation?.score_status || "Scored"} call-level structural audit of the prior issue.`
    : "No reproducible structural score is available for the prior issue.");

  const quality = data.status || pointer?.status || "UNKNOWN";
  const qualityBadge = byId("qualityBadge");
  qualityBadge.textContent = quality;
  qualityBadge.className = `quality-badge ${qualityClass(quality)}`;
  setText("officialStatus", `Official signal: ${quality}`);

  const ranges = data.forecast_freeze || {};
  const noRanges = [ranges.btc_range_low, ranges.btc_range_high, ranges.eth_range_low, ranges.eth_range_high].every((v) => v == null);
  setText("rangeNotice", noRanges
    ? "Numeric BTC / ETH ranges are intentionally not published in this issue because the required spot and volatility inputs were not supplied."
    : "Numeric price ranges are frozen in the official weekly package.");

  renderRotation(data.rotation_ladder);
  renderCountdown(data.altseason_countdown);
  renderList("strengths", data.evaluation?.strengths);
  renderList("misses", data.evaluation?.misses);
  renderList("frozenTests", data.forecast_freeze?.structural_calls);

  setText("publicationStatus", `Publication: ${(pointer?.publication_status || data.publication_status || "unknown").replaceAll("_", " ")}`);
  setText("sourceWeek", pointer ? `Source: completed W${pointer.completed_source_week ?? "-"} · current W${pointer.iso_week ?? "-"}` : "Source: embedded fallback");
}

async function loadNavigator() {
  try {
    const pointerResponse = await fetch(`${RAW_BASE}${POINTER_PATH}?t=${Date.now()}`, { cache: "no-store" });
    if (!pointerResponse.ok) throw new Error(`Pointer HTTP ${pointerResponse.status}`);
    const pointer = await pointerResponse.json();

    const packagePath = `${pointer.week_dir}/CYCLE_NAVIGATOR_MACHINE_PACKAGE.json`;
    const packageResponse = await fetch(`${RAW_BASE}${packagePath}?t=${Date.now()}`, { cache: "no-store" });
    if (!packageResponse.ok) throw new Error(`Package HTTP ${packageResponse.status}`);
    const data = await packageResponse.json();
    renderNavigator(data, pointer);
  } catch (error) {
    console.warn("Cycle Navigator canonical feed unavailable, using embedded fallback", error);
    renderNavigator(FALLBACK, null);
    setText("officialStatus", "Official feed temporarily unavailable");
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
    setText("marketTimestamp", `Updated ${when.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}`);
  } catch (error) {
    console.warn("Live market feed unavailable", error);
    setText("marketTimestamp", "Live feed unavailable, retrying automatically");
  }
}

async function shareSnapshot() {
  const title = `Cycle Navigator #${latestPackage.issue_number ?? ""}`;
  const text = `${compactState(latestPackage.market_state)}. Broad altseason: ${broadAltseasonState(latestPackage.altseason_countdown)}.`;
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
renderNavigator(FALLBACK, null);
loadNavigator();
loadMarket();
setInterval(loadMarket, 60_000);
setInterval(loadNavigator, 5 * 60_000);
