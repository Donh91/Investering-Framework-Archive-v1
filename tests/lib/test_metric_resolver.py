"""UNIT tests for the canonical metric-path resolver (TASK3 R3-15, UNIT family)."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "lib" / "metric_resolver.py"
spec = importlib.util.spec_from_file_location("metric_resolver", MODULE_PATH)
mr = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mr)


def capture(**market_metrics):
    return {"captured_at_utc": "2026-08-16T13:47:45Z", "run_id": "gh-1", "market_metrics": dict(market_metrics)}


DOC = capture(
    derivatives={"BTC-USDT-SWAP": {"mark_price": {"mark_price": 63034.6}}},
    breadth={"advancers": 51, "decliners": 28},
    spot_legacy={},
    sentiment={"cfgi": {"symbols": {"BTC": {"score": 57.5}}}},
)


class ResolverUnitTests(unittest.TestCase):
    # U1
    def test_document_rooted_path_resolves_exact_value(self):
        r = mr.resolve(DOC, "market_metrics.derivatives.BTC-USDT-SWAP.mark_price.mark_price", mr.CAPTURE_DOCUMENT_ROOT)
        self.assertTrue(r.ok)
        self.assertEqual(r.value, 63034.6)
        self.assertEqual(r.root_contract, mr.CAPTURE_DOCUMENT_ROOT)

    # U2
    def test_document_rooted_path_does_not_resolve_under_market_metrics_root(self):
        r = mr.resolve(DOC, "market_metrics.derivatives.BTC-USDT-SWAP.mark_price.mark_price", mr.MARKET_METRICS_ROOT)
        self.assertFalse(r.ok)
        self.assertIsNone(r.value)

    # U3
    def test_market_metrics_relative_path_resolves_under_legacy_root(self):
        r = mr.resolve(DOC, "derivatives.BTC-USDT-SWAP.mark_price.mark_price", mr.MARKET_METRICS_ROOT)
        self.assertTrue(r.ok)
        self.assertEqual(r.value, 63034.6)

    # U4
    def test_missing_leaf_is_metric_unavailable(self):
        r = mr.resolve(DOC, "breadth.does_not_exist", mr.MARKET_METRICS_ROOT)
        self.assertEqual(r.status, mr.METRIC_UNAVAILABLE)
        self.assertIsNone(r.value)

    # U5
    def test_non_numeric_leaf_is_never_coerced(self):
        doc = capture(meta={"label": "sixty", "flag": True, "rows": [1, 2], "nested": {"a": 1}})
        for path in ("meta.label", "meta.flag", "meta.rows", "meta.nested"):
            with self.subTest(path=path):
                r = mr.resolve(doc, path, mr.MARKET_METRICS_ROOT)
                self.assertEqual(r.status, mr.METRIC_UNAVAILABLE)
                self.assertIsNone(r.value)

    # U6
    def test_malformed_paths_return_metric_unavailable_without_raising(self):
        for path in ("", ".", "a..b", "a.", ".b", "a;b", None, 7):
            with self.subTest(path=path):
                r = mr.resolve(DOC, path, mr.MARKET_METRICS_ROOT)
                self.assertEqual(r.status, mr.METRIC_UNAVAILABLE)

    # U7
    def test_path_traversing_a_non_dict_returns_metric_unavailable(self):
        r = mr.resolve(DOC, "derivatives.BTC-USDT-SWAP.mark_price.mark_price.deeper", mr.MARKET_METRICS_ROOT)
        self.assertEqual(r.status, mr.METRIC_UNAVAILABLE)

    # U8
    def test_ambiguous_path_is_refused_not_chosen(self):
        # Synthetic document where the same path resolves numerically under BOTH
        # roots. The real corpus contains zero such cases; the resolver must still
        # refuse rather than pick one.
        doc = {"captured_at_utc": "2026-08-16T13:47:45Z", "twin": {"x": 1.0}, "market_metrics": {"twin": {"x": 2.0}}}
        forecast = {"metric_path": "twin.x", "source_candidate_id": "EC-1"}
        r = mr.resolve_for_forecast(doc, forecast)
        self.assertEqual(r.status, mr.METRIC_PATH_ROOT_AMBIGUOUS)
        self.assertIsNone(r.value)

    def test_unknown_root_contract_is_rejected(self):
        with self.assertRaises(mr.UnknownRootContract):
            mr.resolve(DOC, "breadth.decliners", "SOME_OTHER_ROOT")
        with self.assertRaises(mr.UnknownRootContract):
            mr.declared_root_contract({"metric_path_root": "SOME_OTHER_ROOT"})

    def test_vanished_namespace_is_distinguished_from_a_wrong_lookup(self):
        # market_metrics.spot was renamed to spot_legacy and emptied on 2026-08-08.
        r = mr.resolve(DOC, "spot.BTCUSDT.close", mr.MARKET_METRICS_ROOT)
        self.assertEqual(r.status, mr.EVIDENCE_NAMESPACE_UNAVAILABLE)
        # An emptied placeholder namespace reports the same way.
        r2 = mr.resolve(DOC, "spot_legacy.BTCUSDT.close", mr.MARKET_METRICS_ROOT)
        self.assertEqual(r2.status, mr.EVIDENCE_NAMESPACE_UNAVAILABLE)

    def test_declared_root_is_authoritative_and_never_second_guessed(self):
        forecast = {"metric_path": "market_metrics.breadth.decliners", "metric_path_root": mr.CAPTURE_DOCUMENT_ROOT}
        r = mr.resolve_for_forecast(DOC, forecast)
        self.assertTrue(r.ok)
        self.assertEqual(r.value, 28)
        self.assertEqual(r.root_contract, mr.CAPTURE_DOCUMENT_ROOT)

    def test_producer_attribution_for_undeclared_forecasts(self):
        # experiment_lifecycle.py writes source_candidate_id and stored
        # market-metrics-relative paths.
        self.assertEqual(mr.legacy_root_contract({"source_candidate_id": "EC-1"}), mr.MARKET_METRICS_ROOT)
        # ratify_forecast_candidate.py writes candidate_id and resolves against the
        # baseline evidence document root.
        self.assertEqual(mr.legacy_root_contract({"candidate_id": "c1"}), mr.CAPTURE_DOCUMENT_ROOT)
        # Neither -> not attributable, must not be guessed.
        self.assertIsNone(mr.legacy_root_contract({}))

    def test_unattributable_undeclared_forecast_fails_closed(self):
        r = mr.resolve_for_forecast(DOC, {"metric_path": "derivatives.BTC-USDT-SWAP.mark_price.mark_price"})
        self.assertEqual(r.status, mr.METRIC_PATH_ROOT_UNDECLARED)
        self.assertIsNone(r.value)

    def test_resolver_never_falls_back_to_the_other_root(self):
        # A market-metrics-relative path on a forecast that declares the document
        # root must NOT quietly resolve under the legacy root.
        forecast = {"metric_path": "breadth.decliners", "metric_path_root": mr.CAPTURE_DOCUMENT_ROOT}
        r = mr.resolve_for_forecast(DOC, forecast)
        self.assertFalse(r.ok)
        self.assertEqual(r.status, mr.EVIDENCE_NAMESPACE_UNAVAILABLE)

    def test_canonical_path_is_idempotent_and_only_prefixes(self):
        self.assertEqual(mr.canonical_path("derivatives.BTC-USDT-SWAP.mark_price.mark_price"),
                         "market_metrics.derivatives.BTC-USDT-SWAP.mark_price.mark_price")
        self.assertEqual(mr.canonical_path("market_metrics.breadth.decliners"), "market_metrics.breadth.decliners")
        self.assertEqual(mr.canonical_path(""), "")

    def test_canonical_path_round_trips_through_the_resolver(self):
        # The invariant: a path canonicalised at freeze resolves the same metric at
        # maturity, through the same resolver.
        relative = "derivatives.BTC-USDT-SWAP.mark_price.mark_price"
        at_freeze = mr.resolve(DOC, relative, mr.MARKET_METRICS_ROOT)
        at_maturity = mr.resolve(DOC, mr.canonical_path(relative), mr.CAPTURE_DOCUMENT_ROOT)
        self.assertTrue(at_freeze.ok and at_maturity.ok)
        self.assertEqual(at_freeze.value, at_maturity.value)

    def test_resolver_performs_no_io(self):
        source = MODULE_PATH.read_text()
        for forbidden in ("open(", "Path(", "requests", "urllib", "subprocess", "os.environ"):
            self.assertNotIn(forbidden, source, f"resolver must perform no I/O: found {forbidden}")

    def test_root_contract_set_is_closed(self):
        self.assertEqual(set(mr.ROOT_CONTRACTS), {"CAPTURE_DOCUMENT_ROOT", "MARKET_METRICS_ROOT"})
        self.assertEqual(mr.RESOLVER_VERSION, "METRIC_PATH_RESOLVER_v1")


if __name__ == "__main__":
    unittest.main()
