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
