# FARSIDE BTC ETF FLOW API ALL - SOURCE ARCHIVE

Date added: 2026-07-06
Status: SOURCE_ARCHIVED_FROM_USER_PAYLOAD
Canonical role: DATA_SOURCE_INPUT
Source family: Farside ETF Flow API
Asset: BTC spot ETF flow

## Purpose

Archive the Farside BTC ETF flow API payload supplied by the user for framework use.

This source is relevant for:

- DATA PING ETF flow fields
- Master Monday ETF flow context
- Weekly RAW learning
- Cycle Navigator flow commentary
- recovery-attempt quality checks
- ETF pressure / repair diagnostics

## Payload received

The user supplied a JSON API response with:

```text
status: success
data.data: daily BTC ETF flow rows
data.summary.Total: cumulative fund totals
```

Dataset start:

```text
11 Jan 2024
```

Dataset latest row supplied:

```text
02 Jul 2026
```

## Columns in daily rows

```text
Date
IBIT
FBTC
BITB
ARKB
BTCO
EZBC
BRRR
HODL
BTCW
MSBT
GBTC
BTC
Total
```

## Summary totals from supplied payload

```text
IBIT:   59994.0
FBTC:   10253.0
BITB:    1972.0
ARKB:    1266.0
BTCO:     166.0
EZBC:     328.0
BRRR:     329.0
HODL:    1127.0
BTCW:      96.0
MSBT:     395.0
GBTC:  -27171.0
BTC:     2376.0
Total:  51132.0
```

## Latest rows explicitly visible in supplied payload

```text
29 Jun 2026: Total -231.0
30 Jun 2026: Total -222.6
01 Jul 2026: Total -296.0
02 Jul 2026: Total  223.5
```

## Operational interpretation rules

1. Treat this as an ETF flow data source, not as a trading signal by itself.
2. ETF flow can support or weaken recovery-attempt quality, but cannot alone confirm recovery, rotation, rebuy or deployment.
3. Use trailing flow windows rather than one-day prints when possible.
4. Track both aggregate Total and fund-level dispersion.
5. IBIT, FBTC and GBTC deserve special attention because they can dominate aggregate flow.
6. Zero rows may represent market holidays or unavailable reporting and must not be interpreted as neutral demand without date/calendar context.
7. If Farside conflicts with another ETF source, create a source-conflict row rather than silently choosing one.
8. Do not score flow-led claims unless the exact date window is preserved.

## Suggested DATA PING fields

```text
ETF_FLOW_SOURCE: FARSIDE
ETF_FLOW_SOURCE_STATUS: API_PAYLOAD_SUPPLIED_BY_USER
ETF_FLOW_UNIT: USD_MILLIONS_ASSUMED_VALIDATE_IF_NEEDED
BTC_ETF_TOTAL_1D:
BTC_ETF_TOTAL_3D:
BTC_ETF_TOTAL_5D:
BTC_ETF_TOTAL_7D:
BTC_ETF_TOTAL_10D:
BTC_ETF_TOTAL_20D:
BTC_ETF_STREAK:
BTC_ETF_IBIT_1D:
BTC_ETF_FBTP_OR_FBTC_1D:
BTC_ETF_GBTC_1D:
BTC_ETF_DISPERSION:
BTC_ETF_FLOW_REGIME:
BTC_ETF_REPAIR_QUALITY:
```

## Integration status

Raw payload was supplied directly in the chat thread and is represented here by source schema, date coverage, summary totals and latest rows.

For exact row-by-row machine replay, store a dedicated raw JSON or CSV file in this folder if needed.

Recommended raw filenames:

```text
2026-07-06__farside-btc-etf-flow-api-all__raw.json
2026-07-06__farside-btc-etf-flow-api-all__raw.csv
```

## Governance boundary

This source is subordinate to canonical framework governance:

- CANONICAL_INDEX
- Canonical Weekly Backbone Engine v3.0
- highest active DATA PING version
- verified actuals governance
- source conflict rules

## Update log

- 2026-07-06: Created from user-supplied Farside BTC ETF flow API payload.