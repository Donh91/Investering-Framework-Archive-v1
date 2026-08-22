# Thread state summary

## Objective
The Investering framework is being developed as a research-governed system to improve timing around major crypto rotation/altseason decisions while avoiding false precision, overfitting and unnecessary portfolio churn.

The historical-altseason programme specifically asked whether historical sensors, shadow signals, pullback structure and execution signals contained reproducible, historically observable and incremental information that could improve timing versus simpler baselines.

## Core standing objectives
- Preserve Master Monday and Cycle Navigator as central orchestration concepts.
- Improve warning before altseason/rotation and before distribution/exit risk.
- Prefer missing the final 10–20% of upside over accepting 60–80% drawdowns.
- Keep historical research separate from automatic production promotion.
- User does not manually operate GitHub; bounded repo work is handled through controlled branches/PRs/CI.
- Claude/Cowork is research-only and must not receive GitHub write authority.

## Historical Altseason programme sequence
1. Historical lab design and time-integrity hardening.
2. Free-stage historical data construction.
3. Paid CFGI enrichment with strict budget/reserve accounting.
4. Readiness v3.1 with no-lookahead ASOF alignment for BTC/ETH CFGI.
5. MARKET CFGI historical rows proved provider-unavailable and were frozen as NOT_TESTABLE rather than filled/proxied.
6. Claude Opus Round 1 adversarial historical research.
7. Recovery of `alt_hourly_panel.csv.gz` and Claude Opus Round 2 cross-sectional completion.
8. Internal fixes from research findings, including protection against free-stage regression.
9. Round 2 terminal research decision archived on GitHub.
10. Next step chosen: a clean Round 3 BLUEPRINT on new information dimensions before any further hypothesis testing.

## Important architectural sidecar
An `Intraday Execution Research Layer` was separately introduced as a research-only challenger. It is not the regime engine and has no portfolio execution authority. It studies execution timing inside an already-valid exposure window using families such as session VWAP, relative volume, previous-day high/low, opening range, 1h/4h momentum/acceleration, taker flow, OI, funding, ETH/BTC and Top100 breadth. Historical findings from this layer also max out at FORWARD_TEST.

## Current decision
Do not spend more historical research budget on broad new transformations of the same price/volume/taker-share tape. Round 1 and Round 2 did not uncover robust actionable precursor edge, including at per-asset and liquidity-cohort level.

Next research capital should investigate genuinely new information dimensions such as open interest, funding, basis/term structure, order-book depth/imbalance/liquidity withdrawal, stablecoin exchange flows and cross-venue positioning/divergence.

## Process chosen for Round 3
Use TWO stages and preferably separate fresh research sessions:
A. `ROUND 3 RESEARCH BLUEPRINT` — study design only, source feasibility, 5–10 preregistered hypotheses, negative controls, multiplicity/power and prospective collection plan. NO hypothesis testing yet.
B. After ChatGPT adversarial review and a frozen research contract, start a fresh `ROUND 3 EXECUTION` session.

This separation exists to reduce anchoring, researcher degrees of freedom and post-hoc hypothesis drift.