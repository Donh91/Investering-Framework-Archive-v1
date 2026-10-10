# CoinGecko Crypto News -> existing News Intelligence Shadow, bounded pilot v1

**Created:** 2026-10-10
**Status:** CODE_CANDIDATE_IN_REVIEW / NO LIVE COINGECKO_PRODUCTION_ACCESS
**Authority:** RESEARCH_ONLY_NON_CANONICAL, discovery comparison only
**Owner:** existing News Intelligence & Situation Analysis Research Lab v1
**Parent:** NEWS_INTELLIGENCE_FORWARD_TEST_v1, frozen 2026-10-07
**No new engine, scheduler, score, Compass or CN authority.**

## Decision and access restrictions

The CoinGecko app includes a Market Overview AI summary. The exact displayed TLDR/market-summary text is NOT proven available through an API. CoinGecko separately documents /news and /insights endpoints. These must not be equated with the exact app summary. The official /news API is commercial Analyst-or-above access as of this review. The existing CoinGecko MCP sidecar is optional research access, not proof of licensed GitHub Actions news-feed access. Likewise an in-chat connector response is not GitHub Actions authorization. Do not scrape, extract unofficially, bypass plan restrictions, enable hidden billing or buy a subscription.

Existing owner references:
- 04_MARKET_LEARNING/news/2026-08-23__situation-room-daily-owner-contract-v1__research.md
- 04_MARKET_LEARNING/external_research/situation_room_shadow/README.md
- 04_MARKET_LEARNING/external_research/news_intelligence/2026-10-07__NEWS_INTELLIGENCE_SITUATION_ANALYSIS_RESEARCH_LAB_v1.md
- 04_MARKET_LEARNING/external_research/news_intelligence/NEWS_INTELLIGENCE_FORWARD_TEST_v1.md
- 07_PROMPTS_AND_AGENTS/github_agent/2026-08-11__coingecko-mcp-research-recovery-sidecar-v1__operational.md
- 00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md

## Offline proof-of-concept

Standalone reader: scripts/research/coingecko_news_shadow_probe.py

It compares an explicitly authorized point-in-time CoinGecko news snapshot with one Situation Room daily-owner record. It only calculates discovery coverage. It does not call CoinGecko, use an API key, run on a schedule, write to existing ledgers or issue trading recommendations.

Requires three inputs:
1. An authorized and properly licensed CoinGecko snapshot, stored in approved PRIVATE temporary storage. JSON object with provider="CoinGecko", source_status="PASS", captured_at_utc (UTC ISO timestamp), articles array of objects with title, url, posted_at, type="news", source_name. This is an input schema, not evidence that data was collected.
2. The exact same-window Situation Room daily-owner record, bound to the appropriate main SHA and source receipt. If data restrictions require, use an approved private copy.
3. An explicit UTC knowledge cutoff, before neither input may have been collected.

Example, using only private temporary paths:

    python scripts/research/coingecko_news_shadow_probe.py --coingecko-snapshot "$PRIVATE_TMP/coingecko_news.json" --situation-room-daily "$PRIVATE_TMP/situation_room_daily.json" --as-of-utc 2026-10-10T15:00:00Z
    python -m unittest tests.test_coingecko_news_shadow_probe -v

The CLI prints an aggregate, provider-value-free, noncanonical JSON summary. The optional --private-candidates-output emits titles/URLs/details, so its output MUST be restricted to a private temporary path that is not added to Git. Never commit the snapshot, candidates, provider news text or normalized licensed data in this public control repo. Never print detailed candidates in GitHub Actions logs.

## Interpretation

- SAME_URL_DISCOVERY_ONLY: a normalized publisher URL also appeared in Situation Room, NOT independent confirmation.
- POSSIBLE_HEADLINE_OVERLAP_UNVERIFIED: similar text, NOT fact or event-identity proof.
- NEW_DISCOVERY_UNVERIFIED: not seen in that daily comparison only, NOT a newly verified market catalyst.
- EMPTY_SNAPSHOT_NO_COVERAGE_INFERENCE: an empty snapshot does not mean no events occurred.
- BLOCKED_SOURCE_OR_SCHEMA_UNAVAILABLE: unavailable, invalid or future knowledge input, must fail closed.

Only accept news items, not educational guides. Exclude stale (>48 hours), future-dated, duplicate-URL and invalid records from eligible discovery candidates while reporting aggregate counts. Primary confirmation is performed only by the existing owner. Never promote from headline, same URL, AI summary or apparent consensus of two aggregators.

## Existing frozen forward test stays binding

NEWS_INTELLIGENCE_FORWARD_TEST_v1 retains baselines B0/B1/B2; horizons T+4H/T+24H/T+3D/T+7D; immutable T0 rows; event-family dedupe; category quotas; 50 prospective events; falsification, confidence calibration and kill criteria. CoinGecko is merely a candidate *discovery input* within that same test. This implementation earns ZERO prospective-case credit and cannot create verified NEWS EVIDENCE CARD objects.

Evaluate incremental verified material-event coverage, time-to-verification, independently confirmed missed events and cost/failures compared to the existing Situation Room source. A source URL from CoinGecko that Situation Room also carried is NOT an independent source. Source failure is UNKNOWN, not a clean NO_EVENT.

## Deferred access and activation gates

1. Confirm actual /news and /insights entitlements and whether the exact Market Overview TLDR is licensed through any official endpoint. No new subscription or cost without separate approval.
2. Confirm legally allowed ingest, metadata retention, use and redistribution. Otherwise abandon provider-data storage.
3. If authorized, place credentials only in GitHub Actions Secrets or another approved credential store.
4. Freeze point-in-time coverage semantics, freshness, hashes, license-scoped storage and private-plane receipt binding.
5. Reuse existing Situation Room verification, News Evidence Card, Director and ledger, no parallel automation or market-model owner.
6. Pass offline tests, controlled optional live smoke test and (if separately approved) three natural successful source captures plus consumer readback and independent review before scheduling.
7. If no additional verified-event decision/context value versus existing baseline, kill or simplify the provider addition.

**Current outcome: code + synthetic tests + documentation proposed in isolated PR only. No live feed, no schedule, no site or Compass impact.**
