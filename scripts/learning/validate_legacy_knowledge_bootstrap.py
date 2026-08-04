from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_AUTHORITY = {
    "portfolio_action": False,
    "framework_state_change": False,
    "model_weight_change": False,
    "canonical_promotion": False,
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(root: Path) -> dict:
    errors: list[str] = []
    source_registry = load_json(root / "SOURCE_THREAD_REGISTRY.json")
    sensor_map = load_json(root / "05_NEW_SYSTEM_CROSSWALK/LEGACY_TO_CURRENT_SENSOR_MAP.json")
    queue = load_json(root / "05_NEW_SYSTEM_CROSSWALK/PROSPECTIVE_VALIDATION_QUEUE.json")

    if source_registry.get("raw_exports_public") is not False:
        errors.append("RAW_EXPORT_PUBLICATION_NOT_FORBIDDEN")
    if sensor_map.get("rules", {}).get("automatic_forecast_freeze") is not False:
        errors.append("AUTOMATIC_FORECAST_FREEZE_NOT_DISABLED")

    hypotheses: dict[str, dict] = {}
    path = root / "02_HYPOTHESIS_REGISTRY/ACTIVE_LEGACY_HYPOTHESES.jsonl"
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError:
            errors.append(f"INVALID_JSONL:{line_no}")
            continue
        hid = row.get("legacy_observation_id")
        if not isinstance(hid, str) or not hid.startswith("LKO-"):
            errors.append(f"INVALID_ID:{line_no}")
            continue
        if hid in hypotheses:
            errors.append(f"DUPLICATE_ID:{hid}")
        hypotheses[hid] = row
        if row.get("canonical_evidence") is not False:
            errors.append(f"CANONICAL_EVIDENCE_FORBIDDEN:{hid}")
        if row.get("evidence_level") not in {"L0", "L1", "L2"}:
            errors.append(f"INVALID_LEGACY_LEVEL:{hid}")
        if row.get("authority") != REQUIRED_AUTHORITY:
            errors.append(f"INVALID_AUTHORITY:{hid}")
        if not row.get("sensors"):
            errors.append(f"MISSING_SENSORS:{hid}")

    for item in queue.get("queue", []):
        hid = item.get("hypothesis_id")
        if hid not in hypotheses:
            errors.append(f"QUEUE_UNKNOWN_HYPOTHESIS:{hid}")
        if item.get("candidate_freeze_allowed") is not False:
            errors.append(f"QUEUE_FREEZE_ALLOWED:{hid}")
        if item.get("automatic_promotion") is not False:
            errors.append(f"QUEUE_PROMOTION_ALLOWED:{hid}")

    return {
        "contract": "LEGACY_KNOWLEDGE_BOOTSTRAP_VALIDATION_v1",
        "status": "PASS" if not errors else "FAIL",
        "hypothesis_count": len(hypotheses),
        "queue_count": len(queue.get("queue", [])),
        "errors": errors,
        "authority": REQUIRED_AUTHORITY,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate(args.root)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
