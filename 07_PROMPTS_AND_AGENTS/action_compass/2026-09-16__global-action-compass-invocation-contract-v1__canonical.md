# Global Action Compass Invocation Contract v1.0

**Date:** 2026-09-16  
**Status:** CANONICAL_OPERATIONAL_ROUTING_CONTRACT  
**Owner:** MAIN_FRAMEWORK  
**Scope:** all repository-aware Investering-framework threads, agents and replacement threads  
**Authority:** invocation routing, current-state decision translation and human output rendering only  
**Effective:** on merge to canonical `main`  
**Machine route:** `07_PROMPTS_AND_AGENTS/action_compass/GLOBAL_ACTION_COMPASS_ROUTE_v1.json`  
**Decision vocabulary owner:** `02_DATA_PING/protocols/2026-08-25__three-horizon-action-compass-output-contract-v1__canonical.md`  
**Current production-data owner:** `00_ARCHIVE_CONTROL/2026-09-14__autonomous-data-authority-transition-v1__canonical.md`

## 1. Purpose

Make the framework Action Compass callable from any Investering thread with a minimal prompt while preserving current authority, freshness discipline and compact output.

The user must not need to remember a thread name, DATA PING version, workflow name, repository path or agent name. A compass invocation is a request to resolve the **current** framework state and translate it into a short action view.

This contract does not create a new market engine, forecast engine, signal, threshold, score, portfolio executor or evidence source. It is a global routing and rendering layer over current accepted framework evidence.

## 2. Global invocation rule

Normalize the user message by trimming whitespace, lower-casing and ignoring ordinary trailing punctuation.

The following exact prompts are hard triggers in every repository-aware Investering thread:

```text
kompas
handlekompas
compass
```

The same route also applies when one of those words is clearly used as the primary imperative, for example `send kompas`, `kompas nu`, `vis handlekompas` or `current compass`.

An exact one-word hard trigger must not require a clarification question.

Do not trigger this route when the word is clearly being discussed as an object or term rather than invoked, for example a question about a physical compass, a UI icon or the spelling of the word.

## 3. Current-state authority route

A compass invocation is a **current-state task**, not a DATA PING task merely because the historical Action Compass contract lives under `02_DATA_PING/`.

Resolve evidence in this order:

```text
AGENTS.md
-> LATEST_OPERATIONS_DASHBOARD.json / LATEST_HANDOFF.json
-> 00_ARCHIVE_CONTROL/CURRENT_PRODUCTION_DATA_AUTHORITY.json
-> exact current autonomous pointers, receipts and hash-bound outputs
-> current Main Framework accepted interpretation / ratification
-> current Master Monday / Cycle Navigator / short-horizon outputs that are actually eligible
-> bounded live context from approved tools/connectors only when needed to interpret freshness or current price context
-> Global Action Compass decision translation
```

When the official Daily Compass owner is active, resolve
`04_MARKET_LEARNING/handlekompas/official/LATEST_COMPASS.json` and its exact immutable,
hash-matching target before composing the visible answer. That artifact is the primary current
navigation record for `Kompas` / `Handlekompas` / `Compass`; bounded fresh live context may
clarify it but may not silently rewrite the freeze. A missing, stale or hash-mismatched pointer
fails closed and must never fall back to old chat prose.

The official machine record preserves `NEXT_12H`, `NEXT_1_3D`, `NEXT_5_7D`, the governed
`CYCLE_ALTCOINS_3_8W` lane, and the canonical BTC → ETH → large → mid → small → micro ladder.
Every Compass invocation performs a freshness evaluation before rendering. If the canonical
Auto Market State owner has a newer packet SHA than the latest official Compass source binding,
the route may dispatch the existing Official Compass workflow with `run_reason=ON_DEMAND` and
resolve the resulting immutable pointer before rendering. If the source packet is unchanged,
reuse the existing freeze; the render request itself must not manufacture a prospective receipt.

Hard rules:

- Never promote an old manual DATA PING, `latest` filename or stale thread summary to current authority.
- Never create a parallel forecast merely to fill a missing compass field.
- Follow the freshness and eligibility rules of the current owner files; do not invent a new global freshness threshold here.
- `DATA_MISSING` is `UNKNOWN`, not bearish evidence.
- Material source conflict remains explicit `DATA_CONFLICT` until resolved.
- If the current route cannot support an action horizon, that lane fails closed to `AFVENT` or `INGEN HANDLING` with `KRÆVER FRISKE DATA` or the exact blocking reason.

## 4. Decision semantics

The compass reuses the controlled action vocabulary and altcoin-regime vocabulary from the active Three-Horizon Action Compass owner. Do not create synonyms that change machine meaning.

Primary actions remain:

```text
KØB
TOP-UP
GRADUERET KØB
FORBERED KØB
AFVENT
HOLD
REDUCER
EXIT
INGEN HANDLING
```

Altcoin regime remains one of:

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

Warnings remain separate from actions. A warning is not permission to `REDUCER` or `EXIT`.

The compass may include one plain-language market-direction note such as `bull structure intact`, `neutral`, `bear risk rising` or equivalent when supported by current evidence. That note is explanatory only and does not create a new machine state.

## 5. Required human output

The default response is compact and text-only. It should normally fit on a phone screen without analytical filler.

Use this structure:

```markdown
### 🧭 KOMPAS
Status: <one short current-state sentence>

**NU · 0-3 dage**
Handling: <controlled action>
ETA: <validity / next meaningful decision point>
Kort sagt: <one sentence>

**NÆSTE VINDUE · ca. 5-7 dage**
Handling: <controlled action>
ETA: <date/window>
Kort sagt: <one sentence + decisive condition>

**CYKLUS / ALTCOINS · 3-8 uger**
Retning: <controlled altcoin state + optional plain-language direction note>
Handling: <controlled action>
ETA: <through-date, range or paused/unavailable>
Advarsel: <only when material>

**Konklusion:** <one direct action sentence>
```

Rendering rules:

- Keep each lane short; do not repeat the same rotation story in multiple sections.
- Show ETA where it helps action: next top-up/buy window, expected confirmation window, or meaningful bull/bear decision window.
- Do not print method explanations, internal workflow names, API/provider lists, raw source tables or governance prose unless the user explicitly asks.
- If the state is unchanged, say `UÆNDRET` once rather than rewriting a long justification.
- If one lane is unsupported, fail that lane closed without making the rest of the compass verbose.

## 6. No-widget / internal-tool rendering policy

Compass threads are human decision surfaces, not tool dashboards.

**Visible output policy: TEXT_ONLY.**

Do not intentionally render any of the following in a normal `kompas`, `handlekompas` or `compass` response:

```text
GenUI widgets
market cards
interactive charts
API result cards
connector result cards
raw JSON
raw tool output
source dumps
internal provider diagnostics
```

Approved APIs, connectors, web retrieval and repository tools may be used **internally** to obtain or verify evidence. Their existence is not user-facing content.

Use a non-widget retrieval route when equivalent evidence is available. If the host platform imposes a non-optional system UI surface, the framework must still keep its own authored output text-only and must not add redundant cards or widgets.

Small provenance citations may appear only when required by the host/source policy or when the user explicitly asks for sources; they must not replace the compact compass itself.

## 7. Stability and anti-flip-flop rule

A compass invocation must translate the framework's current accepted state, not react to one noisy datapoint in isolation.

Before changing a prior action state:

1. resolve fresh current authority;
2. determine whether the relevant owner considers the new evidence eligible and material;
3. preserve current state when the evidence does not clear the existing confirmation/invalidation logic;
4. change the action only when the accepted state actually changes or the prior action validity expires.

A short-horizon lane may expire. An expired lane is not silently rolled forward from old prose.

If no fresh evidence supports renewal:

```text
Handling: AFVENT
Kort sagt: KRÆVER FRISKE DATA
```

This rule reduces `wait -> prepare -> wait -> prepare` noise without inventing hysteresis thresholds outside the current owners.

## 8. Render request versus fresh evidence ingest

A plain compass invocation is a **render/current-state request with a freshness evaluation**. It is not automatically a new prospective evidence row.

Therefore:

- compare the current canonical Auto Market State packet SHA with the source packet SHA bound by the latest official Compass;
- when the owner packet changed and is eligible, use the existing Official Compass `workflow_dispatch` path to create one `ON_DEMAND` immutable freeze, then resolve that pointer before rendering;
- when the owner packet is unchanged, reuse the existing immutable freeze and create nothing;
- when the pointer is stale but no newer eligible owner evidence exists, fail closed rather than minting a synthetic fresh timestamp;
- do not extend an old receipt horizon by rendering it again;
- if the same turn separately contains a fresh eligible DATA PING / RAW ingest, the existing fresh-ingest receipt rules still apply;
- if another current owner already creates a prospective decision record, do not duplicate it under this contract.

This gives the user a genuinely on-demand Compass when new canonical evidence exists while preserving the scientific meaning of the accountability ledger.

## 9. Language and naming

Default user-facing title in Danish threads:

```text
🧭 KOMPAS
```

`HANDLEKOMPAS` remains an accepted user trigger and historical label. `COMPASS` is the English trigger and may be used as the title when the user is writing in English.

The user should never need to know which backend owner, API, model or workflow supplied the evidence unless they ask.

## 10. Validation checklist

A compass response is incomplete if any applicable check is `NO`:

```text
GLOBAL_TRIGGER_RESOLVED: YES/NO
CURRENT_AUTHORITY_RESOLVED: YES/NO
CURRENT_DATA_ROUTE_USED: YES/NO
ON_DEMAND_FRESHNESS_EVALUATED: YES/NO
NO_STALE_DATA_PING_PROMOTED: YES/NO
THREE_HORIZONS_PRESENT: YES/NO
CONTROLLED_ACTIONS_USED: YES/NO
ETA_PRESENT_WHERE_ACTIONABLE: YES/NO
WARNING_SEPARATE_FROM_ACTION: YES/NO
STALE_OR_CONFLICTING_DATA_FAILS_CLOSED: YES/NO
NO_DUPLICATE_ROTATION_SECTIONS: YES/NO
VISIBLE_OUTPUT_TEXT_ONLY: YES/NO
NO_RAW_API_OR_TOOL_OUTPUT: YES/NO
NO_RENDER_ONLY_RECEIPT_CREATED: YES/NO
NO_AUTOMATIC_PORTFOLIO_EXECUTION: YES/NO
```

## 11. Authority boundary

This contract may:

- make the compass globally invocable across Investering threads;
- resolve current framework authority before rendering;
- reuse current decision vocabulary;
- compress the current state into a stable phone-friendly output;
- use internal tools and APIs for evidence retrieval without exposing their UI as authored output.

It may not:

- place trades;
- create or change market thresholds, scores or model weights;
- promote research or shadow hypotheses;
- rewrite frozen forecasts or outcomes;
- make manual DATA PING current again;
- create a new market engine or duplicate forecast path;
- turn a render request into a synthetic prospective observation;
- expose private/restricted provider payloads in public output.

## 12. Cross-thread bootstrap requirement

`AGENTS.md` is the bootstrap enforcement point. Any repository-aware model or agent entering a fresh Investering thread must treat the three hard trigger words as a direct route to this contract before generating the compass.

Conversation memory may improve continuity, but it may not replace current repository verification.
