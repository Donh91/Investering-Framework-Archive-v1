# Memes v3 Autonomous Alpha Research Workstream v1

**Dato:** 2026-09-09  
**Status:** OPERATIONAL_OWNER_APPROVED  
**Område:** Memes v3 / Alpha Lab / autonomous research  
**Primary folder:** `07_PROMPTS_AND_AGENTS/memes_alpha/`  
**Depends on:** `research/api_agent/API_AGENT_AND_COMPOUNDING_LEARNING_ARCHITECTURE_v1.md`, `research/api_agent/API_INTELLIGENCE_POLICY_v2.json`, `research/api_agent/CAPABILITY_ROUTING_POLICY_v1.json`, `00_FMOS/AUTOMATION_ORCHESTRATION_ARCHITECTURE_v2.md`, `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`

## 1. Purpose

Create a GitHub-native background research workstream for Memes v3 / Alpha Lab that can collect public on-chain and market evidence, monitor known research cases and wallets, discover new candidates, learn from matured outcomes, and autonomously propose bounded improvements without requiring manual GitHub administration from the repository owner.

This is not a new market engine. It is a research workstream inside the existing Research Automation, Research Governance and Compounding Learning architecture. It has no automatic portfolio or trade authority.

## 2. Primary research objective

The workstream should answer one question better over time:

> Which early wallet, liquidity, launch, narrative and propagation patterns repeatedly precede high-quality meme-token expansion, and which patterns are noise, manipulation or survivorship bias?

Priority research surfaces:

- intentional wallet capital deployment;
- repeatable historical wallet hit rate;
- multiple alpha-wallet convergence on the same token;
- deployer, creator and funding-source relationships;
- early holder and supply accumulation structure;
- CTO and community-takeover formation;
- social propagation ordering;
- phrase capture and memetic derivatives;
- semantic stock/token pairing on Robinhood Chain;
- liquidity quality and distribution risk;
- pre-social on-chain acceleration versus social-first acceleration;
- wallet promotion, degradation and retirement from the watch set.

## 3. Non-negotiable provenance rules

Every case and discovery must preserve origin.

```text
USER_SUPPLIED
AUTONOMOUS_DISCOVERY
HISTORICAL_REFERENCE
EXTERNAL_RESEARCH_LEAD
```

Hard rules:

- A user-supplied case may never be rewritten later as autonomous discovery.
- A Telegram, X or KOL claim is a lead, not evidence by itself.
- An incoming token transfer, dust, spam or airdrop is not wallet alpha.
- Intentional deployment requires transaction-level evidence of a wallet-initiated capital commitment or an equivalently strong deterministic classification.
- Wallet labels remain provisional until repeatable historical evidence exists.
- Missing evidence stays unknown.
- Historical outcome knowledge may not be used to backdate discovery timestamps.

## 4. Data-plane split

### Public control plane

`Donh91/Investering-Framework-Archive-v1` owns:

- source contracts and operational semantics;
- collection and classification code;
- deterministic feature definitions;
- research schemas;
- provider-value-free health and receipts;
- Research Governance and Compounding Learning integration;
- model-routing integration;
- experiment and outcome contracts;
- Codex remediation candidates;
- no exact competitive watchlist values.

### Restricted data plane

`Donh91/secrets` owns:

- exact competitive wallet and token identifiers when privacy is desired;
- immutable user-supplied case/watchlist seed snapshots;
- private normalized Alpha Lab research rows;
- public-source raw captures when they are intentionally retained as restricted competitive research evidence;
- private research alerts when they contain exact alpha identifiers.

The exact competitive seed is not a Round 3 raw-provider capture and must not be placed under the existing Round 3 `raw/` validator namespace merely to reuse its folder convention.

Seed contract:

```text
MEMES_ALPHA_PRIVATE_SEED_V1
```

Current seed route:

```text
private_research/memes_alpha/seeds/YYYY/MM/DD/seed.json
```

Credentials remain in GitHub Actions Secrets or an approved runtime secret manager. They never enter either repository as files.

## 5. Preferred free/public source stack

Use deterministic public data first.

Initial source order:

1. Robinhood Chain official RPC / Blockscout explorer APIs for transactions, transfers, holders and contract evidence.
2. DexScreener public API for pool discovery, pair state, boosts, profiles, community takeovers and token/pair activity.
3. GeckoTerminal public API for pools, trades, OHLCV history and historical outcome windows.
4. Ethereum public explorer APIs for historical ERC20 wallet research when the case is on Ethereum.
5. Optional approved public metadata sources only when they add unique evidence.

Do not add paid providers or paid infrastructure without separate owner authorization.

## 6. Adaptive collection cadence

The scheduler may execute hourly, while internal state determines whether the run performs a full refresh or a deterministic no-op.

```text
COLD   = full refresh every 6 hours
WATCH  = full refresh every 2 hours
HOT    = full refresh every 1 hour
EVENT  = immediate bounded follow-up on a new high-value event when existing GitHub orchestration supports it safely
```

Escalation must be evidence-driven. HOT/EVENT examples include:

- a watched historically strong wallet intentionally buys a previously unseen microcap;
- two or more independently qualified wallets converge on one token;
- rapid concentration/accumulation change plus real liquidity growth;
- CTO/community takeover appears while wallet accumulation rises;
- social propagation accelerates after an on-chain lead event;
- a provisional wallet creates another matured winning case;
- a known high-risk distribution pattern appears in an active case.

Routine noise should no-op rather than consume API budget.

## 7. Deterministic event classification

The first stage must be code and rules, not an LLM.

Required event classes:

```text
INTENTIONAL_BUY
PASSIVE_RECEIPT
DUST_OR_SPAM
SELL_OR_DISTRIBUTION
FUNDING_SOURCE_LINK
NEW_TOKEN_ACQUISITION
MULTI_WALLET_CONVERGENCE
SUPPLY_ACCUMULATION_CHANGE
CTO_OR_COMMUNITY_TAKEOVER
SOCIAL_METADATA_CHANGE
LIQUIDITY_QUALITY_CHANGE
WALLET_QUALITY_REVIEW_DUE
```

Every event must preserve source references, observed timestamp, chain, transaction/pool identity where available, origin class and missingness.

## 8. Research features, not buy scores

The workstream may maintain research features such as:

- wallet quality;
- historical hit-rate coverage;
- entry earliness;
- independent-wallet convergence;
- accumulation persistence;
- liquidity quality;
- narrative propagation state;
- propagation lead/lag;
- distribution/rug-risk evidence;
- confidence and missingness.

No feature or aggregate may become an automatic BUY, SELL, position-size or portfolio instruction.

## 9. Outcome and learning loop

Every autonomous discovery or meaningful watched-wallet event should freeze a research row before later outcomes are known.

Default observation windows may include:

```text
1 hour
6 hours
24 hours
7 days
```

Where supported, attach price/liquidity/volume outcomes, survival, drawdown, propagation ordering and later wallet behavior.

```text
observe
-> freeze event/case row
-> wait for maturity
-> attach deterministic outcomes
-> classify false positive / useful lead / unresolved
-> update wallet evidence history
-> pass repeated errors or successes into existing Compounding Learning Controller
-> generate a bounded falsifiable child proposal when justified
-> route through Research Memory Novelty, Decision Impact / VOI, Adversarial Sentinel and Meta Orchestrator
```

The existing Compounding Learning Controller remains owner of what to test next. Memes v3 does not create a parallel self-learning engine.

## 10. Wallet promotion and degradation

Wallet status may evolve only from matured evidence.

```text
PROVISIONAL
WATCH
QUALIFIED_ALPHA
DEGRADED
RETIRED
CONTEXT_ONLY
```

Promotion should require multiple independent matured cases or similarly strong reproducible evidence. One historical win is insufficient. Repeated dust, passive receipts, post-pump entries, low-liquidity artifacts or poor forward hit rate reduce confidence. All state changes require a durable reason and previous state.

## 11. Model routing

Follow current `CAPABILITY_ROUTING_POLICY_v1` and API budget owners.

- deterministic collection/classification first;
- Luna for cheap extraction, deduplication and routine triage when a model adds value;
- Terra/Sol only for higher-value conflict review or synthesis;
- Astra only when a future qualified task genuinely needs architecture-level, cross-domain or difficult research capability;
- no routine Astra burn;
- cheapest qualified executor wins;
- never exceed current API hard stop or lane caps without explicit owner authorization.

Feed models deterministic collector evidence. The model does not need to browse autonomously when source acquisition can be deterministic.

## 12. Research-value routing

Heavy research is justified only when novelty and expected research value are high, such as:

- two qualified wallets converge before social propagation;
- a provisional wallet's historical hit rate materially changes;
- a new repeatable propagation sequence appears;
- source disagreement changes the case interpretation;
- a case falsifies an active Alpha Lab hypothesis;
- an implementation/data gap blocks a high-value research question.

Otherwise continue deterministic observation.

## 13. Adaptive development and autonomous expansion

The workstream may autonomously:

- discover evidence gaps;
- propose additional public data sources;
- propose better deterministic classifiers;
- propose new child hypotheses;
- propose wallet promotion/degradation tests;
- propose bounded code improvements;
- create research-to-Codex candidates under existing Codex Intake governance when the improvement is code-local and reproducible;
- retire redundant research paths after evidence shows low incremental value.

It may not autonomously:

- create a new canonical market rule;
- change portfolio logic;
- create automatic trades;
- change API budgets;
- authorize paid data;
- weaken provenance/privacy controls;
- self-promote a hypothesis;
- rewrite historical event timestamps/outcomes;
- self-merge Codex changes;
- create an overlapping parallel research-governance stack.

## 14. User-facing alert policy

The owner should not receive routine status noise.

Human-facing alerts are reserved for:

```text
HIGH_SIGNAL_NEW_BUY
MULTI_ALPHA_WALLET_CONVERGENCE
PROVISIONAL_WALLET_PROMOTED_OR_DEGRADED
PRE_SOCIAL_ONCHAIN_ACCELERATION
MATERIAL_DISTRIBUTION_OR_RISK_CHANGE
NEW_HIGH_VALUE_RESEARCH_FINDING
RESEARCH_PIPELINE_BLOCKED
```

A routine scan with no meaningful change produces no alert.

## 15. Initial pilot success criteria

The first implementation succeeds only if it can:

1. Read the private seed through an explicit cross-repository route without exposing it publicly.
2. Poll at least Robinhood Chain and Ethereum public evidence deterministically.
3. Distinguish intentional wallet deployment from passive receipt in positive and negative fixtures.
4. Detect a synthetic multi-wallet convergence event.
5. Persist immutable research event rows with origin and source lineage.
6. Preserve USER_SUPPLIED versus AUTONOMOUS_DISCOVERY truthfully.
7. Produce no portfolio action.
8. Stay inside existing API budget and use zero model calls when no model value exists.
9. Produce provider-value-free public health/readback.
10. Run at least 24 hours in shadow mode without duplicate-alert spam, private-data leakage or uncontrolled API usage before alert escalation is trusted.

## 16. Implementation route

Implementation is code work and follows existing Codex routing.

```text
owner-approved operational contract
-> bounded CODEX_RESEARCH_CANDIDATE
-> Remediation Maturation Controller
-> CODEX_READY or NEEDS_MORE_EVIDENCE
-> isolated Codex branch
-> deterministic positive and negative tests
-> high-impact workflow safety gate and safepoint before workflow changes
-> PR and independent review
-> merge only after governance permits it
-> post-fix / post-activation observation
```

No manual GitHub steps should be delegated to the repository owner when an authorized agent or existing automation can perform them safely.

## 17. Kill / rollback conditions

Pause the workstream on:

```text
PRIVATE_WATCHLIST_LEAK
CREDENTIAL_EXPOSURE
UNBOUNDED_API_SPEND
DUPLICATE_ALERT_STORM
AUTONOMOUS_DISCOVERY_BACKDATED
PASSIVE_RECEIPT_MISCLASSIFIED_AS_ALPHA_REPEATEDLY
SOURCE_RATE_LIMIT_FAILURE_WITHOUT_BACKOFF
PROVENANCE_BREAK
CROSS_REPO_BINDING_FAILURE
PORTFOLIO_ACTION_EMITTED
```

The correct failure mode is explicit degradation or pause, never fabricated continuity.
