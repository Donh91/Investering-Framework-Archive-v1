# Codex owner packet updates — ETF (2026-09-23)

**Scope and constraints**
- No active Codex owner was implemented. No new candidate was submitted, because every gap already has an owner.
- CODEX_READY is not self-declared.
- The updates below strengthen the existing packets with fresh-main evidence (`b854dbc31`, live read 15:29Z).

**Summary**

| Task | Status | Still needed? | Duplicate of |
|---|---|---|---|
| `e9fd7efdc36e5c119072` daily-settled-etf LATEST_RUN_FAILED | CODEX_READY | **YES** | Same defect as `d15b736c` |
| `d15b736c1a1d967ca3e1` daily-settled-etf REPEATED_CONSECUTIVE_FAILURES | CODEX_READY | **YES** (clears with the same fix) | Same defect as `e9fd7efd` |
| `4a968f5f8577265ab5fd` / `codex-research-etf-history-pack-v1-1-row-integrity-v1` (#1212, E1X D01) | CODEX_READY | **YES** | none |
| `ebaa23067c15f9617f44` / `codex-research-audit-etf-adapter-v1` | RESOLVED | no, correctly closed | — |
| #1211 / E1X F04 | owner issue | Owner decision (packet `ETF_OWNER_DECISION_PACKET_1211.md`), **not Codex** | — |

**Dedupe.** `e9fd7efd` and `d15b736c` are two health signatures for one root cause: ETH `HEADER_NOT_FOUND`.
- Execute them as **one branch**.
- Each closes separately through its own `3_SUCCESSFUL_EXPECTED_RUNS` post-fix gate.
- A second implementation must not be opened for `d15b736c`.

---

## 1. `e9fd7efd` / `d15b736c` — daily-settled-etf-calibration (live settled owner)

### 1.1 Corrected root cause: two source changes, not one

Between 2026-09-17T11:35Z (the last good settled capture) and the first failing run on 2026-09-18, Farside changed the ETH table in two ways:

1. **Column added.** MSSE (Morgan Stanley) was inserted between EZET and ETHE, making 11 funds. It has values from 2026-07-27; 41 rows are non-blank and 14 non-zero.
2. **Layout changed.**
   - The issuer-name `<th>` row is gone.
   - The ticker row is now `['', ETHA, …, MSSE, ETHE, ETH, 'Total']`, followed by a `<th>` Fee row.
   - The owner's `SOURCE_TWO_ROW_TICKER_HEADER` path expects `issuer row ending in Total → ticker row`, so it can no longer match. That was the mode of every stored v4 ETH snapshot from 2026-08-10 to 2026-09-15.

Additional facts:
- BTC is unchanged: `DIRECT_DATE_TOTAL`.
- All 555 ETH date rows have 13 cells. All reconcile to Total when MSSE is included, and 10 fail without it.
- The fixture `ISOLATE_LAYOUT_ONLY_NEW_LAYOUT_10F` shows the layout change on its own is not what fails today: production binds it through the width fallback.

### 1.2 The "smallest change" (add MSSE to `CANONICAL_FUND_HEADERS['ETH']`) is unsafe on its own

It makes the live page pass only through `CANONICAL_ASSET_SCHEMA_EXACT_WIDTH_FALLBACK`, which binds columns **by width, not by name**. In the fixture matrix (`ETF_LIVE_SCHEMA_REPRODUCTION.json`, 16 fixtures × 3 variants) it accepts 5 negative fixtures:

| Negative fixture | Add-MSSE result |
|---|---|
| Header last cell not "Total" | accepted |
| No header row at all | accepted |
| MSSE replaced by unregistered same-width ticker | **SILENT_MISLABEL** (25/25 rows) |
| ETHE/ETH columns swapped in source | **SILENT_MISLABEL** (18/25 rows; parity still passes) |
| Duplicate ticker | accepted |

It also breaks `tests/architecture/test_full_architecture_1to7.py::test_farside_fixture_parser`, whose ETH fixture is the old issuer + ticker 10-fund layout.
- That fixture must be **replaced** by the current real layout.
- It must not be deleted or loosened.

### 1.3 Proposed repair: stays inside the allowed scope, changes no finality semantics

A research prototype (`STRICT_REGISTRY_PROTOTYPE` in `live_schema_lab.py`) passes all 16 fixtures:
- live BTC/ETH and recent history are accepted with a mapping identical to the source,
- all 9 negatives fail closed.

It does four things:
1. Binds columns only from the published ticker row: a unique row, first cell blank or "Date", last cell "Total". The issuer-row + ticker-row form is still supported.
2. Keeps a per-asset **schema registry**. Exact match gives `KNOWN_SCHEMA`. `FARSIDE_ETH_v2_11F_MSSE` is registered as `KNOWN_ADDITIVE_SCHEMA_REVISION` (added: MSSE).
3. Fails closed on anything else: `UNKNOWN_SCHEMA_REVISION`, `UNKNOWN_SCHEMA_REVISION:REORDERED`, `DUPLICATE_TICKER`, `HEADER_AMBIGUOUS`.
4. Removes the width-only fallback from the live path, or restricts it to explicitly named test fixtures.

Keep `header_mode` / `schema_id` in the snapshot. Also record it in the settled capture, which currently drops it.

**Acceptance tests to add** (all offline, fixtures from `live_schema_lab.py`):
- Live ETH layout is accepted with `schema_id=FARSIDE_ETH_v2_11F_MSSE`.
- The old two-row 10-fund layout is accepted as `FARSIDE_ETH_v1_10F`.
- BTC is unchanged.
- Negatives fail closed: no Total label, no header, same-width unknown ticker, reordered ETH, reordered BTC, duplicate ticker, missing Total column, one row missing its Total cell.
- Parity and finality asserts in the workflow stay byte-identical.

### 1.4 Deadline

- The owner keeps only the last 10 sessions (`--history-limit 10`).
- Session 2026-09-17 leaves that window with the first retrieval dated 2026-10-02.
- **The first successful settled run must happen no later than 2026-10-01 UTC.** Otherwise the settled captures for 09-17 onward (09-17, 09-18, 09-21, …) are lost for good.
- As of the live read, the first fixed run would write:
  - new sessions 09-17, 09-18, 09-21 and 09-22, plus whatever has accrued since;
  - new-signature files for 09-09 → 09-16, because `fund_headers` gains MSSE. Only ETH 09-15 changes its total (−142.3 → −142.0).

### 1.5 Owner-gated items: not for Codex, listed so they are not mixed in

These are finality semantics and route to the #1211 owner. Codex must neither strengthen nor weaken them without owner authority.
- Rows with unresolved `'-'` cells are accepted when parity holds. Seven settled rows were stored like this. Four were revised later (08-17/08-19, up to +353 M USD).
- An all-`'-'` row with Total `0.0` passes every assert as a 0.0 flow. This was observed for 2026-09-08 at 05:55Z. It is the same shape Farside uses for closure days.
- `session_final=True` is a calendar flag set for every row dated before the UTC retrieval date. It is not observed finality.
- Revision labelling for the six re-signatured sessions.

---

## 2. `4a968f5f` — history pack v1.1 (#1212, E1X D01)

Revalidated against fresh main and the independent 2026-09-23 live vintage (`ETF_V1_1_REVALIDATION.json`). **Still needed.** The packet is consistent with fresh evidence. Add:

1. **Frozen rows confirmed.** All 11 malformed rows (9 BTC, 2 ETH) have `recovery_evidence` values equal to the live table **by ticker**: 11/11 totals and 11/11 fund vectors.
2. **Repair must be keyed.** The repair must map by fund name, from the export JSON keys or the live ticker header. Repairing from the one-cell-short v1 cells is ambiguous: 0 of 11 rows have a unique dropped position, because zero columns are interchangeable. Add a negative test for this.
3. **v1 readback target.** Current v1 bytes do **not** match the pack's own `CHECKSUMS.sha256` / manifest for 3 partitions:
   - `btc_2025`, `btc_2026`, `eth_2024`: 4 bytes short per malformed row.
   - The other 3 partitions match.
   - "v1 byte-identical" must therefore be checked against **main's current bytes** (sha256 in the revalidation JSON), not against `CHECKSUMS.sha256`, which would fail before any change.
4. **Validator.** The pack's own validator fails on the committed bytes (`FAIL: btc: null cell`), although the README says "0 null cells". Nothing runs it in CI.
   - v1.1 tests should run the validator on v1.1.
   - v1's README must not be edited.
5. **Closure rows.** There are 26 (16 BTC 2024-01-15 → 2025-06-19, 10 ETH).
   - They are all-zero in v1.
   - On the live page they are every fund `'-'` with Total `'0.0'`.
   - Farside lists no closure rows after 2025-06-19.
6. **Expected regression deltas** for "closures are not sessions" (production W30 `build_etf_trailing`):

   | Asset | N-session sums change on | Signed streak changes on |
   |---|---|---|
   | BTC | 238 session rows | 54 rows |
   | ETH | 141 session rows | 35 rows |

   All 26 closure rows currently reset the streak and emit 0.0 flow.
7. **Source export hashes.** They could not be re-verified in this session: the Projects tool returns extracted text, not bytes. Content equality with the live vintage (1,127/1,127 comparable rows) stands in for them. Keep the recorded hashes as the binding.
8. **Keep separate from #1211.** v1.1 must not add `knowledge_available_at` or change `AVAILABLE_AFTER_US_SESSION_CLOSE`. That belongs to the owner decision.

---

## 3. Research candidates not submitted (gaps already owned)

| Gap | Owner that absorbs it |
|---|---|
| Width-fallback mislabel risk | `e9fd7efd` packet (§1.3) |
| All-dash 0.0 rows, unresolved-cell finality | #1211 owner decision (D1/D2) |
| W30 feature claim not cumulative-max | #1211 owner decision (D6); W30 semantics change needs owner authority |
| Pack validator not in CI / checksum drift | `4a968f5f` packet (§2.3–2.4) |
| Director consumed false-final settled rows | #1211 D1 (consumer audit: SOURCE_VINTAGE_RISK; consumers not changed) |
