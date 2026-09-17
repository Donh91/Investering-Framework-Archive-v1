# Skill quality runtime harness

Status: IMPLEMENTATION_PENDING_REVIEW
Authority: EVIDENCE_COLLECTION_ONLY

`scripts/skill_quality_gate/run_eval.py` implements the existing gate's bounded
execution plumbing using the Python standard library. It does not accept, reject,
retire, edit or register a skill. The canonical quality gate and calibration
contract remain the owners of evaluation and governance semantics.

## Offline verification

```bash
PYTHONDONTWRITEBYTECODE=1 python -B -m unittest discover -s tests/skill_quality_gate -v
```

The suite creates disposable Git histories with frozen baseline/candidate skills,
cases, assertions and common context. It runs repeated baseline, candidate and
no-skill conditions, including negative controls. These are harness tests, not
evidence that any model or repository skill performs better.

## Plan and immutable inputs

The plan selects an exact source commit, the exact case-set and assertion-file
SHA-256s, skill commit/blob identities and common input paths. All inputs must be
regular tracked files. Moving refs, unavailable commits, symlinks, path traversal,
missing/duplicate cases and hash mismatches fail before any runner is invoked.

Illustrative plan shape (replace placeholders with verified immutable identities):

```json
{
  "contract": "SKILL_QUALITY_RUNTIME_PLAN_v1",
  "skill_name": "canonical-context-router",
  "source_ref": "<full-commit-sha>",
  "case_set": {
    "path": "07_PROMPTS_AND_AGENTS/skill_quality_gate/EVAL_CASES.json",
    "sha256": "<sha256-of-exact-case-file-bytes>"
  },
  "assertions": {
    "path": "07_PROMPTS_AND_AGENTS/skill_quality_gate/runtime/<frozen-assertions>.json",
    "sha256": "<sha256-of-exact-assertion-file-bytes>"
  },
  "case_ids": ["router-private-unavailable-002"],
  "context_paths": ["AGENTS.md", "00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md"],
  "repetitions": 2,
  "conditions": [
    {"name": "baseline", "skill": {"ref": "<baseline-commit>", "path": ".agents/skills/canonical-context-router/SKILL.md", "blob_sha": "<baseline-blob>"}},
    {"name": "candidate", "skill": {"ref": "<candidate-commit>", "path": ".agents/skills/canonical-context-router/SKILL.md", "blob_sha": "<candidate-blob>"}},
    {"name": "no_skill"}
  ],
  "evaluator_calibration_state": "NOT_USED"
}
```

The existing case set contains prose expectations; the harness does not pretend
those are executable assertions. A reviewer must freeze an assertion sidecar
before the experiment, keyed by each selected case ID. Supported checks are
`output_contains`, `output_excludes`, `json_equals` (JSON key/index path), and
`workspace_unchanged`. Each selected case requires at least one check. Example:

```json
{
  "router-private-unavailable-002": [
    {"kind": "output_contains", "value": "PRIVATE_DATA_AUTHORITY_UNAVAILABLE"},
    {"kind": "workspace_unchanged"}
  ]
}
```

String checks establish only their literal assertion. They do not prove routing,
honesty, privacy, or correct tool use. Choose stronger owner validators or trace
evidence when those properties are load-bearing. This runner's side-effect record
observes file changes inside its temporary workspace; it cannot infer outside
network activity or prove that unobserved actions did not occur.

Common context is copied from `source_ref` into a fresh directory for every run.
Only the selected condition's skill is installed. No-skill runs omit it. The
original case prompt, common context and repetition ordering are the same across
conditions. Requests expose no baseline/candidate condition names. Keep common
context free of copies of the tested skill; that responsibility cannot be inferred
from file names alone. Missing historical objects in a shallow checkout are a
blocked input, never a reason to substitute current content.

## Fixture and command adapters

A fixture JSON maps each case ID to a response:

```json
{"router-private-unavailable-002":{"status":"COMPLETED","output":"PRIVATE_DATA_AUTHORITY_UNAVAILABLE"}}
```

```bash
python -B scripts/skill_quality_gate/run_eval.py \
  --repo-root . --plan /private/temp/plan.json --fixture /private/temp/fixture.json
```

This prints a structured report. It never writes a report into the repository.
Exit 0 means the selected deterministic assertions passed, 1 means deterministic
evidence is blocked, and 2 means inputs or execution could not be established.
None is a skill-acceptance verdict.

For a separately authorized runtime, `--command-json` accepts a JSON argv array
for a trusted adapter and requires `--authorize-live`. The adapter receives JSON
on stdin (`case_id`, `prompt`, `repetition`, common `instruction`), runs with its
working directory set to the disposable workspace, and returns JSON on stdout:

```json
{"status":"COMPLETED","output":"final response","usage":{"input_tokens":100,"output_tokens":20,"cost_usd":0.01}}
```

`FAILED` and `INCOMPLETE` statuses remain in the report. Missing or invalid usage
is `UNKNOWN`. Fixture usage is always `UNKNOWN`; measured host wall time remains
observed even for fixtures. `runtime_model` and `runtime_effort` in a plan are
operator-declared provenance, explicitly not independently verified telemetry.
The report counts adapter attempts separately. An attempted adapter, even one
returning successfully, reports `ADAPTER_ATTEMPTED_MODEL_EXECUTION_UNVERIFIED`;
it does not prove that a model executed. When zero adapter calls were attempted,
the status is `NOT_ATTEMPTED`.
The adapter must populate usage only from observed telemetry. Unsupported costs
must remain absent. An adapter may wrap an installed Codex CLI, but the harness
does not install, authenticate, start or spend on Codex automatically.

The command environment excludes inherited credentials, home configuration and
hooks. Authentication and tool policy need a separately approved adapter/runtime.
A temporary workspace is **not an OS security sandbox**. Supply a sandboxed
runtime where filesystem/network isolation is needed; this harness grants no
additional permission and does not broaden credentials. Arbitrary untrusted
executables must not be evaluated as adapters.

## Reports, privacy and judgment

Each run records exact bindings, completion state, deterministic grades, observed
wall time, observed usage when available, hashed output, hashed changed paths and
cleanup status. Failed/incomplete runs are never dropped. Raw output, stderr,
exception text, file contents and credentials are excluded from reports. Review
even metadata before public persistence; private traces stay private.

The optional Python `judge` callback receives neutrally labelled outputs only
after deterministic grades are fixed. Labels and observation order are randomized
before judgment; the condition mapping is revealed only in the returned report.
Its result is hashed and strictly advisory.
This runner does not verify human-labelled calibration datasets and never treats
even a claimed `CALIBRATED_HELDOUT` state as release authority. A judge cannot
accept/reject a release or override a deterministic blocker. Reports preserve
the calibration claim separately from `calibration_verified: false`.

Counts by condition and failures are descriptive. A single stochastic run is
never superiority proof; repeated runs alone do not establish superiority either.
No-skill results remain separately visible, but value and retirement judgments
require the owning gate and adequate comparative evidence.

## Current implementation verification limits

The initial implementation was verified with offline fixtures and local Python
protocol stubs only. No real Codex CLI was available in the implementation
environment; live runtime evidence, model performance, tokens, provider cost and
latency comparisons remain UNKNOWN. Post-merge main readback and any applicable
live smoke remain outstanding; local tests do not close the remediation lifecycle.
