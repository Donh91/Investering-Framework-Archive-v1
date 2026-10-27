# MODEL CLASS CURRENCY POLICY v1.0 · 27 October 2026

**Status:** proposed in PR; production authority unchanged. **Source:** official OpenAI model directory and [GPT-6.1 Terra launch](https://openai.com/index/introducing-gpt-6-1-terra/).

## Current verified default within each class
- Luna: `gpt-6-luna` (routine, inexpensive)
- Terra: `gpt-6.1-terra` (bounded synthesis, visual/computer use, selected scoped code tasks)
- Sol: `gpt-6.1-sol` (deep reviews, scientific audit, complex reasoning)
- Astra: `gpt-6-astra` (highest-complexity work)

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
