# Framework Strategist · Governed Semantic Reasoning v2

**STATE: SOURCE RELEASE THROUGH EXISTING PR #1667; actual merge/runtime receipts belong in #1156.**
Owner instruction of 20 October 2026 explicitly permits self-review and governed single-account integration for this mission. Record `SELF_REVIEW` and `SINGLE_ACCOUNT_OWNER_AUTHORIZED_MERGE` honestly, never independent acceptance or GitHub `APPROVED`. Historical requests for an additional model review do not require recursive review handoffs under this owner-directed release. Real platform safeguards and unresolved material defects still stop release.
The deterministic Strategist v1 is merged in main and remains sole source of machine-audited observations. This PR adds a low-cost reasoning **specialist call inside the EXISTING** Framework Learning Supervisor workflow, not a new supervisor, queue, workflow, recurring scheduled task, persistent agent, model router or recovery authority.

## Minimal execution contract
`scripts/framework_intelligence/framework_strategist_semantic_v1.py` owns (a) validated source-bound context (b) stable fingerprint representing only material question semantics (not daily source timestamps) (c) append-only one-attempt financial reservation packet and (d) post-call verification.
`scripts/api_agent/api_gateway.py` remains existing model/billing receipt owner. Only the existing `.github/workflows/framework-learning-supervisor.yml` invokes it, once and only on new material evidence after existing monthly+lane budget gates.

Input: SHA-bound `research/framework_learning/strategist/LATEST.json`, exact allowlisted original owner sources and `STRATEGIC_INTENT_v1.json`. The model receives *only* 0-3 bounded question codes/severities/owners/fingerprints, no portfolio/private data and no unfiltered source documents.

Output:
- `research/framework_learning/strategist/semantic/LATEST.json` — optional, untrusted model opinion; no scientific promotion.
- `research/api_agent/outputs/framework_strategist/run-<github_run_id>/receipt.json` — actual provider token/cost receipt through existing gateway.
- `research/framework_learning/strategist/semantic/reservations/<sha256>.json` — **created on main via GitHub's atomic Contents API before API billing**. If this create fails, NO MODEL CALL. On any failed or uncertain paid response this reservation remains: no automated retry for same material fingerprint.

## Cost
Model default `gpt-6.1-terra`, high reasoning effort, 5,400 output-token ceiling, strict one-attempt gateway override. Global monthly hard stop **$40 unchanged**, reserve **$4 unchanged**. New strategist sublane cap **$0.75/month** and minimum **$0.05** remaining; user authorized OpenAI API but never blanket budget expansion. No automatic senior/Astra fallback; manual, separately reviewed specialist path remains required. No payment without `OPENAI_API_KEY`, existing budget receipts and verified GitHub prepayment reservation. Single-call budget does not prove actual provider-side debits: hold/reconcile separately if uncertain.

## Behavior
1. Deterministic Strategist generates source-fresh, SHA-verified 0-3 owner-bound proposals.
2. `prepare` sees whether at least one HIGH/MEDIUM/CRITICAL question exists and checks frozen material fingerprint against any earlier durable paid-attempt reservation.
3. Old material fingerprint, missing/ambiguous input, optional source absent without use, malformed original SHA, absent budget proof, missing key, or failed reservation => NO CALL.
4. If admitted: existing code creates a durable reservation in main, then one Terra 6.1 High API gateway request. **No auto retry.**
5. Output is verified against task, model, exact source/context/prompt SHA, reservation run ID, response hash, cost/attempt receipt, bounded output and empty forecast candidates.
6. Only advisory untrusted result is published; never send model prose into GitHub command executor, new queue, Grok, Codex, market or portfolio logic. Existing Supervisor will only read a semantic interpretation after a separately reviewed **bounded consumer adaptation** (this PR does not cause strategy-based automated actions).

## Independent reviewer tasks
- Reproduce upstream falsification: tampered original receipts, wrong contract, stale strategist, duplicate paid attempt, cross-run reservation mismatch, invalid API hashes/status/attempt_count, excessive text, prompt injection, symlink file escape, stale head and optional source semantics.
- Verify no GPT-6.1 Terra hidden spend, no new schedulers, global $40 hard stop unchanged, model name runtime eligibility in provider and accuracy of per-token budget pricing; avoid claiming model API live success without real call.
- Scrutinize GitHub Contents API reservation race/atomic first-create semantics. Simulate repeated/concurrent runner attempts and partial provider failure. The new receipt goes to main ahead of the normal end-of-run learning commit: test rebase/readback and ensure it doesn't cause a livelock.
- Check that semantic fingerprint avoids daily reload noise without suppressing truly new high-value outcomes. Check resilience if missing source data makes `prepare` fail; parent Supervisor's core products should not be silently suppressed.
- Governed merge only after independent model audit and all applicable CI green. No fake GitHub APPROVED. No 30-day shadow test requirement; targeted post-release production readback and value measurement mandatory.

## Complexity budget / sunset
No new schedule, separate owner, parallel queue, new credential, autonomous order, forecast output or changed core budget cap. One new semantic script and one bounded test module; minor registry/price and existing workflow integration. Following release, measure accepted owner investigations minus noisy proposals and incremental inference cost. Sunset if no measurable decision benefit after ten admissible opportunity events; no prelaunch waiting period.

## Connection audit correction, 20 October 2026

This prepared #1667 revision reconciles current main Resource Steward additions rather than overwriting them. The existing workflow now finishes deterministic producers, then calls `framework_learning_supervisor.py --finalize-strategist`. That command validates the current brief through the original source-hash/authority reader, requires a current-run state and producer timestamp, and atomically updates only existing `LATEST_SUPERVISOR_STATE.json`. It does not rerun source producers, rewrite old snapshots, add a queue, or enable automatic action. Original snapshots remain producer-stage observations. A real post-brief source mutation remains `SOURCE_MOVED`; old briefs cannot be relabeled as current production.

Resource Steward is optional for free deterministic observations, but mandatory before a new semantic paid attempt. `CRITICAL`, `CONSERVE`, `UNKNOWN`, missing or invalid resource advice sets `run_allowed=false`; reservation creation is then refused. A critical budget warning cannot authorize spending to analyze itself. Synthetic `NORMAL` test fixtures are not provider billing evidence; ordinary lane/global/key/reservation checks remain necessary. No API call was made in this audit.

Grok's owner-approved Bridge-only report policy is separate from Claude's pause. An incoming report is advisory evidence, not a new automatic source or an authenticated provider-run receipt. This change installs no Bridge polling, task queue or Grok dispatcher. Only existing owner adjudication may supply an independently verified source-bound handoff.

Release requires current-head technical inspection, applicable GitHub checks and safepoint/release requirements under the explicit owner-directed procedure above. After release demand one existing natural run with matching producer/consumer hash and proposal IDs. A prepared commit, local tests or a green producer alone is not this proof.

## Monthly liability admission

The existing workflow also claims a conservative maximum bill in one month-wide GitHub Contents CAS blob before calling the gateway. Different material fingerprints contend on that same blob SHA; duplicate fingerprints, a lost CAS race, HTTP/auth/transport uncertainty, malformed/tampered ledger or missing exact PUT receipt stop payment. Both per-question reservation and maximum monthly liability remain consumed after failure/unknown provider response; neither is automatically refunded. The existing $0.75 lane cap/$0.05 reserve and global $40/$4 receipt gates remain. This repository accounting is not an account-wide provider billing limit or proof of actual charges across unrelated clients.

## Owner correction: latest Terra High, October 27
Current `FRAMEWORK_STRATEGIST_SEMANTIC` on PR #1823 uses `gpt-6.1-terra` HIGH rather than 6.1 Sol for routine material-delta strategic reasoning. Existing single-attempt, source-bound context, atomic paid reservation and budget gates ($0.75 lane, $40 global, $3 per-call) remain unchanged. Sol High is an explicitly approved separate senior escalation; Astra is excluded from all paid API model routing. Old Sol receipts stay frozen; no new workflow or schedule was created.
