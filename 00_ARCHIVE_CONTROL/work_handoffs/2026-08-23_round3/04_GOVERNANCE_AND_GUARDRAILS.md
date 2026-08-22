# Governance and guardrails

## Non-negotiable research boundaries
- Historical research is RESEARCH_ONLY.
- No automatic portfolio execution authority.
- No automatic market-rule, threshold, weight or policy-semantic changes.
- Maximum historical classification: `FORWARD_TEST`.
- Promotion requires separate review and, where appropriate, prospective evidence.
- Claude/Cowork may READ GitHub but must not WRITE to GitHub.
- No paid API/CFGI calls unless explicitly authorized in a bounded contract.
- MARKET CFGI historical unavailable slices must remain NOT_TESTABLE; no proxy, interpolation or synthetic fill.

## Method constraints inherited from Round 1/2
1. Independent market episodes, not hourly rows/assets, are the default inferential unit.
2. No candidate may be promoted because a threshold holds for N adjacent hours without dependence-preserving calibration.
3. Persistence/run statistics require a null that preserves the full family/search process, ideally event-label permutation.
4. Report observed max statistic, null median, null p95 or stronger, family-wise p, and overlap/autocorrelation implications.
5. Separate a predeclared actionable window from broad descriptive pre-event windows.
6. Post-top discrimination is confirmation/descriptive information, not precursor edge.
7. Search width must be declared before running. Broad discovery requires full family-wise correction and may not be described as confirmatory post hoc.
8. HOLD remains mandatory benchmark for trim/reload work. Report opportunity cost, duty cycle, execution-delay sensitivity and friction alongside hit rate.

## Episode definitions
Frozen V0 remains the historical definition for Round 1/2 results.

Future candidate only:
`V2_RESEARCH_LABEL_CANDIDATE`
- preserve existing drawdown trigger semantics;
- close episode when 0.75 recovery occurs OR 336 hours have elapsed, whichever happens first;
- rebuild episodes/controls/anchors from scratch;
- use a fresh multiplicity budget;
- do not rescore old candidates and choose whichever label produces stronger signals.

Status: `RESEARCH_LABEL_CANDIDATE_ONLY`.
Purpose: improve testability/era balance, not prove edge.

## Research-lane status
Closed for broad re-mining:
- price transforms
- volume transforms
- taker-share transforms
- broad cross-sectional/cohort mining of the same tape

May only be reopened if a separately preregistered narrow hypothesis identifies one/few exact cells before outcomes are inspected.

Priority new information dimensions:
- open interest and OI changes/acceleration/deleveraging
- funding
- futures basis / term structure
- order-book depth, imbalance and liquidity withdrawal
- liquidations where historically sourceable
- stablecoin exchange inflows/outflows
- exchange reserves/flows where scientifically defensible
- cross-venue positioning/divergence
- spot-vs-derivatives divergence
- venue-specific positioning/flow divergence

## Product-level objective boundary
These research decisions do not replace the broader Investering framework. Master Monday, Cycle Navigator, altseason/rotation warning, and distribution/exit protection remain high-level objectives. Research is meant to improve falsifiability and timing quality without silently mutating those objectives.