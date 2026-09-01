# WORK MASTER HANDOFF — OnChainMind / Public Historical Data Admission

**Mission date:** 2026-09-01  
**Repository:** `Donh91/Investering-Framework-Archive-v1`  
**Prepared branch:** `agent/task-20260901-onchainmind-source-admission`  
**Mode:** autonomous engineering + research, audit-first, fail-closed  
**User requirement:** do not ask the user to perform manual GitHub work.

## Mission

Take over the prepared OnChainMind/public-data source-admission package and carry it from bounded research scaffolding to a fully tested, source-governed Research Lab implementation.

The goal is **not** to add more indicators.

The goal is to determine whether newly accessible historical/on-chain/expectations data can produce measurable incremental research value while preserving the existing framework's authority, evidence and anti-overfitting rules.

## Read first

Read current `main` and the prepared branch. Current main may have advanced since the branch was created.

Mandatory governance/context:

- `01_CORE_FRAMEWORK/governance/2026-07-25__external-indicator-admission-gates__canonical-addendum.md`
- `01_CORE_FRAMEWORK/governance/2026-07-22__sensor-relationship-and-incremental-value-standard__canonical.md`
- `.agents/skills/prospective-evidence-ledger/SKILL.md`
- `.agents/skills/research-lab-red-team/SKILL.md`
- `06_RESEARCH_LAB/historical_sensor_recovery_v1/HISTORICAL_SENSOR_PROVENANCE_AND_VALIDATION_METHODS_2026-08-21.md`
- `research/api_agent/mcp/MCP_CONNECTION_EVALUATION_METHOD_v1.md`
- `research/api_agent/API_INTELLIGENCE_POLICY_v2.json`
- `research/api_agent/SHADOW_ADMISSION_AI_POLICY_v1.json`
- `scripts/data_terminal/defillama_stablecoin_owner.py`
- `04_MARKET_LEARNING/external_research/2026-09-01__bitcoin-legacy-onchain-proxy-decay__shadow.md`

Prepared package:

- `06_RESEARCH_LAB/audit_summaries/2026-09-01__onchainmind-public-data-source-admission-audit__shadow.md`
- `06_RESEARCH_LAB/audit_summaries/onchainmind_source_admission_v1/SOURCE_CAPABILITY_MANIFEST.json`
- `06_RESEARCH_LAB/onchainmind_source_admission_v1/README.md`
- `06_RESEARCH_LAB/onchainmind_source_admission_v1/SOURCE_CONTRACTS_v0_1.json`
- `06_RESEARCH_LAB/onchainmind_source_admission_v1/PRIORITY_AND_KILL_MATRIX_v0_1.json`
- `06_RESEARCH_LAB/onchainmind_source_admission_v1/RESEARCH_EXPERIMENT_SPEC_v0_1.md`
- `scripts/research_sources/*.py`
- `tests/research_sources/*.py`

## Non-negotiable boundaries

1. Do not scrape/crawl/mine OnChainMind or ChartInspect.
2. Do not copy OnChainMind or ChartInspect raw/premium data into GitHub.
3. Do not persist BGeometrics raw API payloads in the public control plane.
4. Re-check BGeometrics terms before any durable private/restricted storage. If rights remain ambiguous, use transient retrieval + value-free public receipts only.
5. Polymarket network collection remains disabled until official storage/derived-use rights are explicitly resolved.
6. Do not use OCM derivatives to bypass the existing Round 3 restricted-data firewall.
7. Do not add a new engine.
8. Do not change live thresholds, weights, gates, Cycle Navigator semantics, DATA PING decisions or portfolio actions.
9. Do not count correlated on-chain measures as independent votes.
10. No LLM-extracted chart values as numeric evidence.
11. Missing data is UNKNOWN, not bearish.
12. No hindsight-created prospective rows. Do not claim matured future outcomes before the required future time has actually passed.

## Phase 0 — synchronize and re-audit

- Fetch current `main`.
- Compare prepared branch to current main.
- Rebase or reconstruct cleanly if needed, preserving the prepared changes.
- Inspect all changes to source/data governance since the branch merge-base.
- Confirm no parallel source owner already landed.
- Run targeted tests and broad relevant CI before proceeding.
- If current main supersedes any assumption, update the handoff artifacts rather than silently carrying stale assumptions.

## Phase 1 — source-contract hardening

### Coin Metrics Community

Build/finish an immutable-source receipt path.

Requirements:

- evidence runs must pin an exact Coin Metrics git commit SHA, not `main`;
- record source URL, source ref, payload SHA-256, byte count, row count, earliest/latest dates and field presence;
- use the official versioned archive/API;
- do not create a second permanent copy of the whole upstream dataset unless a bounded fixture is genuinely needed;
- verify current license and attribution requirements.

### BGeometrics

Harden the bounded research probe.

Requirements:

- allowlist only the minimal initial metrics required by the research spec;
- conservative rate limiting;
- fail closed on schema changes, empty payloads and invalid date semantics;
- public outputs contain no raw provider series;
- receipts must prove the fetched payload existed without redistributing it;
- explicitly determine the permitted internal/restricted storage class before any long-lived observation job.

### Polymarket

Do not enable the network collector by assumption.

First resolve from official provider material:

- automated public API use;
- durable storage of historical public market data;
- derived-feature storage/publication;
- redistribution constraints;
- market identifier/resolution semantics.

If any material point remains ambiguous, keep `NETWORK_COLLECTION_BLOCKED`.

## Phase 2 — deterministic compact on-chain replay

Use the exact Experiment A spec.

Primary candidate families:

- one holder-valuation axis: MVRV **or** STH-MVRV;
- one realized-behavior axis: SOPR;
- one old-coin-spending axis: VDD or one equivalent.

Do not test a zoo of variants.

Treat raw address count, transaction count and UTXO count as potentially decayed adoption proxies in the financialized/ETF era. Do not admit them as adoption truth without a separately validated financialization-adjusted specification.

Use identical timestamps and predeclared 7D, 14D and 28D outcomes.

Baseline ladder:

1. simple BTC price/trend;
2. existing framework BTC state at the same timestamp;
3. simpler component family;
4. matched controls;
5. time-shift placebo where sensible.

Use expanding/walk-forward only. All transforms must be trailing-only.

Do not select the best threshold, horizon or regime after seeing results.

Report negative results.

The output must answer:

> Does any compact on-chain family measurably improve decision-relevant information beyond the simpler baseline and current framework state?

Allowed terminal outcomes:

- `KEEP_RESEARCH_ACTIVE`
- `KEEP_CROSSCHECK_ONLY`
- `SHADOW_OBSERVATION`
- `HOLD`
- `KILL`

No retrospective result may directly become live authority.

## Phase 3 — URPD source observation and topology study

Treat URPD first as a data/provenance problem.

Determine:

- exact earliest retrievable point-in-time date;
- snapshot cadence;
- weekend/date gaps;
- revisions;
- bin boundaries through time;
- whether the provider changes bin granularity with price;
- exact `pctSupply` and `btcSupply` normalization;
- BTC price source/settlement needed for spot-relative features.

Do not manufacture missing historical snapshots.

If durable internal storage is contractually permitted, create the minimum restricted-plane source-observation contract and validator required to preserve point-in-time topology. Public control plane should hold receipts/hashes and aggregate research results only.

Candidate topology features are provisional hypotheses, not rules:

- supply near spot share;
- nearest dense shelf distance;
- nearest sparse/vacuum distance;
- above/below spot supply asymmetry;
- concentration/entropy.

Run redundancy tests against simpler price/holder-stress features before retaining them.

## Phase 4 — Polymarket expectations only if rights clear

If Phase 1 clears collection:

- predeclare event taxonomy before outcome-linked collection;
- use canonical market IDs and explicit resolution rules;
- store query parameters/source timestamps;
- avoid cherry-picking markets because they later mattered;
- test probability **changes** and calibration, not simplistic probability thresholds;
- compare with scheduled-event data, macro data and contemporaneous crypto price.

If rights do not clear, retain offline parser and return `HOLD` or `KILL`.

## Phase 5 — ETF-era institutional/organic confirmation

Only after simpler work above is complete.

Reuse the existing settled ETF owner.

Choose at most one independent native/on-chain capital-flow representation.

Test divergence/confirmation value without creating multiple votes.

Kill if settled ETF flow + price already explains the same information.

## Heavy path intentionally deferred

Self-hosted historical URPD from a Bitcoin node/UTXO index is not part of the initial mission.

Open tooling exists for parsing Bitcoin Core UTXO snapshots, but true realized-cost-basis reconstruction requires historical coin acquisition/last-move lineage plus price-at-time mapping and materially heavier indexing/storage.

Only reopen this path if licensed/reproducible upstream sources fail or a later audit proves the expected value justifies the engineering burden.

## Testing requirements

At minimum:

- new probe/parser/validator unit tests;
- malformed JSON/CSV;
- missing fields;
- empty payload;
- source schema drift;
- authority escalation rejection;
- raw-persistence rejection;
- mutable-ref rejection for evidence-mode Coin Metrics;
- rate-limit/HTTP failure behavior;
- URPD empty-date behavior;
- Polymarket network-block behavior while contract is unresolved.

Run targeted tests first, then all repository gates affected by the changed paths.

Preserve a CI/readback receipt.

## Git workflow

- Do not write directly to `main`.
- Work from a current-main-based branch.
- Commit in reviewable units.
- Open/update PR.
- Inspect CI.
- Remediate relevant failures.
- Review current-main drift/conflicts before merge.
- Merge only after required gates pass.
- Read back merged `main` and verify exact files/commit.
- If live/prospective observation is enabled, verify the first production receipt without pretending future outcomes have matured.

## Definition of done

The mission is complete only when:

1. source contracts are explicit and fail closed;
2. prepared probes are hardened and tested;
3. compact on-chain replay has a reproducible result versus baselines, including negative results;
4. URPD is either safely observable with an explicit retention/storage contract or explicitly held/killed;
5. Polymarket is either contract-cleared and bounded or remains disabled;
6. no new sensor/weight/engine was smuggled into live semantics;
7. all relevant tests/CI pass;
8. PR is merged;
9. main readback is verified;
10. final report distinguishes:
   - implemented source infrastructure,
   - retrospective research result,
   - prospective observations,
   - unresolved future maturation.

Do not declare prospective predictive success until actual future observations mature.
