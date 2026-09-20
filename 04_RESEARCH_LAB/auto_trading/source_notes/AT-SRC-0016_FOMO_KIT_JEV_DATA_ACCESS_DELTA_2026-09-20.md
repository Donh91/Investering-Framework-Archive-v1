# External Intelligence Delta Archive - FOMO Kit, Jev and Data-Access Challengers

Date captured: 2026-09-20
Status: RESEARCH_ONLY / DELTA_ONLY / NO_NEW_AUTHORITY
Primary owner: Alpha Lab / #1087
Purpose: preserve only material information from the 2026-09-20 owner-supplied FOMO Wallet Kit screenshots and X/Grok brief that was not already represented in the framework.

## Deduplication performed

This archive was written only after checking current main against the new material.

Already present and therefore NOT re-archived as new findings:
- FOMO Robinhood Radar architecture, wallet resolution, receipt provenance, dust/seeded-token filtering, wallet-book reconstruction, burst/convergence and exit consensus.
- ADDRESS_ROLE_GATE and service/inventory/router/pool exclusion before wallet PnL.
- entity-adjusted wallet convergence, point-in-time wallet quality, winner-selection controls and prospective/OOS G3 testing.
- rule that one winning trade does not establish smart money.
- Freqtrade, CCXT, NautilusTrader, Hummingbot, FinRL and AI Hedge Fund as execution/research benchmarks rather than alpha evidence.
- official/licensed data > unofficial UI scraping, deterministic risk/execution separation, paper/dry-run before any governed live authority.
- existing capability-routing / API-agent / compounding-learning architecture. No second agent stack is created.

Existing references include:
- AT-SRC-0010_MARAN_RH_TOOL_STACK_AND_WALLET_LEADERBOARD_AUDIT.md
- AT-SRC-0012_FOMO_RADAR_WALLET_INTELLIGENCE.md
- AT-SRC-0012_FOMO_ROBINHOOD_RADAR_FORENSIC_BENCHMARK.md
- CLEAN_G3_INCREMENTAL_EDGE_PREREG_v1.md
- MOONSHOT_SENTINEL_CHAMPION_v1.json
- EXECUTION_SUBSTRATE_AND_TRADINGVIEW_POLICY_AUDIT_2026-09-13.md

## Delta A - FOMO Wallet Kit source surfaces

Owner-supplied screenshots expose a broader external dataset/tool surface than the currently archived FOMO Radar implementation.

Source claims visible in screenshots, requiring independent verification:
- FOMO token holder view carries Position, PnL and Avg. entry expressed in market-cap terms.
- Opening a trader row reportedly exposes buys and sells with market cap at execution, average entry, dollars invested and trader thesis.
- One CATE snapshot reportedly contained 87,800 holder rows.
- Larger candidate sets are claimed:
  - 2,526 KOL wallets
  - 66 degen wallets
  - 60-wallet NFT tracker across Robinhood Chain and Arc, tagged with Founding Charter / OnchainSharc
  - separate lists for Pons, ARC and stable memes.
- Source workflow:
  - profile -> copyfomo.com/find -> address
  - address -> Blockscout or Arc explorer -> full history
  - handle -> FOMO Holders table -> average entry across touched tokens
  - fomoscope.xyz -> API access rather than manual clicking.
- Source caveats are unusually compatible with framework discipline:
  - copied addresses must be checked before trusting the set
  - one-token/one-snapshot observations must be refreshed
  - low average entry does not mean a wallet still holds; sells matter.

### CATE winner-conditioned casebook

The screenshot is useful as a candidate-generation casebook, not evidence of repeatable skill.

At a claimed ~120m CATE market cap, early-wallet examples include:
- KCh8 - avg entry ~3.3m, screenshot PnL claim +1,356%
- PoorGoat_ - ~3.7m, +2,663%
- Erika0616 - ~4.8m, +2,287%
- Bayc364 - ~6.0m, +1,885%
- boosteryting - ~6.8m, +1,076%
- Aurelius0121 - ~12m, +389%
- DopamineFeenFr - ~12.7m, +367%
- christianbieri - ~12.8m, +805%
- bombocapital - ~16.4m, +624%
- hespaid - ~18.5m, +347%
- RelaxShrimp - ~23.2m, +294%
- Bull_Path - ~24.5m, +399%
- ticktockstocks - ~29.2m, +311%
- theyeeman - ~29.7m, +304%
- BarBarrBinks - ~35.7m, +241%

The same source labels later large bags such as fabulous, SolSwizzle, MarcusVickEBC, GMannnnn and hob66 as late entrants. Preserve only as a retrospective casebook for falsification.

Example detail visible in screenshots:
- PoorGoat_ on CATE reportedly invested $129,617.25, avg entry ~$3.7m, 528 transactions and position ~$2.9m at snapshot.
- GMannnnn example shows multiple sells around ~$105.6m-$108.4m market cap. This reinforces that current position, realized exits and average entry must be separated.

No wallet above receives SMART_WALLET status from this archive.

## Delta B - FOMO ecosystem tools not yet represented by name

The final screenshot identifies seven surfaces around FOMO profiles:
- fomoscan.sh - claimed full Solana and EVM addresses / one-click copy
- copyfomo.com/find - claimed profile-to-wallet resolution
- fomoguard.family - claimed pre-buy token scoring
- fomosignal.family - claimed wallet, position and cluster tracking
- copyfomo.com - copy-trading surface
- github.com/mickeyhogen/fomo-helper - browser helper for holder notes and position sizes
- fomoscope.xyz - claimed APIs for leaderboards, trades and positions

Research disposition:
- fomoscope.xyz: HIGH PRIORITY API feasibility / denominator-scale research lead.
- copyfomo.com/find and fomoscan.sh: identity-resolution challengers only; cross-verify on-chain.
- fomosignal.family: external cluster-hypothesis generator only.
- fomoguard.family: external score challenger only; no champion weight without transparent features + prospective evidence.
- fomo-helper: code-review candidate for extraction/holder-analysis ideas; license/security/semantics review before reuse.
- copyfomo execution: OUT OF SCOPE for autonomous execution.

API/source failure must remain UNKNOWN/DEGRADED, never zero/absence.

## Delta C - wallet candidates exposed in screenshots

The screenshots expose candidate handles and EVM address mappings. Because screenshots can truncate or visually wrap addresses, the canonical rule is:

SCREENSHOT_TRANSCRIPTION -> UNVERIFIED_IDENTITY -> MACHINE/SOURCE RE-PULL -> ONCHAIN CROSS-CHECK -> ELIGIBLE_CANDIDATE

Visible handles include:
ogle, MEADGod, 0xnobi, kyle, unipcs, econoar, traderpow, CryptoKaleo, AvgJoesCrypto, loganlim_x, MINHxDYNASTY, frankdegods, rasmr, orangie, tjrtradez, DipWheeler, remusofmars, 0xleo, bluntz_capital, The__Solstice, PoorGoat, FartmanSacks, himgajria, notanicecat69, 0xAvast, Rowdy, brrgrrrz, wrld_sol, inyourwalls, SolSwizzle, Salem1299534, Quanterity, feeeq, boosteryting, theyeeman, DumbCrayonEater, change, metaversejoji, flbs and insentos.

Do not promote screenshot-transcribed addresses into canonical identity. Re-pull the original table/API.

## Delta D - proposed Robinhood/Arc prospective experiment

This is incremental mainly because the new source may provide a much larger denominator and API-accessible position/trade history.

Champion:
- existing Alpha Lab / Moonshot discovery machinery.

Challenger:
- verified FOMO/Fomoscope wallet activity features.

Required experiment:
1. Freeze wallet-set membership BEFORE future outcomes.
2. Resolve profile -> execution wallet -> address role -> economic entity.
3. Reconstruct full eligible history, including losers, rugs, dust, passive receipts and exits.
4. Compute wallet quality only from outcomes matured before each candidate cutoff.
5. Separate single-wallet signal from independent multi-wallet convergence.
6. Test timing relative to public/social discovery and Alpha Lab first-seen.
7. Measure incremental discovery lead time, precision, top-k recall, FNP, rug/unsellable burden, MFE/MAE, sellability and realized outcome.
8. Stratify by Robinhood/Arc venue, token age, entry market cap, liquidity and regime.
9. Preserve E2/wallet sensor as HOLD until incremental effect survives entity, insider, Sybil, sniper, capacity and winner-selection controls.
10. Kill/revise if edge disappears after these controls.

Potential high-value trigger remains:
VERIFIED_INDEPENDENT_WALLET_CONVERGENCE -> P2 DEEP_DIVE
not
SMART_WALLET_BOUGHT -> BUY.

## Delta E - Jev / TypeSafe decision-layer lead

Owner supplied an X/Grok brief describing Jev as a typed System-One decision model with Choice / Score / Noul outputs, proposed for cheap routing before expensive browser/research/retry/subagent operations.

This archive does NOT accept vendor performance, latency, price, RLCD or biography claims as verified facts. Those require first-party verification before implementation.

Incremental hypothesis worth retaining:
- benchmark a typed low-cost decision layer as a CHALLENGER inside existing capability routing.
- do not create a GrokBot parallel orchestrator.
- candidate actions map conceptually to existing routing semantics: reuse_cache, stop_retry, run_deterministic, chat_only, research_capped, allow_subagent, ask_human.
- typed output reduces format ambiguity but does not establish epistemic correctness.
- start shadow-only, log decision/action/adherence, and require rollback/kill switch.
- evaluate whether it reduces expensive model/tool calls without worsening task quality, false negatives, safety or reliability.
- Sol/other System-2 models remain for reasoning, synthesis, code/research tasks where needed.

Promotion evidence should include:
- routing agreement/disagreement versus existing director
- avoided expensive calls
- incremental false negatives / missed high-value tasks
- latency/cost delta
- calibration of confidence if exposed
- failure under stale/incomplete state
- deterministic reproducibility of downstream policy
- no silent authority expansion.

## Delta F - data-access challengers

Owner/Grok supplied:
- Panniantong/Agent-Reach
- D4Vinci/Scrapling
- whaleyxbt/patchright-enhanced

These are NOT adopted dependencies.

Incremental research question:
Can any of these close a demonstrated source-coverage/reliability gap more cheaply or robustly than existing official API / connector / Firecrawl-style routes?

Required ordering remains:
OFFICIAL/API -> deterministic HTTP/source adapter -> adaptive scraper if permitted -> browser only when necessary.

Evaluate each only against a concrete failing source and record:
- terms/robots/login constraints
- data fidelity
- timestamp/provenance quality
- selector drift resilience
- rate limits
- anti-bot risk
- latency/cost
- deterministic replayability
- maintenance/security/license burden.

No generic 'scrape everything' capability is promoted.

## Delta G - Jesse

Jesse was newly owner-supplied, but the broad execution/backtest category is already deeply covered by the existing execution-substrate audit.

Retain only as a future comparison candidate if a surviving strategy requires a Python crypto strategy-development/backtest environment and Jesse offers a concrete incremental property not already met by Freqtrade/current simulator.

No new engine or integration is justified now.

## Priority after dedupe

P0 - verify Fomoscope/API feasibility and whether denominator-scale historical + point-in-time trade/position data can be obtained lawfully/reliably.
P1 - prospective Robinhood/Arc wallet cohort from independently verified identities, with frozen membership.
P2 - independent-wallet convergence challenger against existing champion, using existing G3/P2/P3 owners.
P3 - Jev typed-router shadow benchmark only after first-party/API verification and only if it can replace expensive low-information decisions.
P4 - data-access challengers only for proven coverage gaps.
DEFER - Jesse and additional trading engines until execution semantics become a bottleneck.

## Authority

Research archive only.
No BUY/SELL/sizing.
No copy trading.
No wallet/exchange keys.
No autonomous capital authority.
No new parallel scanner, scorer, ledger, learning controller or orchestrator.
