# Task-first Skill Discovery: existing agents, no new orchestration

**Dato:** 2026-11-13  
**Status:** OPERATIONAL_CANDIDATE / REQUIRES_NATIVE_PR_MERGE_AND_CONSUMER_PROOF  
**Område:** agent skill routing, actual use and minimal learning  
**Primary folder:** `07_PROMPTS_AND_AGENTS/github_agent/`  
**Original owner:** `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`, `canonical-context-router`, S1 #1156 for S1 only, original Research/Alpha domain owners otherwise  
**Existing proof/learning owner:** `06_RESEARCH_LAB/architecture/2026-09-23__agent-invocation-contribution-ledger-shadow-contract-v1.md`

## Decision

Do **not** put the whole skill archive in long-term model memory, add another agent, create a scheduler, add a model router or automatically run every skill. Instead give existing agents a **cheap discovery habit**: inspect the already-owned `SKILL_ROUTING_INDEX.json` metadata after current authority, load only the eligible matching skill file, and prove actual use only from native read/invocation receipts.

A skill registry/index entry does **not** mean any model, S1 scheduled task, Claude, Grok, Codex or external consumer has read or adopted it. Live task prompts, actual GitHub permissions, current main and domain owner remain authoritative.

## Tiny native selector, where a local checkout exists

```bash
python scripts/agent_skills/discover_task_skills.py \
  --task "reproduced S1 original PR merge conflict and missing closure proof"
```

- Reads the local existing derived index. Does not fetch model output or open any SKILL.md.
- Returns up to three exact skill paths, matched literal trigger strings, maturity, checkout-local index SHA256 and `invocation_status`.
- Never includes unaccepted candidates by default. `--include-pilot` is a review-only discovery option, **not** an activation flag.
- `allow_implicit_invocation=false` means **EXPLICIT_ADMISSION_REQUIRED**. The candidate may be inspected by an agent only if separately permitted by current task/owner policy.
- This is a **lexical hint**, not semantic task comprehension, evaluation, actual execution or a skill router with independent authority. No-match and skip are valid results.
- For agents without a shell, read only `00_ARCHIVE_CONTROL/SKILL_ROUTING_INDEX.json`, choose matching metadata and read the exact `SKILL.md` source manually; do not invent a script execution receipt.
- Never send credentials, private market/provider values or personal portfolio details as command-line task descriptions, GitHub logs or comments.

## Existing-agent adoption, source- and action-first

| Existing actor | When to perform lightweight discovery | No-op and limits |
|---|---|---|
| **Chat S1**, existing hourly task only | On material new original-owner defect, repeated HOLD with new evidence, unfamiliar source/skill error or eligible approved remediation needing a specialist procedure | A fully qualified original PR merge is executed first, not delayed for a skill catalog scan. Monday read-only still applies. No new S1, identity or saved-task edit from this file. |
| **Research Lab / Task2 / CRE** | At initiation of a *new* material research problem, falsification or source issue, or after a surprising high-value conclusion | Existing scientific owner/forward gate must admit claims, pilots require review and an external API requires its budget authority. No automatic Sol MAX calls or retrospective prediction credit. |
| **Alpha Lab / S4 / S5** | On actual new executable sellability, source-PIT, wallet provenance or outcome-validation issue | Source and native on-chain proof outrank skill prose; no new token scanners, tasks, wallet signing or real trading. Respect separate repo access. |
| **Claude/Grok via Bridge** | When a source-bound original owner explicitly asks for a bounded external review and the provider actually has access to the pinned skill | A text mention in public Archive is not proof that external Claude/Grok ran that skill. |

## Execution First - common method reference for existing agents (2026-11-25)

For material work that the current actor is already permitted to execute, use the existing [Research Package method, Execution First section](../../06_RESEARCH_LAB/methods/RESEARCH_PACKAGE_TO_REVIEW_PR_v1.md#execution-first---owner-directed-procedure-refinement-2026-11-25) as the shared internal-work reference, not as a new task, skill or mandate. The objective is to maximize completed, tested, coherent work per session, not maximize reports, handoffs or PR size. Select the smallest necessary skill set, then execute.

- Interactive ChatGPT/Work and authorized product-development agents: research, implement, test, self-red-team, repair, retest and package together within the existing owner, scope and tool permission. Request consolidated final review only at the applicable mandatory boundary.
- Research Lab/Task2/CRE and Alpha research: apply the same loop to permitted analyses, prototypes and source qualification; scientific admission, Round 3 collection-only, original test owners and active-lane limits still bind. Read-only collectors/observers do not become writers.
- Codex: when already assigned a bounded original-owner task, deliver actual scoped changes and executed tests, not an intermediate research summary. This is not a Codex dispatch or readiness authorization.
- Claude or other designated independent reviewer: receive a complete source-bound candidate for adversarial review; an author cannot independently review its own head. Use the established Bridge routing for research versus formal release control. Where separately authorized as a developer, do not also act as the independent reviewer for that delivery.
- S1: existing pinned bootstrap, action loop, one-tick action bounds, review admission, Monday read-only and release authority are unchanged. A qualified release or due obligation takes precedence; this reference is not executable S1 policy or a prompt update.

Keep only material checkpoints in the existing issue/PR/run receipt, including actual artifacts, executed vs proposed tests, remaining blocker and next trigger. A temporary lack of independent reviewer is not a reason to stop unrelated authorized development. A mandatory prior review/admission gate is a reason to stop the affected action, not permission to bypass it. No extra external review of each internal substep unless the current governing contract requires it.

Availability of this reference does not demonstrate adoption by a particular task. Existing nonimplicit/pilot invocation and skill-quality gates remain unchanged; no automatic default promotion from documentation.

## Minimal user-visible and machine receipt

Use an **existing run/issue/PR receipt**, not a new ledger, only when a skill materially changes an existing high-value decision or repair:

```yaml
task_original_owner: <existing owner>
task_source_ref: <exact current ref, if actually read>
skill_discovery_status: SKIPPED_ROUTINE | NO_MATCH | SHORTLIST | BLOCKED | NOT_RUN
index_ref_or_sha256: <exact read or UNKNOWN>
skill_path: <exact SKILL.md path or NONE>
skill_blob_sha: <verified blob if actually read, otherwise UNKNOWN>
skill_use_status: SUGGESTED_ONLY | READ_CONFIRMED | PROCEDURE_APPLIED | NOT_APPLICABLE
evidence_effect: <one concrete falsifier, original PR result, corrected priority, or UNKNOWN>
next_owner_action: <one original owner action or NO_ACTION>
```

A listed path or a generated JSON hint is **not** `READ_CONFIRMED`. A read is **not** `PROCEDURE_APPLIED`. A procedure used is **not** proof of edge, profitable trades, reduced token cost, successful merge or natural S1 execution. Use the existing Agent Invocation Contribution Ledger shadow taxonomy when the source- and time-bound join can actually be made. Missing telemetry = UNKNOWN, not zero.

## Validation and promotion, with no background obligation

1. PR CI runs existing skill architecture validator plus selector's independent positive, negative, candidate/nonimplicit and no-action tests. Tests establish code contract, **not** runtime skill benefit.
2. Read back exact merged main blobs. No production change without original-owner release gates.
3. For actual adoption, collect a bounded sample of source-verified S1 and Research/Alpha uses through existing receipts; compare baseline without selector, missed relevant skills, needless skill reads, native closure and action quality, token/cost where actually observed.
4. Independent `skill-quality-gate` adjudicates any claim of skill-performance improvement. Do not count model self-evaluation as independent.
5. Reuse `AGENTS.md`, `SKILL_REGISTRY.md`, current original domain methods and S1 saved task. A future saved-task alteration requires a separate current-task readback, parity tests and the **same** existing task ID, with no automatic promotion from this documentation.

## Failure modes and kill conditions

- **Over-trigger**: ordinary status, routine answers or approved merges slowed by extra discovery.
- **Authority drift**: pilot/nonimplicit skill treated as authorized; public archive metadata treated as private data; suggestion treated as market/trading/release policy.
- **False completion**: JSON shortlist or skill list logged as applied work.
- **Index drift or broken source**: do not guess a missing skill. Continue known canonical operations and flag source metadata mismatch for the original owner.
- **No measurable value**: after bounded real cases, narrow or retire the helper rather than keep an expensive ceremony.

**Explicit out of scope:** new supervisor, cron, paid API, model/provider switch, new Skill Registry or science engine, changed data authority, frozen forecast edits, portfolio orders, independent GitHub identity, automatic PR release and external memory upload.
