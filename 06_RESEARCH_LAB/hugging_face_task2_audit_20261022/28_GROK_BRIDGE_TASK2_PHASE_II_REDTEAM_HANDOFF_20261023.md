# 28 | GROK BOT → TASK 2 PHASE II: adversarial research handoff

**Prepared:** 2026-10-23 · **Owner:** existing Task 2 scientific issue [#1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596) · **Research stage:** PROPOSED_BRIDGE_ADVISORY_NOT_DISPATCHED · **Release:** none.

## Decision and why Grok

Use the already approved Grok Bot as an **independent falsification researcher**, not another framework builder or signal forecaster. Ask it to attempt to disprove a small set of specific Task 2 scientific claims and to identify the cheapest *new information* that actually changes the research decision. Research, not repetition, is the deliverable.

**Preferred allocation:** one bounded deep review in the EXISTING provider-native routine `Investering · Grok Daily Intelligence` (09:30 Europe/Copenhagen), or one owner-initiated interactive Grok session if the routine is unavailable. Existing provider skill: `investering-framework-audit`. No additional routine, supervisor, schedule, queue, GitHub workflow, paid API, external subscription, GPU or GitHub private CI dispatch.

**Important current operational distinctions as of 2026-10-23:**

- Bridge `Donh91/Investering-AI-Audit-Bridge` is PRIVATE. At observed main `9334fa42042e7578f041ce09e365f5dcb1454128`, `governance/GROK_CLIENT_STATE` reads `ACTIVE`; `decisions/GROK_BRIDGE_WRITE_RELEASE_V1.md` authorizes Grok's exact add-only Markdown report/branch/PR delivery. The account-scoped GitHub connection is **SOFT_GUARDED_UNISOLATED**, not an isolated fine-grained credential; only behavioral target checks limit it.
- [Bridge PR #56](https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/56), head `a23e29119047c1921086881984429ff89d149077`, contains the separate Shadow/C2/phase-activation task. [Bridge PR #55](https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/55), head `bd0779ae4561532c2e0246ee9795ec7ffbf6a796`, contains TechDev/long-range research. Both remained OPEN **unmerged**, so the *main* inbox contained only README at this checkpoint. **Do not present either as automatically delivered.**
- [Bridge PR #58](https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/58), head `bbbd01eb545ebb13ff8f55df3e9f4e424f8e90c7`, is an owner-initiated interactive Grok-style report stating the existing scheduled routine failed on October 21–23 for provider usage exhaustion; this is the report's statement, not provider-runtime telemetry independently verified in this document. [PR #57](https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/57) likewise demonstrates interactive report delivery, not successful scheduled intake. Check native provider state on next run.
- Bridge PR #58 identifies a stale stop-condition in #55: "Grok inbox remains PAUSED". Its older wording must be reconciled against authoritative current `GROK_CLIENT_STATE` before provider consumption; do not read it literally as an always-on kill switch. Changes to #55 still need owner/integrator review and normal GitHub rules.
- The current owner/ChatGPT and Supervisor, **not Grok**, control adjudication, code changes and merges. Bridge research reports never count as formal GitHub APPROVED.

## Immutable Task 2 source anchors and anti-hindsight facts

Before substantive work, re-read current Archive and Bridge `AGENTS.md`/owner policy, obtain each current SHA40, and compare with these immutable checkpoints. If newer authoritative work supersedes them, explicitly re-pin; preserve originals as historical evidence.

| Reference | Pinned source or exact Git blob | Research significance |
| --- | --- | --- |
| Task 2 existing research PR [#1747](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1747) | head `4b093105b7a69c3127f889cf4637f67e4cb074b2` at preparation | Draft, *not* merged or canonical scientific release |
| Original Oct14 records | public main `5fd81f3714e95198cfc731e7db6b1404056a51e1` | Six original forecast/outcome 12h pairs |
| Original native engine | `scripts/data_ping/native_handlekompas.py`, Git blob `d00d38bed517861fa2487dce42d330bf05812f6d` | Same engine file checked at six Oct14 original source commits |
| Evidence #23 | `06_RESEARCH_LAB/hugging_face_task2_audit_20261022/23_SOURCE_CUSTODY_AND_SCOPED_DEVELOPMENT_20261023.md` | Eleven Oct12–13 v3 source replays and exposed diagnostic |
| Evidence #25 | `06_RESEARCH_LAB/hugging_face_task2_audit_20261022/25_PHASE_II_OCT14_SOURCE_AND_TARGET_CLOCK_CENSUS_20261023.json` | Six source snapshots; five capture jobs; 6/6 before-issue logs; distinct issue-to-target lead |
| Evidence #26 | `06_RESEARCH_LAB/hugging_face_task2_audit_20261022/26_PHASE_II_OCT14_B2_EXPOSED_DEVELOPMENT_20261023.json` | Oct14 six issued: 2 DOWN, 2 MIXED, 2 UNAVAILABLE; four direction slots; model and B2 both 4/4, zero paired lift |
| Evidence #27 | `06_RESEARCH_LAB/hugging_face_task2_audit_20261022/27_PHASE_II_NEXT12H_B2_STRUCTURAL_IDENTITY_20261023.json`, blob `2d6363e6b92b09b783e2782eeefc298c24aed455` | Structural B2-equivalence hypothesis, source trace, 256-state *logical* sanity check, not full runtime replay |
| Original funding metadata repair [#1749](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1749) | head `238c7d67b0c6c1ce951fd06183eba6e6e64254ee` | Fix to distinguish scheduled OKX funding settlement from quote observation; DRAFT/unmerged |
| Existing Shared Row [#1738](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1738) | merged original head `b443a88e5b42a3cecd99f04ee9b0de5249e17376` | Already owned by pending Bridge task #56, do not duplicate its primary assignment |

**Factual research state:** Original Oct12–13 matched development cohort: 16/16 B2/Compass direction agreement, 7/16 correct for each, zero paired lift, one overlapping connected event block. Oct14: 6 issued, 2 DOWN, 2 MIXED, 2 UNAVAILABLE, 4 matched BTC/ETH directional slots both correct 4/4, zero paired lift, one overlapping connected block. Both old-hourly (>180m) October 14 scheduled forecasts were **originally marked STALE_OR_UNAVAILABLE + UNAVAILABLE/NO_EDGE**, so do not wrongly claim a silent stale-source failure. Two nominal '12h' source-reference targets left 7.074h and 8.204h of actual issuance-to-outcome lead time. Full original R1 information admissibility is still **NOT_ADMITTED**. Round 3 private outcomes are **OFF**.

## Research mission: G1 → G2 → G3, one bounded review per run

### G1 — Falsify the structural B2-equivalence finding (highest priority)

**Exact question:** Is it true, for the *original* issued NEXT_12H code, that conditional on an issued `UP` or `DOWN` prediction the per-asset B2 prior-packet sign is mechanically identical to the issued direction?

1. Inspect **actual original** Python source at the pinned blob, especially `_delta_pct`, `derive_market_now`, `owner_freshness`, `horizon_map` and `evidence_snapshot`; trace the producer call chain and original forecast JSON. Distinguish the logical 256-state test from a real runtime replay: neither is the other.
2. Independently try to construct at least **six adversarial counterexamples**: BTC/ETH discordance; zero/no-price-update; missing/NaN delta; unhealthy/future/stale timestamp; old packet reissue; diverging per-asset horizon or hidden overwrites. Show actual test execution if feasible; otherwise provide a precise deterministic fixture/test command marked `NOT_RUN`.
3. Identify any code-path/version/dependency conditions under which an original UP or DOWN can legitimately diverge from sign-of-delta B2. If none, label `STRUCTURAL_IDENTITY_SUPPORTED_WITH_SCOPE` and recommend **STOP evaluating directional correctness lift against same-feature B2**; use another independent baseline and separately assess coverage/abstention.
4. Explicitly distinguish *identity of forecasts* from their **absolute forecast skill** and whether abstention filters protect users. Do not award edge for the structurally forced agreement.

**High-value output:** precise source path/line/blob + PASS/FAIL/UNKNOWN per counterexample, minimal reproducer, residual unknowns; one correction to the current methodological conclusion **only if falsified**.

### G2 — Adversarial R1 clocks, denominator and actionability audit

**Exact question:** What is the next smallest **original** evidence item that could move a bounded source/forecast relationship into R1 admissibility, with absolutely no hindsight?

1. Select the original October 14 sources by **pre-existing non-outcome criteria**: prioritize clearly issued directional rows and separately preserve MIXED/UNAVAILABLE. Never select on realized correctness.
2. Inspect original source-snapshot Git membership, hourly retrieval clocks, five original successful capture-upload job logs, actual packet-generated time, source server first committed/publication proof, original code dependencies and frozen original issue clock. Capture upload **is not** identical to packet publication and is not vendor original first-known.
3. Independently challenge the Oct14 receipt's `24 selected-feature` inventory. It is a feature index, **not** proof that all 24 fields were causally used in NEXT_12H; identify the actual decision inputs and separate contextual attribution from decision logic. Highlight unavailable original provider first-known/response evidence and malformed future scheduled funding clocks without retroactive repair.
4. Test that six Oct14 original targets form a single overlap block; one block is **not** six independent shocks. Define a simple dependence-aware unit of analysis and an **untouched** prospective follow-up, not a post-hoc fake holdout.
5. Keep the original 12-hour **reference-window** horizon separate from actual issue-to-target lead. Negative fixture: an old-but-PASS cached source must not become a falsely new forecast; an original `STALE_OR_UNAVAILABLE` issue must remain an abstention. For information-edge R1/R2, owner delivery is **not universally required**; for investor-economic R3, first actionable delivery and realistic fills/costs are required.
6. Produce the smallest original-evidence-request matrix `path | SHA | needed clock | authoritative original receipt | failure reason | likely recoverable? | owner`. If source clock cannot be reconstructed, `NOT_IDENTIFIABLE`, no fabricated values. **No raw private-secrets repo reads or provider values.**

**High-value output:** a ranked ≤5 item R1 unblocker list, realistic feasibility and exact authorized owner actions, not another generic 200-line gate summary.

### G3 — Research redesign: what *would* add independent value?

**Exact question:** After eliminating the same-signal B2 directional comparison, which *single* next test gives the best expected information gain for Kompas?

Keep the existing R0–R7 architecture and existing Task 2 #1596/Shadow #56/Compass #1553/#1516 ownership.

Propose no more than **three ranked alternatives**, each with a cheap independent control, required original source availability and clear falsifier:

- **Primary:** original issuance/abstention utility: compare whole-population coverage-aware deterministic controls versus original Compass, including MIXED, NO_NEW_OBSERVATION and UNAVAILABLE, false positives, false negatives, response latency and *when the source actually became available*. An abstention has risk/foregone-opportunity implications, not automatic performance credit.
- **Second:** original CN-conditioned 1–3d and 5–7d forecasts vs independently specified matched-clock cheap baselines, only after original CN decision projection and source-clock admissibility. Never silently reconstruct later CN values into historical issues.
- **Third:** prospective same-row simple-trio vs Shadow-only with proper prior-version/feature availability and independent event families. **Bridge #56 already owns detailed Shadow C2/phase-validator work; refer to it rather than repeating its audit.**

For each alternative specify research hypothesis, adverse control, source/clock, cohort and missingness, nonindependence/embargo, immutable preregistration before future outcomes, outcome maturity, implementation complexity, minimal economic relevance and **kill criterion**. Mark `NOT_ADMITTED`, `READY_FOR_PROSPECTIVE`, or `DEVELOPMENT_ONLY` without upgrading science.

### Outside scope / deferred

TechDev reconstruction and long-range visuals are already queued in **Bridge #55**. Shadow July C2 historical sequence and phase gate are already queued in **Bridge #56**. Alpha/X signal credibility is relevant after scientific source admission or for a distinct Alpha owner request; do not introduce unbounded social/X scans into this Task 2 Phase II review. No duplicate Shadow gauntlet.

## Delivery: ONE report usable by ChatGPT

Write a **single** evidence-dense advisory Markdown report, target **≤5,000 output tokens** and **one deep technical review** (provider usage constraints are not an entitlement guarantee; abort if remaining credits are insufficient). No paid APIs; use original authorized GitHub read tools and local deterministic tests only.

Report sections (exact names):

1. `EXECUTIVE_VERDICT` — 3–6 sentences, what was disproven / not disproven.
2. `SOURCE_PIN_MATRIX` — exact SHA40, paths and code lines, source clock semantics.
3. `G1_COUNTEREXAMPLES_AND_TESTS` — ≥6 adversarial cases, command, actual PASS/FAIL/NOT_RUN; distinguish logical proof versus actual Python replay.
4. `G2_FIRST_KNOWN_AND_CUSTODY_GAPS` — original source and issue timing, fail-closed uncertainty, no post-hoc repair.
5. `G3_NEXT_MARGINAL_EXPERIMENT` — ranked max three with real decision delta.
6. `NEGATIVE_RESULTS_AND_REJECTED_HYPOTHESES` — explicitly state where no novel signal or useful implementation exists.
7. `FIRST_FINITE_NEXT_ACTION` — exactly one small action, exact owner/issue/path, evidence needed and stop states.
8. `DELIVERY_AND_AUTHORITY` — exact report PR URL/HEAD, audit SHAs, test status, advisory-only; `R1_NOT_ADMITTED` unless independently verified evidence warrants a separate governed scientific ruling.

Every material assertion must carry `VERIFIED_BY_SOURCE`, `LOCALLY_REPRODUCED`, `HYPOTHESIS`, `UNKNOWN` or `BLOCKED` labels. Do not claim formal GitHub approval or completed runtime implementation.

Report transport: only create a **NEW** file `reports/grok/automated/YYYY/MM/*.md` on a **NEW non-main branch** and ONE PR to `Donh91/Investering-AI-Audit-Bridge`, after checking `GROK_CLIENT_STATE=ACTIVE` on actual Bridge main. Follow `governance/GROK_CLIENT_PROTOCOL_V1.md`, including exact YAML `GROK_ADVISORY_REPORT_V1`, `body_sha256`, filename/path construction and `tools/grok_report_preflight.py`. **No writes to the public Archive, secrets, other repositories or Bridge main; no edits to existing Bridge files, task inbox or registry; no formal approvals/merges, tools usage expansion, provider bypass, new Routine or trading.** If provider quota is exhausted, policy not active, bridge PR creation fails or external scope would be required, STOP with `BRIDGE_DELIVERY=FAILED_OR_BLOCKED` and return a copyable report in Grok chat.

**Provider runtime status:** a pending Bridge inbox PR is not provider delivery proof. If #56 or #55 have not been safely merged, or the existing saved routine cannot be confirmed to read updated instructions, classify `PENDING_PROVIDER_INTAKE`. Do not claim Grok has accepted this assignment just because this Archive research note exists.

## ChatGPT / Supervisor consumption contract

1. Existing #1156 Supervisor checks new Bridge Grok report PR at exact SHA, verifies path-only diff, body SHA256, source SHAs, real tests and independence of author; performs report preflight before any merge.
2. Existing #1596 scientific owner adjudicates each Grok claim as `ACCEPT`, `MODIFY`, `REJECT`, `NOT_IDENTIFIABLE` or `PROSPECTIVE_TEST`. Same-source agreement with ChatGPT does not establish external independence.
3. For any accepted **new** reproducible finding, issue the smallest existing-owner research/test delta under #1596 and existing Task 2 PR #1747 or a separately required reviewed PR. Bind it to exact original sources; do not rewrite original issued predictions/outcomes.
4. #1156 handles integration only under original GitHub security/review/CI and destructive-authority separation; no advisory report bypasses a protected branch.
5. Preserve Bridge report and ChatGPT adjudication independently; `REPORT → VERIFY → ADJUDICATE → BOUNDED TEST → NORMAL GOVERNED PR → MAIN READBACK`. No silent auto-consumption, automatic production promotion, model-weights changes, Shadow activation or private Round 3 inference.

**Expected value:** find the first genuinely independent comparator or narrow evidence gate that changes a science decision. **Kill rule:** if G1 reconfirms structural equivalence and G2 cannot recover original first-known, reject repeat directional B2 comparisons and prioritize fresh prospective source-bound independent episodes. Do not spend more Grok quota on redundant agreement.