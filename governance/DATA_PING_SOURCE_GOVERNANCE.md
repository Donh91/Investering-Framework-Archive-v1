# DATA PING Source Governance

Status: ACTIVE
Effective date: 2026-07-04

## Canonical rule

HIGHEST ACTIVE DATA PING VERSION WINS.

DATA PING threads are versioned by number:

V1 < V2 < V3 < V4 < V5 < V6 etc.

The highest explicitly active DATA PING version is the live operational feed.

## Current state

Current expected live operational feed: DATA PING V4.

If DATA PING V5 or higher is explicitly activated, that newer version becomes the live operational feed.

Older DATA PING versions are ARCHIVE_CONTEXT only unless the user explicitly reactivates them.

## Health check requirement

Every framework health check must verify:

- highest active DATA PING version
- whether any active automation still hardcodes an older DATA PING version
- whether old DATA PING threads are treated only as archive context
- whether Weekly RAW, Canonical Backbone, Master Monday and Auto Stabilizer agree on the same live feed

## Role separation

- DATA PING: sensor and verified input layer
- Grok: shadow and adversarial context
- ChatGPT: framework and governance layer
- GitHub: versioned archive and audit trail

## Hard ban

Do not use old DATA PING thread content as live trigger input unless explicitly reactivated by the user.
