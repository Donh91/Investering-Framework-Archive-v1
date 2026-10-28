# AUTO_TRADING × ALPHA LAB · Horizon-aware signal research interface v1.0

**Date:** 2026-10-28 · **Class:** PUBLIC_SAFE_RESEARCH_SPECIFICATION · **Owner:** existing Auto Trading Research Vault / Alpha Lab #194 and #77 · **Authority:** RESEARCH_ONLY, no exchange access, order placement, live wallet, signing, alert activation, new scheduler or change to current paper-trader freeze version.

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
| CONTROL | material admin/mint/blacklist/LP withdrawal/hook powers reviewed | WATCH | confirmed catastrophic privileged risk |
| DEPTH | capacity and depth consistent with proposed notional; V4 LP not inferred from pooled reserves | WATCH | no workable route/depth |
| TIME | immutable point-in-time source and first-machine timestamps, no later features | HISTORICAL_ONLY | fabricated freeze or future leakage |
| LOSS | potential full-loss is budgeted against total capital; no leverage | NO_SIZING | outside accepted risk budget |

Any critical UNKNOWN is not converted into a numeric zero or a PASS. A high weighted score cannot override the veto. Existing production safety gates and governance remain authoritative.

## Published research weights, 0–10 descriptive features

Anchors: 0 adverse verified, 2 weak/concern, 5 mixed, 8 strong independently corroborated, 10 exceptionally well supported. Unknown = NULL. `coverage = sum(known weights)/100`; `weighted_score = sum(weight*feature)/sum(known weights)`. Publish coverage alongside score. These are not calibrated probabilities and cannot change canonical trade authority.

| Component | FRESH % | SWING % | CONVICTION % |
|---|---:|---:|---:|
| Remaining multiple from decision price | 25 | 15 | 5 |
| Independent buyers / wallet retention | 20 | 15 | 5 |
| Two-sided execution capacity and liquidity | 20 | 20 | 15 |
| Catalyst / first-source timing | 15 | 15 | 10 |
| Organic attention | 10 | 10 | 5 |
| Supply distribution and creator overhang | 10 | 15 | 15 |
| Verified token-economic value capture | 0 | 5 | 25 |
| Durable governance/security | 0 | 5 | 20 |
| **Total** | **100** | **100** | **100** |

Separate visible 1–10 scores: asymmetry, signal evidence, exit-risk evidence, long-term quality, learning value. Do not map score X/10 to X0% probability.

## Deterministic classifier pseudocode (not an execution algorithm)

```text
freeze SOURCE and candidate identity at decision_time
if wrong chain/CA or confirmed catastrophic sell/contract danger => AVOID
if missing verified intended-size exit or critical mechanism => WATCH_NOT_EXECUTABLE
if no pre-outcome source clock => HISTORICAL_ONLY
choose lane from intended horizon; never use 6-month durability veto on 72h meme
score only known inputs with published lane weights, print UNKNOWN coverage
compute remaining 2x/5x/10x/20x scenarios from current decision baseline
estimate net realizable multiple using actual size-specific quotes, costs and ability to exit
if short lane and 5x/10x remains plausible => SPECULATIVE_BUY_CANDIDATE research
if longer lane and evidence matches requirements => REVIEW_POSITION research
otherwise WATCH, REJECT or NO_TRADE with reason and time expiry
```

## Test plan, same original denominators and clocks

Reuse existing Alpha Lab outcomes #77 and current paper v4, no new wallet, no scheme change. Keep original frozen studies immutable. For launches and failed/never-launched cases, preregister both candidate and control at original first observation, not retroactively at onchain event time; preserve wrong-token, no-pool and unsellable rows.

Compare: (a) current old unified gate; (b) early WATCH only; (c) same hard-veto gates but horizon-specific speculative BUY_CANDIDATE, all on the same opportunity-set freeze. Outcomes: MFE/MAE and 2x/3x/5x/10x/20x thresholds at +15m/+1h/+6h/+24h/+72h/+7d; time-to-high vs time-to-collapse, $100/$500/$1000 feasible roundtrips after fees, provider latency, no-fill, catastrophic loss rate, precision/recall and total portfolio drawdown. Baselines: no-trade, random launch and simple momentum, with matched failing cohorts. Sparse data = CENSORED, not a negative verdict. Existing paper wallet decisions cannot be rewritten by a new label.

**Release gates:** at least one independently verified source-timestamped same-cohort comparison with negative controls and realized-size capacity, new frozen prospective holdout, Grok or equivalent independent adversarial review and exact-head tests. If adding speculative candidates creates only unfillable wins or unacceptable losses, reject the change. This file does not authorize an automatic BUY, code deploy, notification or new capital exposure.

## Cross-repository source ownership

Private detailed Alpha Lab methodology: `Donh91/Meme-Alpha-Lab/research/alpha_audit/MOONSHOT_SIGNAL_HORIZON_AND_RISK_ALGORITHM_V1.md` (review-branch pending, not necessarily merged). This public copy is intentionally sanitized, not byte-identical, because the public control plane cannot replicate private case or personal account evidence.

Research links: https://github.com/Donh91/Meme-Alpha-Lab/issues/194 and https://github.com/Donh91/Meme-Alpha-Lab/issues/77 ; governance in this vault `GOVERNANCE.md` and `research_inputs/PAIRED_RESEARCH_ARCHIVE.md`. Request separate source-pinned external Grok Bridge review via the existing provider workflow; a filed request does not establish that Grok actually executed it.
