# Task 2 · Entire native v3 Compass source-clock census (11 issued forecasts)

**Research-only · 2026-10-14.** Historical exact source ref: `098c50d36b222c4c8ffa179a5879d36a74194bc4`. Companion machine artifact: [11 original source-clock chains](2026-10-14__TASK2_R1_NATIVE_V3_11_SOURCE_CLOCK_CASES_v1.json). Parent fixed original-forecast/outcome denominator: [17-issue census](2026-10-14__TASK2_R1_NATIVE_V3_12H_CENSUS_v1.md). This note is **not** an approved historical backtest or execution readiness decision.

## What was actually checked

All **11 originally issued `OFFICIAL_DAILY_COMPASS_SCORING_v3` forecasts** on October 12–13 were retrieved at an explicit Git SHA, together with the exact public `auto_market_state/runs` packet path recorded in each forecast. For the **10 distinct packets**, the packet's Git blob, self-declared `packet_sha256`, and earliest visible Git path commit were read back; the original forecast's self-declared packet pointer matched in **11/11** cases. The first recorded packet path commit precedes the forecast's recorded `issued_at_utc` in **11/11** cases. These are source-identity and public Git chronology checks, **not** independently authenticated upstream provider publication or first-known dates.

Nine of the 11 v3 forecasts already had matching original 12h outcome receipts at the pinned snapshot, with correct target observation clocks; **two lacked an outcome at that snapshot** and must retain an unresolved state. They are neither automatic errors nor automatic censures. The original six scoring-v2 forecasts in the separate 17-issuance parent are excluded from native-v3 scoring comparisons.

## Source-age anomaly that requires owner adjudication

`CMP-20261013-bfb7ff123449` was issued on **2026-10-13 14:14:43 UTC** but references the previously used packet `2026/10/13/121858_d2568ca43db0.json`, generated at **12:18:58 UTC** and first committed at **12:18:59 UTC**. Its **source-generated → issue gap is 6,945 seconds = 115m45s**. `CMP-20261013-aa70b21fc6b0`, issued at 12:20:35, references the very same packet only 97 seconds after generation. Thus one source packet is reused after nearly two hours.

**Scientific verdict:** `SOURCE_AGE_ATTENTION`, **not** a proven bad signal, provider-lookahead breach, production freshness violation or reason to silently discard a historically issued forecast. No applicable canonical maximum source age was verified for these original cases. An exploratory 60-minute flag is only a human-review threshold, **not a new rule**. Original source age should be evaluated using the *actual owner contract at issuance*, current source override policy, and any newer available packet that could have been intentionally skipped; do not replace the original packet retroactively.

Other original packet-to-issue gaps ranged from **67 seconds to 9m03s**. All recorded packet first-commit timestamps were earlier than their respective forecast issuance timestamps. This is useful reproducible lineage, but **Git author/committer time is not independently attested vendor-first-publication, a bound end-user delivery clock, or an authoritative first-known source timestamp.** A matching self-declared source SHA also does not mean the original provider bytes were rehashed in this intake.

## Admission / next owner actions

- **R1 family/denominator:** existing #1596 owner must preserve all 11 v3 attempts and two absent outcome states, plus original v2 separation and BTC/ETH `ABSTAINED` labels. None of these 11 is an independently verified market shock family merely by existing as a row.
- **R1 exact as-of:** prove externally or via independently attested original capture receipts that every underlying vendor field existed and was known before the corresponding source capture/forecast. Check capture revision, provider engine era, original time zone, first-known, clock and delivery latency. For CFGI, distinguish v3 retrieval of historical data in 2026 from contemporaneous 2025 availability; split pre/post 2026-07-08 vendor scoring engine vintages.
- **R1 source reuse:** check why `bfb7ff123449` reused the 12:18 packet, whether intentional fallback or stale source, and document the **original contractual freshness maximum at issue time**. Preserve the actual source packet and measured 6,945-second gap even if later determined acceptable. No invented stale/fresh verdict.
- **R2 next test:** only after first-known admission and independent family grouping, pre-register same-clock persistence/momentum/price/volume/volatility controls with complete attempt denominators, abstentions, realistic costs and chronology-aware splits. No retrospectively selected winners or shifted outcome clock.

**Counts:** 11 issued native-v3 / 10 unique source packets / 11 match original declared packet SHA pointer / 11 recorded packets pre-issue / 9 later 12h outcomes in pinned snapshot / 2 absent at pinned snapshot / **0 R1 scientifically admitted rows** / **0 R2 economic simulations**. No original forecast or outcome changed. No new scheduler, owner, data purchase, production action or private provider values exported.
