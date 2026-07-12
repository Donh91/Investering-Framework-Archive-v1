# David Ondrej Agent Skills Repository - Source Note

**Dato:** 2026-07-12  
**Status:** SOURCE_NOTE  
**Område:** external agent-skill design reference  
**Primary folder:** `08_SOURCE_MATERIAL/github/`  
**Related folders:** `07_PROMPTS_AND_AGENTS/github_agent/`, `.agents/skills/`

## Source

```text
Repository: https://github.com/davidondrej/skills
Reviewed commit: 5c99080334072075eb9e0a17837f7d24e4f3e6ae
License: MIT
Repository status at review: public, active, not archived
```

## Relevant design ideas used as inspiration

- one skill per capability or process discipline;
- YAML frontmatter with a routing-oriented description;
- progressive disclosure through `SKILL.md`, references and scripts;
- state-check before action;
- verify, fix and re-verify loops;
- persistent repository artifacts for cross-session continuity;
- explicit failure modes;
- small composable skills instead of one monolithic workflow;
- adversarial trigger and execution testing;
- security review before trusting third-party skills.

## Import boundary

No third-party scripts or executable code were imported.

The Investering implementation was written specifically for the project's existing canonical governance, archive map, safety policy, evidence discipline and new-engine freeze.

The external repository is source context and design inspiration only. It has no framework authority.

## License note

The source repository is MIT-licensed. Any future direct copying or substantial derivative inclusion must preserve the applicable copyright and permission notice.
