# BACKTEST WAVE 1.3 — Authority & Lineage Recovery

```yaml
wave: BACKTEST_WAVE_1_3
status: PARTIAL_DURABLE_PASS
A_class_policy_events: 0
approved_direct_ETHBTC_challenger: COINBASE_ETH-BTC
conditional_direct_shadow: KRAKEN_ETHXBT
owner_registry: FINAL_FOR_SELECTED_SCOPE
actual_policy_replay_unlocked: NO
final_holdout_opened: NO
```

## Decision lineage

### FT-1

The rule is substantially reconstructed. First exact rule evidence is `2026-06-11T03:53:21Z`; v0.1.1 confirmation is `2026-06-11T04:28:41Z`; expected confirmation cost was 5–7%; evaluation was due 2026-07-10. The rule was superseded by v0.2 on `2026-07-02T17:13:36Z`.

FT-1 remains non-replayable because the original exact 2026-06-10 freeze timestamp, execution or explicit no-action receipt, actual transaction-cost contract and settled closeout row are missing.

Verdict: `B_RECONSTRUCTED_NOT_POLICY_REPLAYABLE`.

### FNP-001

The eight-week period ended on 2026-05-25. The canonical row was created on `2026-06-13T11:03:08Z` and finalized at `2026-06-13T11:13:47Z`, after the outcome horizon.

Verdict: `C_RETROSPECTIVE_POLICY_QUARANTINE`. It remains valid retrospective learning but is forbidden as actual-policy evidence.

### TD-97

TD-97 opened on `2026-06-29T17:34:05Z` as a forward macro/rotation claim with deployment, rebuy and rotation-confirmation authority explicitly set to none. Later framework receipts preserved NO_ROTATION and no portfolio action.

Verdict: `B_FORWARD_CLAIM_NO_ACTION_AUTHORITY`.

## Direct ETH/BTC venue validation

Frozen contract:

- minimum 30 settled UTC sessions;
- median absolute close deviation <= 5 bps;
- p95 <= 20 bps;
- maximum <= 75 bps;
- gate agreement >= 99% at 0.0275 and 0.0300.

### Coinbase versus Binance, recent 90 settled sessions

```yaml
overlap: 90
median_abs_close_dev_bps: 1.95
p95_abs_close_dev_bps: 8.51
max_abs_close_dev_bps: 12.67
gate_agreement_0_0275: 100%
gate_agreement_0_0300: 100%
verdict: APPROVED_DIRECT_CHALLENGER_OUTAGE_CONFIRMATION
```

### Kraken versus Binance, recent 90 settled sessions

```yaml
overlap: 90
median_abs_close_dev_bps: 2.59
p95_abs_close_dev_bps: 8.30
max_abs_close_dev_bps: 11.23
gate_agreement_0_0275: 98.89%
gate_agreement_0_0300: 100%
verdict: CONDITIONAL_DIRECT_SHADOW
```

One near-threshold 0.0275 disagreement prevents Kraken from passing the frozen 99% agreement gate.

## Authority consequence

Binance remains canonical owner. Coinbase is approved for direct outage confirmation, but does not silently become owner. Derived ETH/USD divided by BTC/USD remains diagnostic only.

## Prospective repair

No historical A-class event was fabricated. Instead, a mandatory prospective decision receipt now captures exact knowledge, decision, execution or no-action timestamps, source hashes, costs, label horizon and overlap cluster.

```yaml
actual_policy_replay: BLOCKED_FAIL_CLOSED
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
canonical_state_change: NONE
portfolio_action: NONE
```