# OpenAI Agents API — Infrastructure Opportunity Source Note

**Dato:** 2026-09-11  
**Status:** SOURCE_NOTE  
**Område:** agent infrastructure / Astra / Codex harness / orchestration  
**Primary folder:** `07_PROMPTS_AND_AGENTS/astra/`  
**Depends on:** `07_PROMPTS_AND_AGENTS/astra/ASTRA_RESEARCH_INTELLIGENCE_LANDING_ZONE_v1.md`, `research/api_agent/CAPABILITY_ROUTING_POLICY_v1.json`, `research/api_agent/API_INTELLIGENCE_POLICY_v2.json`, `00_FMOS/AUTOMATION_ORCHESTRATION_ARCHITECTURE_v2.md`

## Source

Official OpenAI announcement, published 2026-09-10:

`https://openai.com/index/introducing-the-agents-api/`

Product state at capture: `PUBLIC_BETA`.

## Why this matters to the Investering framework

The Agents API exposes the Codex agent harness and supporting infrastructure as a developer API. This is directly relevant to the framework's prepared Astra / API-agent architecture because it provides several capabilities we have already been designing around internally:

- long-running cloud agent sessions;
- context management across long sessions, including automatic compaction;
- MCP, custom functions and built-in tools;
- tool discovery / tool search;
- programmatic parallel tool calling;
- multi-agent execution with parallel subagents and separate subagent contexts;
- OpenAI-hosted sandboxes with files, code execution and artifact production;
- alternative execution environments on own infrastructure or supported sandbox partners;
- versioned access to an evolving Codex harness maintained alongside model releases.

OpenAI states that the Agents API can run work that spans hours or days and that the same harness family underpins Codex. The official example uses `gpt-6-astra`, MCP tools, an OpenAI-hosted environment and multiple concurrent subagents.

## Framework interpretation

This is **not** a reason to create a new framework engine.

It is a potentially important **execution-infrastructure option** for the existing agent architecture.

The strongest potential value is reducing custom orchestration glue that we otherwise have to own ourselves, especially around:

1. durable session/context handling;
2. subagent fan-out and coordination;
3. tool discovery and efficient tool loading;
4. sandbox provisioning;
5. recovery/continuation of long-running work;
6. model/harness upgrades over time.

This aligns closely with the current Astra landing-zone direction:

- Minimum Sufficient Intelligence;
- bounded parallelism;
- unique question ownership;
- capability routing;
- explicit budgets;
- long-horizon research;
- GitHub-first handoff and reproducibility;
- use of strong models only where they add material information value.

## What it does **not** change

The Agents API must not be treated as authority over framework logic.

It does not change:

- DATA PING truth authority;
- market rules or portfolio permissions;
- Research Lab governance;
- F12 / falsification rules;
- cross-repository data boundaries;
- credential handling;
- repository write/merge governance;
- least-privilege requirements;
- Astra model-routing and budget authority.

The agent harness is infrastructure. Repository governance remains the authority layer.

## Future evaluation candidate

When the framework next evaluates Astra/API-agent execution infrastructure, compare the current stack against an Agents API lane using a frozen benchmark set.

Recommended evaluation dimensions:

- task completion quality;
- failure / recovery rate;
- long-session continuity;
- tool-selection accuracy;
- duplicate-question / redundant-agent rate;
- subagent coordination quality;
- wall-clock latency;
- model and tool token cost;
- context efficiency / compaction quality;
- provenance and evidence preservation;
- GitHub handoff quality;
- least-privilege compliance;
- behavior under unavailable tools or partial evidence.

Promotion should require measured improvement over the existing stack, not novelty.

## Candidate future uses

If qualified, the Agents API could become an execution option for:

- Astra heavy research missions;
- bounded parallel red-team / replication tasks;
- repository audits;
- research-to-Codex investigations;
- long-running source recovery;
- structured multi-source research;
- batch evaluation / calibration jobs;
- durable orchestration where current chat or Codex session limits create friction.

Use the existing `ResearchContract` / run-envelope and capability-routing logic rather than inventing a parallel agent-control system.

## Archive decision

Classification: `NEW_INFORMATION`  
Status: `SOURCE_NOTE`  
Authority: `NONE_BY_ITSELF`  
Operational change: `NONE`  
Immediate implementation: `NO`  
Future review priority: `HIGH`

This note exists so future repository-aware models understand that OpenAI now offers a first-party, managed Codex-harness API that may materially simplify the framework's agent execution architecture, while preserving the requirement to qualify it against the current governed stack before adoption.
