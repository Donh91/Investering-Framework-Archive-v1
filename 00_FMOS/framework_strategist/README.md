# Framework Strategist v1 — strategic reasoning over existing owner evidence

**STATE: IMPLEMENTATION_CANDIDATE / NOT ACTIVE / BLOCKED ON INDEPENDENT GROK EXACT-HEAD REVIEW.**

**Owner:** existing Framework Learning Supervisor (no new supervisor/queue/cron/model router).
**Advisory client:** existing cross-repository Supervisor; optional existing Grok bridge only after bridge independently authenticated and source/budget gates passed.
**Authority:** proposal-only. ZERO permission to call paid APIs, run code, alter PRs, create tasks, change forecasts, promote scientific results, trade, change risk parameters, or bypass review/merge.

## North star — owner's purpose
Protect capital and evidence integrity before chasing a marginal final upside. Improve science-backed market cycle and tactical decisions, prospective Alpha Lab signal discrimination, measurable Task 2 falsification, Cycle Navigator usability, and operational reliability per krone. Preserve both missed winners and rugged/failed candidates. Distinguish investments/results from engineering throughput. Value improvement only when backed by original evidence and time-correct outcomes.

## Existing owners, no competing planes
- FMOS maintains provenance, time-correct retrieval and conflict graphs.
- Compounding Learning owns hypothesis family interpretation.
- Experiment Lifecycle + Unified Adjudication own experiments and scientifically admissible outcomes.
- Framework Learning Supervisor already owns cross-week memory, method-staleness, unconsumed-information and bounded delegation.
- #1156 owns remediation. #1157 owns independent adaptation scoring.
- Existing Task 2, Alpha Lab, Cycle Navigator, Pullback and Master Monday owners remain authoritative.
- Grok is an independent *question recipient/reviewer* only, never canonical truth and never automatic approval.

Strategist is one deterministic, side-effect-constrained stage in the EXISTING Framework Learning Supervisor workflow, not a second brain with autonomous decision rights. It reads only enumerated, integrity-hashed current-owner outputs. It emits a compact *read-only* briefing and up to three proposed investigations. This is NOT an agent running continuously. A future model may explain a validated briefing after owner routing, never free-roam raw repositories.

## Desired outcomes
1. Identify legitimate weakening/strengthening, contradiction and stale/missing source coverage early, without equating activity or hypotheses with evidence of alpha.
2. Connect problems across domains and retain "why" and prior decisions, without treating model summaries as independent observations.
3. Detect mission drift and unconsumed high-value data and route to the existing Supervisor or existing owner.
4. Generate up to three reproducible, bounded, grounded questions, including an optional Grok candidate only when the Grok bridge is authenticated, authorized and budget-governed.
5. Show UNKNOWN prominently when cross-repository proof or multiweek evidence is missing.

## Deployment
This PR includes a prepared integration into the **existing** `.github/workflows/framework-learning-supervisor.yml`. The PR MUST remain unmerged until exact-head independent Grok code + threat-model review is available, material findings remediated, full relevant CI PASS and explicit owner-governed release allowed. Never treat a PR comment, external model answer or self-review as GitHub APPROVED. No new automation is created.

## Scope and measurable complexity declaration
This is a material extension under `00_FMOS/SUBSYSTEM_SUNSET_CONTRACT_v1.md`.
- `expected_decision_impact`: at least one evidenced, nonduplicate strategic finding leads the existing Supervisor to reprioritize a review, retire a futile idea, or request a grounded investigation that its current queue would otherwise miss.
- `evaluation_horizon`: inspect the first 10 actionable findings OR first 4 normal Supervisor executions, whichever is later. This is a nonblocking **post-activation** effectiveness audit; there is no pre-launch 30-day shadow period.
- `kill_criterion`: if no incremental useful consumer action, or false positives lead to unsafe routing, disable this stage in the existing workflow and merge its documentation into the existing owner.
- `existing_owner_overlap`: high; identical owner and read-only view, only added longitudinal goal anchoring and cross-domain evidence-gap triage.
- `complexity_budget`: zero new schedules; zero new queue; zero new paid model calls; zero new credential; zero new write/merge authority; one script, one declarative intent contract, one test suite and one derived JSON product.

## Canonical references
`00_FMOS/FRAMEWORK_INTELLIGENCE_AND_LEARNING_LOOP_v1.md`, `00_FMOS/GRAPH_AND_RETRIEVAL.md`, `00_FMOS/WEEKLY_FORENSICS_META_HEALTH_v1.md`, `AGENTS.md`, `00_FMOS/OPERATIONAL_MEMORY_AND_RETRIEVAL_v1.md`.

## Operational contract
`scripts/framework_intelligence/framework_strategist_v1.py` -> `research/framework_learning/strategist/LATEST.json`.
Advisory-only and deterministic first. Source receipts include immutable hash and UTC age. A green workflow is never proof of investment alpha. Missing/partial/stale receipts force DEGRADED/UNKNOWN, never inferred health or positive progress. Do not publish the briefing as a new market indicator.
