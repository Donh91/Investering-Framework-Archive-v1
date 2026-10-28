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
        "source_bindings": {"auto_market_state": {"packet_sha256": "a" * 64}},
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
        "forecast_first_known_at_utc": "2026-10-27T12:00:00Z",
        "source_first_known_at_utc": "2026-10-27T12:00:00Z",
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

    def test_relabeling_same_original_source_packet_never_inflates_event_count(self):
        from scripts.learning.compass_outcomes import canon
        first = fixture()
        second = copy.deepcopy(first)
        # Two independently named forecast objects and different caller event
        # IDs tied to the identical immutable source packet.
        forecast = json.loads(second["forecast_original_json"])
        forecast["compass_id"] = "CMP-SYNTHETIC-2"
        forecast["compass_sha256"] = hashlib.sha256(canon({
            k: v for k, v in forecast.items() if k != "compass_sha256"
        })).hexdigest()
        outcome = json.loads(second["outcome_original_json"])
        outcome["compass_id"] = forecast["compass_id"]
        outcome["compass_sha256"] = forecast["compass_sha256"]
        outcome["outcome_sha256"] = hashlib.sha256(canon({
            k: v for k, v in outcome.items() if k != "outcome_sha256"
        })).hexdigest()
        second["forecast_original_json"], second["forecast_blob_sha256"] = _encode(forecast)
        second["outcome_original_json"], second["outcome_blob_sha256"] = _encode(outcome)
        second["source_event_id"] = "RELABELED_DIFFERENT_SOURCE_EVENT"
        paired = compare_shadow_12h([first, second])
        self.assertEqual(paired["provisional_paired"], 1)
        self.assertEqual(paired["rows"][1]["reason"], "DUPLICATE_SOURCE_PACKET_TARGET")
        self.assertEqual(paired["rows"][0]["source_packet_sha256"], "a" * 64)

    def test_missing_or_malformed_original_source_packet_digest_cannot_score(self):
        from scripts.learning.compass_outcomes import canon
        for value in (None, "bad", "a" * 63, "G" * 64):
            with self.subTest(value=value):
                def mutate(obj):
                    obj["source_bindings"]["auto_market_state"]["packet_sha256"] = value
                    # Spoofed legacy top-level SHA must never rescue a missing
                    # real producer binding.
                    obj["source_packet_sha256"] = "a" * 64
                    obj["compass_sha256"] = hashlib.sha256(canon({
                        k: v for k, v in obj.items() if k != "compass_sha256"
                    })).hexdigest()
                row = changed_blob(fixture(), "forecast_original_json", "forecast_blob_sha256", mutate)
                # Keep both original producer objects mutually hash-bound so the
                # missing source SHA guard, rather than an earlier custody gate,
                # is the precise failure under test.
                forecast = json.loads(row["forecast_original_json"])
                outcome = json.loads(row["outcome_original_json"])
                outcome["compass_sha256"] = forecast["compass_sha256"]
                outcome["outcome_sha256"] = hashlib.sha256(canon({
                    k: v for k, v in outcome.items() if k != "outcome_sha256"
                })).hexdigest()
                row["outcome_original_json"], row["outcome_blob_sha256"] = _encode(outcome)
                result = compare_shadow_12h([row])
                self.assertEqual(result["provisional_paired"], 0)
                self.assertEqual(result["rows"][0]["reason"], "FORECAST_SOURCE_PACKET_SHA_UNBOUND")

    def test_immutable_outcome_binding_target_and_maturity(self):
        from scripts.learning.compass_outcomes import canon
        # Rehash mutated outcome *after* changing the field so each negative
        # fixture reaches the specific guard under examination.
        edits = (
            (lambda o:o.update(target_at_utc="2026-10-27T11:59:00Z"), "SCORER_REFERENCE_PLUS_12H_MISMATCH"),
            (lambda o:o.update(matured_at_utc="2026-10-27T23:00:00Z"), "TARGET_OBSERVATION_OUTSIDE_SCORER_TOLERANCE"),
            (lambda o:o.update(compass_sha256="b"*64), "FORECAST_OUTCOME_CUSTODY_UNBOUND"),
            (lambda o:o.update(horizon="72h"), "FORECAST_OUTCOME_CUSTODY_UNBOUND"),
            (lambda o:o.update(issued_at_utc="2026-10-27T12:04:00Z"), "FORECAST_OUTCOME_CUSTODY_UNBOUND"),
        )
        for edit, reason in edits:
            def mutate(outcome):
                edit(outcome)
                outcome["outcome_sha256"] = hashlib.sha256(canon({
                    k: v for k, v in outcome.items() if k != "outcome_sha256"
                })).hexdigest()
            row = changed_blob(fixture(), "outcome_original_json", "outcome_blob_sha256", mutate)
            with self.subTest(reason=reason):
                result = compare_shadow_12h([row])
                self.assertEqual(result["provisional_paired"], 0)
                self.assertEqual(result["rows"][0]["reason"], reason)

    def test_two_distinct_source_hashes_same_target_remain_two_provisional_events(self):
        from scripts.learning.compass_outcomes import canon
        original = fixture()
        second = copy.deepcopy(original)
        forecast = json.loads(second["forecast_original_json"])
        forecast["compass_id"] = "CMP-SYNTHETIC-2"
        forecast["source_bindings"]["auto_market_state"]["packet_sha256"] = "b" * 64
        forecast["compass_sha256"] = hashlib.sha256(canon({
            k: v for k, v in forecast.items() if k != "compass_sha256"
        })).hexdigest()
        outcome = json.loads(second["outcome_original_json"])
        outcome["compass_id"] = forecast["compass_id"]
        outcome["compass_sha256"] = forecast["compass_sha256"]
        outcome["outcome_sha256"] = hashlib.sha256(canon({
            k: v for k, v in outcome.items() if k != "outcome_sha256"
        })).hexdigest()
        second["forecast_original_json"], second["forecast_blob_sha256"] = _encode(forecast)
        second["outcome_original_json"], second["outcome_blob_sha256"] = _encode(outcome)
        second["source_event_id"] = "SYNTHETIC_DISTINCT_PACKET"
        result = compare_shadow_12h([original, second])
        self.assertEqual(result["provisional_paired"], 2)
        self.assertEqual(result["rows"][1]["status"], "PROVISIONAL_RESEARCH_ONLY")
        self.assertFalse(result["scientific_edge_verified"])
        # Distinct hashes are an internal cluster control, NOT independent
        # evidence of provider first-known source ownership or a trading edge.

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

    def test_as_issued_receipt_one_second_late_cannot_score(self):
        # An after-issuance receipt does not prove a signal existed when
        # issued. Even a five-minute grace would be hindsight-permissive.
        for timestamp in ("2026-10-27T12:00:01Z", "2026-10-27T12:05:00Z"):
            with self.subTest(timestamp=timestamp):
                late = fixture()
                late["forecast_first_known_at_utc"] = timestamp
                denied = compare_shadow_12h([late])
                self.assertEqual(denied["provisional_paired"], 0)
                self.assertEqual(
                    denied["rows"][0]["reason"],
                    "FORECAST_FIRST_KNOWN_AFTER_ISSUANCE",
                )
        boundary = fixture()
        allowed = compare_shadow_12h([boundary])
        self.assertEqual(allowed["provisional_paired"], 1)
        self.assertFalse(allowed["scientific_edge_verified"])

    def test_source_cannot_be_first_known_before_reference_candle_closes(self):
        row = fixture()
        row["source_first_known_at_utc"] = "2026-10-27T11:59:59Z"
        result = compare_shadow_12h([row])
        self.assertEqual(result["provisional_paired"], 0)
        self.assertEqual(
            result["rows"][0]["reason"],
            "SOURCE_FIRST_KNOWN_BEFORE_SCORER_REFERENCE_CLOSE",
        )

    def test_stale_candle_cannot_masquerade_as_prior_hour_baseline(self):
        row = fixture()
        row["prior_hour_end_at_utc"] = "2026-10-27T10:00:00Z"
        result = compare_shadow_12h([row])
        self.assertEqual(result["provisional_paired"], 0)
        self.assertEqual(result["rows"][0]["reason"], "PRIOR_HOUR_BASELINE_STALE_OR_FUTURE")

    def test_no_original_records_is_no_scientific_claim(self):
        x=compare_shadow_12h([])
        self.assertIsNone(x["provisional_coverage"])
        self.assertFalse(x["scientific_edge_verified"])

    def test_malformed_nested_scorer_objects_are_excluded_not_batch_crashes(self):
        # Original bytes and both canonical self-digests remain valid: these
        # negatives must reach schema guards rather than a hash mismatch.
        from scripts.learning.compass_outcomes import canon
        invalid_basis = changed_blob(
            fixture(), "outcome_original_json", "outcome_blob_sha256",
            lambda o: (
                o.update(time_basis="not-an-object"),
                o.update(outcome_sha256=hashlib.sha256(canon({
                    k: v for k, v in o.items() if k != "outcome_sha256"
                })).hexdigest()),
            ),
        )
        invalid_reference = fixture()
        forecast = json.loads(invalid_reference["forecast_original_json"])
        forecast["market_reference"] = "not-an-object"
        forecast["compass_sha256"] = hashlib.sha256(canon({
            k: v for k, v in forecast.items() if k != "compass_sha256"
        })).hexdigest()
        outcome = json.loads(invalid_reference["outcome_original_json"])
        outcome["compass_sha256"] = forecast["compass_sha256"]
        outcome["outcome_sha256"] = hashlib.sha256(canon({
            k: v for k, v in outcome.items() if k != "outcome_sha256"
        })).hexdigest()
        invalid_reference["forecast_original_json"], invalid_reference["forecast_blob_sha256"] = _encode(forecast)
        invalid_reference["outcome_original_json"], invalid_reference["outcome_blob_sha256"] = _encode(outcome)

        for bad, expected in (
            (invalid_basis, "SCORER_TIME_BASIS_NOT_MAPPING"),
            (invalid_reference, "SCORER_REFERENCE_NOT_MAPPING"),
        ):
            with self.subTest(reason=expected):
                batch = compare_shadow_12h([bad, fixture()])
                self.assertEqual(batch["attempted"], 2)
                self.assertEqual(batch["provisional_paired"], 1)
                self.assertEqual(batch["rows"][0]["reason"], expected)
                self.assertEqual(batch["rows"][1]["status"], "PROVISIONAL_RESEARCH_ONLY")
                self.assertFalse(batch["scientific_edge_verified"])

    def test_non_directional_signal_never_receives_accuracy(self):
        row=changed_blob(fixture(),"forecast_original_json","forecast_blob_sha256",
                         lambda f:f["horizons"]["NEXT_12H"].update(expected_direction="MIXED"))
        self.assertEqual(compare_shadow_12h([row])["provisional_paired"],0)


if __name__=="__main__":
    unittest.main()
