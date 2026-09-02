# CLAUDE PROMPT ENGINEERING STANDARD v1.1 — CANDIDATE

Status: Candidate, not canonical
Date proposed: 2026-09-02
Supersedes: nothing until ratified
Basis: framework experience + Anthropic current prompt-audit guidance
Applies to: Claude prompts, Research Lab prompts, Cowork-style audits, framework review and research handoffs

## Principle

Give Claude the context, authority boundaries, evidence rules and definition of success that only the framework can supply. Let the model own planning and reasoning unless execution order is itself part of validity or safety.

Prompt quality is measured by task performance and epistemic integrity, not prompt length or number of instructions.

## Standard

For substantial Claude tasks, include the following when relevant.

### 1. Mission
State the outcome or decision the work must support. Prefer a concrete research question, audit objective or deliverable over generic instructions to analyse thoroughly.

### 2. Role and authority boundary
Define Claude's role where it matters. For framework research, Claude is normally an independent challenger, auditor or researcher. It may recommend changes, but external-model output is not canonical by default.

### 3. Static context
Provide framework facts Claude cannot infer safely: architecture, governance, definitions, accepted contracts, source hierarchy, constraints and known state.

### 4. Dynamic input
Identify the current evidence, files, repository state, captures, logs, datasets or user-provided actuals that belong to this run. Keep static instructions distinct from changing inputs when practical.

### 5. Evidence and provenance contract
Specify the epistemic rules that matter to the task. Examples include source authority, timestamp requirements, no-hindsight boundaries, observed-versus-inferred separation, and prohibition on inventing source calls, receipts, hashes, tests or repository state.

Claude must be allowed to return insufficient evidence, unresolved or no-edge when supported.

### 6. Falsification and acceptance criteria
For research and audit work, state what would strengthen, weaken or falsify the hypothesis and what constitutes success, failure, rejection, deferral or a need for forward testing.

Use measurable thresholds when the framework genuinely defines them. Do not invent numerical thresholds merely to make the prompt look rigorous.

### 7. Operational constraints
Specify tool, repository, write, security, budget or environment constraints when they affect what Claude may actually do.

Prescribe an ordered procedure only when order is load-bearing, such as no-hindsight replay, timestamped capture, validation-before-write, destructive operations or protocol execution. For open-ended research and judgment, state outcomes and verification requirements and let Claude choose the working plan.

### 8. Deliverable contract
State what must be returned or produced. Use schemas or rigid formatting only when a downstream consumer requires them. Otherwise prefer the clearest format for the task.

### 9. Verification
Require verification appropriate to the task: source cross-checks, tests, replay checks, repository readback, contradiction search, or explicit unresolved items.

Do not equate a confident narrative with verification.

## Uncertainty

Claude should communicate material uncertainty. A formal confidence score is required only when the workflow or downstream schema consumes one. Avoid false precision.

## Examples and few-shot material

Use examples when they establish a genuinely sensitive output shape, domain convention or edge case. Treat examples as illustrative unless exact conformity is required. Avoid carrying old examples forward merely because earlier models needed them.

## Prompt hygiene

State important requirements once at the correct authority level. Prefer precise positive requirements and their rationale over stacks of MUST, NEVER, CRITICAL and repeated prohibitions.

Do not add generic instructions such as 'be accurate', 'be thorough' or 'do not hallucinate' when the actual need can be expressed as a concrete evidence, provenance or verification rule.

Do not require step-by-step planning, hidden-thought reproduction or mechanical reasoning sections for ordinary judgment tasks.

Do not repeat critical rules at the end by default. Repetition requires a reproduced failure showing that the target model otherwise misses the rule.

## Framework research default

For Research Lab and major framework audits, the semantic flow remains:

data -> evidence -> interpretation -> framework impact -> implementation recommendation.

This is an epistemic separation rule, not a mandatory visible response template.

Research Lab remains the framework's professional opponent. It should seek blind spots, stress-test assumptions, test opportunity cost, challenge acceptance theater, prevent closed loops, separate evidence from interpretation and classify findings before promotion.

ChatGPT remains the framework governance and ratification layer. User-verified actuals retain their established authority. External model output is research input until reviewed.

## Migration from v1.0

The following v1.0 elements remain load-bearing:

- role where role establishes authority,
- task/mission,
- static context,
- dynamic input,
- output/deliverable contract,
- evidence threshold or acceptance criteria,
- permission to conclude insufficient evidence.

The following become conditional:

- ordered reasoning steps,
- formal confidence score,
- examples and rigid formatting.

The following are removed as universal requirements:

- generic hallucination guardrail slot,
- critical rules repeated at the end.

They are replaced by task-specific provenance and verification contracts.

## Ratification gate

This candidate must not replace v1.0 until representative A/B tasks show that it preserves or improves evidence integrity, constraint adherence, useful falsification and operational completion. Token reduction alone is not sufficient evidence.
