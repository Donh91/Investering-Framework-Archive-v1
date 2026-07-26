# Tom Hougaard Research Package

**Dato:** 2026-07-26  
**Status:** SOURCE_NOTE / RESEARCH_ONLY  
**Område:** external trader method / payoff asymmetry / confirmation scaling  
**Primary folder:** `08_SOURCE_MATERIAL/external_methods/`  
**Related folders:** `06_RESEARCH_LAB/audit_summaries/`, `06_RESEARCH_LAB/forward_tests/`  
**Source class:** USER_SUPPLIED_CLAUDE_SUMMARY_PLUS_PUBLIC_SOURCE_QA

## Supplied material

The user supplied:

1. one social-media screenshot attributing a motivational trading clip to Tom Hougaard;
2. a Claude/Fable research summary dated 2026-07-26;
3. framework mappings labelled L1-L5 and row candidates R1-R3.

Screenshot identity:

```yaml
file_name: 7D92BB07-CEE3-4E5C-B1C2-DDEE340B9BAA.png
size_px: 1206x2622
size_bytes: 699860
sha256: e2ca6e43aa0362557a4a4430a116635ca56298e0ac783c82ff9655cd24c53a44
```

The screenshot is evidence of the repost and its caption only. It does not independently authenticate the speaker, original interview, trading record or performance claims.

## Public-source verification

### Profile and book

Verified through the publisher and the author's official site:

```text
Harriman House book page:
https://www.harriman-house.com/bestloserwins

Harriman House author profile:
https://www.harriman-house.com/authors/profile/tomhougaard/17660

Official author site:
https://tradertom.com/
```

Supported facts:

- `Best Loser Wins` was published by Harriman House on 2022-08-16;
- the publisher describes economics and finance study at two UK universities;
- the publisher describes employment at JPMorgan Chase and a later Chief Market Strategist role at a CFD broker;
- the official site identifies City Index as the broker role;
- the publisher and official site describe full-time self-directed trading since 2009;
- the publisher carries a Jack Schwager endorsement.

The publisher also repeats competition wins, the approximately GBP 25,000 to more than GBP 1 million claim and stakes up to GBP 3,500 per point. These remain:

```text
AUTHOR_OR_PUBLISHER_MARKETING_CLAIMS
NOT_INDEPENDENTLY_AUDITED_PERFORMANCE
```

They receive no framework evidentiary weight.

### Trading method

The author's official site supports the following broad method description:

- price action and mechanical entries rather than indicator dependence;
- breakout-style entries in selected strategies;
- explicit stop-loss use and swing-based stop placement;
- moving stops behind developing price structure;
- adding to winning positions;
- accepting stopped-out attempts and re-entering when the setup remains valid.

Relevant official pages:

```text
https://tradertom.com/articles/
https://tradertom.com/breakout-strategy-for-the-dax-and-dow-open/
https://tradertom.com/chapters-from-my-book-intro/
https://tradertom.com/disclaimer/
```

This verifies the conceptual method family, not its profitability or transferability to weekly crypto governance.

## FXCM empirical anchor

Claude reported:

```text
25,000 accounts
43 million trades
15 months
62 percent profitable trades
average winner 43 pips
average loser 83 pips
```

The broad conclusion is source-backed, but the compressed numbers mix different levels of aggregation.

The older FXCM study covered more than 43 million real client trades across 15 major currency pairs from 2014-03-01 through 2015-03-31. The study found that most pairs had more than 50 percent winning trades while average losing trades were materially larger than winners.

Pair-level examples preserved in the public study:

```text
EUR/USD:
winning-trade share approximately 61 percent
average winner approximately 48 pips
average loser approximately 83 pips

GBP/USD:
winning-trade share approximately 59 percent
average winner approximately 43 pips
average loser approximately 83 pips
```

Public source reproducing the original FXCM figures and methodology note:

```text
https://www.moneyshow.com/articles/currency-42927/
```

Current official FXCM guidance retains the same behavioural conclusion, cut losses and let profits run:

```text
https://www.fxcm.com/eu/trading-guides/traits-successful-traders/
```

Hougaard's own book chapter attributes the study to analyst David Rodriguez and states approximately 25,000 traders over 15 months:

```text
https://tradertom.com/chapters-from-my-book-intro/
```

Evidence classification:

```yaml
43_million_trade_dataset: SOURCE_BACKED
study_period_and_15_pair_scope: SOURCE_BACKED
more_than_half_of_trades_profitable: SOURCE_BACKED
43_vs_83_pips_as_universal_average: REJECTED_CONFLATION
43_vs_83_pips_as_GBPUSD_example: SUPPORTED
25_000_account_count: AUTHOR_ATTRIBUTED_SECONDARY
behavioural_payoff_asymmetry_conclusion: SUPPORTED_AS_BROKER_CLIENT_STYLIZED_FACT
transfer_to_crypto_weekly_governance: REQUIRES_FRAMEWORK_SPECIFIC_ROWS
```

## Claude supplied framework claims

The supplied summary proposes:

```text
L1: payoff asymmetry matters more than hit rate
L2: add-to-winners maps to confirmed deployment after unlock
L3: the framework is already strong at damage limitation but weaker at winner capture
L4: short-term price reading has low direct transfer, except confirmation discipline and possible sweep-versus-structural-breach taxonomy
L5: process and journalling are already institutionalised in the framework
```

Candidate actions supplied by Claude:

```text
R1: retrospectively annotate 14 M5 breach-day rows as SWEEP versus STRUCTURAL
R2: add captured-versus-foregone asymmetry fields
R3: pre-register a post-unlock deployment confirmation ladder if Stage-1 is ratified
```

These are recommendations only. Their governance disposition is recorded in the related shadow audit.

## Source boundary

```text
PROFILE: PARTIALLY VERIFIED
BOOK IDENTITY: VERIFIED
PERFORMANCE CLAIMS: UNVERIFIED
METHOD FAMILY: VERIFIED AT HIGH LEVEL
FXCM PAYOFF-ASYMMETRY LESSON: SUPPORTED WITH NUMERIC CORRECTION
INTRADAY METHOD TRANSFER: NOT ESTABLISHED
FRAMEWORK ACTION AUTHORITY: ZERO
```
