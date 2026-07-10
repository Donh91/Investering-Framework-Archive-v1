# Governance Binding — FRLP v0.1 B1–B9

**Date:** 2026-07-10  
**Status:** CANONICAL GOVERNANCE BINDING  
**Protocol:** Forward Range Ledger Protocol v0.1  
**Effect:** Activates FRLP for first resumed Cycle Navigator post / CN #12.

---

## Binding decision

The project owner instructed: **Activate FRLP v0.1.**

Governance therefore approves the recommended B1–B9 bindings from FRLP v0.1.

```text
B1 APPROVED — Human midpoint shift <=0.5x Wilder ATR14; written pre-week rationale mandatory.
B2 APPROVED — Official range never narrower than DUMB_1.5 width.
B3 APPROVED — DUMB_1.5 is official adjustment anchor; alpha still reported versus DUMB_1.5 and DUMB_2.0.
B4 APPROVED — Wilder ATR14, SMA seed, at least 60 settled daily candles, whole-USD rounding.
B5 APPROVED — UTC daily week [publication date; publication date+6], seven candles; post before day-1 close.
B6 APPROVED — FMP EOD-full primary, freshness-checked Kraken fallback; >0.5% difference creates SOURCE_CONFLICT; self-actuals forbidden.
B7 APPROVED — LOW_CONFIDENCE maximum 2 of rolling 8 scored weeks.
B8 APPROVED — Shadow re-anchor = trigger-day close +/-1.5x ATR14(trigger day), scored versus official over same remaining sub-window.
B9 APPROVED — K1-K3 use rolling 8 scored weeks; K4-K8 are event-based.
B10 OPTIONAL — ETH row is created whenever an ETH range is published, under identical rules.
```

---

## Authority boundary

This binding ratifies the **protocol mechanics**, not a range model's predictive skill.

```text
FRLP protocol: ACTIVE
Range model: FORWARD_TEST_ONLY
Official re-anchor: LOCKED / UNREACHABLE in v0.1
Portfolio authority: NONE
Market-call authority: NONE
```

---

## Operational consequence

From CN #12 onward:

```text
Every official range must have a frozen pre-week ledger row.
Every baseline must be calculated before publication.
Every score must use verified actuals.
Every range result must be separated from phase/structure scoring.
Every kill criterion must be monitored.
```

---

## Precedence

This binding supersedes any ambiguous or informal prior range-scoring practice that conflicts with FRLP v0.1.

It does not supersede broader Cycle Navigator, DATA PING, Master Monday or framework governance unless specifically stated.
