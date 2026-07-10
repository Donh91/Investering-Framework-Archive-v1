# FRLP v0.1 — First Post Launch Checklist

**Activated:** 2026-07-10  
**Use from:** First resumed Cycle Navigator post under FRLP / CN #15  
**Last public post before FRLP:** CN #14  
**Status:** CANONICAL OPERATING CHECKLIST

---

## Internal pre-publication checklist

```text
[ ] B1-B9 governance bindings confirmed
[ ] Settled UTC candles fetched
[ ] Source / anchor checks passed
[ ] Wilder ATR14 calculated from at least 60 settled daily candles
[ ] DUMB_1.5 calculated and frozen
[ ] DUMB_2.0 calculated and frozen
[ ] PREVWK calculated and frozen
[ ] Official range declared
[ ] Official width is not narrower than DUMB_1.5
[ ] Human adjustment is <=0.5xATR14
[ ] Human adjustment rationale written before publication
[ ] Phase label logged
[ ] Structure label logged
[ ] TRIAD state logged
[ ] Confidence NORMAL or LOW logged
[ ] LOW reason written where applicable
[ ] Shadow state logged
[ ] Official re-anchor flag remains FALSE
[ ] Two or three invalidators written
```

## Publication freeze

```text
[ ] X post published
[ ] publication_ts captured
[ ] publication_url captured
[ ] Frozen Group F ledger row completed
[ ] Raw post archived in GitHub
[ ] Ledger row committed to GitHub
[ ] X timestamp + commit hash form double freeze proof
```

## Public layout guardrails

```text
[ ] Familiar/lightweight CN identity preserved
[ ] Phase/Structure shown separately
[ ] Range shown separately
[ ] Prior range score versus baselines shown separately
[ ] Pullback Weather shown briefly
[ ] Rotation state uses staged language
[ ] Shadow observations clearly marked shadow-only
[ ] Invalidators included
[ ] No blended Overall Score
[ ] No unverified/self-reported actuals
[ ] No intra-week official range-update promise
```

## During the week

```text
[ ] Daily breach count updated internally
[ ] TRIAD / transition state observed
[ ] Shadow re-anchor row appended only if triggered
[ ] Official range never edited
[ ] Shadow range never described as official
```

## After week end

```text
[ ] FMP EOD-full actuals verified, or Kraken fallback used and marked
[ ] SOURCE_CONFLICT row created if source deviation >0.5%
[ ] Group S scored once
[ ] Winkler alpha=0.10 calculated
[ ] Winkler alpha=0.20 calculated
[ ] DUMB_1.5 / DUMB_2.0 / PREVWK calculated from frozen values
[ ] adjustment_alpha calculated with positive = human value-add
[ ] Jaccard / containment / breach / bias / width ratio calculated
[ ] Separate scorecard archived
[ ] K1-K8 monitor evaluated
```

---

## Public CN skeleton

```text
CYCLE NAVIGATOR — #15

1. PHASE / STRUCTURE
[short familiar phase/structure summary]

2. RANGE FORECAST
BTC [L-H] · basis [BASELINE_1.5 / bounded adjustment] · confidence [NORMAL/LOW]

3. LAST WEEK RANGE SCORE
CN [W] | B1.5 [W] | B2.0 [W] | PREVWK [W]
Held [x/7] days · verified actual source [source]

4. PULLBACK WEATHER
TRIAD [state] · [one line]

5. ROTATION STATE
[staged status] · gates are repair markers, not confirmation

6. SHADOW OBSERVATIONS
[brief or none]

7. WHAT WOULD INVALIDATE THIS
[2-3 concrete falsifiers]
```

---

## Boundary

```text
Internal machinery may be complex.
Public output remains curated and familiar.
CN #15 is the first real FRLP forward row.
No market or portfolio authority is created by this checklist.
```
