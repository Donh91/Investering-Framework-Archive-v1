import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2] / "scripts" / "research"))
import compounding_learning_v1_core as core


def spec(target="derivatives.BTC-USDT-SWAP.mark_price.mark_price", **kw):
    return dict({"target_metric_path":target, "target_direction":"RANGE", "kind":"FORECAST_TEST",
                 "target_unit_contract_version":"FORECAST_TARGET_UNITS_v2",
                 "novelty_reason":"DAILY_DIRECTOR_FORECAST", "components":[]}, **kw)


class CoarseFamilyTest(unittest.TestCase):
    def test_aliases_and_distinct_assets(self):
        keys = {core.coarse_family_key(spec(p)) for p in core.TARGET_ALIAS_MAP if "BTC" in p}
        self.assertEqual(len(keys), 1)
        self.assertNotIn(core.coarse_family_key(spec("derivatives.ETH-USDT-SWAP.mark_price.mark_price")), keys)
        self.assertNotIn(core.coarse_family_key(spec("spot.BTCUSDT.close")), keys)
        self.assertNotIn(core.coarse_family_key(spec("derivatives.BTC-USDT-SWAP.index_price")), keys)

    def test_bounds_and_horizon_are_coverage_not_equivalence(self):
        self.assertEqual(core.coarse_family_key(spec(horizon_days=3,target_range_lower_pct=-2)),
                         core.coarse_family_key(spec(horizon_days=7,target_range_lower_pct=-8)))
        for changes in ({"target_direction":"UP"},{"target_unit_contract_version":"legacy"},
                        {"novelty_reason":"OTHER"},{"components":[{"metric_path":"breadth.advancers"}]}):
            self.assertNotEqual(core.coarse_family_key(spec()), core.coarse_family_key(spec(**changes)))

    def test_unknown_is_not_family(self):
        self.assertIsNone(core.coarse_family_key({}))
        self.assertIsNone(core.coarse_family_key(spec(components=[{}])))
        self.assertIsNone(core.coarse_family_key(spec(novelty_reason="ROUND_3")))
        self.assertIsNone(core.coarse_family_key(spec(target_mode="ABSOLUTE_VALUE")))

    def test_coverage_no_pooling_or_admission(self):
        reg={"candidates":[{"candidate_id":"a","kind":"FORECAST_TEST","forecast_ids":["f"]},
                           {"candidate_id":"b","kind":"FORECAST_TEST","forecast_ids":[]},
                           {"candidate_id":"c","kind":"FORECAST_TEST","forecast_ids":["g"]}]}
        adm={"candidates":[{"candidate_id":"a","semantic_fingerprint":"x","status":"QUALIFIED_FOR_FORWARD_TEST"},
                           {"candidate_id":"b","semantic_fingerprint":"y","status":"QUALIFIED_FOR_FORWARD_TEST"},
                           {"candidate_id":"c","semantic_fingerprint":"z","status":"SEMANTIC_DUPLICATE_KEEP_SHADOW"}]}
        out=core.coarse_family_coverage(reg,adm,{k:spec() for k in "abc"})
        self.assertEqual(len(out["families"]),1)
        self.assertEqual(out["families"][0]["semantic_fingerprints"],["x","y","z"])
        self.assertEqual(out["families"][0]["served_candidate_ids"],["a"])
        self.assertFalse(out["allocation_authorized"])
        self.assertFalse(out["scientific_equivalence_asserted"])
        missing=core.coarse_family_coverage(reg,adm,{"a":spec()})
        self.assertFalse(missing["coverage_complete"])
        self.assertEqual(missing["unmapped_candidate_ids"],["b","c"])
        with self.assertRaises(ValueError):
            core.coarse_family_coverage({"candidates":reg["candidates"]*2},adm,{})

    def test_duplicate_admission_and_registry_mismatch_unmapped(self):
        reg = {"candidates":[{"candidate_id":"a","kind":"FORECAST_TEST","forecast_ids":["f"],
                              "semantic_fingerprint":"x"}]}
        adm = {"candidate_id":"a","semantic_fingerprint":"x","status":"QUALIFIED_FOR_FORWARD_TEST"}
        for rows, reason in (([adm,dict(adm)],"DUPLICATE_ADMISSION_ID"),
                             ([{**adm,"semantic_fingerprint":"y"}],"REGISTRY_METADATA_CONFLICT")):
            out = core.coarse_family_coverage(reg,{"candidates":rows},{"a":spec()})
            self.assertEqual(out["unmapped_reasons"],{"a":reason})
            self.assertFalse(out["coverage_complete"])

    def test_conflicting_forecast_owner_and_malformed_ids_unmapped(self):
        reg = {"candidates":[{"candidate_id":"a","kind":"FORECAST_TEST","forecast_ids":["f"]},
                             {"candidate_id":"b","kind":"FORECAST_TEST","forecast_ids":["f"]},
                             {"candidate_id":"c","kind":"FORECAST_TEST","forecast_ids":["g","g"]}]}
        adm = {"candidates":[{"candidate_id":cid,"semantic_fingerprint":cid,
                              "status":"QUALIFIED_FOR_FORWARD_TEST"} for cid in "abc"]}
        out = core.coarse_family_coverage(reg,adm,{cid:spec() for cid in "abc"})
        self.assertEqual(out["families"],[])
        self.assertEqual(set(out["unmapped_reasons"].values()),{"FORECAST_IDENTITY_UNVERIFIED"})

    def test_registered_forecasts_not_independent_episodes(self):
        reg = {"candidates":[{"candidate_id":"a","kind":"FORECAST_TEST","forecast_ids":["f","g"]}]}
        adm = {"candidates":[{"candidate_id":"a","semantic_fingerprint":"x","status":"QUALIFIED_FOR_FORWARD_TEST"}]}
        out = core.coarse_family_coverage(reg,adm,{"a":spec()})
        self.assertEqual(out["families"][0]["registered_qualified_forecast_id_count"],2)
        self.assertEqual(out["denominator_semantics"],"REGISTERED_FORECAST_IDENTITIES_NOT_INDEPENDENT_EPISODES")
        self.assertFalse(out["allocation_authorized"])

    def test_shared_roster_guard_accepts_asynchronous_partial_adjudication(self):
        core._validate_shared_candidate_rosters(
            {"candidates": [{"candidate_id": "a"}, {"candidate_id": "b"}]},
            {"candidates": [{"candidate_id": "a"}, {"candidate_id": "b"}]},
            {"candidate_actions": [{"candidate_id": "a"}]})

    def test_shared_roster_ambiguity_stops_before_learning_products(self):
        from unittest.mock import patch
        from datetime import datetime, timezone
        for index, field, label in ((0, "candidates", "registry"),
                                    (1, "candidates", "admission"),
                                    (2, "candidate_actions", "adjudication")):
            for rows, reason in (
                ([{"candidate_id": "a", "status": "QUALIFIED_FOR_FORWARD_TEST"},
                  {"candidate_id": "a", "status": "TARGET_UNIT_QUARANTINED"}], "ID_DUPLICATE"),
                ([{"candidate_id": "a"}, {"candidate_id": "a"}], "ID_DUPLICATE"),
                ([{"candidate_id": True}], "ID_INVALID"),
                ([{"candidate_id": " a"}], "ID_INVALID"),
                ([None], "ID_INVALID"),
                (None, "ROSTER_INVALID"),
            ):
                for ordered in (rows, list(reversed(rows)) if isinstance(rows, list) else rows):
                    docs = [{"candidates": [{"candidate_id": "a"}]},
                            {"candidates": [{"candidate_id": "a"}]},
                            {"candidate_actions": [{"candidate_id": "a"}]}]
                    docs[index] = {field: ordered}
                    with self.subTest(label=label, reason=reason, rows=ordered), \
                         patch.object(core, "evaluate_candidates") as produce, \
                         patch.object(core, "persist_json") as write:
                        with self.assertRaisesRegex(RuntimeError, f"SHARED_CANDIDATE_{reason}:{label}"):
                            core._build_products(*docs, {}, {}, {}, datetime(2026, 11, 26, tzinfo=timezone.utc))
                        produce.assert_not_called()
                        write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
