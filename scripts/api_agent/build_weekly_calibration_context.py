from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--weekly-pointer", type=Path, required=True)
    parser.add_argument("--daily-output-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    weekly = load_json(args.weekly_pointer)
    outputs = []
    for path in sorted(args.daily_output_root.rglob("DAILY_DIRECTOR_OUTPUT.json"))[-7:]:
        try:
            value = load_json(path)
        except Exception:
            continue
        receipt_path = path.with_name("DAILY_DIRECTOR_RECEIPT.json")
        receipt = load_json(receipt_path) if receipt_path.exists() else None
        outputs.append({"path": str(path), "output": value, "receipt": receipt})

    context = {
        "contract": "WEEKLY_API_CALIBRATION_CONTEXT_v1",
        "authority": "SHADOW_ONLY",
        "weekly_capture_pack": weekly,
        "daily_director_rows": outputs,
        "daily_director_count": len(outputs),
        "handoff_targets": ["RAW_WEEKLY_CALIBRATION", "FORECAST_LEDGER", "MASTER_MONDAY_PREP", "SPECIALIST_REVIEW"],
        "rules": [
            "Do not rewrite frozen forecasts.",
            "Separate data quality from market evidence.",
            "Preserve disagreement, missingness and censored outcomes.",
            "No framework-state, model-weight or portfolio authority.",
        ],
    }
    context["context_hash"] = hashlib.sha256(canonical(context)).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical(context))
    print(json.dumps({"status": "PASS", "daily_rows": len(outputs), "context_hash": context["context_hash"]}, sort_keys=True))


if __name__ == "__main__":
    main()
