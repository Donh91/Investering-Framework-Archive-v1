# CN Time Machine · Graph History v1

**Status:** Source-only implementation candidate. Begins **2026-W45 / 2026-11-02**. W44 and earlier are not backfilled, and W45 future predictions must not be created until the original Monday Cycle Navigator issues them.

## Purpose and authority

The graph archive is a **durable presentation/readback layer**, not a forecast issuer, scoring authority, market classifier, API caller, or trading engine. Its immutable forecast owner remains:

`05_CYCLE_NAVIGATOR/weekly/<year>/W<week>/CYCLE_NAVIGATOR_FORECAST_FREEZE.json`

The source bytes are verified against their original `CYCLE_NAVIGATOR_DELIVERY_POINTER.json` SHA-256 and, where available, their public freeze receipt. `CN_FROZEN_DAILY_PRICE_PATH_v1` must contain exactly seven valid Monday-Sunday predicted end-of-day closes to draw a blue dashed expected-close segment. `UNAVAILABLE` generates **no** synthetic expected close, midpoint, backfill, or trendline. An archived summary can never change the original source.

## Paths

```text
05_CYCLE_NAVIGATOR/graph_history/v1/
  README.md                         # this contract
  index.json                        # continuous W45 onward manifest
  weeks/YYYY/WNN/
    forecast-reference.json         # never overwritten once first archived
    actual-series.json              # append-only verified hourly closes after week ends

05_CYCLE_NAVIGATOR/site/dist/
  data/graph-history/timeline.json  # regenerable public view
  graph-history/index.html          # independent product preview
```

The index contains explicit `MISSING_FREEZE` entries, previous-week identity, source SHA, and a deterministic digest chain, not an editable concatenation of forecast trajectories. Missing weeks do not make the whole graph disappear. **Hash chaining is an integrity consistency check, not a cryptographic signature or independent trust anchor.**

Green actuals are the existing publicly committed Hourly Sequence `spot_status=PASS/OK` UTC hourly closes, deduplicated and ordered. Observations are not interpolated across gaps. New, previously absent hours can be appended after delayed collector recovery. A change/deletion of already archived hour values stops with `ACTUAL_MUTATION_OR_LOST_HOUR`, requiring source-governed correction rather than silent history rewriting. Time is UTC throughout; no DST-dependent day length.

Quote distinction is preserved: weekly CN forecasts use USD levels, captured spot closes use USDT quotes. The visual price-axis comparison is **nominal/indicative**, and it is NOT a new calibrated accuracy score. Existing official Price Range scoring is unchanged.

## Two modes in EXISTING workflows

- `python scripts/cycle_navigator/build_graph_history.py --repo-root . --mode archive`
  - Run after the existing weekly CN builder and before its existing Git commit on `main`.
  - Create the new week's immutable reference. Finalize previous closed weeks' real observed hours and retry any historic incomplete week for late bona fide data.
  - No independent schedule, API, direct-main bot, or alternative writer.
  - If history fails, CN itself is allowed to publish: the history step must report failure, never corrupt a source-owned freeze.
- `python scripts/cycle_navigator/build_graph_history.py --repo-root . --mode public`
  - Run in existing Pages and SITE gate after `build_public_live_precision.py`. Publish the historical timeline and append only this week's source-validated public hourly readback.
  - Copy the independent preview route into `dist/graph-history/` without changing canonical homepage layout.
  - This public file is derived. It can always be rebuilt from repository sources.

The public `/graph-history/` preview is a standalone first-party view, **not** a new SITE homepage/navigation decision. The SITE owner (#1578) decides placement/visual acceptance and can replace its renderer without modifying historical source files. BTC is the default graph; ETH remains preserved in archival data for optional future support.

## Monday closure and acceptance

For each natural Monday:
1. Source owner publishes and freezes current target week before outcome, and retains the unchanged hash, original issue clock and forecast source identity.
2. Archive job appends exactly one `forecast-reference.json` (or explicit missing-week entry). PUBLISHED daily forecasts require 7 real points, while UNAVAILABLE remains empty.
3. Prior week's hourly data are attached as `actual-series.json` with `observed_hours/168`; incomplete series remain PARTIAL. Reconciliation must never manufacture a close.
4. Pages combines historic actuals and the current public live hour series. Each blue seven-point segment is drawn **only** inside its issuing week; no blue line is connected across independent CN issues.
5. Verify source blob hashes, anchored eligible UTC cutoff, new Pages artifact/CDN parity, genuine browser 390/430px run and no history regression. Missing provenance or CI means `RELEASE_PENDING`, not `COMPLETE`.

### Negative test matrix

- W44 is not generated retrospectively; W45 is the first eligible Monday.
- Missing original W45 source keeps a named hole instead of fabricating forecast prices.
- A source mismatch, changed original source bytes, duplicate timestamp with conflicting prices, or changing a committed historic close is rejected.
- Invalid/wrong-week/unclosed live observation is not backfilled.
- Late source issuances are never relabelled as a prospectively valid seven-point path.
- Rebuilds are deterministic and idempotent; ISO year rollover is continuity-safe.
- Site uses the same public Hourly price owner and never creates BUY/SELL authority.

### Existing owners

CN / Master Monday: issue [#1593](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1593). SITE display owner: [#1578](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1578). Existing Supervisor: [#1156](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156). Do not create a duplicate forecast issuer, scorer, task, cron or AI budget.

**Production caveat:** code merged on a Sunday is not proof of any future Monday's real seven-point expected-close issuance. A first natural W45 run and real public CDN readback are still required.
