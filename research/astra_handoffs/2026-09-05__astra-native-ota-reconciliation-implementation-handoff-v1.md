# ASTRA Handoff — Native OTA Reconciliation Implementation v1

**Prepared:** 2026-09-05  
**Priority:** HIGH / OPERATIONAL SIMPLIFICATION  
**Authority:** RESEARCH_ONLY / NO_CANONICAL_OR_PORTFOLIO_AUTHORITY  
**Primary design:** `research/native_ota_reconciliation/README.md`

## Mission

Finish the migration from recurring manual Claude OTA research pings to a GitHub-native OTA reconciliation workflow.

The target is **not** to clone Claude. The target is to preserve the useful OTA functions while making the current GitHub framework itself the operator and source of truth.

The desired end-state is:

> Routine Claude OTA pings are no longer necessary because GitHub Actions can natively reconcile current owner outputs, detect settled-vs-live changes, identify true source gaps, track registered gate proximity/failure, produce source QA, and summarize what changed since the previous accepted research run.

Claude/Astra may remain optional external challengers and deep-research tools.

## First instruction — inspect current main before coding

Read `research/native_ota_reconciliation/README.md` in full, then inspect current `main` and map every required function to an existing owner wherever possible.

Do **not** assume paths in older OTA reports are current.

Do **not** create a new collector until you prove a true owner gap.

Known capabilities already observed in current framework history include:

- passive pullback forensics with executed-liquidation capture;
- current option-chain/moneyness observations;
- Situation Room catalyst context;
- settled ETF calibration;
- Hourly / ETHBTC persistence evidence;
- Daily Director and conflict-review infrastructure;
- prospective evidence ledgers and learning workflows.

Astra must confirm their current contracts, paths, schedules, evidence roles and freshness semantics on current main.

## The key reconciliation problem

Recent manual Claude OTA output incorrectly treated several things as framework gaps because its own context was stale:

- it described ETF context as an 8-day bridge while the GitHub ETF owner had a newer settled session;
- it said executed liquidations were not run while native pullback forensics had already captured them;
- it treated options/moneyness as unobserved/blocked while a bounded current owner already had research observations.

The native system must make that class of error structurally difficult by using current GitHub owner evidence as higher-precedence than external/manual OTA context.

## Functional parity Astra must preserve

The native result should cover the useful parts of the OTA report:

1. run slot / predecessor lineage;
2. current settled-vs-live market state relevant to the research question;
3. registered gate status and proximity;
4. ETH/BTC / relative-leadership persistence where owned;
5. lane status and whether a lane is truly missing or already owned elsewhere;
6. source QA and freshness;
7. deterministic `what_changed` against prior accepted report;
8. early-review trigger evaluation;
9. clear separation of NEW_INFORMATION / EVIDENTIAL / CONTEXT_ONLY / BLOCKED / STALE;
10. zero canonical state, portfolio action, threshold or experiment-promotion authority.

## Suggested implementation shape

Astra may simplify after current-main inspection, but a reasonable default is:

- `scripts/research/native_ota_reconcile.py`
- `scripts/research/validate_native_ota_report.py`
- schema/contract fixture under the repository's existing contract conventions
- `.github/workflows/native-ota-research-reconciliation.yml`
- tests under the repository's established test layout
- immutable outputs under `research/native_ota_reconciliation/outputs/`
- `research/native_ota_reconciliation/LATEST_ACCEPTED.json`

Do not add a second AI market-analysis agent if Daily Director or another existing bounded owner can supply any optional narrative layer.

## Trigger design

Implement fixed Monday + Friday execution plus a bounded early-trigger path.

Prefer event-driven reuse of existing owner workflow completion over external polling.

A full early report should be materialized only when a registered condition is met. The evaluator may observe registered conditions, but may not invent thresholds.

The historical example to preserve conceptually is ETH/BTC settled gate monitoring: a live intraday breach or proximity change is not the same as a settled gate failure.

## Non-negotiable QA

Astra must lock the following with tests and runtime validation:

- a live/in-progress high can never be labelled `cycle_high` or settled maximum;
- lower-precedence external/manual context cannot overwrite fresher GitHub owner evidence;
- stale bridges remain labelled bridges/stale;
- a lane cannot be called missing when a current owner exists;
- a true missing lane cannot be fabricated;
- gate proximity is distinct from gate failure;
- early trigger requires the correct registered settled semantics;
- all authority fields remain false;
- output lineage to previous accepted native report is reproducible;
- no duplicate external calls are introduced when current owners already hold the data.

## Migration requirement

Use the latest available Claude OTA report(s) only as **comparison fixtures**.

Do not treat Claude as truth when it conflicts with current owner data.

After implementation, produce a reconciliation table/report showing for each major OTA function:

- Claude/manual behavior;
- native owner/source;
- whether parity is COMPLETE / PARTIAL / NOT_NEEDED;
- any true residual gap;
- marginal call/cost impact.

## Production proof and cutover

Astra should execute the work end-to-end as far as permissions allow:

1. create/refresh an implementation branch from current main;
2. build the smallest safe native layer;
3. add tests and fixtures;
4. run relevant local/CI checks;
5. open PR;
6. audit main drift before merge;
7. require exact-head CI success;
8. merge;
9. verify current-main readback;
10. run production-safe manual proof(s);
11. verify outputs and pointers;
12. write a migration verdict.

Do not ask the user to perform manual GitHub work.

## Final migration verdict

Astra must conclude with exactly one operational verdict:

- `CLAUDE_OTA_ROUTINE_RETIREMENT_READY`
- `CLAUDE_OTA_ROUTINE_RETIREMENT_PARTIAL_BLOCKERS`
- `CLAUDE_OTA_ROUTINE_RETIREMENT_NOT_READY`

For `READY`, demonstrate that the native workflow covers the useful routine OTA role and that any remaining Claude/Astra use is optional challenger/deep research rather than required operation.

For `PARTIAL_BLOCKERS` or `NOT_READY`, list only true current-main blockers and do not count stale external-context gaps as framework blockers.

## Guardrails

- no new market rule;
- no threshold tuning;
- no portfolio action;
- no canonical state mutation;
- no experiment promotion;
- no hindsight-labelled prospective evidence;
- no parallel market-data stack without demonstrated owner gap;
- preserve historical OTA reports as archive evidence;
- prefer deterministic reconciliation over unnecessary LLM dependence;
- minimize ongoing API cost.

## Success definition

The implementation succeeds when the framework itself can say, reproducibly and from current owner evidence:

> what changed, what is settled, what remains live, which lanes are truly available, which gaps are real, whether a registered early-review event occurred, and how the evidence differs from the previous accepted research run — without needing a recurring manual Claude OTA ping.
