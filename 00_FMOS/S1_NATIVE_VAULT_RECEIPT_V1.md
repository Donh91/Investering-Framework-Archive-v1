# S1 native Vault receipt input

Use this read-only adapter for the technical half of Archive #1593 and the
existing S1 v4.3 release classifier. It creates no schedule or GitHub access.

`python scripts/governance/s1_vault_receipt_v1.py < evidence.json`

The input has two objects:

- `comment` contains `url`, `body`, and the numeric GitHub `author_id` read
  from the original Archive #1593 comment.
- `native` contains the independently verified `receipt_author_id` for the
  authorized publisher, current Archive `source_sha` and `source_tree_sha`,
  and the Vault `snapshot_ref` and `snapshot_head` read back at use.
  Include `run` with the decimal-string `id` and `attempt`, `repository`,
  `workflow_file`, `head_sha`, `event`, `status`, `conclusion`,
  `snapshot_job`, and `publish_archive_receipt_job`. Use the existing
  separately authorized readback channel for the native Vault observations.
  Also supply `manifest_sha256`, `inventory_sha256`, `verified_files`,
  `verified_manifest_shards`, `remote_readback`, and `restore` from that
  channel for the exact snapshot. Do not populate these inputs by copying
  the Archive comment.

A zero exit returns technical evidence in the existing classifier's format.
The same input can be supplied under `native_vault_evidence` in an existing
S1 v4.3 release record. When supplied for a HIGH candidate, it takes precedence
over the technical fields in `recovery`. The independently authenticated
custody inputs and release assessment remain separate. Existing callers that
have their own authenticated technical input keep the existing interface.
Any failed binding returns a named reason and exits 1. Independently check
current source freshness, safepoint, reviewed workflow commit and the
separate custody assessment through existing policy. The technical result
retains `native_release_permission=false` and provides no custody or merge
permission. Missing access to the native evidence channel leaves the release
blocked. An in-progress backup never supplies a terminal receipt.
