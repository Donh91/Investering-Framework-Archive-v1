#!/usr/bin/env python3
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import build_historical_altseason_bundle as base

REPO = base.REPO
SIDECAR = REPO / "07_PROMPTS_AND_AGENTS" / "historical_altseason_pullback" / "COWORK_OPUS5_MAX_VALUE_SIDECARS.md"
LAUNCH = REPO / "07_PROMPTS_AND_AGENTS" / "historical_altseason_pullback" / "COWORK_OPUS5_LAUNCH_INSTRUCTION.md"
INTRADAY = REPO / "04_MARKET_LEARNING" / "intraday_execution"
INTRADAY_SCRIPTS = REPO / "scripts" / "intraday_execution"

for required in [SIDECAR, LAUNCH, INTRADAY, INTRADAY_SCRIPTS]:
    if not required.exists():
        raise SystemExit(f"COWORK_MAX_VALUE_BLOCKED missing={required.relative_to(REPO)}")

# Extend the frozen base bundler without changing readiness, billing or authority semantics.
for path in [SIDECAR, LAUNCH]:
    if path not in base.REQUIRED_BASE:
        base.REQUIRED_BASE.append(path)
    if path not in base.CORE_SELECTED_PATHS:
        base.CORE_SELECTED_PATHS.append(path)

for path in [INTRADAY, INTRADAY_SCRIPTS]:
    if path not in base.PROSPECTIVE_SELECTED_PATHS:
        base.PROSPECTIVE_SELECTED_PATHS.append(path)

base.build_bundle()

manifest = json.loads(base.MANIFEST_PATH.read_text(encoding="utf-8"))
source_paths = {x["source_path"] for x in manifest["files"]}
required_sources = {
    str(SIDECAR.relative_to(REPO)),
    str(LAUNCH.relative_to(REPO)),
}
missing_sources = sorted(required_sources - source_paths)
if missing_sources:
    raise SystemExit(f"COWORK_MAX_VALUE_BLOCKED missing_manifest_sources={missing_sources}")

# Both prospective intraday directories must contribute at least one concrete file.
for prefix in [str(INTRADAY.relative_to(REPO)), str(INTRADAY_SCRIPTS.relative_to(REPO))]:
    if not any(p == prefix or p.startswith(prefix + "/") for p in source_paths):
        raise SystemExit(f"COWORK_MAX_VALUE_BLOCKED intraday_not_bundled={prefix}")

with zipfile.ZipFile(base.ZIP_PATH, "r") as zf:
    if zf.testzip() is not None:
        raise SystemExit("COWORK_MAX_VALUE_BLOCKED corrupt_zip")
    names = set(zf.namelist())
    required_members = {
        "COWORK_RESEARCH_INPUT/CORE/REPO/07_PROMPTS_AND_AGENTS/historical_altseason_pullback/COWORK_OPUS5_MAX_VALUE_SIDECARS.md",
        "COWORK_RESEARCH_INPUT/CORE/REPO/07_PROMPTS_AND_AGENTS/historical_altseason_pullback/COWORK_OPUS5_LAUNCH_INSTRUCTION.md",
        "COWORK_RESEARCH_INPUT/CORE/REPO/06_RESEARCH_LAB/historical_altseason_pullback_v1/INTRADAY_EXECUTION_COWORK_ADDENDUM.md",
    }
    missing_members = sorted(required_members - names)
    if missing_members:
        raise SystemExit(f"COWORK_MAX_VALUE_BLOCKED missing_zip_members={missing_members}")

print(json.dumps({
    "status": "PASS",
    "contract": "COWORK_MAX_VALUE_BUNDLE_EXTENSION_v1",
    "sidecars": True,
    "intraday_execution_data": True,
    "intraday_execution_code": True,
    "launch_instruction": True,
    "readiness": manifest["readiness_verdict"],
    "zip": str(base.ZIP_PATH.relative_to(REPO)),
}, sort_keys=True))
