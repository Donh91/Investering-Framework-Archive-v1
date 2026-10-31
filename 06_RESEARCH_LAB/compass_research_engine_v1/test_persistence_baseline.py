import unittest

from persistence_baseline import compare_pairs, sign


def row(cluster, forecast, actual, mom, pit=True, mature=True):
    return {"cluster_id": cluster, "forecast_direction": forecast,
            "actual_direction": actual, "known_momentum_pct": mom,
            "pit_verified": pit, "matured": mature}


class BaselineTests(unittest.TestCase):
    def test_persistence_tie_not_edge(self):
        r = compare_pairs([row("a", "UP", "UP", .3), row("b", "DOWN", "UP", -.4)])
        self.assertEqual(r["forecast_correct"], 1)
        self.assertEqual(r["baseline_correct"], 1)
        self.assertIsNone(r["incremental_edge_certified"])

    def test_discordance_matched(self):
        r = compare_pairs([row("a", "UP", "UP", -.3), row("b", "DOWN", "UP", .4)])
        self.assertEqual((r["forecast_only_correct"], r["baseline_only_correct"]), (1, 1))

    def test_no_pit_or_pending_not_scored(self):
        r = compare_pairs([row("a", "UP", "UP", .3, pit=False), row("b", "UP", "UP", .4, mature=False)])
        self.assertEqual(r["n_independent_clusters"], 0)
        self.assertEqual(r["excluded_unverified"], 1)
        self.assertEqual(r["excluded_unmatured"], 1)

    def test_duplicate_cluster_fails(self):
        with self.assertRaisesRegex(ValueError, "UNIQUE_CLUSTER"):
            compare_pairs([row("a", "UP", "UP", .3), row("a", "UP", "UP", .3)])

    def test_unverified_then_later_duplicate_fails(self):
        with self.assertRaisesRegex(ValueError, "UNIQUE_CLUSTER"):
            compare_pairs([row("a", "UP", "UP", .3, pit=False), row("a", "UP", "UP", .3)])

    def test_abstentions_not_silent_success(self):
        r = compare_pairs([row("a", "SIDEWAYS", "UP", .3), row("b", "UP", "SIDEWAYS", .3)])
        self.assertEqual(r["n_independent_clusters"], 0)
        self.assertEqual(r["excluded_abstained"], 2)

    def test_no_valid_values(self):
        for x in (None, True, "1", float("nan"), float("inf")):
            with self.subTest(x=x), self.assertRaises(ValueError):
                sign(x)


if __name__ == "__main__":
    unittest.main()
