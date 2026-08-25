# Three-Horizon Action Compass Output Contract v1.0

**Date:** 2026-08-25  
**Status:** CANONICAL_OPERATIONAL_PROTOCOL  
**Owner:** MAIN_FRAMEWORK / CHATGPT  
**Scope:** Main-Framework interpretation outputs after DATA PING or RAW ingest, including all future DATA PING thread versions  
**Authority:** DECISION_TRANSLATION_AND_OUTPUT_ONLY  
**Effective:** on merge to canonical `main`  
**Supersession:** remains mandatory until explicitly superseded by a newer canonical contract

## 1. Purpose

Translate the Main Framework's current evidence and decision state into one short, explicit, non-ambiguous three-horizon compass that a user can act on without re-interpreting the analytical prose.

This contract standardizes communication only. It does not create a market engine, signal, score, threshold, sensor, forecast result or automatic portfolio authority.

The underlying DATA PING / RAW collector remains evidence-only and may continue to state `framework_interpretation: DEFERRED_TO_MAIN_FRAMEWORK` and `portfolio_execution: FORBIDDEN`. The compass is produced only by the Main Framework after resolving current canonical context.

## 2. Mandatory scope

The human-readable `HANDLEKOMPAS` block is mandatory at the end of every Main-Framework response whose primary input is any of the following:

- a DATA PING packet, regardless of DATA PING version;
- a RAW collector packet or RAW market-data message submitted for Main-Framework interpretation;
- a replay or duplicate of such a packet;
- a corrected or superseding DATA PING / RAW packet that changes current interpretation.

It applies across new chats, replacement threads, handovers, agents and future thread versions whenever repository-aware routing is available.

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
    "contract": "THREE_HORIZON_ACTION_COMPASS_v1",
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
```
