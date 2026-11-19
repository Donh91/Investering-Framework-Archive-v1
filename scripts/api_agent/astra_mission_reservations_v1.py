"""Generic owner Astra mission reservations for the shared monthly cost guard (append-only ledger key).

Each row of `astra_mission_reservations` in API_PENDING_BILLING_RISK_V1.json holds one owner mission's full
upper cost BEFORE any HTTP, until independently reviewed provider settlement removes it. A row is valid only
when a reviewed mission folder 06_RESEARCH_LAB/astra_missions/<work_id>/mission.json exists whose max_usd
equals the row's upper_usd. This module grants no POST; the runner enforces the owner event and the claim.

A row is OWNER_RESERVED_PREHTTP (launchable once) or CONSUMED_PENDING_INVOICE (its one POST happened; bound to the
run, the response id and the receipt's estimated upper cost). A consumed row is still counted at its FULL upper_usd
until reviewed invoice settlement removes it; the launcher refuses it (only OWNER_RESERVED_PREHTTP launches).
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MISSIONS = ROOT / "06_RESEARCH_LAB/astra_missions"
KEY = "astra_mission_reservations"
SOURCE = "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156"
MISSION_ID = re.compile(r"ASTRA-[A-Z0-9]{1,24}(?:-[A-Z0-9]{1,24}){1,10}\Z")
MONTH = re.compile(r"20[0-9]{2}-(?:0[1-9]|1[0-2])\Z")
MAX_MISSION_USD = 25.0
MAX_ROWS = 12
RESERVED = "OWNER_RESERVED_PREHTTP"
CONSUMED = "CONSUMED_PENDING_INVOICE"
CONSUMED_FIELDS = {"consumed_run_id", "consumed_response_id", "consumed_estimated_upper_usd"}
RESPONSE_ID = re.compile(r"resp_[A-Za-z0-9_-]{4,180}\Z")
FIELDS = {"work_id", "created_month_utc", "status", "lower_usd", "upper_usd", "source", "one_paid_post_max",
          "reconciliation_required", "authorization", "basis"} | CONSUMED_FIELDS


def mission_max_usd(work_id: str, missions: Path = MISSIONS):
    path = missions / work_id / "mission.json"
    if path.is_symlink() or not path.resolve().is_relative_to(missions.resolve()) or not path.is_file():
        raise ValueError("ASTRA_MISSION_RESERVATION_WITHOUT_MISSION")
    mission = json.loads(path.read_text(encoding="utf-8"))
    if mission.get("contract") != "ASTRA_MISSION_V1" or mission.get("mission_id") != work_id:
        raise ValueError("ASTRA_MISSION_RESERVATION_MISSION_INVALID")
    return mission.get("max_usd")


def mission_reservations(ledger: dict, other_work_ids: set, missions: Path = MISSIONS):
    """(upper_usd_total, count, work_ids). Raises on any unbounded, duplicate or unbound row."""
    rows = ledger.get(KEY, [])
    if not isinstance(rows, list) or len(rows) > MAX_ROWS:
        raise ValueError("ASTRA_MISSION_RESERVATION_LEDGER_INVALID")
    total, seen = 0.0, set()
    for row in rows:
        if not isinstance(row, dict) or not set(row) <= FIELDS:
            raise ValueError("ASTRA_MISSION_RESERVATION_ROW_INVALID")
        work, upper = row.get("work_id"), row.get("upper_usd")
        if (not isinstance(work, str) or not MISSION_ID.fullmatch(work) or work in seen or work in other_work_ids
                or not isinstance(row.get("created_month_utc"), str) or not MONTH.fullmatch(row["created_month_utc"])
                or row.get("status") not in (RESERVED, CONSUMED) or row.get("lower_usd") != 0
                or type(upper) not in (int, float) or not math.isfinite(upper) or not 0 < upper <= MAX_MISSION_USD
                or row.get("source") != SOURCE or row.get("one_paid_post_max") != 1
                or row.get("reconciliation_required") is not True
                or not isinstance(row.get("basis"), str) or len(row["basis"].strip()) < 30):
            raise ValueError("ASTRA_MISSION_RESERVATION_UNVERIFIED")
        if row["status"] == RESERVED and set(row) & CONSUMED_FIELDS:
            raise ValueError("ASTRA_MISSION_RESERVATION_UNVERIFIED")
        if row["status"] == CONSUMED:
            run, rid, est = (row.get(k) for k in ("consumed_run_id", "consumed_response_id",
                                                  "consumed_estimated_upper_usd"))
            if (type(run) is not int or run <= 0 or not isinstance(rid, str) or not RESPONSE_ID.fullmatch(rid)
                    or type(est) not in (int, float) or not math.isfinite(est) or not 0 < est <= upper):
                raise ValueError("ASTRA_MISSION_CONSUMPTION_UNVERIFIED")
        if mission_max_usd(work, missions) != upper:
            raise ValueError("ASTRA_MISSION_RESERVATION_COST_MISMATCH")
        seen.add(work)
        total += float(upper)   # consumed rows too: full upper_usd until invoice settlement
    return total, len(seen), seen
