# 02 · Budget, ChatGPT Pro grants, prepaid card control and model unit economics
**As-of:** 2026-10-30; planning not an account read/write. **No billing controls changed.** Currency USD. No raw user billing/account/organization details in public repo.

## Four DIFFERENT monetary concepts - do not conflate
1. **ChatGPT subscription** (Plus / eligible Pro 100, 200, 500): a separate subscription monthly payment. Pro eligibility is NOT inferable from an API project, Build tier, card top-up, or social screenshot.
2. **Promotional API grant:** eligible Pro 100/200/500 users can, after >=7 active subscription days and completing Billing→Link API Organization, receive up to $100/$200/$500 per **subscription billing period**; first grant prorated, unused expires, no rollover, subject to geography/availability and project entitlement. Not automatic just because user is on Pro; must see actual grant in **Credit grants** tab of the selected linked org. Plus is NOT eligible for this grant. Grants apply to API, not logged-in Codex/Work quota.
3. **Organization spend limit:** limits measured API spend in the organization at the selected billing window; may block usage EVEN if promotional credits have not all been used. Project-level limits and model rate caps can bind separately. The user screenshot shows a dollar-valued org spend limit; do not assume it is 30% of a subscription.
4. **Prepaid purchased API balance and automatic credit reload:** auto-recharge is a **card purchase mechanism**, not a free allowance. Separate threshold, target balance and optional **monthly purchased reload limit**. Manual credit purchases do not count against the auto-reload monthly limit. Spend limit, recharge limit, promotional balance and prepaid balance are NOT a single safety cap; check each independently.

**Critical ambiguity:** user typed `Max 30% auto top op om måneden`. Earlier screenshot showed organization `$30.00` and auto-reload MONTHLY `$30` in dollars; not a percentage. Do NOT read 30% as granted budget and do NOT change settings without explicit semantic confirmation. For all cost models below use an **illustrative $30/month total paid API spend planning envelope**, with actual current project + org UI controlling.

Sources: https://help.openai.com/en/articles/20001626-api-credits-benefit-for-eligible-chatgpt-subscriptions ; https://help.openai.com/en/articles/8264644-what-is-prepaid-billing ; https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform

## Current model cost snapshot - STANDARD processing, short context (<272k input tokens)
Official per 1M tokens on 2026-10-30; models selected by exact API ID, not ChatGPT product naming.

| Model ID | Uncached input | Cached input | New 30m cache write | Output (includes reasoning) | Preferred existing owner / task |
|---|---:|---:|---:|---:|---|
| `gpt-6-luna` | $0.10 | $0.01 | $0.125 | $0.50 | Routine typed metadata triage and summaries |
| `gpt-6.1-terra` | $1.00 | $0.05 | $1.25 | $5.00 | Bounded technical fix and science interpretation |
| `gpt-6.1-sol` | $2.00 | $0.10 | $2.50 | $10.00 | Hard code/forensic reviews with positive expected value |
| `gpt-6-astra` | $10.00 | $1.00 | $12.50 | $50.00 | **Not authorized by owner's existing API model policy**; reference price ONLY |

Official pricing: https://developers.openai.com/api/docs/pricing ; model pages https://developers.openai.com/api/docs/models/gpt-6.1-terra and https://developers.openai.com/api/docs/models/gpt-6.1-sol . Input >272k tokens can incur 2x input and 1.5x output pricing; Fast mode, regional processing (+10% where applicable), tools, sandbox, retries and cache writes add further cost. Cached reads are NOT free and cannot be assumed in forecasting.

### Standard noncached deterministic examples
Illustrative **per complete one-model request** of 20,000 uncached input tokens and 5,000 output tokens INCLUDING all reasoning, **no tool, no sandbox, no cached writes, no retries**:
- Luna: `20,000 / 1M * $0.10 + 5,000 / 1M * $0.50 = $0.0045`; 100 such calls $0.45.
- Terra: `20,000 / 1M * $1 + 5,000 / 1M * $5 = $0.045`; 100 = $4.50.
- Sol: `20,000 / 1M * $2 + 5,000 / 1M * $10 = $0.09`; 100 = $9.00.
- A blended *not scheduled* illustration: 600 Luna + 100 Terra + 20 Sol such calls ≈ $9.00 in model tokens; remaining $21 in a $30 illustrative envelope is **not free overhead** if agents create larger contexts, repeated turns, tool searches and hosted containers. An Agents API task may contain MANY model requests or subagents; do not price it as one request.

**Decisions API:** official GA `/v1/decisions` only `gpt-6-luna`; **$0.10 per 1M uncached input tokens, output tokens free for this endpoint**, caching writes/reads per Luna policy, regional/long-context additional. For 50,000 eligible uncached input tokens across one or more decisions calls, model input ≈ $0.005 before cache-write/regional fees. Use a real first call and receipt to verify billing in the project; its `confidence` is not real market-event probability.

**Batch:** if supported and nonurgent, effective ~50% of Standard model rate with 24h completion window; no shortcut for emergency P0, release gates or actual market event delivery. Prompt caching 30m writes cost 1.25x, 12h writes 2.5x; do not charge a cache miss as a hit.

**Hosted sandbox/tools:** official pricing lists hosted containers (example 1GB $0.03 per 20-minute session, 4GB $0.12), web search roughly $10/1,000 calls plus content-token charges where applicable, and other tool/storage charges; verify live rates per workload. All billed separately from model output. https://developers.openai.com/api/docs/pricing and https://developers.openai.com/api/docs/guides/agents-api/observability

## Three budget scenarios
| Scenario | Eligibility assumption | Conservative paid-API ceiling | Recommended action |
|---|---|---:|---|
| **A. Current pay-as-you-go** | No activated subscription grant proved, existing org spend-limit & auto-reload | USD 30 nominal monthly total API consumption, provided actual limit applies to all relevant projects | Keep existing limits. Prioritize receipts, tracing, dry-run/evals; implement no new hosted-agent cycle by default |
| **B. Pro 100 ALREADY subscribed and actual $100 grant present** | Link to correct API org, 7+ days, grant visibly issued and unexpired | Owner's independent **paid-card** auto-reload cap stays unchanged; org spend limit may still restrict spending of grant | Use granted API credit only within original owner tasks and current spend policy. **Do not automatically raise org spend limit** to consume promotion; make a separate owner decision if grant is trapped behind lower org cap |
| **C. Consider upgrading Pro for API credits alone** | User currently without grant and API use only few dollars/month | New $100/month subscription vs at most ~$30/month illustrative API costs | **Do NOT upgrade solely for grant**; it likely costs more than the avoided API bill. Evaluate Work/Codex/ChatGPT Pro usage benefits separately, not counted as free API |

Important: existing subscription could be Plus, Pro, a Business seat or another plan and the screenshots alone do **not** demonstrate a Pro grant. Pro tier names (Pro 100/200/500) are not usage tier 'Build'. To confirm actual user plan navigate ChatGPT Settings→Billing; to confirm **grant** navigate linked Platform org Billing→Credit grants. Only the user can authorize linking/change.

## Example $30 owner policy envelope, NOT a license to spend
- $8 steady-state existing low-cost LUNA/required scheduled API tasks
- $8 bounded original-owner code/science work (Terra, occasional Sol)
- $5 **separate** controlled QA/Decisions/evaluation
- $3 tools, sandbox/container and caching/retries reserve
- $6 uncommitted holdback for unexpected source/incident; no auto-overrun
**Sum $30.** This is *planning allocation*, not a configured project quota, no request to change current routing and does NOT imply all categories will spend their allowance. Preferred target < $20 routine and >=$10 contingency until actual receipts show quality.

A different policy is to cap paid-card auto-recharges at 30% of the Pro subscription amount; this is **NOT currently established** and would be $30 for Pro100, $60 for Pro200, $150 for Pro500. If the user really meant a percentage, confirm separately; no setting changes now.

## Payment and value reconciliation - CRITICAL P0
The current `LATEST_OPERATIONS_DASHBOARD.json` states `openai_api.cost_estimate_status=COMPLETE_FROM_RECEIPTS`, `spend_breakdown_semantics=DEDUPED_RECEIPT_ESTIMATES_NOT_PROVIDER_BILLING_OR_CAUSAL_VALUE`. It is an internal cost **estimate** for deduplicated framework receipts. Screenshots of Platform `Usage` can be filtered by project, API source, date (UTC), or keys and may show different totals. The org's actual purchases, grant use and usage are further different objects.

**Never treat a mismatch as a confirmed overcharge** until same-window, same-organization, all-project selection and identical rates/currencies are reconciled. Start from the **exact receipt IDs**:
1. UTC billing window with start and end inclusive/exclusive; project ID vs selected project, org ID, all API keys and source filters; whether screenshot cutoff is midmonth.
2. Every original request ID, model ID and per-request usage from existing GitHub receipts; dedup repeated runs/requests; retries and generated **reasoning** output tokens; tool calls + cached writes + sandboxes; batch/fast/regional rates and prices at request time.
3. Provider Platform org usage report vs project report; promotional grant consumption vs purchased prepaid; invoices record *credit purchases*, not model tokens consumed.
4. Reconciliation grid: `run_id, original_request_id, model, actual_input, cached_reads, cache_writes_30m, cache_writes_12h, output_incl_reasoning, tools, sandbox, region, actual_or_est_cost, linked_project, actual_provider_reporting_period, actual_producer_and_consumer_status, reconciliation_state`. Exclude private labels; make public report aggregate only.
5. Classify `MATCHED`, `SCOPE_MISMATCH`, `RATE_ESTIMATE_GAP`, `RETRY_DUPLICATE`, `PROVIDER_BILLING_PENDING` or `UNVERIFIED`. New budget changes only after issue-level evidence.

**Start this with existing #1156 Supervisor + current API accounting owner, not another finance/automation bot.** No new API key is needed merely to begin metadata-based reconciliation.

## Explicit tripwires
- On any org/project spend-cap or reload-limit breach: fail closed, no secret fallback account, no API model downgrade that changes semantics without owner approval.
- Do not set up auto recharge with infinite top-up, change paid card purchase amount, or silently raise platform org limit.
- No second subscription to buy marginal capacity before evaluating real existing API usage and included Pro benefits.
- If actual Pro credit issued and card auto-reload on, **promotional first** does not mean automatic purchases will never occur after grant expiry; check balances and reset. 
- Monthly external API dollars are **separate** from GitHub Actions included minutes, ChatGPT Work/Pro signed-in usage, Codex seat usage, CFGI/Birdeye paid sources or exchange fees.
