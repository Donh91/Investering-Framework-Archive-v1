# S1 Executable Sellability Truth - Execution Receipt - 2026-10-06

Status: PAIRED_EVIDENCE_DENOMINATOR_MERGED / PROSPECTIVE_DATA_PENDING / RESEARCH_ONLY
Master issue: #1512
Alpha execution issue: Donh91/Meme-Alpha-Lab#98
Provider capability PR: Donh91/Meme-Alpha-Lab#100
Paired denominator PR: Donh91/Meme-Alpha-Lab#104
Merge commit: 791095442909d659c8c41c893baa125f103a0218

## What is now proven

Provider source capability:
- GoPlus Token Security on Robinhood chain 4663 passed repeated fixture-level source audit.
- Honeypot.is passed repeated fixture-level source audit on its documented Ethereum fixture.
- normalized provider observations can be captured into a hash-chained ledger.

Scientific denominator:
- provider observations are stored independently of internal mechanics truth;
- internal mechanics evidence can preserve PASS, FAIL, NO_ROUTE, REVERT and UNKNOWN;
- exact chain + token + bounded timestamp matching is required before comparison;
- absence of a sell/event cannot become negative mechanics evidence;
- direct successful on-chain execution may prove PASS only for the observed state/size/path;
- negative mechanics requires explicit reproducible evidence;
- deterministic disagreement classes are generated without changing paper-wallet state.

## Important audit finding

The existing execution_shadow_v4 intentionally persists only PASS mechanics. That is correct for paper-trade execution, but it cannot by itself form the negative denominator needed to test PROVIDER_SAFE_INTERNAL_FAIL.

The solution was additive:
- research/sellability/provider_observations_v1.csv
- research/sellability/internal_mechanics_observations_v1.csv
- research/sellability/sellability_pairs_v1.csv
- scripts/sellability_cohort_v1.py

No second execution engine or paper wallet was created.

## Remaining hard gap

EVM_NEGATIVE_SELLABILITY_PROOF_V1 is now explicit.

The Framework still needs an independent bounded route/revert/no-route primitive capable of proving negative mechanics on supported EVM paths without using the external provider verdict as truth.

Candidate evidence families:
- public RPC eth_call/state-override where actually supported;
- bounded fork simulation;
- first-party router/pool calls;
- reproducible failed transaction/trace evidence.

Do not infer failure from inactivity.

## Current scientific ruling

S1 method/capability: IMPLEMENTED.
Provider superiority/edge: UNKNOWN.
Matched live cohort: DATA_PENDING.
Negative independent mechanics adapter: OPEN.

The next value from S1 comes from prospective paired observations, not more provider-discovery work.
