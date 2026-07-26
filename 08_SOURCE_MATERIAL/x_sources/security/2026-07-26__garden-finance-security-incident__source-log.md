# Garden Finance security incident — X source and verification log

**Candidate run:** `2026-07-26T19:45:00Z`  
**Search window:** `2026-07-25T19:45:00Z` to `2026-07-26T19:45:00Z`  
**Origin:** Grok X-source discovery  
**Status:** `INCIDENT_CORROBORATED / LOSS_SIZE_UNRESOLVED / POSTMORTEM_PENDING`

## Candidate 1 — Garden official account

- Handle: `@gardenfi`
- Post time supplied: `2026-07-26T18:10:12Z`
- URL: `https://x.com/gardenfi/status/2081441973651804359`
- Source type: `OFFICIAL_PROTOCOL`
- Supplied claim: Garden identified unusual activity and temporarily took the app offline while investigating.

### Verification status

- The exact X post could not be independently fetched in the verification environment because X returned a cache/fetch failure.
- The handle, URL, timestamp and wording are preserved as user-supplied primary-source metadata.
- Garden's public marketing site remained reachable during verification, but this does not prove that transaction execution in the app was available.
- The app endpoint exposed only a minimal shell to the verifier and could not establish operational status.

### Authority

`HIGH_FOR_PROTOCOL_RESPONSE_IF_POST_AUTHENTIC / CONTENT_FETCH_NOT_REPRODUCED`

The candidate is accepted as the best available source for the protocol's service-outage response, but not for exploit size, root cause or affected-contract scope.

## Candidate 2 — Blockaid

- Handle: `@blockaid_`
- Post time supplied: `2026-07-26T16:00:11Z`
- URL: `https://x.com/blockaid_/status/2081409252489298100`
- Source type: `PRIMARY_SECURITY_DATA_PROVIDER`
- Supplied claim: an ongoing exploit affected Garden Finance HTLC contracts, with approximately `$450,000 USDT` drained across Ethereum, Base, Arbitrum and BSC.
- Supplied Ethereum evidence pointer: `https://etherscan.io/address/0x25b224c05f6cc5e132165c1621de1a4c3b316999`

### Verification status

- The exact X post and supplied Ethereum address page could not be independently fetched in the verification environment.
- The claim is retained as a credible early incident alert, not a final loss assessment.
- Blockaid has an established record of publishing real-time on-chain exploit alerts, but that general source reputation does not independently validate every numeric detail in this specific post.

### Authority

`HIGH_FOR_EARLY_DETECTION / PROVISIONAL_FOR_LOSS_SIZE_AND_FINAL_SCOPE`

## Independent corroboration and estimate conflict

Later independent evidence materially changed the loss-size picture:

- BscScan labels address `0x98BCc6c34A489CEfdD9DfA8d792CFEFb02Ea2D12` as `Garden Finance Exploiter`, citing ZachXBT.
- ZachXBT reported that Garden Finance was likely exploited for `$10.8M+` across multiple chains and that an address related to the team sent an on-chain message offering a 10% whitehat bounty.

These sources corroborate that a material Garden-related security incident occurred, but they do not establish a final audited loss amount.

## Loss-size treatment

```yaml
early_blockaid_estimate_usd: approximately_450000
later_zachxbt_estimate_usd: approximately_10800000_plus
final_loss_size: UNRESOLVED
estimate_relationship: EARLY_PARTIAL_ESTIMATE_LIKELY_SUPERSEDED
```

The `$450,000` value must not be retained as the final incident size. The `$10.8M+` figure is also not final until Garden publishes a postmortem or reconciled on-chain accounting.

## Root-cause treatment

The available evidence supports `GARDEN_HTLC_RELATED_SECURITY_INCIDENT`, but does not yet justify a canonical root-cause label such as:

- smart-contract logic exploit;
- compromised private key;
- solver compromise;
- signature-validation failure;
- integration or relayer failure.

No root cause is promoted before a protocol postmortem or reproducible transaction-level analysis.

## Source disposition

```yaml
candidate_1_garden_official:
  accepted_for: SERVICE_PAUSE_AND_INVESTIGATION_STATUS
  blocked_for: LOSS_SIZE_ROOT_CAUSE_FINAL_SCOPE
candidate_2_blockaid:
  accepted_for: EARLY_EXPLOIT_DETECTION_AND_MULTI_CHAIN_ALERT
  blocked_for: FINAL_LOSS_SIZE_FINAL_ROOT_CAUSE
independent_corroboration:
  status: PASS_WITH_OPEN_ESTIMATE_CONFLICT
incident_status: CONFIRMED_MATERIAL_PROTOCOL_SECURITY_EVENT
systemic_market_status: NOT_DEMONSTRATED
```

## Required follow-up evidence

1. Garden official postmortem.
2. Final affected-contract list and chain-by-chain reconciliation.
3. Confirmed exploit transaction graph and attacker addresses.
4. User-fund, solver-fund and protocol-fund separation.
5. App reopening and remediation evidence.
6. Final recovered, frozen, returned and net-loss amounts.
