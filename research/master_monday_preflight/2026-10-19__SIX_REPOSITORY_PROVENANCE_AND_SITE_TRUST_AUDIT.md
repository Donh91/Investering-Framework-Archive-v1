# Six-repository provenance, Master Monday, Compass and SITE trust audit — 2026-10-19

Status: **BOUNDED CODE AUDIT + ISOLATED FIXES IN PR #1683; NOT MERGED / NOT PRODUCTION VERIFIED**.
Audit snapshot: main `f331e2769d25d295986241072cc642d3857aafdf`; subsequent PR head must be checked separately. Public-safe metadata only. Owner declined a proposed new "Frozen weekly forecast vs actual market" illustration: **do not add it**; existing governed charts remain untouched.

## Coverage / limitations
Accessible GitHub repositories: **6**. Root metadata, AGENTS/README, archive routing, cross-repo boundaries, current production pointers, relevant source scripts, CI, workflows and overlapping PRs were inspected. Main and Experiment Execution Plane recursive GitHub trees are **truncated** at 50,309 and 62,772 entries; therefore this is **NOT an exhaustive audit of every archive file, private dataset or historical commit**. No private raw payload or credential was read or copied into this public audit. No browser-based iPhone production QA or deployed Pages same-origin readback was performed.

| Repository | Main SHA at audit | Role / finding |
|---|---|---|
| `Donh91/Investering-Framework-Archive-v1` | `f331e2769d25d295986241072cc642d3857aafdf` | PUBLIC canonical/control, Master Monday, Official Compass/CN/SITE. Relevant source and code audited. |
| `Donh91/Eksperimenter-framework-` | `60ae47a5ae5167bcb91e807be0fe09d0498e22e4` | PUBLIC noncanonical prospective experiment execution, independent request/receipt replication. No direct SITE action authority. |
| `Donh91/secrets` | `c216f94c3f90a06febab7067182d3125177d6b8d` | PRIVATE restricted data plane. Metadata/AGENTS/README only; no private provider values in this PR or proposed API packet. |
| `Donh91/Meme-Alpha-Lab` | `7bb5c7cb6ab099065d8042ff88cee62a1872c43e` | PRIVATE independent alpha research; not automatic CN/Kompas action authority. |
| `Donh91/Investering-AI-Audit-Bridge` | `9334fa42042e7578f041ce09e365f5dcb1454128` | PRIVATE AI-to-AI review bridge; advisory evidence not automatic merge or forecast authority. |
| `Donh91/CycleNavigator-scores` | `c67a4832267f63e5a1f44e6cd5ae3e4c6899ac58` | PUBLIC independent proof/mirror design. `PROTOCOL.md` says DESIGN_ONLY / NOT DEPLOYED; historical legacy mirror lacks independent ex-ante proof. Never call these VERIFIED solely because mirrored. |

Archive routing anchors reviewed: `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`, `INDEX_ADDENDUM_REGISTRY.md`, `ARCHIVE_MAP_AND_ROUTING.md`, `CROSS_REPO_DATA_BOUNDARY.md`, `CROSS_REPO_AGENT_CONTEXT_MAP.json`, `CURRENT_PRODUCTION_DATA_AUTHORITY.json`, `00_FMOS/AUTOMATION_ORCHESTRATION_ARCHITECTURE_v2.md`, `AGENTS.md`, global Kompas route. Legacy `canonical-project-archive/` is read-only context, not current authority; manual DATA PING is not a required current upstream.

## Verified operational baseline
- `research/api_agent/outputs/weekly/2026/W42/MASTER_MONDAY_DELIVERY_POINTER.json`: preflight FULL_MASTER_MONDAY_INPUT; producer READY; consumer VERIFIED/PASS; scorecard and operational translation `UNAVAILABLE_API_CONTRACT`; learning impact `NOT_EVALUABLE_NOVEL_INPUT_NOT_CONSUMED`.
- `05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json`: W43 forecast, completed W42, public issue #30, CN delivery DEGRADED/COVERAGE_LIMITATION; X ready not confirmed published.
- `05_CYCLE_NAVIGATOR/weekly/2026/W43/CYCLE_NAVIGATOR_FORECAST_FREEZE.json`: day-by-day expected-close profiles UNAVAILABLE. This is an honest abstention, not permission to synthesize a line or ETA.
- `04_MARKET_LEARNING/handlekompas/official/LATEST_COMPASS.json` and `PUBLIC_LATEST_COMPASS.json`: exact matching compass_id `CMP-20261019-8ca1978b5bd2`, issued 11:06:58Z; currentness must be rechecked at each future invocation.
- `LATEST_OPERATIONS_DASHBOARD.json`: AMBER overall; 22 open incidents, 5 AMBER automations at observed snapshot; API receipt-estimated October spend $12.322115; not equivalent to provider invoice.
- Current `05_CYCLE_NAVIGATOR/site/SITE_CONTRACT.md` already separates weekly CN, live Official Compass, shadow and private values. `build-public.mjs` produces public-safe projections and full-stack readback; the premium NOW renderer is the effective action view.
- `05_CYCLE_NAVIGATOR/site/market-compass-premium.js` maps DE_RISK/PROTECT/EXIT to PROTECT CAPITAL; older `compass-product-v5.js` HOLD mapping is a **legacy/non-effective renderer concern**, not verified as an active mislabel. SELL is a separate typed assessment owned by `COMPASS_SELL_ASSESSMENT_v1`.

## Proven defect repaired in PR #1683 (unmerged)
`05_CYCLE_NAVIGATOR/site/build-public.mjs` verified the hash of the Master Monday delivery POINTER but marked `full_stack.source_status.master_monday=SOURCE_ALIGNED` **without reading/verifying the pointed-to machine package**. This can overstate completeness when the machine target is missing or changed.

**Fix:** verify allowed path, exact machine contract, ISO year/week and canonical `package_sha256` self-digest with existing `verifiedRawDigest`; do not incorrectly compare raw JSON SHA to a canonical self-digest. Failing checks become UNVERIFIED while other valid Compass lanes remain available. No market logic changed.

**Tests:** extended `05_CYCLE_NAVIGATOR/site/tests/full-stack-readback.test.mjs` with valid, missing, tampered, wrong-digest, wrong-week, not-ready and escaped-path cases. Site Product Gate ran successfully on commit `9aa322dd7ac893933a5e0055a839c94a71223bec` (run 39254676066).

## Derived weekly machine audit implementation in PR #1683 (unmerged)
- `scripts/master_monday/publish_master_monday_outputs.py` now writes `MASTER_MONDAY_WEEKLY_INTELLIGENCE_AUDIT_<machine_self_digest_prefix>.md` in the **existing** weekly output directory, after the existing consumer receipt and delivery pointer.
- One metadata-only JSON fenced section: exact completed ISO week, freeze/preflight/context self-digests, machine self-digest vs file-byte digest (explicitly distinct), pointer byte digest, API/model/cost-estimate status, analytical completeness, learning impact and truthful `PENDING_DOWNSTREAM_OWNER` for CN/SITE.
- New machine digest → new filename; same digest with different bytes is a hard collision. No extra `LATEST`, cron, queue, model call, score, portfolio action, source promotion, retrospective backfill or private values.
- Existing `.github/workflows/weekly-api-calibration-shadow.yml` publish readback manifest includes this sidecar; existing GitHub Actions writer remains sole durable publisher.
- Added positive/negative tests to `tests/master_monday/test_durable_repairs.py`: deterministic metadata, no private payload, API failure honesty, wrong week, digest mismatch and invalid file hash.
- Master Monday Preflight Gate successful on `9aa322dd7ac893933a5e0055a839c94a71223bec` (run 39254676075).
- **NOT YET VERIFIED:** first natural post-merge Monday production, actual generated sidecar, exact remote readback and next-week CN/SITE correlation. CI is not production.

## Unresolved work — do not hide
1. **P0 analytical completeness:** `WEEKLY_CALIBRATION_SHADOW` API schema does not currently provide `scorecard` or `operational_translation`. Publisher's typed fallback is honest, but upstream contract/prompt/schema/eligibility must be reviewed. Matured count cannot be presented as scored/admitted skill. No fabricated values.
2. **P1 SITE weekly content contract:** site full-stack currently verifies Master Monday delivery **pointer**, not a complete typed, public-safe weekly analytical summary. Existing CN package carries governed weekly synthesis, but user-requested direct Monday-to-SITE consumption still needs owner-approved allowlisted fields, exact week/horizon semantics and tests. Coordinate with active SITE PR #1680; do not fork the frontend or leak private data.
3. **P1 phase/ETA:** W43 canonical phase is UNAVAILABLE; cannot classify as missing source versus insufficient evidence without tracing the exact accepted phase-gate owner. No synthetic phase/ETA.
4. **P1 science/proof:** CycleNavigator-scores proof protocol remains design-only; public historical mirrors do not independently establish ex-ante timestamps. Task 4 confirmatory skill must remain UNPROVEN until exact accepted inference.
5. **P1 complete Compass parity:** a full chat source cross-read can be fresher than a deployed static SITE snapshot. Parity is conditional on identical source identities/as-of times; prove normalized decision agreement, including separate SELL/protection/re-entry, all tiers and horizons. Existing tests cover parts, not an exhaustive live cross-client run.
6. **P1 SITE production QA:** iPhone Safari 390px, DA/EN, current deployed Pages asset hash/readback and natural Monday→hourly refresh continuity still require verified production observation. No assertion of deployed success.
7. **P2 cross-repo audit coverage:** truncated large archive trees and restricted raw source audit require staged exact-scope sampling by each domain owner; no blanket "all archives passed" conclusion.

## API review routing — avoid wasted money
Official API docs confirm `gpt-6.1-sol` is available via Responses API, but this does **not** establish availability in the current repo gateway or authorization for a new task. Existing `TEMP_SOL_PR_REVIEW` route is date-gated through **2026-10-17** and cannot legitimately run on 2026-10-19. Existing `SENIOR_REPAIR_AUDIT` is a fixed-context GPT-6 Sol audit of older PR #1348–#1357 and would **not** review this PR. `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` has another owner/scope. Do not trigger any of these under a false premise.

Owner requests a separate **adversarial Sol API review** of this exact PR head and the six-repository architecture, via an **existing authorized gateway and Supervisor owner**, with explicit source inventory, scope-bounded private metadata, cost reservation and a durable receipt. Until an appropriate existing route is verified, status is `SOL_REVIEW_REQUESTED_NOT_EXECUTED`, not PASS.

## Required release gates
- Verify fresh main, PR #1680 overlap, exact PR head and changed-file diff.
- Require current-site and Master Monday CI, tests sensitive to removed guards, no privacy leak, no accidental change to production owners.
- Technical Sol/independent review advisory only; existing governance and owner authorization govern merge. No bypass or fake GitHub approval.
- After merge, verify exact main blob and the next natural weekly output, source hash, machine audit file, remote readback, CN binding and SITE public output. Only then claim production DONE.
