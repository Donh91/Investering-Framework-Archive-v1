# AT-SRC-0009 — AWESOME TRADING AGENTS DISCOVERY RADAR

Date captured: 2026-09-11
Status: `RESEARCH_DISCOVERY_SOURCE`
Evidence class: `EXTERNAL_CAPABILITY_RADAR_NOT_SIGNAL_EVIDENCE`
Authority: `NONE_BY_ITSELF`
Primary source: https://github.com/LLMQuant/awesome-trading-agents

## Purpose

Retain `LLMQuant/awesome-trading-agents` as a curated external radar for agent, MCP and skill patterns that may expose a capability the Investering Framework has not solved well enough yet.

This is not a dependency bundle and must not be installed wholesale. A repository entry earns attention only when it can demonstrate a capability delta against the current framework.

## Directly verified source characteristics

The upstream repository describes itself as a curated list of LLM-driven trading agents, MCP servers and agent skills for market research, strategy and execution. Its scope is intentionally Agents / MCPs / Skills rather than classic quant libraries.

Current high-value references include:

- `TauricResearch/TradingAgents` — multi-agent financial research/trading architecture. Its 2026 v0.4.0 release explicitly includes look-ahead / point-in-time fixes, decision-log memory corrections, checkpoint-resume fixes and Trader price grounding. These are useful adversarial references for temporal-integrity and replay tests.
- `tradermonty/claude-trading-skills` — machine-readable skill/workflow organization. Verified workflow manifests include `market-regime-daily`, `trade-memory-loop`, `monthly-performance-review`, `core-portfolio-weekly` and `swing-opportunity-daily`. The useful transfer is typed workflow contracts and validated memory/postmortem boundaries, not duplication of the Investering Framework's existing regime engine.
- `LLMQuant/data-mcp` — candidate research-literature discovery source. The upstream catalogue describes semantic access to 50k+ quant knowledge entries and 1,200+ papers plus conventional market/fundamental data. The market-data portion overlaps existing sources and must pass duplicate-value testing before adoption.

## Capability-delta gate

Any project discovered through this source must be classified before deeper work:

- `DUPLICATE`
- `IDEA_ONLY`
- `BENCHMARK`
- `DATA_SOURCE`
- `CODE_CANDIDATE`
- `REJECT`

Evaluate at minimum:

- unique capability relative to current owners;
- point-in-time / look-ahead discipline;
- provenance quality;
- determinism and reproducibility;
- machine-checkable contracts/tests;
- cost and dependency risk;
- licensing/security;
- framework overlap;
- whether it solves a frozen problem rather than creating a fashionable parallel stack.

Popularity, stars and persuasive demos are not promotion evidence.

## Alpha Lab relevance

The strongest Alpha Lab transfer is not a particular trading agent. It is the discipline of turning candidate-discovery and launch research into replayable, point-in-time artifacts with explicit memory, checkpoint and failure semantics.

For meme launches, the framework should prefer:

`DISCOVERY -> IMMUTABLE T0 STATE -> VENUE/EXECUTION STATE -> FIXED FOLLOWUPS -> FAILURE/REJECTION MEMORY -> ADJUDICATION`

This aligns with the existing Memes v3 empirical-hardening owner rather than creating a new engine.

## Provenance caveat from owner-supplied prior discussion

A prior user-supplied discussion referenced filenames such as `meme_record.py`, `meme_lab.py` and `meme_snipe.py` as examples of prospective launch-recording design. A search of the current `LLMQuant/awesome-trading-agents` repository did not independently locate those filenames. Therefore they are retained only as `USER_SUPPLIED_WORKFLOW_IDEA`, not attributed to the upstream repository unless a direct source is later recovered.

## Current verdict

`KEEP_AS_EXTERNAL_CAPABILITY_RADAR`

Use it to ask: **has someone solved one of our known gaps better than we have?**

Do not let it rewrite architecture merely because a new agent or MCP appears.