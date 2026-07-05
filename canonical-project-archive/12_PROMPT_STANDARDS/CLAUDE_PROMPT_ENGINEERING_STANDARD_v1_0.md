# CLAUDE PROMPT ENGINEERING STANDARD v1.0

Status: Canonical
Date added: 2026-07-05
Effective from: 2026-07-05
Source context: ChatGPT
Applies to: Claude prompts, Research Lab prompts, audit prompts, framework review

## Executive summary

Claude should be prompted as a structured audit and research system, not as a generic analyst.

## Canonical content

Use this prompt structure for major Claude tasks:

1. Role.
2. Task.
3. Static context.
4. Dynamic input.
5. Ordered reasoning steps.
6. Hallucination guardrails.
7. Output format.
8. Evidence threshold.
9. Confidence score.
10. Critical rules repeated at the end.

## Operational implication

Claude prompts should separate instructions from input and force a clear evaluation sequence:

data -> evidence -> interpretation -> framework impact -> implementation.

## Governance notes

Claude must be allowed to say insufficient evidence.
Do not ask Claude to confirm a preferred conclusion.

## Update log

- 2026-07-05: Created.