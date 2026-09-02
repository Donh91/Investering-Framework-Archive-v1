# Exact Settlement Price Owner v1

Status: `SHADOW_ACCOUNTABILITY_INFRASTRUCTURE`

## Purpose

Close the forecast-outcome timing defect without rewriting historical forecasts or outcomes. The owner creates forecast-bound adjudication evidence for the price metric families verified in the forecast-accountability audit.

## Settlement rule

For an arbitrary frozen `outcome_due_utc`, use the last fully completed 1-minute source candle whose close is at or before the target time.

The following clocks are independent and must remain explicit:

1. `settlement_target_utc` - the frozen forecast horizon.
2. `source_candle_open_utc` - start of the selected 1-minute source bar.
3. `source_candle_close_utc` - completion time of that source bar.
4. `source_retrieved_at_utc` - when the framework retrieved the already-completed source bar.

Retrieval/publication delay may never move the adjudicated market observation forward. The source candle close must be no later than target and no more than 60.001 seconds before target.

`captured_at_utc` on `FORECAST_SETTLEMENT_EVIDENCE_v1` is deliberately the adjudication target time so the existing canonical maturation engine can enforce exact frozen-target matching. It is therefore paired with the mandatory semantic marker `ADJUDICATION_TARGET_TIME_NOT_SOURCE_OBSERVATION`; the actual source clock remains separately recorded and hash-bound.

## Supported metric paths

- `spot.BTCUSDT.close`
- `spot.ETHUSDT.close`
- `spot.ETHBTC.close`
- `derivatives.BTC-USDT-SWAP.mark_price.mark_price`
- `derivatives.ETH-USDT-SWAP.mark_price.mark_price`

Document-root paths prefixed with `market_metrics.` normalize to the same five metrics. No fuzzy or neighbouring-metric substitution is allowed.

## Sources

- Binance public spot 1-minute klines for BTCUSDT, ETHUSDT and ETHBTC.
- OKX historical 1-minute mark-price candles for BTC-USDT-SWAP and ETH-USDT-SWAP.

Every evidence object binds the raw response by byte count and SHA-256. Missing, malformed, unconfirmed, wrong-candle, future-candle and unsupported-metric conditions fail closed.

## Persistence lanes

Settlement evidence is intentionally separate from `03_DAILY_CAPTURE_LOGS/captures`. It must not enter the legacy evidence pool, because legacy forecasts use first-capture-after-due semantics.

Per forecast the prospective chain is:

`FROZEN_FORECAST_v1`
→ raw source response
→ `FORECAST_SETTLEMENT_EVIDENCE_v1`
→ existing `outcome_maturation_engine.py`
→ `MATURED_OUTCOME_v3`
→ `FORECAST_SETTLEMENT_OUTCOME_BINDING_v1`

The binding preserves the source candle and retrieval clocks without changing the existing outcome schema.

## Authority and scientific boundary

This owner has no portfolio, market-state, model-weight, promotion or scientific-skill authority.

Correct settlement is necessary for later skill evaluation but is not evidence that the forecasting system has skill. Replication, disagreement, independence, baseline and power gates remain separate.

## Prospective activation boundary

This implementation does not backdate `settlement_contract_version` into historical forecasts and does not rewrite historical outcome files. Only forecasts frozen after a separately reviewed producer activation may opt into `FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1`.

## Kill / fail conditions

Fail closed if any of the following occurs:

- provider no longer exposes a verifiable completed 1-minute bar for the requested target;
- selected candle is later than the target or older than the last-closed-minute window;
- provider completion status cannot be verified where supplied;
- raw payload cannot be retained and hash verified;
- forecast hash, metric path or target timestamp does not match the evidence;
- source semantics change so the parser can no longer prove the same clock convention.

Do not replace a failed owner with first-capture-after-due settlement, interpolation, forward fill or a neighbouring price series.
