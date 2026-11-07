/**
 * GitHub Pages W46 interactive visual acceptance: TEST-ONLY synthetic market fixtures.
 * Never imported by canonical Pages producers, CN forecast publisher or official client.
 * Each screenshot uses the ORIGINAL deployed site HTML, CSS and Graph B runtime.
 */
const HOUR = 3_600_000;
const DAY = 24 * HOUR;
const monday = Date.parse('2026-11-09T00:00:00Z');
const asIso = ms => new Date(ms).toISOString().replace('.000Z', 'Z');
const assets = {
  BTC: {
    closes: [72860, 73450, 72720, 73880, 74460, 74020, 75140],
    lows: [71780, 72050, 71650, 72500, 73300, 72900, 73900],
    highs: [73750, 74300, 74050, 74750, 75350, 75400, 76200],
    observedStart: 72450,
    hourlyDrift: 11,
    amplitude: 65,
  },
  ETH: {
    closes: [2413, 2441, 2405, 2458, 2493, 2470, 2533],
    lows: [2369, 2380, 2360, 2410, 2440, 2420, 2490],
    highs: [2460, 2488, 2485, 2511, 2545, 2550, 2590],
    observedStart: 2383,
    hourlyDrift: 0.46,
    amplitude: 2,
  },
};
const modes = ['mandag', 'onsdag', 'afstaar', 'valutafejl'];
const clone = value => JSON.parse(JSON.stringify(value));
const dayStart = n => asIso(monday + n * DAY);

export function buildFixture(mode = 'mandag') {
  if (!modes.includes(mode)) throw new Error('QA_SCENE_UNSUPPORTED');
  const abstain = mode === 'afstaar';
  const quote = mode === 'valutafejl' ? 'USD' : 'USDT';
  const wednesday = mode === 'onsdag';
  const observedHours = wednesday ? 60 : 12;
  const nowUtc = wednesday ? '2026-11-11T17:30:00Z' : '2026-11-09T16:30:00Z';
  const observedThroughUtc = asIso(monday + observedHours * HOUR);
  const scoringFirst = '2026-11-09T08:00:00Z';
  const issuedAt = '2026-11-09T07:00:00Z';

  const windowScores = {};
  const rows = [];
  const windows = [['day_1_2', 0, 2], ['day_3_4', 2, 4], ['day_5_7', 4, 7]];
  for (const [key, start, end] of windows) {
    windowScores[key] = {
      window_start_utc: dayStart(start),
      window_end_utc: dayStart(end),
      scoring_start_utc: scoringFirst,
    };
    for (const [asset, source] of Object.entries(assets)) {
      rows.push({
        asset,
        window: key,
        forecast_low: Math.min(...source.lows.slice(start, end)),
        forecast_high: Math.max(...source.highs.slice(start, end)),
      });
    }
  }

  const dailyPath = { contract: 'CN_FROZEN_DAILY_PRICE_PATH_v1', forecast_week: '2026-W46' };
  const dailyRanges = { contract: 'CN_FROZEN_DAILY_RANGE_PLAN_v1', forecast_week: '2026-W46' };
  const hourlyPath = {
    contract: 'CN_PUBLIC_HOURLY_PRICE_PATH_v1',
    source: 'HOURLY_SPOT_PASS_ONLY',
    semantics: 'OBSERVED_HOURLY_CLOSE_NOT_A_PROSPECTIVE_FORECAST',
    forecast_week: '2026-W46',
    public_issue_number: 33,
    observed_through_utc: observedThroughUtc,
  };
  const dailyObservations = {
    contract: 'CN_PUBLIC_DAILY_OBSERVATIONS_v1',
    timezone: 'UTC',
    observed_through_utc: observedThroughUtc,
  };
  const historyActual = [];

  for (const [asset, source] of Object.entries(assets)) {
    dailyPath[asset] = {
      status: abstain ? 'UNAVAILABLE' : 'PUBLISHED',
      reason: abstain ? 'Simuleret kildeafståelse, ingen original dagsprisprognose.' : '',
      points: abstain ? [] : source.closes.map((expected_close, i) => ({
        day: i + 1, expected_close, low: source.lows[i], high: source.highs[i],
      })),
    };
    dailyRanges[asset] = {
      status: abstain ? 'UNAVAILABLE' : 'PUBLISHED',
      reason: abstain ? 'Simuleret kildeafståelse, ingen original daglig range.' : '',
      points: abstain ? [] : source.closes.map((_, i) => ({
        day: i + 1,
        low: source.lows[i],
        high: source.highs[i],
        why: 'Fiktiv, individuelt fastlagt dagsrange til GitHub UI-kontrol.',
        invalidate_if: 'Den oprindelige kildeidentitet kan ikke bekræftes.',
      })),
    };

    const prices = [];
    const hourly = [];
    for (let h = 1; h <= observedHours; h += 1) {
      const movement = [0, 1.4, -1.2, 0.7, 1.9, -0.8, 0.2, 1.1][h % 8];
      const price = Math.round((source.observedStart + h * source.hourlyDrift + movement * source.amplitude) * 100) / 100;
      const observedAt = asIso(monday + h * HOUR);
      hourly.push({ observed_at_utc: observedAt, close: price });
      prices.push(price);
      if (asset === 'BTC') historyActual.push({ time: observedAt, close: price });
    }
    hourlyPath[asset] = hourly;
    dailyObservations[asset] = Array.from({ length: 7 }, (_, i) => {
      const hours = Math.max(0, Math.min(24, observedHours - i * 24));
      const section = prices.slice(i * 24, i * 24 + hours);
      return {
        day: i + 1,
        date: dayStart(i).slice(0, 10),
        coverage_complete_to_date: hours > 0,
        observed_hours: hours,
        expected_hours: hours,
        status: hours === 24 ? 'COMPLETE' : 'LIVE',
        low: hours ? Math.min(...section) : null,
        high: hours ? Math.max(...section) : null,
        close: hours ? section.at(-1) : null,
        as_of_utc: asIso(monday + (i * 24 + hours) * HOUR),
      };
    });
  }
  const snapshot = {
    schema: 'CN_PUBLIC_SNAPSHOT_V2',
    public_series: {
      current_public_projection: { public_issue_number: 33, forecast_week: '2026-W46' },
    },
    public_live_precision: {
      contract: 'CN_PUBLIC_LIVE_PRICE_PRECISION_v1',
      public_issue_number: 33,
      forecast_week: '2026-W46',
      frozen_at_utc: issuedAt,
      scoring_valid_from_utc: scoringFirst,
      freshness_sla_minutes: 90,
      live_as_of_utc: observedThroughUtc,
      window_scores: windowScores,
      rows,
      price_quote_labels: {
        contract: 'CN_PUBLIC_PRICE_QUOTE_LABELS_v1',
        actual_native_spot: { BTC: 'USDT', ETH: 'USDT' },
        forecast_model_declared: { BTC: quote, ETH: quote },
        conversion_applied: false,
      },
      daily_price_path: dailyPath,
      daily_range_plan: dailyRanges,
      hourly_price_path: hourlyPath,
      daily_observations: dailyObservations,
    },
  };
  const lineage = {
    contract: 'CN_PUBLICATION_LINEAGE_RELEASE_RECEIPT_v1',
    forecast_week: '2026-W46',
    public_issue_number: 33,
    source_to_public_equality: 'PASS',
    last_observed_close_utc: observedThroughUtc,
  };
  return {
    mode, nowUtc, quote, observedHours, issuedAt, observedThroughUtc,
    snapshot, lineage, historyActual,
    frozenForecast: clone({ BTC: dailyPath.BTC, ETH: dailyPath.ETH }),
    frozenRanges: clone({ BTC: dailyRanges.BTC, ETH: dailyRanges.ETH }),
  };
}

export async function historyFixture(fixture) {
  const raw = JSON.stringify({
    forecast: fixture.frozenForecast,
    ranges: fixture.frozenRanges,
    issued_at: fixture.issuedAt,
    week: '2026-W46',
    quote: fixture.quote,
  });
  const bytes = new TextEncoder().encode(raw);
  const hash = await crypto.subtle.digest('SHA-256', bytes);
  const sourceHash = Array.from(new Uint8Array(hash)).map(n => n.toString(16).padStart(2, '0')).join('');
  return {
    contract: 'CN_GRAPH_HISTORY_TIMELINE_v1',
    actual_unit: 'USDT',
    weeks: [
      {
        week: '2026-W45',
        forecast_status: 'UNAVAILABLE',
        forecast_model_declared_quote: 'UNAVAILABLE',
        forecast: [],
        observed_hours: 0,
        actual_status: 'Ingen simuleret historik',
      },
      {
        week: '2026-W46',
        forecast_status: fixture.frozenForecast.BTC.status,
        forecast_model_declared_quote: fixture.quote,
        issued_at_utc: fixture.issuedAt,
        first_eligible_utc: '2026-11-09T08:00:00Z',
        source_sha256: sourceHash,
        forecast: fixture.frozenForecast.BTC.points,
        observed_hours: fixture.observedHours,
        actual_status: 'Kun fiktiv testserie',
      },
    ],
    actual: fixture.historyActual,
  };
}
