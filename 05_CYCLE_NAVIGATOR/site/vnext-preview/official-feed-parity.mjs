/**
 * Read-only Cycle Navigator vNext adapter for the EXISTING production site feeds.
 *
 * Inputs MUST be the official site/build-public.mjs outputs:
 *   dist/data/latest.json  (CN_PUBLIC_SNAPSHOT_V2)
 *   dist/data/compass.json (PUBLIC_COMPASS_PROJECTION_v1)
 *
 * This module does not fetch secrets, publish a forecast, score prices,
 * change official actions, or generate any production HTML.
 * Keep it on the isolated design branch until source parity is accepted.
 */

import { officialPullbackDisplay } from './official-pullback-eta.mjs';
import { officialPullbackStage } from './official-pullback-stage.mjs';
import { officialPullbackInvestorView } from './official-pullback-investor-view.mjs';
import { officialBullBear } from './official-bullbear.mjs';
import { officialPathView } from './official-path.mjs';

const RANGE_FORMULA = '70pct_containment_plus_30pct_jaccard';
const SCORE_CONTRACT = 'CN_PUBLIC_WEEKLY_SCORECARD_v1';
const PUBLIC_SERIES_CONTRACT = 'CN_PUBLIC_SERIES_INDEX_v1';
const VALID_WEEKLY_HEALTH = new Set(['OK', 'PASS', 'DEGRADED']);
const HOUR_MS = 3600000;

function finite(value) {
  return typeof value === 'number' && Number.isFinite(value);
}

function validUtc(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d(?:\.\d+)?)?(?:Z|[+-]\d\d:\d\d)$/.test(value)) return null;
  const unix = Date.parse(value);
  return Number.isFinite(unix) ? unix : null;
}

function normalizeAge(value, nowEpochMs, maxHours) {
  const issued = validUtc(value);
  if (issued === null) return 'NO_TIMESTAMP';
  const diff = nowEpochMs - issued;
  if (diff < -5 * 60000) return 'FUTURE_TIMESTAMP';
  if (diff > maxHours * HOUR_MS) return 'STALE';
  return 'FRESH';
}

function sourceRange(low, high) {
  return finite(low) && finite(high) && low > 0 && high > low ? { low, high } : null;
}

function scoreRowEligible(row) {
  return row && ['forecast_low', 'forecast_high', 'actual_low', 'actual_high', 'score'].every((field) => finite(row[field])) &&
    row.forecast_low > 0 && row.forecast_low < row.forecast_high &&
    row.actual_low > 0 && row.actual_low <= row.actual_high &&
    row.score >= 0 && row.score <= 100 &&
    ['BTC', 'ETH'].includes(row.asset) &&
    ['day_1_2', 'day_3_4', 'day_5_7'].includes(row.window);
}

/**
 * @param {object} latest official generated latest.json
 * @param {object} compass official generated compass.json
 * @param {object} options for deterministic tests: {nowUtc, compassMaxAgeHours, deliveryMaxAgeHours}
 * @returns {object} source-bounded public presentation state only
 */
export function inspectOfficialPublicFeeds(latest, compass, options = {}) {
  const {
    nowUtc = new Date().toISOString(),
    compassMaxAgeHours = 24,
    deliveryMaxAgeHours = 24
  } = options;
  const nowEpochMs = validUtc(nowUtc);
  if (nowEpochMs === null || !finite(compassMaxAgeHours) || compassMaxAgeHours <= 0 ||
      !finite(deliveryMaxAgeHours) || deliveryMaxAgeHours <= 0) {
    throw new Error('INVALID_READBACK_CLOCK_POLICY');
  }
  const result = {
    contract: 'CN_VNEXT_PUBLIC_FEED_PARITY_v1',
    source_authority: 'READ_ONLY_PRESENTATION',
    generated_at: latest?.generated_at ?? null,
    delivery_health: 'UNAVAILABLE',
    weekly: {
      state: 'UNAVAILABLE', public_issue_number: null, machine_issue_number: null,
      forecast_week: null, btc_range: null, eth_range: null, path_state: 'UNAVAILABLE'
    },
    compass: {
      state: 'UNAVAILABLE', compass_id: null, issued_at_utc: null,
      weekly_alignment: 'UNVERIFIED', action_now: 'UNAVAILABLE',
      pullback_risk_state: 'UNAVAILABLE', distribution_risk: 'UNKNOWN',
      sell_assessment_state: 'UNAVAILABLE', reentry_state: 'UNAVAILABLE',
      pullback_window: null, pullback_stage: null, pullback_investor_facts: null, bull_bear_1_3d: null,
      permit_path_live_gates: false
    },
    completed_score: {
      state: 'UNAVAILABLE', public_issue_number: null, forecast_week: null,
      price_range_precision: null, btc_score: null, eth_score: null,
      intraday_window_scores: null, rows: [],
      market_structure_precision: null, combined_score: null,
      proof_state: 'NOT_INDEPENDENTLY_SEALED'
    },
    path: {state:'UNAVAILABLE',source_issue:null,source_week:null,source_health:'UNAVAILABLE',current_checkpoint:null,next_checkpoint:null,phase_eta:null,altseason:null,rotation:[],full_phases:[]},
    edge_claims: { status: 'NO_AUTHENTICATED_FEED', score: null, source: null },
    restrictions: ['NO_SITE_GENERATED_SIGNAL', 'NO_SELL_FROM_PULLBACK',
      'NO_GUESSED_ETA', 'NO_PRICE_SCORE_RECALCULATION', 'NO_CROSS_ERA_AGGREGATE']
  };

  if (latest?.schema !== 'CN_PUBLIC_SNAPSHOT_V2' ||
      latest.public_series?.contract !== PUBLIC_SERIES_CONTRACT ||
      compass?.contract !== 'PUBLIC_COMPASS_PROJECTION_v1') return result;

  result.delivery_health = normalizeAge(latest.generated_at, nowEpochMs, deliveryMaxAgeHours);

  const publicProjection = latest.public_series?.current_public_projection;
  const wk = latest.pointer;
  const pkg = latest.package;
  const issue = publicProjection?.public_issue_number;
  const forecastWeek = publicProjection?.forecast_week;
  const machineIssue = wk?.issue_number;
  const isoWeek = Number(wk?.iso_week), isoYear = Number(wk?.iso_year);
  const expectedWeek = Number.isInteger(isoYear) && Number.isInteger(isoWeek) &&
    isoWeek >= 1 && isoWeek <= 53 ? isoYear + '-W' + String(isoWeek).padStart(2, '0') : null;
  const weeklyAligned = Number.isInteger(issue) && issue > 0 &&
    Number.isInteger(machineIssue) && Number.isInteger(pkg?.issue_number) &&
    machineIssue === pkg.issue_number && typeof forecastWeek === 'string' &&
    forecastWeek === expectedWeek && VALID_WEEKLY_HEALTH.has(pkg?.status) &&
    pkg.status === wk.status;
  if (weeklyAligned) {
    const freeze = pkg.forecast_freeze || {};
    result.weekly = {
      state: pkg.status === 'DEGRADED' ? 'DEGRADED' : 'OK',
      public_issue_number: issue,
      machine_issue_number: machineIssue,
      forecast_week: forecastWeek,
      btc_range: sourceRange(freeze.btc_range_low, freeze.btc_range_high),
      eth_range: sourceRange(freeze.eth_range_low, freeze.eth_range_high),
      path_state: 'WEEKLY_CONTEXT_ONLY'
    };
  } else {
    result.weekly.state = 'MISMATCH';
  }

  const compassAge = normalizeAge(compass.issued_at_utc, nowEpochMs, compassMaxAgeHours);
  // A separate Compass may remain authoritative in the weekly sense, but
  // stale or self-contradictory DELIVERY bytes must never be shown as live NOW.
  const bundleTime = validUtc(latest.generated_at);
  const compassTime = validUtc(compass.issued_at_utc);
  const chronologyAligned = bundleTime !== null && compassTime !== null &&
    compassTime <= bundleTime + 5 * 60000;
  const cOK = result.delivery_health === 'FRESH' && chronologyAligned &&
    compass.data_status === 'OK' && typeof compass.compass_id === 'string' &&
    compass.compass_id.trim().length > 0 && compassAge === 'FRESH';
  const alignedContext = compass.weekly_context;
  const cnJoined = weeklyAligned &&
    alignedContext?.status === 'ALIGNED' &&
    alignedContext?.forecast_week === forecastWeek &&
    alignedContext?.public_issue_number === issue;
  // An otherwise fresh Compass is not actionable without a matching public CN identity.
  // The original hash-verified Official source owner may expire BEFORE the
  // public projection's issue-age window. Never extend it with an arbitrary TTL.
  const ownerFreshness = compass.full_stack?.official_freshness;
  const ownerExpiry = validUtc(ownerFreshness?.valid_until_utc);
  const ownerAsOf = validUtc(ownerFreshness?.source_asof_utc);
  const ownerCurrent = ownerFreshness?.contract === 'OFFICIAL_COMPASS_SOURCE_FRESHNESS_READBACK_v1' &&
    ownerFreshness?.status === 'VERIFIED_OWNER_POLICY' &&
    ownerFreshness?.semantics === 'SOURCE_FRESHNESS_EXPIRY_NOT_FORECAST_ETA' &&
    ownerAsOf !== null && ownerExpiry !== null && ownerAsOf <= ownerExpiry &&
    ownerAsOf <= nowEpochMs + 5 * 60000 && nowEpochMs < ownerExpiry;
  const actionable = cOK && cnJoined && ownerCurrent;
  result.compass = {
    state: actionable ? 'FRESH' : compassAge === 'STALE' ? 'STALE' : 'UNAVAILABLE',
    compass_id: typeof compass.compass_id === 'string' ? compass.compass_id : null,
    issued_at_utc: compass.issued_at_utc ?? null,
    weekly_alignment: cnJoined ? 'ALIGNED' :
      alignedContext?.status === 'MISMATCH' ? 'MISMATCH' : 'UNVERIFIED',
    action_now: actionable && typeof compass.action_now === 'string' ? compass.action_now : 'UNAVAILABLE',
    pullback_risk_state: actionable ? (compass.protection_tracker?.pullback_risk_state || 'UNAVAILABLE') : 'UNAVAILABLE',
    distribution_risk: actionable ? (compass.protection_tracker?.distribution_risk || 'UNKNOWN') : 'UNKNOWN',
    sell_assessment_state: actionable ? (compass.sell_assessment?.state || 'UNAVAILABLE') : 'UNAVAILABLE',
    reentry_state: actionable ? (compass.protection_tracker?.reentry_state || 'UNAVAILABLE') : 'UNAVAILABLE',
    // A source week is not by itself an event onset. Public ETA is permitted
    // ONLY if verified Compass and weekly public CN identities are aligned.
    pullback_window: cOK && cnJoined ?
      (() => {
        const p = officialPullbackDisplay(compass, { forecast_week: forecastWeek }, 'da');
        return p.state === 'VALID' ? {
          window_kind: p.windowKind,
          risk_state: p.riskState,
          window_start_utc: p.windowStartUtc,
          window_end_utc: p.windowEndUtc,
          exact_onset: false,
          headline: p.headline,
          caution: p.note
        } : null;
      })() : null,
    pullback_stage: cOK && cnJoined ? (() => {
      const p=officialPullbackStage(compass, {forecast_week: forecastWeek}, 'da');
      return p.status==='SOURCE_VALID' ? {
        source_risk_state:p.sourceRiskState, stage_label:p.stageLabel,
        ordinal_risk_class:p.ordinalRiskClass, proximity_label:p.proximityLabel,
        evidence_quality:p.qualityLabel, quality_semantics:p.qualitySemantics,
        source_week:p.sourceWeek, authority:'PRESENTATION_ONLY',
        sell_permission:false, confirmed_market_decline:false
      } : null;
    })() : null,
    pullback_investor_facts: cOK && cnJoined ? (() => {
      const v=officialPullbackInvestorView(compass,{forecast_week:forecastWeek},'da');
      return v.status==='VALID' ? {
        authority:'SOURCE_ONLY_UI',risk_state:v.source_risk_state,
        items:v.rows
      } : null;
    })() : null,
    bull_bear_1_3d: actionable ? officialBullBear(compass, '1_3d') : null,
    permit_path_live_gates: actionable
  };

  // PATH is the weekly CN structure plus aligned Official Compass tier ladder.
  // No independent site phase engine: absent/late/misaligned source cannot show
  // a LIVE checkpoint, fake ETH-led transition or interpolated stage ETA.
  if (cOK && cnJoined && Array.isArray(pkg?.rotation_ladder) &&
      Array.isArray(pkg?.altseason_countdown) &&
      Array.isArray(compass.capitalization_ladder)) {
    const view=officialPathView({
      source_status:'OFFICIAL_CANONICAL_PUBLIC_DELIVERY',
      weekly:{
        public_issue_number:issue,forecast_week:forecastWeek,status:pkg.status,
        market_state:pkg.market_state,
        rotation_ladder:pkg.rotation_ladder,
        altseason_countdown:pkg.altseason_countdown,
        decision_projection:pkg.decision_projection,
        base_case_2_3_weeks:pkg.base_case_2_3_weeks,
        base_case_4_8_weeks:pkg.base_case_4_8_weeks
      },
      compass
    }, {mode:'live',verifiedAlignment:true,lang:'da'});
    if (view.status==='SOURCE_BOUND' && view.is_live) {
      result.path={
        state:'SOURCE_BOUND',source_issue:view.source_issue,
        source_week:view.source_week,source_health:view.source_health,
        current_checkpoint:view.current_checkpoint,
        next_checkpoint:view.next_checkpoint,
        next_gate:view.next_gate,
        phase_eta:view.phase_eta,
        source_window:view.source_window,
        full_phases:view.full_phases,
        concise_phases:view.concise_phases,
        altseason:view.altseason,rotation:view.rotation,
        structural_long:view.structural_long,
        distribution_risk:compass.protection_tracker?.distribution_risk||'UNKNOWN',
        sell:compass.sell_assessment?.state||'UNAVAILABLE',
        reentry:compass.protection_tracker?.reentry_state||'UNAVAILABLE',
        source_identity:compass.compass_id,
        official_issued_at_utc:compass.issued_at_utc
      };
    }
  }

  // Current public score is deliberately *last completed*, never current week.
  // No concatenation of Machine Scorecard or old Market/Structure scores.
  const scoreRef = latest.public_series?.latest_completed_score;
  const card = latest.public_scorecard;
  const range = card?.price_range_precision;
  const coverage = range?.actuals_hourly_coverage;
  const sixRows = range?.rows;
  const scoreMatches = card?.contract === SCORE_CONTRACT &&
    // A complete-looking numeric table is not proof of outcome maturity.
    // Both public series index and canonical scorecard must independently
    // attest the SAME final state before any percentage is displayed.
    typeof scoreRef?.status === 'string' && /^FINAL(?:_|$)/.test(scoreRef.status) &&
    card?.status === scoreRef.status &&
    Number.isInteger(scoreRef?.public_issue_number) &&
    card.public_issue_number === scoreRef.public_issue_number &&
    card.forecast_week === scoreRef.forecast_week &&
    card.public_issue_number < issue &&
    card.market_structure_precision === null &&
    card.combined_score === null &&
    range?.formula === RANGE_FORMULA &&
    finite(range.score) && range.score >= 0 && range.score <= 100 &&
    finite(scoreRef.price_range_score) &&
    Math.abs(scoreRef.price_range_score - range.score) <= 0.000001 &&
    coverage === 168 &&
    Array.isArray(sixRows) && sixRows.length === 6 &&
    sixRows.every(scoreRowEligible) &&
    new Set(sixRows.map((r) => r.asset + ':' + r.window)).size === 6;
  if (scoreMatches) {
    result.completed_score = {
      state: 'FINAL_PUBLIC_SCORECARD',
      public_issue_number: card.public_issue_number,
      forecast_week: card.forecast_week,
      price_range_precision: range.score,
      btc_score: finite(range.btc_score) ? range.btc_score : null,
      eth_score: finite(range.eth_score) ? range.eth_score : null,
      intraday_window_scores: range.intraday_window_scores ?? null,
      rows: sixRows.map((row) => ({
        asset: row.asset, window: row.window,
        forecast_low: row.forecast_low, forecast_high: row.forecast_high,
        actual_low: row.actual_low, actual_high: row.actual_high,
        score: row.score
      })),
      market_structure_precision: null,
      combined_score: null,
      proof_state: 'LEGACY_OR_PROVISIONAL_NOT_INDEPENDENTLY_SEALED'
    };
  } else {
    result.completed_score.state = card || scoreRef ? 'MISMATCH_OR_INCOMPLETE' : 'UNAVAILABLE';
  }

  // The existing generated site feeds do not include authenticated v2 typed
  // claim settlements. Never promote a W42 qualitative ABSTAIN into 100.
  return result;
}
