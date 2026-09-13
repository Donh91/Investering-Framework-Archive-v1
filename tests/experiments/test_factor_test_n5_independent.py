import hashlib
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).parents[2]
SCRIPT = REPO / "scripts" / "experiments" / "factor_test_n5_independent.py"
RESULT = REPO / "04_RESEARCH_LAB" / "auto_trading" / "experiments" / "E3_TRIAL_N5_INDEPENDENT_RESULT.json"
SPEC = importlib.util.spec_from_file_location("factor_test_n5", SCRIPT)
n5 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(n5)


class FactorTestN5IndependentTests(unittest.TestCase):
    def test_window_transform_is_causal_and_deterministic(self):
        base = [1.0, 2.0, 3.0, 4.0, 5.0]
        first = n5.window_transform(base)
        extended = n5.window_transform(base + [999.0])
        self.assertEqual(first["RAW"], 5.0)
        self.assertEqual(first["ROLLING_PERCENTILE"], 1.0)
        self.assertGreater(first["ZSCORE"], 0.0)
        self.assertEqual(first["DISTANCE_FROM_EXTREMA"], 1.0)
        self.assertNotEqual(first, extended)

    def test_conflicting_duplicate_event_timestamp_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            day = root / "2026/08/20"
            day.mkdir(parents=True)
            base = {
                "contract": "DAILY_LIVE_ANCHOR_INDEX_v3",
                "captured_at_utc": "2026-08-20T02:00:00Z",
                "market_metrics": {"sentiment": {"cfgi": {
                    "timeframe": "4h",
                    "symbols": {
                        "BTC": {"owner_status": "PASS", "stale": False, "score": 50, "price": 100, "timestamp": "2026-08-20T01:49:16Z"},
                        "ETH": {"owner_status": "PASS", "stale": False, "score": 55, "price": 10, "timestamp": "2026-08-20T01:49:16Z"},
                    },
                }}},
            }
            (day / "a.json").write_text(json.dumps(base))
            changed = json.loads(json.dumps(base))
            changed["captured_at_utc"] = "2026-08-20T02:10:00Z"
            changed["market_metrics"]["sentiment"]["cfgi"]["symbols"]["BTC"]["score"] = 51
            (day / "b.json").write_text(json.dumps(changed))
            with self.assertRaisesRegex(n5.N5IntegrityError, "CONFLICTING_DUPLICATE_EVENT_TIMESTAMP"):
                n5.extract_rows(root)

    def test_build_examples_uses_time_window_and_future_label_only(self):
        start = datetime(2026, 8, 20, tzinfo=timezone.utc)
        rows = []
        for symbol, price0 in (("BTC", 100.0), ("ETH", 10.0)):
            for i in range(30):
                dt = start + timedelta(hours=4 * i)
                rows.append({
                    "symbol": symbol,
                    "event_dt": dt,
                    "event_timestamp": n5.iso(dt),
                    "capture_dt": dt + timedelta(minutes=2),
                    "capture_timestamp": n5.iso(dt + timedelta(minutes=2)),
                    "score": float(40 + (i % 12)),
                    "price": price0 * (1.0 + 0.002 * i),
                    "source_path": f"{symbol}-{i}.json",
                })
        rows.sort(key=lambda r: (r["symbol"], r["event_dt"]))
        examples = n5.build_examples(rows)
        self.assertTrue(examples)
        for row in examples:
            self.assertGreater(row["outcome_dt"], row["event_dt"])
            self.assertGreaterEqual(row["window_observations"], n5.MIN_WINDOW_OBSERVATIONS)
            self.assertGreaterEqual(row["window_span_hours"], n5.MIN_WINDOW_SPAN_HOURS)

    def test_purged_split_prevents_training_outcome_overlap(self):
        start = datetime(2026, 8, 20, tzinfo=timezone.utc)
        examples = []
        for symbol in ("BTC", "ETH"):
            for i in range(60):
                event = start + timedelta(hours=4 * i)
                examples.append({
                    "symbol": symbol,
                    "event_dt": event,
                    "outcome_dt": event + timedelta(hours=24),
                    "features": {name: float(i) for name in n5.TRANSFORMS},
                    "future_return": 0.001 * i,
                })
        train, oos, boundaries = n5.split_purged(examples)
        self.assertTrue(train)
        self.assertTrue(oos)
        for symbol in ("BTC", "ETH"):
            boundary = n5.parse_ts(boundaries[symbol])
            for row in [r for r in train if r["symbol"] == symbol]:
                self.assertLessEqual(row["outcome_dt"], boundary - timedelta(hours=n5.PURGE_HOURS))

    def test_corrected_gate_rejects_less_negative_but_still_negative(self):
        metrics = {}
        for name in n5.TRANSFORMS:
            raw = name == "RAW"
            ic = -0.5 if raw else -0.1
            metrics[name] = {
                "oos_combined": {"spearman_ic": ic, "top_bottom_quartile_spread_pct": -1.0},
                "oos_by_symbol": {
                    "BTC": {"spearman_ic": ic, "top_bottom_quartile_spread_pct": -1.0},
                    "ETH": {"spearman_ic": ic, "top_bottom_quartile_spread_pct": -1.0},
                },
            }
        eligible, checks = n5.adjudicate(metrics)
        self.assertEqual(eligible, [])
        self.assertFalse(checks["ROLLING_PERCENTILE"]["passed"])

    def test_committed_n5_registration_is_monotonic_and_research_only(self):
        candidate = json.loads((REPO / "research/experiment_lifecycle/candidates/2026/09/EC-8f8d7b3dcb494aa2298f.json").read_text())
        admission = json.loads((REPO / "research/experiment_lifecycle/admission/2026/09/EC-8f8d7b3dcb494aa2298f.json").read_text())
        blocked = json.loads((REPO / "04_RESEARCH_LAB/auto_trading/experiments/E3_TRIAL_N4_SOURCE_BINDING_BLOCKED.json").read_text())
        prereg = json.loads((REPO / "04_RESEARCH_LAB/auto_trading/experiments/E3_TRIAL_N5_PREREGISTRATION.json").read_text())
        self.assertEqual(candidate["spec"]["factor_design"]["proposal_trial_n"], 5)
        self.assertEqual(admission["status"], "QUALIFIED_FOR_FORWARD_TEST")
        self.assertEqual(blocked["trial_accounting"]["proposal_trial_n"], 4)
        self.assertFalse(blocked["trial_accounting"]["outcome_inspected"])
        self.assertEqual(prereg["proposal_trial_n"], 5)
        self.assertEqual(prereg["status"], "PREREGISTERED_BEFORE_OUTCOME_REPLAY")
        self.assertEqual(hashlib.sha256(SCRIPT.read_bytes()).hexdigest(), prereg["method"]["code_sha256_before_outcome_replay"])
        self.assertFalse(admission["authority"]["portfolio_execution"])

    def test_n5_repository_replay_is_deterministic_and_research_only(self):
        first = n5.evaluate(REPO)
        second = n5.evaluate(REPO)
        encoded = n5.canonical(first)
        self.assertEqual(encoded, n5.canonical(second))
        self.assertEqual(encoded, RESULT.read_bytes())
        self.assertEqual(first["trial_accounting"]["proposal_trial_n"], 5)
        self.assertEqual(first["adjudication"]["status"], "INDEPENDENT_NOT_SUPPORTED")
        self.assertEqual(first["adjudication"]["eligible_normalized_transforms"], [])
        self.assertFalse(first["authority"]["portfolio_execution"])
        self.assertFalse(first["authority"]["automatic_promotion"])
        print("N5_AGGREGATE_RESULT=" + encoded.decode().strip())


if __name__ == "__main__":
    unittest.main()
