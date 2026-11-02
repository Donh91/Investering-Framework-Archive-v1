"""Explicit, manual, prospective-only same-week supplemental CN daily issuance.

Never modifies the canonical already-frozen CN week. The result is a separately
identified analyst candidate; it cannot replace original freeze/scoring/Graph B.
Only final completed-week evidence enters the extra one-shot synthesis.
"""
from __future__ import annotations

# OWNER_APPROVED_ONE_SHOT_W45_ACTION_TRIGGER_20261102
# SECOND_TRIGGER_ONLY_AFTER_FIRST_RUN_FAILED_PRE_API_ZERO_PAID_CALLS

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.cycle_navigator.daily_path_recovery import recover_daily_path, _canonical, _sha
from scripts.cycle_navigator.daily_price_journey import validate_daily_path


def issue_once(repo: Path, *, year: int, week: int, model: str,
               issued_at: datetime, output: Path, request=None, budget_check=None) -> dict:
    if (year, week) != (2026, 45):
        raise ValueError("LATE_ISSUE_ONE_WEEK_ONLY")
    if issued_at.tzinfo is None:
        raise ValueError("ISSUE_CLOCK_UNZONED")
    frozen_path = repo / f"05_CYCLE_NAVIGATOR/weekly/{year}/W{week:02d}/CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
    machine_path = frozen_path.with_name("CYCLE_NAVIGATOR_MACHINE_PACKAGE.json")
    manifest_path = frozen_path.with_name("CYCLE_NAVIGATOR_SOURCE_MANIFEST.json")
    for source in (frozen_path, machine_path, manifest_path):
        if not source.is_file():
            raise ValueError("ORIGINAL_FREEZE_OR_MANIFEST_MISSING")
    original_bytes = frozen_path.read_bytes()
    original = json.loads(original_bytes)
    machine = json.loads(machine_path.read_text())
    manifest = json.loads(manifest_path.read_text())
    if machine.get("forecast_freeze") != original:
        raise ValueError("ORIGINAL_FREEZE_MACHINE_MISMATCH")
    if (manifest.get("target_iso_year"), manifest.get("target_iso_week")) != (year, week):
        raise ValueError("ORIGINAL_SOURCE_MANIFEST_WEEK_MISMATCH")
    if original["daily_price_path"]["forecast_week"] != "2026-W45":
        raise ValueError("ORIGINAL_PATH_WEEK_MISMATCH")
    validate_daily_path(original["daily_price_path"], original, year, week)
    if not any(original["daily_price_path"][asset]["status"] == "UNAVAILABLE" for asset in ("BTC", "ETH")):
        raise ValueError("NO_ORIGINAL_ABSTENTION")
    completed_year, completed_week = manifest["completed_iso_year"], manifest["completed_iso_week"]
    if (completed_year, completed_week) != (2026, 44):
        raise ValueError("SOURCE_COMPLETED_WEEK_MISMATCH")
    completed_path = repo / "03_DAILY_CAPTURE_LOGS/weekly/2026/W44.json"
    mm_dir = repo / manifest["master_monday_dir"]
    mm_package_path = mm_dir / "MASTER_MONDAY_MACHINE_PACKAGE.json"
    mm_pointer_path = mm_dir / "MASTER_MONDAY_DELIVERY_POINTER.json"
    completed_bytes = completed_path.read_bytes()
    mm_bytes = mm_package_path.read_bytes()
    mm_pointer_bytes = mm_pointer_path.read_bytes()
    mm_hashes = manifest.get("master_monday_files") or {}
    if (hashlib.sha256(mm_bytes).hexdigest() != mm_hashes.get(mm_package_path.name)
            or hashlib.sha256(mm_pointer_bytes).hexdigest() != mm_hashes.get(mm_pointer_path.name)):
        raise ValueError("MASTER_MONDAY_SOURCE_SHA_MISMATCH")
    captured = json.loads(completed_bytes)
    if captured.get("authority") != "SHADOW_CALIBRATION_INPUT_ONLY":
        raise ValueError("SOURCE_AUTHORITY_CHANGED")
    quotes = {asset: ((captured.get("hourly_sequence") or {})
                       .get("spot_flow_readback") or {}).get(asset, {}).get("quote_unit")
              for asset in ("BTC", "ETH")}
    # This quote applies to the explicitly independent USDT/USD supplement.
    # W45's frozen original weekly range did not record a quote: DO NOT label
    # this as the original quote-admitted weekly issuer or official scoring.
    context = {
        "master_monday_pointer": json.loads(mm_pointer_bytes),
        "master_monday_machine_package": json.loads(mm_bytes),
        "completed_week_hourly_capture": captured,
        "weekly_envelope_quote": quotes,
    }
    value = {
        "issue_number": machine.get("issue_number"),
        "base_case_this_week": machine.get("base_case_this_week"),
        "market_state": machine.get("market_state"),
        "forecast_freeze": dict(original),
    }
    candidate, receipt = recover_daily_path(value, context, year=year, week=week,
            model=model, issued_at=issued_at, request=request, budget_check=budget_check,
            cost_receipt_path=repo / "runtime/api-cost-ledger" /
                "CN_W45_LATE_SUPPLEMENT_COST_RESERVATION.json")
    daily_path = candidate["forecast_freeze"]["daily_price_path"]
    validate_daily_path(daily_path, original, year, week)
    status = ("SUPPLEMENTAL_SEVEN_DAY_CANDIDATE" if any(
        daily_path[a]["status"] == "PUBLISHED" for a in ("BTC", "ETH"))
        else "SUPPLEMENTAL_UNAVAILABLE")
    artifact = {
        "contract": "CN_W45_LATE_PROSPECTIVE_SUPPLEMENT_v1",
        "status": status, "forecast_week": "2026-W45",
        "issued_at_utc": issued_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "original_weekly_freeze_sha256": hashlib.sha256(original_bytes).hexdigest(),
        "original_machine_package_sha256": hashlib.sha256(machine_path.read_bytes()).hexdigest(),
        "original_source_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "completed_hourly_source_sha256": hashlib.sha256(completed_bytes).hexdigest(),
        "master_monday_machine_sha256": hashlib.sha256(mm_bytes).hexdigest(),
        "source_quote": quotes,
        "original_weekly_envelope_quote_verified": False,
        "original_freeze_changed": False,
        "original_score_changed": False,
        "original_issuer_replacement": False,
        "eligible_for_official_scoring": False,
        "site_publishing_authority": False,
        "portfolio_execution": False,
        "daily_path": daily_path,
        "recovery_receipt": receipt,
    }
    artifact["supplement_sha256"] = _sha(artifact)
    if output.exists():
        raise ValueError("SUPPLEMENT_OUTPUT_ALREADY_EXISTS")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        stream.write(_canonical(artifact))
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--week", type=int, default=45)
    parser.add_argument("--model", default="gpt-6-sol")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = issue_once(args.repo_root.resolve(), year=args.year, week=args.week,
                          model=args.model, issued_at=datetime.now(timezone.utc), output=args.output)
    # Value-free CI output, never leak market provider details to public logs.
    print(json.dumps({"status": artifact["status"], "issued_at_utc": artifact["issued_at_utc"],
                      "supplement_sha256": artifact["supplement_sha256"],
                      "original_freeze_changed": False}))


if __name__ == "__main__":
    main()
