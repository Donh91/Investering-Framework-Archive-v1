const OFFICIAL_SNAPSHOT_URL = "./data/latest.json";
const MARKET_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true&include_last_updated_at=true";

let latestSnapshot = null;

const $ = (id) => document.getElementById(id);
const text = (id, value) => { const n=$(id); if(n) n.textContent = value ?? "—"; };
const clean = (v) => typeof v === "string" && v.trim() ? v.trim() : null;
const human = (v) => String(v || "unknown").replaceAll("_", " ");

function compactState(state){
  if(!state) return "Official state unavailable";
  return String(state).split(". ")[0].replace(/\.$/, "");
}
function issueLabel(pointer,pkg){
  const issue=pkg?.issue_number ?? pointer?.issue_number;
  const week=pointer?.iso_week ? ` · ${pointer.iso_year}-W${String(pointer.iso_week).padStart(2,"0")}` : "";
  return `Cycle Navigator #${issue ?? "—"}${week}`;
}
function publicQuality(raw){
  const s=String(raw||"").toUpperCase();
  if(s==="COMPLETE"||s==="OK") return {label:"OFFICIAL",cls:"ok",title:"Evidence complete"};
  if(s==="DEGRADED"||s==="PARTIAL") return {label:"LIMITED EVIDENCE",cls:"warn",title:"Official state · limited evidence"};
  return {label:"EVIDENCE CHECK",cls:"warn",title:"Publication evidence"};
}
function formatOfficialTime(unix){
  const n=Number(unix); if(!Number.isFinite(n)||n<=0) return "Official package time unavailable";
  return `Official package: ${new Date(n*1000).toLocaleString([], {year:"numeric",month:"short",day:"numeric",hour:"2-digit",minute:"2-digit"})}`;
}
function price(v){
  if(!Number.isFinite(v)) return "—";
  return new Intl.NumberFormat("en-US",{style:"currency",currency:"USD",maximumFractionDigits:v>=1000?0:2}).format(v);
}
function statusFromText(v){
  const t=String(v||"").toUpperCase();
  if(t.includes("ACTIVE WATCH")||t.includes("UNCONFIRMED")||t.includes("PAUSED")||t.includes("WATCH")) return "watch";
  if(t.includes("ACTIVE")&&!t.includes("INACTIVE")) return "active";
  return "inactive";
}
function phaseStatus(v){
  const t=String(v||"").toUpperCase();
  if(t.includes("ACTIVE WATCH")) return "Active watch";
  if(t.includes("UNCONFIRMED")) return "Unconfirmed";
  if(t.includes("PAUSED")) return "Paused";
  if(t.includes("ACTIVE")&&!t.includes("INACTIVE")) return "Active";
  if(t.includes("INACTIVE")) return "Inactive";
  return "Watching";
}
function cleanPhase(v){return String(v||"").replace(/^\d+\.\s*/,"").replace(/\s[-–—]\s(ACTIVE WATCH|ACTIVE|UNCONFIRMED|INACTIVE|PAUSED).*$/i,"").trim();}

function renderList(id,items,limit=6){
  const root=$(id); if(!root) return; root.innerHTML="";
  const rows=Array.isArray(items)&&items.length?items.slice(0,limit):["Not available in the current official package."];
  for(const value of rows){const li=document.createElement("li");li.textContent=value;root.appendChild(li);}
}
function renderRotation(items){
  const root=$("rotationGrid"); if(!root) return; root.innerHTML="";
  const rows=Array.isArray(items)?items:[];
  for(const item of rows){
    const state=statusFromText(item.status),card=document.createElement("article");card.className=`rotation-item ${state==="active"?"active-card":state==="watch"?"watch-card":""}`;
    const dot=document.createElement("i");dot.className=`status-dot ${state}`;
    const box=document.createElement("div"),strong=document.createElement("strong"),p=document.createElement("p");strong.textContent=item.segment||"Segment";p.textContent=item.status||"Not published";box.append(strong,p);card.append(dot,box);root.appendChild(card);
  }
}
function renderCountdown(items){
  const root=$("countdown"),progress=$("countdownProgress"); if(!root||!progress) return; root.innerHTML="";progress.innerHTML="";
  const rows=Array.isArray(items)?items:[];
  rows.forEach((item,i)=>{
    const state=statusFromText(item.phase),seg=document.createElement("span");seg.className=`progress-segment ${state}`;seg.title=`Stage ${i+1}: ${cleanPhase(item.phase)}`;progress.appendChild(seg);
    const row=document.createElement("div");row.className="timeline-row";const button=document.createElement("button");button.className="timeline-button";button.type="button";button.setAttribute("aria-expanded","false");
    const num=document.createElement("span");num.className="timeline-index";num.textContent=i+1;const copy=document.createElement("div");copy.className="timeline-copy";const strong=document.createElement("strong");strong.textContent=cleanPhase(item.phase);const small=document.createElement("small");small.textContent=item.window||"Timing not confirmed";copy.append(strong,small);const badge=document.createElement("span");badge.className=`timeline-status ${state}`;badge.textContent=phaseStatus(item.phase);const detail=document.createElement("div");detail.className="timeline-detail";detail.textContent=`${phaseStatus(item.phase)}. ${item.window||"No calendar ETA is published."}`;button.append(num,copy,badge);button.onclick=()=>{const open=row.classList.toggle("expanded");button.setAttribute("aria-expanded",String(open));};row.append(button,detail);root.appendChild(row);
  });
}
function broadAltseasonState(items){
  const row=(items||[]).find(x=>String(x.phase||"").toLowerCase().includes("broad altseason")); return row?phaseStatus(row.phase).toUpperCase():"UNCONFIRMED";
}
function weekNumber(value){const m=String(value||"").match(/W(\d{1,2})$/i);return m?Number(m[1]):null;}
function renderRanges(snapshot){
  const root=$("rangeRow"); if(!root) return; root.innerHTML="";
  const freeze=snapshot?.package?.forecast_freeze||{},prospective=snapshot?.prospective_range||{},pointer=snapshot?.pointer||{};
  const pweek=weekNumber(prospective.target_week),currentWeek=Number(pointer.iso_week);
  const weekly=prospective?.weekly||{};
  const prospectivePairs=[["BTC",weekly?.BTC?.low,weekly?.BTC?.high],["ETH",weekly?.ETH?.low,weekly?.ETH?.high]]
    .filter(([,l,h])=>l!=null&&h!=null&&Number.isFinite(Number(l))&&Number.isFinite(Number(h)));
  const useProspective=prospective?.rules?.website_consume===true
    && prospectivePairs.length===2
    && pweek!=null
    && (!Number.isFinite(currentWeek)||pweek>=currentWeek);
  const pairs=useProspective
    ? prospectivePairs
    : [["BTC",freeze?.btc_range_low,freeze?.btc_range_high],["ETH",freeze?.eth_range_low,freeze?.eth_range_high]]
        .filter(([,l,h])=>l!=null&&h!=null&&Number.isFinite(Number(l))&&Number.isFinite(Number(h)));
  if(!pairs.length){root.hidden=true;text("rangeNotice","No prospective or frozen numerical BTC / ETH range is currently available. Nothing is reconstructed from LIVE prices.");return;}
  text("rangeNotice",useProspective
    ? `${prospective.target_week} prospective continuity baseline. It was generated after the completed prior-week close and is never retroactively scored before generation.`
    : "These numerical ranges were frozen in the official weekly package.");
  for(const [asset,l,h] of pairs){const chip=document.createElement("span");chip.className="range-chip";chip.textContent=`${asset}: ${price(Number(l))} – ${price(Number(h))}`;root.appendChild(chip);}root.hidden=false;
}
function officialNextDays(pkg){
  const map=pkg?.forecast_freeze?.intraday_map||{};
  return clean(map.day_1_2)||clean(map.day_3_4)||null;
}

function renderSnapshot(snapshot){
  latestSnapshot=snapshot;
  const pointer=snapshot?.pointer||{},pkg=snapshot?.package||{},live=snapshot?.live_observation||{},action=live?.current_action||null,score=snapshot?.weekly_score_bundle||pkg?.evaluation||{};
  const heroAction=clean(action?.stance)||compactState(pkg.market_state);
  text("issueLabel",issueLabel(pointer,pkg));
  text("marketState",heroAction);
  text("stateSummary",pkg.market_state||"Official weekly state unavailable.");
  text("weekCase",pkg.base_case_this_week||"Not published in this issue.");
  text("forwardCase",pkg.base_case_2_3_weeks||"Timing not confirmed.");
  text("reportState",pkg.market_state||"Unavailable");
  text("altseasonHeadline",broadAltseasonState(pkg.altseason_countdown));
  text("officialTimestamp",formatOfficialTime(pkg.generated_unix));
  text("sourceWeekMeta",pointer.iso_week?`Official state: ${pointer.iso_year}-W${String(pointer.iso_week).padStart(2,"0")}`:"Official source week unavailable");

  text("stillHolding",clean(action?.current)||pkg.market_state||"No current action is published.");
  text("nextRequirement",clean(action?.next_days)||officialNextDays(pkg)||clean(action?.confirmation)||pkg?.forecast_freeze?.breadth_condition||"No supported 1–3 day call is published.");
  text("changedFromPrior",clean(action?.invalidation)||pkg?.evaluation?.misses?.[0]||"No explicit invalidation is published for this issue.");
  text("priorIssueLabel",`Compared with Cycle Navigator #${pkg.previous_issue_number ?? "prior"}`);

  const scoreValue=Number(score?.structural_score);const hasScore=Number.isFinite(scoreValue);if($("scoreRing")) $("scoreRing").style.setProperty("--score",hasScore?Math.max(0,Math.min(100,scoreValue)):0);text("scoreValue",hasScore?`${Math.round(scoreValue)}%`:"—");text("scoreCaption",hasScore?`Official structural score for Cycle Navigator #${score.issue_scored ?? pkg.previous_issue_number ?? "prior"}.`:`No completed structural score is available.`);

  const q=publicQuality(pkg.status||pointer.status);for(const id of ["qualityBadge","dataQualityBadge"]){const n=$(id);if(n){n.textContent=q.label;n.className=`quality-badge ${q.cls}`;}}text("dataQualityTitle",q.title);text("officialStatus",`OFFICIAL weekly #${pkg.issue_number ?? pointer.issue_number ?? "—"}`);text("feedMode",live?.authority?"Feed mode: official weekly + bounded LIVE observation":"Feed mode: official weekly snapshot");

  renderRanges(snapshot);renderRotation(pkg.rotation_ladder);renderCountdown(pkg.altseason_countdown);renderList("strengths",score?.strengths||pkg?.evaluation?.strengths);renderList("misses",score?.misses||pkg?.evaluation?.misses);renderList("frozenTests",pkg?.forecast_freeze?.structural_calls);renderList("uncertainties",pkg.uncertainties,4);
  text("publicationStatus",`Publication: ${human(pointer.publication_status||pkg.publication_status)}`);text("sourceWeek",pointer.completed_source_week?`Completed source week W${pointer.completed_source_week} · current W${pointer.iso_week}`:"Source week unavailable");
}

async function loadNavigator(){
  try{const r=await fetch(`${OFFICIAL_SNAPSHOT_URL}?t=${Date.now()}`,{cache:"no-store"});if(!r.ok)throw new Error(`snapshot HTTP ${r.status}`);const s=await r.json();if(!s?.pointer||!s?.package)throw new Error("snapshot missing official pointer/package");renderSnapshot(s);}catch(e){console.warn("Official snapshot unavailable",e);text("officialStatus","OFFICIAL feed unavailable");text("marketState","OFFICIAL STATE UNAVAILABLE");text("stateSummary","The site is failing closed instead of inventing a market call.");text("stillHolding","No official action available.");text("nextRequirement","Not published while official feed is unavailable.");text("changedFromPrior","Do not infer a signal from LIVE prices alone.");}
}
function pct(v){if(!Number.isFinite(v))return "24h —";return `24h ${v>=0?"+":""}${v.toFixed(2)}%`;}
function setChange(id,v){const n=$(id);if(!n)return;n.textContent=pct(v);n.className=Number.isFinite(v)?(v>=0?"up":"down"):"";}
async function loadMarket(){
  try{const r=await fetch(`${MARKET_URL}&t=${Date.now()}`,{cache:"no-store"});if(!r.ok)throw new Error(`market HTTP ${r.status}`);const d=await r.json(),btc=d.bitcoin,eth=d.ethereum,ratio=Number(eth?.usd)/Number(btc?.usd);text("btcPrice",price(Number(btc?.usd)));text("ethPrice",price(Number(eth?.usd)));text("ethBtc",Number.isFinite(ratio)?ratio.toFixed(5):"—");setChange("btcChange",Number(btc?.usd_24h_change));setChange("ethChange",Number(eth?.usd_24h_change));const updated=Math.max(Number(btc?.last_updated_at||0),Number(eth?.last_updated_at||0));text("marketTimestamp",`LIVE updated ${new Date((updated||Date.now()/1000)*1000).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit",second:"2-digit"})}`);}catch(e){console.warn("LIVE market feed unavailable",e);text("marketTimestamp","LIVE context unavailable");}
}
async function shareSnapshot(){
  const pkg=latestSnapshot?.package||{},action=latestSnapshot?.live_observation?.current_action?.stance;const title=`Cycle Navigator #${pkg.issue_number ?? ""}`;const body=`${action||compactState(pkg.market_state)}. Broad altseason: ${broadAltseasonState(pkg.altseason_countdown)}. Scenario map only, not investment advice.`;try{if(navigator.share){await navigator.share({title,text:body,url:location.href});return;}await navigator.clipboard.writeText(`${title}\n${body}\n${location.href}`);text("shareButton","Copied");setTimeout(()=>text("shareButton","Share snapshot"),1500);}catch(e){console.warn("Share unavailable",e);}
}
if($("shareButton")) $("shareButton").addEventListener("click",shareSnapshot);
loadNavigator();loadMarket();setInterval(loadMarket,60_000);setInterval(loadNavigator,5*60_000);