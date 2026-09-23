import copy
import pytest

from scripts.api_agent.meme_alpha.project_ca_project_memory import (
    append_snapshot, freeze_project_trial, source_observation, stable_project_trial_id,
)


def identity():
    return {"identity_anchor": {"authenticated_control_root": "https://example.invalid/project"}}


def obs(conflict="NONE"):
    return source_observation(source_ref="official:project", observed_at="2026-09-23T15:00:00Z",
        available_at="2026-09-23T14:59:00Z", content_hash="a"*64,
        authentication_state="AUTHENTICATED", conflict_state=conflict)


def trial(**kw):
    base=dict(method_version="pca-bridge-v1", frozen_at_utc="2026-09-23T15:00:01Z",
        eligibility_manifest_sha256="b"*64, discovery={"route":"project_first"},
        project_identity=identity(), source_observations=[obs()])
    base.update(kw)
    return freeze_project_trial(**base)


def test_8ball_no_token_persists_without_outcome():
    x=trial()
    assert x["token_state"]=="NO_TOKEN_OBSERVED"
    assert x["ca_candidates"]==[]
    assert "outcome" not in x
    assert x["authority"]["project_to_ca_binding"] is False


def test_alias_and_order_do_not_create_second_trial():
    a=stable_project_trial_id("pca-bridge-v1", {"control_root":"x","chain":"rh"})
    b=stable_project_trial_id("pca-bridge-v1", {"chain":"rh","control_root":"x"})
    assert a==b


@pytest.mark.parametrize("bad", [{"ticker":"ABC"},{"name":"Project"},{"logo":"x"},{"alias":"p"}])
def test_alias_fields_cannot_establish_identity(bad):
    with pytest.raises(ValueError):
        stable_project_trial_id("pca-bridge-v1", bad)


def test_hoodstack_conflict_is_preserved_not_latest_wins():
    x=trial(source_observations=[obs("NONE"), obs("MATERIAL_CONFLICT")])
    assert [o["conflict_state"] for o in x["source_observations"]]==["NONE","MATERIAL_CONFLICT"]


def test_missing_available_at_remains_unknown():
    o=obs(); o["available_at"]=None
    assert trial(source_observations=[o])["source_observations"][0]["available_at"] is None


def test_history_is_append_only_and_deduplicated():
    first=trial()
    history=append_snapshot([], first)
    before=copy.deepcopy(history)
    history2=append_snapshot(history, first)
    assert history==before
    assert history2==history
    changed=trial(token_state="TOKEN_CANDIDATE", ca_candidates=[{"chain_id":"rh","token_ca":"0x1"}])
    history3=append_snapshot(history, changed, history[0]["snapshot_sha256"])
    assert len(history3)==2
    assert history3[0]==history[0]


def test_p1_candidate_has_no_binding_authority():
    x=trial(token_state="TOKEN_CANDIDATE", ca_candidates=[{"chain_id":"rh","token_ca":"0x1","source":"PONS"}])
    assert x["token_state"]=="TOKEN_CANDIDATE"
    assert x["authority"]["project_to_ca_binding"] is False
