#!/usr/bin/env python3
"""Compatibility wrapper around the Entry Signal owner plus optional auto-state materialization."""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from entry_signal.entry_signal_ledger_core import *  # noqa: F401,F403


def _materialize_auto_market_state() -> None:
    try:
        from data_ping.auto_market_state import assemble_and_write
        result = assemble_and_write(
            repo_root=Path.cwd(),
            output_root=Path("04_MARKET_LEARNING/entry_signals/auto_market_state"),
        )
        print(json.dumps({"auto_market_state": result}, sort_keys=True))
    except Exception as exc:
        # The state assembler is optional QA/aggregation. Its failure must not
        # suppress a healthy Entry Signal owner or become market evidence.
        print(json.dumps({
            "auto_market_state": {
                "status": "DEGRADED_OPTIONAL_ASSEMBLER_FAILURE",
                "error_class": type(exc).__name__,
                "error": str(exc),
                "market_interpretation": "NONE",
                "entry_signal_owner_suppressed": False,
            }
        }, sort_keys=True), file=sys.stderr)


if __name__ == "__main__":
    main()  # imported unchanged from entry_signal_ledger_core
    _materialize_auto_market_state()
