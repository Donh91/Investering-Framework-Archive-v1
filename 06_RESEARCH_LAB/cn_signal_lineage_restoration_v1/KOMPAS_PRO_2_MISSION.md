# KOMPAS PRO 2.0 / CN-MM INTELLIGENCE RESTORATION AND EVOLUTION

Status: OPEN / DRAFT / DO NOT MERGE UNTIL MISSION CLOSURE AND EXISTING RELEASE GATES PASS.
Owner mandate recorded 2026-11-24: continue and expand the mission in full, preserve code and context in GitHub, only merge this mission PR when completed. This is an implementation mission, not a report-writing exercise. No new authority over trading, spending, production, or governance is conferred.

## Resume here from any chat or model

1. Read this file at the current mission PR head; read all PR comments/reviews and changed files, parent Archive #2315, relevant Claude Bridge #173, current main and S1 governance.
2. Compare live heads and identify active writers. One writer per branch. Do not touch the frozen #2315 review head from this branch. This is a stacked continuation of #2315 at 80a37e768677cc14f4a39097b87a9b3ebe269ba2, not a competing implementation. Coordinate parent disposition and reconcile/rebase onto reviewed main before final review; never merge this branch into the parent as a shortcut.
3. Work code-first on the next unresolved gate; reuse canonical owners, data and evaluators. Commit actual implementation and tests, record exact head, verified evidence, outstanding blockers and next action in PR comments. Keep this file current when scope/status materially changes. Never mark closure from prose or green tests alone.
4. Full owner mandate for audit, research, code, integration and tests within existing safety/review rules. No manual private Actions dispatch, paid API, new scheduler, production promotion, force-push, unreviewed merge, historical rewrite, or live trades. Respect active S1/Claude lanes and quotas. Natural PR CI is not a substitute for independent review.

## Starting evidence and code

Parent #2315 and its handoff:
https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2315
https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2315#issuecomment-7128327067

Parent exact head 80a37e768677cc14f4a39097b87a9b3ebe269ba2 was observed draft, not merged, with 17/17 returned PR workflow runs successful; the reported full suite was 6966 passed, one skipped. This evidence does not transfer to this branch. Parent has broader draft integration, not fully restored intelligence.

Preserved implementation:
- scripts/research/ethbtc_persistence_replay_v1.py
- tests/research/test_ethbtc_persistence_replay_v1.py
- 13 standalone tests passed locally; integration and this head's repository CI pending.

New source audit: 79 raw rows, 77 BELOW, 2 ABOVE, 64 BELOW rows left-censored at 168 hours. Positive observations are one observed episode, not independent confirmations: Nov 4 14:00Z 0.02998, 15:00Z 0.03022, source-declared window end 17:00Z. Seven and eleven consecutive above bars at the two original observation commits 98858195f36e136464d20863bf9bcbc5d71479c0 and 983d4ed84c6add22a8ff6a05c24bef3b98ab53de. Both BTC.D MIXED_PATH and breadth BROAD_MAJORITY. Direct source-tail reads, not full independent owner replay or trusted availability. No frozen confirmation duration established.

## P0 next implementation: source-derived persistence

In scripts/research/prospective_evidence_controller.py add alongside existing import core_shared_row_materializer as core:

    from ethbtc_persistence_replay_v1 import verify_window_inputs

Immediately after ETHBTC row reconciliation guard:

    persistence_replay = verify_window_inputs(window, cutoff, window_inputs)

Add persistence_replay to the existing verify_source_bindings return mapping. Keep ancestry, path SHA256, original window digest, baseline, breadth/BTC.D and freshness checks. Replay all existing post-floor rows before enabling mandatory enforcement. Quarantine mismatches via existing governance, never rewrite frozen rows. Test mutated metadata with recomputed provenance hash; no bypass by caller-supplied digest. Integrate the derived object into CN shadow bridge only after owner replay; preserve the existing C01-C07 frozen latest-side Boolean rule and all historical fields. New duration rules require prospective preregistration, not hindsight. At 168 hours report left censoring; distinguish bar time, source-declared availability, independently attested known-by time, actual decision and confirmation time.

## Full mission acceptance register (all OPEN unless explicitly evidenced)

- [ ] M01 Source/PIT integrity: byte-bound source, provenance, independent known-by evidence at the actual decision cutoff; strict missing/late/revised/duplicate/forged-source rejection; historical UNKNOWN remains UNKNOWN. Natural source-to-MM-to-CN readback with exact hashes and clocks.
- [ ] M02 Persistence: full original owner replay, derived run length/episode identity and censoring, adversarial tests, episode deduplication, preregistered confirmation policy with no backdating. Preserve frozen C01-C07.
- [ ] M03 Sequence intelligence: implement and evaluate frozen 13_SEQUENCE_STUDY.md sequences (ETHBTC persistence -> BTC.D rollover/reclaim -> breadth survival; BTC ETF absorption -> ETHBTC weakness -> breadth deterioration; price stress -> liquidation clearance -> OI/funding reset -> reclaim). Separate observation, confirmation, veto, redundant delay, timing value. Missing source families explicitly blocked, not silently approximated. Include opportunity cost and overlapping-event controls.
- [ ] M04 Restore legacy capabilities: trace actual source, evaluator, owner, consumer and outcome receipt for every item in CN_MM_LEGACY_RECOVERY_MAP_v1.json, expand archive inventory; preserve original definitions and adjudications. Early rotation, breadth, dominance, ETF, stablecoin deployment vs supply, leverage, CFGI, Pullback Radar, fakeout/reclaim and regime analysis. No fabricated historical formula, no duplicate correlated sensor, no restoration claim for an untestable item.
- [ ] M05 Meta-learning: CCE dependence/overlap, ODM prespecified 6h/12h/24h/48h/72h/7d/14d/30d maturity, FAE marginal attribution, SRE regime-conditioned reliability, RWE research-only weight proposals. Validate actual outcome receipts, matched denominators, adverse controls, no automatic live weights. Explicitly distinguish recovered originals from methodological descendants.
- [ ] M06 Forecast challenger: retain C0 existing CN, C1 simple independent baseline, C2 source-qualified signal/sequence shadow model; freeze code/inputs/policy/metrics before new outcomes; matched decision cutoffs and identical evaluation cohorts, 1-3d/5-7d/2-3w where valid; daily close MAE, directional skill, range containment/width and interval score. Preserve sealed historical denominator; no outcome leak, post-hoc threshold selection, retrospective official forecast rewrite or unearned edge claim.
- [ ] M07 Interval calibration: audit intended coverage target and issuance time, separate close coverage from full-day high/low containment, evaluate width and interval score against baseline, use only matured prior calibration evidence and honest abstention/insufficient N. W46/W47 reported 20/28 better closes, 0/28 full-day coverage; two retrospectively examined weeks, not proof of prospective edge.
- [ ] M08 MM/CN end-to-end integration: typed source-bound noncanonical analytical translation, real consumer decision mutation tests, source-to-output lineage and utilization map. Existing authorized writers only; isolate shadow failure from canonical delivery and prove idempotent write-once readback. Price-only fallback explicitly degraded.
- [ ] M09 Anti-regression: versioned authoritative capability contract, actual source-to-consumer effect tests per claimed active capability, anti-removal/anti-bypass tests and reviewed required-check protection. No self-comparison loophole or manifest-only proof; respect S1 hash chain and reviewed cutover.
- [ ] M10 Autonomous learning: existing S1 and research owners consume actionable outcome receipts and bounded next actions, no routine owner manual work, no duplicate schedulers. Demonstrate natural cadence readback and actionable failures without silent loss of capabilities.
- [ ] M11 Release closure: reconcile parent and main; all applicable exact-head tests and CI green; independent exact-head review, all blocking findings resolved, existing custody/release/bootstrap requirements satisfied where applicable. No unresolved mandatory gate. Any scientific evidence requiring future maturation stays OPEN; do not fabricate results or promote early.

## Merge hold

Keep mission PR DRAFT and auto-merge disabled. Do not mark ready or merge until each mandatory acceptance gate has inspectable evidence and the existing independent reviewer and release governance permit it. Do not merge merely to make files accessible. If a scientifically unavailable input or future outcome prevents closure, document it as an open blocker, continue other eligible engineering, and leave this mission open. This document records an owner instruction; it is not itself a new protected GitHub ruleset. No bypass or relaxation of existing controls.

## Definition of done

The original analytical intelligence is operational and traceable (or explicitly evidenced as irrecoverable and disposition approved by the owner), the next-generation challenger is prospectively and fairly evaluated, calibration and attribution are reliable, functionality loss is detected, and existing automated owners handle recurring work. Every completion claim has a code path, test and appropriate real evidence. No report-only completion.

## Continuation: original owner extension (2026-11-24)

Added opt-in strict `verify_persistence_source_bindings` to the original prospective evidence owner. It first performs all existing byte/path/ancestry/clock/freshness checks, then replays the actual window and rejects forged duration/metadata or duplicate keys. Old frozen C01-C07 admission remains unchanged until the full cohort is audited. Added read-only full-cohort command:

    python scripts/research/prospective_evidence_controller.py --audit-persistence

The audit reports per-row source replay, rejected rows, left censoring and observed crossing identities without consuming outcomes or rewriting historical rows. Added two real Git fixture tests in existing P0 integrity suite. Full exact-head repository execution and historical cohort readback remain pending. Next: run full audit in trusted checkout, resolve mismatches through existing quarantine rules, integrate verified persistence into MM/CN shadow projection and its independent readback; never credit a censored or repeated observation as an independent signal. M02 remains OPEN.

### Native CI follow-up
At 961609f6, the full repository test run reported 6,979 passed, 2 failed, 1 skipped, 3,992 subtests passed (job 138396017415). The shared-row gate failed on the same new audit fixture (job 138396019142). The fixture had directly appended an unnormalized Python candidate-decision dictionary into CSV; corrected to use production ingest and assert diagnostic details. Data Architecture Gate failed required-job import closure: added the new persistence helper to the derived path manifest and repinned draft lane -> runtime -> bootstrap without changing standing decisions, live task, workflow, or scheduler. Fresh exact-head CI still required; no claim that historical audit passed. No merge.

### Pinned original-owner readback candidate (M02/M08)
Producer, publication and consumer now reuse the original owner through a commit-scoped read-only context, binding ledger/header, frozen registry, activation contract and candidate registry to producer checkout. Rejects source commits not ancestral to producer checkout and replays exact source bytes plus strict duration. No historical code execution or global rebinding. V1 immutable packet shape unchanged; consumer exposes separately versioned noncanonical persistence diagnostic only after source replay. Previously accepted synthetic self-hashed packet without source owners is rejected. Added Git fixture tests for dirty worktree, future-source ancestry and forged duration, and real W47 pinned readback positive/negative cases. New-head CI and full 79-row audit still required. No PIT, confirmation, action or forecast authority granted.

### Full historical cohort native gate (M02)
The existing read-only audit CLI now uses a pinned HEAD replay context rather than mutable worktree data. Added a fresh-process real archive test to the existing native Shared Row Tournament gate: all post-floor rows must replay, zero rejects, unchanged ledger bytes, exact checkout, explicit no-PIT/no-forecast authority. Emits compact PINNED_PERSISTENCE_COHORT counts to native logs. This is an acceptance test, not a claim of passing before the run. No new workflow, schedule, paid call or historical data write.

### Native historical replay verified; initial sequence census (M02/M03/M08)
Exact PR head 8bcde844: all five returned native workflows SUCCESS. Full suite 6983 passed, 1 skipped, 3995 subtests passed (job 138408457596). Native research job 138408457139 at actual checked-out merge commit 2e7a18ef18284c6a8418a7295752ac6b4b1a00bb emitted PINNED_PERSISTENCE_COHORT: 79/79 replayed, 0 rejected, 64 left-censored, 2 above observations, 1 observed above episode. Not independent PIT or stable confirmation proof. Added versioned sequence census from owner-replayed observations, deduplication of observed crossing and source identities, non-overlapping BTC.D falling-path then breadth-majority transitions only, reset on loss of state, no assumed confirmation duration or original sequence equivalence. Explicit blockers for ETF and leverage sequences, no outcome/delay attribution yet. Existing CN readback returns separate sequence diagnostic; no packet rewrite. Six new adversarial tests and extended real W47 test; fresh exact-head native test results pending. All acceptance gates remain open.

### Sequence evaluation and ETF source integration
Native prior head efe7b639 research log job 138414209117: 79/79, one observed episode (Nov 4 15Z crossing, 7/11 hours), zero complete ordered proxies. Corrected lifecycle diagnostics to preserve first observed ordered completion separately from current active proxy and closed episodes; added tests for state loss and episode closure. Reused scripts/experiments/etf_absorption_transmission_v1.py existing owner validator rather than creating a second ETF model. Pinned raw context reads historical LATEST at row source commit only, validates ancestry, owner record, strict pointer/path/signature and verification-completion <= cutoff, reports signed raw BTC/ETH totals as context only; no absorption state, no independently attested PIT, no fallback to current pointer. CN readback exposes optional diagnostic, not official decision. Existing backtest_engine/etf_pit_replay.py ISSUE_1211_D1_D7 requires separate observed verification-completion proof; do not conflate. Leverage liquidation/reclaim remains blocked, OI/funding not substitute. Fresh CI required.

### Existing liquidation owner recovered and optional source cohort (M03/M04/M08)
Recovered ratified Pullback Forensics Passive Pilot v1 and collector v1.1; existing 5x/day live anchor capture stores exact OKX BTC/ETH SWAP executed liquidations with normalized units, lower-bound aggregates, raw event persistence, dated run and source receipts. Completeness is explicitly unverified, receipt time is request START, not completion. Added pinned optional context reader (historical LATEST at exact row source commit + identical dated run, hash, ancestor, receipt clock, instrument and lower-bound checks). It exposes archived aggregate context only; no clearance, reclaim, independent PIT, or outcome claim. Existing CN consumer now attaches context alongside ETF; optional coverage census in full native test job replays same original cohort and counts distinct ETF sessions/liquidation captures without new calls or writer. Four adversarial tests and real W47 check. No new source scheduler. The original liquidation owner exists but complete sequence 3 remains blocked until price stress/reset/reclaim transforms and independent known-by proof are frozen. Next: run native full cohort coverage and verify outcomes via original owner receipts plus path byte replay, then preregister matched delay-cost evaluation. No merge.

### Outcome owner source-byte replay (M03/M05/M06)
Added read-only audit of existing matured outcome receipts at pinned checkout. Reuses existing receipt gate and owner continuous path/endpoint/statistics functions, validates actual Git source bytes and ancestry, frozen row baseline, exact continuous path and count, BTC/ETH/ETHBTC return/MAE/MFE, rejects mismatches and retains explicit missing/orphan counts. Separate native research test emits PINNED_OUTCOME_COHORT; source failures stay blocked and are not silently scored. This is research evidence census, not production gate weakening or delay-cost verdict. Outcomes never enter feature-side projection. Next inspect native outputs and resolve rejected paths before matched comparison. No new workflow, collector, paid call, canonical change or merge.
