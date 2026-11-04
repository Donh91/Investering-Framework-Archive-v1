# Monday CN 7-day forecast product acceptance · v1
Owner mandate: 5 November 2026 · Existing CN owner #1516 · Existing S1 #1156

## Definition of a COMPLETE weekly product
The first-party Cycle Navigator Monday issuance needs **7 individually numbered,
prospectively frozen UTC daily expected closes** and **7 separately explained
UTC daily low/high forecast ranges** for **each of BTC and ETH**. Total:
14 expected closes + 14 daily low/high pairs, not three 2-day/2-day/3-day
range windows described as seven individual forecasts.

* Each expected-close point has `day=1..7`, `expected_close`, `low`, `high`.
* Each daily-range point has `day=1..7`, `low`, `high`, `why`, `invalidate_if`.
* Each asset is validated independently. No missing day, guessed quote
  conversion, synthetic target-week hindsight, or late first-issue credit.
* Forecast must be original and frozen on the target Monday UTC before its
  first UTC daily settlement. A Monday local morning publication is acceptable.
* Original source custody, instrument and quote parity are independently
  enforced upstream by the original #1879 price attestation and issuance gates.
* The published status of a point is **not** a statistical/economic edge claim.

## Separate epistemic and product truth
A legitimate source-driven abstention can be scientifically honest. However
`BTC=0/7`, `ETH=0/7`, or an unavailable seven-daily-range plan is **not** a
completed product. Use `CN_MONDAY_SEVEN_DAY_PRODUCT_ACCEPTANCE_v1.status=INCOMPLETE`;
never describe a green CI or successful weekly 3-window publication as
successful 7/7 delivery.

The product receipt is constructed in the ORIGINAL weekly publisher before the
immutable freeze and duplicated into its hash-bound source manifest and SITE
public freeze receipt. SITE readback independently recomputes it from original
frozen bytes and issue time rather than trusting a free-standing UI flag.
Keep `source/provenance/quote` controls distinct from the product status.

## Operations and first prospective verification
* #1879 source-attestation repair merged on 4 Nov 2026.
* Historical W45 (Monday 2 Nov): frozen BTC 0/7 and ETH 0/7. **No backfill.**
* First qualifying future test: **W46 Monday 9 November 2026**.
* Confirm native original Binance spot price-source quote independently
  (BTCUSDT/ETHUSDT) without silently labeling USDT as USD; check complete
  source 168h, custody, Monday timing, freeze hashes, schema, then 7/7 per
  asset and 7/7 daily range explanations.
* Read back `CYCLE_NAVIGATOR_SOURCE_MANIFEST.json`,
  `CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json`, public
  `/data/latest.json`, and actual Graph B blue/green geometry, keeping all
  observed hourly gaps disconnected.
* If incomplete, the existing owner #1516 and S1 handle a single bounded
  incident/repair path; no duplicate scheduler, automatic secret/paid
  retry, portfolio authority, retrospective source rewrite or misleading
  fallback to a pseudo-daily line.
* A preregistered deterministic benchmark may be explored separately, but it
  must be labeled as a benchmark, never impersonate an original AI-issued
  forecast, and must be scored prospectively against a frozen naive baseline.

## Code and guards
* `scripts/cycle_navigator/daily_price_journey.py`: pure 14-point
  product acceptance and existing primary seven-day forecast validators.
* `scripts/cycle_navigator/build_weekly_cycle_navigator.py`: single
  original model issuer, source attestation, quoted freeze, and receipt.
* `scripts/cycle_navigator/build_public_live_precision.py`: independent
  public verification from source freeze and hash-bound original receipt.
* `05_CYCLE_NAVIGATOR/site/frozen-week-chart.js`, Premium Graph B and
  Graph History: render only genuinely issued original daily forecasts.
