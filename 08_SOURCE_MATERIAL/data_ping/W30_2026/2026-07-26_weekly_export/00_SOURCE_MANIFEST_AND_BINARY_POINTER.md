# DATA PING W30 weekly export — source manifest and binary pointer

**Source date:** 2026-07-26  
**Package generated:** 2026-07-26T19:41:38Z  
**Status:** `SOURCE_VALIDATED / LOGICAL_EVIDENCE_ARCHIVED / BINARY_MATERIALIZATION_PENDING`

## Original supplied artifacts

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `data_ping_uge30_2026.zip` | 702,338 | `c0745b6c0b961fd3765ffa051dc6f2d07db611c86654871122e59e6d4f6abe98` |
| `data_ping_uge30_2026.xlsx` | 80,291 | `8d6727ab3a4a4f6247e34071fa7542b4f53e39794eb4dc324e2bbc8a6cd3b33d` |
| TechDev business-cycle chart | 152,750 | `5b9691af6456ae1148eac7c42897a757c67fa326ca83a0b0875d17850a31af51` |
| ETH weekly / two-week / monthly chart | 272,815 | `d89c1598100bd3904b4e3f1c7601efef13c25cf79c835d0e6339cbee32950bd7` |

The separately supplied workbook is byte-identical to the workbook inside the ZIP.

## ZIP inventory

- Total files: `30`
- Manifest payload entries: `29`
- The manifest excludes itself from its payload list.
- All 29 listed file byte counts and SHA-256 values were independently recomputed and matched.

The package contains:

- 166 BTC 1H rows and 166 ETH 1H rows;
- raw OKX payloads and normalized hourly CSVs;
- combined hourly comparison rows;
- daily and weekly summaries;
- ETF, CFGI, macro, breadth, stablecoin, TVL, DEX and OKX snapshots;
- 61 collection receipts and deduplicated error evidence;
- workbook and three package-generated charts.

## Text-only preservation derivative

A deterministic text-only derivative was produced locally by excluding PNG and XLSX files from the extracted package and creating a gzip-compressed tar archive.

```yaml
text_payload_name: data_ping_uge30_2026_text_payload.tar.gz
text_payload_bytes: 75451
text_payload_sha256: 79344e1dff19e5c93b4579d35e02576f78c7078b0e6c6bbe67048b6c9912ca67
contents: all package text, CSV and JSON files
```

This derivative was used for validation only. It is not claimed as a replacement for the original ZIP.

## Binary materialization limitation

The current direct GitHub write route available in this execution context accepts UTF-8 text but does not accept a local binary attachment path for repository file creation.

Therefore:

```yaml
original_zip_repository_copy: PENDING_CONNECTOR_CAPABILITY
original_xlsx_repository_copy: PENDING_CONNECTOR_CAPABILITY
source_jpeg_repository_copies: PENDING_CONNECTOR_CAPABILITY
hash_and_metadata_preservation: PASS
logical_analysis_preservation: PASS
```

No partial, truncated or base64-corrupted binary representation is retained in the branch.

The original artifacts remain the authority for byte-level source identity. Future binary materialization must verify the hashes above before promotion.

## Routed framework objects

- W30 package audit and framework read:
  `04_MARKET_LEARNING/data_ping/W30_2026/2026-07-26__weekly-data-package-audit-and-framework-read.md`
- TechDev and ETH chart shadow assessment:
  `04_MARKET_LEARNING/techdev/2026-07-26__business-cycle-and-eth-multitimeframe__shadow-assessment.md`

## Authority boundary

This source package improves historical replay and research capability. It does not change current market state, portfolio state, rotation, rebuy, entry permission, Stage-1 or forecast outcomes.
