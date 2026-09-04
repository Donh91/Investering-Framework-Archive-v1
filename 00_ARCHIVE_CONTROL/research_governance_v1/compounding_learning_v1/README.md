# Compounding Learning Controller v1 — Future Agent Entry Point

**Status:** ACTIVE_RESEARCH_ONLY_NON_CANONICAL  
**Role:** post-adjudication learning strategy, never scientific adjudication or market authority.

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
-> Compounding Learning states what was learned, what remains uncertain and what to test next
-> existing Research Governance Stack challenges and ranks the pre-VOI proposal
-> normal Scientific Admission decides whether a new forward child test is allowed
```

## Descriptive checkpoint schedule

The controller supports the bounded operational sequence:

```text
7 / 14 / 30 / 60 / 90 / 120 / 180 / 240 days
```

Profiles expose only the checkpoints relevant to their intended horizon. `LONG` and `CONFIRMATORY` expose the complete schedule. FAST and STANDARD stop earlier. Checkpoints are one-shot learning events and never scientific verdicts by themselves.

Matured-outcome checkpoints remain event-driven where the experiment contract supports them.

## Machine-readable learning contract

Each emitted learning packet is designed to answer:

- `what_we_learned`, copied from the current Unified Adjudication owner action/reason plus an explicit claim limit;
- `uncertainty`, grounded in the frozen Scientific Admission problem, incremental-value claim, regime dependency and complexity tax;
- `falsifier`, copied from the frozen admission failure criteria;
- `what_would_change_view`, split into more-support, less-support and kill/retire criteria;
- `why_information_rich`, explaining why the proposed test discriminates the frozen claim from its baseline and controls;
- frozen baseline and negative controls;
- exact admission-plan source and digest when resolvable.

If the frozen admission detail cannot be resolved, the controller emits empty criteria and an explicit unavailable state. It must never invent a falsifier, baseline or control.

`NEXT_BEST_EXPERIMENT.json` is deliberately a **pre-VOI candidate**, not a final scientific or resource-priority verdict. It must still pass the existing novelty, Decision Impact / VOI, adversarial sentinel, meta-orchestrator and Scientific Admission path.

## Invariants

- Unified Experimental Lifecycle Adjudication remains the scientific interpretation owner.
- The Compounding Learning Controller does not independently reclassify evidence.
- The frozen parent experiment is immutable.
- No retrospective re-score or hindsight threshold search.
- Historical requalifications do not inherit old calendar age as prospective learning time.
- A checkpoint is not a scientific verdict.
- A supportive or failed parent may only generate a **new child proposal**.
- The child must pass novelty, VOI, adversarial review, meta-orchestration and scientific admission before prospective execution.
- Negative evidence is queued before supportive replication as a learning-efficiency rule, not as a market or scientific score.
- No automatic canonical write, threshold change, weight change, market-rule change, portfolio action or promotion.
- Missing or stale Unified Adjudication fails closed to `CONTINUE_OBSERVING`.

## Confirmatory firewall

For `FORECAST_SKILL_CONFIRMATORY_V1_3_1` plus its binding v1.3.2 erratum, controller checkpoints at 7/14/30/60/90/120/180/240 days are operational only:

```text
ACCRUAL_HEALTH
DATA_QUALITY
CONCENTRATION
MATURITY_READINESS
```

They cannot infer interim forecast skill, mutate the method, or create an automatic child test from interim performance. Day 240 means final-evaluation readiness only until the preregistered confirmatory owner runs. The final preregistered confirmatory test owns the verdict. `FORECAST SKILL = UNPROVEN` until legitimate future evidence says otherwise.

## Future Astra / stronger-model audit contract

A future stronger agent should audit this controller for better falsification, event scheduling, information value, regime handling, redundancy control, evidence compression and learning efficiency.

It may propose improvements as a **versioned new methodology**. It must not improve apparent historical performance by rewriting parent hypotheses, outcomes, timestamps, scientific gates or sealed confirmatory rules.

The target is compounding learning quality, not compounding self-confidence.
