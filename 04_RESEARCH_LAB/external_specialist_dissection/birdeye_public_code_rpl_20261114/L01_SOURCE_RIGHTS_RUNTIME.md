# L01 | Source rights, API cost, version and runtime integrity
Question: Which openly documented Birdeye methods can be examined/reimplemented from lawful first-party evidence without provider-data lock-in?
Original owner Archive #1512, source contract L01 Research Precision.
Frozen source: 2dcbd14cad32bcbb57f8d0c0c766d8c496597413; source docs README.md, LICENSE, docs/workflows/skill-support.md, src/runner.ts, src/ledger.ts, src/workflows/planner.ts.

Verified source facts:
1. Birdeye CLI calls itself pre-1.0, development version 0.4.0, with twenty current skills and four compatibility packages. Most implemented skills are Solana only, while the Price Surge skill includes BSC/Base/Ethereum/Robinhood. API chain support is not equivalent to the CLI's narrower implementation.
2. The source code LICENSE is MIT. That license applies to software, NOT vendor API payloads. Birdeye API terms may restrict capturing/republishing/re-using data; treat this as a source-use authorization barrier until separately licensed. Never scrape restricted pages/hidden endpoints.
3. Runner provenance has requestId, retrievedAt, pagination/coverage, query params, estimated costs and uncertain-cost warnings. Provider reports 'complete' for some unpaginated responses but this is response scope, NOT a complete population declaration; low-liquidity wallet holdings are excluded by default.
4. API requests require credentials; MCP CU cost is unknown and cannot be assumed bounded by an estimate. Source estimate is NOT invoice; retrying can increase cost and time.
5. Public official pricing queried 2026-11-14: Standard $0/30,000 CU; Lite $39/1,500,000 CU; Starter $99/5,000,000; Premium $199/15,000,000. Correct prior archived/answer copies reporting 2.5m/8m/20m as unverified/stale. Do not infer First Buyers available in free tier.

Incremental method hypothesis H-L01:
  Source receipt distinguishes ACTUAL_EVENT_TIME, PUBLICATION_TIME, FIRST_MACHINE_SEEN, DECISION_CUTOFF, QUERY_SCOPE, PAGE_COMPLETE, TRUNCATED, PROVIDER_ACCESS and ESTIMATED_VS_OBSERVED_CU. UNKNOWN cannot be converted to 'no event'; first-known cannot be reconstructed from today’s source label.
Existing baseline: source IDs + basic retrievedAt; prefer chain-origin events in original #120 and #126.
Falsifier: first-party raw timestamp or completeness checks cannot be obtained; this adds no decision change beyond current native receipts.
Status: SOURCE_CODE_METHOD_VERIFIED; transfer candidate only.
Source refs: https://github.com/birdeye-so/birdeye_cli/blob/2dcbd14cad32bcbb57f8d0c0c766d8c496597413/src/runner.ts#L253-L299 and https://github.com/birdeye-so/birdeye_cli/blob/2dcbd14cad32bcbb57f8d0c0c766d8c496597413/src/ledger.ts#L39-L88 .
Do not issue provider requests or create another data collector.
