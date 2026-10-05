# M6 Distribution Survival / Exit Timing Kickoff v1

**Mission:** `RL-DISTRIBUTION-SURVIVAL-META-006`  
**Date:** 2026-10-05  
**Owner:** ChatGPT 5.6 Sol High  
**Status:** ACTIVE_RESEARCH  
**Authority:** RESEARCH_ONLY / NO_PORTFOLIO_ACTION / NO_LIVE_EXIT_TRIGGER  
**Framework main at kickoff:** `8e9a1a362cbb8d5d4e28e4a8889ce2d59676b77b`

## Core question

Can the framework demonstrate, under strict point-in-time rules, that it can identify late-cycle distribution or rising systemic pullback risk early enough to reduce severe altcoin drawdown without repeatedly exiting too early and surrendering too much upside?

The objective is not to predict the exact market top.

The objective is a robust staged decision frontier between:
- staying fully exposed too long;
- trimming some risk when evidence deteriorates;
- avoiding repeated premature exits;
- preserving a credible re-entry path.

## Three separate truth lanes

### A. Historical-as-was

Use only:
- signals;
- data vintages;
- rules;
- outputs;
- thresholds;
- and timestamps

that genuinely existed and were knowable at the historical decision time.

This lane measures the historical machine.

### B. Current-machine-on-old-time

Replay only currently valid framework logic against historical data, with strict point-in-time semantics and no outcome-derived inputs.

This lane measures the value of framework evolution.

It must never be reported as historical performance.

### C. Prospective Distribution Survival Lab

Freeze an outcome-blind protocol before the next real distribution episode matures.

This lane is the only route to future confirmation.

## Required decision metrics

No exact-top optimization.

At minimum evaluate:
- warning lead time to local peak;
- warning lead time to deep drawdown;
- max favorable excursion after warning;
- max adverse excursion after warning;
- upside surrendered by staged trim;
- drawdown avoided;
- false-exit frequency;
- re-entry opportunity;
- re-entry price improvement;
- whipsaw cost;
- performance by BTC / ETH / large / mid / small-micro tier where data permit.

Candidate staged action scenarios are research counterfactuals only:
- HOLD;
- 10-20% trim;
- 25-35% trim;
- ~50% trim;
- 75%+ stress comparator.

No scenario is a portfolio recommendation.

## Anti-hindsight rules

- no threshold tuning on the scored episode;
- no revised value before historical knowledge time;
- no current-machine output counted as historical-as-was;
- no cherry-picked crash-only sample;
- include false alarms and recovered distribution scares;
- include missed crashes;
- include upside missed after early exits;
- discovery and validation periods separated where possible;
- overlapping horizons not treated as independent;
- explicit multiplicity / hypothesis-family accounting;
- price-only baseline always included.

## Paired intelligence roles

### Claude Code via Bridge
Full Research Lab testability census, folder archaeology, source/provenance and runnable-test map.

Mandate:
`messages/chatgpt/2026/10/2026-10-05_CLAUDE_RESEARCH_LAB_DISTRIBUTION_SURVIVAL_010.md`

### ChatGPT 5.6 Sol High
Primary research owner and final adjudicator.

Immediate job:
- identify existing owners/tests;
- build deterministic episode and test inventory;
- prioritize cheap decisive falsifiers;
- prevent duplicate research programs.

### GPT-6.1 Sol API
Do not run at kickoff.

Wait until at least one of:
1. Claude census is available;
2. deterministic episode/test results are available;
3. a material scientific conflict needs adjudication.

Sol's role is falsification / economic interpretation, not signal invention.

## First falsification pair

Try to prove both:

H0-A:
> The framework mostly reacts after price deterioration is already obvious and therefore adds too little lead time to justify staged exits.

H0-B:
> The framework warns too early too often, so avoided drawdown is purchased with excessive surrendered upside and whipsaw.

A useful distribution-warning system must survive both.

## Initial research posture

No new live market rule.
No new exit threshold.
No current portfolio action.
No public product change.

First build evidence.
