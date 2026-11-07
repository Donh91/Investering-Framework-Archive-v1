# Task 2 #1596 · Research Parallel Lanes Wave 3, model-loss frontier and cadence gate

**Dato:** 2026-11-07 UTC  
**Status:** SOURCE-BOUND RETROSPECTIVE FALSIFICATION / NO TRADING-UTILITY ADMISSION  
**Område:** Research Lab, Task 2 #1596  
**Original source owner:** Archive #1596, derivatives #387 and private source-health plane retain separate authority  
**Snapshot:** original public source `research/framework_memory/task2_archive_first/LATEST.json` read at source owner 2026-11-07T09:00:10Z, Git blob `00b8d0839d69e375e584e10e033e9a57d99bcb56`. All relevant original binary decisions/outcomes are validated within the existing Task2 source/receipt gate, not independently re-vintaged against historical vendor publications.

## L04, exact decision-loss comparison before adding any real-market assumptions

The **23 matured seven-day ETHBTC binary outcomes** contain **21 positive, 2 negative**. These are overlapping decision timestamps in **ONE 28-day source block**, NOT 23 independent market shocks and NOT a universe of sellable altcoins. The matched original confusion matrices on exactly these 23 outcomes:

| Frozen model | True positive | True negative | False positive | False negative | Overall correct |
|---|---:|---:|---:|---:|---:|
| Always-positive B0 | 21 | 0 | 2 | 0 | 21/23 |
| C02_BREADTH | 7 | 2 | 0 | 14 | 9/23 |
| C07_SIMPLE_3 | 0 | 2 | 0 | 21 | 2/23 |

Define a **purely illustrative binary classification error penalty**, not currency, trading PnL, volatility, realized drawdown or a preferred policy:

`hypothetical_error_units = FP * r + FN * 1`, where `r` is the relative penalty for a wrong positive label versus a wrong negative label. A true negative earns zero utility here, and neither actual signal timing nor wallet executable outcome is represented.

| Hypothetical FP:FN penalty | Always-positive loss units | C02 loss units | C07 loss units |
|---|---:|---:|---:|
| 1:1 | 2 | 14 | 21 |
| 5:1 | 10 | 14 | 21 |
| 7:1 | 14 | 14 | 21 |
| 10:1 | 20 | 14 | 21 |
| 20:1 | 40 | 14 | 21 |

**Exact observed sample break-even:** C02 vs B0 is at `r = 14/2 = 7`, so C02 only has fewer *hypothetical error units* above 7:1. C07 vs B0 break-even at `r = 21/2 = 10.5`. C02 has 7 fewer false negatives than C07 and identical false positives in this exposed sample, hence weakly dominates C07 on these limited binary labels. **This cannot establish C07 is a worse true warning/risk gate in independent crash regimes**; missing independent negatives and sellable after-cost path dominate scientific uncertainty.

For the earlier frozen 20-row snapshot, the analogous C02 vs B0 illustration is `11/2 = 5.5`, showing that this ratio itself is **highly unstable with only three more observations**. Do not tune penalties to make a model win in this exposed period, and do not use either 5.5 or 7 as a live threshold, market probability, portfolio loss function or trading action.

**Interpretation:** Accuracy-only rankings conceal asymmetric error costs. But the archive contains neither a preregistered investor utility function nor time-eligible independent false-positive crash controls. Therefore **economic preference remains UNKNOWN**, regardless of current descriptive ranking, balanced accuracy or these illustrative cost ratios.

## P3/P8, independent private provider-value-free source QA readback

Private `Donh91/secrets` EXACT main at metadata audit: `c9e16b72585d5d22442f8239f6e8432dc241ec0e`.

Authority split: private `GOVERNANCE/COLLECTION_ACTIVATION.json` Git blob `ff3a4489d22ba005a86b7902ed407d6be58e6758` says active prospective collection for SC01/SC03/SC14, while analysis/testing remain forbidden. Private `GOVERNANCE/ROUND3_SOURCE_BINDINGS.json` Git blob `444c50829f843de842033203806fbaa54656b622` retains **hourly OI, 15m funding retrieval, hourly Deribit snapshot** scientific schedules. Live private workflows since the explicit Oct19 owner budget-conservation change instead schedule **2 captures/day/source**, preserving original source cadence as a separate unmet scientific contract. This research did not change the scheduling or private permissions.

No private market values read or published. The source-time facts below use **only immutable Git pathname metadata**, never raw payload, and are safe provider-value-free health evidence.

| Closed UTC calendar day | SC01 count | SC03 count | SC14 count |
|---|---:|---:|---:|
| Nov 1 | 2 | 2 | 2 |
| Nov 2 | 1 | 1 | 1 |
| Nov 3 | 3 | 3 | 3 |
| Nov 4 | 2 | 2 | 2 |
| Nov 5 | 2 | 2 | 2 |
| Nov 6 | 2 | 2 | 2 |
| Six days total | 12 | 12 | 12 |

The shifted one/three-day distribution **must not be turned into a claim of correctly timed 2/day collection**. Its cause (Actions schedule delay, manual dispatch, queueing or another factor) is not established by file count. Use actual availability and source clocks for future analysis. The existing private health report (blob `490bd232e78f35899af61b6d14a6a0382fbe4294`) has 1193 raw/valid capture objects and no integrity failures, but **11 legacy provenance-quarantined**. It verifies payload identity and schema, **not** full cadence coverage, and has no separately exposed cadence-quality class. This follows the original [Task2 metadata-only cadence owner handoff](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596#issuecomment-6707089496) and [six-day addendum](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596#issuecomment-6707101183).

**Status:** `PRIVATE_CAPTURE_ACTIVE_SPARSE_BUDGET_MODE`, `SCIENTIFIC_EXPECTED_CADENCE_NOT_MET`, `FIRST_PUBLICATION_AND_DELIVERY_UNPROVEN`, `ROUND3_SCORING_OFF`. Private collector validation must not be promoted into a clean 1h/15m pullback effect or C02 historical PIT. Keep Oct19 critical-budget conservation until a separate reviewed and backed-up high-impact decision; no reactivation or new collector requested in this research.

## Evidence validation, authority and next scientific gate

The established original archive-first replay is `scripts/research/task2_rpl8_source_replay_v1.py`, with new descriptive loss algebra and adversarial tests `tests/research/test_task2_rpl8_source_replay_v1.py`, invoked through the EXISTING Framework Learning read-only PR validation, not a new workflow. These tests must show matched cohort, non-corrupted confusion counts, expected break-even ratios and negative controls while explicit `real_after_cost_executable_hold_sell_outcomes=false` and `optimal_policy_or_model_selected=false`.

Owner should commission/verify only *genuinely new* prospective negative event families, predeclared error costs, proven user alert-delivery and original full-position executable quote+fee+slippage utility against HOLD. Until then these are robust descriptive controls but NO predictive/economic edge. This is a research continuation, not an autonomous S1 merge, paid model call, active trade, main workflow change or source/backup policy alteration.
