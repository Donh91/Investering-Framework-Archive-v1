# Research Operating System v1.0

Date: 2026-07-07  
Status: INITIAL ARCHIVE BUILD  
Scope: Evidence Registry, Open Questions Register, Data Asset Manifest and No-Hindsight Replay Harness specification.

## Purpose

This folder converts the growing Investering archive from a collection of pings, reports and research files into an evidence-driven research operating layer.

The goal is to answer four recurring governance questions:

1. What has actually been tested?
2. What is still only assumed or shadow-only?
3. Which framework rules are live, ledger-only, governance-only or blocked?
4. How can historical DATA PING / Master Monday / Cycle Navigator rows be replayed without hindsight?

## Included files

- `research_evidence_registry_v1.md`  
  Canonical map of tested rules, evidence grade, result, confidence, implementation layer and next test.

- `open_questions_register_v1.md`  
  Standing list of unresolved research questions and missing evidence.

- `data_asset_manifest_v1.md`  
  Map of available and missing data assets across uploaded files, GitHub archive, Fable outputs and DATA PING sources.

- `no_hindsight_replay_harness_spec_v0_1.md`  
  Specification for future historical replay: what the framework knew at the time, what it would have said, and how outcomes should be scored.

- `custom_gpt_data_request_prompt_v1.md`  
  Optional prompt for Custom GPT to provide structured DATA PING schema/data supplements for v1.1.

## Current baseline

The most important current research results are:

- v0.2 hybrid gate is supported by P1 and P1b, including true OHLC / wick retest.
- 59.0K hard-death remains ratified but must be annotated as a tight hard-death, not a wide ATR buffer.
- 2/3-close persistence is not supported as price edge and was not rescued by flow-conditioning.
- FNP expected-cost prior remains approximately 9% [7-12], p90 approximately 12%, ledger-only.
- Rebuy remains LOCKED.
- Rotation, ETH/BTC persistence, leverage thresholds and breadth thresholds remain unvalidated.

## Operating principle

The research archive should not produce more theory before the evidence registry and replay harness can track whether rules actually helped.

Preferred next evolution:

`research PDFs -> evidence rows -> replay rows -> rule governance`
