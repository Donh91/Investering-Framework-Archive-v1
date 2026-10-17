# Task 2 · R1 original Compass issuance case — frozen negative-admission receipt

**Recorded:** 2026-10-14. **Status:** `R1_BLOCKED_NO_LIVE_PIT_ATTESTATION_AND_LEGACY_SCORING_CONTRACT`. **Baseline public control-plane commit:** `c922b47cd81782efca6a64f6042f6cb0fe5efb64`. **Scope:** exact public Git evidence for one originally issued Compass event, NOT a historical predictive-accuracy test or private source first-known proof.

**Machine receipt:** [2026-10-14__TASK2_R1_ORIGINAL_COMPASS_ISSUANCE_CASE_v1.json](2026-10-14__TASK2_R1_ORIGINAL_COMPASS_ISSUANCE_CASE_v1.json). Existing R0/R1 owner: [Task 1.5 #1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596). Does not compete with its census, rewrite its outcomes or change the source admission oracle.

## Immutable public artifact chain

| Object | Git first path-commit/date (UTC) | Git blob SHA | Evidence |
|---|---|---|---|
| Auto market-state source packet | `7c2e493601cb136a82836310341d65e7d3864c5b` · 2026-09-20 15:59:49 | `b2cb5af13a248c3dbd35e93552f091e8d370ab0d` | [Packet at commit](https://github.com/Donh91/Investering-Framework-Archive-v1/blob/7c2e493601cb136a82836310341d65e7d3864c5b/04_MARKET_LEARNING/entry_signals/auto_market_state/runs/2026/09/20/155948_2103d6afeb8d.json) |
| Original official Compass forecast | `3dc7867b12a7bfb9a68068af08d44d1da5121113` · 2026-09-20 16:00:54 | `30b874a9d8967b44ec7b9a7ab11cb0d27c9b193f` | [Forecast at commit](https://github.com/Donh91/Investering-Framework-Archive-v1/blob/3dc7867b12a7bfb9a68068af08d44d1da5121113/04_MARKET_LEARNING/handlekompas/official/daily/2026/09/20/CMP-20260920-02425db96215.json) |
| 12-hour original legacy outcome | `61f81dcfffb9c7c2f271e1524d5bcdda6c516781` · 2026-09-21 06:44:38 | `4c1028fdb859a09a60fe9334c97faa94eed224f5` | [Outcome at commit](https://github.com/Donh91/Investering-Framework-Archive-v1/blob/61f81dcfffb9c7c2f271e1524d5bcdda6c516781/04_MARKET_LEARNING/handlekompas/official/outcomes/2026/09/20/CMP-20260920-02425db96215_12h.json) |

### Checks actually performed (public Git readback)

1. Source packet was declared generated at **15:59:48Z** and its first path-commit was recorded at **15:59:49Z**, **65 seconds before** the forecast's first path-commit and declared issue time **16:00:54Z**.
2. The forecast's exact source path and declared packet SHA-256 `2103d6afeb8d77786abc2ac16f54bea1d13793a5bf47878f0616e013f0de5cb4` agree with the retrieved packet's metadata. This intake did NOT independently recompute provider/raw SHA-256 values.
3. The outcome's original forecast path, `compass_id`, issued clock, and declared `compass_sha256` match the retrieved frozen forecast.
4. The outcome's nominal `target_at_utc` is **2026-09-21T04:00:54Z** but `target_observation_at_utc` is **2026-09-21T05:00:00Z**, or **3,546 seconds / 59m06s later**. It is an original **`OFFICIAL_DAILY_COMPASS_SCORING_v1`** outcome, not a valid substitute for later v3 target-clock semantics.
5. The original outcome explicitly records **BTC: ABSTAINED; ETH: ABSTAINED**. Neither may be represented as a directional HIT or MISS. The outcome was recorded after the target, and the first path-commit appeared the next morning. That is valid *temporal order* of archival events only, not an admitted source/vintage or matched performance study.

### What this does *not* prove

Git author/committer timestamps and a file's earliest commit in accessible path history are not **independently attested external publication clocks**. The packet was committed first, but its upstream provider's true first-known/publication time, revisions, schema era and permitted investor-visible decision time remain unverified. In particular, a source packet's internal `validation_status=PASS` does not independently certify upstream first-knowledge. There is also no owner-approved evidence mapping this legacy v1 outcome observation to a strict same-target, no-lookahead v3 scoring contract.

**Scientific classification:** `PUBLIC_GIT_LINEAGE_MATCH_PASS`; `SOURCE_PIT_BLOCKED`; `LEGACY_TARGET_CLOCK_OFFSET_QUARANTINED`; `DIRECTIONAL_DENOMINATOR_ABSTENTION`. **R1-admitted directional skill rows = 0; independently scored historical rows by this case = 0; economic action-edge episodes = 0**. One matched lineage is not an independent shock family.

### Explicit next owner work

- Bind source-contract and provider-first-known proof for the original market packet, separately from Git timestamps; keep any restricted proof inside the private data plane.
- Verify original signal publication and investor delivery, preserving abstention as a **complete attempted forecast state**.
- Preserve frozen legacy v1 outcome; do **not** rewrite its 05:00 observation into 04:00:54 or silently reclassify CENSORED/ABSTAINED as matured directional.
- Select a **different** original, clock-aligned scoring-contract-v3 forecast and original outcome for the next candidate R1 cohort; it must have independently verified first-known provenance and complete attempt denominator before any R2 simple-baseline test.

No market rules, live signals, private provider values, new workflows, paid source acquisition, scores or user portfolio actions changed.
