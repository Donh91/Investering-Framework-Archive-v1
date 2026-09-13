from __future__ import annotations

import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/api_agent/augment_director_situation_room_shadow.py"
spec = importlib.util.spec_from_file_location("augment_director_situation_room_shadow", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def _write_valid(tmp_path: Path) -> Path:
    row = tmp_path / "2026-09-10.json"
    row.write_text(json.dumps({
        "authority": "SHADOW_RESEARCH_ONLY_NON_CANONICAL",
        "observation_date_utc": "2026-09-10",
        "status": "SHADOW_HANDOFF_READY",
        "verified_shadow_context": [{
            "shadow_id": "SRSH_1",
            "title": "ECB raises rates as Brent tops 100",
            "event_time_utc": "2026-09-10T06:00:00Z",
            "verification_status": "PRIMARY_LINK_CORROBORATED",
            "verification_method": "SITUATION_ROOM_LINKED_PRIMARY_SOURCE",
            "match_score": 0.7,
            "shared_tokens": ["ecb", "rates"],
            "primary_url": "https://www.ecb.europa.eu/press/example",
            "shadow_admission": "ACCEPTED_VERIFIED_CONTEXT",
        }],
        "pending_verification": [{
            "title": "Unverified discovery",
            "shadow_admission": "NOT_ADMITTED_PENDING_VERIFICATION",
        }],
        "authority_firewall": {
            "canonical_effect": False,
            "market_state_effect": False,
            "portfolio_effect": False,
            "topup_authority": False,
            "execution_authority": False,
        },
    }))
    pointer = tmp_path / "LATEST.json"
    pointer.write_text(json.dumps({
        "authority": "SHADOW_RESEARCH_ONLY_NON_CANONICAL",
        "canonical_effect": False,
        "portfolio_effect": False,
        "path": str(row),
    }))
    return pointer


def test_verified_shadow_is_routed_and_pending_is_not_evidence(tmp_path: Path) -> None:
    pointer = _write_valid(tmp_path)
    out, paths = module.situation_room_shadow(pointer)
    assert out["status"] == "READY"
    assert out["verified_count"] == 1
    assert out["pending_count"] == 1
    assert out["verified_context"][0]["verification_status"] == "PRIMARY_LINK_CORROBORATED"
    assert out["pending_titles_context_only"] == ["Unverified discovery"]
    assert "Pending items are discovery queue metadata, not evidence" in out["instruction"]
    assert len(paths) == 2


def test_authority_breach_fails_closed(tmp_path: Path) -> None:
    pointer = _write_valid(tmp_path)
    row_path = Path(json.loads(pointer.read_text())["path"])
    row = json.loads(row_path.read_text())
    row["authority_firewall"]["portfolio_effect"] = True
    row_path.write_text(json.dumps(row))
    out, _ = module.situation_room_shadow(pointer)
    assert out["status"] == "BLOCKED_AUTHORITY_FIREWALL"


def test_missing_pointer_is_explicit_unavailable(tmp_path: Path) -> None:
    out, paths = module.situation_room_shadow(tmp_path / "missing.json")
    assert out["status"] == "UNAVAILABLE"
    assert out["reason"] == "SITUATION_ROOM_SHADOW_POINTER_MISSING"
    assert paths == []
