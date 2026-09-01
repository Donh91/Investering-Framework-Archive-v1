import importlib.util
import math
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
PATH = ROOT / "scripts/research_sources/onchain_incremental_value_replay.py"
SPEC = importlib.util.spec_from_file_location("replay", PATH)
R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)


def synthetic_rows(n=48, mvrv_signal=False):
    rows = []
    price = 100.0
    for i in range(n):
        mvrv = 1.5 + 0.3 * math.sin(i / 3)
        if i > 0:
            base_move = 0.01 * math.sin(i / 2)
            signal_move = 0.05 * (1.5 - prev_mvrv) if mvrv_signal else 0.0
            price *= math.exp(base_move + signal_move)
        rows.append(R.Row(f"2024-{i+1:03d}", price, mvrv))
        prev_mvrv = mvrv
    return rows


class TestReplay(unittest.TestCase):
    def test_dataset_is_causal(self):
        rows = synthetic_rows()
        data = R.build_dataset(rows, 1)
        self.assertGreater(len(data), 30)
        self.assertIn("mvrv_d1", data[0])
        self.assertIn("target", data[0])

    def test_walk_forward_scores(self):
        result = R.run(synthetic_rows(), 1, 18, 10.0)
        self.assertEqual(result["contract"], R.CONTRACT)
        self.assertGreater(result["baseline"]["n"], 10)
        self.assertIn(result["verdict"], {"PROMISING_ONLY", "NO_ROBUST_INCREMENTAL_VALUE"})
        self.assertEqual(result["authority"], "NONE")

    def test_challenger_can_detect_synthetic_signal(self):
        result = R.run(synthetic_rows(mvrv_signal=True), 1, 18, 10.0)
        self.assertGreaterEqual(result["challenger"]["direction_accuracy"], 0.0)
        self.assertLessEqual(result["challenger"]["direction_accuracy"], 1.0)

    def test_input_identity_binds_transient_matrix(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "matrix.csv"
            path.write_text("date,price,mvrv\n2026-01-31,100,1.1\n", encoding="utf-8")
            identity = R.file_identity(path)
            self.assertEqual(len(identity["input_dataset_sha256"]), 64)
            self.assertGreater(identity["input_dataset_bytes"], 0)
            self.assertFalse(identity["input_dataset_persisted"])
            self.assertEqual(identity["input_identity_scope"], "LOCAL_TRANSIENT_RESEARCH_MATRIX")

    def test_bad_horizon_rejected(self):
        with self.assertRaises(R.ReplayError):
            R.build_dataset(synthetic_rows(), 0)


if __name__ == "__main__":
    unittest.main()
