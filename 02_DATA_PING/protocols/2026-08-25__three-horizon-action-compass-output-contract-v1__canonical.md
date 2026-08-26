# Three-Horizon Action Compass Output Contract v1.1

**Date:** 2026-08-25  
**Last updated:** 2026-08-26
**Status:** CANONICAL_OPERATIONAL_PROTOCOL  
**Owner:** MAIN_FRAMEWORK / CHATGPT  
**Scope:** Main-Framework interpretation outputs after DATA PING or RAW ingest, including all future DATA PING thread versions  
**Authority:** DECISION_TRANSLATION_AND_OUTPUT_ONLY  
**Effective:** on merge to canonical `main`  
**Supersession:** remains mandatory until explicitly superseded by a newer canonical contract

## 1. Purpose

Translate the Main Framework's current evidence and decision state into one short, explicit, non-ambiguous three-horizon compass that a user can act on without re-interpreting the analytical prose.

This contract is the sole current Main-Framework decision vocabulary for these responses. It standardizes communication and its prospective accountability receipt. It does not create a market engine, signal, score, threshold, sensor, forecast result or automatic portfolio authority.

The historical Exit Ladder vocabulary `E0-E7` is `RETIRED_UNIMPLEMENTED`. It is not a parallel decision vocabulary, may not receive rows and may not be inferred from Action Compass states, warnings or actions.

The underlying DATA PING / RAW collector remains evidence-only and may continue to state `framework_interpretation: DEFERRED_TO_MAIN_FRAMEWORK` and `portfolio_execution: FORBIDDEN`. The compass is produced only by the Main Framework after resolving current canonical context.

## 2. Mandatory scope

The human-readable `HANDLEKOMPAS` block is mandatory at the end of every Main-Framework response whose primary input is any of the following:

- a DATA PING packet, regardless of DATA PING version;
- a RAW collector packet or RAW market-data message submitted for Main-Framework interpretation;
- a replay or duplicate of such a packet;
- a corrected or superseding DATA PING / RAW packet that changes current interpretation.

It applies across new chats, replacement threads, handovers, agents and future thread versions whenever repository-aware routing is available.

A fresh ingest also requires one persistence attempt under section 10.1. A duplicate or replay still receives the human `HANDLEKOMPAS`, but it is not a fresh observation and must not create a second receipt.

It does **not** modify the collector's machine-to-machine wire format and must not be inserted inside a frozen RAW packet, collector JSON, GitHub Actions log, source receipt or shadow-only research artifact.

## 3. Required three lanes

Every `HANDLEKOMPAS` must contain exactly these three user-facing lanes, in this order.

### Lane 1 - NU: KØB / TOP-UP / HANDLEPLAN

Purpose: what to do now.

- Nominal decision domain: 0-3 days.
- The output must state the **actual evidence-supported validity**, for example `next 24 hours`, `next 48 hours` or `next 48-72 hours`.
- Never label a view as valid for 72 hours when the evidence only supports 24 hours.
- Must include one explicit action and one short reason.

### Lane 2 - NÆSTE KØBSVINDUE / HANDLEPLAN

Purpose: what the Main Framework currently expects to be the best action window roughly 5-7 days ahead.

- Default forward window: snapshot time +5 through +7 days.
- Must show explicit dates or an exact forward window.
- Must include one explicit action and one short reason/condition.
- This lane is a current forward plan, not a promise that the market will follow the base case.

### Lane 3 - ALTCOIN-MARKEDSKOMPAS

Purpose: preserve the larger directional map so daily noise does not erase the expected regime path.

- Default horizon: 3-4 weeks / 21-28 days.
- It may extend to 4-8 weeks or another longer horizon when the evidence and active regime require it.
- The output must state an explicit through-date or date range.
- Must identify the current expected altcoin regime/path in plain language.
- Must surface a direct warning when the Main Framework sees rising risk of parabolic altseason, distribution, exit risk or structural breakdown.

## 4. Controlled action vocabulary

The primary action must be exactly one of the following machine meanings, rendered with the Danish user label shown here:

| Machine action | User label |
|---|---|
| `BUY` | `KØB` |
| `TOP_UP` | `TOP-UP` |
| `SCALE_IN` | `GRADUERET KØB` |
| `PREPARE_BUY` | `FORBERED KØB` |
| `WAIT` | `AFVENT` |
| `HOLD` | `HOLD` |
| `REDUCE` | `REDUCER` |
| `EXIT` | `EXIT` |
| `NO_ACTION` | `INGEN HANDLING` |

Do not use hedged action labels such as `måske køb`, `lidt positiv`, `overvej eventuelt` or other wording that forces the user to reinterpret the recommendation.

Uncertainty belongs in the reason/evidence status, never inside the action label.

If evidence is insufficient to justify a proactive action, the action must default to `AFVENT` or `INGEN HANDLING`, with the reason stating that evidence is insufficient.

## 5. Altcoin compass vocabulary

Lane 3 must use one primary regime state:

```text
DEFENSIVE
CONSOLIDATION
PRE_ROTATION
ROTATION
BROAD_ALTSEASON
PARABOLIC_ALTSEASON
DISTRIBUTION
EXIT_RISK
UNCLEAR
```

Optional warning, exactly one:

```text
NONE
PARABOLIC_ALTSEASON_WARNING
DISTRIBUTION_WARNING
EXIT_WARNING
STRUCTURAL_BREAKDOWN_WARNING
```

Warning and action are orthogonal fields:

- a warning records an evidence condition that deserves attention;
- an action records the Main Framework's current decision translation;
- `DISTRIBUTION_WARNING` does not imply `REDUCE` or `EXIT`;
- `EXIT_WARNING` does not by itself authorize `EXIT`;
- `REDUCE` or `EXIT` requires independent Main-Framework justification under current canonical authority;
- no warning may be converted to an Exit Ladder state.

`ROTATION` and `BROAD_ALTSEASON` are not synonyms. A valid ETH/BTC or large-cap rotation signal must not be presented as broad altseason unless the current canonical breadth/transmission evidence supports that conclusion.

## 6. Time and expiry discipline

Each lane must visibly state its horizon. Lane 1 and Lane 2 must also be anchored to the current snapshot or interpretation timestamp.

Machine-readable mirrors, when used, must include:

```text
as_of_utc
valid_from_utc
valid_until_utc OR through_date
```

Human-readable output should show Copenhagen local time/date (`CET` or `CEST` as applicable) when a clock-time expiry matters.

A short-horizon recommendation expires. It must not be silently rolled forward because a duplicate packet was replayed or because a new thread inherited old prose.

## 7. Duplicate, replay and stale-input rule

If an identical DATA PING / RAW packet is replayed:

- do not count it as a new observation;
- do not create artificial persistence;
- do not extend the previous `valid_until` merely because the packet was replayed;
- still show the three-lane `HANDLEKOMPAS` because it is mandatory output;
- mark the compass `UNCHANGED_FROM_PRIOR_FRESH_INGEST` when still valid.

If the prior Lane-1 validity has expired and no fresh evidence is available, Lane 1 must become:

```text
Handling: AFVENT
Reason: KRÆVER FRISKE DATA
```

The same principle applies to any forward lane whose evidence basis is no longer current enough to support its stated horizon.

## 8. Evidence and authority rule

The compass must be derived from the Main Framework's resolved current state, not from the collector's own interpretation, one shadow model, conversation memory or one isolated sensor.

Before producing the compass, Main Framework must resolve current authority using the repository routing order and the active DATA PING decision-context owners.

The compass may translate a ratified framework state into plain action. It may not self-ratify a new rule, promote a shadow hypothesis, rewrite a frozen forecast or create automatic execution permission.

`DATA_MISSING` remains `UNKNOWN`, not bearish evidence. Missing or conflicting evidence may reduce confidence or force `AFVENT`, but may not be fabricated into a directional signal.

## 9. Mandatory human format

Keep the block compact. Each lane should normally use no more than three short lines.

```markdown
### 🧭 HANDLEKOMPAS

**1. NU - KØB/TOP-UP**
Horisont: næste 24 timer, gyldig til 26. aug 17:30 CEST
Handling: AFVENT
Kort sagt: Vent på breadth-repair og fortsat stabilisering.

**2. NÆSTE KØBSVINDUE**
Horisont: 5-7 dage, 30. aug-1. sep
Handling: FORBERED KØB
Kort sagt: Et bedre entry kan opstå efter pullback, hvis de aktuelle confirmations holder.

**3. ALTCOIN-MARKEDSKOMPAS**
Horisont: 3-4 uger, til ca. 22. sep
Retning: PRE_ROTATION
Handling: HOLD
Kort sagt: Strukturen er konstruktiv, men bred altseason er endnu ikke bekræftet.
```

The wording after `Kort sagt:` must be plain-language decision translation, not a miniature analyst report.

## 10. Machine-readable mirror

When the surrounding Main-Framework output is JSON or explicitly machine-readable, include this semantic object in addition to, or as the machine equivalent of, the human block:

```json
{
  "action_compass": {
    "contract": "THREE_HORIZON_ACTION_COMPASS_v1_1",
    "as_of_utc": "<timestamp>",
    "near_term": {
      "horizon_hours": 24,
      "valid_from_utc": "<timestamp>",
      "valid_until_utc": "<timestamp>",
      "action": "WAIT",
      "reason": "<short plain reason>"
    },
    "next_window": {
      "window_start_date": "<YYYY-MM-DD>",
      "window_end_date": "<YYYY-MM-DD>",
      "action": "PREPARE_BUY",
      "reason": "<short plain reason>"
    },
    "altcoin_compass": {
      "horizon_days": 28,
      "through_date": "<YYYY-MM-DD>",
      "state": "PRE_ROTATION",
      "action": "HOLD",
      "warning": "NONE",
      "summary": "<short plain-language expected path>"
    }
  }
}
```

The object is semantic, not a new market schema. Existing surrounding packet schemas remain untouched unless separately governed.

## 10.1 Immutable decision-receipt authorization

This owner authorizes one bounded implementation of its own prospective receipt. It does not authorize a new test or market engine.

Authorized follow-on implementation surfaces, which are not current until the implementation pull request merges:

```text
schema: 02_DATA_PING/schemas/THREE_HORIZON_ACTION_COMPASS_RECEIPT_v1_1.schema.json
writer_and_validator: scripts/learning/action_compass_accountability.py
receipt_root: research/framework_memory/action_compass_receipts/
outcome_root: research/framework_memory/action_compass_outcomes/
existing_test_owner: CHIEF_REPRODUCIBILITY / T9
existing_miss_consumer: ADAPTIVE_DECISION_MISS
```

For each fresh eligible ingest, Main Framework must persist exactly one immutable JSON receipt containing:

```text
contract
receipt_id
dedup_id
input_packet_sha256
input_contract
source_reference
source_timestamp_utc
canonical_repository
canonical_commit_sha
owner_contract
interpreted_at_utc
producer_model
action_compass
data_quality_tags
rationale_tags
baseline_observer
persistence_status: PERSISTED
portfolio_execution: false
```

Receipt rules:

1. `input_packet_sha256` is the SHA-256 of the immutable source packet. Use canonical JSON bytes when the source is JSON and exact source bytes otherwise.
2. `dedup_id` and `receipt_id` are deterministic from the input packet hash under the implementation contract. Replaying the same packet is `DUPLICATE_NOOP`, not a new row.
3. A corrected packet must have a new immutable content hash and may therefore produce a new receipt. The correction must not overwrite the prior receipt.
4. `canonical_commit_sha` binds the interpretation to the exact public control-plane commit used at decision time.
5. `action_compass` freezes all three lane states, actions, warning and validity fields before outcomes.
6. Warning and action remain separate machine fields. A downstream consumer must not infer one from the other.
7. `data_quality_tags` and `rationale_tags` are bounded tags, not copied analytical prose.
8. `baseline_observer` may bind exact pre-outcome public evidence paths and hashes for later measurement. It never grants those observations decision authority.
9. The receipt must exclude full chat text, conversation summaries, holdings, quantities, account data, credentials and restricted provider values.
10. No historical chat backfill is allowed. Eligibility begins only after the implementation is merged and applies to fresh ingests from that point forward.
11. If repository write capability is unavailable, the response must report `persistence_status: NOT_PERSISTED`. That interpretation is user-facing only and cannot count as a prospective row.
12. A failed write is also `NOT_PERSISTED`. It must not be represented as durable evidence.

## 10.2 Outcome-sidecar lifecycle

Each persisted receipt may mature into at most one immutable sidecar for each frozen horizon:

```text
24H
7D
30D
90D
180D
```

Sidecars remain separate files. A single receipt must not be expanded retrospectively into multiple source rows.

The outcome owner may measure only continuous, descriptive quantities from the frozen public observer binding:

- terminal return;
- subsequent maximum drawdown from the frozen start;
- subsequent maximum upside from the frozen start;
- elapsed hours to trough;
- elapsed hours to first recovery of the frozen start after the trough;
- observation count and observed span;
- normalized full-exit capital preserved and upside foregone versus continuous one-unit hold.

These quantities are observational counterfactuals, not portfolio results. They assume no personal holdings, trade size, fees, taxes, slippage or execution. `REDUCE` is not assigned an invented percentage. When a required binding is unavailable, the sidecar records explicit censoring instead of inference.

Outcome sidecars must not contain `HIT`, `MISS`, new market labels, new thresholds, promotion decisions or automatic action. They may be consumed by the existing T9 reproducibility review and Adaptive Decision Miss discovery only. Neither consumer may self-promote a rule, sensor or action.

## 11. Output validation checklist

A DATA PING / RAW Main-Framework response is output-incomplete if any answer is `NO`:

```text
THREE_LANES_PRESENT: YES/NO
LANE_1_EXPLICIT_VALIDITY: YES/NO
LANE_2_EXPLICIT_5_7D_WINDOW: YES/NO
LANE_3_EXPLICIT_3_4W_OR_LONGER_HORIZON: YES/NO
PRIMARY_ACTIONS_CONTROLLED_AND_UNAMBIGUOUS: YES/NO
ALTCOIN_STATE_DISTINGUISHES_ROTATION_FROM_BROAD_ALTSEASON: YES/NO
DUPLICATE_REPLAY_DID_NOT_EXTEND_VALIDITY: YES/NO/NOT_APPLICABLE
NO_COLLECTOR_AUTHORITY_INCREASE: YES/NO
NO_AUTOMATIC_PORTFOLIO_EXECUTION: YES/NO
WARNING_AND_ACTION_STORED_SEPARATELY: YES/NO
FRESH_INGEST_PERSISTENCE_STATUS_EXPLICIT: YES/NO
DUPLICATE_CREATED_NO_NEW_RECEIPT: YES/NO/NOT_APPLICABLE
```

Failure of the formatting contract does not invalidate the underlying market data. It means the Main-Framework response must be corrected before it is treated as a complete user-facing DATA PING / RAW interpretation.

## 12. Non-goals and safety boundary

```text
new engine: NO
new sensor: NO
new score: NO
new threshold: NO
new automatic signal: NO
collector wire-format change: NO
automatic portfolio execution: NO
Main Framework interpretation authority: UNCHANGED
user-facing decision translation: MANDATORY
cross-thread persistence: CANONICAL_VIA_GITHUB
sole current decision vocabulary: THREE_HORIZON_ACTION_COMPASS_v1_1
E0_E7 status: RETIRED_UNIMPLEMENTED
prospective decision receipt: AUTHORIZED_OWNER_EXTENSION
historical chat backfill: FORBIDDEN
receipt outcome sidecars: 24H_7D_30D_90D_180D
```
