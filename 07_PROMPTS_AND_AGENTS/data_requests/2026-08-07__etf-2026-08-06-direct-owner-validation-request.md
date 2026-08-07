# TARGETED ETF DIRECT-OWNER VALIDATION — 2026-08-06

```yaml
request_id: DP-ETF-DIRECT-OWNER-20260807-02
target_session: 2026-08-06
owner: DATA_PING_CUSTOM_GPT
framework_interpretation: DEFERRED_TO_MAIN_FRAMEWORK
priority: P1_DECISION_RELEVANT_FLOW_VALIDATION
```

## Objective

Validate the 2026-08-06 BTC and ETH Farside rows to the same owner-grade standard used by `DP-ETF-DIRECT-OWNER-20260806-01`.

Earlier main-thread web candidates observed after publication were:

- BTC `+137.6M USD`
- ETH `+92.1M USD`

These are expectations for conflict detection only. Do not fit to them and do not accept a row merely because it matches.

A separate interrupted DATA PING at approximately 2026-08-06T23:15Z observed a **partial-publication** BTC row with displayed Total `29.2M` while 8 of 12 fund cells were still dashes/unknown. That row is quarantined and is not an owner candidate. It proves that displayed Total tie-out alone is insufficient for finality.

## Required procedure

1. Retrieve the canonical Farside Bitcoin all-data page directly.
2. Retrieve the canonical Farside Ethereum all-data page directly.
3. Select exactly `06 Aug 2026` by displayed session identity.
4. Capture every displayed fund/issuer cell and the displayed Total.
5. Preserve zeros, negatives and dashes distinctly.
6. **Owner nomination MUST be `NO` if any target fund/issuer cell is dash/unknown, even when the displayed Total equals the sum of currently numeric cells. Zero dashes/unknowns is mandatory for owner finality.**
7. Locally sum all numeric fund cells and require exact tie-out to displayed Total.
8. Repeat both canonical page retrievals at least 60 seconds later.
9. Require normalized target rows to be identical across the two retrievals, or report any revision explicitly.
10. Record exact retrieval-completion timestamps UTC.
11. Record page/footer date or equivalent generation-freshness evidence.
12. Compute and retain:
   - argument SHA-256 for each invocation,
   - payload SHA-256 for each successful page retrieval,
   - normalized target-row SHA-256 for each retrieval,
   - final packet SHA-256.
13. Freeze only after final source response; record freeze UTC and require zero post-freeze calls.
14. Preserve one-to-one invocation/receipt bijection.
15. Do not use an issuer cell as Total; resolve column identity from the current displayed header, not a fixed legacy position.
16. Do not infer missing cells and do not convert dashes to zero.
17. Treat a previously observed incomplete row as publication-lifecycle evidence, not as a revision candidate, unless a complete owner-grade retrieval independently reproduces it.

## Cross-asset output after owner validation

Only if BOTH BTC and ETH rows pass owner validation, recompute synchronized owner-ledger rolling sums through 2026-08-06 for exactly 3, 5 and 7 US trading sessions.

Return the exact constituent session dates and values for each sum so the main thread can reproduce them independently.

Do not AUM-normalize unless validated denominators are independently available. If denominators remain unavailable, return `AUM_NORMALIZATION_BLOCKED`.

## Mandatory conflict handling

If any complete owner-grade retrieval disagrees with the current candidate values (`BTC 137.6`, `ETH 92.1`), report the observed rows and revision evidence and stop owner nomination until the conflict is resolved.

If the two retrievals disagree, classify the row `REVISING_NOT_FINAL_FOR_OWNER_LEDGER`.

If either target row contains one or more dashes/unknown issuer cells, classify it `PARTIAL_PUBLICATION_NOT_FINAL_FOR_OWNER_LEDGER` regardless of displayed-total tie-out.

## Required reconciliation package

Return:

```json
{
  "request_id": "DP-ETF-DIRECT-OWNER-20260807-02",
  "framework_interpretation": "DEFERRED_TO_MAIN_FRAMEWORK",
  "session": "2026-08-06",
  "BTC": {
    "issuer_rows": [],
    "displayed_total_usd_m": null,
    "local_tieout_usd_m": null,
    "dash_unknown_count": null,
    "retrieval_1_utc": null,
    "retrieval_2_utc": null,
    "row_sha256_1": null,
    "row_sha256_2": null,
    "payload_sha256_1": null,
    "payload_sha256_2": null,
    "arguments_sha256": null,
    "owner_nomination": "YES|NO"
  },
  "ETH": {
    "issuer_rows": [],
    "displayed_total_usd_m": null,
    "local_tieout_usd_m": null,
    "dash_unknown_count": null,
    "retrieval_1_utc": null,
    "retrieval_2_utc": null,
    "row_sha256_1": null,
    "row_sha256_2": null,
    "payload_sha256_1": null,
    "payload_sha256_2": null,
    "arguments_sha256": null,
    "owner_nomination": "YES|NO"
  },
  "synchronized_rolling_sums_if_both_owner_grade": {
    "BTC_3_session": null,
    "BTC_5_session": null,
    "BTC_7_session": null,
    "ETH_3_session": null,
    "ETH_5_session": null,
    "ETH_7_session": null,
    "constituent_rows": []
  },
  "freeze_recorded_at_utc": null,
  "post_freeze_source_calls": 0,
  "packet_sha256": null,
  "canonical_effect_claimed": "NONE",
  "portfolio_effect_claimed": "NONE",
  "requires_main_thread_crosscheck": "YES"
}
```

## Stop condition

Stop when both 2026-08-06 rows are owner-grade validated or when a specific unresolved revision/source conflict/partial-publication state prevents owner nomination. Do not broaden into market interpretation or additional research.
