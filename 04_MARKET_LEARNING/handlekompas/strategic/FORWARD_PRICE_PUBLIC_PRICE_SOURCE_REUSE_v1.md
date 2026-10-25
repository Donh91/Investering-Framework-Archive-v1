# Forward Price · existing-source reuse: BTC/USDT native first; BTC/USD optional

**Date:** 2026-10-25 · **owner:** existing Forward Path [#1516](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1516), original price-issue [#1593](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1593), Task2 [#1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596), S1 [#1156](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156).  
**Classification:** RESEARCH_ONLY / NON-BINDING / NO NEW SOURCE AUTHORITY. This note does not amend any canonical published market rule, existing FMP/Kraken scoring agreement, source admission, or data-protection/recovery requirement.

## Bottom line (owner explicitly requested Binance/USDT)

**YES: Binance Spot BTCUSDT is an existing, usable native-quote BTC/USDT price-observation source.** Keep quote `USDT` end-to-end. Do not silently write `BTC/USD`, `USD`, $`, or 1.00 USD/USDT in research, freezing, scoring, user display or outcome comparison. USDT stablecoin depegs are a real basis risk. A future documented USD/USDT FX/source transform would be a **different** reviewed source/target contract with the conversion point-in-time frozen; this PR does not implement one.

1. `scripts/daily_capture/build_hourly_sequence.py`: existing Binance public market-data-only `BTCUSDT`, `ETHUSDT`, `ETHBTC` 1h OHLC input. Existing public `03_DAILY_CAPTURE_LOGS/hourly/LATEST.json` reports `HOURLY_SEQUENCE_LATEST_POINTER_v2_2`, `COMPLETE` with **26/26 spot complete hours**, latest 2026-10-25T17:08:06Z. This proves a recent *sequence snapshot*, **not** 24/7 continuous scheduler coverage or a true original-priced forecast.
2. `scripts/daily_capture/build_weekly_market_close_package.py`: existing Binance `BTCUSDT`, `ETHUSDT`, `ETHBTC` 1h settled market-close owner, freeze-complete `03_DAILY_CAPTURE_LOGS/weekly_close/LATEST_WEEKLY_MARKET_CLOSE.json` for W42, UTC 2026-10-19T00:00:00Z. It is a **weekly anchor** from already completed periods, not the next seven daily expected-close numbers.
3. `scripts/learning/forecast_settlement_price_owner.py`: existing Binance `BTCUSDT` 1m spot **outcome/settlement** owner, separate from the forecast issuer. Same-symbol BTCUSDT original issue and future settled observations can be the basis of a native **USDT-scored** research protocol *after independent source/issuer admission*. Do not score a BTC/USD original issue against BTCUSDT actuals or reverse.
4. `04_MARKET_LEARNING/handlekompas/strategic/source_custody/2026/10/24/20261024T133724013031Z.json`: existing distinct Kraken `XXBTZUSD` BTC/USD historical capture, **720 daily + 720 hourly CLOSED rows**, but status `CAPTURED_NOT_ADMITTED`; historical provider original first-known UNKNOWN and collector SHA absent. No flip.
5. Optional Coinbase Advanced public `BTC-USD` `ONE_HOUR/ONE_DAY` endpoint: documented **max 350** buckets/request, no API key for public candles. Possible prospective USD-native challenger subject to real read-only provider probing, snapshotting, independent private source receipt and review. Do not treat an offline parser as a deployed collector or a live verified feed.

## Technical scope delivered by research-only PR

`scripts/learning/forward_price_public_api_candidate.py` contains only:
- `request_window` and `inspect_candle_response`: Coinbase public BTC/USD exact UTC/strict 350-bucket, closed/gap-free typed OHLC parsing of provided **bytes** (no HTTP fetch), returns metadata hashes only, never values.
- `binance_request_window` and `inspect_binance_spot_response`: Binance public BTCUSDT **1h / 1d** request builder and strict 12-field typed spot-candle validation (no HTTP fetch), max 1,000 candles, closed/gap-free OHLC/volume/UTC consistency, returns hashes only. Provider source type asserted by request identity and endpoint contract; raw response by itself **cannot prove** the exact network origin, which requires external receiver custody.
- `existing_source_roles`: fail-closed comparison of existing public hourly/weekly pointers and captured-only Kraken binding. It has **no** outcome/price, issuance, canonical source, market or portfolio authority.

Tests in `tests/learning/test_forward_price_public_api_candidate.py` and `test_forward_price_binance_native_usdt_candidate.py` are imported by the **existing** Strategic Compass test gate. No new workflow, scheduler, collector, secret, API costs or redeployment.

## Exact future acceptance sequence — not completed by this research patch

| Gate | Requirement | Current |
| --- | --- | --- |
| A · Existing BTCUSDT observation | Existing hourly source identity, closed candle, SHA + actual clock + rate/geo reliability; weekly separate | Existing evidence; continuous natural schedule coverage not established |
| B · Source-issuance contract | Independent recovery/destructive-authority proof **PASS**, versioned collector first observed in PRIVATE store; no historical backdating | **BLOCKED**: current integration cannot verify independent Vault; existing Binance source does NOT grant future-price-issue authority |
| C · Genuine first ORIGINAL issue | Decide source `BTCUSDT` + quote `USDT`, horizon/target (terminal CLOSE versus range MIN/MAX), priced interval + original issue and first public delivery receipts, frozen before future result | NOT ISSUED |
| D · Natural matured score | Same `BTCUSDT` price clock source, settled complete bars only, immutable normal/missingness outcome, abstention, same-clock B0/B1/ATR comparisons and width penalty | NOT DONE |
| E · Consumer & science | Short chat `BTC/USDT 24h: X–Y USDT` and 7d, 2–3w, 4–8w only with correctly frozen genuine forecast; Graph B only 7 original daily expected CLOSE nodes | UNAVAILABLE until gate C; **4–8w SHADOW** by default |

**Preference:** use existing Binance spot source and outcome plumbing first for **native USDT-priced, research-only provisional forecast candidate**, provided the governed source/issuance release can be verified. Do **not** demand USD as a prerequisite for the user's useful BTC/USDT forecast. Keep Coinbase USD as optional distinct backup/cross-venue challenger; Kraken historical USD as unadmitted capture; do not create two competing canonical engines. Cross-quote performance comparison is invalid without correct pre-registered FX vintage/normalization. Any live forecast authority change requires the existing separate high-impact governance and recovery safety; do not bypass Vault 404 by using this read-only research PR.

**External references:** [Binance public market-data-only docs](https://developers.binance.com/en/docs/products/spot/rest-api), [Coinbase public product candles spec](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/public/get-public-product-candles).


## Quote-native offline follow-up: same math, separate contract (2026-10-25)

The separate research-only follow-up to existing #1516 introduces `build_native_usdt_shadow()` in the **same existing** `scripts/learning/forward_price_shadow.py` as the USD baseline. It shares exactly the quantile/extrema calculation machinery, while preserving `build_shadow()` as an explicitly **USD-only** entrypoint and maintaining its existing USD contract, 1/7/14/21d horizons, output keys and candidate-hash semantics.

- A USDT-native input must carry `contract=FORWARD_PRICE_DAILY_BAR_INPUT_USDT_v0_1`, `asset=BTC`, `quote=USDT`, `venue=BINANCE_SPOT_BTCUSDT` and **genuine** `low_usdt/high_usdt/close_usdt` fields. USD-labelled fields in the USDT contract or USDT-labelled values in the USD contract are rejected. Zero FX conversion or hidden 1:1 USDT/USD assertion.
- The output is `FORWARD_PRICE_SHADOW_PRICE_ONLY_USDT_CHALLENGER_v0_1`, source `SHADOW_NOT_ISSUED`; quote-specific `anchor_usdt` and `low_usdt/high_usdt` only, distinct SHA and model-method ID from USD. **This is not a genuine issued or published forecast.**
- Research horizons are 1/7/14/21/30/**56** days. The original USD horizon set remains unchanged. The existing strict **12 non-overlapping horizon blocks** upper-bound rule carries through. In a 365-day synthetic history, 30d offers 12 nominal independent blocks (still not independent event families or calibration), while **56d has only six and must `ABSTAIN`**. Never widen or fabricate a 4–8 week target to satisfy UI demand.
- `provider_first_known_proven` is a caller assertion, not proof of actual vendor first-known. The model explicitly reports `source_first_known_independently_rechecked=false`, `no_publication=true`, `probabilities_claimed=false`, `no_portfolio_action=true`. No private provider values should be placed in control-plane artifacts.
- Both quote-specific synthetic methods are tested together in **the existing** `tests/learning/test_strategic_compass.py` CI suite. Do not create a second issuer, downstream outcome scorer, budget, API workflow, scheduler or auto-promotion engine.

**High-impact source gate remains unchanged:** independent recovery/destructive-authority proof, versioned future-only receiver custody, original issue/delivery clock and post-maturity same-quote outcome before any published numerical USDT forecast or website future path. This research refactor cannot admit historical Binance provider vintages or itself set source flags.
