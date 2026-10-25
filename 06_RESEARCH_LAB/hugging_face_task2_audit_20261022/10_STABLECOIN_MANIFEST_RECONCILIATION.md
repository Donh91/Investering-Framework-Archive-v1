# HF-013 | Reproducible stablecoin manifest consistency audit
**Run:** 2026-10-22, live authenticated Hugging Face connector, `Chainticks/stablecoin-flows/_manifest.json`. **Research class:** T0+MANIFEST, NOT T1 data rows, NOT R1 point-in-time source acceptance, no trading inference. **Computation:** Deterministic local JS aggregation over the published JSON manifest returned by the connected Hugging Face file reader; no Parquet data was downloaded, no model inference or billed cloud Jobs were run.

## Observed machine results, derived from creator-owned manifest
| Check | Finding | Interpretation |
| --- | --- | --- |
| Manifest generation UTC | `2026-10-22T03:59:12.269018+00:00` | Snapshot vintage, **not** proof of continuous collection later on Oct 22 |
| Partition calendar span | 2026-05-09 through 2026-10-22 | 167 daily keys / `flows/date=YYYY-MM-DD/` |
| Calendar date continuity | All consecutive calendar days present | Missing-date test PASS for *manifest only* |
| Aggregate `row_counts` | **494,016** | The publisher manifest's own total, comparable to Hub's approximate 494K; **not** a verified Parquet record recount |
| First day | May 9, first event 23:47:59Z, last 23:57:47Z | Intentionally partial date is plausible start of series |
| Last day | Oct 22, 00:00:35Z through 03:54:35Z, 794 rows | Partial final day as of 03:59Z manifest generation; DO NOT use in full-day aggregate |
| **Inner day May 14** | first 00:01:11Z, last **03:53:35Z**, 276 rows | **3.87 h observed event timestamp span**; major suspicious coverage anomaly |
| Consecutive partition gap | May 14 03:53:35Z through May 15 00:22:47Z | **20.487 hours** without events in publisher manifest; *potential outage / missing source events*, not proven collector failure without independent logs |
| Internal days with event span <20h | Only **2026-05-14** | Based solely on first/last event timestamps; does not establish all intra-day gaps absent |

## How to reproduce from exact source metadata
Fetch `hf://datasets/Chainticks/stablecoin-flows/_manifest.json` with authenticated HF filesystem `cat`; parse JSON; assert keys `files`, `row_counts`, `time_ranges`, `generated_at`; sort `flows/YYYY-MM-DD` keys by UTC calendar date; verify `date[i] - date[i-1] = 1 day`; sum `row_counts`; convert each `time_ranges[key].start/end` to UTC instants, measure span and next partition start minus previous end; exclude boundary dates from full-day checks. Refetch/pin exact HF repo SHA before reporting any further repeated result. The calculations above were performed on the returned metadata in this audit turn, not on a cryptographically pinned immutable dataset revision.

## Data-quality judgement and red-team challenge
1. `LATEST_DATE.txt=2026-10-22` is **not** a health proof: it does not guarantee last day's completeness or recent last event close at query time. We have actual manifest vintage and end-of-available-events, which must be used.
2. An all-dates-present check passes while **event coverage can still fail**. This is a distinct and useful negative control for Task 2 collectors and stablecoin source QA.
3. Zero events over 20.487 h could reflect missing collection, publication gaps, upstream filtering or genuinely absent eligible events. Do **not** assert an outage as proven cause. Cross-check chain event logs and per-partition content or provider collection receipts.
4. Stablecoin mint/burn/bridge activity is neither exchange inflow nor economically deployable capital by default. Attribution and event identity must be proven before linking to BTC/ETH or altcoin regime transitions.

## Proposed next authorized owner-side test
- Pin exact HF revision and 1–2 small Parquet partitions, for May 13–15.
- Check row counts against manifest, `source_kind`, event key uniqueness (chain_id + tx hash + log index if present), monotonic block/UTC clock, distribution of time gaps, class labels of mint/burn/bridge and cross-chain identity.
- Compare an independent public chain-source only if licensed and no restricted market values enter the public repository; return `SOURCE_GAP_CONFIRMED`, `NATURAL_ZERO_EVENTS`, `FILTERED_POPULATION` or `INCONCLUSIVE`.
- Before Task 2 R1, source first-known vs original framework signal decision time remains unavailable. Preserve `UNKNOWN` until attested.

**Verdict:** `HF-013 = MANIFEST_METADATA_RECONCILED_WITH_MAJOR_INNER_GAP_FLAG`, not continuous stablecoin deployment evidence. No live signal/data authority, no source-timing proof, no market skill.
