# CoinGecko MCP Research / Recovery Sidecar v1

**Dato:** 2026-08-11  
**Status:** OPERATIONAL_OPT_IN  
**Område:** agent research / source recovery / CoinGecko / GeckoTerminal  
**Primary folder:** `07_PROMPTS_AND_AGENTS/github_agent/`  
**Depends on:** `AGENTS.md`, `07_PROMPTS_AND_AGENTS/github_agent/2026-07-12__research-intake-workflow-v0-1__operational.md`, `00_FMOS/AUTOMATION_ORCHESTRATION_ARCHITECTURE_v2.md`

## Purpose

Provide an optional CoinGecko MCP access path for research-capable agents without making MCP a canonical collector, a production dependency, a market-state owner or a new framework engine.

The sidecar is complementary to the existing deterministic collectors. It is intended for ad hoc research, source recovery, token discovery, liquidity/context checks, CoinGecko breadth/category work and GeckoTerminal onchain/DEX investigation.

## Official transport

Default opt-in transport:

```json
{
  "mcpServers": {
    "coingecko_mcp_research_recovery": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://mcp.api.coingecko.com/mcp"
      ]
    }
  }
}
```

Official documentation:

```text
https://docs.coingecko.com/docs/ai-agents-llm-apps
https://docs.coingecko.com/docs/keyless-public-api
```

The keyless server is the default for this sidecar because the sidecar is non-critical and opt-in. Shared/dynamic rate limits, 429s or temporary unavailability must degrade research only and must never impair canonical collection or weekly execution.

A Pro MCP endpoint may be configured separately when explicitly justified by throughput or research-depth needs. It must not be silently substituted into production collectors or consume a paid budget without the existing API-budget governance.

## Authority boundary

```yaml
canonical_data_owner: false
framework_state_change: false
portfolio_action: false
market_rule_change: false
threshold_change: false
weight_change: false
policy_semantics_change: false
master_monday_authority: false
data_ping_authority: false
weekly_backbone_authority: false
cycle_navigator_authority: false
new_engine: false
new_sensor: false
```

MCP output is `SOURCE_CONTEXT_ONLY` until independently accepted by the relevant existing owner and governance path.

## Allowed uses

- ad hoc token and protocol research;
- CoinGecko coin metadata, market context and category/breadth exploration;
- GeckoTerminal network, token, pool, liquidity, OHLCV and trade context;
- discovery of candidate assets or venues for later bounded research;
- cross-checking an existing observation without replacing its canonical owner;
- recovery of missing source context when the canonical source is unavailable, with explicit degraded provenance;
- Research Lab evidence gathering before red-team evaluation;
- source discovery for microcap, AI, privacy, L1/L2 and sector-comparison work.

## Forbidden uses

The sidecar must not:

- write or overwrite canonical hourly market rows;
- become an input owner for `03_DAILY_CAPTURE_LOGS/`;
- replace Binance or another existing canonical price/derivatives owner;
- alter `02_DATA_PING/` accepted state, gates or truth-layer ownership;
- feed Master Monday or the weekly backbone as an unratified canonical source;
- produce automatic BUY, SELL, deployment, rebuy or exit actions;
- create or change market rules, thresholds, weights, policy evaluators or scoring semantics;
- promote a Research Lab finding into canonical status;
- make MCP availability a prerequisite for scheduled production workflows;
- create a root `.mcp.json` or other repository-wide auto-activation surface without a separately approved architecture change.

## Activation rule

Activation is explicit and per-agent/client. Use the example config under:

```text
research/api_agent/mcp/coingecko_mcp_research_recovery.example.json
```

Do not copy it to repository root as `.mcp.json` by automation.

Before using MCP for a framework-relevant research task:

1. resolve current canonical authority first;
2. use MCP only for the bounded research or recovery question;
3. preserve disagreement with canonical sources rather than replacing them;
4. attach provenance to any durable evidence;
5. route interpretation through the existing Research Lab / framework governance;
6. if MCP is unavailable or rate-limited, mark the research lane `DEGRADED` or `DATA_MISSING` and continue canonical operations unchanged.

## Provenance minimum

Any MCP-derived evidence that is preserved beyond the current conversation should record at minimum:

```yaml
provider: CoinGecko | GeckoTerminal
access_path: COINGECKO_MCP_RESEARCH_RECOVERY
mcp_endpoint_class: KEYLESS_PUBLIC | PRO_AUTHENTICATED
retrieved_at_utc:
asset_or_contract:
network:
method_or_tool:
query_parameters:
source_status: PASS | DEGRADED | DATA_MISSING
canonical_owner_replaced: false
framework_authority: NONE
```

Do not treat a model summary as source bytes. When exact values matter, preserve the returned structured values and enough method/query metadata to reproduce the request.

## Failure semantics

```text
MCP_UNAVAILABLE        -> research lane DEGRADED, canonical pipeline unchanged
MCP_RATE_LIMITED       -> bounded retry/backoff by client, otherwise DEGRADED
MCP_RESULT_CONFLICT    -> preserve conflict, canonical owner remains authoritative
MCP_PROVENANCE_MISSING -> do not promote or persist as decision evidence
MCP_SCOPE_VIOLATION    -> reject the attempted use
```

No MCP failure can block DATA PING, hourly capture, Master Monday, weekly backbone or existing owner collectors.

## Machine-readable contract and validation

Boundary contract:

```text
research/api_agent/mcp/COINGECKO_MCP_RESEARCH_RECOVERY_v1.json
```

Validator:

```text
scripts/api_agent/validate_coingecko_mcp_boundary.py
```

The validator is intentionally deterministic. It checks opt-in status, official keyless endpoint, zero framework authority, forbidden canonical write surfaces and absence of root-level auto-activation.

## Change classification

```yaml
new_engine_created: false
new_skill_created: false
new_market_rule_created: false
new_sensor_promoted: false
canonical_collector_changed: false
master_monday_changed: false
weekly_backbone_changed: false
data_ping_contract_changed: false
portfolio_authority_changed: false
implementation_type: OPTIONAL_AGENT_SIDECAR
```
