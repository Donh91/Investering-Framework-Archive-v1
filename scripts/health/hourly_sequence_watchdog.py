#!/usr/bin/env python3
"""Fail-safe watchdog for the Hourly Sequence -> Intraday/T12 production chain.

The watchdog never writes market state. It only dispatches the existing
``hourly-sequence-capture.yml`` workflow when its durable owner pointer is stale
and no equivalent run is already active/recent. The existing Hourly workflow
remains the sole producer of Hourly and Intraday/T12 evidence.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

CONTRACT = "HOURLY_SEQUENCE_SELF_HEAL_WATCHDOG_v1"
DEFAULT_WORKFLOW = "hourly-sequence-capture.yml"
ACTIVE_STATUSES = {"queued", "in_progress", "waiting", "pending", "requested"}


def parse_utc(value: str) -> datetime:
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def utc_text(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def load_latest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("LATEST payload must be a JSON object")
    return payload


def freshness(latest: dict[str, Any], now: datetime, stale_after_minutes: int) -> dict[str, Any]:
    if stale_after_minutes < 1:
        raise ValueError("stale_after_minutes must be positive")
    status = str(latest.get("status") or "UNKNOWN")
    raw_end = latest.get("window_end_utc")
    if not raw_end:
        return {
            "is_stale": True,
            "reason": "WINDOW_END_MISSING",
            "latest_status": status,
            "window_end_utc": None,
            "age_minutes": None,
        }
    window_end = parse_utc(str(raw_end))
    age_minutes = (now - window_end).total_seconds() / 60.0
    if age_minutes < -5:
        return {
            "is_stale": True,
            "reason": "WINDOW_END_IN_FUTURE",
            "latest_status": status,
            "window_end_utc": utc_text(window_end),
            "age_minutes": round(age_minutes, 3),
        }
    if status != "COMPLETE":
        reason = "LATEST_NOT_COMPLETE"
        is_stale = True
    elif age_minutes > stale_after_minutes:
        reason = "WINDOW_END_STALE"
        is_stale = True
    else:
        reason = "FRESH"
        is_stale = False
    return {
        "is_stale": is_stale,
        "reason": reason,
        "latest_status": status,
        "window_end_utc": utc_text(window_end),
        "age_minutes": round(age_minutes, 3),
    }


def _run_created_at(run: dict[str, Any]) -> datetime | None:
    raw = run.get("created_at")
    if not raw:
        return None
    try:
        return parse_utc(str(raw))
    except (TypeError, ValueError):
        return None


def run_guard(runs: Iterable[dict[str, Any]], now: datetime, recent_guard_minutes: int) -> dict[str, Any]:
    if recent_guard_minutes < 0:
        raise ValueError("recent_guard_minutes cannot be negative")
    rows = [row for row in runs if isinstance(row, dict)]
    active = [row for row in rows if str(row.get("status") or "").lower() in ACTIVE_STATUSES]
    if active:
        newest = max(active, key=lambda row: _run_created_at(row) or datetime.min.replace(tzinfo=timezone.utc))
        return {
            "blocked": True,
            "reason": "ACTIVE_EQUIVALENT_RUN",
            "run_id": newest.get("id"),
            "run_status": newest.get("status"),
            "run_event": newest.get("event"),
        }

    cutoff = now - timedelta(minutes=recent_guard_minutes)
    recent: list[dict[str, Any]] = []
    for row in rows:
        created = _run_created_at(row)
        if created is not None and created >= cutoff:
            recent.append(row)
    if recent:
        newest = max(recent, key=lambda row: _run_created_at(row) or cutoff)
        return {
            "blocked": True,
            "reason": "RECENT_EQUIVALENT_RUN_RACE_GUARD",
            "run_id": newest.get("id"),
            "run_status": newest.get("status"),
            "run_event": newest.get("event"),
        }
    return {"blocked": False, "reason": "NO_ACTIVE_OR_RECENT_EQUIVALENT_RUN"}


@dataclass
class GitHubActionsClient:
    repo: str
    token: str
    workflow: str = DEFAULT_WORKFLOW
    timeout_seconds: int = 20

    def _request(self, url: str, method: str = "GET", body: dict[str, Any] | None = None) -> Any:
        data = None if body is None else json.dumps(body, separators=(",", ":")).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": CONTRACT,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read()
                if not raw:
                    return None
                return json.loads(raw.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:1000]
            raise RuntimeError(f"GitHub API {method} {url} failed: HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"GitHub API {method} {url} failed: {exc.reason}") from exc

    def list_runs(self) -> list[dict[str, Any]]:
        url = f"https://api.github.com/repos/{self.repo}/actions/workflows/{self.workflow}/runs?per_page=20"
        payload = self._request(url)
        rows = (payload or {}).get("workflow_runs", []) if isinstance(payload, dict) else []
        if not isinstance(rows, list):
            raise RuntimeError("GitHub workflow-runs response has invalid shape")
        return [row for row in rows if isinstance(row, dict)]

    def dispatch(self, ref: str = "main") -> None:
        url = f"https://api.github.com/repos/{self.repo}/actions/workflows/{self.workflow}/dispatches"
        self._request(url, method="POST", body={"ref": ref})


def build_receipt(
    latest: dict[str, Any],
    now: datetime,
    stale_after_minutes: int,
    recent_guard_minutes: int,
    runs: Iterable[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    fresh = freshness(latest, now, stale_after_minutes)
    receipt: dict[str, Any] = {
        "contract": CONTRACT,
        "generated_at_utc": utc_text(now),
        "authority": {
            "canonical_market_state": False,
            "portfolio_execution": False,
            "automatic_rule_changes": False,
            "dispatch_existing_owner_only": True,
        },
        "stale_after_minutes": stale_after_minutes,
        "recent_run_guard_minutes": recent_guard_minutes,
        "owner": {
            "contract": latest.get("contract"),
            "run_id": latest.get("run_id"),
            **fresh,
        },
    }
    if not fresh["is_stale"]:
        receipt.update({"decision": "NOOP_FRESH", "guard": None})
        return receipt
    guard = run_guard(runs or [], now, recent_guard_minutes)
    receipt["guard"] = guard
    receipt["decision"] = "NOOP_ACTIVE_OR_RECENT_RUN" if guard["blocked"] else "DISPATCH_REQUIRED"
    return receipt


def write_receipt(path: Path, receipt: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--latest", type=Path, default=Path("03_DAILY_CAPTURE_LOGS/hourly/LATEST.json"))
    parser.add_argument("--repo", default=os.getenv("GITHUB_REPOSITORY", ""))
    parser.add_argument("--token", default=os.getenv("GITHUB_TOKEN", ""))
    parser.add_argument("--workflow", default=DEFAULT_WORKFLOW)
    parser.add_argument("--ref", default="main")
    parser.add_argument("--stale-after-minutes", type=int, default=90)
    parser.add_argument("--recent-run-guard-minutes", type=int, default=12)
    parser.add_argument("--now", help="UTC ISO timestamp for deterministic testing")
    parser.add_argument("--dispatch", action="store_true")
    parser.add_argument("--receipt", type=Path, default=Path("hourly-watchdog-receipt.json"))
    args = parser.parse_args(argv)

    now = parse_utc(args.now) if args.now else datetime.now(timezone.utc)
    try:
        latest = load_latest(args.latest)
        base = freshness(latest, now, args.stale_after_minutes)
        runs: list[dict[str, Any]] = []
        client: GitHubActionsClient | None = None
        if base["is_stale"]:
            if not args.repo or not args.token:
                if args.dispatch:
                    raise RuntimeError("--dispatch requires repo and token")
            else:
                client = GitHubActionsClient(args.repo, args.token, args.workflow)
                runs = client.list_runs()
        receipt = build_receipt(
            latest,
            now,
            args.stale_after_minutes,
            args.recent_run_guard_minutes,
            runs,
        )
        if receipt["decision"] == "DISPATCH_REQUIRED":
            if args.dispatch:
                if client is None:
                    raise RuntimeError("GitHub client unavailable for required dispatch")
                client.dispatch(args.ref)
                receipt["decision"] = "DISPATCHED_SELF_HEAL"
                receipt["dispatch"] = {"workflow": args.workflow, "ref": args.ref}
            else:
                receipt["decision"] = "WOULD_DISPATCH"
        write_receipt(args.receipt, receipt)
        print(json.dumps(receipt, sort_keys=True))
        return 0
    except Exception as exc:  # fail closed and preserve a durable artifact for the job
        failure = {
            "contract": CONTRACT,
            "generated_at_utc": utc_text(now),
            "decision": "WATCHDOG_ERROR",
            "error_class": type(exc).__name__,
            "error": str(exc)[:1500],
            "authority": {
                "canonical_market_state": False,
                "portfolio_execution": False,
                "automatic_rule_changes": False,
                "dispatch_existing_owner_only": True,
            },
        }
        try:
            write_receipt(args.receipt, failure)
        except Exception:
            pass
        print(json.dumps(failure, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
