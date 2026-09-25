# Meme Alpha Lab autonomous runtime

This folder is the public control-plane owner for the research-only Meme Alpha background runtime.

- Policy: `MEME_ALPHA_RUNTIME_POLICY_v1.json`
- Base worker: `scripts/api_agent/meme_alpha_runtime.py`
- Provider hardening: `scripts/api_agent/meme_alpha_runtime_v1_1.py`
- Source-authenticated worker: `scripts/api_agent/meme_alpha_runtime_v1_2.py`
- Deterministic source gate: `scripts/api_agent/meme_alpha_source_auth.py`
- Fresh-launch research/alert layer: `MOONSHOT_SENTINEL_CONTRACT_v1.json`
- Cross-stage token memory: `ALPHA_LAB_LIFECYCLE_ENGINE_v1.json`
- Secondary-expansion/reclaim research: `PHOENIX_RECLAIM_EXPERIMENT_v1.json`
- Deterministic lifecycle classifier: `scripts/api_agent/meme_alpha_lifecycle_v1.py`\n- Blockscout exact-CA enricher: `scripts/api_agent/meme_alpha_blockscout.py`
- Skill: `.agents/skills/meme-alpha-supervisor/SKILL.md`
- Private workspace: `Donh91/secrets/private_research/memes_alpha/`
- Private runtime branch: `agent/task-20260913-meme-alpha-live`
- Existing scientific owner for repeatable-edge claims: AUTO_TRADING experiment lifecycle, including issues #885 and #908

The runtime is not a trading engine. It has zero portfolio, canonical-promotion, market-rule, model-weight or auto-merge authority.

Operational pattern:

`new/changed private research input -> deterministic SHA queue -> Stage0 -> one bounded research task -> source-authentication gate -> provenance receipt -> private runtime branch -> reviewed promotion only when justified`

The lifecycle layer does not replace Moonshot Sentinel. It persists the same exact-CA identity after the first launch phase so later drawdown, dormancy, wallet re-entry, reclaim and failed-reclaim observations remain part of one auditable token history. Moonshot and Phoenix use separate prospective learning populations and may share evidence infrastructure without sharing trained thresholds.

## Source-authentication admission

Discovery and authentication are separate stages. GitHub branding, repository-internal claims, realistic code, exact CAs, commit chronology and a valid GitHub signature may be useful evidence but do not prove first-party ownership.

For a first-party/project-owned claim to survive the v1.2 gate it must have:

1. at least two independent project-controlled trust anchors external to the source being authenticated;
2. at least two distinct anchor categories;
3. no unresolved/blocking adversarial red-team finding;
4. no repository-forensics blocker;
5. for an exact token/CA first-party claim, a HIGH-confidence on-chain binding.

If those conditions are not met, the claim remains `CANDIDATE`, `CONFLICTED` or `INVALIDATED_FIRST_PARTY`; the runtime sets `first_party_claim_allowed=false`, degrades the run when source authentication is material, and moves unauthenticated first-party statements out of `verified_findings`.

A real community/CTO thesis is evaluated separately and does not inherit first-party legitimacy from a spoofed or unauthenticated origin story.

Revoked provenance must propagate into descendant research tasks. PONSCUPINE is retained privately as an adversarial provenance-spoof benchmark so future archaeology is regression-tested against the exact failure mode.

Unchanged inputs are idempotent. Empty queue means no model call. Repeated unchanged failures are dead-lettered after the policy limit. Development findings are candidates only and do not require Codex for ordinary research.
\n## Blockscout exact-CA transport\n\nFor Robinhood Chain exact-CA enrichment, the repository runtime uses `scripts/api_agent/meme_alpha_blockscout.py`. The transport preference is authenticated Blockscout PRO through `BLOCKSCOUT_API_KEY`, then the chain-specific public explorer as a bounded fallback. The credential is runtime-only and must never be persisted.\n\nThe module is downstream of discovery and upstream of first-party cross-binding and market/sellability checks. It can freeze contract state, creation transaction, verified-source status, token metadata and decoded launch-origin fields. It is not a scanner, price oracle or project-ownership oracle.\n