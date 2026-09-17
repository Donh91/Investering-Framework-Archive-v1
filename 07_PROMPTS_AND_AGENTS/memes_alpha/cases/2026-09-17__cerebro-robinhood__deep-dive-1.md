# Alpha Lab — CEREBRO deep dive 1

Status: POST-FREEZE FOLLOW-UP; DOES NOT MODIFY PRE-OUTCOME SNAPSHOT
Observed: 2026-09-17 ~17:36 Europe/Copenhagen
Parent frozen case: `2026-09-17__cerebro-robinhood__pre-outcome-audit.md`
Token: CEREBRO
Chain: Robinhood
CA: `0xeb24a2663af4ee979dcbfe39cb95b5f12d369c4b`
Canonical observed pool: CEREBRO/NVDA Uniswap v4 `0xb553e268a7790255e0db206aa27fa32e805b431645b230441fbd8beeb7618fc8`

## Live market readback

At this follow-up DexScreener showed approximately:
- price $0.001772
- MC/FDV $1.7M
- liquidity $121K
- 24h volume $668K
- 24h traders 519
- 24h txns 1,835
- buys/sells 659/1,176
- buy/sell volume ~$319K/$349K
- 6h -16.99%; 24h -54.61%
- holders shown 1,051
- pair age ~7d23h
- pooled ~34.50M CEREBRO + 275.91 NVDA

This is a material deterioration from the frozen ~13:50 snapshot (~$2.2M MC, ~$138K liquidity), while holder count has increased. Do not infer accumulation from holder growth alone.

## Holder / concentration evidence

A historical Codex-derived report frozen on 2026-09-12 reported 782 holders and aggregate top-10 share 25.8%. Current DexScreener shows 1,051 holders, but the accessible sources in this pass do not expose a trustworthy current per-wallet holder table or adjusted top-10 after removing LP/system addresses. Therefore current adjusted concentration, dev allocation, insider clusters, cost basis and funding provenance remain UNKNOWN rather than estimated.

## Contract / security evidence

DexScreener currently surfaces Go+ Security `No issues` and Quick Intel `No issues`, but explicitly warns audits may not be fully accurate. This is supportive screening evidence only, not a substitute for contract-level review. LP ownership/control/lock status and deployer privileges were not independently resolved in this pass.

## Product/economics verification

Current official Cerebro website states:
- qualifying trades generate a 1.50% fee;
- 50% is directed to the AI Credit Pool;
- credits use time-weighted qualifying holdings;
- holders can claim credits and use supported AI infrastructure.

The site currently marks Inference Rewards COMPLETE and Inference Marketplace COMPLETE, with shipped claims including wallet accounting, API credentials, usage tracking, reward history, protocol statistics, buy/sell inference, USDC settlement and credit accounting. Cerebro Launchpad is IN DEVELOPMENT, with runtime provisioning, project inference accounting and developer infrastructure listed as building.

The public GitBook is stale/inconsistent relative to the new website: it describes stages as Rewards -> Launchpad -> Marketplace, whereas the current website marks Marketplace complete and Launchpad in development. Preserve this as DOCUMENTATION DRIFT, not proof of wrongdoing.

Important unresolved DATA CONFLICT remains: DexScreener project profile says `1% fee`; current official website says `1.50% qualifying trade fee` and 50% to AI Credit Pool. Actual contract/fee routing remains unverified.

## Developer provenance

Anton Karlovskiy's own GitHub commit `b13a43a3311fc3b466cd94238435a69d025f5a2e`, authored/committed by `anton-karlovskiy` on 2026-09-10T20:02:29Z, explicitly added `I'm currently working on the Cerebro project (https://x.com/cerebro_rh).` This is stronger provenance than third-party social claims.

His public profile states 10+ years and prior Google Chrome, Interlay, Mantle Network and BitDAO work. Treat those profile claims separately from independently verified employment history.

## Social/caller layer

CEREBRO is no longer obscure in crypto-social terms. Multiple public Telegram/X surfaces are actively promoting it, including House of Xeus, Onyxx and other Robinhood-chain accounts. Some explicitly compare it with ORBIO/VVV or cite targets such as $10M/$100M. These are promotional/caller claims, not evidence of fundamental value.

This changes the thesis: `unknown builder discovery` is no longer the edge. The remaining potential edge is whether product usage/value capture is real before the broader market prices it, and whether wallet structure remains healthy through the current drawdown.

## New inference / falsification

Positive:
- exact developer-project linkage strengthened by direct GitHub commit evidence;
- holder count increased from historical 782 to current 1,051 while price is in a severe drawdown;
- current liquidity ~$121K remains non-trivial at ~$1.7M MC;
- first-party product scope is more developed than a simple narrative token.

Negative / caution:
- price fell to ~$1.7M MC and -54.6%/24h at this observation;
- sells materially exceed buys and sell volume exceeds buy volume;
- social promotion is spreading, reducing informational novelty and increasing reflexivity;
- fee semantics remain unresolved;
- actual AI-provider spend, credit redemption, marketplace volume, protocol revenue and inference consumption are still not independently evidenced;
- current wallet-level concentration/deployer/LP control remain UNKNOWN.

## Updated Alpha state

`DEEP DIVE / WATCH ENTRY — NO BLIND CHASE`

The fundamental thesis survives this pass, but conviction is not upgraded because the two decisive falsifiers remain unresolved: (1) economic loop/value capture, and (2) wallet/deployer/LP structure. The large drawdown improves nominal valuation but does not itself improve R/R unless those two layers pass.

Next highest-information tasks:
1. obtain current holder/deployer/LP table from a source that exposes Robinhood-chain wallet identities and classify LP/SYSTEM/DEV/TEAM/CEX/EOA/UNKNOWN;
2. trace fee-engine recipient(s) and reconcile 1% vs 1.50%;
3. prove actual AI-credit issuance/redemption/API usage/marketplace settlement with transaction or backend receipts;
4. measure whether holder growth during drawdown is genuine distribution or wallet splitting/sybil behavior;
5. preserve later 24h/3d/7d outcomes against both the frozen first-seen case and this follow-up.
