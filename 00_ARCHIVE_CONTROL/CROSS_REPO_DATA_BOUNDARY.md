# Cross-repository data boundary

Status: `CANONICAL_CROSS_REPO_ROUTING_AUTHORITY`  
Effective: `2026-08-23`  
Scope: agent context, source provenance, restricted market data, credentials, Round 3 collection and cross-repository automation  
Machine map: `00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json`

## Authority and precedence

This file is the public routing authority for the three-plane architecture. It overrides older statements that assume all framework data is held in one repository, that a private destination is still absent, or that `Donh91/Cycle-navigator-` is a current repository route.

It does not change any market rule, source contract, threshold, weight, portfolio rule, Master Monday semantic, Cycle Navigator semantic or frozen Round 3 research commitment. Historical receipts remain historical evidence and are not rewritten.

## Three-plane architecture

| Plane | Authority | May contain | Must not contain |
|---|---|---|---|
| Control plane | `Donh91/Investering-Framework-Archive-v1` | canonical framework state, code, contracts, schemas, governance, research decisions, source-contract IDs, provider-value-free provenance receipts, health status, agent instructions and cross-repository pointers | raw or normalized restricted provider values, credentials |
| Restricted data plane | `Donh91/secrets` | raw/restricted provider payloads, private normalized market data, immutable capture receipts, restricted source-health evidence and private object-store manifests | canonical framework decisions, public market-rule authority, credentials committed as files |
| Credential plane | GitHub Actions Secrets or an explicitly approved runtime secret manager/short-lived workload identity | API keys, tokens, passwords and deployment credentials | ordinary files in either repository, logs, receipts or issue/PR text |

`Donh91/secrets` is a restricted data repository. Its name does not make it a password or credential repository.

## Mandatory read order

Any new ChatGPT Work thread, Claude/Cowork session, Codex task, agent, skill, research controller or automation that may touch source data must:

1. read `Donh91/Investering-Framework-Archive-v1/AGENTS.md`;
2. read the control-plane canonical index, addendum registry, archive map and this file;
3. read `00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json` and the current domain contract/status pointer;
4. determine whether the requested evidence class is public metadata or restricted provider data;
5. if restricted data is required and access is authorized, read `Donh91/secrets/AGENTS.md`, `README.md`, `GOVERNANCE/CROSS_REPO_DATA_BOUNDARY.md`, `GOVERNANCE/PRIVATE_DATA_BOUNDARY.md` and the exact private binding/health record;
6. bind all conclusions to immutable commits and exact paths, never merely to either repository's moving `main`;
7. stop with `PRIVATE_DATA_AUTHORITY_UNAVAILABLE` when restricted evidence is necessary but cannot be read.

Public-only work may stop after step 4. Lack of access to the restricted plane is not permission to infer values, search for them in the public repository or substitute public proxies.

## Data classification and movement

Allowed from restricted to public:

- private repository name;
- immutable private commit SHA;
- exact private receipt or dataset path;
- byte length and SHA-256;
- source-contract ID and schema identifier/version;
- capture, retrieval, availability and normalization timestamps;
- row or object counts, timestamp ranges, gap counts, completeness class and provider-value-free source health;
- public research decisions made only after the relevant analysis gate is opened.

Forbidden from restricted to public:

- raw payload bodies;
- order-book levels, prices, sizes, funding values, open interest, volatility values or other provider-derived market values;
- samples, excerpts, reconstructed values or small aggregates that disclose restricted values;
- object-store credentials, signed URLs, access tokens or sensitive storage coordinates;
- unredacted logs or exception text that contains provider values or credentials.

Movement from public to restricted may include contracts, schemas, collector code and immutable control-plane commit identifiers. It does not transfer canonical decision authority to the restricted repository.

## Required private dataset binding

Every private dataset or immutable capture used by an agent must be bound by one restricted-plane receipt containing, at minimum:

```text
private_repository
private_commit_sha_reachable_from_main
exact_path
bytes
sha256
source_contract_id
provider / venue / instrument_id
collector_commit_sha
schema_id / schema_version / schema_sha256
retrieval_start_utc / retrieval_end_utc
availability_at_utc / captured_at_utc / normalized_at_utc when applicable
row_or_object_count
timestamp_range
gap_count and missingness/completeness status
validation_status
```

When the raw payload is stored in private object/blob storage, the exact object key, immutable object version, storage checksum and retention state live in the private manifest. The public receipt binds to the private commit and exact manifest path, plus its bytes and SHA-256. Public pointers must remain provider-value-free.

Mutable branch names, workflow artifact URLs and latest-file names alone are not provenance.

## Round 3 analysis firewall

Current authority remains:

- mode: `PROSPECTIVE_COLLECTION_ONLY`;
- Round 1 and Round 2: closed evidence, never reopened or rescored by Round 3;
- historical findings: maximum classification `FORWARD_TEST` after separate review;
- hypothesis testing: `OFF`;
- outcome scoring: `OFF`;
- paid historical acquisition: not authorized;
- raw provider values in the control plane: forbidden;
- collection is not evidence of effect, and source health is not an outcome row.

No agent may read Round 3 provider values for hypothesis discovery, directional interpretation, threshold selection, outcome linkage or informal scoring before the frozen analysis gate passes. A private source-health read is limited to source contract, timestamps, sequence/gap status, schema, counts and completeness.

## Verified Round 3 state

The following commitments were verified as ancestors of their repository's `main` during the 2026-08-23 audit:

| State | Immutable reference | Verified result |
|---|---|---|
| V2 durable commitment | control-plane commit `3aad2a9da12992949665e0e30ef8986136e1dfca` | reachable |
| Private data-plane binding | control-plane commit `be9f6f447ddf9e9370e42718b799ace11c1dcde2` | reachable |
| Private collection activation public receipt | control-plane commit `c1be6e87e9462e078065b87448717f8900326380` | reachable |
| Private source canary | workflow run `32633097190` | `PASS` |
| SC01 OKX ETH OI | `Donh91/secrets` | private prospective collection active |
| SC03 OKX realized funding | `Donh91/secrets` | private prospective collection active |
| SC14 Deribit option chain | `Donh91/secrets` | private prospective collection active |
| SC06 Binance depth | persistent runtime required | not fully active |

Audit snapshot, not a moving-latest pointer:

```text
verified_at_utc: 2026-08-23T11:08:24Z
control_main_at_audit: b3ebc5ea194cc7e0a26176b93f2be1baab2919ca
restricted_main_at_audit: a9e735f38959ef636427ed77a1e9b6552aa98f62
```

For current collection state, re-read both repositories and bind the result to the then-current commit SHAs.

## SC06 boundary

SC06 retains the frozen quality requirements:

- at least `99.9%` sequence-contiguous eligible time;
- at least `90%` deterministic snapshot coverage;
- gaps trigger explicit invalidation and re-bootstrap, never interpolation.

GitHub Actions remains suitable for validation, deployment and receipts, but not as the long-running websocket runtime. The reviewed implementation architecture is `06_RESEARCH_LAB/round3_new_information_v1/SC06_PERSISTENT_RUNTIME_AND_STORAGE_ARCHITECTURE.md`. No paid runtime or storage may be deployed without explicit human authorization.

## Repository naming and ownership

`Donh91/Cycle-navigator-` is a historical repository identifier only. It must not be used for current routing. The Cycle Navigator subsystem remains owned inside the control plane under `05_CYCLE_NAVIGATOR/` unless a newer canonical owner decision explicitly changes that route.

## Mandatory stop states

Use an explicit stop state instead of guessing:

```text
PRIVATE_DATA_AUTHORITY_UNAVAILABLE
PRIVATE_BINDING_INCOMPLETE
PRIVATE_HASH_OR_READBACK_MISMATCH
CREDENTIAL_EXPOSURE_SUSPECTED
ROUND3_ANALYSIS_GATE_CLOSED
SC06_PERSISTENT_RUNTIME_NOT_AUTHORIZED
CROSS_REPO_CONTEXT_INCONSISTENT
```

Suspected credential exposure requires immediate cessation of value handling, redaction from agent output, credential rotation through the credential plane and a governed incident record. Never copy a suspected secret into another file to preserve evidence.

## Completion contract

A cross-repository task is complete only when:

1. required repositories and canonical files were read in order;
2. all private evidence has immutable commit/path/bytes/SHA-256/source-contract/time/schema/completeness bindings;
3. no restricted values or credentials entered public files, logs or responses;
4. the Round 3 firewall was preserved;
5. the exact branch, PR, CI and post-merge readback state is reported for each changed repository;
6. unresolved access, infrastructure, retention and paid-service decisions are named as blockers.
