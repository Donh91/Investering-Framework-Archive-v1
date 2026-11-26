# BUILD Stage 0 · Standing owner execution mandate v1
Date: 2026-11-21
Decision source: owner explicitly authorizes ChatGPT to execute approved paid API work **without repetitive confirmation** after the build lane is independently reviewed, merged and qualified. Historical mandate: 3 missions × USD10, plus a separately accounted USD10 reserve; total program ceiling USD40.
Status of this file: **PROPOSED DELEGATION CONTRACT / NON-EXECUTABLE / NO PAID AUTHORITY WHILE HOLD APPLIES.**

## Purpose

Remove repeated human copy/paste and per-stage approval requests for already-approved mission scope while preserving a GitHub-native, auditable, single-use owner-identity launch route. User interaction should be needed only for genuinely new scope, a blocking budget/control change, or HIGH_IMPACT merge decisions. This document records owner intent; it is **not** a trigger comment, GitHub actor authentication, reservation, provider GET, receipt, executable workflow instruction, or override for any current code guard.

## Exactly covered future work

Only `ASTRA-BUILD-M1-20261121-S1`, `ASTRA-BUILD-M2-20261121-S1`, `ASTRA-BUILD-M3-20261121-S1`, plus their explicitly reviewed **stage-two** repair identities for M1/M2/M3 after a verified native failed-sandbox receipt. M1=Kompas; M2=regime feed; M3=S1 closure. No other mission or model is delegated. Only `gpt-6.2-astra` MAX, exact reviewed source bundle, reviewed fixed test command and exact allow/deny paths.

- Hard cap: USD5 per single request, maximum two requests per mission (second is repair-only), USD10 per mission, USD30 cumulative M1–M3.
- A separate USD10 contingency remains **unspent and not implicitly allocable** for additional work; it may be used only after a separately authenticated, owner-visible exception decision and reviewed extension without exceeding USD40 overall.
- All earlier aggregate/monthly provider caps, reserved settled/pending totals and protected safety reserve still apply. A USD40 expression is **not evidence of available headroom** or a replacement for verified billing/provider state. If guard cannot prove headroom or account access, HOLD.
- One paid POST per exact work ID only. On timeout, ambiguous handle, missing receipt or provider outage: NEVER repeat POST; GET-only recovery for a confirmed response ID. Every execution uses the original native shared ledger and a unique durable claim.

## Readiness gates before ANY paid BUILD call

1. Latest intended main SHA read directly, original #2277 (or successor) exact-head native CI all green, independently reviewed by Codex and detached Claude for HIGH_IMPACT, current original owner approval/merge, qualified main readback. User's existing release guard remains authoritative.
2. A genuinely reviewed immutable OCI image with **pytest and Node preinstalled** (and any other test dependencies required by exact M1/M2/M3 commands) is pinned by digest, available in the isolated runner, and has a real native offline smoke verifying each fixed command and blocked outbound-network attempt. **The existing Python-only image does not satisfy this.**
3. `scripts/research/owner_astra_mission_v1.py` currently carries **BUILD_RELEASE_HOLD_PYTEST_NODE_IMAGE_NOT_PINNED** in both reserve and submit. This must remain fail-closed until a separate exact-head reviewed toolchain/release PR proves gate 2. No blanket removal, CI downgrade, fabricated PASS or substitute command.
4. Each exact stage must exist as a source-manifest-bound reviewed mission on main with its one-use request digest, real native cost/ledger admission and accepted original owner boundary. No model-chosen shell, code execution in paid secret job, new scheduler, auto-merge, wallet, live trade, Round3 scoring or private data crossing a public repo.
5. Stage 2 requires an independently authenticated stage 1 native execution *and failed fixed-sandbox test* receipt, not a model excuse or ambiguous paid POST. No automatic second request on non-test failure.
6. Future execution can be initiated by ChatGPT through its **owner-authenticated GitHub connection**, provided the exact comment is emitted as the real `Donh91` owner actor, not impersonated; GitHub's existing `issue_comment` verify job must confirm actor, exact issue, main, immutable bundle digest and all native gates. This is not an authorization for a bot or GitHub Actions account to impersonate Donh91 or to bypass owner-event checks.
7. No silent scheduled/background ChatGPT work is promised by the user's approval. Within an interactive run or a separately existing authorized scheduled task, issue exact owner route only after verifying the live eligibility. Do **not** install a new monitor or dispatcher to make this work.

## What "without hassle" means

Once the actual gates above pass, **do not ask the owner to reconfirm each individually already delegated M1/M2/M3 eligible launch**. Use the existing verified route with current owner connection, post the exact single-use launch, read back the action and its resulting native receipt, inspect the finished output, and continue to the next eligible stage only when real dependencies, budget, scientific authority and reviews permit. Notify the owner only for a true release/budget/safety exception or completed deliverable; do not send routine noise.

## STOP and rollback

Any drift in model, reviewer head, current main, original-owner approval, contract, budget availability, image digest, fixed test command, capability boundary, privacy, origin identity or evidence quality leads to STOP. Revocation of this mandate by the owner halts all future unclaimed stages. Already attempted provider requests cannot be retried or undone. This delegated mandate cannot self-amend and is subordinate to independent code review, S1 governance and the current original owner policy.

**Not an execution receipt:** no BUILD mission has been approved to spend, no budget is reserved by this file, and the Python-only test image hard HOLD remains active.
