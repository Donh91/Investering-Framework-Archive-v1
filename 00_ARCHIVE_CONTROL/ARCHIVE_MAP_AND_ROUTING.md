# Archive Map & Routing Rules

**Dato:** 2026-07-05  
**Status:** Canonical archive control  
**Formål:** Gøre GitHub-arkivet nemt at bruge fremadrettet, så nye framework-noter placeres rigtigt første gang.

---

## 1. Executive rule

GitHub-arkivet skal ikke være en tilfældig backup.

Det skal fungere som et struktureret, søgbart og versionsstyret udvidet projektarkiv.

Fremtidige arkivtilføjelser skal derfor placeres efter funktion, ikke kun dato.

Fast regel:

```text
First classify the note.
Then place it in the right domain folder.
Then add it to the index if it is canonical or operationally important.
```

---

## 2. Top-level archive structure

```text
00_ARCHIVE_CONTROL/
01_CORE_FRAMEWORK/
02_DATA_PING/
03_WEEKLY_OPERATIONS/
04_MARKET_LEARNING/
05_CYCLE_NAVIGATOR/
06_RESEARCH_LAB/
07_PROMPTS_AND_AGENTS/
08_SOURCE_MATERIAL/
09_ARCHIVE_INBOX/
changelog/
```

---

## 3. Folder roles

### 00_ARCHIVE_CONTROL

Used for:

- archive map
- routing rules
- canonical index
- naming rules
- precedence rules
- archive hygiene

This folder answers:

```text
Where should this go?
Which source wins?
What is canonical?
```

---

### 01_CORE_FRAMEWORK

Used for durable framework architecture.

Suggested subfolders:

```text
01_CORE_FRAMEWORK/architecture/
01_CORE_FRAMEWORK/governance/
01_CORE_FRAMEWORK/precedence/
01_CORE_FRAMEWORK/engines/
01_CORE_FRAMEWORK/shadow_layers/
```

Place here:

- framework architecture
- governance rules
- F12 / FNP / Kill Criteria
- precedence maps
- shadow-only rules that affect the whole framework
- core engine summaries

Do not place daily pings here.

---

### 02_DATA_PING

Used for DATA PING rules, protocols and source QA.

Suggested subfolders:

```text
02_DATA_PING/protocols/
02_DATA_PING/version_governance/
02_DATA_PING/source_qa/
02_DATA_PING/sensor_specs/
02_DATA_PING/live_state_handover/
```

Place here:

- DATA PING Trigger Protocol
- V4/V5/V6 handover rules
- source-role QA
- sensor specs
- stablecoin / DEX / FRED handling rules
- Custom GPT prompt patches

Do not place weekly learning here unless it changes DATA PING behavior.

---

### 03_WEEKLY_OPERATIONS

Used for operational weekly machinery.

Suggested subfolders:

```text
03_WEEKLY_OPERATIONS/master_monday/
03_WEEKLY_OPERATIONS/weekly_raw/
03_WEEKLY_OPERATIONS/canonical_backbone/
03_WEEKLY_OPERATIONS/automation_patches/
03_WEEKLY_OPERATIONS/operations_updates/
03_WEEKLY_OPERATIONS/range_audits/
```

Place here:

- Master Monday rules
- Weekly RAW Learning rules
- Canonical Backbone updates
- automation patches
- operations updates
- verified range audit learning
- shadow-ledger access patches

The 2026-07-05 DATA PING V4 + Shadow Ledger update belongs primarily here.

---

### 04_MARKET_LEARNING

Used for market structure learning and regime calibration.

Suggested subfolders:

```text
04_MARKET_LEARNING/etf_era/
04_MARKET_LEARNING/recovery_attempts/
04_MARKET_LEARNING/rotation/
04_MARKET_LEARNING/stress_flush/
04_MARKET_LEARNING/macro_shadow/
04_MARKET_LEARNING/fnp_opportunity_cost/
```

Place here:

- ETF-era absorption learning
- rotation survival learning
- recovery-attempt doctrine
- post-flush structure learning
- FRED macro shadow conclusions
- FNP / opportunity-cost learning
- fakeout / stress / flush learnings

Do not place raw weekly posts here unless they contain canonical market learning.

---

### 05_CYCLE_NAVIGATOR

Used for public product and X-output continuity.

Suggested subfolders:

```text
05_CYCLE_NAVIGATOR/weekly_posts/
05_CYCLE_NAVIGATOR/templates/
05_CYCLE_NAVIGATOR/visuals/
05_CYCLE_NAVIGATOR/checkpoints/
05_CYCLE_NAVIGATOR/performance_tracking/
```

Place here:

- weekly Cycle Navigator posts
- visual templates
- infographic standards
- altseason language rules
- public-facing checkpoint posts
- precision score calibration

---

### 06_RESEARCH_LAB

Used for Claude/Grok/Research Lab outputs after synthesis.

Suggested subfolders:

```text
06_RESEARCH_LAB/phase_i_governance/
06_RESEARCH_LAB/phase_ii_replays/
06_RESEARCH_LAB/phase_iii_offensive_edge/
06_RESEARCH_LAB/audit_summaries/
06_RESEARCH_LAB/forward_tests/
```

Place here:

- Research Lab canonical summaries
- replay findings
- red-team conclusions
- forward test specs
- audit outputs after ratification

Do not store every Claude PDF unless it must be preserved as source material.

Preferred rule:

```text
Archive the learning, not every intermediate report.
```

---

### 07_PROMPTS_AND_AGENTS

Used for prompt engineering and agent workflows.

Suggested subfolders:

```text
07_PROMPTS_AND_AGENTS/claude/
07_PROMPTS_AND_AGENTS/custom_gpt/
07_PROMPTS_AND_AGENTS/grok/
07_PROMPTS_AND_AGENTS/github_agent/
07_PROMPTS_AND_AGENTS/templates/
```

Place here:

- Claude prompt engineering standard
- Research Lab prompt templates
- Custom GPT patch prompts
- GitHub archive agent prompts
- reusable prompt blocks

---

### 08_SOURCE_MATERIAL

Used for source references that are not themselves canonical framework rules.

Suggested subfolders:

```text
08_SOURCE_MATERIAL/techdev/
08_SOURCE_MATERIAL/coingecko/
08_SOURCE_MATERIAL/fred/
08_SOURCE_MATERIAL/glassnode/
08_SOURCE_MATERIAL/screenshots/
```

Place here:

- TechDev issue notes
- source extracts
- external reports
- raw evidence
- screenshots converted to text

Rule:

```text
Source material supports conclusions.
It does not automatically become framework doctrine.
```

---

### 09_ARCHIVE_INBOX

Used only when placement is unclear.

Suggested subfolders:

```text
09_ARCHIVE_INBOX/to_classify/
09_ARCHIVE_INBOX/needs_review/
09_ARCHIVE_INBOX/duplicates_or_legacy/
```

Use this sparingly.

Files should not live here permanently.

---

### changelog

Used for append-only chronological notes and migration history.

Rule:

```text
changelog is a receipt layer.
Domain folders are canonical location.
```

If a file is first written to changelog, later index it under the right domain.

---

## 4. File naming standard

Use this format:

```text
YYYY-MM-DD__short-topic__status.md
```

Examples:

```text
2026-07-05__data-ping-v4-shadow-ledger-ops-update__canonical.md
2026-07-05__fred-targeted-series-rule__canonical.md
2026-07-05__geckoterminal-dex-shadow-only-rule__canonical.md
2026-07-05__recovery-attempt-quality-doctrine__canonical.md
```

Status suffix options:

```text
__canonical.md
__shadow.md
__forward-test.md
__source-note.md
__draft.md
__legacy.md
__superseded.md
```

---

## 5. Placement decision tree

Use this routing logic:

```text
Does it change framework governance?
→ 01_CORE_FRAMEWORK/governance

Does it change DATA PING behavior?
→ 02_DATA_PING

Does it affect Master Monday / Weekly RAW / automations?
→ 03_WEEKLY_OPERATIONS

Does it teach market structure or regime behavior?
→ 04_MARKET_LEARNING

Does it affect Cycle Navigator output, style or scoring?
→ 05_CYCLE_NAVIGATOR

Is it Research Lab / Claude / Grok audit learning?
→ 06_RESEARCH_LAB

Is it a reusable prompt or agent workflow?
→ 07_PROMPTS_AND_AGENTS

Is it raw external source material?
→ 08_SOURCE_MATERIAL

Unclear?
→ 09_ARCHIVE_INBOX/to_classify
```

---

## 6. Status classification

### Canonical

Use when the note should guide future framework behavior.

```text
STATUS: CANONICAL
```

### Shadow

Use when the note is active learning, but not an operative rule.

```text
STATUS: SHADOW_ONLY
```

### Forward test

Use when the note must produce future rows before promotion.

```text
STATUS: FORWARD_TEST
```

### Source note

Use when the note is evidence or external context.

```text
STATUS: SOURCE_NOTE
```

### Legacy

Use when the note was historically valid but newer rules override it.

```text
STATUS: LEGACY
```

### Superseded

Use when the note is replaced by a newer canonical file.

```text
STATUS: SUPERSEDED
```

---

## 7. Required frontmatter for future files

Every new archive file should start with:

```markdown
# Title

**Dato:** YYYY-MM-DD  
**Status:** CANONICAL / SHADOW_ONLY / FORWARD_TEST / SOURCE_NOTE / LEGACY / SUPERSEDED  
**Område:** short domain  
**Primary folder:** folder path  
**Related folders:** optional  
**Supersedes:** optional  
**Depends on:** optional  
```

---

## 8. Indexing rule

If a file is:

- canonical
- operationally important
- governance relevant
- used by Master Monday
- used by DATA PING
- used by Cycle Navigator
- used by Research Lab

then add it to:

```text
00_ARCHIVE_CONTROL/CANONICAL_INDEX.md
```

---

## 9. Duplication rule

Avoid duplicate full documents.

If a topic belongs to multiple domains, choose one primary folder and add cross-links in the index.

Example:

A file about FRED may touch DATA PING, macro learning and Master Monday.

Primary folder:

```text
04_MARKET_LEARNING/macro_shadow/
```

Cross-link from:

```text
02_DATA_PING/source_qa/
03_WEEKLY_OPERATIONS/master_monday/
```

---

## 10. Current routing decision for 2026-07-05 update

The July 5 operations update touches multiple domains:

- DATA PING V4
- Shadow Ledger
- Master Monday
- FRED
- GeckoTerminal
- Recovery Attempt Quality
- Cycle Navigator staged rotation language

Primary classification:

```text
03_WEEKLY_OPERATIONS/operations_updates/
```

Secondary classifications:

```text
02_DATA_PING/protocols/
04_MARKET_LEARNING/recovery_attempts/
04_MARKET_LEARNING/macro_shadow/
05_CYCLE_NAVIGATOR/templates/
```

Because it was first saved under `changelog/`, it is treated as the chronological receipt and indexed as canonical from the archive control layer.

---

## 11. Final archive principle

```text
The archive should answer three questions quickly:

1. What is the current rule?
2. Where did the rule come from?
3. What older assumptions does it override or refine?
```

If a file does not help answer one of those questions, it probably belongs in source material or archive inbox, not canonical framework.