# 44 | Ironflow historic source pilot, first real GitHub execution and methodological correction
**Report date:** 2026-11-06 | **Source:** Ironflow (ironflow.sh), CC BY 4.0 | **Status:** REPRODUCED_PUBLIC_HF_FILE_READ / HISTORICAL_DESCRIPTIVE_ONLY / EDGE_UNPROVEN

## Data and true execution evidence
- PR [#1988](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1988). Initial GitHub run [#42310320953](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42310320953) successfully retrieved 12 files and passed the initial synthetic tests, but the **historical funding join was invalid for most rows** due to publisher millisecond offset. **DO NOT USE INITIAL FUNDING OUTPUT.**
- Corrective run [#42310616110](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42310616110) SUCCESS for **all steps**, HEAD `a57885c769d0aeca6f66f65c87baf6d971da8f72`. 12 pinned public Parquet file SHA256, rowgrain/missingness/source QA, correct 4/12/24/72h descriptive cohorts. GitHub artifact **13548641398**, artifact ZIP SHA256 `808004336d390bd01f7345221f7926425b1323d07a26d3f25e6444c1ed1a239b`, expiry 2026-12-06. This is a 30-day artifact, **not** immutable permanent custody.
- Observed 6,624 completed market-hours (BTC/ETH/HYPE each 744 October 2025 + 720 September 2026 + 744 October 2026). Corrected funding NaNs **zero** (vs false 2,205 / 2,130 / 2,187 missing in initial run). Open interest NaNs zero in this three-market subset. 12 exact bytes and SHA256 in uploaded artifact; full market data not mirrored to the public repo.
- All 12 file observations are **public past-market truth** made available in Nov-2026 source snapshot. For prior 2025 or October-2026 original forecasts, original first-known eligibility is **UNPROVEN**, source cannot enter historical issued forecast feature set.
- In subsequent enhancement attempt [run #42311151584](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42311151584) the new test module had an unclosed test assertion (Python SyntaxError, checkout+dependencies passed, *NO* data analysis run). The exact typo was fixed on PR branch; subsequent new-run receipts must be checked separately. A green previous run does NOT cover later branch commits.

## Corrected 24h retrospective severe drawdown cohort
**Definition:** high liquidation intensity = hourly liquidated *position event* notional / approximate hourly quote turnover > 0.01; target is **any subsequent 24h low <= current completed hour close ×0.98**. Hourly observations strongly OVERLAP. Rows are not independent and are not restricted to first event in a cascade; this study is descriptive, NOT an early alert or performance claim.

| Month | Market | Eligible overlapping hours | Baseline 24h drawdown >= 2% | High-stress hours | High-stress drawdown >= 2% | Difference vs baseline (pp) |
|---|---|---:|---:|---:|---:|---:|
| 2025-10 | BTC-PERP | 719 | 36.7% | 108 | 40.7% | +4.0 |
| 2025-10 | ETH-PERP | 719 | 53.3% | 91 | 70.3% | +17.1 |
| 2025-10 | HYPE-PERP | 719 | 73.3% | 56 | 75.0% | +1.7 |
| 2026-09 | BTC-PERP | 695 | 19.6% | 87 | 26.4% | +6.9 |
| 2026-09 | ETH-PERP | 695 | 34.1% | 30 | 36.7% | +2.6 |
| 2026-09 | HYPE-PERP | 695 | 55.4% | 29 | 58.6% | +3.2 |
| 2026-10 | BTC-PERP | 719 | 27.1% | 85 | 34.1% | +7.0 |
| 2026-10 | ETH-PERP | 719 | 47.3% | 54 | 59.3% | +12.0 |
| 2026-10 | HYPE-PERP | 719 | 59.2% | 32 | 50.0% | **-9.2** |

**Interpretation/kill tests:** This does NOT show that liquidation spikes *predict* falls independently of their simultaneous price crash or volatility. Baseline all-hours includes high-stress hours; marginal comparison is not a disjoint matched counterfactual. HYPE sign flips; no globally consistent signal. Blocked next-day, matched past price/vol, OI/funding and cross-venue controls are mandatory prior to interpreting predictive value. Two or more asset signals at the same time are correlated; never add them as independent n. `RETROSPECTIVE_ONLY`, `NO_INDEPENDENT_SIGNIFICANCE`, `NO_PIT_EDGE`, `NO_ECONOMIC_EDGE`.

## Exact pinned file hash receipts from corrected GitHub job
| Month | Family | SHA256 |
|---|---|---|
| 2025-10 | liquidations/events | `e5382066e77c383e0abe0b5f337242f11997e33e57b674f669465aa7915adca8` |
| 2025-10 | funding | `51c9ebd47a36afc31ae7907b539c1256e456132671f133be488ef3596c9e0a3d` |
| 2025-10 | open-interest | `5fd20253a69b689591fd987af85a706714788ae75d06912879a95b22258c5fc8` |
| 2025-10 | candles | `f30ee1b41fe0c7405c4f5f0dba12adce2d19bdaa60f96bc31d1c1cc30395fad1` |
| 2026-09 | liquidations/events | `35430b107244388721be20026d00b035b2df389035ac790ced0c6c37c4bb502e` |
| 2026-09 | funding | `d8e43faa444e64c263a078b855d8c1edb9ef73fba5b63ef908fc5aa9314ec7bc` |
| 2026-09 | open-interest | `7cb39a7d8ff30c51ce9caf0a6c361e9237e36054d11165032fc5b407e80f1f73` |
| 2026-09 | candles | `c18dda1cf1ce27d6943541613b2c94aae62f657fe690a48620c8824b6780fcd6` |
| 2026-10 | liquidations/events | `3209f97d00ac4edd63ac743ae1f6857ffb2003ca0a73ef22b2ab7c7b67da3b42` |
| 2026-10 | funding | `b081c40f350d3982d1279cd7d019a2d645aabd548cd30358a90e77d4b0e37d8e` |
| 2026-10 | open-interest | `8f12370664f576bacf6ff1bca6fc17655f014a0a200da67823b14d215a7a94b6` |
| 2026-10 | candles | `da6f8ed1c015698512dc78cf8408ec896c63f6289610f3a8f7c7a5a4c38e05ef` |

## Current follow-on and S1 handoff
Follow the newest exact-head #1988 Actions for expanded **T02 dayblocked independent 24h**, **T05 crash/quiet control** and **T08 wallet recurrence/false skill** studies and separate **T04 trades / T10 HIP4** validation job, *not* only these dated T1 artifacts. Rebase and review real active CI/rules; merge once authorized gates met. Bind resulting main SHA and immutable source results; issue #387 is current science source owner, #1596 Task 2, Alpha #22 wallet handoff. Pending: full original source coverage/custody, cross-venue matched baseline, paper cost, prospective first-seen, and unrelated Task 2 acceptance gates. NO completed Task2 claim.
