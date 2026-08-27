# K17 deterministic numeric evidence guard

**Status:** `RESEARCH_GUARD / SHADOW / NO_PORTFOLIO_AUTHORITY`  
**Date:** 2026-08-27

## Rule

A numeric market observation may not become research evidence, a prospective record, a calibration input or a framework state input when the numeric value was extracted or reconstructed by a language-model summarisation layer.

For machine-readable numeric sources, the evidence path must be deterministic:

`source payload -> deterministic parser -> typed observation -> provenance/hash -> validation -> interpretation`

Never:

`source/chart/page -> LLM summary -> numeric observation -> framework evidence`

## Required properties

1. `NOT_PRESENT` / `SOURCE_UNAVAILABLE` is a valid result and must never be converted into an estimated number.
2. Coverage and date range must be checked against the payload actually parsed.
3. Numeric payloads must carry exact source identity, retrieval time and payload/content hash where feasible.
4. Revised macro series used historically require point-in-time/vintage handling when available, for `NFCICREDIT` historical tests this means ALFRED vintages.
5. At least one preregistered sanity anchor should be checked when a stable known-extreme exists. A sanity anchor detects parser/source failures, it does **not** prove provenance.
6. Cross-source or independent deterministic readback is required before a surprising source-coverage change is promoted into research evidence.
7. Any contradiction between declared coverage and parsed observations is `FAIL_CLOSED_SOURCE_CONTRADICTION`.
8. LLMs may interpret already validated observations, but may not originate them.

## Origin

During the 2026-08-27 slow-cycle audit, a summarising fetch layer returned plausible historical NFCI-family values while independent reads returned `NOT_PRESENT`. Those fabricated values were not admitted into the framework. This guard generalises that failure mode for agent-operated data collection.

## Relationship to K16

K16 prevents structural information containment/double counting. K17 prevents unsupported numeric evidence from entering the evidence chain. Passing one does not imply passing the other.
