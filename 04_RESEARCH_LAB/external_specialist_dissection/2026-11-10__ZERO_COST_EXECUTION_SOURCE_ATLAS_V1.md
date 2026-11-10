# ZERO-COST EXECUTION RESEARCH ATLAS V1
**Frozen method inventory:** 2026-11-10, Europe/Copenhagen  
**Owner:** existing Research Lab #1512, implementation owner existing Meme-Alpha-Lab #98, scientific adjudication #1157, release coordination #1156.  
**Status:** RESEARCH_ONLY, SOURCE_REVIEWED_METHODS, ORIGINAL_CODE_NOT_CHANGED, NO_ECONOMIC_EDGE_DEMONSTRATED, NO_PUBLIC_SITE_RELEASE.  
**Cost:** $0 NEW external API spend, $0 paid research service, no keys, no trading, no new schedules/identities.

## Executive decision

Use 0x as evidence that real sized quotes and routes matter, **not** as a required data source. The highest value proprietary-dependency reduction is exact published Pons V2 curve math, native Uniswap V4 pool/hook state, free chain receipts, and local controlled EVM simulation, all tested against the existing sellability research and paper-wallet owners. Never reverse engineer proprietary 0x APIs, harvest 0x quotes at scale, scrape restricted sources, or imply an API's permissive licensing from the existence of an open-source package.

The 2026-07-31 0x changelog adds Robinhood 4663, Pons V2 bonding curves and V2/V3/V4 liquidity sources, which demonstrates route feasibility but NOT guaranteed coverage of any new Pons token. 0x API requires authentication and its own policy warns repeated quote polling without trade submissions may be limited or blocked. Keep the 0x API UNCONNECTED. Public contracts, event ABI, public docs, permissively licensed independent code and own chain reads are the primary source boundary.

## Ranked ten independent method families, exact owner and proof

| Rank | Method | Benefit / falsifiable hypothesis | Free independent source | Existing owner | Acceptance / scientific kill |
|---|---|---|---|---|---|
| **01 P0** | Pons V2 exact-integer, phase-aware buy/sell quote | Predict amount at specified size materially better than marginal reserve ratio | Official Pons V2 docs, contract ABI, chain 4663 RPC, own recorded CurveBuy/CurveSell | Alpha #98 / #120 | Same-block quote vs transaction event, full fee order, all phases and revert controls; kill if cannot reproduce source or quote math |
| **02 P0** | Native V4 pool-state, hooks and Quoter | Recover post-graduation trading reality without treating PoolId as CA | Uniswap docs/interfaces and free on-chain StateView/Quoter | Alpha #98 / #194 | Verified deployment+poolKey+32-byte poolId, tick liquidity and hook fees, paired verified event; UNKNOWN where hook or RPC unsupported |
| **03 P0** | Local negative SELL simulation | Detect reproducible no-route/revert/size failures, without signing or real trading | Local Anvil/REVM, public contract bytecode, free historical state if accessible | Alpha #98 / #194 | Native fork receipts incl clean controls; kill when historical state unavailable or test not reproducible |
| **04 P0** | Observed on-chain fill receipts | Separate a simulated quote from actual historical execution | Original transaction/log/balance deltas; MIT 0x-parser for 0x trades only | Alpha #98 / #77 | Deterministic event/token+quote/gas deltas, canonical block hash; never generalize one successful fill to other size/time |
| **05 P0** | Source-complete first-known event tape | Detect silent log caps, missed events and false-live claims | Free Robinhood RPC, Blockscout, optional MIT Ponder techniques | Alpha #120 / #70 | Provider-specific log cap tests, contiguous windows, gap and source-proof receipts; no cursor advance on incomplete |
| **06 P1** | Sized exit and liquidity stress | Show difference between spot gain and sellable net proceeds | Own #01/#02 data and existing paper-wallet | Alpha #98 / #77 | $50/$100/$250/$500/$1000 + full-size quote with cost and depth stress; report theoretical sensitivity as scenario, not prediction |
| **07 P1** | Pair-currency / decimal / USD truth | Prevent fake USD, marketcap or ROI caused by custom pair or stale FX | PairToken/on-chain decimals and verifiable oracle; optional free DefiLlama when supported | Alpha #98 / #126 | Explicit base/quote currency, as-of USD source and age; otherwise USD_UNVERIFIED, no synthetic stablecoin peg |
| **08 P1** | Basic open AMM route comparison | Reproduce open-protocol route reasoning independently of 0x | Own Pons/V2/V3/V4 independent pool reads and public protocol math | Alpha #98 / #194 | Bounded direct/one-hop quote vs naive direct; fees/gas/hooks; do NOT copy 0x RFQ/proprietary router/data |
| **09 P1** | Prospective after-cost edge falsification | Test whether real opportunity persists at executable size beyond price chart hindsight | Frozen original Alpha cohorts, S4/#77, #228 Strategy Arena, #85 | Alpha #77 / #228 / Archive #1340 | Matched original cohort, 15m/1h/6h/24h/72h/7d, failures/unknown/missed winners; no claim from synthetic cases |
| **10 P2** | Solana cross-chain independent comparator | Stress generalization of quote/exit methodology across chain types | Public Solana chain/program primitives, bounded free Jupiter route docs/keyless offers subject to current rate/rights | Alpha #194 / #98 | Source-authorized small sample, separate SOL chain/mint/fee semantics, no private API, no claimed fill from quote |

**Cross-cutting opportunity:** build original chain-first *quote coverage map*: token/curve/pool + as-of block + life phase + quote side/size + source/route and error taxonomy. Include unscored, rejected, missing or never-graduated tokens. This bridges CrawlScan's 29-case B1/quote gaps without presuming the source can reconstruct original T0 after the fact. It may add more scientific value than another token scoring system.

## P0 mathematical and implementation acceptance, Pons first

Existing source readback: Meme Alpha main scripts/collectors/pons_curve_quote_shadow_v1.py @ Git blob 3270c7911a6d04580cc1f1471aa1ce17344841c4 is **virtual/marginal reserve ratio** only; explicitly execution_verified=false and no two-sided sized output. Existing Pons transfer research is in research/discovery/PONS_V2_PUBLIC_SOURCE_TRANSFER_2026-10-05.md; independent CurveBuy/CurveSell decoder already exists. The accepted unit of change is a scoped extension of original #98 research-only source, not a parallel trading router.

1. Bind exact chain 4663, token CA, curve CA, pairToken address and both token decimals; pin block number/hash before+after all reads and capture UTC. Never join floating 'latest' from multiple blocks.
2. Read getReserves as actual **pricing** reserves including phantom quote, not realQuoteReserve and not displayed marginal price. Read sellableTokens, feeBps, creatorTaxBps, currentSnipeTaxBps(recipient) for BUY only; read readyToGraduate/graduated/phase from actual deployed ABI.
3. BUY: fees and recipient-specific launch snipe tax remove quote amount **before** constant-product pricing. Bound by remaining sellable allocation, cap the last buy at graduation and account for refunded quote. Use integer rounding/order identical to source.
4. SELL: compute gross proceeds by reserve-based amountOut on token->quote then subtract fee and creator tax from quote output; **no snipe tax on SELL**. readyToGraduate=true blocks SELL before graduated status even if old UI suggests sale. Swept/phase1 remains no curve exit until pool is seeded. After graduation, use qualified V4 route with hook fee.
5. Negative fixtures: zero reserves; notional greater than available reserve; phase0 readyToGraduate true; swept but not graduated; non-ETH pair 6 decimals vs token 18; fee and tax corner cases; recipient exemption; pre-/post-transition; custom V4 hook; missing pool/quoter; stale/changed block hash; source RPC 429; permission/revert. Out-of-scope/unknown must never become safe.
6. Pair candidate tests against independent actual historic CurveSell gross/net events at the same block or a controlled pinned simulation. Independent data source and original first-known eligibility separately verified. A perfect after-the-fact event replay demonstrates mechanics, NOT prospective predictive alpha or true transaction fill probability.
7. Source comparison must report expected token/quote amounts, gas, gas currency, fees/taxes, slippage, estimated net USD only if independently convertible, route identity, quote lifetime, after-cost assumed vs actual status. A future source-event cannot contaminate a frozen original entry decision.

## Proof metrics and acceptance hierarchy

**Source quality**: (i) eligible total candidate denominator, (ii) exact first-known source coverage, (iii) independent source age/gaps/invalids, (iv) chain+CA+pool identity match.  
**Mechanical quality**: pass/fail/unknown by requested notional; numeric quote error vs actual event where available; fee error; false-safe/false-blocked fractions; pool/hook/phase misidentification; route disappearance.  
**Economic quality**: after-cost quoted median & tails; full-size quote coverage, no-fill/revert share, realized fill size where observed, missed-winner penalty, matched incumbent improvement, timestamp leakage control.  
**UI quality**: last captured UTC, original source as-of, current TTL state, original vs latest position and evidence version; no fake LIVE or BUY.

Stages: DOCUMENTED_METHOD -> SOURCE_CAPABILITY_PROVEN -> DETERMINISTIC_TESTED -> HISTORIC_MECHANICS_PROVEN -> PROSPECTIVE_SOURCE_ADMITTED -> PROSPECTIVE_OUTCOME_MATURED -> INDEPENDENT_REVIEWED -> QUALIFIED_OR_KILLED. No skipped stage or self-promotion. Only original owners and qualified native CI/merge can change downstream code or public display authority.

## Legal, operational and priority stop conditions

- Zero pay means no billed Deep Research run (TinyFish per-run), no Firecrawl credit-backed agent or paid LLM API, and no new 0x API access until a genuinely no-charge license/rights/plan is **verified**. Existing paid subscriptions or plan allowances do not independently grant user permission to spend money for this mission.
- 0x swap/quote API license and terms apply to its data and private service; reading official docs and independently implementing open on-chain math is separate. Obtain license verification for every copied open-source module (0x-parser MIT; Ponder MIT; REVM MIT; Uniswap mixed licensing).
- Site is a **presentation consumer** of original Alpha source and publication-qualified data, never a browser-side scanner or a key-carrying proxy. Do not publish private wallet IDs, research claims, restricted raw prices or positions, private source path, or unsanitized provider outputs.
- S1/Claude review must not override original source, privacy, exact HEAD CI, site, custody or high-impact release gates; Claude's submitted review is advisory and requires exact-file/head provenance.
- Priorities: #120 true first-known and #98 native sized Pons quote first, then #194 V4 identity and #77 outcomes. Do not create 10 independent PRs, another queue/scheduler, or a new GitHub identity.

## Source ledger, public references

1. Pons V2 official documentation, launch lifecycle and exact quote semantics: https://docs.ponsfamily.com/v2
2. Original 0x Robinhood/Pons V2 support announcement: https://docs.0x.org/changelog/2026/7/31
3. 0x rate/quote polling limitation: https://help.0x.org/articles/9391588008-rate-limits
4. 0x commercial API/data licensing: https://0x.org/legal/api-license-agreement
5. 0x pricing and quote-polling caveat: https://0x.org/pricing
6. Uniswap v4 quotation guidance: https://developers.uniswap.org/docs/sdks/v4/guides/swapping/quoting
7. Uniswap v4 state reading: https://developers.uniswap.org/docs/protocols/v4/guides/state-view
8. MIT 0x-parser, observed 0x trade trace analysis: https://github.com/0xProject/0x-parser
9. Local Anvil: https://getfoundry.sh/anvil/index.html ; MIT REVM: https://github.com/bluealloy/revm
10. Public Robinhood/Blockscout API source limits: https://github.com/blockscout/docs/blob/main/robinhood-api.mdx
11. MIT Ponder architecture: https://github.com/ponder-sh/ponder
12. Public price comparison where supported: https://api-docs.defillama.com/
13. Solana Jupiter free tier and limitations: https://developers.jup.ag/
14. Original owner source contracts: https://github.com/Donh91/Meme-Alpha-Lab/issues/98 ; https://github.com/Donh91/Meme-Alpha-Lab/issues/120 ; https://github.com/Donh91/Meme-Alpha-Lab/issues/77 ; https://github.com/Donh91/Meme-Alpha-Lab/issues/228
15. Canonical source/method gate: https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1512

**Evidence cutoff:** 2026-11-10. Claims about product pricing/free access require contemporaneous verification at next implementation; no provider quote API calls, archive reconstruction, original source releases, synthetic performance or site deployments are asserted here.
