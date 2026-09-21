# Cycle Navigator public scorecards

This folder is the canonical human- and machine-readable archive for **completed public Cycle Navigator scores**.

Each public CN gets one scorecard under:

```text
public_scorecards/YYYY/Www/CNxx_PUBLIC_SCORECARD.json
```

## Identity rule

A public scorecard is identified by:

```text
public series + public CN number + forecast week + immutable forecast source
```

Never use migration-era machine `issue_number` alone. The September 2026 machine counter is one ahead of the published public series.

## What each scorecard must distinguish

1. **Frozen forecast** - what was fixed before the week unfolded.
2. **Outcome evidence** - the matching completed-week evidence.
3. **Frozen-claim precision** - reproducible scoring of the frozen analytical claim set when available.
4. **Market / structure precision** - family-level regime/ETHBTC/breadth/rotation/altseason score.
5. **Price range precision** - BTC/ETH and intraday range accuracy.
6. **Overall** - only when the scorecard's scoring era has an explicit supported aggregation rule.
7. **Calibration** - misses/strengths that can inform later learning without rewriting the frozen forecast.

## Current recent chain

| Public CN | Forecast week | Score source |
|---|---|---|
| CN #23 | 2026-W36 | `2026/W36/CN23_PUBLIC_SCORECARD.json` |
| CN #24 | 2026-W37 | `2026/W37/CN24_PUBLIC_SCORECARD.json` |
| CN #25 | 2026-W38 | `2026/W38/CN25_PUBLIC_SCORECARD.json` |

The current pointer is:

`../LATEST_PUBLIC_SCORECARD.json`

The public-series identity pointer is:

`../public_series/CN_PUBLIC_SERIES_INDEX.json`

## Automation rule

After the completed week is scored, `scripts/cycle_navigator/materialize_public_scorecard.py` must materialize the public scorecard from the public-series binding, frozen range ledger, completed 168-hour actuals and the canonical completed-week CN score evidence.

The website and Master Monday consumers should read these public scorecards rather than infer a score by matching machine issue numbers.
