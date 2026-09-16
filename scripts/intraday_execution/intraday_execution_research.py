#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

# Direct execution by path puts scripts/intraday_execution first on sys.path.
# Add the repository root so the shared hourly owner can be imported reliably.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.daily_capture.hourly_sequence_consumer import read_complete_spot_window
from scripts.intraday_execution import intraday_execution_research_core as _core
from scripts.intraday_execution.intraday_execution_research_core import *  # noqa: F401,F403


# Keep the canonical module as the public runtime surface. Existing tests and
# callers legitimately override these bindings on this module; the core split
# must not silently bypass those overrides.
_RUNTIME_BINDINGS = (
    "ROOT",
    "OBS",
    "EVENTS",
    "LATEST",
    "STATE",
    "SUMMARY",
    "CONFIG",
    "ENTRY",
    "PULLBACK",
    "BREADTH",
    "HOURLY_POINTER",
    "now_utc",
)


def _sync_runtime_bindings() -> None:
    for name in _RUNTIME_BINDINGS:
        setattr(_core, name, globals()[name])


def hourly_rows():
    return read_complete_spot_window(
        _core.HOURLY_POINTER,
        Path("03_DAILY_CAPTURE_LOGS/hourly"),
        minimum_rows=6,
    )


def main():
    _sync_runtime_bindings()
    # Core functions such as build_snapshot resolve hourly_rows in the core
    # module's global namespace, so bind the shared owner for this execution.
    _core.hourly_rows = hourly_rows
    return _core.main()


# Imported core helpers that call hourly_rows directly retain the shared owner.
_core.hourly_rows = hourly_rows


if __name__ == "__main__":
    main()
