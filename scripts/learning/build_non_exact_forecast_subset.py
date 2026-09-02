#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from scripts.lib.forecast_settlement_contract import SETTLEMENT_EXACT_TARGET_TIME_V1


def build_subset(forecast_root: Path, output_root: Path) -> dict[str, int]:
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    copied = excluded_exact = skipped_non_forecast = 0
    for path in sorted(forecast_root.rglob("*.json")) if forecast_root.exists() else []:
        value = json.loads(path.read_text())
        if value.get("contract") != "FROZEN_FORECAST_v1":
            skipped_non_forecast += 1
            continue
        if value.get("settlement_contract_version") == SETTLEMENT_EXACT_TARGET_TIME_V1:
            excluded_exact += 1
            continue
        relative = path.relative_to(forecast_root)
        destination = output_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(path.read_bytes())
        copied += 1

    return {
        "copied_non_exact_forecasts": copied,
        "excluded_exact_forecasts": excluded_exact,
        "skipped_non_forecast_json": skipped_non_forecast,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forecast-root", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    args = ap.parse_args()
    result = build_subset(args.forecast_root, args.output_root)
    result.update({
        "status": "PASS",
        "exact_settlement_visible_to_legacy_engine": False,
    })
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
