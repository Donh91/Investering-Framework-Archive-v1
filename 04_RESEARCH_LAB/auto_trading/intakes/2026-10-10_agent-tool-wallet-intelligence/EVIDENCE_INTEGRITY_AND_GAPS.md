# Research Lab preflight, integrity and negative-evidence ledger
artifact: RL-AUDIT-INTEGRITY-20261010-001
date: 2026-10-10
status: VERIFIED_FOR_FILE_INTEGRITY / UNVERIFIED_FOR_ECONOMIC_CLAIMS
scope: conversation attachment ZIPs, current GitHub source paths and PR draft provenance
No keys, private values, source data replication or execution authority.

## ZIP inspection, direct byte-level reproduction in active conversation container
1. `AT_FOUNDATION_RESEARCH_RUN-001.zip`, SHA256 `046bd5cf9efb6b78d97f2cd623299fcd90dcf6c7f9de3796e30f6e2e2a2f89d8`
- 13 ZIP entries, valid CRC via `zipfile.ZipFile.testzip() == None`.
- The internal `MANIFEST.json` lists **11 files**, all 11 exist and match listed byte counts and SHA256 digests.
- The ZIP also contains its manifest and `PROGRAM_README.md`. The latter is NOT included in manifest-listed files, so manifest is an incomplete **inventory**, not a hash mismatch.
- This same ZIP SHA is stated in Claude's Bridge handoff, and the embedded copy in composite ZIP is byte-identical to this file.
2. `RESEARCH_LAB_Deep_Dive_2026-10-10.zip`, SHA256 `872733498ee04bc1bc9c03b701d97f893c98fc42c3c573d832b19dd61c37923d`
- 26 ZIP entries, valid CRC via `zipfile.ZipFile.testzip() == None`.
- The composite internal `MANIFEST.json` lists **24 files**, all 24 digests and byte counts match actual members.
- The ZIP additionally contains its own manifest and `claude_original/extracted/MANIFEST.json`. The latter is NOT listed in its manifest, so one embedded manifest copy is unindexed, not corrupted.
- Its embedded `claude_original/AT_FOUNDATION_RESEARCH_RUN-001.zip` bytes exactly match the Claude ZIP above.
- Composite package includes two screenshots and 8 main original research files plus nested Claude research and metadata. These attachment bytes are conversation-local; not automatically available in a future GitHub agent's runtime.
**Do not alter/falsely "repair" original source ZIPs**: preserve immutable originals, and generate a complete derived full-member manifest if a future portable release is required. CRC/size/hash integrity does NOT attest truth or execution of research hypotheses.

## Bridge indexing, reproduced structural fault
Source: `Donh91/Investering-AI-Audit-Bridge/registry/ARTIFACT_INDEX.csv`, blob `591af97d5895bead9c551c90780a70e209558e50`; schema header has 11 fields.
- Physical line 21 includes literal two-character `\n` separator **between two distinct records**, resulting in two logically concatenated artifacts on one CSV line.
- Lines 67 and 68 contain extra separator before `SUBMITTED`, yielding 12 comma-separated cells rather than 11.
- Line 95 is RFC4180 quoted but has **12 distinct fields**, with an extra trailing path cell.
- Verified Claude RUN-001 research and its handoff each have explicit entries near end of registry. **They are not missing.**
- Existing Bridge PR #36 touches the same CSV. Issue reported as PR #36 comment on 2026-10-10; owner should reconcile on one branch, preserve all statuses, rerun strict parse and ID/path checks with subsequent exact-main readback. A second competing CSV-write PR is NOT initiated by this package.
- A strict 11-field importer can lose/misalign critical status data unless this is corrected. Do not use registry as a complete machine-authenticated index until validation passes.

## GitHub repo/protection and source rights, as observed
- Five accessible repositories listed under Donh91 in this connection; see `00_MASTER_AUDIT_READ_FIRST.md` for pinned main SHAs and explicit repo names.
- Archive and Experiments report PUBLIC; secrets, MAL, Bridge PRIVATE. Archive status is deliberate under newer `AGENTS.md`.
- Branch API `protected=false` was returned for `main` in all five. Effective ruleset/ruleset-bypass enforcement, backup gate, and secret scanning were **not** independently audited here. Avoid treating `protected=false` as conclusive absence of all server-side gates.
- No exhaustive privacy/credential scanner was run over 50k+ Archive entries, private git history or all PR diffs. **Do not claim no sensitive content exists.**
- Licenses, provider free tiers, redistribution and vendor claims from external sources are preliminary; no third-party bot binary executed.

## Content and result gaps
- Miles X main article from USER-TRANSCRIBED TEXT; original X fetch blocked and image prompts missing. Upstream GARCH code statically read but its model-error suspicion is unverified until a numeric reference test.
- Other X article IDs remain UNKNOWN, not speculative summaries.
- Based Bot documentation gives described functions, not independently reproducible PnL; 14 Telegram bot labels are screenshot observations, not verified accuracy.
- Blockscout v12 published API changes ≠ reproduced production regression; one bounded client test remains necessary.
- D-01/D-02/D-03 are Claude-proposed execution realism studies, not code, matured performance or new evidence rows.
- Basis Desk/MCP and CoinPaprika are proposals; no live connector installed, tokenomics or trading signal moved.
- Robinhood Trading MCP broker account is separate from Robinhood Chain. No real trading or custody authority added.
- Formal multirepo master's own security audit, CI and PR dispositions remain NEXT RUN work; this preflight is narrower.

## Quality verdict
SOURCE_BYTES: PASS for original ZIP members.
SOURCE_MANIFEST_COMPLETENESS: PARTIAL for both ZIPs, documented exact missing records.
BRIDGE_INDEX_STRICT_VALIDITY: FAIL_PENDING_EXISTING_OWNER_REPAIR.
RESEARCH_IDENTITY_AND_AUTHORITY: PASS at document-boundary level, no new trading rights.
CROSS_REPO_MAIN_CURRENT_AT_FUTURE_EXECUTION: UNKNOWN, must fresh-read.
CURRENT_STRATEGY_EDGE: NOT_TESTED.
AUDIT_ENTRYPOINT: READY_FOR_INDEPENDENT_REVIEW, NOT MERGE_APPROVED.
