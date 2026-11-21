# EDGE DETECTIVE CP01 | Solana discovery coverage vs qualified opportunity, source truth

Date: 2026-11-21 Europe/Copenhagen. **CHECKPOINT: READ-ONLY PRIMARY SOURCE AUDIT COMPLETED**, source-pinned sample counts; no edge claimed. Authoring branch is the existing Archive PR #2300. No separate product/research queue, no new process, no market or trading authority, no scheduler, no live writer change.

## 1. Why this checkpoint

Owner directed to make Solana a major investigative priority because Alpha Lab Pro sees significant meme-token activity. This checkpoint does **NOT** claim Solana is the largest global launch market. It tests what current first-party Alpha Lab captures actually count, and whether this sample reaches the same denominator used for meaningful economic comparisons.

Control plane: Archive main read `a3261a2252e749fea5d3365aa698608effefc3c8` (snapshot; recheck on release).
Alpha product original main (at read): `e924bdd9e5cd94d5c42b740704d5d8f85904430f`.
Alpha `AGENTS.md` blob `aaba37712a743a9fbee4c1930474650984416013`: research-only, no wallet signing/trading, original #228, #22, source #120/#70, qualified quote #98, identity #194/#126, outcome #77/#85, same Archive #1512 specialist queue. This audit creates no replacement Alpha owner.

## 2. Direct historical V4 scout CSV readback, fully quote-aware CSV parsing

File: `intelligence/ephemeral/v4/2026/{11/14,11/20,11/21}.csv` in `Donh91/Meme-Alpha-Lab`.

CSV has quoted, sometimes **multiline** project descriptions. A naïve physical-line/split-by-comma count produces 29-39 malformed pseudo-rows and false source counts. This checkpoint used a quote-aware CSV state machine handling commas, doubled quotes, CRLF and embedded newlines, validated each record against the ten-column header and found **0 malformed logical records**. All counts below are **observed rows**, not distinct tokens, eligible launches, independently funded buys or real-time source coverage.

| Day 2026 UTC | Git blob (Alpha main path) | Valid V4 logical rows | Solana observations | Solana share | Source split |
| --- | --- | ---: | ---: | ---: | --- |
| Nov 14 | `412a94822a03cfd11b3bb8a97f064bfc027e8b55` | 252 | 124 | 49.21% | 160 GeckoTerminal, 92 DexScreener |
| Nov 20 | `0dc68b8967720d5dadddc020be12396225324d47` | 263 | 128 | 48.67% | 160 GeckoTerminal, 103 DexScreener |
| Nov 21 | `04627f8c157ea5964fe7d477ce54797f333ad71b` | 265 | 130 | 49.06% | 160 GeckoTerminal, 105 DexScreener |

V4 item kinds observed include TREND, SOL_TREND, BOOST and PROFILE, so the rows sample **discovery/attention**, not a population census of Solana Pump.fun launches. A PROFILE/BOOST label never by itself proves paid promotion, verified buys, independent actor count, pool liquidity, settlement or a paper entry. More Solana records than other chains is not evidence of tradeable alpha.

## 3. Direct source population versus the V4 scout rows

Alpha `research/alpha_audit/population/LATEST.json`, blob `b075ad1f7e3609300a0362488447a36286647e4f` is a **hash-pinned pointer**, not an eligible launch census:
- `contract=ALPHA_OBSERVED_CANDIDATE_POPULATION_POINTER_V1`
- `population_status=OBSERVED_SAMPLE_ONLY`
- `global_eligible_denominator=null`, `paper_entry_authority=false`.
- Points to history `research/alpha_audit/population/history/e8d3bcf3913eaddf566b507e72a1cc22eb6a7517516b320fd02f54a9f6862c5b.json`, blob `6ac668d725a1d28c9f41739f5a1b1a7b507df872`, whose `observed_candidates` array contains **331 records**, all `robinhood-chain`; zero have `first_known_verified=true` and `global_launch_population=null`. The pointer/history SHA-256 relationship was not independently recomputed from raw bytes here; the provided pointer was resolved to content and counted, which is weaker than cryptographic attestation. Do not conflate the 331 RH observed sample with the V4 Solana trending row cohort.
- Alpha `research/alpha_audit/live_shadow/LATEST.json`, blob `5fcf59da7f21724d313ae2b316e875859c8ebf2e`, explicitly declares `scanner_early_alpha_ready=false`, `verified_new_buy_candidates=0`, `five_gate_pass_count=0`; source coverage currently `EARLY_CA_COVERAGE=DEGRADED_BACKLOG_OR_PARTIAL_TAIL`, `PROJECT_CA_ALERT_CLOSED_LOOP=NOT_VERIFIED_END_TO_END`, `WALLET_ENTITY_INDEPENDENCE=PARTIAL_BOUNDED_RESEARCH`. No evidence of a reliable fully qualified Solana purchase opportunity emerges from these receipts.
- Alpha `research/queue/LATEST.json`, blob `17e4c2600e08030e188b51f85ac17d821abedfd8`, has `active_heavy_workstreams=[]` but first three original actions remain D-COVER-01 two contiguous natural first-known windows, E-QUOTE-01 bounded native quote/CurveSell proof, and D-MISS-01 source-to-alert/quote joins. It is **not** permission for parallel work or proof of no work outside the queue.
- Alpha `research/alpha_audit/continuous_improvement/LATEST.json`, blob `d234d46c97dac1fd530443f7d3ad8f326390b248`, is audit proposals only, `approved_to_merge=false`; no autonomous release implied.

## 4. Already implemented capability, avoid a duplicate

Alpha `scripts/research/alpha_edge_economic_tournament_v1.py`, blob `cbaab04c0c73ef477e140d041fcb6f2e580aca36` supports `solana` Base58 exact token/pool syntax, independently provided BUY+SELL quote receipts, 24h/48h/72h and $100/$500/$1000/$5000 capacities, frozen B0-B3 matched arms and cost-aware return descriptors. **It explicitly states its receipt strings are unverified, and `verified_economic_edge=false` even on nonempty input.** Thus syntax support != a working Solana economic pipeline.

Alpha `research/alpha_audit/strategy_arena/README.md`, blob `3368b670960091bcbbc45291feca4b1d5f30764f` already owns eight variants across launch/dip/survivor/Phoenix. Its source contract permits only synthetic/unattested research absent independent chain proof. Alpha `research/sellability/README.md`, blob `3d8a04e866a05eea2b76ecbd51031194b928e338` already owns provider/internal paired mechanics; its current provider route is primarily **EVM** (GoPlus Robinhood, Honeypot on Ethereum/BSC/Base), not proof of Solana native Pump.fun buy/sell quote realism.

**Observed root problem:** broad Solana discovery exists, but no verified end-to-end **early Solana eligible denominator → exact mint+pool → first-known natural capture → same-size executable buy+sell → matured outcome → matched baseline** is established from the inspected current primary pointers. This is a *proof gap*, not proof that the code lacks every function.

## 5. Concrete owner-routed next acceptance, in existing order

1. #120/#70 + original Alpha #228: native full launch/candidate source coverage for **two naturally consecutive** HOT intervals, explicit gaps/unknowns and exact mint/pool, before any claims of scanner recall or unseen missed winners. A trending/boost row alone is not a birth.
2. #194/#126 exact token-to-pool and source-to-consumer identity with frozen first-known receipt, including Solana-specific migration phase (curve → PumpSwap), correct SOL quote/token decimals and entity evidence.
3. #98: $100/$500/$1k source-matched BUY+FULL-SELL quote feasibility, including required costs, latency and unexitable negative observations in original paired-denominator ledger. Native Solana curve mechanics must not silently inherit EVM provider flags.
4. #77/#85 original outcomes: due-only all-success/all-failure/all-unknown population with false-veto cost and no cherry-picked surviving chart winners. Existing `alpha_edge_economic_tournament_v1.py` / strategy arena may consume only *admitted* independently verified rows.
5. Archive #1512 original specialist `S1_EXECUTABLE_SELLABILITY_TRUTH_V1`, state `PAIRED_DENOMINATOR_MERGED_PROSPECTIVE_DATA_PENDING` per `04_RESEARCH_LAB/external_specialist_dissection/QUEUE_V1.json` on main at audit. Do not code the already merged denominator again. A source-admission note is incremental evidence, not a new queue/disposition.

**Final CP01 status:** `SOLANA_DISCOVERY_PRESENT`; `SOLANA_NATIVE_ECONOMIC_EDGE_UNKNOWN`; `CROSS_STUDY_POPULATIONS_NOT_JOINABLE`; `ORIGINAL_SOURCE_TO_EXECUTION_CHAIN_UNVERIFIED`. No model, trading, source contract, private data or public-site change. This checkpoint must only become canonical when PR #2300 passes independent review, native CI and original S1 routing.
