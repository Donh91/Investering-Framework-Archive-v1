---
name: adaptive-analysis-methods
description: 'Read-only, bounded method selection for complex framework audits, repeated failures, uncertain research and high-consequence reviews. Select one primary and at most one complementary method; execute within existing owner permissions. Do not use for routine status, simple fixes or as a model/API router.'
---

# Adaptive Analysis Methods v1.0 (pilot)

## Purpose
Choose the *kind* of reasoning needed, not the model or its hidden thinking time. This skill is a small preflight for complex tasks, not an agent, scheduler, scorer, reviewer, queue, or new authority. A method must improve evidence or completion, not length.

## Activation
- Explicit: deep audit, forensic review, scientific validation, repeated unresolved defect, root-cause investigation, high-consequence architecture review, or user invocation.
- Conditional: conflicting primary evidence, two or more documented unsuccessful attempts, or a material unresolved causal assumption.
- Negative: routine status, ordinary Data Ping, straightforward code fix, simple PR merge, regular reporting, or tasks already under a verified executable plan. A bare word "audit" requires task relevance; it never authorizes writes or API use.
- Do not infer thinking duration or hidden reasoning tokens. Default L0 (direct execution); L1 (one method) when relevant; L2 (one primary plus at most one complementary method) only when materially justified.

## Required preflight
1. Resolve current authority using `canonical-context-router` and domain owner; inspect existing PRs, owners, evidence, and existing skill coverage before selecting.
2. Freeze user objective, permitted actions, success criterion and existing stop condition. Preserve an approved execution plan unless new evidence invalidates it.
3. Identify the *one* limiting uncertainty: missing expertise, raw evidence, falsifiability, root cause, experiment design, or completion.
4. Select one primary method from `references/METHODS.md`; optionally one complement if it addresses a different material failure.
5. Run the method within the existing task, then return to execution. Reconsider only upon a new, material finding; never restart merely because an audit sounds important.

## Composition and authority
- Existing `research-lab-red-team` owns claim falsification and its verdicts. This skill does not replace or invoke it implicitly against its explicit-only policy.
- Existing `developer-source-research` handles public upstream technical sourcing; `prospective-evidence-ledger` governs registered evidence rows; `archive-governance` governs repository writes; `skill-quality-gate` evaluates this candidate separately.
- A selected method does not invoke other restricted skills, external tools, paid models, Work, Codex, Sol API, workflows or queues without their own authority and budget gates.
- No market, forecast, portfolio, threshold, scoring, data-authority, evidence-promotion, repository-write or merge authority.
- Never copy restricted evidence into public surfaces. Missing evidence remains UNKNOWN. No hindsight credit.

## Compact output contract
For L1/L2, internally or in the task's existing record capture:
```yaml
objective:
level: L1 | L2
primary_method:
complementary_method: NONE | METHOD_NAME
owner_and_existing_work_checked:
decisive_raw_evidence:
falsifier_or_failure_test:
next_executable_action:
stop_condition:
status: EXECUTED | BLOCKED | INCOMPLETE
```
Do not add a separate user-visible report when execution can proceed. Never claim execution or verification without a receipt.

## Pilot and retirement
Test positive and negative triggers, owner boundaries, blocked sources, duplicate work, actual completion, and cost/context impact using the existing skill-quality-gate. STATIC_ONLY or fixture tests cannot prove model improvement. If it increases loops, incorrect authority, unnecessary invocation or fails to add measurable value over no-skill, modify or retire through existing governance.
