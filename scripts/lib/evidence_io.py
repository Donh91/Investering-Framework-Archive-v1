"""Small strict JSON reader: missing evidence is not unreadable evidence."""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Evidence:
    path: str
    state: str
    value: Any = None
    reason: str | None = None


def _finite_float(raw: str) -> float:
    value = float(raw)
    if not math.isfinite(value):
        raise ValueError("NON_FINITE_NUMBER")
    return value


def _reject_constant(raw: str) -> None:
    raise ValueError("NON_FINITE_NUMBER")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("DUPLICATE_OBJECT_KEY")
        value[key] = item
    return value


def load_evidence(path: Path | str) -> Evidence:
    path = Path(path)
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return Evidence(str(path), "MISSING", reason="FILE_NOT_FOUND")
    except (OSError, UnicodeError):
        return Evidence(str(path), "UNREADABLE", reason="READ_ERROR")
    try:
        value = json.loads(raw, parse_float=_finite_float, parse_constant=_reject_constant,
                           object_pairs_hook=_unique_object)
    except (ValueError, RecursionError):
        # Never include exception messages or document fragments in diagnostics.
        return Evidence(str(path), "UNREADABLE", reason="INVALID_JSON")
    return Evidence(str(path), "USABLE", value=value)


def json_evidence_paths(root: Path) -> tuple[list[Path], list[dict[str, str]]]:
    """Do not silently omit an unreadable subtree during accounting."""
    paths = []
    errors = []
    def onerror(exc: OSError) -> None:
        errors.append({"path": str(exc.filename or root), "reason": "DIRECTORY_UNREADABLE"})
    for directory, _, filenames in os.walk(root, onerror=onerror):
        paths.extend(Path(directory) / name for name in filenames if name.endswith(".json"))
    return sorted(paths), errors


def finite_nonnegative(value: Any) -> bool:
    try:
        return type(value) in (int, float) and math.isfinite(value) and value >= 0
    except (OverflowError, ValueError):
        return False


def created_utc(value: dict) -> datetime | None:
    """Require explicit timezones; never infer a machine-local timezone."""
    if "created_unix" in value:
        raw = value["created_unix"]
        if not finite_nonnegative(raw):
            return None
        try:
            return datetime.fromtimestamp(raw, timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    for key in ("created_at_utc", "generated_at_utc", "retrieved_at_utc"):
        if key not in value:
            continue
        raw = value[key]
        if not isinstance(raw, str):
            return None
        try:
            stamp = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            return stamp.astimezone(timezone.utc) if stamp.utcoffset() is not None else None
        except (OverflowError, ValueError):
            return None
    return None


def cost_receipt_identity(value: dict, path: Path, created: datetime) -> tuple:
    """Prefer provider call IDs to a weaker request/creation-time observation."""
    single = value.get('response_id')
    multiple = value.get('response_ids')
    if single is not None and (not isinstance(single, str) or not single.strip()):
        raise ValueError('COST_IDENTITY_INVALID')
    if multiple is not None and (not isinstance(multiple, list) or
            any(not isinstance(x, str) or not x.strip() for x in multiple)):
        raise ValueError('COST_IDENTITY_INVALID')
    if multiple:
        if len(set(multiple)) != len(multiple) or (single is not None and single not in multiple):
            raise ValueError('COST_IDENTITY_INVALID')
        return ('paid_responses', tuple(sorted(multiple)))
    if single is not None:
        return ('paid_responses', (single,))
    request = value.get('request_hash') or value.get('request_sha256')
    return ('request_observation', str(request), created.isoformat()) if request else ('path', str(path))
