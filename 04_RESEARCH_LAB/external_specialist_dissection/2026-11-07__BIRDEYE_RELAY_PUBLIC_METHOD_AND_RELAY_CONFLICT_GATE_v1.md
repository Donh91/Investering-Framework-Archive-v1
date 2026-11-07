# Birdeye + Relay: official-site-only method transfer and adversarial infra gate
Date: 2026-11-07 (Europe/Copenhagen)  
State: RESEARCH_ONLY / PUBLIC_METHOD / SHADOW_REGRESSION  
Authority: existing Research Lab #1512, Strategist #1157, original S2/S3/S1/S4/S6 owners; no trading, API provider-data collection or model promotion.

## Research execution and evidence classes
- Research Parallel Lanes v1 **Mode A**: three bounded independent read-only inquiries in one assistant conversation: (A) Birdeye first-party capabilities/rights, (B) Relay first-party settlement/error semantics, (C) existing Archive/Meme Alpha owners/code/adversarial BYTE evidence. NO concurrent independent AI agents or parallel Actions research jobs were invoked.
- Direct official website/documentation read evidence, not provider API responses, measured latency, live price/wallet records, subscriptions, rights grants or empirically verified alpha. Claim class for all suggested indicators = HYPOTHESIS / NO SCORED OUTCOME. Public source links are below; treat published API descriptions as capabilities **claimed/documented**, not proven 0-cost availability.
- All source/method fields here are independently authored summaries, **not copied vendor datasets or vendor code**. No raw/normalized private or restricted provider values in public code/issue/PR.

## Official sources (source identity only)
1. Birdeye https://birdeye.so/ , visible terminal: token phases, liquidity, holder concentration, wallet/PnL/volume surfaces.
2. Birdeye First Buyers official explainer https://birdeye.so/data-api/blog/detail/new-api-token-first-buyers-identify-the-earliest-buyers-of-any-solana-token , published 2026: Solana `GET /token/v1/first-buyers`; up to 1000 first buyers, current position status and tags.
3. Birdeye historical wallet reference https://docs.birdeye.so/reference/get-wallet-v2-net-worth-details : hour/day time-point holdings with historical price; hourly history only past seven days and Solana-only; endpoint availability shown in docs is not live response proof.
4. Birdeye pricing https://docs.birdeye.so/docs/pricing : Standard $0/30k CU/month/limited access/1 rps; Lite advertised $39/month/most APIs. Free CU is **not evidence that First Buyers is in Standard**; earlier internal Oct 30 provider audit says First Buyers requires Lite+, re-verify before any integration.
5. Birdeye terms https://birdeye.so/data-api/terms-of-service : automated scraping/recording/storage/reverse engineering and non-intended provider-data reuse restricted absent written permission. Do NOT scrape UI, call hidden endpoints, import scores/tags, persist provider outputs, or assume generic free API access grants derivative model rights.
6. Relay interface https://relay.link/ ; public transaction lookup https://relay.link/transactions and official help https://support.relay.link/en/articles/9260724-how-do-i-find-my-transaction : transaction page exposes both legs, hashes, status, fees; lookup does NOT establish comprehensive historical licensed export.
7. Relay own crosschain integration https://relay.link/blog/how-to-integrate-relay-api : quote -> steps -> origin submission -> requestId -> destination fill; documented states waiting/pending/success, not a source-PIT data guarantee.
8. Relay official quote errors https://docs.relay.link/references/api/api_core_concepts/handling-errors : INSUFFICIENT_LIQUIDITY, NO_SWAP_ROUTES_FOUND, SWAP_IMPACT_TOO_HIGH, destination failure and unsupported chain/currency are distinct mechanisms.
9. Relay vault/source liquidity https://docs.relay.link/references/protocol/vaults/overview and https://docs.relay.link/references/protocol/vaults/backend : solver liquidity/vaults are infrastructure, not token-specific retail demand.

## Deduplicated primitive ledger
| ID | Primitive | Original owner | Incremental value and falsifier | Current status |
|---|---|---|---|---|
| B1 | Lifecycle snapshots (bonding -> migration -> exit) with first-known cutoff | S4 launch/retention | Hold out first-eligible cohort; compare prior phase-only and price/liquidity baselines. Kill if no incremental prospective net sellability. | DEDUP_EXISTING_OWNER; no new scanner |
| B2 | Earliest buyers with native, pre-frozen cohorts; avoid current wallet tags and survivorship | S2 wallet quality / S4 first buyer | Independently identify first-N buyers using native chain launch/curve events, include sells and missing-history; compare qualified vs age/price-only, realized after-cost controls. | HIGH_VALUE_EXISTING_S2; existing Pons first-10 first forward case remains priority |
| B3 | Wallet repeatability and historical PnL without current-status lookahead | S2/CLEAN_G3 | Complete history, losing trades, one-hit concentration, sellable route. Kill if after-cost edge disappears vs simple controls. | EXISTING; no Birdeye PnL ingestion |
| B4 | Volume normalized by executable pool liquidity and independent buyers | S1/S4 | Compare price-only, raw volume, volume/liquidity, after-cost exit; freeze depth at t. | EXISTING/SOURCE_GAP; no new hot path |
| B5 | Size-conditioned whale trades rather than nominal $ thresholds | S6 distribution / S1 | Normalize against pool-depth, avoid LP/CEX/internal transfers, compare false positives. | METHOD_ONLY |
| B6 | Historical token net-worth snapshots as QA method, not PnL source of truth | S2 / Task2 clock | Hour/day cutoff and publication vs event time. Kill if provider's historical label is retrospective. | DOCUMENTED / PAID_ACCESS_UNVERIFIED |
| R1 | Relay/bridge solver infrastructure must NOT imply shared economic control | S3 cluster and operator enrichment | If infrastructure and non-benign claims conflict, never promote a positive operator alarm. A deterministic contradiction regression is feasible now. | EXECUTABLE_LOW_RISK_GATE; PR implements conflict fix |
| R2 | Link origin deposit to fill by request ID, origin/destination hash, token/chain/time | S3/S6 | Treat routed funds as movement until verified subsequent independent swap/buy; do not count twice. | REQUIRES_ORIGINAL_SOURCE_QUALIFICATION |
| R3 | Solver liquidity/vault capacity as route context, not bullish alpha | S1 sellability | Compare published quote and actual route with matched contemporaneous executable alternatives; never infer honeypot from one provider no-route. | P2 SOURCE_ONLY |
| R4 | Route failure ontology: no route vs low funds vs slippage vs destination revert | S1 sellability | Negative/no-route only provider-specific unless independently reproduced with viable route and control. | METHOD_ONLY_EXISTING_S1 |
| R5 | Cross-chain rotation context with dual-clock confirmation | S6/Altseason | First-known bridge deposit != token demand; count only confirmed destination fills and independently attributable purchases. | P2/NO_ACTION unless source improvement appears |
| R6 | Provider labels versus internal chain truth, provenance and unknown states | X0/S3 | No positive identity from shared bridges, exchange hubs, solvers; require independent behavior and exact evidence clocks. | EXISTING; regression now expands |

## Observed overlap and negative cases
- Existing Archive BYTE research: `06_RESEARCH_LAB/alpha_lab/2026-09-28__byte-holder-graph-coordinated-cohort-followup-v1.md` documents several Relay-like shared-funder paths and a possible fake cabal conclusion. Its later post-exit note explicitly rejects treating generic Relay cash-out as next-project operator lineage.
- Existing `scripts/research/memes_alpha/adversarial_operator_enrichment.py` already labels Relay/bridge/router/settlement, while `adversarial_operator_counting.py` already has the core benign infrastructure veto and a regression for a non-conflicting Relay class. No new classification engine needed.
- NEW small code audit: `infra_state()` historically gives `benign_infra_excluded=True` precedence over conflicting `common_funder_class=RELAY`, or `False` over `NON_BENIGN`, and prioritizes `lineage_class` above an opposing funder class. Contradictions could allow positive Stage1/Stage2 qualification without resolving the conflict. Mitigation: all acknowledged evidence must agree or classify infra as UNKNOWN. Negative-control unit tests exercise both directions and inter-class contradiction. Synthetic tests prove this deterministic safety property only, not reconstructed BYTE activity or predictive edge.
- Earlier Grok advisory (2026-10-30) and original S2 Birdeye source expansion (2026-09-29) had already flagged provider access, PIT and rights issues. Do not count this intake as a novel Birdeye integration or a new autonomous agent.

## Research Parallel Lanes v1 decision matrix
- A, Birdeye: OFFICIAL_DOCS_REVIEWED; legal boundary confirmed; no provider/first-buyer sample; next = S2 already-owned prospective native Pons first-10 case, with first-known, COMPLETE_WINDOW and loser denominator.
- B, Relay: OFFICIAL_MECHANICS_REVIEWED; no provider calls; next = deterministic contradictory-infrastructure unit regression under existing S3/operator code, then standard existing CI.
- C, Internal: EXISTING_CODE_AND_BYTE_CASE_REVIEWED; fix contradictions, not new engine; next = verify exact-head tests and native PR receipts, then Strategist adjudication of incremental benefit.
- Future empirical study, not run: freeze native origin and destination chains+clock+hashes for independently permitted sources; control for bridges/routers/CEX; compare operator false positives BEFORE and AFTER infrastructure exclusion using *genuine new cases*, not synthetic-only tests. Kill if no material incremental false-positive reduction or independent behavioral evidence is lost.

## Stop rules and permissions
- $0 external API spend, $0 subscriptions, no API key, no automated page scraping, no extra workflow/automation/agent/reviewer account, no live token scoring/weights, no trading and no model promotion.
- Do not change `QUEUE_V1.json.current_next_action`; Pons first-forward case retains priority. Do not break Round 3: PROSPECTIVE_COLLECTION_ONLY, scoring OFF. Any outcome tests require independently approved scientific gates, true first-known, negative denominators, matured outcomes and matched after-cost baselines.
- Reviewer/Strategist disposition: accept this code as deterministic safety hardening only, or reject if contradictory evidence is shown to have legitimate ordered source authority; never claim that green CI proves investing alpha.
