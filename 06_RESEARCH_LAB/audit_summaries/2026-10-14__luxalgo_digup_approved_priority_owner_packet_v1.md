# LuxAlgo + DigUp — approved zero-spend owner packet (2026-10-14)

**Status:** SHADOW_ONLY / GOVERNED_OWNER_HANDOFF / NO_EXECUTION_OR_ALPHA_CLAIM  
**Owner:** existing Research Lab for source-level methodology; existing Cycle Navigator #1578, Experiment Lifecycle + Conditional Edge Envelope, and FMOS/Framework Learning for the three distinct consumer tasks  
**Decision:** user approved the ranked shortlist and the no-spend, incremental-value-first recommendation on 2026-10-14  
**Main source:** current GitHub main, owner source files read on 2026-10-14  
**Budget:** $0 incremental; 0 new permanent agents, GitHub schedules, market authorities, broker credentials or provider subscriptions  
**Production site:** no change. Existing main/site and sole vNext owner PR #1576 are untouched.

## One decision, five existing owner routes — do not create parallel queues

| Frozen order | Candidate | Existing owner and next gate | Current factual status and output | Stop / kill |
|---|---|---|---|---|
| 1 | LuxAlgo **Vela** as a *site chart library challenger*, not a signal | Cycle Navigator owner issue [#1578](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1578); design owner PR [#1576](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1576) | **PROPOSED_NONPRODUCTION_PROTOTYPE**. Compare exact current vNext chart UX against a **standalone isolated preview**, bound to the same public OHLCV fixture and official frozen weekly range/score. Browser QA is not yet done and no frontend change is approved in this packet. | Any binding mismatch, forecast reinterpretation, licence/NOTICE breach, significantly worse iPhone rendering or unacceptable size/performance. |
| 2 | LuxAlgo **Edge Stats / Conditional Edge Envelope** | Existing Research Lab / Experiment Lifecycle owner of \`CONDITIONAL_EDGE_ENVELOPE_v1\` | **PREREGISTERED_BLOCKED**. Stage A (2026-09-14) froze 10 questions; Stage B (2026-10-04) says \`execution_authorized=false\`, \`outcome_queries_performed=0\`, 9 \`MAPPING_BLOCKED\` and 1 \`DUPLICATE_ACTIVE_OWNER\`. No outcome mining, queue jump or new experiment slot. | Insufficient PIT original-source evidence or owner mappings, no incremental benefit over existing evaluation, multiplicity/holdout invalid. |
| 3 | **DigUp-inspired hybrid retrieval** over existing FMOS, never as independent AI memory authority | FMOS \`00_FMOS/GRAPH_AND_RETRIEVAL.md\` + current Framework Learning retrieval owner | **FROZEN_QUESTIONS_NOT_YET_RUN**. 30 retrieval queries from 15 distinct file families now recorded under the same Research Lab shadow area at \`06_RESEARCH_LAB/forward_tests/2026-10-14__digup_fmos_retrieval_preregistered_queries_v1.json\`. Run current FMOS deterministic-first baseline before any challenger. Do not install DigUp in GitHub runners or index private data. | No confirmed missed high-value source, a false canonical/version match, unacceptable overhead, provider/privacy/license risk, or duplication. |
| 4 | LuxAlgo **Market Trackers** (public records) | Existing Research Lab source-admission and Situation Room/macro gap owner | **SOURCE_CANDIDATE_ONLY**. The inspected public \`LuxAlgo/market-trackers-data/manifest.json\` reported \`generatedAt=2026-09-07T15:13:09.121Z\`, CFTC COT \`rows=0\` and \`stale=true\`. First verify latest valid primary-source content and event-time/first-known/freshness, then whether it supplies a genuinely missing input; do not treat third-party \`stale=false\` as current truth. | No fresh coverage, ambiguous provider licenses, duplicative data, missing original source clock, or no measurable marginal insight. |
| 5 | LuxAlgo **PineTS** external strategy parity research only | Existing \`EXTERNAL_STRATEGY_REPLAY_LAB_v1\` proposal from LuxAlgo audit | **PARK_AFTER_Q1_GATE**. Prior qualification specifies Q1 terminal gate before Q2 execution; PineTS AGPL-3.0/commercial and Pine-v5/v6 compatibility claims require exact script-by-script parity tests. No new runtime dependency. | Parity unresolved, legal coupling too expensive or no unique replay benefit over current tools. |

## A. Vela non-production chart feasibility: exact two-arm check

*Existing CN source of truth:* \`05_CYCLE_NAVIGATOR/site/SITE_CONTRACT.md\`, \`05_CYCLE_NAVIGATOR/site/public-product.js\`, current official CN freeze/score pointers and vNext single-owner #1578/#1576. Current production must stay untouched.

**Arm B0** = existing preview's chart and published interpretation, measured on the exact same immutable OHLCV/weekly public data. **Arm C1** = single isolated Vela chart using its Apache-2.0 library with visible Vela NOTICE attribution. No live broker/order interface; no PineTS add-on. Pin upstream Vela commit and library version at *implementation*, verify checksum/licence before importing and record dependency delta.

**Freeze before screenshot/evaluation:** same BTC/ETH OHLCV bars, exact interval, UTC/timezone and day-close semantics; full input SHA/bytes; weekly freeze, ranges, scorecard pointers and timestamp; source-health/degraded classification. If the public data cannot be bound correctly, use a visibly labelled synthetic preview and do **not** call it parity.

**Acceptance:** both 390×844 and 430×932 iPhone; slow/fast network and low-end performance, resize and chart navigation; keyboard/screen reader/reduced motion, loading and offline fail-closed; bars + weekly range overlay and legend match B0 **without interpolated, revised or fabricated points**. Log initial render time, interaction latency, bundle kilobytes and source alignment and preserve screenshots plus reviewer verdict. No self-certifying a visual match.

**Output needed:** a bounded prototype commit/PR under #1578 after existing owner confirms non-overlap; independent visual/source review. Current site state remains authority. No new website or early deployment.

## B. Edge Stats Q1: preserve the already frozen scientific study

Verified:
- \`06_RESEARCH_LAB/audit_summaries/2026-09-14__luxalgo-mechanism-qualification-v1__shadow.md\`: prior Q1–Q6 method dispositions, including pinning \`LuxAlgo/edge-stats@7cfa6d52f561e2c764ba900252e80356b03af9fe\`.
- \`06_RESEARCH_LAB/forward_tests/2026-09-14__conditional-edge-envelope-v1__shadow-preregistration.md\`: CEE-Q01..10, nulls, trial budget, conditional vs unconditional baseline, controls, anti-p-hacking and source provenance.
- \`06_RESEARCH_LAB/forward_tests/2026-10-04__conditional-edge-envelope-v1__stage-b-mapping.json\`: **0 permitted outcome queries**, 0 executable mapped questions, 1 known duplicate. This is the current stop gate.

**Owner's narrow next step** is only to resolve original-source PIT + native evaluator/minimum-N/horizon definitions for each *already frozen* question, or record BLOCKED/DUPLICATE permanently. Do not replace a blocked question with a convenient proxy, retroactively tune, or relabel data capture as measured alpha. Once lawful, original-source evidence and queue slot mature under the existing Experiment Lifecycle, not a new LuxAlgo scanner.

## C. DigUp challenger: measurable retrieval, not another memory system

**Upstream inspected:** \`ARahim3/DigUp\` README, MIT LICENSE blob \`1e722998ff7d8d3d4685de111238805d5473078f\`, \`Sources/DigUpKit/Searcher.swift\` blob \`4d7b6def59be60219e3c92f807c9baeecf9399a6\` and \`evals/synthetic.json\` blob \`04b1d7563ccfb7fee60798e2d5403db28138ed43\`. Design uses keyword/full-text and multi-modal embedding, but their reported scores are developer claims, not transferable framework evidence. The Mac app is not an iPhone or GitHub Actions service; no install or source indexing authorized here.

**Framework baseline:** existing deterministic operational memory \`scripts/framework_intelligence/operational_memory_v1.py\` serves prior *commit episodes*, whereas \`00_FMOS/GRAPH_AND_RETRIEVAL.md\` defines broader authority-bound source retrieval. Neither should be mistaken for the other. The evaluator must compare **the actual consumer path being improved**, preserving main-source precedence.

**Frozen evaluation:** JSON contains 30 DA/EN natural-language prompts across 15 independent authority/file families, each with exact expected *public* main path and observed original blob SHA. Two paraphrases within one family are **correlated**, never 30 independent wins. Scorer must report top-1/top-5 recall, MRR, family-level hit rates, owner/path/version correctness, false authoritative matches, latency, memory and incremental dollars (must be $0). Record exact baseline results and source HEAD before testing the same frozen questions on the challenger; do not modify queries after outcome inspection.

**Hard constraints:** never copy private \`Donh91/secrets\` evidence or wallet data into an external embedding service; never let a semantic match override source permission, chronological cutoffs or canonical ownership. Do not deploy permanent vector index, new cron, always-on model worker, extra processor or paid inference until the current consumer exhibits independently verified important misses **and** the challenger fixes them without regressions. Semantic retrieval is optional and never itself truth. Missing/changed path must be marked \`GROUND_TRUTH_DRIFT\` and reapproved, not rewritten silently.

**Acceptance and negative outcome:** at least one demonstrably previously missed high-value source correctly recovered, no false official/predecessor promotion or security breach, and reasonable resource costs. If deterministic already retrieves all 15 families correctly, classify \`NO_INCREMENTAL_VALUE\` and stop. A report of no new code is a valid result.

## D. Market Trackers original-source gate

Review current open public data and the primary upstream publisher separately: SEC EDGAR, FINRA, Fed communications, CFTC COT and other relevant official publishers. Record original publication UTC/first-known UTC, row-level timestamp and revision/correction semantics, geographic/market coverage, licence and permitted processing and incremental value against current first-party sources. Existing reviewed \`market-trackers-data/manifest.json\` was 37 days old at this research date; don't use it to infer today's values or an evergreen live feed. Never introduce a new required source into Situation Room or pullback logic as a side effect of cataloguing it.

## E. PineTS deferred replay

Review exact effective AGPL/commercial terms and compatibility for the requested integration mode before copying or linking. Use frozen public Pine source and framework-owned OHLCV; verify parity, unsupported constructs, timestamp alignment and execution costs. Do not place this after a false Q1 completion or grant order routing.

## Automatic continuation / queue truth

This packet is a **read-only method, prerequisite and owner mapping** on an isolated task PR. It **does not** constitute:
- an automatic executable queue intake, CODEX_READY receipt, merged instruction, permission to run outcome queries, completed Chart QA or completed data source qualification;
- authority to create an independent research priority queue, provider subscription, ongoing watcher, schedule or model router;
- user acceptance of any later live signals, forecast revisions or broker connectivity.

After independent review and merge, existing **Research Lab #1512** records method owners and deduplicates; **CN #1578** owns the bounded visual trial; **FMOS/Framework Learning** owns retrieval baseline and challenger maturity; **Experiment Lifecycle** owns CEE and potential PineTS slot. Each must produce \`source -> owner -> eligible next action -> actual execution/receipt -> consumer readback -> terminal or explicit waiting state\`. If an owner does not consume the note, show \`HANDOFF_NOT_VERIFIED\`, never \`DONE\`.

No active automation or supervisor has been modified by this PR. Existing queue continuity governance [PR #1616](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1616) is a separate proposed rule until merged.

## Sources & licence boundaries

- https://github.com/LuxAlgo/Vela — Apache-2.0 plus NOTICE visible Vela attribution on chart screens
- https://github.com/LuxAlgo/edge-stats — MIT; local OHLCV statistics not inherently predictive
- https://github.com/LuxAlgo/market-trackers and https://github.com/LuxAlgo/market-trackers-data — separate code/data terms to verify per dataset and vendor
- https://github.com/LuxAlgo/PineTS — AGPL-3.0 / commercial option
- https://github.com/LuxAlgo/luxalgo-mcp-server — MIT integration, not provider-data licence for paid products
- https://github.com/ARahim3/DigUp — MIT application source; Google model and transitive libraries have their own licences
- Current GitHub files as above; external vendors do not outrank current local authority.