from scripts.experiments.build_experiment_yield_shadow import build_shadow


def test_shadow_classifies_without_production_authority():
    registry = {"rows": [
        {"experiment_id": "blocked", "state": "WAITING_FOR_DATA"},
        {"experiment_id": "dup", "state": "PROPOSED", "duplicate_of": "x"},
        {"experiment_id": "quiet", "state": "MATURED_INCONCLUSIVE", "observation_count": 0},
        {"experiment_id": "base", "state": "MATURED_SUPPORTED"},
    ]}
    result = build_shadow(registry, {"rows": []})
    rows = {r["experiment_id"]: r for r in result["rows"]}
    assert rows["blocked"]["shadow_state"] == "OBSERVE"
    assert rows["dup"]["shadow_state"] == "OBSERVE"
    assert rows["quiet"]["shadow_state"] == "OBSERVE"
    assert rows["base"]["shadow_state"] == "SHADOW_BASELINE"
    assert result["mode"] == "SHADOW_OBSERVE_ONLY"
    assert result["promotion_policy"]["natural_observation_window_required"] is True
    assert result["promotion_policy"]["automatic_retirement_allowed"] is False
    assert result["authority"]["production_suppression"] is False
