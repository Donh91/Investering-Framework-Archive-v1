# Daily Rule Effectiveness Summary — P1b Gate Window Partial Replay

Date: 2026-07-07  
Status: PARTIAL_REPLAY_WITH_ASOF_LIMITS / MARKET_ONLY_RULE_SIMULATION

## Scope

Replay window: 2026-06-02 to 2026-07-02.

Sources used:

- FMP composite BTC OHLC from P1b
- Farside BTC ETF flow file from P1b
- Current ratified v0.2/FNP/ETF governance rules

Not used:

- full DATA PING rows
- breadth ledger
- BTC.D ledger
- stablecoin official ledger
- funding/OI ledger
- full ETHBTC daily ledger

These are DATA_MISSING.

## Key mechanical findings

- Rows: 31 daily rows.
- Close <59.4K soft breach count: 1.
- Close <59.0K hard-death count: 1.
- 2 consecutive closes <59.4K count: 0.
- First close <59.0K: 2026-06-30.
- First close above 60.9K after hard-death date: 2026-07-02.

## ETF context

- ETF negative-print rows: 25.
- ETF positive print but 5-ETF-day trend still negative rows: 6.
- ETF positive print and positive 5-ETF-day trend rows: 0.
- 2026-07-02 showed positive BTC ETF print (+223.5M) but trailing 5 ETF-day sum remained negative in this file, so it is improvement, not flow confirmation.

## Rule-level interpretation

### v0.2 hybrid gate

No separate soft-breach-only save appeared in this narrow window because the first close below 59.4K was also below 59.0K on 2026-06-30.

In this window, hybrid and a binary shelf-death trigger largely converge on the same death date.

Interpretation:

- v0.2 mechanics work as specified.
- This narrow replay does not prove hybrid superiority over binary, because the critical breach was already a hard-death breach.
- This does not weaken P1b’s broader OHLC result; it only says this specific window is not where the hybrid design shows its biggest advantage.

### 59.0K hard-death

Triggered on 2026-06-30 close at 58,523.93.

Interpretation:

- Mechanical shelf-loss trigger worked.
- Outcome window in this file is too short to declare whether 59.0K was ultimately too tight or ideal.
- Keep existing annotation: 59.0K is tight hard-death, not wide ATR buffer.

### 2/3-close discipline

No reliable recovery confirmation should be inferred.

Interpretation:

- Close persistence is tracked as discipline only.
- No price-edge claim.
- No recovery confirmation.

### ETF flow

ETF flow context helped by blocking overconfident recovery language throughout a mostly negative ETF trend.

2026-07-02 positive print is improvement, not full flow confirmation, because the trailing 5 ETF-day sum remained negative.

### FNP

Not fully scoreable because first-permitted-entry and full live DATA PING rows are missing.

Keep ledger-only.

## Framework consequence

```text
keep / partial-confirm mechanics / needs more data
```

Portfolio action: none.  
Rebuy status: unchanged / LOCKED.  
Recovery Confirmed: no.  
Rotation Confirmed: no.

## Missing before full replay

- Complete DATA PING rows for 2026-06-02 to 2026-07-02.
- Daily breadth ledger.
- Daily BTC.D ledger.
- Stablecoin official mcap/7D/30D ledger.
- Funding/OI full-window ledger.
- Full ETHBTC daily ledger.

## Hindsight status

PASS for market-only rule simulation.

As-of fields use only same-day or prior OHLC/ETF rows. Future data is limited to outcome columns.

However, because the rules were ratified after the historical window, this is a counterfactual rule replay, not proof of actual live framework behavior at the time.
