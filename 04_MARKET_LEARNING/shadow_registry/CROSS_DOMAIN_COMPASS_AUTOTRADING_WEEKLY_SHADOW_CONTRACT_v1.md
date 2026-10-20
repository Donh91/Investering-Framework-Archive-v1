# Cross-domain weekly shadow learning — Compass, AUTO_TRADING & Alpha Lab

**State:** `DRAFT_RESEARCH_ONLY` until independent review + merge of this PR, exact main readback and a **natural Monday candidate and main-consumer proof**. The existing framework must not claim automatic weekly end-to-end evaluation because only the generation pipeline exists until those gates are observed. No new GitHub Actions schedule, ChatGPT automation, private data ingestion, API budget, wallet signer, order execution or scanning engine.

## Reuse the only existing weekly source path

```text
Existing market/hourly/Compass and existing experiment lifecycle owners (do not touch)
  |
  | already committed PUBLIC, source-valid, time-stamped JSON
  v
Existing 07:41 Monday Shadow Registry Weekly workflow
  | deterministic-only new cross_domain_review subfield in Wxx weekly snapshot
  | no fresh API/web/LLM calls, no source switching, no price/market computation
  v
Existing review-required Shadow Registry weekly PR (NOT direct-to-main)
  | until independently reviewed, merged, exact main SHA readback
  v
Existing Framework Learning Supervisor (09:35 Monday + normal schedule)
  | deterministic 'LATEST_MASTER_MONDAY_LEARNING_PACKET.cross_domain_shadow_weekly'
  | if current weekly PR not accepted yet => PENDING_REVIEWED_WEEKLY_SNAPSHOT
  v
Existing S1 cross-repo Supervisor / #1530 / #1557 / #1340 owners
  | review material source changes, owner-aware falsification once per week
  | new tests only after independent scientific admission
  v
APPEND_ONLY learning/evidence through the SAME canonical owners
```

**Timing caveat:** Current Shadow Registry [W41 PR #1491](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1491) and [W42 PR #1588](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1588) are **open, not published on main** as of 2026-10-12. Even when this PR merges, the 09:35 supervisor may have run before an independently approved 07:41 weekly snapshot merges. It MUST output PENDING; no candidate PR counts as accepted proof. No force merging old candidate PRs or rewriting immutable weeks to simulate activity. First natural qualifying week likely W43 or later, conditional on independent acceptance.

## The 3 domain research contracts (zero promoted investment edge)

| Lane | Existing source/owner | Weekly question, no hindsight | Current scientific blocker |
|---|---|---|---|
| COMPASS | `04_MARKET_LEARNING/handlekompas/shadow_v2/LATEST.json` + `research/framework_memory/action_compass_calibration/LATEST_EXIT_WARNING_CALIBRATION.json` + `research/framework_memory/edge_compound_governor/LATEST.json`; #1530/#1553/#1516 | What was **actually** forecast before outcome, matured, censored, missed or delivered? Did 12/72/168h, 7d, 14–21d warning beat HOLD, cash and mechanical baseline **after trade friction**? | Eligible calibration rows ≠ verified timely warnings; 0 warning-series rows in recent accepted owner; information/action edge UNPROVEN |
| AUTO_TRADING | `research/experiment_lifecycle/weekly_adjudication/LATEST.json` + `research/experiment_lifecycle/SEQUENTIAL_RESEARCH_QUEUE_v1.json`; #1557 and Experiment Lifecycle | Are all proposals, abandoned trials, revisions, failures and negative results in the global prior-to-outcome denominator? Was the paper order realistically executable? | Research candidate count ≠ global attempted hypothesis/trial denominator; `BROAD_SEARCH_BLOCKED` until #1557 resolved, no authenticated paper net PnL |
| ALPHA_LAB | Private `Donh91/Meme-Alpha-Lab` existing owner #88/#77/#126 and Archive #1340 | Were onchain token/CA and first-source-seen correct *prospectively*, buyer economics independent after router exclusions, both sides tradable, and matched failures retained? | PRIVATE_NOT_IMPORTED until independently source-authenticated **value-free** existing owner export; no false public reads of private holdings, wallets or alerts |

**Source-valid ≠ scientific-valid:** Contract-valid input rows only prove source metadata was read. A `PASS` calibration validator may have **zero qualified warning successes**. The current AUTO adjudication has hundreds of research candidates; these may be aliases/siblings and **may NOT** be called the global trial count or investment attempts. None of the three lanes is credited with profitable strategy performance.

## Minimum shadow observations once prospective owners permit them

At decision time freeze exactly: `owner`, `chain+exact_CA_or_asset`, `policy_version`, `source_hash`, `source_observed_utc`, `decision_issued_utc`, `horizon`, `counterfactual_ACTION`, `HOLD/cash/trend baselines`, `risk_size_assumption` and `notional`. Store such records only in their EXISTING immutable research owner, **not** this registry. No user MetaMask address/holdings or private wallets in public. Missing source-clock, price, allowed route, slippage, execution tax, sellability, funds or due outcome => UNKNOWN / CENSORED, never assume fill or mark zero profit.

At maturity compute separately for the right cohorts:
- **Compass:** warning lead time, true/false SELL, false/missed distribution, downside avoided, upside lost, calibration, regime/asset/horizon, decision delivery.
- **Paper trading:** attempted/blocked/rejected trades, cash vs hold, realized-executable exit proxies, total slippage/spread/fees/gas/funding, maximum adverse excursion, capacity, missed trades, drawdown and capital-at-risk. First trade eligibility and counterfactual exit quote must predate later outcome and be independently captured.
- **Alpha Lab:** exact chain+CA, independent economic buyer flow (exclude router/proxy), wallet realized **all trade** outcomes, early entry vs second wave, missed right-tail winners, complete denominator.

These are **research fields requested from existing owners**, not newly built trading, scoring, event or source collectors. Actual observations must exist in their owner files before being counted.

## Cheap weekly supervisor decision rule

At most one bounded, non-overlapping improvement **proposal** per relevant owner/week after comparing new **source-validated** outcome and the prior accepted result:
- `NO_MATERIAL_NEW_EVIDENCE` => deterministic no-op; **zero GPT/Claude/Work/Codex/API spend** and no user notification.
- `NEW_VALIDATED_OUTCOME` or `NEW_FALSE_POSITIVE_OR_MISSED_WINNER` => deterministic hypothesis/counterfactual selection first.
- `CONFLICTED` / `SOURCE_STALE` / `NO_REVIEWED_WEEKLY_SNAPSHOT` => source repair / reviewer gate first, no interpretation or performance credit.
- Complex genuinely new ambiguity only => use the **existing** delegated assistant API lane if spare budget and the canonical cost/safepoint admits the exact single task. No new paid source or subscription; no nightly model brainstorming.
- New hypothesis/weight/threshold is proposal only; independent review, predefined matched controls, prospectively frozen holdout and genuine consumer proof are mandatory before any governed promotion.

## Trading boundary and optional future progression

1. **Now: RESEARCH_SHADOW.** Existing Compass/Alpha/Auto watchers feed immutable source/outcome claims; no account access.
2. **Later: PAPER_LIVE (not authorized by this PR).** Only when original data have actual first-seen, bid/ask/pool depth, executable buy **AND sell** route, fees/gas/tax, failure/abstention and matched negative controls, with monotonic global proposal count. Simulated order includes quantity, liquidity capacity, route and *hypothetical*, not executed, entry/exit; never mutate portfolio cash.
3. **After independently proven walk-forward incremental after-cost value:** an explicit separate live trading authorization by user and governed risk/security design is required, including order size, asset allowlist, per-trade and daily loss cap, no leverage by default, kill switch, monitoring, broker/exchange permission separation and testnet/dry-run readiness. There is **no current authority to grant this from a shadow finding, a weekly PASS, or a supervisor model inference**.

## Implementation and bill

- `scripts/research/shadow_cross_domain_weekly_v1.py`: 5 fixed public JSON input paths, SHA-256 fingerprints, type/contract/authority and UTC age checks, 3 tiny sanitized lane reviews; no network or external Python package.
- `scripts/research/shadow_registry_weekly.py`: attaches the optional `cross_domain_review` to the existing weekly immutable artifact; older weekly snapshots stay byte-for-byte valid and untouched. No new workflow schedule or direct-main publication.
- `scripts/framework_intelligence/framework_learning_supervisor.py`: reads only **current reviewed main** weekly snapshot and publishes advisory lane statuses in the existing supervisor packet; rejects stale/no review/authority breaches.
- Incremental external LLM calls: **0 per week**. Incremental provider queries and paid USD: **0**. GitHub Actions existing runner minutes remain a small nonzero infrastructure cost, not a claim of literally free cloud compute.

**Governance:** public safe only, zero notification/auto trade/portfolio authority, correct sample denominator/clock/sellability required, no source and wallet private leakage, exact-head CI and independent review, and a natural post-merge Monday source-to-consumer test. Current production stays unchanged until merge.
