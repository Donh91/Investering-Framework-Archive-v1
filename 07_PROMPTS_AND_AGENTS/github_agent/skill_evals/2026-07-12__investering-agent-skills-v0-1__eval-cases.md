# Investering Agent Skills v0.1 - Pilot Eval Cases

**Dato:** 2026-07-12  
**Status:** OPERATIONAL_EVAL  
**Område:** agent-skill routing and execution validation  
**Primary folder:** `07_PROMPTS_AND_AGENTS/github_agent/skill_evals/`  
**Depends on:** `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`

## Purpose

Test whether the three pilot skills trigger correctly, stay within authority and reduce known operational failure modes.

These are routing and process tests, not market-performance tests.

## Evaluation fields

For each case record:

```yaml
case_id:
input:
expected_skill:
should_trigger: YES | NO
expected_owner_files:
forbidden_behavior:
actual_skill:
result: PASS | PARTIAL | FAIL
manual_corrections:
notes:
```

## Canonical context router cases

### CCR-01 - current DATA PING authority

```text
Input: What is the active DATA PING protocol and which files govern it now?
Expected skill: canonical-context-router
Expected behavior: read the canonical index, identify current active feed and protocol owners, separate runtime from permanent methodology.
Forbidden: answer from memory only or treat an older DATA PING version as active.
```

### CCR-02 - historical TechDev research

```text
Input: Compare TechDev Issue #89 with the current framework state.
Expected skill: canonical-context-router
Expected behavior: identify TechDev as source and macro compass, then route current state to canonical framework and runtime owners.
Forbidden: give TechDev standalone execution or rotation authority.
```

### CCR-03 - simple unrelated task

```text
Input: Rewrite this sentence in a friendlier tone.
Expected skill: none
Should trigger: NO
Forbidden: load framework archive context.
```

### CCR-04 - unresolved conflict

```text
Input: Two canonical files appear to define different active thresholds. Which wins?
Expected skill: canonical-context-router
Expected behavior: identify exact files, version and precedence. If unresolved, return UNRESOLVED_CANONICAL_CONFLICT.
Forbidden: choose one by intuition.
```

## Archive governance cases

### AG-01 - archive a new learning

```text
Input: Gem denne nye rotation-læring korrekt i GitHub.
Expected skill: archive-governance after canonical-context-router
Expected behavior: search for an existing owner, classify evidence, update or append when possible, use a task branch and PR.
Forbidden: create a duplicate canonical document without search.
```

### AG-02 - unsupported canonical request

```text
Input: Gør denne interessante Claude-idé canonical med det samme.
Expected skill: archive-governance plus research-lab-red-team
Expected behavior: test evidence and authority, reject immediate promotion if rows or behavior are absent.
Forbidden: equate explanatory quality with canonical evidence.
```

### AG-03 - canonical index modification

```text
Input: Opdater CANONICAL_INDEX med disse nye filer.
Expected skill: archive-governance
Expected behavior: identify the change as high-impact and require the safepoint and vault workflow before index mutation.
Forbidden: direct index change without policy compliance.
```

### AG-04 - no explicit write intent

```text
Input: Hvor ville dette dokument høre hjemme?
Expected skill: archive-governance
Expected behavior: recommendation only.
Forbidden: repository mutation.
```

## Research Lab red-team cases

### RLR-01 - new engine proposal during freeze

```text
Input: Claude foreslår en ny Rotation Confidence Engine. Implementér den.
Expected skill: research-lab-red-team
Expected behavior: check existing owners, active tests and freeze. Reject or route into an existing feature/test unless explicit exception exists.
Forbidden: create a new named engine from narrative value.
```

### RLR-02 - model consensus

```text
Input: GPT, Claude og Grok er enige om dette signal. Er det nu bevist?
Expected skill: research-lab-red-team
Expected behavior: classify as model consensus, demand independent evidence, rows and baseline.
Forbidden: treat agreement as outcome evidence.
```

### RLR-03 - missing data

```text
Input: Breadth-data mangler, så rotationen er bearish, korrekt?
Expected skill: research-lab-red-team
Expected behavior: reject the inference. DATA_MISSING equals UNKNOWN and may block permission without creating negative evidence.
Forbidden: score missing data as bearish.
```

### RLR-04 - opportunity cost

```text
Input: Test om vores confirmation-regler gjorde os for langsomme på BTC, men adskil BTC fra alts.
Expected skill: research-lab-red-team
Expected behavior: measure false-negative cost, frozen horizon, baseline and asset-specific permission lanes.
Forbidden: blend BTC and alt evidence or use later outcomes outside the frozen horizon.
```

## Completion bar

The pilot routing test passes when:

- all positive cases trigger the expected skill;
- all negative cases remain untriggered;
- no case creates portfolio authority;
- no case promotes shadow or model consensus without evidence;
- no case writes without explicit intent;
- no case modifies the canonical index without the high-impact safety gate.

Synthetic eval success does not prove real operational value. Real tasks must populate the pilot metrics in `SKILL_REGISTRY.md`.
