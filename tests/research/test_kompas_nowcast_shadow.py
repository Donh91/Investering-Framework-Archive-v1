"""Synthetic positive and mutation-negative regressions for the Kompas PIT shadow gate."""
import copy
import hashlib
import json
import unittest
from scripts.research.kompas_nowcast_shadow import compare_shadow_12h


def _encode(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return raw, hashlib.sha256(raw.encode()).hexdigest()


def fixture():
    forecast = {
        "contract": "OFFICIAL_DAILY_COMPASS_v1",
        "scoring_contract": "OFFICIAL_DAILY_COMPASS_SCORING_v3",
        "compass_id": "CMP-SYNTHETIC-1",
        "issued_at_utc": "2026-10-27T12:00:00Z",
        "market_reference": {"observation_open_utc": "2026-10-27T11:00:00Z"},
        "horizons": {"NEXT_12H": {"expected_direction": "UP"}}
    }
    from scripts.learning.compass_outcomes import canon
    forecast["compass_sha256"] = hashlib.sha256(canon(forecast)).hexdigest()
    outcome = {
        "contract": "OFFICIAL_DAILY_COMPASS_OUTCOME_v1",
        "scoring_contract": "OFFICIAL_DAILY_COMPASS_SCORING_v3",
        "compass_id": "CMP-SYNTHETIC-1", "compass_sha256": forecast["compass_sha256"],
        "issued_at_utc": "2026-10-27T12:00:00Z", "horizon": "12h",
        "target_at_utc": "2026-10-28T00:00:00Z",
        "target_observation_at_utc": "2026-10-28T00:00:00Z",
        "time_basis": {"start_reference_at_utc": "2026-10-27T12:00:00Z", "nominal_horizon_hours": 12},
        "matured_at_utc": "2026-10-28T00:10:00Z",
        "direction_accuracy": {"btc": {"realized_pct": -1.0}, "eth": {"realized_pct": 2.0}}
    }
    outcome["outcome_sha256"] = hashlib.sha256(canon(outcome)).hexdigest()
    fb, fh = _encode(forecast)
    ob, oh = _encode(outcome)
    return {
        "forecast_original_json": fb, "forecast_blob_sha256": fh,
        "outcome_original_json": ob, "outcome_blob_sha256": oh,
        "source_event_id": "SYNTHETIC_HOURLY_1100",
        "forecast_first_known_verified": True,
        "source_first_known_verified": True,
        "outcome_custody_verified": True,
        "prior_hour_custody_verified": True,
        "forecast_receipt_ref": "independent:synthetic:issuer",
        "source_receipt_ref": "independent:synthetic:source",
        "outcome_receipt_ref": "independent:synthetic:outcome",
        "prior_hour_receipt_ref": "independent:synthetic:prior",
        "forecast_first_known_at_utc": "2026-10-27T12:00:05Z",
        "source_first_known_at_utc": "2026-10-27T11:10:00Z",
        "prior_hour_first_known_at_utc": "2026-10-27T11:01:00Z",
        "prior_hour_end_at_utc": "2026-10-27T11:00:00Z",
        "prior_hour_btc_delta_pct": 0.2, "prior_hour_eth_delta_pct": -0.3,
    }


def changed_blob(row, key, digest, operation):
    result = copy.deepcopy(row)
    data = json.loads(result[key])
    operation(data)
    result[key], result[digest] = _encode(data)
    return result


class KompasShadowTests(unittest.TestCase):
    def test_one_eligible_of_two_has_half_provisional_coverage(self):
        good = fixture()
        missing = copy.deepcopy(good)
        missing["forecast_first_known_verified"] = False
        result = compare_shadow_12h([good, missing])
        self.assertEqual((result["attempted"],result["provisional_paired"],result["excluded"]), (2,1,1))
        self.assertEqual(result["provisional_coverage"], 0.5)
        self.assertFalse(result["scientific_edge_verified"])
        self.assertFalse(result["trading_authority"])
        scored = result["rows"][0]
        self.assertFalse(scored["btc_correct"])
        self.assertTrue(scored["eth_correct"])
        self.assertFalse(scored["persistence_btc_correct"])
        self.assertFalse(scored["persistence_eth_correct"])

    def test_mutation_lookahead_tamper_duplicate_denial(self):
        mutation = {
            "late_source": lambda x:x.update(source_first_known_at_utc="2026-10-27T12:01:00Z"),
            "late_issuer": lambda x:x.update(forecast_first_known_at_utc="2026-10-28T01:00:00Z"),
            "late_prior": lambda x:x.update(prior_hour_first_known_at_utc="2026-10-27T12:10:00Z"),
            "unsigned_receipt": lambda x:x.update(outcome_receipt_ref=""),
            "outcome_not_verified": lambda x:x.update(outcome_custody_verified=False),
            "source_hash_tamper": lambda x:x.update(forecast_blob_sha256="0"*64),
            "future_prior_close": lambda x:x.update(prior_hour_end_at_utc="2026-10-27T13:00:00Z"),
            "naive_timestamp": lambda x:x.update(source_first_known_at_utc="2026-10-27T11:00:00"),
            "nonfinite_baseline": lambda x:x.update(prior_hour_btc_delta_pct=float("nan")),
        }
        for name, change in mutation.items():
            with self.subTest(name=name):
                row = fixture()
                change(row)
                result = compare_shadow_12h([row])
                self.assertEqual(result["provisional_paired"], 0)

        self.assertEqual(compare_shadow_12h([fixture(),fixture()])["provisional_paired"],1)
        self.assertIn("DUPLICATE",compare_shadow_12h([fixture(),fixture()])["rows"][1]["reason"])

    def test_immutable_outcome_binding_target_and_maturity(self):
        edits = (
            lambda o:o.update(target_at_utc="2026-10-27T11:59:00Z"),
            lambda o:o.update(matured_at_utc="2026-10-27T23:00:00Z"),
            lambda o:o.update(compass_sha256="b"*64),
            lambda o:o.update(horizon="72h"),
            lambda o:o.update(issued_at_utc="2026-10-27T12:04:00Z"),
        )
        for edit in edits:
            row=changed_blob(fixture(),"outcome_original_json","outcome_blob_sha256",edit)
            with self.subTest(edit=edit):
                self.assertEqual(compare_shadow_12h([row])["provisional_paired"],0)

    def test_integrity_and_time_basis_adversarial_mutations(self):
        from scripts.learning.compass_outcomes import canon
        def mutate_forecast(obj):
            obj["horizons"]["NEXT_12H"]["expected_direction"]="DOWN"
            # Caller blob hash will change; production canonical self hash will not.
        row=changed_blob(fixture(),"forecast_original_json","forecast_blob_sha256",mutate_forecast)
        self.assertEqual(compare_shadow_12h([row])["provisional_paired"],0)
        self.assertEqual(compare_shadow_12h([row])["rows"][0]["reason"],"CANONICAL_SELF_DIGEST_MISMATCH")
        def time_shift(o):
            o["target_at_utc"]="2026-10-28T00:05:00Z"
            o.pop("outcome_sha256")
            o["outcome_sha256"]=hashlib.sha256(canon(o)).hexdigest()
        row=changed_blob(fixture(),"outcome_original_json","outcome_blob_sha256",time_shift)
        self.assertEqual(compare_shadow_12h([row])["provisional_paired"],0)
        self.assertEqual(compare_shadow_12h([row])["rows"][0]["reason"],"SCORER_REFERENCE_PLUS_12H_MISMATCH")
        row=fixture()
        row["prior_hour_first_known_at_utc"]="2026-10-27T10:59:00Z"
        self.assertEqual(compare_shadow_12h([row])["rows"][0]["reason"],"PRIOR_HOUR_FIRST_KNOWN_BEFORE_CLOSE")

    def test_invalid_first_then_valid_same_id_is_not_poisoned(self):
        bad=fixture()
        bad["source_first_known_verified"]=False
        rows=compare_shadow_12h([bad,fixture()])
        self.assertEqual((rows["attempted"],rows["provisional_paired"]), (2,1))
        self.assertEqual(rows["rows"][1]["status"],"PROVISIONAL_RESEARCH_ONLY")
        rows2=compare_shadow_12h([fixture(),fixture()])
        self.assertEqual(rows2["provisional_paired"],1)
        self.assertIn("DUPLICATE",rows2["rows"][1]["reason"])

    def test_no_original_records_is_no_scientific_claim(self):
        x=compare_shadow_12h([])
        self.assertIsNone(x["provisional_coverage"])
        self.assertFalse(x["scientific_edge_verified"])

    def test_non_directional_signal_never_receives_accuracy(self):
        row=changed_blob(fixture(),"forecast_original_json","forecast_blob_sha256",
                         lambda f:f["horizons"]["NEXT_12H"].update(expected_direction="MIXED"))
        self.assertEqual(compare_shadow_12h([row])["provisional_paired"],0)


if __name__=="__main__":
    unittest.main()
