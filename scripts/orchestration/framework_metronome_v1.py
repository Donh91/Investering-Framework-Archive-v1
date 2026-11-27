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
  S1BRIEF    s1-tick-brief.yml once per UTC hour from :20, unless a cron or manual run of it was created
             this hour from :18 (so an on-time '18 * * * *' cron serves the hour; no double build). The S1 task
             runs at :45 (it may start up to ~15 min late) and needs a brief younger than 45 minutes
             (00_FMOS/S1/TICK.md T2). The tick period is ~10.5 min: the dispatch lands :20-:31, or :31-:41 after one
             TARGET_ACTIVE deferral (an in-flight push/workflow_run due check), and a 2-4 min build still publishes
             before :45. 2026-11-20: from :15 the brief was ~20-30 min old at :45 (BRIEF_STALE(drift_unreadable) on
             8 commits / 300+ files); from :27 one deferral could miss :45 (review of this change).
             A dispatched run always builds (read-only token, no secrets); the push/workflow_run fallback
             builds only when no cron or manual run happened in the last hour, so it stays quiet.
  S1EXEC     s1-executor.yml (no inputs) for the ACTUAL publication: the newest s1-tick-brief.yml run on main that
             completed with success at most S1EXEC_MAX_AGE_MINUTES ago and whose publish log says WRITTEN, while
             no executor attempt is proven to have evaluated it, none is active and none is unknown (s1exec_due). GitHub creates no workflow_run event for a run started with this
             workflow token, so the brief runs dispatched above never started the executor by themselves. The
             executor resolves that brief from the published issue, proves its run natively and evaluates a brief
             run at most once (its own rule); its job token stays read-only (SHADOW). Next tick after the brief:
             ~10 min, inside the decision's 20-minute execution window.

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
import re
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Iterable
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

CONTRACT = "FRAMEWORK_METRONOME_TICK_v1"
REPO = "Donh91/Investering-Framework-Archive-v1"
SELF_WORKFLOW = "framework-metronome.yml"
ENVIRONMENT = "framework-metronome"
MODE_PATH = "00_FMOS/METRONOME_MODE_v1.json"
MIN_WAIT_MINUTES = 5
MAX_WAIT_MINUTES = 30
# Bounded native FINAL failover: GitHub's own cron can be 5-8h late.
MAX_FINAL_ATTEMPTS_PER_MONDAY = 3
FINAL_RETRY_COOLDOWN_MINUTES = 20
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
S1BRIEF = {"key": "S1BRIEF", "workflow": "s1-tick-brief.yml", "inputs": {}, "from_minute": 20, "serves_from_minute": 18}
S1BRIEF_BUILDING_EVENTS = ("schedule", "workflow_dispatch")   # these always build; push/workflow_run mostly do not
# The S1 executor (SHADOW, read-only job token). Dispatched once per completed, successful building brief run (above).
S1EXEC = {"key": "S1EXEC", "workflow": "s1-executor.yml", "inputs": {}}
S1EXEC_MAX_AGE_MINUTES = 20           # 00_FMOS/S1 EXECUTE_MAX_AGE_MINUTES: an older decision is refused (BRIEF_STALE) anyway
DISPATCH_ALLOWLIST = {HOURLY["workflow"], RECOVERY["workflow"], CLOSE_WORKFLOW, MONDAY["workflow"], S1BRIEF["workflow"],
                      S1EXEC["workflow"], SELF_WORKFLOW}


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


S1EXEC_PUBLICATION_READS = 3          # fresh successful brief runs inspected for the ACTUAL publication (2 reads each)
S1EXEC_ATTEMPT_READS = 6              # executor run attempts classified for that publication (2 reads each)
EXECUTE_STEP = "Execute the one decided action (re-verified natively; writes only when the switch on main is LIVE)"
HEALTH_LINE = re.compile(r"S1_EXECUTOR_HEALTH (\{[^\n]*\})")
EVALUATED, NOT_EVALUATED, UNKNOWN, ACTIVE = "EVALUATED", "PROVEN_NOT_EVALUATED", "UNKNOWN", "ACTIVE"


def publication_of(reader: Any, run: dict) -> str:
    """WRITTEN when this brief run's own publish job log says it wrote the brief (S1_TICK_BRIEF_PUBLISHED run=<id>
    result=WRITTEN), NONE when its publish job was skipped or logged NOT_PUBLISHED, else UNKNOWN. The run row alone
    cannot tell: a push or workflow_run fallback run that built nothing also concludes success."""
    jobs = reader.jobs(run["id"], None)
    if not isinstance(jobs, list):
        return UNKNOWN
    pub = [j for j in jobs if isinstance(j, dict) and j.get("name") == "publish"]
    if not pub:
        return "NONE" if any(isinstance(j, dict) and j.get("name") == "build" for j in jobs) else UNKNOWN
    if len(pub) > 1 or pub[0].get("status") != "completed":
        return UNKNOWN
    if pub[0].get("conclusion") == "skipped":
        return "NONE"
    if pub[0].get("conclusion") != "success" or type(pub[0].get("id")) is not int:
        return UNKNOWN
    text = reader.log(pub[0]["id"])
    if not isinstance(text, str):
        return UNKNOWN
    wrote = re.findall(rf"S1_TICK_BRIEF_PUBLISHED issue=\d+ run={run['id']} result=WRITTEN\b", text)
    skipped = re.findall(rf"S1_TICK_BRIEF_NOT_PUBLISHED issue=\S+ run={run['id']} result=SKIPPED\b", text)
    if len(wrote) == 1 and not skipped:
        return "WRITTEN"
    if len(skipped) == 1 and not wrote:
        return "NONE"
    return UNKNOWN


def attempt_state(reader: Any, run: dict, n: int, brief: dict) -> str:
    """What executor run `run` attempt `n` did for publication `brief` (a brief run row): EVALUATED, PROVEN_NOT_EVALUATED,
    UNKNOWN or ACTIVE. The same evidence as the executor's own once-only rule (s1_executor_v1 evaluated_before): its
    execute job and that job's ONE S1_EXECUTOR_HEALTH line, bound to the run and the attempt."""
    jobs = reader.jobs(run["id"], n)
    if not isinstance(jobs, list):
        return UNKNOWN
    ex = [j for j in jobs if isinstance(j, dict) and j.get("name") == "execute"]
    if not ex:
        return NOT_EVALUATED if run.get("status") == "completed" and run.get("conclusion") in ("skipped", "cancelled") else UNKNOWN
    if len(ex) > 1:
        return UNKNOWN
    j, steps = ex[0], ex[0].get("steps") if isinstance(ex[0].get("steps"), list) else []
    started = any(isinstance(st, dict) and st.get("status") in ("in_progress", "completed") and st.get("conclusion") != "skipped" for st in steps)
    if j.get("status") != "completed":
        return ACTIVE
    if j.get("conclusion") == "skipped" or (j.get("conclusion") == "cancelled" and not started and j.get("started_at") is None):
        return NOT_EVALUATED
    step = [st for st in steps if isinstance(st, dict) and st.get("name") == EXECUTE_STEP]
    if len(step) == 1 and step[0].get("status") == "completed" and step[0].get("conclusion") == "skipped":
        return NOT_EVALUATED                                     # failed before the execute step ran
    if type(j.get("id")) is not int:
        return UNKNOWN
    text = reader.log(j["id"])
    found = HEALTH_LINE.findall(text) if isinstance(text, str) else []
    try:
        line = json.loads(found[0]) if len(found) == 1 else None
    except ValueError:
        line = None
    if not isinstance(line, dict) or str(line.get("run")) != str(run["id"]) or str(line.get("attempt")) != str(n) \
            or not isinstance(line.get("result"), str):
        return UNKNOWN
    result, brief_run, brief_attempt = line["result"], line.get("brief_run"), line.get("brief_attempt")
    if str(brief_run) == str(brief["id"]) and brief_attempt in (None, "", str(brief.get("run_attempt", 1))):
        if not result.startswith("NO_DECISION(") or result.startswith("NO_DECISION(already_evaluated="):
            return EVALUATED
        return UNKNOWN                                           # the executor refused this publication: no blind retry
    if result.startswith(f"NO_DECISION(brief_run={brief['id']}:"):
        return UNKNOWN                                           # a dispatched run that could not prove this brief run
    if brief_run in (None, "") and not result.startswith("NO_DECISION("):
        return UNKNOWN                                           # a crash line names no brief
    return NOT_EVALUATED                                         # it was about another brief (e.g. NO_DECISION(published_run=...))


def s1exec_due(now: dt.datetime, brief_runs: list[dict], exec_runs: list[dict], reader: Any = None) -> tuple[bool, str]:
    """Liveness round (L1, FA-P2-02 recovery, Bridge #173/7215315226). Due when the ACTUAL publication P is fresh and no
    executor attempt is proven to have evaluated it, none is active and none is unknown:
      P   the newest brief run that completed with success at most S1EXEC_MAX_AGE_MINUTES ago AND whose own publish
          job logged WRITTEN (a fallback run that built nothing is skipped over; at most S1EXEC_PUBLICATION_READS runs)
      every attempt of every executor run created since P's run was created is classified (attempt_state, at most
          S1EXEC_ATTEMPT_READS): EVALUATED -> ALREADY_EVALUATED; ACTIVE (or an active run) -> TARGET_ACTIVE; UNKNOWN ->
          EVALUATION_UNKNOWN; only when every one is PROVEN_NOT_EVALUATED (or there is none) -> DUE.
    UNKNOWN fails closed and expires with the window: an old brief is never re-run, the next publication is the
    recovery. A dispatched executor still applies its own once-only rule. Re-dispatches per publication are bounded by
    the window: at most ceil(20 / tick period) + 1. Any read failure is UNKNOWN for this target only."""
    if any_active(exec_runs):
        return False, "TARGET_ACTIVE"
    if reader is None:
        return False, "EVALUATION_UNREAD"
    try:
        ok = [r for r in brief_runs or [] if r.get("status") == "completed" and r.get("conclusion") == "success"]
        if not ok:
            return False, "NO_BRIEF_RUN"
        ok.sort(key=lambda r: utc(r["created_at"]), reverse=True)
        fresh = [r for r in ok if now - utc(r["updated_at"]) <= dt.timedelta(minutes=S1EXEC_MAX_AGE_MINUTES)]
        if not fresh:
            return False, "BRIEF_TOO_OLD"
        pub = None
        for r in fresh[:S1EXEC_PUBLICATION_READS]:
            state = publication_of(reader, r)
            if state == UNKNOWN:
                return False, "PUBLICATION_UNKNOWN"
            if state == "WRITTEN":
                pub = r
                break
        if pub is None:
            return False, "NO_FRESH_PUBLICATION"
        since = utc(pub["created_at"])
        attempts = []
        for e in exec_runs or []:
            if utc(e["created_at"]) < since:
                continue
            last = e.get("run_attempt", 1)
            if type(last) is not int or last < 1:
                return False, "EVALUATION_UNKNOWN"
            attempts += [(e, n) for n in range(1, last + 1)]
        if len(attempts) > S1EXEC_ATTEMPT_READS:
            return False, "EVALUATION_UNKNOWN"
        states = [attempt_state(reader, e, n, pub) for e, n in attempts]
    except (KeyError, TypeError, ValueError, AttributeError):
        return False, "RUN_ROW_UNREADABLE"
    if EVALUATED in states:
        return False, "ALREADY_EVALUATED"
    if ACTIVE in states:
        return False, "TARGET_ACTIVE"
    if UNKNOWN in states:
        return False, "EVALUATION_UNKNOWN"
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
    # Do not burn unlimited Actions minutes on a broken market-close producer.
    # The source writer remains authoritative; only native failed run census
    # from this specific Monday may control a bounded retry. Never classify an
    # early Sunday preclose as a successful Monday final.
    eligible = []
    for row in runs:
        try:
            when = utc(row["created_at"])
        except (KeyError, ValueError, TypeError):
            return False, "FINAL_RUN_CLOCK_UNREADABLE"
        if when >= start.astimezone(dt.timezone.utc):
            eligible.append(when)
    if len(eligible) >= MAX_FINAL_ATTEMPTS_PER_MONDAY:
        return False, "FINAL_RETRY_BUDGET_EXHAUSTED"
    if eligible and now - max(eligible) < dt.timedelta(minutes=FINAL_RETRY_COOLDOWN_MINUTES):
        return False, "FINAL_RETRY_COOLDOWN"
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
DATA_TARGET_KEYS = frozenset({"HOURLY", "RECOVERY", "S1BRIEF", "S1EXEC"})


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
           s1brief_runs: list[dict] | None = None, s1exec_runs: list[dict] | None = None,
           s1exec_reader: Any = None) -> dict:
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
        (S1EXEC, lambda: s1exec_due(now, s1brief_runs or [], s1exec_runs or [], s1exec_reader)),
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


class _LogRedirect(urllib.request.HTTPRedirectHandler):
    """Follow a job-log redirect only to GitHub's log storage, and never forward the token to another host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urlsplit(newurl)
        host = target.hostname or ""
        azure = re.fullmatch(r"productionresultssa[0-9]{1,3}[.]blob[.]core[.]windows[.]net", host) is not None
        if target.scheme != "https" or target.username or target.password or target.port not in (None, 443) \
                or not (host == "api.github.com" or host.endswith(".githubusercontent.com") or azure):
            raise ValueError("JOB_LOG_REDIRECT_HOST_UNVERIFIED")
        follow = super().redirect_request(req, fp, code, msg, headers, newurl)
        if follow is not None and host != urlsplit(req.full_url).hostname:
            for store in (follow.headers, follow.unredirected_hdrs):
                for key in list(store):
                    if key.casefold() in ("authorization", "proxy-authorization", "cookie"):
                        del store[key]
        return follow


class S1ExecReader:
    """The S1EXEC target's reads (jobs, logs), each failure an unread (None) for THAT target only: the other targets
    and the loop never fail because of it. Capped: S1EXEC_PUBLICATION_READS and S1EXEC_ATTEMPT_READS pairs."""

    MAX_READS = 2 * (S1EXEC_PUBLICATION_READS + S1EXEC_ATTEMPT_READS)

    def __init__(self, gh: Any):
        self.gh, self.reads = gh, 0

    def _call(self, fn, *args):
        if self.reads >= self.MAX_READS:
            return None
        self.reads += 1
        try:
            return fn(*args)
        except Exception:  # noqa: BLE001  (unread: UNKNOWN for S1EXEC)
            return None

    def jobs(self, run_id, attempt):
        return self._call(getattr(self.gh, "jobs", None) or (lambda *a: None), run_id, attempt)

    def log(self, job_id):
        return self._call(getattr(self.gh, "log", None) or (lambda *a: None), job_id)


class Github:
    """Minimal client: GET runs/environment/mode file, GET the S1 brief/executor jobs and job logs, POST workflow
    dispatches. Nothing else."""

    READ_BUDGET_SECONDS = 90  # total wall-clock budget for all reads in one tick (fail closed when spent)

    def __init__(self, token: str, repo: str = REPO, budget_seconds: float | None = None):
        self.token, self.repo = token, repo
        self.deadline = time.monotonic() + (self.READ_BUDGET_SECONDS if budget_seconds is None else budget_seconds)

    def _req(self, method: str, route: str, payload: dict | None = None) -> Any:
        allowed = (
            (method == "GET" and route.startswith(f"/repos/{self.repo}/actions/workflows/") and "/runs?" in route)
            or (method == "GET" and route == f"/repos/{self.repo}/environments/{ENVIRONMENT}")
            or (method == "GET" and route == f"/repos/{self.repo}/contents/{MODE_PATH}?ref=main")
            # liveness round (L1): the S1 brief's publish log and the executor's job logs (actions: read, held already)
            or (method == "GET" and re.fullmatch(rf"/repos/{re.escape(self.repo)}/actions/runs/\d{{1,20}}(?:/attempts/\d{{1,3}})?/jobs\?per_page=30", route) is not None)
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

    def jobs(self, run_id: int, attempt: int | None) -> Any:
        """The jobs of one run (latest attempt) or of one attempt; a malformed answer raises."""
        tail = f"/attempts/{int(attempt)}" if attempt is not None else ""
        doc = self._req("GET", f"/repos/{self.repo}/actions/runs/{int(run_id)}{tail}/jobs?per_page=30")
        if not isinstance(doc, dict) or not isinstance(doc.get("jobs"), list) or doc.get("total_count") != len(doc["jobs"]):
            raise ValueError("JOBS_INVALID_SHAPE")
        return doc["jobs"]

    def log(self, job_id: int) -> str:
        """One job's log (GET actions/jobs/<id>/logs). GitHub redirects to its log storage: only GitHub's own storage
        hosts are followed and the token is never sent to the second host. Size-capped; read budget applies."""
        if time.monotonic() >= self.deadline:
            raise TimeoutError("READ_BUDGET_EXCEEDED")
        req = urllib.request.Request(f"https://api.github.com/repos/{self.repo}/actions/jobs/{int(job_id)}/logs", method="GET", headers={
            "Accept": "application/vnd.github+json", "Authorization": "Bearer " + self.token,
            "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "framework-metronome-v1"})
        with urllib.request.build_opener(_LogRedirect()).open(req, timeout=max(1.0, min(30.0, self.deadline - time.monotonic()))) as r:
            raw = r.read(4 * 1024 * 1024 + 1)
        if len(raw) > 4 * 1024 * 1024:
            raise ValueError("JOB_LOG_TOO_LARGE")
        return raw.decode("utf-8", "replace")

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
        ("S1EXEC", S1EXEC["workflow"]),
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
                  s1brief_runs=production_runs(raw_runs["S1BRIEF"]),
                  s1exec_runs=production_runs(raw_runs["S1EXEC"]),
                  s1exec_reader=S1ExecReader(gh))
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
