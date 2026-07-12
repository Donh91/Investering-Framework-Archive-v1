# Research Intake Workflow v0.1

**Dato:** 2026-07-12  
**Status:** OPERATIONAL  
**Område:** external research triage / X posts / architecture learning  
**Primary folder:** `07_PROMPTS_AND_AGENTS/github_agent/`  
**Depends on:** Agent Control Loop v0.1, Canonical Context Router, Research Lab Red Team, Archive Governance

## Purpose

Convert external posts, threads, papers and practitioner claims into decision-useful research without letting novelty bypass existing framework governance.

## Input

```yaml
source_urls:
source_text_or_extract:
source_type:
user_question:
requested_action:
write_intent:
```

## Mandatory workflow

1. Resolve current authority with `canonical-context-router`.
2. Separate the source claim from the source's marketing or confidence.
3. Identify whether the idea already exists in the repository.
4. Classify the source.
5. Map useful ideas to an existing owner or a repeated workflow gap.
6. Run `research-lab-red-team` for claims about framework improvement.
7. Propose the smallest test or operational change.
8. Use `archive-governance` only when the user explicitly requests a write.

## Classification

Use exactly one primary class:

```text
SOURCE_EVIDENCE
PRACTITIONER_ANECDOTE
ARCHITECTURE_INSPIRATION
MARKETING_OR_UNVERIFIED
DUPLICATE_OF_EXISTING_OWNER
REPEATED_GAP_CANDIDATE
NOT_RELEVANT
```

## Required output

```markdown
## RESEARCH INTAKE

Source:
Primary classification:
Confidence in source:
Core claim:
What is genuinely useful:
What is hype or unsupported:
Current framework overlap:
Existing owner:
Repeated gap demonstrated:
Recommended action:
Recommended test:
Verifier:
Stop condition:
Archive decision:
Authority boundary:
```

## Decision rules

- A useful post is not evidence of trading edge.
- A recurring workflow failure may justify infrastructure before a new Skill.
- One post cannot authorize a new engine, score, threshold or portfolio rule.
- Practitioner cost or token anecdotes remain anecdotes unless independently measured.
- Prefer deterministic verification, state and receipts over a larger prompt.
- Prefer a narrow pilot with a kill criterion over a permanent architecture change.
- Reject duplicate memory systems when GitHub already owns durable state.
- Research may recommend an experiment. It may not self-ratify the result.

## Write rule

When explicit write intent exists, archive only the durable synthesis or test contract.

Do not archive every post or every intermediate analysis.
