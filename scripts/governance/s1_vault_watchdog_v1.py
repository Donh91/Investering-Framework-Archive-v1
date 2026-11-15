#!/usr/bin/env python3
"""S1 and Vault watchdog that needs no Claude session (read-mostly; posts at most one alert).

Runs inside the EXISTING twice-daily "Automation Production Health" workflow (no new
schedule). It reads Archive issue comments only:

  - #1156: the newest S1_HEARTBEAT_v1 must be younger than HEARTBEAT_MAX_AGE_H.
  - #1593: the NEWEST VAULT_FINAL_REF_RECEIPT_v1 authored by the Vault receipt GitHub App
           (a bot identity S1 cannot impersonate) must parse as a valid seal (schema, state,
           ref, run, hashes) and be younger than VAULT_MAX_AGE_H. Text matching is never used.

On a breach it posts ONE alert on #1156 per cause per UTC day, mentioning the owner so
GitHub notifies him. It never reads the Vault, never dispatches anything and never
changes any file.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.request
from typing import Callable, Iterable

REPO = "Donh91/Investering-Framework-Archive-v1"
S1_ISSUE, VAULT_ISSUE = 1156, 1593
HEARTBEAT_MAX_AGE_H = 26
VAULT_MAX_AGE_H = 30
OWNER_MENTION = "@Donh91"
VAULT_APP_SLUG = "framework-vault-receipts"  # set once the owner has created the App
ALERT_TAG = "S1_VAULT_WATCHDOG_ALERT_v1"
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def utc(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def newest(comments: list[dict], pred: Callable[[dict], bool]) -> dict | None:
    hits = [c for c in comments if isinstance(c, dict) and pred(c)]
    return max(hits, key=lambda c: utc(c["created_at"])) if hits else None


def is_heartbeat(c: dict) -> bool:
    return str(c.get("body", "")).lstrip().startswith("S1_HEARTBEAT_v1")


RECEIPT_MARKER = re.compile(r"<!-- VAULT_FINAL_REF_RECEIPT_v1:(\d+)-(\d+) -->")
NATIVE_RECEIPT_MARKER = re.compile(r"<!-- VAULT_NATIVE_RECEIPT_V1:(\d+)-(\d+) -->")
JSON_BLOCK = re.compile(r"~~~json\s*\n(.*?)\n~~~", re.S)
FINAL_REF = re.compile(r"^refs/heads/backup/vault-final-\d{8}-(\d+)-(\d+)$")


def is_app_comment(c: dict) -> bool:
    """Only the Vault receipt App counts; a comment from the shared owner account never does."""
    user = c.get("user") or {}
    app = c.get("performed_via_github_app") or {}
    return (user.get("type") == "Bot" and user.get("login") == f"{VAULT_APP_SLUG}[bot]"
            and app.get("slug") == VAULT_APP_SLUG)


def is_receipt_comment(c: dict) -> bool:
    return is_app_comment(c) and RECEIPT_MARKER.search(str(c.get("body", ""))) is not None


def is_native_receipt_comment(c: dict) -> bool:
    """Distinct native recovery proof, not final-ref authority."""
    return is_app_comment(c) and NATIVE_RECEIPT_MARKER.search(str(c.get("body", ""))) is not None


def valid_seal(body: str) -> bool:
    """Structured check of one VAULT_FINAL_REF_RECEIPT_v1. Anything unknown or malformed is NOT a seal."""
    marker = RECEIPT_MARKER.search(body)
    block = JSON_BLOCK.search(body)
    if not marker or not block:
        return False
    try:
        r = json.loads(block.group(1))
    except ValueError:
        return False
    if not isinstance(r, dict):
        return False
    ref = FINAL_REF.match(str(r.get("final_ref", "")))
    return (r.get("schema") == "VAULT_FINAL_REF_RECEIPT_v1"
            and r.get("final_state") == "CREATED_BY_THIS_FINALIZER"
            and r.get("release_permission") is False
            and ref is not None
            and str(r.get("run_id")) == marker.group(1) == ref.group(1)
            and str(r.get("run_attempt")) == marker.group(2) == ref.group(2)
            and all(isinstance(r.get(k), str) and SHA40.match(r[k]) for k in ("snapshot_commit", "source_sha", "source_tree_sha"))
            and isinstance(r.get("verified_files"), int) and not isinstance(r.get("verified_files"), bool)
            and r["verified_files"] > 0)


def evaluate(s1_comments: list[dict], vault_comments: list[dict], now: dt.datetime) -> list[dict]:
    """Return the list of breached causes (empty when healthy)."""
    causes = []
    hb = newest(s1_comments, is_heartbeat)
    if hb is None:
        causes.append({"cause": "S1_HEARTBEAT_MISSING", "last": None})
    elif now - utc(hb["created_at"]) > dt.timedelta(hours=HEARTBEAT_MAX_AGE_H):
        causes.append({"cause": "S1_HEARTBEAT_STALE", "last": hb["created_at"]})
    vr = newest(vault_comments, is_receipt_comment)  # the NEWEST App receipt decides, never an older one
    if vr is None:
        native = newest(vault_comments, is_native_receipt_comment)
        if native is not None:
            causes.append({"cause": "VAULT_APP_FINAL_REF_MISSING", "last": native["created_at"]})
        else:
            causes.append({"cause": "VAULT_APP_RECEIPT_MISSING", "last": None})
    elif not valid_seal(str(vr.get("body", ""))):
        causes.append({"cause": "VAULT_RECEIPT_INVALID", "last": vr["created_at"]})
    elif now - utc(vr["created_at"]) > dt.timedelta(hours=VAULT_MAX_AGE_H):
        causes.append({"cause": "VAULT_RECEIPT_STALE", "last": vr["created_at"]})
    return causes


def already_alerted(s1_comments: list[dict], cause: str, now: dt.datetime) -> bool:
    day = now.strftime("%Y-%m-%d")
    return any(str(c.get("body", "")).startswith(f"{ALERT_TAG} {cause} {day}") for c in s1_comments)


def alert_body(cause: dict, now: dt.datetime) -> str:
    fixes = {
        "S1_HEARTBEAT_MISSING": "Open the S1 task in ChatGPT and check its run history; restore the task text to 00_FMOS/S1/BOOTSTRAP.txt verbatim if it drifted.",
        "S1_HEARTBEAT_STALE": "Open the S1 task in ChatGPT and check its run history; restore the task text to 00_FMOS/S1/BOOTSTRAP.txt verbatim if it drifted.",
        "VAULT_APP_RECEIPT_MISSING": "Neither an App-authored native receipt nor an App-authored final-ref receipt is visible. Have the independent Vault owner inspect the normal scheduled run and publisher before considering any further backup. Agents never dispatch Vault.",
        "VAULT_APP_FINAL_REF_MISSING": "A genuine App-authored native recovery receipt exists, but no App-authored FINAL REF seal is visible. Investigate the finalizer job, protected ref, App installation-token POST identity and 403/429 errors. Do not re-run the snapshot as the first remedy. HIGH merges remain on HOLD.",
        "VAULT_RECEIPT_STALE": "The App-authored final-ref seal is stale. Have the independent Vault owner inspect newer natural backup and finalizer receipts before considering another run. HIGH merges remain on HOLD.",
        "VAULT_RECEIPT_INVALID": "The newest Vault receipt is not a valid seal (schema, state, ref or hashes do not check out). Open the Vault Actions run named in it and the #1593 comment; HIGH merges stay on hold.",
    }
    return (f"{ALERT_TAG} {cause['cause']} {now:%Y-%m-%d}\n\n{OWNER_MENTION} last seen: {cause['last'] or 'never'}. "
            f"{fixes[cause['cause']]}\n\nPosted by the Automation Production Health watchdog. No Claude session is needed.")


class Github:
    def __init__(self, token: str):
        self.token = token

    def _req(self, method: str, route: str, payload: dict | None = None):
        if not route.startswith("/repos/" + REPO + "/issues/"):
            raise ValueError("ROUTE_NOT_ALLOWED")
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request("https://api.github.com" + route, data=data, method=method, headers={
            "Accept": "application/vnd.github+json", "Authorization": "Bearer " + self.token,
            "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "s1-vault-watchdog-v1"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)

    def comments(self, issue: int, pages: int = 3) -> list[dict]:
        meta = self._req("GET", f"/repos/{REPO}/issues/{issue}")
        total = int(meta.get("comments", 0))
        last = max(1, (total + 99) // 100)
        out: list[dict] = []
        for page in range(max(1, last - pages + 1), last + 1):
            out += self._req("GET", f"/repos/{REPO}/issues/{issue}/comments?per_page=100&page={page}")
        return out

    def post(self, issue: int, body: str) -> None:
        self._req("POST", f"/repos/{REPO}/issues/{issue}/comments", {"body": body})


def run(gh, now: dt.datetime, dry_run: bool) -> dict:
    s1, vault = gh.comments(S1_ISSUE), gh.comments(VAULT_ISSUE)
    causes = evaluate(s1, vault, now)
    posted = []
    for cause in causes:
        if already_alerted(s1, cause["cause"], now):
            continue
        if not dry_run:
            gh.post(S1_ISSUE, alert_body(cause, now))
        posted.append(cause["cause"])
    return {"contract": "S1_VAULT_WATCHDOG_RESULT_v1", "checked_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "causes": [c["cause"] for c in causes], "posted": posted, "dry_run": dry_run}


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(list(argv) if argv is not None else None)
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print(json.dumps({"status": "SKIPPED_NO_TOKEN"}))
        return 0
    result = run(Github(token), dt.datetime.now(dt.timezone.utc), args.dry_run)
    print(json.dumps(result, sort_keys=True))
    return 0  # never fails the health job; the alert comment is the signal


if __name__ == "__main__":
    sys.exit(main())
