# DATA PING TOP-UP AND BUY-WINDOW OUTPUT RULE v1.0

**Status:** CANONICAL OPERATIONAL OUTPUT RULE  
**Effective:** 2026-07-30  
**Scope:** Every user-facing main-framework DATA PING reconciliation, regardless of whether the run is accepted as a canonical successor, retained as a bounded observation, or classified as partial.

## Purpose

Every DATA PING may contain extensive market, source-QA and governance analysis. The user-facing response must therefore end with one short, adaptive and unambiguous sentence that translates the current evidence into a practical decision about topping up existing altcoin holdings.

This sentence is an operational translation of the analysis. It does not replace the full analysis and does not independently alter canonical framework state.

## Mandatory terminal format

The final market-action line must be the last substantive sentence in the DATA PING response and must begin exactly with:

```text
Top-up og købsvindue:
```

Preferred rendered form:

```text
**Top-up og købsvindue:** [one adaptive, complete and unambiguous sentence]
```

## Required content

The sentence must contain all three elements:

1. **Action now** — choose one clear action.
2. **Time horizon or trigger** — state when the decision should be revisited.
3. **Reason** — name the one or two decisive market conditions.

The line must answer the practical question:

> Should the user top up existing high-conviction altcoin holdings now, buy only a small tranche, or wait for a potentially better entry window?

## Permitted action classes

Use natural Danish wording, but the conclusion must map to exactly one of these classes:

### 1. ACTIVE_GRADUAL

Use when broad and relative altcoin strength is sufficiently confirmed.

Example:

```text
**Top-up og købsvindue:** Top gradvist op nu i de stærkeste eksisterende beholdninger, fordi altcoin-breadth og ETH/BTC begge viser vedvarende styrke; behold dog en restreserve til udsving.
```

### 2. SMALL_TRANCHE_ONLY

Use when evidence is improving but confirmation is incomplete.

Example:

```text
**Top-up og købsvindue:** Køb højst en lille første tranche nu og behold hovedparten i reserve, indtil styrken enten bekræftes eller et lavere købsvindue opstår inden for de næste 2–4 dage.
```

### 3. WAIT_FOR_BETTER_WINDOW

Use when weakness, failed persistence or conflicting signals make a lower price plausible.

Example:

```text
**Top-up og købsvindue:** Afvent cirka 2–4 dage med hovedparten af købene, fordi altcoin-styrken endnu ikke er bekræftet, og der fortsat er god mulighed for lavere priser.
```

### 4. DO_NOT_ADD_RISK

Use when risk is clearly elevated or downside transmission is active.

Example:

```text
**Top-up og købsvindue:** Undlad nye top-ups nu og afvent en ny settled bekræftelse, fordi breadth, ETH/BTC og prisstrukturen samtidig peger på forhøjet risiko for yderligere altcoin-svaghed.
```

### 5. NO_NEW_ASSESSMENT

Use only when the incoming packet contains no valid new market evidence, is a pure duplicate, or cannot support an updated timing conclusion.

Example:

```text
**Top-up og købsvindue:** Ingen ny købsvurdering kan udledes af denne kørsel; den seneste gyldige anbefaling fastholdes, indtil et nyt brugbart markedssnapshot foreligger.
```

## Decision inputs

The sentence must be derived from the full framework read, with emphasis on:

- direct ETH/BTC owner data and persistence around relevant thresholds;
- filtered altcoin breadth and whether strength persists or relapses;
- BTC dominance and ETH versus BTC relative leadership;
- absolute price structure and expected near-term path;
- derivatives, taker flow, funding and open-interest risk;
- ETF and liquidity evidence when current and usable;
- event risk and data-quality limitations.

No single sensor should mechanically determine the sentence unless a canonical hard gate explicitly requires it.

## Clarity rules

- Use exactly one sentence after the prefix.
- State a definite action: buy gradually, buy only a small tranche, wait, or do not add risk.
- Include a concrete horizon such as `1–2 days`, `2–4 days`, `3–5 days`, or a measurable trigger when appropriate.
- Do not use vague wording such as `måske`, `eventuelt`, `kan overvejes`, or `det kommer an på` without resolving it into one action.
- Do not include a confidence score unless it materially improves the decision.
- Do not repeat the complete framework analysis in the terminal line.
- Do not infer that an asset is attractive merely because it trades below the user's original entry price.
- Keep the sentence adaptive; do not force a fixed 2–4 day horizon when another horizon or trigger is better supported.

## Authority boundary

The line is user-facing operational guidance, not an automatic trade instruction and not an independent state transition.

It may not override:

- `rotation`;
- `rebuy`;
- `new_entry`;
- `large_caps`;
- portfolio locks;
- source-QA or predecessor-lineage restrictions.

When canonical state remains locked, the sentence must remain consistent with that lock. A small-tranche formulation is permitted only when the main framework explicitly supports it as a bounded operational choice rather than a canonical unlock.

## Auditability

Archive the exact published sentence with the DATA PING framework read whenever practical. Later evaluation may score whether the recommended timing, action class and stated reason were useful.

The sentence must remain frozen after publication. Corrections must be appended as a new dated assessment rather than silently rewriting the original line.
