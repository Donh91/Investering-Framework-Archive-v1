#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import experiment_lifecycle as lifecycle  # noqa: E402

CONTRACT = "DAILY_DIRECTOR_CONFIDENCE_BINDING_v1"
HEADER_RE = re.compile(
    r"^CYCLE_HEADER \| PHASE=([^|\n]+?) \| WARNING=([^|\n]+?) \| "
    r"DIRECTION=([^|\n]+?) \| CONFIDENCE=(LOW|MEDIUM|HIGH)$"
)


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object_required:{path}")
    return value


def parse_header(summary: Any) -> dict[str, str] | None:
    if not isinstance(summary, str):
        return None
    first_line = summary.splitlines()[0].strip() if summary.splitlines() else ""
    match = HEADER_RE.fullmatch(first_line)
    if not match:
        return None
    return {
        "phase": match.group(1).strip(),
        "warning": match.group(2).strip(),
        "direction": match.group(3).strip(),
        "confidence": match.group(4),
        "raw": first_line,
    }


def direct_candidate_ids(output: dict[str, Any], context: dict[str, Any]) -> list[str]:
    latest = ((context.get("latest_capture") or {}).get("market_metrics") or {})
    specs: list[dict[str, Any]] = []
    for raw in output.get("experiment_candidates") or []:
        if isinstance(raw, dict):
            try:
                specs.append(lifecycle.normalize(raw))
            except Exception:
                continue
    for raw in output.get("forecast_candidates") or []:
        if not isinstance(raw, dict):
            continue
        mapped = lifecycle.from_forecast(raw, latest)
        if mapped is None:
            continue
        try:
            specs.append(lifecycle.normalize(mapped))
        except Exception:
            continue
    return sorted({"EC-" + lifecycle.sha(lifecycle.identity_spec(spec))[:20] for spec in specs})


def linked_forecast_ids(forecast_root: Path, candidate_ids: list[str], frozen_at_utc: str | None) -> list[str]:
    if not candidate_ids or not frozen_at_utc or not forecast_root.exists():
        return []
    allowed = set(candidate_ids)
    result: set[str] = set()
    for path in forecast_root.rglob("*.json"):
        try:
            value = read(path)
        except Exception:
            continue
        if value.get("contract") != "FROZEN_FORECAST_v1":
            continue
        if value.get("source_candidate_id") not in allowed or value.get("frozen_at_utc") != frozen_at_utc:
            continue
        forecast_id = value.get("forecast_id")
        if isinstance(forecast_id, str) and forecast_id:
            result.add(forecast_id)
    return sorted(result)


def build_binding(
    output: dict[str, Any],
    context: dict[str, Any],
    receipt: dict[str, Any],
    *,
    output_path: str,
    context_path: str,
    receipt_path: str,
    forecast_root: Path,
) -> dict[str, Any] | None:
    header = parse_header(output.get("summary"))
    if header is None:
        return None
    candidate_ids = direct_candidate_ids(output, context)
    frozen_at = (context.get("latest_capture") or {}).get("captured_at_utc")
    forecast_ids = linked_forecast_ids(forecast_root, candidate_ids, frozen_at)
    source = {
        "daily_output_path": output_path,
        "daily_output_sha256": sha(output),
        "daily_context_path": context_path,
        "daily_context_sha256": sha(context),
        "daily_receipt_path": receipt_path,
        "daily_receipt_sha256": sha(receipt),
        "source_run_id": (context.get("latest_capture") or {}).get("run_id"),
        "source_captured_at_utc": frozen_at,
    }
    identity = {"source": source, "cycle_header": header, "candidate_ids": candidate_ids, "forecast_ids": forecast_ids}
    return {
        "contract": CONTRACT,
        "binding_id": "DCB-" + sha(identity)[:20],
        "status": "BOUND",
        "bound_at_utc": frozen_at,
        "cycle_header": header,
        "emitted_candidate_ids": candidate_ids,
        "emitted_forecast_ids": forecast_ids,
        "source": source,
        "calibration_boundary": {
            "historical_prose_backfill": False,
            "automatic_confidence_tuning": False,
            "market_rule_change": False,
            "portfolio_action": False,
            "eligible_future_outcomes": "CAUSALLY_LINKED_MATURED_NON_CENSORED_ONLY",
        },
    }


def materialize(binding_root: Path, binding: dict[str, Any]) -> Path:
    timestamp = str(binding.get("bound_at_utc") or "")
    if len(timestamp) < 10:
        raise ValueError("source_captured_at_utc_required")
    path = binding_root / timestamp[:4] / timestamp[5:7] / timestamp[8:10] / f"{binding['binding_id']}.json"
    payload = canonical(binding)
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError("IMMUTABLE_BINDING_CONFLICT")
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--daily-output", type=Path, required=True)
    parser.add_argument("--daily-context", type=Path, required=True)
    parser.add_argument("--daily-receipt", type=Path, required=True)
    parser.add_argument("--forecast-root", type=Path, required=True)
    parser.add_argument("--binding-root", type=Path, required=True)
    args = parser.parse_args()

    output = read(args.daily_output)
    context = read(args.daily_context)
    receipt = read(args.daily_receipt)
    binding = build_binding(
        output,
        context,
        receipt,
        output_path=str(args.daily_output),
        context_path=str(args.daily_context),
        receipt_path=str(args.daily_receipt),
        forecast_root=args.forecast_root,
    )
    if binding is None:
        print(json.dumps({"status": "CONFIDENCE_BINDING_UNAVAILABLE", "reason": "MISSING_OR_MALFORMED_CYCLE_HEADER"}, sort_keys=True))
        return
    path = materialize(args.binding_root, binding)
    print(json.dumps({"status": "BOUND", "binding_id": binding["binding_id"], "path": str(path)}, sort_keys=True))


if __name__ == "__main__":
    main()
