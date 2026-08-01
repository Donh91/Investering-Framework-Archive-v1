# T4 Microstructure Two-Live-Readback Receipt

**Dato:** 2026-08-01  
**Status:** PROSPECTIVE_SOURCE_CAPTURE_VERIFIED  
**Område:** Existing T4 repair / Binance Spot source verification  
**Primary folder:** `06_RESEARCH_LAB/forward_tests/`  
**Depends on:** `2026-07-31__t4-execution-microstructure-repair-protocol-v0-1__forward-test.md`  

---

## 1. Executive result

Two explicit live Binance Spot microstructure captures were executed in separate GitHub Actions runs and independently read back from uploaded artifacts.

```yaml
required_live_readbacks: 2
verified_live_readbacks: 2
source_capture_status: PROSPECTIVE_SOURCE_CAPTURE_VERIFIED
eligible_t4_event_rows: 0
valid_outcome_rows: 0
execution_edge_status: NOT_PROVEN
market_state_changed: false
gates_changed: false
portfolio_action_changed: false
```

The source gate is passed.

The decision-value gate is not passed.

---

## 2. Live readback 1

```yaml
workflow_run_id: 30714802392
workflow_job_id: 91408474991
artifact_id: 8822996310
artifact_digest: sha256:64f51154b163ca7fb9d14cb709e5f56e690b5662da8f5f3af749a5186daf9c8a
run_id: T4_MICRO_20260801T192750_59fa27c55eb4
retrieval_timestamp: 2026-08-01T19:27:50.761013Z
manifest_members: 6
owner_sha256: 7e28927c59b241a370af0609814d54a7f30e7e022d6a68ef2f04caac6686d818
unit_tests: PASS
compile: PASS
live_capture: PASS
manifest_readback: PASS
artifact_readback: PASS
```

Raw payload lineage:

```yaml
BTCUSDT_depth: eb93b1ff9394f6220b6563c663682b500d5b1e886f10d9d5d05c686e50bfa167
BTCUSDT_aggTrades: d51616a47d521f3b929c9623eeffcd4d14c8b740113958e5888faf89286bb6fe
ETHUSDT_depth: a0d1a849519151d2dff10d7bf8e54d5e09653d79cafce33c959f95623a076a6e
ETHUSDT_aggTrades: 8dceaf3b48efd9a63c027cba07a8bc4f63e5c0ede7887f1609fcdc1deb69a4d8
```

---

## 3. Live readback 2

```yaml
workflow_run_id: 30714836332
workflow_job_id: 91408568893
artifact_id: 8823005774
artifact_digest: sha256:b12a60d4f81bf30c67fcae9dfc9a7935ea0b56dd4b7b1c58ca246fe6a6d46527
run_id: T4_MICRO_20260801T192842_52157ea301ef
retrieval_timestamp: 2026-08-01T19:28:42.616583Z
manifest_members: 6
owner_sha256: a7f1d51f2e3343e2d4b7096d89a26fb3bbfd6fbb8cf10ae01de81497acf61341
unit_tests: PASS
compile: PASS
live_capture: PASS
manifest_readback: PASS
artifact_readback: PASS
```

Raw payload lineage:

```yaml
BTCUSDT_depth: a63ef8e907e1622cdc56103a75659ca13643558273b1c85ecb3b1a1e9ade62ca
BTCUSDT_aggTrades: a38aaa729d7a1a1feca331aa5bbd77ad652b260dff4fe3e6bde3d194751c3de5
ETHUSDT_depth: bc7f7b84b802a476c2944e16f60c2fe2f777f91a1ff6dbdffcc444777cbb9294
ETHUSDT_aggTrades: dec6f47e9e7e93107f77b748af12a44acc9a59b659efdd3b37923b4718a6f0b5
```

---

## 4. Independence and change verification

The two captures are distinct live observations, not duplicate artifact copies.

Verified differences include:

```text
- different GitHub Actions workflow runs and artifacts;
- different run IDs and retrieval timestamps;
- all four raw source-payload hashes changed;
- BTC and ETH order-book update IDs changed;
- aggregate-trade ID windows advanced;
- owner snapshot hashes changed;
- artifact ZIP digests changed.
```

This supports prospective source operability and reproducible artifact materialization.

It does not establish trading edge.

---

## 5. Binding interpretation

```text
LIVE SOURCE VERIFIED != SIGNAL VERIFIED
SOURCE ROW != ELIGIBLE EVENT ROW
ELIGIBLE EVENT ROW != MATURED OUTCOME ROW
POINT_IN_TIME_DEPTH != REPLENISHMENT
DEPTH IMBALANCE != BUY OR SELL AUTHORITY
TAKER IMBALANCE != STANDALONE DIRECTIONAL AUTHORITY
```

The next evidence gate is an eligible, pre-registered T4 event with frozen price-only baseline, attached microstructure source fields and matured 1H, 4H, 12H and 24H outcomes.

Until then:

```yaml
framework_behavior_changed: false
source_extension_authority: zero
promotion_status: blocked_by_outcome_rows
```
