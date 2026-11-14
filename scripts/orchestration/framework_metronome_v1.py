#!/usr/bin/env python3
"""Framework metronome: a reliable clock for the data chain (dispatch-only, no data writes).

Why: GitHub starts only ~25 % of this account's scheduled runs, and daily crons run 5-8 h late
(Vault '17 2 * * *' starts 08:49-09:53Z every day). Dispatched runs start within seconds.
So the metronome replaces the *clock*, not any owner: it dispatches the existing owners'
workflow_dispatch entry points when they are due, and their own preflights stay authoritative.

Loop: framework-metronome.yml waits in the GitHub Environment `framework-metronome`
(owner-set wait timer, no runner held while waiting), runs one tick, then dispatches its own
next iteration. A sparse cron only restarts a dead loop.

Targets (deliberately minimal; everything else already chains from these):
  HOURLY   hourly-sequence-capture.yml (chain_entry_signal=true) once per UTC hour from :05.
  MONDAY   weekly-api-calibration-shadow.yml (Master Monday) once per Monday from 02:40 Copenhagen;
           CN Weekly Publication follows by its existing workflow_run trigger.

Fail-closed rules:
  - mode is read from 00_FMOS/METRONOME_MODE_v1.json on main; anything but ACTIVE is SHADOW
    (logs WOULD_DISPATCH, dispatches nothing but its own next tick).
  - the next tick is dispatched only if the environment's wait timer is >= MIN_WAIT_MINUTES
    and no other metronome run is queued/waiting/in progress (exactly one loop).
  - only allowlisted workflow files can be dispatched; only allowlisted API routes are called.
It never writes files, commits, reads secrets other than GITHUB_TOKEN, or touches the Vault.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Iterable
from zoneinfo import ZoneInfo

CONTRACT = "FRAMEWORK_METRONOME_TICK_v1"
REPO = "Donh91/Investering-Framework-Archive-v1"
SELF_WORKFLOW = "framework-metronome.yml"
ENVIRONMENT = "framework-metronome"
MODE_PATH = "00_FMOS/METRONOME_MODE_v1.json"
MIN_WAIT_MINUTES = 5
MAX_WAIT_MINUTES = 30
CPH = ZoneInfo("Europe/Copenhagen")
ACTIVE_STATUSES = {"queued", "in_progress", "waiting", "requested", "pending"}

HOURLY = {"key": "HOURLY", "workflow": "hourly-sequence-capture.yml",
          "inputs": {"chain_entry_signal": "true"}, "from_minute": 5}
MONDAY = {"key": "MONDAY", "workflow": "weekly-api-calibration-shadow.yml", "inputs": {},
          "local_weekday": 0, "local_time": (2, 40)}
DISPATCH_ALLOWLIST = {HOURLY["workflow"], MONDAY["workflow"], SELF_WORKFLOW}


def utc(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def iso(t: dt.datetime) -> str:
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def created(runs: Iterable[dict]) -> list[dt.datetime]:
    out = []
    for r in runs or []:
        try:
            out.append(utc(r["created_at"]))
        except (KeyError, TypeError, ValueError):
            continue
    return out


def any_active(runs: Iterable[dict], exclude_id: int | None = None) -> bool:
    return any(isinstance(r, dict) and r.get("status") in ACTIVE_STATUSES and r.get("id") != exclude_id
               for r in runs or [])


def hourly_due(now: dt.datetime, runs: list[dict]) -> tuple[bool, str]:
    hour = now.replace(minute=0, second=0, microsecond=0)
    if now.minute < HOURLY["from_minute"]:
        return False, "BEFORE_MINUTE_%02d" % HOURLY["from_minute"]
    if any_active(runs):
        return False, "TARGET_ACTIVE"
    # Any run (cron, chain or metronome) created in this hour after :03 already serves it.
    if any(t >= hour + dt.timedelta(minutes=3) for t in created(runs)):
        return False, "ALREADY_RAN_THIS_HOUR"
    return True, "DUE"


def monday_due(now: dt.datetime, runs: list[dict]) -> tuple[bool, str]:
    local = now.astimezone(CPH)
    if local.weekday() != MONDAY["local_weekday"]:
        return False, "NOT_MONDAY_CPH"
    h, m = MONDAY["local_time"]
    start = local.replace(hour=h, minute=m, second=0, microsecond=0)
    if local < start:
        return False, "BEFORE_MONDAY_SLOT"
    if any_active(runs):
        return False, "TARGET_ACTIVE"
    day_start = local.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(dt.timezone.utc)
    if any(t >= day_start for t in created(runs)):
        return False, "ALREADY_RAN_THIS_MONDAY"
    return True, "DUE"


def read_mode(doc: Any) -> str:
    return "ACTIVE" if isinstance(doc, dict) and doc.get("mode") == "ACTIVE" else "SHADOW"


def wait_minutes(environment: Any) -> int | None:
    rules = environment.get("protection_rules") if isinstance(environment, dict) else None
    for rule in rules or []:
        if isinstance(rule, dict) and rule.get("type") == "wait_timer":
            value = rule.get("wait_timer")
            if isinstance(value, int) and not isinstance(value, bool):
                return value
    return None


def decide(now: dt.datetime, *, mode: str, hourly_runs: list[dict], monday_runs: list[dict],
           self_runs: list[dict], self_run_id: int | None, environment: Any) -> dict:
    """Pure decision. Returns dispatches (may be empty), would_dispatch and loop decision."""
    plan: dict[str, Any] = {"contract": CONTRACT, "now_utc": iso(now), "mode": mode,
                            "targets": {}, "dispatch": [], "would_dispatch": [], "next_tick": False,
                            "next_tick_reason": None}
    for target, runs, fn in ((HOURLY, hourly_runs, hourly_due), (MONDAY, monday_runs, monday_due)):
        due, reason = fn(now, runs)
        plan["targets"][target["key"]] = reason
        if due:
            item = {"workflow": target["workflow"], "inputs": target["inputs"]}
            (plan["dispatch"] if mode == "ACTIVE" else plan["would_dispatch"]).append(item)
    wait = wait_minutes(environment)
    plan["wait_timer_minutes"] = wait
    if wait is None or not MIN_WAIT_MINUTES <= wait <= MAX_WAIT_MINUTES:
        plan["next_tick_reason"] = "WAIT_TIMER_MISSING_OR_OUT_OF_RANGE"  # never spin a fast loop
    elif any_active(self_runs, exclude_id=self_run_id):
        plan["next_tick_reason"] = "ANOTHER_METRONOME_RUN_ACTIVE"  # exactly one loop
    else:
        plan["next_tick"] = True
        plan["next_tick_reason"] = "LOOP_CONTINUES"
    for item in plan["dispatch"]:
        if item["workflow"] not in DISPATCH_ALLOWLIST:
            raise ValueError("DISPATCH_NOT_ALLOWLISTED")
    return plan


class Github:
    """Minimal client: GET runs/environment/mode file, POST workflow dispatches. Nothing else."""

    def __init__(self, token: str, repo: str = REPO):
        self.token, self.repo = token, repo

    def _req(self, method: str, route: str, payload: dict | None = None) -> Any:
        allowed = (
            (method == "GET" and route.startswith(f"/repos/{self.repo}/actions/workflows/") and "/runs?" in route)
            or (method == "GET" and route == f"/repos/{self.repo}/environments/{ENVIRONMENT}")
            or (method == "GET" and route == f"/repos/{self.repo}/contents/{MODE_PATH}?ref=main")
            or (method == "POST" and route.startswith(f"/repos/{self.repo}/actions/workflows/")
                and route.endswith("/dispatches")
                and route.split("/")[-2] in DISPATCH_ALLOWLIST)
        )
        if not allowed:
            raise ValueError("ROUTE_NOT_ALLOWED")
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request("https://api.github.com" + route, data=data, method=method, headers={
            "Accept": "application/vnd.github+json", "Authorization": "Bearer " + self.token,
            "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "framework-metronome-v1"})
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read()
        return json.loads(body) if body else None

    def runs(self, workflow: str) -> list[dict]:
        return (self._req("GET", f"/repos/{self.repo}/actions/workflows/{workflow}/runs?per_page=30") or {}).get(
            "workflow_runs", [])

    def environment(self) -> Any:
        try:
            return self._req("GET", f"/repos/{self.repo}/environments/{ENVIRONMENT}")
        except urllib.error.HTTPError:
            return None

    def mode(self) -> Any:
        import base64
        try:
            doc = self._req("GET", f"/repos/{self.repo}/contents/{MODE_PATH}?ref=main")
            return json.loads(base64.b64decode(doc["content"]))
        except (urllib.error.HTTPError, KeyError, ValueError, TypeError):
            return None

    def dispatch(self, workflow: str, inputs: dict) -> None:
        self._req("POST", f"/repos/{self.repo}/actions/workflows/{workflow}/dispatches",
                  {"ref": "main", "inputs": inputs})


def run(gh, now: dt.datetime, self_run_id: int | None) -> dict:
    plan = decide(now, mode=read_mode(gh.mode()), hourly_runs=gh.runs(HOURLY["workflow"]),
                  monday_runs=gh.runs(MONDAY["workflow"]), self_runs=gh.runs(SELF_WORKFLOW),
                  self_run_id=self_run_id, environment=gh.environment())
    errors = []
    for item in plan["dispatch"]:
        try:
            gh.dispatch(item["workflow"], item["inputs"])
        except Exception as exc:  # report, keep the loop alive
            errors.append(f"{item['workflow']}:{type(exc).__name__}")
    if plan["next_tick"]:
        try:
            gh.dispatch(SELF_WORKFLOW, {})
        except Exception as exc:
            errors.append(f"{SELF_WORKFLOW}:{type(exc).__name__}")
            plan["next_tick"] = False
            plan["next_tick_reason"] = "SELF_DISPATCH_FAILED"
    plan["errors"] = errors
    return plan


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-run-id", type=int, default=None)
    args = ap.parse_args(list(argv) if argv is not None else None)
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print(json.dumps({"contract": CONTRACT, "status": "SKIPPED_NO_TOKEN"}))
        return 0
    plan = run(Github(token), dt.datetime.now(dt.timezone.utc), args.self_run_id)
    print(CONTRACT + " " + json.dumps(plan, sort_keys=True))
    # A dead loop or a failed dispatch must be visible as a failed run.
    return 1 if plan["errors"] or not plan["next_tick"] and plan["next_tick_reason"] != "ANOTHER_METRONOME_RUN_ACTIVE" else 0


if __name__ == "__main__":
    sys.exit(main())
