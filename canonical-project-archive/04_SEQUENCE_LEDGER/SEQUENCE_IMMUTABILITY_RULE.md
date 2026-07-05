# SEQUENCE IMMUTABILITY RULE

Status: Canonical
Date added: 2026-07-05
Effective from: 2026-07-05
Source context: ChatGPT
Applies to: Sequence Ledger, PTR, Pullback Tracker, Forecast Ledger

## Executive summary

A sequence expectation must not be rewritten after creation.

## Canonical content

Once a sequence ID is created, the original expected path stays frozen.

Only outcome states may change.

Allowed outcome states:

- PENDING
- CONFIRMED
- FAILED
- SKIPPED
- RETURNED

## Operational implication

This prevents hindsight bias and protects learning quality.

## Governance notes

If the market path changes, create an update note or a new sequence. Do not edit the original expectation.

## Update log

- 2026-07-05: Created.