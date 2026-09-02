# CLAUDE PROMPT AUDIT — 2026-09-02

Status: Proposed research/audit artifact
Scope: canonical Claude prompt standard and Research Lab role
Upstream authority reviewed: anthropics/skills, skills/claude-api/shared/prompt-audit.md
Target: current Claude generation used for framework research and Cowork-style work

## Executive verdict

The framework's Claude prompting philosophy remains sound, but CLAUDE_PROMPT_ENGINEERING_STANDARD_v1_0 contains several model-era-specific prescriptions that should no longer be canonical as universal requirements.

The audit does not recommend weakening framework governance, evidence standards, falsification, provenance, source hierarchy, or the Research Lab role. Those are load-bearing framework context that the model cannot infer independently.

Recommended disposition: KEEP the governance core, SIMPLIFY orchestration language, REMOVE universal requirements for hand-authored reasoning choreography and repeated critical rules, and REPLACE the v1.0 standard with a tested v1.1 candidate.

## Inventory audited

1. canonical-project-archive/12_PROMPT_STANDARDS/CLAUDE_PROMPT_ENGINEERING_STANDARD_v1_0.md
2. canonical-project-archive/05_RESEARCH_LAB/RESEARCH_LAB_ROLE.md
3. Current framework practice established around Claude/Cowork audits: Claude as independent red-team/research opponent, evidence-first, falsification-capable, with ChatGPT as governance/ratification layer.

This audit does not claim exhaustive coverage of every historical one-off handoff prompt in the repository. Those should inherit the new standard prospectively and can be audited when reused.

## Findings

### F1 — Ordered reasoning steps as a universal requirement
Location: CLAUDE_PROMPT_ENGINEERING_STANDARD_v1_0.md, canonical content item 5.
Classification: SIMPLIFY / conditionalize.
Confidence: High.

Reason: Anthropic's current prompt-audit guidance flags step-by-step choreography for judgment tasks as dated over-specification. Ordered steps remain appropriate where sequence is genuinely load-bearing, for example no-hindsight replay, data validation, destructive operations, or protocol execution. They should not be mandatory for every major Claude task.

Proposed rule: specify outcomes, constraints, evidence requirements and verification. Prescribe execution order only where changing the order can change validity or safety.

### F2 — Critical rules repeated at the end
Location: CLAUDE_PROMPT_ENGINEERING_STANDARD_v1_0.md, canonical content item 10.
Classification: REMOVE as universal requirement.
Confidence: High.

Reason: Anthropic's current guidance identifies repeated instructions and pressure-language accumulation as potential prompt cruft. A rule should normally appear once, at the correct authority level, with its reason where useful. Repetition is justified only by a reproduced model failure or a harness-specific retention issue.

### F3 — Hallucination guardrails as a generic structural slot
Location: CLAUDE_PROMPT_ENGINEERING_STANDARD_v1_0.md, canonical content item 6.
Classification: SIMPLIFY.
Confidence: Medium-high.

Reason: Generic prohibitions such as 'do not hallucinate' add little. Framework-specific epistemic controls remain essential: distinguish observed data from inference, never fabricate source calls/receipts/hashes, say insufficient evidence when appropriate, preserve no-hindsight boundaries, and do not promote external-model output to truth-layer.

Proposed rule: replace generic hallucination language with explicit epistemic and provenance contracts tied to the task.

### F4 — Confidence score as a universal requirement
Location: CLAUDE_PROMPT_ENGINEERING_STANDARD_v1_0.md, canonical content item 9.
Classification: CONDITIONAL.
Confidence: Medium-high.

Reason: A numeric or categorical confidence field is useful only when downstream governance consumes it or when uncertainty calibration is part of the task. Requiring it universally can create false precision and formatting overhead.

Proposed rule: require calibrated uncertainty, but require a formal confidence score only where the workflow or schema uses it.

### F5 — Fixed pipeline: data -> evidence -> interpretation -> framework impact -> implementation
Location: CLAUDE_PROMPT_ENGINEERING_STANDARD_v1_0.md, Operational implication.
Classification: KEEP AS SEMANTIC ORDER, not mandatory response choreography.
Confidence: High.

Reason: This is framework-specific epistemic separation and remains valuable. It should define the logic of the work, not force every response to expose five sections or mechanically narrate each step.

### F6 — Role, task, static context, dynamic input, output format, evidence threshold
Location: CLAUDE_PROMPT_ENGINEERING_STANDARD_v1_0.md, items 1-4 and 7-8.
Classification: KEEP, with flexible composition.
Confidence: High.

Reason: These carry information Claude cannot reliably infer: mission, framework state, current evidence, acceptance criteria and deliverable contract. They are not dated prompting tricks.

### F7 — Research Lab as professional opponent
Location: RESEARCH_LAB_ROLE.md.
Classification: KEEP.
Confidence: High.

Reason: The role establishes framework-specific authority boundaries and research purpose. It prevents model output from becoming self-ratifying framework truth.

### F8 — Research Lab duties: blind spots, stress tests, opportunity cost, acceptance theater, closed loops, evidence/interpretation separation, classification before promotion
Location: RESEARCH_LAB_ROLE.md.
Classification: KEEP.
Confidence: High.

Reason: These are substantive research objectives, not model-behavior scaffolding.

### F9 — ChatGPT governance/ratification boundary and user-verified actuals priority
Location: RESEARCH_LAB_ROLE.md.
Classification: KEEP.
Confidence: High.

Reason: These are authority and provenance contracts specific to this framework.

## Proposed v1.1 design

A major Claude task should provide the information needed to succeed, without prescribing reasoning Claude can own itself.

Required when relevant:

1. Mission and decision/outcome sought.
2. Role and authority boundary.
3. Static framework context that is not otherwise available.
4. Dynamic inputs and source hierarchy.
5. Evidence, provenance and uncertainty rules.
6. Success, failure, falsification or kill criteria.
7. Tool/repository constraints where operationally important.
8. Deliverable/output contract.
9. Verification requirements.

Conditional, not universal:

- Ordered execution steps, only when order is validity- or safety-critical.
- Formal confidence score, only when consumed downstream.
- Examples, only when they pin a genuinely sensitive output shape.
- Repeated instructions, only when a reproduced failure demonstrates need.

Avoid by default:

- Generic 'be accurate/thorough' padding.
- Pressure-language stacks such as repeated MUST/NEVER/CRITICAL.
- Hand-written planning choreography for open-ended research or judgment.
- Generic anti-hallucination slogans instead of concrete provenance rules.
- Duplicated rules at the end of prompts.
- Format requirements that exist only because an older model needed them.

## Framework-specific invariants that must survive prompt cleanup

- Claude/Research Lab is an independent challenger and research input, not the framework truth-layer.
- External-model output is not canonical by default.
- Evidence must be separable from interpretation.
- Insufficient evidence is a valid result.
- No-hindsight, timestamp, provenance and source-authority contracts remain binding where applicable.
- Never invent source calls, receipts, hashes, test results, repository state or live observations.
- Falsification and negative findings are first-class outcomes.
- Promotion into canonical framework state requires governance review.

## Acceptance plan before superseding v1.0

Do not ratify v1.1 solely because the upstream guidance recommends simpler prompts.

Run representative old-vs-new prompt comparisons on at least these task classes when practical:

1. Independent architecture/evidence audit.
2. Research hypothesis falsification task.
3. Repository/handoff execution task with strict operational constraints.
4. Historical/no-hindsight replay task where ordered steps are intentionally retained.

Compare:

- factual/provenance violations,
- missed constraints,
- unnecessary clarification or stopping,
- tool/repository autonomy,
- false certainty,
- useful falsification,
- output usability,
- token/input overhead where measurable.

Ratify v1.1 only if it preserves governance and evidence quality while matching or improving task completion. A clean A/B result with no material improvement is grounds to keep v1.0 or adopt only the clearly supported removals.

## Managed Agents disposition

HOLD. Anthropic Managed Agents, persistent memory, multi-agent coordination, outcomes, scheduled deployments, webhooks and session budgets are strategically relevant to a future API-driven Research Lab, but they are not required for this prompt-standard update. Do not create a new framework engine or architecture around them without a concrete use case and bounded evaluation.

## Audit conclusion

GO for a v1.1 candidate and bounded A/B validation.
HOLD Managed Agents implementation.
NO-GO for copying the Anthropic claude-api skill wholesale into the investment framework.
