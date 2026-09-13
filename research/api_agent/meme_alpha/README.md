# Meme Alpha Lab autonomous runtime

This folder is the public control-plane owner for the research-only Meme Alpha background runtime.

- Policy: `MEME_ALPHA_RUNTIME_POLICY_v1.json`
- Worker: `scripts/api_agent/meme_alpha_runtime.py`
- Skill: `.agents/skills/meme-alpha-supervisor/SKILL.md`
- Private workspace: `Donh91/secrets/private_research/memes_alpha/`
- Private runtime branch: `agent/task-20260913-meme-alpha-live`
- Existing scientific owner for repeatable-edge claims: AUTO_TRADING experiment lifecycle, including issues #885 and #908

The runtime is not a trading engine. It has zero portfolio, canonical-promotion, market-rule, model-weight or auto-merge authority.

Operational pattern:

`new/changed private research input -> deterministic SHA queue -> one bounded research task -> source/provenance receipt -> private runtime branch -> reviewed promotion only when justified`

Unchanged inputs are idempotent. Empty queue means no model call. Repeated unchanged failures are dead-lettered after the policy limit. Development findings are candidates only and do not require Codex for ordinary research.
