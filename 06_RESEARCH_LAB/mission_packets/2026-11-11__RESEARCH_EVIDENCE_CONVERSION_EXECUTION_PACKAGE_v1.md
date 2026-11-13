# Research Lab | Evidence-to-Decision Conversion · execution package v1.0

**Date:** 2026-11-11 · **owner mandate:** explicit, full authorized source-safe execution · **status:** ACTIVE OWNER HANDOFF, BRANCH-ONLY UNTIL GATED MERGE  
**One existing scientific owner:** Archive #1157 (Adaptive Evolution / admission); **Research Lab routing:** Archive #1512; **Task 2:** #1596; **S1 closure:** Archive #1156, existing Chat S1 task `6ae5fd466b48819187abc224ec0f1c5f`.  
**Type:** `MODIFY_EXISTING_TEST` + `SOURCE_PROVENANCE_REPAIR`. **Not** a new engine, agent, workflow, paid job, queue controller, live market model, public forecast or trading strategy.  
**Latest public evidence is AS-OF 2026-11-11, not an asserted invariant after main moves.** Revalidate source commit and first-known receipts at each original task start.  
**Deliverable here:** executable READ-ONLY preflight, adversarial regression tests, falsifiable original-owner implementation work and Claude/Grok/Fable coordination decision. No automatic admission, no historical score backfill.

## 0. Answer the real question

**North star:** Convert independently authenticated, first-known research observations into matched baseline tests and demonstrable marginal improvement in an ORIGINAL owner decision, not into more research documents, green CI checks, model opinions or speculative features.

```text
AUTHENTICATED SOURCE + CLOCK + VERSION
→ preregistered eligible opportunity/forecast/NO_DECISION
→ immutable due outcome, unknown/censor retained
→ scientific admission or explicit REJECT(code)
→ paired simple baseline and event-family independence
→ uncertainty, tail and opportunity-cost verdict
→ original-owner bounded PR, tests, independent review, actual merge
→ fresh-main/consumer readback
→ later post-merge measured delta or RETAIN_UNPROVEN / KILL
```

**Success is not** a merged plan, zero errors, a filled queue, a PASS from a paid model, a count of 1,504 correlated outcomes or a retrospectively inferred profitable trade.

## 1. Independently inspected baseline and hard scientific warning

| Source | Public main blob SHA, observed | Finding | DO NOT INFER |
|---|---|---|---|
| `research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json` | `4d5f0185cbd7b618cdc1ab1ec389f0904d7c84f0` | 735 candidate rows; 1,504 candidate-summed matured outcomes; 0 science-score-eligible | 1,504 independent trials or zero market outcomes |
| `research/experiment_lifecycle/LATEST_SCIENTIFIC_ADMISSION_REGISTRY.json` | `9ce559dd1cb02c04c6d76159c61bd72ac41738a4` | 337 forward-test qualified candidate identities, 389 semantic duplicates, 8 quarantined, 1 waiting | 337 independently validated predictive edges |
| `scripts/experiments/source_git_anchor.py` | `247913a2cd8bfdd5e3e8154dc372876077992192` | `AcceptedMainSource.matches(... accepted_before/after ...)` **intentionally returns False for any temporal requirement**: no authenticated server-side acceptance clock | An accidental defect or permission to delete time gate |
| `scripts/experiments/experiment_lifecycle.py` | `e18fb0388369d2fb503452972fe11ddfbf925ae2` | Lifecycle invokes `anchor.matches(... accepted_before=due)` for frozen forecast and `accepted_after=due` for settlement raw | Correct original future-source timestamps or first-published data |
| `06_RESEARCH_LAB/shared_row_model_tournament_v1/RUNTIME_STATUS.json` | `2e2d136710962e6ce6726f8410d92c82481f41a4` | `eligible_prospective_rows=0` (older state claim) | Current outcome row census |
| `06_RESEARCH_LAB/shared_row_model_tournament_v1/NEXT_ACTION_STATE.json` | `3cc81f67e8292f62e62570ea429ee0cd7058254e` | 45 eligible, 32 matured 7d, 150 divergences, one pairwise prospective block, terminal `INSUFFICIENT_EVIDENCE` | A production defect, independent N=150 or model edge |
| `research/framework_memory/fnp_forward_rows/LATEST.json` | `a563d8251cda6518df6f1c31504c62b81b28a401` | 0 source rows, 5 ignored receipts, `PASS_NO_ELIGIBLE_INPUT`, FNP evaluator unavailable | No false-negative opportunity loss in reality |
| `05_CYCLE_NAVIGATOR/autonomous_calibration_v1/STATE.json` | verified Nov11 | 0 eligible verified rows; legacy FRLP CSV has EXAMPLE_ONLY row | No real CN forecasts anywhere |
| `research/autonomous_research_portfolio/PORTFOLIO_MANIFEST_v1.json` | `fbe3e35a2440edaead8df5a2b88b2c0927834885` | ARP 1–5 and ten owner-linked actions are a proposal/routing design, not five running engines | Executed experiments |
| `research/historical_reality_engine/CROSS_ERA_RESULTS_20261107.md` | existing verified report | price-only controls warn too late on many selected overlapping crisis windows | Actual original historical Kompas edge |

**Critical root cause RC1:** The missing experiment science-score eligibility is at least partly an **intentional provenance lockdown**. Several matured candidates explicitly report `FORECAST_SOURCE_ANCHOR_REJECTED`. A proposed fix that simply removes `accepted_before/after`, trusts commit-author dates, or reclassifies historical data to get positive scores is a **P0 SCIENTIFIC SAFETY FAILURE**. Prove a server-accepted, receipt-bound, prospective original issuance clock and settlement first-known independently, or keep zero.

**Additional nuance RC3:** Shared Row's `RUNTIME_STATUS` and `NEXT_ACTION_STATE` may intentionally summarize different eligibility grains. Reconcile field definitions/producer/run/fingerprint before writing a 'stale status' patch. A numerically unequal count is not itself evidence of data corruption.

## 2. Executable, SMALL original-owner work packages

### EC-00 · Now: source-safe independent census and first useful truthful report · P0, ChatGPT/Codex

**Actual initial implementation in this PR:** `scripts/research/research_lab_evidence_conversion_preflight_v1.py` and `tests/research/test_research_lab_evidence_conversion_preflight_v1.py`.

Run on a fresh, pinned, full current owner checkout (does not fetch, write or change registry):
```bash
python -m unittest tests.research.test_research_lab_evidence_conversion_preflight_v1 -v
python -m scripts.research.research_lab_evidence_conversion_preflight_v1 --repo-root . > /tmp/research_lab_conversion_preflight.json
python -m json.tool /tmp/research_lab_conversion_preflight.json > /dev/null
```

**Receipt:** exact main SHA, file hashes, timestamp, exit code, test count, output JSON digest and any SOURCE_MISSING/DRIFT. Report descriptive original counts and nonadmission reason taxonomy. DO NOT change `LATEST` files or claim this script has independently executed in native Actions until an Actions run actually contains these commands.

**Kill:** code cannot safely classify existing registry without changing producer/clock semantics. If so report `FAIL_CLOSED` and assign the original owner a narrower source-format issue, no new monitor/scheduler.

### EC-01 · Timed admission without backfill or fabricated clocks · P0, existing #1157 + experiment owner

**Frozen hypothesis:** genuinely first-issued, future-timed original forecast and later outcome can be admitted with a server-accepted trustworthy artifact clock while forged/revised/stale/unknown payloads remain excluded.

**Codex concrete code test proposal:** audit `source_git_anchor.py`, `experiment_lifecycle.py`, producer's initial forecast/settlement immutable receipt, original GitHub API server-side event time and source delivery. Design exactly ONE observer-verified prospective receipt contract that binds (a) original Git blob/hash, original source path/identity, (b) GitHub-controlled acceptance event ID and clock, (c) first-known availability vs target due, (d) after-due immutable raw settlement and quote/venue, (e) all applicable ownership and copy/rewrite checks. Cross-reference #1827, no duplicate proof store.

**Mandatory negative tests:** forged Git author/committer time; amended/rebased original; re-upload on different ref; wrong repo/branch; shallow history; force rewritten receipt; due == publish time; settlement raw appearing before due; wrong forecast/target; incorrect quote/venue; missing delivery/first-published clock; symlink/path traversal; alternate last-main; clock changed between producer and scorer. Include positive freshly generated timestamped test fixture *only if* production-equivalent provider-controlled proof is available.

**Falsifier:** no secure original server acceptance and immutable source available, or admission can be bypassed on fake receipt.  
**DONE:** original owner shows FAIL(base)/PASS(patch) on legitimate prospective row, forged cases still FAIL, one future actual event+due outcome enters scientific eligibility at most ONCE, all old rejected rows remain unchanged; if no eligible future row due yet, `SOURCE_READY_OUTCOME_PENDING`, not DONE/edge.
**DO NOT:** relax source clock/anchor, infer 2026 historical original first-publication from later Git revisions, import Round3, raise market score, change canonical rule.

### EC-02 · FNP observer actually runs, emits provenance and matures divergence · P0/P1, existing #1478 / #1157

**Hypothesis:** one expected producer->observer/persistence edge is absent or incorrectly wired; an intentionally zero divergence population is the competing null. Compare source-native production workflow ancestry and `forward_evidence_observer.py` `observe/mature/coverage-health` invocation, the original T2 coverage/maturity contract and `fnp_cumulative_forward.py` source row filter.

**Execution:** first reconstruct exact native workflow run and mandatory `BTC_PARTIAL_WAIT_COVERAGE_RECEIPT_v1`/maturity receipt persistence. Codex handles the smallest existing-workflow patch only if an actual missing invocation is proven; if a natural alternate producer exists, update source-bound owner routing instead of duplicating work. Claude/Grok independent falsification of zero-divergence vs observer never invoked. No retrospective owner-compensating FNP rows.

**DONE:** one real scheduled original-owner GitHub Actions run read back with expected inputs, either a genuine qualified current divergence with immutable due receipt or explicit validated `ZERO_ELIGIBLE_BY_DESIGN` with denominator and native provenance; later due maturation receipts and opportunity-loss scoring only if authoritative evaluation exists. `PASS_NO_ELIGIBLE_INPUT` alone NEVER counts.
**Kill:** private source rights / no authoritative evaluator, `SOURCE_BLOCKED_WITH_EXACT_TRIGGER`, not 'done'.

### EC-03 · Shared Row statistical truth and cohort comparison · P0/P1, original Shared Row / Task2 #1596

**Hypothesis:** C02 breadth and other candidates may have different performance across independent periods, but currently observed paired wins are concentrated in one prospective block; always-positive can beat more elaborate rules.

**Execution:** reconcile runtime and next-action grain; match one 7d event/target per predeclared candidate+baseline, freeze actual action clock, risk/false-positive costs and genuinely independent market blocks. Use B0 always-positive/negative, momentum/price and C07 Simple3; report effective N and clustered uncertainty. Compare not only conditional C02-vs-C07 disagreement wins, but all eligible cases and utility of NO_DECISION. Never multiply a 7-day window into independent hourly samples.

**DONE:** signed source and consumer census, 7d paired baseline matrix, realized tail-error and FNP cost decomposition and `PASS/INCONCLUSIVE/REJECT` without model promotion. If one block: `INSUFFICIENT_INDEPENDENT_BLOCKS`. No threshold selection or false confidence.

### EC-04 · CN forecast calibration and width-aware baselines · P1, original #1516 + #1479

**Hypothesis:** a genuine prospectively issued CN range/point path can beat a same-width last-close and 24h-mean naive baseline after proper scoring, not simply because the CN interval is wide.

**Inputs:** verified W41–W46 first-issued and ledger from Claude OT-2/OT-2B; W41–W46 design-seen only. New **W47+** eligible cohorts must be frozen before their scoring windows. Existing `FORWARD_RANGE_LEDGER_v0_1.csv` is an EXAMPLE_ONLY legacy target, `STATE.json` zero verified, while newer production source is distinct. Do not paste historical actuals into an allegedly originally frozen baseline.

**Scoring:** weekly BTC/ETH correlated as one week-cluster; each day's expected close vs realized close, simultaneous low/high containment, Winkler or weighted interval score/width, median absolute error/coverage vs naive baselines; separate all-horizon 12h NOWCAST measurement from prospective 24/72h forecasts.

**DONE:** correct source-clock joined original forecast+actual+first-issue receipts, original owner accepts one measured W47+ scored unit and same-clock dumb baseline, and tests verify failure on missing/unavailable/immature/changed USD/USDT inputs. Prospective skill requires an *untouched* and independently sufficient collection period, no early positive winner.

### EC-05 · Economic transfer, AFTER source admission, not before · P1/P2, Alpha #228/#98 + Task2/derivatives

**Hypothesis:** market protection, early rotation or dip ideas have incremental *executable* decision value vs simple matched strategy given full-position exit, slippage, gas, funding, route failure, capital occupancy and missed rebounds.

**Use existing:** Alpha v4 paper-wallet, 8-arm Strategy Arena, Genome and existing native sellability/first-buyer output. No second paper wallet, no new Pons/Hyperliquid engine, no private data copies. The [FuturAI vault methodology source note](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2081) is a test-design challenger ONLY, not evidence of profits or small-cap transfer.

**DONE:** at least one source-qualified prospective paper-opportunity/NO_TRADE event with eligible exit/no-exit and matched baseline, append-only outcome; explain uncertainty. Stop/REJECT if no eligible sell quote, PIT label, or safe denominator. No investment authority.

### EC-06 · Conversion closure, not another scoreboard · P1, existing Strategist #1157 / S1 #1156

Every EC lane has **one original owner** and immutable source fingerprint plus:
```text
PHASE: PROPOSED | SOURCE_BLOCKED | TEST_READY | NATIVE_TESTED | SHADOW_FORWARD
     | MATURED_INCONCLUSIVE | REJECTED | QUALIFIED_FOR_REVIEW | MERGED_UNVERIFIED
     | MAIN_VERIFIED | POST_MERGE_VALIDATED | SUPERSEDED
ORIGINAL_OWNER_URL, CURRENT_MAIN_SHA, SOURCE_CLOCK_CLASS, RUN_ID, PR_EXACT_HEAD,
BASELINE, FALSIFIER, NEGATIVE_TESTS, N_INDEPENDENT, COST, NEXT_EVIDENCE_TRIGGER.
```
A comment, API verdict, review or green test DOES NOT reach `POST_MERGE_VALIDATED`; only a verified original observed consumer effect can. No new scheduled scoreboard, use existing #1157 anti-false-success receipts and S1 run.

## 3. Delegate to best available executor, not permanent model dependence

| Actor | Work to assign | Independent constraint |
|---|---|---|
| **ChatGPT interactive** | source-census/current-main reconciliation, initial safe PRE-FLIGHT, executable package, original PR, S1/Bridge communication, ownership map | Does not impersonate a scheduled S1 run or claim a native Actions execution |
| **Codex** | EC-01 event-clock source-gate engineering, EC-02 existing workflow producer wiring and negative tests, EC-04 compatible scorer patch if source admitted | At most one original small code change concurrently; native exact-head CI; Codex is not mandatory for qualified Claude-reviewed work |
| **Claude auditor (existing :10)** | independent exact-HEAD review, AUDIT-04b cause and source/time provenance, EC-01 wrong-clock and EC-03 false-edge red team | Must avoid duplicating Fable v1.0; logged on existing `claude/log` only |
| **Grok (existing Bridge lane, when available)** | independently reproduce false-safe claims, source clock and baseline math, challenge C02 and source-authority assumptions, review negative outcomes | Advisory, not GitHub approval, paid entitlement, or execution |
| **S1 existing hourly** | classify/route original EC tasks; merge only fully qualified exact-HEAD original PRs within existing <=3 per tick and native source/custody gates; main+consumer readback; avoid duplicate current PR work | Sole scheduled supervisor; source native evidence outranks Bridge/status prose; no new task, schedule, rights, prompts or identities |
| **Fable 5.2 one-shot** | ONLY the previously GO-audited frozen v1.0 Kompas daily/weekly state inconsistency, conditional shadow patch and parity; narrow research invariant input below | Existing manual owner+effort+served-model gate; never silently launched or changed by this package |

**Preferred mix:** ChatGPT gathers and verifies; Codex builds bounded code/test patch; Claude independently reviews; Grok separately falsifies causal/scoring assumptions; S1 controls qualified original release and natural follow-up. If a provider is unavailable, proceed with source-native deterministic work; do NOT make research depend on model quota.

## 4. Fable 5.2 scope adjudication and preparation

**Read authoritative frozen package:** Bridge `tasks/claude/FABLE_5_2_PACKAGE_v1.0_FROZEN.md` on `chatgpt/fable52-v1-frozen-20261111` @ commit `351a0567cb454590f9e8ba6218cf456ce5f08131`, blob `435b8385a3d2c1d98ddde07e41d25270e7e10e2b`. Claude independent package audit at Bridge PR #173 comment `6797741043`: **GO**, 4 operational wrapper notes; actual manual Fable execution not attested. Do not revise, relaunch, rescope or auto-trigger this one-shot.

**What belongs INSIDE Fable: just two direct Research Lab falsifiers, already compatible with v1.0:**
1. `RL-F1 DAILY_SOURCE_DECISION_TIME_TRUTH`: daily original source last-known/first-known stale vs weekly BUILDING; test source absent, UNKNOWN/DEGRADED, no-decision, label-clock parity; fail-before/pass-after only if original current code still demonstrates defect. Reconcile corrected 33 healthy, 8 degraded, healthy breadth 0.76→0.08 (0.83 came from a degraded packet), and morning subset denominator before citing 5/8 or 6/8.
2. `RL-F2 SHADOW_DECISION_PARITY_AND_ECONOMIC_HONESTY`: healthy original decision fields unchanged, negative cases explicitly fail closed, zero claims of predictive/executable improvement; if optional Alpha public context is available, design-only falsifier for hypothetical after-cost utility vs matched HOLD/NO_TRADE and full exit, no private values.

**Before Fable, WITHOUT asking it to solve clerical source work:** produce exact current main/owner SHA manifest, original packet ledger/clock parity subset, minimal ≥10 test fixture list, negative/healthy controls, current C1 status, existing ARP01/ARP04/OT-2 no-duplicate map, no-decision acceptance, rollback anchor, source/usage availability and owner original repo map. This is work for ChatGPT/Codex/S1. Let Fable read those pointers, not 200 broad repos.

**Explicitly OUTSIDE Fable:** EC-01 timed Git server provenance repair, EC-02 FNP producer implementation, EC-03 full 7d statistical tourney, EC-04 CN forecast baseline catch-up, EC-05 microcap paper-wallet execution, Scientific Conversion audit originally deferred under Bridge #173 comment `6794016800`, Sol MAX #2080, private secrets work, broad Alpha redesign, OT-9/OT-12 or Phase B. Those tasks are original-owner work before or after Fable; never consume one-shot Fable usage for them.

**Portion to merge:** about **20–30% of Research Lab mission reasoning** has direct incremental Fable relevance, **zero additional mandatory implementation phases**. This is a scope allocation, not a measured empirical percentage. The remaining 70–80% belongs to EC original-owner tasks. Recommend ONE small Bridge #173 additive message with exact provenance and Fable read-pointers, not a rewrite of the GO-audited v1.0 frozen file.

**Fable result acceptance** = reproduced source-clock root cause OR evidence-based REJECTED/SUPERSEDED/UNTESTABLE, ≥10 precisely specified adversarial fixtures, actual executed count separate, clean healthy parity, shadow-only patch IF reproduced, main implementation handoff, tests and rollback, native served-model/usage receipt. No official signal, no retroactive 2026 edge.

## 5. S1 execution order and anti-parking SLA

**Immediately on next eligible EXISTING tick:** first respect P0 security/production original PRs and Monday 09:30–10:30 READ-ONLY. Then parse this PR+manifest and source-verify against current main. Score expected scientific marginal value, originality, source permission, native opportunity and risk. **Do not just acknowledge a plan**.

1. EC-00: qualify this actual 4-file documentation+code PR and run native/hosted tests when its PR CI is available; Codex or ChatGPT source review. If gate blocks, record exact gate/run/HEAD, not generic 'review pending'. Explicit native test commands above.
2. EC-01: identify one exact original prospective clock owner, prove whether secure server event exists; if available implement smallest safely gated original branch and tests; else `SOURCE_BLOCKED` with exact source/event and reactivation trigger. Do NOT weaken anchor under pressure.
3. EC-02: trace original workflow invocation and producer persisted receipts, complete one native negative/positive case. Only after confirmed missing connection, use original owner patch. Do not create a new workflow.
4. EC-03: reconcile competing counters by field definitions/producer SHA, publish one correct paired denominator and one-block warning. Do not promote C02 based on conditional wins.
5. EC-04: attach prospective W47+ range scoreboard to existing original CN source, no design-seen credit.
6. EC-05: after authentic prospectives exist, one bounded executable Alpha experiment; do not pre-empt source repairs.
7. EC-06: verify actual original PR main+consumer readback, later scientific effect, cost and negative results; close when evidence supports. Record links in original #1157 and Research Lab #1512, not a second supervisor.

**Owner-visible receipts required:** `S1_RESEARCH_CONVERSION_DECISION_v1` with EC-id, actor route, SHA, original owner, source and code decision, `EXECUTE_NOW | DELEGATE_CODEX | CLAUDE_REVIEW | GROK_FALSIFY | SOURCE_BLOCKED | DUPLICATE_KILLED`, next executable action and exact evidence URI; at most one nonduplicate note per material event.

**Stop conditions:** identical failed attempt twice without changed evidence, data rights unknown, stronger safety gate absent, main drift, source clock untrusted, Fable served model unproven, hidden private values risk, no incremental falsifier, competing active PR for same owner or any high-impact Vault/recovery separation unverified. Preserve every genuine negative result.

**Time discipline:** EC-00 and owner+PR routing now. EC-01/02 are the highest-priority P0 diagnostic before optional deep research; EC-03/04 parallel only if no same-owner conflict; EC-05 contingent on eligible outcomes. No fabricated calendar commitments or automatic runs.

## 6. Acceptance board, not vanity score

| Gate | Required actual receipt | Otherwise |
|---|---|---|
| Source reality | GitHub server-authoritative original first-acceptance and valid original issuer/due clock | SOURCE_BLOCKED |
| Correct pipeline | Native workflow real invocation/receipt plus persisted input and negative test | IMPLEMENTATION_UNPROVEN |
| Quality | Correct prospective denominator incl NO_DECISION, duplicates, missing/censor, false-safe controls | QUARANTINED |
| Marginal skill | Same-event paired naive baseline, effective independent N, calibrated uncertainty | INSUFFICIENT_EVIDENCE |
| Decision utility | False-positive cost, FNP missed upside, executable full-exit cost, no hindsight | EXPLANATORY_ONLY |
| Release | Exact HEAD native CI, independent risk-specific review, safe merge + main blob readback | NOT_DEPLOYED |
| Learning | Later source-independent consumer outcome / attributable delta vs baseline | NOT_VALIDATED |

**Primary owner disposition:** `MODIFY_EXISTING_TEST`. This package is DONE as preparation only when its preflight, tests, PR and S1 routing are verified. The underlying scientific program remains OPEN until source-authenticated forward results and actual code-to-consumer evaluation exist.
