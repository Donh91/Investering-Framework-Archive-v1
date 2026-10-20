# X0 - Disagreement Alpha v1

Status: SPECIFIED / TRANSVERSAL / RESEARCH_ONLY
Priority: P0
Master queue: README.md
Master issue: #1512

## Core question

When a specialist provider and the Framework disagree about the same point-in-time object, is the disagreement itself informative?

This is not a voting system.

The research object is the mismatch.

Examples:
- provider SMART_MONEY vs internal LUCK_COMPATIBLE;
- provider SAFE vs internal execution failure;
- provider cluster link vs weak raw provenance;
- provider creator identity vs canonical launch-origin evidence;
- provider bullish attention signal vs qualified-wallet distribution.

## Why this is distinct

Agreement can be redundant.

Disagreement can reveal:
- provider blind spots;
- internal blind spots;
- stale data;
- hidden assumptions;
- regime dependence;
- false positives;
- false negatives;
- semantic mismatch.

The strongest specialist transfer may therefore be the provider's error surface rather than its headline label.

## Minimal disagreement receipt

Freeze:
- disagreement_id;
- subject_type;
- chain + exact subject identity;
- cutoff_utc;
- provider;
- provider_claim;
- provider_confidence/score if exposed;
- provider_source_hash;
- provider_observed_at_utc;
- internal_owner;
- internal_claim;
- internal_confidence/state;
- internal_evidence_refs;
- semantic_compatibility;
- disagreement_class;
- later matured mechanics/outcome;
- resolution_state.

## Required disagreement classes

- PROVIDER_POSITIVE_INTERNAL_NEGATIVE
- PROVIDER_NEGATIVE_INTERNAL_POSITIVE
- PROVIDER_KNOWN_INTERNAL_UNKNOWN
- PROVIDER_UNKNOWN_INTERNAL_KNOWN
- IDENTITY_CONFLICT
- TIMESTAMP_CONFLICT
- COVERAGE_CONFLICT
- SEMANTIC_CONFLICT
- AGREEMENT_POSITIVE
- AGREEMENT_NEGATIVE

Agreement rows are required denominators.

## First consumers

S1 Sellability Truth:
SAFE/UNSAFE versus executable mechanics.

S2 Wallet Skill Truth:
SMART_MONEY/KOL/SNIPER/etc versus complete-history internal skill state.

S3 Cluster/Bundle:
linked/clustered versus deterministic common-funder/transfer/timing evidence.

S4 Launch trajectory:
Ocellus derived state versus first-party Pons chain evidence.

S6 Distribution egress:
entity/exchange destination labels versus raw path evidence.

## Metrics

Per provider + claim family:
- agreement rate;
- disagreement rate;
- provider precision/recall versus later resolved mechanics;
- internal precision/recall;
- unresolved fraction;
- stale-data disagreement rate;
- disagreement-conditioned return/risk outcome where scientifically admissible;
- incremental value versus using internal state alone;
- incremental value versus provider alone.

Do not optimize on a single provider accuracy score when semantics differ.

## Promotion possibilities

### DISAGREEMENT_SIGNAL_SUPPORTED
A preregistered disagreement class predicts a relevant later outcome prospectively.

### PROVIDER_ERROR_SURFACE_SUPPORTED
Disagreement mostly identifies a specific recurring provider weakness.

### INTERNAL_ERROR_SURFACE_SUPPORTED
Provider disagreement identifies a recurring internal weakness.

### REDUNDANT
Agreement dominates and provider adds no information.

### SEMANTIC_MISMATCH
Claims were not actually comparable. Fix schema or kill comparison.

## Governance

No majority vote.
No provider ensemble score by default.
No automatic trade action.
No retrospective relabeling after outcomes.
UNKNOWN remains UNKNOWN.
A provider can be useful because it is wrong in a systematic way, but that requires prospective evidence.

## Activation

Do not build a standalone heavy engine.

Implement the disagreement receipt only as S1-S3 create real paired observations.

Until then this spec remains the shared schema and research question.
