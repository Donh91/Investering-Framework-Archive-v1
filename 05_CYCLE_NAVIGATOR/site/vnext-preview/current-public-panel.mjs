/* Read-only current/public status rail beside the W40/W41 ARCHIVE preview.
 * Current data authority is site/build-public.mjs, not individual raw Compass
 * files, a new prediction engine, or the frozen historical seed.json.
 * If the canonical public delivery is unreachable, this panel FAILS CLOSED.
 */
import { inspectOfficialPublicFeeds } from './official-feed-parity.mjs';

export const CANONICAL_PUBLIC_DATA_ROOT =
  'https://donh91.github.io/Investering-Framework-Archive-v1/data/';
const APPROVED_ACTIONS = new Set(['HOLD_WAIT','HOLD','HARD_WAIT','WAIT','BUY','BUY_DIP','PREPARE','UNAVAILABLE']);
const APPROVED_DIRECTIONS = new Set(['UP','DOWN','MIXED','SIDEWAYS','NEUTRAL','BULLISH','BEARISH']);
const PREVIEW_UNKNOWN = Object.freeze({
  status:'UNAVAILABLE', action:'UNAVAILABLE', direction:'UNKNOWN',
  risk:'UNKNOWN', phase:'UNKNOWN', gate:'UNKNOWN',
  forecast_week:null, issue:null, issued_at_utc:null,
  generated_at:null, source_identity:null
});

const text = (v) => typeof v === 'string' && v.trim()
  ? v.trim().replace(/\s+/g,' ').slice(0,180) : null;

export function summarizeCurrentPublic(latest, compass, { nowUtc = new Date().toISOString() } = {}) {
  const view = inspectOfficialPublicFeeds(latest, compass, { nowUtc });
  const action = typeof view.compass.action_now === 'string' &&
    APPROVED_ACTIONS.has(view.compass.action_now) ? view.compass.action_now : 'UNAVAILABLE';
  const current = view.compass.state === 'FRESH' &&
    view.compass.permit_path_live_gates === true &&
    action !== 'UNAVAILABLE';
  // An archived or unjoined feed cannot supply an apparently current horizon.
  if (!current) return {
    ...PREVIEW_UNKNOWN,
    forecast_week: view.weekly.forecast_week,
    issue: view.weekly.public_issue_number,
    generated_at: text(latest?.generated_at),
    source_identity: text(compass?.compass_id)
  };
  const directionCode = compass?.horizons?.NEXT_12H?.expected_direction;
  const hasPath = view.path.state === 'SOURCE_BOUND';
  return {
    status:'CURRENT_VERIFIED',
    action,
    direction: APPROVED_DIRECTIONS.has(directionCode) ? directionCode : 'UNKNOWN',
    risk: text(view.compass.pullback_risk_state) || 'UNKNOWN',
    phase: hasPath ? text(view.path.current_checkpoint?.label) || 'UNKNOWN' : 'UNKNOWN',
    gate: hasPath ? text(view.path.next_gate) || 'UNKNOWN' : 'UNKNOWN',
    forecast_week: view.weekly.forecast_week,
    issue: view.weekly.public_issue_number,
    issued_at_utc: text(view.compass.issued_at_utc),
    generated_at: text(view.generated_at),
    source_identity: text(view.compass.compass_id)
  };
}

// Do not redirect to a different provider or silently fall back to a
// third-party mirror. Two public feed files are a single joined readback.
export async function loadCanonicalPublicFeeds(fetchImpl = fetch) {
  const read = async (filename) => {
    const url = CANONICAL_PUBLIC_DATA_ROOT + filename;
    const response = await fetchImpl(url, {cache:'no-store', mode:'cors', redirect:'error'});
    if (!response?.ok || response.url !== url) throw new Error('CANONICAL_PUBLIC_FEED_UNAVAILABLE');
    return response.json();
  };
  const [latest, compass] = await Promise.all([read('latest.json'),read('compass.json')]);
  return {latest,compass};
}

let observedFeeds = null;
let lastError = false;
const $ = (id) => document.getElementById(id);
function put(id, value) { const element = $(id); if (element) element.textContent = String(value); }

export function paintCurrentPublicPanel(language = 'da', nowUtc = new Date().toISOString()) {
  if (!$('cn-current-status')) return;
  const da = language !== 'en';
  let readback = PREVIEW_UNKNOWN;
  if (observedFeeds) {
    try {
      readback = summarizeCurrentPublic(observedFeeds.latest, observedFeeds.compass, {nowUtc});
    } catch { readback = PREVIEW_UNKNOWN; }
  }
  const verified = readback.status === 'CURRENT_VERIFIED';
  const section = $('cn-current-public-panel');
  if (section) section.dataset.state = verified ? 'CURRENT_VERIFIED' : 'UNAVAILABLE';
  put('cn-current-kicker',da?'AKTUELT · OFFENTLIG KILDE':'CURRENT · PUBLIC SOURCE');
  put('cn-current-status',verified
    ? (da?'KILDE KONTROLLERET · NU':'SOURCE VERIFIED · CURRENT')
    : (da?'UTILGÆNGELIG · IKKE LIVE':'UNAVAILABLE · NOT LIVE'));
  put('cn-current-action-label',da?'OFFICIEL HANDLING · NU':'OFFICIAL ACTION · NOW');
  put('cn-current-direction-label',da?'RETNING · NÆSTE 12 TIMER':'DIRECTION · NEXT 12 HOURS');
  put('cn-current-action', verified ? readback.action : 'UNAVAILABLE');
  put('cn-current-direction',verified ? readback.direction : 'UNKNOWN');
  put('cn-current-risk-label',da?'PULLBACK-RISIKO':'PULLBACK RISK');
  put('cn-current-risk',verified ? readback.risk : 'UNKNOWN');
  put('cn-current-phase-label',da?'CYKLUSFASE':'CYCLE PHASE');
  put('cn-current-phase',verified ? readback.phase : 'UNKNOWN');
  put('cn-current-gate-label',da?'NÆSTE KILDEGATE':'NEXT SOURCE GATE');
  put('cn-current-gate',verified ? readback.gate : 'UNKNOWN');
  const identity = readback.forecast_week && readback.issue
    ? 'CN #'+readback.issue+' · '+readback.forecast_week : (da?'Uge ikke verificeret':'Week unverified');
  put('cn-current-provenance',verified
    ? identity+' · '+(da?'udstedt ':'issued ')+(readback.issued_at_utc||'—')
    : (da?'Ingen verificeret aktuel handling. Arkivet nedenfor er historisk.'
          :'No verified current action. The archive below is historical.'));
  put('cn-current-delivery',verified
    ? (da?'Offentlig levering: ':'Public delivery: ')+(readback.generated_at||'—')
    : (lastError
      ? (da?'Offentlige data kan ikke indlæses eller valideres.':'Public feeds could not be loaded or validated.')
      : (da?'Kilde udløbet, ufuldstændig eller endnu ikke verificeret.'
            :'Source expired, incomplete or not yet verified.')));
}

export async function initializeCurrentPublicPanel(language = 'da') {
  paintCurrentPublicPanel(language);
  try {
    observedFeeds = await loadCanonicalPublicFeeds();
    lastError = false;
  } catch {
    observedFeeds = null;
    lastError = true;
  }
  paintCurrentPublicPanel(document.documentElement.lang || language);
  // No repeated network requests: the page rechecks its cached, original
  // source expiry every minute, so an unattended tab never stays LIVE forever.
  if (typeof window !== 'undefined') {
    window.setInterval(() => paintCurrentPublicPanel(document.documentElement.lang || 'da'), 60000);
    window.addEventListener('focus', () => paintCurrentPublicPanel(document.documentElement.lang || 'da'));
  }
}
