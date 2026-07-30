# DCR-20260730-EVENT-003 package pointer

```yaml
request_id: DCR-20260730-EVENT-003
capture_status: PARTIAL
received_via: current_chat_upload
original_package_name: DCR-20260730-EVENT-003_package.zip
original_package_bytes: 6364
original_package_sha256: 4ad0ab1b32fc1382c5c45e09e39180c112fa3be2dd03f035ca49c3fe0e7192cf
package_content_sha256: d032147bceef52bc9ab77e22bad6ad9976d6d92be2ac3f96df2271af9d8e3637
manifest_sha256: 96747c3cb3f06685ab89cdbb87f9497fa81bf8ca563f461e597fba2cdfe97b5c
freeze_timestamp_utc: 2026-07-30T17:09:25Z
post_freeze_source_calls: 0
binary_zip_committed: false
unpacked_text_payload_committed: true
```

## Integrity readback

The uploaded ZIP was opened from the grounded chat-upload path and independently hashed before ingest.

- ZIP SHA-256 matched the handoff.
- Manifest SHA-256 matched the handoff.
- Package-content SHA-256 recomputed from the manifest scope matched the handoff.
- All seven non-manifest file byte sizes and SHA-256 values matched the manifest.
- No silent truncation, current-universe substitution or derived-USD owner substitution was detected.

## Evidence boundary

The package preserves a complete failure and non-substitution ledger, but it does not contain direct ETHBTC owner rows, the first settled follow-up close, exact CoinGecko constituent sidecars or direct challenger-venue rows.

The original ZIP remains external to GitHub. Every text payload contained in the ZIP has been archived in this directory with byte-for-byte content.
