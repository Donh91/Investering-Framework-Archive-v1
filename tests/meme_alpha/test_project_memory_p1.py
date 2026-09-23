import unittest

from research.api_agent.meme_alpha.project_memory_p1 import (
    ProjectMemoryError,
    build_project_memory,
    supersede_project_memory,
)


def base(**overrides):
    kwargs = dict(
        method_version="p1-test",
        frozen_at_utc="2026-09-23T15:30:00Z",
        eligibility_manifest_sha256="a" * 64,
        discovery={"source": "fixture"},
        project_identity={
            "control_roots": [{
                "root_type": "AUTHENTICATED_PROJECT_ROOT",
                "root_value": "https://example.test/project",
            }],
            "aliases": ["Eight Ball", "8-Ball"],
        },
        source_observations=[{
            "source_ref": "fixture:official",
            "observed_at_utc": "2026-09-23T15:29:00Z",
            "available_at_utc": "2026-09-23T15:00:00Z",
            "content_sha256": "b" * 64,
            "authentication_state": "AUTHENTICATED",
            "conflict_state": "NONE",
        }],
        token_state="NO_TOKEN_OBSERVED",
    )
    kwargs.update(overrides)
    return kwargs


class ProjectMemoryP1Tests(unittest.TestCase):
    def test_8ball_no_token_persists_without_outcome(self):
        row = build_project_memory(**base())
        self.assertEqual(row["token_state"], "NO_TOKEN_OBSERVED")
        self.assertTrue(row["project_trial_id"].startswith("PCA-P1-"))
        self.assertFalse(row["authority"]["project_ca_binding"])

    def test_alias_order_does_not_create_second_trial(self):
        a = build_project_memory(**base())
        ident = dict(base()["project_identity"])
        ident["aliases"] = ["totally-new-alias", "8-Ball"]
        b = build_project_memory(**base(project_identity=ident))
        self.assertEqual(a["project_trial_id"], b["project_trial_id"])

    def test_name_ticker_or_alias_cannot_establish_identity(self):
        with self.assertRaises(ProjectMemoryError):
            build_project_memory(**base(project_identity={"aliases": ["SFX"], "ticker": "SFX"}))

    def test_source_timestamps_hash_and_conflict_are_preserved(self):
        row = build_project_memory(**base())
        src = row["source_observations"][0]
        self.assertEqual(src["observed_at_utc"], "2026-09-23T15:29:00Z")
        self.assertEqual(src["available_at_utc"], "2026-09-23T15:00:00Z")
        self.assertEqual(src["content_sha256"], "b" * 64)

    def test_hoodstack_conflicting_mutable_sources_preserved(self):
        sources = list(base()["source_observations"]) + [{
            "source_ref": "fixture:official",
            "observed_at_utc": "2026-09-23T15:31:00Z",
            "available_at_utc": "2026-09-23T15:31:00Z",
            "content_sha256": "c" * 64,
            "authentication_state": "AUTHENTICATED",
            "conflict_state": "CONFLICTED",
        }]
        # Freeze after both conflicting observations exist. A 15:30 snapshot
        # must not contain the 15:31 observation.
        row = build_project_memory(**base(source_observations=sources, frozen_at_utc="2026-09-23T15:32:00Z"))
        self.assertEqual(len(row["source_observations"]), 2)
        self.assertEqual(
            {x["content_sha256"] for x in row["source_observations"]},
            {"b" * 64, "c" * 64},
        )

    def test_supersession_is_append_only_and_same_trial(self):
        first = build_project_memory(**base())
        second = supersede_project_memory(
            first,
            frozen_at_utc="2026-09-23T16:00:00Z",
            material_delta={"state": "NEW_AUTHENTICATED_OBSERVATION"},
        )
        self.assertEqual(first["project_trial_id"], second["project_trial_id"])
        self.assertEqual(second["project_memory_before"], first)
        self.assertEqual(second["lineage"]["supersedes_snapshot_sha256"], first["snapshot_sha256"])

    def test_outcome_derived_discovery_is_rejected(self):
        with self.assertRaises(ProjectMemoryError):
            build_project_memory(**base(discovery={"source": "fixture", "outcome": "winner"}))

    def test_p1_cannot_grant_binding_or_trading_authority(self):
        with self.assertRaises(ProjectMemoryError):
            build_project_memory(**base(authority={"project_ca_binding": True}))
        with self.assertRaises(ProjectMemoryError):
            build_project_memory(**base(authority={"automatic_trading": True}))

    def test_ca_candidate_does_not_bind(self):
        row = build_project_memory(**base(
            token_state="TOKEN_CANDIDATE",
            ca_candidates=[{"chain_id": 1, "token_ca": "0x123", "source": "PONS_FACTORY"}],
        ))
        self.assertFalse(row["authority"]["project_ca_binding"])
        self.assertEqual(row["token_state"], "TOKEN_CANDIDATE")


class ProjectMemoryP1IndependentReviewTests(unittest.TestCase):
    """Independent-review regressions: temporal and hindsight hardening."""

    def later_source(self, observed="2026-09-23T15:31:00Z", available=None):
        return {
            "source_ref": "fixture:official",
            "observed_at_utc": observed,
            "available_at_utc": available,
            "content_sha256": "c" * 64,
            "authentication_state": "AUTHENTICATED",
            "conflict_state": "CONFLICTED",
        }

    def test_observation_after_freeze_cannot_enter_frozen_snapshot(self):
        sources = list(base()["source_observations"]) + [self.later_source()]
        with self.assertRaises(ProjectMemoryError):
            build_project_memory(**base(source_observations=sources))

    def test_availability_after_freeze_cannot_enter_frozen_snapshot(self):
        sources = [self.later_source(observed="2026-09-23T15:00:00Z", available="2026-09-23T16:00:00Z")]
        with self.assertRaises(ProjectMemoryError):
            build_project_memory(**base(source_observations=sources))

    def test_later_observation_is_admitted_through_append_only_supersession(self):
        first = build_project_memory(**base())
        second = supersede_project_memory(
            first,
            frozen_at_utc="2026-09-23T15:32:00Z",
            source_observations=list(first["source_observations"]) + [self.later_source()],
            material_delta={"state": "CONFLICTING_MUTABLE_SOURCE"},
        )
        self.assertEqual(len(second["source_observations"]), 2)
        self.assertEqual(second["lineage"]["supersedes_snapshot_sha256"], first["snapshot_sha256"])

    def test_backdated_supersession_is_rejected(self):
        first = build_project_memory(**base())
        with self.assertRaises(ProjectMemoryError):
            supersede_project_memory(first, frozen_at_utc="2026-09-23T15:00:00Z")

    def test_free_text_or_offset_timestamps_are_rejected(self):
        for value in ("yesterday", "2026-09-23T15:30:00+02:00"):
            with self.assertRaises(ProjectMemoryError):
                build_project_memory(**base(frozen_at_utc=value))
        bad = dict(base()["source_observations"][0], observed_at_utc="sometime")
        with self.assertRaises(ProjectMemoryError):
            build_project_memory(**base(source_observations=[bad]))

    def test_nested_outcome_fields_in_discovery_are_rejected(self):
        for discovery in (
            {"source": "fixture", "meta": {"outcome": "winner"}},
            {"source": "fixture", "signals": [{"mfe": 5.0}]},
        ):
            with self.assertRaises(ProjectMemoryError):
                build_project_memory(**base(discovery=discovery))

    def test_non_outcome_nested_discovery_is_still_accepted(self):
        row = build_project_memory(**base(discovery={"source": "fixture", "meta": {"channel": "official"}}))
        self.assertEqual(row["discovery"]["meta"]["channel"], "official")


if __name__ == "__main__":
    unittest.main()
