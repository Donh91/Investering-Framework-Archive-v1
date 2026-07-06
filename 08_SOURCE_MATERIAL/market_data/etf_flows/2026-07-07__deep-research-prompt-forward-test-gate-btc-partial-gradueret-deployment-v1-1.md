# Deep Research Prompt — Forward Test: GATE-BTC-PARTIAL FT-1 + Gradueret Deployment v1.1

**Dato:** 2026-07-07  
**Status:** SOURCE_MATERIAL / PROMPT_ARCHIVE  
**Område:** ETF flows, DATA PING, forward test, FNP, deployment logic, GATE-BTC-PARTIAL, gradueret deployment  
**GitHub path:** `08_SOURCE_MATERIAL/market_data/etf_flows/`  
**Purpose:** Arkivere en forbedret Deep Research-prompt, der kan bruges til at udtrække maksimal værdi fra den foreslåede forward test uden hindsight, uden falske fremtidsrækker og uden at promovere operationelle test-regler som canonical før dokumenterede rækker findes.

---

## Why this prompt exists

Grok's preliminary prompt correctly identified the two relevant ideas:

1. **GATE-BTC-PARTIAL FT-1**: retain a permanent 10% BTC or BTC/stable exposure tranche during BTC Dominant / No Rotation states.
2. **Gradueret Deployment v1.1**: avoid binary WAIT/DEPLOY by scaling alt exposure only after staged rotation confirmation.

This improved prompt converts that idea into a professional Research Lab / Deep Research task:

- pre-register the test,
- define exact ledger rows,
- specify allowed data,
- prevent hindsight,
- prevent synthetic future simulation,
- measure both downside protection and opportunity cost,
- connect ETF-flow data to absorption / transmission logic,
- define promotion and kill criteria,
- and produce an implementation-ready forward-test protocol.

---

# PROMPT TO USE IN DEEP RESEARCH

```xml
<role>
You are Research Lab for the Investering framework.

Your role is not to confirm the proposed update.
Your role is to stress-test, formalize and falsify it.

Treat this as a pre-registered forward-test design task, not as a market prediction task.

You are evaluating whether two proposed framework changes create real decision value:

1. GATE-BTC-PARTIAL FT-1
2. GRADUERET DEPLOYMENT v1.1
</role>

<framework_context>
The Investering framework is a shadow-first ETF-era adaptive market-state framework.

Core principles:
- DATA PING = truth layer
- Shadow = learning
- Consensus = de-noising
- Chief = action layer
- Forecast Ledger = accountability
- Research Lab = professional opponent
- Forward tests before retrospective explanations
- Opportunity cost must be measured, not ignored
- BTC health is not ecosystem health
- Liquidity existence is not liquidity deployment
- ETF inflows are not automatically bullish
- Stablecoin growth is not automatically bullish
- Price stability alone is not confirmation
- Confirmation over anticipation remains active
- But false negatives and delayed deployment costs must be measured
- No new rule may be promoted without documented rows
- No shadow layer may exist without kill criteria

Important current Phase III learning:
The framework is probably not fundamentally too defensive.
Its weakness may be that defensive logic is applied too uniformly across assets and regimes.
BTC and alts should not necessarily share the same offensive gate structure.
BTC-specific partial exposure may be evaluated separately from full ecosystem / alt deployment.
Gradueret deployment is a hypothesis, not a proven improvement.
</framework_context>

<source_material>
Primary source folder:
`08_SOURCE_MATERIAL/market_data/etf_flows/`

Use this folder as ETF-flow source material if accessible.

Also use available DATA PING rows from the live operational feed if provided in the dynamic input.

Allowed source hierarchy:
1. Verified DATA PING rows
2. ETF-flow files in `08_SOURCE_MATERIAL/market_data/etf_flows/`
3. Forecast Ledger / active forward-test rows if provided
4. Current canonical framework rules if provided
5. External sources only if explicitly provided or needed to document source definitions

Do not use unsupported assumptions.
Do not infer missing market values.
Do not simulate future data as if it happened.
</source_material>

<dynamic_input>
Paste here:

1. Latest DATA PING rows from 2026-07-06 onward
2. ETF-flow data files or summaries from `08_SOURCE_MATERIAL/market_data/etf_flows/`
3. Any existing forward-test rows
4. Any relevant price data if already verified
5. Any current framework state / CHIEF PING / Rotation state
6. Any active rules for GATE-BTC-PARTIAL, Rotation Readiness, FNP, or deployment tiers
</dynamic_input>

<task>
Design a rigorous forward-test protocol for:

TEST 1 — GATE-BTC-PARTIAL FT-1
A permanent 10% BTC or BTC/stable tranche during BTC Dominant / No Rotation states.

TEST 2 — GRADUERET DEPLOYMENT v1.1
A staged alt deployment model that only activates after rotation confirmation develops in steps.

Your goal is to maximize decision value.

Do not merely rewrite the idea.
Convert it into a testable, falsifiable, ledger-ready research design.
</task>

<critical_rules>
1. Do not use hindsight.
2. Do not invent missing data.
3. Do not simulate future 30-day rows as real data.
4. If live rows are unavailable, create the ledger schema and mark first row as DATA_MISSING.
5. Use only data that would have been known at the time of each row.
6. Separate BTC recovery, ecosystem recovery and alt deployment.
7. Separate ETF print from ETF trend.
8. Separate price stabilization from transmission confirmation.
9. Treat this as SHADOW FORWARD TEST unless evidence later supports promotion.
10. The test must include kill criteria.
11. The test must include promotion criteria.
12. The test must include FNP / opportunity-cost tracking.
13. Return a clear final verdict on whether the test is ready to run.
</critical_rules>

<test_definitions>
TEST 1 — GATE-BTC-PARTIAL FT-1

Hypothesis:
When STATE = BTC Dominant and ROTATION = No Rotation, maintaining a minimum 10% BTC or BTC/stable exposure may reduce false-negative opportunity cost without meaningfully increasing drawdown versus full WAIT.

Do not assume this is true.
Test it.

State logic:
- PENDING = conditions not yet met or insufficient data
- ARMED = BTC Dominant / No Rotation state present, but entry condition not triggered or incomplete
- ENTERED = 10% BTC tranche activated by pre-defined conditions
- HELD = tranche remains active
- EXPIRED = setup no longer valid or test window ends
- FAILED = invalidated by hard failure condition
- DATA_MISSING = required data unavailable

Minimum fields to log daily:
- date
- source timestamp
- BTC price
- ETH price if available
- ETH/BTC
- BTC dominance
- ETF BTC daily print
- ETF BTC 3D / 5D / 7D trend if available
- ETF ETH daily print if available
- ETF relative strength BTC vs ETH
- breadth state
- rotation state
- DATA PING state
- CHIEF state
- BTC allocation
- stable allocation
- alt allocation
- cf_state
- action taken
- reason for action
- no-hindsight evidence used
- days_saved_vs_framework_wait
- opportunity_cost_vs_wait
- running return vs pure BTC
- running drawdown
- data_quality
- missing fields

TEST 2 — GRADUERET DEPLOYMENT v1.1

Hypothesis:
A staged alt deployment model may capture early upside better than binary WAIT/DEPLOY while preserving protection against fake rotations.

The test must not weaken ETH/BTC, breadth or deployment gates for full alt exposure.
It may only test whether partial tiers improve asymmetry.

Suggested tier logic to evaluate and refine:

Tier 0 — WAIT / NO ROTATION
- Alt allocation: 0%
- BTC/stable allocation: 100%
- Applies when ETH/BTC is weak, breadth is weak, BTC.D elevated or rising, deployment not confirmed.

Tier 1 — FIRST ROTATION CONFIRMATION
- Alt allocation: 10%
- Primary bucket: Large caps only
- Requires at minimum:
  - ETH/BTC stabilization or improvement
  - breadth not deteriorating
  - BTC.D not aggressively reclaiming
  - ETF flow trend not worsening materially
  - no obvious fake-rotation signature

Tier 2 — SECOND CONFIRMATION
- Additional alt allocation: +25%
- Total alt allocation: 35%
- Primary bucket: Large + Mid caps
- Requires:
  - ETH/BTC persistence, not spike
  - breadth survival across at least large + partial mid caps
  - BTC.D deceleration or decline
  - stablecoin deployment / liquidity transmission improving if available
  - post-flush reclaim quality improving if relevant

Tier 3 — FULL CONFIRMATION
- Alt allocation: up to 65%
- Primary bucket: Large + Mid + selected Small caps
- Requires 3/3 confirmation stack:
  1. ETH/BTC persistence
  2. breadth survival
  3. deployment / flow congruence
- BTC.D must not be in defensive reclaim.
- Fake rotation density must be low or falling.

The remaining allocation stays in BTC / stable depending on DATA PING and CHIEF state.

Do not include microcaps unless broad altseason or parabolic phase is confirmed by the framework.
</test_definitions>

<analysis_steps>
Follow these steps in order.

1. Source inventory
   - Identify which ETF-flow files are available.
   - List coverage start/end dates.
   - Identify BTC, ETH and SOL ETF-flow datasets if present.
   - Identify fields, missing days, zero rows, holiday/weekend issues and source conflicts.
   - Classify ETF data as usable / degraded / insufficient.

2. Rule extraction
   - Extract all proposed rules from the draft.
   - Separate actual mechanical rules from vague intentions.
   - Identify undefined terms, including “rotation confirmation”, “breadth”, “cf_state”, “pure BTC benchmark”, “alt allocation” and “days_saved_vs_wait”.

3. No-hindsight pre-registration
   - Freeze exact daily logging rules.
   - Define what data is allowed for each daily row.
   - Define how missing data is handled.
   - Define when a row is eligible for scoring.
   - Define what cannot be changed after the test starts.

4. Ledger design
   - Produce a daily ledger schema.
   - Produce a weekly summary schema.
   - Produce an FNP / opportunity-cost schema.
   - Produce a promotion / kill-criteria tracker.

5. Benchmark design
   - Define benchmark A: pure BTC.
   - Define benchmark B: framework default WAIT/CHIEF allocation if available.
   - Define benchmark C: static stable/no-risk if useful.
   - If alt price proxy is missing, mark return comparison as UNSCORABLE instead of inventing it.
   - Suggest acceptable alt proxies only if data exists.

6. ETF-flow integration
   - Define how ETF BTC flows influence BTC partial confidence.
   - Define how ETF ETH relative strength influences rotation readiness.
   - Separate daily ETF print from trend.
   - Do not treat one positive ETF day as recovery.
   - Define flow-supported pullback vs flow-driven deterioration.

7. FNP / opportunity-cost design
   - Define how to measure days_saved_vs_wait.
   - Define how to measure % move missed.
   - Define how to attribute delay to specific gates.
   - Define when caution was justified.
   - Define when delay becomes genuine false negative.

8. Failure modes
   Identify at least 8 ways this test can fail, including:
   - fake rotation
   - ETF print vs trend conflict
   - BTC outperforms but alts fail
   - ETH/BTC spikes then dies
   - breadth data unavailable
   - alt proxy mismatch
   - low volatility chop creates false confidence
   - test cannot differ from baseline enough to matter
   - rules are too discretionary
   - missing data makes returns unscorable

9. Kill criteria
   Define when the test should be retired, for example:
   - insufficient data after X days
   - no decision divergence from default framework after X rows
   - materially worse drawdown without improved upside capture
   - repeated false rotation entries
   - inability to score returns due to missing price/proxy data
   - overlap with existing framework rules without added decision value

10. Promotion criteria
   Define what must happen before either change can move closer to operational relevance:
   - minimum number of completed rows
   - minimum number of actual state changes
   - required comparison against baseline
   - drawdown threshold
   - opportunity-cost reduction threshold
   - evidence that rules changed behavior, not just explanation

11. Starter output
   - If actual 2026-07-06 data is provided, produce the first daily row.
   - If data is not provided, produce a placeholder row with DATA_MISSING.
   - Do not fabricate BTC price, ETH/BTC, breadth, ETF flow, return or drawdown.

12. Final verdict
   - Decide whether the test is ready to run.
   - If not ready, state exactly what is missing.
   - If ready, provide the final frozen protocol.
</analysis_steps>

<required_output_format>
Return exactly the following sections.

1. EXECUTIVE VERDICT
- READY_TO_RUN / READY_WITH_MISSING_DATA / NOT_READY
- Confidence 0-100
- One-paragraph reason

2. SOURCE INVENTORY
- Available ETF-flow files
- Coverage
- Required missing sources
- Data quality verdict

3. RULE CLARIFICATION
- Final mechanical definition of GATE-BTC-PARTIAL FT-1
- Final mechanical definition of GRADUERET DEPLOYMENT v1.1
- Undefined items resolved
- Items still unresolved

4. FORWARD TEST PROTOCOL
- Start date
- Allowed data
- No-hindsight rule
- Daily row rule
- Weekly summary rule
- State machine
- Allocation rules

5. LEDGER SCHEMAS
Provide in markdown table format:
A. Daily ledger schema
B. Weekly summary schema
C. FNP / opportunity-cost schema
D. Kill / promotion tracker

6. FIRST ROW
If data exists:
Date | BTC Price | ETH/BTC | Breadth | Rotation | ETF BTC Trend | BTC Alloc | Stable Alloc | Alt Alloc | cf_state | Action | Notes | Data Quality

If data does not exist:
Return the same row with DATA_MISSING fields.

7. BENCHMARKS
- Pure BTC benchmark
- Framework default benchmark
- Stable/no-risk benchmark if relevant
- Alt proxy rules
- What is unscorable

8. ETF-FLOW INTERPRETATION RULES
- Print vs trend
- BTC ETF flow use
- ETH ETF relative strength use
- Flow-supported pullback
- Flow-driven deterioration
- Missing-data handling

9. FNP / OPPORTUNITY-COST RULES
- days_saved_vs_wait
- % move missed
- gate delay attribution
- justified caution vs genuine false negative

10. FAILURE MODES
List at least 8.

11. KILL CRITERIA
List exact retirement conditions.

12. PROMOTION CRITERIA
List exact conditions required before operational relevance.

13. FINAL FROZEN PROMPT / SPEC
Provide a clean copy-paste version of the final forward-test spec.

14. WHAT NOT TO DO
Explicitly list what would violate the test.
Include:
- no simulated future rows
- no hindsight rows
- no invented missing data
- no promotion without rows
- no loosening ETH/BTC or breadth gates for full alt deployment
</required_output_format>

<quality_bar>
A high-quality answer must:
- make the test more mechanical than the draft,
- reduce ambiguity,
- preserve governance,
- generate ledger-ready output,
- protect against fake evidence,
- measure both downside and opportunity cost,
- and clearly separate BTC partial recovery from alt deployment.

A low-quality answer:
- simply rewrites the draft,
- simulates fake future data,
- declares the strategy good without evidence,
- ignores missing data,
- or treats ETF inflows as automatic bullish confirmation.
</quality_bar>

<critical_reminders>
Use only provided material.
Do not invent data.
Do not simulate the next 30 days.
Do not backfill with hindsight.
Do not promote to canonical without rows.
Treat this as a shadow forward test until proven otherwise.
Rows beat theory.
If evidence is insufficient, say so clearly.
</critical_reminders>
```

---

## Operational note

This prompt is intentionally stricter than the preliminary Grok version.

Main upgrade:

- Grok's draft asks the model to run or simulate a forward test.
- This version asks Deep Research to build a falsifiable, no-hindsight, ledger-ready forward-test protocol.

That is safer and more valuable for the framework.
