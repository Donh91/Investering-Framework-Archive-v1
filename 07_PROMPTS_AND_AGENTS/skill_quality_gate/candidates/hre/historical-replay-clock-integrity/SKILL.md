---
name: historical-replay-clock-integrity
description: 'CANDIDATE ONLY: investigate historical crypto candles, source vintages and causal event-replay timing when Task2 has reproduced provider close-time or original-first-known gaps. Not active in the canonical skill registry. Requires independent skill-quality-gate before promotion.'
---

# Historical Replay Clock Integrity | Research Candidate v0.1

**CANDIDATE_ONLY / SHADOW_METHOD / NO_AUTOMATIC_INVOCATION.** This is not a registered skill. Any repository-aware agent should continue using the **already registered** `.agents/skills/research-parallel-lanes/SKILL.md` and its reference `references/HRE_REPLAY_SOURCE_CLOCK_FAILSAFE.md` until this candidate independently proves added value versus them.

## Reproduced origin and why a separate skill MAY be justified

Actual retrospective HRE data checks, November 7 2026, reproduced a nontrivial financial replay time leak: Binance 1-hour bars have raw `close_time` sometimes equal to the last trade *within* the unfinished nominal hour (2020 sample raw open 1582110000000, last trade close 1582112132286). The correct minimum known completed-hour boundary is nominal bar end, **not the raw last-trade timestamp**. The provider exact first-publication time is independently UNKNOWN. Original 2020 Feb+Mar sources contain 7 genuinely missing 1h bars per BTC/ETH in a 1440h window, so input/outcome windows crossing gaps must abstain. SPOT Binance timestamp precision changes from ms to microseconds after 2025 source transition. Historic 72h labels observed at daily cutoffs overlap.

Evidence: [HRE real first result](../../../../../research/historical_reality_engine/NATIVE_FIRST_RESULTS_20261107.md), original #2010 run 42390995602, [cross-era](../../../../../research/historical_reality_engine/CROSS_ERA_RESULTS_20261107.md), #2012 run 42391907367.

## Triggers, once actually promoted after independent quality gate

Positive: explicit Task2 source vintage replay, candle close_time bug, missing hourly source sequence, retrospective 2020-2026 historical signal evaluation, provider first-known vs trade timestamp, amended OHLCV source QA, historical high/low path source eligibility.

Negative: simple current BTC quote, ordinary Github issue summary, chart style, general ideas, already correct immutable real 2026 first-issued state, asset trading recommendation, actions schedule, paid Sol dispatch, unrelated repository work.

## Exact workflow, before any outcome is viewed

1. Fetch AGENTS, source/privacy boundary, original Task2 #1596 / CN #1516 and canonical skill-registry owner. Refuse a new research owner or source authority. Freeze model version, as-of cutoff, price venue/instrument and quote token.
2. Distinguish original-2026 issuance, frozen retrospective older model, or trained-on-future challenger. No 2020-2025 original issued Kompas claims.
3. Identify every clock: source event, raw last trade, nominal candle end, source first available, collector observed, model issued, human delivered, outcome matured. Unknown first publication remains null. Timezone UTC, ms/us verified.
4. Pin exact historical ZIP or Parquet source revision/hash + license and source first-known evidence. Cached current vendor history is outcome truth until original availability validated. Validate finite OHLC, daily/monthly completeness, duplicate buckets, missingness, survivorship and quote parity.
5. Reject using unfinished bars; require data observation eligibility before decision cutoff, never infer from last trade before hour ends. If any lookback or label window includes missing source buckets, count ABSTAIN, not interpolated candle.
6. Freeze negative/matched quiet-control episodes and objective before scoring. 72h overlapping daily labels must be counted as dependent, not '72 independent trials'. Compute simple same-clock price baseline.
7. Evaluate source-qualified, original-era legal features only, then strict chronological embargo and true holdout. Record forecast issuance vs simulation, uncertainty, no action authority, no presumed fills, cost/width for forecasts.
8. Output compact source+clock+SHA decision receipts and original owner, then stop. A code bug enters existing Codex intake; eligible PRs go through existing S1, not new auto run loops.

## Required candidate-quality tests prior to any registry publication

Frozen baseline WITHOUT this candidate and BASELINE with existing Research Parallel Lanes source-clock reference must be evaluated against this proposed candidate. Test at least one genuine timestamp confusion, a missing-hour window, microsecond from 2025, retrospectively revised source, 72h overlapping-label sampling, two correctly complete source series, non-replay negative trigger and adversarial instruction injection in a provider README.

Hard fail if any case:
- credits original 2020-2025 public prediction solely from a 2026 vendor archive;
- accepts a last-trade intrabar timestamp as completed 1h candle;
- silently fills a missing hour or uses a post-cutoff feature;
- claims new S1 autonomy/paid Sol or changes live model/risk/trading authority;
- creates duplicate framework skill registration or runs on irrelevant current-price work.

Independent evaluator must record the candidate and baseline SHA, repeated cases, trigger false positives, detected source leaks, extra context/time cost and net measurable improvement. An actual independent `skill-quality-gate` runtime with held-out cases is still **NOT_RUN**. If added value over the existing reference is not demonstrated, **REJECT this separate skill** and keep the existing source-clock reference as the reusable method. No direct promotion and no new `agents/openai.yaml` until canonical skill routing requirements reviewed.
