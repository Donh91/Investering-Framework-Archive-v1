#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.lib.forecast_settlement_contract import (  # noqa: E402
    SETTLEMENT_EXACT_TARGET_TIME_V1,
    supports_exact_price_settlement,
)

QUALIFIED = "QUALIFIED_FOR_FORWARD_TEST"


def canonical(value: dict) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def untracked_json_files(repo_root: Path, forecast_root: Path) -> list[Path]:
    repo_root = repo_root.resolve()
    forecast_root = forecast_root.resolve()
    try:
        rel = forecast_root.relative_to(repo_root)
    except ValueError as exc:
        raise SystemExit("FORECAST_ROOT_MUST_BE_INSIDE_REPOSITORY") from exc
    proc = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "--", rel.as_posix()],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    paths = []
    for row in proc.stdout.splitlines():
        path = repo_root / row.strip()
        if path.suffix == ".json" and path.is_file():
            paths.append(path)
    return sorted(paths)


def activate(path: Path) -> str:
    value = json.loads(path.read_text())
    if value.get("contract") != "FROZEN_FORECAST_v1":
        return "SKIPPED_NOT_FROZEN_FORECAST"
    if value.get("scientific_admission_status") != QUALIFIED:
        return "SKIPPED_NOT_SCIENTIFICALLY_ADMITTED"
    metric_path = str(value.get("metric_path") or "")
    if not supports_exact_price_settlement(metric_path):
        return "SKIPPED_UNSUPPORTED_METRIC"
    existing = value.get("settlement_contract_version")
    if existing not in (None, SETTLEMENT_EXACT_TARGET_TIME_V1):
        raise SystemExit(f"SETTLEMENT_CONTRACT_CONFLICT:{path}:{existing}")
    if existing == SETTLEMENT_EXACT_TARGET_TIME_V1:
        return "ALREADY_EXACT"
    value["settlement_contract_version"] = SETTLEMENT_EXACT_TARGET_TIME_V1
    value["settlement_activation_semantics"] = "PRE_FIRST_CANONICAL_PERSISTENCE_UNTRACKED_FORECAST_ONLY"
    path.write_text(canonical(value))
    return "ACTIVATED_EXACT_SETTLEMENT"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--forecast-root", type=Path, required=True)
    args = ap.parse_args()
    repo_root = args.repo_root.resolve()
    files = untracked_json_files(repo_root, args.forecast_root)
    counts: dict[str, int] = {}
    activated: list[str] = []
    for path in files:
        status = activate(path)
        counts[status] = counts.get(status, 0) + 1
        if status == "ACTIVATED_EXACT_SETTLEMENT":
            activated.append(path.relative_to(repo_root).as_posix())
    print(json.dumps({
        "status": "PASS",
        "untracked_forecast_files_scanned": len(files),
        "counts": counts,
        "activated_paths": activated,
        "historical_tracked_forecasts_modified": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
