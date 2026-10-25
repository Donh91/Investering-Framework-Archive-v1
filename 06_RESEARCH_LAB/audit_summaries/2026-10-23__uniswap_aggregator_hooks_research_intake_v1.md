# Uniswap Aggregator Hooks: Research Lab intake (2026-10-23)

Status: RESEARCH_ONLY, owner-approved investigation, not production evidence.
Source: https://blog.uniswap.org/aggregator-hooks-are-now-live

## A. Source
Uniswap's October 22 announcement reports external-liquidity aggregation via v4 hooks on Ethereum, Base and Robinhood Chain. Deployment addresses, exact event semantics and actual coverage are not independently verified here.

## B. Existing owners
Reuse S6 distribution-egress (#1512), S9 execution-order (#1512), Alpha Lab (#1087, #1340), Task 2 (#1530), Adaptive Evolution (#1157), Framework Learning Supervisor/Strategist and operations #1156. S6 already distinguishes router/aggregator transit from actual sells. Do not duplicate scanners.

## C. Deterministic tests pending
Freeze onchain contract ABI, deployment block and tx hashes. Compare direct swaps with aggregator routes, multi-event same-transaction swaps, router-only transfers, unknown pool, failed tx and missing trace. Measure parser misses, double counts, actor attribution and source latency. No such tests have yet been executed.

## D. Preregistered hypotheses
H1: route-aware parser improves trade capture without duplication.
H2: route-aware attribution reduces false wallet and sell classification.
H3: route-aware liquidity metrics improve decision value net of execution costs versus same-clock incumbent baseline.
Require point-in-time original receipts, negative controls, independent outcomes and false-negative costs. Round 3 remains collection-only.

## E. Mandatory owner receipt
Finding UNI-AGG-20261023-001. Evidence: SOURCE_BACKED_NOT_OUTCOME. Priority P1 research. Route first to Alpha Lab/S6, then Task 2 if a reproducible divergence survives, then Framework Learning Supervisor/Strategist for advisory synthesis, then #1156 only for governed code remediation. Record issue/PR acceptance receipt and final owner decision; an archived report alone is not acceptance. Kill if no incremental decision value or code defect.

## F. Verdict and gaps
Verdict: MODIFY_EXISTING_TEST, research only.
Completed: repository overlap audit, scope, test plan and owner routing.
Open: exact deployment/trace proof, replay, quantitative comparisons, Task 2 evaluation, owner acceptance, governed merge and production readback. No Kompas/Cycle Navigator/portfolio authority or new automation.
