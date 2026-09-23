# ETF Temporal Integrity & Source Revision Lab v1

**Run facts**
- START MAIN `b854dbc31f751af06d9934364a46d9df4d6bbbf0` (2026-09-23T15:17:21Z). Lab time 15:23–16:10Z.
- Mode: Cowork research, no Codex.
- GitHub push/API return 403 in this session, so everything is delivered as files plus a local branch bundle.

**Rules held throughout**
- No consumer, owner, workflow, finality rule, W30 semantics or history-pack byte was changed.
- No timestamp was invented. UNKNOWN stays UNKNOWN.
- No lag was chosen for performance.
- v1.1 (#1212) and #1211 were kept apart.

**Artifacts**

| Artifact | Section |
|---|---|
| `ETF_LIVE_SCHEMA_REPRODUCTION.json` | §2 |
| `ETF_VINTAGE_LEDGER.jsonl` | §3 |
| `ETF_REVISION_SUMMARY.json` | §4 |
| `ETF_KNOWLEDGE_TIME_POLICY_COMPARISON.json` | §5 |
| `ETF_RIGHT_TRUNCATION_RESULTS.json` | §6–7 |
| `ETF_V1_1_REVALIDATION.json` | §8 |
| `ETF_CONSUMER_AUDIT.json` | §1, §9 |
| `ETF_OBSERVATION_v1.schema.json` | §10 |
| `ETF_OWNER_DECISION_PACKET_1211.md` | §11 |
| `CODEX_OWNER_PACKET_UPDATES.md` | §13 |
| `lab/` scripts, `branches/` bundle, patch and PR body | §14 |

---

## 0. Boot

**Cockpit** (`LATEST_CODEX_EXECUTION_STATE` 15:17:21Z): CODEX_READY 24, POST_FIX 21, PERSISTING 14, RESOLVED 14, IN_REMEDIATION 6, OBSERVED 1.

**ETF tasks**
- `e9fd7efd` / `d15b736c`: daily-settled-etf, LATEST_RUN_FAILED / REPEATED.
- `4a968f5f`: v1.1, E1X D01.
- `ebaa2306`: audit-etf-adapter, RESOLVED.

**Architecture blockers**
- `ETF_OWNER_STALE`: FLO snapshots stop at 2026-09-15.
- `OWNER_COVERAGE_DEGRADED`.

**Production owner re-run** (15:28:53Z): `DEGRADED`, with `ETH HEADER_NOT_FOUND`; BTC PASS.

## 1. Owner map

Details are in `ETF_CONSUMER_AUDIT.json` → `owner_map`.

| Component | Owner (existing) | Knowledge / finality semantics today | Codex |
|---|---|---|---|
| Live source parser | `farside_etf_owner.py` | `retrieved_at` = script start; `session_final=True` for every row dated before the UTC date (calendar claim) | `e9fd7efd`/`d15b736c` |
| Live settlement verifier | `daily-settled-etf-calibration.yml` | Two reads 65 s apart; parity; unknown cells tolerated if parity holds | same |
| Live settled capture | `03_DAILY_CAPTURE_LOGS/etf` + LATEST + lifecycle receipts | Append-only by row signature; `verification_completed_at` on receipts | same |
| FLO owner capture | `framework-learning-operations.yml` → `research/etf_owner` | Snapshot per run, continue-on-error | — |
| Historical raw pack | Project exports (uploaded 2026-07-26T19:28:44Z) and the 07-06 raw CSVs | Session date only | — |
| Historical normalized pack v1 | truth-layer pack (commit `4e2ba082d`) | `AVAILABLE_AFTER_US_SESSION_CLOSE` | `4a968f5f` |
| Historical feature builders | Pack `build_etf_flow_features.py`; W30 `build_etf_trailing` / `divergence` | Feature knowledge = the row's own session close | none (F04 → owner) |
| Backtest knowledge-time contract | #1211 (owner) | undecided | not code-only |
| E1X test | `strategy_factor_leakage_e1_production.py` | `Record.available_at` = evidenced time | — |

**No component is missing an owner.** What is missing is:
- a shared record contract (§10), and
- an owner decision (§11).

## 2. Live ETH schema

**Capture.** Captured with the owner's own client path (`urllib`, owner User-Agent). The same User-Agent over `curl` got a Cloudflare 403 challenge; that was not retried or circumvented.

**Current ETH shape**
- One ticker `<th>` row: `['', ETHA, ETHB, FETH, ETHW, TETH, ETHV, QETH, EZET, MSSE, ETHE, ETH, Total]`.
- Then a `<th>` Fee row, a `<td>` Seed row (MSSE seed blank), a stray unclosed `<tr>`, the date rows, and a `<td>` Total footer.
- 555 date rows, 2024-07-23 → 2026-09-23, all 13 cells wide.

**MSSE**
- Position: index 8, between EZET and ETHE.
- First value 2026-07-27. 41 rows are non-blank and 14 non-zero; every earlier cell is `'-'`.
- All 555 rows reconcile to Total when MSSE is included. 10 fail parity without it.

**A second change was found.** The issuer-name row, followed by a ticker row with blank edges, is gone.
- That old layout was what `SOURCE_TWO_ROW_TICKER_HEADER` matched (every v4 ETH snapshot from 08-10 to 09-15).
- The two-row header is no longer valid.

**Raw HTML hash is not a vintage id.** The page's sha256 changes on every fetch (`6b37840e…` at 15:28:53Z, `eceaf80c…` at 15:29:03Z). A stable vintage id must hash the parsed table (`table_content_sha256`).

**Fixture matrix** (16 fixtures × 3 variants):

| Variant | Live and history | Old shapes | Negatives failing closed | Verdict |
|---|---|---|---|---|
| Production (main) | ETH FAIL (`HEADER_NOT_FOUND`) | pass | 8/9 (accepts missing-Total-column via width fallback; parity then fails) | fails on live |
| Add MSSE to frozen schema | pass, **via width fallback** | old two-row layout now FAILS | **4/9**: accepts no-Total-label, no-header, duplicate ticker; **silent mislabel** on same-width unknown ticker and on reordered ETH columns (parity passes) | unsafe on its own |
| Strict registry prototype | pass (`KNOWN_ADDITIVE_SCHEMA_REVISION`) | pass | **9/9** | meets contract |

- `KNOWN_ADDITIVE_SCHEMA_REVISION` is accepted explicitly (MSSE registered).
- `UNKNOWN_SCHEMA_REVISION` fails closed.
- The CODEX_READY repair was **not** implemented; its packet was improved (§13).

## 3. Vintage ledger

`ETF_VINTAGE_LEDGER.jsonl` has 3,732 append-only rows: one per asset × session × observation time × source vintage, covering 1,246 asset-sessions.

**Sources**

| Source | Rows |
|---|---|
| FLO owner snapshots v1/v4 | 1,164 |
| Settled captures | 78 |
| Re-verification receipts | 20 |
| July DATA PING payloads and Farside supplements | 60 |
| v1 pack (retrospective vintage 2026-07-26) | 1,164 |
| Live read 2026-09-23 | 1,246 |

**Fields carried by every row**
- Observation times: `observed_at` and its basis, `source_retrieved_at`, `verification_completed_at` (from the lifecycle receipt of the same run).
- Hashes: source, schema and row.
- Values: fund header set, reported and calculated Total, parity, unknown cells.
- Status: session-final claim, workflow status.
- Provenance: evidence path, and the git commit and time that added it.
- Session-level derivations:
  - first and later observed totals and times
  - revision detected / delta / kinds
  - first complete observation
  - first verified-final observation
  - `knowledge_time_status`

**Knowledge-time status:** 118 sessions OBSERVED, 1,128 LOWER_BOUND_ONLY.

**Not-a-source-revision rows are kept but flagged:**
- the ETH 2026-07-20 value 3.7, a transcription error;
- the 11 malformed v1 rows.

## 4. Revision taxonomy

DATA REVISIONS: 35 sessions, 39 events. Knowledge-time delay is counted separately (§5).

| Kind | Events | BTC / ETH | Median / max \|Δ\| (M USD) | Lag after close, median / max |
|---|---|---|---|---|
| LATE_FUND_VALUE | 26 | 14 / 12 | 60.1 / 503.0 | 11.4 h / 30.6 h |
| NEW_FUND_BACKFILL (MSSE) | 13 | 0 / 13 | 0.8 / 14.3 | 835 h / **1,363 h (56.8 d)** |
| TOTAL_RECOMPUTE, SOURCE_CORRECTION, SCHEMA_EXTENSION-only, UNKNOWN_REVISION, LATE_PUBLICATION | 0 | — | — | — |

- **Sign changes:** 2 (BTC 08-11 −42.4 → +7.8; ETH 08-10 +5.3 → −14.6).
- **Zero → value:** 3 (BTC/ETH 09-08 all-dash 0.0 → −46.6 / −24.3; ETH 08-12).
- **Material revisions (|Δ| ≥ 100 M):** 11.
  - All 11 were provisional rows first seen around T+1 02:20–02:45Z, before IBIT/ETHA reported.
  - 3 of them (BTC 08-17, BTC 08-19, ETH 08-19) were still provisional when the settled double-read stored them.
- **Rolling features, first-observed vs latest vintage (W30):**
  - BTC total differs on 14 rows (max 503); 3/5/10/20-session sums differ on 20/26/40/48 rows (max 1,892 M); signed streak differs on 8 rows.
  - ETH total differs on 21 rows (max 210 M); sums differ on 34/39/40/40 rows (max 887 M); signed streak differs on 5 rows.
- **History:** all 1,127 comparable v1 rows equal the 2026-09-23 vintage. No historical restatement was observed except the MSSE column.
- **Pending shape:** an all-`'-'` row with Total `0.0` was accepted as a PASS 0.0 flow (BTC and ETH 09-08 at 05:55Z). Farside uses the same shape for closure days.

**Downstream decisions**
- The Daily Director (SHADOW_CONTEXT_ONLY) consumed the false-final settled rows in 15 contexts and quoted them in 5 outputs. Example: "Settled ETF context is verified for 2026-08-19: BTC 164.2", later 517.2.
- The effect on forecast candidates is not attributable, so it is UNKNOWN.
- The weekly W34 calibration used the corrected values.
- The July Stage-1 flow leg waited correctly for the late IBIT value (07-16).

## 5. #1211 policy experiment

Full table in `ETF_OWNER_DECISION_PACKET_1211.md` §2. Judged against the pre-MSSE vintage:

| Policy | Verdict | Why |
|---|---|---|
| A (session close) | UNSUPPORTED | 26 proven lookahead, 92 unknown, 0 consistent |
| B (first observed) | Vintage time only | 26 later revised (max 24.2 h); drops 1,102 sessions |
| C (first complete, live rule) | SUPPORTED on 104 evidenced sessions | 0 contradictions; drops 1,116 sessions |
| D (settled double-read) | UNSUPPORTED as finality | 4 revised (08-17, 08-19) |
| E (close + 30.6 h) | NOT_ENOUGH_EVIDENCE | 30.6 h is the in-sample maximum completion of 54 daily-cadence sessions: consistent by construction, not validated for history |
| F (next session open) | UNSUPPORTED | 4 proven lookahead |

Against the latest vintage, the MSSE backfill adds 9–13 revisions or lookaheads to every policy. **No fixed lag covers it.**

## 6. Right truncation per policy

The E1X harness was used unchanged. Feature families:
- W30 trailing: total, 1/3/5/10/20 sums, signed streak, acceleration, reversal, concentration
- BTC−ETH divergence
- the pack pandas builder
- W30 with a cumulative-max feature claim (a harness extension)

Each family was run in two modes: truncate, and poison (future values set to 1e6, future revisions removed).

**Attribution rules.** Each minimised mismatch is attributed as one of:
- **PROVEN leakage**: evidence table shows the input was not knowable at the claim.
- **Vintage**: the culprit is a later REVISION of a session.
- **Non-monotone feature claim.**
- **OBSERVATION_LIMITED (UNKNOWN)**: the record is late only because no capture looked earlier.

| Policy | W30 | W30 with cumulative-max claim | Pack builder |
|---|---|---|---|
| A | TRUE_FUTURE_LEAKAGE (proven) | TRUE_FUTURE_LEAKAGE | UNKNOWN |
| B | TRUE_FUTURE_LEAKAGE (non-monotone claim) + vintage | **SOURCE_VINTAGE_RISK only** | SOURCE_VINTAGE_RISK |
| C | TRUE_FUTURE_LEAKAGE (non-monotone claim) | **INSUFFICIENT_HISTORY** (pre-MSSE) / SOURCE_VINTAGE_RISK (latest) | INSUFFICIENT_HISTORY / SOURCE_VINTAGE_RISK |
| D | SOURCE_VINTAGE_RISK | SOURCE_VINTAGE_RISK | SOURCE_VINTAGE_RISK |
| E | Pre-MSSE: UNKNOWN, plus 1 vintage at its own defining boundary (lead 0 s). Latest: SOURCE_VINTAGE_RISK (MSSE) | same | PASS |
| F | SOURCE_VINTAGE_RISK (08-17, 08-19 BTC; plus MSSE on latest) | same | UNKNOWN |

- Poison and truncate agree in every case.
- **Key structural result:** W30 claims each trailing feature at its own row's time. Feature knowledge must be the cumulative max of its inputs' knowledge times (ETF_OBSERVATION_v1 rule 1).

## 7. F04 contamination

- **Structural leak: CONFIRMED.** Every evidenced session was first observed ≥ 6.3 h after its close. 0 of 177 evidenced W30 feature rows were computable at their session-close claim.
- **Stage-1 signal timing** (3 positive BTC sessions with IBIT positive, from July onward): the signal became supportable 10.6 h to 110.8 h after the claimed time. Part of that range is observation-limited.
- **Material performance impact: UNKNOWN.**
  - No recorded backtest decision, forecast, score or outcome consumes W30 ETF features or the pack feature table. The only consumers are the golden-fixture signature replay and E1X.
  - Impact appears only once a strategy consumes them.

## 8. v1.1 revalidation (#1212 only)

- **Malformed rows.** All 11 (9 BTC, 2 ETH) match the frozen recovery rows and the live vintage by ticker: 11/11. Repairing from v1 cells alone is ambiguous (0/11 unique), so the repair must be keyed.
- **Closure rows.** All 26 (16 BTC, 10 ETH, ending 2025-06-19) are zero in v1. The live page shows `'-'` with Total `'0.0'`.
- **Unaffected rows.** 1,127 rows are identical to the live vintage.
- **Checksums.** v1 bytes match `CHECKSUMS` for 3 of 6 partitions. `btc_2025`, `btc_2026` and `eth_2024` drift by 4 bytes per malformed row. v1 was touched by a single commit, `4e2ba082d`.
- **Validator.** The pack's own validator FAILS on the committed bytes, while the README claims 0 null cells.
- **Non-session prototype (W30).** Closures:
  - emit 0.0 flow,
  - reset streaks on all 26 rows,
  - change N-session sums on 238 BTC and 141 ETH session rows,
  - change streaks on 54 BTC and 35 ETH rows.
- **Source export sha256.** Not re-verifiable this session, because the Projects tool returns text, not bytes. Content was verified instead.
- **Verdict: v1.1 still needed.** The packet is consistent with fresh evidence.

## 9. Consumer audit

`ETF_CONSUMER_AUDIT.json`: 21 consumers, 0 changed.

| Classification | Count | Consumers |
|---|---|---|
| BROKEN | 3 | owner parser, settled workflow, phase-4 replay (corrupt 07-06 CSV) |
| SOURCE_VINTAGE_RISK | 8 | owner, settled, `auto_market_state`, `native_handlekompas`, director context, weekly calibration, preflight v3, native OTA readback |
| V1.1_DEPENDENT | 3 | W30, pack builder, pack validator |
| #1211_DEPENDENT | 2 | W30, pack builder |
| SAFE | 2 | absorption experiment (as-of retrieved_at), E1X harness |
| NOT_APPLICABLE | 6 | — |

Assumptions found in the code:
- date row = session
- zero = observed, including all-dash 0.0 rows
- Total exists
- all funds exist (width fallback)
- session close / calendar flag = knowledge and finality
- latest snapshot = historical (weekly rebuilds)

## 10. Minimal shared contract ETF_OBSERVATION_v1

See `ETF_OBSERVATION_v1.schema.json`. It is a record shape that the existing owners emit or map to; it is not a new subsystem.

**Separate fields**
- `session_date`
- `source_observed_at_utc` and its status
- `verification_completed_at_utc`
- `knowledge_available_at_utc` with `knowledge_time_status` (OBSERVED / LOWER_BOUND_ONLY / ASSUMED_BY_OWNER_RULE / UNKNOWN) and the owner rule id
- schema status (KNOWN / KNOWN_ADDITIVE / UNKNOWN → fail closed)
- per-cell status (REPORTED / REPORTED_ZERO / DASH_UNRESOLVED / DASH_STRUCTURAL / ABSENT_COLUMN)
- completeness (… / PENDING_ALL_DASH)
- finality (PROVISIONAL / VERIFIED_STABLE_AT_OBSERVATION / SUPERSEDED; never FINAL)
- revision chain
- `table_content_sha256`

**Rules**
1. Feature knowledge = the cumulative max of its inputs' knowledge times.
2. The calendar is never knowledge.
3. Historical rules never set live finality.
4. Non-sessions and all-dash rows are never counted as sessions and are never 0.0 flows.

## 11. #1211 outcome

**OWNER_DECISION_READY.** See `ETF_OWNER_DECISION_PACKET_1211.md`:
- D1–D7 cover usable timestamp, fallback, UNKNOWN handling, source vintage, backtest eligibility with options a/b/c, feature knowledge, and post-cutoff revisions.
- It also lists the unknown remainder.
- Nothing was implemented.

## 12. Live/historical firewall

- Historical options (D5 a/b) are replay-only.
- `ASSUMED_BY_OWNER_RULE` can never set `finality_status` or feed `daily-settled-etf-calibration`, the LATEST pointer, auto-state or the director.
- Conversely, live verification times are evidence for history only as `OBSERVED` ledger rows; they are never extrapolated into a lag without an owner rule.
- The research prototype's schema registry is live-parser binding only. It does not touch finality.

## 13. Codex owners

See `CODEX_OWNER_PACKET_UPDATES.md`:
- `e9fd7efd` and `d15b736c` are one defect, handled on one branch; still needed. The deadline for the first green run is 2026-10-01 UTC.
- `4a968f5f` is still needed. The packet now covers the checksum-drift readback target, keyed repair, the validator failure and expected deltas.
- `ebaa2306` was correctly RESOLVED.
- No new candidate was submitted: every gap is already owned.

## 14. Safe execution

**Local branch** `agent/task-20260923-etf-temporal-integrity-lab` from `b854dbc31`, delivered as a bundle and patch because push returns 403. It contains:
- `scripts/research/etf_temporal_integrity_lab/` (lab code, read-only against owners)
- `tests/research/test_etf_temporal_integrity_lab.py` (offline)
- `research/etf_temporal_integrity/2026-09-23/` (artifacts; ledger gzipped)

**Not changed:** no production, owner, workflow or consumer file.
