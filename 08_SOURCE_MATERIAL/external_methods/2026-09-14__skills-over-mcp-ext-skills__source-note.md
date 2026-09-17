# Skills Over MCP / ext-skills — source note

**Date:** 2026-09-14  
**Status:** SOURCE_NOTE / RESEARCH_ONLY / NO_AUTHORITY  
**Area:** agent architecture / skill distribution / provenance / skill security  
**Primary folder:** `08_SOURCE_MATERIAL/external_methods/`  
**Core impact:** NONE  
**Skill-registry impact:** RESEARCH CANDIDATE ONLY

## Source

```yaml
repository: modelcontextprotocol/ext-skills
url: https://github.com/modelcontextprotocol/ext-skills
pinned_commit: d866efdba298b55b8156c7b7aa1bdebc1b625f4c
license: Apache-2.0
upstream_status: EXPERIMENTAL_INCUBATION
normative_spec_owner: SEP-2640 in modelcontextprotocol/modelcontextprotocol
```

The repository explicitly describes itself as an experimental incubation space for the Skills Over MCP Working Group. It is not itself an official MCP specification. Any future implementation must re-check the current normative SEP rather than treating this archived snapshot as protocol authority.

## Why this is worth preserving

The durable value is not a ready-made framework skill. It is a concentrated body of implementation evidence around a problem already relevant to this framework:

```text
How can agents discover rich workflow knowledge dynamically without turning remote instructions into invisible authority or repeated context overhead?
```

High-value themes in the reviewed snapshot:

1. remote skill discovery and progressive disclosure;
2. dynamic skill distribution through MCP instead of static local installation;
3. cross-server composition and namespace collision risk;
4. provenance and origin visibility to the model;
5. digest-bound skill resources and drift detection;
6. caching and repeated-discovery cost control;
7. explicit separation between skill content and host authority;
8. prompt-injection, permission-widening and implicit-code-execution threat models;
9. immutable host-private caching as a way to reduce content-rotation / TOCTOU risk;
10. observed skill-adherence problems and the need to test whether a skill is actually loaded and followed rather than merely present.

## Framework-relevant research questions

These are research questions, not adopted rules:

```text
A. Should repository-local skills eventually be discoverable through a dynamic catalog rather than only static routing?
B. Can remote skills be consumed while preserving explicit origin, digest, version and authority boundaries?
C. Can repeated discovery be cached without creating stale or silently replaced skill content?
D. Should every externally supplied skill be treated as untrusted data until verified and bounded by host policy?
E. Can the existing Skill Quality Gate test not only skill quality but discovery, loading and adherence reliability?
```

## Candidate design principles to test later

The following pattern is worth carrying into future architecture review:

```text
discover
-> bind origin
-> bind exact version/digest
-> verify every fetched resource
-> cache immutably when appropriate
-> expose origin to the model
-> preserve host-side authority gates
-> measure actual skill loading/adherence
```

This pattern must not be promoted merely because it appears sensible or because an upstream working group is exploring it.

## Security boundary

The source's most important transferable principle is:

```text
REMOTE SKILL CONTENT IS UNTRUSTED INPUT, NOT HIGHER-AUTHORITY INSTRUCTION.
```

Future testing should specifically challenge:

- prompt injection inside skill content or supporting files;
- hidden or changing content after approval;
- same-name skills from different origins;
- remote `allowed-tools` or equivalent permission widening;
- implicit local execution caused by skill instructions or hooks;
- provenance loss when MCP content is materialized locally;
- digest consistency being mistaken for author trust.

## Private disaster-recovery binding

The upstream repository has been preserved independently in the private recovery Vault.

```yaml
vault_repository: Donh91/Investering-Framework-Vault
vault_path: external_sources/modelcontextprotocol-ext-skills/2026-09-14/
receipt: receipts/2026-09-14__external-research-assets-dr-receipt.json
manifest: external_sources/modelcontextprotocol-ext-skills/2026-09-14/manifest.json
source_pinned_commit: d866efdba298b55b8156c7b7aa1bdebc1b625f4c
source_commit_count_all_refs: 460
source_ref_count: 157
source_file_count_at_pin: 26
full_history_bundle_sha256: 3a37f31456d1c531fe7607b724bb5025d1ad5982ce3b0995362297b1bc641c2d
source_tree_sha256: 7aaa5dddddffeaf2011b9df433ad18f6edb96392027fef2b3d2856c8ee2e5964
restore_status: PASS
```

The Vault copy is disaster-recovery material only. The public control plane owns any later framework interpretation or decision.

## Disposition

```yaml
ARCHIVE: YES
RESEARCH_VALUE: HIGH
DIRECT_TRADING_VALUE: NONE
DIRECT_IMPLEMENTATION: NO
CANONICAL_CHANGE: NONE
NEW_SKILL: NONE
NEW_ENGINE: NONE
NEXT_BEST_ACTION: use as prior art when the framework next reviews dynamic skill discovery, remote skill trust, skill loading reliability or MCP-distributed workflows
```
