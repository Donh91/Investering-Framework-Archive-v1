# Minimum-sufficient delegation benchmark pilot

**Date:** 2026-10-15  
**Status:** SHADOW_ONLY / IMPLEMENTATION_CANDIDATE / REAL_BENCHMARK_NOT_RUN  
**Primary folder:** `07_PROMPTS_AND_AGENTS/astra/`  
**Depends on:** `ASTRA_LANDING_ZONE_POLICY_v1.json`, `ASTRA_SKILLS_AND_AGENTS_AUDIT_MISSION_v1.md`

This is an offline receipt comparator under the existing Astra agent-utility owner. It does not dispatch agents, call APIs, change routing or add a scheduler. Keep the one-agent default until independently verified marginal benefit justifies delegation.

## Execution

```bash
python scripts/astra/agent_delegation_benchmark_v1.py --input <case.json> --receipt-root <read-only-checkout>
python -m unittest discover -s tests/astra -v
```

The original package's 21 tests passed before modification. Independent advisory review reproduced invented zero costs and invented outcomes becoming eligible with unchanged demo receipts. The integrated implementation therefore separates byte-consistent metadata from empirical eligibility. `byte_consistent_pair_count` reports byte checks only; `paired_eligible_count` remains zero and `eligible` remains false. All delta fields are provisional, self-reported metadata. Hashes and different identity labels cannot establish real execution, truthful billing, shared rubric, prompt equivalence or reviewer independence. Those require the existing owner to inspect actual execution/accounting/review evidence; this script cannot grant that authority. Missing measurements remain null, not free.

The comparator requires a **single, frozen, byte-verified scoring rubric** (`rubric_path` and `rubric_sha256`) per comparison case, in addition to the frozen question and evidence bundle. Both arms must be assessed against that same registered rubric; equal numeric check totals alone do not establish comparable checks. The comparator rejects unknown fields, missing/changed files, path escape, source/receipt aliasing, cross-case receipt laundering, cross-arm verifier conflicts, zero or unequal check denominators, self-labelled same-identity reviews, unbounded swarms and duplicate assignments. Synthetic examples are test fixtures, never empirical outcomes. A rubric hash still cannot prove the reviewer genuinely applied that rubric; external independent evaluation is mandatory for any empirical claim.

## One real pair, after integration gates

Freeze a public non-market Skills & Agents audit slice, exact source commit, evidence and rubric digests, same task and evidence entitlement for both arms, a stop time and cost ceiling before execution. Arm A uses one qualified GPT-6 executor. Arm B uses 2-3 disjoint specialist responsibilities with the same qualified model where possible. Include parent synthesis, verification, failures and retries in all-in accounting. Independently evaluate both against the same rubric; record quality, false findings, missed findings and marginal verified evidence separately. Unknown Work-credit conversion or model identity must remain UNKNOWN.

The supplied handoff requires PR checks, eligible independent review, merge and exact-main readback before this real pair. Until those gates pass, no real-pair completion or efficiency gain is claimed. The active Task 2 R1/CFGI slot is protected and must not be displaced for this experiment. One pair demonstrates feasibility only, never causal or general efficiency gain. Existing landing-zone activation, utility/pruning and qualification gates remain unchanged.
