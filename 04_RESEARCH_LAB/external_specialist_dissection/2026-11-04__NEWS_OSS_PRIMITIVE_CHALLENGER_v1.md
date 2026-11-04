# NEWS OSS PRIMITIVE CHALLENGER v1
**Date:** 2026-11-04. **Status:** RESEARCH_ONLY / NOT PRODUCTION / NO AUTOMATIC PROMOTION.
**Parent:** Archive [#1888](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1888), original P0 release [PR #1889](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1889), research owner [#1512](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1512), Strategist #1157, S1 #1156, Alpha Lab [#218](https://github.com/Donh91/Meme-Alpha-Lab/issues/218).
**One bounded source/primitive evaluation.** No new scheduler, third-party bot, live signal owner, trading, secrets, paid feed, or retrospective official truth.

## Question and lowest-cost baseline
Can reused open-source IDEAS improve material-event recall, exact news-event grouping, verified independent-source counts and next-day Compass context compared against the already-existing Situation Room owner and Daily Director? Baseline is the six agency/regulatory webpages + one unverified discovery source, keyword-gated article links, URL-derived event IDs and current fail-closed Director bridge. Nov 3 election outcome is a retrospective missing-event control, not a claim that a real old forecast existed.

## 2026-11-04 pinned source scan and license gate
GitHub source commit hashes and repository license metadata are verified; model weights, data rights and publisher access are distinct. Every external source requires a fresh security and license check before installing or copying code.

| Rank | Repo and pinned source commit | License | Source-derived primitive | Decision |
|---|---|---|---|---|
| 1 | [AIHOT](https://github.com/KKKKhazix/AIHOT) cd424b0a513c7c8535b6f291b106a3086d6b75bf | MIT | packages/backend/src/events/group.ts and relate.ts: SAME_OCCURRENCE, SAME_STORY, UNRELATED, ROUNDUP; fact vs story, manual corrections protected, ambiguous merge independent model check | ADAPT_IDEA, not its Node/Postgres/paid-LLM pipeline |
| 2 | [Horizon](https://github.com/Thysrael/Horizon) d7406f738c711df82b8f060fa1d5e9999d36cca0 | MIT | src/orchestrator.py plus deduplication.py: source-specific failures, canonical URL collapse before topic-level dedup, same real-world event distinction | ADAPT_IDEA, not its new digest app or budget |
| 3 | [xnews](https://github.com/underloam/xnews) cff4044076a6ba8470ff0896de22d3e0c67c7817 | Apache-2.0 | provider policy/catalog and feed parsers for SEC, GDELT, OFAC, economics; source terms explicit | EVALUATE_ADAPTER only; Node24 ESM and very new repo |
| 4 | [Trafilatura](https://github.com/adbar/trafilatura) ba50901169a3d38e256034939cd1b66c203d2b43 | Apache-2.0 | robust article text and publication metadata extraction | TEST_AS_OPTIONAL_DEPENDENCY against existing HTML parser |
| 5 | [FinGPT](https://github.com/AI4Finance-Foundation/FinGPT) ac5c5443fbeeafad801e7a3c188e4f24cfaad4d8 | MIT (repo) | Financial sentiment versus quantitative expectation surprise are different measures; sentiment is not a market forecast | RESEARCH_BASELINE_ONLY, model weights/deps separately licensed |
| 6 | [Huginn](https://github.com/huginn/huginn) 62c9d80dc59d82c6757a46f1b68e2dd9a4939038 | MIT | agentic monitoring/transform recipes | REJECT_DEPLOYMENT: duplicate of GitHub Actions/owner/S1 |
| 7 | [RSSHub](https://github.com/DIYgod/RSSHub) 8f4fd435601c7f5048ce65284405f276f70fb918 | AGPL-3.0 | feed-route patterns | IDEA_ONLY: no direct code reuse without license and network-serving review |
| 8 | [Scrapy](https://github.com/scrapy/scrapy) | BSD-3-Clause | crawlers, politeness, retry | DEFER: increases broad scraping and cost before proving source coverage |
| 9 | [FinBERT](https://github.com/ProsusAI/finBERT) 3b4bfed383a8bb6b013db2f1ce9c766ff5100d24 | Apache-2.0 CODE ONLY | finance sentiment label baseline | NO AUTOMATIC WEIGHTS: separately licensed CC BY-NC-SA 4.0 weights and third-party datasets |
| 10 | [cryptocurrency.cv](https://github.com/nirholas/cryptocurrency.cv) 86d291a257f249e298988c80b0804a24181812b1 | NOASSERTION (source-available) | claimed free many-source crypto news/API | NOT-OSS-COPY; README says all-rights-reserved, validate live source/terms independently before using any API |

## Five high-value extractable primitives

1. **Transport is not event coverage** (Horizon/xnews). Keep per-provider fetch/parsing health, input freshness, source universe coverage and material-event miss rate as distinct metrics. Use the existing source owner rather than spawning a new watcher.
2. **Article identity differs from occurrence identity** (Horizon/AIHOT). Normalize only known URL tracking params, compare actor+action+target+event-time, distinguish one event from direct developments, unrelated reports and multi-event roundups. Never transitive-merge a whole story through a shared topical article. Preserve correction/version history.
3. **Independence is not URL count** (AIHOT). A syndicated wire distributed to 20 publisher domains is one reporting origin. Independently publish factual source receipts with a first-known and response-completed time. A duplicated source does not increase confidence; social copy-paste is not verification.
4. **Text polarity is not surprise or market causality** (FinGPT). Separate favourable phrasing from actual-vs-expected data release surprise, transmission and competing macro/crypto shocks. Sentiment F1 does not demonstrate better BTC 12h/72h/168h directional edge.
5. **Falsifiable event-learning tournament**. Existing NEWSFT B0 headline polarity, B1 verified fact+reaction and B2 structured evidence must be frozen at T0 with full event/miss denominator, T+4h/24h/3d/7d matured outcomes, matched no-news/price baseline and kill rules. N>=50 prospectively documented, not cherry-picked.

## Bounded actual implementation in this research PR

Pure standard-library research module scripts/research/news_oss_event_challenger.py plus 18 negative/positive fixtures in tests/research/test_news_oss_event_challenger.py.

- Emits SAME_ARTICLE, POSSIBLE_SAME_OCCURRENCE, RELATED_DEVELOPMENT, DIFFERENT_EVENT or REVIEW_REQUIRED, never merges the original ledger.
- Normalizes URLs without erasing meaningful query IDs; unknown actors, multi-event roundups, date-only timestamps and time collisions fail to auto-merge.
- Reports per-origin independent counts only when source role, already-verified status and complete retrieval/first-known clocks precede cutoff. Publisher-group strings are *assumed input provenance*, not new proof of publisher ownership; verification stays with the original owner.
- Has no network, model calls, secret reads, scheduler, persistence, official forecast, portfolio permissions or source subscriptions.
- It is deliberately conservative: same actor/action/target within 1 hour is only POSSIBLE, not an automatic factual event merge. Similarity recall and entity aliases need separate measured validation.

## Implementation gate sequence, existing owners only

**NI-OSS-0** Keep P0 PR #1889 independent; ensure qualified merge and real producer-to-Director readback. This P1 research code must not delay P0.

**NI-OSS-1** Research Lab #1512 performs documented overlap check against existing merged CoinGecko offline comparator #1567, News Intelligence #1563, Decisions API pilot #1760 and Alpha #218, then routes one accepted material family through Strategist #1157. No parallel queue.

**NI-OSS-2** Offline head-to-head: label same-event, subsequent development, separate same-asset news, incident rumours, correction, syndication, composite roundups and exact source clocks. Compare existing URL-only method vs conservative candidate on FPR/FNR with abstention and latency. Reject if no measurable benefit or too many ambiguous reviews.

**NI-OSS-3** If method wins, owner #1888 may implement a bounded native integration into the EXISTING Situation Room producer and Director, with first-party source rights, dedup before events, versioned corrections, source-publisher proof and complete PIT receipts. No historical rewrites.

**NI-OSS-4** Reuse approved official government/regulatory feeds and vetted discovery (e.g. GDELT) only after terms, rate and actual semantic recall tests. More keyword matches on existing six pages cannot magically produce unmonitored election results.

**NI-OSS-5** Alpha Lab #218 consumes public-safe event metadata keyed by chain_id + token contract; isolate viral amplification/boosts from verified protocol/news facts. Test benefit over same-clock onchain/market-only candidate baseline.

**NI-OSS-6** S1 #1156 logs exact original issue + PR outcome + production readback; research dispositions from #1512/#1157 must end in accepted test, rejected/no-go, or precise triggered blocker. No infinite HOLD. Never call an independent API review a formal approval or silently increase budget.

## Explicit non-claims and stop conditions
- The new code does not collect real news, enable fresh RSS, or improve Compass today; this is a reproducible challenger, not a production integration.
- If source first-known is missing, keep PIT_UNKNOWN. Date-only publication is not an intraday publication time.
- If publishers are not authenticated as independent, keep confidence UNKNOWN.
- If expected news decision benefit does not survive forward tests, use simpler B1 or existing baseline.
- Licenses of copied code, upstream model weights, original articles and hosted APIs must each be cleared separately. **No third-party application wholesale cloned or running.**
