# BACKTEST BUILD source index — Custom GPT Phase 05/06 and Claude megapack

**Collection status:** `ACTIVE`  
**Controlled test execution:** `LOCKED`

## Artifacts

| Provenance | Artifact | Bytes | SHA-256 | Role |
|---|---|---:|---|---|
| Custom GPT | `DATA_PING_BACKTEST_HISTORY_PACK_20260727T054034Z(1).zip` | 4,747,666 | `28bf9d3fa71342731b01081fe1b1ee15be87c3244e9003e8470e1b49739989a3` | exact duplicate of prior Phase 04; deduplicated |
| Custom GPT | `DATA_PING_BACKTEST_HISTORY_PACK_20260727T055608Z.zip` | 9,544,646 | `5114f3c99bfcdf47b08f14edded44386c8ae02c2c9fc2e53d1d3cbe36496a93e` | Phase 05 cumulative source |
| Custom GPT | `DATA_PING_BACKTEST_HISTORY_PACK_20260727T062839Z.zip` | 19,137,076 | `7686e30631aba300a4c1fb09ca4e79b22e753eb3880fb7b3a81a07ccb4d83f9d` | Phase 06 latest Custom GPT cumulative source |
| Claude | `DATA PING BACKTEST HISTORY PACK 20260727T052808Z.zip` | 190,546,648 | `303d63946fd7696237b8d1a7208fa5aadd877e55aba57d5b51ea17aa46d18c9f` | independent broad historical research archive |

## Lineage

- Phase 06 embeds Phase 05 byte-for-byte.
- Phase 05 embeds the previously archived Phase 04 package.
- The repeated Phase 04 upload has the exact previously accepted hash and contributes no new sample coverage.
- The Claude archive is independent of the Custom GPT cumulative chain and must be deduplicated at dataset/file level before owner selection.

## Current source authority

```yaml
custom_gpt_okx_swap_daily:
  role: SAME_METHOD_VENUE_SPECIFIC_EXTENSION
  coverage: 2021-05-14_to_2026-04-17
  direct_assets: BTC_USDT_SWAP_AND_ETH_USDT_SWAP
  derived_pair: ETHBTC_DERIVED_NOT_DIRECT

claude_megapack:
  role: BROAD_RESEARCH_DATA_CANDIDATE
  raw_data_value: HIGH
  preliminary_results_authority: NONE
  test_code_status: REWRITE_REQUIRED
```

## Binary materialization policy

The source identities, byte sizes, hashes, inventories and audits are preserved now. Raw binary repository copies are not created in this PR because:

- Custom GPT packages are cumulative and still growing;
- storing every nested predecessor would duplicate bytes repeatedly;
- the Claude ZIP is approximately 190.5 MB and exceeds GitHub's normal single-file limit;
- the current connector does not provide Git LFS or release-asset upload.

At collection-batch close, the archive needs a binary-capable owner route, such as Git LFS, release assets, workflow artifacts or the approved Vault, with a repository pointer and read-back receipt.

## Governance boundary

No artifact in this index authorizes a backtest, parameter choice, sensor promotion, market interpretation, framework-state change or portfolio action.