from __future__ import annotations

import ast
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.cycle_navigator import build_weekly_cycle_navigator as mod

# Reuse the existing CN PR-only pytest gate for the opt-in F5 shadow tests.
from tests.cycle_navigator.test_range_skill_shadow_v1 import RangeSkillShadowTests as TestRangeSkillShadowV1


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode()


def install_responses(monkeypatch: pytest.MonkeyPatch, responses: list[dict | BaseException]) -> list[int]:
    budgets: list[int] = []
    pending = list(responses)

    def fake_urlopen(request, timeout=180):
        assert timeout == 180
        payload = json.loads(request.data)
        budgets.append(int(payload["max_output_tokens"]))
        if not pending:
            raise AssertionError("unexpected_extra_openai_call")
        next_item = pending.pop(0)
        if isinstance(next_item, BaseException):
            raise next_item
        return FakeResponse(next_item)

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


def test_double_encoded_structured_object_is_normalized_without_retry(monkeypatch):
    inner = json.dumps({"ok": True})
    budgets = install_responses(monkeypatch, [
        {"status": "completed", "output_text": json.dumps(inner), "usage": {}}
    ])
    value, _ = mod.call_openai("test-model", "prompt", {}, 12_000)
    assert value == {"ok": True}
    assert budgets == [12_000]


def test_transport_timeout_never_reposts_an_ambiguous_paid_call(monkeypatch):
    budgets = install_responses(monkeypatch, [
        TimeoutError("read timed out"),
        {"status": "completed", "output_text": json.dumps({"ok": True})},
    ])
    with pytest.raises(RuntimeError, match="openai_transport_outcome_unknown_no_retry"):
        mod.call_openai("test-model", "prompt", {}, 12_000)
    assert budgets == [12_000]  # The potential second POST was never sent.


def test_connection_error_does_not_retry_or_spawn_another_paid_post(monkeypatch):
    from urllib.error import URLError
    budgets = install_responses(monkeypatch, [
        URLError("upstream disconnected"),
        {"status": "completed", "output_text": json.dumps({"ok": True})},
    ])
    with pytest.raises(RuntimeError, match="openai_transport_outcome_unknown_no_retry"):
        mod.call_openai("test-model", "prompt", {}, 12_000)
    assert budgets == [12_000]


def test_billable_token_limit_incomplete_never_posts_again(monkeypatch):
    budgets = install_responses(monkeypatch, [
        {"status": "incomplete", "incomplete_details": {"reason": "max_tokens"},
         "output_text": '{"partial":'},
        {"status": "completed", "output_text": json.dumps({"ok": True})},
    ])
    with pytest.raises(RuntimeError, match="openai_incomplete_no_repost:max_tokens"):
        mod.call_openai("test-model", "prompt", {}, 5_000)
    assert budgets == [5_000]


def test_billable_malformed_json_never_posts_again(monkeypatch):
    budgets = install_responses(monkeypatch, [
        {"status": "completed", "output_text": '{"ok":'},
        {"status": "completed", "output_text": json.dumps({"ok": True})},
    ])
    with pytest.raises(RuntimeError, match="invalid_structured_output_json_no_repost"):
        mod.call_openai("test-model", "prompt", {}, 12_000)
    assert budgets == [12_000]


def test_double_encoded_but_invalid_json_never_retries(monkeypatch):
    budgets = install_responses(monkeypatch, [
        {"status": "completed", "output_text": json.dumps('{"bad":')},
        {"status": "completed", "output_text": json.dumps({"ok": True})},
    ])
    with pytest.raises(RuntimeError, match="invalid_structured_output_json_no_repost"):
        mod.call_openai("test-model", "prompt", {}, 12_000)
    assert budgets == [12_000]


def test_non_token_incomplete_fails_without_retry(monkeypatch):
    budgets = install_responses(monkeypatch, [
        {
            "status": "incomplete",
            "incomplete_details": {"reason": "content_filter"},
            "output_text": "",
        }
    ])
    with pytest.raises(RuntimeError, match="openai_incomplete_no_repost:content_filter"):
        mod.call_openai("test-model", "prompt", {}, 12_000)
    assert budgets == [12_000]


def test_non_object_result_fails_without_duplicate_post(monkeypatch):
    budgets = install_responses(monkeypatch, [
        {"status": "completed", "output_text": json.dumps(23)},
        {"status": "completed", "output_text": json.dumps({"ok": True})},
    ])
    with pytest.raises(RuntimeError, match="invalid_structured_output_type_no_repost:int"):
        mod.call_openai("test-model", "prompt", {}, 12_000)
    assert budgets == [12_000]


def test_intraday_validation_does_not_shadow_structured_output_mapping():
    source = (ROOT / "scripts/cycle_navigator/build_weekly_cycle_navigator.py").read_text()
    assert 'bucket_value = str(intraday.get(bucket)' in source
    main = next(node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == 'main')
    bucket_loop = next(node for node in ast.walk(main) if isinstance(node, ast.For) and isinstance(node.target, ast.Name) and node.target.id == 'bucket')
    assert not any(isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'value' for target in node.targets) for node in ast.walk(bucket_loop))



def test_decision_projection_is_required_and_typed():
    schema = mod.output_schema()
    assert "decision_projection" in schema["required"]
    projection = schema["properties"]["decision_projection"]
    assert projection["additionalProperties"] is False
    assert set(projection["required"]) == {"contract", "next_1_3d", "next_5_7d", "next_2_3w", "next_21_30d", "weeks_4_8", "protection"}
    assert projection["properties"]["contract"]["const"] == "CYCLE_NAVIGATOR_DECISION_PROJECTION_v1"
    protection = projection["properties"]["protection"]
    assert "pullback_risk_state" in protection["required"]
    assert "distribution_risk" in protection["required"]


def test_weekly_publication_dispatches_fresh_official_compass_after_durable_readback():
    weekly = (ROOT / ".github/workflows/cycle-navigator-weekly-publication.yml").read_text()
    daily = (ROOT / ".github/workflows/daily-compass.yml").read_text()
    assert "actions: write" in weekly
    readback = weekly.index("- name: Durable readback of complete Cycle Navigator package")
    handoff = weekly.index("- name: Refresh Official Compass from newly published weekly CN")
    assert readback < handoff
    handoff_block = weekly[handoff:]
    assert "if: steps.precheck.outputs.skip != 'true'" in handoff_block
    assert "gh workflow run daily-compass.yml --ref main -f run_reason=EVENT_DRIVEN" in handoff_block
    assert "group: framework-main-writer" in weekly
    assert "workflow_dispatch:" in daily
    assert "Publish current Compass to Cycle Navigator Pages" in daily
    assert "gh workflow run cycle-navigator-pages.yml --ref main" in daily
    assert "'.github/workflows/cycle-navigator-weekly-publication.yml'" in daily


def test_publication_workflow_does_not_mask_builder_failure():
    workflow = (ROOT / ".github/workflows/cycle-navigator-weekly-publication.yml").read_text()
    build = workflow.split("- name: Build Cycle Navigator from final Master Monday", 1)[1]
    build = build.split("- name: Validate publication contract", 1)[0]
    assert "shell: bash" in build
    assert "set -euo pipefail" in build
    assert "--max-output-tokens 12000" in build
    assert "| tee runtime_cycle_navigator_pointer.json" in build


def test_next_iso_week_handles_52_and_53_week_years():
    assert mod.next_iso_week(2026, 53) == (2027, 1)
    assert mod.next_iso_week(2025, 52) == (2026, 1)


def test_range_benchmark_rewrite_conflict_is_fail_soft_not_publication_abort():
    source = (ROOT / "scripts/cycle_navigator/build_weekly_cycle_navigator.py").read_text()
    assert "deterministic_range_baseline_rewrite_blocked" not in source
    assert "deterministic_range_baseline_score_rewrite_blocked" not in source
    assert "RETAINED_EXISTING_REWRITE_CONFLICT" in source
    assert "deterministic_range_baseline_persistence" in source



def test_existing_weekly_api_owns_conditional_daily_scenario_without_extra_call():
    source = (ROOT / "scripts/cycle_navigator/build_weekly_cycle_navigator.py").read_text()
    assert "DAILY HIGH/LOW FIRST:" in source
    assert "A MIXED market is not itself grounds to abstain" in source
    assert "abstain per asset only if real source" in source
    assert "do NOT fabricate price evidence".lower() in source.lower()
    assert "daily_path_issue_summary(freeze.get(\"daily_price_path\")" in source
    assert '"daily_path_issuance": daily_path_issue' in source
    # Owner-authorized original final publication is API-free; optional analysis stays upstream.
    assert source.count("value, raw = call_openai(args.model, prompt, context, args.max_output_tokens)") == 0
    assert source.count("value = build_offline_value(context, range_forecast, prev_machine,") == 1
    assert 'api_request_performed": False' in source
    workflow = (ROOT / ".github/workflows/cycle-navigator-weekly-publication.yml").read_text()
    assert "python scripts/cycle_navigator/build_weekly_cycle_navigator.py" in workflow
    assert "--model gpt-6-sol" in workflow
    assert "--max-output-tokens 12000" in workflow




def test_monday_daily_range_guidance_is_day_first_and_source_bound():
    """A 3-day band is min/max of three ORIGINAL forecasts, never a fabricated split."""
    source = (ROOT / "scripts/cycle_navigator/build_weekly_cycle_navigator.py").read_text()
    tree = ast.parse(source)
    issuer = next(n for n in tree.body
                  if isinstance(n, ast.FunctionDef) and n.name == "call_openai")
    text = " ".join(n.value for n in ast.walk(issuer)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str))
    assert text.count("DAILY HIGH/LOW FIRST:") == 1
    assert text.count("DAILY THREE-WINDOW SUMMARY:") == 1
    assert text.count("DAILY OUTPUT AND PRODUCT ACCEPTANCE:") == 1
    assert text.index("DAILY HIGH/LOW FIRST:") < text.index("DAILY THREE-WINDOW SUMMARY:")
    assert "low=min(member daily lows)" in text
    assert "high=max(member daily highs)" in text
    assert "a 2-3-day band alone cannot determine the individual days" in text
    assert "daily_price_path publish the SAME daily low/high pairs" in text
    for guard in (
        "168-hour completed-week", "independently verified native price quote",
        "7 prospectively issued ordered daily low/high pairs", "expected_close INSIDE",
        "abstain per asset only if real source", "immutable W45",
        "no extra paid model retry", "no changes to scoring",
        "exact reversal day or exact price", "not two independent engines",
    ):
        assert guard in text
    # Old verbose/duplicated instructions had conflated uncertain day bands
    # with knowing the actual future turning point.
    assert "NEW DAILY RANGE RESEARCH:" not in text
    assert "PRIMARY SEVEN-DAY PRICE PATH PRODUCT:" not in text
    assert "OWNER-APPROVED MONDAY PRODUCT ACCEPTANCE:" not in text


def test_single_post_fails_closed_on_unexpected_provider_status(monkeypatch):
    budgets = install_responses(monkeypatch, [
        {"status": "queued", "output_text": json.dumps({"ok": True})},
        {"status": "completed", "output_text": json.dumps({"ok": True})},
    ])
    with pytest.raises(RuntimeError, match="openai_unusable_status_no_repost:queued"):
        mod.call_openai("test-model", "prompt", {}, 12_000)
    assert budgets == [12_000]


def test_single_post_source_guard_has_no_retry_loop():
    source = (ROOT / "scripts/cycle_navigator/build_weekly_cycle_navigator.py").read_text()
    tree = ast.parse(source)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "call_openai")
    assert not any(isinstance(n, (ast.For, ast.While)) for n in ast.walk(fn))
    posts = [n for n in ast.walk(fn) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Attribute) and n.func.attr == "urlopen"]
    assert len(posts) == 1
