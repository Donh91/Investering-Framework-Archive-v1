---
name: meme-alpha-supervisor
description: 'Operate Meme Alpha Lab as a research-only background subsystem. Use for meme/microcap token cases, contract addresses, wallet forensics, caller/cabal hypotheses, launch replays, smart-money provenance, source-authentication, prospective Easter-egg trials, research queue triage, 24/7 Meme Alpha runtime health, or adaptation of external wallet-intelligence tools. Differentiator: separates discovery from source authentication, outcome maturation and verified on-chain evidence, preserves point-in-time labels, prefers deterministic/free sources before API spend, and routes code findings into existing governed owners instead of creating a parallel engine.'
---

# Meme Alpha Supervisor

## Purpose

Keep `Donh91/secrets/private_research/memes_alpha` alive as a continuously worked research subsystem while preserving the framework's existing scientific, API-budget, cross-repository and no-execution boundaries.

This skill does not own trading, portfolio actions, market rules or canonical promotion. It does not create a separate experiment engine. Scientific strategy/factor tests continue through the existing experiment lifecycle and AUTO_TRADING owner.

## Required read order

1. Run `canonical-context-router`.
2. Read `AGENTS.md`, `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md` and `CROSS_REPO_AGENT_CONTEXT_MAP.json`.
3. Read `research/api_agent/meme_alpha/MEME_ALPHA_RUNTIME_POLICY_v1.json`.
4. Read `research/api_agent/meme_alpha/MEME_ALPHA_PROSPECTIVE_HARDENING_v1.json` for prospective Easter-egg/cohort work.
5. If restricted Meme Alpha material is needed, read `Donh91/secrets/AGENTS.md`, `README.md`, the Meme Alpha runtime contract and only the exact relevant files.
6. For prospective wallet or event evidence, compose with `prospective-evidence-ledger`.
7. For claims of edge, first-party provenance or promotion, compose with `research-lab-red-team`.
8. For bounded code defects, use `codex-intake` only after deterministic evidence exists.
9. Use `archive-governance` before any repository write.

## Runtime principles

```text
FREE / DETERMINISTIC FIRST
DISCOVERY IS NOT AUTHENTICATION
DISCOVERY_COMPLETE IS NOT OUTCOME_MATURED
POINT-IN-TIME BEFORE HINDSIGHT
SELF-INITIATED TRADE BEFORE ATTRIBUTION
NEGATIVE CASES BEFORE PERFORMANCE CLAIMS
FALSE NEGATIVES COUNT TOO
ADVERSARIAL SOURCE CHECK BEFORE FIRST-PARTY CLAIM
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

### Blockscout exact-CA enrichment

For EVM / Robinhood Chain work, Blockscout is a first-class deterministic enrichment and verification source after discovery or exact candidate identification.

Use the two surfaces according to execution context:

- ChatGPT interactive research: use the installed Blockscout connector when available for bounded address, transaction, ABI/source and transfer forensics.
- Repository/runtime research: use `scripts/api_agent/meme_alpha_blockscout.py`. It reads `BLOCKSCOUT_API_KEY` from runtime environment when available, prefers the authenticated unified PRO endpoint for chain 4663, and falls back to the Robinhood chain public Blockscout endpoint when permitted.
- Cross-repository credential routing: GitHub Actions secrets are repository-scoped. The autonomous restricted runtime executes in `Donh91/secrets`, so `BLOCKSCOUT_API_KEY` must exist in that repository's Actions secret scope as well as anywhere it is used in the public control plane. A working secret in the public repository does not authenticate the restricted runtime.

Required order for a candidate is:

`DISCOVERY -> EXACT_CA -> BLOCKSCOUT_ENRICHMENT -> FIRST_PARTY_CROSS_BIND -> MARKET/SELLABILITY -> OUTCOME`.

Blockscout does not replace the Pons/RPC launch-discovery owner, first-party authentication, market-price/liquidity sources, sellability evidence or the prospective evidence ledger. It is enrichment, not a second scanner.

Persist immutable launch/origin facts once where appropriate. Time-stamp mutable fields such as holder count, exchange rate and volume. Missing/quota/transport failure is `DEGRADED/UNAVAILABLE`, never negative chain evidence. Never persist, print or place `BLOCKSCOUT_API_KEY` in URLs, receipts, issues, prompts or repository files.

The exact-CA enricher is intentionally fail-open toward the existing discovery row: enrichment failure must never erase a valid chain/factory launch event. Project ownership remains unproven until the existing source-authentication gate passes.

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
- preserve completion receipts and source provenance;
- prefer event-driven dispatch for P0 launch/discovery work;
- record P0 queue-age breach after 60 minutes, P1 after 240 minutes and P2 after 1440 minutes;
- never rewrite the prospective discovery timestamp to hide queue latency.

## Prospective Easter-egg cohort discipline

The first prospective program is a measurement program, not a winner-finding contest.

### Trial state

Use separate states:

```text
DISCOVERY_OPEN
DISCOVERY_COMPLETE
OUTCOME_MATURING
OUTCOME_MATURED
INVALIDATED
```

`DISCOVERY_COMPLETE` means only that the immutable point-in-time discovery snapshot exists. It does not count toward the minimum method-review denominator. Only a unique ecosystem trial in `OUTCOME_MATURED` counts toward the minimum 20 trials.

### Denominator hierarchy

Use:

```text
ECOSYSTEM TRIAL
  -> ARTIFACT CANDIDATE
      -> TOKEN MATCH
```

Artifact and token children never increase the method-level trial count. One ecosystem cannot create ten independent trials merely because it yields ten strings or tokens.

### Cohort selection

Trial 001 is a grandfathered pilot. Trial 002 and later require a frozen eligibility manifest before ecosystem selection, archaeology or live-token search. Preserve every eligible ecosystem and every exclusion/reason. Use deterministic selection from the frozen manifest and never choose a case because a meme already pumped.

### Lineage

From Trial 002 onward, preserve at minimum:

```text
method_version
method_sha256
runtime_contract
runtime_input_sha256
runtime_output_sha256
policy_sha256
prompt_sha256
model_id
model_snapshot_or_version
query_manifest_sha256
retrieval_manifest_sha256
```

### Outcome maturation

Do not overwrite the immutable discovery snapshot. Mature lead time, social propagation, MFE, MAE, sellability, realizable return, matched controls, missed-winner audit and final falsifier in separate records.

Positive alpha requires executable/sellable evidence. Peak market cap alone is never realizable alpha.

Every matured ecosystem trial must include a missed-winner audit. A sellable ecosystem winner missed by the frozen discovery process counts against recall.

### Method review and kill criteria

Do not review/promote the Easter-egg method before at least 20 valid `OUTCOME_MATURED` unique ecosystem trials. At review, kill or redesign rather than extend the sample merely because results disappoint if any preregistered kill criterion fires, including zero sellable surviving signals, no precision edge versus matched controls, materially poor missed-winner recall without compensating precision, broken cohort-selection integrity or missing required lineage.

## Source authentication and Easter-egg archaeology

Be aggressive in discovery and hostile in verification.

For new chains, launchpads, protocols and large crypto products, actively search for:

- mascots, examples, test tokens and sample contracts;
- old commits and deleted/superseded files;
- SDK examples, docs, metadata and naming conventions;
- candidate tickers/CAs matching first-party lore;
- dormant narratives that may later propagate socially.

A discovery hit is only `CANDIDATE`. Never infer first-party ownership from any combination of repository name, self-description, realistic source code, exact CA, commit chronology or GitHub `Verified` signature.

Every provenance assertion must carry a structured claim type such as `PROJECT_OWNERSHIP`, `REPOSITORY_OWNERSHIP`, `MASCOT_CANONICITY`, `LORE_CANONICITY`, `TOKEN_ISSUANCE`, `TOKEN_CA_OWNERSHIP` or separate `CTO_COMMUNITY_LEGITIMACY`.

Before `AUTHENTICATED_FIRST_PARTY`, require all applicable controls:

1. at least two independent project-controlled trust anchors external to the source being authenticated;
2. at least two different anchor categories;
3. at least two distinct `control_root_id` values so two pages under the same control root do not masquerade as independent anchors;
4. repository forensics covering owner/account age, author identity/email, fork/clone ancestry, alternate repositories, copied code and timeline consistency;
5. an adversarial red-team attempt to explain the evidence as a look-alike/spoof;
6. for exact token/CA claims, structured `TOKEN_CA_OWNERSHIP` plus HIGH-confidence on-chain binding to authenticated project infrastructure;
7. no unresolved/blocking red-team finding or repository-forensics blocker.

Source states are:

```text
NOT_APPLICABLE
UNASSESSED
CANDIDATE
AUTHENTICATED_FIRST_PARTY
INVALIDATED_FIRST_PARTY
CONFLICTED
```

If authentication fails, `first_party_claim_allowed` must be false. Keep community/CTO legitimacy as a separate thesis. A real CTO never inherits official provenance from a spoofed origin story.

If a previously admitted source is invalidated, preserve the failure as a negative/adversarial benchmark and propagate the revocation into descendant research. Do not silently rewrite history. PONSCUPINE is the regression benchmark for this exact failure mode.

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

A qualified v1.2 run should return:

```yaml
status: READY | DEGRADED | BLOCKED
input_sha256:
verified_findings: []
disconfirming_evidence: []
uncertainties: []
wallet_candidates: []
network_connections: []
source_authentication:
  scope: NONE | PROJECT_SOURCE | TOKEN_SOURCE | TOKEN_CA_BINDING | CTO_COMMUNITY
  state: NOT_APPLICABLE | UNASSESSED | CANDIDATE | AUTHENTICATED_FIRST_PARTY | INVALIDATED_FIRST_PARTY | CONFLICTED
  claim_types: []
  first_party_claim_allowed: false
  external_trust_anchors: []
  repository_forensics: []
  onchain_bindings: []
  red_team_findings: []
  gate_reasons: []
source_urls: []
next_research_steps: []
development_candidates: []
priority_after_run: LOW | MEDIUM | HIGH | CRITICAL
```

Each external trust anchor should include `control_root_id`.

Development candidates are proposals only. They may identify a reproducible gap and its existing owner, but may not modify production code, self-merge or grant new authority.

## Relationship to AUTO_TRADING and #908

Meme Alpha discovery/wallet research may run continuously without Codex. Any claim that a wallet/network/source signal creates repeatable trading edge must enter the existing scientific owner, preserve immutable trial count and point-in-time evidence, and satisfy the leakage and prospective requirements already established under AUTO_TRADING.

FOMO Radar, STAMPEDE or similar upstream tools are research inputs/benchmarks. Do not copy their thresholds, wallet scores or success claims as truth.

## Stop conditions

Stop or mark blocked on:

```text
PRIVATE_DATA_AUTHORITY_UNAVAILABLE
PRIVATE_BINDING_INCOMPLETE
CREDENTIAL_EXPOSURE_SUSPECTED
BUDGET_HARD_STOP
UNTRUSTED_SOURCE_ONLY
SOURCE_AUTHENTICATION_REQUIRED
SOURCE_AUTHENTICATION_CONFLICTED
SOURCE_PROVENANCE_INVALIDATED
SELLABILITY_UNKNOWN_FOR_POSITIVE_ALPHA_CLAIM
POINT_IN_TIME_PROVENANCE_MISSING
PROSPECTIVE_ELIGIBILITY_MANIFEST_MISSING
PROSPECTIVE_LINEAGE_INCOMPLETE
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
