# 49 | Ironflow 18-month public wallet-liquidation ecology, real 2.85M-event full-population study

**Executed:** 2026-11-07 UTC (source snapshots through 2026-10-31), [GitHub Actions #42314267605](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42314267605) full 18-month job **SUCCESS**. Original source Ironflow (ironflow.sh), **CC BY 4.0**. Exact 72-file frozen family source history, full wallet event data from `liquidations/events`. Source artifact ID **13549393095**, ZIP SHA256 `b32c5fbd107b9549c1849ad05a6c2505062f82ee1d9eca0970d7e47b7e961c79`; contains `FULL18M_WALLET_ECOLOGY.json`. Expires 2026-12-06; upstream pinned HF SHA + exact file hashes durable in accompanying registry.

## Correct event grain, denominator and observed recurrence

| Population measure | Actually observed count |
|---|---:|
| **Liquidated wallet × perp-market position events** | **2,848,413** |
| **Distinct public wallets with >=1 forced liquidation** | **506,880** |
| Wallets with >=2 liquidation events (any month) | 322,546 |
| Wallets liquidated in >=2 distinct UTC months | **208,150** |
| Wallets liquidated in >=3 months | **100,838** |
| Wallets liquidated in >=6 months | **21,208** |
| Wallets liquidated in >=12 months | **2,077** |
| Wallets with liquidations in >=2 *distinct markets* | **255,736** |
| Top 1% of *liquidated* wallet addresses' share of **liquidated notional** | **79.5243%** |

**Important denominator:** These are *wallets with liquidation events*, not all 2025/2026 Hyperliquid traders. Wallets with no liquidation and undetected trader accounts are not in this cohort. This is also not a census of distinct beneficial owners, since one person or custodian may control multiple public addresses.

### Time-to-second liquidation, right-censor adjusted observational denominator

Only count an account whose FIRST OBSERVED liquidation occurs sufficiently far before the 2026-10-31 end to allow complete follow-up time; compute the next observed event separately for 7/30/90 days. Source starts 2025-05-25 and is left truncated, so 'first' is merely first **in this archive**.

| Window after first observed liquidation | At-risk addresses eligible for full observation | At least one repeat liquidation | Empirical selected-cohort repeat rate |
|---|---:|---:|---:|
| <=7 days | 495,378 | 210,926 | **42.58%** |
| <=30 days | 464,127 | 258,255 | **55.64%** |
| <=90 days | 391,145 | 245,375 | **62.73%** |

These are **not** survival estimates for a representative trader population. They do not control for wallet activity level, account leverage, strategy, multiple addresses, capital size or market regimes. The recurrence is not a prospective prediction model and is not evidence these wallets lose overall, because liquidation notional is not net economic PnL.

## Monthly regime and concentration counter-evidence

- **2025-10**: 256,803 liquidated positions (all available markets), **$10.586bn liquidated notional**, 76,755 distinct addresses liquidated that month, top 1% of that month's liquidated addresses contributed **81.16%** of liquidated notional.
- **2026-02**, the most adverse month for the separately tested derivative warning challenger: 173,549 events, **$2.374bn** notional, 55,017 distinct liquidated wallets; top 1% share **69.04%**.
- **2026-10**: 251,828 events, **$2.421bn**, 89,475 liquidated addresses, top 1% **69.72%**.
- Notional concentration varies substantially by regime, so a fixed 'whale risk' index would require strict size/venue/liquidity normalization and closed-future censoring.

## Alpha Lab interpretation and research use

**What is genuinely useful:** 
- A repeat-liquidation hazard proxy, independently described with censoring and all observed liquidated-address denominators.
- A concentrated position stress / 'whale blowup' historical reference for a *perp wallet survivability red-team*, not a smart-money score.
- A lesson for the 0xArchive 99.3%-wins claim: closed profitable trades are insufficient without open losing positions, leveraged drawdowns, forced liquidations and all capital-at-risk.
- A falsifiable hypothesis that *transferring* one venue's historical forced-liquidation stress to early-meme liquidity/rug screening is likely weak and must be tested with exact source+chain+CA and matched false positives.

**What cannot be inferred:** wallet profitability, pre-launch funding, ETH/Robinhood meme contract creator, 'cabal', net loss, owner identity, future trading skill or copyable trade fills. No wallet-address exports were stored in public Git research output. Do not apply automatic BUY/SELL, blacklist, social accusations or position sizing.

## Future experiments, bounded to existing scientific owners

1. Stratify by event size, markets, month and activity-adjusted risk exposure; require complete *nonliquidated* wallet control sample to estimate population incidence.
2. Compare liquidation-history safety outcomes with all wallet fills, funding, margin/open positions and unrealized PnL if independently available; do not assume the six Ironflow datasets provide that full portfolio.
3. Link to existing Alpha Lab #88 wallet skill vs relationship evidence only through real on-chain cross-chain/identity proof; no same-hex-string ownership claims.
4. Model repeated forced-liquidation incidence in a prospectively frozen 30/90day window with event censoring, fees, source clocks and matched active-wallet controls, no background new collectors until authorized eligible owner.
5. Task 2 #1596 and derivatives #387 may use this as retrospective context for large cascading stress events, but the published Nov2026 HF source cannot be backdated as a 2025-era early warning.

**Research decision:** `WALLET_ECOLOGY_DESCRIPTIVE_COMPLETE`, `REPEAT_FORCED_LIQUIDATION_EVIDENCE_PRESENT`, `TRADER_ALPHA_UNPROVEN`, `MEME_LAUNCHER_LINK_UNPROVEN`, `PIT_SIGNAL_UNPROVEN`, `T3_OFFLINE_RAW_COPY_PENDING`.
