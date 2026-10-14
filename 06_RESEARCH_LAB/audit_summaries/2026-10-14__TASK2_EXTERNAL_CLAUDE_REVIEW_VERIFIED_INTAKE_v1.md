# Task 2 · External Claude Scientific Review — verified intake receipt v1

**Received and audited:** 2026-10-14. **Source:** user-supplied `TASK2_COMPLETE_RESEARCH_AND_CLAUDE_REVIEW_2026-10-14(1).zip`; bundle SHA-256 `bc2725e4959dc7377629a10320861722ebae67f1774311d44fabad1035e4f954`. **Class:** `PUBLIC_SAFE_RESEARCH_INTAKE / NO_HINDSIGHT / NO_NEW_OWNER`. **Status:** `PARTIAL_SOURCE_CHECKS_VERIFIED__R1_LIVE_PIT_BLOCKED__NO_NEW_R2_TO_R7_EXECUTION`.

**SOURCE PRECEDENCE:** current `AGENTS.md`, `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`, canonical [Task 2 handoff](../../04_MARKET_LEARNING/handlekompas/research/2026-10-13__TASK2_FULL_STACK_NO_HINDSIGHT_AUDIT_WORK_HANDOFF_v1.md) and existing Task 1.5 [#1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596) / EDGE [#1530](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1530) / Compass [#1553](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1553). Claude's direction to write only to Audit Bridge has **no authority to override** its current **PAUSED/MANUAL_ONLY** governance. This is an additive public-safe intake, **not** a Claude bridge call, new control tower, workflow, paid data request or signal change.

## 1. Exact artifact provenance — 8+8+1 packaged source files

ZIP contains: 8 original research PDFs; 8 Claude review files (peer review, five P0 designs, 91-claim CSV, E1–E16, handoff, README, power code and output); 1 new start-here note; plus a 17-entry SHA manifest. **Every 17/17 embedded member hashes and byte counts matched** direct SHA-256 recomputation. ZIP itself SHA-256 above; its bytes remain outside the public control plane.

| PDF | ZIP member SHA-256 | Critical provenance treatment |
|---|---|---|
| R01 No-hindsight framework | `984a3db08bb81166b2f7eaf19390b72e905b3b0f74b83c2652cf6ff248dfd46a` | Retrospective audit claims require original predictions and outcome receipts |
| R02 MAEVE | `b223e08ff91226a6aed96056c6141c2438ca99857b9f01b620cf9ff85416b1ef` | Parent ≠ fill; DCA and after-entry CFGI must be time-adjudicated |
| R03 Historical data | `110e188d3a2c81c1796566310f879fbf1c4190db22b5e7f18d735655dbb5ed59` | Reported archive coverage ≠ as-of source first-known |
| R04 CFGI | `198fb059396338b02681addc34f6743a232648dff1cf765cfc7f88e6ee17ffb4` | Vendor engine era and per-row source vintage required |
| R05 Pullback | `cbf4ad591018ccde5c938f6dcb3a76c91f61d7ead8e4aefa3b2542b0f43f57a5` | Scope-limited negative test; cannot generalize to all regimes |
| R06 Derivatives | `6aae0656031eb8bee5151009e27e08b8359921978e88a3bd01134bf5058a1b90` | Six documented experiment sketches ≠ 20 actual runs |
| R07 Rotation | `31de1102fa4e9c46d1cb5e2ab757525dcdf9d5c4ee0b86f8cea90f637fb8370f` | Original issued 2021 CN not authenticated; ten sketches only |
| R08 AI Edge | `97f8ca31c73d59a008419db64b4bedbcc8cc62fcf69c25581c3494ab1398b2df` | AI ablation/result claims require actual original logs and replay |

**Exact external reviewer inputs:** `03_Claim_Provenance_Ledger.csv` SHA-256 `d1e78022b1d2cb1c48fa4d6aed9c110d481e2ba6565a8804a4d905a65a96c11f` (**91 distinct L001–L091**, reports R1:20, R2:14, R3:11, R4:9, R5:10, R6:5, R7:10, R8:7, BRIEF:2, MEMO:3); E1–E16 document SHA `805c4f7db8b0cd48c049b5ae56dc6e7f74846a6ce9ab938cb1ddd1d753f`; five P0 protocol SHA `a766e519d6412a0ed0fc024eb94ffaec8e960dfe70ffb3d9214d3a5e67bb77bd`. Claude never independently authenticated GitHub or restricted source data. Its 70/40/55/15/25 percent claimed P0 success probabilities are subjective and **not** empirical.

**Versioned companion receipts:** [91-claim status ledger](2026-10-14__TASK2_EXTERNAL_CLAUDE_REVIEW_VERIFIED_INTAKE_v1_CLAIM_LEDGER.json) (preserves all 91 original IDs, source pages and Claude's assessments **separately** from our independent statuses); [E1–E16 + P0-1…5 gate matrix](2026-10-14__TASK2_EXTERNAL_CLAUDE_REVIEW_VERIFIED_INTAKE_v1.json). Source verbatim claim text stays in the original user ZIP; **no private raw values or user PDF binary copied publicly**.

## 2. Verified actual checks (not merely echoed from Claude)

### E1: Git SHA history chronology

GitHub read-only REST commit lookup independently resolved all eight **specific** reported prefixes, with exact UTC committer clocks:

| Repo | SHA prefix | UTC timestamp |
|---|---|---|
| Archive | `fa75ad5a` | 2026-10-13 19:35:44 |
| Archive | `a7387d5e` | 2026-10-13 20:16:30 |
| Archive | `86ac5704` | 2026-10-13 21:17:47 |
| Archive | `0556486b` | 2026-10-13 21:45:16 |
| Archive | `05f9daba` | 2026-10-14 06:06:59 |
| Private `secrets` (metadata only) | `2a331f90` | 2026-10-13 15:44:08 |
| Private `secrets` (metadata only) | `7e329eb2` | 2026-10-13 19:41:43 |
| Private `secrets` (metadata only) | `dc4dfdd0` | 2026-10-13 21:04:34 |

These are **chronological snapshots**, not contradictions. Main head, private head and Bridge head are pinned in companion JSON **only at readback time**; do not substitute them for the future current state. No private source values were read for this step. E1 complete original source–issuance–outcome lineage still blocked.

### E5: CN 2021 vs 2026 — historical reconstruction is not frozen publication

Public `canonical-project-archive/06_CYCLE_NAVIGATOR/published-x-posts/CN_001_PUBLISHED_X_POST_2026-03-30.md`: original copy labels week **March 30–April 6, 2026**, but its own header states **2026-07-05 import**, X/Grok/user-supplied recovered text and **week range inferred**. GitHub independently confirms that file's **first path commit `b9d867ddc10c967338c1dabaa64c5bd4bf102613` was 2026-07-05 20:32:52Z**; file blob `203268f206612647209e4fc1653fedf6e02fdafd`. The recovered post includes **forecast→actual retrospective score text**, not an independently time-attested pre-outcome original freeze.

The 65-week range/envelope experiment at `05_CYCLE_NAVIGATOR/calibration/2026-07-08__cn-rd-audit-regime-phase-range-calibration__canonical.md` is a **historical research baseline**, NOT 65 original issued Cycle Navigator publications. GitHub's public register records #1 (March 30), #9 (May 25), #15 (July 6); modern machine issue numbers migrated and do not equal actual public series. No independent source has yet proved **original issued Cycle Navigator forecasts from 2021**. This is `UNVERIFIED_ANACHRONISM_RISK`, **not** a demonstration that no external 2021 precursor ever existed. Reject 2021-CN historical scoring unless independently frozen original first-known receipts are found.

### Power: executable reviewer's arithmetic reproduced exactly, but not inference

Executed uploaded, inspected `06_power_calc.py` in an isolated Python environment; process exited **0**. Its standard output **exactly matched** bundled `06_power_calc_output.txt` (2015 stripped characters; source SHA-256 `e009b98ec59fcc49c26fc620133acec70df192f3dde3e3dda259fe823c42a538`; supplied output SHA `05cc16fbb5c07e9ff2150f3416bf8f27126605e58089c40778367fd7a86c5308`). Example: normal approximation for 46 vs 45 independent observations and Bonferroni /42 yields model MDE `d≈0.86` / AUC `≈0.73`. This is **NOT a measured AUC, achieved real power, a sufficient scientific cutoff, or proof of any model's null**. Effective N may be dramatically lower because episodes are clustered; assumptions were NOT independently verified. Scoped R5 negative results must be preserved as reported, but `FALSIFIED_IN_ALL_REGIMES` is unjustified.

### E9/E16 and existing R1 integrity work

Existing public Task2 research intake records the CFGI vendor statement of the upgraded scoring engine from **2026-07-08**, old v2 Madrid-local vs v3 ISO-UTC clock treatment, and *2025-dated* 478 selected BTC/ETH 1h observations **retrieved retrospectively in Aug 2026**. They are useful historical research data, not automatically PIT-valid original 2025 decision inputs. Contemporary October 2026 original v3 Compass archive had 36/36 selected CFGI fields with `retrieved_at <= forecast_issued_at` across nine overlapping 12h-outcome examples; the upstream per-field first-known still unverified.

A separate source timestamp semantics defect already appears in [the R1 Clock audit](../../04_MARKET_LEARNING/handlekompas/research/2026-10-14__TASK2_R1_NATIVE_V3_FEATURE_CLOCK_AUDIT_v1.md): 12 OKX funding `observed_at` entries actually point to **scheduled settlement** rather than quote retrieval. **Claude's P0-1 instruction that funding is first knowable only *after settlement* is too coarse:** current funding quotes may be published before their future settlement time. Keep captured quote-first-known separate from settlement, and do not falsely call future settlement `observed_at` proven lookahead.

At intake time PR #1614 was still **OPEN**; the old prefix `05f9daba` is a real 2026-10-14 06:06Z historical commit, not current main. Prior pinned R0 36/36 Git source objects with 16 changed / 20 unchanged are public **object-integrity** receipts, not historical source accuracy. Existing R0 verifier PRs (#1614, #1617, consolidated #1627) require refreshed live reviews; not merged or superseded merely because this review packet is filed.

## 3. Claim court — what this changes in Task 2

- **R6 derivatives**: vendor datasets and OI/funding hypotheses may be plausible; reported successful/failed experiments remain **`UNVERIFIED_CLAIM`** until actual source data, parameters, code commit, run outputs and independent event-family counts are bound. Six specified sketches ≠ 20 completed tests.
- **R7 rotation**: alleged original 2021 CN forecasts, 30–40% exit accuracy, and 2026 price examples remain **`UNVERIFIED_CLAIM`**; ten sketches are specified, later ellipsis does not supply ten experiments. Historical directional prediction should be compared only on actual issued receipts.
- **R8 AI-vs-rules**: alleged level-3 vs level-8 wins and confirmed ablations lack original log receipts in the report. **`NOT_ESTABLISHED` ≠ `FALSIFIED`**; nine described hypotheses / ten deliverable packets do not equal twenty executed experiments.
- **R5**: predecessor bounded Round-2 adverse event samples (46 anchors + 45 matched controls, 11 reload strategies no documented HOLD beats in their specified trials) are **scoped historical findings**; do not re-label closed data as untouched OOS or infer robust global no-edge.
- **MAEVE R2**: 432 parents, 1073 fills and 641 DCA legs need matched parent-level NONE/ENTRY/EXIT opportunities and original provider entry-time component snapshots. Fills are not independent parents; later `analisis_hora` is suspected post-entry leakage. A descriptive DCA profit rate is not proven economic entry skill.
- **CFGI R4**: limited selected historical windows (478 BTC/ETH, 0 MARKET in those specific event windows) and short retrospective component vintages cannot establish broad cycle-general incremental edge; use contemporaneous forward captures and strong same-clock price+volume+vol baselines.
- **Report dependence**: R1/R3/R4/R5 reuse portions of the same audit/source families; cross-report agreement does not multiply independent observations.

## 4. E1–E16 and five P0 studies — strict admission decisions

The companion [E1–E16 matrix](2026-10-14__TASK2_EXTERNAL_CLAUDE_REVIEW_VERIFIED_INTAKE_v1.json) documents a separate factual status and next proof for every E1–E16. Here are the decisive gates:

| Existing protocol | Verifiable preparation from this intake | Scientific status |
|---|---|---|
| P0-1 · G0/source clocks & original family registry | ZIP integrity, eight old Git commit SHA clocks, first CN archival source, reproducible reviewer power arithmetic | `PARTIAL_EVIDENCE_CHECKS_EXECUTED`; family compiler, MAEVE timestamps and full clock census **BLOCKED** |
| P0-2 · BTC/ETH exposure-matched placebo + HOLD/SMA/vol target | Fee assumptions and design inspectable in attached protocol | `DESIGN_ONLY`: requested continuous 2017→ source history not verified (known current free price panel metadata from **2020-09**); no untouched holdout certified |
| P0-3 · MAEVE DCA parent counterfactual | Parent-level design and prior source inventory available | `BLOCKED_PRIVATE_ENTRY_CLOCKS_AND_MISSING_OPPORTUNITY_DENOMINATOR` |
| P0-4 · Original CN interval/Compass benchmark | 2026 recovered post chronology independently narrowed; 65-week ATR study distinguished from actual issuance | `BLOCKED_ORIGINAL_PRE_OUTCOME_PUBLISHING_AND_COERCED_HORIZONS` |
| P0-5 · Derivative OI/funding stress | Existing source owners/collectors identified; future settlement-time misuse separately diagnosed | `BLOCKED_SOURCE_VINTAGE_AND_20_INDEPENDENT_FAMILIES` |

**No P0 historical performance experiment in this external intake meets all scientific gates.** Do not pretend partial archival verification equals a run of P0-2, P0-3, P0-4 or P0-5. Claude's 48-hour checklist is an estimate, not a hard SLA and does not override Round3 `PROSPECTIVE_COLLECTION_ONLY`; hypothesis testing/outcome scoring remain OFF.

## 5. Next execution round — only existing owners; highest scientific value first

1. **P0 G0/E5+E1:** recover earliest *independently published/frozen* CN originals, explicitly distinguish July-recovered posts from issued-in-week sources, reconcile 65 week research and 142 freezes vs actual public series, and produce independent Git source clocks.
2. **P0 G0/E2+E3:** locate exact closed Round-2 compiler/catalogue and its immutable source data, reproduce `family_id` checksum **twice** without selecting/trading on those learned windows; publish scoped negative and complete multiplicity counts, not re-mined winners.
3. **P0 MAEVE E7+E8:** 20–30 stratified parent-entry time-locked provider snapshots with ENTRY vs `analisis_hora`; value-free public receipts, original private rows stay private.
4. **P0 R1/CFGI:** adjudicate native 2026 first-known/Capture/engine and all missing/abstention attempts against original models; then pre-register `price+momentum+vol+volume` vs `+CFGI` composite vs non-price components on separate independent event families.
5. **P0 E10:** derivative asset×venue×field×native-cadence×first-known/gap census only. No derivative historical edge claim until PIT and ≥20 independent families; keep Round3 collection-only.
6. **P1 E11+E12:** evidence-court named R6/R7/R8 historical test claims and original AI model/prompt/temperature/latency/output SHA; do not invent missing logs, and do not conflate model identity with runtime tracking.
7. **P1 E13:** reconcile all previously tried hypotheses and 144 frozen variant families in the **existing** trial ledger. No previously studied period may be resurrected as prospective untouched OOS.
8. **P1 P0-2:** a reproducible **exploratory** price-only baseline on honestly covered dates may be run by existing owner when fixed trial parameters, data archive and matched exposure costs are admitted; do not call it the specified 2017–2026 untouched test unless that complete tape actually exists and remains untouched.

**No new automations, new owners, API-credit spending, Bridge polling, historical outcome rewrites, trading/portfolio actions or production model changes.** Independently verified **economic AI framework edge remains NOT_ESTABLISHED**. Positive, negative, blocked and unresolved outcomes will continue to have distinct source-bound statuses. This receipt is a bounded, completed external scientific intake; Task 2 remains underway.
