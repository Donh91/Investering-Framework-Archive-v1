from scripts.learning import rotation_survival_sampling_validity as validity


def provenance(mode):
    adaptive = mode == validity.ADAPTIVE_BOOST
    return {
        "contract": validity.PROVENANCE_CONTRACT,
        "sampling_mode": mode,
        "capture_origin": "ADAPTIVE_ROTATION_CADENCE" if adaptive else "RICH_BREADTH_CHECKPOINT",
        "capture_run_id": "gh-42-1",
        "parent_cadence_run_id": "gh-42-1" if adaptive else None,
        "parent_cadence_observation_path": "03_DAILY_CAPTURE_LOGS/cadence/cadence-42-1.json" if adaptive else None,
        "parent_cadence_observation_sha256": "a" * 64 if adaptive else None,
        "adaptive_selection": adaptive,
        "independence_policy": "DOWNSTREAM_EXPLICIT_ORIGIN_AND_NON_OVERLAPPING_WINDOW_VALIDATION_REQUIRED",
        "can_create_market_evidence": False,
        "can_create_rotation_vote": False,
        "can_create_portfolio_permission": False,
        "can_change_canonical_state": False,
    }


def checkpoint(timestamp, mode=None):
    value = {
        "contract": "RICH_BREADTH_CHECKPOINT_v1",
        "retrieved_at_utc": timestamp,
        "authority": {
            "binding": False,
            "canonical_acceptance": False,
            "state_change": False,
            "portfolio_action": False,
        },
        "observation": {
            "retrieval_timestamp_utc": timestamp,
            "window_semantics": validity.ROLLING_24H,
        },
    }
    if mode is not None:
        value["sampling_provenance"] = provenance(mode)
    return value


def test_one_normal_plus_multiple_same_window_boosts_is_one_confirmation():
    report = validity.summarize(
        [
            ("normal.json", checkpoint("2026-09-01T00:00:00Z", validity.ORDINARY_CHECKPOINT)),
            ("boost-1.json", checkpoint("2026-09-01T02:00:00Z", validity.ADAPTIVE_BOOST)),
            ("boost-2.json", checkpoint("2026-09-01T04:00:00Z", validity.ADAPTIVE_BOOST)),
        ]
    )
    assert report["raw_capture_count"] == 3
    assert report["adaptive_boost_capture_count"] == 2
    assert report["independent_observation_count"] == 1
    assert report["survival_confirmation_count"] == 1
    assert report["non_independent_capture_count"] == 2
    normal, boost_1, boost_2 = report["sampling_context"]
    assert normal["independent_observation"] is True
    assert boost_1["independent_observation"] is False
    assert boost_2["independent_observation"] is False
    assert boost_1["independence_group_id"] == normal["independence_group_id"]
    assert boost_2["independence_group_id"] == normal["independence_group_id"]
    assert boost_1["independence_reason"] == "ADAPTIVE_BOOST_ENDOGENOUS_NOT_ADDITIONAL_CONFIRMATION"


def test_overlapping_ordinary_windows_are_not_multiple_confirmations():
    report = validity.summarize(
        [
            ("ordinary-0.json", checkpoint("2026-09-01T00:00:00Z", validity.ORDINARY_CHECKPOINT)),
            ("ordinary-12.json", checkpoint("2026-09-01T12:00:00Z", validity.ORDINARY_CHECKPOINT)),
            ("ordinary-24.json", checkpoint("2026-09-02T00:00:00Z", validity.ORDINARY_CHECKPOINT)),
        ]
    )
    assert report["raw_capture_count"] == 3
    assert report["independent_observation_count"] == 2
    assert [row["independent_observation"] for row in report["sampling_context"]] == [True, False, True]
    assert (
        report["sampling_context"][1]["independence_reason"]
        == "OVERLAPPING_ROLLING_WINDOW_NOT_ADDITIONAL_CONFIRMATION"
    )


def test_boost_only_observations_cannot_create_survival_confirmation():
    report = validity.summarize(
        [
            ("boost-0.json", checkpoint("2026-09-01T00:00:00Z", validity.ADAPTIVE_BOOST)),
            ("boost-30.json", checkpoint("2026-09-02T06:00:00Z", validity.ADAPTIVE_BOOST)),
        ]
    )
    assert report["raw_capture_count"] == 2
    assert report["independent_observation_count"] == 0
    assert report["survival_confirmation_count"] == 0


def test_legacy_missing_origin_remains_unknown_and_is_not_inferred():
    report = validity.summarize([("legacy.json", checkpoint("2026-09-01T00:00:00Z"))])
    assert report["unknown_origin_capture_count"] == 1
    assert report["ordinary_capture_count"] == 0
    assert report["independent_observation_count"] == 0
    context = report["sampling_context"][0]
    assert context["sampling_mode"] == "UNKNOWN"
    assert context["capture_origin"] == "UNKNOWN"
    assert context["independence_reason"] == "LEGACY_ORIGIN_UNKNOWN_NOT_INFERRED"


def test_invalid_or_authoritative_provenance_fails_closed_to_unknown():
    value = checkpoint("2026-09-01T00:00:00Z", validity.ORDINARY_CHECKPOINT)
    value["sampling_provenance"]["can_create_market_evidence"] = True
    report = validity.summarize([("invalid.json", value)])
    assert report["unknown_origin_capture_count"] == 1
    assert report["survival_confirmation_count"] == 0
    assert report["sampling_context"][0]["independence_reason"] == "INVALID_PROVENANCE_FAIL_CLOSED"


def test_invalid_checkpoint_contract_or_authority_cannot_count():
    value = checkpoint("2026-09-01T00:00:00Z", validity.ORDINARY_CHECKPOINT)
    value["authority"]["binding"] = True
    report = validity.summarize([("binding.json", value)])
    assert report["survival_confirmation_count"] == 0
    assert report["sampling_context"][0]["sampling_mode"] == "UNKNOWN"
    assert report["sampling_context"][0]["independence_reason"] == "CHECKPOINT_CONTRACT_OR_AUTHORITY_INVALID"


def test_report_has_no_market_or_portfolio_authority():
    report = validity.summarize(
        [("normal.json", checkpoint("2026-09-01T00:00:00Z", validity.ORDINARY_CHECKPOINT))]
    )
    assert all(value is False for value in report["authority"].values())
