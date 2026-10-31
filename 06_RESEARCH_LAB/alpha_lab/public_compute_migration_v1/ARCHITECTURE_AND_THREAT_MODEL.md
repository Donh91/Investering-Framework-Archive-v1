# Alpha Public Compute Migration v1.0 | Architecture and threat model

Status: **OWNER-APPROVED DESIGN / PR-ONLY / NO RUNTIME DEPLOYMENT / GROK ADVERSARIAL REVIEW PENDING**  
Authority: existing Alpha source owner [Meme-Alpha-Lab #120](https://github.com/Donh91/Meme-Alpha-Lab/issues/120), research owner #22, scientific owner #77, source/safety owner #98/#194, existing sole framework Supervisor [Archive #1156](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156), existing Strategist #1157.  
Date: 2026-10-31. Audience: architecture, security, source reliability and Grok independent review.  
Source pins at design freeze: Archive main `b8c88dc1118fe99cee6594f9d7d31a681c4ddd1a`; Alpha main `51d887c81227bb7ff5e963e02f97bafcaede02e4`, Pons cursor blob `ea8d0b84395b537fb024934c3dbadd8b4b3a8bd9`, census workflow blob `5abed86ae211d3eda8b1ec37c675cc60f3758a84`. Recheck original heads before any implementation.

## Grok #118 independent review disposition | 31 Oct 2026, exact original design HEAD `ba1c22a03901ab60f5a0ed5babcaf40c0507c28b`

**ADOPT_WITH_BOUNDARIES / SECURITY_AND_IP_REVISED.** Independent [Bridge #118](https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/118) reviewed the original draft and recommended the above-isolated design with tighter public input scope, no worker self-admission, explicit dual cursors and narrower budget claims. The revised HEAD requires separate delta-review. Grok's local *guard prototype* tested one positive and five negative fixtures, but its actual fork/permission, schema-specific negative tests, real runner, private import and source terms remain **NOT_RUN**. No real public compute repo has been created.

**Critical correction after owner-source readback:** Grok #118 §2 F2 and §7 treated the `Donh91/Eksperimenter-framework-` execution-plane 5×/day as private-minute savings potential. This is **REFUTED**: GitHub's actual `get_repo` reports visibility `public`; `.github/workflows/experiment-execution-plane.yml` is in that already PUBLIC repo, blob `831a9d4b849478c35f2d1ed4910ecc621e2b3665`, cron `15 0,6,11,15,19 * * *`, standard `ubuntu-latest`. Hence the suggested ~1,100-1,400 'private' minutes/month saved by moving or reducing this job are **0** under current standard-public-runner pricing. It may be rational to optimize *science/IO/cost of RPC* separately, but it is **not** a reclaimable private Actions billing pool. No claim that the user's total private cost falls 1,500-3,500 minutes from this proposal is supported without Billing readback. Likewise public Archive's existing jobs already consume zero included private minutes on standard runners.

**Actual owner decision:** A dedicated compute-only public repo is the default required W1 execution venue; public Archive is the policy/control plane, not a fallback compute venue unless a separately demonstrated protection review overrides this decision. A source gate must publish an **exhaustive, outcome-independent, explicitly approved** public universe, not a subset of private target CAs or privately requested time windows. If the selected universe/factory itself discloses proprietary attention and has not been approved for publication, public collector admission is **REJECTED**, even if the blockchain events were publicly accessible.

**Internal first-known correction:** prospectively complete fresh-tail windows and historical gap closure require *separate immutable cursor families*: `live_tail_cursor` starting at a documented fresh first-observation release boundary, and `backfill_cursor` continuing the older canonical Oct21 historical archive. An original public tail receipt can qualify for its own prospective sample only after verifying the entire declared contemporaneous interval and actual machine first observed clock; it cannot certify an unrelated earlier gap. Mark `LIVE_WINDOW_COMPLETE_WITH_HISTORICAL_BACKLOG`, not `CANONICAL_BACKLOG_CLOSED`. Private original #120 remains a single canonical authority until proven W3 cutover.

**Existing public IP risk:** [Archive Draft #1826](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1826) already publicly exposes uncalibrated hypothesis weight tables, threshold floors, private-source path references and case specifics. Grok #118 finds no verified proprietary *edge* disclosure but recommends redacting unnecessary future public weight/floor and private case/path metadata on the **existing** PR; historic Git visibility cannot be reversed by editing/deleting. Private calibrated weights, proprietary decisions and user-specific signals never enter public collectors, Git history, run names or reports. A public 'draft' is still public.

## 1. Decision and hard technical constraint

**Goal:** move essentially all *eligible* deterministic computation and public-source collection to free standard GitHub-hosted Actions in an actually PUBLIC **caller** repository, thereby reserving the monthly 3,000 private GitHub Pro Actions minutes for code and data that truly require private access. Preserve an independent private source/strategy/recovery boundary and improve evidence at actual first-machine observation time. This is not permission to open all existing Alpha, secrets, Bridge or Vault repositories.

**Non-negotiable:** a normal public GitHub Actions runner cannot compute a function of secret inputs or run secret algorithms while keeping those inputs/algorithms secret. Running encrypted blobs or sending unsalted/SHA-256 hashes of prices, ranks, watchlists or thresholds to public code does not solve this. Use public runners only for non-secret inputs and public/generic implementations; preserve a private last-mile computation for private ranking, user holdings, paid provider records, proprietary factors and private longitudinal outcomes. FHE/MPC, an attested confidential-computing environment and hardware-protected enclaves are **NOT** capabilities of ordinary standard Actions and are outside v1 scope. Do not promise 100% zero-private-compute or zero information leakage.

**Verified platform:** GitHub public standard GitHub-hosted Actions runners are free; private GitHub Pro includes 3,000 minutes. Larger public runners, artifact storage, cache and outside providers are separately bounded/billable. A private caller that uses a public reusable workflow is **still billed to the private caller**. This migration therefore needs an INDEPENDENT PUBLIC WORKFLOW START and a PUBLIC-ONLY input graph, not `uses: owner/public/.github/workflows/...@...` from Alpha. Github source: docs.github.com/en/billing/concepts/product-billing/github-actions and docs.github.com/en/actions/concepts/billing-and-usage.

## 2. Existing authorities that MUST remain true

Read these original files on current main before implementation:
- Public: `AGENTS.md`, `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md` (blob at design `c8ead1b0e92c32eef4a911ad1b6bf33a09170966`), `00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json` (blob `3cd5ec75bc1ea9432aeedc263e0a8e114296b6`).
- Alpha: `AGENTS.md` (blob `73e51f5c181654f561b686bde58d4bb307719536`) and `governance/PUBLICATION_POLICY_V1.json` (blob `d552e2321e6dbd6a65c7202b27e4ce41bffcd4cf`). The policy applies **regardless of Alpha's current private visibility**.
- Restricted plane: `Donh91/secrets` holds restricted research payloads and can be inspected only by an authorized private evidence owner; do not mirror raw/normalized provider values, wallets, user data, sensitive query samples, or credentials into public code, logs or reports. No data-movement authorization is inferred from ownership of both repos.
- Archive Research Lab/CRE remains shadow/falsification only; Round 3 remains `PROSPECTIVE_COLLECTION_ONLY`, private analysis/feedback/tuning gate closed. Public computation does not lower those gates.
- No autonomous trading, signed transaction, public BUY/SELL promotion, portfolio threshold, strategy weight or automatic release.

**Existing production diagnosis (Oct 31):** Alpha canonical Robinhood/Pons cursor remains Oct 21, `last_block=90213238`, `catchup_pending=true`; its Oct 21 historical receipt measured a **4,050,607-block deficit at that time only**. Actual current deficit is UNKNOWN without a fresh head at a matching clock. `prospective-census-v4.yml` uses `17 6,18 * * *` (2/day under private quota, not hourly); its one combined job has an 8-minute wall limit and multiple unrelated consumers/writers. A public refactor must not conflate historical backfill with fresh capture or take a false retrospective first-seen credit.

## 3. Compute separation | four execution planes

```text
PUBLIC SOURCE PLANE: open chain RPC, public contract ABIs, released public candles,
                       public deterministic tests, documented public data terms
         |  no credentials, no secret/private addresses, no private trigger parameters
         v
PUBLIC COMPUTE PLANE: isolated standard-ubuntu GitHub Actions PUBLIC caller
         |  A: source-agnostic codecs / chain identity / public factory birth census
         |  B: separate LIVE safe-head tail and bounded historical backfill
         |  C: generic price/candle replay and matched public/synthetic controls
         |  D: schema checks, coverage/gap receipts, source clocks, cost/capability health
         v
PUBLIC RELEASE PLANE: immutable public source receipts from trusted main-only publisher
         |  contract+schema SHA, original run ID+time, exact covered ranges,
         |  content digest, validity/coverage, no private ranks or selected universe
         v   ALLOWLISTED ONE-WAY READ: private consumer pulls pinned public blob
PRIVATE ADMISSION PLANE (existing Meme-Alpha-Lab / secrets as authorized)
         |  verifies original public data + source/clock and public repo SHA
         |  binds private sensitive measurements, proprietary score, wallet/source rights
         |  owns proprietary model decisions, controlled S4 outcomes and audit evidence
         v
EXISTING FRAMEWORK STRATEGIST / SOLE CHAT S1
         |  review, falsify, code/PR release, outcomes, cost and rollback readback
```

The public compute plane is **untrusted for private decisions by default**, even though its code is open source and its GitHub run green. A valid public receipt is evidence of claimed public observations, not a source-authenticated private conclusion, trade, favorable return or Pons LIVE recovery.

**Recommended deployment isolation:** a dedicated PUBLIC compute-only repo under the same owner, distinct from the existing public canonical Archive, with ONLY stripped public source collector and zero existing production secrets, source writers or third-party PR pipelines. This is an isolated **execution venue for the same #120 collector authority**, NOT a second scanner, research owner or canonical decision engine. It has no GitHub access to private repos. Github connector access currently cannot be assumed to create/configure repositories or branch rules; choosing this repo is a release/infrastructure gate. Until secured, this design alone lives in Archive; no pilot executes in Archive's crowded production workflows.

**Why not direct Archive deployment yet:** independent Grok audit [Bridge #108](https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/108) found 199 Archive workflows, including 72 main pushers and multiple privileged PR workflows, at its pinned snapshot; this is a reviewed lead, not a timeless census. Current Archive ruleset `25307191` is `enforcement=disabled` at this design check; branch-protection read requires integration admin and is unavailable. Source path-scoping and Markdown policy alone do NOT enforce isolation. A public repository can also expose all of its workflow logs and artifacts.

## 4. Confidentiality classes (admission deny by default)

| Input or output type | Allowed on public runner? | Public publication | Private destination |
| --- | --- | --- | --- |
| Generic public protocols, factory ABI, general-purpose decoder and synthetic fixtures | YES | Code, protocol metadata, tests and negative fixtures | May reuse by pinned SHA |
| Complete public-source chain log range with exact chain/factory/block/tx/log identity | MAYBE, after explicit class/scope approval | ONLY approved exhaustive, outcome-independent public launch evidence; no private subset | Existing #120 validates, stores adopted original result |
| Public vendor-owned market data with restrictive terms | NO unless terms explicitly permit automated republication | Default NO | Only with source rights/provenance |
| Selected watchlist, early private candidate shortlist, wallet clusters/funder relations, research priorities | NO | NEVER, including hashes or leaked request parameters | Original restricted plane |
| Proprietary features, weights, thresholds, hypotheses, model versions, expected upside, order route/size, user positions | NO | NEVER | Authorized private computation only |
| Private provider raw/normalized measurements, Round 3, paid source tokens, license data | NO | NEVER | Restricted plane only, subject to its own analysis gate |
| Public source-health ranges/count/gap metadata | YES if itself not sensitive | Only allowlisted low-risk fields; no selected cohort/denominator disclosure | Admitted receipt |
| Private source-health value-free metadata | NO by default on public runner | Only separately allowed, batch-frozen and independently reviewed sanitized metadata; beware differencing | Private origin authoritative |

No untrusted public workflow may discover private data availability through a differing HTTP response, shared cache, webhook return value, branch naming, timestamp jitter, query volume, small cohort aggregate or error message. Direct SHA-256 of low-entropy sensitive values is NOT confidentiality. If a private value is needed to determine what to compute, compute that final step privately. Public outputs never accept arbitrary private queries.

## 5. Ownership and public runtime workflow isolation

**Public worker (new dedicated repo ONLY after security bootstrap):**
1. Trusted default-branch `schedule` at offset minutes (avoid top-of-hour load); independent public trigger, not private `workflow_call`, not private `repository_dispatch` containing restricted parameters. Default `permissions: contents: read`, `id-token: none`, **NO repository/environment/org secrets** or cloud credentials, no access to private repo tokens. `persist-credentials:false`.
2. Two distinct jobs/paths: `recent_birth_window` for timeliness (safe head minus confirmations, bounded 5k public RPC chunks) and `historical_repair` for non-overlapping contiguous holes. Each writes a different receipt class and original first-known clock. A separate bounded public publisher of validated public artifacts may have narrowly scoped `contents:write` only on main, never PR; publish only scrubbed allowlisted files and GitHub run ID. Don't execute PR code with write token.
3. Source integrity: check Robinhood chain id 4663, known factory/event ABI and topic0, token/curve/deployer/pair identity, tx+blockHash+logIndex, removed/reorg flags, canonical head with 2-confirmation policy, multi-source discrepancy; never advance durable cursor through a partial RPC error. Source RPC failure is not zero events. Monotonic non-overlapping cursor; overlap replay by stable unique `(chain, blockHash, txHash, logIndex)`, reorg correction explicit.
4. Coverage receipts reference exact block start/end, safe head and timestamps, RPC completeness, actual GitHub job/run start and completed timestamps, causal event-first-seen and receipt availability; actual github.run_id and run database timestamp are used for independent latency plausibility. A Git commit's author timestamp or a signed/hash artifact alone is NOT original first-seen proof. Runner can be delayed/dropped; prove coverage by observed block ranges, not expected cron.
5. No `pull_request_target`; public PR jobs `contents: read` only, no code from third-party fork in privileged steps, no `workflow_run` untrusted-artifact promotion, no generic dynamic `eval`/shell interpolation from data; pin third-party Actions to reviewed commit hashes. Gate changed paths/symlinks/import closure and workflows in a *trusted base* guard plus required check+code-owner review/branch rules. Separate branch/ruleset for data writer, no self-merge with same identity.
6. Source outputs are immutable by content and must have retention policy; rolling pointers are convenience only. A published original receipt cannot be modified silently, deleted via normal maintenance, or rewritten to `LIVE` retroactively; incident rollback must preserve original bytes in private recovery.
7. No import of proprietary private source from Archive/Alpha into public test harness, including in test fixtures, exception text, `git` patches, public PR discussions or cache keys. An audit of all original code/docs/workflows and dataset history is required before any code is copied into a public repo. Git history remains visible even if a file is deleted later.

**Private consumer:** use a scheduled or due-only **short-lived private validation/import**, pinned to trusted public release commit and allowlisted exact path, verifying byte digest/schema/source identity/completeness and public run-origin evidence; never take a value from `latest` alone; no `workflow_run` of arbitrary forked public artifact. It must not execute public blob as code, receive actions from public runner, or use general cross-repo write credentials. It can copy **explicitly admitted public evidence** into original Alpha #120 source store, but private S4/#77 outcomes, case privacy and proprietary scoring stay private. If nothing new, `NO_CHANGE` and zero heavy workload. GitHub public runner must never have any private downstream credential even for a 'simple push'.

## 6. Pons source recovery without scientific self-deception

At cutover, canonical #120 owns **ONE** accepted pointer to the public producer, with a monotonically increasing coverage+cursor epoch. During shadow period existing private canonical v4 is unchanged, and fresh public observations are tagged `PUBLIC_SHADOW_NOT_CANONICAL`. A recent-tail capture is `PARTIAL_TAIL_SAMPLE` until completeness proven for the claimed range; historical replay is `DELAYED_CATCHUP`, never retroactive machine-first-known. Backfill is separate from fresh capture, and may be CPU/network bounded independently so it cannot starve live. A public empty window is `ZERO_EVENTS_VERIFIED` only when 100% complete original range and source proof; runner not started => `RUNNER_NOT_STARTED`, RPC partial => `SOURCE_UNKNOWN`.

**Handoff gates:** 48-72h parallel prospective source observation with exact safe-head and public workflow step readback, independent original snapshots; no future-clock input, no missing/reordered block range, idempotent byte-identical full+incremental replay, explicit missing-window denominator. Two consecutive complete timely accepted canonical-window observations, then an owner-approved **atomic authority switch**; independent same-interval diff before/after; dual-publisher guard; public producer may supply a new canonical source only if private owner confirms complete data lineage. Keep the private original producer as reversible fallback for downtime, but it must NOT run simultaneously as a second accepted writer. Rollback to prior immutable pointer with private recovery separation and no retroactive source-time upgrade.

**Moonshot timing:** if public worker schedules hourly, this is not guaranteed hourly actual discovery; for <15m launch study require observed end-to-end <=15m with source receipts and actual first-known plus provenance. GitHub schedule is not a websocket/realtime SLA; cron may be delayed/dropped. Public shadow must measure event→first machine observation and missing minutes. If not timely, evaluate alternative continuous public-source indexing without false promise, or leave source P0 blocked.

## 7. Financial economics and relevance to the original 3,000 private minutes

Historical independent Grok [Bridge #96](https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/96) estimated October private usage: Alpha PR-CI **1,500-2,200 min/month**, restricted-plane scheduled captures ~570 min and Alpha scheduled jobs ~360 min, plus Vault UNKNOWN. These are run-duration proxies, **not actual billed minutes**. Pons 2/day at median ~3min is roughly 180 private min/month; moving Pons alone barely addresses draft PR-CI as the largest expense. A genuine independent public 24/day Pons capture at 3 min = ~2,160 standard hosted compute min/month **free** instead of consuming the private quota, with RPC/retention/runner limits and no guaranteed timeliness. A public workflow invoked BY a PRIVATE reusable caller does not save minutes.

Separate actions:
- Migrate public-sourced Pons hot/cold data and generic collection contracts into isolated public runner: large **potential** headroom to restore original timing, small actual *present* private saving until cadence increases.
- Move only truly public/generic deterministic test suites, reproducible synthetic methods and future public research into public compute **without shipping proprietary implementation**. Private Alpha code tests stay private, budgeted and release-gated. A public tests-only service that downloads or executes private code either bills private caller or leaks proprietary code; explicitly NOT the chosen architecture.
- Independently implement Grok #96 private savings: draft PR gating without sacrificing final current-head hosted CI, job timeouts, coalesced private gates, concurrency on PRs only, reviewed API costs; do not bypass P0 private QA.
- Actual savings formula: `baseline private billed minutes - post-migration private billed minutes`, paired with original source coverage and qualifying matured outcomes, not number of public job runs.

## 8. Security threat register and falsifiers

| ID | Threat | Required negative test | Default failure state |
| --- | --- | --- | --- |
| T01 | Public workflow executes altered PR with write permissions / malicious fork | Fork modifies collector, guard and workflow simultaneously; write token absent, base-trusted guard rejects | BOOTSTRAP_SECURITY_HOLD |
| T02 | Public runner reads restricted information via token, cloud OIDC or private repository_dispatch | Search committed+runtime workflow env, permissions and all referenced Actions; deny `id-token:write`, `secrets.*`, cross-repo token | PUBLIC_PRIVATE_ACCESS_DENIED |
| T03 | Value leakage through hashed small-domain price/rank/watchlist, branch names, timestamps, logs | Offline dictionary/differencing on proposed payload and two adjacent receipts | PRIVATE_VALUE_LEAK_RISK |
| T04 | Public token-launch filter reveals private target or strategic watchlist | Inspect exact factory/topic/output and cadence for strategy disclosure with qualified owner | RECLASSIFY_PRIVATE_OR_BROADEN_PUBLIC_UNIVERSE |
| T05 | Spoofed public run or edited first-known timestamp | Tamper file timestamp, change SHA, insert successful 0-step run; consumer rejects or marks unverified | SOURCE_ATTESTATION_UNKNOWN |
| T06 | Missing schedule/RPC and source fallback mislabeled no events | Simulate schedule absent, 429, wrong chain, removed log, partial chunk | COVERAGE_GAP_NOT_ZERO |
| T07 | Live/high-value opportunity retroactively claimed from historical backfill | Replay stale birth with `LIVE` status; admission refuses | NO_PROSPECTIVE_CREDIT |
| T08 | Two source owners both advance canonical cursor / reorg gap | Dual-writer overlap, nonmonotonic cursor, changed blockhash | DUAL_WRITER_STOP |
| T09 | PR CI drift, base-guard replaced, symlink/import escape | Negative scope tests of all workflow/paths, changed-head rerun | SECURITY_REVIEW_REQUIRED |
| T10 | Public release imports sensitive/private outcome payload or proprietary model | Golden-sensitive fixture fails strict schema/field allowlist+cross-file scan | PUBLICATION_REJECT |
| T11 | Quota shifts from private to public but data rights/retention/budget exceed cap | Provider terms, storage usage, bounded job/runtime and cost receipt | COST_OR_LICENSE_HOLD |
| T12 | Supposed edge from selected survivors, data churn or circular controls | Complete launch denominator incl dead, matched no-signal controls, original T0, prospective holdout and net quotes | RESEARCH_ONLY_NO_EDGE |
| T13 | Compromised public writer pushes malicious data into private consumer | Consumer treats JSON as untrusted data, strict schema, exact pinned repo SHA, no code execution | IMPORT_QUARANTINE |
| T14 | Side channel via repeated public queries or metadata receipts | Same-cohort differencing and zero/deny-oracle tests | PRIVATE_DISCLOSURE_HOLD |

**Important controls:** privacy-safe `SHA-256` is an *integrity* identifier only, not concealment. An HMAC of private inputs may only be created and validated inside private trust boundary and never offered as arbitrary public oracle; even metadata count/timing may leak. For true public chain raw observations, publish only once original owner affirmatively accepts revealing the target universe and timestamps.

## 9. Implementation waves and explicit stop conditions

**Wave 0 | design/preregistration (this PR).** Document the precise input/output classes, cost model, owner table, receipt schema and negative tests. Obtain independent Grok [Bridge] review on exact SHA, owner security review, source terms audit, privacy disclosure assessment and compare current PR #186/#193/#178/#202/CRE for overlap. NO workflow, source code, public dataset, repo visibility or auth change. Current Archive ruleset disabled and private authority unverified. **WAVE0_DESIGN_ONLY**.

**Wave 1 | zero-secret public shadow bootstrap.** After Grok issues resolved, choose isolated execution repo (or prove equivalent isolation in Archive), protect main with tested independent guards, publish ONLY synthetic fixture and generic schema, implement public `contents:read` dry-run, 1 positive + 1 adversarial fork test, bound retry/cost. No market source yet. **WAVE1_TESTED_NO_PUBLIC_MARKET**.

**Wave 2 | genuine public-source canary.** Review public RPC terms and exactly what data/target disclosure is allowed. Run bounded recent-tail+historical backfill separately; collect 48-72h source coverage receipts with honest gaps, original run jobs/steps+latency, reorg challenges, independent source identity and total spend. Pons original #120 is still canonical, no BUY. **WAVE2_SHADOW_ONLY**.

**Wave 3 | one-way private admission and controlled cutover.** Private owner verifies schema/exact source commit, publication class, complete contiguous original coverage, 2 timely windows, actual source-run observations, cost/rollback/safepoint and downstream compatibility. Independent security review and authoritative S1 approval before one atomic cutover; disable old active publisher safely, preserve immutable receipts. **WAVE3_RELEASE_GATED**.

**Wave 4 | public research expansion.** Move only generic public science, exhaustive launch baselines, public-source wallet distributions, matched negatives, null-attack fixtures and regression tests. Reuse existing Alpha #22 Genome / #77 outcome / Archive CRE rather than a second engine. Fix Genome `runs`=selection-not-execution metric before reporting quality. 14 days of real prospective evaluation and weekly false-positive/false-negative, cost and timebox measurement before any scientific promotion. **WAVE4_RESEARCH_ONLY**.

A wave cannot be advanced by Chat automation prompt, issue comment, Grok narrative, hash alone, archived report, 0-step CI or paid model. Release needs exact code/head, actual executed tests and original source receipts, privacy owner and rollback. Key results: source completeness, **fraction of launches captured within 15m/60m** (observed only), false-early-credit=0, import reject count, secret leaks=0, private billed minute reduction, and number of preregistered hypotheses actually resolved versus baseline. A pilot with weaker coverage or privacy than original must be stopped or rolled back.

## 10. Questions Grok MUST attack (do not defend the plan)

1. Demonstrate a concrete public-to-private disclosure route even if all files pass schema: logs, stdout, PR branches, selected factory topics, job timings, cohort differencing, OIDC, untrusted Actions import.
2. Is a dedicated public repo actually more isolated than a hardened subdir in Archive, given GitHub repo ownership, permissions and operational bottlenecks? Present a contrary minimum design and explicit tradeoffs.
3. Is the public birth capture truly source-complete and economically helpful, or will GitHub cron jitter and RPC caps still miss the first 15 minutes? Show bounded negative tests and alternatives.
4. Identify any current private dependency in the existing Pons v4/fast/shadow collectors that makes naive public code migration invalid (imports, credentials, private downstream writes, hidden src, case-store history, licensing).
5. Can an attacker spoof GitHub provenance or confuse `captured_at_utc`, `source_first_known`, `block.timestamp`, GitHub run scheduling and first usable receipt? What minimum original receipt structure is defensible?
6. Can a public selected-token list or exhaustive Pons data leak model attention/positioning by timing? How to publish without a private request oracle?
7. Do the proposed Phase 1-3 acceptance metrics actually justify release? Identify skipped/reordered range, reorg, retry, duplicate, pool-CA and wrong chain failures.
8. Does the actual GitHub Pro private-cost baseline show that moving the current 2/day Pons to public is poor ROI versus private PR-CI draft gating? Quantify with actual job-based metadata, mark billing unknown.
9. Can a same-account attacker or agent change the public policy and release guard in one PR given currently disabled ruleset? Specify externally enforced controls, approval requirements and safe fallback.
10. Which parts cannot be public without revealing proprietary inputs, algorithm or result? Explicitly recommend keeping any impossible part private, with bounded cloud minutes rather than hand-waving encryption.

**Do not call the migration active, source repaired, budget saved or scientific edge improved until matching future main/readback evidence exists.**