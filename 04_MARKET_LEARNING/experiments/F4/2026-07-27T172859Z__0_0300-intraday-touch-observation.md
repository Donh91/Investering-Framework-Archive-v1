# ETH/BTC 0.0300 intraday observation

## Supplied observations

| Session | High | Observed/settled close | Audit label |
|---|---:|---:|---|
| 2026-07-26 UTC, settled | 0.03000 | 0.02989 | `INTRADAY_TOUCH_SETTLED_CLOSE_BELOW` |
| 2026-07-27, in progress | 0.03020 | approximately 0.02988 at observation | `INTRADAY_BREAK_IN_PROGRESS_CURRENTLY_BELOW` |

The first session touched, but did not exceed, 0.0300 at its high and settled below. The second session exceeded 0.0300 intraday but was not settled at the observation time.

## Governance

```yaml
settled_close_above_0_0300: NO
second_close_rejection_claim: PREMATURE
F4_status: GATE_UNMET_SCORED_CLOSED
F4_reopened: NO
new_gate_test_preregistered: NO
rotation_consequence: NONE
```

UTC and CEST close bases remain materially different near the threshold. Any future test must preregister its settlement basis before observation.