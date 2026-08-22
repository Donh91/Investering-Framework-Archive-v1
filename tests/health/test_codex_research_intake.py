import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MERGER_PATH = ROOT / "scripts/remediation/merge_codex_research_intake.py"
BINDER_PATH = ROOT / "scripts/remediation/write_codex_research_transition_receipt.py"

spec = importlib.util.spec_from_file_location("codex_intake_merger", MERGER_PATH)
merger = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(merger)

spec2 = importlib.util.spec_from_file_location("codex_intake_binder", BINDER_PATH)
binder = importlib.util.module_from_spec(spec2)
assert spec2.loader
spec2.loader.exec_module(binder)


def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def base_docs(repo: Path):
    out = repo / "research/remediation"
    dump(out / "LATEST_REMEDIATION_QUEUE.json", {"tasks": [], "codex_ready_tasks": [], "needs_more_evidence": []})
    dump(out / "LATEST_CODEX_READY_TASKS.json", {"contract": "CODEX_READY_TASKS_v1", "contract_revision": "1.1", "tasks": []})
    dump(out / "LATEST_NEEDS_MORE_EVIDENCE.json", {"tasks": []})
    return out


def candidate(cid="codex-research-20260822-parser-fix", linked=None, owner=False):
    return {
        "contract": "CODEX_RESEARCH_CANDIDATE_v1",
        "candidate_id": cid,
        "submitted_at_utc": "2026-08-22T13:00:00Z",
        "status": "SUBMITTED",
        "origin": {"type": "RESEARCH_THREAD", "thread_label": "test", "source_paths": ["research/example.json"]},
        "title": "Repair bounded parser defect",
        "objective": "Repair the reproducible parser defect without changing framework semantics.",
        "finding_key": "RESEARCH_PARSER_DEFECT",
        "primary_target": "scripts/example.py",
        "allowed_change_scope": ["scripts/example.py", "tests/test_example.py"],
        "evidence": [{"kind": "TEST", "ref": "tests/test_example.py::test_repro"}],
        "reproduction": "Run pytest tests/test_example.py::test_repro and observe the deterministic failure.",
        "acceptance_tests": {
            "positive": ["pytest tests/test_example.py::test_repro"],
            "negative": ["pytest tests/test_example.py::test_authority_boundary"],
        },
        "authority_boundary": "CODE_REMEDIATION_ONLY",
        "requires_framework_owner_authority": owner,
        "forbidden_changes": [
            "market gates", "model weights", "canonical authority", "portfolio logic", "API budget", "new policy semantics"
        ],
        "linked_health_signature": linked,
        "requested_priority": "EXPEDITED",
        "post_fix_gate": "CI_PLUS_ONE_PRODUCTION_SHAPE_RUN",
    }


def test_valid_research_candidate_enters_same_codex_queue_and_ledger(tmp_path):
    out = base_docs(tmp_path)
    c = candidate()
    path = tmp_path / "research/codex/intake/2026/08" / f"{c['candidate_id']}.json"
    dump(path, c)
    result = merger.merge(tmp_path, out)
    assert result["codex_ready"] == 1
    ready = json.loads((out / "LATEST_CODEX_READY_TASKS.json").read_text())
    task = ready["tasks"][0]
    assert task["source_type"] == "RESEARCH_INTAKE"
    assert task["candidate_id"] == c["candidate_id"]
    assert task["requested_priority"] == "EXPEDITED"
    assert task["state"] == "CODEX_READY"
    state = json.loads((tmp_path / "LATEST_CODEX_EXECUTION_STATE.json").read_text())
    assert state["queue_authority"] == "LATEST_CODEX_READY_TASKS.json"
    assert state["summary"]["codex_ready"] == 1
    assert "CODEX_READY" in (tmp_path / "research/codex/CODEX_EXECUTION_LEDGER.jsonl").read_text()


def test_framework_owner_candidate_is_rejected_not_queued(tmp_path):
    out = base_docs(tmp_path)
    c = candidate(owner=True)
    path = tmp_path / "research/codex/intake/2026/08" / f"{c['candidate_id']}.json"
    dump(path, c)
    result = merger.merge(tmp_path, out)
    assert result["codex_ready"] == 0
    status = json.loads((tmp_path / "research/codex/LATEST_CODEX_INTAKE_STATUS.json").read_text())
    assert status["error_count"] == 1
    assert "FRAMEWORK_OWNER_AUTHORITY_REQUIRED" in status["errors"][0]["reasons"]


def test_research_candidate_deduplicates_to_active_health_signature(tmp_path):
    out = base_docs(tmp_path)
    sig = "0123456789abcdefabcd"
    health_task = {
        "signature": sig,
        "workflow": "example.yml",
        "finding": "LATEST_RUN_FAILED",
        "state": "CODEX_READY",
        "route": "CODEX_PR",
        "objective": "fix",
    }
    dump(out / "LATEST_REMEDIATION_QUEUE.json", {
        "tasks": [health_task.copy()],
        "codex_ready_tasks": [health_task.copy()],
        "needs_more_evidence": [],
    })
    dump(out / "LATEST_CODEX_READY_TASKS.json", {"contract": "CODEX_READY_TASKS_v1", "tasks": [health_task.copy()]})
    c = candidate(linked=sig)
    path = tmp_path / "research/codex/intake/2026/08" / f"{c['candidate_id']}.json"
    dump(path, c)
    merger.merge(tmp_path, out)
    ready = json.loads((out / "LATEST_CODEX_READY_TASKS.json").read_text())
    assert len(ready["tasks"]) == 1
    assert ready["tasks"][0]["signature"] == sig
    assert ready["tasks"][0]["research_intake_sources"][0]["candidate_id"] == c["candidate_id"]


def test_research_fresh_state_binding_rejects_changed_candidate(tmp_path):
    out = base_docs(tmp_path)
    c = candidate()
    path = tmp_path / "research/codex/intake/2026/08" / f"{c['candidate_id']}.json"
    dump(path, c)
    merger.merge(tmp_path, out)
    (tmp_path / "LATEST_CODEX_READY_TASKS.json").write_text(
        (out / "LATEST_CODEX_READY_TASKS.json").read_text(), encoding="utf-8"
    )
    task = json.loads((tmp_path / "LATEST_CODEX_READY_TASKS.json").read_text())["tasks"][0]
    receipt = binder.build_receipt(tmp_path, task["signature"], "agent/task-fix")
    assert receipt["candidate_sha256"] == task["candidate_sha256"]
    c["objective"] = "mutated after queue binding"
    dump(path, c)
    try:
        binder.build_receipt(tmp_path, task["signature"], "agent/task-fix")
    except ValueError as exc:
        assert "STALE_CANDIDATE_HASH_MISMATCH" in str(exc)
    else:
        raise AssertionError("changed candidate must fail fresh-state binding")


def test_fast_path_uses_nonwriting_dispatcher_and_preserves_single_writer():
    dispatcher = (ROOT / ".github/workflows/codex-intake-dispatch.yml").read_text(encoding="utf-8")
    writer = (ROOT / ".github/workflows/remediation-maturation.yml").read_text(encoding="utf-8")
    assert "research/codex/intake/**/*.json" in dispatcher
    assert "research/codex/transitions/*.json" in dispatcher
    assert "research/codex/completions/*.json" in dispatcher
    assert "actions: write" in dispatcher
    assert "contents: read" in dispatcher
    assert "gh workflow run remediation-maturation.yml" in dispatcher
    assert "contents: write" not in dispatcher
    assert "git push" not in dispatcher
    assert "group: framework-main-writer" in writer
    assert "timezone: 'Europe/Copenhagen'" in writer
    assert "merge_codex_research_intake.py" in writer
    assert "\n  push:\n" not in writer
