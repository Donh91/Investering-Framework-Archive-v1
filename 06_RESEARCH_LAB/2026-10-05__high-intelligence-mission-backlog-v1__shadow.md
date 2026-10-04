# Research Lab High-Intelligence Mission Backlog v1

**Date:** 2026-10-05  
**Status:** SHADOW_PLANNING / RESEARCH_BACKLOG  
**Authority:** NONE_BY_ITSELF  
**Execution rule:** ONE MISSION AT A TIME  
**Implementation constraint:** NO_CODEX for this sequence unless the owner later changes the mandate.  
**Canonical source snapshot used for routing:** `Donh91/Investering-Framework-Archive-v1@f3ed5764b887ea10edd7841a3c8d49dc5afe91f7`

## Purpose

Preserve the five highest-value Research Lab missions identified from the current archive, and route work by comparative advantage rather than by model preference.

The sequence is deliberately evidence-first:

1. ETF Temporal Integrity / True Decision Value
2. Offensive Edge / False-Negative Opportunity Cost
3. Cycle Navigator Skill Decomposition vs Mechanical Baseline
4. Auto Trading Evidence Machine / Hypothesis Selection
5. TechDev #97 Final Adjudication

No item below is a canonical promotion, market-rule change, threshold/weight change or portfolio instruction.

---

## M1 — ETF Temporal Integrity & True Decision Value

**Priority:** P0 / FIRST  
**Core question:** Is ETF-flow persistence still one of the framework's strongest documented decision edges when every historical decision is replayed using only the ETF information actually knowable at that exact decision time?

### Claude Code role
Read-only, Bridge-only output.

- trace ETF owner/parser/finality/vintage code and all material consumers across the framework;
- reconstruct first-observed, first-complete, settled-double-read and latest-vintage semantics;
- identify any remaining future leakage, stale-finality, schema-drift or consumer-assumption pathways;
- map which historical calls could have been affected;
- independently challenge the existing Temporal Integrity Lab;
- produce exact path/SHA evidence, falsifiers and code/test design only;
- do not modify framework repositories.

### GPT-6.1 Sol API role
Research/adjudication, no code authority.

- quantify true decision value under point-in-time knowledge;
- compare first-known vs later-settled/latest-vintage counterfactuals;
- evaluate warning quality, false positives, false negatives, lead time and decision divergence;
- test whether the claimed ETF asymmetry, outflows high-value / inflows low-value, survives knowledge-time correction;
- separate source-vintage defects from actual signal weakness;
- return VERIFIED / WEAKENED / REJECTED / INSUFFICIENT_EVIDENCE by claim.

### ChatGPT 5.6 Sol High role
Primary owner and adjudicator.

- fresh-read current source state;
- continue analysis in-chat using deterministic evidence and files;
- integrate Claude and API evidence only after independent review;
- challenge both external outputs;
- produce final Research Lab verdict and route only the minimum justified next action.

---

## M2 — Offensive Edge / False-Negative Opportunity Cost

**Priority:** P1  
**Core question:** How much upside has the framework sacrificed through delayed confirmation, by asset tier and regime, and when was that delay justified by drawdown avoided?

### Claude Code role
- reconstruct gate logic, FNP infrastructure, timestamps, asset-tier permissions and decision lineage;
- test whether opportunity-cost rows are point-in-time valid and complete;
- identify missing or non-comparable episodes;
- produce a clean evidence package, not an economic conclusion.

### GPT-6.1 Sol API role
- compare WAIT, actual framework permission, partial BTC/ETH deployment and preregistered graduated-deployment counterfactuals;
- segment by BTC, ETH, large, mid, small/micro and regime;
- quantify return captured, drawdown, delay days and false-negative cost;
- explicitly test the hypothesis that one uniform defensive posture is suboptimal across tiers.

### ChatGPT role
Adjudicate whether any change is warranted without weakening verified defensive edge.

---

## M3 — Cycle Navigator Skill Decomposition vs Mechanical Baseline

**Priority:** P1  
**Core question:** What part of Cycle Navigator is genuine incremental skill versus a mechanical volatility/range baseline?

### Claude Code role
- reconstruct frozen forecast/scoring history and upgraded CN scoring implementation;
- verify no retrospective score mutation;
- build/inspect deterministic benchmark data and scoring reproducibility;
- identify missing weeks, methodological discontinuities and score-family dependencies.

### GPT-6.1 Sol API role
- evaluate range width, range center/placement, direction, regime and rotation skill separately;
- compare CN against dumb volatility-band and other frozen mechanical baselines;
- test regime dependence and statistical uncertainty;
- distinguish product value from range-prediction value.

### ChatGPT role
Final interpretation, public-score governance remains unchanged unless separately authorized.

---

## M4 — Auto Trading Evidence Machine / Next Empirical Phase

**Priority:** P2  
**Core question:** Is the evidence machine now clean enough to test economic hypotheses, and which 2–3 hypotheses deserve scarce forward-test capacity?

### Claude Code role
- inspect data plane, persistence invariance, PIT safety, trial denominator, leakage tests and experiment wiring;
- verify repaired evidence-path assumptions;
- identify only remaining blocking defects;
- do not search for alpha and do not implement an execution layer.

### GPT-6.1 Sol API role
- rank existing hypotheses by value of information, testability, statistical power, duplication risk and forward-test cost;
- design falsifiable preregistrations for only the top candidates;
- penalize multiple testing and hypothesis proliferation;
- prefer killing hypotheses to generating more.

### ChatGPT role
Select/kill candidates and enforce the rule that history falsifies while clean forward evidence confirms.

---

## M5 — TechDev #97 Final Adjudication

**Priority:** P2 / CHEAP CLOSURE  
**Core question:** Did the frozen June 29 claims about September ETH/BTC breakout and DeFi/Aave leadership survive their stated criteria?

### Claude Code role
- recover exact frozen claim text, dates, validation/failure criteria and source lineage;
- verify that evaluation uses the original goalposts;
- gather repository evidence needed for adjudication.

### GPT-6.1 Sol API role
- assess the frozen claims against the completed observation window;
- distinguish genuine early leadership from coincident beta/oversold rebound;
- return a claim-by-claim verdict without moving criteria after outcome.

### ChatGPT role
Close the ledger honestly and extract only reusable learning.

---

## Resource-routing rule

Use the existing framework hierarchy:

`DETERMINISTIC EVIDENCE -> CHATGPT 5.6 SOL HIGH -> CLAUDE INDEPENDENT READ-ONLY REVIEW WHEN MATERIALLY USEFUL -> GPT-6.1 SOL API FOR DIFFICULT SCIENTIFIC SYNTHESIS/FALSIFICATION -> CHATGPT ADJUDICATION`

Claude is not an implementation worker.  
GPT-6.1 Sol API has no repository-write or canonical authority.  
ChatGPT remains the Research Lab owner for this sequence.

## Current execution state

**M1 is active.**

M2–M5 are now fully staged as paired Claude/Sol missions and are locked behind predecessor adjudication:

- M2 `RL-OFFENSIVE-FNP-002` — `QUEUED_WAIT_PREDECESSOR`
- M3 `RL-CN-SKILL-BASELINE-003` — `QUEUED_WAIT_PREDECESSOR`
- M4 `RL-AUTOTRADING-EVIDENCE-004` — `QUEUED_WAIT_PREDECESSOR`
- M5 `RL-TECHDEV97-005` — `QUEUED_WAIT_PREDECESSOR`

Shared protocol:
`06_RESEARCH_LAB/mission_packets/2026-10-05__PAIRED_INTELLIGENCE_PROTOCOL_v1.md`

Queue owner:
`06_RESEARCH_LAB/mission_packets/2026-10-05__PAIRED_INTELLIGENCE_QUEUE_v1.json`

Bridge mirror:
`Donh91/Investering-AI-Audit-Bridge:programs/research_lab_paired_intelligence/QUEUE_v1.json`

Queue presence is not execution authority. Only ChatGPT final adjudication of the predecessor, or an explicit owner override, releases the next mission.
