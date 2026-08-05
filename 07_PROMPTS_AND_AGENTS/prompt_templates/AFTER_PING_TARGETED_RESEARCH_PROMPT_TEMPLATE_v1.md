# After-Ping Targeted Research Prompt Template v1

Use this template only when `AFTER_PING_RESEARCH_ESCALATION_POLICY_v1` returns `RESEARCH_ESCALATION: YES`.

---

## Copy-ready prompt

```text
TARGETED AFTER-PING RESEARCH REQUEST

REQUEST ID
<generate unique request id>

TRIGGER
A newly reconciled <DATA PING / CLAUDE OTA> at <timestamp UTC and Europe/Copenhagen> produced the following material observation:

<exact observation, values, source owner, and comparison baseline>

WHY THIS CANNOT WAIT
<explain why the next ordinary ping is insufficient or too late, and what decision, experiment, source-QA question, or precision issue may be affected>

ROLE
Work as an independent Research + Source Verification + Falsification Layer.
Do not change framework state, rotation status, rebuy lock, entry permission, trim status, or portfolio action.
Set all framework effects to `NOT_ASSESSED_BY_RESEARCH_AGENT`.

PRIMARY RESEARCH QUESTION
<one precise question>

SECONDARY QUESTIONS
1. <mechanism or attribution question>
2. <historical/base-rate question>
3. <source or measurement question>
4. <falsification question>

TIME WINDOW
- Observation window: <exact start and end>
- Historical comparison window: <exact range or justified analogue selection rule>
- Use Europe/Copenhagen for display and preserve original UTC timestamps.

SOURCE PRIORITY
1. Direct primary sources and exchange/issuer/regulatory data.
2. Official documentation, filings, fund pages, APIs, and timestamped datasets.
3. High-quality secondary research only where primary data cannot answer the question.

DATA AND QA RULES
- Label every item DIRECT, DERIVED, INFERRED, or UNRESOLVED.
- Preserve source timestamps and retrieval timestamps.
- Report revisions, stale payloads, missing denominators, owner conflicts, and parser uncertainty.
- Do not interpolate missing observations.
- Do not carry forward stale values as current.
- Distinguish settled observations from in-progress observations.
- Distinguish correlation from mechanism.
- Search actively for counterevidence and alternative explanations.

REQUIRED OUTPUT
1. Executive finding in no more than 10 lines.
2. Evidence table with source, timestamp, authority, freshness, and result.
3. Mechanism map: what could explain the observation and what evidence supports each path.
4. Historical/base-rate comparison using clearly stated selection criteria.
5. Falsification section: evidence that would invalidate the leading explanation.
6. Remaining unknowns and exact next evidence needed.
7. Source-QA events and provenance anomalies.
8. Main-thread reconciliation package with individually numbered claims.
9. Exact next event or maturity that should be checked.

STOP CONDITION
Stop when the primary research question is answered with the highest available authority or when further work is blocked by explicitly documented missing data. Do not broaden into general market commentary.

MAIN-THREAD RECONCILIATION PACKAGE SCHEMA
For each claim provide:
- item_id
- category
- claim
- value
- previous_value_or_state
- delta
- direct_or_derived
- source_name
- source_identifier
- source_timestamp
- retrieval_timestamp
- method_or_formula
- authority_level
- freshness_status
- revision_status
- counterevidence
- unresolved_dependencies
- suggested_framework_use
- requires_main_thread_crosscheck: YES
- canonical_effect_claimed: NONE
- portfolio_effect_claimed: NONE
```

## Selection note

For Custom GPT, add the exact active DATA PING authority files and require the usual receipts, invocation bijection, freeze rules, and deterministic transforms.

For Claude, emphasize adversarial synthesis, mechanism analysis, historical analogues, and experiment-design implications while preserving the same source and reconciliation requirements.

For BOTH, send separate prompts with the same request ID and do not expose one agent's output to the other before independent completion.
