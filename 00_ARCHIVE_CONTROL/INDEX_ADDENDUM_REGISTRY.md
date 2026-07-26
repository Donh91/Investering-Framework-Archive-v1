# Index Addendum Registry

**Dato:** 2026-07-20  
**Status:** CANONICAL_OPERATIONAL_REGISTRY  
**Område:** archive discoverability / index addenda  
**Primary folder:** `00_ARCHIVE_CONTROL/`  
**Depends on:** `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`, `00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md`

## Purpose

This registry provides a low-impact discovery layer for valid index addenda that are not yet listed directly in `CANONICAL_INDEX.md`.

It does not replace the canonical index. It prevents repository-aware agents from overlooking newer addenda merely because a direct index modification would require the high-impact safepoint workflow.

## Mandatory use

Repository-aware agents must read:

```text
00_ARCHIVE_CONTROL/CANONICAL_INDEX.md
00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md
```

before resolving current cross-domain authority.

A registry entry is a navigation pointer only. The referenced file's own status, owner, evidence class and supersession rules still determine authority.

## Active registry

| Addendum or routing anchor | Domain | Discovery status |
|---|---|---|
| `00_ARCHIVE_CONTROL/2026-07-10__index-addendum-data-ping-hybrid-edge-event-archive.md` | DATA PING / edge events | INDEX_LISTED |
| `00_ARCHIVE_CONTROL/2026-07-10__index-addendum-gpt-5-6-fresh-eyes-audit-implementation.md` | framework governance | INDEX_LISTED |
| `00_ARCHIVE_CONTROL/2026-07-11__index-addendum-techdev-historical-batch-1.md` | TechDev source archive | INDEX_LISTED |
| `00_ARCHIVE_CONTROL/2026-07-11__index-addendum-techdev-historical-batch-2.md` | TechDev source archive | INDEX_LISTED |
| `00_ARCHIVE_CONTROL/2026-07-11__index-addendum-techdev-historical-batch-3.md` | TechDev source archive | INDEX_LISTED |
| `00_ARCHIVE_CONTROL/2026-07-10__legacy-namespace-manifest__canonical.md` | legacy routing | INDEX_LISTED |
| `00_ARCHIVE_CONTROL/2026-07-11__index-addendum-external-vault-activation.md` | backup / vault | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-12__index-addendum-investering-agent-skills-v0-1.md` | agent workflows | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-12__index-addendum-cmc-btc-d-defillama-completion-and-replay.md` | truth layer / research completion | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-12__index-addendum-full-sensor-simulation-backtest-v1.md` | full sensor backtest | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-12__index-addendum-sensor-survival-timing-placebo-regime-audit-v1.md` | sensor audit / machine improvement | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-12__index-addendum-agent-control-loop-v0-1.md` | agent workflows / automation integrity | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-12__index-addendum-marginal-decision-value-and-breadth-truth-v1.md` | Research Lab / frozen breadth / marginal sensor value | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-12__index-addendum-daily-sensor-pair-discovery-lab-v0-1.md` | prospective sensor pairs / DATA PING thread integration | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-12__index-addendum-data-ping-thread-handoff-v0-1.md` | DATA PING thread source transport / automation fallback | REGISTRY_DISCOVERABLE |
| `06_RESEARCH_LAB/forward_tests/2026-07-13__daily-sensor-pair-discovery-accepted-log-fallback-v0-1__canonical-addendum.md` | DATA PING accepted-log fallback / sensor-pair source resolution | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-13__index-addendum-techdev-calibration-b1-and-audit-gate-v1.md` | TechDev outcomes / BTC.D reproducibility / Issue #98 prospective calibration / research cadence | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-14__index-addendum-master-monday-durable-handoff-v1.md` | Master Monday / durable handoff / pointer integrity | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-20__index-addendum-techdev-market-update-98-source-archive.md` | TechDev source archive / Issue #98 | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-06__index-addendum-master-monday-pointers.md` | Master Monday / W28 pointer history - superseded by W28 lineage correction | SUPERSEDED |
| `00_ARCHIVE_CONTROL/2026-07-07__index-addendum-data-ping-alert-router-v0-1.md` | DATA PING alert router history - superseded by Hybrid v0.5.1 | SUPERSEDED |
| `00_ARCHIVE_CONTROL/2026-07-08__index-addendum-cn-rd-audit-calibration.md` | Cycle Navigator / R&D calibration | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-08__index-addendum-m1-pullback-weather-degraded-execution.md` | pullback weather / degraded execution | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-08__index-addendum-m2-sensor-combination-tournament.md` | sensor tournament / degraded execution | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-08__index-addendum-m4-rotation-survival-degraded-first-pass.md` | rotation survival / degraded first pass | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-08__index-addendum-m5-range-skill-audit.md` | range skill audit / degraded scoring | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-08__index-addendum-range-model-review-v0-1.md` | range model review / design only | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-10__index-addendum-frlp-v0-1-activation.md` | FRLP v0.1 / range ledger protocol | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-11__index-addendum-repository-safety-and-backup-rotation.md` | repository safety / backup rotation | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-11__index-addendum-techdev-benchmarks-forward-calibration-v1.md` | TechDev benchmarks / forward calibration | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-11__index-addendum-techdev-complete-corpus-audit-v1.md` | TechDev complete corpus audit | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-11__index-addendum-techdev-vault-recovery.md` | TechDev vault / file-library recovery | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-11__index-addendum-truth-layer-data-pack.md` | truth-layer data pack | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-11__index-addendum-ultimate-framework-attack-governance-and-s4-hybrid.md` | framework audit / S4 hybrid governance | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-12__index-addendum-data-completion-control-plane.md` | data completion / truth-layer control plane | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-12__index-addendum-final-truth-layer-gap-closure-and-m3-forward.md` | truth-layer gap closure / M3 forward collection | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-12__index-addendum-transmission-matrix-forward-test-v0-1.md` | Transmission Matrix forward test | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-12__index-addendum-truth-layer-recovery-and-github-lineage-upgrade.md` | truth-layer recovery / GitHub lineage | REGISTRY_DISCOVERABLE |
| `01_CORE_FRAMEWORK/governance/2026-07-25__external-indicator-admission-gates__canonical-addendum.md` | external indicators / specification dispersion / saturation / FX decomposition | REGISTRY_DISCOVERABLE |
| `00_ARCHIVE_CONTROL/2026-07-26__index-addendum-etf-flow-history-backtest-pack.md` | ETF flow history / truth-layer backtest input | REGISTRY_DISCOVERABLE |

## Registration contract

When an index addendum is created or materially updated, `archive-governance` must:

1. verify the addendum path exists;
2. verify its owner paths exist;
3. add or update exactly one row in this registry;
4. classify it as `INDEX_LISTED`, `REGISTRY_DISCOVERABLE`, `SUPERSEDED` or `BROKEN_POINTER`;
5. avoid modifying `CANONICAL_INDEX.md` unless the high-impact safepoint and vault workflow has been completed;
6. record the registry change in the pull request or skill-run receipt.

## Failure states

```text
ADDENDUM_PATH_MISSING
ADDENDUM_OWNER_MISSING
ADDENDUM_NOT_REGISTERED
ADDENDUM_DUPLICATE_ENTRY
ADDENDUM_SUPERSESSION_UNRESOLVED
```

A missing or broken addendum must not be silently treated as current authority.

## Maintenance rule

This registry is append-and-correct, not append-only in the literal sense. Existing rows may be updated when an addendum becomes index-listed, superseded or broken. Historical files remain preserved in Git history.

Direct changes to `CANONICAL_INDEX.md` remain governed by the repository high-impact safety policy.
