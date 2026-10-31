# Alpha Public Compute v1.0 | Release plan, test matrix and cost acceptance

Status: **DRAFT TEST CONTRACT, NOTHING DEPLOYED.** Parent: `ARCHITECTURE_AND_THREAT_MODEL.md`; schema: `PUBLIC_RECEIPT_CONTRACT_V1.schema.json`. All acceptance is source-bound, independent and intentionally conservative. Existing canonical source owner: private Alpha #120; permanent Research Genome #22, S4/#77, existing S1 #1156 and Strategist #1157. Existing Grok 09:30 DK advisory Bridge is the independent attacker, NOT an executing code reviewer/merge-authority.

## 1. Boundaries and chosen placement

Decision: use **public compute repo as isolated host, Archive as policy/research control plane, existing private Alpha as admitted source/scientific authority, `Donh91/secrets` restricted data**, existing Vault independent recovery. The compute repo has no authority to read any private data or call private accounts; isolation must be real GitHub permissions and separate tokens, not a README. If new public repo creation or branch protections are unsupported by available tools, `INFRASTRUCTURE_SETUP_NOT_VERIFIED` and stop. Do not make private repositories public or move their git history.

Alternative A (preferred): isolated new public repo with only public collector and generic science. Alternative B: hardened public Archive subdirectory ONLY after a separate exhaustive workflows/secret/import/ruleset audit; Grok #108 found too many privileged workflows to assume safe. Alternative C: private-only status quo, fail-closed when no secure public venue. Never auto-fall back from failed A to insecure B.

## 2. RACI, no duplicated canonical truth

| Workstream | Authoritative owner | Public worker | Private owner | Grok/S1 |
| --- | --- | --- | --- | --- |
| Public chain birth source and contiguous coverage | Alpha #120 | Execute research-only public-source collector, publish complete/partial receipts | Validate one-way import, preserve original census evidence | S1 authorizes handoff; Grok red-team |
| Public generic methods, falsification and synthetic regressions | Alpha Genome #22, Archive Research Lab | Execute generic/transparent tests, not secret alpha | Evaluate proprietary downstream relevance privately | S1 resolves owner/reject |
| Pons trader/LP safety and realistic quotes | Alpha #98/#194 | Public generic static/fuzz fixtures only | Inspect actual holder/LP roles and private decision rules | Independent exact-head safety review |
| PIT outcome and false-positive/negative learning | Alpha #77 / S4 | Public complete-denominator *public-source* baseline, if publication allowed | Admit private frozen cohorts, matched quotes, execution realism, confidential outcomes | S1 release; Grok adversarial science |
| GitHub credentials, private keys, subscription provider values, wallet ownership | Restricted private and credential planes | No access whatsoever | Only authorized private runtime | No Grok raw secret access |
| Merge and cross-repo safety | Existing #1156 and canonical AGENTS | Cannot merge private source or own releases | Owner-approved, actual CI and recovery | Grok advisory, S1 actual release evidence |

S5 `Project→CA · Alpha Source Watch · Chat` remains a cheap **observer** of producer freshness, not a new source. Chat S1 remains sole Supervisor. Do not add another repeating task, Genome, scorer or Grok agent. Keep existing Bridge as advisory exchange, no new Bridge workflows.

## 3. Concrete waves with owner-signed exit gates

### W0 | Design and independent hostile review - current PR
- [ ] Verify exact Archive, Alpha and Grok Bridge source SHA(s), existing overlap and public/private boundaries.
- [ ] Grok reviews this exact design HEAD; give P0/P1/P2 counterexamples, minimalist diffs, alternative deployment and cost/utility alternatives.
- [ ] Source/privacy owner examines whether factory/ABI, follow-up values, expected launch times, pinned target universes and code comments disclose strategic information; private data reviewer is not Grok.
- [ ] Keep public schema non-authoritative, disallow anything besides documented metadata. No live source, code, cron, secrets, repo visibility, notifications or merge policy changes.
**Success:** review accepted/revised with evidence and a bounded release plan. **Stop:** `DESIGN_NOT_APPROVED` or source/privacy uncertain.

### W1 | Dedicated public worker bootstrap (no market data)
- [ ] Verify repo visibility public, distinct from Archive, default branch protection/ruleset actually enforced, CODEOWNERS/most-recent-push review where available, required correct-head tests, no write bypass.
- [ ] Check all workflows for `secrets.`, `id-token: write`, privileged `pull_request_target` and `workflow_run` untrusted artifact use, third-party action source, `contents:write`, `permissions`, workflow refs, import graph, symlinks, external code calls. Synthetic negative test attacks their use.
- [ ] A plain `pull_request` synthetic-only CI uses no secrets and `contents:read`. A future trusted **main-only** publisher uses only an isolated minimal write token and strictly checks public output. No branch-owned writer.
- [ ] Positive test: clean JSON metadata and bounded simulated range accepted. Adverse: secret-like field, raw JSON values, private repo path, high-entropy disguise, price hash, fake OIDC, fake source clocks, manipulated GitHub run ID, malicious path/symlink rejected.
- [ ] Public output file immutability, content SHA, retention and built-in cleanup-policy verified. No data from private source.
**Success:** exact-head positive/negative hosted jobs with executed steps, GitHub readback, independent security admission. **Stop:** `PUBLIC_BOOTSTRAP_SECURITY_HOLD`.

### W2 | Public market-source shadow canary
- [ ] Independently review public source terms, original factory/topic and candidate output disclosure. No proprietary shortlisted subset; either publish full, approved, outcome-independent source census or keep targeting private.
- [ ] Run bounded `RECENT_TAIL` and `HISTORICAL_BACKFILL` as distinct contracts. First source observation after actual release, no retrospective machine discovery.
- [ ] Track each 5k-ish RPC chunk, safe-head+timestamp, actual missing ranges, removed logs, wrong chain and factory identity, duplicate/replay and reorg. Source was not observed if a runner failed to start, a query timed out or a partial log was returned. A gap is not a zero launch.
- [ ] Three consecutive days of observation (minimum 48h, preferred 72h). Actual wall-clock coverage and delays, 15m/60m eligibility, source availability, selection-bias and job errors must be tabulated, including failed windows.
- [ ] Genuine producer-run provenance: GitHub job step count >0, job result and verified run ID, public release immutable blob; GitHub event/available times independently read. Collector self-reported `first_observed` is not independently attested.
- [ ] No download/execution of public artifact by private importer, until W3. No 24/day blind schedule switch. Define affordable public run rate based on observed source latency and actual coverage; do not mistake no-dollar job time for unlimited RPC/provider availability.
**Success:** consecutive source-complete receipts, replays idempotent and gaps honestly recorded, confirmed zero sensitive payload. **Stop:** `PUBLIC_SOURCE_QUALITY_UNVERIFIED`.

### W3 | Private admitted readback and atomically governed cutover
- [ ] Original private #120 importer reads PUBLIC release by exact `repo + code SHA + content SHA + original run ID + approved path`, schema/permissions/source-contract and chronological integrity. No `latest` trust, no private action triggered by untrusted public PR.
- [ ] Simulate altered blob, forged metadata, 0-step run, wrong-factory log, invalid timestamp, missing block, double publisher and consumer code execution attack, all fail closed. Private receipt binds original public evidence and private admission; no public field indicates private score/BUY.
- [ ] Two consecutive timely, independently complete source windows (and any stricter original #120 gates). Zero retroactive early detection. Separate historic backfill debt from current live cadence; one canonical source pointer and a single accepted writer.
- [ ] Preserve exact old `main`/cursor/immutable receipts and a **tested** revert/rollback with independent Vault recovery separation; no simultaneous destructive control of canonical/recovery. No private writer stopped until public-source readback actually works.
- [ ] Owner ratifies cutover only after current-head hosted security CI and independent challenge. A public source receipt can never auto-publish a private BUY or update scoring weights.
**Success:** `CANONICAL_SOURCE_PUBLIC_PRODUCER_ADMITTED` with exact postmerge proof and natural 48h continuity. **Stop:** `SOURCE_ADMISSION_FAIL`, rollback to prior private authoritative state.

### W4 | Research compute expansion and learning
- [ ] Move only public-source, legal and truly generic work: exact public chain event normalization, synthetic attacks, same-cohort negative controls, source-clock stress testing, cost monitoring and public matched-baseline backtests. Private proprietary model/backtest remains private.
- [ ] Research Genome #22 corrects `runs` semantic defect: legacy queue selection count vs executed qualified study, true independent first-known and matured outcome; no rewrite of historic scores.
- [ ] Every experiment preregisters source cohort before knowing outcome, split by regime and time, declares matched null/persistence baseline, multiplicity and finite kill criteria. Failed methods retired rather than endlessly retuned.
- [ ] First 14 days: score data integrity, measured private-minute savings and true research output, not number of PRs, requests or clock ticks. Kill expensive unproductive research.
**Success:** better source coverage, fewer accidental false successes, reproducible falsifications and actual private Actions headroom without disclosure. **Stop:** `NO_MEASURABLE_UTILITY` and reduce worker frequency/complexity.

## 4. Prioritized attack/test matrix with minimal fixtures

| Test | Positive fixture | Adversarial fixture | Expected fail-closed |
| --- | --- | --- | --- |
| A01 Repo boundary | Public isolated repo with no private read tokens | Public PR attempts read `Donh91/secrets` or uses cross-repo write token | Access unavailable, no leaked token |
| A02 PR trust | Untrusted PR only read-only tested | PR changes YAML guard + code + symlink, or fork artifact promoted by a privileged workflow | Scope/test guard fails, no secrets |
| A03 Data confidentiality | Public synthetic full-universe source only | `price_usd`, `my_wallet`, threshold, watchlist, fee, base64 encoded secret, hash of rounded BTC price | Schema and publication scanning fail; inspect logs as second path |
| A04 Side-channel | Fixed cadence public metadata independent of private query | Cohort n=12 then n=11 difference, 50 guesses, different denied/held latency | No arbitrary private query API, no public response difference |
| A05 Provenance | External GitHub run created/completed times agree with receipt within rules | Self-claimed fake T0 before workflow started, commit author timestamp backdated | Independent PIT unknown, admission rejected |
| A06 Source gap | Fully contiguous logs and matching safe head | Omitted middle chunk, 429, wrong chain, removed log, partial fallback source | Missing counted, zero-event unverified |
| A07 Reorg & dedup | Stable block+tx+index replay identical | Two block hashes for same height; repeated event; cursor beyond unverified range | Quarantine/reorg receipt, no silent advance |
| A08 No hindsight | Original event observed within captured interval | Historical backfill for a past winner republished as LIVE | No prospective credit, no BUY |
| A09 Dual writer | Private canonical while public shadow only | Both claim canonical, stale imported cursor overtakes source | Single accepted authority or fail-closed |
| A10 Cost | Public jobs and private billing measured by owner | 0-step run, scheduled run dropped, provider rate-limit, artifact retention bill | No savings or live coverage claims |
| A11 Science | Frozen cohort, included losses and null model | Selected winners, repeated correlated observations, source_clock unknown | Research-only/no edge certification |
| A12 Kill switch & rollback | One public producer only; private recovery snapshots checked | Public repo compromised, wrong releases, original private write canceled prematurely | Disable public admission, restore prior authority without deleting evidence |

## 5. Bounded minute economics - distinguish numbers from facts

Historical **Grok advisory** [Bridge #96](https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/96), source-pinned 2026-10-30:
- Alpha private PR-CI historically estimated **1,500-2,200 min/30d**, largest cost lane.
- Private `secrets` scheduled collectors ~570 min/30d, separate licensed/restricted source.
- Alpha scheduled ~360 min/30d, of which existing 2/day Pons ~180. Vault is UNKNOWN.
- These are per-run rounded/elapsed **proxies**, not verified account billing. Account actual 3,000 used was independently user-reported; do NOT promise specific percent reduction without billing view.

| Pons capture interval assumption | Runs per 30d | At illustrative 3 min/job if PRIVATE | In truly public standard-runner repo | Limitations |
| --- | ---: | ---: | --- | --- |
| 12h, current cost-saving | 60 | 180 min | $0 standard-runner minutes | Poor original first-hour coverage |
| 60 min | 720 | 2,160 min | $0 standard-runner minutes | GitHub schedule unreliable, source first-seen/coverage TBD |
| 15 min | 2,880 | 8,640 min | $0 standard-runner minutes | No guaranteed sub-15m event observation, provider/retention risk |
| 5 min theoretical | 8,640 | 25,920 min | $0 standard-runner minutes | GitHub schedule ceiling not practical real-time SLA, strong queue/rate-limit risk |

Illustrations only. Additional public research 3 daily generic jobs at 3 min each = ~270 public minutes/30d for $0 standard-runner cost, with no model/API included. Avoid claiming private compute savings from activity never running privately. **Critical:** the current 2/day Pons transfer saves only about 180 private minutes at the proxy baseline; real private savings must ALSO come from independent draft PR CI consolidation and moving strictly public method work. Private source/strategy computation continues to use the 3,000-minute allowance.

Define weekly measures:
```
private_billed_minutes_actual = billing owner readback by repo and runner SKU
public_job_minutes = actual completed public standard-runner jobs (cost separately zero)
valid_covered_minutes = independently verified contiguous public-source intervals
lag_p50_p95 = original event -> first recorded availability, qualified events only
gap_ratio = missing or unverified expected coverage / total required intervals
false_early_credit = count of historical/partial observations labeled machine-T0 (target 0)
secret_exposure_incidents = confirmed public disclosure events (target 0)
qualified_studies = completed with receipts + controls + due original outcome (not queue selections)
```

Never claim `LIVE_RECOVERED` solely on running scheduled jobs. Do not raise collection frequency if RPC cost, quota or missed observations worsen, even though public runner minutes are free. A real-time requirement may justify a separate, owner-approved continuous collector only after explicit alternative budget/security review.

## 6. Data and source publication preflight

No actual production code/data is in this PR. Before implementation, conduct a **separate private code and file history audit**:
1. Enumerate full existing Pons collector import closure, private configs, schemas, environment variables, output directories, token/factory constants, source rights and every data file committed to `Meme-Alpha-Lab`. Redact and export only a generic allowlisted derivative, never whole git history or a source subtree unreviewed.
2. Repo-scoped public runner token cannot read restricted repos, must have no secrets `id-token: write` or OIDC trust; avoid public `repository_dispatch` with private payloads.
3. Approve whether publicly identifying Pons launchpad/factory reveals research interest. A public full-census output for all relevant public factories is safer than publishing a proprietary *selected subset*, but may still reveal strategy focus from timing. If target disclosure itself is sensitive, do not offload the targeted scanning stage.
4. Read actual provider terms, especially commercial/free public endpoints and rate-limit policies. Public-source availability does not automatically grant redistribution rights.
5. Ensure no proprietary alpha factors/weights are exposed as code or as outcomes. Public outputs can only be generic raw event completeness or public benchmark measurements, not scores or candidate lists.

## 7. Grok independent review disposition contract

Grok Bot's **existing** 09:30 Europe/Copenhagen Routine and Bridge report writer may independently read this public source PR **at one pinned SHA** and deposit a single new report in its already private Bridge `reports/grok/automated/` path, via new report branch/PR. No extra scheduler, new API budget, direct edits in Archive/Alpha or private data reads. If PR SHA changes, REVIEW_HEAD_STALE and explicit delta re-review, no stale approval. Required:

```
VERDICT = ADOPT / ADAPT / REJECT / HOLD
claimed public-free billing and privacy feasibility with sources
P0/P1/P2 repros, exact source SHA and file path, patches and paired tests
which tasks MUST stay private, what proprietary data could leak
real vs theoretical savings (public runs, private original billing, API/provider)
a defensible isolated public repo trust and GitHub ruleset bootstrap
no 0-step or README-only pass; no irreversible cutover
one minimal first implementation PR with test/rollback and owner
```

Report review is **advisory** and not GitHub APPROVED/green CI, code execution, Grok native Routine delivery guarantee, or canonical framework permission.

**Final Wave0 recommendation:** approve this proposal for **hostile review, not runtime activation**. Proceed to actual implementation only after adjudication of Grok P0/P1 defects and an original-source privacy/runners ruleset review. Source code must be inspected privately before any public extraction.
