# Task 2 · GPT-6.1 Sol bounded scientific review handoff (no API call started)

**Recorded:** 2026-10-14. **Status:** `PREPARED_NOT_QUEUED_NOT_RUNNING`. **Binding:** [machine packet](2026-10-14__TASK2_R0_R1_SOL61_ADVERSARIAL_READY_v1.json). **Canonical owners:** existing Task 2 R0–R7 handoff, R1/Task1.5 [#1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596), R0 [#1627](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1627), existing Research Lab Sol queue. This file is evidence for **one-at-a-time future bounded calls**, not a new controller, budget or a command to run now.

## Actual runtime/cost preflight

- Existing public `research/api_agent/research_lab_sol/RESEARCH_LAB_SOL_QUEUE_v1.json`: model `gpt-6.1-sol`, reasoning `high`, **max_active_missions=1**. At inspection, mission `RL-DISTRIBUTION-SURVIVAL-META-006` was `ACTIVE_RELEASED` and held the active slot.
- Existing API Gateway `research/api_agent/API_TASK_REGISTRY_v1.json`: **$3 per-call** and **$40 monthly** hard-stop. Actual monthly balance, remaining quota and individual account permission were not accessible in this chat. No API call or paid dispatch has been executed by this handoff.
- OpenAI official model docs: https://developers.openai.com/api/docs/models/gpt-6.1-sol — Standard short-context tokens $2/million input and $10/million output. A hypothetical 40k input + 12k output costs approximately **$0.20**, excluding tools, long-context, other billing effects; **NOT a charge or exact future run forecast**. Never increase the existing caps or bypass the cost meter.
- No direct approved GitHub workflow dispatch or authenticated gateway invocation was available from this chat. Do **not** signal `QUEUED`, `RUNNING`, `PASS` or `REVIEWED` until the existing owner records an actual dispatch/job/receipt after clearing its active slot.

## Sequenced missions, one at a time

| Stage | Model / bounded deliverable | Admission |
| --- | --- | --- |
| **1 · R0 independent code falsification** | GPT-6.1 Sol High, exact PR #1627 review: source SHA/type, base root tree, ancestry, path grammar, synthetic negative controls; locate untested vulnerabilities and produce reproducible fail fixtures | Start only after existing Sol slot is clear, refreshed source hashes and budget confirmed |
| **2 · R1/CFGI first-known scientific red-team** | GPT-6.1 Sol High: 11 native-v3 original issue→packet chains, nine 12h outcomes, two absent, 36 CFGI feature entries in nine outputs, 12 funding-time semantics errors and source reuse after ~115m | Same owner-controlled release, zero lookahead invention, source-first-known must be separately authenticated |
| **3 · AI vs simple rules tribunal** | GPT-6.1 Sol High: evaluate *already executed* same-clock, same-capital deterministic baseline results versus frozen original AI results on R1-admitted independent event families | **Blocked until real R1 admission**, original model/prompt receipts and after-cost decision logs |

Model's outputs are **advisory and adversarial**: Pass/Fail/Unknown with original primary source path, hash and falsifier. No attempt to backfill private 2025 CFGI publication times with Aug-2026 retrieved values, infer economic skill from overlapping nine forecast rows, validate own R0 code, score markets, place orders or write/merge source. The original Deep Research DR-A–DR-E package already covers broad literature/research; these Sol tasks must deliver a **new independent reproducible test or claim adjudication**, not duplicate the report.

## Work that does not need Sol

1. Deterministic source object verification and CI — current exact-reconciliation R0 PR #1627 remains under independent-review gate (do not merge merely because local tests pass).
2. Fix OKX **settlement** timestamp mislabeled as funding quote `observed_at`: a bounded research-to-Codex intake has been merged through [PR #1631](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1631), to be independently classified as `CODEX_READY/NEEDS_MORE_EVIDENCE/REJECTED`. It is NOT a completed code repair.
3. Preserve immutable Compass issues, original outcome denominators, abstentions/misses, original v2/v3 scoring contracts, and original CFGI engine eras; run mechanical baseline calculations ONLY after independent first-known source admission.
4. Keep Sol idle on duplicated/unchanged scientific issues and pre-filter with deterministic source-clock gates. The existing temporary Chat Supervisor and API controller retain routing authority without any additional scheduled task.

**Pass/fail for future API use:** At least one exact, independently challengeable previously unsupported claim or R0 code weakness with a reproducible fixture and owner-bound remedy; otherwise the reviewer should explicitly report `INSUFFICIENT_EVIDENCE` and stop. Model review alone does not confer historical PIT admission, independent PR approval, predictive skill or portfolio action rights.
