import hashlib
import importlib.util
import json
import pathlib
import unittest

spec = importlib.util.spec_from_file_location("ledger_screen", pathlib.Path(__file__).resolve().parents[2] / "research/s1_root_v2/ledger_screen.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def row(**kw):
    r = dict(seq=1,repo="example/repo",pr=1,head="a"*40,verdict="APPROVE",verdict_line_exact=True,receipt_comment=1,report_blob="b"*40,bridge_commit="c"*40,lane_eligible="NO")
    r.update(kw)
    return r

def run(rows, entries=None, minimum=1, head="a"*40):
    raw = b"".join(json.dumps(r).encode()+b"\n" for r in rows)
    s = dict(schema="CLAUDE_APPROVAL_CURRENT_v1",ledger_sha256=hashlib.sha256(raw).hexdigest(),ledger_last_seq=len(rows),entries=[rows[-1]] if entries is None else entries)
    return m.screen(json.dumps(s).encode(),raw,"example/repo",1,head,minimum)

class LedgerScreenTest(unittest.TestCase):
    def test_exact_is_not_authority(self):
        self.assertEqual(run([row()]),"EXACT_APPROVAL_ONLY")
    def test_stale_and_changed_head(self):
        self.assertEqual(run([row()],minimum=2),"UNKNOWN")
        self.assertEqual(run([row()],head="d"*40),"HOLD")
    def test_veto(self):
        for verdict in ("REQUEST_CHANGES","BLOCK","VETO"):
            rows=[row(),row(seq=2,verdict=verdict)]
            self.assertEqual(run(rows),"HOLD")
            self.assertEqual(run(rows,entries=[rows[0]]),"UNKNOWN")
    def test_missing_evidence(self):
        self.assertEqual(run([row(report_blob=None)]),"UNKNOWN")
        self.assertEqual(run([row()],entries=[]),"UNKNOWN")
        self.assertEqual(run([row(seq=2)]),"UNKNOWN")

    def test_boolean_pr(self):
        self.assertEqual(run([row(pr=True)]),"UNKNOWN")
        self.assertEqual(m.screen(b"{}",b"","example/repo",True,"a"*40,1),"UNKNOWN")
