# Compass Research Engine | Stage 0: shadow bootstrap

**State:** PR_ONLY_SHADOW_BOOTSTRAP, not a scheduled or production system.
**Authority:** read-only public research with no canonical promotion, no trade or portfolio action, no automatic merge, no private-data runner, no added API budget.
**Owner:** canonical 06_RESEARCH_LAB and existing research/experiment_lifecycle lifecycle; one-to-one reuse of the existing queue, no independent authoritative registry.

## What is implemented

- persistence_baseline.py is a deterministic paired descriptive comparator for NEXT_12H vs a simple pre-outcome momentum sign. It requires provenance admission upstream (pit_verified), matured outcomes, and unique independently specified cluster IDs. Unverified, unmatured, abstained and valid rows have separate denominators; duplicate clusters fail closed. It never declares edge.
- public_receipt.py is a second-line fail-closed public metadata validator, explicitly refusing value-like data, per-value hashes, counts, scores, timestamps and free-form strings. Its request_alias and evidence_alias must be high-entropy opaque IDs minted by a trusted private owner, not hashes of a low-entropy market value. This parser is not authorization for private-to-public transfer; the binding and private decision stay in the private plane.
- test_*.py covers adversarial negative cases in an isolated standard-library environment.
- PREREGISTRATION.md defines the first proposed prospectively gated question. It is not ratified merely by this branch or PR.

## Mandatory scientific sequencing

1. Read fresh AGENTS.md, 00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md, current Research Lab owner and Task2/Kompas contracts.
2. Inventory the historical Master Monday/Kompas archive, preserving scoring era, 12h target definition, actual first-known times and exclusion counts. Historical replay is diagnostic, never prospective proof.
3. Owner/S1 ratifies a versioned preregistration before future holdout collection. No agent-selected seen historical window is a valid confirmatory holdout.
4. Reproduce the existing official Kompas score without rewriting any frozen or legacy record. Deduplicate before fitting. Match every baseline to exactly the same eligible forecast/outcome cluster.
5. Count all attempts, compare the mechanical persistence baseline and report uncertainty. Use null/negative controls and no automatic weight/threshold change.
6. Only after admissible future observations and applicable owner/domain reviews may a research candidate use existing promotion pathways.

## Private Evidence Bridge boundary

This release deploys no private executor and does not read or dispatch into Donh91/secrets. The Stage-0 receipt validator explicitly rejects the PRIVATE_SOURCE_HEALTH lane; it cannot attest that a syntactically opaque identifier carries no private values. Only a future owner-approved private executor with private-side keyed identifier verification, cross-query controls and a separately audited disclosure contract could enable that lane. Round 3 remains PROSPECTIVE_COLLECTION_ONLY, with hypothesis tests, effect calculations, threshold calibration and PnL forbidden. Restricted values never enter public GitHub Actions, logs, caches, attachments, comments, issue bodies or public artifacts, whether encrypted or hashed. Public disclosure may use only the existing authorized value-free binding and schema. Cross-query disclosure / differencing protections must be enforced by the trusted private owner, not by this public parser. The public NO_PUBLIC_DISCLOSURE status is deliberately non-explanatory.

## Release and CI constraints

This directory is not an independent execution or release owner. Existing workflows are unchanged; no new scheduler, agent, supervisor, API call, secret, credentials, main writer or yellow merge authority is created here. This bootstrap MUST NOT be interpreted as completing the Grok #108 security gate. Before autonomous merges, a separately owner-ratified bounded policy, enforceable branch/ruleset controls, trusted read-only path/privilege guard and actual required CI must be verified on current GitHub state. Two reviews from the same agent 24 hours apart are still not independent formal approvals. The owner also needs a transition plan that doesn't break scheduled main publishers.

If PR_ONLY_SHADOW_BOOTSTRAP is incompatible with current policy, stop at read-only/no-update. Do not force it into production.
