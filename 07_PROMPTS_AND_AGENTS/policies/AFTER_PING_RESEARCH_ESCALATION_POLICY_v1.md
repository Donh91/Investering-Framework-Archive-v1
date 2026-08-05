# After-Ping Research Escalation Policy v1

```yaml
policy_id: AFTER_PING_RESEARCH_ESCALATION_POLICY_v1
status: ACTIVE
applies_to:
  - DATA_PING
  - CLAUDE_OTA
  - EXTENDED_DATA_PING
  - CYCLE_NAVIGATOR_PRECURSOR_READS
owner: MAIN_FRAMEWORK
purpose: MAXIMIZE_UNDERSTANDING_AND_PRECISION_WITHOUT_CREATING_RESEARCH_NOISE
```

## Core rule

After every DATA PING or OTA reconciliation, the main framework must perform a separate **research-escalation assessment** in addition to the market-state assessment.

The assessment asks:

> Did the new evidence create a material, time-sensitive uncertainty whose resolution could improve the next framework decision, falsification test, source-quality judgment, experiment design, or forecast precision before the next ordinary DATA PING or OTA?

When the answer is yes, the user must be told immediately and given a complete, copy-ready prompt for the most suitable research agent.

## Mandatory user-visible output

Every completed DATA PING or OTA response must contain one of the following:

```yaml
RESEARCH_ESCALATION: NO
reason: NEXT_PLANNED_PING_OR_KNOWN_MATURITY_IS_SUFFICIENT
```

or:

```yaml
RESEARCH_ESCALATION: YES
priority: P0_IMMEDIATE | P1_SAME_DAY | P2_BEFORE_NEXT_MAJOR_REVIEW
trigger: <specific new observation>
why_now: <why waiting reduces information value or decision precision>
research_owner: CUSTOM_GPT | CLAUDE | BOTH
copy_ready_prompt: <exact prompt>
expected_return: <specific evidence package>
stop_condition: <what is sufficient and what must not be inferred>
framework_destination: <ledger, experiment, source-QA, state reconciliation, or archive path>
```

The research block must appear before the final `Top-up og købsvindue:` sentence.

## Escalation triggers

Escalate when at least one trigger is present and the expected information value is high:

1. **Load-bearing threshold event**
   - A material touch, close, failed breakout, reclaim, or loss near a framework gate.
   - The event is not adequately resolved by the next already-scheduled maturity.

2. **Cross-sensor contradiction**
   - Price, ETF flow, breadth, derivatives, liquidity, macro, sentiment, or source evidence point in materially different directions.
   - The contradiction could change state interpretation or experiment design.

3. **Unexpected structural novelty**
   - A pattern appears that is not covered by the current architecture or prior ledger.
   - Examples: new transmission path, unusual issuer concentration, venue divergence, abnormal spot/derivative split, or regime-specific source behavior.

4. **Source or provenance anomaly**
   - Freshness, revision, parser, membership, timestamp, owner, denominator, or lineage uncertainty can materially change the reading.

5. **Experiment maturity with unresolved mechanism**
   - An experiment matures or repeatedly fails in a way that exposes an undefined lapse, retire, retrigger, or falsification rule.

6. **Decision-relevant missing denominator or context**
   - A numerator is known but scale, normalization, AUM, market share, historical percentile, or comparable baseline is absent.

7. **Time-sensitive external catalyst question**
   - A sudden move may be associated with a current event, policy announcement, flow event, market-structure change, outage, liquidation cascade, or venue-specific incident that should be resolved before the next decision point.

8. **Model disagreement or owner-ledger mismatch**
   - OTA, DATA PING, repository owner, or derived windows disagree and the discrepancy cannot be explained from available rows.

## Non-escalation conditions

Do not escalate solely because:

- a move is large but the decisive candle or official print will settle within the next planned run;
- the question is interesting but cannot affect state, experiment design, source QA, or forecast precision;
- the same uncertainty is already tracked with an exact next event;
- evidence is in-progress and external research would mainly invite narrative fitting;
- a normal next ping will answer the question with higher authority and lower ambiguity.

## Priority

```yaml
P0_IMMEDIATE:
  horizon: NOW_TO_2_HOURS
  use_when: A live anomaly or external event may materially alter interpretation before the next maturity.

P1_SAME_DAY:
  horizon: BEFORE_NEXT_DAILY_SETTLE_OR_DECISION_WINDOW
  use_when: The uncertainty matters today but does not require interruption within minutes.

P2_BEFORE_NEXT_MAJOR_REVIEW:
  horizon: BEFORE_MASTER_MONDAY_OR_NEXT_EXPERIMENT_REVIEW
  use_when: The issue is structural, methodological, or calibration-related rather than market-immediate.
```

## Agent selection

Use **Custom GPT** when the task primarily requires the active DATA PING source stack, deterministic retrieval, exact time windows, direct market data, receipts, hashes, or source-ledger compatibility.

Use **Claude** when the task primarily requires synthesis, mechanism research, literature review, hypothesis construction, historical analogues, experiment design, or adversarial interpretation.

Use **BOTH** when independent collection and independent synthesis materially reduce error. Their outputs must remain separate until main-thread reconciliation.

## Prompt requirements

Every research prompt must specify:

- exact triggering observation and timestamp;
- precise research question;
- sources or source classes to prioritize;
- required time window;
- direct-versus-derived labeling;
- provenance and freshness requirements;
- explicit prohibitions against framework-state changes and portfolio advice;
- exact deliverables;
- stop condition;
- reconciliation package for the main thread.

## Governance

Research escalation does not itself change canonical state, portfolio permissions, experiment scores, or owner pointers.

All returned research remains non-canonical until reconciled against the current DATA PING/OTA owner and archived with source QA.

The escalation decision should be logged in the relevant DATA PING or OTA framework read as:

```yaml
research_escalation_decision: YES | NO
research_escalation_reason: <reason code>
research_request_id: <id or null>
```
