from __future__ import annotations

import importlib.util
import json
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[2]/"scripts/health/build_operations_dashboard.py"
spec=importlib.util.spec_from_file_location("build_operations_dashboard",SCRIPT); module=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module)


def test_weekly_pointer_accepts_semantic_package_hash(tmp_path: Path) -> None:
    (tmp_path/"package.json").write_text(json.dumps({"contract":"MASTER_MONDAY_MACHINE_PACKAGE_v1","package_sha256":"semantic-hash","generated_at_utc":"2026-08-24T00:00:00Z"})+"\n")
    value,path,status=module.verified_weekly_target(tmp_path,{"machine_package_path":"package.json","machine_package_sha256":"semantic-hash"})
    assert status=="MATCH" and path=="package.json" and value["package_sha256"]=="semantic-hash"
    assert module.sha256_path(tmp_path/"package.json")!="semantic-hash"


def test_weekly_pointer_rejects_wrong_semantic_hash(tmp_path: Path) -> None:
    (tmp_path/"package.json").write_text(json.dumps({"contract":"MASTER_MONDAY_MACHINE_PACKAGE_v1","package_sha256":"x"})+"\n")
    value,path,status=module.verified_weekly_target(tmp_path,{"machine_package_path":"package.json","machine_package_sha256":"wrong"})
    assert value is None and path=="package.json" and status=="TARGET_HASH_MISMATCH"
