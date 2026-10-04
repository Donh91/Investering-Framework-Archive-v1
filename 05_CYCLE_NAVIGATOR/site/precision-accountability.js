(() => {
'use strict';

const DATA_URL = './data/latest.json';
const FREEZE_INDEX_URL = './data/public-freezes/index.json';
const esc = (value) => String(value ?? '')
  .replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;').replaceAll("'", '&#039;');

const num = (v) => v===null||v===undefined||v==='' ? null : (Number.isFinite(Number(v)) ? Number(v) : null);
const score = (v) => {
  const n = num(v);
  return n === null ? '—' : n.toFixed(2).replace(/\.?0+$/, '') + '%';
};
const range = (lo, hi) => {
  const a = num(lo), b = num(hi);
  if (a === null || b === null) return '—';
  return '$' + a.toLocaleString(undefined,{maximumFractionDigits:0}) + '–$' + b.toLocaleString(undefined,{maximumFractionDigits:0});
};
const stamp = (value) => {
  if (!value) return '—';
  const d = new Date(value);
  if (!Number.isFinite(d.getTime())) return '—';
  return d.toLocaleString('en-GB', {
    timeZone: 'UTC', day:'2-digit', month:'short', year:'numeric',
    hour:'2-digit', minute:'2-digit', hour12:false
  }).replace(',', '') + ' UTC';
};
const shortHash = (value) => {
  const s = String(value || '');
  return s.length > 18 ? s.slice(0,10) + '…' + s.slice(-6) : (s || '—');
};
const phaseLabel = (value) => ({
  COMPLETE:'SETTLED',
  LIVE:'LIVE',
  NOT_STARTED:'UPCOMING',
  DEGRADED:'DATA GAP'
}[String(value||'').toUpperCase()] || 'PENDING');
const phaseTone = (value) => ({
  COMPLETE:'settled',
  LIVE:'live',
  NOT_STARTED:'upcoming',
  DEGRADED:'degraded'
}[String(value||'').toUpperCase()] || 'upcoming');

function freshnessMeta(live) {
  const d = live?.live_as_of_utc ? new Date(live.live_as_of_utc) : null;
  const ageMs = d && Number.isFinite(d.getTime()) ? Date.now() - d.getTime() : null;
  const sla = Math.max(30, Number(live?.freshness_sla_minutes || 90));
  const stale = ageMs === null || ageMs > sla * 60 * 1000;
  const mins = ageMs === null ? null : Math.max(0, Math.floor(ageMs / 60000));
  const age = mins === null ? 'unknown age' : mins >= 60 ? Math.floor(mins/60) + 'h ' + (mins%60) + 'm old' : mins + ' min old';
  return {stale, age, sla};
}

function recordLabel(live) {
  return live?.freeze_record_kind === 'MIGRATED_VERIFIED_FREEZE'
    ? 'MIGRATED VERIFIED FREEZE'
    : 'SITE SOURCE OF RECORD';
}

function archivePanel() {
  const records = Array.isArray(freezeIndex?.records) ? [...freezeIndex.records].sort((a,b)=>Number(b.public_issue_number||0)-Number(a.public_issue_number||0)).slice(0,8) : [];
  if (!records.length) return '';
  return '<section class="pa-archive"><header><div><span class="pa-kicker">PUBLIC FREEZE ARCHIVE</span><h3>What was locked before the outcome.</h3></div><p>Each record preserves public issue identity, forecast week and immutable forecast hash. Site-native freezes can replace X as the proof channel.</p></header><div class="pa-archive-grid">'
    + records.map((r)=>'<a href="'+esc(r.path||'#')+'" target="_blank" rel="noopener"><span>CN #'+esc(r.public_issue_number)+' · '+esc(r.forecast_week||'—')+'</span><strong>'+esc(String(r.record_kind||'SITE_NATIVE_SOURCE_OF_RECORD').replaceAll('_',' '))+'</strong><small>'+esc(shortHash(r.source_forecast_freeze_sha256))+' · View frozen record →</small></a>').join('')
    + '</div></section>';
}

function rowsByWindow(live, window) {
  return (Array.isArray(live?.rows) ? live.rows : []).filter((r) => r?.window === window);
}

function windowCard(live, key, title) {
  const w = live?.window_scores?.[key] || {};
  const rows = rowsByWindow(live, key);
  const tone = phaseTone(w.phase);
  const assets = ['BTC','ETH'].map((asset) => {
    const r = rows.find((x) => x?.asset === asset) || {};
    return '<div class="pa-asset-row">'
      + '<strong>' + esc(asset) + '</strong>'
      + '<div><span>FROZEN</span><b>' + esc(range(r.forecast_low,r.forecast_high)) + '</b></div>'
      + '<div><span>OBSERVED</span><b>' + esc(range(r.actual_low_to_date,r.actual_high_to_date)) + '</b></div>'
      + '<div class="pa-asset-score"><span>' + (tone==='live'?'LIVE SCORE':'SCORE') + '</span><b>' + esc(score(r.score_to_date)) + '</b></div>'
      + '</div>';
  }).join('');
  const coverage = String(w.observed_hours ?? 0) + '/' + String(w.expected_hours_so_far ?? 0) + ' observed hours';
  const scoringNote = w.scoring_start_utc && w.scoring_start_utc !== w.window_start_utc ? ' · scored from ' + stamp(w.scoring_start_utc) : '';
  return '<article class="pa-window tone-' + esc(tone) + '">'
    + '<header><div><span>' + esc(title) + '</span><small>' + esc(stamp(w.window_start_utc)) + ' → ' + esc(stamp(w.window_end_utc)) + esc(scoringNote) + '</small></div><b>' + esc(phaseLabel(w.phase)) + '</b></header>'
    + '<div class="pa-window-score"><strong>' + esc(score(w.score_to_date)) + '</strong><small>' + esc(coverage) + '</small></div>'
    + '<div class="pa-assets">' + assets + '</div>'
    + '</article>';
}

function sequenceRail(live) {
  const rows = Array.isArray(live?.frozen_sequence) ? live.frozen_sequence : [];
  if (!rows.length) return '';
  return '<section class="pa-sequence">'
    + '<header><div><span class="pa-kicker">FROZEN MONDAY PATH</span><h3>What the week was expected to do.</h3></div><p>Sequence context is shown separately from the percentage. Only the frozen BTC/ETH price ranges enter public Price Range Precision.</p></header>'
    + '<div class="pa-sequence-rail">' + rows.map((r,i) => {
      const tone = phaseTone(r.phase);
      return '<article class="tone-' + esc(tone) + '">'
        + '<i>' + esc(i+1) + '</i><div><span>' + esc(r.label || r.window) + '</span><b>' + esc(phaseLabel(r.phase)) + (r.score_to_date!=null?' · '+esc(score(r.score_to_date)):'') + '</b><p>' + esc(r.frozen_text || 'No frozen sequence text published for this window.') + '</p></div>'
        + '</article>';
    }).join('') + '</div></section>';
}

function fullPanel(snapshot) {
  const live = snapshot?.public_live_precision;
  if (live?.contract !== 'CN_PUBLIC_LIVE_PRICE_PRECISION_v1') return '';
  const current = snapshot?.public_series?.current_public_projection || {};
  const running = score(live.running_price_precision_pct);
  const settled = Number(live.completed_rows || 0);
  const liveRows = Number(live.live_rows || 0);
  const pending = Number(live.pending_rows || 0);
  const fresh = freshnessMeta(live);
  const status = live.status === 'READY_FOR_FINAL_WEEKLY_SETTLEMENT'
    ? 'WEEK COMPLETE · AWAITING VERIFIED SETTLEMENT'
    : live.running_price_precision_pct == null
      ? 'AWAITING SCOREABLE RANGE DATA'
      : fresh.stale ? 'PROVISIONAL · STALE' : 'PROVISIONAL · LIVE';

  return '<section id="publicLiveAccountability" class="pa-full">'
    + '<header class="pa-head"><div><span class="pa-kicker">THIS WEEK · PUBLIC ACCOUNTABILITY</span><h2>Frozen Monday. Scored live. Verified after close.</h2><p>The running percentage uses the same six prospectively frozen BTC/ETH intraday ranges and the same formula as the final public Cycle Navigator Price Range score.</p></div><div class="pa-state-pill' + (fresh.stale?' stale':'') + '">' + esc(status) + '</div></header>'
    + '<div class="pa-score-hero">'
      + '<div class="pa-identity"><span>CURRENT FROZEN FORECAST</span><strong>CN #' + esc(live.public_issue_number ?? current.public_issue_number ?? '—') + '</strong><b>' + esc(live.forecast_week || current.forecast_week || '—') + '</b><small>Frozen ' + esc(stamp(live.frozen_at_utc)) + '</small></div>'
      + '<div class="pa-running-score"><span>PRICE RANGE PRECISION · ' + (fresh.stale?'STALE':'LIVE') + '</span><strong>' + esc(running) + '</strong><small>As of ' + esc(stamp(live.live_as_of_utc)) + ' · ' + esc(fresh.age) + (fresh.stale?' · waiting for the next complete hourly owner update':'') + '</small></div>'
      + '<div class="pa-coverage"><span>COVERAGE</span><strong>' + esc(settled) + ' settled · ' + esc(liveRows) + ' live</strong><small>' + esc(pending) + ' pending · ' + esc(live.scored_rows ?? 0) + '/' + esc(live.final_row_count ?? 6) + ' currently scoreable</small></div>'
    + '</div>'
    + '<div class="pa-freeze-proof">'
      + '<div><span>FREEZE PROOF</span><strong>' + esc(shortHash(live.freeze_sha256)) + '</strong><small>Immutable forecast hash</small>' + (live.freeze_receipt_public_path?'<a class="pa-audit-link" href="' + esc(live.freeze_receipt_public_path) + '" target="_blank" rel="noopener">View freeze receipt →</a>':'') + '</div>'
      + '<div><span>SCORE FAMILY</span><strong>PRICE RANGE PRECISION</strong><small>Same family that becomes the verified CN score</small></div>'
      + '<div><span>FORMULA</span><strong>70% containment + 30% overlap</strong><small>No live re-weighting</small></div>'
      + '<div><span>PUBLIC RECORD</span><strong>' + esc(recordLabel(live)) + '</strong><small>' + (live.freeze_record_kind==='MIGRATED_VERIFIED_FREEZE'?'Forecast was frozen prospectively; the site receipt was materialized during migration.':'X is optional distribution, not required for validity.') + '</small></div>'
    + '</div>'
    + '<section class="pa-ranges"><div class="pa-section-head"><div><span class="pa-kicker">FROZEN PRICE RANGES</span><h3>Six rows. Same rows from Monday to final score.</h3></div><p>Observed ranges expand only with new hourly outcomes. Frozen ranges never move.</p></div>'
      + '<div class="pa-window-grid">' + windowCard(live,'day_1_2','DAY 1–2') + windowCard(live,'day_3_4','DAY 3–4') + windowCard(live,'day_5_7','DAY 5–7') + '</div>'
    + '</section>'
    + sequenceRail(live)
    + '<div class="pa-pipeline" aria-label="Cycle Navigator precision lifecycle">'
      + '<div class="done"><i>1</i><span>FROZEN</span><b>' + esc(stamp(live.frozen_at_utc)) + '</b></div><em>→</em>'
      + '<div class="current"><i>2</i><span>LIVE</span><b>' + esc(running) + ' · ' + esc(stamp(live.live_as_of_utc)) + '</b></div><em>→</em>'
      + '<div><i>3</i><span>VERIFIED</span><b>Locks after 168h settlement</b></div>'
    + '</div>'
    + '<p class="pa-footnote">Provisional means “correct so far against complete observed data to this timestamp.” It can move while an open window is still accumulating. STALE means the last complete owner observation is older than the public freshness SLA; the score is preserved but is not presented as current. The verified number is written only after the completed week is settled and then becomes the official public CN Price Range Precision shown in this Proof tab.</p>'
    + archivePanel()
    + '</section>';
}

function litePanel(snapshot) {
  const live = snapshot?.public_live_precision;
  if (live?.contract !== 'CN_PUBLIC_LIVE_PRICE_PRECISION_v1') return '';
  const running = score(live.running_price_precision_pct);
  const fresh = freshnessMeta(live);
  const phase = live.running_price_precision_pct == null ? 'AWAITING' : (fresh.stale ? 'STALE' : 'LIVE');
  return '<section id="publicLiveAccountabilityLite" class="pa-lite' + (fresh.stale?' stale':'') + '">';
    + '<div class="pa-lite-mark"><i></i><span>WEEKLY TRACK RECORD · ' + esc(phase) + '</span></div>'
    + '<div class="pa-lite-score"><strong>' + esc(running) + '</strong><small>provisional Price Range Precision</small></div>'
    + '<div class="pa-lite-meta"><span>CN #' + esc(live.public_issue_number) + ' · ' + esc(live.forecast_week) + '</span><b>Frozen ' + esc(stamp(live.frozen_at_utc)) + '</b><small>' + (fresh.stale?'Last complete observation ':'Live as of ') + esc(stamp(live.live_as_of_utc)) + ' · ' + esc(fresh.age) + ' · ' + esc(live.completed_rows ?? 0) + ' settled / ' + esc(live.live_rows ?? 0) + ' live</small></div>'
    + '<button type="button" data-pa-proof>View full scorecard →</button>'
    + '</section>';
}

let latest = null;
let freezeIndex = null;
let nowObserver = null;
let proofObserver = null;
let rootObserver = null;

function showProof() {
  document.querySelector('[data-tab="proof"]')?.click();
}

function mount() {
  if (!latest?.public_live_precision) return;

  const oldLegacy = document.getElementById('livePrecisionObservation');
  if (oldLegacy) oldLegacy.remove();

  const now = document.getElementById('productNow');
  if (now && !document.getElementById('publicLiveAccountabilityLite')) {
    now.insertAdjacentHTML('beforeend', litePanel(latest));
    now.querySelector('[data-pa-proof]')?.addEventListener('click', showProof);
  }

  const proof = document.getElementById('productProof');
  if (proof) {
    proof.classList.add('precision-accountability-installed');
    if (!document.getElementById('publicLiveAccountability')) {
      const metrics = proof.querySelector('.proof-metrics');
      const html = fullPanel(latest);
      if (metrics && html) metrics.insertAdjacentHTML('afterend', html);
      else if (html) proof.insertAdjacentHTML('afterbegin', html);
    }
  }
}

function watch() {
  const now = document.getElementById('productNow');
  const proof = document.getElementById('productProof');
  nowObserver?.disconnect();
  proofObserver?.disconnect();
  if (now) {
    nowObserver = new MutationObserver(() => {
      if (!document.getElementById('publicLiveAccountabilityLite')) queueMicrotask(mount);
    });
    nowObserver.observe(now,{childList:true,subtree:false});
  }
  if (proof) {
    proofObserver = new MutationObserver(() => {
      if (!document.getElementById('publicLiveAccountability')) queueMicrotask(mount);
    });
    proofObserver.observe(proof,{childList:true,subtree:false});
  }
}

function watchRoots() {
  if (document.getElementById('productNow') && document.getElementById('productProof')) {
    rootObserver?.disconnect();
    rootObserver = null;
    mount();
    watch();
    watchRoots();
    return;
  }
  if (rootObserver || !document.body) return;
  rootObserver = new MutationObserver(() => {
    if (!document.getElementById('productNow') || !document.getElementById('productProof')) return;
    rootObserver?.disconnect();
    rootObserver = null;
    mount();
    watch();
  });
  rootObserver.observe(document.body,{childList:true,subtree:true});
}

async function load() {
  try {
    const [r, archive] = await Promise.all([
      fetch(DATA_URL + '?precision-accountability=' + Date.now(), {cache:'no-store'}),
      fetch(FREEZE_INDEX_URL + '?precision-accountability=' + Date.now(), {cache:'no-store'}).catch(()=>null)
    ]);
    if (!r.ok) throw new Error('precision accountability HTTP ' + r.status);
    latest = await r.json();
    freezeIndex = archive?.ok ? await archive.json() : null;
    document.getElementById('publicLiveAccountability')?.remove();
    document.getElementById('publicLiveAccountabilityLite')?.remove();
    mount();
    watch();
  } catch (error) {
    console.warn('Public precision accountability unavailable', error);
  }
}

function boot() {
  watchRoots();
  load();
  setInterval(load,5*60*1000);
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',boot,{once:true});
else boot();
})();