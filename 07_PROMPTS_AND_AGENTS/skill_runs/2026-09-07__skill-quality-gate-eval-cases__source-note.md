# Skill Quality Gate Representative Cases Draft

**Dato:** 2026-09-07  
**Status:** SOURCE_NOTE  
**Område:** agent skill evaluation  
**Primary folder:** `07_PROMPTS_AND_AGENTS/skill_runs/`

Representative-case families for later deterministic or blind comparison:

1. Correct trigger: the intended skill activates on a matching request.
2. Negative trigger: the skill does not activate on adjacent but out-of-scope work.
3. Authority boundary: the skill refuses or routes work outside its authority.
4. Canonical routing: current owner files beat legacy, shadow or memory-only context.
5. Write governance: repository mutation requires explicit intent, verified non-default branch and readback.
6. Evidence integrity: missing or stale evidence remains unknown rather than inferred.
7. Autonomy: agent-owned work is performed rather than unnecessarily handed back to the user.
8. Completion truth: completion is claimed only after fresh verification evidence.
9. Regression case: historically observed failure modes remain blocked.
10. Baseline value: evaluate whether the model without the skill performs equivalently on the claimed capability.

This file is a design draft only. No case is considered executed by creating this note.
