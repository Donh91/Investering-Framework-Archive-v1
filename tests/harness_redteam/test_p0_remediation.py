from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_absolute_price_threshold_is_rejected():
    gateway = load_module("api_gateway", "scripts/api_agent/api_gateway.py")
    candidate = {
        "metric_path": "spot.BTCUSDT.close",
        "direction": "DOWN",
        "threshold_pct": 63508.0,
        "range_lower_pct": None,
        "range_upper_pct": None,
        "horizon_days": 7,
        "rationale": "regression fixture",
    }
    try:
        gateway.validate_candidate(candidate)
    except ValueError as exc:
        assert "threshold" in str(exc)
    else:
        raise AssertionError("absolute price masquerading as percent was accepted")


def test_valid_directional_percent_is_accepted():
    gateway = load_module("api_gateway_valid", "scripts/api_agent/api_gateway.py")
    gateway.validate_candidate({
        "metric_path": "spot.BTCUSDT.close",
        "direction": "DOWN",
        "threshold_pct": 3.5,
        "range_lower_pct": None,
        "range_upper_pct": None,
        "horizon_days": 7,
        "rationale": "valid fixture",
    })


def test_outcome_validation_rejects_out_of_bounds_threshold():
    engine = load_module("outcome_engine", "scripts/learning/outcome_maturation_engine.py")
    forecast = {
        "frozen_at_utc": "2026-08-01T00:00:00Z",
        "outcome_due_utc": "2026-08-08T00:00:00Z",
        "direction": "DOWN",
        "threshold_pct": 63508.0,
        "start_value": 64000.0,
        "metric_path": "spot.BTCUSDT.close",
    }
    try:
        engine.validate_forecast(forecast)
    except ValueError as exc:
        assert "threshold_pct" in str(exc)
    else:
        raise AssertionError("maturation accepted impossible threshold")


def test_materializer_is_idempotent(tmp_path: Path):
    output = tmp_path / "output.json"
    source_receipt = tmp_path / "receipt.json"
    pending = tmp_path / "pending"
    candidate = {
        "metric_path": "spot.BTCUSDT.close",
        "direction": "DOWN",
        "threshold_pct": 3.0,
        "range_lower_pct": None,
        "range_upper_pct": None,
        "horizon_days": 7,
        "rationale": "fixture",
    }
    output.write_text(json.dumps({"forecast_candidates": [candidate]}))
    source_receipt.write_text(json.dumps({"output_hash": "a" * 64, "model": "test", "task": "test", "prompt_hash": "b" * 64, "context_hash": "c" * 64}))
    command = [sys.executable, str(ROOT / "scripts/api_agent/materialize_forecast_candidates.py"), "--output", str(output), "--receipt", str(source_receipt), "--pending-root", str(pending)]
    first = subprocess.run(command, check=True, capture_output=True, text=True)
    second = subprocess.run(command, check=True, capture_output=True, text=True)
    first_receipt = json.loads(first.stdout)
    second_receipt = json.loads(second.stdout)
    assert len(first_receipt["created"]) == 1
    assert len(second_receipt["created"]) == 0
    assert len(second_receipt["duplicate_skipped"]) == 1
    candidates = [p for p in pending.rglob("*.json") if p.name != "LATEST_MATERIALIZATION_RECEIPT.json"]
    assert len(candidates) == 1


def test_api_dry_run_always_writes_terminal_receipt(tmp_path: Path):
    registry = tmp_path / "registry.json"
    prompt = tmp_path / "prompt.txt"
    context = tmp_path / "context.json"
    out = tmp_path / "out"
    registry.write_text(json.dumps({
        "status": "ACTIVE_SHADOW_ONLY",
        "single_run_hard_stop_usd": 100.0,
        "authority": {"portfolio_action": False},
        "tasks": {"test": {"model": "gpt-5.6-luna", "reasoning_effort": "low", "max_output_tokens": 1000, "max_input_tokens": 1000, "allowed_write_prefix": "tmp/test"}},
    }))
    prompt.write_text("test")
    context.write_text("{}")
    command = [sys.executable, str(ROOT / "scripts/api_agent/api_gateway.py"), "--task", "test", "--registry", str(registry), "--prompt-file", str(prompt), "--context-file", str(context), "--output-dir", str(out), "--intended-write-prefix", "tmp/test", "--dry-run"]
    subprocess.run(command, check=True)
    receipt = json.loads((out / "receipt.json").read_text())
    assert receipt["contract"] == "API_AGENT_RECEIPT_v4"
    assert receipt["status"] == "PASS"
    assert (out / "output.json").exists()
