from __future__ import annotations

import importlib.util
import json
from pathlib import Path

MODULE_PATH = Path(__file__).parents[2] / "scripts" / "api_agent" / "evidence_gap_validation_auditor.py"
spec = importlib.util.spec_from_file_location("evidence_gap_validation_auditor", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def _doc(index: int, payload_chars: int) -> dict:
    value = {
        "id": index,
        "signal": "x" * payload_chars,
        "tail": {"source_time": f"2026-09-{(index % 28) + 1:02d}T00:00:00Z", "score": index},
    }
    return {
        "path": f"research/example/{index:03d}.json",
        "mtime_utc": f"2026-10-01T00:{index % 60:02d}:00Z",
        "sha256": module.sh(value),
        "value": value,
    }


def test_large_evidence_set_is_deterministically_context_bounded() -> None:
    items = [{"gap_id": "GAP-1", "metric_name": "test", "previous_validation": None}]
    docs = [_doc(index, 50_000) for index in range(30)]

    first, first_budget = module.build_context(
        items,
        docs,
        module.DEFAULT_MAX_CONTEXT_CHARS,
        module.DEFAULT_MAX_DOCUMENT_CHARS,
    )
    second, second_budget = module.build_context(
        items,
        docs,
        module.DEFAULT_MAX_CONTEXT_CHARS,
        module.DEFAULT_MAX_DOCUMENT_CHARS,
    )

    assert first == second
    assert first_budget == second_budget
    assert first_budget["context_char_count"] <= module.DEFAULT_MAX_CONTEXT_CHARS
    assert first_budget["included_document_count"] > 0
    assert first_budget["dropped_document_count"] > 0
    assert first_budget["source_document_count"] == 30
    assert any("value_projection" in doc for doc in first["evidence_documents"])
    assert all(doc["sha256"] for doc in first["evidence_documents"])


def test_small_document_preserves_full_value_and_provenance() -> None:
    items = [{"gap_id": "GAP-1"}]
    doc = _doc(1, 100)

    ctx, budget = module.build_context(items, [doc], 40_000, 12_000)

    assert budget["included_document_count"] == 1
    assert budget["dropped_document_count"] == 0
    assert ctx["evidence_documents"][0] == doc
    assert ctx["evidence_documents"][0]["sha256"] == doc["sha256"]


def test_projection_keeps_both_ends_and_declares_truncation() -> None:
    doc = _doc(7, 50_000)

    projected = module.project_document(doc, 12_000)
    projection = projected["value_projection"]

    assert projected["path"] == doc["path"]
    assert projected["sha256"] == doc["sha256"]
    assert projection["truncated"] is True
    assert projection["original_char_count"] > 12_000
    assert projection["prefix"]
    assert projection["suffix"]
    assert "source_time" in projection["suffix"]


def test_tiny_context_budget_fails_closed() -> None:
    try:
        module.build_context([{"gap_id": "GAP-1"}], [_doc(1, 100)], 10_000, 12_000)
    except ValueError as exc:
        assert str(exc) == "max_context_chars_below_safe_minimum"
    else:
        raise AssertionError("unsafe context budget must fail closed")


def test_context_contract_exposes_budget_and_never_exceeds_cap() -> None:
    items = [{"gap_id": f"GAP-{index}", "metric_name": "metric"} for index in range(12)]
    docs = [_doc(index, 20_000) for index in range(12)]

    ctx, budget = module.build_context(items, docs, 90_000, 8_000)
    encoded = json.dumps(ctx, sort_keys=True, separators=(",", ":"))

    assert ctx["contract"] == "EVIDENCE_GAP_VALIDATION_INPUT_v1_1_TOKEN_BOUNDED"
    assert len(encoded) == budget["context_char_count"]
    assert len(encoded) <= 90_000
    assert ctx["context_budget"]["included_document_count"] == budget["included_document_count"]
    assert ctx["context_budget"]["dropped_document_count"] == budget["dropped_document_count"]
