# Compounding Learning Controller v1 — Future Agent Entry Point

**Status:** ACTIVE_RESEARCH_ONLY_NON_CANONICAL  
**Role:** post-adjudication learning strategy; never scientific adjudication or market authority.

## Mandatory read order for work touching experiment learning, calibration or automatic improvement

1. `research/api_agent/API_AGENT_AND_COMPOUNDING_LEARNING_ARCHITECTURE_v1.md`
2. `00_FMOS/EXPERIMENT_LIFECYCLE_AND_EXECUTION_PLANE_v1.md`
3. `00_FMOS/EXPERIMENT_SCIENTIFIC_ADMISSION_AND_UNIFIED_ADJUDICATION_v1.md`
4. `research/experiment_lifecycle/weekly_adjudication/LATEST.json`
5. `00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1/POLICY.json`
6. `00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1/STATE.json`
7. `00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1/NEXT_BEST_EXPERIMENT.json`
8. `scripts/research/compounding_learning_controller.py`

## One-line architecture

```text
Mature prospective evidence
-> Unified Adjudication decides what the evidence means
-> Compounding Learning decides what to learn/test next
-> existing Research Governance Stack challenges the proposal
-> normal Scientific Admission decides whether a new forward child test is allowed
```

## Invariants

- The frozen parent experiment is immutable.
- No retrospective re-score or hindsight threshold search.
- Historical requalifications do not inherit old calendar age as prospective learning time.
- A checkpoint is not a scientific verdict.
- A supportive or failed parent may only generate a **new child proposal**.
- The child must pass novelty, VOI, adversarial review, meta-orchestration and scientific admission before prospective execution.
- No automatic canonical write, threshold change, weight change, market-rule change, portfolio action or promotion.
- Missing or stale Unified Adjudication fails closed to `CONTINUE_OBSERVING`.

## Confirmatory firewall

For `FORECAST_SKILL_CONFIRMATORY_V1_3_1` plus its binding v1.3.2 erratum, controller checkpoints at 30/60/90/120/180 days are operational only:

```text
ACCRUAL_HEALTH
DATA_QUALITY
CONCENTRATION
MATURITY_READINESS
```

They cannot infer interim forecast skill, mutate the method, or create an automatic child test from interim performance. The final preregistered confirmatory test owns the verdict. `FORECAST SKILL = UNPROVEN` until legitimate future evidence says otherwise.

## Future Astra / stronger-model audit contract

A future stronger agent should audit this controller for better falsification, event scheduling, information value, regime handling, redundancy control, evidence compression and learning efficiency.

It may propose improvements as a **versioned new methodology**. It must not improve apparent historical performance by rewriting parent hypotheses, outcomes, timestamps, scientific gates or sealed confirmatory rules.

The target is compounding learning quality, not compounding self-confidence.
