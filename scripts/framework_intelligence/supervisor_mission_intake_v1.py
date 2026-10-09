#!/usr/bin/env python3
"""Fail-closed owner-approved mission intake for existing Framework supervisor.

This is an evidence/claim gate, NOT Codex-ready authority or an autonomous merge.
"""
import argparse
import json
import sys

MARKER = "[SUPERVISOR_EXECUTE]"
ISSUE_ALLOWLIST = {1552}
STATES = {"ACTIONABLE_UNCLAIMED", "CLAIMED_ACTIVE", "REVIEW_WAIT", "POST_FIX_WAIT",
          "NATURAL_WAIT", "RESOURCE_GATED", "AUTHORITY_GATED", "VERIFIED_COMPLETE"}

def classify(event, allowed=ISSUE_ALLOWLIST):
    issue = event.get("issue") or {}
    comment = event.get("comment") or {}
    if not isinstance(issue, dict) or not isinstance(comment, dict):
        return "IGNORED", "malformed_event"
    if issue.get("number") not in allowed or "pull_request" in issue:
        return "IGNORED", "not_approved_queue_issue"
    if issue.get("state") != "open":
        return "IGNORED", "issue_not_open"
    if comment.get("author_association") != "OWNER":
        return "IGNORED", "not_owner"
    body = comment.get("body")
    if not isinstance(body, str) or not (body == MARKER or body.startswith(MARKER + "\n")):
        return "IGNORED", "no_first_line_marker"
    if not isinstance(comment.get("id"), int):
        return "IGNORED", "missing_comment_id"
    return "ACTIONABLE_UNCLAIMED", "owner_marker_triage_only_not_human_authentication"

def receipt(event, repository, head_sha):
    state, reason = classify(event)
    issue = event.get("issue") or {}
    comment = event.get("comment") or {}
    return {
        "contract": "SUPERVISOR_MISSION_INTAKE_v1",
        "state": state, "reason": reason,
        "repository": repository,
        "issue_number": issue.get("number"),
        "comment_id": comment.get("id"),
        "workflow_event_sha": head_sha,
        "code_ref": "main",
        "human_approval_verified": False,
        "claim_key": f"{repository}#{issue.get('number')}:{comment.get('id')}",
        "execution_started": False,
        "codex_ready": False,
        "authority": "TRIAGE_ONLY",
        "next_gate": "fresh cockpit, dedupe, governed CODEX_RESEARCH_CANDIDATE intake and independent review",
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--event", required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--head-sha", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    with open(a.event, encoding="utf-8") as f:
        event = json.load(f)
    result = receipt(event, a.repo, a.head_sha)
    with open(a.output, "w", encoding="utf-8") as f:
        json.dump(result, f, sort_keys=True, indent=2)
        f.write("\n")
    print(f"SUPERVISOR_INTAKE={result['state']} reason={result['reason']} issue={result['issue_number']}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
