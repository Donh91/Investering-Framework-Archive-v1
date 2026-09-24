from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import patch

from scripts.remediation.auto_verify_post_fix import verify


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, text=True, capture_output=True).stdout.strip()


def test_auto_verifier_writes_completion_only_when_all_predicates_pass(tmp_path: Path):
    git(tmp_path, "init")
    git(tmp_path, "config", "user.name", "test")
    git(tmp_path, "config", "user.email", "test@example.com")
    marker = tmp_path / "marker.txt"
    marker.write_text("base\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-m", "base")
    merge_sha = git(tmp_path, "rev-parse", "HEAD")

    candidate_id = "candidate-a"
    task = {
        "candidate_id": candidate_id,
        "source_type": "RESEARCH_INTAKE",
        "state": "POST_FIX_OBSERVATION",
        "signature": "abc",
        "candidate_sha256": "candidate-sha",
        "task_contract_sha256": "task-sha",
        "post_fix_gate": "TEST_GATE",
        "merge_commit_sha": merge_sha,
        "pr_number": 7,
    }
    (tmp_path / "LATEST_CODEX_EXECUTION_STATE.json").write_text(json.dumps({"tasks": [task]}))
    merge_path = tmp_path / "research/codex/merges" / f"{candidate_id}.json"
    merge_path.parent.mkdir(parents=True)
    merge_path.write_text("{}\n")
    specs = {
        "contract": "CODEX_POST_FIX_VERIFICATION_SPECS_v1",
        "candidates": [{
            "candidate_id": candidate_id,
            "predicates": [
                {"kind": "N_CONSECUTIVE_SUCCESSFUL_RUNS", "workflow": "x.yml", "count": 2},
                {"kind": "NO_MERGED_RESEARCH_ZOMBIES"},
            ],
        }],
    }
    spec_path = tmp_path / "specs.json"
    spec_path.write_text(json.dumps(specs))
    runs = [
        {"id": 2, "status": "completed", "conclusion": "success", "head_sha": merge_sha, "created_at": "2026-09-24T12:00:00Z"},
        {"id": 1, "status": "completed", "conclusion": "success", "head_sha": merge_sha, "created_at": "2026-09-24T11:00:00Z"},
    ]
    with patch("scripts.remediation.auto_verify_post_fix.completion_requires_convergence", return_value=False):
        report = verify(tmp_path, spec_path, lambda workflow: runs)
    assert [row["candidate_id"] for row in report["verified"]] == [candidate_id]
    completion = json.loads((tmp_path / "research/codex/completions/candidate-a.json").read_text())
    assert completion["status"] == "VERIFIED"
    assert completion["merge_commit_sha"] == merge_sha


def test_auto_verifier_does_not_write_on_failed_predicate(tmp_path: Path):
    git(tmp_path, "init")
    git(tmp_path, "config", "user.name", "test")
    git(tmp_path, "config", "user.email", "test@example.com")
    (tmp_path / "marker.txt").write_text("base\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-m", "base")
    merge_sha = git(tmp_path, "rev-parse", "HEAD")
    task = {
        "candidate_id": "candidate-b", "source_type": "RESEARCH_INTAKE", "state": "POST_FIX_OBSERVATION",
        "signature": "def", "candidate_sha256": "c", "task_contract_sha256": "t",
        "post_fix_gate": "TEST_GATE", "merge_commit_sha": merge_sha, "pr_number": 8,
    }
    (tmp_path / "LATEST_CODEX_EXECUTION_STATE.json").write_text(json.dumps({"tasks": [task]}))
    specs = {"contract": "CODEX_POST_FIX_VERIFICATION_SPECS_v1", "candidates": [{
        "candidate_id": "candidate-b",
        "predicates": [{"kind": "N_CONSECUTIVE_SUCCESSFUL_RUNS", "workflow": "x.yml", "count": 2}],
    }]}
    spec_path = tmp_path / "specs.json"
    spec_path.write_text(json.dumps(specs))
    runs = [{"id": 1, "status": "completed", "conclusion": "success", "head_sha": merge_sha, "created_at": "2026-09-24T11:00:00Z"}]
    report = verify(tmp_path, spec_path, lambda workflow: runs)
    assert report["blocked"]
    assert not (tmp_path / "research/codex/completions/candidate-b.json").exists()


def test_auto_verifier_accepts_valid_required_convergence(tmp_path: Path):
    git(tmp_path, "init")
    git(tmp_path, "config", "user.name", "test")
    git(tmp_path, "config", "user.email", "test@example.com")
    (tmp_path / "marker.txt").write_text("base\\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-m", "base")
    merge_sha = git(tmp_path, "rev-parse", "HEAD")
    task = {
        "candidate_id": "candidate-converged", "source_type": "RESEARCH_INTAKE", "state": "POST_FIX_OBSERVATION",
        "signature": "conv", "candidate_sha256": "c", "task_contract_sha256": "t",
        "post_fix_gate": "TEST_GATE", "merge_commit_sha": merge_sha, "pr_number": 10,
    }
    (tmp_path / "LATEST_CODEX_EXECUTION_STATE.json").write_text(json.dumps({"tasks": [task]}))
    spec_path = tmp_path / "specs.json"
    spec_path.write_text(json.dumps({"contract": "CODEX_POST_FIX_VERIFICATION_SPECS_v1", "candidates": [{
        "candidate_id": "candidate-converged",
        "predicates": [{"kind": "N_CONSECUTIVE_SUCCESSFUL_RUNS", "workflow": "x.yml", "count": 1}],
    }]}))
    runs = [{"id": 1, "status": "completed", "conclusion": "success", "head_sha": merge_sha, "created_at": "2026-09-24T11:00:00Z"}]
    with (
        patch("scripts.remediation.auto_verify_post_fix.completion_requires_convergence", return_value=True),
        patch("scripts.remediation.auto_verify_post_fix.validate_convergence_receipt", return_value={"receipt_sha256": "abc"}),
    ):
        report = verify(tmp_path, spec_path, lambda workflow: runs)
    assert [row["candidate_id"] for row in report["verified"]] == ["candidate-converged"]
    assert report["verified"][0]["checks"][-1] == {
        "kind": "MISSION_CONVERGENCE", "pass": True, "evidence": "receipt_sha256=abc"
    }
    assert (tmp_path / "research/codex/completions/candidate-converged.json").exists()


def test_auto_verifier_blocks_machine_gate_without_required_convergence(tmp_path: Path):
    git(tmp_path, "init")
    git(tmp_path, "config", "user.name", "test")
    git(tmp_path, "config", "user.email", "test@example.com")
    (tmp_path / "marker.txt").write_text("base\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-m", "base")
    merge_sha = git(tmp_path, "rev-parse", "HEAD")
    task = {
        "candidate_id": "candidate-c", "source_type": "RESEARCH_INTAKE", "state": "POST_FIX_OBSERVATION",
        "signature": "ghi", "candidate_sha256": "c", "task_contract_sha256": "t",
        "post_fix_gate": "TEST_GATE", "merge_commit_sha": merge_sha, "pr_number": 9,
    }
    (tmp_path / "LATEST_CODEX_EXECUTION_STATE.json").write_text(json.dumps({"tasks": [task]}))
    specs = {"contract": "CODEX_POST_FIX_VERIFICATION_SPECS_v1", "candidates": [{
        "candidate_id": "candidate-c",
        "predicates": [{"kind": "N_CONSECUTIVE_SUCCESSFUL_RUNS", "workflow": "x.yml", "count": 1}],
    }]}
    spec_path = tmp_path / "specs.json"
    spec_path.write_text(json.dumps(specs))
    runs = [{"id": 1, "status": "completed", "conclusion": "success", "head_sha": merge_sha, "created_at": "2026-09-24T11:00:00Z"}]
    with patch("scripts.remediation.auto_verify_post_fix.completion_requires_convergence", return_value=True), \
         patch("scripts.remediation.auto_verify_post_fix.validate_convergence_receipt", return_value=None):
        report = verify(tmp_path, spec_path, lambda workflow: runs)
    assert report["verified"] == []
    assert report["blocked"][0]["checks"][-1] == {
        "kind": "MISSION_CONVERGENCE",
        "pass": False,
        "evidence": "MISSION_CONVERGENCE_REQUIRED",
    }
    assert not (tmp_path / "research/codex/completions/candidate-c.json").exists()


def test_auto_verifier_surfaces_unconfigured_post_fix_debt(tmp_path: Path):
    tasks = [
        {
            "candidate_id": "configured",
            "state": "POST_FIX_OBSERVATION",
            "post_fix_gate": "ONE_RUN",
        },
        {
            "candidate_id": "semantic-only",
            "state": "POST_FIX_OBSERVATION",
            "post_fix_gate": "TEN_NATURAL_ROWS_PLUS_SEMANTIC_REVIEW",
        },
        {
            "candidate_id": "done",
            "state": "RESOLVED",
            "post_fix_gate": "DONE",
        },
    ]
    (tmp_path / "LATEST_CODEX_EXECUTION_STATE.json").write_text(json.dumps({"tasks": tasks}))
    spec_path = tmp_path / "specs.json"
    spec_path.write_text(json.dumps({
        "contract": "CODEX_POST_FIX_VERIFICATION_SPECS_v1",
        "candidates": [{
            "candidate_id": "configured",
            "predicates": [{"kind": "JSON_PATH_EQUALS", "path": "probe.json", "field": "ok", "value": True}],
        }],
    }))
    (tmp_path / "probe.json").write_text(json.dumps({"ok": False}))
    report = verify(tmp_path, spec_path, lambda workflow: [], write=False)
    assert report["coverage"] == {
        "post_fix_total": 2,
        "machine_spec_configured": 1,
        "machine_spec_unconfigured": 1,
    }
    assert report["unconfigured"] == [{
        "candidate_id": "semantic-only",
        "post_fix_gate": "TEN_NATURAL_ROWS_PLUS_SEMANTIC_REVIEW",
        "reason": "NO_MACHINE_VERIFICATION_SPEC",
    }]
    assert report["blocked"][0]["candidate_id"] == "configured"
