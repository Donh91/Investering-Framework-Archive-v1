# SOL 6.1 API — WEEKLY INTELLIGENCE → COMPASS → CN → SITE END-TO-END MISSION
Date: 2026-10-19
Status: OWNER-REQUESTED IMPLEMENTATION MISSION / NOT YET EXECUTED BY API
Repository: Donh91/Investering-Framework-Archive-v1
Related review: PR #1683
Priority: P0 provenance and coherent Monday-to-next-week publication; P1 operational completeness; P2 longitudinal learning
Mode: use existing GitHub Actions/API lanes and current owners only; no Work credits, no new supervisor, queue, cron, writer, model router, secret store or canonical state.

## Mission outcome
Make the Monday weekly freeze, final Master Monday, current Official Compass, Cycle Navigator's next-week forecast and public SITE operate as one **verified, time-aware, provenance-bound system**. Keep distinct: (a) settled completed-week outcomes, (b) next-week frozen forecasts, (c) hourly fresh Compass live actions, (d) contextual/shadow research, (e) X/public projection. Every displayed fact must identify its owner, effective week/horizon, freshness, exact immutable source hash, and eligibility. Site must load next week's Monday-produced context plus latest valid Compass without treating either as a substitute for the other.

**Do not** assert this mission has run, that Sol 6.1 is enabled, or that any code has shipped merely because this file exists.

## Current-main sources — read afresh, in canonical order
1. `AGENTS.md`, `LATEST_OPERATIONS_DASHBOARD.json`, `LATEST_HANDOFF.json`, `research/architecture_health/LATEST_AUTOMATION_HEALTH.json`, `research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json`, `LATEST_REMEDIATION_QUEUE.json`, `LATEST_CODEX_READY_TASKS.json`, `LATEST_CODEX_EXECUTION_STATE.json`.
2. `00_FMOS/AUTOMATION_ORCHESTRATION_ARCHITECTURE_v2.md`, `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`, `00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json`, `00_ARCHIVE_CONTROL/CURRENT_PRODUCTION_DATA_AUTHORITY.json`.
3. `03_DAILY_CAPTURE_LOGS/README.md`, Daily Capture v2.2 owner, exact W42 weekly close/final catch-up/calibration/enriched sequence/ETF and `research/master_monday_preflight/frozen/2026/W42/WEEKLY_EVIDENCE_FREEZE.json`.
4. `research/api_agent/outputs/weekly/2026/W42/MASTER_MONDAY_MACHINE_PACKAGE.json`, `MASTER_MONDAY_REPORT.md`, `MASTER_MONDAY_DELIVERY_POINTER.json`, `MASTER_MONDAY_CALIBRATION_SCORECARD.json`, operational translation, API receipt and existing publisher `scripts/master_monday/publish_master_monday_outputs.py`.
5. `05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json`, `05_CYCLE_NAVIGATOR/weekly/2026/W43/CYCLE_NAVIGATOR_FORECAST_FREEZE.json`, `CYCLE_NAVIGATOR_PUBLIC_SERIES_BINDING.json`, `CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json`, CN machine package and `05_CYCLE_NAVIGATOR/public_series/CN_PUBLIC_SERIES_INDEX.json`.
6. `04_MARKET_LEARNING/handlekompas/official/LATEST_COMPASS.json`, `04_MARKET_LEARNING/handlekompas/official/PUBLIC_LATEST_COMPASS.json`, official immutable Compass target, native Handlekompas, strategic Compass (only eligible horizons), and accepted protection/sell/re-entry source owners.
7. `05_CYCLE_NAVIGATOR/site/SITE_CONTRACT.md`, `05_CYCLE_NAVIGATOR/site/build-public.mjs`, site client rendering/validators, current Pages deploy workflow and existing tests.
8. `research/api_agent/API_INTELLIGENCE_POLICY_v2.json`, current API gateway/model allowlist and receipts. Verify current availability and pricing for Sol 6.1 in the **actual approved gateway** before any call. Never assume model string availability.
9. Current Task 4 preregistration, study-admission and exact frozen outcome contracts; do not infer forecast skill from public interval coverage.

## Already verified facts (revalidate before changing code)
- W42 Master Monday producer READY and consumer VERIFIED/PASS, yet `scorecard` and `operational_translation` show `UNAVAILABLE_API_CONTRACT`. The publisher has explicit fallbacks. Trace the **upstream producer/validator** before altering output semantics.
- Site contract already makes CN pointer and immutable machine package the weekly authority; the site builder reads `LATEST_CYCLE_NAVIGATOR_POINTER.json`, Official Compass public/internal pointers, `LATEST_HANDOFF.json`, range/public series pointers and several shadow/context feeds.
- SITE_CONTRACT rule 26: if Official Compass unavailable or Compass→weekly alignment not ALIGNED, live PATH overlays fail closed. Rule 24 forbids synthesized countdown. Rule 23 requires distribution/sell/reentry typed owners. Rule 8 requires public issue number from public-series projection, not internal machine issue.
- Site builder's `sanitizePackage` selects explicit fields; weekly Master Monday information may be absent even when source exists. Identify exactly which useful **public-safe** Monday fields are missing, and why, before expanding the whitelist.
- W43 binding shows public CN issue #30, internal machine #31, `X_READY_NOT_CONFIRMED_PUBLISHED`; never display internal issue as public #31.
- W43 phase `UNAVAILABLE` may be a legitimate unsupported conclusion; test missing owner/edge vs insufficient accepted evidence. Never manufacture phase, ETA or 4–8-week direction.
- API policy `API_INTELLIGENCE_POLICY_v2` has a $40 monthly hard stop and $4 global reserve, with existing task lane caps. Do not change caps, schedule, task names, or budgets. `SENIOR_REPAIR_AUDIT` is owner-gated, max 4/week, automatic code write/merge false.

## Deliverables — execute in the existing governed code path

### D0. Frozen contract and failure matrix BEFORE coding
Identify exact producer/consumer paths, trigger graph, canonical owner per field, source hashes, schema versions, readback and release rules. Record known-good example and one reproducible broken example per issue. Map observed symptoms separately from suspected root causes. Identify overlapping open PRs/issues and avoid duplicate changes. Scope one PR per independently testable causal defect; avoid a giant unsafe PR.

### D1. Master Monday API analytical completeness — P0
- Locate prompt/request payload, gateway, response schema, parser, validation and publisher for `WEEKLY_CALIBRATION_SHADOW`.
- Fix scorecard and operational translation *only* if their semantics are defined and source-supported by the current owner. If they are intentionally not in the contract, revise report semantics to distinguish `NOT_REQUESTED` from `UNAVAILABLE_API_CONTRACT` and do not fabricate completeness.
- Matured registry count is not scored/admitted count. Use exact Task 4 state and frozen outcome identity. No new inferential claim, market threshold, or trade command.
- Add positive/negative regression tests for API success with missing/malformed fields, partial API failure, stale/mismatched week/hash, duplicate receipts, source conflict, censored/pending outcomes, and public-safe serialization.
- Consumer `PASS` must remain independent from analytical completeness; expose both states.

### D2. Monday → next-week CN and SITE public contract — P0
- Define or extend the **existing** CN-owned, privacy-safe weekly public projection; do not create another canonical feed. Include source-bound Monday weekly close, three material changes, calibrated risk posture, previous-week verified range score if eligible, W43 frozen forecast envelopes/horizons, current phase/next gate/ETA status, weekly rotation context, and provenance + freshness + missingness. Include `public_issue_number` from public-series authority.
- Site reads existing public projection + Official Compass public projection. Bind forecast week and completed week explicitly; reject mismatched week, wrong issue, stale/future timestamps, SHA mismatch, unknown contract, invalid public field, path traversal, and private/restricted values.
- **Two clocks:** Monday weekly baseline is frozen; Compass is a faster refreshed live overlay. A new hourly Compass must not rewrite the Monday freeze or historical forecast; a new Monday baseline must not overwrite fresh Official Compass decisions.
- Explicit UI conflict: weekly forecast MIXED while live Compass HOLD/WAIT/SELL must show both horizons with distinct labels, not collapse into one false status.
- Build and validate public snapshot with existing `build-public.mjs` / current Pages workflow and existing release/readback gates. No browser-side model inference.
- Render compact Market Cycle current checkpoint, NEXT GATE, typed confirmed/missing gates, conditional ETA only if owner-supported; THIS WEEK'S ROTATION from typed Compass capitalization ladder. No duplicated ladders, no forced phase promotion.
- Ensure DA/EN labels, 390px iPhone view, accessibility, status/age badges, and no fake live feed. Preserve SITE_CONTRACT and established UI hierarchy.
- X/public text must omit private shadow internals, unratified experiments and technical remediation details. The weekly report may contain a separate internal section not exported to SITE/X.

### D3. Canonical phase/ETA diagnostic — P1
- Trace canonical phase owner and accepted gates (ETH/BTC, BTC.D, TOTAL2/TOTAL3, breadth, CFGI, flows, leverage/funding, macro/liquidity, price/regime) and their freshness/independence.
- Distinguish `MISSING_SOURCE`, `STALE`, `CONFLICT`, `INSUFFICIENT_EVIDENCE`, `NO_CANONICAL_OWNER`, `NOT_ESTIMABLE`, `VALID`.
- The public board should have exactly one current phase **only when canonical**; otherwise explicit `UNAVAILABLE` with explanation and next gate. Advance warning never becomes phase promotion. ETA is null unless evidence supports a bounded watch window.
- Avoid correlated-signal double counting, shadow promotion, retroactive market-phase labels and inferred timelines.

### D4. Machine-only weekly longitudinal audit — P1
- Integrate a compact `Wxx_WEEKLY_INTELLIGENCE_AUDIT.md` as a deterministic **derived sidecar** of the existing Master Monday writer, only after owner contract approval. Append-only per ISO week; immutable hash-bound source references; exact readback; no new LATEST pointer or duplicate writer.
- Minimum sections: producer graph and source SHA; freeze/calibration/API/consumer status; field-by-field provenance/freshness/typed missingness; weekly vs live Compass alignment; CN public identity; forecast-vs-matured outcome only when eligible; calibration deltas; accepted vs shadow learning; known open defects with existing owner/next gate; code SHA/schema/model ID; budget receipts; site publication/readback status.
- Never log private payloads, credentials, normalized restricted provider values or unverifiable claims. Preserve an explicit `NOT_EVALUABLE` when a novel learning packet was not consumed. Do not rewrite prior weeks.
- Distinguish delivery success, completeness, scientific admission and forecast skill. Machine-readable fenced YAML/JSON section may be included only as a derivative of existing receipts, not an authority registry.

### D5. End-to-end integration tests and operational QA — P0
Positive chain: W42 final settled inputs → freeze/readback → API receipt/validated fields → machine package → CN W43 freeze → official Compass public binding → SITE public projection → Pages build → public readback; confirm Monday baseline stays frozen after hourly refresh.
Negative/mutation tests:
1. Missing/mismatched W42 SHA, altered freeze bytes, wrong ISO week.
2. Stale/missing official Compass, hash mismatch, wrong compass_id, weekly alignment not ALIGNED.
3. W43 public #30 vs machine #31 identity confusion.
4. Missing API scorecard/translation, API failure, duplicate/late receipt.
5. Shadow-only data trying to promote a phase or public score.
6. Unsupported ETA, absent daily close path, null range becoming fabricated number.
7. Restricted value or private path leaking into public JSON/HTML.
8. Pending/censored/unscored outcome presented as accuracy or forecast skill.
9. Monday baseline overwritten by live prices; stale live overlay labeled LIVE.
10. Missing SITE field silently replaced by old embedded fallback without warning.
11. Replay across year/ISO-week rollover, partial publication, concurrent writer.
12. Correlated gates double-counted; distribution context converted to unauthorized SELL.
Prove critical guard tests are mutation-sensitive. Run relevant Python, Node, site and workflow tests; capture actual commands/results. Do not assert tests passed if not run.

### D6. Governed delivery and post-merge observation
- Implement bounded PRs in existing domain scopes, run CI, inspect exact SHA/diff and current rules, obtain real required review/owner release authorization. Never self-approve, bypass branch protection, or fake an independent review.
- No automatic merge under an API analysis receipt alone. Sol 6.1 may analyze and draft code only through a separately authorized existing executor; current API policy says `automatic_code_write=false`, `automatic_merge=false` for `SENIOR_REPAIR_AUDIT`.
- On merge, verify exact main blobs and wait for the next **natural** weekly production run; verify weekly artifact, site build, public hash/readback, Compass alignment and public issue identity. Do not manufacture an artificial success receipt.
- Supervisor gets a concise actionable handoff via **existing** remediation/Codex intake, not a new queue. Avoid expensive Work runs.

## Model and budget routing
Use current approved gateway and its verified model allowlist. If `Sol 6.1` exists and is approved for this task/lane, choose it for bounded root-cause synthesis and adversarial design. If not, select an existing approved cost-efficient model or return `MODEL_UNAVAILABLE` with evidence. Use deterministic local grep/tests for code search; reserve paid reasoning for architecture decisions and nontrivial adversarial review. Cache static source hashes and dedupe prompts. No new paid service, model router or budget. Stop when the existing task cap/global reserve would be breached.

## Completion criteria
- Weekly Monday report remains correct under API partial failure.
- Missing analytical fields have either validated source-backed content or precise typed failure semantics.
- SITE reliably consumes next-week frozen CN + Monday public-safe summary + freshest eligible Official Compass, without authority crossover.
- Internal machine audit is produced by existing writer, provenance-valid, readback-verified, and longitudinally comparable.
- Existing CI and negative tests pass; first natural post-merge production output verified.
- No market/portfolio authority change, private leak, synthetic ETA, historical rewrite, duplicate scheduler, new queue, or unapproved cost.
- Final handoff must state DONE vs PARTIAL vs BLOCKED per deliverable with exact commit, PR, CI, hashes, API receipts, budget and remaining gates.

## Initial API execution prompt (copy into existing approved owner-gated lane)
Read `research/master_monday_preflight/2026-10-19__SOL_6_1_WEEKLY_INTELLIGENCE_SITE_COMPASS_EXECUTION_MISSION.md` on PR #1683 head, plus current main governance and sources. Perform D0 and D1/D2 root-cause analysis first, then produce bounded code diffs/tests through an authorized existing executor. Do not use Work, create new automation, raise budget, auto-merge, or alter canonical market rules. Return a structured verified execution receipt and scoped follow-up for existing Supervisor.
