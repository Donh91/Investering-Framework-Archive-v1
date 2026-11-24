# CN / Master Monday signal lineage - draft evidence

Base: `ec36550041fe48b2976c06733dc4bad093b9eed5`. This is a partial implementation, not certification of the mission. No production algorithm, scheduler, historical freeze, decision authority, private data, or paid API is changed. The offline-readable attribution is a proposed future output change only; it is not deployed.

## Reconstructed events

- 2026-08-24: `3cbe4bee4a7aa1c7863b0dd5faa22007c56ae92f` distinguishes Master Monday API contract gaps from immature outcomes. Current `publish_master_monday_outputs.py` still supplies `UNAVAILABLE_API_CONTRACT` when `operational_translation` is absent. W47's stored artifact confirms the condition. The mission references a 2026-10-19 record; that particular document and its complete causal history remain to be verified.
- 2026-11-09 09:48:26 UTC: `0df77e9348081bd8f220b796b0b7e343deb9d8e3` introduces fixed sequence source-based issuer.
- 2026-11-09 09:49:22 UTC: `c4412693d29b3b10e485221e7ecac7c04e4f6c5f` replaces the publisher's `call_openai(..., context, ...)` with `build_offline_value`. Rich context being previously supplied is proven; the prior model's actual incremental use and predictive edge are UNKNOWN.
- 2026-11-15: `efe72c7a4d3dd504126fdf391a755fb8a3436be2` isolates offline issuance from paid API HOLD. The added budget tests enforce offline operation but do not test retained market-signal sensitivity. Continuity and semantic completeness are different properties.

## Bounded source-to-decision evidence

`build_weekly_cycle_navigator.py` supplies context, range baseline and previous machine package to `build_offline_value`. The daily path consumes completed-week BTC/ETH open and close, baseline asset low/high, and fixed sequences. The prior freeze is copied; pullback protection state is explicitly inherited, not reevaluated. The code requires week identity, 168 observed hours, source capture paths, baseline readiness and a prior package; those are eligibility checks, not evidence that the individual non-price signals affected a decision.

| Family | Proven status in the tested issuer | Evidence / limit |
| --- | --- | --- |
| BTC and ETH price | DIRECT_NUMERIC_DRIVER | Real W47 inputs; price mutation changes BTC daily path. |
| Range baseline | DIRECT_NUMERIC_DRIVER | Low/high bound path and bands. |
| ETHBTC, ETF, rotation context, retained spot-flow and OI coverage | DISCONNECTED from issuer output for the tested mutations | Actual W47 nested fields replaced one at a time; full issuer return unchanged. This does not establish that every possible source encoding has been traced end-to-end. |
| Breadth, BTC.D, macro, liquidation, funding, research | UNKNOWN / no proven issuer consumption | Synthetic top-level mutations are negative probes, not proof of upstream source presence or complete end-to-end lineage. |
| Pullback | INHERITED | Protection state comes from previous issue; not a current fresh veto. |
| Master Monday | POINTER ELIGIBILITY; other effects UNKNOWN | Week pointer checked; injected context does not change issuer output. No claim about other upstream processes. |
| Price outcomes | SCORING_ONLY | Prior range evaluated against completed week; not evidence of incremental forecast skill. |

W48 exact-close replay: W47 `03_DAILY_CAPTURE_LOGS/weekly/2026/W47.json` SHA-256 `ca1e2ab0ab25c890fa3373ed656e5d312a5071c7c01c0d6d74cb281544dad258`; W48 baseline `05_CYCLE_NAVIGATOR/range_baselines/forecasts/2026/W48.json` SHA-256 `ed9afad3da8091a4b21898fbd9988ff5f2ddb31a4bcf1a3a2e384c2ffdef3bb8`; W48 freeze `05_CYCLE_NAVIGATOR/weekly/2026/W48/CYCLE_NAVIGATOR_FORECAST_FREEZE.json` SHA-256 `c1ee5ead33c0b16cd6b0b1a60474b3710af74d90625ec7be9d56246a328b4fd0`. Test asserts 14/14 two-decimal expected closes. This proves reproduction, not accuracy or prospective skill. Broad weekly range and daily interval envelopes must not be conflated.

## What is implemented and what is not

- A shadow-only typed snapshot prototype rejects malformed hashes/authority and duplicate IDs, and produces UNKNOWN for late, stale, contradictory or missing values. A syntactically valid hash does not verify underlying bytes. Provider first-known clocks, source independence, authorized thresholds and upstream bindings remain unverified.
- A draft machine-readable domain inventory and manifest comparison helper detects removal or changes to fields. Entries marked UNKNOWN are placeholders, not a completed constitution. The helper is not wired to protected required PR checks and does not enforce independent approval or prove non-bypassability.
- An explicit price-only/degraded sentence is proposed for future readable output; other public surfaces and complete-research scoring have not been audited or repaired.
- Counterfactual tests cover the actual issuer, not a full producer-to-consumer DAG or source clocks. Full historical #18 and W36-W46 precedence reconstruction, a semantic completeness gate, Master Monday typed translation, sequence-informed challenger, independent matched C0/C1/C2 evaluation and promotion evidence are NOT COMPLETE. Effective independent N for a restored challenger here is zero; edge is UNKNOWN. No number of captured hours or complete price paths proves skill.

Run `python -m unittest tests.cycle_navigator.test_signal_lineage_restoration tests.cycle_navigator.test_weekly_offline_issuer -v`. No GitHub Actions result is implied.

## Follow-up implementation on the same draft branch

`weekly_shadow_analysis_v1.py` verifies SHA-256 against a caller-provided expected digest, requires the weekly source's self-declared generated clock before freeze, checks the completed ISO week and 168-hour readiness, and derives separate BTC, ETH and ETH/BTC open-to-close facts with a typed non-trading operational translation. W47 verifies BTC DOWN, ETH DOWN, ETH/BTC UP. Missing families remain UNKNOWN. This proves a local executable analysis, not a restored Master Monday publisher: the caller still needs an independently authenticated source-byte binding and first-known clock, neither of which is established merely by a digest or a self-declared clock. The W47 freeze binds a pointer, and that pointer does not include the target weekly file's digest. The output is not wired into canonical Master Monday.

The sequence routine checks source byte digests and strict ordering and returns `ORDERED_CLAIMS_ONLY`; event classification and first-known times remain caller claims, not validated features or a price model. Late, equal-time, missing and unverified-source events abstain. No threshold or production authority was added.

The manifest now lists all 12 domains and a candidate PR workflow runs the local semantic tests and compares a base manifest where available. It has not been shown to be a GitHub-required check and cannot itself prevent a future PR modifying or disabling the workflow/guard; branch protection, independent review and anti-bypass evidence remain mandatory. Its domain fields do not prove end-to-end sensitivity for every family. The first introduction has no base manifest to compare, and requires careful review. Current effective independent N for the restored challenger remains zero; no claimed skill improvement.

## Prospective weekly producer byte binding

The existing weekly orchestration controller now places a canonical-week capture path, actual SHA-256 and explicit UNKNOWN first-known status into the evidence freeze. The existing weekly publication workflow creates a write-once-per-freeze sidecar and extends the existing durable readback to cover both the sidecar and exact weekly source bytes. It fails if bytes change between freeze and readback. The sidecar uses an exclusive local write; this alone is not a protected GitHub immutability rule. Consumers can verify freeze hash, pointer hash, source ID/path/week/bytes and stored sidecar via `verify_sidecar`. These checks verify content integrity, not independently authenticated first-known time, provider-time semantics, or retrospective scientific eligibility.

The original W47 freeze lacks this byte binding. The real historical W47 test therefore returns UNKNOWN and must not be retroactively counted as point-in-time evidence. The local controller integration test exercises a new binding with the real W47 bytes as a synthetic fixture; it is not authentic historical proof. A separate mutation changes ETH/BTC in the provisional W47 shadow analysis and changes its structured output, while remaining first-known unverified. The canonical Master Monday consumer and CN decision are not wired, and no forecast-impact claim is made. Review producer, workflow and sidecar code at the exact head before any merge. No rule or required-check setting has been changed.
