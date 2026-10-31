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
| CONTROL | CONTROL_BOUNDED: source-confirmed role, hook, mint, blacklist and V4 LP/NFT privileges with absent/bounded catastrophic exit and drain control | WATCH_NOT_EXECUTABLE | confirmed catastrophic privileged risk |
| DEPTH | capacity and depth consistent with proposed notional; V4 LP not inferred from pooled reserves | WATCH | no workable route/depth |
| TIME | immutable point-in-time source and first-machine timestamps, no later features | HISTORICAL_ONLY | fabricated freeze or future leakage |
| LOSS | potential full-loss is budgeted against total capital; no leverage | NO_SIZING | outside accepted risk budget |

Any critical UNKNOWN is not converted into a numeric zero or a PASS. A high weighted score cannot override the veto. Existing production safety gates and governance remain authoritative.

## Published research weights, 0–10 descriptive features

Anchors: 0 adverse verified, 2 weak/concern, 5 mixed, 8 strong independently corroborated, 10 exceptionally well supported. Unknown = NULL. `coverage = sum(known weights)/100`; `weighted_score = sum(weight*feature)/sum(known weights)`. Publish coverage alongside score. These are not calibrated probabilities and cannot change canonical trade authority.

| Component | FRESH % | SWING % | CONVICTION % |
|---|---:|---:|---:|
| Remaining multiple from decision price | 15 | 15 | 5 |
| Independent buyers / wallet retention | 20 | 15 | 5 |
| Two-sided execution capacity and liquidity | 30 | 20 | 15 |
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
if missing verified intended-size exit or G2 CONTROL_BOUNDED or critical mechanism => WATCH_NOT_EXECUTABLE
if no pre-outcome source clock => HISTORICAL_ONLY
choose lane from intended horizon; never use 6-month durability veto on 72h meme
score only known inputs with published lane weights, print UNKNOWN coverage
compute remaining 2x/5x/10x/20x scenarios from current decision baseline
estimate net realizable multiple using actual size-specific quotes, costs and ability to exit
if short lane and 5x/10x remains plausible AND execution_quality>=7 AND TRADING_SAFETY_EVIDENCE>=7 AND all hard gates PASS => SPECULATIVE_BUY_CANDIDATE research
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


## Independent Grok Bridge #82 · ADAPT change contract (research only, 28 Oct 2026)

Source: [Independent Grok report #82](https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/82) on original Alpha #198 / Archive #1826 pinned revisions. **Grok advisory ADAPT is not formal code review, verified backtest or authorization to trade.** This public-safe interface mirrors the specific conclusions below, not private Alpha evidence. Existing governance and source owners unchanged.

**P0 CONTROL_BOUNDED:** A token with a verified ERC20 but a *different* non-renounceable or privileged V4 hook, factory or LP position is NOT automatically protected. Require exact token+pool+V4 position/NFT ownership, hook fee/admin/blacklist/withdrawal/tax powers and role/timelock source receipts. Unbounded operator control and withdrawable LP => **no BUY_CANDIDATE**; confirmed critical exploit or blocked sell => AVOID. Inspected but UNKNOWN permissions => WATCH_NOT_EXECUTABLE. A non-renounceable hook with **strictly bounded operational control** is not automatically a scam; document exact residual risk before classification. New G2 status `CONTROL_BOUNDED` is REQUIRED, not inferred from owner()=dead.

**P0 weighting and floor:** FRESH_MOONSHOT remaining upside weight **15** and execution/quoted market quality **30**, other weights constant (total 100); interim research hypothesis only, not optimized on historical winners. Both feature `execution_quality` and separate `TRADING_SAFETY_EVIDENCE` must be >=7/10 **plus all G0–G5 hard gates PASS** for a research-only speculative BUY_CANDIDATE. Missing key permissions/liquidity do not get a neutral 5 and never pass based on a weighted mean.

**P0 economic proof:** Actual USDG transfers and REBATE burns show mechanics function; they do NOT prove unaffiliated fees, unique paying customers or sustainable tokenholder cash flow. If fee/burn optics are observed without proved independent paying demand, value-capture score **provisional ceiling 2/10 if circular mechanical activity is actually evidenced**, otherwise UNKNOWN when independent provenance cannot be assessed. No fabricated revenue label. FRESH_MEME weighting for this component remains zero.

**P1 executable $ capacity:** Timestamped, route-consistent read-only **both-direction** quote for $100, $500, $1000 or explicit `CAPACITY_BELOW_MIN/UNSUPPORTED_SIZE` per tier. Log `FULL_FILL/PARTIAL_FILL/NO_FILL/UNKNOWN` with taxes, fees, slippage, gas, LP depth and timestamps. A feasible current $100 sell does NOT certify $500 or a future 10x exit; quote validity expires quickly.

**P1 portfolio correlation:** Treat every speculative stake as potentially 100% lost, and correlated same-funder/launchpad/narrative/venue exposures as one stress bucket. Ten positions each 0.5% total capital = 5% portfolio wipe in joint failure; illustrative only. If total sleeve budget, existing overlap or trade-size portfolio risk unknown, NO_SIZING and no large-capital BUY.

**P1 test fixtures before shadow BUY:** N1 wrong CA/pool -> ID_FAIL; N2 blocked sell -> NO_FILL; N3 arbitrary privileged drain/LP control -> AVOID; N4 missing machine first_seen -> historical/owner-only; N5 same-funder fake buyer breadth -> no independence credit. O1 cancelled launch -> NEVER_LAUNCHED; O2 10x mark but no seller -> SPOT_ONLY_NO_FILL; O3 2x then rug -> net partial exit only if filled; O4 5x after -80% MAE -> precommitted stop respected; O5 verifiable net 5x for $100 but $500 NO_FILL -> success only for proven $100. **Fixture descriptions are NOT run tests.**

**Finite STOP:** Original #85 frozen 2x rule unchanged; a new per-horizon metric is additive. Same PIT complete-denominator comparison old unified / EARLY_WATCH / safety-bounded speculative, with after-cost $100/$500/$1000 outcomes, B0/B1 and negative controls; exact-head deterministic tests plus independent validation. If changes increase catastrophic exposure or unfillable 5x without a measurable net utility improvement, REJECT promotion. **Status SHADOW_RESEARCH_SPEC_ONLY / NOT_LIVE / NO_EXECUTION.**