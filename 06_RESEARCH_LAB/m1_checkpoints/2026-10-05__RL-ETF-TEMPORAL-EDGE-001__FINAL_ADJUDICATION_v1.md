# M1 Final Research Lab Adjudication v1

**Mission:** `RL-ETF-TEMPORAL-EDGE-001`  
**Date:** 2026-10-05  
**Adjudicator:** ChatGPT 5.6 Sol High  
**Status:** FINAL_RESEARCH_ADJUDICATION  
**Authority:** RESEARCH_ONLY / NO_CANONICAL_EFFECT  
**Framework head read at adjudication:** `d66cb9c56aaf703115252f5d855bd4710eac2f0a`

## Final verdict

### Strong claim
> ETF flow persistence is one of the framework's strongest documented decision edges.

**Verdict: REJECTED.**

The current point-in-time evidence does not support that ranking.

### Narrow hypothesis
> Persistent BTC ETF outflows can contain defensive urgency information.

**Verdict: WEAKENED / NOT KILLED.**

The narrow hypothesis remains plausible but is not prospectively confirmed.

### Current research-role recommendation

**DEMOTE_TO_SHADOW_CONTEXT pending clean prospective restoration.**

This is a Research Lab recommendation only. It does not itself alter a canonical sensor role, threshold, market state, portfolio rule or public product.

## Why the strong claim fails

1. The corrected PIT replay has only 23 admissible BTC sessions in the observed 49-session calendar window.
2. A1 is evaluable at 19/45 endpoints and A2 at 21/47 endpoints.
3. There is one independent A2 onset and one later independent A1 onset. Persistence endpoints are not independent observations.
4. Both onsets were followed by positive BTC endpoint returns at approximately 24h, 72h and 7d.
5. The A1 onset on 2026-09-16 was followed by approximately +12.65% BTC over 7d with only approximately -1.27% maximum adverse excursion from the available anchor.
6. No current prospective registry evidence supplies matured positive confirmation for the relevant ETF pairs.
7. The stronger historical evidence base contains material knowledge-time, source-vintage and finality defects.
8. No comparable point-in-time utility ranking versus other framework sensors exists.

## What survives

- The September PIT reconstruction itself survives in the supplied deterministic artifact:
  - A2 first legally evaluable at 2026-09-11T11:12:13Z from -46.6, -120.2, -282.7m.
  - A1 first legally evaluable at 2026-09-16T11:25:33Z from -120.2, -282.7, -13.2, +159.9, -450.4m = -706.6m.
- The two signals did not flip after first evaluation in the supplied replay.
- A narrow defensive-context hypothesis is therefore not falsified merely by temporal repair.
- Existing zero direct action authority provided useful containment: the official Sep16 Compass action function did not directly consume ETF flow, so no direct ETF-caused action divergence is demonstrated for that episode.

## What is not established

- No reliable false-positive rate.
- No reliable false-negative rate.
- No economically attributable opportunity cost caused by ETF.
- No outflow-versus-inflow asymmetry.
- No incremental value versus price, breadth and rotation.
- No robust warning-lead advantage.
- No cross-regime transport.
- No evidence that `URGENCY_ONLY` deserves promotion or even retention as a decision edge.

## Separate implementation/provenance finding

Current live settled ETF normalization and the ratified PIT knowledge-time rule are not semantically identical.

Current `scripts/data_ping/auto_market_state.py` accepts rows with:
- `session_final=true`;
- `total_parity=true`;
- numeric reported totals;

without requiring zero non-structural unknown fund cells.

The #1211-style PIT rule is stricter.

This is a real semantic divergence and should be treated as an implementation/provenance remediation item, not as evidence for or against economic ETF edge.

## GPT-6.1 Sol evidence

Pass 1:
- verdict `INSUFFICIENT_EVIDENCE`
- cost approximately $0.1864
- correctly refused to infer economic edge from temporal defects alone.

Pass 2, after deterministic PIT replay + outcome crosswalk:
- verdict `WEAKENED`
- cost approximately $0.2123
- found no positive bearish endpoint confirmation in the two independent onsets.
- preserved the narrow hypothesis as unproven rather than globally rejected.

Pass 3:
- failed closed on an HTTP read timeout before a durable paid-call receipt.
- contributes no analytical evidence and is not retried because pass 2 already supplied the material adjudication.

## Claude status

The M1 full-folder Claude audit remains a non-blocking external challenge.

It may reopen M1 only if it produces a material, source-backed contradiction to a premise used above, for example:
- a reproduced replay error that changes the September A1/A2 onsets;
- a missing point-in-time outcome or action pathway that materially changes decision divergence;
- a provenance defect invalidating the deterministic replay inputs.

Absence of a Claude reply does not keep M1 open indefinitely.

## Restoration burden for a stronger ETF claim

Any future attempt to restore a stronger role must use:
- strict point-in-time admissibility;
- exact consecutive-session windows;
- revision-aware as-of joins;
- non-overlapping/appropriately dependent outcome treatment;
- frozen success/failure definitions;
- matched baseline with contemporaneous price/breadth/rotation;
- both positive and negative ETF regimes;
- regime-diverse prospective evidence;
- prespecified uncertainty/power logic rather than a post-hoc numerical sample target.

## Queue decision

M1 is closed as **FINAL_RESEARCH_ADJUDICATION**.

M2 `RL-OFFENSIVE-FNP-002` is released.

No canonical ETF role, threshold, market state, model weight or portfolio action is changed by this adjudication.
