# Permanent Agent Safety Invariants

## Separation of Destructive Authority

All agents operating on the Investering Framework must read and obey the canonical rule at:

`00_ARCHIVE_CONTROL/PERMANENT_SEPARATION_OF_DESTRUCTIVE_AUTHORITY.md`

No autonomous agent may simultaneously possess sufficient authority to irreversibly destroy both the canonical source system and its independent recovery layer.

Human mnemonic:

> You may improve the aircraft, but you must not simultaneously have authority to destroy both the aircraft and the parachute.

If the separation cannot be proven for a destructive operation, return `AUTHORITY_SEPARATION_BLOCK` and do not broaden permissions to make the task pass.

This rule is permanent and model-agnostic. It applies to Sol, Astra, Codex, API agents, external models, and future agents.
