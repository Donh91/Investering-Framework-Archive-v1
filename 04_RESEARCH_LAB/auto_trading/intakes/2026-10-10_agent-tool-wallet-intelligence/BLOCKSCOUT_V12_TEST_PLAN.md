# P0 Blockscout v12.0.0 compatibility test (no incident asserted)
Read the 2026-10-07 gradual-rollout release notes: https://docs.blockscout.com/blockscout-v12-0-0-api-updates-and-breaking-changes

Current consumers: framework `scripts/api_agent/meme_alpha_blockscout.py`, `scripts/api_agent/meme_alpha_eth_blockscout_provenance.py`, and secrets `collectors/memes_alpha/moonshot_blockscout_enrichment.py`. The Blockscout MCP source is already admitted as exact-CA enrichment; do not invent a new owner or scheduler.

Minimum tests:
1. Sorted paginated requests reattach `sort`, `order`, and `items_count` when v12 omits them in `next_page_params`.
2. No unsupported `limit` param on token transfers or internal transfers; cursor `state_changes_count` instead of prior `state_changes`.
3. Constructor `0x` prefix and null handled; mixed-version fixtures.
4. JSON-RPC errors `{code,message}` instead of text; `eth_getLogs` block numbers are hex/tag; `eth_call` might return -32601 if operator disabled method.
5. 503 transaction-summary retries bounded; scam-token filtering does not produce false zero-transfer evidence.
6. PRO/public fallback credentials never appear in receipts or persisted URL; distinguish HTTP errors, schema failures and actual absence of onchain activity.
7. Small live smoke checks with timestamp+exact endpoint+version observation; no invented production impact and no credential disclosure.

Outcome: PASS => CLEAN_NOOP. Reproduced FAIL => smallest patch in existing owner, tests, independent review, governed PR, post-merge readback. This file is TEST_DESIGN only. Route coordination to existing #1512 and currently relevant owners. No live orders, keys or new wallets.
