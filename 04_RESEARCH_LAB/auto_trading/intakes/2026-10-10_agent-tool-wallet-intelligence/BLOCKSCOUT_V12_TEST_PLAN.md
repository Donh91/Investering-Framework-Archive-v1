# Blockscout compatibility test design, no incident asserted
Source pointer: https://docs.blockscout.com/blockscout-v12-0-0-api-updates-and-breaking-changes
status: TEST_DESIGN
owner: existing public Blockscout adapters and #1512 coordination

Current public consumer paths include scripts/api_agent/meme_alpha_blockscout.py and scripts/api_agent/meme_alpha_eth_blockscout_provenance.py. Fresh-read their exact heads and consumers; do not infer a private collector's behavior.

## Proposed bounded checks
1. Preserve requested sort/order/page-size when a returned pagination cursor omits them.
2. Check removed parameters and changed cursor names against current documented endpoint contracts.
3. Handle constructor argument prefixes, nulls and mixed-version responses explicitly.
4. Distinguish structured RPC errors, supported block-number formats and host-disabled methods from genuine absence of activity.
5. Keep transient retries bounded and source degradation separate from negative market evidence.
6. Ensure credentials never appear in persisted URLs or receipts.
7. Only after offline tests, consider a narrowly authorized live smoke check with exact endpoint and observation time.

No regression is established by this documentation alone. A reproduced defect requires the existing owner, narrow patch, tests, independent review, allowed merge and downstream readback. CLEAN_NOOP is valid. No order, signing, new wallet, collector or scheduler.
