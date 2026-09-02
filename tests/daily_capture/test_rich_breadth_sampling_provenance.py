import hashlib
import json
from pathlib import Path

import pytest

from scripts.daily_capture import rich_breadth_checkpoint as runtime


WORKFLOW = Path(".github/workflows/adaptive-rotation-cadence.yml")


def cadence_document(run_id="gh-42-3", *, boost_active=True):
    return {
        "generated_at_utc": "2026-09-01T00:00:00Z",
        "cadence_contract": "ADAPTIVE_ROTATION_CADENCE_v1",
        "authority": "OPERATIONAL_SAMPLING_ONLY_NON_BINDING",
        "source_run_id": run_id,
        "source_workflow": "adaptive-rotation-cadence.yml",
        "normal_cadence_hours": 4,
        "boost_cadence_hours": 2,
        "boost_active": boost_active,
        "market_semantics_changed": False,
        "thresholds_changed": False,
    }


def write_parent(root, value=None):
    path = root / "03_DAILY_CAPTURE_LOGS/cadence/2026/09/01/cadence-42-3.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(value or cadence_document()) + "\n", encoding="utf-8")
    return path


def test_adaptive_provenance_binds_exact_parent_observation(tmp_path, monkeypatch):
    monkeypatch.setattr(runtime, "ROOT", tmp_path)
    parent = write_parent(tmp_path)
    provenance = runtime.sampling_provenance(
        runtime.ADAPTIVE_BOOST,
        parent_run_id="gh-42-3",
        parent_cadence_observation=parent.relative_to(tmp_path).as_posix(),
    )
    assert provenance["sampling_mode"] == "ADAPTIVE_BOOST"
    assert provenance["capture_origin"] == "ADAPTIVE_ROTATION_CADENCE"
    assert provenance["parent_cadence_run_id"] == "gh-42-3"
    assert provenance["parent_cadence_observation_path"] == parent.relative_to(tmp_path).as_posix()
    assert provenance["parent_cadence_observation_sha256"] == hashlib.sha256(parent.read_bytes()).hexdigest()
    assert provenance["adaptive_selection"] is True
    assert provenance["can_create_market_evidence"] is False
    assert provenance["can_create_rotation_vote"] is False
    assert provenance["can_create_portfolio_permission"] is False
    assert provenance["can_change_canonical_state"] is False


@pytest.mark.parametrize(
    "parent_run_id,parent_value",
    [
        (None, cadence_document()),
        ("gh-42-3", cadence_document(run_id="gh-other-1")),
        ("gh-42-3", cadence_document(boost_active=False)),
    ],
)
def test_adaptive_provenance_fails_closed_without_matching_active_parent(
    tmp_path, monkeypatch, parent_run_id, parent_value
):
    monkeypatch.setattr(runtime, "ROOT", tmp_path)
    parent = write_parent(tmp_path, parent_value)
    with pytest.raises(ValueError):
        runtime.sampling_provenance(
            runtime.ADAPTIVE_BOOST,
            parent_run_id=parent_run_id,
            parent_cadence_observation=parent.relative_to(tmp_path).as_posix(),
        )


def test_ordinary_checkpoint_is_explicit_and_cannot_claim_adaptive_parent(monkeypatch):
    monkeypatch.setenv("GITHUB_RUN_ID", "77")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "2")
    provenance = runtime.sampling_provenance(runtime.ORDINARY_CHECKPOINT)
    assert provenance["sampling_mode"] == "ORDINARY_CHECKPOINT"
    assert provenance["capture_origin"] == "RICH_BREADTH_CHECKPOINT"
    assert provenance["capture_run_id"] == "gh-77-2"
    assert provenance["parent_cadence_run_id"] is None
    assert provenance["adaptive_selection"] is False
    with pytest.raises(ValueError):
        runtime.sampling_provenance(
            runtime.ORDINARY_CHECKPOINT,
            parent_run_id="gh-77-2",
            parent_cadence_observation="cadence.json",
        )


def test_adaptive_main_writes_self_describing_checkpoint(tmp_path, monkeypatch):
    monkeypatch.setattr(runtime, "ROOT", tmp_path)
    parent = write_parent(tmp_path)
    monkeypatch.setenv("GITHUB_RUN_ID", "42")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "3")
    monkeypatch.setattr(runtime.owner, "fetch", lambda _url: b"fixture")
    monkeypatch.setattr(
        runtime.owner,
        "parse",
        lambda _raw: ([{"asset_id": "bitcoin"}], [], {"advance_ratio": 0.5}),
    )
    monkeypatch.setattr(
        runtime.owner,
        "owner_interface",
        lambda _aggregate, retrieval: {
            "observation": {
                "cutoff_utc": retrieval,
                "retrieval_timestamp_utc": retrieval,
                "window_semantics": "SOURCE_REPORTED_ROLLING_24H_AT_RETRIEVAL",
            }
        },
    )
    output = tmp_path / "breadth"
    assert runtime.main(
        [
            "--output-root",
            str(output),
            "--sampling-mode",
            "ADAPTIVE_BOOST",
            "--parent-run-id",
            "gh-42-3",
            "--parent-cadence-observation",
            parent.relative_to(tmp_path).as_posix(),
        ]
    ) == 0
    payload = json.loads((output / "LATEST.json").read_text())
    assert payload["contract"] == "RICH_BREADTH_CHECKPOINT_v1"
    assert payload["sampling_provenance"]["sampling_mode"] == "ADAPTIVE_BOOST"
    assert payload["sampling_provenance"]["capture_run_id"] == "gh-42-3"
    assert payload["authority"]["binding"] is False


def test_workflow_preserves_thresholds_and_binds_boost_capture_to_gate_run():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "cron: '16 0,4,8,12,16,20 * * *'" in text
    assert "normal_cadence_hours': 4" in text
    assert "boost_cadence_hours': 2" in text
    assert "distance_pct <= 0.01" in text
    assert "breadth >= 0.45" in text
    assert "--sampling-mode ADAPTIVE_BOOST" in text
    assert '--parent-run-id "${{ steps.gate.outputs.cadence_run_id }}"' in text
    assert '--parent-cadence-observation "${{ steps.gate.outputs.cadence_observation_path }}"' in text
    assert "market_semantics_changed': False" in text
    assert "thresholds_changed': False" in text
