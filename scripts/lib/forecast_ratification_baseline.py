from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable

MUTABLE_CAPTURE_FILENAMES = frozenset({"LATEST.json"})
MAX_BASELINE_AGE_MINUTES = 60


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
    max_age_minutes: int = MAX_BASELINE_AGE_MINUTES,
) -> tuple[Path, dict[str, Any], datetime]:
    """Choose the freshest immutable archived capture at/before owner decision.

    Selection is capture-first, never metric-history-first. The function first
    identifies the newest immutable archived capture timestamp at/before the
    owner decision. Only captures at that timestamp may supply the baseline
    metric. If the metric disappeared because of schema/path drift, selection
    fails closed rather than reaching backwards to the last historical document
    where the old path happened to resolve.

    A separate age ceiling protects against a capture-system outage making an
    otherwise "freshest" document scientifically stale.
    """
    if max_age_minutes <= 0:
        raise ValueError("INVALID_BASELINE_MAX_AGE_MINUTES")

    root = capture_root.resolve()
    candidates: list[tuple[datetime, Path, dict[str, Any]]] = []
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
        candidates.append((observed, path, value))

    if not candidates:
        raise ValueError("NO_ARCHIVED_BASELINE_EVIDENCE_AT_OR_BEFORE_RATIFICATION_DECISION")

    latest_at = max(row[0] for row in candidates)
    if decision_at - latest_at > timedelta(minutes=max_age_minutes):
        raise ValueError("FRESHEST_ARCHIVED_BASELINE_CAPTURE_STALE")

    latest = [row for row in candidates if row[0] == latest_at]
    metric_rows: list[tuple[datetime, Path, dict[str, Any], float]] = []
    for observed, path, value in latest:
        start = metric_value(value, metric)
        if isinstance(start, (int, float)) and not isinstance(start, bool):
            metric_rows.append((observed, path, value, float(start)))

    if not metric_rows:
        raise ValueError("BASELINE_METRIC_UNAVAILABLE_IN_FRESHEST_ARCHIVED_CAPTURE")

    distinct_values = {row[3] for row in metric_rows}
    if len(distinct_values) != 1:
        raise ValueError("AMBIGUOUS_BASELINE_CAPTURE_AT_DECISION")

    metric_rows.sort(key=lambda row: row[1].as_posix())
    observed, path, value, _ = metric_rows[0]
    return path, value, observed
