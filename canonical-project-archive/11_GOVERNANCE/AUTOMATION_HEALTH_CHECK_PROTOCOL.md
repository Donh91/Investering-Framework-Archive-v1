# AUTOMATION HEALTH CHECK PROTOCOL

Status: Active operational protocol
Date added: 2026-07-05
Effective from: 2026-07-05
Source context: ChatGPT
Applies to: automations, Master Monday, Weekly RAW, Archive Sync

## Executive summary

Automation health checks protect the framework from drift, stale source rules and silent failures.

## Required checks

- Active DATA PING version rule is current.
- No weekly process is hardcoded to an older feed.
- Weekly RAW runs before Master Monday.
- Canonical Backbone runs before final weekly synthesis.
- Auto Stabilizer checks source governance.
- GitHub Archive Sync runs after weekly synthesis.
- Blocked writes are reported.
- Disabled automations are not treated as active.

## Status labels

Use:

- GREEN
- AMBER
- DEGRADED
- BLOCKED

## Operational implication

A failed automation should create a health note and should not silently change framework state.

## Governance notes

Automations are execution shells. They are not independent truth-layers.

## Update log

- 2026-07-05: Created.