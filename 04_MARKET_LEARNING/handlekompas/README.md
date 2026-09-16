# KOMPAS / Handlekompas

KOMPAS is a first-class point-in-time decision and learning layer for the investment framework.

It has two linked products:

1. `NATIVE_HANDLEKOMPAS_v1` — the conservative source-call-free action owner generated from pinned Auto Market State.
2. `COMPLETE_KOMPAS_v1` — the richer investor-facing and research-facing readback that adds explicit time horizons, market direction, the BTC→microcap capital ladder, ETA explanations and point-in-time evidence provenance.

Cycle Navigator remains the frozen weekly forecast. KOMPAS is the live intra-week answer to **what should I do now, what is likely over the next defined horizon, and what evidence would change that posture?** KOMPAS never rewrites the weekly forecast.

## Continuous stream

Native Handlekompas is event-chained from the framework state machinery and has an hourly fallback watchdog. Complete KOMPAS is event-chained from Native Handlekompas. Every successful materialization is timestamped and retained under `04_MARKET_LEARNING/handlekompas/`.

The complete KOMPAS always exposes:

- **NOW** action posture;
- **NEXT 12H** direction, confidence, action, confirmation and invalidation;
- **NEXT 1–3D** direction, confidence, action, confirmation and invalidation;
- **NEXT 5–7D** direction, confidence, action, confirmation and invalidation;
- a BTC → ETH → large caps → midcaps → small caps → microcaps ladder;
- posture, ETA and ETA explanation for every capital tier;
- one plain-language conclusion per time horizon;
- altcoin / altseason status derived from the same capital-transmission ladder rather than a duplicate decision engine;
- data-health state and a bound point-in-time evidence manifest.

## Daily immutable backtest benchmark

The first successful Complete KOMPAS run at or after **12:00 Europe/Copenhagen** freezes one immutable benchmark for that local calendar day:

`04_MARKET_LEARNING/handlekompas/daily/YYYY/MM/YYYY-MM-DD.json`

`DAILY_LATEST.json` points to the newest daily freeze.

The freeze records the exact KOMPAS plus its point-in-time evidence manifest and due times for later evaluation at:

- +12 hours;
- +3 days, representing the 1–3 day endpoint;
- +7 days, representing the 5–7 day endpoint.

Suggested outcome dimensions are frozen with the packet: direction by horizon, action-posture utility, ETH/BTC relative strength, breadth/participation, cap-tier transmission, altseason state, and drawdown avoidance versus foregone upside.

The forecast packet is immutable. Outcome evidence must be appended separately later. Historical KOMPAS calls are never rewritten to make them look better.

## Point-in-time evidence

The evidence manifest binds the exact Auto Market State packet, daily live-anchor capture, breadth-universe membership, current Cycle Navigator package and Native Handlekompas source.

The daily capture currently contains a broad point-in-time feature surface including prices, derivatives, macro, microstructure, flows, liquidity, sentiment, rotation context and a **100-constituent breadth universe** where available. The framework deliberately does **not** claim that every KOMPAS is a synthetic score of exactly 100 datapoints; it freezes the actual contemporaneous feature manifest so future research can cross-measure the call against the evidence that genuinely existed at that moment.

## Cycle Navigator integration

The Cycle Navigator public build receives a privacy-safe sanitized KOMPAS object. Internal hashes, source paths and the proprietary decision recipe are not exposed publicly. The website can therefore display live KOMPAS action, horizons, direction and capital-ladder state while the weekly Cycle Navigator remains immutable.

## Safety / authority

KOMPAS is non-binding and cannot execute trades, mutate canonical market state, alter thresholds or model weights, switch source owners, promote proxy evidence into canonical evidence, or rewrite history.

Proxy breadth may make KOMPAS **more defensive**, but it never self-promotes a risk-on / top-up state. Positive deployment still requires registered canonical confirmation or an already-active framework entry signal.
