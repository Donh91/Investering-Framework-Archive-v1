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
  HOURLY     hourly-sequence-capture.yml (chain_entry_signal=true) once per UTC hour from :05.
  RECOVERY   native-market-recovery.yml once per UTC hour from :35 (the only repair loop for the
             Live Anchor/ETF/BTC.D/stablecoin/Entry owners; it has its own cooldowns).
  PRECLOSE   sunday-market-close-and-cfgi.yml mode=preclose, Sunday 23:35-23:59 Copenhagen
             (a preclose after midnight fails WEEKLY_CLOSE_SCHEDULED_WEEK_ROLLOVER_UNBOUND).
  FINAL      sunday-market-close-and-cfgi.yml mode=final, Monday from 02:05 Copenhagen, until a
             run created after 02:00 Monday has SUCCEEDED (a late-firing preclose cron fails and
             does not count).
  MONDAY     weekly-api-calibration-shadow.yml (Master Monday) once per Monday from 02:40 Copenhagen,
             and ONLY after FINAL succeeded (Master Monday hard-requires the final close);
             CN Weekly Publication follows by its existing workflow_run trigger.
  S1BRIEF    s1-tick-brief.yml once per UTC hour from :15, unless a cron or manual run of it was created
             this hour from :13. The S1 task runs at :45 (it may start up to ~15 min late) and needs a brief
             younger than 45 minutes (00_FMOS/S1/TICK.md T2): a :15-:25 dispatch plus a 3-11 min build
             publishes between :18 and :36. GitHub's '18 * * * *' cron is mostly not started (2 of 20 h on
             2026-11-19); when it does start on time after the dispatch, that hour builds twice (bounded).
             A dispatched run always builds (read-only token, no secrets); the push/workflow_run fallback
             builds only when no cron or manual run happened in the last hour, so it stays quiet.

Fail-closed rules:
  - mode is read from 00_FMOS/METRONOME_MODE_v1.json on main; ACTIVE, ACTIVE_DATA (hourly data owners only) or else SHADOW
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
import time
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
PRODUCTION_BRANCH = "main"

HOURLY = {"key": "HOURLY", "workflow": "hourly-sequence-capture.yml",
          "inputs": {"chain_entry_signal": "true"}, "from_minute": 5}
# Recovery's own cron fires at :24; from minute 26 an on-time cron run (created >= :24) already serves the hour,
# so the metronome adds no second run then. A cron run that starts late, after the metronome dispatched, can still
# double up; recovery's concurrency group serialises the two, and its (possibly credit-billed) repairs keep their cooldowns.
RECOVERY = {"key": "RECOVERY", "workflow": "native-market-recovery.yml", "inputs": {}, "from_minute": 26}
CLOSE_WORKFLOW = "sunday-market-close-and-cfgi.yml"
PRECLOSE = {"key": "PRECLOSE", "workflow": CLOSE_WORKFLOW, "inputs": {"mode": "preclose"},
            "local_weekday": 6, "local_time": (23, 35)}
FINAL = {"key": "FINAL", "workflow": CLOSE_WORKFLOW, "inputs": {"mode": "final"},
         "local_weekday": 0, "local_time": (2, 5)}
MONDAY = {"key": "MONDAY", "workflow": "weekly-api-calibration-shadow.yml", "inputs": {},
          "local_weekday": 0, "local_time": (2, 40)}
# The S1 tick brief (evidence only; read-only build, issues:write publish of its own issue only). Its cron is '18 * * * *'.
S1BRIEF = {"key": "S1BRIEF", "workflow": "s1-tick-brief.yml", "inputs": {}, "from_minute": 15, "serves_from_minute": 13}
S1BRIEF_BUILDING_EVENTS = ("schedule", "workflow_dispatch")   # these always build; push/workflow_run mostly do not
DISPATCH_ALLOWLIST = {HOURLY["workflow"], RECOVERY["workflow"], CLOSE_WORKFLOW, MONDAY["workflow"], S1BRIEF["workflow"],
                      SELF_WORKFLOW}


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


def production_runs(runs: Iterable[dict]) -> list[dict]:
    """Only main-branch, non-PR runs can serve or occupy a production slot.

    Target workflows skip production off main, and native-market-recovery.yml also runs on
    pull_request. Such runs must neither count as "already ran" nor as "target active".
    A run without branch/event metadata is kept (conservative: it suppresses, never doubles).
    """
    return [r for r in runs or [] if isinstance(r, dict)
            and r.get("head_branch", PRODUCTION_BRANCH) == PRODUCTION_BRANCH
            and r.get("event") != "pull_request"]


def any_active(runs: Iterable[dict], exclude_id: int | None = None) -> bool:
    return any(isinstance(r, dict) and r.get("status") in ACTIVE_STATUSES and r.get("id") != exclude_id
               for r in runs or [])


def hourly_due(now: dt.datetime, runs: list[dict], target: dict = HOURLY) -> tuple[bool, str]:
    hour = now.replace(minute=0, second=0, microsecond=0)
    if now.minute < target["from_minute"]:
        return False, "BEFORE_MINUTE_%02d" % target["from_minute"]
    if any_active(runs):
        return False, "TARGET_ACTIVE"
    # Any run (cron, chain or metronome) created in this hour after (from_minute - 2) already serves it.
    if any(t >= hour + dt.timedelta(minutes=target["from_minute"] - 2) for t in created(runs)):
        return False, "ALREADY_RAN_THIS_HOUR"
    return True, "DUE"


def recovery_due(now: dt.datetime, runs: list[dict]) -> tuple[bool, str]:
    return hourly_due(now, runs, RECOVERY)


def s1brief_due(now: dt.datetime, runs: list[dict]) -> tuple[bool, str]:
    """One brief build per UTC hour, before the S1 task's :45 run. Only a cron or manual run serves the hour: a push or
    workflow_run run is a fallback that builds only after a missed cron, and its run row cannot show whether it built.
    Any run of the workflow still in flight (also a fallback's short due check) waits for the next tick."""
    hour = now.replace(minute=0, second=0, microsecond=0)
    if now.minute < S1BRIEF["from_minute"]:
        return False, "BEFORE_MINUTE_%02d" % S1BRIEF["from_minute"]
    if any_active(runs):
        return False, "TARGET_ACTIVE"
    since = hour + dt.timedelta(minutes=S1BRIEF["serves_from_minute"])
    for r in runs or []:
        try:
            if r.get("event", "schedule") in S1BRIEF_BUILDING_EVENTS and utc(r["created_at"]) >= since:
                return False, "ALREADY_RAN_THIS_HOUR"
        except (KeyError, TypeError, ValueError, AttributeError):
            return False, "RUN_ROW_UNREADABLE"   # conservative: an unreadable row suppresses, never doubles
    return True, "DUE"


def succeeded_since(runs: Iterable[dict], since: dt.datetime) -> bool:
    for r in runs or []:
        try:
            if utc(r["created_at"]) >= since and r.get("status") == "completed" and r.get("conclusion") == "success":
                return True
        except (KeyError, TypeError, ValueError):
            continue
    return False


def _local_slot(now: dt.datetime, target: dict) -> tuple[dt.datetime, dt.datetime] | None:
    local = now.astimezone(CPH)
    if local.weekday() != target["local_weekday"]:
        return None
    h, m = target["local_time"]
    return local, local.replace(hour=h, minute=m, second=0, microsecond=0)


def preclose_due(now: dt.datetime, runs: list[dict]) -> tuple[bool, str]:
    slot = _local_slot(now, PRECLOSE)
    if slot is None:
        return False, "NOT_SUNDAY_CPH"
    local, start = slot
    if local < start:
        return False, "BEFORE_PRECLOSE_SLOT"
    if local >= local.replace(hour=23, minute=59, second=0, microsecond=0):
        return False, "TOO_CLOSE_TO_MIDNIGHT"  # never risk a rollover-unbound preclose
    if any_active(runs):
        return False, "TARGET_ACTIVE"
    if any(t >= (start - dt.timedelta(minutes=5)).astimezone(dt.timezone.utc) for t in created(runs)):
        return False, "ALREADY_RAN_THIS_SLOT"
    return True, "DUE"


def final_done(now: dt.datetime, runs: list[dict]) -> bool:
    local = now.astimezone(CPH)
    since = local.replace(hour=2, minute=0, second=0, microsecond=0).astimezone(dt.timezone.utc)
    return local.weekday() == FINAL["local_weekday"] and succeeded_since(runs, since)


def final_due(now: dt.datetime, runs: list[dict]) -> tuple[bool, str]:
    slot = _local_slot(now, FINAL)
    if slot is None:
        return False, "NOT_MONDAY_CPH"
    local, start = slot
    if local < start:
        return False, "BEFORE_FINAL_SLOT"
    if final_done(now, runs):
        return False, "FINAL_SUCCEEDED_THIS_MONDAY"
    if any_active(runs):
        return False, "TARGET_ACTIVE"  # e.g. a late preclose cron still running; it will fail and not count
    return True, "DUE"


def monday_due(now: dt.datetime, runs: list[dict], close_runs: list[dict] | None = None) -> tuple[bool, str]:
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
    if not final_done(now, close_runs or []):
        return False, "WAITING_FOR_SUNDAY_FINAL"
    return True, "DUE"


# ACTIVE_DATA dispatches only the free hourly owners (hourly capture: free public candles; market recovery:
# bounded, cooldown-limited repairs; the S1 tick brief: read-only GitHub reads). The Sunday close and the paid
# Master Monday stay log-only.
# Anything but an exact known mode is SHADOW.
MODES = ("ACTIVE", "ACTIVE_DATA")
DATA_TARGET_KEYS = frozenset({"HOURLY", "RECOVERY", "S1BRIEF"})


def read_mode(doc: Any) -> str:
    mode = doc.get("mode") if isinstance(doc, dict) else None
    return mode if mode in MODES else "SHADOW"


def dispatches(mode: str, target_key: str) -> bool:
    return mode == "ACTIVE" or (mode == "ACTIVE_DATA" and target_key in DATA_TARGET_KEYS)


def wait_minutes(environment: Any) -> int | None:
    rules = environment.get("protection_rules") if isinstance(environment, dict) else None
    for rule in rules or []:
        if isinstance(rule, dict) and rule.get("type") == "wait_timer":
            value = rule.get("wait_timer")
            if isinstance(value, int) and not isinstance(value, bool):
                return value
    return None


def decide(now: dt.datetime, *, mode: str, hourly_runs: list[dict], monday_runs: list[dict],
           self_runs: list[dict], self_run_id: int | None, environment: Any,
           recovery_runs: list[dict] | None = None, close_runs: list[dict] | None = None,
           s1brief_runs: list[dict] | None = None) -> dict:
    """Pure decision. Returns dispatches (may be empty), would_dispatch and loop decision."""
    plan: dict[str, Any] = {"contract": CONTRACT, "now_utc": iso(now), "mode": mode,
                            "targets": {}, "dispatch": [], "would_dispatch": [], "next_tick": False,
                            "next_tick_reason": None}
    close_runs = close_runs or []
    checks = (
        (HOURLY, lambda: hourly_due(now, hourly_runs)),
        (RECOVERY, lambda: recovery_due(now, recovery_runs or [])),
        (PRECLOSE, lambda: preclose_due(now, close_runs)),
        (FINAL, lambda: final_due(now, close_runs)),
        (MONDAY, lambda: monday_due(now, monday_runs, close_runs)),
        (S1BRIEF, lambda: s1brief_due(now, s1brief_runs or [])),
    )
    for target, fn in checks:
        due, reason = fn()
        plan["targets"][target["key"]] = reason
        if due:
            item = {"workflow": target["workflow"], "inputs": target["inputs"]}
            (plan["dispatch"] if dispatches(mode, target["key"]) else plan["would_dispatch"]).append(item)
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

    READ_BUDGET_SECONDS = 90  # total wall-clock budget for all reads in one tick (fail closed when spent)

    def __init__(self, token: str, repo: str = REPO, budget_seconds: float | None = None):
        self.token, self.repo = token, repo
        self.deadline = time.monotonic() + (self.READ_BUDGET_SECONDS if budget_seconds is None else budget_seconds)

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
        # GET-only bounded retry. Never retry a POST: an ambiguous dispatch might
        # have succeeded and repeating it could duplicate a workflow or paid call.
        for attempt in range(3):
            remaining = self.deadline - time.monotonic()
            if method == "GET" and remaining <= 0:
                raise TimeoutError("READ_BUDGET_EXCEEDED")  # never act on reads from minutes ago
            try:
                with urllib.request.urlopen(req, timeout=max(1.0, min(30.0, remaining)) if method == "GET" else 30) as r:
                    body = r.read()
                return json.loads(body) if body else None
            except urllib.error.HTTPError as exc:
                if method != "GET" or exc.code not in {429, 500, 502, 503, 504} or attempt == 2:
                    raise
            except (urllib.error.URLError, TimeoutError):
                if method != "GET" or attempt == 2:
                    raise
            time.sleep(2 ** attempt)
        raise RuntimeError("GET_RETRY_EXHAUSTED")

    def runs(self, workflow: str) -> list[dict]:
        doc = self._req("GET", f"/repos/{self.repo}/actions/workflows/{workflow}/runs?per_page=30&branch={PRODUCTION_BRANCH}")
        # A malformed HTTP 200 is not evidence that no workflow is in flight.
        if not isinstance(doc, dict) or not isinstance(doc.get("workflow_runs"), list):
            raise ValueError("WORKFLOW_RUNS_INVALID_SHAPE")
        rows = doc["workflow_runs"]
        if any(not isinstance(row, dict) for row in rows):
            raise ValueError("WORKFLOW_RUNS_INVALID_ITEM")
        # Every row must carry the fields the decision reads; an unreadable row could hide a run in flight.
        for row in rows:
            if type(row.get("id")) is not int or not isinstance(row.get("status"), str) \
                    or not isinstance(row.get("created_at"), str):
                raise ValueError("WORKFLOW_RUNS_INVALID_ITEM")
            try:
                dt.datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
            except ValueError:
                raise ValueError("WORKFLOW_RUNS_INVALID_ITEM") from None
        count = doc.get("total_count")
        # total_count is required, and a page must hold exactly min(total_count, per_page=30) rows.
        if type(count) is not int or count < 0 or len(rows) != min(count, 30):
            raise ValueError(f"WORKFLOW_RUNS_COUNT_CONTRADICTION:count={count!r}:len={len(rows)}")
        return rows

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


CLOCK_DRIFT_MAX = dt.timedelta(seconds=30)


def run(gh, now: dt.datetime, self_run_id: int | None, clock=None) -> dict:
    # Reads are not authority. On a partial or transient GitHub read failure,
    # never interpret missing evidence as "no run exists" and dispatch a target.
    # The self-loop may continue only if its native concurrency census and wait
    # timer were both read successfully. Otherwise rely on the sparse restart cron.
    errors: list[str] = []
    failed_reads: set[str] = set()

    def read(name: str, fn, fallback):
        try:
            value = fn()
            if value is None:
                raise ValueError("EMPTY_READ")
            return value
        except Exception as exc:
            failed_reads.add(name)
            errors.append(f"READ_{name}:{type(exc).__name__}")
            detail = str(exc)[:80].replace(" ", "_")  # keep the cause visible in the tick log
            if detail:
                errors.append(f"READ_{name}_DETAIL:{detail}")
            return fallback

    # Loop-safety reads (wait timer, mode, own census) come first: a slow API spends the read budget on the
    # targets, which then fail closed, never on the reads that keep the loop alive.
    environment = read("ENVIRONMENT", gh.environment, {})
    mode_doc = read("MODE", gh.mode, {})
    raw_runs = {}
    for name, workflow in (
        ("SELF", SELF_WORKFLOW),
        ("HOURLY", HOURLY["workflow"]),
        ("RECOVERY", RECOVERY["workflow"]),
        ("MONDAY", MONDAY["workflow"]),
        ("CLOSE", CLOSE_WORKFLOW),
        ("S1BRIEF", S1BRIEF["workflow"]),
    ):
        raw_runs[name] = read(name, lambda wf=workflow: gh.runs(wf), [])
        if not isinstance(raw_runs[name], list):
            failed_reads.add(name)
            errors.append(f"READ_{name}:INVALID_SHAPE")
            raw_runs[name] = []
    if not isinstance(environment, dict):
        failed_reads.add("ENVIRONMENT")
        errors.append("READ_ENVIRONMENT:INVALID_SHAPE")
        environment = {}

    # Decide on the clock as it is after the reads; slow reads must not dispatch on a stale "now".
    if clock is not None:
        later = clock()
        if later - now > CLOCK_DRIFT_MAX:
            failed_reads.add("CLOCK")
            errors.append(f"READ_CLOCK:DRIFT_{int((later - now).total_seconds())}S")
        now = later

    # Fail closed for ALL targets if even one data source is unverified.
    mode = "SHADOW" if failed_reads else read_mode(mode_doc)
    plan = decide(now, mode=mode,
                  hourly_runs=production_runs(raw_runs["HOURLY"]),
                  monday_runs=production_runs(raw_runs["MONDAY"]),
                  self_runs=raw_runs["SELF"], self_run_id=self_run_id,
                  environment=environment,
                  recovery_runs=production_runs(raw_runs["RECOVERY"]),
                  close_runs=production_runs(raw_runs["CLOSE"]),
                  s1brief_runs=production_runs(raw_runs["S1BRIEF"]))
    plan["read_status"] = "DEGRADED" if failed_reads else "PASS"
    plan["failed_reads"] = sorted(failed_reads)
    if failed_reads:
        plan["dispatch"] = []
        plan["would_dispatch"] = []  # unknown evidence is NOT a forecast
    if "SELF" in failed_reads or "ENVIRONMENT" in failed_reads:
        plan["next_tick"] = False
        plan["next_tick_reason"] = "LOOP_SAFETY_READ_UNVERIFIED"

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
    clock = lambda: dt.datetime.now(dt.timezone.utc)  # noqa: E731
    plan = run(Github(token), clock(), args.self_run_id, clock=clock)
    print(CONTRACT + " " + json.dumps(plan, sort_keys=True))
    # A dead loop or a failed dispatch must be visible as a failed run.
    return 1 if plan["errors"] or not plan["next_tick"] and plan["next_tick_reason"] != "ANOTHER_METRONOME_RUN_ACTIVE" else 0


if __name__ == "__main__":
    sys.exit(main())
