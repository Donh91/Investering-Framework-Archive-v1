# Alpha Lab Evidence-Driven Launch Runtime Contract v2

Status: prospective, fail-closed, research/evidence only.
Canonical owner: #1087. Experiment child: #1134.
This is not a scanner, scorer, trading engine, or second learning loop.

## Purpose

Separate cheap passive discovery from bounded launch-window research while preserving causal evidence.

PASSIVE -> CANDIDATE -> CANDIDATE_RANKED -> PRIMARY_PUBLICATION_SEEN -> IDENTITY_VERIFIED -> ALERT_CREATED -> ENRICHMENT -> OUTCOME

A user/group/X/Telegram hint may create a candidate immediately, but its origin remains USER_SUPPLIED or EXTERNAL_FEED and can never earn autonomous discovery credit.

## Identity truth

Ticker, name, logo, topic[3], or a reused deployer are corroborating attributes only. None is sufficient for VERIFIED_CA.

receipt.from may be stored as deployer/signer corroboration, but is not a stand-alone identity primitive.

Before an exact first-party CA is available, the strongest permitted state is CANDIDATE_RANKED. It must be marked non-trade-authoritative.

IDENTITY_VERIFIED requires:
1. exact chain;
2. exact CA from a pre-frozen first-party publication surface or equivalent canonical primary evidence;
3. canonical on-chain existence/provenance for that exact CA;
4. no unresolved same-symbol/same-name collision;
5. healthy source/transport evidence.

No fuzzy/ticker/name-only promotion. UNKNOWN never passes.

## Deciding experiment: E3 delta_publish

For every eligible launch, freeze before T0:
- exact first-party publication surface;
- surface/content hash and frozen_at;
- external benchmark definition;
- expected chain/venue when known;
- origin and eligibility.

Record:
- Tpre: first eligible prelaunch evidence;
- Tarm: bounded experiment readiness;
- T0: canonical launch time at the precision the chain actually supports;
- T1: detector observation;
- Tpublish: first exact-CA publication on the frozen first-party surface;
- T3: alert creation when applicable;
- Tack: observable downstream acknowledgement if available;
- Text: independently defined external first-seen benchmark;
- censoring/data-health/coverage.

Do not fabricate sub-second T0 when chain timestamps are second-granular. Tdelivery is not claimed unless independently observable. Human reaction belongs in Tack, not transport latency.

Target >=30 genuinely pre-frozen eligible launches.

The VERIFIED-before-public thesis is killed/re-scoped if the preregistered E3 rule concludes median delta_publish is worse than the external-edge budget. No post-hoc surface substitution or exclusion repair.

## Cursor and transport integrity

cursor=head is forbidden for a launch-critical collector.

Any bounded collector must use:
- persistent cursor;
- overlap/backfill on restart;
- deterministic dedup;
- advancing-head/dead-man evidence;
- exact production-client transport preflight including headers/User-Agent;
- source health and requested/returned coverage;
- redundant transport comparison where available.

Transport/query failure, implausible empty result, or unproven coverage is UNKNOWN/DEGRADED, never numeric zero or negative evidence.

The terminal SHADOW-04 result from 2026-09-19 remains FAIL because its preregistered provider-consistency gate failed. This v2 contract must not reinterpret or retry that frozen result.

## Fast path

The minimum alert path, if later justified prospectively, is:
CANDIDATE_RANKED -> PRIMARY_PUBLICATION_SEEN -> IDENTITY_VERIFIED -> ALERT_CREATED.

Wallets, holders, MC/FDV, narrative and R/R are enrichment and must not delay minimum identity verification.

Until prospective evidence proves information value and acceptable latency, these alerts have research authority only.

## E1 and E4 relationship

E1 disclosed-address -> future deployer and E4 dev-buy OOS remain independent challengers under #1134.

They may enrich candidate ranking only after their own prospective gates pass. They cannot substitute for exact primary CA identity.

E2 wallet sensor remains HOLD until its endogeneity/insider/Sybil/sniper falsification survives prospectively.

## Runtime architecture

GitHub remains control/evidence/governance plane.

A finite Actions collector is acceptable for bounded experiments when its lifetime covers the frozen window. It is not evidence that GitHub Actions is adequate for permanent seconds-critical monitoring.

A persistent listener/websocket/webhook worker may be evaluated only after E3 demonstrates enough information value to justify the operational complexity.

## Promotion and kill rules

No promotion from replay or historical showcase.

Promotion requires prospective, source-bound evidence with immutable preregistration and data-health PASS.

Kill/re-scope when any applies:
- E3 kill rule fires;
- identity correction occurs after VERIFIED_CA;
- repeated misses occur despite proven readiness;
- source coverage cannot be established;
- alert latency has no measurable information value;
- human execution latency dominates the opportunity;
- complexity/cost exceeds measured edge;
- functionality is already better owned by an existing runtime.

## Authority

Portfolio execution: FORBIDDEN.
Autonomous buying: FORBIDDEN.
Canonical market-state effect: NONE.
Predictive alpha claim: UNPROVEN until prospective outcomes satisfy existing promotion gates.
