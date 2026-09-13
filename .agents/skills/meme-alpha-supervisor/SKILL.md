---
name: meme-alpha-supervisor
description: 'Operate Meme Alpha Lab as a research-only background subsystem. Use for meme/microcap token cases, contract addresses, wallet forensics, caller/cabal hypotheses, launch replays, smart-money provenance, research queue triage, 24/7 Meme Alpha runtime health, or adaptation of external wallet-intelligence tools. Differentiator: separates discovery from verified on-chain evidence, preserves point-in-time wallet labels, prefers deterministic/free sources before API spend, and routes code findings into existing governed owners instead of creating a parallel engine.'
---

# Meme Alpha Supervisor

## Purpose

Keep `Donh91/secrets/private_research/memes_alpha` alive as a continuously worked research subsystem while preserving the framework's existing scientific, API-budget, cross-repository and no-execution boundaries.

This skill does not own trading, portfolio actions, market rules or canonical promotion. It does not create a separate experiment engine. Scientific strategy/factor tests continue through the existing experiment lifecycle and AUTO_TRADING owner.

## Required read order

1. Run `canonical-context-router`.
2. Read `AGENTS.md`, `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md` and `CROSS_REPO_AGENT_CONTEXT_MAP.json`.
3. Read `research/api_agent/meme_alpha/MEME_ALPHA_RUNTIME_POLICY_v1.json`.
4. If restricted Meme Alpha material is needed, read `Donh91/secrets/AGENTS.md`, `README.md`, the Meme Alpha runtime contract and only the exact relevant files.
5. For prospective wallet or event evidence, compose with `prospective-evidence-ledger`.
6. For claims of edge or promotion, compose with `research-lab-red-team`.
7. For bounded code defects, use `codex-intake` only after deterministic evidence exists.
8. Use `archive-governance` before any repository write.

## Runtime principles

```text
FREE / DETERMINISTIC FIRST
POINT-IN-TIME BEFORE HINDSIGHT
SELF-INITIATED TRADE BEFORE ATTRIBUTION
NEGATIVE CASES BEFORE PERFORMANCE CLAIMS
ONE BOUNDED TASK PER RUN
NO CODE AUTHORITY FROM RESEARCH
NO PORTFOLIO AUTHORITY
```

### Free-first order

Prefer, in order:

1. already archived evidence and deterministic local transforms;
2. GitHub/public developer sources;
3. free or already-authorized provider/API bindings available to the runtime;
4. OpenAI Luna with bounded web research;
5. Sol only for material conflict, high-value forensics or failed lower-cost adjudication;
6. Astra only by separate explicit policy/mission, never as the default heartbeat model.

Do not claim that a ChatGPT app plugin is callable from GitHub Actions unless a real API/MCP/runtime binding exists. App-local availability and unattended runtime availability are different capabilities.

## Queue contract

Eligible Meme Alpha material may enter from:

```text
private_research/memes_alpha/research_leads/
private_research/memes_alpha/cases/
private_research/memes_alpha/discovery/
private_research/memes_alpha/wallet_research/
```

The runtime must:

- compute immutable SHA-256 identity for the exact input;
- avoid reprocessing an unchanged input;
- re-open work only when the source changes or an explicit follow-up task is created;
- process at most one bounded task per heartbeat;
- leave an empty queue as a no-model-call no-op;
- use bounded retries and dead-letter repeated failures;
- preserve completion receipts and source provenance.

## Wallet and cabal forensics

Never equate token receipt with a voluntary buy.

For every wallet claim distinguish where evidence permits:

```text
SELF_INITIATED_TRADE
ROUTER_ATTRIBUTED_TRADE
DIRECT_TRANSFER
DUST_OR_SEEDED_RECIPIENT
UNKNOWN
```

Track separately:

- first buy vs repeat accumulation;
- funding source and wallet age;
- distinct-wallet count vs repeated transactions;
- pre-call vs post-call entry;
- realized exits vs touched MFE;
- liquidity and sellability at observation time;
- current vs historical wallet conviction;
- caller/social propagation vs on-chain causality.

A wallet is `PROVISIONAL` until its history is independently supported. Later wallet quality may not be retroactively applied to earlier alerts.

## Research output

A qualified run should return:

```yaml
status: READY | DEGRADED | BLOCKED
input_sha256:
verified_findings: []
disconfirming_evidence: []
uncertainties: []
wallet_candidates: []
network_connections: []
source_urls: []
next_research_steps: []
development_candidates: []
priority_after_run: LOW | MEDIUM | HIGH | CRITICAL
```

Development candidates are proposals only. They may identify a reproducible gap and its existing owner, but may not modify production code, self-merge or grant new authority.

## Relationship to AUTO_TRADING and #908

Meme Alpha discovery/wallet research may run continuously without Codex. Any claim that a wallet/network signal creates repeatable trading edge must enter the existing scientific owner, preserve immutable trial count and point-in-time evidence, and satisfy the leakage and prospective requirements already established under AUTO_TRADING.

FOMO Radar, STAMPEDE or similar upstream tools are research inputs/benchmarks. Do not copy their thresholds, wallet scores or success claims as truth.

## Stop conditions

Stop or mark blocked on:

```text
PRIVATE_DATA_AUTHORITY_UNAVAILABLE
PRIVATE_BINDING_INCOMPLETE
CREDENTIAL_EXPOSURE_SUSPECTED
BUDGET_HARD_STOP
UNTRUSTED_SOURCE_ONLY
SELLABILITY_UNKNOWN_FOR_POSITIVE_ALPHA_CLAIM
POINT_IN_TIME_PROVENANCE_MISSING
REPEATED_RUNTIME_FAILURE
```

## Authority

```yaml
portfolio_action: false
automatic_trading: false
canonical_promotion: false
framework_state_change: false
market_rule_change: false
model_weight_change: false
automatic_merge: false
```
