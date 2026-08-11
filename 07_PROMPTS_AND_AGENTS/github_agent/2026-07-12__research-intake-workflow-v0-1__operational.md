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

## Optional research-data sidecars

For CoinGecko or GeckoTerminal research, an agent may opt in to the bounded CoinGecko MCP Research / Recovery Sidecar defined at:

```text
07_PROMPTS_AND_AGENTS/github_agent/2026-08-11__coingecko-mcp-research-recovery-sidecar-v1__operational.md
research/api_agent/mcp/COINGECKO_MCP_RESEARCH_RECOVERY_v1.json
```

This sidecar is a research access path only. It does not change this workflow's governance order and cannot become a canonical collector, DATA PING owner, weekly input owner, market-state authority or portfolio-action source. MCP failure or rate limiting degrades the research lane only.

When the sidecar is used, preserve the method/query provenance required by its contract and classify the result as source context until the existing owner and governance path accept it.

### Sequential MCP connection evaluation program

The user-approved provider set Dune, LunarCrush, CoinMarketCap, The Graph, altFINS and Binance Agent Native is governed by:

```text
07_PROMPTS_AND_AGENTS/github_agent/2026-08-11__mcp-connection-evaluation-program-v1__operational.md
research/api_agent/mcp/MCP_CONNECTION_EVALUATION_PROGRAM_v1.json
research/api_agent/mcp/MCP_CONNECTION_EVALUATION_METHOD_v1.md
```

CoinGecko is the bounded baseline. The remaining providers are tested one at a time. A provider may be retained only inside its predeclared research/crosscheck/shadow/candidate-discovery/diagnostics ceiling after deterministic boundary checks, live read-only evidence when available, redundancy review and Research Lab Red Team review.

No MCP connection may become a new engine, canonical owner, DATA PING owner, Master Monday owner, Cycle Navigator authority, market-rule source or portfolio-action source through this workflow.

External dependency blocks such as missing provider credentials or an unverified official endpoint remain explicit and advance the queue rather than causing unofficial workarounds or blocking unrelated framework operation.

### Deep Research Horizon Queue

Retained provider connections are consumed by the bounded operational queue at:

```text
research/api_agent/deep_research/DEEP_RESEARCH_QUEUE_v1.json
research/api_agent/deep_research/LATEST_DEEP_RESEARCH_STATE.json
research/api_agent/deep_research/NEXT_DEEP_RESEARCH_TASK.json
research/api_agent/deep_research/DEEP_RESEARCH_METHOD_v1.md
```

The queue studies market direction and cycle transitions separately at `1_3D`, `5_7D`, `2_3W` and `CROSS_HORIZON`, with priority on pre-altseason accumulation context, real-versus-fake rotation, distribution precursors and provider incremental value.

Only providers already retained by the MCP connection scorecard may be used. A provider still in discovery, queued, held, killed, blocked or data-blocked cannot enter a deep-research task. Provider ceilings remain binding.

This queue is explicitly `RESEARCH_QUESTION_NOT_FORWARD_TEST`. It does not replace the canonical Open Questions Register or Active Test Registry, cannot create valid outcome rows and cannot add a new active test. When a research item relates to an existing question or test, it routes evidence to that existing owner. Any finding that would require a new test or a change to market rules, thresholds, weights, policy semantics, sensors or portfolio behavior remains a separate governance proposal.

At most one deep-research item is active. Provider dependency blocks may be skipped temporarily so unrelated research can continue. Every item requires a baseline, hypothesis, decision divergence, falsifier, kill condition, provider provenance and Research Lab Red Team review before any integration proposal.

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
