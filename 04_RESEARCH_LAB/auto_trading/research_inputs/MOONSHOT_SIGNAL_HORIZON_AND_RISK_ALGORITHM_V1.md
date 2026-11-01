# AUTO_TRADING × ALPHA LAB · Horizon-aware signal research interface v1.0

**Date:** 2026-10-28 · **Class:** PUBLIC_GENERIC_RESEARCH_PROTOCOL / HYPOTHESIS_ONLY · **Owner:** existing Auto Trading Research Vault / Alpha Lab #194 and #77 · **Authority:** RESEARCH_ONLY, no exchange access, order placement, live wallet, signing, alert activation, new scheduler or change to current paper-trader freeze version.

## Purpose

Research whether evaluating an ultra-short-lived speculative asset under a short-horizon asymmetry objective (rather than a multi-month investment standard) can improve *realizable* upside discovery without increasing catastrophic financial losses. A displayed 2x is a useful partial-exit milestone, not the success definition for a 5x/10x moonshot. A token that could die tomorrow may be studied as a short-horizon speculation and still fail every larger-capital or long-term investment standard.

## Decision table

| Lane | Typical horizon | Key evidence | Research-only output |
|---|---|---|---|
| PROJECT_FIRST | before token launch | authenticated issuer, dated catalyst, no token yet | WATCH_PROJECT; never BUY |
| FRESH_MOONSHOT | 15 min–72 h, at most 7 days with renewed evidence | verified live token/pool, quote-size sellability, independent demand, remaining 5x and 10x cases | WATCH_FLASH or SPECULATIVE_BUY_CANDIDATE (advisory only) |
| PHOENIX_REVIVAL | 1–7 days | objectively dormant token, wallet buys before reprice, fresh genuine demand | WATCH_REVIVAL or speculative candidate |
| SWING | 1–21 days | retest/catalyst, buyer retention, drawdown and distribution | SWING_WATCH or SWING_BUY_CANDIDATE |
| CONVICTION | 1–6 months | independently supported token-linked revenue, security, adoption and unlock risk | POSITION_REVIEW |
| DEFENSIVE_LARGE | longer / substantial exposure | strong capital protection review, executable full-size exit and durable evidence | DEFENSIVE_REVIEW / NO_LARGE_BUY |

**Caution:** BUY_CANDIDATE is a research classification only; no auto trade or personalized large-size BUY recommendation.

## Required hard gates (all before a trade-candidate label)

| Gate | Required proof | Missing state | Hard veto |
|---|---|---|---|
| IDENT | independently verified chain + exact token contract + pool and issuer source | WATCH | fake token / wrong chain |
| EXIT | both buy/sell execution route quote at intended size, cost including taxes, fee, spread, slippage, gas | WATCH_NOT_EXECUTABLE | blocked sell / confiscatory hook |
| CONTROL | CONTROL_BOUNDED: source-confirmed role, hook, mint, blacklist and V4 LP/NFT privileges with absent/bounded catastrophic exit and drain control | WATCH_NOT_EXECUTABLE | confirmed catastrophic privileged risk |
| DEPTH | capacity and depth consistent with proposed notional; V4 LP not inferred from pooled reserves | WATCH | no workable route/depth |
| TIME | immutable point-in-time source and first-machine timestamps, no later features | HISTORICAL_ONLY | fabricated freeze or future leakage |
| LOSS | potential full-loss is budgeted against total capital; no leverage | NO_SIZING | outside accepted risk budget |

Any critical UNKNOWN is not converted into a numeric zero or a PASS. A high weighted score cannot override the veto. Existing production safety gates and governance remain authoritative.

## Public research factor classes, no published calibrated weights

This document supplies a **general scientific comparison protocol**, not a published scoring model. Descriptive factor classes that may be compared include remaining upside, independent buyer participation, two-sided liquidity, source timeliness, organic attention, supply distribution, documented economic use and governance or security. No public relative weights, numerical promotion floors, portfolio allocations, proprietary formulas, private cohort membership or calibrated thresholds are specified or authorized. Any future private implementation must be independently version-frozen and reviewed in its appropriately restricted owner repository.

Missing input is `UNKNOWN`, never neutral-imputed, and a research gate never substitutes for verified execution, source clock or privileged-token safety. Public comparisons should report data coverage, missingness and matched outcomes with transparent null baselines, not private scores.

## Deterministic classifier pseudocode (not an execution algorithm)

```text
freeze SOURCE and candidate identity at decision_time
if wrong chain/CA or confirmed catastrophic sell/contract danger => AVOID
if missing verified intended-size exit or G2 CONTROL_BOUNDED or critical mechanism => WATCH_NOT_EXECUTABLE
if no pre-outcome source clock => HISTORICAL_ONLY
choose lane from intended horizon; never use 6-month durability veto on 72h meme
evaluate only permitted evidence; keep any calibrated private weights and floors inside the private authority; report source coverage and UNKNOWN
compute remaining 2x/5x/10x/20x scenarios from current decision baseline
estimate net realizable multiple using actual size-specific quotes, costs and ability to exit
if short lane shows plausible remaining asymmetric opportunity AND privately governed execution and safety thresholds pass AND all hard gates PASS => research-only candidate for separate governed review
if longer lane and evidence matches requirements => REVIEW_POSITION research
otherwise WATCH, REJECT or NO_TRADE with reason and time expiry
```

## Test plan, same original denominators and clocks

Reuse existing Alpha Lab outcomes #77 and current paper v4, no new wallet, no scheme change. Keep original frozen studies immutable. For launches and failed/never-launched cases, preregister both candidate and control at original first observation, not retroactively at onchain event time; preserve wrong-token, no-pool and unsellable rows.

Compare: (a) current old unified gate; (b) early WATCH only; (c) same hard-veto gates but horizon-specific speculative BUY_CANDIDATE, all on the same opportunity-set freeze. Outcomes: MFE/MAE and 2x/3x/5x/10x/20x thresholds at +15m/+1h/+6h/+24h/+72h/+7d; time-to-high vs time-to-collapse, $100/$500/$1000 feasible roundtrips after fees, provider latency, no-fill, catastrophic loss rate, precision/recall and total portfolio drawdown. Baselines: no-trade, random launch and simple momentum, with matched failing cohorts. Sparse data = CENSORED, not a negative verdict. Existing paper wallet decisions cannot be rewritten by a new label.

**Release gates:** at least one independently verified source-timestamped same-cohort comparison with negative controls and realized-size capacity, new frozen prospective holdout, Grok or equivalent independent adversarial review and exact-head tests. If adding speculative candidates creates only unfillable wins or unacceptable losses, reject the change. This file does not authorize an automatic BUY, code deploy, notification or new capital exposure.

## Public provenance and release policy

This public version is deliberately limited to generic, uncalibrated methodological principles. The detailed source evidence, selection universes, private research links and any proprietary factor calibration are restricted to their existing authorized owner. The historical public versions of this Draft may remain visible in Git history, forks and caches; removing unnecessary detail here does **not** erase an earlier disclosure or imply proven proprietary edge.

Prior independent advice in [Grok Bridge #82](https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/82) and [#118](https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/118) informed the generic hard gates and public IP review. Those are advisory reports, not formal GitHub APPROVED or performed same-cohort test results. No original candidate, quote, private research document, selected wallet, live BUY, portfolio action, exact-head CI, execution or scientific edge is certified by this document. An approved **document** is distinct from releasing the uncalibrated research hypothesis or promoting an eventual private model.

**Acceptance:** independently reviewed research-document privacy gate and current-head code/document CI can close this public artifact if allowed by the original owner; **quantitative model promotion** separately requires prospective source-clock admission, identical cohorts, negative controls, size-specific actual executable quotes, costs and statistically honest uncertainty. Frozen original outcomes must not be rewritten.
