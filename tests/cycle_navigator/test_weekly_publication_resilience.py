from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.cycle_navigator import build_weekly_cycle_navigator as mod


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode()


def install_responses(monkeypatch: pytest.MonkeyPatch, responses: list[dict]) -> list[int]:
    budgets: list[int] = []
    pending = list(responses)

    def fake_urlopen(request, timeout=180):
        assert timeout == 180
        payload = json.loads(request.data)
        budgets.append(int(payload["max_output_tokens"]))
        if not pending:
            raise AssertionError("unexpected_extra_openai_call")
        return FakeResponse(pending.pop(0))

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(mod.urllib.request, "urlopen", fake_urlopen)
    return budgets


def test_completed_structured_output_parses_without_retry(monkeypatch):
    budgets = install_responses(monkeypatch, [
        {"status": "completed", "output_text": json.dumps({"ok": True}), "usage": {}}
    ])
    value, raw = mod.call_openai("test-model", "prompt", {}, 12_000)
    assert value == {"ok": True}
    assert raw["status"] == "completed"
    assert budgets == [12_000]


def test_token_limit_incomplete_retries_once_with_larger_budget(monkeypatch):
    budgets = install_responses(monkeypatch, [
        {
            "status": "incomplete",
            "incomplete_details": {"reason": "max_tokens"},
            "output_text": '{"partial":',
        },
        {"status": "completed", "output_text": json.dumps({"ok": True}), "usage": {}},
    ])
    value, _ = mod.call_openai("test-model", "prompt", {}, 5_000)
    assert value == {"ok": True}
    assert budgets == [5_000, 12_000]


def test_truncated_json_retries_once_then_succeeds(monkeypatch):
    budgets = install_responses(monkeypatch, [
        {"status": "completed", "output_text": '{"ok":'},
        {"status": "completed", "output_text": json.dumps({"ok": True}), "usage": {}},
    ])
    value, _ = mod.call_openai("test-model", "prompt", {}, 12_000)
    assert value == {"ok": True}
    assert budgets == [12_000, 16_000]


def test_second_truncated_json_fails_closed(monkeypatch):
    budgets = install_responses(monkeypatch, [
        {"status": "completed", "output_text": '{"ok":'},
        {"status": "completed", "output_text": '{"still":'},
    ])
    with pytest.raises(RuntimeError, match="invalid_structured_output_json"):
        mod.call_openai("test-model", "prompt", {}, 12_000)
    assert budgets == [12_000, 16_000]


def test_non_token_incomplete_fails_without_retry(monkeypatch):
    budgets = install_responses(monkeypatch, [
        {
            "status": "incomplete",
            "incomplete_details": {"reason": "content_filter"},
            "output_text": "",
        }
    ])
    with pytest.raises(RuntimeError, match="openai_incomplete:content_filter"):
        mod.call_openai("test-model", "prompt", {}, 12_000)
    assert budgets == [12_000]


def test_output_budget_growth_is_bounded():
    assert mod._next_output_budget(5_000) == 12_000
    assert mod._next_output_budget(12_000) == 16_000
    assert mod._next_output_budget(16_000) == 16_000


def test_publication_workflow_does_not_mask_builder_failure():
    workflow = (ROOT / ".github/workflows/cycle-navigator-weekly-publication.yml").read_text()
    build = workflow.split("- name: Build Cycle Navigator from final Master Monday", 1)[1]
    build = build.split("- name: Validate publication contract", 1)[0]
    assert "shell: bash" in build
    assert "set -euo pipefail" in build
    assert "--max-output-tokens 12000" in build
    assert "| tee runtime_cycle_navigator_pointer.json" in build
