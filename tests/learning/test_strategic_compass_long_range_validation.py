import copy
import unittest

from scripts.learning.strategic_compass_long_range_validation import validate_candidate

H = "f" * 64


def fixture():
    return {
        "contract": "LONG_RANGE_SCENARIO_v0_1_CANDIDATE", "authority": "SHADOW_SCENARIO_ONLY", "status": "SCENARIO_ONLY",
        "frozen_issue": {"forecast_id": "candidate-a", "issued_at_utc": "2026-10-21T08:00:00Z", "cutoff_utc": "2026-10-21T07:45:00Z", "source_manifest_sha256": H, "model_policy_version": "research-1", "freeze_content_sha256": H, "revision_of": None, "revision_cost": None},
        "observation": {"as_of_utc": "2026-10-21T07:30:00Z", "items": [{"id": "settled-copper", "value_state": "PRESENT", "settled": True, "source_first_known_utc": "2026-10-20T12:00:00Z"}]},
        "hypothesis_families": [{"family_id": "macro-a", "clock": "MACRO_CYCLE_CLOCK", "asset_id": "bitcoin", "horizon": "3_6M", "scenarios": [{"scenario": "BASE", "window_start_utc": "2027-01-21T00:00:00Z", "window_end_utc": "2027-04-21T00:00:00Z", "price_band_low": 70000.0, "price_band_high": 125000.0, "confirmation": ["independent breadth evidence"]}], "invalidation": [{"rule": "settled monthly macro turns down", "settled_only": True}], "falsifier_dates": [{"date_utc": "2027-04-21T00:00:00Z", "test": "direction vs baseline", "derived_from": "PREREGISTERED_BY_OWNER"}], "probability": None, "evidence_quality": "UNKNOWN", "source_available": True}]}


class LongRangeCandidateTests(unittest.TestCase):
    def test_positive(self):
        validate_candidate(fixture())

    def reject(self, patch):
        v = copy.deepcopy(fixture())
        patch(v)
        with self.assertRaises(ValueError):
            validate_candidate(v)

    def test_future_knowledge(self):
        self.reject(lambda v: v["observation"]["items"][0].update(source_first_known_utc="2026-10-22T00:00:00Z"))

    def test_source_first_known_after_observation_asof_but_before_cutoff(self):
        self.reject(lambda v: v["observation"]["items"][0].update(
            source_first_known_utc="2026-10-21T07:40:00Z"))

    def test_future_cutoff(self):
        self.reject(lambda v: v["frozen_issue"].update(cutoff_utc="2026-10-22T00:00:00Z"))

    def test_future_observation_as_of(self):
        self.reject(lambda v: v["observation"].update(as_of_utc="2026-10-21T08:00:01Z"))

    def test_reversed_window(self):
        self.reject(lambda v: v["hypothesis_families"][0]["scenarios"][0].update(window_end_utc="2027-01-20T00:00:00Z"))

    def test_window_before_issue(self):
        self.reject(lambda v: v["hypothesis_families"][0]["scenarios"][0].update(window_start_utc="2026-10-20T00:00:00Z"))

    def test_negative_price(self):
        self.reject(lambda v: v["hypothesis_families"][0]["scenarios"][0].update(price_band_low=-1))

    def test_nonfinite_price(self):
        self.reject(lambda v: v["hypothesis_families"][0]["scenarios"][0].update(price_band_high=float("nan")))

    def test_boolean_price(self):
        self.reject(lambda v: v["hypothesis_families"][0]["scenarios"][0].update(price_band_low=True))

    def test_inverted_price_band(self):
        self.reject(lambda v: v["hypothesis_families"][0]["scenarios"][0].update(price_band_low=150000))

    def test_single_price_edge(self):
        self.reject(lambda v: v["hypothesis_families"][0]["scenarios"][0].update(price_band_high=None))

    def test_self_revision(self):
        self.reject(lambda v: v["frozen_issue"].update(revision_of="candidate-a"))

    def test_unknown_original_revision(self):
        self.reject(lambda v: v["frozen_issue"].update(revision_of="candidate-before"))

    def test_revision_requires_original_earlier(self):
        v = fixture()
        v["frozen_issue"]["revision_of"] = "prior"
        with self.assertRaises(ValueError):
            validate_candidate(v, prior_issues={"prior": {"forecast_id": "prior", "issued_at_utc": "2026-10-22T08:00:00Z", "freeze_content_sha256": H}})

    def test_valid_revision_preserves_original(self):
        v = fixture()
        v["frozen_issue"]["revision_of"] = "prior"
        original = {"forecast_id": "prior", "issued_at_utc": "2026-10-20T08:00:00Z", "freeze_content_sha256": H}
        before = copy.deepcopy(original)
        validate_candidate(v, prior_issues={"prior": original})
        self.assertEqual(before, original)

    def test_revision_cycle(self):
        v = fixture()
        v["frozen_issue"]["revision_of"] = "prior"
        with self.assertRaises(ValueError):
            validate_candidate(v, prior_issues={"prior": {"forecast_id": "prior", "issued_at_utc": "2026-10-20T08:00:00Z", "freeze_content_sha256": H, "revision_of": "candidate-a"}})

    def test_probability_is_not_calibrated(self):
        self.reject(lambda v: v["hypothesis_families"][0].update(probability=0.8))

    def test_missing_invalidation(self):
        self.reject(lambda v: v["hypothesis_families"][0].update(invalidation=[]))

    def test_missing_falsifier(self):
        self.reject(lambda v: v["hypothesis_families"][0].update(falsifier_dates=[]))

    def test_unsettled_source(self):
        self.reject(lambda v: v["observation"]["items"][0].update(settled=False))

    def test_unknown_source_clock(self):
        self.reject(lambda v: v["observation"]["items"][0].update(source_first_known_utc=None))

    def test_matured_actual_not_on_issue(self):
        self.reject(lambda v: v.update(afterwards_actual={"return": 0.12}))

    def test_revision_cost_not_on_issue(self):
        self.reject(lambda v: v["frozen_issue"].update(revision_cost={"days": 1}))

    def test_unavailable_fails_closed(self):
        v = fixture()
        v["status"] = "UNAVAILABLE"
        family = v["hypothesis_families"][0]
        family["source_available"] = False
        family["scenarios"][0]["price_band_low"] = None
        family["scenarios"][0]["price_band_high"] = None
        validate_candidate(v)
        family["scenarios"][0]["price_band_high"] = 100000
        with self.assertRaises(ValueError):
            validate_candidate(v)

    def test_abstain_requires_available_sources(self):
        v = fixture()
        v["status"] = "ABSTAIN"
        v["hypothesis_families"][0]["scenarios"][0]["price_band_low"] = None
        v["hypothesis_families"][0]["scenarios"][0]["price_band_high"] = None
        validate_candidate(v)
        v["hypothesis_families"][0]["source_available"] = False
        with self.assertRaises(ValueError):
            validate_candidate(v)

    def test_duplicate_scenario(self):
        self.reject(lambda v: v["hypothesis_families"][0]["scenarios"].append(copy.deepcopy(v["hypothesis_families"][0]["scenarios"][0])))

    def test_duplicate_observation(self):
        self.reject(lambda v: v["observation"]["items"].append(copy.deepcopy(v["observation"]["items"][0])))

    def test_duplicate_family(self):
        self.reject(lambda v: v["hypothesis_families"].append(copy.deepcopy(v["hypothesis_families"][0])))

    def test_extra_private_data_field(self):
        self.reject(lambda v: v.update(private_wallet={"address": "hidden"}))

    def test_malformed_utc_date(self):
        self.reject(lambda v: v["frozen_issue"].update(issued_at_utc="2026-10-21"))


if __name__ == "__main__":
    unittest.main()
