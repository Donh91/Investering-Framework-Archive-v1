"""Fail-closed static W1 security contract (not a replacement for GH rulesets).

Check both actual YAML semantics and executable step bodies. No private inputs,
cron, release writers, hidden workflow types, unpinned actions or other jobs.
Base-protected PR review and no-secret repo setup remain mandatory externally.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import yaml


class _UniqueBaseLoader(yaml.BaseLoader):
    """Reject duplicate YAML mapping keys; never let later keys hide privilege."""

    def construct_mapping(self, node, deep=False):
        result = {}
        for k_node, v_node in node.value:
            key = self.construct_object(k_node, deep=deep)
            if key in result:
                raise UnsafePublicWorkflow("DUPLICATE_YAML_KEY")
            result[key] = self.construct_object(v_node, deep=deep)
        return result

REPO = "Donh91/investering-public-compute"
WORKFLOW = ".github/workflows/w1-synthetic-security.yml"
CHECKOUT = "actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683"
PIP = "python -m pip install --disable-pip-version-check --no-cache-dir --only-binary=:all: --require-hashes -r requirements-ci.txt"
TEST = "python -m unittest discover -s tests -p 'test_*.py' -v"
BUILD = "python -m tools.produce_synthetic --out /tmp/w1-synthetic.json"
VERIFY = "python -m tools.validate_receipt /tmp/w1-synthetic.json --schema contracts/public_receipt_v1.schema.json"
EXPECTED_JOB_IF = (
    "github.repository == 'Donh91/investering-public-compute' && "
    "github.ref == 'refs/heads/main' && github.event_name == 'workflow_dispatch'"
)


class UnsafePublicWorkflow(ValueError):
    pass


def _run(job: dict) -> list[str]:
    return [step.get("run") for step in job.get("steps", []) if "run" in step]


def guard_workflow(raw: str) -> None:
    """Fail closed as a typed security error, including malformed key types."""
    try:
        _guard_workflow(raw)
    except UnsafePublicWorkflow:
        raise
    except (AttributeError, TypeError, ValueError, KeyError) as exc:
        raise UnsafePublicWorkflow("W1_MALFORMED_STRUCTURE") from exc


def _guard_workflow(raw: str) -> None:
    """Validate the *complete* parsed W1 workflow, not regex only."""
    try:
        cfg = yaml.load(raw, Loader=_UniqueBaseLoader)
    except yaml.YAMLError as exc:
        raise UnsafePublicWorkflow("INVALID_YAML") from exc
    if not isinstance(cfg, dict) or set(cfg) != {"name", "on", "permissions", "concurrency", "jobs"}:
        raise UnsafePublicWorkflow("TOP_LEVEL_SCOPE_INVALID")
    if cfg.get("name") != "W1 Public Compute Synthetic Security Only":
        raise UnsafePublicWorkflow("W1_NAME_DRIFT")
    if cfg.get("on") != {"pull_request": "", "workflow_dispatch": ""}:
        raise UnsafePublicWorkflow("W1_TRIGGER_NOT_ALLOWLISTED")
    if cfg.get("permissions") != {"contents": "read"}:
        raise UnsafePublicWorkflow("W1_WRITER_OR_OIDC_FORBIDDEN")
    concurrency = cfg.get("concurrency", {})
    if (concurrency.get("group") != "public-w1-${{ github.workflow }}-${{ github.event.pull_request.number || github.run_id }}"
            or concurrency.get("cancel-in-progress") != "${{ github.event_name == 'pull_request' }}"):
        raise UnsafePublicWorkflow("W1_CONCURRENCY_INVALID")
    if not isinstance(cfg.get("jobs"), dict) or set(cfg["jobs"]) != {"test", "synthetic_receipt"}:
        raise UnsafePublicWorkflow("W1_JOB_SCOPE_INVALID")
    test, issue = cfg["jobs"]["test"], cfg["jobs"]["synthetic_receipt"]
    for job in (test, issue):
        allowed = {"runs-on", "timeout-minutes", "steps"}
        if job is issue:
            allowed |= {"if", "needs"}
        if not isinstance(job, dict) or set(job) != allowed:
            raise UnsafePublicWorkflow("W1_JOB_KEYS_INVALID")
        if job["runs-on"] != "ubuntu-latest" or job["timeout-minutes"] != "5":
            raise UnsafePublicWorkflow("W1_RUNNER_INVALID")
        if not isinstance(job["steps"], list):
            raise UnsafePublicWorkflow("W1_STEPS_INVALID")
        for step in job["steps"]:
            if not isinstance(step, dict):
                raise UnsafePublicWorkflow("W1_STEP_INVALID")
            if "uses" in step:
                if set(step) != {"uses", "with"}:
                    raise UnsafePublicWorkflow("W1_ACTION_KEYS_INVALID")
                if step["uses"].split(" #")[0] != CHECKOUT or step["with"] != {"persist-credentials": "false"}:
                    raise UnsafePublicWorkflow("W1_ACTION_NOT_PINNED_OR_CREDENTIALS_PRESENT")
            elif "run" in step:
                if set(step) != {"name", "run"} or not isinstance(step["run"], str):
                    raise UnsafePublicWorkflow("W1_RUN_KEYS_INVALID")
            else:
                raise UnsafePublicWorkflow("W1_UNRECOGNIZED_STEP")
    # Step names are public UI/log output; never permit attacker-controlled
    # expressions, bidi characters or ambiguous labels in either job.
    if [step.get("name") for step in test["steps"]] != [
        None, "Install pinned security test libraries", "Run public-only security and receipt regression suite",
    ] or [step.get("name") for step in issue["steps"]] != [
        None, "Install pinned receipt validator", "Generate synthetic-only source receipt to runner temp",
        "Validate synthetic-only source receipt (NEVER private admission)",
    ]:
        raise UnsafePublicWorkflow("W1_STEP_NAME_UNSAFE")
    if test.get("if") or _run(test) != [PIP, TEST] or len(test["steps"]) != 3:
        raise UnsafePublicWorkflow("W1_TEST_COMMAND_DRIFT")
    if (issue.get("if") != EXPECTED_JOB_IF or issue.get("needs") != "test" or
            _run(issue) != [PIP, BUILD, VERIFY] or len(issue["steps"]) != 4):
        raise UnsafePublicWorkflow("W1_SYNTHETIC_COMMAND_OR_TRUST_DRIFT")


def guard_repository(root: Path) -> None:
    expected = {WORKFLOW}
    discovered = {str(p.relative_to(root)) for p in (root / ".github" / "workflows").rglob("*.yml")}
    discovered |= {str(p.relative_to(root)) for p in (root / ".github" / "workflows").rglob("*.yaml")}
    if discovered != expected:
        raise UnsafePublicWorkflow("UNEXPECTED_WORKFLOW_FILE")
    if (root / ".github" / "workflows").is_symlink():
        raise UnsafePublicWorkflow("WORKFLOW_DIRECTORY_SYMLINK")
    if any((root / rel).is_symlink() for rel in expected):
        raise UnsafePublicWorkflow("WORKFLOW_SYMLINK")
    guard_workflow((root / WORKFLOW).read_text(encoding="utf-8"))


if __name__ == "__main__":
    guard_repository(Path(__file__).resolve().parents[1])
    print("W1_PUBLIC_SECURITY_GUARD_PASS_SYNTHETIC_ONLY")
