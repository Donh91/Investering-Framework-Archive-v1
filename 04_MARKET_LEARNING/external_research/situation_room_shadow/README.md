# Situation Room Verification -> Shadow Bridge

Status: ACTIVE_SHADOW_RESEARCH_BRIDGE
Authority: SHADOW_RESEARCH_ONLY_NON_CANONICAL

## Purpose

Situation Room remains a discovery/radar source only. New Situation Room discoveries are automatically checked for independent primary-source corroboration before they may enter Shadow context.

## Automatic path

Situation Room Daily Static Discovery
-> current discovery captured
-> deterministic verification bridge runs automatically after the discovery workflow completes
-> corroboration is attempted against either already verified primary-source events from the Situation Room owner or authoritative primary links exposed by the Situation Room briefing
-> corroborated items are written to this Shadow lane
-> unresolved items remain explicitly pending and are not admitted as verified Shadow context
-> the next Daily Director context build receives the verified Shadow subset through `augment_director_compounding_learning_context.py`
-> pending discoveries are routed only as queue metadata and are explicitly forbidden from being treated as evidence

A scheduled 08:40 Europe/Copenhagen safety-net reruns the bridge after the normal 08:20 discovery. `source_run_id` idempotence prevents duplicate admission.

## Accepted automatic verification methods

- `OWNER_PRIMARY_EVENT_TITLE_OVERLAP`
- `SITUATION_ROOM_LINKED_PRIMARY_SOURCE`

The bridge is deliberately conservative. A Situation Room headline is never treated as verified merely because it was fetched successfully.

## Durable outputs

- `LATEST.json` - latest bridge pointer and counts
- `YYYY/MM/YYYY-MM-DD.json` - dated verification and Shadow handoff state
- `VERIFIED_SHADOW_LEDGER.jsonl` - append-only deduplicated verified Shadow records

## Director routing

Verified rows are exposed to Daily Director as `situation_room_shadow.verified_context` with provenance hashes. The Director may use these rows as corroborated non-canonical catalyst context.

`pending_verification` never becomes Director evidence. It may only signal that a discovery still awaits corroboration.

This satisfies the framework routing principle: collected information is not considered available to an agent unless it is explicitly present in that agent's context.

## Authority firewall

This bridge may enrich Shadow/catalyst context only.

It has no authority to:

- change canonical market state;
- change framework thresholds or model weights;
- activate top-up or entry signals;
- change portfolio state;
- execute trades.

Any future promotion beyond Shadow must use the framework's existing evidence/adjudication process. Situation Room never self-promotes.

## Failure semantics

No corroboration means `PENDING_PRIMARY_VERIFICATION`, not a verified event.
Source/network failure means unavailable/unknown evidence, never silent confirmation and never `NO_EVENT` by inference.
