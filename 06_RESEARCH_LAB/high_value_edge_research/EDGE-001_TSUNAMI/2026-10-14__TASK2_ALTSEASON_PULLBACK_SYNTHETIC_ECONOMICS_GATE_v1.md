# Task 2 / EDGE-001: altseason pullback, protection & re-entry, synthetic economic gate

**Date:** 2026-10-14. **Classification:** RESEARCH_ONLY / SYNTHETIC_EXECUTED_LOCALLY / HISTORICAL_PIT_BLOCKED. **Existing owners:** #1530 (EDGE-001), #1553 (risk-to-action), #1596 (Task1.5/R1), and the canonical Task 2 R0–R7 handoff. **No new engine of market truth, new schedule, signal owner, data collector, AI API usage, portfolio authorization or SELL rule.** This is a bounded test utility that can be independently reviewed and later reused *only after* a distinct source/outcome approval.

## 1. Two claims, never conflated

- **Information edge:** Did original state/feature evidence, with independently verified first-known, issue and first-delivered timestamps, warn earlier than **same-clock** P1 (-5% from peak), P2 (-3%), volatility and trend controls? Includes *all* missed adverse families, recovered warning families and healthy pumps.
- **Economic action edge:** Would a separately frozen, lawfully deliverable and executable partial trim plus fixed causal re-entry increase terminal wealth or reduce tail loss **after** total trading costs compared with an incumbent HOLD position? Also report false-exit regret and *inability to fill*. This is a research counterfactual, not live action authority. `WARNING != SELL; LIVE_EXIT_RULE = NONE`.

The source of scenario candidates remains the existing R4P A–T (20 adversarial scenarios) and the original EDGE-001 charter. The **144 original sensitivity variants remain untouched** (3 minimum states × 4 persistence × 3 delays × 4 cooldowns), do not constitute 144 independent market events, and may not be optimized on already-opened 2025–26 outcome history.

## 2. Implemented bounded code and actual local tests

- `scripts/research/task2_protection_synthetic_v1.py` validates a single synthetic warning, synthetic hourly executable **bid/ask** quotes, bounded size capacity, UTC source-known/issue/delivered clocks, and a *predeclared* holder-only partial trim and fixed-clock re-entry. It refuses historical provenance and unauthorized warning states, and executes at the **first quote strictly after** delivery plus delay. A rejected fill cannot be retried at a conveniently better quote; re-entry has one opportunity after its fixed clock.
- `tests/research/test_task2_protection_synthetic_v1.py` contains **29 unittest cases** for early crash, fast V rebound, pump false warning, delayed delivery, inability to sell/re-enter, spread/fees, causal next-quote, no historical-source spoofing, source/capture clock inversion, duplicate bars, NaN, policy bounds and zero live authority.
- Local Linux/Python: **29/29 PASS**, including six additional first-warning versus online running-peak P1 (-5%) / P2 (-3%) causal controls. Exact GitHub PR-head code still requires independent check/run on a checkout and review; local test execution is **not** a forecast validation or second-principal approval.
- Run from repository root (stdlib only):
  `python -m unittest discover -s tests/research -p 'test_task2_protection_synthetic_v1.py' -v`.
- A second function `price_only_lead_synthetic` calculates first running-peak -5%/-3% price-only crossings using only each synthetic quote known so far. It reports original warning delivery minus baseline crossing with a signed lead (late warnings remain negative), tests pump false positives, and refuses fabricated early source/capture clocks. It does **not** declare real early-warning precision or authorize alternate P1/P2 policy thresholds.
- Per-fill synthetic intermediate fees, slippage, gas, nominal turnover and time out of market are explicitly reported, with blocked fills costing no fictitious trade fees; two additional regression tests cover these totals.
- No historical market data or restricted payload was consumed. There is deliberately **no historical backtest CLI** and no path for caller-supplied proof strings to activate one.

**Tiny mechanical illustration, NOT a performance estimate:** $10,000 incumbent at first quote, synthetic 50% trim, assumed 0.1% per-trade fee + 0.1% slippage, zero bid/ask spread and adequate fictional liquidity. On explicit synthetic 6-quote crash path [100,95,60,50,55,58] the terminal economic delta versus HOLD is approximately **+$1,829.20**; on a V-recovery [100,95,98,110,130,160] it is approximately **-$2,175.01**; on a pump [100,110,120,145,170] approximately **-$3,018.94**. In a deliberately illiquid case the sale fails and no imaginary protection is credited. These amounts change with any quote/cost/clock assumptions. **None** is an observed crypto-trading result or action advice.

## 3. Full altcoin cycle / pullback investigation matrix, proposed research, NOT tests executed

| Dimension | Require separately frozen observation/decision/after-cost condition | Falsifier / critical control |
| --- | --- | --- |
| Market phase | BTC-led, ETH catch-up, broad large/mid rotation, small/micro acceleration, euphoria, distribution, cooldown, rebound; phases can overlap/skip/regress | Fixed-sequence PATH vs simple relative-strength, trend and no-rotation models, vintage-aware altseason labels |
| Severity | BTC and ETH separately; liquid large/mid; survivorship-adjusted small/micro/meme groups; % depth, tail drawdown, velocity, volume and 2h–56d recovery | BTC -2% with micro -30%, or false large-cap proxy; no use of current winners as old universe |
| Warning lead | First source publication, collector as-of, original issued, first seen by user, action clock, price-only trigger/onset/trough | Late signal after trough; source capture/revision after market move |
| Liquidity | Real prevailing bid/ask, spread, executable notional, depth withdrawal, pool tax, volatility halt, minimum trade, provider/venue downtime | Failure to sell when danger highest; use no fantasy BTC-priced microcap fill |
| Derivatives | Causally knowable OI, funding *estimate vs future settlement*, liquidation and basis, spot/perp participation | OI/funding follows price rather than precedes, settlement mislabel, vendor time drift |
| Breadth & rotation | As-of top-N membership incl. delistings; ETH/BTC, BTC.D, USDT.D, TOTAL2/3 and breadth with native cadence; stablecoin issuance vs deployment | Momentum/volume baseline explains entire signal, trailing altseason label used as predictor |
| Sentiment | CFGI composite and components, velocity/divergence, engine before/after 2026-07-08, true first-known | Price-only residual comparison, later backfill presented as early |
| Action | Distinguish existing holder, new cash, position tier, partial trim 10/25/50% as research candidates, transaction tax uncertainty and fixed capital | false exit during pumps, early/late trim, missed upside, adverse fill |
| Re-entry | Fixed time or *prospectively frozen* reclaim rule, first available price, latency, missed fill, second leg costs; same clock as BUY-and-HOLD | hindsight trough purchase, stale reclaim, range-bound chop, repeated fees |
| Causal regime | Sudden liquidations, long slow bleed, V recovery, repeated bear traps, bullish grinding volatility, narrative shock, false OI surge | negative-control continuation periods; preserve no-warning/no-event observations |

Research horizons are separate **0–6h, 6–24h, 1–3d, 4–7d, 8–21d, 22–56d**, not a shared scalar probability. Any sensitivity grids for trims/costs/horizons are candidate descriptions, **not authorized market thresholds** or an ex-post winner search.

## 4. Admission requirements before *historical* replay (MANDATORY)

1. R0 verifies immutable source Git object and enumerates every issued forecast/abstention/missing outcome, non-events and current/read-only owner boundaries. A public Git blob does **not** independently prove the provider knew the value.
2. R1 validates provider-first-known, actual observation versus funding settlement, model/scoring effective version, delivery to investor, native horizon target and outcome source. No historical code path until **independent owner-approved, cryptographically bound** admission and valid source-specific freshness.
3. Original M6/EDGE-001 T2B joins remain **blocked** where no typed warning at the historical decision time can be proven. No retrofitting current ELEVATED/HIGH categories into predecessor signals.
4. Existing Round 3 private prospectively collected source health can be inspected for provenance only; current `analysis_authorized=false` prohibits label joins, effect sizes and outcomes. **No paid collection or inference** from private schema alone.
5. Event families must be clustered across BTC/ETH/correlated alt crises and time; use frozen 14d M6 merge rule with 7d/30d sensitivity; 91 prior retrospective event/control rows are not 91 independent market crises.
6. Pre-register historical baselines B0 independent random prior, B1 abstention, B2 momentum/persistence, P1/P2 original price-only, static HOLD, price+volatility, simple relative strength and cash-WAIT. Original warning must beat fair *same time, same asset, same fills/costs* controls. Exposed 2025–26 history is **development**, not untouched holdout.
7. Future sealed validation with embargo >= overlapping largest forecast horizon, family-level confidence intervals, all variant results, negative controls, no retroactive replacements, and independent review. If independent N is too small say `NOT_IDENTIFIABLE_YET`, not PASS/FAIL.
8. Only after scientific information-edge review, a *separately authorized* economic action replay with comparable capital and documented execution costs can be proposed. **Never** auto-activate SELL or change current Compass/CN site based on this harness.

## 5. Measurable outcomes in the eventual approved tournament

For every independently eligible adverse or control family: attempted warnings, abstains/no-data/missing, false-alert hours and missed falls; event onset and first actionable warning lead vs P1/P2; duration, drawdown by tier, recovery and re-entry; fill failures, turnover, fee/spread/slippage/gas, return/cash opportunity, exposure time, worst-regime max DD, CVaR if powered, terminal after-cost wealth vs original HOLD, plus uncertainty. Show *each* signal/information/calibration/decision/economic/delivery verdict independently. No combined “edge” score. Use prospective evaluation before any promotion.

## 6. Remaining gates and exact owner handoff

This isolated branch contains only a synthetic economics utility, its tests and this note. It is **not** a second EDGE engine or new scheduler. An independent reviewer should reproduce all 29 tests at exact PR SHA and inspect the fill/clock/denominator limits. After guarded merge if approved, the test utility can stay research-only as preparation for a **different** independently authorized historical implementation. Next high-value work is existing #1596 R1 real source issue/delivery/funding fix, #1530 EDGE-001 T2B historical warning admissibility, #1553 investor action economics owner and the frozen original 144-variant surface. The older scoped Round-2 negative result (11 reload variants none beat HOLD in their tested population) remains immutable and is **not** reopened.

**Status:** `ENGINEERING_SYNTHETIC_TESTED / HISTORICAL_SCORE_NOT_RUN / SOURCE_R1_BLOCKED / ZERO_TRADING_AUTHORITY`.
