# MAEVE EVIDENCE REGISTER

Purpose: track what is actually supported, where it came from, and how strongly it may be used in later reverse-engineering work.

## Evidence classes

- `PRIMARY_PUBLIC` - original CFGI/MAEVE source or first-party documentation.
- `SECONDARY_CONTEMPORARY` - contemporary third-party article, mirror or preserved discussion.
- `SECONDARY_TECHNICAL` - technically detailed reconstruction/summary whose primary provenance is incomplete.
- `CLAIM_ONLY` - promotional/community claim without row-level evidence.

---

## MAEVE-EV-0001 - Public launch / roadmap

Source: https://pastebin.com/zx6Y4wT4
Date: 2025-01-09
Class: PRIMARY_PUBLIC

Supported:
- M.A.E.V.E = Markets and Emotion Valuation Engine.
- Powered by CFGI.io.
- Public beta v1.00.
- Official X account identified as `CFGI_MAEVE`.
- Roadmap included risk-on improvements, GMDI integration and later live dashboard/user integration.

Does NOT support:
- exact decision rules;
- performance quality;
- exact private features.

---

## MAEVE-EV-0002 - Detailed architecture reconstruction

Source: https://studylib.net/doc/28348344/maeve-trading-strategy---maeve-trading-strategy--1---2-
Class: SECONDARY_TECHNICAL

Supported only as a research lead unless primary material is recovered.

Reported concepts:
- three aligned data points for entry/exit in earlier system;
- coin/timeframe-specific triggers;
- ten public CFGI inputs plus four private inputs;
- DCA;
- later rolling Market Range Evaluator;
- dynamic Optimal Data Trigger selection;
- compatibility/redundancy checks;
- global + asset GMDI context;
- portfolio-aware position sizing;
- target, stop and time-loss;
- single-condition exit and possible reversal.

Risk:
The page appears to contain a derived summary/conversation rather than authenticated CFGI source documentation. Do not label these exact mechanics as verified proprietary architecture.

---

## MAEVE-EV-0003 - Mid-2025 performance promotion

Source: https://medium.com/@cplguru606/cfgi-m-a-e-v-e-real-trades-real-revenue-real-utility-42d54ef91553
Date: 2025-07-01 era
Class: SECONDARY_CONTEMPORARY / PROMOTIONAL

Reported:
- 660+ live trades;
- 91.3% win rate;
- 4.1% average monthly portfolio growth;
- 21.8% YTD;
- claim that trades were posted live and history was available on CFGI.

Use:
Performance checkpoint / source-discovery lead only.

Do not treat as audited performance.

---

## MAEVE-EV-0004 - Official September 2025 performance checkpoint

Source: https://cfgi.io/articles/how-maeve-ai-trading-maximizes-crypto-profits
Date: 2025-09-10
Class: PRIMARY_PUBLIC, PERFORMANCE CLAIM

Reported:
- 84.85% win rate;
- 1,427 trades;
- 1.20% monthly returns;
- approximately 25% over eight months;
- V2 added leverage trading.

Research importance:
The lower win rate relative to earlier 90%+ claims suggests performance/version/regime drift worth reconstructing rather than assuming one stable strategy.

Still not audited unless row-level trade history independently reproduces it.

---

## MAEVE-EV-0005 - AI dashboard / public-history claim

Sources:
- https://mfgi.io/ai-trading
- archived search/mirror references to `cfgi.io/ai-dashboard`
Class: PRIMARY/SECONDARY MIXED

Reported:
- public real-time dashboard;
- full trading history;
- 91.30% headline win rate during one historical snapshot.

Research priority:
Locate/capture historical dashboard payloads, static HTML, API calls or cached page data if still publicly retrievable.

---

## MAEVE-EV-0006 - Multi-timeframe CFGI relationship

Sources:
- CFGI press releases and current developer documentation.
Class: PRIMARY_PUBLIC

Supported:
- MAEVE was described as applying CFGI's multi-timeframe sentiment framework.
- CFGI exposes historical/public API data and algorithmic components.

Research implication:
Reconstructing public CFGI state around MAEVE timestamps is technically plausible if historical access and licensing permit.

---

## MAEVE-EV-0007 - X public-forward history

Source target: https://x.com/CFGI_MAEVE
Class: PRIMARY_PUBLIC TARGET
Status: NOT YET FULLY RECOVERED

What is known:
Multiple contemporary references claim individual trades were posted live on the MAEVE X account.

What is NOT yet known:
- completeness of recoverable tweet history;
- deleted posts;
- exact timestamp-to-fill convention;
- whether every DCA/partial exit was posted;
- whether X posts were synchronous or delayed.

No completeness claim is permitted until reconciled against an independent trade count/checkpoint.

---

## MAEVE-EV-0008 - Third-party X mirrors/checkpoints

Examples include TwStalker-preserved posts/comments citing roughly:
- 500+ trades at approximately 94-95% win rate;
- 650+ trades at approximately 91.3% win rate.

Class: SECONDARY_CONTEMPORARY

Use:
- establish approximate checkpoint chronology;
- discover original account/status URLs;
- cross-check missing periods.

Do not use mirror claims as trade rows unless original trade text/timestamp is preserved.

---

## Open evidence hunts

1. Original X trade posts from `CFGI_MAEVE`.
2. Search-engine cached tweet text/status IDs.
3. Third-party X mirrors with timestamp + full post body.
4. Old `cfgi.io/ai-dashboard` HTML/API/network endpoints.
5. GitBook pages or historical docs describing MAEVE rules.
6. Telegram public MAEVE trade channel/log if one existed.
7. Version-change announcements to define v1/v2 epochs.
8. Screenshots/images that contain historical trade tables.
9. Exact meaning of `win`, breakeven and DCA trade counting.
10. Primary source for MRE/ODT technical description.
