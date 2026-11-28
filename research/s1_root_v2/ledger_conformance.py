"""Conformance vectors for any runtime consumer of CLAUDE_APPROVAL_CURRENT_v1 + APPROVALS.jsonl.

Each vector: (name, snapshot_bytes, ledger_bytes, repo, pr, head, minimum_seq, expected) where
expected is ADMIT (exact-head approval proven), HOLD (well-formed evidence that does not approve
this head) or UNKNOWN (integrity or type failure). A consumer passes when ADMIT is returned for
exactly the ADMIT vectors; HOLD vs UNKNOWN is checked as strict class too (both fail closed).
Synthetic data only; never production or historical evidence.
"""
import hashlib, json

REPO = "Donh91/Investering-Framework-Archive-v1"
H1, H2 = "a" * 40, "b" * 40
BLOB, BC = "c" * 40, "d" * 40
VIEW_KEYS = ("seq", "repo", "pr", "head", "verdict", "verdict_line_exact",
             "lane_eligible", "receipt_comment", "report_blob", "bridge_commit")

def row(seq, pr=7, head=H1, verdict="APPROVE", exact=True, repo=REPO, receipt=1000, **kw):
    r = {"schema": "CLAUDE_APPROVAL_LEDGER_v1", "seq": seq, "ts": "2026-11-24T00:00:%02dZ" % seq,
         "repo": repo, "pr": pr, "head": head, "verdict": verdict, "verdict_line_exact": exact,
         "lane_eligible": "YES", "receipt_comment": receipt + seq, "report_blob": BLOB,
         "bridge_commit": BC, "source": "SYNTHETIC"}
    r.update(kw)
    return r

def enc_ledger(rows):
    return b"".join(json.dumps(r, sort_keys=True).encode() + b"\n" for r in rows)

def view(rows, ledger_bytes, entries=None, **over):
    newest = {}
    for r in rows:
        newest[(r["repo"], r["pr"])] = r
    if entries is None:
        entries = [{k: r.get(k) for k in VIEW_KEYS} for r in newest.values()]
    v = {"schema": "CLAUDE_APPROVAL_CURRENT_v1", "ledger_path": "reports/claude/APPROVALS.jsonl",
         "ledger_sha256": hashlib.sha256(ledger_bytes).hexdigest(), "ledger_last_seq": len(rows),
         "rule": "synthetic", "open_pr_filter": False, "entries": entries}
    v.update(over)
    return json.dumps(v, sort_keys=True).encode()

def vectors():
    out = []
    def add(name, rows, expected, head=H1, pr=7, minimum=1, ledger=None, snap=None, repo=REPO):
        lb = enc_ledger(rows) if ledger is None else ledger
        sb = view(rows, lb) if snap is None else snap(rows, lb)
        out.append((name, sb, lb, repo, pr, head, minimum, expected))
    base = [row(1, pr=5), row(2)]
    add("approve_exact_head", base, "ADMIT")
    add("approve_other_head", base, "HOLD", head=H2)
    add("newer_request_changes", base + [row(3, verdict="REQUEST_CHANGES")], "HOLD")
    add("newer_block_other_head", base + [row(3, head=H2, verdict="BLOCK")], "HOLD")
    add("newer_veto_no_head", base + [row(3, head=None, verdict="VETO")], "HOLD")
    add("verdict_not_literal", [row(1, exact=False)], "HOLD")
    add("approve_newer_than_block", [row(1, verdict="BLOCK"), row(2)], "ADMIT")
    add("no_entry_for_pr", base, "UNKNOWN", pr=9)
    add("other_repo_same_pr_ignored", [row(1, repo="Donh91/Meme-Alpha-Lab", verdict="BLOCK"), row(2)], "ADMIT")
    add("stale_snapshot_rollback", base, "UNKNOWN", minimum=3)
    add("ledger_sha_mismatch", base, "UNKNOWN", snap=lambda r, lb: view(r, lb + b" "))
    add("seq_gap", [row(1, pr=5), row(3)], "UNKNOWN",
        snap=lambda r, lb: view(r, lb, ledger_last_seq=2))
    add("view_entry_not_newest", base + [row(3, verdict="BLOCK")], "UNKNOWN",
        snap=lambda r, lb: view(r, lb, entries=[{k: r[1].get(k) for k in VIEW_KEYS}]))
    add("view_duplicate_entries", base, "UNKNOWN",
        snap=lambda r, lb: view(r, lb, entries=[{k: r[1].get(k) for k in VIEW_KEYS}] * 2))
    add("view_duplicate_json_key", base, "UNKNOWN",
        snap=lambda r, lb: view(r, lb).replace(b'{"entries"', b'{"schema":"X","entries"', 1))
    add("wrong_schema", base, "UNKNOWN",
        snap=lambda r, lb: view(r, lb, schema="CLAUDE_APPROVAL_CURRENT_v0"))
    add("pr_bool_type_confusion", [row(1, pr=1)], "UNKNOWN", pr=True)
    add("head_uppercase", [row(1, head="A" * 40)], "UNKNOWN", head="A" * 40)
    add("receipt_missing", [row(1, receipt_comment=None)], "UNKNOWN")
    add("bridge_commit_short", [row(1, bridge_commit="d" * 8)], "UNKNOWN")
    add("nan_in_ledger", base, "UNKNOWN",
        ledger=enc_ledger(base).replace(b'"lane_eligible": "YES"', b'"lane_eligible": NaN', 1))
    add("blank_line_in_ledger", base, "UNKNOWN", ledger=enc_ledger(base[:1]) + b"\n" + enc_ledger(base[1:]))
    add("minimum_seq_zero", base, "UNKNOWN", minimum=0)
    add("snapshot_not_bytes", base, "UNKNOWN", snap=lambda r, lb: view(r, lb).decode())
    return out

def run(screen, mapping):
    """screen(snapshot, ledger, repo, pr, head, minimum_seq) -> label; mapping: label -> class."""
    fails = []
    for name, sb, lb, repo, pr, head, minimum, expected in vectors():
        try:
            got = mapping.get(screen(sb, lb, repo, pr, head, minimum), "INVALID_LABEL")
        except Exception as e:  # a consumer must never raise
            got = "RAISED:" + type(e).__name__
        if got != expected:
            fails.append((name, expected, got))
    return fails
