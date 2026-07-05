# Canonical Weekly Backbone Engine v3.0 - Framework Operating System

**Dato:** 2026-07-05  
**Status:** CANONICAL  
**Område:** Canonical Backbone, GitHub archive controller, weekly operations  
**Primary folder:** 01_CORE_FRAMEWORK/engines/  
**Related folders:** 00_ARCHIVE_CONTROL/, 02_DATA_PING/, 03_WEEKLY_OPERATIONS/, 04_MARKET_LEARNING/, 05_CYCLE_NAVIGATOR/, 07_PROMPTS_AND_AGENTS/  
**Supersedes:** Canonical Weekly Backbone Engine v2.1 as primary operating controller  
**Depends on:** CANONICAL_INDEX.md, ARCHIVE_MAP_AND_ROUTING.md, DATA PING TRIGGER PROTOCOL v0.1, Highest Active DATA PING Version Wins

---

## Executive conclusion

Canonical Weekly Backbone Engine v3.0 upgrades the weekly backbone from a prompt-runner into a Framework Operating System.

The engine must read GitHub first, use the canonical index as navigation, discover the highest active DATA PING version, incorporate available shadow rows, produce the weekly canonical state, and report whether the engine itself needs a future version upgrade.

---

## Mandatory GitHub-first sequence

Every v3.0 run must follow this order:

```text
1. Identify the repository.
2. Read 00_ARCHIVE_CONTROL/CANONICAL_INDEX.md.
3. Read 00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md when placement or precedence is unclear.
4. Discover all DATA PING V* candidates.
5. Select highest explicitly active DATA PING version.
6. Load newest canonical files referenced by the index.
7. Load available DATA PING TRIGGER PROTOCOL v0.1 shadow rows.
8. Load newest FRED / macro_shadow status.
9. Load verified WTD / weekly range ledger if available.
10. Produce Canonical Backbone output with completeness, missing inputs and archive recommendation.
```

If GitHub access is unavailable, the engine must mark:

```text
GITHUB_ACCESS_STATUS: UNAVAILABLE
run_status: MANUAL_BACKFILL_PASS or BLOCKED
```

It must not claim GitHub was read unless the connector was actually used.

---

## DATA PING live feed discovery

Standing rule:

```text
HIGHEST ACTIVE DATA PING VERSION WINS
```

Procedure:

```text
1. Search repository and index for DATA PING V*.
2. Parse integer version number.
3. Keep only feeds marked ACTIVE, LIVE, OPERATIONAL or current active feed.
4. Exclude feeds marked ARCHIVE, LEGACY or SUPERSEDED.
5. Highest active integer wins.
6. If no higher active feed is found, use the current feed stated in CANONICAL_INDEX.md.
7. Never permanently hardcode V2, V3, V4 or any future version.
```

Required output fields:

```text
live_feed
expected_live_feed
highest_active_data_ping_version
archive_feed_status
source_governance_status
```

Conflict rule:

```text
If memory says one DATA PING version and GitHub says a newer active version, GitHub wins.
If two GitHub files conflict, newest canonical file wins.
If active status is ambiguous, mark DATA_PING_ACTIVE_STATUS_CONFLICT and continue conservatively.
```

---

## Shadow ledger ingestion

Before producing output, v3.0 must read or explicitly report accessibility for:

```text
RAW 1-3d
RAW 5-7d
PTR / sequence rows
source-conflict rows
FNP diagnostics
calibration tags
WTD / range ledgers
verified weekly actuals
Claude / Grok / Custom GPT source-role classifications
Master Monday eligibility notes
```

If unavailable:

```text
SHADOW_ROWS_NOT_ACCESSIBLE
```

and list exact missing inputs.

Shadow rows affect confidence, readiness and learning. They do not become official decisions unless ratified.

---

## Source governance

```text
Custom GPT / user-verified actuals = truth-layer
Grok = shadow / adversarial context
Claude / Research Lab = audit / challenger
ChatGPT = governance / ratification
TechDev = macro compass, not execution motor
GitHub = durable archive / canonical memory
```

Truth-layer actuals beat model interpretation. Canonical GitHub governance beats older thread memory. Shadow sources may compress confidence but cannot unlock rebuy, rotation or deployment alone.

---

## Price, range and precision

For weekly precision, use only:

```text
price_source = VERIFIED
price_source = USER
```

Unverified numeric ranges must be marked:

```text
IGNORE_FOR_PRECISION
```

DATA PING snapshots are ping samples only unless explicitly supplied as verified WTD or final weekly range ledger.

---

## Required v3.0 output

Every run must include:

```text
live_feed
expected_live_feed
highest_active_data_ping_version
archive_feed_status
shadow_ledger_status
GitHub access status
Repository completeness score
Master Monday readiness
canonical regime
pullback status with ETA / timing
recovery / rotation confirmation
rebuy status
portfolio action by tier
STATUS BLOCK
EXACT PATH / URL LOGS if available
source-governance status
missing inputs
VERSION_UPGRADE_DIAGNOSTIC
CANONICAL_LEARNING_QUEUE
ARCHIVE_RECOMMENDATION
run_status: AUTO_PASS / MANUAL_BACKFILL_PASS / BLOCKED
```

---

## Run-status logic

```text
AUTO_PASS
```

Use only when GitHub was accessible, CANONICAL_INDEX.md was read, highest active DATA PING was determined, shadow ledger status was checked, and verified ranges were available if scoring is performed.

```text
MANUAL_BACKFILL_PASS
```

Use when some required files or rows are missing, but thread memory or user-provided data is enough to produce a non-scoring operational row.

```text
BLOCKED
```

Use only when no canonical state can be established or critical truth-layer inputs are absent.

Self-healing rule:

```text
One missing file should not block the whole run. Continue, log warning, downgrade completeness.
```

---

## Repository completeness score

Every run should output:

```text
Repository completeness: 0-100%
```

Suggested scoring:

```text
+20 CANONICAL_INDEX.md read
+15 ARCHIVE_MAP_AND_ROUTING.md read or not needed
+20 highest active DATA PING determined
+15 shadow ledger checked
+10 FRED / macro status checked
+10 weekly range / WTD ledger checked
+5 Cycle Navigator / Master Monday context checked
+5 source-governance conflicts checked
```

---

## Adaptive weekly version-upgrade diagnostic

At the end of every weekly run, the engine must assess whether it should stay on the current version or be upgraded.

Required field:

```text
VERSION_UPGRADE_DIAGNOSTIC:
  current_engine_version:
  upgrade_needed: YES / NO / WATCH
  proposed_next_version:
  reason:
  trigger_count:
```

Upgrade triggers:

```text
1. New DATA PING fields not handled by current engine.
2. GitHub folder structure changes or new canonical domains appear.
3. Two or more weekly runs require the same manual workaround.
4. Shadow rows are repeatedly inaccessible despite GitHub access.
5. Scoring or range logic needs a new verified-data rule.
6. Source-governance conflict repeats across Claude, Grok, Custom GPT or ChatGPT.
7. Master Monday or Cycle Navigator needs a field that backbone does not expose.
8. A new external source becomes production-grade and needs routing.
9. Current output becomes too noisy, too sparse or no longer maps to framework decisions.
10. The user explicitly changes framework objectives.
```

Decision logic:

```text
0 triggers = upgrade_needed NO
1 trigger = upgrade_needed WATCH
2-3 triggers in one run = WATCH or YES depending severity
2+ repeated triggers across two weekly runs = YES
Critical governance break = YES immediately
```

This rule makes the framework adaptive week after week without unnecessary version churn.

---

## Canonical Learning Queue

Every run must include:

```text
CANONICAL_LEARNING_QUEUE:
1. Potential new durable learning
2. Evidence needed
3. Suggested archive location
4. Status: IGNORE / WATCH / ARCHIVE_CANDIDATE / CANONICAL_READY
```

Rule:

```text
Rows before new architecture. Archive only durable learning, governance changes or repeated failure handling.
```

---

## Archive recommendation

Every run ends with:

```text
ARCHIVE_RECOMMENDATION:
  archive: YES / NO / WATCH
  reason:
  suggested_path:
  index_update_needed: YES / NO
```

Archive YES requires a new canonical rule, source-governance correction, verified range audit, weekly learning that changes calibration, engine patch or durable Cycle Navigator change.

---

## Supersession note

```text
CWB v2.1 = LEGACY_FALLBACK
CWB v3.0 = CANONICAL_CURRENT when GitHub connector access exists
```

Final rule:

```text
Read GitHub first when access exists.
Use CANONICAL_INDEX.md as the navigation layer.
Use highest active DATA PING version.
Do not silently ignore shadow rows.
Do not score unverified ranges.
Do not claim repository writes unless GitHub returns a commit SHA.
Always end with version-upgrade diagnostic and archive recommendation.
```
