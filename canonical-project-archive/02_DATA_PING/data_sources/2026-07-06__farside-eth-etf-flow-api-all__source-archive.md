# FARSIDE ETH ETF FLOW API ALL - SOURCE ARCHIVE

Date added: 2026-07-06
Status: SOURCE_ARCHIVED_FROM_USER_PAYLOAD
Canonical role: DATA_SOURCE_INPUT
Source family: Farside ETF Flow API
Asset: ETH spot ETF flow

## Purpose

Archive the Farside ETH ETF flow API payload supplied by the user for framework use.

This source is relevant for:

- DATA PING ETF flow fields
- ETH ETF flow diagnostics
- ETH/BTC rotation-quality checks
- Master Monday ETF flow context
- Weekly RAW learning
- Cycle Navigator ETH-flow commentary
- recovery-attempt quality checks
- ETF pressure / repair diagnostics

## Payload received

The user supplied a JSON API response with:

```text
status: success
data.data: daily ETH ETF flow rows
data.summary.Fee: fund fee map
data.summary.Seed: seed / initial holdings map
data.summary.Total: cumulative fund totals
```

Dataset start:

```text
23 Jul 2024
```

Dataset latest row supplied:

```text
02 Jul 2026
```

## Columns in daily rows

```text
Date
ETHA
ETHB
FETH
ETHW
TETH
ETHV
QETH
EZET
ETHE
ETH
Total
```

## Summary fees from supplied payload

```text
ETHA: 0.0025
ETHB: 0.0025
FETH: 0.0025
ETHW: 0.0020
TETH: 0.0021
ETHV: 0.0020
QETH: 0.0025
EZET: 0.0019
ETHE: 0.0250
ETH:  0.0015
Total: 0.0
```

## Summary seed values from supplied payload

```text
ETHA:    10.6
ETHB:   104.7
FETH:     4.4
ETHW:     2.5
TETH:     2.3
ETHV:    10.2
QETH:     1.1
EZET:     2.7
ETHE:  9199.3
ETH:   1022.5
Total: 10360.0
```

## Summary totals from supplied payload

```text
ETHA:  11124.2
ETHB:    518.9
FETH:   2126.0
ETHW:    385.3
TETH:     27.8
ETHV:    163.4
QETH:     24.5
EZET:     66.1
ETHE:  -5331.9
ETH:    1813.0
Total: 10917.3
```

## Latest rows explicitly visible in supplied payload

```text
29 Jun 2026: Total -29.9
30 Jun 2026: Total -27.6
01 Jul 2026: Total  14.8
02 Jul 2026: Total  29.0
```

## Operational interpretation rules

1. Treat this as an ETF flow data source, not as a trading signal by itself.
2. ETH ETF flow can support or weaken ETH recovery-quality and ETH/BTC rotation diagnostics, but cannot alone confirm rotation, rebuy or deployment.
3. Use trailing flow windows rather than one-day prints when possible.
4. Track both aggregate Total and fund-level dispersion.
5. ETHA, FETH, ETHE and ETH deserve special attention because they can dominate aggregate ETH ETF flow.
6. ETHE outflow can distort aggregate flow and should be separated from new-product inflow where relevant.
7. Zero rows may represent market holidays or unavailable reporting and must not be interpreted as neutral demand without date/calendar context.
8. If Farside conflicts with another ETH ETF source, create a source-conflict row rather than silently choosing one.
9. Do not score flow-led claims unless the exact date window is preserved.

## Suggested DATA PING fields

```text
ETH_ETF_FLOW_SOURCE: FARSIDE
ETH_ETF_FLOW_SOURCE_STATUS: API_PAYLOAD_SUPPLIED_BY_USER
ETH_ETF_FLOW_UNIT: USD_MILLIONS_ASSUMED_VALIDATE_IF_NEEDED
ETH_ETF_TOTAL_1D:
ETH_ETF_TOTAL_3D:
ETH_ETF_TOTAL_5D:
ETH_ETF_TOTAL_7D:
ETH_ETF_TOTAL_10D:
ETH_ETF_TOTAL_20D:
ETH_ETF_STREAK:
ETH_ETF_ETHA_1D:
ETH_ETF_FETH_1D:
ETH_ETF_ETHE_1D:
ETH_ETF_NEW_PRODUCT_TOTAL_EX_ETHE:
ETH_ETF_DISPERSION:
ETH_ETF_FLOW_REGIME:
ETH_ETF_REPAIR_QUALITY:
ETH_ETF_VS_BTC_ETF_FLOW_SPREAD:
```

## Framework use

Use this source together with the BTC Farside ETF flow archive when evaluating:

- BTC-led versus ETH-led repair
- whether ETH is absorbing capital before BTC
- ETF-flow confirmation quality
- ETH/BTC rotation durability
- false rotation risk

## Integration status

Raw payload was supplied directly in the chat thread and is represented here by source schema, date coverage, summary fee/seed/total values and latest rows.

For exact row-by-row machine replay, store a dedicated raw JSON or CSV file in this folder if needed.

Recommended raw filenames:

```text
2026-07-06__farside-eth-etf-flow-api-all__raw.json
2026-07-06__farside-eth-etf-flow-api-all__raw.csv
```

## Governance boundary

This source is subordinate to canonical framework governance:

- CANONICAL_INDEX
- Canonical Weekly Backbone Engine v3.0
- highest active DATA PING version
- verified actuals governance
- source conflict rules

## Update log

- 2026-07-06: Created from user-supplied Farside ETH ETF flow API payload.