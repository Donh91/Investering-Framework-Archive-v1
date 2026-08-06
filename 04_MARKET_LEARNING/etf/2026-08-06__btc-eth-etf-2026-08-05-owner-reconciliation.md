# ETF Owner Reconciliation — 2026-08-05

## Decision

Targeted validation `DP-ETF-DIRECT-OWNER-20260806-01` passed all owner-grade conditions.

Accepted rows:

- BTC ETF net flow: **+244.4M USD**
- ETH ETF net flow: **+60.8M USD**
- cross-asset flow spread: **BTC +183.6M USD**
- same-session sign: **DUAL_POSITIVE**

The earlier candidates `BTC +2.8M` and `ETH 0.0M` are permanently superseded as non-owner values because their source packets failed `INV-006` and the values exactly match the tenth fund cells rather than the Total columns.

## Issuer structure

BTC: IBIT +196.8, FBTC +11.3, BITB +10.6, ARKB +37.6, HODL -14.7, MSBT +2.8; all other funds zero. IBIT contributed approximately 80.5% of the total.

ETH: ETHA +50.3, ETHB +4.9, FETH +2.9, ETHW +1.4, TETH +1.3; all other funds zero. ETHA contributed approximately 82.7% of the total.

## Reproduced rolling windows from the repository row ledger

Through 2026-08-05:

| Window | BTC USD M | ETH USD M |
|---|---:|---:|
| 3 sessions | +626.0 | +102.0 |
| 5 sessions | +593.7 | +123.8 |
| 7 sessions | +576.1 | +100.3 |
| 10 sessions | +99.3 | +67.6 |
| 15 sessions | +809.8 | +224.5 |

The repository contains 16 directly owned rows in the active July-August ledger, so a 20-session calculation remains unavailable.

## Framework interpretation

The owner-grade result is stronger than the prior 4 August state:

- both assets received substantial positive flows;
- ETH participation is real and no longer unresolved;
- BTC remains dominant in absolute dollar absorption;
- the result supports repair and broad institutional demand, but does not independently prove ecosystem transmission or rotation.

It does not override:

- H7 `COND2 1/3 NOT MET`;
- no settled ETH/BTC close above 0.0300;
- incompatible/unconfirmed locked v1.1 breadth;
- absence of a valid newer bounded DATA PING because `INV-006` remains unresolved.

## State effect

```yaml
rotation: NO_ROTATION
capital_lifecycle: WAIT
rebuy: LOCKED
new_entry: NOT_ACTIVE
operational_risk_class: DO_NOT_ADD_RISK
canonical_state_change: NONE
portfolio_action: NONE
A_class_increment: 0
shadow_dual_run_increment: 0
```

## Engineering consequence

The exact earlier-value signature strongly supports a variable-width table parser defect. Issue #318 owns total-column resolution by normalized header identity. Issue #317 remains owner of invocation/payload and packet hash integrity.

## Research escalation

`RESEARCH_ESCALATION: NO`

The targeted source question is resolved. Remaining work is deterministic engineering and a fresh full DATA PING after both parser and `INV-006` remediation.