# Mandatory independent Grok review — Framework Strategist v1

This is a **release gate**, not a request for Grok to merge or approve GitHub in a human's name. If the Grok bridge is unverified or not operating, the PR remains OPEN. Reviewer must be genuinely independent of authoring identity and inspect the **EXACT current PR head**.

## Required inputs
1. Current GitHub main and AGENTS.md, permanent source-recovery policy and subsystem sunset contract.
2. Full PR diff at exact head SHA; do not review an earlier author ZIP as final.
3. `00_FMOS/framework_strategist/README.md`, `STRATEGIC_INTENT_v1.json`, strategist script and its entire test suite.
4. Existing Framework Learning Supervisor, Compounding Learning, Experiment Lifecycle, FMOS knowledge graph, #1156 / #1157, latest learning/source products.
5. Existing workflow diff: no additional cron, duplicated queue, privilege escalation, credential exposure, money spend or automatic integration.

## Adversarial review missions
- **Truth/causality:** Can stale/future/negative/ambiguous or duplicated source events be interpreted as credible improvement? Can unsupported hypothesis statuses become proven alpha? Is a single week's change presented as a multiweek trend? Is 'no candidate' confused with 'no risk'?
- **Read provenance:** Source path allowlist; branch-safe path handling; source bytes hashed; generated_at UTC; main readback; can't trust mutable model text or rewrite original inputs. Invalid/absent optional sources must fail closed without writer crash.
- **Idempotence:** Re-running identical source hashes gives identical observation IDs; no duplicated Grok candidate or queue item. Prior output cannot act as original evidence; timestamps do not turn one event into many.
- **Security and prompt injection:** No external text can request execution/merges/payments/repo file reads; no secrets from other repositories; hardcoded owner routing stays bounded; no direct Grok dispatch until authenticated provider/budget gate.
- **Operations:** Existing schedule ONLY, valid PR CI negative tests, exactly one git commit/readback and no destructive GitHub actions; failure isolates to advisory, doesn't suppress original existing producer truth.
- **Science:** independent source roots; false winners; regression vs actual outcome; negative evidence retained and nonpromotion.
- **Efficiency:** max 3 actionable proposals; bounded input memory/time; no status chatter or duplicate recommendations; meaningful mission drift requires proof.

## Deliverable format
Return a JSON review including:
- `exact_head_sha`; `files_reviewed`; `risk_tier`;
- `findings[]` each with `id,severity,path,lines,concrete_reproduction,impact,patch,regression_test`;
- `missing_tests[]`, `architecture_overlap`, `cost_and_security`, `ready_for_owner_release`.
Return an MD human executive summary as well. Findings with code changes must be reproduced on current PR and retested; repeat review whenever head changes. **Do not automatically trust "PASS" from same identity, and do not infer platform APPROVED.**

## Postmerge acceptance
Exact merge SHA, expected files/hashes on main, natural production run attributable to updated code, actual `research/framework_learning/strategist/LATEST.json` readback, owner handoff consumed, no false scientific promotion, no unapproved Grok spend, zero new schedules.
