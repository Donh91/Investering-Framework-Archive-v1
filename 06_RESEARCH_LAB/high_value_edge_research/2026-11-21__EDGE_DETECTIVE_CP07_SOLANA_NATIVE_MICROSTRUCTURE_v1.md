# EDGE DETECTIVE CP07 | Source-pinned native Solana microstructure feasibility

**Date:** 2026-11-21 Copenhagen. **Authority:** RESEARCH_ONLY / SOURCE_FEASIBILITY, no live execution, trade, simulated PnL, provider integration, API key, schedule, wallet signing or model promotion. **No new Alpha scanner.** Owner Archive #1512; Alpha original #228, source/identity #126/#194, sellability #98, outcomes #77/#85. Prior CP05/CP06 corrected that V4 Solana is explicitly trending/narrative-only, NOT a verified launch or execution lane. This document supplies reproducible primary protocol evidence and finite falsification cases for eventual *original-owner approval* of a Solana source study.

## Pinned actual official primary source

Official Pump.fun `pump-fun/pump-public-docs` main read at Git commit `bc35796152027d2744ca02066d305438e34b67e7` (21 Nov 2026). Individual content blobs:

| File | Git blob | Source-backed invariant |
| --- | --- | --- |
| `docs/PUMP_PROGRAM_README.md` | `cdd6e6744c2797e9d502615a84a316cfe97a3ff8` | Pump bonding-curve mint/event/address and curve/complete mechanics |
| `docs/PUMP_SWAP_README.md` | `c2837ee4dd0f8a4839ec41f920369c05d90ca0fc` | PumpSwap post-migration pool, exact base/quote, pool state, effective reserves |
| `docs/SYNTHETIC_MIGRATION.md` | `1dcbb0e6cc6c520abe90fd67be6269077b7c121f` | v3 completing buy can consume the end of curve and a **synthetic future pool** in one transaction |
| `docs/VIRTUAL_QUOTE_RESERVES_FEE_ADJUSTMENT.md` | `14d7c316bad91feb976d06e3f88955ae637ea609` | Fee retention means raw vault may exceed real tradable quote liquidity |
| `docs/NEGATIVE_VIRTUAL_QUOTE_RESERVES.md` | `96fa56d171b92e750ad4f965ea71b7cc2fa4b01b` | Since Sep 30, `Pool::virtual_quote_reserves` can be **negative signed i128** |
| `README.md` | `af2a9de683c1810ef4212ff5dc72137471ecbf2f` | Snapshot documents Oct13 custom nested quote depth; anticipated Nov25 fee-recipient rotation |

**Protocol identifiers, for source-binding only:** Pump `6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P`; PumpSwap `pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA`. These are official documentation, **not a live RPC source-health receipt**. Both program IDs require actual on-chain verification and event discriminator/version matching before any historical inference.

### Mechanisms that change inference

1. **Bonding curve → Pool migration is an explicit stage boundary.** The mint, bonding-curve account, eventual PumpSwap pool and quote mint are different entities. A curve is not a post-migration LP, and a ticker is not a mint.
2. **Synthetic final buy:** Official synthetic migration docs describe `TradeEvent` for the curve portion, `CompleteEvent`, then `PostCompleteBuyEvent` for the synthetic pool portion, *before the real pool exists*. An indexer that counts only `TradeEvent` **undercounts** a complete buyer's tokens/quote; one that separately counts a full buy and its two components can **double count**. The named events must be grouped to their unique Solana signature and event index before source-ready independent buy volume is inferred. The very final buy does NOT automatically prove new, additional independent demand.
3. **Effective reserves:** `effective_quote_reserves = pool_quote_token_account.amount + signed(Pool::virtual_quote_reserves)`. A negative signed reserve component from retained protocol/creator fees must not be interpreted as an unsigned reserve, nor should the raw quote vault alone be called executable liquidity. Any quoted sell size must use the exact contemporaneous pool account state and correct units and actual fees.
4. **Non-SOL quotes and quote chains:** `create_v2` supports quote assets such as USDC and Pump coins, including multi-hop configurations; newly added Oct13 depth-2 quote supports quote-asset paths. A raw quote amount is not always SOL; market cap and trade value require the full contemporaneously available quote path and denominator, or else `VALUE_UNIT_UNKNOWN`.
5. **Time-variant fees and trading versions:** Pump/PumpSwap newer v2/v3 trade instructions change fee retention/event shape. The docs' planned protocol fee-recipient rotation is **Nov25 2026**, future relative to this checkpoint; it must NOT be applied retrospectively to Nov21 as if already live. On-chain activation and version should always outrank a rolling latest README in historical reconstruction.
6. **Mayhem mode:** synthetic finishing trade is not supported on mayhem curves; separate them from classic launches for sample eligibility, just as the public dataset itself cautions.

### Independent Alpha overlap readback

- Alpha `architecture/MEME_ALPHA_V4_PROSPECTIVE_CENSUS.md` Git blob `0bc9bac2a801b2ddd270207052177936fa087493`: SOLANA observation-only, no birth census or paper trading.
- Alpha `scripts/research/launch_window_fee_quote_sanity_v1.py` Git blob `a182e46a968b435781acfaa23d0b8ee1e4470dce`: intentionally offline read-only simple quote/fee sanity. Its docstring explicitly excludes curve convexity/dynamic taxation and says NOT an executable quote. **This is not an identified software bug**, and this research note must not expand its authority by fiat.
- Alpha `scripts/exit_quote_quality_v1.py` Git blob `4d55017d76243c521b372ed222503d59396de1f6`: original research Case Memory quote gate is EVM-only. Its Solana exclusion is documented source policy, not automatically a defect.
- Alpha original `scripts/research/alpha_edge_economic_tournament_v1.py` supports Solana Base58 syntax and after-cost comparisons but requires caller-provided source receipts it explicitly cannot authenticate. Any future Solana economics must pass an original independent receipt admission layer first.
- Current GitHub code search in Alpha repo returned **no indexed hit** for `virtual_quote_reserves`, `PostCompleteBuyEvent`, `buy_v3` or `multi_hop_swap`. This is a **search-index observation**, not proof that all private services or deployed versions lack these capabilities. Avoid bug/coverage assertion without exact owner/current code test.

## Minimal native Solana feasibility probes before suggesting any code

A **bounded, read-only, unscheduled** original-owner source-admission proof should freeze a program ID + IDL version, one actual source-time window and a fixed birth/candidate denominator. Read-only RPC/event decoder to be chosen by existing owner; **do not dispatch from this report**. No wallets or signers.

- **F1 positive curve identity:** valid launch signature, exact mint, canonical curve PDA, quote mint/units and truly observed-after-finality `first_known_utc`; independently compare decoded event to raw transaction meta. No ticker joins or post-event first-known backfill.
- **F2 complex buy:** synthetic finishing transaction contains curve trade + complete + post-complete contribution. Check atomic trade grouping and full buyer size vs same-signature raw transfers. Negative cases include only first event, duplicated event, wrong mint/quote and out-of-order migration.
- **F3 pool reserve:** compare observed vault and signed virtual reserve, both positive and negative synthetic fixtures. Wrong unsigned cast, bad decimals, fee-held-as-liquidity and future pool state must fail quote eligibility. Source oracle is actual on-chain time/slot, not latest docs.
- **F4 two-way, same-size:** quote $100/$500/$1k buys and sells (full acquired quantity) on both curve and PumpSwap stage where legal, with exact fee/priority/route/finality receipts, V4 no-sign policy; NO_ROUTE/REVERT/UNKNOWN remain separate from positive sell proof. No exchange-traded high equals a realizable sell.
- **F5 longevity and negative controls:** include launches that die, non-SOL quote, mayhem, late-migration, missing events/provider downtime, invalid project metadata. Freeze first-known cohort before outcome maturation, compare simple age+liquidity to issuer/funder signals and measure lost tradable winners.
- **F6 unit and era:** historic interval across Sep30 negative reserve semantics and Oct13 quote changes; **only source-state evidence at each date**. A current provider parser must not silently apply post-event schema to older events.

**Decision:** no verified native Solana source or execution edge yet. **Best next action:** original Alpha #194/#126 with Archive #1512 perform a *source feasibility acceptance* of a bounded first-party Pump program launch/event parser and original #98 consider its 2-way route/fee semantics. Only if data/cost/privacy gates prove doable, open one focused original-owner code+test PR, keeping current V4's Solana observation-only production behavior unchanged until independently accepted. A clean technical parser is necessary but NOT sufficient for economic skill.

**Scientific disposition:** `PROTOCOL_SOURCE_MAPPED`; `SOLANA_NATIVE_EVENT_DECODER_PROOF_NOT_RUN`; `HOLD_ECONOMIC_EDGE_UNTIL_PROSPECTIVE_SOURCE_AND_QUOTES`. Preserve this as one source-pinned checkpoint under existing PR #2300, no duplicate program or new paid mission.
