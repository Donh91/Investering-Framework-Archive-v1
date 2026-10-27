# MODEL CLASS CURRENCY POLICY v1.0 · 27 October 2026

**Status:** proposed in PR; production authority unchanged. **Source:** official OpenAI model directory and [GPT-6.1 Terra launch](https://openai.com/index/introducing-gpt-6-1-terra/).

## Current verified default within each class
- Luna: `gpt-6-luna` (routine, inexpensive)
- Terra: `gpt-6.1-terra` (bounded synthesis, visual/computer use, selected scoped code tasks)
- Sol: `gpt-6.1-sol` (deep reviews, scientific audit, complex reasoning)
- Astra: `gpt-6-astra` (historical pricing/readback metadata ONLY; prohibited for new API execution)

**Rule:** select the newest officially documented *and actually available and qualified* model inside the already approved capability class. A higher version is not a reason to change task ownership, role, budget, model class, output contract, or decision authority.

## Safeguards
1. Check official model ID, list/pricing, Responses API features, context, reasoning modes, account-level availability and existing output/structured-schema contract. A provider marketing release alone is not account-runtime verification.
2. Evaluate representative deterministic tests and immutable golden packets against the previous model, including failure modes. Compare accepted accuracy, retries, tokens and **total cost per successful task**, not token price alone.
3. Update the approved routing snapshot, fixed-price budgeting, task registry and exact model-binding tests **together**, via normal GitHub PR, CI and independent review. Never infer API prices from a numeric version.
4. Prepaid reservation, per-task and shared monthly hard caps, source-time gates, read-only scope and explicit model receipts remain mandatory. Model upgrade never increases financial ceilings.
5. Legacy model IDs in historical receipts, scientific comparisons, immutable experiments and backward-compatible cost readback **must remain intact**. A registered prospective experiment may migrate only with a new preregistration and independent comparison, never by historical rewrite.
6. If new model is not runtime-available or not qualified: **fail closed** or explicitly approve a measured same-class fallback. Never silently escalate to Sol/Astra, consume additional Work credits or merge a PR.
7. Review on provider release and at monthly audit; this is a governance check of existing work, **not** a new scheduled automation or paid discovery loop. No autonomous self-updating of production routes.

## Scope of this patch
Update active central API routing, relevant consumers/CI tests, and site/CN model defaults. Frozen PDLT v1.1 arms and historical receipts retain original identifiers. Rollout waits for CI availability, independent review and controlled live API confirmation. GitHub Actions quota can delay verification; do not bypass the release gates.

## Owner override · API class whitelist (27 October 2026)
The only approved **paid OpenAI API** model classes in this framework are **Luna, Terra and Sol**. This excludes Astra from routing, independent-model review, task overrides and other paid API invocation. An Astra model appearing in `/v1/models` is NOT authorization. Preserve old Astra/legacy prices for historical cost receipts, but never call Astra. ChatGPT Work or other non-API model selection is a separate owner decision, not an API loophole.

Preferred currently documented IDs: `gpt-6-luna`, `gpt-6.1-terra`, `gpt-6.1-sol`. Routine model selection follows minimum sufficient capability, verified runtime qualification, source/prompt scope, budget and expected *cost of successful completion*. Luna for cheap routine; Terra High for medium reviews/supervisor API escalation; Sol High for hard scientific/architecture issues. Terra Max is owner-authorized only for ONE bounded endgame audit; never periodic or default. Code changes remain the existing Codex/GitHub PR owner's responsibility; model output cannot merge or trade.

When OpenAI releases a later Luna/Terra/Sol model, agents may PROPOSE the latest same-class model, but production activation requires official model ID+pricing, account availability, representative output contract/negative smoke, budget proof, updated checked-in allowlist/pricing and independent code review. Runtime model listings are discovery, **not** qualification. No silent auto-migration, no version-to-price guesses. If a task requires Astra-exclusive capability, fail closed rather than paying for Astra or pretending the capability is met.

Never increase monthly/per-call hard stops, create parallel supervisors, launch an automatic paid retry, or bypass backup/source integrity gates to force activation. Existing GitHub Actions changes in PR #1823 are HIGH_IMPACT and require independent recovery evidence and exact-head CI before merge. Changes on the isolated PR branch are not production activation.
