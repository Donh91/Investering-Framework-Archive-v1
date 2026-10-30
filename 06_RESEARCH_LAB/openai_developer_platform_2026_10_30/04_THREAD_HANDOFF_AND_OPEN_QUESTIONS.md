# 04 · Cross-thread handoff, state machine and unanswered questions
**Created:** 2026-10-30. **Role:** persistent conversation-resumable Research Lab index; manually maintained source-linked investigation. Not an automation task, agent prompt on cron, active workflow or canonical release policy.

## Current evidence snapshot (read-only, no new API charges)
- OpenAI Agents API official: durable managed Codex-harness sessions, optional hosted Linux/shell with API model + tools + container charges; sessions can resume; **data residency US only, no ZDR support** at audit time.
- Decisions API official: generally available, gpt-6-luna only, `POST /v1/decisions` and low-cost typed classification; provider claims speed advantage, but **framework benchmark not yet executed**. Existing original pilot #1760 is owner; 60 frozen +20 heldout design present.
- Datasets official: recommended prompt/model eval UI; old Evals read-only after 2026-10-31 and scheduled 2026-11-30 retirement.
- Prompt caching: reuse stable >=1024-token context with 30m/12h charge differences; Batch: 50% pricing on supported async 24h jobs.
- Current framework operations files (see root README) already have model and estimated spending receipts; **provider-billing consistency has not been established**. Internal total may have a different project/filter/time/rate scope than individual screenshots.
- Only screenshots, not live connection: user shows OpenAI Platform organization spending, prepaid credit and card auto-recharge. Nothing in this archive changes actual settings.
- Conditional ChatGPT Pro grant: Pro100/200/500 may offer corresponding $100/$200/$500 monthly API credits after eligibility/linking; **not confirmed for the current user or API organization**. Usage tier "Build" is unrelated.
- User's text "30%" vs screenshot "$30" ambiguous. Working spend envelope **USD 30**, not percentage; no payment changes permitted.

## READ THIS FIRST in a future thread
1. Root `Donh91/Investering-Framework-Archive-v1/AGENTS.md`; `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`; `00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json`.
2. Whether this research documentation PR was actually merged. Use merged main latest or exact unmerged head, not a guessed stale file path.
3. `06_RESEARCH_LAB/openai_developer_platform_2026_10_30/README.md` then `01_OFFICIAL_CAPABILITIES_AND_FIT.md`, `02_BUDGET_AND_CREDITS.md`, `03_IMPLEMENTATION_AND_EVALUATION_ROADMAP.md` and `05_SOURCE_AND_CLAIM_REGISTER.json`.
4. Actual `LATEST_OPERATIONS_DASHBOARD.json`, `LATEST_HANDOFF.json`, `research/architecture_health/LATEST_AUTOMATION_HEALTH.json`, `research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json`, `LATEST_REMEDIATION_QUEUE.json`, `LATEST_CODEX_READY_TASKS.json`, `LATEST_CODEX_EXECUTION_STATE.json`.
5. Existing original issue #1156 (Supervisor), #1760 (Decisions), #1596 (Task2), #1512 (Research Lab) and external specialist queue plus exact current PRs. Read Grok Bridge #93 for Birdeye separately - do not merge it here.
6. Official OpenAI Help Center/Developer Docs current prices, grants, migration dates, model availability and rights (sources in register).
7. Only after 1-6: choose **one** bounded measurable mission; stop on missing original source, account authorization or payment risk.

## Immediate resume instruction - copy into a new ChatGPT thread
> Continue the approved OpenAI Developer Platform deep-research program from the current GitHub archive `Donh91/Investering-Framework-Archive-v1/06_RESEARCH_LAB/openai_developer_platform_2026_10_30/`. First check whether the original documentation PR has merged; read the exact latest README/roadmap/source register and current canonical AGENTS/operational cockpit. Fresh-audit existing #1156, #1760 and #1596 before any work. Do the R0 no-spend accounting and execution-lineage audit first. Precisely distinguish (a) actual OpenAI API billing per org/project and prepaid reload (private UI only), (b) framework estimated API receipts, (c) conditional subscription credit grants, (d) project and org hard limits. Do not ask me to repeat prior framework mandates and do not request API key in chat. Keep card auto-reload monthly ceiling and org spending limit unchanged. Use current source citations, actual GitHub diffs/tests and after-merge readback; don't create a duplicate Supervisor, new automation or broad PR queue. If the R0 audit finds a reproducible code defect, route through existing Codex intake with exact unit tests. After R0 evaluate current Decisions #1760 with public/sanitized offline examples, and only then a single sandboxed Agents API coding test if it adds measurable closed-work value within the preapproved budget and security constraints. Maintain Task 2 immutable original clocks and private data boundary. Update only the existing research archive with evidenced deltas and produce a concise owner-facing checkpoint and next verified step.

## Work that is **already done** by this research archive, not by underlying runtime
- Official current source audit / feature comparison: COMPLETED_DOC_ONLY.
- Existing GitHub owners and overlap: COMPLETED_DOC_ONLY.
- Conditional economic scenarios and example token arithmetic: COMPLETED_DOC_ONLY; estimated, not live provider measurement.
- R0 provider cost/usage reconciliation: **NOT_RUN**.
- Any API calls, actual grants, key creation, charge or subscription change: **NOT_RUN**.
- Decisions actual 60+20 local/model benchmark: **NOT_RUN**.
- Agents API hosted-session pilot, separate public sandbox: **NOT_RUN**.
- GitHub production code changes and releases: **NOT_RUN**.
- Runtime observation and actual improvement in PR closure: **NOT_PROVEN**.

## The next 10 precise research questions, in priority order
1. Does the user actually have eligible Pro100/200/500 currently, or Plus? Verify only via authorized ChatGPT Billing, not memory, API usage tier or social post.
2. If Pro active, is the exact linked API organization credited? What grant amount, period and expiry are shown? Does a $30 org spending limit throttle consuming a larger promotional grant? Do not increase limits without owner's separate explicit approval.
3. How many of the last 30d API expenses are actually billed to this API organization versus estimated GitHub receipts with different scope? Are there duplicate retry receipts or missing tool costs?
4. For three actual original issue IDs, what proportion of paid agent activity has original code→verified CI→merge→natural data readback? What is cost per **genuinely closed** task?
5. Does current owner already emit needed completion/cost identifiers? Can a tiny deterministic patch close the gap before buying a cloud Agents session?
6. Can typed Decisions beat the existing deterministic + Luna Responses baseline on the existing sealed #1760 public trial including unknown and prompt injection?
7. Would one hosted Agents session (US-only, non-ZDR) violate privacy/terms for any contemplated source? If yes use synthetic/public or fail closed.
8. Is an original PR fix truly too heavy for the existing owner, or can Sol/Terra improve it without a new agent endpoint?
9. Is dataset upload of evaluated examples safe under the 3-plane source governance? Which examples remain synthetic-only?
10. Should any tools/Batches/caching be enabled after verifying **actual end-to-end savings** rather than cheaper unit rates?

## Owner controls to preserve
`NEW_SUBSCRIPTION=false`; `NEW_API_KEY=false`; `INCREASE_ORG_SPEND_LIMIT=false`; `CHANGE_PREPAID_AUTO_RELOAD=false`; `NEW_SUPERVISOR=false`; `NEW_SCHEDULER=false`; `TRADE=false`; `PROMOTE_MARKET_MODEL=false`; `ACCESS_PRIVATE_PLANE_WITHOUT_AUTH=false`; `BYPASS_GITHUB_PROTECTION=false`. The documentation-only branch/PR may be merged only after actual repo protections, CI and release requirements.

## Handoff update rule
After a future readback, append a dated checkpoint at the end of this file or a separate YYYY-MM-DD progress note within this same folder:
`date_utc | github_main_sha | platform_doc_changed | original_owner | input_source_hashes | action_done | tests/CI | real_spend_usd | actual PR/merge/readback | evidence_state | next single step`.
Never rewrite frozen initial hypotheses after seeing economic outcomes.
