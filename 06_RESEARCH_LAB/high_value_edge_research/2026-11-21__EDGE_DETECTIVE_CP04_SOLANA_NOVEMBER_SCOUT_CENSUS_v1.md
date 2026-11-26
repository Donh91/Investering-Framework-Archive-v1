# EDGE DETECTIVE CP04 | Full available November V4 scout-file census (not a Solana launch census)

**Date:** 2026-11-21 Europe/Copenhagen. **Authority:** RESEARCH_ONLY; no discovery/source promotion; original Alpha #228/#120/#70 and Archive #1512 control next work. This checkpoint extends CP01's 3-day sample to **all 21 available November 2026 dated files**, with exact source Git blob SHAs.

## Method

Read `Donh91/Meme-Alpha-Lab/intelligence/ephemeral/v4/2026/11/DD.csv` at original main, one dated file for each day 2026-11-01 through 2026-11-21. Use a quote-aware CSV parser with exactly 10 header fields, handling quoted commas, doubled quotes, and embedded newlines in project descriptions. Every parsed logical record was checked to have the 10 fields; **no malformed logical rows** were found for these files. Count `chain == "solana"` directly per logical CSV row. Do NOT naïvely count physical newlines because descriptions can be multiline. No wallet, token, identifier or source-derived value row is copied into this public control-plane checkpoint.

This was a **scout/discovery/attention source** count (GeckoTerminal trends + DexScreener trending/boost/profile), not a launch denominator, independent token identity census, first-known buy, trade, qualified signal, quote, real exit or market-share statistic. **Rows can recur across dates and sources.** The date-file write cadence is variable; a day with fewer rows is not proof of less market activity or of an outage.

## Exact reproducible per-day inventory

| File date UTC | Logical observed rows | Solana observed rows | Solana share within that day's file | Original Alpha blob SHA |
| --- | ---: | ---: | ---: | --- |
| Nov 01 | 271 | 127 | 46.86% | `e58d03ef44a947948da892d8c2443d9cf64609de` |
| Nov 02 | 135 | 63 | 46.67% | `240512647dc3546147f85cc578d26990a71cbf9b` |
| Nov 03 | 404 | 198 | 49.01% | `274a72674e66b005c2a2ccb4ef2f925682749c3b` |
| Nov 04 | 266 | 126 | 47.37% | `c17ac48600ae93ca05b14d9e92d74ef90f2ec639` |
| Nov 05 | 260 | 123 | 47.31% | `d63c23e0f8ddf4b85decb67f9ee7b37d1529919f` |
| Nov 06 | 266 | 128 | 48.12% | `3cc24721cb8f4b6281ed418009a1ee324c9f6fd8` |
| Nov 07 | 260 | 119 | 45.77% | `c40e5530bdca59752a6bc30bbd596042c40f8fe6` |
| Nov 08 | 232 | 98 | 42.24% | `56117c781db713ad0cf910d61738cfade31c6518` |
| Nov 09 | 116 | 44 | 37.93% | `66bfb8e4b50f0249a52fd704754a8d38b4ab2d34` |
| Nov 10 | 364 | 165 | 45.33% | `e1f26425cc99414e16d5ed6148a382f47d7eaafc` |
| Nov 11 | 129 | 62 | 48.06% | `d4e35b080fd3bb9848bd9e0597f8a0a00b4d3ede` |
| Nov 12 | 394 | 198 | 50.25% | `04a72497a68daffd635dcc265c440a7b12657dcb` |
| Nov 13 | 265 | 128 | 48.30% | `545e21a57dcf8ed1e59fb8695ba63ab7dc38fa7f` |
| Nov 14 | 252 | 124 | 49.21% | `412a94822a03cfd11b3bb8a97f064bfc027e8b55` |
| Nov 15 | 267 | 136 | 50.94% | `cf767fc8c0d5ab0c4715838cb7d7ba355e55ba00` |
| Nov 16 | 133 | 61 | 45.86% | `b7f87c2b5a4f3273374e3ba1628ebc11ea7e932e` |
| Nov 17 | 267 | 128 | 47.94% | `8abce28413236174281bca57b3da744ce88d282b` |
| Nov 18 | 269 | 134 | 49.81% | `b56edf0257536bfeb71aaf8f1c4d66e83ebdeea4` |
| Nov 19 | 262 | 116 | 44.27% | `97c32dae0b02f72346a5a19ea1d9d49ad39a182e` |
| Nov 20 | 263 | 128 | 48.67% | `0dc68b8967720d5dadddc020be12396225324d47` |
| Nov 21 | 265 | 130 | 49.06% | `04627f8c157ea5964fe7d477ce54797f333ad71b` |

## Bounded conclusions

- **5,340** total logical row observations across 21 files, **2,536** with `chain=solana` (**47.49%** of row observations). The unweighted mean of 21 within-day Solana shares is **47.09%**; day range **37.93% to 50.94%**.
- Days **Nov 2, 9, 11, 16** had below 150 logical records (135, 116, 129, 133), compared to many days with ~250-400; **cannot attribute** smaller files to source API outages, fewer launches or different opportunities without origin job receipts and source-clock denominator.
- Solana accounts for almost half of existing V4 observed row volume **in this selected set of providers and collection rules**. It does **NOT** imply half of all Solana memecoins, half of wallets, or half of realizable moonshot opportunities.
- Original `research/alpha_audit/population/LATEST.json` still says `OBSERVED_SAMPLE_ONLY` and `global_eligible_denominator=null`; its frozen sample of **331** candidates includes only Robinhood Chain, as inspected in CP01. This is an **unjoined population**, not a contradiction because the V4 scout and P2a candidate receipts have different purposes and grains.
- Source -> Pons native exact mint/pool -> independent buyers -> $100/$500/$1000 **two-way** sellability -> original outcome/scientific champion remains **unverified**, so `SOLANA_INFORMATION_EDGE=UNKNOWN`, `SOLANA_ACTION_EDGE=NOT_TESTABLE` based on these records alone.
- Next meaningful original owner step is **proof of adjacent natural first-known source intervals**, plus explicit event-to-candidate match/attrition, not increasing trending source count, importing a proprietary leaderboard, promoting 20%-insider from a nonrandom viewer sample or starting another scanner.

**CP04 disposition:** `CENSUS_OF_SCOUT_FILE_ROWS_COMPLETE_WITHIN_21_FILES`, `FULL_LAUNCH_CENSUS_NOT_ESTABLISHED`, `NO_REALIZED_EDGE`. Review/CI and native source contract remain separate; this research note is not canonical until original PR #2300 exact-head independent merge and main readback.
