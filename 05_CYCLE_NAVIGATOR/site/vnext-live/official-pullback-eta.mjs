/**
 * Official Pullback time-window reader for CN vNext.
 *
 * Public-display only. NO prediction, independent ETA model, SELL permission,
 * retrospective onset assignment, probability or unverified date interpolation.
 * Calendar conversion is allowed solely for explicitly source-bounded forecast
 * week + ordinal day labels (not a prediction of a real pullback event).
 */
const RISK_STATES = new Set(['NORMAL','BUILDING','ELEVATED','HIGH','CONFIRMED','UNAVAILABLE']);

function isoWeekMonday(forecastWeek) {
  if (!/^\d{4}-W\d{2}$/.test(String(forecastWeek))) return null;
  const [year, week] = forecastWeek.split('-W').map(Number);
  if (week < 1 || week > 53) return null;
  const jan4 = new Date(Date.UTC(year,0,4));
  const day = (jan4.getUTCDay()+6)%7;
  const monday = new Date(jan4.valueOf()-day*86400000+(week-1)*7*86400000);
  const thursday = new Date(monday.valueOf()+3*86400000);
  if (thursday.getUTCFullYear()!==year) return null;
  return monday;
}
const ymd = (date) => date.toISOString().slice(0,10);
const offset = (monday,dayNumber) => ymd(new Date(monday.valueOf()+(dayNumber-1)*86400000));
function dateUtc(value) {
  if (typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/.test(value)) return null;
  const n=Date.parse(value);
  return Number.isFinite(n)?n:null;
}
const compactDay = (ymdValue, lang) => {
  const locale = lang==='en'?'en-GB':'da-DK';
  return new Intl.DateTimeFormat(locale,{timeZone:'UTC',day:'numeric',month:'short'}).format(new Date(ymdValue+'T12:00:00Z'));
};

export function officialPullbackDisplay(compass, weekly, language='da') {
  const lang = language==='en'?'en':'da';
  const unknown = {
    state:'UNAVAILABLE', riskState:'UNAVAILABLE', sourceWeek:null, windowKind:'UNAVAILABLE',
    windowStartUtc:null, windowEndUtc:null, exactOnset:false,
    headline:lang==='da'?'ETA ikke tilgængelig':'ETA unavailable',
    note:lang==='da'?'Ingen bekræftet start/slut eller SELL-signal.':'No confirmed onset/end or SELL signal.'
  };
  const r=compass?.protection_tracker;
  const forecastWeek=weekly?.forecast_week;
  const monday=isoWeekMonday(forecastWeek);
  if (compass?.data_status!=='OK' || r?.contract!=='COMPASS_PROTECTION_TRACKER_v1' ||
      r?.authority?.new_market_classifier!==false ||
      r?.authority?.portfolio_execution!==false ||
      !RISK_STATES.has(r.pullback_risk_state) ||
      !monday) return unknown;

  const base={...unknown,state:'VALID',riskState:r.pullback_risk_state,sourceWeek:forecastWeek};
  // A risk owner may explicitly publish NO warning. This must not become
  // "possible this week" merely because a forecast week exists.
  if (r.pullback_risk_state==='NORMAL') {
    return {...base,windowKind:'NO_ACTIVE_WATCH',
      headline:lang==='da'?'Ingen aktiv pullback-watch':'No active pullback watch',
      note:lang==='da'?
        'Ingen varslet start/slut. Sælgesignal skal komme separat.':
        'No forecast onset/end. SELL authority remains separate.'};
  }
  if (r.pullback_risk_state==='UNAVAILABLE') {
    return {...unknown,sourceWeek:forecastWeek};
  }
  const extended=r.public_explanation;
  if (extended!==null && extended!==undefined) {
    if (extended.contract!=='CN_PUBLIC_PROTECTION_COPY_v1' ||
        extended.forecast_week!==forecastWeek ||
        extended.risk_state!==r.pullback_risk_state) {
      return {...base,windowKind:'SOURCE_MISMATCH',
        headline:lang==='da'?'ETA ikke verificeret':'ETA not verified'};
    }

    const start=extended.onset_start_utc, end=extended.onset_end_utc;
    if (start!==null && start!==undefined || end!==null && end!==undefined) {
      const a=dateUtc(start),b=dateUtc(end);
      if (a!==null && b!==null && a<=b) {
        const startIso=ymd(new Date(a)),endIso=ymd(new Date(b));
        return {...base,windowKind:'GOVERNED_PROSPECTIVE_WINDOW',
          windowStartUtc:start,windowEndUtc:end,exactOnset:false,
          headline:lang==='da'?
            'Prognosevindue: '+compactDay(startIso,lang)+' – '+compactDay(endIso,lang):
            'Forecast window: '+compactDay(startIso,lang)+' – '+compactDay(endIso,lang),
          note:lang==='da'?
            'Kildens mulige tidsvindue; faktisk start/slut er ikke bekræftet. Ikke SELL.':
            'A possible source forecast window; actual onset/end remain unconfirmed. Not SELL.'};
      }
      return {...base,windowKind:'INVALID_DATE_PAIR',
        headline:lang==='da'?'ETA ikke verificeret':'ETA not verified'};
    }
    // A governed WEEK is not a forecast of a specific onset or end.
    return {...base,windowKind:'WEEK_ONLY',
      headline:lang==='da'?'Muligt i uge '+forecastWeek.slice(-2)+' · ingen præcis ETA':
        'Possible in week '+forecastWeek.slice(-2)+' · no precise ETA',
      note:lang==='da'?
        'Start/slut og størrelse er ikke kvantificeret. Kun watch – ikke SELL.':
        'Onset/end and size are unquantified. Watch only – not SELL.'};
  }

  // Older archived official snapshots have a human ETA sentence but no typed
  // public_explanation. Only this exact canonical W41 source phrase is eligible
  // for DAY ordinal mapping. Otherwise keep the window unavailable.
  const match=/^Possible W(\d{2}) retest, particularly Day ([1-7])–([1-7]); timing and occurrence unconfirmed\.$/
    .exec(String(r.eta_window||''));
  if (match && Number(match[1])===Number(forecastWeek.slice(-2))) {
    const first=Number(match[2]),last=Number(match[3]);
    if (first<=last) {
      const a=offset(monday,first),b=offset(monday,last);
      return {...base,windowKind:'ARCHIVED_SCENARIO_DAY_WINDOW',
        windowStartUtc:a,windowEndUtc:b,exactOnset:false,
        headline:lang==='da'?
          'Muligt vindue: '+compactDay(a,lang)+' – '+compactDay(b,lang)+' (uge '+match[1]+')':
          'Possible window: '+compactDay(a,lang)+' – '+compactDay(b,lang)+' (W'+match[1]+')',
        note:lang==='da'?
          'Historisk kildevurdering; hverken start, slut eller selve faldet blev lovet. Ikke SELL.':
          'Historic source scenario; onset, end and even a decline were unconfirmed. Not SELL.'};
    }
  }
  return {...base,windowKind:'NO_SUPPORTED_ONSET',
    headline:lang==='da'?'Start/slut: ikke fastlagt':'Onset/end: not established',
    note:lang==='da'?
      'Official Compass har ikke angivet en pålidelig ETA. Ingen SELL-tilladelse.':
      'Official Compass has not given a reliable ETA. No SELL authorization.'};
}
