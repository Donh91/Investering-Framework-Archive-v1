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
VAULT_APP_BOT_USER_ID = 356654356  # framework-vault-receipts[bot], read back on Archive #1593
S1_LOGIN = "Donh91"  # the account S1 posts its heartbeat from
ALERT_LOGIN = "github-actions[bot]"  # the identity this workflow posts alerts as
ALERT_TAG = "S1_VAULT_WATCHDOG_ALERT_v1"
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def utc(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def newest(comments: list[dict], pred: Callable[[dict], bool]) -> dict | None:
    hits = [c for c in comments if isinstance(c, dict) and pred(c)]
    return max(hits, key=lambda c: utc(c["created_at"])) if hits else None


def unedited(c: dict) -> bool:
    """GitHub lets repository writers edit other users' comments while the author fields stay the same."""
    return isinstance(c.get("created_at"), str) and c.get("updated_at") == c.get("created_at")


def is_heartbeat(c: dict) -> bool:
    """Only S1's own account counts; anyone can comment on a public issue, so a body prefix alone is not enough."""
    user = c.get("user") if isinstance(c.get("user"), dict) else {}
    return user.get("login") == S1_LOGIN and str(c.get("body", "")).lstrip().startswith("S1_HEARTBEAT_v1")


RECEIPT_MARKER = re.compile(r"<!-- VAULT_FINAL_REF_RECEIPT_v1:(\d+)-(\d+) -->")
NATIVE_RECEIPT_MARKER = re.compile(r"<!-- VAULT_NATIVE_RECEIPT_V1:(\d+)-(\d+) -->")
JSON_BLOCK = re.compile(r"~~~json\s*\n(.*?)\n~~~", re.S)
FINAL_REF = re.compile(r"^refs/heads/backup/vault-final-(?P<day>\d{8})-(?P<run>\d+)-(?P<attempt>\d+)$")


def is_app_identity(c: dict) -> bool:
    """Only the Vault receipt App counts; a comment from the shared owner account never does."""
    user = c.get("user") if isinstance(c.get("user"), dict) else {}
    app = c.get("performed_via_github_app") if isinstance(c.get("performed_via_github_app"), dict) else {}
    return (user.get("type") == "Bot" and user.get("login") == f"{VAULT_APP_SLUG}[bot]"
            and user.get("id") == VAULT_APP_BOT_USER_ID and app.get("slug") == VAULT_APP_SLUG)


def is_app_comment(c: dict) -> bool:
    """An App comment counts only if nobody edited it after the App posted it."""
    return is_app_identity(c) and unedited(c)


def is_edited_app_receipt(c: dict) -> bool:
    body = str(c.get("body", ""))
    return (is_app_identity(c) and not unedited(c)
            and (RECEIPT_MARKER.search(body) is not None or NATIVE_RECEIPT_MARKER.search(body) is not None))


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
    except (ValueError, RecursionError):
        return False
    if not isinstance(r, dict):
        return False
    ref = FINAL_REF.match(str(r.get("final_ref", "")))
    return (r.get("schema") == "VAULT_FINAL_REF_RECEIPT_v1"
            and r.get("final_state") == "CREATED_BY_THIS_FINALIZER"
            and r.get("release_permission") is False
            and ref is not None
            and str(r.get("run_id")) == marker.group(1) == ref.group("run")
            and str(r.get("run_attempt")) == marker.group(2) == ref.group("attempt")
            and all(isinstance(r.get(k), str) and SHA40.match(r[k]) for k in ("snapshot_commit", "source_sha", "source_tree_sha"))
            and isinstance(r.get("verified_files"), int) and not isinstance(r.get("verified_files"), bool)
            and r["verified_files"] > 0)


def seal_day(body: str) -> dt.date | None:
    """The UTC day encoded in the sealed final ref (only called for a valid seal)."""
    try:
        ref = FINAL_REF.match(str(json.loads(JSON_BLOCK.search(body).group(1)).get("final_ref", "")))
        return dt.datetime.strptime(ref.group("day"), "%Y%m%d").date() if ref else None
    except (ValueError, RecursionError, AttributeError):
        return None


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
    else:
        # A fresh comment must also seal a fresh run. The ref day is the UTC day the sealed attempt ran,
        # so it may trail the comment by at most one day; an App re-post of an old run is stale.
        day = seal_day(str(vr.get("body", "")))
        if day is None or day > now.date():
            causes.append({"cause": "VAULT_RECEIPT_INVALID", "last": vr["created_at"]})
        elif day < (now - dt.timedelta(hours=VAULT_MAX_AGE_H + 24)).date():
            causes.append({"cause": "VAULT_RECEIPT_STALE", "last": vr["created_at"]})
    edited = newest([x for x in vault_comments if is_edited_app_receipt(x) and isinstance(x.get("updated_at"), str)
                     and now - utc(x["updated_at"]) <= dt.timedelta(hours=VAULT_MAX_AGE_H)], lambda _x: True)
    if edited is not None:
        causes.append({"cause": "VAULT_APP_RECEIPT_EDITED", "last": edited["updated_at"]})
    return causes


def already_alerted(s1_comments: list[dict], cause: str, now: dt.datetime) -> bool:
    """Only an alert this workflow itself posted can suppress a repeat; any other author's line cannot."""
    day = now.strftime("%Y-%m-%d")
    def by_watchdog(c: dict) -> bool:
        user = c.get("user") if isinstance(c.get("user"), dict) else {}
        return user.get("login") == ALERT_LOGIN and user.get("type") == "Bot"
    return any(isinstance(c, dict) and by_watchdog(c)
               and str(c.get("body", "")).startswith(f"{ALERT_TAG} {cause} {day}") for c in s1_comments)


def alert_body(cause: dict, now: dt.datetime) -> str:
    fixes = {
        "S1_HEARTBEAT_MISSING": "Open the S1 task in ChatGPT and check its run history; restore the task text to 00_FMOS/S1/BOOTSTRAP.txt verbatim if it drifted.",
        "S1_HEARTBEAT_STALE": "Open the S1 task in ChatGPT and check its run history; restore the task text to 00_FMOS/S1/BOOTSTRAP.txt verbatim if it drifted.",
        "VAULT_APP_RECEIPT_MISSING": "Neither an App-authored native receipt nor an App-authored final-ref receipt is visible. Have the independent Vault owner inspect the normal scheduled run and publisher before considering any further backup. Agents never dispatch Vault.",
        "VAULT_APP_FINAL_REF_MISSING": "A genuine App-authored native recovery receipt exists, but no App-authored FINAL REF seal is visible. Investigate the finalizer job, protected ref, App installation-token POST identity and 403/429 errors. Do not re-run the snapshot as the first remedy. HIGH merges remain on HOLD.",
        "VAULT_RECEIPT_STALE": "The App-authored final-ref seal is stale. Have the independent Vault owner inspect newer natural backup and finalizer receipts before considering another run. HIGH merges remain on HOLD.",
        "VAULT_RECEIPT_INVALID": "The newest Vault receipt is not a valid seal (schema, state, ref or hashes do not check out). Open the Vault Actions run named in it and the #1593 comment; HIGH merges stay on hold.",
        "VAULT_APP_RECEIPT_EDITED": "An App-authored Vault receipt on #1593 was edited after the App posted it. Edited receipts never count. Check the comment's edit history; HIGH merges stay on hold.",
        "WATCHDOG_ERROR": "The watchdog itself failed and could not evaluate S1 or the Vault. Open the Automation Production Health run log; treat the state as unverified.",
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
    posted, post_errors = [], []
    for cause in causes:
        if already_alerted(s1, cause["cause"], now):
            continue
        if not dry_run:
            try:  # one failed POST never hides the remaining causes
                gh.post(S1_ISSUE, alert_body(cause, now))
            except Exception as exc:  # noqa: BLE001
                post_errors.append(f"{cause['cause']}:{type(exc).__name__}")
                continue
        posted.append(cause["cause"])
    return {"contract": "S1_VAULT_WATCHDOG_RESULT_v1", "checked_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "causes": [c["cause"] for c in causes], "posted": posted, "post_errors": post_errors, "dry_run": dry_run}


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(list(argv) if argv is not None else None)
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print(json.dumps({"status": "SKIPPED_NO_TOKEN"}))
        return 0
    now = dt.datetime.now(dt.timezone.utc)
    gh = Github(token)
    try:
        result = run(gh, now, args.dry_run)
    except Exception as exc:  # noqa: BLE001 - the step is continue-on-error; never fail silently
        result = {"contract": "S1_VAULT_WATCHDOG_RESULT_v1", "status": "WATCHDOG_ERROR", "error": type(exc).__name__,
                  "checked_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "dry_run": args.dry_run}
        if not args.dry_run:
            try:
                gh.post(S1_ISSUE, alert_body({"cause": "WATCHDOG_ERROR", "last": None}, now))
            except Exception as post_exc:  # noqa: BLE001
                result["post_error"] = type(post_exc).__name__
    if result.get("status") == "WATCHDOG_ERROR" or result.get("post_errors"):
        print(f"::error title=S1 Vault watchdog::{result.get('status', 'POST_ERRORS')} "
              f"{result.get('error', '')} {','.join(result.get('post_errors', []))}".strip())
    print(json.dumps(result, sort_keys=True))
    return 0  # never fails the health job; the alert comment and the ::error annotation are the signal


if __name__ == "__main__":
    sys.exit(main())
