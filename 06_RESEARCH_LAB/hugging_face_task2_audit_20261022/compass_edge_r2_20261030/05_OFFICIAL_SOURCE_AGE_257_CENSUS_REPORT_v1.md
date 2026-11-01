# C02 / Kompas PRO · Complete October Official Source-Freshness Census

**Status:** FULL 257/257 original public archive rows retrieved, 0 source-file errors. **Research-only, not a scientific PIT/edge certification, not a proposed new live threshold.** Owner: existing [Task 2 #1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596) and [P0 data lineage #1827](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1827).

## Why this matters

A recently *generated* Auto Market State packet can wrap an older source observation. For the current 12-hour Kompas presentation, that distinction is material: `CURRENT/NOWCAST` is not an independently validated 12-hour forward forecast, and a fresh packet timestamp does not prove a fresh or investor-delivered original market observation. This study deliberately tests **source-age coverage**, not price skill.

## Locked source population and readback

- Fixed original public repository commit: `ef896285328cb0f8ae27f8ddd0eaa38fdc16a5e3` (original #1852 merge snapshot).
- Exact original subtree: `04_MARKET_LEARNING/handlekompas/official/daily/2026/10`, immutable Git tree `5185a933dbc1bd72bfe8fe0e397c292a908f2a71`.
- Study interval: **all calendar days Oct 01–30, 2026**, day directories 01..30, files matching `DD/CMP-202610DD-<hex>.json`. **257 distinct archived ORIGINAL Official Compass files**, 0 directory missing, 0 parse/fetch errors, 0 unknown original source age or packet age.
- Every file was retrieved independently by its Git blob SHA, not from a mutable `latest` pointer. The 15 non-overlapping batches are fully enumerated, including indexed counts, in [machine results](05_OFFICIAL_SOURCE_AGE_257_POPULATION_AUDIT_v1.json).
- Source clock: `source_bindings.auto_market_state.freshness.checks[ lane="source_observation_freshness" ].age_seconds`. Packet clock: corresponding `lane="auto_market_state_packet"`. **NOT** original vendor first-published or investor first-delivered time. `data_status` is Official state, whereas `freshness.status` is the separate source freshness check; never conflate them.

## Full-population quantitative result

| Original Official outcome/age | Count of 257 | Rate |
|---|---:|---:|
| Official status `OK` | **225** | 87.55% |
| Official status `DEGRADED` | **32** | 12.45% |
| Source freshness status `PASS` | **238** | 92.61% |
| Source observation age strictly >30 minutes | **169** | 65.76% |
| Source observation age strictly >60 minutes | **77** | 29.96% |
| Source observation age strictly >120 minutes | **37** | 14.40% |
| Source observation age strictly >180 minutes | **19** | 7.39% |
| **Packet age <=30m BUT actual source observation age >30m** | **108** | 42.02% |
| **Official `OK` with source observation age >30m** | **143** | 55.64% of all, **63.56% of OK** |

The data-age-only qualification scenarios below are **coverage sensitivity** counts, not real status transitions, portfolio-return backtests, a recommendation to degrade all stale records, or production policy:

| Hypothetical age-only maximum | Qualified by observation age | Lost relative to 257 |
|---|---:|---:|
| 30 minutes | **88/257 (34.24%)** | 169 |
| 60 minutes | **180/257 (70.04%)** | 77 |
| 120 minutes | **220/257 (85.60%)** | 37 |
| Existing 180-minute scale | **238/257 (92.61%)** | 19 |

**Crucial trade-off:** A blind 30-minute hard gate would exclude **143 original `OK` runs** because their market observations were older than 30 minutes. Some may still be appropriate for a slow horizon; automatically quarantining them would risk excessive unnecessary `UNAVAILABLE/DEGRADED`, and could bias any subsequent model evaluation by discarding difficult periods. The appropriate initial fix is distinct, explicit **market observation age vs packet age** display and a shadow policy/coverage comparison. A future per-horizon age gate requires its own owner approval and false-unavailable + actual utility evaluation.

The earlier predetermined 36-file sample in #1827 found **30/36 >30m (83.3%)**, materially higher than this full population **169/257 (65.8%)**. Do **not** promote the 36-sample rate to the October population and do not add sample and census denominators together.

## Independently reproducible, no network access needed once repo is checked out

From a clone with the **pinned commit and Git tree available locally** (a shallow checkout may require earlier approved fetch under normal GitHub mechanics):

```bash
python scripts/research/official_compass_source_age_census.py --verify
python -m unittest tests.research.test_official_compass_source_age_census -v
```

The script verifies that the month tree resolved from the immutable commit matches the frozen tree SHA, enumerates the original 257 files with strict day/path matching, reads Git object blobs, extracts the exactly specified fields, and refuses `--verify` if any published count differs. It performs no requests, no repo writes and no private-data access. It never imports the Official producer/forecast engine. The accompanying fixtures exercise age bound equality, 30m fresh-wrapper/old-source mismatch, status separation, missing/duplicated clocks, negative/null ages and adverse source states. **The frozen GitHub blob batch audit was executed; the new replay script and its repo-local unit suite require exact-head CI or an independent local run before claiming them executed successfully.**

## Source integrity / science gates still open

1. **C02 PIT:** True first provider publication/revision and actual original first public/investor delivery are missing for historic R1; (0/11) original independently PIT-admitted. Internal Git/packet timestamps do not fill the hole.
2. **C03:** Prospective protocol already merged #1852, but no sealed/first-known future cohort, no eligible Round 3 scoring, no validated real warning lead or prospective independent shock power.
3. **P1 source freshness:** Full 257-row source-age denominator is now documented. Next conservative research step is separate metadata clocks: `source_observation_age_seconds`, `packet_age_seconds`, completed hourly price candle reference age, optional nullable provider-first-known and delivery. Distinct `OK`, `SOURCE_OLD`, `QUALITY_DEGRADED`, and `FIRST_KNOWN_UNKNOWN` states are informative; do not collapse to a fake single confidence score.
4. **Validation needed for policy:** Run a *future* complete issue/abstain universe with clock proofs, stratify 12–24h vs 1–3d vs 5–7d, count false unavailable, stale-alert misses, early-warning lead, after-cost action changes and independent event clusters. A threshold change is unproven, and protection pullback P=4/5 / SELL/REBUY do not follow from source age alone.
5. **Release boundaries:** No code change to production, no Official/NEXT/Daily/CN/Data Ping producer patch, no new cron, no API spend, no private Round3 scoring, no deployment/auto trading.

**Conclusion:** Confirmed whole-population source-quality issue: `freshness_of_wrapper != freshness_of_underlying_market_observation`. Source freshness transparency and per-horizon monitoring deserve prioritized shadow engineering, while any predictive or economic claim remains **UNVERIFIED**.
