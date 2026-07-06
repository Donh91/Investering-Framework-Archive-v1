# Custom GPT Truth Layer + Grok Shadow v10.26

**Date:** 2026-07-06  
**Status:** CANONICAL  
**Domain:** DATA PING source governance / shadow protocol  
**Primary folder:** `02_DATA_PING/protocols/`

---

## Canonical decision

From now on:

```text
Custom GPT = DATA PING truth-layer.
Grok = standalone shadow sensor.
```

This role split is canonical for future DATA PING processing.

---

## Custom GPT role

Custom GPT is the preferred source for verified DATA PING values:

```text
- BTC / ETH price ledger
- BTC dominance
- ETH/BTC
- close-ledger
- CFGI public scrape or API values
- ETF-flow ledger when verified
- stablecoin / TVL official values
- weekly range verification
- source QA
- missing-data marking
```

Custom GPT should prioritize:

```text
exact values
source traceability
no estimation
clear missing-data labels
DATA_ONLY sensor discipline
```

CFGI belongs to Custom GPT.

---

## Grok role

Grok is now:

```text
GROK_STANDALONE_SHADOW
```

Grok may run alone in a fresh thread every time, but its output is shadow-only.

Grok’s useful role is to add:

```text
- fakeout risk
- absorption quality
- deployment quality
- post-flush read
- regime tension
- rotation sanity check
- missing confirmation flags
- narrative disagreement
```

---

## Grok v10.26 accepted status

Accepted automated prompt:

```text
DATA PING v10.26 — GROK SHADOW MINI / NO CFGI
```

Status:

```text
ACCEPTED_FOR_OPERATIONAL_USE
SHADOW_ONLY
```

Operational notes:

```text
Grok runs standalone.
Grok has no memory.
Grok must not use CFGI.
Grok uses Alternative.me only for sentiment.
Grok must include SOURCES_USED.
SHADOW_VALUE_ADD is the primary value-add section.
```

---

## CFGI governance

Canonical rule:

```text
CFGI = Custom GPT truth-layer.
Grok = no CFGI.
```

Grok must not scrape, estimate, interpret or output CFGI.

Alternative.me may remain in Grok as broad sentiment backdrop only.

---

## Merge rule

Future DATA PING processing should read inputs as follows:

```text
1. Custom GPT verified values are the primary data layer.
2. Grok v10.26 is the shadow layer.
3. If Grok conflicts with Custom GPT, Custom GPT wins.
4. If Grok highlights fakeout risk, absorption weakness, deployment weakness or missing confirmations, include it as shadow caution.
5. No official framework state may be based on Grok alone.
```

---

## Canonical summary

```text
Going forward, register Custom GPT as the DATA PING truth-layer and Grok v10.26 as the standalone shadow sensor. Custom GPT owns CFGI and verified DATA PING values. Grok must not use CFGI and should instead provide shadow-only context through fakeout risk, absorption quality, deployment quality, post-flush read, regime tension, rotation sanity and missing confirmation flags. Grok v10.26 is accepted operationally in its current form because it is correctly scoped as shadow-only and adds value through SHADOW_VALUE_ADD rather than truth-layer claims.
```
