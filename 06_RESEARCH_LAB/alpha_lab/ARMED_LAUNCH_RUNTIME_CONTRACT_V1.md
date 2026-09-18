# Alpha Lab ARMED Launch Runtime Contract v1

Status: prospective, fail-closed. Owner: issue #1087. This extends existing Alpha Lab evidence owners; it is not a parallel alpha/scoring engine.

## Purpose

Separate low-cost passive research from a latency-critical launch window.

PASSIVE -> CANDIDATE -> ARMED_PRECHECK -> ARMED_READY | ARMED_DEGRADED -> LAUNCH_SEEN -> IDENTITY_VERIFIED -> ALERT_CREATED -> ENRICHMENT -> OUTCOME

A user-supplied Telegram/X/group hint may immediately create a CANDIDATE and request ARMED_PRECHECK. It remains EXTERNAL_USER origin and can never earn autonomous discovery credit.

## Passive mode

Passive discovery may run periodically. Freeze first_seen_at, source, content hash, project identity, claimed chain/ticker/venue, canonical publication surfaces, CA state and origin. Do not require second-level monitoring.

## ARMED readiness gate

ARMED_READY is forbidden unless all applicable checks pass immediately before the launch window:

1. exact expected chain ID verified;
2. canonical venue/factory/router/event path frozen when known;
3. raw-event parser replayed against at least one immutable same-venue fixture;
4. at least two usable independent transports when available, otherwise DEGRADED;
5. restart/backfill overlap test passes;
6. current head/cursor lag within threshold;
7. identity regression fixtures pass, including ASKR != BASKR;
8. alert path can create a canary notification;
9. runtime has sufficient remaining lifetime to cover expected launch window;
10. evidence timestamp for the readiness canary is persisted.

Workflow/file existence is never liveness proof.

## Fast verified-CA gate

The first time-critical alert must not wait for holders, wallets, MC/FDV, narrative or full R/R.

VERIFIED_CA requires:
- expected chain;
- exact CA from canonical on-chain event OR first-party publication subsequently tied to canonical provenance where applicable;
- bytecode exists;
- successful event/receipt provenance where applicable;
- exact pre-frozen project identity agreement;
- no substring/fuzzy ticker identity;
- healthy observation transport.

If identity is incomplete, label UNVERIFIED_CANDIDATE. Never make it look trade-ready.

## Freshness

Record Tpre, Tarm, T0, T1, T2, T3, Tdelivery when measurable, and Text.

- T0: canonical launch timestamp
- T1: detector observation
- T2: minimum identity verification
- T3: alert creation
- Text: independently observed external/Rick/Telegram first-seen

An alert outside the configured early-latency budget must be downgraded to LATE_DETECTION_ANALYSIS_ONLY. It cannot earn early-edge credit.

Positive information-edge evidence requires a new unknown launch, no user-supplied CA, T3 < Text, and no later identity correction. Replay cannot earn this claim.

## Runtime architecture rule

GitHub remains the control/evidence/governance plane.

A finite GitHub Actions polling job is acceptable for bounded prospective experiments only when its lifetime covers the launch window and ARMED readiness is proven. Do not infer that this is adequate for permanent seconds-level monitoring.

Before productionizing a permanent ARMED runtime, independently evaluate a persistent event listener/websocket/webhook worker with restart-always semantics, health endpoint, redundant RPC transports, persistent cursor, overlap backfill and direct low-latency push. Prefer the smallest architecture that measurably reduces T3/Tdelivery without weakening provenance.

## QLO-derived challenger ideas

Test, do not blindly copy:
- persistent event-driven listener instead of finite polling;
- explicit health endpoint/runtime liveness;
- freshness cutoff that suppresses stale "early" alerts;
- parallel enrichment only after the minimum identity path;
- prospective outcome checkpoints;
- direct notification transport independent of evidence archival.

These are challenger hypotheses. Promotion requires prospective evidence on Robinhood Chain.

## Sol 5.6 API role

During a bounded ARMED window, Sol may spend more API budget to red-team readiness:
- reconstruct launch path from first-party and venue evidence;
- find missing canonical surfaces;
- verify event/factory/router assumptions;
- generate collision/wrong-chain/wrong-factory tests;
- attack RPC/runtime assumptions;
- choose the next cheapest deterministic falsification;
- audit whether any enrichment is delaying the fast path.

Sol is not chain truth and may not invent a CA, venue or provenance.

## Kill criteria

Retire or redesign this layer if prospective trials show any of:
- identity correction after VERIFIED_CA;
- repeated false negatives despite ARMED_READY;
- T3 consistently loses to external first-seen with no fixable latency component;
- notification delivery is unobservable/unreliable;
- runtime cost/complexity exceeds measured information value;
- duplicate functionality is better owned by an existing production runtime.
