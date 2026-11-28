"""Post-freeze, non-scoring C5 context. No data collection or API calls."""
from pathlib import Path
from datetime import timezone
import sys

PREREG = "research/programs/MARKET_ANTICIPATION_RESEARCH_PROGRAM_v1/C5_MM_CONTEXT_PREREG_v1.md"
AUTHORITY = "CONTEXT_ONLY_NOT_DECISION_OR_SCORING"

def read_c5_context(root, now):
    root = Path(root).resolve()
    unavailable = {"contract": "C5_MM_CONTEXT_v1", "status": "UNAVAILABLE",
                   "authority": AUTHORITY, "scoring_allowed": False,
                   "as_of_utc": now.astimezone(timezone.utc).isoformat()}
    if not (root / PREREG).is_file():
        return {**unavailable, "reason": "C5_PREREG_NOT_FROZEN"}
    # Support existing script-entry-point execution without a new workflow.
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from scripts.daily_capture.c5_context import build_c5_context, valid_seal
        result = build_c5_context(root, now)
        if (not valid_seal(result) or result.get("contract") != unavailable["contract"]
                or result.get("authority") != AUTHORITY or result.get("scoring_allowed") is not False):
            return {**unavailable, "reason": "C5_CONTEXT_UNVERIFIED"}
        return result
    except (ImportError, OSError, ValueError, TypeError, KeyError, ArithmeticError):
        return {**unavailable, "reason": "C5_ADAPTER_UNAVAILABLE"}
