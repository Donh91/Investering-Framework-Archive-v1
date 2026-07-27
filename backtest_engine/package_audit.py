from __future__ import annotations

import json
import re
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from .utils import sha256_bytes, sha256_file

_CHECKSUM_RE = re.compile(r"^([0-9a-fA-F]{64})\s+[* ]?(.+?)\s*$")


@dataclass(frozen=True)
class PackageAudit:
    path: str
    bytes: int
    sha256: str
    zip_members: int
    zip_crc_status: str
    checksum_file: str | None
    checksum_entries: int
    checksum_mismatches: int
    missing_checksum_targets: int
    manifest_files_claimed: int | None
    manifest_self_reference_defect: bool
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _resolve_checksum_target(names: set[str], checksum_name: str, target: str) -> str | None:
    normalized = str(PurePosixPath(target))
    if normalized in names:
        return normalized
    root = str(PurePosixPath(checksum_name).parent)
    candidate = str(PurePosixPath(root) / normalized)
    if candidate in names:
        return candidate
    top = checksum_name.split("/", 1)[0]
    candidate = str(PurePosixPath(top) / normalized)
    if candidate in names:
        return candidate
    matches = [name for name in names if PurePosixPath(name).name == PurePosixPath(normalized).name]
    return matches[0] if len(matches) == 1 else None


def _find_checksum_file(names: list[str]) -> str | None:
    preferred = [name for name in names if PurePosixPath(name).name in {"CHECKSUMS.sha256", "backtest_file_checksums.sha256"}]
    if preferred:
        preferred.sort(key=lambda value: (0 if value.endswith("CHECKSUMS.sha256") else 1, len(value)))
        return preferred[0]
    generic = [name for name in names if name.lower().endswith("checksums.sha256") or name.lower().endswith("checksum.sha256")]
    return sorted(generic, key=len)[0] if generic else None


def audit_zip(path: Path) -> PackageAudit:
    if not path.exists():
        raise FileNotFoundError(path)
    if not zipfile.is_zipfile(path):
        raise ValueError(f"not a ZIP archive: {path}")

    outer_sha = sha256_file(path)
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        name_set = set(names)
        bad_crc = archive.testzip()
        crc_status = "PASS" if bad_crc is None else f"FAIL:{bad_crc}"

        checksum_name = _find_checksum_file(names)
        checksum_entries = 0
        mismatches = 0
        missing = 0
        if checksum_name:
            text = archive.read(checksum_name).decode("utf-8-sig", errors="strict")
            for line in text.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                match = _CHECKSUM_RE.match(line)
                if not match:
                    continue
                expected, target = match.groups()
                checksum_entries += 1
                resolved = _resolve_checksum_target(name_set, checksum_name, target)
                if resolved is None:
                    missing += 1
                    continue
                actual = sha256_bytes(archive.read(resolved))
                if actual.lower() != expected.lower():
                    mismatches += 1

        manifest_name = next((name for name in names if PurePosixPath(name).name == "manifest.json"), None)
        manifest_claimed: int | None = None
        manifest_self_defect = False
        if manifest_name:
            try:
                manifest = json.loads(archive.read(manifest_name).decode("utf-8-sig"))
                claimed = manifest.get("file_count")
                if isinstance(claimed, int):
                    manifest_claimed = claimed
                files = manifest.get("files")
                if isinstance(files, list):
                    for item in files:
                        if not isinstance(item, dict):
                            continue
                        item_path = str(item.get("path") or item.get("filename") or "")
                        if PurePosixPath(item_path).name != "manifest.json":
                            continue
                        resolved = _resolve_checksum_target(name_set, manifest_name, item_path)
                        if resolved is None:
                            manifest_self_defect = True
                            continue
                        payload = archive.read(resolved)
                        claimed_bytes = item.get("bytes") or item.get("size")
                        claimed_sha = item.get("sha256")
                        if claimed_bytes is not None and int(claimed_bytes) != len(payload):
                            manifest_self_defect = True
                        if claimed_sha is not None and str(claimed_sha).lower() != sha256_bytes(payload).lower():
                            manifest_self_defect = True
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError):
                manifest_self_defect = True

    status = "PASS"
    if crc_status != "PASS" or mismatches or missing:
        status = "FAIL"
    elif manifest_self_defect:
        status = "PASS_WITH_MANIFEST_SELF_REFERENCE_DEFECT"

    return PackageAudit(
        path=str(path),
        bytes=path.stat().st_size,
        sha256=outer_sha,
        zip_members=len(names),
        zip_crc_status=crc_status,
        checksum_file=checksum_name,
        checksum_entries=checksum_entries,
        checksum_mismatches=mismatches,
        missing_checksum_targets=missing,
        manifest_files_claimed=manifest_claimed,
        manifest_self_reference_defect=manifest_self_defect,
        status=status,
    )
