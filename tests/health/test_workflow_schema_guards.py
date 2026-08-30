from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_ROOT = ROOT / ".github" / "workflows"
DIRECTOR = WORKFLOW_ROOT / "daily-director-shadow.yml"


def workflow_files():
    return sorted([*WORKFLOW_ROOT.glob("*.yml"), *WORKFLOW_ROOT.glob("*.yaml")])


def test_no_workflow_uses_invalid_cancel_in_progress_key():
    offenders = []
    for path in workflow_files():
        text = path.read_text(encoding="utf-8")
        if "cancel_in_progress:" in text:
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == [], f"invalid GitHub Actions concurrency key cancel_in_progress found in: {offenders}"


def test_daily_director_uses_valid_cancel_in_progress_key():
    text = DIRECTOR.read_text(encoding="utf-8")
    assert "concurrency:" in text
    assert "cancel-in-progress: false" in text
    assert "cancel_in_progress:" not in text
