# Source QA incident — DATA PING run 72b3eaf3

## Incident A: Binance geo restriction

All 23 `BINANCE_CONTEXT` actions and all 11 `BINANCE_FINAL` actions failed with the same error evidence:

```yaml
error_category: GEO_RESTRICTION
reason: Binance service unavailable from connector location
affected_core_actions: 34
```

Consequences:

- no direct Binance BTC, ETH or ETH/BTC feed
- no Binance spot windows
- no Binance funding or OI history
- no Binance taker ratios
- no Binance basis or cross-venue mark features
- no Binance realized-volatility features

The packet remains partially usable because CoinGecko and OKX current feeds passed.

## Incident B: null max-final-source timestamp

`meta.max_final_source_timestamp_utc` is null even though current source timestamps exist, including:

- CoinGecko: `2026-07-27T14:23:47.455Z`
- OKX: `2026-07-27T14:28:43.242Z`

This is classified as a metadata/serialization defect. It must not be interpreted as absence of current source data.

Recommended repair:

1. Define whether `max_final_source_timestamp_utc` means maximum timestamp across all accepted final sources or only the `BINANCE_FINAL` group.
2. If it is global, populate it from the maximum accepted source timestamp regardless of venue failure.
3. If it is Binance-specific, rename the field to prevent misleading null semantics.
4. Add a validation rule that rejects null when any accepted live source timestamp exists under global semantics.

## Materiality

```yaml
market_data_loss: HIGH_FOR_BINANCE_FEATURES
packet_total_loss: NO
canonical_state_harm: NONE
portfolio_harm: NONE
```
