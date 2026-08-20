#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import build_historical_altseason_bundle as base

REPO = base.REPO
LAB = REPO / "06_RESEARCH_LAB" / "historical_altseason_pullback_v1"
ART = LAB / "artifacts"
PROMPT_DIR = REPO / "07_PROMPTS_AND_AGENTS" / "historical_altseason_pullback"
DIST = base.DIST
ZIP_PATH = base.ZIP_PATH
MANIFEST_PATH = base.MANIFEST_PATH
SHA_PATH = base.SHA_PATH
STAGE = DIST / "COWORK_RESEARCH_HANDOFF"

HANDOFF_FILES = [
    base.PROMPT,
    PROMPT_DIR / "COWORK_OPUS5_LAUNCH_INSTRUCTION.md",
    PROMPT_DIR / "COWORK_OPUS5_MAX_VALUE_SIDECARS.md",
    PROMPT_DIR / "COWORK_GITHUB_RESEARCH_MAP.md",
    LAB / "COWORK_READINESS_PROTOCOL.md",
    LAB / "COWORK_OPUS5_RESEARCH_PROTOCOL_ADDENDUM.md",
    LAB / "INTRADAY_EXECUTION_COWORK_ADDENDUM.md",
    LAB / "CLAUDE_COWORK_DEEP_RESEARCH_BRIEF.md",
    LAB / "config.json",
    ART / "RESEARCH_READINESS_MANIFEST.json",
    ART / "CFGI_BILLING.json",
    ART / "CFGI_FIELD_COVERAGE.json",
    ART / "CFGI_COVERAGE.json",
    ART / "FREE_BULK_ARTIFACT_POINTER.json",
    ART / "FREE_SOURCE_AUDIT.json",
    ART / "TIME_INTEGRITY_AUDIT.json",
    REPO / "00_ARCHIVE_CONTROL" / "research_runtime" / "HISTORICAL_ALTSEASON_CFGI_PAID_RESERVATION.json",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    readiness = base.validate_readiness()
    for path in HANDOFF_FILES:
        if not path.exists() or not path.is_file() or path.stat().st_size == 0:
            raise SystemExit(f"COWORK_COMPACT_HANDOFF_BLOCKED missing={path.relative_to(REPO)}")

    if DIST.exists():
        shutil.rmtree(DIST)
    STAGE.mkdir(parents=True, exist_ok=True)

    files = []
    for src in HANDOFF_FILES:
        rel = src.relative_to(REPO)
        dest = STAGE / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        files.append({
            "source_path": rel.as_posix(),
            "size_bytes": src.stat().st_size,
            "sha256": sha256(src),
        })

    manifest = {
        "contract": "COWORK_GITHUB_NATIVE_HANDOFF_MANIFEST_v1",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "repo": "Donh91/Investering-Framework-Archive-v1",
        "authoritative_ref": "main",
        "delivery_model": "COMPACT_INSTRUCTIONS_PLUS_DIRECT_GITHUB_READ",
        "readiness_verdict": readiness["readiness_manifest"]["readiness_verdict"],
        "automatic_promotion": False,
        "historical_findings_max_classification": "FORWARD_TEST",
        "heavy_bulk_delivery": "BOUND_GITHUB_ACTIONS_ARTIFACT_VIA_FREE_BULK_ARTIFACT_POINTER",
        "cowork_entrypoint": "07_PROMPTS_AND_AGENTS/historical_altseason_pullback/COWORK_OPUS5_LAUNCH_INSTRUCTION.md",
        "research_map": "07_PROMPTS_AND_AGENTS/historical_altseason_pullback/COWORK_GITHUB_RESEARCH_MAP.md",
        "expected_output_zip": "HISTORICAL_ALTSEASON_COWORK_OPUS5_RESEARCH_PACKAGE.zip",
        "files": files,
    }
    manifest_dest = STAGE / "COWORK_HANDOFF_MANIFEST.json"
    manifest_dest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(STAGE.rglob("*")):
            if path.is_file():
                zf.write(path, arcname=str(Path("COWORK_RESEARCH_HANDOFF") / path.relative_to(STAGE)))
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        if zf.testzip() is not None:
            raise SystemExit("COWORK_COMPACT_HANDOFF_BLOCKED corrupt_zip")
        names = set(zf.namelist())
        for required in [
            "COWORK_RESEARCH_HANDOFF/COWORK_HANDOFF_MANIFEST.json",
            "COWORK_RESEARCH_HANDOFF/07_PROMPTS_AND_AGENTS/historical_altseason_pullback/COWORK_OPUS5_MASTER_RESEARCH_PROMPT.md",
            "COWORK_RESEARCH_HANDOFF/07_PROMPTS_AND_AGENTS/historical_altseason_pullback/COWORK_OPUS5_LAUNCH_INSTRUCTION.md",
            "COWORK_RESEARCH_HANDOFF/07_PROMPTS_AND_AGENTS/historical_altseason_pullback/COWORK_GITHUB_RESEARCH_MAP.md",
            "COWORK_RESEARCH_HANDOFF/06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts/FREE_BULK_ARTIFACT_POINTER.json",
        ]:
            if required not in names:
                raise SystemExit(f"COWORK_COMPACT_HANDOFF_BLOCKED zip_missing={required}")

    zip_hash = sha256(ZIP_PATH)
    SHA_PATH.write_text(f"{zip_hash}  {ZIP_PATH.name}\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "contract": manifest["contract"],
        "readiness": manifest["readiness_verdict"],
        "handoff_file_count": len(files),
        "zip": str(ZIP_PATH.relative_to(REPO)),
        "zip_sha256": zip_hash,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
