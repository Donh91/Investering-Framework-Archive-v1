# Kompas L04: ETF-flow location increment, prospective preregistration v1

- **Status:** PREREGISTERED. It is frozen by its git blob at the merge commit, before cohort 1 is issued.
- **Owners:** #1596, #1516 and #1827. #1157 adjudicates.
- **Origin:** Research Closure RC04 / KOMPAS-L04 (Sol, run 44551495413).
- **Authority:** research only. There is no production forecast change, official score rewrite, trading, paid call or scheduler. This is not Round 3.

## 1. Question

Does the sign of last week's US spot BTC ETF net flow, known before the week starts, improve the *location* of the existing price-only weekly BTC band? This is one fixed feature with no feature search.

## 2. Units and clocks

- **Cohort w.** One ISO week, Monday 00:00 UTC to Sunday 24:00 UTC.
  - **Cohort 1 is 2026-W48** (2026-11-23 to 2026-11-29).
  - The plan runs **26 eligible cohorts**. That is a design, not a power claim.
- **Cutoff.** Monday 00:00 UTC at the start of week w. No information known after the cutoff may enter cohort w.
- **Target Y_w.** The BTC close of week w in `03_DAILY_CAPTURE_LOGS/weekly/<year>/W<ww>.json`. This is the same spot venue and quote, and the same weekly source, that the price-only band is built from.

## 3. Price-only band (the comparator, unchanged)

- The band is `[L_w, H_w]` = `assets.BTC.low` and `assets.BTC.high` in `05_CYCLE_NAVIGATOR/range_baselines/forecasts/<year>/W<ww>.json`. This is the frozen B1 baseline, issued before the week.
- Its centre is `c_w = (L_w + H_w)/2` and its half-width is `h_w = (H_w − L_w)/2`.
- If the baseline file for week w is missing, or its status is not READY, the cohort is `INELIGIBLE_BASELINE`.

## 4. Feature (fixed before any outcome is seen)

- **Sessions.** The US trading sessions dated Monday through Friday of ISO week w−1.
- **Vintage.** For each session, take the latest capture `03_DAILY_CAPTURE_LOGS/etf/YYYY/MM/DD/HHMMSS_<session_date>.json` that meets three conditions:
  - its capture time, from its path, is before the cutoff;
  - `session_final` is true;
  - the parity check passes.

  Later revisions are ignored.
- **Flow.** `F_w` is the sum of `btc_reported_total_musd` over those sessions.
- **Abstention.** If fewer than 4 sessions are admitted, the cohort is `ABSTAIN_SOURCE`. Abstentions are counted and reported, never dropped.
- **Shift sign.** `s_w = +1` if `F_w ≥ +250`, `−1` if `F_w ≤ −250`, otherwise `0`. Units are USD m. The threshold and the fraction below are fixed now and never tuned.

## 5. Candidate

- **Shifted band.** `c'_w = c_w + s_w · 0.25 · h_w`, with the same width: `[c'_w − h_w, c'_w + h_w]`.
- **Implicit hypothesis.** Net inflows precede higher week-end location, and net outflows lower.

## 6. Metrics, paired per eligible cohort

- **Primary.** `D_w = |Y_w − c_w| − |Y_w − c'_w|`. A positive value means the flow shift helped. Cohorts with `s_w = 0` have `D_w = 0`; they stay in the denominator and their share is reported.
- **Secondary.** Containment of `Y_w` in the shifted band versus the price-only band. Also the Winkler interval score at nominal coverage 0.70, computed for both bands.
- **Context.** `|Y_w − P_w|`, where `P_w` is the last weekly close before the cutoff (persistence).

## 7. Leakage and luck control (block permutation, deterministic)

- For each cohort w, take the flow of one other eligible cohort u. The index is `int(sha256(week_id_w)[:8], 16)` modulo the number of eligible cohorts excluding w, over the final cohort list.
- Apply the identical sign rule to `F_u`, giving `D^perm_w`.
- A real effect must beat this control (§8).

## 8. Decision, once only, after 26 mature eligible cohorts (about 2027-W21)

- **Statistic.** Moving-block bootstrap with block length 4 weeks and 10,000 resamples. The seed is the integer of the first 16 hex characters of this file's sha256.
- **`EDGE_CANDIDATE`** only if both of these hold:
  - the 90% lower bound of mean `D` is greater than 0;
  - the 90% lower bound of mean `(D − D^perm)` is greater than 0.
- **`NO_EDGE`** if the 90% upper bound of mean `D` is below 0.
- **`INSUFFICIENT_EVIDENCE`** otherwise.
- **Interim reports** are allowed, but they are descriptive only and never change the decision.
- **Even `EDGE_CANDIDATE` is not promotion.** It goes to #1157 and needs a separate held-out confirmation.

## 9. Falsifiers and stops

- **Late data.** Any flow captured after the cutoff makes the cohort `INELIGIBLE_LATE_SOURCE`. More than 20% of cohorts ineligible ends the study as `SOURCE_BLOCKED`.
- **Permutation result.** A permuted lift comparable to the real one rejects an edge interpretation.
- **No changes.** No change of threshold, fraction, sessions, band or target after cohort 1 begins. Any change is a new preregistration with new cohorts.
- **No parallel tests.** No second ETF feature and no ETH variant inside this study.

## 10. Implementation note

The scorer is a small deterministic reader over the paths above, written later against synthetic fixtures. It is admitted only if it reproduces this text exactly. No scorer is needed before the first cohort matures (2026-11-29).
