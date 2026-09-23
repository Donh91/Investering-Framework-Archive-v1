import copy
import hashlib
import json
import unittest

from scripts.api_agent.meme_alpha.project_memory_p1 import (
    append_observation, derive_project_trial_id, freeze_project_trial,
)

def h(x):
    return hashlib.sha256(x.encode()).hexdigest()

def source(ref, observed, body, auth="AUTHENTICATED_FIRST_PARTY", available=None):
    return {
        "source_family": "FIRST_PARTY_WEB_DOCS_APP",
        "source_ref": ref,
        "observed_at_utc": observed,
        "available_at_utc": available or observed,
        "content_sha256": h(body),
        "authentication_state": auth,
        "source_health": "HEALTHY_NONEMPTY",
        "claims": {"body": body},
    }

class ProjectMemoryP1Tests(unittest.TestCase):
    def identity(self, name="8-Ball", aliases=None):
        return {
            "display_name": name,
            "aliases": aliases or [],
            "ticker": "BALL",
            "logo_ref": "non-authoritative",
            "control_roots": [{"kind": "OFFICIAL_WEBSITE", "value": "https://example.invalid/project"}],
        }

    def test_8ball_no_token_persists_without_outcome(self):
        row = freeze_project_trial(
            frozen_at_utc="2026-09-23T15:00:00Z",
            eligibility_manifest_sha256=h("manifest"),
            discovery={"source": "ecosystem-directory", "first_seen_utc": "2026-09-23T14:59:00Z"},
            project_identity=self.identity(),
            source_observations=[source("official", "2026-09-23T14:59:00Z", "serious project, no token")],
        )
        self.assertEqual(row["token_state"], "NO_TOKEN_OBSERVED")
        self.assertNotIn("outcome", row)
        self.assertFalse(row["authority"]["project_to_ca_binding"])

    def test_alias_and_order_do_not_create_second_trial(self):
        a = self.identity(aliases=["Eight Ball", "8Ball"])
        b = self.identity(name="renamed display", aliases=["8Ball", "Eight Ball", "new alias"])
        b["control_roots"] = list(reversed(b["control_roots"]))
        self.assertEqual(derive_project_trial_id(a), derive_project_trial_id(b))

    def test_alias_name_ticker_logo_alone_cannot_establish_identity(self):
        with self.assertRaises(ValueError):
            derive_project_trial_id({"display_name": "copied", "ticker": "COPY", "aliases": ["real"]})

    def test_hoodstack_conflicting_mutable_sources_are_preserved(self):
        first = freeze_project_trial(
            frozen_at_utc="2026-09-23T15:00:00Z",
            eligibility_manifest_sha256=h("manifest"),
            discovery={"first_seen_utc": "2026-09-23T14:00:00Z"},
            project_identity=self.identity(name="HoodStack"),
            source_observations=[source("docs", "2026-09-23T14:00:00Z", "CA=A")],
        )
        frozen_copy = copy.deepcopy(first)
        second = append_observation(
            first,
            frozen_at_utc="2026-09-23T16:00:00Z",
            source_observations=[source("docs", "2026-09-23T15:55:00Z", "CA=B", auth="CONFLICTED")],
            token_state="TOKEN_CONFLICT",
            ca_candidates=[{"chain_id": "robinhood", "token_ca": "A"}, {"chain_id": "robinhood", "token_ca": "B"}],
            material_delta={"class": "AUTHENTICATED_CONTRADICTION", "state": "CONFLICTED"},
        )
        self.assertEqual(first, frozen_copy)
        self.assertEqual(len(second["source_observations"]), 2)
        self.assertEqual(second["token_state"], "TOKEN_CONFLICT")
        self.assertEqual(second["lineage"]["supersedes_snapshot_sha256"], first["snapshot_sha256"])
        self.assertFalse(second["authority"]["project_to_ca_binding"])

    def test_missing_available_at_is_preserved_unknown_not_zero(self):
        s = source("repo", "2026-09-23T14:00:00Z", "x")
        s["available_at_utc"] = None
        row = freeze_project_trial(
            frozen_at_utc="2026-09-23T15:00:00Z",
            eligibility_manifest_sha256=h("manifest"),
            discovery={},
            project_identity=self.identity(),
            source_observations=[s],
        )
        self.assertIsNone(row["source_observations"][0]["available_at_utc"])

if __name__ == "__main__":
    unittest.main()
