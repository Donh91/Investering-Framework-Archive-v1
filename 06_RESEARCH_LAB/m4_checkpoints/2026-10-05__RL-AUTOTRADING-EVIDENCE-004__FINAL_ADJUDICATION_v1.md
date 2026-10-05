# M4 Final Research Lab Adjudication v1

**Mission:** `RL-AUTOTRADING-EVIDENCE-004`  
**Date:** 2026-10-05  
**Adjudicator:** ChatGPT 5.6 Sol High  
**Status:** FINAL_RESEARCH_ADJUDICATION  
**Authority:** RESEARCH_ONLY / NO_EXECUTION / NO_PORTFOLIO_EFFECT  
**Framework head read at adjudication:** `0820347ff07000a353e1f2a7f6d90f8c9801dc0c`

## Final verdict

**Evidence machine:** `PARTIALLY_READY`

**Broad autonomous hypothesis search:** `NOT_READY`

**New economic hypothesis admission on the evidence supplied to M4:** `BUILD_NOTHING`

**Existing bounded research infrastructure:** `KEEP_AND_USE`

The framework has demonstrated that it can:
- reconcile a major historical data source;
- detect planted and real leakage;
- repair a real persistence defect prospectively;
- preserve failed, blocked and method-invalid trials;
- preregister a bounded test;
- produce an independent negative result without promoting it.

That is substantial progress.

But M4 does not establish that any *new* existing hypothesis currently has the complete candidate-specific package required to consume a scarce forward slot.

## What is now verified

### AT-EXP-004 is closed

Issue #941 is closed as completed.

`research/codex/convergence/codex-research-at-exp-004-bounded-remediation-closure-v1.json` is `CONVERGED` with no gaps.

Therefore the old persistence defect is not a current system-wide blocker.

Prospective repaired derived evidence is usable under existing gates.

Pre-fix damaged derived history remains quarantined for retrospective alpha claims.

### Temporal-integrity machinery is real

E1/E1X is a demonstrated falsification capability, not doctrine only.

It has caught:
- true future leakage;
- source-vintage risk;
- warm-up / recursive convergence defects;
- replay-only latent contamination paths;
- a real AT-E3 decision-clock issue.

The correct lesson is not "all data are clean".

The lesson is that cleanliness can now be tested and must be asserted per data lane.

### Honest negative hypothesis evidence exists

AT-HYP-0019 / AT-E3-0019 preserved:
- N2 historical result;
- N3 method correction;
- N4 source-binding block;
- N5 preregistered independent-source replay;
- N5 final `INDEPENDENT_NOT_SUPPORTED`.

This is a success for the evidence process and a failure for the tested hypothesis.

Both should be retained.

## Trial accounting verdict

### Local trial accounting
**SUPPORTED in demonstrated sequences.**

AT-HYP-0019 shows that blocked and failed attempts remain visible and numbered.

### Global AUTO_TRADING proposal denominator
**CENTRALIZATION GAP / BROAD-SEARCH BLOCKER.**

The architecture decision required one global immutable monotonic hypothesis-attempt denominator.

Fresh current-main search finds no such live object.

Historical references to:
`04_RESEARCH_LAB/auto_trading/trials/AT_TRIAL_LEDGER_v2.json`

do not resolve to a current file.

Candidate registry plus local `proposal_trial_n` can support a carefully bound single experiment.

They do not justify high-throughput search across many hypotheses and variants.

## Sol pass 1

GPT-6.1 Sol returned:

`VERDICT=INSUFFICIENT_EVIDENCE`

and selected:

`SELECTED_CANDIDATES_MAX_3=[]`

Its advisory disposition was:
`BUILD_NOTHING`

for new tests on the supplied packet.

Key reason:
No proposed new economic test was supplied with all of:
- immutable candidate/attempt identity;
- replay-safe data;
- frozen baseline;
- cost model;
- adequate power / outcome plan;
- release-condition confirmation.

This is accepted.

The approximate API cost of that pass was $0.0911.

## Sol falsifier reviewed by ChatGPT

Sol raised a possible N5 train/OOS label-overlap concern because label matching permits ±9,000 seconds around t+24h.

Direct code review resolves this concern.

`split_purged()` only includes a training example when:

`outcome_dt <= oos_start - 24h`

Therefore an included training outcome is at least 24 hours before the OOS event boundary.

The ±2.5-hour label-match tolerance cannot make such an included training label cross into the OOS period.

**Verdict on this falsifier: REJECTED / NOT A REPRODUCED OVERLAP DEFECT.**

The existing unit test checks the same invariant.

## N5 caveat that remains real

E1X found that N5 features / entry price were anchored at CFGI event time although the row was only captured 72-879 seconds later.

That is a genuine small decision-clock lookahead.

Because N5 concluded `INDEPENDENT_NOT_SUPPORTED`, the lookahead cannot be used to explain away a positive result.

No historical result rewrite is required.

Future comparable factor tests should use capture-time knowledge semantics.

## Candidate ranking

No new candidate is admitted by M4.

Conditional design tractability only, not admission:
1. AT-HYP-0005 - no-trade as explicit action;
2. AT-HYP-0017 - time-loss exits;
3. AT-HYP-0016 - global + asset-specific regime hierarchy.

These are not selected tests.

AT-HYP-0002 is broader and overlaps more existing framework logic, so it should not be the first scarce slot.

AT-HYP-0019 should not be immediately retried without genuinely new evidence or a materially different preregistered hypothesis.

## Minimum next action for Auto Trading

Before spending a new forward slot, create **one** candidate-specific evidence packet for the best existing theory.

It must bind before outcome inspection:

1. theory ID;
2. immutable attempt ID / local trial number and its relation to prior attempts;
3. exact source paths / hashes / knowledge-time semantics;
4. exact baseline;
5. exact cost / fill model if the test is economic;
6. exact primary metric;
7. exact falsifier;
8. explicit multiple-testing family;
9. power / minimum sample or maturity requirement;
10. execution-slot requirement;
11. no-retroactive-rescore rule.

Only after that packet is audited should a test run.

Do not create multiple packets in parallel just to find one that looks attractive.

## Relationship to the new Distribution Survival audit

A separate Claude Bridge mission has been queued:

`CLAUDE-RL-DISTRIBUTION-SURVIVAL-010`

It will audit the full Research Lab for runnable backtests, simulations and point-in-time historical/prospective tests, with special focus on whether the framework can identify distribution early enough to reduce catastrophic broad-alt drawdown without repeatedly exiting too early.

That audit is complementary to M4.

It may produce the evidence basis for the next candidate-specific packet, but it does not itself authorize a strategy test or portfolio action.

## Queue decision

M4 is closed as `FINAL_RESEARCH_ADJUDICATION`.

M5 `RL-TECHDEV97-005` is released for ChatGPT/Sol final adjudication.

Claude's next high-value work after M4 is the separately queued Distribution Survival audit before its lower-priority TechDev provenance task, unless the external Claude runner has already committed to another released heavy task.

No Codex is used.
No execution layer is opened.
No market threshold, portfolio logic, model weight or canonical state is changed.
