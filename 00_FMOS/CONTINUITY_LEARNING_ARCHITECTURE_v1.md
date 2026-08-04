# Continuity + Learning Architecture v1

Status: ACTIVE_SHADOW_ONLY

This document is the authoritative routing guide for agents working on the OpenAI API, CFGI, daily owner captures, Master Monday, legacy knowledge and adaptive learning layers.

## Operating chain

```text
OWNER COLLECTORS
  -> compact capture index
  -> compressed raw cold-evidence archive
  -> Daily Director delta gate
  -> current evidence + separate legacy hypothesis lane
  -> Luna shadow synthesis
  -> unratified forecast candidates
  -> explicit ChatGPT ratification
  -> FROZEN_FORECAST_v1
  -> outcome maturation
  -> MODEL_CALIBRATION_LEDGER
  -> weekly and monthly proposal-only calibration
```

## Non-negotiable boundaries

- Raw bytes must remain reproducible. A hash without retained bytes is not sufficient evidence.
- Daily Director may call OpenAI only when at least one comparable metric delta exists.
- Forecast candidates are not forecasts, evidence, actions or model promotions.
- Only explicitly ratified candidates may become `FROZEN_FORECAST_v1`.
- No automatic portfolio authority, canonical promotion or model-weight change.
- Missing data remains UNKNOWN.
- Legacy ChatGPT and pre-GitHub material is research memory, never current owner evidence.
- A legacy match may support only a new unratified candidate. It cannot count as a historical prospective hit.

## Legacy knowledge lane

The research package lives at:

`04_MARKET_LEARNING/legacy_framework_knowledge_bootstrap_v1/`

Daily Director and weekly calibration receive it under `legacy_research_context`, separately from current owner evidence. Consumers may classify a hypothesis as `MATCH`, `PARTIAL_MATCH`, `CONTRADICTION` or `NOT_EVALUABLE`.

Legacy extraction can advance an idea only to evidence level L2. L3 requires an independent prospective match under the current pipeline. L4 requires a frozen forecast and matured outcome.

Raw ChatGPT exports, personal material and paid research are processed privately. The public repository stores only sanitized observations, source hashes, receipts and research-only registries.

## CFGI collection policy

- 4H is the coherent primary series, sampled at all five daily capture slots.
- A 1D score-only anchor is sampled at the first daily slot.
- 1H and 15M are disabled unless a preregistered experiment explicitly requires them.
- CFGI data may influence weights only after forward-only scoring through the maturation engine.

## Passive operating cadence

- Owner capture: five times daily in Europe/Copenhagen.
- Daily Director: once daily after the final owner capture, with zero-cost skip when no comparable delta exists.
- Continuity maintenance: nightly candidate materialization, maturation, calibration ledger, reliability ledger and handoff refresh.
- Automation and architecture health: twice daily.
- Operations Dashboard: twice daily after health refresh.
- Weekly close, calibration and Master Monday: weekly frozen and durable chain.

## Permanent paths

- Compact captures: `03_DAILY_CAPTURE_LOGS/captures/`
- Raw cold evidence: `03_DAILY_CAPTURE_LOGS/raw/`
- Reliability ledger: `03_DAILY_CAPTURE_LOGS/weekly/RELIABILITY_LEDGER.csv`
- Daily outputs: `research/api_agent/outputs/daily/`
- Forecast candidates: `research/api_agent/forecast_candidates/PENDING/`
- Frozen forecasts: `research/api_agent/forecast_candidates/FROZEN/`
- Model calibration: `research/api_agent/MODEL_CALIBRATION_LEDGER.csv`
- Legacy research: `04_MARKET_LEARNING/legacy_framework_knowledge_bootstrap_v1/`
- Agent routing surface: `/LATEST_HANDOFF.json` and `/LATEST_HANDOFF.md`
- Operations cockpit: `/LATEST_OPERATIONS_DASHBOARD.json` and `/LATEST_OPERATIONS_DASHBOARD.md`
- Incidents: `09_SOURCE_QA/incidents/`

## Governance lanes

### Data lane, scheduled bot writes allowed

`03_DAILY_CAPTURE_LOGS/**`, `research/api_agent/outputs/**`, `research/api_agent/forecast_candidates/PENDING/**`, `research/etf_owner/**`, `09_SOURCE_QA/**`, `research/architecture_health/**`, `research/operations_dashboard/**`, `LATEST_HANDOFF.*`, `LATEST_OPERATIONS_DASHBOARD.*`

Required controls: bot identity, `framework-main-writer`, immutable or append-only paths, retry, remote readback.

### Code and governance lane, PR required

`scripts/**`, `.github/**`, `tests/**`, `00_ARCHIVE_CONTROL/**`, `01_CORE_FRAMEWORK/**`, `04_MARKET_LEARNING/legacy_framework_knowledge_bootstrap_v1/**`, registries, schemas, specialist contracts and `AGENTS.md`.

Direct-to-main changes in this lane are policy violations and must create an incident.

## Storage escalation

Each owner payload has an enforced per-capture ceiling. If compressed cold-evidence growth exceeds 20 MB per month, move the raw lane to a dedicated public or private data repository while retaining immutable manifests and pointers in the canonical repository.

## Read order for new agents

1. `LATEST_OPERATIONS_DASHBOARD.json`
2. `LATEST_HANDOFF.json`
3. this document
4. `AGENTS.md`
5. latest automation and architecture health
6. relevant contract or registry
7. only then the underlying evidence objects
