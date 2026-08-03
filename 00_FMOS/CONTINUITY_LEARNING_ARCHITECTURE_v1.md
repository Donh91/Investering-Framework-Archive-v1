# Continuity + Learning Architecture v1

Status: ACTIVE_SHADOW_ONLY

This document is the authoritative routing guide for agents working on the OpenAI API, CFGI, daily owner captures, Master Monday and adaptive learning layers.

## Operating chain

```text
OWNER COLLECTORS
  -> compact capture index
  -> compressed raw cold-evidence archive
  -> Daily Director delta gate
  -> Luna shadow synthesis
  -> unratified forecast candidates
  -> explicit ChatGPT ratification
  -> FROZEN_FORECAST_v1
  -> outcome maturation
  -> MODEL_CALIBRATION_LEDGER
  -> monthly proposal-only meta audit
```

## Non-negotiable boundaries

- Raw bytes must remain reproducible. A hash without retained bytes is not sufficient evidence.
- Daily Director may call OpenAI only when at least one comparable metric delta exists.
- Forecast candidates are not forecasts, evidence, actions or model promotions.
- Only explicitly ratified candidates may become `FROZEN_FORECAST_v1`.
- No automatic portfolio authority, canonical promotion or model-weight change.
- Missing data remains UNKNOWN.

## CFGI collection policy

- 4H is the coherent primary series, sampled at all five daily capture slots.
- A 1D score-only anchor is sampled at the first daily slot.
- 1H and 15M are disabled unless a preregistered experiment explicitly requires them.
- CFGI data may influence weights only after forward-only scoring through the maturation engine.

## Permanent paths

- Compact captures: `03_DAILY_CAPTURE_LOGS/captures/`
- Raw cold evidence: `03_DAILY_CAPTURE_LOGS/raw/`
- Reliability ledger: `03_DAILY_CAPTURE_LOGS/weekly/RELIABILITY_LEDGER.csv`
- Daily outputs: `research/api_agent/outputs/daily/`
- Forecast candidates: `research/api_agent/forecast_candidates/PENDING/`
- Frozen forecasts: `research/api_agent/forecast_candidates/FROZEN/`
- Model calibration: `research/api_agent/MODEL_CALIBRATION_LEDGER.csv`
- Agent routing surface: `/LATEST_HANDOFF.json` and `/LATEST_HANDOFF.md`
- Incidents: `09_SOURCE_QA/incidents/`

## Governance lanes

### Data lane, scheduled bot writes allowed

`03_DAILY_CAPTURE_LOGS/**`, `research/api_agent/outputs/**`, `research/api_agent/forecast_candidates/PENDING/**`, `research/etf_owner/**`, `09_SOURCE_QA/**`, `research/architecture_health/**`, `LATEST_HANDOFF.*`

Required controls: bot identity, `framework-main-writer`, immutable or append-only paths, retry, remote readback.

### Code and governance lane, PR required

`scripts/**`, `.github/**`, `tests/**`, `00_ARCHIVE_CONTROL/**`, `01_CORE_FRAMEWORK/**`, registries, schemas, specialist contracts and `AGENTS.md`.

Direct-to-main changes in this lane are policy violations and must create an incident.

## Storage escalation

Each owner payload is limited to 2 MB uncompressed per capture. If compressed cold-evidence growth exceeds 20 MB per month, move the raw lane to a dedicated public or private data repository while retaining immutable manifests and pointers in the canonical repository.

## Read order for new agents

1. `LATEST_HANDOFF.json`
2. this document
3. `AGENTS.md`
4. latest architecture health
5. relevant contract or registry
6. only then the underlying evidence objects
