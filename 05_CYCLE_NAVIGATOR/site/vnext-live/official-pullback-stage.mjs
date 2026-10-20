/**
 * Source-only progressive presentation for Official Compass pullback risk.
 *
 * The source already owns the classification: NORMAL / BUILDING / ELEVATED /
 * HIGH / CONFIRMED / UNAVAILABLE. This file only translates an existing
 * validated state to language and context, never computes a new risk state,
 * an event clock, action, severity in market returns, or a confidence percent.
 *
 * IMPORTANT: a higher classification is NOT a prediction that a pullback
 * will inevitably begin, nor an independent "imminent" signal. Confidence is
 * evidence quality, not calibrated probability.
 */
import { officialPullbackDisplay } from './official-pullback-eta.mjs';

const STAGES = Object.freeze({
  NORMAL: {
    da:'Roligt · ingen aktiv varsling', en:'Quiet · no active warning', order:0
  },
  BUILDING: {
    da:'Opbygning · under observation', en:'Building · under watch', order:1
  },
  ELEVATED: {
    da:'Forhøjet · følg næste bekræftelse', en:'Elevated · await confirmation', order:2
  },
  HIGH: {
    da:'Høj risiko · vurder udviklingen', en:'High risk · reassess conditions', order:3
  },
  CONFIRMED: {
    da:'Bekræftet risikotilstand · følg officiel opdatering',
    en:'Confirmed risk state · follow official update', order:4
  }
});
const QUALITY = Object.freeze({
  LOW:{da:'Lav evidenskvalitet',en:'Low evidence quality'},
  MEDIUM:{da:'Middel evidenskvalitet',en:'Moderate evidence quality'},
  HIGH:{da:'Høj evidenskvalitet',en:'High evidence quality'}
});
export function officialPullbackStage(compass, weekly, lang='da') {
  const locale=lang==='en'?'en':'da';
  const timed=officialPullbackDisplay(compass, weekly, locale);
  const source=compass?.protection_tracker;
  const phase=timed.state==='VALID' ? STAGES[timed.riskState] : null;
  const quality=phase ? QUALITY[source?.confidence_quality] : null;
  const unavailable=locale==='da'?'Kan ikke vurderes':'Cannot be assessed';
  const unknownQuality=locale==='da'?'Evidenskvalitet ukendt':'Evidence quality unknown';
  const noOnset=locale==='da'?'Nært forestående: ikke dokumenteret':'Imminent: not evidenced';
  // A typed prospective window can support a *possible interval*, but neither
  // "imminent", true event onset nor any numerical certainty without a separate
  // first-party forecast authority and point-in-time evidence.
  return {
    contract:'CN_PUBLIC_PULLBACK_STAGE_PRESENTATION_v1',
    authority:'PRESENTATION_ONLY',
    sourceRiskState:phase ? timed.riskState : 'UNAVAILABLE',
    status:phase ? 'SOURCE_VALID' : 'UNAVAILABLE',
    stageLabel:phase?.[locale] || unavailable,
    // "order" is an ordinal classification, NOT a progress fraction, %
    // probability, confidence score or a forecast of time remaining.
    ordinalRiskClass:phase?.order ?? null,
    windowKind:phase ? timed.windowKind : 'UNAVAILABLE',
    etaLabel:phase ? timed.headline : timed.headline,
    proximityLabel:noOnset,
    qualityLabel:quality?.[locale] || unknownQuality,
    qualitySemantics:'EVIDENCE_QUALITY_NOT_PROBABILITY',
    sellPermission:false,
    confirmedMarketDecline:false,
    explanation:timed.note,
    alertQualified:null,
    sourceWeek:phase ? timed.sourceWeek : null
  };
}
