# Research Lab: three Telegram token-scanner specialists | Monsta, PIRBView, SAFE Analyzer

**Observed and researched:** 2026-11-07 (Europe/Copenhagen). User supplied screenshots of `@MonstaScanBot`/`@monsta_x`, `@SafeAnalyzerbot`, `@coinscan`/`@PirbViewBot` (PIRBView).  
**Authority:** `RESEARCH_ONLY / SOURCE_CHALLENGER / NO_NEW_SCANNER / NO_TRADE / NO_WALLET_AUTHORIZATION / NO_NEW_SCHEDULE / NO_API_SPEND`.  
**Destination:** existing Research Lab `#1512`, unchanged [canonical external specialist queue](QUEUE_V1.json). Existing Alpha Lab owners: #88 (wallet and cluster), #126 (CA/project intake/scanner recall), #194/#98 (execution safety), #77/#85 (prospective outcome), plus existing S1/S2/S3/S7, X0.  
**Protocol:** [External Specialist Dissection v1](https://github.com/Donh91/Meme-Alpha-Lab/blob/main/architecture/EXTERNAL_SPECIALIST_DISSECTION_V1.md): niche -> reproducible primitive -> independent raw/official evidence -> controls -> forward test -> retain/kill.  
**Verdict:** **METHOD_ONLY_TRANSFER + EXISTING_OWNER_EXTEND**, no vendor SDK/code integrated. Highest-value niche: social first-mention/recycled-account chronology (Monsta), entity-adjusted early-buyer/airdrop/overlap/holder maps (PIRBView), and safe-label vs notional-executable exit disagreements (SAFE). All bot results remain vendor claims without authenticated original point-in-time receipts.

## 1. Identity and official source reconciliation

| Bot as seen in owner's Telegram screenshot | Authenticated first-party/declared sources | Distinguish clearly |
|---|---|---|
| Monsta `@MonstaScanBot`, also `@monsta_x` | [docs.monstalabs.io](https://docs.monstalabs.io/), [monstalabs.io](https://monstalabs.io/), [Telegram @MonstaScanBot](https://t.me/MonstaScanBot), [official announcement channel](https://t.me/s/monstalabs) | `docs.monsta.com.br` is an **unrelated infrastructure product**. Do not cite it as Monsta crypto bot documentation. |
| SAFE Analyzer `@SafeAnalyzerbot` | [DexAnalyzer bot docs](https://www.dexanalyzer.io/docs/safeanalyzerbot), [DexAnalyzer API & pricing](https://www.dexanalyzer.io/api), [Telegram bot](https://t.me/SafeAnalyzerbot), [report descriptions](https://www.dexanalyzer.io/docs/safesniper-desc) | `SafeAnalyzer` is a bot and a paid API offering, not a verified open-source wallet/safety engine. Earlier docs emphasize PancakeSwap/BSC. |
| PIRBView `@coinscan`, also `@PirbViewBot`, developer public `@Heisenman` | [pirb.tech](https://pirb.tech/), [PIRBView bot](https://t.me/PirbViewBot), [project Medium feature explanation](https://pirb.medium.com/pirbview-contract-scanner-by-pirb-dd219120c2de), [PIRBView Guide](https://t.me/PIRBViewGuide), [public guide mirror](https://telemetr.io/es/channels/2328990747-pirbviewguide/posts) | `docs.coinscan.com` describes **another CoinScan trading platform**. The `@coinscan` alias alone is not proof of any relationship. `$PIRB` token is not the bot's scan verdict. |

**Screenshot-only metadata:** SAFE shown with 1,326 monthly users, PIRBView 36,059; screenshots display affiliate incentives of 80% (SAFE) and 90% (PIRB). These are **user-supplied UI snapshots**, not independently validated active-user, revenue, billing or audit metrics. Their unusually high displayed commissions create potential distribution incentives, NOT proof that safety outputs are deliberately false. Monsta shows its public bot handle but no independently verified current usage/revenue.

**GitHub code audit:** Global public repository-name searches on 2026-11-07 for `MonstaScanBot`, `MonstaLabs token scanner`, `PIRBView`, `PIRBViewBot`, `SafeAnalyzerbot` returned **no verifiable first-party bot source repositories**. This is an evidence-limit statement, not proof that private or undiscovered code does not exist. No published vendor open-source licence allowing us to copy their bot implementation was verified. **We can reproduce independently known ideas with our own code; DO NOT claim vendor code is free/open source, or scrape/invoke private bot endpoints.**

## 2. Monsta | strongest competence: social + first-observed attention + bundles

First-party official docs:
- [Token Scanner](https://docs.monstalabs.io/core-features/token-scanner): advertises >100 chain coverage, price/market cap/ATH/LP value/lock, holder/developer distribution and EVM tax/bundle/limits. Chain marketing is not per-chain canonical support proof. No live scan was run here.
- [X tools](https://docs.monstalabs.io/core-features/x-twitter-tools): `/x {handle}` account age/status and claimed handle-recycling info; `/del {handle}` purported deleted-post recovery; `/mention {CA}` claimed first five accounts mentioning exact CA; `/prev {handle}` prior CA posts.
- [Social commands](https://docs.monstalabs.io/core-features/social-commands): `/web {domain}` registration/NS/DNS/TXT; `/user {handle}` alleged Telegram user identity/history; `/soc {CA}` social account discovery. Returned accounts are **candidates requiring issuer/exact-CA binding**. Deleted X posts and historical TG account history require provenance and rights, not blind trust.
- [Bundles, Tax's & Wallets](https://docs.monstalabs.io/core-features/bundles-taxs-and-wallets): `/bundle {CA}` bundles + held/sold; `/tax {CA}` ETH fee receiver flow; `/wallet {address}` balance. Multiple commands' marketing text has copy/paste inconsistencies (e.g. wallet example appears as `/tax`); do not infer exact API format beyond documented command. `/calc` valuation, low incremental.
- [Smart Alerts](https://docs.monstalabs.io/core-features/smart-alerts): scanned-asset LP lock/burn, DexPaid/CTO, pump/MC thresholds, launch migration, bags claims. These are claims of **Telegram user notification capabilities**; not source-clock-certified feed and cannot substitute for original machine+delivery receipt.
- [Market commands](https://docs.monstalabs.io/core-features/market-commands): `/pvp {name}` similarly named cross-chain tickers ordered by volume. Good idea for **symbol collision / clone token** adversarial checks, but volume is not identity.
- [PNL cards](https://docs.monstalabs.io/core-features/leaderboards-and-pnls): `/pnlath` uses visible historical ATH; this measures **paper peak**, NOT a realizable position exit. Negative-control requirement under existing Alpha outcome contract.
- [Vendor website](https://monstalabs.io/) claims free baseline/freemium and optional premium but does not publish validated machine API endpoint, public rate limits or open bot code. `API = NOT_VERIFIED`, not `API impossible`.

**Incremental hypotheses:**
1. `X_IDENTITY_REUSE_CHAIN`: issuer posts CA after an X account handle or Telegram username reuse; account ID history and prior linked CA may flag serial promotion; test source validity and legitimate rebrands.
2. `EARLIEST_SOCIAL_MENTION_DECISION_CLOCK`: source-declared first five CA mentions vs internal first *observed* timestamp and actual original publication. Only independent authenticated post URL/author/date enters research. Cannot award prospective machine discovery using later-reconstructed old posts.
3. `SOCIAL_ATTENTION_TO_QUALIFIED_BUYER`: detect verified promotion BEFORE new independently financed wallets and liquidity improvements vs mere pump-following KOL posts. **Existing S7 owner** already specifies DEX boost/profile attention truths; this is a **new social-source challenger** only if source rights and timestamp integrity pass.
4. `SIMILAR_CA_OR_TICKER_COLLISION`: compare similarly named assets across chain/issuer to prevent token misidentification, not price-chase into a clone.

**Major risks:** claims about deleted posts/history lack independent immutable provenance; bot social API coverage & completeness not documented. Telegram access can leak token/watchlist interest, chat memberships or message content; do NOT add any vendor bot as admin to private Research/Framework groups. No Telegram user-account scraping or unauthorized X history extraction. Bot output is potentially selected/incentivized, not canonical.

## 3. PIRBView | strongest competence: early-wallet anatomy, overlap and map-based overhang

First-party product [PIRB website](https://pirb.tech/) and [2023 official feature write-up](https://pirb.medium.com/pirbview-contract-scanner-by-pirb-dd219120c2de) confirm:
- `/e {CA}` first **50 buyers** (free at original documentation); related PRO claims tracking first 100 with alerts (see [CoinMarketCap project description](https://coinmarketcap.com/currencies/pirb/), independently presented but project-supplied).
- `/a {CA}` airdrop map; `/b {CA}` bubble holder links; `/h {CA}` top holder analysis; `/i`/`/s` light/full scans; `/tax {CA}`, `/ta` and `/ma` TA/MA chart overlays.
- [PIRBView guide public mirror](https://telemetr.io/es/channels/2328990747-pirbviewguide/posts) describes `/o CA1 CA2` **OverlapMap**, common owners among two token's top 80 wallets at scan time; `/floor CA` holder buy-in levels (Solana); `/pnl wallet chain` historical P/L from last 15 traded tokens (claimed PRO 50); `AirdropMap` 50/PRO 210 recipients and current retained/sold state; `HoldersMap` buy/sell/transfer statuses; `BubbleMaps` up to 10 clusters among top 100 (PRO 20 clusters/top 200).
- These limits are **vendor-documented marketing descriptions, not measured current output or coverage assurance**. Individual group categories can overlap and should not be summed. The claim that more common holder overlap means greater future upside is an **UNVERIFIED HYPOTHESIS** very prone to survivorship, KOL-selection and common-bot/market-maker confounding.
- PRO access claimed [by project site](https://pirb.tech/) as holding >=34,710 PIRB (0.05% of supply) or ~0.1 ETH/month. Neither an appropriate framework dependency nor justified by this research. Don't send ETH, sign transactions, or verify personal wallets with vendor bots for research.
- No authenticated read-only REST/API or official bot source code identified. **Only manual/permissioned independent challenger data if access is lawful and bounded.**

**Incremental hypotheses:**
1. `FIRST_50_QUALIFIED_RETAINED_BUYERS`: count *independent funded entities* among first 50 after filtering bot/MEV/routers, time-specific retained % and sale overhang. Existing S2/S3/S4 owns much of this. PIRB output only challenger if frozen at same timestamp.
2. `AIR_DROP_TO_SYBIL_DISTRIBUTION`: founder/treasury transfer maps, subsequent transfers, linked wallet funding and simultaneous sell; distinguish real market buys from free distributions. False positive risk for legitimate marketing airdrops and AMM infrastructure.
3. `TOKEN_PAIR_HOLDER_OVERLAP`: top-N overlap across token pairs plus issuer/funder linkage. **Compare to baseline Jaccard overlap and propensity expected from shared chain, liquidity, meme regime and popular KOL**. Beware true upside in tokens with zero overlap (new audiences).
4. `WHALE_COST_BASIS_EXIT_OVERHANG`: top holder average acquisition cost, realized sales, current concentration and size-specific available exit. No invented all-time average when CEX deposits or cross-wallet transfers obscure cost basis.
5. `LAST_15_TRADES_WINNER_BIAS`: P/L summary on only 15/50 visible tokens is not full wallet skill. Native S2 already requires realized+losing exits, survivorship, median copy window, cash exit, recent edge decay and matched controls. Keep provider P/L as biased challenger, not truth.

**Novel from ROCCO rug negative case:** [historical onchain-forensic case](https://github.com/Donh91/Meme-Alpha-Lab/blob/main/research/alpha_audit/2026-11-07_ROCCO_ETH_V4_COORDINATED_DUMP_RUG_FORENSIC_V1.md) established 4 wallets bought same second 36s after launch and exited together; later a common ETH beneficiary linked them, but that **later evidence was unknowable at the initial timestamp**. This is a direct adversarial test of PIRB first50/BubbleMap claims. A pure same-second group must not be upgraded to `COMMON_CONTROL` without independent supporting edges, and never use the later beneficiary in a simulated pre-rug alert.

## 4. SAFE Analyzer | strongest competence: static contract gates, modest incremental value

- [Official bot docs](https://www.dexanalyzer.io/docs/safeanalyzerbot): `/safe 0x...`; claims BSC/PancakeSwap-era tokenomics/holders/owner/LP/limits, malicious-code checks, tax/mcap; may also support ETH in newer API. Website says >20k reports daily, **unverified marketing claim**, and content is older.
- [Report field description](https://www.dexanalyzer.io/docs/safesniper-desc): owner `STILL_EXIST / RENOUNCED`, lock rate, max tx, honeypot risk with simulation caveats. Owner renouncement does not establish safety against V4 inventory dumps, malicious hooked pools, developer-linked distributor wallets or quote depletion.
- [Official DexAnalyzer API & prices](https://www.dexanalyzer.io/api): documented developer access via **POST API**; displayed **$999/month** personal entry, **$2,699/3 months** commercial and **$4,999/6 months** commercial, enterprise custom; lists BSC/ETH forms. Public docs do not establish a free high-volume API allowance, authorized API key or general chain coverage. **Direct purchase/recommendation: REJECT** under the framework's <$40/month API preference/budget.
- Affiliate 80% screenshot raises a conflict-of-incentives research question but does NOT prove unsafe results. Its Telegram recommended group-admin role is **unnecessary** for our framework and would expose sensitive group activity.

**Value:** independent `SAFE_PROVIDER_LABEL` challenger for canonical **S1 EXECUTABLE_SELLABILITY_TRUTH** and transversal `X0 DISAGREEMENT_ALPHA`. Compare raw risk label with source-verified privileged functions, actual paired route, $100/$500/$1000 net exits, liquidity at cutoff, and later egress. Do not buy expensive API merely for an extra contract score.

**Critical negative:** ROCCO's GoPlus (NOT SAFE Analyzer) said basic ERC20/no mint/no honeypot and LP burned, yet the asset lost >99% and its ETH quote capacity vanished. **This illustrates class-level static-vs-economic failure, NOT a proven false-safe claim issued by SAFE Analyzer for ROCCO.** Never falsely attribute a vendor output that was not queried.

## 5. Public methods/code we CAN inspect and legally reuse, separate from these proprietary bot implementations

| Reproducible source | Snapshot/license evidence | Existing-system use | Intellectual-property/drift constraints |
| --- | --- | --- | --- |
| [NetworkX](https://github.com/networkx/networkx/tree/e59d71890e745effb3724dc4b5620b23f92e0ee3) | GitHub main `e59d71890e745effb3724dc4b5620b23f92e0ee3`; **BSD-3-Clause** confirmed in upstream `LICENSE.txt` | Connected components, temporal multigraphs, adjacency, Jaccard/bipartite holder overlap for **existing S3** | Graph algorithms are not evidence of beneficial control. Respect licence when copying code; prefer dependency only where existing environment permits. |
| [Sourcify source code](https://github.com/sourcifyeth/sourcify/tree/d9fc09b1fa81be715b9b76634e77b612f9506689) | Repo at `d9fc09b1fa81be715b9b76634e77b612f9506689`; **MIT** in upstream LICENSE, repo last updated 2025 | Verify independently submitted Solidity sources/ABI versus bytecode | **Use current [Sourcify v2 API](https://docs.sourcify.dev/docs/api/index.html)**. Legacy v1 API shutdown 2026-07-07. API forbids mass crawling; for bulk use released Parquet/BigQuery dataset. No wallet keys. |
| [Slither](https://github.com/crytic/slither/tree/97c1d10d8107e76a9426dd484c03c1afd846c186) | `97c1d10d8107e76a9426dd484c03c1afd846c186`, **AGPL-3.0** | Reference static Solidity/Vyper analysis/contract privilege checks | AGPL obligations and environment/security isolation before integration; avoid copying internals into our code. Re-verify compiler dependencies and untrusted contract inputs. |
| [Blockscout](https://github.com/blockscout/blockscout/tree/5e22da2f0427ff11b99736d5ede34cccfb168878) | `5e22da2f0427ff11b99736d5ede34cccfb168878`; upstream LICENSE is **LicenseRef-Blockscout v1.0 effective 2026-04-22**, NOT MIT | Use instance public explorer/API v2 to reconstruct holders, swaps, transfers, internal value and funding | **Use public documented API per instance policy**; do NOT copy/relicense Blockscout code as open MIT. Provider API outputs not historical snapshots unless block scoped. |
| [Uniswap v4 core](https://github.com/Uniswap/v4-core/tree/bea7f6d1c11cd5dc4f0d5151ffa37a1c239feee6) | `bea7f6d1c11cd5dc4f0d5151ffa37a1c239feee6`; no universal licence verified from repository root; check contract-level SPDX before copying | Decode canonical V4 swap/poolID/hook semantics for Ethereum rug scenarios | Never infer token CA from 32-byte pool ID; no blanket licence claim. No swaps or wallet actions. |
| [GoPlus Security API](https://docs.gopluslabs.io/reference/api-overview) | [published free rate](https://docs.gopluslabs.io/reference/support) **30 calls/min** | Existing contract risk challenger and EVM/SOL simulations where chain-specific support verified | Free API can rate-limit; never treat `safe` as buy permission. Existing framework already uses it; do NOT create a new adapter. |
| [Honeypot.is API](https://docs.honeypot.is/ishoneypot) | Current [auth docs](https://docs.honeypot.is/authentication) say **no key currently required**; may change | Honeypot, tax, maxSell/gas and pair reference challenge for supported chains | Simulation may be missing/fail; 200 responses do NOT guarantee executable future size. Respect ToS; existing S1 already owns. |
| [DEX Screener API](https://docs.dexscreener.com/api/reference) | Public documented token/pair endpoints at **300 req/min** and token profile/paid order feeds at **60 req/min** | Identity, market event, paid promotion observations, liquidity/quote fields, first **observed** changes for S7 | Data/paid flags NOT verified KOL endorsements or true upstream event origin; already ingested where applicable. |

**No complete third-party codebase for Monsta/PIRBView/SAFE was located or copied.** This code inventory identifies independent auditable substitutes and licence restrictions, not new implementation authority or permission to scrape vendor bot responses.

## 6. Alpha Lab architecture dedup, exactly where each idea belongs

| Finding | Existing owner/lane, current overlap | New research value vs duplicate | Disposition |
| --- | --- | --- | --- |
| X early CA mentions, deleted posts, prior ticker/CA per account | S7 attention conversion + existing social research and exact first-known events | Potentially **new source family**, but archival first-post clock and compliance are not established | **ADAPTER_GAP / S7 shadow challenger**, not a new X collector |
| TG account/website DNS identity recycling | Existing #126 issuer binding / S7 and Narrative Researcher | Independent domain and user-ID provenance, useful for serial-larp detection if truth is provable | **P2 METHOD_ONLY**, beware privacy and false positive |
| /bundle, first50, airdrop, bubble-map | S3 cluster/relationships; #88 wallet detective, S4 birth/retention | Mostly overlapping; useful cross-provider disagreement/falsifier | **S3 existing owner only**, no additional clustering service |
| /o top80 overlap cross-token | S3 graph and S2 wallet qualification | Potential fresh **cross-CA co-holding** feature, but denominator/popularity selection confounds | **P1 SHADOW HYPOTHESIS**, first raw benchmark |
| PIRB wallet P/L last 15/50 | S2 wallet skill, complete losers and copyability required | Mostly **INFERIOR/INCOMPLETE** to canonical full replay | **REFERENCE_ONLY**, reject standalone signal |
| LP alerts / SAFE checks | S1 executable quote and #194/#98 | Provider disagreement has research value, not proof of exit | **S1/X0 challenger**, no paid SAFE API |
| PIRB/Monsta ATH PNL cards, heatmap, fib/RSI, follower counts | Existing outcome ledger and market stack | Weak incremental, selection/survivorship and false fill risk | **DUPLICATE_NO_ACTION** |
| PIRB Telegram /token call leaderboards | Existing first-known/eligible denominator | Candidate complementary social call source if publisher ID+timestamp recoverable | **SOURCE_GAP**, do not fake machine signal |

**Research priority is NOT a recommendation to immediately build all features.** Canonical `QUEUE_V1.json` remains unchanged, original S1/S2/S3/S7 priorities and active work respected. If heavy source work begins, reuse original owner and obey one-heavy-lane rule.

## 7. Three bounded experiments with explicit falsifiers (no implementation yet)

### E1 | Monsta X chronology -> S7 attention conversion

**Case input:** original frozen exact CA + chain, verified issuer X account ID and archived source post permalink; provider reports `first 5 mentions`, deleted posts or prior CAs, if lawfully supplied.

Freeze per post: `published_at_utc` (only independently verified), `first_machine_observed_utc`, `provider_observed_utc`, account numeric ID, handle as-of, exact CA in text, archival survival/version hash, source link, missing coverage. Never turn a retrospectively recovered deleted X post into prospective visibility.

Comparator: S7 current native DEX boost/profile first-observed vs Monsta vendor observation vs 10–30s/1m raw buyer retention and sell-side, by exact eligible source. Controls: same launch age, chain, market regime, social baseline, token float, prior price move. Outcome: independent buyer conversion, time-to-new-liquidity, realizable exit, false positive rate. **Kill** if X first five mentions were already stale/incomplete or do not add signal over existing S7 attention observations.

### E2 | PIRB wallet overlap/airdrop -> S3 independent-entity and S2 wallet skill

**Input:** same frozen top-N holder and first-N buyer windows at `T0`, token pair CA1/CA2, source block hash/time and executor labels.

Candidate metrics: `JACCARD_OVERLAP(raw)`, `JACCARD_OVERLAP(excluding LP/routers/CEX)`, share of first-N unique funded economic entities, repeated bidirectional token/native transfers, incoming free allocation and proportion sold, center/leaf fan-out, cross-token co-buy stage. Relationship must follow existing S3 taxonomy; shared CEX/routing ≠ same owner. Keep direct transfers and inferred human control distinct.

Benchmark exact outcomes +15m/+1h/+6h/+24h/+72h, compare provider map to raw holder and transaction reconstruction, matched independent investors, launch snipers and successful memes. **Negative control:** ROCCO's initial four same-second buys cannot use next-day shared-beneficiary transfers when deciding at T0. **Kill** if overlap/cluster metric fails to beat concentration + same-block buying + early retention baseline out of sample, or bans a disproportionate share of real winner cohorts.

### E3 | SAFE/Monsta/GoPlus "SAFE" or LP lock -> S1 actual exit

Without paying third-party subscriptions, compare provider scan fields **only when permissioned samples exist** to current S1 GoPlus/Honeypot and canonical historical route evidence. For each cutoff, calculate $100/$500/$1k nominal-to-actual USD roundtrip net after gas+tax+slippage and note quote freshness. **Counterexample:** ROCCO native holder post-crash: marketed "$2,249 pool liquidity" but reported ~0.00185 ETH quote (~$4.14), GoPlus (NOT SAFE) listed no mint/honeypot, burn-position LP. No provider label can be called false SAFE absent an actual same-time provider output. **Kill** paid provider if it adds no calibrated incremental detection over existing safety+quote baseline.

### Minimum evidence/promotion

- Propose **one bounded original-owner shadow PR at a time** only when raw authorized source exists; no new continuous Telegram polling.
- Study at least matched winners and losers, not just rugs; include `SOURCE_UNAVAILABLE`, `INELIGIBLE`, fake/imposter issuer, liquidity failure, stale post, missing first-known.
- All documents and derived rows must remain public-safe, exclude user wallet mappings and private positions.
- Negative controls: one vendor-safe-but-exit-fail, one provider-unsafe-but-route-works, one true four-wallet team cluster, one independent synchronized launch bot group, one genuine viral organic meme, one fake resurrected KOL recycled account.
- Original #77/#85 outcome grading and #126 scanner recall must compare only same admissible UTC windows; do not label a provider discovery a Framework discovery.
- Terminal `SUPPORTED` only after signed-off independent evidence and prospective effect. Until then: `HYPOTHESIS / METHOD_ONLY / NO_PRODUCTION_CHANGE`.

## 8. Operations, cost and security decision

**Do not directly integrate Telegram third-party bots yet.** No first-party bot API/open code was established for Monsta/PIRBView; SAFE published API is prohibitively expensive. Telegram's [current Bot-to-Bot Communication Mode docs](https://core.telegram.org/bots/features) describe opt-in bot-to-bot interactions in some group/private contexts, but that does NOT prove these three proprietary bots enabled it, grant output scraping permission or make the interface stable. The older generic Bot FAQ describes ordinary bots ignoring other bots, so check exact operational mode and consent rather than claiming bot-to-bot is categorically impossible.

**Cost:** report/archive research $0 extra provider spend. Potential existing authorized raw-API challenger measurements via GoPlus/DexScreener/Honeypot/Blockscout/Sourcify subject to per-provider rate/terms and existing S5/original owners. No additional scheduler, paid Telegram PRO, private GitHub Actions polling, new cloud database, wallet signing or API key exposure. Concurrency and 3,000 minute GitHub Actions monthly owner ceiling still apply.

**Security:** Never send owner MetaMask/Robinhood wallet addresses, private CA interests or portfolio mapping to third-party Telegram bots. Never connect wallets, sign messages, follow verification transfer prompts, grant admin rights in private groups, or reveal protected alerts. External bot content may include malicious links, fake issuer associations, wallet-drainer promotions or persuasive affiliate claims.

**Privacy/ToS:** Research of public chain addresses and public/authorized channel publications only. Follow X/Telegram terms and vendor licence. No mass message scraping, account impersonation, vendor access bypass, bot-group admin promotion or attempts to reconstruct private identifiable individuals.

## 9. End disposition, next original-owner proof and receipts

**Monsta:** `METHOD_ONLY_TRANSFER / S7_SOCIAL_SOURCE_ADAPTER_GAP`, top focus earliest-mention and reused issuer/social identity with real published vs observed clocks.  
**PIRBView:** `METHOD_ONLY_TRANSFER / S3_S2_DEDUPED / CROSS_CA_OVERLAP_CHALLENGER`, top focus first50/airdrop/entity-adjusted overlap rather than any raw wallet quality score.  
**SAFE:** `SOURCE_CHALLENGER_ONLY / PAID_API_NO_GO / S1_X0_EXISTING_OWNER`, no vendor API buy.  
**Research Lab #1512:** store this durable external specialist intake and original issue receipt; **do not** rewrite existing queue rank/state or automatically open implementation PR.  
**Alpha Lab #88/#126:** issue-reference this study, and retain original ownership on any future experiment.

**UNOBSERVED / NOT CLAIMED:** No actual Telegram bot was operated, no token submitted to the bots, no bot proprietary source code obtained, no paid vendor account/API used, no independent recall or precision test, no merged scoring changes, no source-to-Framework data feed, no automated trading, no canonical Case Memory event. Future user-submitted CA analyses should use the already merged universal 22-domain Alpha Lab template.
