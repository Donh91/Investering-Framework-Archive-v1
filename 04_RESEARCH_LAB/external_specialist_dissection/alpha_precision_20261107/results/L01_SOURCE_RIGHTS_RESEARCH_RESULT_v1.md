# L01 | Public source rights and reproducible licensed code
**Mission:** ALPHA RESEARCH LAB PRECISION HARVEST (PR #2024)  
**Evidence class:** OFFICIAL_DOC_SOURCE_REVIEW / NOT A PREDICTIVE BACKTEST  
**State:** SOURCE_TRIAGE_PARTIALLY_COMPLETED, PIT/independent execution NOT verified  
**Owner:** existing Research Lab #1512, handoff only to original Alpha owners  
**Frozen control-plane SHA:** `cf9dc8d83a7494be6a196fd16dfcd71c1c810b60`  
**Frozen Alpha SHA:** `eb24295358b5f4884e1d0a5b7383c491e84c830f`  
**Cost:** $0 incremental API/provider; no provider API calls, no new GitHub Actions jobs  
**Review date:** 2026-11-08 Copenhagen (official documentation; no live request-rate benchmark)

## Narrow testable proposition
New public/licensed source access might yield incremental, *as-of-available* code or data quality beyond native S1-S10. Source existence, code verification and third-party safety classifications alone are not incremental predictive edge.

## Verified source and method inventory (as published in official docs)
| Source | Official first-party evidence | Lawful no-new-subscription scope | Decision, pending independent test |
| --- | --- | --- | --- |
| Sourcify API v2 | https://docs.sourcify.dev/docs/api/index.html ; v1 API **off since 2026-07-07**, v2 contract lookup and verification; API forbids single-contract crawling for bulk, use documented public datasets for bulk | Targeted **read-only** verified source/code comparison at exact chain+CA and revision; not proof of security or owner privileges. Reuse MIT implementation only after file-level licence check | **RETAIN_METHOD** for contract verification/provenance; **KILL** any legacy v1 endpoint assumption |
| DEX Screener | https://docs.dexscreener.com/api/reference ; latest profiles and boosts 60 req/min, most pair endpoints documented 300 req/min | Public pair-level metadata at actual fetch time, chain+pair bound; boosts reflect paid attention and cannot prove organic buyer conversion | **RETAIN_NATIVE_BASELINE**, no second collector without incremental-clock proof |
| GeckoTerminal public API | https://support.coingecko.com/articles/6867086195-does-geckoterminal-have-an-api ; Beta public API and 30 req/min free limit (support page updated 2026-10-02) | Public pool checks where explicit terms permit; exact pair, liquidity and stale-clock controls | **MODIFY_IF_SOURCE_GAP_PROVEN**; do not duplicate existing collection |
| GoPlus | https://docs.gopluslabs.io/reference/support documents free access and 30 calls/min; https://www.gopluslabs.io/en/security-api markets a free tier with CU-based limits (150 CU/min) | Public token-security source claims, no guarantee of route-depth or executable size; **different 'calls/min' and 'CU/min' units must not be conflated** | **RETAIN_AS_CHALLENGER** alongside native S1, never treat `provider_can_sell` as actually executable trade |
| Honeypot.is | https://docs.honeypot.is/ and https://docs.honeypot.is/ishoneypot ; docs say no auth currently, `simulationResult` and max sell **not guaranteed** | Targeted supported-chain simulations if allowed; missing simulation must remain UNKNOWN, not a SAFE label | **RETAIN_AS_CHALLENGER** with negative-control tests for absent/no-route/revert/size limits |
| Uniswap v4 | https://developers.uniswap.org/docs/protocols/v4/concepts/poolmanager and https://developers.uniswap.org/docs/protocols/v4/concepts/hooks ; singleton PoolManager, per-pool key, dynamic optional hooks, swap callbacks | Read protocol semantics and independently inspect swap/quote side; generic pool TVL cannot prove real token-to-quote route capacity | **RETAIN_SOURCE_SEMANTICS**; shadow replay against S1 size-aware exit |
| Monsta / PIRBView | Source-limited vendor docs documented in existing `2026-11-07__TG_SCANNER_METHOD_TRANSFER_MATRIX_v1.json` | Public descriptions/method hypotheses only; first-party bot source, lawfully automatable API, actual historical first-observed receipts NOT VERIFIED | **NO_API / METHOD_ONLY** until authenticated rights, timing, independent matched controls |
| SAFE Analyzer | https://www.dexanalyzer.io/api ; original source matrix records quoted $999/mo API entry, not authorized under this mission | Official docs only, no premium API purchase or scraped Telegram data | **KILL_PAID_DEPENDENCY**; keep claim as an externally challenged hypothesis |
| Birdeye / Relay / Sparsity | Existing `BIRDEYE_RELAY_PUBLIC_METHOD_REGISTRY_20261107.json` and prior approved source audits | Source-documentation concepts only unless API and usage rights independently verified; never copy provider database | **MODIFY_RESEARCH_ONLY**, no source contract admission |

**Licence separation:** Repository names or an MIT licence on a different codebase are not consent to redistribute proprietary Monsta/PIRB/SAFE bot output. The source-matrix's NetworkX BSD-3, Sourcify MIT, Slither AGPL-3, Blockscout custom and Uniswap v4 file-level/licence notes remain research references and must be checked at exact upstream code SHA before code copying. This report includes no copied external code.

## Targeted comparison to native Alpha on fresh main
- Existing `scripts/sellability_provider_challenger_v1.py` explicitly normalizes GoPlus and Honeypot API claims into **provider** observations with tri-state UNKNOWN.
- Existing `scripts/sellability_cohort_v1.py` keeps a separate internal-mechanics and pair ledger with source hashes, chronological records, chain+CA and sell-notional.
- Therefore **do not introduce another vendor safety scanner, scorer or parallel owner**. First compare same-clock provider claim vs native internal route evidence across eligible cases, including false SAFE and false UNSAFE.
- The L01 hypothesis of new *incremental* source/data advantage has **NOT** been demonstrated. Public documentation confirms technical feasibility only.

## Adversarial exclusions and precise next tests
1. If a supposed V4 pool's TVL or price changes while quote-side exit capacity remains missing, emit `UNKNOWN/NO_ROUTE`, never an inferred sellable size. Preserve pair/pool/hook and decimals.
2. If Honeypot API omits `simulationResult`, `maxSell` or fails a chain, classify the individual claim `UNKNOWN`. Do not transform lack of coverage into UNSAFE/SAFE.
3. For GoPlus, independently calibrate API calls versus *compute units*. Do not set schedule based on a mistaken 150-request assumption.
4. Audit native source selectors for Sourcify v1. No actual v1 caller was found in the targeted default-branch code search; therefore no broken production integration is claimed.
5. An actual new provider joins only if it yields authenticated, timestamp-valid information which changes an original owner decision beyond matching native S1-S10, AND survives an eligible winner/loser control.

## RETAIN / MODIFY / KILL decision, correctly limited
- **RETAIN:** documented Sourcify v2/source truth; existing DEX Screener and S1 GoPlus/Honeypot *challenger* methods.
- **MODIFY (test, no new engine):** rate-unit-aware source contracts; missing-simulation negative tests; chain/pool route and quote-side eligibility; first-machine-seen chronology.
- **KILL at current approved budget:** paid SAFE/unknown bot APIs, bulk Sourcify crawls, unlicensed vendor source copying, equating static SAFE to sized execution.
- **Research status:** `L01 RUNNING`, `SOURCE_BACKED_NOT_OUTCOME`. **NOT COMPLETE_VERIFIED** until exact fetch receipts, licence/rights at code SHAs, and original-owner signed scientific adjudication. No claim of detected winners, rugs, numerical lift or forward outcomes.

## Owner handoff and activation
Research Lab #1512 (source/licence gate) -> Strategist #1157 (distinct value, scientific gate) -> existing S1 Alpha #98/#194 and S7/S3/S2 owners only if new data/defect proven -> original PR targeted tests -> main readback. **Trigger:** a same-cutoff provider/native disagreement record bound to exact chain+CA+pool, $100/$500/$1000 sized execution evidence and unambiguous legal source scope. If none, register DUPLICATE_NO_ACTION rather than new code.

**No jobs claimed:** no GH Actions research job IDs/artifacts exist from this chat yet; static CI on PR #2024 is not research execution.
