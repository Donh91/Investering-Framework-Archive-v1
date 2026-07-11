# S4 Hybrid Zero-Weight Shadow Logging Protocol v0.1

**Date:** 2026-07-11  
**Status:** ACTIVE_SHADOW  
**Authority:** ZERO_WEIGHT / NO_EXECUTION_AUTHORITY

## 1. Percentile Gate Log

Purpose: compare fixed ETH/BTC gates with cycle-normalized gates.

Default shadow calculations:
- rolling window: 365 settled daily closes
- `ratio_percentile`
- repair candidate: percentile > p60
- rotation candidate: percentile > p80

These thresholds are Fable design hypotheses, not active rules.

Log every eligible fixed-gate cross in parallel with:
- fixed gate
- ratio percentile
- 365d distribution coverage
- hold days
- 14/30/60d outcomes
- fake-fast / fake-standard / slow-bleed / real-candidate label

Kill:
- after at least 10 resolved crosses, if percentile gates do not beat fixed gates on pre-registered fake-rate/retention metrics, reject or redesign.

## 2. Exit Ladder E0–E7 Log

Purpose: instrument the framework's exit-side blind spot.

States:
- E0 NEUTRAL
- E1 PRE_ALT_PREP
- E2 ALT_ACTIVE_MONITOR
- E3 PROFIT_READINESS
- E4 DISTRIBUTION_WARNING
- E5 EXIT_RISK_ESCALATION
- E6 TERMINAL_ALERT
- E7 POST_TOP_PROTECTION

Rules:
- all states are walk-forward and zero weight
- E1–E4 contain no trade-size or sell instruction
- no state may skip a level
- every transition needs an explicit falsifier
- only governance may approve action language
- minimum eight forward rows per material state before any authority discussion

## 3. Challenger Log

Purpose: score a contemporaneous alternative against the official framework.

Requirements:
- same data cutoff
- same source quality
- frozen before the outcome
- no post-hoc parameter changes
- explicit kill criteria at birth
- challenger never alters official output

## 4. Promotion boundary

No component can move beyond shadow unless:
- minimum frozen sample is met
- benchmark is beaten
- performance survives regime stratification
- placebo/ablation checks do not falsify it
- governance ratifies the change
