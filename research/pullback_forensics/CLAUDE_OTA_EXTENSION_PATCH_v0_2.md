# OTA EXTENSION PATCH v0.2 — PULLBACK_FORENSICS

```text
STATUS:        PROPOSED PATCH to PULLBACK_FORENSICS_EXTENSION_v0.1
REPLACES:      nothing. v0.1's authority rules, trigger conditions, anti-hindsight
               rule, matched-control rule and source-receipt rule stand unchanged.
CHANGES:       three lane-level corrections forced by live source verification
AUTHORITY:     can_affect_canonical_state: NO | can_affect_portfolio_action: NO
```

The existing v0.1 extension is already active in the OTA protocol. It was written before any source was probed. Three of its four lanes now need correction — not because the design was wrong, but because the sources turned out differently than the design assumed.

## PATCH 1 — Lane 1: name the venue, mark aggregates as lower bounds

v0.1 says: *"Where fresh and verifiable, collect BTC/ETH long and short liquidations."*

It does not say from where. Verified today: Binance returns HTTP 451 and Bybit returns HTTP 403 from this egress. Only OKX works.

```text
REPLACE the Lane 1 paragraph with:

  Source is OKX public/liquidation-orders, instType=SWAP, state=filled.
  Binance and Bybit are geo-blocked from this environment and must not be
  attempted or reported as UNAVAILABLE-for-market-reasons; they are
  SOURCE_BLOCKED_GEO, which is a source fact, not a market fact.

  All 24h notional aggregates are LOWER BOUNDS. The endpoint returned 966
  events for a request carrying limit=100 and page completeness is unverified.
  Every reported aggregate must carry page_truncated and the value must never
  be described as a total.

  Do NOT report liquidation clusters, heatmaps, cluster density or cluster
  clearance. Every available source for these is a MODELLED_LIQUIDATION_MAP,
  not an observation. v0.1 already requires distinguishing the two; this
  patch resolves the distinction by excluding the modelled half entirely.
```

## PATCH 2 — Lane 2: the skew you can actually observe is not 25-delta skew

v0.1 says: *"collect BTC/ETH 7d IV, 30d IV, 25d downside skew/risk reversal, 7d–30d term structure."*

25-delta skew requires per-instrument greeks: 792 API calls per asset. During a 792-call loop the surface moves, so the result is not a snapshot of anything.

```text
REPLACE the Lane 2 paragraph with:

  Observe DVOL (Deribit volatility index) as the IV level. It is exchange-native,
  one call, and backfillable to 2021-03-21 — so a missed observation costs nothing
  and must never be reported as a data gap.

  For skew, observe MONEYNESS_BUCKET_SKEW: mark_iv at strike/spot = 0.90 (put)
  minus mark_iv at strike/spot = 1.10 (call), from one get_book_summary_by_currency
  call, reported per expiry.

  This is NOT 25-delta skew. It must never be labelled, stored or compared as
  such. Mixing the two is exactly the vendor-definition mixing v0.1 forbids.

  7d/30d term structure: only report if both tenors come from the same
  construction. Do not interpolate an ATM curve and present it alongside DVOL.
```

## PATCH 3 — Lane 3: state the cadence limit inside the lane

v0.1 says: *"Where reproducible, collect BTC/ETH spread, bid/ask depth ... post-sweep refill if observable."*

The word "observable" is doing work it cannot do. The OTA runs at discrete moments; a flush lasts minutes. Post-sweep refill is never observable this way, and a snapshot taken hours after a flush looks like a valid measurement while describing a different market.

```text
REPLACE the Lane 3 paragraph with:

  Order-book depth may be observed as a single instantaneous snapshot and
  reported ONLY as CONTEXT_SNAPSHOT with observation_class INSTANTANEOUS.

  Do NOT report: post-sweep refill, depth evaporation, wall persistence,
  cancellation proxies, or any change-versus-prior-observation where the
  prior observation is more than 60 minutes old. At OTA cadence these are
  not measurements of the phenomenon they name.

  Never infer historical depth from the current book. v0.1 already says this;
  it remains the most important sentence in the lane.
```

## PATCH 4 — Lane 4: add the anti-hindsight anchor

v0.1's Lane 4 is the strongest of the four and needs only one addition.

```text
ADD to the Lane 4 required fields:

  classification_recorded_at_utc   — the timestamp at which the classification
                                     was written down. If this does not precede
                                     the outcome window's end, the row is not
                                     evidence and must be marked
                                     RETROSPECTIVE_TAG_NOT_EVIDENCE.

  outcome_window_end_utc           — fixed at tag time, never adjusted later.

ADD to the Lane 4 discipline:

  scheduled: true|false must be resolved against a macro calendar frozen BEFORE
  the observation window. It is a lookup, not a judgement. Answering "was this
  scheduled?" after the fact is a hindsight operation.
```

## PATCH 5 — one new field in the output block

```text
ADD to the pullback_forensics object:

  "perishability_note": {
    "lane1": "HARD_24H_ROLLING_WINDOW — not captured means permanently lost",
    "lane2_dvol": "NONE — backfillable to 2021-03-21, a miss costs nothing",
    "lane2_skew": "CURRENT_CHAIN_ONLY — not captured means permanently lost",
    "lane3": "EXTREME — but capture at OTA cadence is not evidential",
    "lane4": "TAGGER_CONTAMINATION — retrospective tagging is not recoverable"
  }
```

This exists so that a NOT_TRIGGERED run makes clear what was and was not lost by not running. A missed DVOL observation is not a gap. A missed liquidation window is.

## What does not change

v0.1's authority rules, `DATA_MISSING = UNKNOWN`, the trigger conditions, the prohibition on inventing a new fixed threshold to force a trigger, the anti-hindsight freeze rule, the matched-control rule, the source-receipt requirements, and `NO_INCREMENTAL_INFORMATION_OBSERVED` as a permitted and expected output — all stand exactly as written.

The instruction *"do not force a finding"* is the single most valuable line in v0.1 and is reaffirmed rather than modified.
