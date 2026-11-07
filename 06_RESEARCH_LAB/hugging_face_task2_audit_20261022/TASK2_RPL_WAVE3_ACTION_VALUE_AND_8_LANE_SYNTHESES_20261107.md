# Task 2 #1596 | P3 investor action / P4 Research Parallel Lanes Wave 3
**Source snapshot date:** 2026-11-07. **Original owner:** #1596, existing M1/M4/Shared Row/Research Lab/S1 owners remain separate.  
**Authority:** SOURCE_BOUND_RESEARCH_ONLY. **No new automation, AI-agents, paid calls, market thresholds, trading or historical source backfill.**  
**Runnable:** `scripts/research/task2_rpl_wave3_action_value_sensitivity_v1.py`; existing `tests/research/test_task2_archive_first_edge_matrix_v1.py` loads eight additional hard-fail controls from `tests/research/test_task2_rpl_wave3_action_value_sensitivity_v1.py`.

## P3, an executable decision needs an actually received signal, not a classification label

The original R1 as-issued cohort has **11 registered attempts, 9 original outcome receipts and 0/11 scientific admissions**, and **0 original first-user-delivery time receipts**. Zero verified deliveries is not proof that zero people actually received an alert, and original Git push does not prove investor visibility.

The separate original Task 1.5 record has **824 retrospective price joins**, only **814 originally registered outcome receipts**, of which **500 were CENSORED and 314 MATURED**, and **10 had NO ORIGINAL RECEIPT**. A later price tape cannot retroactively transform the original 500 censored or 10 missing into original due-time outcomes. The full original no-warning/no-forecast/unalerted population remains unenumerated.

Historical M1 **legacy C2** had 14 unique signal dates and 2 marked false-alarm dates (**14.29% of original signal dates**, NOT a population false-positive rate); 30d matched-random reported single-rule p≈0.058, C-family p≈0.006 on correlated alternative rules. A warning with no user delivery and no feasible costed order cannot be scored as investor return. Neither the original R1 nor this research is an approved live SELL/HOLD rule.

### Original historical operational-delay sensitivity, TWO distinct strategies

Original `M4_STRATEGY_OPERATIONAL_LATENCY_TEST.csv` source blob `5689ebe69096ef6e348146c1408be447a85469d0`. Scenarios already include an original one-day lag. The extra delay shown below is **on top of that historical lag**, not original issue-to-receipt latency and not the marginal trading cost of a live action.

| Historical development strategy | +0 additional days total return | +1 additional day total return | Additional day delta |
|---|---:|---:|---:|
| DEPLOYMENT_EXPANDING | +17.545% | -4.978% | **-22.523 percentage points** |
| JOINT_TRANSMISSION | +10.999% | +19.353% | **+8.354 percentage points** |

This is an actual source-backed **interaction**: latency worsened one ex-post strategy and improved another. The two approaches have materially different exposure and original switches; none of these percentages are matched, after-cost or original-user-executable HOLD comparisons. No generic rule like "always sell immediately after a warning" is inferred.

## P4 Wave 3, new *hypothetical misclassification-cost* falsifier

The original source-matured 23 ETHBTC sign rows (21 UP, 2 DOWN) and 20 earlier matured rows were held to their ORIGINAL frozen observations and outcome receipts. There is only **one 28-day calendar block, independent shock-family count UNKNOWN**. This is **not a basket trade or a market-independent prospective out-of-sample cohort**. The Wave 3 analysis is a hypothetical *unit-loss ratio* test, **not** a PnL simulation.

On the **23 same-source matured rows**:

| Binary classifier | True positive | True negative | False positive | False negative | Correct |
|---|---:|---:|---:|---:|---:|
| Always predict ETHBTC UP | 21 | 0 | 2 | 0 | 21/23 |
| Shared Row C02_BREADTH | 7 | 2 | 0 | 14 | 9/23 |
| Shared Row C07_SIMPLE_3 | 0 | 2 | 0 | 21 | 2/23 |

Let a *hypothetical* miss of an actually UP 7-day ETHBTC label have abstract loss `C_FN = 1`, and a falsely predicted UP against DOWN have cost `C_FP = x`. These are **arbitrary unit penalties**, *not fees, slippage, expected return, drawdown or investable trade costs*. Then the observed sample's loss is:
- Always UP = `2x`
- C02 breadth = `14`
- C07 strict three-condition = `21`

Therefore C02 first beats ALWAYS-UP **only when `x > 7`**, with equality at `x = 7`. The earlier 20-row window's threshold was `x > 5.5`, illustrating the apparent utility's instability when three new UP outcomes mature without additional C02 hits. For C07, threshold versus ALWAYS-UP is `x > 10.5`; with the observed identical FP=0 and TN=2, C07 is also dominated by C02 for any positive missed-UP penalty **within this exposed sample only**. These thresholds are the relevant sensitivity analysis for the common question "could a conservative early-warning rule be worth missing many positives?" They **do not show an economic advantage** for any candidate.

Unit-loss scenarios (same 23 source rows):

| Abstract false-UP cost `x` | Always-UP loss | C02 loss | C07 loss |
|---|---:|---:|---:|
| 1 | 2 | 14 | 21 |
| 5 | 10 | 14 | 21 |
| 8 | 16 | 14 | 21 |

One overlapping development block and only two DOWN labels make true prospective downside protection, market conditions and live investable utility unknowable. Do not tune actual classifier weights to these exposed threshold values.

## Eight scientifically different questions, and what actually ran

| ID | Question | Mode and verdict |
|---|---|---|
| W3-L01 | Earliest original issued R1 forecast eligible at actual first-known vintage? | Public immutable metadata read, **0/11** admitted, vendor vintage BLOCKED |
| W3-L02 | Which original fields causally determine BTC/ETH 12h direction? | Existing original AST causal matrix + current preflight, 22 delta instances, 198 nondirect context, **not predictive edge** |
| W3-L03 | Can M1 C2 warn before actual investor action, with full unalerted controls? | Existing original timing atlas reviewed; 2/14 signal dates marked false alarm, no no-warning population, BLOCKED |
| W3-L04 | How do conservative C02/C07 and always-UP compare under varying asymmetrical binary error costs? | **New deterministic replay + 8 tests**; C02 break-even `C_FP/C_FN = 7`, no economic/market claim |
| W3-L05 | Is one more day delay universally harmful? | **New cross-strategy original archived replay**; opposing +8.354pp and -22.523pp response, hypothesis falsified |
| W3-L06 | Does breadth or strong ETF persistence replicate after price and release clock? | Existing negative owners *reconciled, not newly rerun*, no positive admissible edge |
| W3-L07 | Does Ironflow or CFGI independently add predictable lift after price/vol? | Existing corrected null owners *reconciled, not newly rerun*, original source first-known still unavailable |
| W3-L08 | Does the warning beat a costed actually executable HOLD? | Original action-to-delivery audit; original delivery+fill clocks absent, outcome **NOT IDENTIFIABLE**, not 0% edge |

This is **one coordinating chat with source-grounded parallel investigations and one deterministic source-bound Python replay**. Any completed native independent GitHub PR checks must be reported with real run+job IDs separately. No claim of eight independent autonomous AI agents, eight parallel GH jobs or a new Sol MAX response. Reuse past corrected Ironflow rather than paying/download 18-month data again.

## Stop rules / owner's next finite action

1. Preserve all original outcomes, original HEADs, negative baselines and non-independent blocks. Do **not** promote C02 or a latency timing rule.
2. Original #1596: ensure first-known provenance for the two direct price-delta chains and **all eleven required source-health lanes**, no-forecast/abstention/negative episodes. A source-only preflight marked BLOCKED is a useful result, not a failed automation.
3. Existing actual delivery owner #1553: register per user-visible warning an immutable first-delivery timestamp, actual eligible action time and frozen reference fill/fees/slippage, then compare to same-clock HOLD/no-warning on **new** true eligible events. A timestamp is a necessary condition, not sufficient economic evidence.
4. Existing private Round 3 owner: keep `PROSPECTIVE_COLLECTION_ONLY`, budget-driven two daily capture schedules until actual monthly GH minutes P50/P95 and reviewed cadence allow changes. Do not merge source-value scoring into the restricted collection workflows.
5. Existing CRE/S4/Research Lab: collect due-only prospectively frozen independent event families; evaluate full horizon uncertainty, negative controls, and policy loss with preregistered action stakes. Independent prospective shock N remains UNKNOWN here.

**Completion semantics:** On-demand P3/P4 falsification and owner archive implementation may be COMPLETE once native exact-HEAD CI and `main` readback prove the original research deliverables. **Claim of scientific R1 or investable warning edge remains BLOCKED** and cannot be solved by another PR alone.
