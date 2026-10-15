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


def is_codex(row):
    user = row.get("user") or {}
    return isinstance(user, dict) and str(user.get("login", "")).casefold().startswith("chatgpt-codex-connector")


def decision(head, comments, reviews, inline):
    """Require positive exact-head completion AFTER the latest human request."""
    fail = lambda reason: {"status": reason, "technical_review_accepted": False}
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        return fail("INVALID_HEAD")
    try:
        requests = [stamp(row.get("created_at")) for row in comments
                    if not is_codex(row) and re.search(r"(?mi)^\s*@codex\s+review\b", str(row.get("body") or ""))]
        if not requests:
            return fail("REVIEW_NOT_REQUESTED")
        last = max(requests)
        completed = []
        positive = []
        for row in comments:
            if not is_codex(row):
                continue
            body = str(row.get("body") or "")
            when = stamp(row.get("updated_at") or row.get("created_at"))
            if when < last:
                continue
            m = re.search(r"<!-- codex-review-state:v1\s+(.+?)\s*-->", body, re.S)
            if m:
                state = json.loads(m.group(1)).get("code_review", {})
                if state.get("commit_sha") == head and state.get("status") == "completed":
                    completed.append(state)
            if "Codex Review: Didn't find any major issues" in body:
                m = re.search(r"Reviewed commit:\*\*\s*\x60([a-f0-9]{10,40})\x60", body)
                if m and head.startswith(m.group(1)):
                    positive.append(when)
        if not completed or not positive:
            return fail("REVIEW_IN_PROGRESS_OR_UNVERIFIED")
        if completed[-1].get("has_unresolved_findings") is not False:
            return fail("UNRESOLVED_CODEX_FINDINGS")
        last_positive = max(positive)
        for row in reviews:
            if (not is_codex(row) or row.get("commit_id") != head
                    or stamp(row.get("submitted_at")) < last):
                continue
            body = str(row.get("body") or "")
            if stamp(row.get("submitted_at")) > last_positive and re.search(r"\bP[012]\b|review suggestions", body, re.I):
                return fail("LATER_MATERIAL_REVIEW_FINDINGS")
        for row in inline:
            if not is_codex(row) or head not in (row.get("commit_id"), row.get("original_commit_id")):
                continue
            if stamp(row.get("created_at")) >= last and re.search(r"\bP[012]\b|codex-code-review-finding:v1", str(row.get("body") or "")):
                return fail("CURRENT_HEAD_INLINE_FINDING")
        return {"status": "FINAL_TECHNICAL_REVIEW", "technical_review_accepted": True,
                "head": head, "review_requested_at": last.isoformat(),
                "not_formal_github_approved": True}
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
        pr = gh_get(f"repos/{a.repo}/pulls/{a.pr}")
        if pr.get("head", {}).get("sha") != a.head or pr.get("state") != "open" or pr.get("draft"):
            raise ValueError("PR_HEAD_OR_STATUS_CHANGED")
        result = decision(a.head, paged(a.repo, f"issues/{a.pr}/comments"),
                          paged(a.repo, f"pulls/{a.pr}/reviews"),
                          paged(a.repo, f"pulls/{a.pr}/comments"))
    except (ValueError, TypeError, KeyError, subprocess.SubprocessError, json.JSONDecodeError):
        pass
    print(json.dumps(result, sort_keys=True))
    if not result.get("technical_review_accepted"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
