# #1211 owner decision packet — ETF knowledge time (E1X F04)

**Status: OWNER_DECISION_READY.** The evidence is enough for the owner to decide. It is not enough to make the decision on the owner's behalf: nothing here changes historical feature semantics or any consumer.

- **Evidence base:** fresh main `b854dbc31`, live Farside read at 2026-09-23T15:29Z, and the vintage ledger (3,732 rows, 1,246 asset-sessions, 118 of them with real-time evidence).
- **Supporting files:** every number below comes from `ETF_KNOWLEDGE_TIME_POLICY_COMPARISON.json`, `ETF_REVISION_SUMMARY.json` and `ETF_RIGHT_TRUNCATION_RESULTS.json`.

## 1. What the evidence shows

**Publication (knowledge-time delay):**

- No evidenced session was observable at its session close.
- The first observation came 6.3 h or more after the close, typically T+1 ≈ 02:20Z.
- 27 of the 88 evidenced sessions that can be assessed were **provisional** at first observation by the live rule (the other 30 have total-only evidence and cannot be assessed):
  - `'-'` cells for funds that report late (IBIT, ETHA, …), or
  - an all-`'-'` row showing Total `0.0` (BTC and ETH 2026-09-08 at T+1 05:55Z).

**Completion:**

- Across the 54 daily-cadence sessions, the first observation that was complete by the live rule came:
  - typically around T+1 07:00Z (median 11.1 h after close, p90 15.6 h),
  - in the worst case 30.6 h after close (BTC 2026-08-19, complete at T+2 02:35Z).
- The smallest lag not contradicted by any incomplete observation is 9.9 h.

**Data revisions:** 35 sessions / 39 events.

- **26 LATE_FUND_VALUE** (14 BTC, 12 ETH).
  - Median |Δ| is 60 M USD and the maximum is 503 M USD.
  - All arrive within 30.6 h of the close.
  - Two changed sign.
  - Four of them were already stored by the settled double-read as "final":
    - 08-17: BTC 137.3 → 297.5, ETH 5.0 → 30.9
    - 08-19: BTC 164.2 → 517.2, ETH 17.7 → 186.8
- **13 NEW_FUND_BACKFILL** (ETH, MSSE).
  - Farside added MSSE between 2026-09-17 and 2026-09-18, with values back to 2026-07-27.
  - Median |Δ| is 0.8 M and the maximum is 14.3 M.
  - They were observed up to 56.8 days after the close (1,363 h).
  - **No fixed lag bounds this kind of revision.**

**History:**

- All 1,127 comparable v1 rows (2024-01-11 → 2026-07-24) are identical to the 2026-09-23 vintage.
- Across two vintages two months apart, no historical value was restated.
- Their publication times are nevertheless **unknowable after the fact**: `LOWER_BOUND_ONLY` for 1,102 sessions.

## 2. Policy results

The table is judged against the pre-MSSE vintage, which isolates knowledge-time delay. The LATEST column shows the same policy judged against the vintage that includes MSSE.

| Policy | Coverage | Consistent | Proven lookahead / revised after K | Data loss | Verdict | With MSSE (LATEST) |
|---|---|---|---|---|---|---|
| A: session close | 1220 | 0 of 118 | 26 lookahead, 92 unknown | 0 | UNSUPPORTED | 35 lookahead |
| B: first observed | 118 | 92 | 26 revised later (max 24.2 h) | 1102 | Vintage time only, not finality | 35 revised |
| C: first complete observed (live rule) | 104 | 104 | 0 | 1116 | SUPPORTED on evidenced sessions | 13 revised (MSSE) |
| D: first settled double-read | 74 | 70 | 4 revised (08-17, 08-19) | 1146 | UNSUPPORTED as finality | 16 revised |
| E: close + 30.6 h (in-sample max) | 1220 | 66 of 118 | 0 in-sample by construction | 0 | NOT_ENOUGH_EVIDENCE for history | 13 lookahead |
| F: next session open | 1220 | 62 of 118 | 4 lookahead (08-17, 08-19) | 0 | UNSUPPORTED | 16 lookahead |

**Right truncation** (production W30 features and the pack builder, run with the E1X harness unchanged):

- **A** leaks: proven TRUE_FUTURE_LEAKAGE.
- **B and C** leak through the feature claim itself. W30 claims each trailing feature at its own row's time, so under a per-session policy a feature is claimed before a window input is known. With a cumulative-max feature claim the leak disappears:
  - B reduces to SOURCE_VINTAGE_RISK.
  - C reduces to INSUFFICIENT_HISTORY (pre-MSSE).
- **D** is SOURCE_VINTAGE_RISK.
- **E and F** are UNKNOWN (observation-limited) plus SOURCE_VINTAGE_RISK.

## 3. Decision items, each with its evidence-backed options

**D1. Usable live timestamp.**

- *Option (evidence-supported):*
  - `knowledge_available_at` = the verification time of the first double-read observation that is **complete by the live rule**.
  - Complete by the live rule means all four of:
    - parity holds,
    - a Total is present,
    - there are no `'-'` cells except structural ones,
    - the row is not all-`'-'`.
  - This is C ∧ D. C alone had 0 contradictions on 104 evidenced sessions. D alone had 4, and all 4 were rows C rejects (unresolved `'-'` cells).
- *Alternative:* keep D as it is. That knowingly accepts the 08-17/08-19 false finality.

**D2. Fallback when no verified complete observation exists.**

- Use B (first observation) as `PROVISIONAL` with `finality_status = PROVISIONAL`, never as final.
- An all-dash row is `PENDING_ALL_DASH`, never 0.0 flow.

**D3. UNKNOWN handling.**

- Sessions with no timed capture keep `knowledge_time_status = LOWER_BOUND_ONLY`. That is 1,102 sessions: everything before 2026-06-26 plus gaps. The first timed capture was 2026-07-15T20:48Z and it covered sessions back to 2026-06-26.
- A replay may use them only under D5.

**D4. Source-vintage handling.**

- Keep the append-only vintages, one per row hash; the ledger is the model.
- A replay at cutoff t binds the latest vintage observed ≤ t.
- Later vintages are appended with a `revision_kind`, never rewritten.
- The single 2026-07-26 pack is one retrospective vintage. Its observed stability (0 restatements in 1,127 rows) does not make MSSE-type backfills impossible.

**D5. Backtest eligibility of history.** The owner picks exactly one:

- **(a) Exclude.** ETF features are ineligible for knowledge-time-sensitive backtests before the first timed capture (2026-07-15T20:48Z).
- **(b) Assumed rule.** `knowledge_available_at = ASSUMED_BY_OWNER_RULE`, for example close + L with L ≥ 30.6 h (T+2 ≈ 03:00Z) or the next-but-one session open. It must be labelled ASSUMED, never OBSERVED, and must declare:
  - the sample it rests on (54 sessions, 2026-08 → 2026-09),
  - that it does not cover MSSE-type backfills.
- **(c) Current rule.** Keep `AVAILABLE_AFTER_US_SESSION_CLOSE`. **Not supportable:** falsified by 26 proven lookahead sessions and by 0 of 177 evidenced feature rows being computable at the claimed time.
- The lab does not recommend a lag value. Per the mission rule, 30.6 h is reported as an evidence quantity, not chosen for performance.

**D6. Feature knowledge time.**

- Adopt "feature knowledge = cumulative max of its input rows' knowledge times".
- W30 `build_etf_trailing` currently uses the row's own time. That is correct only while the rule is monotone in session date (A, E, F), and wrong for B, C and D.

**D7. Post-cutoff revisions.**

- A backtest evaluated at cutoff t never sees revisions observed after t.
- Scores already produced on a superseded vintage keep that vintage and are not rescored silently.
- A re-evaluation is a new, labelled run.

## 4. Recommended contract

`ETF_OBSERVATION_v1` (`ETF_OBSERVATION_v1.schema.json`) separates the fields that are currently merged:

- `session_date`
- `source_observed_at_utc`
- `verification_completed_at_utc`
- `knowledge_available_at_utc` (plus `knowledge_time_status` and the owner rule id)
- schema status (`KNOWN` / `KNOWN_ADDITIVE` / `UNKNOWN` → fail closed)
- completeness, finality and revision

It is a record shape the existing owners emit or map to, not an engine.

## 5. Unknown remainder (cannot be resolved with current evidence)

- Actual Farside publication time of any session: only observation upper bounds exist.
- Publication and completion behaviour before 2026-07-15, and whether the 2026-08/09 pattern generalises.
- Future schema backfills: when, how far back, and how large.
- The first time the new ETH layout was live: between 2026-09-17T11:35Z and the first failing settled run on 2026-09-18, whose snapshot is not committed.
- Whether `'-'` cells that were never resolved (BTC 07-27 BTCO, 08-07 EZBC; ETH 07-27 QETH) are zero flows or missing data.

## 6. What this packet does not do

- It changes no consumer, W30 semantics, manifest rule, live finality rule or history pack.
- The live/historical firewall holds: D5 applies to replay only and can never set live `finality_status` or feed `daily-settled-etf-calibration`.
