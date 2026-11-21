# Kompas L04 preregistration, addendum A1: baseline and anchor clocks

- **Status:** PREREGISTERED. It is frozen by its git blob at its merge commit. It takes effect only if that merge commit is on main **before 2026-11-23T00:00:00Z** (the cohort 1 cutoff). If it lands later, it applies from the first cohort whose cutoff follows the merge, and 2026-W48 is not admitted under it retroactively.
- **Amends:** `2026-11-19__KOMPAS_L04_ETF_FLOW_LOCATION_PREREGISTRATION_v1.md` (blob 7a285ff2d275d442113e053989ba36d25bff6a64). v1 is not edited, so the §8 seed (from v1's sha256) is unchanged.
- **Owners:** #1596, #1516 and #1827. #1157 adjudicates.
- **Authority:** research only. Nothing in v1 §1 and §3–§10 changes: question, band definition, feature, threshold, fraction, sessions, target, metrics, permutation, decision rule and stops.

## Why

v1 §2 says that no information known after the cutoff (Monday 00:00 UTC) may enter cohort w. v1 §3 takes the band from the frozen B1 file "issued before the week".

B1 is published by the weekly Cycle Navigator package job on Monday morning, after the cutoff: W45 at 08:19Z, W46 at 10:33Z, W47 at 08:35Z. The weekly anchor pack it is built from is also generated Monday morning. Read as a publication-time rule, every cohort would be ineligible.

B1 is deterministic. `scripts/cycle_navigator/deterministic_range_baseline.py` `build_baseline` takes no clock input, and it reads only the weekly packs of the weeks before w. Its content can therefore carry no information from after the cutoff. This addendum states the rule as a data as-of rule with an availability bound.

## A1.1 Clock rule for B1 and the anchor pack (replaces the reading of "issued before the week")

Cohort w uses the B1 file `05_CYCLE_NAVIGATOR/range_baselines/forecasts/<year>/W<ww>.json` only if **all** of these hold. Otherwise the cohort is `INELIGIBLE_BASELINE`.

1. `status` is `READY`, `target_iso_year`/`target_iso_week` equal w, `expected_anchor_iso_year`/`expected_anchor_iso_week` equal w−1, and `anchor_contiguous` is true.
2. `source_weeks` ends with w−1 and contains no week ≥ w.
3. **As-of bound.** The anchor weekly pack `03_DAILY_CAPTURE_LOGS/weekly/<year>/W<w−1>.json` has `hourly_sequence.last_hour_utc` ≤ the cutoff minus 1 hour (Sunday 23:00:00Z). The same bound holds for every source week.
4. **Availability bound.** The commit that first adds the B1 file for week w to main has a committer time before Tuesday 00:00:00Z of week w (cutoff + 24 h). The file is never modified afterwards on main. A later change of its bytes makes the cohort `INELIGIBLE_BASELINE`.
5. **Reproducibility.** Running `build_baseline(repo, target_year, target_week=w)` on the tree of the commit from point 4 gives exactly the file's `baseline_sha256`. This proves that the band depends only on the pinned source packs.

`P_w` (v1 §6 context) is read from the same anchor pack under the same as-of bound.

## A1.2 What does not change

- The ETF feature keeps its strict capture-time vintage rule (v1 §4): a flow capture after the cutoff never enters cohort w.
- `INELIGIBLE_LATE_SOURCE` and the 20% `SOURCE_BLOCKED` stop (v1 §9) apply to the ETF feature as before. A1.1 failures are counted as `INELIGIBLE_BASELINE` and are reported. They count towards the same 20% stop.
- Cohort 1 is still 2026-W48 when this addendum is on main before its cutoff. The decision time, the 26 eligible cohorts and the seed are unchanged.

## A1.3 Scorer note

The future scorer (v1 §10) implements A1.1 points 1–5 as checks. It needs fixtures for each one: a READY file, a wrong week, a source week ≥ w, a last_hour after the cutoff, a first commit at or after Tuesday 00:00Z, a later modification, and a baseline_sha256 mismatch.
