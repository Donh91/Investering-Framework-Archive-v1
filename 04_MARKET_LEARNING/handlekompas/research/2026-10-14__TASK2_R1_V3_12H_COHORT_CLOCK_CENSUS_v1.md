# Task 2 · R1 12h Original Compass v2/v3 Clock Census · 12–13 Oct 2026

**Recorded:** 2026-10-14. **Evidence:** PUBLIC-ARCHIVE ORIGINAL-ISSUE/OUTCOME GIT METADATA ONLY. **Exact immutable sample commit:** `098c50d36b222c4c8ffa179a5879d36a74194bc4` (do not replace with moving main). **Status:** `PUBLIC_V3_ISSUE_OUTCOME_CLOCK_MATCHED__PROVIDER_FIRST_KNOWN_NOT_INDEPENDENTLY_ADMITTED`. Existing R1 owner [#1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596).

This is a **complete file-level census for the two specified issuance dates**, not the complete historical Compass population and not nine independent market-shock families. All counts below were read from the four pinned GitHub directories under `04_MARKET_LEARNING/handlekompas/official/{daily,outcomes}/2026/10/{12,13}` with contents fetched at the same exact commit. See [machine-readable receipt](2026-10-14__TASK2_R1_V3_12H_COHORT_CLOCK_CENSUS_v1.json) for every original forecast ID and its status.

## Population and preservation of all attempts

| Original state in frozen sample | 12 Oct | 13 Oct | Total |
| --- | ---: | ---: | ---: |
| Original daily forecast files | 8 | 9 | **17** |
| Original `OFFICIAL_DAILY_COMPASS_SCORING_v2` | 6 | 0 | **6** |
| Original `OFFICIAL_DAILY_COMPASS_SCORING_v3` | 2 | 9 | **11** |
| v3 with original 12h outcome file (exact ID+hash match) | 2 | 7 | **9** |
| v3 without original 12h outcome file at pinned HEAD | 0 | 2 | **2** |
| v2 without original 12h outcome file at pinned HEAD | 6 | 0 | **6** |
| Matched v3 with `target_observation_at_utc == target_at_utc` | 2 | 7 | **9** |

All **nine** original outcomes match the linked forecast's `compass_sha256`, forecast identity and v3 scoring contract. The original labels among **nine outcomes × two assets** were BTC: 4 CORRECT, 4 INCORRECT, 1 ABSTAINED; ETH: 3 CORRECT, 5 INCORRECT, 1 ABSTAINED. These are **existing historical labels**, not a new or independently valid accuracy estimate; horizons and price shocks overlap, source-first-known is not independently certified, and some forecasts abstained.

**Critical:** All 17 frozen forecasts had `outcome_maturity["12h"] = PENDING_MATURITY` at **the time of forecast issuance**. That is not a valid current-state label. Conversely, an absent original 12h outcome in this exact Git snapshot **does not establish** MISSING, CENSORED, correct, incorrect or a completed result. The six v2 originals cannot be relabeled as v3 simply because later 12h outcomes use v3.

## A fully traced **negative** v3 example

- `CMP-20261012-468da783e9d8`: original source market-state packet `04_MARKET_LEARNING/entry_signals/auto_market_state/runs/2026/10/12/232245_a3021c904445.json`, blob `48a061318da52279c761cff46456a17f0822954f`, first path-commit `7ed9e997573fc23b2b89fd4998b69391e4063306` at **2026-10-12T23:22:45Z**.
- Original forecast blob `5239ba0450c97e425e5d5791e9c6c6cfa07e1613`, first path-commit `749f995d129ded0f86acd74c8d13eb00741418fa` at **23:24:26Z**; originally declared issue **23:24:24Z**. Source packet Git commit preceded declared issuance by **99 seconds**, while forecast Git commit was **two seconds later**. That is an internally consistent repository order, not an externally witnessed market-data or investor-delivery timestamp.
- Original outcome blob `34b7ed2820c07c7cdd221e547f26891e0f2ce426`, first path-commit `d7e53ac6c46e477a66aa5f8bccb33ffb929ef61b` at **2026-10-13T16:10:25Z**. The original target and target observation both equal **2026-10-13T11:00:00Z** (zero lag). Original BTC and ETH direction labels are both **INCORRECT**, retained as negative evidence, not overwritten.
- The packet's declared SHA-256 agrees with the forecast source pointer (metadata match, not independent provider-content rehash). No independent upstream source first-knowable/publication or original delivery attestation was produced by this work.

## Scientific gate and first admissible experiment

**Pass:** original v3 forecast/outcome identity, source pointer, same-target scoring clock for nine outcomes; frozen complete two-day issuance file denominator; preservation of both abstentions and errors.

**Blocked:** actual provider first-known/vintage at decision time; independent external forecast-publication/delivery; verified independent market event-family N; absent outcome status determination; original model/source rights. These are conditions of **R1 admission**, not optional enhancements. Do not classify nine matched receipt files as nine eligible or independent historical simulation trials. Do not compute an AI-vs-price-only edge from this sample.

**Next existing-owner packet:** Authenticate first-known for one original v3 episode (prefer a recorded error so success-selection bias cannot creep in), reconcile all 11 v3 attempts including both without outcomes, then match a *same-clock* B2 persistence or B4/B5 simple price baseline on identical source vintage and 12h observation. The scientific output remains `BLOCKED/UNKNOWN` until R1's external attestation is independently reviewed. Respect the private `Donh91/secrets` data plane, and leave all original files/forecast/outcome scores immutable.

**No private provider raw values, new scheduler, trading actions, live signal or historical R2–R7 simulation produced.**
