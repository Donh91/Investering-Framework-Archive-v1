# Claude OTA source record — CE-02 falsification / BTC ETF update

```yaml
source_run_timestamp_utc: 2026-08-07T19:22:30.567Z
source_run_timestamp_cest: 2026-08-07T21:22:30+02:00
operating_mode: STANDALONE_OTA
reference_bridge_present: false
reference_data_ping_run_id: null
previous_claude_ota_reference: 2026-08-06T23:03:54.029Z
canonical_effect_claimed: NONE
portfolio_effect_claimed: NONE
requires_main_thread_crosscheck: YES
```

## Source-supplied claims

### 6 Aug UTC settlement
- BTC settled close 64323.61; H 64999.00; L 64172.00.
- ETHBTC settled close 0.02960; H 0.02965.
- No 0.0300 touch; source reports fourteenth session without touch.
- F1 follow-through: thirteen post-window sessions with zero settled breach; H-WIN-01 unchanged LOW_MODERATE.
- H7 row 17 was NOT_FORMED at source run; no row-17 scoring permitted.

### BTC ETF direct source update
Source reports Farside BTC rows:
- 2026-08-03 +170.1M
- 2026-08-04 +211.5M
- 2026-08-05 +244.4M
- 2026-08-06 +137.6M
Four-session sum +763.6M; IBIT contribution +606.8M (79.46%).
Issuer details highlighted: HODL -14.7M then -32.8M; GBTC +7.5M on 6 Aug.

### Claude rolling sums requiring reconciliation
Claude reported BTC 3/5/7/20-session = +593.5 / +498.2 / +730.8 / +651.4M. Main-thread crosscheck finds the 7-session number inconsistent with the supplied ledger; correct synchronized 7-session BTC candidate through 6 Aug is +763.4M. The 20-session claim is not independently reproducible from the current owner ledger and remains unaccepted.

Claude also corrected its prior asynchronous ETH-exceeds-BTC claim. Main-thread synchronized owner/candidate windows support the direction of that correction, but Claude's through-5-Aug BTC 5/7-session numbers are again incorrect and must not become owner data.

### CE-02
Claude reports exploratory test n=16:
- Pearson r(|BTC 1D|, spread) = +0.004
- small-move half n=8: mean spread +0.220pp, ETH lead 5/8
- large-move half n=8: mean spread +0.050pp, ETH lead 4/8
Source labels CE-02 FALSIFIED.

Main-thread handling: preserve as exploratory self-falsification of the stated post-hoc hypothesis only. Do not rescore H7. Do not promote CE-01 confidence merely because CE-02 failed; absence of this correlation is not independent evidence of a memoryless symmetric generating process.

## Market-intelligence note
Claude argues that the framework's defensible edge is shorter error half-life rather than being first to every market fact. Retained as architecture/process learning, not as a market finding. Claims about exact media/Farside latency and prior replication multipliers remain non-canonical unless separately source-backed.
