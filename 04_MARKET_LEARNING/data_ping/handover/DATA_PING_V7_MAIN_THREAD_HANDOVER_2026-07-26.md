# DATA PING V7 — MAIN THREAD HANDOVER

**Handover date:** 2026-07-26  
**Purpose:** Safe continuation in a new main thread without framework reset  
**Status:** `ACTIVE_HANDOVER / NON_CANONICAL_ARCHIVE_OBJECT`  
**Repository baseline at handover:** main includes W30 evidence recovery and final receipt through merge `2d4d1df8c4540b427539ae8959f2c07c729439a2`

## 1. Continuity rule

The next main thread must continue the existing investment framework. It must not treat DATA PING V7, FMOS or the new thread as a new framework.

The new thread must preserve:

- accepted framework state;
- forecast and maturity ledgers;
- source-QA and method lineage;
- shadow evidence and conflict registries;
- canonical/non-canonical boundaries;
- GitHub archive and write governance;
- all outstanding maturity events and confounders.

Chat history is not authority. GitHub and explicitly frozen framework artifacts are the replay source.

## 2. Current framework state at handover

```yaml
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
stage1: GOVERNANCE_PENDING
recovery_upgrade: NONE
altseason_confirmation: NONE
```

No new thread may infer a state change merely because context is missing.

## 3. Active DATA PING runtime

Latest improved collector supplied in the source thread:

```yaml
contract: DATA_PING_RUN_FIRST_STATELESS_v1
version: 15.0
runtime: DATA_PING_LONGITUDINAL_COLLECTOR_v1
trigger: Data ping
semantic_packet_status: PASS
root_key_count: 15
collector_role: COLLECTOR_AND_DETERMINISTIC_FEATURE_EXTRACTOR
framework_interpretation: DEFERRED_TO_MAIN_FRAMEWORK
```

Mandatory first-class assets:

- BTCUSDT
- ETHUSDT
- ETHBTC

Version 15 improvements that must survive into V7:

- live versus settled temporal status;
- method versions;
- ETH and ETH/BTC as first-class assets;
- spot taker windows;
- BTC and ETH funding, OI, basis and positioning ratios;
- Binance/OKX cross-venue tagging;
- volatility and 48H structure;
- ETF extraction state model;
- stablecoin fallback hierarchy;
- deterministic derived features;
- readiness and missing-field blocks;
- explicit predecessor/comparison block;
- no threshold pass/fail or portfolio authority in the collector.

Known V15 limitations at handover:

- breadth can fail if CoinGecko page 1 returns empty;
- BTC/ETH per-asset CFGI endpoints can fail;
- DeFiLlama payloads can exceed connector limits;
- predecessor comparison is unavailable in a fresh thread unless the previous accepted snapshot is supplied by the main framework;
- chat transport remains unverified;
- binary artifact output is not required for the normal inline packet.

## 4. Latest DATA PING V15 snapshot reference

```yaml
run_id: dprun_20260726T095746Z_001
snapshot_id: dpsnap_20260726T101847086Z_001
run_started_at_utc: 2026-07-26T09:57:46Z
snapshot_utc: 2026-07-26T10:18:47.086Z
freeze_basis: MAX_BINANCE_FINAL_SOURCE_TIMESTAMP
current_collection_complete: true
mandatory_assets_ready: true
deterministic_features_ready: true
packet_ready_for_main_framework: true
breadth_ready: false
predecessor_comparison_ready: false
```

Key snapshot facts, preserved only as predecessor context and not as live truth:

```yaml
BTCUSDT_last: 64497.62
ETHUSDT_last: 1884.12
ETHBTC_last: 0.02921
BTC_D_pct: 56.48347660570602
ETH_D_pct: 9.922404350528312
BTC_ETF_2026-07-24_usd_m: -240.1
ETH_ETF_2026-07-24_usd_m: -70.7
global_CFGI: 26 Fear
stablecoin_market_cap_usd_fallback: 310477000000
```

Important derived features from that snapshot:

```yaml
BTC_24h: PRICE_UP_OI_DOWN
ETH_24h: PRICE_UP_OI_UP
ETHBTC_24h_return_pct: 0.5511539786427821
ETH_relative_strength_24h_pp: 0.5293991717577606
ETHBTC_distance_to_0_0300_pct: -2.6333333333333333
ETHBTC_distance_to_0_0275_pct: 6.218181818181818
BTC_OI_24h_pct: -0.754312
ETH_OI_24h_pct: 1.714041
```

These values are stale immediately after handover and must never be presented as current without a new source run.

## 5. W30 external evidence package

Claude recovery package is archived as `MASTER_MONDAY_EXTERNAL_EVIDENCE_W30`.

Package identity:

```yaml
zip_name: CN W30 MASTER MONDAY EVIDENCE RECOVERY 2026-07-26.zip
zip_bytes: 1676211
zip_members: 109
zip_sha256: 9353f2fcefb9aaf38d8102dd3a4ec538fba302352178e883e1bcf0cdc6472ad8
pdf_name: W30 MASTER MONDAY EVIDENCE RECOVERY.pdf
pdf_sha256: 23b0f7f9b8aa7dc0612b2f757744f934f1246dd16ea81670e0f54c06ed5cdae3
classification: RESEARCH_EVIDENCE_ONLY / NON_CANONICAL / NON_BINDING
```

Primary archive paths:

- `04_MARKET_LEARNING/master_monday/W30_2026/2026-07-26_claude_evidence_recovery/`
- `08_SOURCE_MATERIAL/master_monday/W30_2026/2026-07-26_claude_evidence_recovery/`
- `07_PROMPTS_AND_AGENTS/skill_runs/2026-07-26__w30-master-monday-evidence-recovery__receipt.md`

The package supplements DATA PING while V15/V7 is developing. It does not replace DATA PING or own framework adjudication.

## 6. Active forecast and maturity state

### F1

```yaml
threshold_authority: 62200 frozen truth-layer
62342_status: unresolved provenance refinement
window: 2026-07-21 through 2026-07-27 UTC
maturity: 2026-07-28T00:00:00Z
status_at_recovery_package: 5/7 settled
score: WITHHELD_UNTIL_MATURITY
```

Required rows after package anchor:

- 2026-07-26 settled UTC close;
- 2026-07-27 settled UTC close.

No interim F1 score.

### F4

```yaml
status: MATURED
threshold: ETHBTC settled close >= 0.0300
window: 2026-07-15 through 2026-07-24
UTC_result: 0/10
CEST_result: 0/10
directional_score: GATE_UNMET
causal_attribution: CONFOUNDED
reopen_allowed: false
```

Independent Claude recompute matched archived values with parity `0.000` across four fields.

### F5

```yaml
status: CLOSED_TRIGGERED
approx_event_date: 2026-07-23
retrigger_allowed: false
frozen_text_local_availability: unavailable in Claude package
adjudication_owner: main framework
```

### H7

```yaml
basis: CEST settled closes
rows_at_recovery_package: 4/5
row5_maturity: 2026-07-26T22:00:00Z
final_score: PENDING
slope_condition_text: requires main-framework frozen source
```

### Low-vol E12 forward observation

```yaml
5d_maturity: 2026-07-28T00:00:00Z
interpretive_weight: NONE_FRAGILE pending recompute
status: INTERNAL_ARITHMETIC_CONFLICT
```

Do not score until the conflict is recomputed from frozen anchor and settled rows.

### Leading claim / July 14 case 2

```yaml
maturity: approximately 2026-07-30
FOMC: preregistered confound
P2_antecedent: not met in external package
kill_test: 2 of 3 cases fail 12-session durability
status: PENDING
```

### EXT-GCBLO-2026-07-24

```yaml
status: PENDING
maturity: 2026-10-23
```

## 7. Open conflict registry

The next thread must load and preserve the conflict registry. No silent repair.

Open conflicts:

1. F1 threshold lineage: `62,200` frozen versus `62,342` unresolved refinement.
2. Fed-chair source conflict in Claude package.
3. BTC dominance total-market versus ex-stablecoin basis.
4. UTC versus CEST close basis.
5. OKX versus Binance derivatives continuity.
6. Bitstamp ETH/BTC last trade versus midpoint.
7. Expected macro publication lag versus stale-source classification.
8. Provisional versus settled Farside values.
9. Low-vol arithmetic: incompatible result sets.
10. Stage-1 persistence count: three versus four closes below 65,600 in Claude material.
11. Stablecoin depeg summary versus detailed scan.
12. BTC ETF leader/concentration malformed fields.

Authoritative registry path:

`04_MARKET_LEARNING/master_monday/W30_2026/2026-07-26_claude_evidence_recovery/04_CONFLICT_REGISTRY.md`

## 8. Master Monday immediate requirements

Before adjudication, obtain and settle as applicable:

- H7 row 5 on the preregistered CEST basis;
- F1 rows 6 and 7 on the preregistered UTC basis;
- low-vol 5D recomputation;
- latest DATA PING V7 full collector packet;
- Farside latest settled session, with weekends/non-sessions never zero-filled;
- refreshed FRED DGS2, DGS10, VIX and HY OAS when published;
- ETH/BTC settled persistence and distance to 0.0300;
- FOMC confound log when the event occurs;
- source-QA classification for all failures and fallbacks.

## 9. Safe new-thread behavior

The new main thread must:

1. Read this handover and the linked W30 archive before making a framework statement.
2. State the inherited framework state explicitly.
3. Treat old market values as predecessor evidence, not current data.
4. Run a fresh DATA PING before current market interpretation.
5. Attach the previous accepted snapshot ID when available.
6. Keep RAW rows and deterministic features separate from framework interpretation.
7. Preserve all venue, method, temporal and session tags.
8. Never manufacture missing predecessor history.
9. Never reset forecast ledgers because the thread is new.
10. Never unlock rebuy, entry or rotation from collector output alone.

## 10. FMOS boundary

FMOS work continues in a separate new thread.

FMOS remains additive:

- ChatGPT: active reasoning and working memory;
- GitHub: long-term machine memory and replay archive;
- Claude: external research and adversarial audit;
- Codex: Knowledge Gardener.

FMOS must not rewrite the investment framework or redefine DATA PING. DATA PING V7 can emit Knowledge Objects for FMOS, but canonical market-state authority remains governed by the existing framework.

## 11. Handover acceptance test

A new main thread is safe to continue when it can return all of the following without guessing:

```yaml
inherited_rotation: NO_ROTATION
inherited_rebuy: LOCKED
inherited_new_entry: NOT_ACTIVE
latest_collector_contract: DATA_PING_RUN_FIRST_STATELESS_v1
latest_collector_version: 15.0
latest_snapshot_id: dpsnap_20260726T101847086Z_001
F4: MATURED / GATE_UNMET / CAUSAL_CONFOUNDED
F1: PENDING_FINAL_ROWS
H7: PENDING_ROW5_AND_SLOPE_ADJUDICATION
low_vol: BLOCKED_BY_INTERNAL_ARITHMETIC_CONFLICT
leading_claim: PENDING_WITH_FOMC_CONFOUND
W30_external_evidence: ARCHIVED_PASS_WITH_CONFLICTS
canonical_state_change_from_handover: NONE
```

If any item cannot be recovered, the thread must read GitHub rather than initialize a blank framework state.
