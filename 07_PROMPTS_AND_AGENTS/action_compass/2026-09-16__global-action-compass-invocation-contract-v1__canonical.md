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

For an explicit month-ahead / 21-30D / 4-8W request, also resolve
`04_MARKET_LEARNING/handlekompas/strategic/LATEST_STRATEGIC_COMPASS.json` and hash-verify its
immutable anchor when present. The 21-30D lane is valid only when it was prospectively frozen by
the governed weekly Cycle Navigator decision projection. The 4-8W lane remains Cycle Navigator-owned.
Never stretch `NEXT_2_3W` into a month forecast and never create a parallel long-cycle engine.
If the strategic pointer/anchor is absent because the new forward-only system has not yet produced
its first anchor, state that limitation rather than reconstructing one with hindsight.
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

## 3.1 Permanent complete Compass across chat and site (2026-10-08)

**User mandate:** Every ordinary `Kompas` request requires one comprehensive current, critical analysis of ALL relevant Compass layers, not just the Official Daily Compass. The same evidence-selection and safety policy powers the Cycle Navigator site's public composite Compass readback.

**Required source cross-read, every invocation:** canonical production Auto Market State and freshness, immutable Official Daily Compass, Native Handlekompas, Shadow Compass v2, governed weekly Master Monday/Cycle Navigator, Strategic Compass, and currently eligible pullback/distribution, SELL/Swing, re-entry, rotation, market health, Bull/Bear and outcome accountability where available. Inspect each latest source and its contract, timestamp, origin, provenance and authority; record a missing or stale source as `NOT_VERIFIED`, `UNAVAILABLE` or `DEGRADED`. Shadow is an independent NON-BINDING analytical challenge, never an owner of official action, threshold, score or site-confirmed cycle phase. Do not count common underlying source packets as multiple independent confirmations.

**Default complete human output:** clear STATUS / HANDLING / TID for BTC, ETH, large, mid, small, micro and memes; horizons 12–24h, 1–3d, 5–7d, 2–3w, 21–30d and 4–8w, with source-backed direction/path/ranges, pullback/distribution and separate SELL/Swing/re-entry assessment. Mark unsupported windows and ranges as unavailable. Identify official-vs-shadow agreement/disagreement. End with `🧠 MIN FORTOLKNING — <SPECIFIC FORWARD HORIZON>`: independent, evidence-led market direction and next action without hopium. Specific narrower user windows may abbreviate presentation, NEVER the cross-read. Keep iPhone-friendly and strictly TEXT_ONLY / no widgets.

**Public site consumption:** the site must consume a sanitised, reproducible full-stack Compass projection assembled from the same current verified owner evidence as chat; this is a readback/interpretation layer, never a new market engine, owner or new prospective receipt. Site may show the latest non-binding AI research outlook clearly separated from the official decision, including when official navigation is degraded; it must never turn shadow or live prices into a verified BUY/SELL or imply the official status recovered. Public snapshots must carry source-alignment, freshness and unavailable labels and must not leak private/restricted data. Site builds are not a substitute for an autonomous agent or a claim of fresh AI inference.

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

The default response is compact, text-only and phone-first. The short template below is abbreviated; complete cross-layer coverage remains mandatory under Section 3.1.

The following block defines the minimum decision semantics for packet/legacy text renderings; user-invoked chat Kompas additionally follows the **mandatory two-table presentation** in section 5.1:

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

## 5.1 Permanent two-table presentation for on-demand chat Kompas

For every user-invoked `kompas`, `handlekompas` or `compass` request in a repository-aware Investering chat, render **both** compact, phone-first Markdown tables below in this order. These two views are REQUIRED, not optional decorations. Keep the rest of the response brief. They do not change the official Compass machine schema, its freeze, governed actions, source authority or scoring.

**A. Mit taktiske Kompas**

| Tid | Retning | Handling |
|---|---|---|
| 0–12t / 24t* | ↑ / → / ↓ / Ukendt | KØB / HOLD / AFVENT / ... |
| 1–3 dage | ... | ... |
| 5–7 dage | ... | ... |
| 2–3 uger | ... | ... |
| 4–8 uger | ... | ... |

`*` Use the exact supported near-term validity (e.g. 0–12 hours, not 24 hours unless evidenced). Display the longer-cycle lane as `Ukendt / AFVENT` when unavailable; 21–30D is only available from its dedicated governed strategic owner. No fabricated range, trend, score or ETA to fill a cell.

**B. Aktivklasser**

| Aktiv | Status | Handling |
|---|---|---|
| BTC | ... | ... |
| ETH | ... | ... |
| Large caps | ... | ... |
| Mid caps | ... | ... |
| Small caps | ... | ... |
| Microcaps | ... | ... |
| Memes | ... | ... |

Rules for both tables:

- The `Retning` / `Status` cells summarize the latest eligible official owner observations. The `Handling` cells use ONLY the active controlled action vocabulary (`KØB`, `TOP-UP`, `GRADUERET KØB`, `FORBERED KØB`, `AFVENT`, `HOLD`, `REDUCER`, `EXIT`, `INGEN HANDLING`), and must NOT convert directional optimism or a risk warning into buy/sell authority.
- The two tables remain visible even during `DATA_DEGRADED`, source conflicts, unsupported horizons or missing meme owner. State `Ukendt` / `AFVENT` or `INGEN HANDLING` with a short reason. Do not infer meme permission from microcaps or create a 24-hour forecast from a 12-hour signal.
- After the two tables and any material `SELL / Swing` note, end with `🧠 MIN FORTOLKNING — <TIME HORIZON>` (1–3 concise sentences): give an evidence-grounded expected sequence (`↗ → ↔ → ↘` etc.) only if supported. Label any independent assistant judgement `Selvstændig fortolkning, ikke nyt officielt maskinsignal`. Never silently overwrite the official direction or governed action.
- Preserve the separate `SELL / Swing` or protection note when materially relevant, including pullback/distribution/re-entry warning versus action and any supported ETA. No duplication of the asset/rotation table.
- These are plain text Markdown tables, not widgets. Max three columns per table, no cards, carousel, GenUI, charts, unsupported confidence scores or wide layouts. Layout only; do not mint a new forecast receipt by rendering.

This user-facing format supplements rather than supersedes the Three-Horizon action vocabulary and all exact current-pointer / fail-closed rules.

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
ALL_COMPASS_LAYERS_VERIFIED_OR_EXPLICITLY_UNAVAILABLE: YES/NO
CHAT_AND_SITE_SHARED_SOURCE_SEMANTICS: YES/NO
OWN_HORIZON_LABELED_ANALYSIS_AND_PROTECTION_COVERED: YES/NO
CURRENT_AUTHORITY_RESOLVED: YES/NO
CURRENT_DATA_ROUTE_USED: YES/NO
ON_DEMAND_FRESHNESS_EVALUATED: YES/NO
NO_STALE_DATA_PING_PROMOTED: YES/NO
THREE_HORIZONS_PRESENT: YES/NO
REQUESTED_STRATEGIC_HORIZON_RESOLVED_OR_FAILED_CLOSED: YES/NO
CONTROLLED_ACTIONS_USED: YES/NO
ETA_PRESENT_WHERE_ACTIONABLE: YES/NO
WARNING_SEPARATE_FROM_ACTION: YES/NO
STALE_OR_CONFLICTING_DATA_FAILS_CLOSED: YES/NO
NO_DUPLICATE_ROTATION_SECTIONS: YES/NO
VISIBLE_OUTPUT_TEXT_ONLY: YES/NO
TWO_REQUIRED_COMPACT_MARKDOWN_TABLES_PRESENT: YES/NO
TACTICAL_INTERPRETATION_SEPARATE_FROM_ACTION_AUTHORITY: YES/NO
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

## 5.2 Owner-approved decision-support overlay · Kompas PRO (2026-10-25)

Owner authorization in Investering: merge the best of the already-approved
mobile Kompas layout (#1810) and Kompas PRO as the **permanent complete
human-readable Kompas format**. This is a PRESENTATION AND RECOMMENDATION
extension only; none of Sections 3, 4, 5.1, 6, 7, the production source
contracts or their buy/sell authority are overridden. The two compact
action tables and no third-party widgets remain mandatory.

A normal `Kompas` now must prioritize answers to five human questions:

1. **What do I do now?** Lead with the actual fresh OFFICIAL action, then
   a separately labeled **MY RECOMMENDATION** in clear, usable language:
   e.g. hold core exposure, do not add speculative beta, prepare a
   position-by-position protection/trim plan, or wait for a specific
   source-confirmation. Recommendation is an independent opinion based
   on disclosed evidence, not a new official trade state, automatic SELL,
   or portfolio order. Do not present static site checklist text as new
   real-time AI inference. Avoid ambiguous `HOLD` alone.
2. **How severe is pullback risk, and how confident are we?** Use the
   existing source-owned ordinal 5-stage classification
   NORMAL/BUILDING/ELEVATED/HIGH/CONFIRMED; a `3/5` ordinal location
   describes the **third category**, not a 60% probability, expected
   decline of 3/5, or calibrated confidence. Show qualitative
   **evidence quality** separately. The occurrence probability is
   `NOT CALIBRATED` until independently prospectively measured.
3. **How soon and how deep?** Show typed, prospectively bound pullback
   onset/start-window only when actually available and eligible. Show
   next official reassessment window separately, never as event ETA.
   Expected drawdown percent and depth class remain
   `NOT QUANTIFIED` until a governed typed frozen forecast exists.
   Explicitly say when a former week's scenario ETA has expired.
4. **At what BTC/ETH prices could this unfold?** Print real source-frozen
   ranges for their EXACT forecast horizons and asset pairs. Give source
   issuer/week and label base/bull/bear conditional envelopes only when
   their own frozen evidence exists; otherwise `NOT ISSUED`.
   NEVER stretch weekly W43 bands into upcoming W44 or a new 1–3d/2–3w
   forecast; do not invent expected closing price, drawdown, confidence,
   calibration or date from qualitative `MIXED`.
5. **What about SELL, protection and re-entry?** Always display the
   separate official SELL/TRIM state with its owner status, distribution,
   re-entry, confirmation/invalidation criteria and supported timing.
   If the SELL decision owner is absent, explicitly say
   `SELL UNAVAILABLE: NO GOVERNED SIGNAL`; do not suppress the question
   or silently infer a reduction from pullback HIGH/CONFIRMED. Offer a
   nonbinding, concrete risk-preparation plan and the evidence that
   would justify reconsidering it. Actual portfolio execution remains
   exclusively the user's decision.

**End with `YOUR ACTION NOW` and the `🧠 MIN FORTOLKNING` section**,
explicit about 1–3d and 5–7d disagreement, uncertainty, what changes the
view and next meaningful review. The user's investment choice remains
their own; do not imply predictive certainty or know portfolio-specific
taxes, liquidity and cost basis without authorized source evidence.

Production requirements and science remain under existing #1516 and
#1578, site overlay under `SITE_CONTRACT.md`. The source-only
`compass-pro-readback.mjs` may produce pre-authored planning text, but
**never** an official market classifier, SELL rule or trading signal.
