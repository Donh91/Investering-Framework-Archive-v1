# JEV Decision Gate v1 — 2026-09-20

Status: **NARROW / KEEP IN SHADOW**
Authority: research-only. No trading, portfolio, canonical-state, threshold, merge, or autonomous promotion authority.

## Decision

Jev 1.13.0 has earned a bounded place as a cheap semantic challenger / triage layer inside the existing Alpha Lab evidence chain. It has **not** earned general framework routing authority, trading authority, or a claim of alpha.

This is intentionally narrower than a generic "JEV works" conclusion.

## What is proven

- Live TypeSafe connectivity and typed interface work end-to-end.
- Pinned model: `jev-1.13.0`; SDK: `typesafe-sdk==0.7.0`.
- Immutable observation hashing, outcome-leakage rejection, point-in-time checks, UNKNOWN preservation, no-DROP route set, and authority=false guards are enforced in code.
- Malformed/non-finite Noul values fail closed.
- Deterministic stress suite includes T-12 shape canary, T-39 no-model baseline, T-06/T-07/T-08 adversarial safety envelope, T-35 fail-closed checks.
- Bounded live matched run: 30 calls, 5 repeats over clean + 3 hostile states + 2 representation variants.
- Live result: zero route flips, zero injection downgrades, zero representation route disagreements.
- Clean and every challenger state routed DEEP_DIVE.
- Matched live median latency: 155.45 ms; range 91.5–317.8 ms.
- Matched run input tokens: 37,485 total. At the documented $42/B input-token price used by this experiment, estimated Jev model input cost is about $0.00157 for the 30 calls. This is an experiment estimate, not an end-to-end framework cost claim.

## Important falsification finding

Representation order changed judgment magnitudes even though it did not change the route in this run.

Mean clean vs reordered:
- evidence_conflict: 0.544 -> 0.638
- frontier_review_need: 0.478 -> 0.536
- material_evidence: 0.734 -> 0.786
- deep_dive_value: 0.626 -> 0.634
- preserve_verbatim: 0.818 -> 0.818

Therefore:
1. Do not treat Jev probabilities as calibrated truth.
2. Do not promote thresholds from this synthetic run.
3. Canonical deterministic state ordering is required before any production-like use.
4. Borderline threshold behavior remains UNPROVEN.

Hostile evidence did not suppress escalation. In this synthetic packet it generally increased material/conflict/deep-dive judgments. That is safer than a downgrade for the tested route, but it can create a false-positive / cost-amplification attack. Injection resistance is therefore **partially supported, not proven**.

## What is not proven

- Incremental utility over deterministic rules on real Alpha Lab observations.
- Alpha, precision, recall, sellability, realized return, or missed-winner improvement.
- Calibration of any Noul probability or Score.
- Threshold safety near decision boundaries.
- General robustness to arbitrary prompt injection / source spoofing.
- Full-state vs compact-state superiority.
- Net savings after downstream Sol/Codex/Work/Astra calls.
- Prospective held-out outcome advantage.

The repository currently exposes the contracts and synthetic fixtures needed for replay, but no sufficient real `OUTCOME_MATURED` cohort was found in the public control plane or restricted repository search used for this gate. Real-cohort superiority must therefore remain NOT_RUN rather than fabricated.

## Role allowed by this gate

Allowed, shadow-only:
- semantic evidence triage;
- deep-dive-value challenger;
- preserve-verbatim challenger;
- conflict/materiality feature generation;
- FULL vs COMPACT state experiments;
- research escalation experiments;
- model/context routing experiments where deterministic code retains authority.

Not allowed:
- DROP of evidence;
- direct BUY/SELL/sizing;
- identity/provenance truth determination;
- arithmetic/date/exact lookup authority;
- autonomous threshold changes;
- autonomous promotion;
- replacing deterministic invariants;
- declaring Alpha Lab success.

## Contract recommendation

Do not expand the six-question contract. Treat it as an experimental battery.

Likely candidates for a future smaller contract are `deep_dive_value` and `preserve_verbatim`, with `evidence_conflict` retained only as a challenger beside deterministic conflict checks. `information_density` must not route from its scalar alone. `frontier_review_need` is downstream/circular and should remain experimental until it demonstrates incremental utility.

## Promotion / kill gate

Promotion beyond shadow requires prospective or held-out real observations where Jev beats the frozen deterministic/current-policy baseline on a preregistered primary endpoint while preserving critical-evidence recall and all authority/provenance/data-integrity floors.

Kill or redesign the role if:
- deterministic baseline matches Jev within the preregistered margin;
- false-negative critical evidence loss appears;
- representation sensitivity causes route flips near operational thresholds;
- injection causes route downgrade or unacceptable escalation-cost amplification;
- end-to-end cost per successful task is not better;
- held-out/prospective evidence fails to reproduce retrospective gains.

## Final v1 verdict

**KEEP, NARROW, SHADOW-ONLY.**

Jev is technically viable and cheap enough to continue using as an experimental semantic decision fabric. The evidence does not justify general routing authority or an Alpha Lab edge claim. Framework development does not need to wait for more Jev testing: integrate only the bounded shadow role and let prospective Alpha Lab evidence decide whether it deserves promotion later.
