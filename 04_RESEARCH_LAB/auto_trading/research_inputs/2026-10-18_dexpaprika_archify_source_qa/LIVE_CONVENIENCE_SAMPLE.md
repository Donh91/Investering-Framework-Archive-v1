# DexPaprika — 30-Pool Top-Volume Convenience Sample, 2026-10-18

**Status:** PUBLIC_READ_ONLY_PROVIDER_QA / 30_POOL_CONVENIENCE_SAMPLE_COMPLETED / NOT_PROSPECTIVE / NOT_POINT_IN_TIME_ADMITTED / NOT_TRADING_EVIDENCE.

**Sampling protocol actually executed:** Three anonymous GET requests, one each on `ethereum`, `solana` and `robinhood` with `/networks/{chain}/pools/search?order_by=volume_usd_24h&sort=desc&limit=10`. Parse `results` exactly once from each returned payload. Compute one QA class for `liquidity_usd == 0`, one for `0 <= liquidity_usd < 1 USD`, one for simultaneous `volume_usd_24h > 1,000,000 USD` and `liquidity_usd < 1 USD`, and track field presence. No retries, credentials, token selection by later outcome, promotion or orders. All three calls returned ten pool objects.

**Important limit:** This convenience sample is deliberately **conditioned on top trailing 24-hour volume**, not a random or prospectively frozen eligible Alpha Lab cohort. It cannot estimate the prevalence among all tokens, quality of a proposed buy, real fill/sellability, what was knowable earlier, provider latency, predictive edge, or any of Task 2's historical skill. Exact immutable payload hashes/retrieval receipts were NOT captured; execution is an indicative live snapshot, not admitted independent evidence.

## Observed aggregate QA classes

| Chain | Returned pools | Reported liquidity exactly zero | Reported liquidity less than $1 | Trailing >$1m volume AND current liquidity under $1 | Missing token array |
| --- | ---: | ---: | ---: | ---: | ---: |
| Ethereum | 10 | 4 | 4 | 4 | 0 |
| Solana | 10 | 1 | 8 | 8 | 0 |
| Robinhood | 10 | 6 | 7 | 7 | 0 |
| **Total** | **30** | **11** | **19** | **19** | **0** |

**Inference allowed:** A volume-descending pool discovery list contains many entries with extremely low **reported current** liquidity; therefore a volume-only top-pool list should not be elevated into a buyable/sellable token candidate feed. Two different classes must be kept separate: `zero` is an actual numeric response, while `missing` would be UNKNOWN. The 19/30 rate describes **only these 30 returned rows at this anonymous observation**, not a population rate or confirmed missing real liquidity.

**Inference prohibited:** Source data wrong, wash trading proven, scam proven, rug proven, Alpha Lab would have lost capital, DexPaprika is worse/better than other providers, missing order-book depth has been measured, any present liquidity implies ability to trade, or an entry would have been visible 1h/24h/7d before its outcome.

## Endpoint receipts (public URLs, not immutable private receipts)

- Ethereum: https://api.dexpaprika.com/networks/ethereum/pools/search?order_by=volume_usd_24h&sort=desc&limit=10
- Solana: https://api.dexpaprika.com/networks/solana/pools/search?order_by=volume_usd_24h&sort=desc&limit=10
- Robinhood: https://api.dexpaprika.com/networks/robinhood/pools/search?order_by=volume_usd_24h&sort=desc&limit=10

Re-executing these URLs later will likely return different rows and cannot reproduce the original observations absent immutable capture. **Do not mark as reproduced** based only on these URLs.

## Three-provider qualitative spot-checks already performed

- Solana thin PumpSwap case: DexPaprika, DexScreener, and GeckoTerminal independently returned very low current displayed liquidity despite substantial trailing 24h activity.
- Robinhood V4 case: DexPaprika displayed zero current liquidity; DexScreener returned pool identity without an explicit liquidity object. Missing **does not** equal a confirming zero.
- Solana active Orca case: three providers agreed qualitatively on an active pool and similar price/liquidity, but one vendor reported a different pool creation date from the other two. No single aggregator date becomes token-birth authority.

Detailed URLs and semantics: `DEEP_RESEARCH.md`.

## Transfer to existing owner

- Archive #1017/#1087 may use this as a **negative-control fixture idea**, once its source-field-map precondition is verified.
- Add a check in the existing provider QA adapter, *if missing*, for high trailing activity combined with unavailable/near-zero live sellability. This is **not** a new buy/sell rule and cannot use an arbitrary $1 threshold as production authority. Threshold here is purely diagnostic to make the anomaly visible.
- Before any actual data-source promotion, prospectively freeze the 30 mixed-case source universe defined in `ACCEPTANCE_MATRIX.md` and bind captures to the authorized evidence plane. This convenience sample does not satisfy that requirement.

**Research decision remains:** `DEXPAPRIKA = CONDITIONAL_READ_ONLY_SOURCE_QA_CHALLENGER`; no integration, no performance claim and no independent event-level confirmation.
