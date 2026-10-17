"""Read-only exact-head Codex review finality preflight; NEVER approves or merges."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone


def stamp(value):
    if not isinstance(value, str):
        raise ValueError("TIMESTAMP_MISSING")
    d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if d.tzinfo is None:
        raise ValueError("TIMESTAMP_UNAWARE")
    return d.astimezone(timezone.utc)


def effective_request_time(row):
    """Edits adding @codex review are new requests, not old comments."""
    created = stamp(row.get("created_at"))
    updated = stamp(row["updated_at"]) if row.get("updated_at") else created
    if updated < created:
        raise ValueError("COMMENT_CLOCK_REGRESSION")
    return updated


def is_codex(row):
    user = row.get("user") or {}
    return (isinstance(user, dict) and user.get("login") == "chatgpt-codex-connector[bot]" and user.get("type") == "Bot" and user.get("id") == 199175422)


def decision(head, comments, reviews, inline):
    """Require positive exact-head completion AFTER the latest human request."""
    fail = lambda reason: {"status": reason, "technical_review_accepted": False}
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        return fail("INVALID_HEAD")
    try:
        requests = [effective_request_time(row) for row in comments
                    if not is_codex(row) and re.search(r"(?mi)^\s*@codex\s+review\b", str(row.get("body") or ""))]
        if not requests:
            return fail("REVIEW_NOT_REQUESTED")
        last = max(requests)
        completed = []
        latest_state = []
        positive = []
        for row in comments:
            if not is_codex(row):
                continue
            body = str(row.get("body") or "")
            when = stamp(row.get("updated_at") or row.get("created_at"))
            # GitHub comment timestamps are second-resolution. A receipt with
            # the same time as a request could PRECEDE it; fail closed.
            if when <= last:
                continue
            m = re.search(r"<!-- codex-review-state:v1\s+(.+?)\s*-->", body, re.S)
            if m:
                state = json.loads(m.group(1)).get("code_review", {})
                if state.get("commit_sha") == head:
                    latest_state.append((when, state))
                    if state.get("status") == "completed":
                        completed.append((when, state))
            if "Codex Review: Didn't find any major issues" in body:
                m = re.search(r"Reviewed commit:\*\*\s*\x60([a-f0-9]{10,40})\x60", body)
                if m and head.startswith(m.group(1)):
                    positive.append((when, m.group(1)))
        if not completed or not positive:
            return fail("REVIEW_IN_PROGRESS_OR_UNVERIFIED")
        # GitHub exposes second-resolution comment timestamps. Sorting tied
        # state events by pagination/API order would allow a preceding clean
        # completion to conceal a later running or adverse review. Treat an
        # indistinguishable latest state conflict as UNVERIFIED, not APPROVED.
        latest_time = max(when for when, _state in latest_state)
        tied_states = [state for when, state in latest_state if when == latest_time]
        if any(state != tied_states[0] for state in tied_states[1:]):
            return fail("AMBIGUOUS_CODEX_STATE_SEQUENCE")
        latest = tied_states[0]
        if latest.get("status") != "completed":
            return fail("NEWER_CODEX_REVIEW_NOT_COMPLETE")
        if latest.get("has_unresolved_findings") is not False:
            return fail("UNRESOLVED_CODEX_FINDINGS")
        last_positive, positive_ref = max(positive)
        # Codex currently emits a 10-hex receipt but a full SHA in its trusted
        # state JSON. The same separately authenticated bot must attest both,
        # and the complete state must finish no later than the positive receipt.
        # Never accept a short-prefix receipt without this exact full-SHA bind.
        if not any(state_time < last_positive and state.get("commit_sha") == head
                   and state.get("has_unresolved_findings") is False
                   for state_time, state in completed):
            return fail("POSITIVE_WITHOUT_EXACT_HEAD_COMPLETION")
        for row in reviews:
            if (not is_codex(row) or row.get("commit_id") != head
                    or stamp(row.get("submitted_at")) <= last):
                continue
            body = str(row.get("body") or "")
            if stamp(row.get("submitted_at")) > last_positive and re.search(r"\bP[012]\b|review suggestions", body, re.I):
                return fail("LATER_MATERIAL_REVIEW_FINDINGS")
        for row in inline:
            if not is_codex(row) or head not in (row.get("commit_id"), row.get("original_commit_id")):
                continue
            if stamp(row.get("created_at")) >= last and re.search(r"\bP[012]\b|codex-code-review-finding:v1", str(row.get("body") or "")):
                return fail("CURRENT_HEAD_INLINE_FINDING")
        # This is a read-only snapshot, not a lock on same-head comments.
        # No caller may infer atomic authorization to merge from this result.
        return {"status": "FINAL_TECHNICAL_REVIEW", "technical_review_accepted": True,
                "head": head, "review_requested_at": last.isoformat(),
                "not_formal_github_approved": True, "merge_authorized": False,
                "atomic_review_merge_binding": False}
    except (TypeError, ValueError, KeyError, json.JSONDecodeError):
        return fail("REVIEW_FINALITY_UNVERIFIED")


def gh_get(path):
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=45, check=False)
    if r.returncode:
        raise ValueError("GITHUB_API_UNAVAILABLE")
    return json.loads(r.stdout)


def paged(repo, path):
    rows = []
    for index in range(1, 11):
        batch = gh_get(f"repos/{repo}/{path}?per_page=100&page={index}")
        if not isinstance(batch, list) or any(not isinstance(x, dict) for x in batch):
            raise ValueError("INVALID_PAGE")
        rows.extend(batch)
        if len(batch) < 100:
            return rows
    raise ValueError("PAGINATION_NOT_EXHAUSTIVE")


def consistent_live_snapshot(repo: str, number: int, head: str) -> dict:
    """Double-read PR and all review events; any mutation during census blocks.

    This is a conservative read-only release preflight, not an atomic GitHub
    compare-and-swap for issue comments. The merger must run it immediately
    before a GitHub exact-head merge with no intermediate asynchronous work.
    """
    def read_once():
        pr = gh_get(f"repos/{repo}/pulls/{number}")
        if (pr.get("head", {}).get("sha") != head or pr.get("state") != "open"
                or pr.get("draft")):
            raise ValueError("PR_HEAD_OR_STATE_CHANGED")
        comments = paged(repo, f"issues/{number}/comments")
        reviews = paged(repo, f"pulls/{number}/reviews")
        inline = paged(repo, f"pulls/{number}/comments")
        return (pr.get("head", {}).get("sha"), pr.get("updated_at"),
                comments, reviews, inline)
    before = read_once()
    after = read_once()
    if before != after:
        raise ValueError("REVIEW_SNAPSHOT_CHANGED_DURING_CENSUS")
    return decision(head, after[2], after[3], after[4])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pr", type=int, required=True)
    ap.add_argument("--head", required=True)
    a = ap.parse_args()
    result = {"status": "REVIEW_FINALITY_UNVERIFIED", "technical_review_accepted": False}
    try:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", a.repo) or a.pr < 1:
            raise ValueError("BAD_PR_INPUT")
        result = consistent_live_snapshot(a.repo, a.pr, a.head)
    except (ValueError, TypeError, KeyError, subprocess.SubprocessError, json.JSONDecodeError):
        pass
    print(json.dumps(result, sort_keys=True))
    if not result.get("technical_review_accepted"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
