# Research Lab Evidence Pack — GATE-BTC-PARTIAL FT-1 + GRADUERET DEPLOYMENT v1.1

**Archive date:** 2026-07-07  
**Archive status:** SHADOW_TEST_ONLY / NO_PROMOTION  
**Placement:** `04_MARKET_LEARNING/forward_tests/`  
**Source:** Custom GPT parallel Research Lab output + uploaded evidence pack  
**Purpose:** Preserve the evidence package as a forward-test support document, not as canonical promotion.  
**Operational boundary:** DATA_ONLY / SHADOW_ONLY. No portfolio action, no deployment unlock, no official row.

---

## Archive Control Note

This file is archived as a shadow evidence pack because it identifies:

1. which parts of `GATE-BTC-PARTIAL FT-1` and `GRADUERET DEPLOYMENT v1.1` are testable,
2. which data layers remain missing,
3. where decision divergence can occur,
4. why ETF print and ETF trend must be separated,
5. why promotion is not justified without actual timestamped ledger rows.

This file does **not** promote either test.

Required next operational layer:

```text
Forward-test ledger rows must be created separately.
First row must be DATA_MISSING / NO_ACTION unless all timestamped inputs exist.
Rows beat theory.
```

---

## 0. Scope

This document converts the Research Lab verdict into concrete evidence claims.

Important boundary:

- This is **not** proof that either framework change improves returns.
- This is proof of:
  1. which parts are testable,
  2. which parts are not testable with current data,
  3. where decision divergence can occur,
  4. why ETF print and ETF trend must be separated,
  5. why promotion is not justified without actual ledger rows.

Rows beat theory.

---

## 1. Evidence Claim Matrix

| Claim | Evidence status | Result |
|---|---|---|
| GATE-BTC-PARTIAL can create real decision divergence vs WAIT | PROVEN_BY_MECHANICS | If default WAIT = 0% BTC and FT-1 = 10% BTC, returns diverge whenever BTC return != 0. |
| GATE-BTC-PARTIAL has enough price/range data to run as shadow test | PROVEN_BY_SOURCE_INVENTORY | BTC/ETH/ETHBTC daily OHLCV, rungs, ATR, range and streak fields are defined by extractor. |
| GATE-BTC-PARTIAL is promotion-ready | NOT_PROVEN | Actual forward-test ledger rows do not exist yet. |
| Gradueret Deployment can create decision divergence vs binary WAIT/DEPLOY | PROVEN_BY_MECHANICS | Tier 1/2/3 allocations differ from both 0% alt and full deployment. |
| Gradueret Deployment is fully scoreable now | DISPROVEN_BY_MISSING_DATA | Daily breadth, BTC.D, stablecoin deployment, fake-rotation density and fixed alt-proxy ledgers are missing. |
| ETF print must be separated from ETF trend | PROVEN_BY_DATA | BTC 02 Jul 2026 print is positive while 3D/5D/7D trend remains negative. |
| Single positive ETF print confirms ecosystem recovery | DISPROVEN_BY_RULE_AND_DATA | Positive print can coexist with negative multi-day trend and weak/missing ecosystem data. |
| Rows are sufficient for promotion | NOT_PROVEN | No forward-test rows yet. |

---

## 2. Proof A — GATE-BTC-PARTIAL Creates Decision Divergence If Entered

Definition:

```text
Default WAIT allocation:
  BTC = 0%
  Stable = 100%
  Alt = 0%

GATE-BTC-PARTIAL allocation after ENTERED:
  BTC = 10%
  Stable = 90%
  Alt = 0%
```

Let BTC return over the test window be `R_btc`.

```text
Default WAIT return = 0
FT-1 return = 0.10 * R_btc
Decision divergence = 0.10 * R_btc
```

Therefore:

```text
If R_btc != 0, FT-1 creates non-zero return divergence vs WAIT.
```

This proves FT-1 is not merely a narrative layer **if and only if** it enters on a row where default framework remains WAIT.

It does **not** prove the divergence is beneficial. That requires actual forward rows, return, and drawdown.

---

## 3. Proof B — BTC ETF Print/Trend Conflict Exists

Source rows used:

| Date | BTC ETF Total |
|---|---:|
| 24 Jun 2026 | -469.0 |
| 25 Jun 2026 | -691.7 |
| 26 Jun 2026 | -444.5 |
| 29 Jun 2026 | -231.0 |
| 30 Jun 2026 | -222.6 |
| 01 Jul 2026 | -296.0 |
| 02 Jul 2026 | 223.5 |
| 06 Jul 2026 | 0.0 placeholder / pending |

Calculations:

```text
BTC ETF latest completed print = +223.5M on 02 Jul 2026

3D net = -222.6 + -296.0 + 223.5 = -295.1M
5D net = -444.5 + -231.0 + -222.6 + -296.0 + 223.5 = -970.6M
7D net = -469.0 + -691.7 + -444.5 + -231.0 + -222.6 + -296.0 + 223.5 = -2131.3M
```

Conclusion:

```text
ETF_PRINT = POSITIVE
ETF_TREND_3D/5D/7D = NEGATIVE
```

This proves ETF print and ETF trend are not interchangeable.

Framework implication:

```text
Allowed:
  latest print supports "print improved"

Not allowed:
  latest print confirms durable flow trend
  latest print confirms recovery
  latest print confirms rotation
  latest print unlocks deployment
```

---

## 4. Proof C — ETH ETF Print/Trend Conflict Is Mixed, Not Fully Confirming

Source rows used:

| Date | ETH ETF Total |
|---|---:|
| 24 Jun 2026 | -30.3 |
| 25 Jun 2026 | -81.9 |
| 26 Jun 2026 | -12.8 |
| 29 Jun 2026 | -29.9 |
| 30 Jun 2026 | -27.6 |
| 01 Jul 2026 | 14.8 |
| 02 Jul 2026 | 29.0 |
| 06 Jul 2026 | 0.0 placeholder / pending |

Calculations:

```text
ETH ETF latest completed print = +29.0M on 02 Jul 2026

3D net = -27.6 + 14.8 + 29.0 = 16.2M
5D net = -12.8 + -29.9 + -27.6 + 14.8 + 29.0 = -26.5M
7D net = -30.3 + -81.9 + -12.8 + -29.9 + -27.6 + 14.8 + 29.0 = -138.7M
```

Conclusion:

```text
ETH ETF_PRINT = POSITIVE
ETH ETF_3D_TREND = POSITIVE
ETH ETF_5D/7D_TREND = NEGATIVE
```

This supports a **watch / partial repair** label, not full confirmation.

---

## 5. Proof D — Price/Range Layer Supports GATE-BTC-PARTIAL Better Than Gradueret Deployment

The extractor defines:

```text
BTC daily OHLCV
ETH daily OHLCV
ETH/BTC daily OHLCV
BTC rungs:
  63.3K
  61.9K
  61K
  60.9K
  60K
  59.4K
  59K
Reclaim/failure fields
ATR14
range %
streaks
forward outcome columns for scoring only
```

This is enough to evaluate:

```text
GATE-BTC-PARTIAL:
  BTC current/close survival
  BTC drawdown
  BTC vs WAIT return
  BTC vs pure BTC return
  ETH/BTC no-rotation guard
```

This is not enough to evaluate full Gradueret Deployment because it does not provide:

```text
daily breadth universe
daily BTC.D series
daily stablecoin official mcap / 7D / 30D
alt proxy baskets
fake rotation density
microcap exclusion data
```

Result:

```text
GATE-BTC-PARTIAL = TESTABLE
GRADUERET DEPLOYMENT = PARTIALLY TESTABLE / UNSCORABLE FOR OUTCOME UNTIL ALT PROXY + BREADTH + BTC.D LEDGERS EXIST
```

---

## 6. Proof E — No-Hindsight Rule Is Enforceable

The extractor includes forward-looking outcomes:

```text
btc_fwd_1d_return_pct
btc_fwd_3d_return_pct
btc_fwd_5d_return_pct
btc_fwd_7d_return_pct
btc_fwd_14d_return_pct
btc_fwd_30d_return_pct
btc_fwd_3d_max_high_pct
btc_fwd_3d_max_drawdown_pct
...
```

These are valid only for supervised scoring after the fact.

Evidence rule:

```text
Any row using forward outcome fields as an input signal is invalid.
```

This prevents lookahead.

---

## 7. Proof F — Promotion Cannot Be Justified Yet

Required for promotion:

```text
actual daily rows
timestamped source cutoffs
entry/exit basis fixed before outcome
decision divergence days
return vs WAIT
return vs pure BTC
drawdown
DATA_MISSING count
UNSCORABLE count
```

Current status:

```text
actual forward-test rows: 0
valid divergence days: 0
scored episodes: 0
unambiguous promotion evidence: 0
```

Conclusion:

```text
Promotion evidence = NOT_PRESENT
Allowed status = CONTINUE AS SHADOW FORWARD TEST
```

---

## 8. Evidence-Based Verdict

```text
GATE-BTC-PARTIAL FT-1:
  evidence_status: TESTABLE
  decision_value_status: PLAUSIBLE_NOT_PROVEN
  promotion_status: NO

GRADUERET DEPLOYMENT v1.1:
  evidence_status: PARTIALLY_TESTABLE
  decision_value_status: PLAUSIBLE_BUT_COMPLEX
  promotion_status: NO
  main_blocker: missing breadth/BTC.D/stablecoin/alt-proxy/fake-rotation daily ledgers
```

Final lab judgment:

```text
Continue both as shadow forward tests.
Prioritize GATE-BTC-PARTIAL first because it has cleaner data, cleaner benchmark, and clearer divergence.
Do not promote Gradueret Deployment until missing data ledgers are locked.
```

---

## 9. What This Evidence Does Not Prove

```text
It does not prove FT-1 improves returns.
It does not prove FT-1 reduces drawdown.
It does not prove staged alt deployment works.
It does not prove rotation.
It does not prove recovery.
It does not prove deployment.
It does not justify portfolio action.
It does not create an official row.
```

Rows beat theory.
