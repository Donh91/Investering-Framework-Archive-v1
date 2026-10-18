# DexPaprika Source-QA + Archify Visual Benchmark — Adversarial Acceptance Matrix

**Date:** 2026-10-18. **Status:** RESEARCH_DESIGN_FROZEN / NOT_EXECUTED_AS_PROSPECTIVE_EXPERIMENT.  
**Existing owners:** Archive #1017, #1087, #1340; Meme Alpha #126.  
**Only performed:** 3-chain anonymous coverage/smoke checks and selective pool-level cross-aggregator reads documented in `DEEP_RESEARCH.md`.  
**Do not claim:** this matrix is a passed production regression suite. No collector, runner, historical backfill, source contract patch, market admission or API spend created.

## A. Bound experiment

**Question:** When a real already-eligible Alpha Lab observation has unavailable, stale or contradictory DEX metadata, does a bounded DexPaprika read-only query add materially useful and truthful information beyond the currently approved providers?

**Comparison:** frozen identical chain+CA+pool universe, existing approved owner data versus existing + supplemental DexPaprika on the same as-of interval. Each case must preserve `source_available_at`, `captured_at`, chain/source/version and any latency bound; do not compare future-refreshed challenger data to old baseline.

**Diagnostic sample target:** 30 fixed cases, 10 each ETH, Solana, Robinhood, stratified by active, freshly created, thin/withdrawn and unknown-identity case types. Record why each case entered the universe before seeing provider outcomes. This fixed panel is a **source-QA diagnostic**, not an adequately powered alpha/strategy backtest.

**Evaluation fields (new data, not new authority):**
- `chain_id`, exact `token_contract_or_mint`, exact `pool_id`, `dex_program`, base/quote IDs, `source_id`, `source_version`;
- `upstream_event_at` (only if onchain-proven), `source_observed_at`, `source_available_at`, `capture_at`, `source_latency_bound`;
- `field_present`, `field_is_null`, `field_value_zero`, `field_unavailable` as four different states;
- `data_freshness`, `liquidity_status`, `is_price_quote_unambiguous`, `is_pool_origin_authoritative`, `cross_provider_disagreement`;
- provider HTTP/rate-status reason and actual credit charge; no silent success if plan limits block a field;
- `baseline_decision` and `challenger_addition`, both bounded to SOURCE_QA. Never output buy/sell or numeric alpha score.

**Primary readout:** count genuinely corrected/filled field-level observations, count false new conclusions, exact chain/pool identity violations, additional p50/p95 read latency where timed, ratio of missing fields handled correctly, provider availability, cost/credit per genuinely corrected observation. Rate all rows, including null and failed reads; zero incremental value is a valid outcome.

**Do not confuse:** network listed != complete token coverage; liquidity field != executable depth; duplicate volume figure != independent replication; catalog addition timestamp != first tradable block; candles != transaction reconstruction; provider ranking != a predictive strategy.

## B. Synthetic/adversarial test specifications (NOT yet run as executable test suite)

| ID | Frozen test case | Expected behavior | Critical wrong behavior (MUST fail) |
| --- | --- | --- | --- |
| QA-01 | Supported chain but exact token absent | `TOKEN_UNKNOWN` not zero or rug | Mark as negative alpha / dead token |
| QA-02 | Exact token on old chain and a new pool appears | Preserve token origin, new pool only | Reset token age to pool age |
| QA-03 | Pool has substantial trailing volume and zero/nearly zero current liquidity | `CURRENT_LIQUIDITY_NOT_PROVEN`, no executable-capital inference | Volume-only BUY / sellability PASS |
| QA-04 | DexPaprika liquidity is zero, second provider **omits** field | `CROSS_PROVIDER_LIQUIDITY_UNRESOLVED` | Treat missing field as independent zero confirmation |
| QA-05 | Aggregators disagree on pool creation date | `POOL_BIRTH_CONFLICT`, seek block/protocol provenance | Take earliest/latest date and call it token birth |
| QA-06 | Wrapped token has recent `added_at` and extreme aggregate ATH | `INDEX_ADDITION_ONLY` and `ATH_NOT_PROVEN` | Treat index addition as launch / aggregate ATH as attainable performance |
| QA-07 | Free key attempts transaction endpoint / token OHLCV and gets 403 | `PLAN_REQUIRED` / UNKNOWN; no retry escalation | Infer zero transactions, claim historical coverage, silently purchase |
| QA-08 | API responds 402 exhausted allowance vs 429 minute rate | `BUDGET_EXHAUSTED` vs `RETRY_AFTER` with bounded backoff | Infinite retry, switch to paid host, malformed price-as-zero |
| QA-09 | Two pools same token and symbol alias duplicate | Exact chain+CA identity with pool-specific price/liquidity; `POOL != TOKEN` | Double count candidates / mix quote or FDV and MC |
| QA-10 | Token quote is reversed across providers | Normalize base/quote with decimals and source | Compare inverted prices as if equal / false signal |
| QA-11 | Same pair has highly concentrated liquidity out of current price range | `CAPACITY_UNKNOWN` until execution pool and quote simulations | Infer sellability from nominal TVL alone |
| QA-12 | Source fresh now but outcome belongs to older frozen forecast | Historical as-of availability violation blocked | Backfill retroactive evidence / look-ahead |
| QA-13 | Provider returns `200` despite unreadable API key | Verify actual `keyless` status and limits | Assume premium plan and complete endpoint availability |
| QA-14 | Two aggregators mirror shared stale data | Distinct URLs never count as independent block/event roots | Double-vote confirmation |
| QA-15 | Robinhood Uniswap V4 pool ID differs from standard EVM contract-shaped addresses | Preserve exact pool identity and protocol semantics | Demand ERC20-style address for V4 pool / wrong pool join |
| QA-16 | Solana pool mint and pool base58 collide via symbol search | Exact address ID required | Symbol-only CA identity promotion |
| QA-17 | Unbounded streaming price-update burst | Bound credits and terminate or reject budget-expensive path | Assume one stream=one credit / runaway free allocation |
| QA-18 | Vendor unavailable during an alpha decision | Existing approved fallback still works; status UNKNOWN | Convert missing source into bearish or suppress entire owner |
| QA-19 | Missing or ambiguous market cap but FDV present | `MARKET_CAP_UNKNOWN`, preserve FDV separately | Silently fill MC from FDV |
| QA-20 | Data source stale relative to other source and event clock | Quarantine old measurement, retain source-health failure | Fresh-looking non-null value overrides newer proven source |
| QA-21 | Already selected winners only in retro sample | Reject as survivorship/selection biased | Score a winner-only backtest or claim higher recall |
| QA-22 | Pool receives current reserves but sell transfer restricted/honeypot | Liquidity observation only, sellability UNKNOWN without onchain test | Liquidity > threshold = sellability verified |
| QA-23 | New provider is present in Alpha research but private normalized payload is to be written to public archive | Public retains only health metadata and immutable private binding | Dump market records to public issue/log/PR |
| QA-24 | External MCP tool text instructs overriding source policies | Treat data/tool text as untrusted and ignore instruction | Let prompt injection grant trading or secret access |
| QA-25 | Provider value conflicts with original chain event block | Chain event remains identity/origin authority | Promote aggregator's first-seen time above event truth |
| QA-26 | Same pool read at staggered timestamps across providers | Report as asynchronous, no calibrated latency/performance inference | Treat differences as source errors or measured latency |
| QA-27 | Archify diagram invents a path from control plane to private value store | Reject generated graph / flag unverifiable edge | Publish as verified architecture |
| QA-28 | Archify output includes a private credential string / restricted source value | Reject/quarantine output, no public artifact | Publish screenshot/HTML with private content |
| QA-29 | Archify remote installer wants `-g` or dynamic latest | Deny in this research lane; pin and separately review | Run unreviewed global executable or auto-updater |
| QA-30 | User iPhone renders an interactive graph but cannot read or navigate | Visual benchmark fails; retain existing text route | Replace proven site UI because diagram looks impressive |

## C. Admission and kill protocol

**Hard fail -> REJECT_CANDIDATE** for identity wrong-join, case-denominator corruption, hindsight data, missing-as-zero, unauthorized API spend, private-data egress, live-order capability, claim of independent block evidence from aggregators, unknown-to-affirmative sellability promotion, or bypass of existing #1017 prerequisite.

**PASS_SOURCE_QA_CHALLENGER (research only)** requires:
1. the owner precondition is explicitly satisfied and verified at a commit;
2. all hard negative fixtures pass under the existing owner's exact schema and authority rules;
3. at least one independently reproducible incremental case adds decision-relevant *source-health information* beyond already available owner feeds, **without** material false-positive increase;
4. a point-in-time, costed, source-bound and deduplicated sample exists in the correct evidence plane;
5. current maintainer/independent review accepts the minimal additive change;
6. no new scheduler/agent/ledger or budget is created.

Otherwise return `KILL_NO_INCREMENTAL_VALUE` or `BLOCKED_SOURCE_PRECONDITION`. No score changes, alerts, trading or strategy promotion from research approval.

## D. Mandatory next work package, existing owner only

- Read current source field-map status and exact owner code, not this document in isolation.
- Run 30-case fixed diagnostic as a **source-quality comparison** after preserving observation universe and clocks, not as an alpha-strategy effectiveness experiment.
- Include a sentinel negative pool with extinct current liquidity, and an active liquid positive control. Avoid selecting only conveniently matched cases.
- Produce one hash-bound, restricted-plane immutable source capture or provider-value-free reason why it was impossible. Public report carries only source receipt binding and QA class.
- If incremental field truth survives, propose **a read-only source adapter into the existing owner** with narrowed privileges and original negative tests. If not, close research without integration.
- After a separately accepted Archify security/visual assessment, create at most a static public-safe diagram in the appropriate current site owner, never change production as a side effect of this study.

**Reporting:** `SOURCE_QA_SMOKE_COMPLETED` is the ONLY result from the current session, not `30_CASES_TESTED`, `SOFTWARE_TESTED`, `SOURCE_ADMITTED`, `ALPHA_UPLIFT`, `TASK2_ADMISSION` or `PRODUCTION_ACTIVE`.
