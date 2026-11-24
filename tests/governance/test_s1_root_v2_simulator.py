import importlib.util
import pathlib
import sys
import unittest

P = pathlib.Path(__file__).resolve().parents[2] / "research/s1_root_v2/simulator.py"
S = importlib.util.spec_from_file_location("s1_root_v2_simulator", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)

class SimulatorTest(unittest.TestCase):
    def test_positive(self):
        self.assertEqual(M.decide(dict.fromkeys(M.GATES, True)).decision, M.Decision.SIMULATE_MERGE)
    def test_gate_mutants(self):
        for gate in M.GATES:
            for value in (False, None, 1, "true", [], {}):
                with self.subTest(gate=gate, value=value):
                    e = dict.fromkeys(M.GATES, True)
                    e[gate] = value
                    self.assertNotEqual(M.decide(e).decision, M.Decision.SIMULATE_MERGE)
            e = dict.fromkeys(M.GATES, True)
            del e[gate]
            self.assertNotEqual(M.decide(e).decision, M.Decision.SIMULATE_MERGE)
    def test_open_intent_and_clock(self):
        e = dict.fromkeys(M.GATES, True)
        e["intent_clear"] = False
        self.assertEqual(M.decide(e).decision, M.Decision.RECONCILE_ONLY)
        e["clock_writable"] = False
        self.assertEqual(M.decide(e).decision, M.Decision.NOOP)
    def test_recovery(self):
        e = dict.fromkeys(("native_read_verified", "merged", "intent_binding",
            "single_parent", "subject_bound", "main_ancestry", "changed_blobs_equal", "no_bypass"), True)
        self.assertEqual(M.reconcile(e).decision, M.Decision.VERIFIED)
        for gate in ("single_parent", "subject_bound", "main_ancestry", "changed_blobs_equal", "no_bypass"):
            self.assertEqual(M.reconcile(dict(e, **{gate: False})).decision, M.Decision.HALT)
            self.assertEqual(M.reconcile(dict(e, **{gate: None})).decision, M.Decision.RECONCILE_ONLY)
        self.assertEqual(M.reconcile(dict(e, merged=False)).decision, M.Decision.ABSENT)
        self.assertEqual(M.reconcile(dict(e, intent_binding=False)).decision, M.Decision.FOREIGN)
        self.assertEqual(M.reconcile({}).decision, M.Decision.RECONCILE_ONLY)
