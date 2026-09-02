from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

MUTABLE_CAPTURE_FILENAMES = frozenset({"LATEST.json"})


def _is_archived_capture_path(root: Path, path: Path) -> bool:
    if path.name in MUTABLE_CAPTURE_FILENAMES or path.is_symlink():
        return False
    try:
        relative = path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError("BASELINE_CAPTURE_OUTSIDE_ARCHIVE_ROOT") from exc
    if not relative.parts:
        return False
    year = relative.parts[0]
    return len(year) == 4 and year.isdigit()


def select_archived_baseline(
    capture_root: Path,
    metric: str,
    decision_at: datetime,
    *,
    metric_value: Callable[[dict[str, Any], str], Any],
    evidence_timestamp: Callable[[dict[str, Any]], datetime],
) -> tuple[Path, dict[str, Any], datetime]:
    """Choose the latest immutable archived metric observation at/before decision.

    Mutable pointers are never admissible. If the most recent eligible timestamp
    contains conflicting values for the same metric, selection fails closed rather
    than resolving the conflict by filename ordering.
    """
    root = capture_root.resolve()
    eligible: list[tuple[datetime, Path, dict[str, Any], float]] = []
    for path in sorted(capture_root.rglob("*.json")) if capture_root.exists() else []:
        if not _is_archived_capture_path(root, path):
            continue
        try:
            value = json.loads(path.read_text())
            observed = evidence_timestamp(value)
        except Exception:
            continue
        if observed > decision_at:
            continue
        start = metric_value(value, metric)
        if not isinstance(start, (int, float)) or isinstance(start, bool):
            continue
        eligible.append((observed, path, value, float(start)))

    if not eligible:
        raise ValueError("NO_ARCHIVED_BASELINE_EVIDENCE_AT_OR_BEFORE_RATIFICATION_DECISION")

    latest_at = max(row[0] for row in eligible)
    latest = [row for row in eligible if row[0] == latest_at]
    distinct_values = {row[3] for row in latest}
    if len(distinct_values) != 1:
        raise ValueError("AMBIGUOUS_BASELINE_CAPTURE_AT_DECISION")

    latest.sort(key=lambda row: row[1].as_posix())
    observed, path, value, _ = latest[0]
    return path, value, observed
