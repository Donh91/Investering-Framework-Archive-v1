"""Research-only ledger screening. Never substitutes for native review/veto checks."""
import hashlib
import json
import re

OID = re.compile(r"[0-9a-f]{40}")
def unique(pairs):
    result = {}
    for k,v in pairs:
        if k in result:
            raise ValueError("duplicate")
        result[k] = v
    return result

def screen(snapshot, ledger, repo, pr, head, minimum_seq):
    try:
        if type(pr) is not int or pr <= 0:
            return "UNKNOWN"
        if type(snapshot) is not bytes or type(ledger) is not bytes:
            return "UNKNOWN"
        s = json.loads(snapshot, object_pairs_hook=unique)
        if s["schema"] != "CLAUDE_APPROVAL_CURRENT_v1" or s["ledger_sha256"] != hashlib.sha256(ledger).hexdigest():
            return "UNKNOWN"
        if type(minimum_seq) is not int or minimum_seq < 1 or type(s["ledger_last_seq"]) is not int:
            return "UNKNOWN"
        rows = [json.loads(line, object_pairs_hook=unique) for line in ledger.splitlines()]
        if not rows or any(type(r["seq"]) is not int or r["seq"] != i for i,r in enumerate(rows,1)):
            return "UNKNOWN"
        if len(rows) != s["ledger_last_seq"] or len(rows) < minimum_seq:
            return "UNKNOWN"
        matches = [r for r in rows if r["repo"] == repo and type(r["pr"]) is int and r["pr"] == pr]
        current = [r for r in s["entries"] if r["repo"] == repo and type(r["pr"]) is int and r["pr"] == pr]
        if not matches or len(current) != 1:
            return "UNKNOWN"
        r = matches[-1]
        keys = ("seq","repo","pr","head","verdict","verdict_line_exact","receipt_comment","report_blob","bridge_commit","lane_eligible")
        if any(k not in r or k not in current[0] or r[k] != current[0][k] for k in keys):
            return "UNKNOWN"
        if r["verdict"] != "APPROVE" or r["head"] != head or r["verdict_line_exact"] is not True:
            return "HOLD"
        if not all(isinstance(r[k],str) and OID.fullmatch(r[k]) for k in ("head","report_blob","bridge_commit")) or type(r["receipt_comment"]) is not int or r["receipt_comment"] <= 0:
            return "UNKNOWN"
        return "EXACT_APPROVAL_ONLY"
    except (ValueError,TypeError,KeyError,AttributeError,RecursionError):
        return "UNKNOWN"
