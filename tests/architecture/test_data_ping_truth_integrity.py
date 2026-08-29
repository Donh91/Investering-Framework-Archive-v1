from __future__ import annotations

import hashlib
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.data_ping import truth_integrity as integrity


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = json.loads(
    (ROOT / "tests/fixtures/data_ping_1552/2026-08-28_incidents.json").read_text()
)
PINNED_SHA = "a" * 40
ADVANCED_SHA = "b" * 40
NOW = datetime(2026, 8, 28, 19, 53, 22, tzinfo=timezone.utc)


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


class FakeRepository:
    def __init__(self, values, *, observed_commit=PINNED_SHA):
        self.values = values
        self.observed_commit = observed_commit
        self.requested_refs = []

    def read(self, path, commit_sha):
        self.requested_refs.append(commit_sha)
        if path not in self.values:
            raise FileNotFoundError(path)
        value = self.values[path]
        raw = value if isinstance(value, bytes) else integrity.canonical_json(value)
        return integrity.GitHubObject(
            path=path,
            commit_sha=self.observed_commit,
            raw=raw,
            git_blob_sha=git_blob_sha(raw),
        )


def daily_values():
    incident = FIXTURE["live_anchor"]
    return {
        "03_DAILY_CAPTURE_LOGS/captures/LATEST.json": incident["pinned_pointer"],
        "03_DAILY_CAPTURE_LOGS/captures/2026/08/28/163419_gh-33190569765-1.json": incident["pinned_target"],
    }


class IncidentRegressionTests(unittest.TestCase):
    def snapshot(self, values=None, *, observed_commit=PINNED_SHA):
        repository = FakeRepository(daily_values() if values is None else values, observed_commit=observed_commit)
        resolves = []

        def resolve():
            resolves.append(PINNED_SHA)
            return PINNED_SHA

        return integrity.PinnedGitHubSnapshot.open("Donh91/Investering-Framework-Archive-v1", resolve, repository.read), repository, resolves

    def test_20260828_pinned_live_anchor_selects_163419_target(self):
        snapshot, repository, resolves = self.snapshot()
        result = integrity.resolve_pointer_chain(
            snapshot,
            "03_DAILY_CAPTURE_LOGS/captures/LATEST.json",
            integrity.DAILY_POINTER,
            now_utc=NOW,
        )
        self.assertEqual(result["target"]["captured_at_utc"], "2026-08-28T16:34:19Z")
        self.assertEqual(result["run_id"], "gh-33190569765-1")
        self.assertEqual(result["freshness"]["contract"], "DATA_PING_MULTI_DIMENSIONAL_FRESHNESS_v1")
        self.assertEqual(result["freshness"]["retrieval_freshness"]["timestamp"], "2026-08-28T16:34:19Z")
        self.assertEqual(result["freshness"]["source_observation_freshness"]["status"], "UNAVAILABLE")
        self.assertEqual(resolves, [PINNED_SHA])
        self.assertEqual(set(repository.requested_refs), {PINNED_SHA})

    def test_stale_112427_cached_latest_conflicts_with_pinned_pointer(self):
        with self.assertRaisesRegex(integrity.IntegrityError, "GITHUB_POINTER_CONFLICT"):
            integrity.validate_cached_pointer(
                FIXTURE["live_anchor"]["pinned_pointer"],
                FIXTURE["live_anchor"]["stale_cached_pointer"],
            )

    def test_identical_cached_pointer_is_accepted(self):
        result = integrity.validate_cached_pointer(
            FIXTURE["live_anchor"]["pinned_pointer"],
            dict(FIXTURE["live_anchor"]["pinned_pointer"]),
        )
        self.assertEqual(result["status"], "PASS")

    def test_main_advance_after_resolution_cannot_change_read_ref(self):
        snapshot, repository, resolves = self.snapshot()
        current_main = [PINNED_SHA]

        def changing_resolver():
            current_main[0] = ADVANCED_SHA
            return PINNED_SHA

        snapshot = integrity.PinnedGitHubSnapshot.open(
            "Donh91/Investering-Framework-Archive-v1", changing_resolver, repository.read
        )
        integrity.resolve_pointer_chain(
            snapshot, "03_DAILY_CAPTURE_LOGS/captures/LATEST.json", integrity.DAILY_POINTER, now_utc=NOW
        )
        self.assertEqual(current_main[0], ADVANCED_SHA)
        self.assertEqual(set(repository.requested_refs), {PINNED_SHA})
        self.assertEqual(snapshot.consistency()["resolution_count"], 1)

    def test_mixed_snapshot_reader_fails_closed(self):
        snapshot, _, _ = self.snapshot(observed_commit=ADVANCED_SHA)
        with self.assertRaisesRegex(integrity.IntegrityError, "GITHUB_MIXED_SNAPSHOT"):
            snapshot.read_json("03_DAILY_CAPTURE_LOGS/captures/LATEST.json")

    def test_pointer_target_run_mismatch_fails_closed(self):
        values = daily_values()
        values["03_DAILY_CAPTURE_LOGS/captures/2026/08/28/163419_gh-33190569765-1.json"] = {
            **values["03_DAILY_CAPTURE_LOGS/captures/2026/08/28/163419_gh-33190569765-1.json"],
            "run_id": "different-run",
        }
        snapshot, _, _ = self.snapshot(values)
        with self.assertRaisesRegex(integrity.IntegrityError, "run_id_mismatch"):
            integrity.resolve_pointer_chain(
                snapshot, "03_DAILY_CAPTURE_LOGS/captures/LATEST.json", integrity.DAILY_POINTER, now_utc=NOW
            )

    def test_missing_pointer_target_fails_closed(self):
        snapshot, _, _ = self.snapshot({"03_DAILY_CAPTURE_LOGS/captures/LATEST.json": FIXTURE["live_anchor"]["pinned_pointer"]})
        with self.assertRaisesRegex(integrity.IntegrityError, "GITHUB_SOURCE_READ_FAIL"):
            integrity.resolve_pointer_chain(
                snapshot, "03_DAILY_CAPTURE_LOGS/captures/LATEST.json", integrity.DAILY_POINTER, now_utc=NOW
            )

    def test_future_pointer_timestamp_fails_closed(self):
        values = daily_values()
        values["03_DAILY_CAPTURE_LOGS/captures/LATEST.json"] = {
            **values["03_DAILY_CAPTURE_LOGS/captures/LATEST.json"], "captured_at_utc": "2026-08-29T00:00:00Z"
        }
        target_path = "03_DAILY_CAPTURE_LOGS/captures/2026/08/28/163419_gh-33190569765-1.json"
        values[target_path] = {**values[target_path], "captured_at_utc": "2026-08-29T00:00:00Z"}
        snapshot, _, _ = self.snapshot(values)
        with self.assertRaisesRegex(integrity.IntegrityError, "future_pointer_timestamp"):
            integrity.resolve_pointer_chain(
                snapshot, "03_DAILY_CAPTURE_LOGS/captures/LATEST.json", integrity.DAILY_POINTER, now_utc=NOW
            )

    def test_stale_pointer_with_fresh_target_is_conflict(self):
        values = daily_values()
        values["03_DAILY_CAPTURE_LOGS/captures/LATEST.json"] = FIXTURE["live_anchor"]["stale_cached_pointer"]
        values["03_DAILY_CAPTURE_LOGS/captures/2026/08/28/112427_gh-stale-1.json"] = FIXTURE["live_anchor"]["pinned_target"]
        snapshot, _, _ = self.snapshot(values)
        with self.assertRaisesRegex(integrity.IntegrityError, "run_id_mismatch|timestamp_mismatch"):
            integrity.resolve_pointer_chain(
                snapshot, "03_DAILY_CAPTURE_LOGS/captures/LATEST.json", integrity.DAILY_POINTER, now_utc=NOW
            )

    def test_fresh_pointer_with_stale_target_is_conflict(self):
        values = daily_values()
        target_path = "03_DAILY_CAPTURE_LOGS/captures/2026/08/28/163419_gh-33190569765-1.json"
        values[target_path] = {
            **values[target_path], "captured_at_utc": "2026-08-28T11:24:27Z"
        }
        snapshot, _, _ = self.snapshot(values)
        with self.assertRaisesRegex(integrity.IntegrityError, "timestamp_mismatch"):
            integrity.resolve_pointer_chain(
                snapshot, "03_DAILY_CAPTURE_LOGS/captures/LATEST.json", integrity.DAILY_POINTER, now_utc=NOW
            )

    def test_pointer_chain_replay_is_deterministic(self):
        first, _, _ = self.snapshot()
        second, _, _ = self.snapshot()
        left = integrity.resolve_pointer_chain(
            first, "03_DAILY_CAPTURE_LOGS/captures/LATEST.json", integrity.DAILY_POINTER, now_utc=NOW
        )
        right = integrity.resolve_pointer_chain(
            second, "03_DAILY_CAPTURE_LOGS/captures/LATEST.json", integrity.DAILY_POINTER, now_utc=NOW
        )
        self.assertEqual(integrity.normalized_sha256(left), integrity.normalized_sha256(right))

    def test_partial_github_source_failure_has_explicit_classification(self):
        snapshot, _, _ = self.snapshot({})
        with self.assertRaises(integrity.IntegrityError) as caught:
            snapshot.read_json("03_DAILY_CAPTURE_LOGS/captures/LATEST.json")
        self.assertEqual(caught.exception.classification, "GITHUB_SOURCE_READ_FAIL")

    def test_etf_26_aug_is_rejected_when_27_aug_is_final(self):
        etf = FIXTURE["etf"]
        with self.assertRaisesRegex(integrity.IntegrityError, "ETF_SESSION_LAG"):
            integrity.validate_latest_eligible_etf_session(etf["history_rows"], etf["stale_selected_rows"])

    def test_etf_27_aug_final_is_selected(self):
        etf = FIXTURE["etf"]
        result = integrity.validate_latest_eligible_etf_session(etf["history_rows"], etf["correct_selected_rows"])
        self.assertEqual(result["latest_eligible_settled_session"], "2026-08-27")
        self.assertEqual(result["session_lag_days"], 0)

    def test_newer_not_final_etf_session_does_not_displace_final_session(self):
        etf = json.loads(json.dumps(FIXTURE["etf"]))
        for asset in ("BTC", "ETH"):
            etf["history_rows"][asset].append({
                "asset": asset, "date": "2026-08-28", "reported_total": 1.0,
                "session_final": False, "total_parity": True,
            })
        result = integrity.validate_latest_eligible_etf_session(etf["history_rows"], etf["correct_selected_rows"])
        self.assertEqual(result["selected_session_date"], "2026-08-27")

    def test_btc_oi_factor_ten_absolute_delta_is_rejected(self):
        delta = FIXTURE["btc_oi_delta"]
        with self.assertRaisesRegex(integrity.IntegrityError, "DELTA_INTEGRITY_FAIL"):
            integrity.validate_delta(
                current=delta["current"], predecessor=delta["predecessor"],
                reported_absolute_delta=delta["reported_wrong_absolute_delta"],
                reported_pct_delta=delta["correct_pct_delta"],
            )

    def test_btc_oi_correct_delta_and_pct_pass(self):
        delta = FIXTURE["btc_oi_delta"]
        result = integrity.validate_delta(
            current=delta["current"], predecessor=delta["predecessor"],
            reported_absolute_delta=delta["correct_absolute_delta"],
            reported_pct_delta=delta["correct_pct_delta"],
            current_context=delta["unit_context"], predecessor_context=dict(delta["unit_context"]),
        )
        self.assertAlmostEqual(result["absolute_delta"], 5_136_260.919032097)
        self.assertAlmostEqual(result["pct_delta"], 0.22661544162032587)

    def test_wrong_pct_delta_is_rejected_even_when_absolute_is_right(self):
        delta = FIXTURE["btc_oi_delta"]
        with self.assertRaisesRegex(integrity.IntegrityError, "PCT_DELTA_MISMATCH"):
            integrity.validate_delta(
                current=delta["current"], predecessor=delta["predecessor"],
                reported_absolute_delta=delta["correct_absolute_delta"], reported_pct_delta=2.266154416,
            )

    def test_incompatible_predecessor_is_rejected(self):
        delta = FIXTURE["btc_oi_delta"]
        incompatible = {**delta["unit_context"], "venue": "DIFFERENT_OWNER"}
        with self.assertRaisesRegex(integrity.IntegrityError, "DELTA_PREDECESSOR_INCOMPATIBLE"):
            integrity.validate_delta(
                current=delta["current"], predecessor=delta["predecessor"],
                reported_absolute_delta=delta["correct_absolute_delta"], reported_pct_delta=delta["correct_pct_delta"],
                current_context=delta["unit_context"], predecessor_context=incompatible,
            )

    def test_delta_block_degrades_only_failed_optional_item(self):
        block = integrity.validate_delta_block([
            {"current": 2.0, "predecessor": 1.0, "reported_absolute_delta": 1.0, "reported_pct_delta": 100.0},
            {"current": 2.0, "predecessor": 1.0, "reported_absolute_delta": 10.0, "reported_pct_delta": 100.0},
        ])
        self.assertEqual(block["status"], "DEGRADED")
        self.assertEqual(block["validated_count"], 1)
        self.assertEqual(block["failure_count"], 1)

    def test_freshness_dimensions_remain_distinct(self):
        result = integrity.freshness_vector(
            now_utc=NOW,
            policy=integrity.FreshnessPolicy(
                "TEST_CADENCE", retrieval_max_age=timedelta(hours=1),
                source_observation_max_age=timedelta(days=2), pointer_max_age=timedelta(hours=1),
                coverage_max_lag=timedelta(days=1),
            ),
            retrieval_timestamp="2026-08-28T19:30:00Z",
            source_observation_timestamp="2026-08-27T19:30:00Z",
            pointer_timestamp="2026-08-28T18:00:00Z",
            coverage_timestamp="2026-08-28T19:00:00Z",
        )
        self.assertEqual(result["retrieval_freshness"]["status"], "PASS")
        self.assertEqual(result["source_observation_freshness"]["status"], "PASS")
        self.assertEqual(result["pointer_freshness"]["status"], "STALE")
        self.assertEqual(result["status"], "FAIL")

    def test_missing_freshness_policy_is_not_silently_passed(self):
        result = integrity.freshness_vector(
            now_utc=NOW, policy=integrity.FreshnessPolicy("OWNER_CONTRACT_REQUIRED"),
            retrieval_timestamp="2026-08-28T19:30:00Z",
        )
        self.assertEqual(result["status"], "UNCONFIRMED_POLICY")
        self.assertEqual(result["retrieval_freshness"]["status"], "POLICY_UNAVAILABLE")

    def test_absent_freshness_evidence_is_unavailable_not_pass(self):
        result = integrity.freshness_vector(
            now_utc=NOW, policy=integrity.FreshnessPolicy("OWNER_CONTRACT_REQUIRED")
        )
        self.assertEqual(result["status"], "UNAVAILABLE")

    def test_hash_semantics_distinguish_request_raw_normalized_and_blob(self):
        snapshot, _, _ = self.snapshot()
        _, provenance = snapshot.read_json("03_DAILY_CAPTURE_LOGS/captures/LATEST.json")
        self.assertRegex(provenance["request_arguments_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(provenance["raw_response_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(provenance["normalized_payload_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(provenance["git_blob_sha"], r"^[0-9a-f]{40}$")
        self.assertNotEqual(provenance["request_arguments_sha256"], provenance["raw_response_sha256"])

    def test_fresh_pinned_macro_owner_avoids_three_fallback_calls(self):
        result = integrity.select_macro_evidence(
            {"DGS2": 3.1, "DGS10": 4.0, "VIX": 18.2}, owner_authority_valid=True,
            owner_snapshot_commit_sha=PINNED_SHA, expected_snapshot_commit_sha=PINNED_SHA,
            retrieval_freshness_status="PASS", source_observation_freshness_status="PASS",
        )
        self.assertEqual(result["status"], "OWNER_REUSE")
        self.assertEqual(result["external_calls_avoided"], 3)

    def test_stale_macro_owner_requires_existing_fallback(self):
        result = integrity.select_macro_evidence(
            {"DGS2": 3.1, "DGS10": 4.0, "VIX": 18.2}, owner_authority_valid=True,
            owner_snapshot_commit_sha=PINNED_SHA, expected_snapshot_commit_sha=PINNED_SHA,
            retrieval_freshness_status="PASS", source_observation_freshness_status="STALE",
        )
        self.assertEqual(result["status"], "DIRECT_FALLBACK_REQUIRED")
        self.assertIn("SOURCE_OBSERVATION_FRESHNESS_NOT_PASS", result["reasons"])


class DeterministicPropertyChecks(unittest.TestCase):
    """One hundred separately counted deterministic adversarial/property checks."""


def _property_case(index):
    def check(self):
        if index < 40:
            predecessor = (index + 1) * (10.0 ** ((index % 7) - 3))
            multiplier = 1.0 + ((index % 9) - 4) / 100.0
            current = predecessor * multiplier
            expected_absolute = current - predecessor
            expected_pct = (current / predecessor - 1.0) * 100.0
            result = integrity.validate_delta(
                current=current, predecessor=predecessor,
                reported_absolute_delta=expected_absolute, reported_pct_delta=expected_pct,
            )
            self.assertEqual(result["status"], "PASS")
        elif index < 60:
            predecessor = 1000.0 + index
            current = predecessor * 1.01
            with self.assertRaises(integrity.IntegrityError) as caught:
                integrity.validate_delta(
                    current=current, predecessor=predecessor,
                    reported_absolute_delta=(current - predecessor) + (index - 39) * 0.01,
                    reported_pct_delta=1.0,
                )
            self.assertEqual(caught.exception.classification, "DELTA_INTEGRITY_FAIL")
        elif index < 80:
            predecessor = 500.0 + index
            current = predecessor * 0.99
            with self.assertRaises(integrity.IntegrityError) as caught:
                integrity.validate_delta(
                    current=current, predecessor=predecessor,
                    reported_absolute_delta=current - predecessor,
                    reported_pct_delta=-1.0 + (index - 59) * 0.01,
                )
            self.assertEqual(caught.exception.classification, "DELTA_INTEGRITY_FAIL")
        elif index < 90:
            seconds = index - 80
            policy = integrity.FreshnessPolicy("BOUNDARY", retrieval_max_age=timedelta(seconds=seconds))
            result = integrity.freshness_vector(
                now_utc=NOW, policy=policy,
                retrieval_timestamp=(NOW - timedelta(seconds=seconds)).isoformat().replace("+00:00", "Z"),
            )
            self.assertEqual(result["retrieval_freshness"]["status"], "PASS")
        else:
            value = {"case": index, "nested": {"a": 1, "b": 2}}
            reordered = {"nested": {"b": 2, "a": 1}, "case": index}
            mutated = {"case": index + 1, "nested": {"a": 1, "b": 2}}
            self.assertEqual(integrity.normalized_sha256(value), integrity.normalized_sha256(reordered))
            self.assertNotEqual(integrity.normalized_sha256(value), integrity.normalized_sha256(mutated))
    return check


for _index in range(100):
    setattr(DeterministicPropertyChecks, f"test_adversarial_property_{_index:03d}", _property_case(_index))


if __name__ == "__main__":
    unittest.main()
