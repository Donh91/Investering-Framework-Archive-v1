import unittest

from research.api_agent.meme_alpha.project_ca_binding_p2 import (
    ProjectCABindingError, build_binding,
)


def memory():
    return {
        "contract": "PROJECT_CA_PROJECT_MEMORY_P1_v1",
        "project_trial_id": "PCA-P1-test",
        "snapshot_sha256": "1" * 64,
    }


def evidence(available="2026-09-23T17:00:00Z"):
    return [{
        "evidence_ref": "official:token",
        "observed_at_utc": "2026-09-23T17:01:00Z",
        "available_at_utc": available,
        "evidence_sha256": "a" * 64,
        "authentication_state": "AUTHENTICATED_FIRST_PARTY",
        "conflict_state": "NONE",
    }]


def onchain(ca="0xabc"):
    return {"verified": True, "chain_id": "rh", "token_ca": ca, "evidence_sha256": "b" * 64}


def control():
    return {"authenticated": True, "evidence_sha256": "c" * 64}


def bind(**overrides):
    kw = dict(
        project_memory=memory(),
        chain_id="rh",
        token_ca="0xabc",
        relationship_type="FIRST_PARTY_EXPLICIT_CA",
        binding_provenance=evidence(),
        first_candidate_at_utc="2026-09-23T17:00:00Z",
        onchain_verification=onchain(),
        project_control_binding=control(),
    )
    kw.update(overrides)
    return build_binding(**kw)


class P2BindingTests(unittest.TestCase):
    def test_first_party_exact_ca_can_reach_bound_high(self):
        self.assertEqual(bind()["binding_state"], "BOUND_HIGH")

    def test_project_controlled_onchain_relation_can_reach_bound_high(self):
        self.assertEqual(bind(relationship_type="PROJECT_CONTROLLED_ONCHAIN_RELATION")["binding_state"], "BOUND_HIGH")

    def test_pons_factory_launch_is_candidate_only(self):
        row = bind(relationship_type="FACTORY_LAUNCH_CANDIDATE_ONLY")
        self.assertEqual(row["binding_state"], "CANDIDATE_BINDING")

    def test_social_only_is_candidate_only(self):
        self.assertEqual(bind(relationship_type="SOCIAL_CANDIDATE_ONLY")["binding_state"], "CANDIDATE_BINDING")

    def test_missing_available_at_cannot_reach_bound_high(self):
        self.assertEqual(bind(binding_provenance=evidence(None))["binding_state"], "CANDIDATE_BINDING")

    def test_wrong_exact_ca_cannot_reach_bound_high(self):
        self.assertEqual(bind(onchain_verification=onchain("0xdef"))["binding_state"], "CANDIDATE_BINDING")

    def test_material_conflict_forces_conflicted(self):
        row = bind(conflicts=[{"conflict_id": "same-ticker-two-ca", "state": "UNRESOLVED"}])
        self.assertEqual(row["binding_state"], "CONFLICTED")

    def test_safix_style_conflict_never_latest_wins(self):
        row = bind(
            relationship_type="FIRST_PARTY_EXPLICIT_CA",
            conflicts=[{"conflict_id": "SAFIX-SFX-CA-A-vs-CA-B", "state": "UNRESOLVED"}],
        )
        self.assertEqual(row["binding_state"], "CONFLICTED")
        self.assertIsNone(row["bound_high_at_utc_or_null"])

    def test_migration_requires_explicit_continuity(self):
        candidate = bind(relationship_type="MIGRATION_WITH_CONTINUITY_PROOF")
        self.assertEqual(candidate["binding_state"], "CANDIDATE_BINDING")
        high = bind(
            relationship_type="MIGRATION_WITH_CONTINUITY_PROOF",
            continuity_proof={"explicit": True, "evidence_sha256": "d" * 64},
            supersedes_binding={"binding_id": "old-binding", "binding_state": "BOUND_HIGH", "chain_id": "rh", "token_ca": "0xold"},
        )
        self.assertEqual(high["binding_state"], "BOUND_HIGH")
        self.assertEqual(high["superseded_prior_binding"]["lineage_state"], "SUPERSEDED_WITH_PROOF")

    def test_source_outage_is_not_revocation(self):
        row = bind(project_control_binding={"authenticated": False, "source_health": "UNAVAILABLE"})
        self.assertEqual(row["binding_state"], "CANDIDATE_BINDING")

    def test_revocation_requires_explicit_hashed_evidence(self):
        with self.assertRaises(ProjectCABindingError):
            bind(explicit_revocation={"explicit": True})
        self.assertEqual(
            bind(explicit_revocation={"explicit": True, "evidence_sha256": "e" * 64})["binding_state"],
            "REVOKED",
        )

    def test_requires_p1_memory(self):
        with self.assertRaises(ProjectCABindingError):
            bind(project_memory={"contract": "wrong", "project_trial_id": "x"})


if __name__ == "__main__":
    unittest.main()
