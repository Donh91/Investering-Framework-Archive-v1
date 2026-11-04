# NEWS INTELLIGENCE P0 | SOURCE-TO-DECISION RECOVERY, 2026-11-04

**Status:** IMPLEMENTATION_CANDIDATE_IN_PR, NOT MERGED, NOT PRODUCTION_VERIFIED.  
**Main issue:** [#1888](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1888)  
**Existing owner:** [#1563](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1563)  
**Research:** [#1760](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1760), [#1476](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1476)  
**Supervisor:** [#1156](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156)  
**Authority:** RESEARCH_ONLY_NON_CANONICAL. Never silently change market state, forecast, thresholds, portfolio actions, trading permissions, or retroactively create forecast signals.

## Verified prior-state defects (Nov 4, 2026)
- Four November Situation Room source rows (Nov 1–4) all had 0 verified events and each was DEGRADED with one unverified discovery; the Nov 4 row reported primary landing-fetch 6/6 PASS. This does NOT show complete market-news coverage.
- 2 verified events in current Situation Room EVENT_LEDGER.jsonl. One frozen NEWSFT row, despite a preregistered minimum of 50 cases. This is a source-limited count, not a global count of world events.
- Existing candidate_links() uses a lexical pre-article gate; no election/midterm/congress vocabulary. Earlier source date filter admitted same UTC date only.
- Prior FetchResult timestamp was request-start, while offline CoinGecko research PIT comparators require retrieval_end_utc. Historical missing completion clocks stay UNKNOWN.
- Producer is currently a daily Situation Room discoverer + six regulatory/macro official agency pages; Daily Director Shadow consumes source-bound research context, and Official Compass does NOT confer news independent action authority.
- Nov 3 US midterm outcome is a RETROSPECTIVE_MISS_CONTROL only. Do not create an as-if Nov 3 prospective news event.

## This PR's bounded change, no new source/provider/network/policy
1. Add specific US-election phrases to existing discovery vocabulary and noncanonical election context taxonomy; avoid generic 'vote' or 'house' words that create false matches.
2. Permit yesterday's UTC publications in daily primary discovery **only** when timestamp precise; preserve original event time, mark DATE_ONLY prior-day ineligible. This is a bounded one-calendar-day lookup, not proof that yesterday's knowledge was available yesterday.
3. New FetchResult receipt includes response-completion timestamp, while existing fetched_at_utc remains request start; old/mocked observations explicitly keep retrieval_end_utc=null. No historical receipt rewrite or artificial PIT promotion.
4. Add deterministic tests of the actual lexical miss, irrelevant headline, dated boundary, prior-day primary event and completion clock.

**Limits of this PR:** It does not add actual election-results providers, prove event recall, repair entire review queue, deliver live official news cards, register a 50-row prospective outcome stream, create a paid feed, or launch Sol. Those are open gates on issue #1888.

## Candidate source matrix for Phase G1 after a license and operational review

| Family | Candidate | Role & permission | Coverage/caveat |
|---|---|---|---|
| Monetary policy | [Federal Reserve RSS](https://www.federalreserve.gov/feeds/feeds.htm) | Official primary, public feeds | Decisions and communications; not election results |
| Macro labor/inflation | [BLS RSS](https://www.bls.gov/feed/) | Official primary, public feeds | Employment/CPI/PPI, subject to release embargo/time clocks |
| SEC filings/market regulation | [SEC RSS](https://www.sec.gov/about/rss-feeds) | Official primary, public feeds | Verify actual filing/order/action, not just headline |
| Treasury liquidity | [TreasuryDirect RSS](https://www.treasurydirect.gov/rss/) | Official primary, public feeds | Auctions, offering/results; other Treasury releases remain separately sourced |
| Derivatives enforcement | [CFTC updates](https://www.cftc.gov/RSS/index.htm) | Official HTML/press release | CFTC reports RSS temporarily disabled as of Oct 2026, do not assume feeds are active |
| US elections | [State/local election offices](https://www.fec.gov/introduction-campaign-finance/election-results-and-voting-information/) | Government primary for official/certified results | FEC explicitly does NOT administer/validate election results; certification can lag |
| US election race calls | [AP Elections API](https://developer.ap.org/ap-elections-api/) | Licensed data, ACCESS_UNVERIFIED | AP race calls are independent media calls, not state certification |
| Broad global discovery | [GDELT](https://docs.gdeltcloud.com/API_DOCUMENTATION_GUIDE) | Discovery-only; entitlement/terms to verify | News grouping can support recall, never primary verification |
| Crypto publisher discovery | [CoinGecko News API](https://www.coingecko.com/en/api/news) | Analyst+; production entitlement UNVERIFIED | Existing offline code #1567 does not grant data access |
| Crypto publisher discovery | [CryptoPanic API](https://cryptopanic.com/developers/api/) | Key+plan, ACCESS_UNVERIFIED | 403/429 limits, source and redistribution rights; never same-article duplicates as corroboration |
| Exchange outages | [Coinbase Status API](https://status.coinbase.com/api) | Official machine-readable status | Useful for service incidents, NOT independent proof of hack/custody loss |
| Meme token context | [DEX Screener API](https://docs.dexscreener.com/api/reference) | Market discovery, check terms/rate limit | Boosts/paid attention ≠ verified news, organic demand or alpha |
| Microcap on-chain | [GeckoTerminal public API](https://support.coingecko.com/articles/6867086195-does-geckoterminal-have-an-api) | Public beta market data (documented free 30/min cap) | Spot/DEX context, not source verification or ticker-identity proof |

**Selection rule:** Choose legally retrievable, reliable, timestamped first-party sources first. Add independent publisher discovery only when incremental event recall is actually measured; no new subscription or scraping bypass.

## Follow-up repair and scientific acceptance (existing #1888)
- G0: source-family coverage and first-known/retrieval completion fingerprint. Parser health distinct from HTTP 200.
- G1: alternate official sources, bounded polling/cadence, material-event miss census, positive and negative elections; no all-news zero conclusion from six landing pages.
- G2: fact/adjudication closure, source-independent family clustering, versioned corrections, anti-prompt-injection and independent verification.
- G3: event -> Daily Director Shadow -> read-only official Kompas/Site factual explanation, with consumer readback. News may *contextualize* existing action, not overrule it.
- G4: frozen B0/B1/B2 on N≥50 prospectively admitted events, 4h/24h/3d/7d outcomes, baseline and cost-sensitive falsification; 2026 midterm replay is retrospective only.
- G5: Alpha Lab social/narrative event overlay keyed by verified chain+token contract; test whether news provides actual incremental false-positive reduction, not social virality.
- G6: existing S1 must track original issue #1888 until actual code merged and natural production/consumer receipts checked.

## Regression inventory
NI1 lexical positive/irrelevant negative, NI2 late-night UTC timestamp, NI3 DATE_ONLY prior-day rejection, NI4 older than one date rejection, NI5 request-start vs completion, NI6 false VERIFIED from uverified Tether, NI7 family dedup, NI8 source coverage transport != semantic, NI9 missed event census, NI10 no duplicate paid review, NI11 no canonical/trading change.

## Scientific/API mission boundary
Existing Research Lab Sol dispatcher #1476 supports `RESEARCH_LAB_SOL_ANALYSIS` = `gpt-6.1-sol`, High. The active mission slot is still held by `TASK2-PIT-P0-SOL61-20261019-002`, which has a historical completed paid receipt. **Do not issue a new trigger until exact current main releases the old slot, adds a frozen News Intelligence packet, marks exactly one ACTIVE_RELEASED and checks the previous actual receipt.** Then an issue comment by GitHub OWNER on #1476 with `[RESEARCH_LAB_SOL] mission=<WHITELISTED_MISSION>` activates the existing GitHub Actions path. A comment from an App identity that is not OWNER will NOT activate the workflow. Report actual run/receipt or blocker; a queued comment is not payment evidence.

**No independent verified news edge or Kompas predictive lift is currently demonstrated.**
