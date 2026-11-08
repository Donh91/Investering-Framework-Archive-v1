# S1 Release Control · Optional agent-to-agent work hub v1

**Existing original domain owner:** S1 [#1156](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156). Built on merged authenticated discovery #2033 and the pre-existing read-only agent contract. **Not** a new canonical backlog, operator, scheduler, workflow, GitHub identity, merger, task assignment authority or condition of completion.

## Goal, explicitly NONBLOCKING
Give existing S1, Grok, Codex, Strategist and research agents a convenient bounded view of **all credential-accessible open original PRs and non-PR issues**, both public and private, with source links, native assignees when observed, last update and conservative work-lane hints. Original GitHub records retain ownership. This hub is OPTIONAL and never an extra approval/gate.

### One existing authorized runtime, on demand only
```sh
node tools/s1-release-control/agent-work-hub-v1.mjs
# Only in an existing authorized, private, nonlogging agent runtime with an already-available GitHub credential:
node tools/s1-release-control/agent-work-hub-v1.mjs --private-details
# Optional research hints only; never reopens closed tasks:
node tools/s1-release-control/agent-work-hub-v1.mjs --private-details --closed-parked
```
Default output never contains private titles/IDs even if a caller passes a private-filled source object. A `--private-details` request must be executed only in an already-authorized restricted runtime with appropriate existing GitHub repository scope; never in public Actions, AppDeploy static HTML, artifact upload, GitHub issue/PR, or an unrestricted agent context. Do not create secrets or broaden permissions. The restricted provider-data repo `Donh91/secrets` is **excluded** from this operational work hub, not from its separate canonical restricted-plane obligations. An inaccessible repo remains UNKNOWN, never empty.

### Agent-to-agent responsibility and decision discipline
- An **ASSIGNED_ON_GITHUB** owner means a native GitHub assignee, not proof of original domain ownership or approval. With no assignee, use **OWNER_UNOBSERVED**, never assign the PR author or infer ownership from title, labels or apparent activity. Multiple native assignees are explicitly ambiguous.
- `OPEN_DRAFT_HINT`, `OPEN_PR_NOT_READY_PROOF`, `OPEN_ISSUE_ACTIVITY_UNVERIFIED` and parked hints are *triage*, not READY, progress, HOLD, priority, review or an instruction to merge.
- Original linked issues/PRs, policy, assigned current owner, HEAD, CI, reviews, dependencies, custody, domain rules and authenticated source clock decide actions. Check them natively whenever action matters. The optional hub doesn't decide, execute, supersede, close, merge, expand roles or create jobs.
- In case of **any** missing input, error, partial pagination, unknown owner, stale source, unavailable token, model budget exhaustion or hub downtime: **CONTINUE_WITH_ORIGINAL_GITHUB_OWNERS**. Do not insert a new waiting step, HOLD loop, PR release gate, mandated read, paid call or additional task. Natural S1 action still observes Monday read-only, max 3 eligible actions, current original policy and exact-HEAD approval criteria. Never score absence from this hub as missing original work.
- Avoid overlapping writers: before an agent edits an original PR branch, re-read native current PR, last edit, changed filenames, original issue, HEAD and main. If another agent is actively writing the same source, defer the conflicting edit and choose independent original work. Hub is a discovery accelerator, not a transactional lock or lease.

### Honest proof and rollout
`S1_AGENT_WORK_HUB_v1` carries `can_block_actions:false`, `release_permission:false`, `fallback`, completeness flags and `adoption:UNPROVEN_UNTIL_NATURAL_AGENT_RUN_RECEIPT`. Only a future actual native run consuming source SHA, using a concrete original owner decision, and recording run/PR/main outcome proves agent adoption. Neither creating this file nor saying "the agents use it" does. Use original S1 #1156 for a materially new verified natural outcome, not repetitive status comments. Tests: `node --test tools/s1-release-control/test-agent-work-hub-v1.mjs`.

**Security:** Public webapp stays PUBLIC_ONLY and never accesses Bridge/Alpha/secret tokens. No new API endpoints or public ingest. Repo enumeration is credential-scope bounded. No private details in public logs, PRs, receipts or site.

**Closed research scan:** `--closed-parked` is opt-in only. When explicitly requested, results appear as `CLOSED_RESEARCH_HINT_NOT_ACTIVE` and are counted separately from open work. Never perform broad closed-history scans as a routine hourly hub preflight.
