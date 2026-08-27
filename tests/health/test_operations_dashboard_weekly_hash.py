from __future__ import annotations

import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/health/build_operations_dashboard.py"
spec = importlib.util.spec_from_file_location("build_operations_dashboard", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_weekly_pointer_uses_semantic_package_hash(tmp_path: Path) -> None:
    package = tmp_path / "package.json"
    package.write_text(json.dumps({
        "contract": "MASTER_MONDAY_MACHINE_PACKAGE_v1",
        "package_sha256": "semantic-hash",
        "generated_at_utc": "2026-08-24T00:00:00Z",
    }) + "\n")
    pointer = tmp_path / "pointer.json"
    pointer.write_text(json.dumps({"path": "package.json", "sha256": "semantic-hash"}) + "\n")
    result = module.verified_weekly_target(tmp_path, "pointer.json")
    assert result["hash_status"] == "MATCH"
    assert result["hash_mode"] == "SEMANTIC_PACKAGE_HASH"
    assert result["raw_file_sha256"] != "semantic-hash"


def test_weekly_pointer_rejects_wrong_contract(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(json.dumps({"contract": "OTHER", "package_sha256": "x"}))
    (tmp_path / "pointer.json").write_text(json.dumps({"path": "package.json", "sha256": "x"}))
    result = module.verified_weekly_target(tmp_path, "pointer.json")
    assert result["hash_status"] == "MISMATCH"
    assert result["contract_status"] == "MISMATCH"
