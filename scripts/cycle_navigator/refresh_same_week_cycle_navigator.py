from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def replace_etf_gap(text: str, correction: str) -> str:
    replacements = [
        "The settled ETF sequence remains unavailable, and outcome ingestion is incomplete. Those gaps limit confidence and prevent ETF-based conclusions.",
        "The required completed-W37 settled ETF sequence is unavailable, so no ETF-flow premise is used in the evaluation or new forecast.",
    ]
    for old in replacements:
        text = text.replace(old, correction)
    return text


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--master-monday-pointer", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo_root.resolve()
    mm_ptr_path = repo / args.master_monday_pointer
    mm_ptr = read_json(mm_ptr_path)
    year = int(mm_ptr["iso_year"])
    completed_week = int(mm_ptr["iso_week"])
    target_week = completed_week + 1

    latest_path = repo / "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json"
    latest = read_json(latest_path)
    if int(latest.get("iso_year", -1)) != year or int(latest.get("completed_source_week", -1)) != completed_week:
        raise SystemExit("NOT_SAME_WEEK_REFRESH")

    issue = int(latest["issue_number"])
    target_dir = repo / str(latest["week_dir"])
    if issue != 26 or target_week != 38:
        raise SystemExit(f"BOUNDED_REFRESH_IDENTITY_MISMATCH:issue={issue},target_week={target_week}")

    machine_path = target_dir / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json"
    score_path = target_dir / "CYCLE_NAVIGATOR_SCORECARD.json"
    freeze_path = target_dir / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
    readable_path = target_dir / "CYCLE_NAVIGATOR_READABLE.md"
    x_path = target_dir / "CYCLE_NAVIGATOR_X_READY.md"
    manifest_path = target_dir / "CYCLE_NAVIGATOR_SOURCE_MANIFEST.json"
    delivery_path = target_dir / "CYCLE_NAVIGATOR_DELIVERY_POINTER.json"
    receipt_path = target_dir / "CYCLE_NAVIGATOR_SAME_WEEK_REFRESH_RECEIPT.json"

    machine = read_json(machine_path)
    score = read_json(score_path)
    freeze = read_json(freeze_path)
    manifest = read_json(manifest_path)
    before = {
        "forecast_freeze_sha256": sha256_path(freeze_path),
        "scorecard_sha256": sha256_path(score_path),
        "master_monday_pointer_sha256": str(latest.get("master_monday_pointer_sha256") or ""),
        "machine_package_sha256": sha256_path(machine_path),
    }

    if machine.get("issue_number") != issue or machine.get("previous_issue_number") != 25:
        raise SystemExit("MACHINE_ISSUE_IDENTITY_MISMATCH")
    if score.get("issue_scored") != 25 or score.get("structural_score") != 90.0 or score.get("score_status") != "REPRODUCIBLE":
        raise SystemExit("SCORECARD_BASELINE_MISMATCH")

    preflight_path = repo / "research/master_monday_preflight/frozen" / str(year) / f"W{completed_week:02d}" / "MASTER_MONDAY_GAP_FILL_PACKAGE.json"
    preflight = read_json(preflight_path)
    weekly = preflight.get("etf", {}).get("weekly", {})
    expected_dates = weekly.get("expected_session_dates") or []
    records = weekly.get("records") or []
    totals = weekly.get("week_total_reported_units") or {}
    if weekly.get("calendar_completeness") != "COMPLETE":
        raise SystemExit("ETF_WEEK_NOT_CALENDAR_COMPLETE")
    if int(weekly.get("expected_session_count", -1)) != 4 or len(expected_dates) != 4 or len(records) != 4:
        raise SystemExit("ETF_WEEK_EXPECTED_FOUR_SESSION_HOLIDAY_WEEK")
    btc_total = float(totals.get("BTC"))
    eth_total = float(totals.get("ETH"))
    if round(btc_total, 1) != -462.7 or round(eth_total, 1) != 196.9:
        raise SystemExit(f"ETF_TOTAL_MISMATCH:{btc_total},{eth_total}")

    correction = (
        "CORRECTION — repaired final Master Monday now contains the calendar-complete W37 settled ETF sequence "
        "for all four expected NYSE sessions (2026-09-08 through 2026-09-11): BTC ETF flows totaled -462.7 and "
        "ETH ETF flows +196.9 in source-reported units. This evidence correction updates context only; it does not "
        "change CN #26's frozen W38 forecast or CN #25's locked 90% W37 structural score. Outcome ingestion remains incomplete."
    )

    readable = replace_etf_gap(readable_path.read_text(), correction)
    x_ready = replace_etf_gap(x_path.read_text(), correction)
    # Ensure the correction is visible even if the original X copy omitted the stale sentence.
    if "calendar-complete W37 settled ETF sequence" not in x_ready:
        marker = "**CURRENT STATE**"
        if marker in x_ready:
            x_ready = x_ready.replace(marker, marker + "\n" + correction + "\n", 1)
        else:
            x_ready = correction + "\n\n" + x_ready
    if "calendar-complete W37 settled ETF sequence" not in readable:
        marker = "## Current state"
        if marker in readable:
            readable = readable.replace(marker, marker + "\n\n" + correction, 1)
        else:
            readable = correction + "\n\n" + readable

    new_uncertainties: list[str] = []
    for item in machine.get("uncertainties", []):
        s = str(item)
        if "settled ETF sequence is unavailable" in s or "settled ETF sequence remains unavailable" in s:
            continue
        new_uncertainties.append(s)
    new_uncertainties.insert(0, correction)
    machine["uncertainties"] = new_uncertainties
    machine["readable_markdown"] = readable
    machine["x_ready_markdown"] = x_ready
    machine["generated_unix"] = int(time.time())

    mm_dir = repo / "research/api_agent/outputs/weekly" / str(year) / f"W{completed_week:02d}"
    required_mm = [
        "MASTER_MONDAY_CALIBRATION_SCORECARD.json",
        "MASTER_MONDAY_DELIVERY_POINTER.json",
        "MASTER_MONDAY_MACHINE_PACKAGE.json",
        "MASTER_MONDAY_OPERATIONAL_TRANSLATION.json",
        "MASTER_MONDAY_REPORT.md",
    ]
    mm_hashes = {name: sha256_path(mm_dir / name) for name in required_mm}
    mm_latest_sha = sha256_path(mm_ptr_path)
    if mm_hashes["MASTER_MONDAY_DELIVERY_POINTER.json"] != mm_latest_sha:
        raise SystemExit("LATEST_MM_POINTER_NOT_BYTE_IDENTICAL_TO_WEEK_POINTER")

    manifest["master_monday_files"] = mm_hashes
    manifest["issue_number"] = issue
    manifest["previous_issue_number"] = 25
    manifest["completed_iso_week"] = completed_week
    manifest["target_iso_week"] = target_week
    write_json(manifest_path, manifest)
    manifest_sha = sha256_path(manifest_path)
    machine["source_manifest_sha256"] = manifest_sha

    # Preserve immutable accountability objects exactly.
    machine["evaluation"] = read_json(score_path)
    machine["forecast_freeze"] = freeze
    write_json(machine_path, machine)
    readable_path.write_text(readable)
    x_path.write_text(x_ready)

    after_freeze_sha = sha256_path(freeze_path)
    after_score_sha = sha256_path(score_path)
    if after_freeze_sha != before["forecast_freeze_sha256"]:
        raise SystemExit("FORECAST_FREEZE_CHANGED_HINDSIGHT_REWRITE_FORBIDDEN")
    if after_score_sha != before["scorecard_sha256"]:
        raise SystemExit("SCORECARD_CHANGED_ACCOUNTABILITY_REWRITE_FORBIDDEN")

    delivery = {
        "completed_source_week": completed_week,
        "contract": "CYCLE_NAVIGATOR_DELIVERY_POINTER_v1",
        "forecast_freeze_sha256": after_freeze_sha,
        "iso_week": target_week,
        "iso_year": year,
        "issue_number": issue,
        "machine_package_sha256": sha256_path(machine_path),
        "master_monday_pointer_sha256": mm_latest_sha,
        "publication_status": machine.get("publication_status", "X_READY_NOT_CONFIRMED_PUBLISHED"),
        "status": machine.get("status", "DEGRADED"),
        "week_dir": str(target_dir.relative_to(repo)),
    }
    write_json(delivery_path, delivery)
    write_json(latest_path, delivery)

    stale = [
        "settled etf sequence remains unavailable",
        "required completed-w37 settled etf sequence is unavailable",
    ]
    combined = (readable + "\n" + x_ready + "\n" + machine_path.read_text()).lower()
    bad = [token for token in stale if token in combined]
    if bad:
        raise SystemExit("STALE_ETF_GAP_SURVIVED:" + ",".join(bad))

    receipt = {
        "authority": "ACCOUNTABILITY_PRESERVING_SAME_WEEK_CORRECTION_ONLY",
        "completed_source_week": completed_week,
        "contract": "CYCLE_NAVIGATOR_SAME_WEEK_REFRESH_RECEIPT_v1",
        "issue_number": issue,
        "target_iso_week": target_week,
        "before": before,
        "after": {
            "forecast_freeze_sha256": after_freeze_sha,
            "scorecard_sha256": after_score_sha,
            "master_monday_pointer_sha256": mm_latest_sha,
            "machine_package_sha256": sha256_path(machine_path),
            "source_manifest_sha256": manifest_sha,
        },
        "etf_week": {
            "calendar_completeness": weekly.get("calendar_completeness"),
            "expected_session_count": weekly.get("expected_session_count"),
            "expected_session_dates": expected_dates,
            "btc_total": btc_total,
            "eth_total": eth_total,
        },
        "invariants": {
            "issue_number_preserved": True,
            "forecast_freeze_byte_preserved": True,
            "scorecard_byte_preserved": True,
            "hindsight_rewrite": False,
            "new_issue_created": False,
        },
        "status": "PASS",
    }
    write_json(receipt_path, receipt)
    print(json.dumps(delivery, sort_keys=True))


if __name__ == "__main__":
    main()
