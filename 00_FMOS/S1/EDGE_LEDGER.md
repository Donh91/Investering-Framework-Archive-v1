S1 EDGE LEDGER v1.0 (rubric of 00_FMOS/S1/ACTION_LOOP.md binding B7 and rule 6(b); pinned by rubric_blobs in 00_FMOS/S1/RUNTIME_CONTRACT.json; AGENTS.md section 0.2g)

PURPOSE
Research improves only when evidence adds up. EDGE_LEDGER_v1 is one append-only weekly ledger per research stream: a frozen question, an identical-clock baseline, evidence that multiplies week by week, and a mechanical decision. Every stream ends: it is promoted, killed, parked or closed as inconclusive. Nothing is decided on hindsight, and S1 never states that an edge exists before the ledger says so. S1 does not score outcomes itself: the deterministic scorer on main does, in CI. S1 checks the bindings below and applies the DECISION TABLE to the scorer's summary row.

SCOPE AND FIREWALL
- A stream is a directory 06_RESEARCH_LAB/edge_ledger_v1/streams/<stream_id>/ on main. The scorer writes 06_RESEARCH_LAB/edge_ledger_v1/LEDGER.jsonl (one row per stream and week) and 06_RESEARCH_LAB/edge_ledger_v1/LEDGER_SUMMARY.json (one object per stream, the fields of E3). While that summary file does not exist on main this rubric has no candidate, and the open-work index reads edge=ABSENT. This release ships the rules only: the ledger directory and its scorer arrive by their own reviewed PRs.
- No stream reads Round 3 data. Every preregistration lists each data path it reads in data_paths; one that names a Round 3 path or any private-plane path, or that lists none, is INVALID_PREREG. This file changes no Round 3 rule.
- A decision here is research evidence. It never changes a live product, a site page or a trading setting: a promotion that touches the site or a producer is its own PR and follows every gate of ACTION_LOOP.md (site and producer paths stay OWNER_GATED or HIGH).

GATES (machine-readable; tests/governance/test_s1_edge_ledger_v1.py reads this block and holds the reference model)
```json
{"contract": "S1_EDGE_LEDGER_GATES_v1",
 "ledger_dir": "06_RESEARCH_LAB/edge_ledger_v1",
 "summary_file": "LEDGER_SUMMARY.json",
 "prereg_required_fields": ["stream_id", "hypothesis", "forecaster_ref", "scorer_ref", "baselines", "data_paths", "outcome", "loss",
                            "unit", "clip_c", "MDE", "n_min", "n_max", "family_id", "family_k_max", "bootstrap", "kill_rules",
                            "readiness_checks", "first_week"],
 "n_min": 8,
 "n_max": 26,
 "alpha_family": 0.05,
 "harm_e": 20,
 "lambda_max": 0.5,
 "confirm_weeks": 4,
 "park_readiness_fail_share": 0.25,
 "futility_ci": 0.9,
 "mde_min_share_of_clip": 0.01,
 "max_parked_weeks": 8,
 "decisions": ["INVALID_PREREG", "PARKED", "KILLED_HARM", "KILLED_FUTILITY", "PROMOTED", "PROMOTE_CANDIDATE",
               "CLOSED_INCONCLUSIVE", "ACCUMULATE"],
 "final_decisions": ["INVALID_PREREG", "KILLED_HARM", "KILLED_FUTILITY", "PROMOTED", "CLOSED_INCONCLUSIVE"],
 "streams_per_run": 3}
```
A preregistration may tighten a gate (a higher n_min, a lower n_max, a larger MDE, a lower harm bound) and never loosen one: S1 uses the stricter of the two values.

E1 PREREGISTRATION ON MAIN BEFORE THE WINDOW
- One file per version: streams/<stream_id>/PREREG_v<k>.json with every field of prereg_required_fields. forecaster_ref, scorer_ref and every baseline name a script path and its blob. bootstrap fixes the block length, the number of replicates and the seed behind ci_upper.
- FLOORS: clip_c is above 0 and MDE is at least mde_min_share_of_clip times clip_c; otherwise INVALID_PREREG. A stream cannot define its own success away.
- FAMILY CAP: the first preregistration of a family fixes family_k_max, the largest number of confirmatory streams the family will ever hold, and every later member repeats the same value. S1 counts the stream directories on main that name the family_id: more members than family_k_max, or a member with another value, is INVALID_PREREG (reason family_cap) for the newcomer.
- BEFORE THE WINDOW: the PR that added the file was merged to main before first_week's Monday 00:00 UTC. The clock is the native merged_at of that PR and the file's first commit on main's first-parent history; a commit's own author or committer date is never the clock.
- FROZEN: a later commit on main that changes an existing PREREG_v<k>.json blob makes the stream INVALID_PREREG. An amendment is a new file PREREG_v<k+1>.json; it applies only to weeks that start after its own merged_at.
- AN AMENDMENT ONLY TIGHTENS: against v<k> it may raise MDE or n_min, lower n_max or the harm bound, add a baseline or a readiness check, and nothing else. A changed hypothesis, outcome, loss, unit, clip_c, forecaster_ref, scorer_ref, family or bootstrap, or a removed baseline, is a new stream with a new stream_id and an e-process that starts at 1.
- Weeks used to choose the estimator (selection-exposed weeks) are never counted, whatever the file says.
- NO RERUN: a new stream whose hypothesis and forecaster_ref equal those of a stream with a final decision of KILLED_HARM, KILLED_FUTILITY or CLOSED_INCONCLUSIVE is INVALID_PREREG (reason rerun_of_killed). An INVALID_PREREG stream that has no scored week in LEDGER.jsonl never held evidence, so correcting its preregistration under a new stream_id is allowed; one that was scored before it became invalid (a preregistration edited later, a firewall breach) is banned like a killed one. A stream cannot escape a kill by being parked, closed or amended and then registered again.
- RATCHET: when a stream on the same outcome is PROMOTED, every later preregistration for that outcome lists it in baselines; otherwise INVALID_PREREG (reason baseline_ratchet).

E2 IDENTICAL-CLOCK BASELINE
- For every issuance the model and ALL baselines are computed in the same job run from the same as-of snapshot, and written as one frozen row with one issue_clock, one snapshot id and one run id.
- A baseline computed later, in another run or from another snapshot is not admissible: that week is a readiness failure for the stream. S1 never repairs a row; a missing or inadmissible row stays missing.
- For the evidence process E_t the bar is the BEST baseline of the week on the stream's loss, not a chosen one (the hardest bar for an edge claim). For the harm process E'_t the bar is the baseline with the best cumulative loss up to the PREVIOUS week, so that picking the weekly winner after the fact cannot manufacture harm.

E3 WEEKLY EVIDENCE (an anytime-valid e-process, so a weekly look costs no error)
- Unit: one ISO week. d_w = mean over the week's units of (loss of the best baseline - loss of the model), clipped to [-clip_c, clip_c]. Positive means the model is better. H0: the expected d is at most 0.
- E_t = product over weeks of (1 + lambda_w * d_w / clip_c), with lambda_w in [0, lambda_max] chosen from EARLIER weeks only. A lambda that depends on its own week's outcome makes the row inadmissible.
- The reverse process E'_t uses the negated difference against its own bar (E2) with the same rule. It measures harm.
- LEDGER.jsonl is append-only: a PR that changes or removes an existing row is not a ledger PR, and S1 treats the stream as PARKED (reason ledger_rewritten) until the Research Lab answers.
- Each weekly ledger PR is a normal PR: it needs the B4 CI tuples, an independent exact-head review (REVIEW_ADMISSION.md) and the lane's gates. Its summary object per stream in LEDGER_SUMMARY.json holds: n (valid weeks), e_value, e_reverse, mean_d, ci_upper (the upper bound of the futility_ci block-bootstrap interval of mean_d, with the preregistered bootstrap), readiness_fail_share and the week it covers. weeks_since_candidate and candidate_held are NOT scorer fields: S1 derives them from its own S1_EDGE_DECISION_v1 posts on #1512. weeks_since_candidate is the number of posts for a NEW VALID WEEK (n exactly one higher than in the previous post) since the first PROMOTE_CANDIDATE post of the current candidacy; a calendar week with no new valid row adds nothing. candidate_held is true only when every one of those posts quoted mean_d at or above MDE and a readiness_fail_share no higher than in the post before it.
- Never report a p-value from overlapping windows, and never restate E_t as a probability.

E4 DECISION TABLE (first matching row wins; S1 quotes the inputs it used)
1. INVALID_PREREG: E1 fails, or the firewall is breached.
2. PARKED: readiness_fail_share is above park_readiness_fail_share, or the data source is not point-in-time admissible, or the ledger was rewritten. The clock stops and no evidence is lost. A parked stream returns to ACCUMULATE when its readiness is repaired by a reviewed PR. A stream that is parked, or that gets no new ledger row, for more than max_parked_weeks consecutive weeks is CLOSED_INCONCLUSIVE instead: no stream waits forever.
3. KILLED_HARM: e_reverse is at or above harm_e. S1 changes nothing that is shown anywhere: replacing the model by the baseline on a product surface is its own gated PR (SCOPE AND FIREWALL), which the daily summary lists for the owner.
4. KILLED_FUTILITY: n is at or above n_min and ci_upper is below MDE. The stream is logged and never rerun.
5. PROMOTED: the stream's previous decision is PROMOTE_CANDIDATE, weeks_since_candidate is at or above confirm_weeks, candidate_held is true, and an independent exact-head review of the scorer run exists. It becomes a baseline (E1 RATCHET).
6. PROMOTE_CANDIDATE: e_value is at or above family_k_max / alpha_family, mean_d is at or above MDE, n is at or above n_min and below n_max + confirm_weeks, and an independent exact-head review of the scorer run exists. A candidate that stops holding falls back to ACCUMULATE, and its e-process continues; a later candidacy starts its confirmation weeks again.
7. CLOSED_INCONCLUSIVE: n is at or above n_max with no decision above. A candidate may finish its confirmation weeks past n_max, so every stream has a final decision by n_max + confirm_weeks valid weeks at the latest.
8. ACCUMULATE: otherwise.
- family_k_max is the family cap of E1, never less than 1. Because every member of the family uses the same cap from the start, the threshold family_k_max / alpha_family is the Bonferroni bound for e-values over the whole family, valid under any dependence and however many members have already ended.
- A final decision (final_decisions) is final: S1 never reopens it. A new question is a new stream with a new preregistration.

E5 WHAT S1 DOES (rule 6(b), first in its order; at most streams_per_run streams per run; no new schedule)
- Once per ISO week per stream, after the weekly ledger PR is on main: check E1 and E2 from native reads, read the stream's object in 06_RESEARCH_LAB/edge_ledger_v1/LEDGER_SUMMARY.json at M, apply E4, and post one S1_EDGE_DECISION_v1 on #1512: stream / week / decision / the inputs (n, e_value, e_reverse, mean_d, ci_upper, MDE, family_k_max, readiness_fail_share, weeks_since_candidate, candidate_held) / prereg blob and its merged_at / summary blob at M / contract=<8>. Never post a second decision for the same stream and week.
- A RESEARCH work item that claims an effect, an improvement or an edge names its stream_id. Without a stream that passes E1 the item cannot enter REVIEW as a conclusion: S1 sends one S1_RESEARCH_HANDOFF_v1 asking for the preregistration (reason needs_prereg), under the budgets of STEWARD_STATES.md.
- A preregistration or amendment PR is merged only through the lane, with an independent review, and only before the window it claims: one that would merge after its first_week's Monday 00:00 UTC is skipped as skipped=<PR>:E1:window_started, and the stream starts in a later week by a new version.
- A PROMOTED, KILLED_HARM, KILLED_FUTILITY or CLOSED_INCONCLUSIVE decision is listed in the daily summary. Promotion to a product surface is the owner-visible PR named in SCOPE AND FIREWALL.
- When a summary row or a required field cannot be read, the decision is not made: the index reads edge=<stream>:UNREADABLE and S1 guesses nothing.
