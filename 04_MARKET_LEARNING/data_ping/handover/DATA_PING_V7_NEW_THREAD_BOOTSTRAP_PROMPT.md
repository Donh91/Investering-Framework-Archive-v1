# DATA PING V7 — NEW MAIN THREAD BOOTSTRAP PROMPT

Copy this block into the first message of the new DATA PING V7 main thread.

```text
DATA PING V7 — MAIN THREAD CONTINUATION BOOTSTRAP

This is a continuation of the existing Investering framework, not a new framework and not a reset.

Before making any framework interpretation, read the GitHub handover:

04_MARKET_LEARNING/data_ping/handover/DATA_PING_V7_MAIN_THREAD_HANDOVER_2026-07-26.md

Also read the archived W30 evidence package index, forecast ledger and conflict registry:

04_MARKET_LEARNING/master_monday/W30_2026/2026-07-26_claude_evidence_recovery/00_EVIDENCE_INDEX.md
04_MARKET_LEARNING/master_monday/W30_2026/2026-07-26_claude_evidence_recovery/02_FORECAST_MATURITY_LEDGER.md
04_MARKET_LEARNING/master_monday/W30_2026/2026-07-26_claude_evidence_recovery/04_CONFLICT_REGISTRY.md
07_PROMPTS_AND_AGENTS/skill_runs/2026-07-26__w30-master-monday-evidence-recovery__receipt.md

Inherited framework state:

rotation = NO_ROTATION
rebuy = LOCKED
new_entry = NOT_ACTIVE
large_caps = WATCH_ONLY
portfolio_action = NONE
canonical_state_change = NONE
stage1 = GOVERNANCE_PENDING

Latest collector contract:

contract = DATA_PING_RUN_FIRST_STATELESS_v1
version = 15.0
runtime = DATA_PING_LONGITUDINAL_COLLECTOR_v1
latest_snapshot_id = dpsnap_20260726T101847086Z_001

Treat all values from that snapshot as predecessor evidence only. They are not current market data.

Active forecast state:

F4 = MATURED / GATE_UNMET / CAUSAL_CONFOUNDED / DO_NOT_REOPEN
F1 = PENDING final settled UTC rows; no interim score
F5 = CLOSED_TRIGGERED / DO_NOT_RETRIGGER
H7 = PENDING final row and frozen slope adjudication
low-vol = BLOCKED by internal arithmetic conflict until deterministic recompute
leading claim = PENDING with FOMC as preregistered confound
EXT-GCBLO-2026-07-24 = PENDING to 2026-10-23

Do not silently resolve any conflict. Load the conflict registry first.

Run behavior:

1. A normal user message “Data ping” triggers one fresh full V7 collector run.
2. Use BTCUSDT, ETHUSDT and ETHBTC as mandatory first-class assets.
3. Preserve LIVE, SETTLED, LATEST_AVAILABLE, STALE, PARTIAL and UNKNOWN temporal tags.
4. Preserve method versions, venue tags, source-QA, fallback levels and exact timestamps.
5. Include predecessor comparison only when an accepted predecessor is actually available.
6. Do not invent history in a fresh thread.
7. Collector output may calculate deterministic features but must not decide rotation, recovery, rebuy, entry, deployment, altseason or portfolio action.
8. Main-framework interpretation occurs only after the packet is complete enough and the inherited state is loaded.
9. Weekends and ETF non-sessions are never zero-filled.
10. No forecast ledger is reset merely because this is a new chat thread.

First response requirement:

Return a concise THREAD_BOOTSTRAP verification containing:

- handover_loaded: YES/NO
- inherited framework state
- collector contract/version
- latest predecessor snapshot ID
- active forecast statuses
- open conflict count
- current-data status: NOT_YET_COLLECTED
- ready_for_fresh_data_ping: YES/NO

Do not run market sources until the user asks “Data ping”.
Do not change canonical state during bootstrap.
```
