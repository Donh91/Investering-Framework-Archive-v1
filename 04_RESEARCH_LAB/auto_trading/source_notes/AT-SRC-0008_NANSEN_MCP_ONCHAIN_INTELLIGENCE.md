# AT-SRC-0008 — NANSEN MCP / ONCHAIN INTELLIGENCE

Date captured: 2026-09-11
Status: RESEARCH_QUEUED
Evidence class: PRIMARY PRODUCT/DOCUMENTATION EVIDENCE FOR CAPABILITIES; NO TRADING EDGE ASSUMED
Authority: NONE_BY_ITSELF

## Source anchors

- User-supplied setup/docs link: https://docs.nansen.ai/mcp/grok
- Nansen MCP registry: https://github.com/nansen-ai/nansen-mcp-registry
- Nansen for Agents: https://agents.nansen.ai/
- Nansen API overview: https://nansen.ai/api
- Nansen Academy, MCP intro: https://academy.nansen.ai/articles/2711728-get-started-with-nansen-mcp
- Nansen Academy, data/coverage: https://academy.nansen.ai/articles/3084751-data-and-coverage-for-nansen-mcp

## What is directly supported by current Nansen material

Nansen exposes onchain intelligence to agents through MCP, API and CLI. Public Nansen material describes capabilities including:

- Smart Money tracking/signals;
- wallet/address/entity profiling;
- wallet PnL analysis;
- token discovery/screening;
- token-holder analysis;
- DEX trades;
- exchange flows/netflows;
- flow intelligence by holder segment;
- transaction lookup;
- trending-token discovery;
- portfolio/DeFi context;
- multi-chain coverage;
- a large labeled-address corpus.

Nansen's public materials currently describe 30+ MCP tools and 400M+ labeled addresses, while chain-count claims vary by page/version (roughly 18+ to 25+). Treat the exact current chain count as versioned provider metadata, not a framework invariant.

The public MCP registry currently identifies:

- server URL: `https://mcp.nansen.ai/ra/mcp`
- transport: Streamable HTTP
- authentication: API key header `NANSEN-API-KEY`

Nansen public API materials state that API access does not require a Pro subscription and advertise credit purchases at USD 10 per 10,000 API credits, with endpoint-specific credit costs and rate limits. This is provider pricing metadata only and must be rechecked before any paid acquisition.

## Why this matters to Investering Framework

The strongest relevance is NOT 'let an agent ask Nansen what to buy'.

The strongest relevance is that Nansen may provide a high-level labeled onchain feature layer that would otherwise require substantial wallet/entity classification work internally.

Candidate use cases:

1. **Alpha Lab / memes / early-token research**
   - first-buyer quality;
   - recurring profitable-wallet participation;
   - smart-money accumulation vs distribution;
   - holder concentration and holder-type changes;
   - wallet PnL/profile context;
   - DEX trade flow;
   - entity labels and exchange interactions;
   - candidate wallet-cluster validation.

2. **AUTO_TRADING research**
   - point-in-time onchain features as upstream strategy inputs;
   - regime-conditioned smart-money/flow features;
   - prospective feature capture for forward tests;
   - historical signal replay where endpoint history is available and licensed;
   - provider-vs-open-source feature ablation.

3. **Astra-era research infrastructure**
   - Nansen MCP can be treated as a capability/tool provider under the existing Astra/Agents API execution harness;
   - Astra should query Nansen only when an unresolved research question requires Nansen-specific labels or analytics;
   - Nansen must not become a new market-state owner or orchestration engine.

## Important architectural boundary

Nansen also advertises transaction/trading-oriented product capabilities. Those are OUT OF SCOPE for this research vault.

No Nansen MCP/API tool may acquire execution authority, signing authority, exchange authority or wallet authority through this source note.

Permitted scope here is read-only research/data use.

## Main risk: expensive duplication

Nansen may overlap with data already present or derivable from:

- existing onchain/history archives;
- exchange/DEX data;
- token-holder snapshots;
- wallet-cluster work;
- other data providers already in the framework;
- public chain explorers;
- future direct-indexing pipelines.

Therefore every Nansen field must pass a duplicate-coverage audit before recurring or historical paid use.

Classify each desired field as:

- `EXISTING_EXACT`
- `EXISTING_APPROXIMATE`
- `DERIVABLE_FREE`
- `NANSEN_LABEL_ADVANTAGE`
- `NANSEN_HISTORY_ADVANTAGE`
- `PAID_GAP`
- `NOT_NEEDED`

The key question is not 'can Nansen provide this?' but 'does Nansen add information, labeling quality, historical depth or retrieval efficiency that we do not already possess?'

## Highest-value hypotheses

### NANSEN-H1 — label value
Nansen wallet/entity labels add measurable predictive or explanatory value beyond raw wallet-flow features.

### NANSEN-H2 — Smart Money is conditional, not universal
Smart-money accumulation is only useful in specific market/regime/liquidity conditions and should not be treated as a universal bullish signal.

### NANSEN-H3 — wallet-quality beats raw wallet count
A small set of historically strong wallets may contain more signal than broad holder/buyer growth alone.

### NANSEN-H4 — provider label drift matters
Wallet labels and rankings may change over time. Historical research must preserve point-in-time label semantics where possible rather than applying today's labels retrospectively without caveat.

### NANSEN-H5 — incremental feature value
Nansen-derived features should survive an ablation test against simpler/free baselines after endpoint costs, latency and licensing constraints.

## Point-in-time / leakage requirements

Every research capture must preserve, where obtainable:

- `effective_at`
- `observable_at`
- `retrieved_at`
- chain
- token / wallet identifier
- endpoint/tool
- provider version / response schema version if available
- label/ranking window if applicable
- raw-vs-derived field distinction

Historical research must explicitly test for retrospective label leakage. A wallet classified as 'Smart Money' today must not automatically be assumed to have carried that label at a historical decision timestamp.

## Cost policy

1. Use existing archive data first.
2. Use public/free chain data second.
3. Use limited live Nansen queries prospectively where they answer a unique question.
4. Measure endpoint credit burn per useful feature.
5. Buy/backfill only the minimum historical gap needed for a frozen experiment.
6. Never run broad paid polling simply because MCP makes it easy.

## Current verdict

**HIGH RESEARCH VALUE, CONDITIONAL ACQUISITION.**

Nansen is potentially one of the more valuable external providers for Alpha Lab and future Astra-era onchain strategy research because its differentiation is labeled entities/wallets, not merely raw chain data.

But the correct integration is as a governed read-only data/capability adapter with strict duplicate and cost control, not as a signal oracle and not as an execution layer.
