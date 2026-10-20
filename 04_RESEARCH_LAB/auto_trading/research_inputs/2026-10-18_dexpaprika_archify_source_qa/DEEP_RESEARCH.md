# External Source QA Deep Research: DexPaprika + Archify (2026-10-18)

**State:** RESEARCH_ONLY / SOURCE_QA_SMOKE_COMPLETED / INCREMENTAL_VALUE_UNPROVEN  
**Authority:** existing Alpha Lab / Meme Alpha source-adapter owner Archive #1017, empirical owner #1087, prospective denominator owner #1340, Meme-Alpha-Lab #126. No new owner.  
**Control-plane baseline:** `4afaf77c36e7fafbcbdddf821735064bf6563c83` (main before this research branch).  
**Scope:** public, unauthenticated read-only provider checks and upstream documentation/code-source review. No private dataset read, no credentials, no trading, no paid service, no external code installed, no new task/queue/engine.  
**Evidence class:** external source claims + illustrative *current* anonymous smoke probes. Live API observations were not immutably captured in the restricted plane, so these are **not** admitted historical, point-in-time, outcome, performance, or source-quality proof.

## Executive decision

**DEXPAPRIKA: CONDITIONAL CANDIDATE, NOT ADOPTED.** New upside: its public `GET /networks` explicitly includes `robinhood`, alongside `ethereum` and `solana`. It can be compared with existing DexScreener and GeckoTerminal source families for pool/token discovery context and **liquidity/sellability source QA**. It is not an early-block Robinhood/ETH/Solana launch source, identity authority, independent validation of transaction hashes, or a historical Task 2 data substitute. Free-plan lag and history depth matter.

**ARCHIFY: BORROW PRESENTATION PRINCIPLE / ISOLATED VISUAL BENCHMARK ONLY.** Potentially useful to visualize existing owner boundaries, data lifecycles, trust boundaries and Cycle Navigator PATH, but a diagram does not certify code correctness. No global skill installation, repo-wide agent permission, private repo upload, public deployment or production visual changes.

**WEAK CONCLUSION THAT MUST NOT BE PROMOTED:** multiple aggregators showing similar data does not prove independent chain-level evidence; they may reflect shared indexing and overlapping venue feeds. Pair `created_at` is not token genesis, token `added_at` is not launch time, volume is not currently executable depth, FDV is not automatically market cap, and a pool is not its token.

## 1. Existing ownership / deduplication

- Archive #1017 explicitly owns a *governed cross-chain source adapter*, preconditioned on its predecessor's verified source-field map. This research cannot satisfy that precondition or activate a chain adapter.
- Archive #1087 requires `exact CA -> chain -> canonical execution pool -> quote -> price -> supply -> MC/FDV -> liquidity -> timestamp/source`, `UNKNOWN != 0`, stale-data quarantine and demonstrably flowing prospective rows.
- Archive #1340 owns immutable candidate denominator, including REJECTED/EXPIRED/NEVER_LAUNCHED/UNSELLABLE/MISSED. Do not retroactively select only winning tokens in any provider comparison.
- Meme-Alpha-Lab #126 and the existing Meme Alpha Supervisor remain execution/observation owners.
- `04_RESEARCH_LAB/external_specialist_dissection/S7_EXECUTION_RECEIPT_2026-10-06.md` documents an already-owned DexScreener/GeckoTerminal event source with a real prospective event denominator, not an invitation to duplicate it.
- `04_MARKET_LEARNING/tactical_microcap_lab/PUBLIC_SOURCE_POLICY.md` already places chain events/explorers above aggregators for identity and market provenance.
- `04_RESEARCH_LAB/auto_trading/research_inputs/2026-09-15_external_tooling_audit/ASTRA_ADJUDICATION_BRIEF.md` requires incremental capability proof before importing any tool.

**Research route:** link a read-only source-QA challenger to #1017 / #1087. Do not register a second ledger or permit this to bypass source-field-map or scientific gates.

## 2. Vendor contract confirmed from its current official pricing/docs

Official references:
- https://dexpaprika.com/api/pricing
- https://github.com/coinpaprika/dexpaprika-mcp (README blob observed `828630af3e744e4a632731247b1c236f74e957fd`)
- https://github.com/coinpaprika/skills/blob/main/dexpaprika-api/SKILL.md
- https://github.com/coinpaprika/dexpaprika-sdk-python
- https://docs.dexpaprika.com/

Contract as shown on official pricing page on 2026-10-18 (re-check before implementation):
- Keyless: 15 req/min per IP; 10,000 rolling-30-day credits; first page of search.
- Free API key: 30 req/min; 100,000 rolling-30-day credits; up to 60s stated data delay; pool OHLCV last 7 days, 10m-or-longer intervals; pagination; no transaction-history endpoint or aggregated token OHLCV.
- Dev: $30/month excluding VAT; 120 req/min; 30 days pool OHLCV incl. 1m; token OHLCV and transaction endpoint.
- Pro: $99/month excluding VAT; 500 req/min; full pool/token OHLCV history; paid transaction endpoint; overage billing possible.
- Data-plan boundaries apply *through* MCP; MCP is an adapter, not a route around paid endpoints. Check `getKeyStatus` after configuring any future key; unreadable keys may silently yield anonymous 200 responses. Paid API uses a different host.
- SSE changes may cost one credit **per update**, not merely per connection. A busy token can rapidly consume free credits.
- Live access does not imply backfillable first-block provenance, independent block timestamps, sellability or exact order execution.
- Source includes both `arc` and `robinhood` network ids; `arc` is **not** evidence of or related to the user's earlier FerrumVir ARC-chain GitHub repo.

**Budget inference:** 100,000 credits over 30 days permit ~2.31 average single-credit requests per minute if used continuously. A multi-chain high-frequency full-universe scan could exhaust even a free allocation. No paid keys, plan changes, auto-recharge or new recurring collectors authorized.

## 3. Actual read-only source probes, 18 Oct 2026

Protocol: anonymous provider network/pool/token REST GET, then existing independent *aggregator* REST GET on the same exact chain/pool. No keys, no wallets. The probes are contemporary snapshots, **not time-synchronized captures**. Exact endpoint links enable later independent reproduction. We intentionally do not place provider price, liquidity, volume, wallet, transaction or restricted normalized payload values into this PUBLIC control-plane report.

| Check | Exact public subject / route | Observed qualitative result | Correct decision |
| --- | --- | --- | --- |
| Network coverage | https://api.dexpaprika.com/networks | `ethereum`, `solana`, **`robinhood`** present | Coverage exists; verify individual DEX/program coverage, first-observed lag and semantics separately |
| Robinhood V4 zero-liquidity case | https://api.dexpaprika.com/networks/robinhood/pools/search?order_by=volume_usd_24h&sort=desc&limit=3 and https://api.dexscreener.com/latest/dex/pairs/robinhood/0xb77683d503a1be7dcd72b5533b9bbea04fc03dac494138db8e32ef8260a760cc | DexPaprika displayed zero reported current liquidity on a high-volume pool; DexScreener returned the pair but **did not expose an explicit liquidity field** | `LIQUIDITY_NOT_PROVEN` / `UNKNOWN`; a missing field must **not** be read as agreement with zero |
| Solana dried-pool negative control | https://api.dexpaprika.com/networks/solana/pools/search?order_by=volume_usd_24h&sort=desc&limit=3 and https://api.dexscreener.com/latest/dex/pairs/solana/Ds2fyB2fnz8F1KjZ8WycHMh2u6aRpjy81errtEtY5nEw and https://api.geckoterminal.com/api/v2/networks/solana/pools/Ds2fyB2fnz8F1KjZ8WycHMh2u6aRpjy81errtEtY5nEw | All three sources described an extremely thin current pool despite large trailing volume | Do not rank by volume alone or assume a realizable entry/exit; source concordance is not onchain proof |
| Solana healthy-pool positive control | https://api.dexpaprika.com/networks/solana/pools/Czfq3xZZDmsdGdUyrNLtRhGc47cXcZtLG4crryfu44zE and https://api.dexscreener.com/latest/dex/pairs/solana/Czfq3xZZDmsdGdUyrNLtRhGc47cXcZtLG4crryfu44zE and https://api.geckoterminal.com/api/v2/networks/solana/pools/Czfq3xZZDmsdGdUyrNLtRhGc47cXcZtLG4crryfu44zE | Same exact Orca SOL/USDC pool; prices and liquidity broadly agree in three asynchronous reads | Useful comparative pool observability, **not** evidence of faster discovery or edge |
| Pool chronology semantics | Same healthy Orca pool links above | GeckoTerminal's reported pool-created date differs by days from DexPaprika / DexScreener | `POOL_BIRTH_CONFLICT`; do not substitute either for exact onchain token birth. Investigate source definition before any temporal test |
| Token metadata anomaly | https://api.dexpaprika.com/networks/ethereum/tokens/0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2 | WETH token metadata include a recently added-to-index field and an extreme ATH field unsuitable as credible genesis/ATH authority without pool/venue reconstruction | `INDEXED_AT != BIRTH_AT`; `AGGREGATE_ATH_NOT_ADMITTED` |

**Critical correction:** The anomalous Solana pool is NOT proven to be a DexPaprika bug. The independent-looking aggregator outputs show the same thin-liquidity condition. The primary issue is **trailing activity vs present sellability**, and ambiguous field semantics. Robinhood's second aggregator did *not* report zero: it omitted the liquidity object.

**NOT PERFORMED:** controlled same-block or same-minute timestamp alignment, complete pool-universe recall, exact birth block verification, factory event comparison, chain-specific sellability swap simulation, provider catch-up latency study, restricted receipt capture, prospective Alpha Lab experiment, original historical Task 2 replay. Those require existing owner + correctly admitted data.

## 4. Actual incremental-value hypotheses, testable and falsifiable

**H1 — Pool metadata QA lift.** At an immutable observation time, DexPaprika identifies correct chain+pool+base/quote metadata or detects missing/implausible current liquidity on some existing Alpha Lab observations that are `UNKNOWN` or materially conflicting in the existing sources. Compare against the **same exact universe and observation clock**, with matching treatment of retries and missingness. Falsifier: no decision-relevant source gap is closed or new provider contributes only duplicate data.

**H2 — Sellability triage context.** A secondary pool-liquidity observation reduces false *assumptions of sellability*, not necessarily real rug risk. Prespecified negative controls include zero/near-zero liquidity with high historical volume; withdrawn pool with old token; V4 concentrated-range liquidity; zero displayed reserves but valid pool identity; no field returned. Falsifier: comparator adds noisy or stale data, or changes an existing true sellability claim into an unvalidated one. Requires actual chain-/DEX-specific execution semantics before any capital inference.

**H3 — Cross-chain supplemental recall.** Cheap provider pool discovery adds independently documented relevant pools (especially Robinhood, Ethereum, Solana) to existing *eligible* Alpha Lab observations before existing sources show them. The prospective denominator remains anchored to #1340; provider missing token/pool is never a negative signal. Falsifier: no lead-time/recall gain at matched cost, or delays erase any speed advantage. Free up-to-60-second vendor latency makes first-block lead-time **unlikely**, not disproved.

**H4 — Archify reduces architecture comprehension burden.** A nonexecuting, source-pinned standalone diagram of public source boundaries clarifies existing trust/data paths without topology hallucination or leaking restricted artifacts. Benchmark static existing architecture diagram / markdown against one generated diagram. Falsifier: unverified invented edge, insecure data movement, slow iPhone rendering, inaccessible/unreadable output or insufficient incremental usefulness.

## 5. Minimal continuation contract

1. **Owner reconciliation first**: inspect #1017 precondition/status and source-field map; #1087 current first-seen source/provenance; #1340 denominator; Meme-Alpha-Lab #126 and existing chain-native RPC / DexScreener / GeckoTerminal owners. If unfulfilled, remain research-only.
2. **Freeze 30 source-QA cases before outcomes**: 10 each Ethereum, Solana, Robinhood; each chain deliberately stratified into fresh/active/withdrawn or thin pools; exact chain+CA, pool id, base/quote, intended observation timestamp; preserve ordinary failures, UNKNOWN and ambiguous identities. A 30-case diagnostic panel is *not* a statistical power claim or hypothesis trial approved by #1557.
3. **Minimal source-health comparison only**: check reachability, schema/type, chain/pool identity, contradictory creation/added timestamps, field missingness, stale data, liquidity/volume separation, 402/403/429 behavior, pagination and credit attribution, cross-provider conflict; no price-direction or trading scoring.
4. **Adversarial checks** in `ACCEPTANCE_MATRIX.md`. Do not take public marketing output as a service-level guarantee.
5. **No private data in public**. If a real immutable provider capture is required, the existing authorized restricted evidence owner creates a private hash-bound receipt; public stores only provider-value-free status and exact immutable binding.
6. **Decision after evidence**: `REUSE_EXISTING`, `ADMIT_READ_ONLY_SHADOW_CHALLENGER` (only after precondition and safe tests), or `KILL_NO_INCREMENTAL_VALUE`. No new source-scoring owner, scheduler, periodic expensive searches, auto-trader, new token scoring, live alerts, model weights or paid plans.
7. Never score Round 3 restricted collections or reopen closed R1/R2 evidence. Historical data supplied at a later index time cannot become a point-in-time forecast feature.

## 6. Archify-specific bounded review

Official upstream: https://github.com/tt-a1i/archify, MIT; file `README_EN.md` observed blob `a87d57dfc5514ff8b1fb76070e04ddc31c69100a`, `SECURITY.md` blob `d0513681f817593543ece09f21514f47e052515e`. It generates a self-contained interactive HTML visualization from typed input. The upstream's newest version and installation guidance may change; pin an exact reviewed version if experimenting.

First benchmark only:
- a sanitized public architecture map of **existing** `GitHub control plane -> restricted plane binding -> source QA -> Alpha Lab research -> evidence ledger`;
- an independent mobile-first PATH conceptual mockup, **not** a replacement for the website.
- Each arrow must carry a checked exact source file/line or explicit `HYPOTHESIS_ONLY`, with forbidden public/private paths absent.
- Render locally from allowlisted public-safe typed inputs, prevent external network imports or outbound data transmission, examine generated HTML/JS/scripts and any upstream skill text before use.
- No `npx skills add ... -g`, `@latest` remote execution, unrestricted repository crawling, private repo exposure, workflow modification or deploy without a separate risk-adjusted review.
- Archify is not an architecture auditor, CI check, source authority or research evaluator.

## 7. Final value order, as of 2026-10-18

1. **NOW:** record DexPaprika as a source-health challenger through existing #1017/#1087, with falsifiers and no integration.
2. **AFTER owner precondition:** test 30 exact cases for source freshness, pool-vs-token semantics, sellability field integrity and unique incremental coverage.
3. **PARALLEL LOW COST:** assess one Archify public-only diagram vs current architecture text as a human usability aid.
4. **DEFER:** paid DexPaprika OHLCV/swaps, SSE collectors, NautilusTrader, extra backtest engine, Agent Desk. Historical Task 2 admission work and Alpha Lab full prospective denominators outrank tool expansion.

## Evidence status and next readback

- This is a **research candidate**, not a code-adoption proposal. Case probes were read-only and anonymous; there is no installed runtime and no empirical uplift estimate.
- In the originating session, source URLs and upstream GitHub README/policy blobs were directly checked. Subsequent users must verify newest docs/pricing/owners before running.
- If accepted into main, mark only `SOURCE_RESEARCH_DOCUMENT_MERGED`, not `DATA_SOURCE_ADOPTED` or `ALPHA_IMPROVED`.
