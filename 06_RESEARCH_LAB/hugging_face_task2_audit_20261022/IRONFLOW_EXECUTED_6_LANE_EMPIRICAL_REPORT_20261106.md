# 45 | Ironflow T02/T04/T05/T08/T10: executed source and stress evidence
**As-of:** 2026-11-06, after actual Actions [#42311443044](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42311443044) on PR [#1988](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1988), HEAD `235f2e3e57f36475672b4479aebf0e490e6934bc`. **Status:** actual source analysis, not a confirmed trading or early-warning edge.
**Attribution:** Ironflow (ironflow.sh), CC BY 4.0. Historic source appeared Nov 2026; prior-era original feature knowledge is UNPROVEN. Public licensed source, never user's personal wallet/portfolio.

## Actual run and retention truth
Two separate jobs succeeded (historical T1/T2/T5/T8, and tick/HIP4 T4/T10); all configured steps green on run #42311443044.
- `ironflow-task2-public-source-T1` artifact **13548283807**, ZIP SHA256 `11ffaaac68f79ca588ffb3b54f4f16cc3923fd1cba9bd856541abd92eb5d8c33`, expires 2026-12-06. Contains source hashes, original T1, 264-anchor dayblock, wallet recurrence and adverse crash/quiet day reports.
- `ironflow-task2-tick-hip4-scope` artifact **13548452685**, ZIP SHA256 `fabb7923d5da81482429c931529874257dbc35e15b3b2b9154b4d836b1ca1e6d`, expires 2026-12-06. Contains tick/HIP4 reports; trade shard `2026-10-07` 155,823,063 bytes SHA256 `81372a3595b99b93771b737f1e3fc4933661c534b03288dd250176dcfed9e984`, control `2026-10-23` 145,926,845 bytes SHA256 `3241a0c72399c37317c47963157e6df3f880c4882681dc6275396df1687d2d15`; HIP4 matching days SHA256 `cb1b61645e3a196852ab74e13172fedb672907810bdf9f63cbebc5244fd268c5` and `5db4bb991f396c0924e9344d9bd19cc7a715ec9a8cc17ce6bf04189141a98673`.
- All raw files were downloaded, processed and then discarded on GitHub runner; **not** permanently copied into either GitHub code repo. Current artifacts have 30-day retention; immutable upstream HF repo SHA+source digests let an eligible owner reproduce while source continues to exist. Full offline custody still pending; do not claim otherwise.

## T02: Dayblocked outcome test, 264 non-overlapping day anchors
Decision clock: next UTC midnight after last fully complete prior UTC day, lookback completed 24h; next 24h target is >=2% intraday drawdown. 29 day anchors in 2025-Oct and 2026-Sep, 30 in 2026-Oct, *per each of BTC/ETH/HYPE*. Daily anchors reduce within-market outcome overlap but cross-asset/day correlations and observational confounding persist. High liquidation pressure: prior-24h liquidation events notional / approximate traded quote volume >1% (not an ex ante tuned operating threshold).
| Market/month | High-pressure days | Subsequent >=2% drawdown | Lower-pressure days | Subsequent >=2% drawdown |
|---|---:|---:|---:|---:|
| BTC / 2025-10 | 15 | 6/15 = 40.0% | 14 | 5/14 = 35.7% |
| BTC / 2026-09 | 9 | **1/9 = 11.1%** | 20 | 5/20 = 25.0% |
| BTC / 2026-10 | 12 | 4/12 = 33.3% | 18 | 5/18 = 27.8% |
| ETH / 2025-10 | 15 | 9/15 = 60.0% | 14 | 5/14 = 35.7% |
| ETH / 2026-09 | 4 | 2/4 = 50.0% | 25 | 7/25 = 28.0% |
| ETH / 2026-10 | 11 | 6/11 = 54.5% | 19 | 8/19 = 42.1% |
| HYPE / 2025-10 | 7 | 6/7 = 85.7% | 22 | 17/22 = 77.3% |
| HYPE / 2026-09 | 2 | 1/2 = 50.0% | 27 | 13/27 = 48.1% |
| HYPE / 2026-10 | 3 | 1/3 = 33.3% | 27 | 13/27 = 48.1% |

This is **not a transferable unconditional forecast edge**: BTC-Sep and HYPE-Oct invert, HYPE + ETH can have high baseline drawdown, denominators are small; threshold may measure already falling market. Price-only control required. Repeat with original-eligible source first-known and untouched holdout to establish any reliable alert.

## T05: Historic liquidation-event anatomy, not warning lead
Three studied markets (BTC/ETH/HYPE) on crash date **2025-10-10**:
- BTC $2.20035bn and 13,769 liquidated position events.
- ETH $1.65593bn and 11,154 events.
- HYPE $0.53616bn and 6,318 events.
- Sum ~$4.39244bn across these three markets (not total Hyperliquid, not total crypto).
- Largest per-market hourly liquidation cluster in **hour ending 22:00 UTC**: BTC $1.8593bn, ETH $1.3346bn, HYPE $0.5123bn; it documents an ongoing cascade, not a pre-crash alert.
Adverse cases Oct 7/8 2026 and quiet 2025-10-17/2026-10-23 are included in executable artifact. No actual original Compass alert delivery or estimated predictive lead-time is proved.

## T04: Real tick-market coverage and independent grain crosscheck
Hyperliquid trade day **2026-10-07** (BTC/ETH/HYPE perp only) vs **2026-10-23**:
| Market | Oct 7 taker-buy vs sell notional imbalance as % total trade quote notional | Oct 23 |
|---|---:|---:|
| BTC | -11.63% | +0.42% |
| ETH | -5.86% | -8.10% |
| HYPE | -11.49% | -1.94% |
Exact (market,trade `tid`) uniqueness: **6/6 market/day comparisons** had all trades unique. Placeholder counterparties for these *perps*: zero. Across the six market/day comparisons, sum of distinct trade rows marked `liquidation` matches the separate public liquidation *event* file's total liquidated USD notional **to the cent**, e.g. BTC 7 Oct $76,480,028.43 in both and BTC 23 Oct $16,767,407.09 in both. These two Ironflow tables derive from the SAME upstream Hyperliquid fills. The agreement is a useful internal reconciliation, NOT independent validation by a different provider; liquidation trade count != liquidated position event count.

## T08: Wallet risk and anti-selection
Across three months, public Hyperliquid **BTC/ETH/HYPE** liquidation positions:
- 107,920 distinct addresses with >=1 liquidation; 13,475 appear in >=2 of three studied months; **857** in all three.
- Per month/market, **top 1% of liquidated wallets** account for approximately **64–82% of liquidated notional**. For BTC/ETH 2025-Oct specifically ~78.1%/~81.7%; 2026-Oct ~70.9%/~81.3%.
- This measures **liquidated notional concentration, not cumulative investment PnL or financial loss**, nor beneficial ownership, nor an ETH token launcher. Winners and surviving non-liquidated wallets are outside this denominated sample. Strong survivorship/selection effect; no automatic wallet score or blacklist.

## T10: HIP-4 outcome market QA, no forecast leakage
- 2026-10-07: 47,691 fills, 1,039 distinct markets, 1,709 distinct public addresses.
- 2026-10-23: 320,008 fills, 1,177 markets, 1,233 distinct addresses.
- No invalid price outside [0,1], missing market IDs or non-USDC fee rows in these bounded source samples. These tests **do not** validate original market metadata as-of, actual resolved outcomes, unrealized PnL or executable quote probability.

## Next research gates and falsifiability
1. **T02/T03 chronological ablation** code added to same PR after these receipts: day-cluster bootstrap, constant vs price+volatility vs incremental liquidation/OI/funding; next actual run and correction required. If Brier/AUC shows no robust improvement, record `NO_INCREMENTAL_EDGE`, do not tune to this sample.
2. **T06** Binance independent provider same-time baseline, maturity and venue matching, not performed yet.
3. **T07** genuine live collector original-first-known and user delivery, not performed.
4. **T09** join to Alpha's prospective original exact-chain CA and staged-exit lab, not performed.
5. Full once-only original-source/revision custody still needed for long-term offline analysis; neither GitHub Actions artifacts nor README source metadata are a permanent mirror.
6. Respect owner #1596 / #387, Round3 prospective collection-only firewall, no new scheduled agents/parallel writers, no trading, no canonical Kompas release.
