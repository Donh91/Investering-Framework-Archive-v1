# Archive Control Registration - Permanent Separation of Destructive Authority

**Date:** 2026-09-03  
**Status:** CANONICAL_GOVERNANCE_REGISTRATION

Registered canonical governance artifact:

`00_ARCHIVE_CONTROL/PERMANENT_SEPARATION_OF_DESTRUCTIVE_AUTHORITY.md`

Agent-readable pointers:

- `.agents/PERMANENT_SEPARATION_OF_DESTRUCTIVE_AUTHORITY.md`
- `07_PROMPTS_AND_AGENTS/PERMANENT_AGENT_SAFETY_INVARIANTS.md`

The registered invariant is permanent and model-agnostic: no autonomous execution context may simultaneously hold sufficient authority to irreversibly destroy both the canonical source system and its independent recovery layer.

Any destructive operation for which this separation cannot be proven must fail closed with `AUTHORITY_SEPARATION_BLOCK`.

The rule may not be weakened, deleted, bypassed, or self-amended by an autonomous agent. Amendment requires explicit human-owner approval, fresh verified recovery evidence, and an auditable high-impact governance change path.
