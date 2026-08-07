# Claude OTA framework reconciliation — 2026-08-07 19:22 UTC

## H7 / settlement

- 6 Aug UTC settlement is accepted as source-supplied direct-settled evidence: BTC 64323.61, ETHBTC 0.02960, no 0.0300 touch.
- H7 row 17 was not formed at the source run and receives no scoring.
- Historical H7 score remains `EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION`.
- Row-16 recurrence remains follow-through only under `H7_LIFECYCLE_GOVERNANCE_DECISION_v1`; no retrigger is invented.

## ETF reconciliation

Accepted direct BTC session totals: 3 Aug +170.1M, 4 Aug +211.5M, 5 Aug +244.4M, 6 Aug +137.6M. Four-session sum = +763.6M; IBIT = +606.8M, 79.46% of the four-session complex. HODL was -14.7M then -32.8M; GBTC printed +7.5M on 6 Aug.

Main-thread arithmetic corrections:

- synchronized candidate through 6 Aug: BTC 3/5/7 = +593.5 / +498.2 / +763.4M; ETH 3/5/7 = +206.0 / +203.1 / +183.0M.
- authoritative owner through 5 Aug: BTC 3/5/7 = +626.0 / +593.7 / +576.1M; ETH 3/5/7 = +102.0 / +123.8 / +100.3M.
- Claude's +730.8M BTC 7-session, +392.7M/+404.4M BTC through-5-Aug 5/7-session, +123.9M/+91.1M ETH through-5-Aug 5/7-session are not accepted.
- 20-session +651.4M is quarantined because the current owner ledger does not contain enough validated rows for independent reproduction.

The substantive cross-asset correction is nevertheless accepted: synchronized windows show BTC absolute ETF flow remains materially larger than ETH. Anti-transmission remains withdrawn because both assets show positive multi-session absorption. 6 Aug is still a complete-row candidate, not owner, until `DP-ETF-DIRECT-OWNER-20260807-02` completes two independent retrievals >=60 seconds apart with hashes/freeze/finality.

## CE-02 / CE-01

CE-02 is retained as an exploratory falsification of its own stated hypothesis: the source reports r=+0.004 across n=16. It may be useful as process evidence that explicit falsification rules shorten hypothesis lifetime. It cannot rescore H7 or become a canonical feature.

CE-01 is **not** confidence-upgraded. Failure to find dependence on |BTC 1D| in n=16 does not prove a memoryless symmetric generating process. CE-01 remains governance backlog only.

## Architecture learning

The source's stronger lesson is accepted in a bounded form: the framework should optimize for short error half-life, provenance, falsifiability and rapid correction rather than assuming faster access to lagging public indicators creates predictive edge. This is process/governance learning, not a new market sensor.

## Decision state

No canonical state change. No portfolio action. `NO_ROTATION`, `WAIT`, `REBUY_LOCKED`, `NEW_ENTRY_NOT_ACTIVE`, `DO_NOT_ADD_RISK` remain in force pending broader spot/breadth/ETHBTC confirmation and owner-grade data continuity.
