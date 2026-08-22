# GitHub Agent Change-Control Tools

Wave A adds two dependency-free, read-only helpers for reviewed Codex changes:

1. `scope_creep_guard.py` checks an explicit intent against a staged, base, file, or stdin unified diff and emits deterministic JSON.
2. `commit_archaeology.py` inspects local Git history for a tracked path and emits deterministic JSON or a concise text view.

Intended invocation order for larger changes:

```text
intent declaration
-> commit archaeology for sensitive paths
-> implementation
-> scope-creep report
-> tests
-> human/Codex review
```

Examples:

```bash
python 07_PROMPTS_AND_AGENTS/github_agent/tools/scope_creep_guard.py --intent "Wave A read-only GitHub-agent tools only" --staged
python 07_PROMPTS_AND_AGENTS/github_agent/tools/scope_creep_guard.py --intent-file intent.txt --base HEAD^
python 07_PROMPTS_AND_AGENTS/github_agent/tools/commit_archaeology.py 07_PROMPTS_AND_AGENTS/github_agent/2026-07-19__harvested-agent-patterns-v0-1__implementation-spec.md
```

Boundaries: no workflow, schedule, dependency, Skill, market logic, DATA PING state, portfolio authority, external service, LLM call, deletion, rename, move, automated repair, merge, or writeback. PR #49 remains owner of canary, archive hygiene, maturity queue, and weekly workflow ownership. PR #82 remains owner of Data Terminal Phase 1 and Wave B stage/receipt work.
