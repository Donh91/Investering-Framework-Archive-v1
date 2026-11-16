# G1 Strategic Compass source census correction, 2026-11-15

**Owner-approved research scope:** PR #2162, G0/G1 public read-only source and provenance preparation only.
**Latest main read at start:** 6293fec633edde65470c9808bc0ae2409bd7dcc0.
**Status:** DOCUMENTED_SOURCE_CORRECTION, NOT_A_BACKTEST / NOT_NEW_SCIENCE_ROW / NOT_PROMOTION.
**Owner:** Existing Task2 #1596 + integrity #1827 + CN/Forward Path #1516; parent Market Anticipation #209.
**Supersedes a narrow G1 statement, not the frozen forecast sources:** The earlier audit reviewed only the most recent 2026-11-09 anchor and said no eligible long-horizon B1 was available. That is too strong for 21-30D issuance. Original 21-30D anchors and genuine maturity rows exist since October 5, but mostly abstain on BTC and sometimes predict ETH/ETHBTC DOWN. The absence of asset-specific 4-8W forecasts remains true for all inspected original anchors. These discoveries do not prove originally user-delivered issuance or economic edge.

## 1. Original issued anchor evidence in main, not synthetic model hindsight

**GitHub timestamp correction after Claude's independent v3 review:** `issued_at_utc` and git commit committer time can come from the SAME runner and do not prove independent server acceptance. The native GitHub producing workflow `created_at`/`updated_at`, or a check-suite `created_at`, is required. Until independently joined, all seven remain `SOURCE_FILE_PRESENT / SERVER_TIME_UNPROVEN / PUBLIC_DELIVERY_UNVERIFIED` for scientific admission. The original paths and declared issue times remain archive facts.

| CN week | Original anchor | Git blob SHA | Declared issued UTC | Original 21-30D market/BTC/ETH/ETHBTC | Original 4-8W |
|---|---|---|---|---|---|
| W41 | SC-20261005-f2800fe3e50d | 1ef7caa172530b05e15406575703103098b60b55 | 2026-10-05 06:14:07Z | MIXED / MIXED / MIXED / NO_EDGE | UNAVAILABLE |
| W42 | SC-20261012-150bdbb2792c | ffc3f09e531f58173e444edc9f2680e726a1e59e | 2026-10-12 06:32:25Z | MIXED / MIXED / MIXED / DOWN | UNAVAILABLE |
| W43 | SC-20261019-bfe8f75a6c13 | f8c50c223417549aa1d20d3de22fa7b92561c904 | 2026-10-19 05:19:14Z | MIXED / MIXED / MIXED / DOWN | UNAVAILABLE |
| W44 | SC-20261026-00f4bc172099 | c2dcbb5895e95fa446e4edc03fd4d5c5b52bdd75 | 2026-10-26 06:57:50Z | MIXED / MIXED / DOWN / DOWN | UNAVAILABLE |
| W45 | SC-20261102-c96cd50e9ea9 | 3c9d3f13138f249e82633666135ac5590a7a57e0 | 2026-11-02 08:19:08Z | MIXED / MIXED / DOWN / DOWN | UNAVAILABLE |
| W46 first version | SC-20261109-9ebca5ac05e4 | 39b7e753e811507906a2bfdde3bf6df410eb86f1 | 2026-11-09 10:33:42Z | NO_EDGE / NO_EDGE / NO_EDGE / NO_EDGE / NO_EDGE | UNAVAILABLE |
| W46 later version | SC-20261109-1e86e732812d | f6eb1b76abbaf5efbeaec399b355e395b11eff32 | 2026-11-09 10:52:40Z | NO_EDGE / NO_EDGE / NO_EDGE | UNAVAILABLE |

The two Nov 9 anchors are different preserved original versions, not seven independent weekly trials. Each frozen file has an own issue time and source fingerprint. A file currently on main is not by itself proof it was on main, consumed or publicly delivered before the event; that requires history and consumer receipts. W47 package, freeze and delivery pointer were NOT_FOUND on the inspected main, consistent with a week not yet issued on Sun 2026-11-15, not proof W47 will not be issued.

All scenario weights observed in these anchors have the source contract UNCALIBRATED_SCENARIO_WEIGHT_NOT_PROBABILITY (the spelling is exact without soft hyphen in source contract, see v1.1). They must not be scored as numeric calibrated probabilities.

## 2. Actual existing matured outcome receipts, no new calculated score

| Original anchor | Original existing outcome | Git blob SHA | Status already in source |
|---|---|---|---|
| 2026-10-05 W41 | SC-20261005-f2800fe3e50d_30d.json | b60096d63f8cbc78906ee1cedfa915828a988064 | FINAL_MATURITY, BTC and ETH MIXED both ABSTAINED; BTC realized -9.11%, ETH -15.16%; no claim the model forecast declines |
| 2026-10-12 W42 | SC-20261012-150bdbb2792c_30d.json | a8eb028dc7d601d9b21589f361cd655eaf3aaef0 | FINAL_MATURITY, BTC/ETH MIXED ABSTAINED; BTC -12.12%, ETH -18.96%. Original ETHBTC DOWN result CORRECT (within existing scorer). |
| 2026-10-19 W43 | SC-20261019-bfe8f75a6c13_21d.json | bcbff83a6a7923c8830ba891cc76225b582f3725 | STRATEGIC_CHECKPOINT, BTC/ETH MIXED ABSTAINED; ETHBTC DOWN CORRECT |
| 2026-10-26 W44 | SC-20261026-00f4bc172099_14d.json | d1063276759bb458e4cfdf727843aba0a2b0c29a | MONITOR_ONLY, BTC MIXED ABSTAINED; ETH DOWN and ETHBTC DOWN CORRECT |
| 2026-11-02 W45 | SC-20261102-c96cd50e9ea9_7d.json | b093333057c154e23201720c0ef21d7ec1d3ad15 | MONITOR_ONLY, BTC MIXED ABSTAINED; ETH DOWN and ETHBTC DOWN CORRECT |
| 2026-10-12 W42 | SC-20261012-150bdbb2792c_28d.json | 63e844fa5d1e2bedfbff88b8df870628d3891a37 | MONITOR_ONLY 4-8W, asset-specific forecasts ABSENT and results UNAVAILABLE_NO_ASSET_SPECIFIC_FORECAST |

**Scientific warning:** These rows overlap strongly, and a few correctly labelled ETH/ETHBTC forecasts are not an independent edge or mature 30d investor utility. In the existing source, 21d is a strategic checkpoint, 30d final maturity, 14d/7d monitoring; never upgrade monitoring to an end-horizon decisive success. Source-authoritative result labels were read, not recomputed. Model predicted MIXED and NO_EDGE are abstention, not falsely scored wrong/hit directional calls. All path/regime/rotation and breadth outcome categories named in v1.1 remain unscored pending their actual governed series/scorers.

**Frozen existing final-direction sample, not an independent model trial:** `30d FINAL_MATURITY` outcome files are present for **2 separate original weekly anchors (W41 and W42)**. BTC directional outcomes: **0** (both `MIXED` / `ABSTAINED`). ETH directional outcomes: **0** (both `MIXED` / `ABSTAINED`). ETHBTC directional final outcomes: **1** (W42 `DOWN`, existing scorer `CORRECT`; W41 `NO_EDGE` / `ABSTAINED`). Therefore total final directional outcomes across these assets = **1**, not a claim of independent predictive edge. All 7d/14d are MONITOR_ONLY and 21d is STRATEGIC_CHECKPOINT; none adds to that 30d count.

**Source SHA syntax lint:** Each actual Git blob SHA in both source tables above must consist of exactly **40 lowercase hexadecimal characters**, tested on the isolated PR branch before a release request. Git SHA validity is syntax only, not an owner provenance, source-first-known, or consumer delivery proof. The full 40-character W42 30d blob above was independently read from GitHub.

## 3. Concrete next legal G1 step, no activation of G2-G5

**Original-owner task:** Under existing #1827 and #1516, perform a bounded issuance/receipt lineage check for W41-W46, prioritizing W41/W42 first because their 30d outcome receipts exist, and W45/W46 because consumer/pointer and revised issue states matter.

For each original anchor: original Git first-add committer time (context only, NOT independent server acceptance), the producing workflow run `id/created_at/updated_at` or the GitHub check-suite `created_at` (server acceptance), CN package source SHA, final consumer receipt and actual delivery time if independently verified, scenario label/asset directions, the actual outcome receipt and due/observed time, missing first-known provider source, and whether any same-UTC mechanical B0 could be fairly computed. Record three separate facts: SOURCE_FILE_PRESENT, ORIGINAL_ISSUED_WITH_SERVER_TIME_PROOF, and PUBLIC_DELIVERY_VERIFIED. Do not equate them.

**Cheap independent falsifier:** For all seven anchor commits (W41 `498b1e7a`, W42 `300f8664`, W43 `ddad4afe`, W44 `ca7563d4`, W45 `ae6a3b5f`, W46 v1 `fc0f12f7`, W46 v2 `53315f7a`), use native producing GitHub Actions run `created_at/updated_at` or check-suite `created_at` and compare server receipt with the actual decision cutoff. If server acceptance/producer completion is later than the eligible decision cutoff, classify CURRENT_ARCHIVE_ONLY; if no independent server receipt, SERVER_TIME_UNPROVEN. Do not use the Git committer time to pass this check. The older frozen fields are preserved, no retrospective removal or editing.

If any W41/W42 original clock is eligible, the later scientific question becomes whether their high MIXED/NO_EDGE abstention rate and some correct ETH relative downside predictions can be improved by a sparse Shadow challenger **without excessive false positives or forfeiting profitable upside**, on untouched prospective future blocks. C1/2/3 family test stays blocked until identical source rows and external tier0-2 foundation evidence.

Existing ETF D5 pre-first-capture cutoff, ALFRED historical revisions, CMC BTC.D source convention, fixed Top100 breadth universe and restricted Round3 collection-only rules still stand unchanged.

## 4. Correction and record integrity

This document supplements, does not replace, the original G1 source audit and owner-approved v1.0 mission. It corrects only the overbroad inference that there was no historical 21-30D original issuance. It is NOT a new workflow, publication, model, official provider baseline score, paper trade, research edge, release permit or independent Claude approval.

**Minimum paired cohort gate:** If fewer than 8 non-overlapping source-eligible original issues exist for a fixed horizon by a registered owner-chosen future cutoff, mark B1 `INSUFFICIENT_EVIDENCE` and C4-vs-B1 `SOURCE_BLOCKED`; do not leave a new experiment indefinitely pending. This is a proposed preregistration threshold, not an authorization to score historical rows. C2/C3 must beat C1 on identical predeclared rows or be rejected; C4 is CONTEXT_ONLY without a native source-clock-qualified expected-policy-path series. No premature model selection.

**Next owners:** Task2 #1596 + integrity #1827 + Forward/CN #1516, parent MAR #209. Independent method review remains requested on Claude Bridge #173 with exact PR current head. Zero paid calls / no new automations / no trading / no main merge.
