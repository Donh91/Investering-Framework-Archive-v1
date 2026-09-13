# AT-EXP-004 consolidation checkpoint

Date: 2026-09-14
Issue: #941
Canonical implementation owner: PR #947
Donor implementation: PR #948
Fresh-main preflight: `a2de33483ad06ead7f134b0204264592ae0034ea`
Pre-consolidation #947 head: `32d6e7702c67ee85f9ec60c90c2372f1bf7b2d98`
Donor #948 head: `40d79913de72f517d65d2bec77e2808e07a2050f`
Task signature: `fcc1788f4f8ef1d1e330`

## Consolidation decision

PR #947 remains the only implementation owner. Its two production files and three focused tests are carried forward byte-identically from the previously tested head. PR #948 contributes only governed research-summary evidence and additional Situation Room regression assertions that do not introduce its alternative same-attempt PASS-to-DEGRADED exception.

The fresh-main audit confirmed the bounded preconditions remain present on main before consolidation. Main changes since the original implementation base do not modify the two repaired producer/writer files. No weekly, entry-signal, generic intraday, market-rule, model-weight, portfolio, budget, canonical-authority, raw-history or raw-OHLCV semantics are added to scope.

## Preserved semantics

- Missing adjacent previous close does not fabricate a one-hour return.
- Missing price/OI derived inputs produce empty, non-authoritative state.
- Hourly quality is categorical and tied to the affected BTC/ETH derived evidence, not a scalar score.
- Hourly `PASS > DEGRADED`; equal quality keeps the existing stored row because no genuine detection timestamp exists.
- Situation Room `PASS > DEGRADED`; equal quality may replace only on a later valid timezone-aware `detection_time_utc`.
- Rejected downgrades remain auditable and may not mutate canonical dated/interval state or admit rejected Situation Room events.
- Historical damaged rows remain immutable.

## Evidence caveat

`RESEARCH_PACKAGE_v1.json` is a governed summary of the verified evidence recorded in issue #941. It does not claim recovery of the original external AT-EXP-004 package bytes and does not claim that the 867-row census or detector suite was rerun during consolidation. Full #941 closure must not claim original-byte preservation unless that original package is separately recovered and hash-bound.

## Required gate from this commit

Run focused producer -> persistence -> reread regressions, the two-schedule every-bar/every-sixth-bar replay, the Situation Room donor assertions, and relevant repository CI. Do not weaken the live hourly OI source gate and do not fabricate absent OI. If any precondition or owned seam changes, stop and reopen adjudication rather than widening scope.

Even if the PR becomes green, do not reopen AUTO_TRADING alpha research from the PR alone. Merge only the single owner PR, then test/read back the exact merged-main commit, re-evaluate downstream quarantine, publish the existing completion lifecycle receipt, and only then close #941 if every acceptance item is satisfied.
