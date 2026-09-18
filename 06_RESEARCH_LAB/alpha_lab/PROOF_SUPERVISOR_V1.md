# Alpha Lab Proof Supervisor v1

Owner: #1087
Plane: research/evidence only
Portfolio execution: FORBIDDEN

## Purpose

Close the manual follow-up gap after prospective Alpha Lab experiments without creating a parallel scanner, scorer or forecast engine.

The supervisor is a deterministic state machine. It does not claim that ChatGPT is continuously working. GitHub owns collection, adjudication, next-step routing and escalation.

## States

WAIT_SHADOW04 -> SHADOW04_RUNNING -> SHADOW04_PASS | SHADOW04_FAIL
SHADOW04_PASS -> WAIT_SHADOW07
WAIT_SHADOW07 -> SHADOW07_RUNNING -> EDGE_SUPPORTED | EDGE_NOT_SUPPORTED | INSUFFICIENT_EVIDENCE
Any invariant violation -> HALT_CRITICAL

## Evidence authority

Only immutable artifacts produced after a pre-registration freeze can advance a gate.

Labels:
- PROSPECTIVE_PASS
- PROSPECTIVE_FAIL
- RETROSPECTIVE
- EXTERNAL_REVIEW_MEASURED
- NOT_RUN

Only PROSPECTIVE_PASS advances.

## SHADOW-04 gate

Required:
- n >= 1000 future launches
- prospective == true
- provider_disagreement == 0
- PASS_COLLECTION == true
- spec_sha256 present
- future_start_block present
- no evidence that the freeze occurred after the credited start block

Failure routes:
- provider disagreement -> FAIL_DATA_INTEGRITY
- incomplete sample / runtime error -> RETRY_BOUNDED
- schema/spec mismatch -> HALT_CRITICAL

The supervisor never converts measured receipt.from/topic3/ticker statistics into VERIFIED identity. They are research outputs.

## SHADOW-07 gate

Rows are eligible only if first-party surface was frozen before T0 while CA was absent/COMING_SOON.

Minimum evidence target: 30 eligible launches.

Report median/IQR Δ_publish and Text where independently observed.

Decision:
- if verified publication systematically misses the pre-registered external-edge budget -> EDGE_NOT_SUPPORTED and stop VERIFIED-before-public engineering;
- if evidence supports the budget -> EDGE_SUPPORTED and unlock persistent ARMED-runtime engineering;
- otherwise -> INSUFFICIENT_EVIDENCE and collect more without changing thresholds post hoc.

Exact threshold/budget must be frozen in the SHADOW-07 experiment spec before outcomes.

## Retry policy

A failed infrastructure run may retry at most 2 times if and only if:
- failure happened before an outcome was observed;
- test assertions/spec hash remain unchanged;
- new run freezes a new future start block.

Scientific/adjudication FAIL is never auto-retried into PASS.

## Automatic next action

The controller emits one machine-readable NEXT_ACTION:
- WAIT
- RETRY_SHADOW04
- START_SHADOW07
- COLLECT_SHADOW07
- BUILD_ARMED_RUNTIME
- STOP_VERIFIED_EDGE_PROGRAMME
- HALT_CRITICAL

No autonomous code mutation is authorized by this controller. Engineering work is opened as an issue/packet after a gate, then follows normal review/governance.

## Noise policy

Notify/escalate only on:
- first valid PASS of a major gate;
- scientific FAIL / kill criterion;
- HALT_CRITICAL;
- repeated infrastructure failure after retry budget exhausted.

Routine WAIT/RUNNING produces no user-facing alert.

## Self-termination

The temporary hourly SHADOW-04 collector must NOOP once a valid >=1000 prospective artifact has been adjudicated, and its temporary schedule must be retired in the completion packet.

No repeated 1000-launch runs merely because a cron exists.
