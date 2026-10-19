# CRITICAL ADDENDUM — FULL COMPASS PARITY ACROSS CHAT AND SITE (2026-10-19)

Status: OWNER-REQUIRED DESIGN / REVIEW-ONLY. Companion to Sol 6.1 mission in PR #1683. This addendum **does not change** existing canonical contracts, market rules, site code, scheduled jobs or owner authority.

## Core correction to the mission
**Every invocation of “Kompas” in chat and every Site Kompas view must be a COMPLETE CURRENT CROSS-READ of the framework, not a Monday summary, not merely Official Daily Compass, and not a static weekly CN card.** Official Compass is the highest-authority *current action/navigation owner*, but the **complete Compass analysis** cross-reads all relevant accepted layers. Its interpretation does not supersede the independent canonical ownership of market state, frozen forecasts, Task 4 scientific evidence, sell/protection decisions or the weekly CN horizon.

This is **already required** by `07_PROMPTS_AND_AGENTS/action_compass/2026-09-16__global-action-compass-invocation-contract-v1__canonical.md` §3.1, and the site already has a partial/full-stack projection architecture. **Do not create a second Compass engine or replace this contract. Implement only evidence-backed missing connections and regressions.**

## Verified existing implementation (read 2026-10-19)
- Global invocation §3.1 requires Auto Market State, immutable Official Daily Compass, Native Handlekompas, Shadow Compass v2 (NON-BINDING), governed weekly Master Monday/CN, Strategic Compass, pullback/distribution, SELL/Swing, re-entry, rotation, market health, Bull/Bear, and outcome accountability; every request cross-reads even when the user asks for a short horizon.
- Chat output: STATUS/HANDLING/TID for BTC, ETH, large, mid, small, micro, memes; horizons 12–24h, 1–3d, 5–7d, 2–3w, 21–30d, 4–8w; pullback, separate SELL/Swing and re-entry; official-vs-shadow disagreements; independent interpretation; TEXT_ONLY, iPhone-friendly.
- `05_CYCLE_NAVIGATOR/site/build-public.mjs` already reads official public/internal Compass, CN, Native, Shadow, Strategic, Auto Market State, weekly handoff and public series. `05_CYCLE_NAVIGATOR/site/compass-product-v5.js` already renders `PUBLIC_COMPASS_FULL_STACK_READBACK_v1` with official/shadow/strategic/weekly status and horizons. `05_CYCLE_NAVIGATOR/site/validate-compass-site-v5.mjs` already checks full-stack readback, authority, source hashes and freshness.
- Current Official public and internal pointers share `compass_id=CMP-20261019-8ca1978b5bd2` and issuance `2026-10-19T11:06:58Z` at inspection; do not assume current at later execution.
- `05_CYCLE_NAVIGATOR/site/SITE_CONTRACT.md` rules 1–28 already establish canonical weekly/Official Compass ownership, site delivery-only authority, current-week alignment, protection/sell/re-entry owners, source-supported ETA and public issue identity. Preserve them.
- `05_CYCLE_NAVIGATOR/site/compass-product-v5.js` has `friendlyAction` mapping `DE_RISK|PROTECT|EXIT|SELL` to displayed `HOLD`. This **requires explicit safety review**: confirm the source semantics and whether the public presentation hides material protective state. Do NOT blindly change to SELL (public portfolio execution is not authorized), but do not silently dilute a confirmed protective risk instruction either.
- The site `fullStackSection` reports `COMPLETE` vs `PARTIAL EVIDENCE`; verify that COMPLETE truly means all *required* current layers were checked, not merely a small subset. Source presence alone does not imply source freshness or eligibility.

## Non-negotiable invariants
1. **Same evidence, same decision:** for a shared exact snapshot ID/source hashes and evaluation time, chat and SITE must agree on official action, segment-level status, horizon status, protection/distribution/re-entry, next gate, and unavailable/degraded reason. Language/layout may differ, authority may not.
2. **Current ≠ weekly:** Monday's completed-week outcomes and next-week frozen CN are immutable context; live Official Compass is the current action authority. A current-time Compass request reads all eligible layers again. No stale weekly `WAIT` may overwrite fresh official action. No live price may rewrite weekly freeze.
3. **Full cross-read, no shadow promotion:** Shadow/independent research must be examined for agreement/conflict but cannot set official BUY/SELL, phase, thresholds or prospective receipt. Common source packet must not count as two independent confirmations.
4. **All segments and horizons:** BTC, ETH, large, mid, small, micro, memes; 12–24h, 1–3d, 5–7d, 2–3w, 21–30d, 4–8w. Preserve `UNAVAILABLE` for unsupported horizon, not a guessed range. Micro does not proxy memes.
5. **Risk layers separate:** pullback ≠ distribution ≠ SELL ≠ swing ≠ re-entry. Protection and SELL assessment remain with their typed existing owners. Do not conflate generic public HOLD with confirmed protection state.
6. **Freshness and fail-closed:** verify hashes, source packet identity, timestamp, contract version, current/week alignment, public sanitization and source freshness. If one required lane is stale, expose PARTIAL/DEGRADED and its exact reason, preserving independently valid lanes; do not report COMPLETE falsely.
7. **No hidden interpretation split:** client JS may format, translate and order fields but not infer new market phase, action, ETA, Bull/Bear or threshold. Chat must not use remembered prior messages as substitute for latest owner reads.
8. **Public privacy:** private portfolio/wallet/position sizing, API receipts with sensitive values, restricted providers and internal challenger reasoning never reach public JSON, HTML, X or browser logs.
9. **No regressions:** do not alter existing workflows, owners, public issue numbering, scheduled refresh, budgets, frozen historical outputs, 390px layout, DA/EN, GitHub Pages routing or source integrity to force a pass.

## Required architecture before code
Build a SOURCE→DECISION→RENDER matrix, per lane:
`source_owner | canonical path | immutable identity/hash | producer cadence | expected SLA | source_status | admission | decision authority | public projection field | site renderer | chat renderer | test owner`.
Cover Auto State, Official Daily, Native, Shadow, Strategic, weekly Master Monday, CN freeze/public identity, pullback, distribution, sell/swing, re-entry, market weather, Bull/Bear, outcomes and liquidity/rotation inputs. **Do not invent an SLA**; use current owner contract. Mark genuinely missing edge as MISSING rather than adding another engine.

## Required parity tests
- Freeze exact test fixtures and compare normalized chat/SITE decisions by source identity (not free-form prose).
- Monday→Tuesday and Monday→Sunday: weekly baseline unchanged; live Official Compass advances; both clients show latest eligible official state.
- Fresh Official Compass vs stale Monday commentary: official current action wins, weekly context stays labeled.
- Valid weekly + stale Compass: weekly forecast remains visible; live action fails closed.
- Source hash mismatch, cross-week binding mismatch, missing Native, stale Shadow, conflicting Strategic, missing SELL owner, absent meme-specific signal: correct typed partial status; no synthesized BUY/SELL/phase/ETA.
- Simultaneous official protective warning and shadow bullish research: official risk state dominates action; independent research remains labeled NON-BINDING.
- `DE_RISK`, `PROTECT`, `EXIT`, `SELL` render mappings: verify public semantics never disguise material protective status; never expose private execution instructions.
- Distinct short horizon vs 21–30d vs 4–8w: do not extrapolate 2–3w into longer horizon.
- Weekly public #30 vs machine #31: no numbering crossover.
- Site `COMPLETE` iff required evidence cross-read and verified; partial source outage cannot be presented as COMPLETE.
- iPhone 390px and DA/EN presentation, accessible risk indicators, source age, no fabricated live data.
- Regression of all existing `validate-compass-site-v5.mjs`, full-stack readback tests and relevant weekly/CN/Compass suites. Add tests rather than weakening existing ones.

## Implementation order and risk containment
A. **READ-ONLY D0:** exact fresh main, AGENTS, open PR overlap, source→decision→render inventory, reproducible missing edge and risk severity. Do not label an existing working edge broken.
B. **TEST-FIRST D1:** add normalized parity fixtures and negative tests in existing test suite; no production change.
C. **SMALL D2 PRs:** repair only demonstrably broken source binding/contract field, with owner approvals and CI; keep Monday→CN→SITE public-safe summary separately from Official Compass live overlay.
D. **D3 logging:** compact weekly machine-only evidence index via existing writer and readback, not a new queue/pointer or market source. Preserve Task 4 scientific firewall.
E. **D4 release:** required independent review and protected merge by authorized existing executor, natural production run and public Pages readback. If blocked, return exact SHA, test and owner gate to existing Supervisor; no workaround bypass.

## Sol 6.1 execution boundary
Use **only** an already approved existing owner-gated API task/gateway, after verifying Sol 6.1 availability and lane budget. `research/api_agent/API_INTELLIGENCE_POLICY_v2.json` says `SENIOR_REPAIR_AUDIT` automatic code write/merge are false; API research receipt cannot itself authorize merges. Existing authorized GitHub executor may make scoped code PRs. No Work credits, new agent, cron, scheduler, router, paid service or independent authority.

## Definition of success
On any weekday, the same official frozen/current source identities yield matching chat/SITE decisions across all relevant assets, horizons and protection layers. Monday report is source-bound context, not a competing current decision. Missing data is explicit; private data stays private; weekly freezes and Task 4 remain immutable. Every critical assertion is tested with a failing mutation case and verified actual CI receipt.
