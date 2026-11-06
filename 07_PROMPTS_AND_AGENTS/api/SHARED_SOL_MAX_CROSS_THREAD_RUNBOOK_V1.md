# Shared SOL MAX cross-thread owner lane · v1 · 2026-11-06

## Purpose

This is the SAME existing Research Lab Sol owner route, not a new supervisor,
schedule, model credential, independent reviewer, financial authority or trade
actor. Any ChatGPT conversation that can use the authorized GitHub connector
can prepare a **new** Sol MAX research mission and execute the native GitHub
Actions event with the owner's **explicit per-call mandate**. The chat thread
is not an authorization identity. The GitHub event identity, original queue,
packet hash, consent, budgets, claim and provider output are the proof.

Canonical GitHub owners:
- Owner authorization / consent journal: `Donh91/Investering-Framework-Archive-v1#1156`
- Original API trigger / results issue: `#1476`
- Existing workflow: `.github/workflows/research-lab-sol-dispatch.yml`
- Mission queue: `research/api_agent/research_lab_sol/RESEARCH_LAB_SOL_QUEUE_v1.json`
- Immutable provider receipts: `research/api_agent/outputs/research_lab_sol/`
- Shared source-verified model policy: `research/api_agent/coordination/SOL_MAX_SHARED_MODEL_POLICY_V1.json`
- Owner's existing model, receipt, budget and CI policies remain binding.

## Starting a NEW mission in any conversation

1. First check `AGENTS.md`, the relevant original owner issue, open work,
   prior research receipts, actual budget risk, current main and the shared
   model policy. Explicitly identify the research task and confirm the owner
   has authorized this particular NEW paid MAX analysis. Reuse existing
   evidence before proposing a paid duplicate. Do not implicitly grant a
   new paid call merely because a previous mission received consent.
2. Use the existing public GitHub repo only. Create a source-frozen mission
   packet under `06_RESEARCH_LAB/mission_packets/` with a NEW unused
   `mission_id` matching `[A-Z][A-Z0-9-]{15,109}`, one task, hypothesis,
   falsifiers, scope, evidence allowlist, all-zero write/portfolio/trading
   authority, `reasoning_effort=max`, `max_runs_for_this_release=1`,
   `review_only_no_code_write=true`, `original_owner_issue=1156`,
   `public_source_only=true`, `public_storage_consent_30_days=true`.
   The standing public-only 30-day consent is owner GitHub #1156 comment
   `6682722905`, verified by the authenticated GitHub API before payment.
   Set `public_storage_consent_comment_id=6682722905` and
   `one_shot_owner_mandate=https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156#issuecomment-6682722905`.
   This is consent to storage only, NOT permission to purchase each mission.
3. Specify `max_model_output_tokens_per_new_attempt` between 2,048
   and the CURRENT verified Sol model ceiling (today up to 128,000).
   The amount is a *ceiling*, not a target. Cap the complete serialized
   public-source context at 180,000 bytes for a MAX run and require
   worst-case provider token price quote <= USD3, with the existing
   monthly USD40 / protected USD4 reserve / Research Lab lane USD10
   and all outstanding unknown POST upper liabilities. Otherwise reduce
   scope/split the research or BLOCK before any payment.
4. In the SAME original queue, hold/supersede the previous single
   `ACTIVE_RELEASED` mission with its exact old output/claim/receipt
   preserved, set it `new_paid_attempts_authorized=false`; add exactly
   ONE distinct current active owner-approved mission. A prior succeeded,
   failed, terminal, disconnected, completed or unknown paid POST is
   NEVER repeated. No new workflow or runner.
5. Make a normal bounded source PR. Perform tests including wrong actor,
   altered packet hash, old claim reuse, private source, budget upper,
   missing consent, output limits and no Astra. Check actual GitHub
   head/CI/rules, protect independently sourced evidence, owner-authorized
   qualified merge only, and verify main readback. Do not mislabel a
   chat-owned merge as autonomous S1 or a comment review as formal APPROVED.
6. AFTER the exact packet is frozen on main, compute SHA-256 over the
   complete, literal UTF-8 packet FILE BYTES, not just a JSON object,
   using the GitHub file content or local verified bytes. Publish ONE
   authenticated original OWNER comment on issue #1476. It MUST contain
   exactly one native trigger plus these owner release lines (substitute
   literal values, not placeholders):

```text
[RESEARCH_LAB_SOL] mission=NEW-UNIQUE-MISSION-ID
<!-- SOL_MAX_OWNER_RELEASE_V1 mission=NEW-UNIQUE-MISSION-ID packet_sha256=64-LOWERCASE-HEX -->
PUBLIC SOURCE ONLY; 30 DAYS; max_output_tokens=128000
```

   The owner GitHub actor/login must be Donh91 and issue #1476; model
   activation requires the source-frozen queue, exact signed packet hash,
   eligible public files, standing storage consent, project/model pricing,
   a verified native bot claim and no existing paid mission liability.
   Never invent a claim or send the trigger before qualified code/main release.
7. Observe the ONE native Actions run, its pre-HTTP bot claim, the
   Responses provider handle and `background=true, store=true`.
   GET-only recovery is permitted only with exact authenticated original
   claim/response-handle artifact; no repeated paid POST on errors,
   disconnects or terminal incomplete. Native source-bound `PASS` plus
   immutable output/receipt and actual original consumer readback are
   necessary to credit scientific/operational completion.
8. Report source, actual provider output/usage, estimated versus billed
   costs, and unresolved liabilities back in existing #1156 and #1476.
   Before admitting another mission, conservatively reserve any new
   unverified provider charge as a fresh upper risk in BOTH canonical
   ledger and mandatory source guard; do not treat absence of invoice as $0.
   A completed research report does NOT automatically merge code or alter
   scientific, market or portfolio rules.

## Model choice, including future 6.2

Current verified model: `gpt-6.1-sol`, 128k maximum output and the
source-pinned price/long-context policy. `gpt-6.2-sol` is a FUTURE
candidate, not an approved or yet verified model (2026-11-06).
When official 6.2 identifier, price, capability, context and availability
can actually be verified, the EXISTING S1/Strategist should propose the
minimal source-reviewed policy + API gateway price update through the
existing PR/CI lane. Once qualified on main, future runs automatically
prefer the highest verified/priced Sol, probe project availability by
nonpaid `GET /v1/models/...`, and fall back to Sol 6.1 if not accessible.
Never guess an unreleased model's price; if provenance fails, retain 6.1.

**ASTRA: ABSOLUTELY NO AUTOMATIC SELECTION OR FALLBACK.** No S1,
Strategist, background task, Research Lab, model router, other ChatGPT
thread or system may route to Astra without a NEW, explicit owner-authored
manual message/approval scoped to Astra. If Sol cannot proceed, return
BLOCKED / fail closed. The normal shared Sol MAX route never invokes Astra.

## What this does NOT authorize

A new paid request without a genuine current owner mandate, reusing a
historical single-use mission/claim, inventing a provider invoice or cost,
private source transfer, credential creation, autonomous GitHub merges,
new schedulers, unattended Astra, live trades or rewriting first-known
forecasts are all prohibited. ChatGPT threads lacking the connected
GitHub execution capability may draft a mission packet for owner
review but must not report that a GitHub action or API POST occurred.
