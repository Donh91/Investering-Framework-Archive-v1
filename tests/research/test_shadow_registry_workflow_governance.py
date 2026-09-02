from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEEKLY = ROOT / ".github/workflows/shadow-registry-weekly.yml"
GATE = ROOT / ".github/workflows/shadow-registry-gate.yml"


def test_weekly_uses_reviewed_pr_not_direct_main():
    text = WEEKLY.read_text()
    assert "pull-requests: write" in text
    assert "actions: write" in text
    assert "gh pr create" in text
    assert "git push --set-upstream origin \"$BRANCH\"" in text
    assert "git push origin HEAD:main" not in text
    assert "git push origin main" not in text


def test_native_branch_gates_are_dispatched_and_bound_to_exact_head():
    text = WEEKLY.read_text()
    for workflow in (
        "shadow-registry-gate.yml",
        "data-architecture-gate.yml",
        "storage-health-gate.yml",
    ):
        assert workflow in text
    assert 'gh workflow run "$wf"' in text
    assert '--ref "$BRANCH"' in text
    assert 'expected_sha="$(git rev-parse HEAD)"' in text
    assert 'actual_sha="$(printf' in text
    assert 'actual_sha" != "$expected_sha' in text
    assert 'gh run watch "$run_id"' in text
    assert "--exit-status" in text
    assert "SHADOW_REGISTRY_NATIVE_BRANCH_GATES_PASS" in text


def test_existing_open_pr_still_runs_native_gates():
    text = WEEKLY.read_text()
    marker = 'SHADOW_REGISTRY_REVIEW_PR_EXISTS number=$pr_number branch=$BRANCH'
    assert marker in text
    tail = text.split(marker, 1)[1]
    assert "gh workflow run" in tail


def test_shadow_registry_gate_runs_workflow_governance_regression():
    text = GATE.read_text()
    assert "test_shadow_registry_workflow_governance.py" in text
