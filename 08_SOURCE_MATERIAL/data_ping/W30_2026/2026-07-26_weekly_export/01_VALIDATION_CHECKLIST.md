# W30 weekly export — validation checklist

```yaml
manifest_entries_checked: 29
manifest_byte_counts_match: true
manifest_sha256_match: true
zip_inventory_count: 30
external_xlsx_matches_embedded_xlsx: true
btc_rows: 166
eth_rows: 166
settled_rows_each: 165
partial_rows_each: 1
timestamp_duplicates: 0
timestamp_gaps: 0
raw_ohlc_mismatches: 0
raw_settled_flag_mismatches: 0
weekly_summary_mismatches: 0
etf_total_mismatches: 0
workbook_formula_errors: 0
```

## Audit boundary

The checklist validates source structure and deterministic calculations. It does not validate the economic truth of every upstream provider observation and does not convert an incomplete Sunday into a final weekly close.
