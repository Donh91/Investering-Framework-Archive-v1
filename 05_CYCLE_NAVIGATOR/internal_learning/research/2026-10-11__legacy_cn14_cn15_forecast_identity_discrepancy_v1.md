# Historical CN #14 → #15 forecast-identity discrepancy (bounded source audit)
Date: 2026-10-11
Status: RESEARCH_ONLY / PUBLIC_SOURCE_ONLY / SOURCE_MISMATCH_REPRODUCED / NO_EDGE_PROMOTION
Existing owners: #209 historical Market Anticipation; Cycle Navigator/M3 precision; current audit owner #1565. No new queue.

## Critical discovery
The archived CN #14, labelled forecast June 29–July 5, 2026, publishes BTC **62.8–67.2K** and ETH **1.67–1.84K**. The next archived CN #15's retrospective WEEKLY PRECISION SCORE — #14 instead attributes BTC **58.5–64.2K**, reports realized BTC **57.8–63.4K**, and gives an **82% BTC range score**. ETH attribution remains 1.67–1.84K. Both BTC intervals cannot be the same frozen original forecast for that week. A separate eligible pre-outcome revision might exist, but was not established in the checked public archive. This is a material SOURCE-VERSION mismatch, NOT proof of intentional manipulation.

The previous merged legacy source audit already found that CN #14 repeated CN #13's weekly and intraday forecast maps following the earlier downside miss. This note adds a **different**, independently checked following-recap mismatch; it does not rewrite or duplicate that audit.

## Pinned sources (public Git blob identities)
| Evidence | Path under Donh91/Investering-Framework-Archive-v1 main | Git blob SHA |
|---|---|---|
| CN11 | canonical-project-archive/06_CYCLE_NAVIGATOR/published-x-posts/CN_011_PUBLISHED_X_POST_2026-06-08.md | 85e1e8a2986c06f32fcae36d616b949271f59227 |
| CN12 | canonical-project-archive/06_CYCLE_NAVIGATOR/published-x-posts/CN_012_PUBLISHED_X_POST_2026-06-15.md | d04415e3f655cc863de4ca4932c71bfb207a961f |
| CN13 | canonical-project-archive/06_CYCLE_NAVIGATOR/published-x-posts/CN_013_PUBLISHED_X_POST_2026-06-22.md | 84b067e5fd7827ba6d4e81af99e841eff43f1a88 |
| **CN14** | canonical-project-archive/06_CYCLE_NAVIGATOR/published-x-posts/CN_014_PUBLISHED_X_POST_2026-06-29.md | d2a8e7fc5e693cc019a4eb6966fd589d7b44a8c5 |
| **CN15** | canonical-project-archive/06_CYCLE_NAVIGATOR/published-x-posts/CN_015_PUBLISHED_X_POST_2026-07-06.md | 541f40cbf0f40e3819457c2a30779877ddca5a84 |
| MM 29 June | canonical-project-archive/07_MASTER_MONDAY/runs/MM_2026-06-29.md | 28e303146aeff1499ec93c2e59867e0b8bbfcec9 |
| Earlier legacy audit | 05_CYCLE_NAVIGATOR/internal_learning/research/2026-10-10__legacy_to_automated_kompas_cross_archive_evidence_audit_v1.md | ddce14c3a325b9615ea518a2b0af9695e16f30e8 |
| 12 July shadow chronology critique | 04_MARKET_LEARNING/shadow_sources/2026-07-12__grok-execution-quality-and-framework-evolution-audits__shadow-assessment.md | 4b216474c352982dd193a64193278eb957f57b14 |
| 10 July FRLP numbering correction | 00_ARCHIVE_CONTROL/2026-07-10__correction-frlp-first-forward-row-cn15__canonical.md | d86cee3092f17be98dbe4bfbe696b1db6439dc70 |

MM 2026-06-29 explicitly states RECONSTRUCTED_FROM_ARCHIVE and agrees with CN #14 BTC 62.8–67.2K; it is not an independent pre-outcome original Master Monday freeze. The published-text archive records for CN #14/#15 were imported on July 5/6, respectively; these GitHub import dates are NOT verified original X issue timestamps and must not be treated as proof that the forecast was fixed before the result.

## Four consecutive pairs: forecast in previous post versus recap in following post
| Pair | BTC forecast identity | ETH forecast identity |
|---|---|---|
| CN11 → CN12 | MATCH 61–69K | MATCH 1.55–1.90K |
| CN12 → CN13 | MATCH 63–71K | MATCH 1.65–1.95K |
| CN13 → CN14 | MATCH 62.8–67.2K | MATCH 1.67–1.84K |
| **CN14 → CN15** | **FAIL 62.8–67.2K versus 58.5–64.2K** | MATCH 1.67–1.84K |

Scope is exactly these four successive comparisons, not every historical CN issue and not original-X timestamp verification.

## Material impact — descriptive interval geometry only
Using CN15's reported rounded actual BTC interval **57.8–63.4K**:
- If the original CN14 forecast is **62.8–67.2K**, the intersection is 0.6K; Jaccard overlap = 0.6 / 9.4 = **6.38%**, actual-span containment 0.6 / 5.6 = **10.71%**.
- If the CN15 recap substitutes **58.5–64.2K**, the intersection is 4.9K; Jaccard overlap = 4.9 / 6.4 = **76.56%**, actual-span containment 4.9 / 5.6 = **87.50%**.

These percentages are descriptive geometry, **NOT** a replacement for the original historical 82% published score or a reproduction of its scoring formula. Actual market prices and source data vintage were not independently revalidated by this spot comparison. The arithmetic establishes that source identity materially influences any claimed skill.

## Independent chronology/issue-identity warning
The July 6 archived CN15 describes a user-published public post, while the July 10 FRLP correction calls CN15 the first prospective FRLP row and the July 12 shadow critique refers to CN15 as a DRAFT targeted for July 13 and rejects Grok's 83% attribution. These may be **different artifact types/vintages/week mappings**, not automatically a contradiction proving fabricated history. Resolve by forecast week + artifact type + public issue + first available source time + exact hash, never by CN issue number alone. Modern public-series index already warns that machine/public issue numbers can differ; do not retrofit modern scoring-contract behavior onto legacy 2026.

## Existing-owner actions and gates
1. #209 / historical CN owner: search archived original X receipt/snapshot and contemporaneous forecast revisions for **CN14 June 29–July 5**. Admit a changed 58.5–64.2K forecast only if proven publicly/otherwise immutably fixed **before outcome time**, with explicit source version. Do not invent publication clocks.
2. If no eligible revision exists, record the CN15 claimed 82% as HISTORICAL_PUBLISHED_SCORE / NOT_ADMITTED_AS_SKILL_DUE_TO_SOURCE_MISMATCH in an **additive** reconciliation. Preserve the original CN14, CN15, Master Monday reconstruction, website historical displays and any frozen source score.
3. Recover CN6 and CN10 original texts where feasible: the existing PUBLISHED_X_POST_GAP_TRACKER_2026-07-05.md marks both missing. Do not use their successors' retrospective forecast claims as original source freezes.
4. Use a bounded source-identity check across all available archived pairs before interpreting legacy performance. Distinguish original publication, import, revision, evaluation, actual vintage, and whether eligible pre-outcome evidence exists.
5. Do NOT file a runtime bug/Codex candidate merely because old user-imported text conflicts. First reproduce an analogous defect in the current immutable score pipeline and use existing AGENTS.md §0.2 if proven. Prospective official scores, model weights, warning/SELL authority, trading and sealed holdouts remain untouched.
6. Research/governance: keep original June Shadow percentage/failure-rate claims and CN range scoring historical results separated from prospective evidence. No new mining before #1557 trial accounting.

## Disposition
- TEXT_SOURCE_PAIR_PARITY: FAIL_ONE_OF_FOUR_SAMPLED_PAIRS
- LEGACY_CN14_BTC_82_PCT_SCIENTIFIC_ADMISSION: WAIT_FOR_ORIGINAL_OR_REVISION
- ORIGINAL_X_PUBLICATION_TIME: UNVERIFIED
- MARKET_ACTUAL_VINTAGE: NOT_REPLAYED
- CURRENT_PRODUCTION_CN_DEFECT: NOT_ESTABLISHED
- NO_NEW_ENGINE / NO_TRADE_OR_PORTFOLIO_AUTHORITY

This is public-source text verification only. No private raw/provider values, wallet, restricted repository source identifiers or restricted data have been included.
