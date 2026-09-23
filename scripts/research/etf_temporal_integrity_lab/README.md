# ETF temporal integrity lab (research only)

This lab reads the owner outputs and writes only to `$ETF_LAB_WORK`, which defaults to `/tmp/etf_temporal_integrity_lab`. It changes no owner, workflow, consumer or pack byte.

## Run order

Run from this directory with the repository root as `ETF_LAB_REPO` (the default).

```
python capture_live.py        # live Farside read (owner client path)
python live_schema_lab.py     # §2 schema reproduction + fixture matrix
python vintage_ledger.py      # §3 raw ledger + capture attempts
python revisions.py           # §3/§4 session chains + revision events
python policies.py            # §5 policies A-F (latest and pre-backfill references)
python rt_policies.py         # §6 E1X right truncation per policy (a few minutes)
python v1_1_revalidation.py   # §8 (#1212 only)
python consumer_audit.py      # §1/§9
python summaries.py           # deliverable JSONs + final ledger + F04 contamination
```

## Results

The results of the 2026-09-23 run are in `research/etf_temporal_integrity/2026-09-23/`.
