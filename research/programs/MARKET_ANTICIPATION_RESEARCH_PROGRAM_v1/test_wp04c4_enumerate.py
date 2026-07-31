from wp04c4_enumerate import evaluate


def test_empty_registry_fails_closed():
    out = evaluate({"datasets": []})
    assert out["status"] == "BLOCKED"
    assert out["enumeration_authorized"] is False
    assert all(value is None for value in out["candidate_event_counts"].values())
    assert out["outcome_access"] is False


def test_declared_but_unverified_is_not_replayable():
    out = evaluate({"datasets": [{
        "dataset_id": "DGS2",
        "materialization_status": "REPLAYABLE_OWNER",
        "member_sha256_verified": False,
        "raw_normalized_parity": "PASS"
    }]})
    assert "DGS2" in out["missing_required_owner_datasets"]


def test_no_outcome_fields_emitted():
    out = evaluate({"datasets": []})
    forbidden = {"forward_returns", "hit_rate", "drawdown", "economic_rank"}
    assert forbidden.isdisjoint(out)
