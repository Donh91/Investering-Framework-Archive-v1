# Permanent Agent Safety Pointer

All agents operating on this repository must read and obey:

`00_ARCHIVE_CONTROL/PERMANENT_SEPARATION_OF_DESTRUCTIVE_AUTHORITY.md`

Core invariant:

> An autonomous agent may improve the source system, but must never simultaneously possess sufficient authority to irreversibly destroy both the canonical source system and its independent recovery layer.

If separation cannot be proven for a destructive operation, fail closed with `AUTHORITY_SEPARATION_BLOCK` and do not broaden your own permissions.

This is permanent, model-agnostic governance and applies to GPT-5.6 Sol, Astra, Codex, OpenAI API agents, external models, and future agent systems.
