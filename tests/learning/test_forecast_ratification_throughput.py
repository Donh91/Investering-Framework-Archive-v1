from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
sys.path.insert(0, str(ROOT / "scripts" / "learning"))

from forecast_ratification_contract import CUTOVER_COMMIT_SHA  # noqa: E402
from build_forecast_ratification_queue import build_queue  # noqa: E402
from process_forecast_ratifications import process  # noqa: E402

UTC = timezone.utc


def canon(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value):
    return hashlib.sha256(canon(value)).hexdigest()


class ForecastRatificationThroughputTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=self.repo, check=True)
        self.pending = self.repo / "research/api_agent/forecast_candidates/PENDING"
        self.packets = self.repo / "research/api_agent/forecast_candidates/RATIFICATION_INBOX"
        self.terminals = self.repo / "research/api_agent/forecast_candidates/RATIFICATION_TERMINAL"
        self.frozen = self.repo / "research/api_agent/forecast_candidates/FROZEN"
        self.captures = self.repo / "03_DAILY_CAPTURE_LOGS/captures"
        for path in (self.pending, self.packets, self.terminals, self.frozen, self.captures):
            path.mkdir(parents=True, exist_ok=True)
        self.addCleanup(self.tmp.cleanup)

    def commit(self, message: str, when: str):
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        env = dict(os.environ)
        env["GIT_AUTHOR_DATE"] = when
        env["GIT_COMMITTER_DATE"] = when
        subprocess.run(["git", "commit", "-qm", message], cwd=self.repo, check=True, env=env)

    def candidate(self, cid="new-1", created="2026-09-02T10:10:00Z"):
        return {
            "contract": "FORECAST_CANDIDATE_v1",
            "authority": "UNRATIFIED_RESEARCH_ONLY",
            "candidate_id": cid,
            "created_at_utc": created,
            "model": "gpt-5.6-luna",
            "task": "DAILY_DIRECTOR_SHADOW",
            "prompt_sha256": "a" * 64,
            "context_sha256": "b" * 64,
            "source_output_sha256": "c" * 64,
            "candidate": {
                "metric_path": "derivatives.BTC-USDT-SWAP.mark_price.mark_price",
                "direction": "UP",
                "target_mode": "PCT_MOVE",
                "threshold_pct": 1.0,
                "target_value": None,
                "range_low": None,
                "range_high": None,
                "horizon_days": 1,
                "rationale": "prospective fixture",
            },
            "ratification_status": "PENDING",
            "self_promotion_allowed": False,
        }

    def packet(self, candidate, decision="RATIFY", decision_at="2026-09-02T10:20:00Z"):
        return {
            "contract": "FORECAST_RATIFICATION_PACKET_v2",
            "candidate_id": candidate["candidate_id"],
            "candidate_sha256": digest(candidate),
            "decision": decision,
            "decision_at_utc": decision_at,
            "authority": "CHATGPT_FRAMEWORK_OWNER",
            "owner_actor": "GPT-5.6 Sol",
            "outcome_blind": True,
            "self_promotion_allowed": False,
            "prospective_cutover_commit_sha": CUTOVER_COMMIT_SHA,
            "decision_basis_scope": ["RATIFICATION_QUEUE", "CANDIDATE_RECORD"],
            "outcome_paths_read": [],
            "decision_rationale": "Independent owner decision based only on the frozen candidate and ratification queue.",
        }

    def write_candidate(self, candidate):
        path = self.pending / "2026/09/02" / f"{candidate['candidate_id']}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(canon(candidate))
        return path

    def write_capture(self, name, observed, value):
        path = self.captures / "2026/09/02" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "captured_at_utc": observed,
            "market_metrics": {
                "derivatives": {
                    "BTC-USDT-SWAP": {"mark_price": {"mark_price": value}}
                }
            },
        }
        path.write_bytes(canon(payload))
        return path, payload

    def write_packet(self, packet, relative=None):
        path = self.packets / (relative or f"{packet['candidate_id']}.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(canon(packet))
        return path

    def test_ratify_freezes_at_owner_decision_and_uses_last_predecision_baseline(self):
        candidate = self.candidate()
        self.write_candidate(candidate)
        before_path, before = self.write_capture("before.json", "2026-09-02T10:19:00Z", 100.0)
        self.write_capture("after.json", "2026-09-02T10:21:00Z", 200.0)
        self.commit("candidate and captures", "2026-09-02T10:19:30Z")
        packet = self.packet(candidate)
        self.write_packet(packet)
        self.commit("ratification packet", "2026-09-02T10:21:00Z")

        result = process(
            self.pending, self.packets, self.terminals, self.frozen, self.captures, self.repo,
            datetime(2026, 9, 2, 10, 30, tzinfo=UTC),
        )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["counts"]["RATIFIED_AND_FROZEN"], 1)
        frozen_files = list(self.frozen.glob("*.json"))
        self.assertEqual(len(frozen_files), 1)
        frozen = json.loads(frozen_files[0].read_text())
        self.assertEqual(frozen["frozen_at_utc"], "2026-09-02T10:20:00Z")
        self.assertEqual(frozen["outcome_due_utc"], "2026-09-03T10:20:00Z")
        self.assertEqual(frozen["start_value"], 100.0)
        self.assertEqual(frozen["baseline_evidence_sha256"], digest(before))
        self.assertEqual(Path(frozen["baseline_evidence_path"]), before_path)
        self.assertEqual(frozen["settlement_contract_version"], "FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1")
        self.assertEqual(frozen["settlement_activation_semantics"], "FROZEN_AT_RATIFICATION_DECISION_PROSPECTIVE_ONLY")
        terminal = json.loads((self.terminals / "new-1.json").read_text())
        self.assertEqual(terminal["disposition"], "RATIFIED_AND_FROZEN")
        self.assertEqual(terminal["baseline"]["selection_semantics"], "LATEST_IMMUTABLE_ARCHIVED_CAPTURE_AT_OR_BEFORE_OWNER_DECISION")
        self.assertFalse(terminal["outcome_data_read"])

    def test_reject_is_terminal_and_creates_no_forecast(self):
        candidate = self.candidate(cid="reject-1")
        self.write_candidate(candidate)
        self.commit("candidate", "2026-09-02T10:11:00Z")
        packet = self.packet(candidate, decision="REJECT")
        self.write_packet(packet)
        self.commit("reject packet", "2026-09-02T10:21:00Z")
        result = process(
            self.pending, self.packets, self.terminals, self.frozen, self.captures, self.repo,
            datetime(2026, 9, 2, 10, 30, tzinfo=UTC),
        )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["counts"]["REJECTED_BY_OWNER"], 1)
        self.assertEqual(list(self.frozen.glob("*.json")), [])
        self.assertEqual(json.loads((self.terminals / "reject-1.json").read_text())["disposition"], "REJECTED_BY_OWNER")

    def test_pre_cutover_candidate_is_hindsight_ineligible_even_without_packet(self):
        candidate = self.candidate(cid="legacy-1", created="2026-09-01T23:34:00Z")
        self.write_candidate(candidate)
        self.commit("legacy candidate", "2026-09-01T23:35:00Z")
        result = process(
            self.pending, self.packets, self.terminals, self.frozen, self.captures, self.repo,
            datetime(2026, 9, 2, 11, 0, tzinfo=UTC),
        )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["counts"]["LEGACY_PRE_CUTOVER_HINDSIGHT_INELIGIBLE"], 1)
        self.assertEqual(json.loads((self.terminals / "legacy-1.json").read_text())["disposition"], "LEGACY_PRE_CUTOVER_HINDSIGHT_INELIGIBLE")

    def test_missing_owner_decision_expires_after_sla(self):
        candidate = self.candidate(cid="expire-1")
        self.write_candidate(candidate)
        self.commit("candidate", "2026-09-02T10:11:00Z")
        result = process(
            self.pending, self.packets, self.terminals, self.frozen, self.captures, self.repo,
            datetime(2026, 9, 2, 11, 11, tzinfo=UTC),
        )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["counts"]["EXPIRED_NO_OWNER_DECISION"], 1)
        self.assertEqual(json.loads((self.terminals / "expire-1.json").read_text())["disposition"], "EXPIRED_NO_OWNER_DECISION")

    def test_expired_candidate_cannot_be_resurrected_by_late_ratification(self):
        candidate = self.candidate(cid="expired-lock")
        self.write_candidate(candidate)
        self.commit("candidate", "2026-09-02T10:11:00Z")
        expired_at = datetime(2026, 9, 2, 11, 11, tzinfo=UTC)
        first = process(self.pending, self.packets, self.terminals, self.frozen, self.captures, self.repo, expired_at)
        self.assertEqual(first["counts"]["EXPIRED_NO_OWNER_DECISION"], 1)
        before = (self.terminals / "expired-lock.json").read_bytes()
        late_packet = self.packet(candidate, decision="RATIFY", decision_at="2026-09-02T10:20:00Z")
        self.write_packet(late_packet)
        self.commit("late ratification after terminal expiry", "2026-09-02T11:12:00Z")
        second = process(
            self.pending, self.packets, self.terminals, self.frozen, self.captures, self.repo,
            datetime(2026, 9, 2, 11, 13, tzinfo=UTC),
        )
        self.assertEqual(second["status"], "PASS")
        self.assertEqual(second["counts"]["ALREADY_TERMINAL"], 1)
        self.assertEqual((self.terminals / "expired-lock.json").read_bytes(), before)
        self.assertEqual(list(self.frozen.glob("*.json")), [])

    def test_rejected_candidate_cannot_be_resurrected_by_packet_mutation(self):
        candidate = self.candidate(cid="reject-lock")
        self.write_candidate(candidate)
        self.commit("candidate", "2026-09-02T10:11:00Z")
        rejected = self.packet(candidate, decision="REJECT")
        packet_path = self.write_packet(rejected)
        self.commit("reject packet", "2026-09-02T10:21:00Z")
        first = process(
            self.pending, self.packets, self.terminals, self.frozen, self.captures, self.repo,
            datetime(2026, 9, 2, 10, 30, tzinfo=UTC),
        )
        self.assertEqual(first["counts"]["REJECTED_BY_OWNER"], 1)
        before = (self.terminals / "reject-lock.json").read_bytes()
        changed = self.packet(candidate, decision="RATIFY", decision_at="2026-09-02T10:20:00Z")
        packet_path.write_bytes(canon(changed))
        self.commit("attempt packet decision mutation", "2026-09-02T10:31:00Z")
        second = process(
            self.pending, self.packets, self.terminals, self.frozen, self.captures, self.repo,
            datetime(2026, 9, 2, 10, 32, tzinfo=UTC),
        )
        self.assertEqual(second["status"], "PASS")
        self.assertEqual(second["counts"]["ALREADY_TERMINAL"], 1)
        self.assertEqual((self.terminals / "reject-lock.json").read_bytes(), before)
        self.assertEqual(list(self.frozen.glob("*.json")), [])

    def test_backdated_candidate_created_at_fails_closed(self):
        candidate = self.candidate(cid="candidate-late")
        self.write_candidate(candidate)
        self.commit("candidate recorded too late", "2026-09-02T10:30:00Z")
        result = process(
            self.pending, self.packets, self.terminals, self.frozen, self.captures, self.repo,
            datetime(2026, 9, 2, 11, 11, tzinfo=UTC),
        )
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("CANDIDATE_CREATED_AT_BACKDATED_OR_LATE_RECORDED", result["errors"][0]["error"])
        self.assertEqual(list(self.terminals.glob("*.json")), [])

    def test_decision_cannot_precede_candidate_git_visibility(self):
        candidate = self.candidate(cid="visibility-1")
        self.write_candidate(candidate)
        self.commit("candidate", "2026-09-02T10:19:00Z")
        packet = self.packet(candidate, decision_at="2026-09-02T10:12:00Z")
        self.write_packet(packet)
        self.commit("packet", "2026-09-02T10:20:00Z")
        result = process(
            self.pending, self.packets, self.terminals, self.frozen, self.captures, self.repo,
            datetime(2026, 9, 2, 10, 21, tzinfo=UTC),
        )
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("RATIFICATION_PRECEDES_CANDIDATE_GIT_RECORD", result["errors"][0]["error"])

    def test_backdated_packet_fails_closed(self):
        candidate = self.candidate(cid="late-1")
        self.write_candidate(candidate)
        self.commit("candidate", "2026-09-02T10:11:00Z")
        packet = self.packet(candidate, decision_at="2026-09-02T10:20:00Z")
        self.write_packet(packet)
        self.commit("late packet", "2026-09-02T10:50:00Z")
        result = process(
            self.pending, self.packets, self.terminals, self.frozen, self.captures, self.repo,
            datetime(2026, 9, 2, 10, 55, tzinfo=UTC),
        )
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("RATIFICATION_PACKET_BACKDATED_OR_LATE_RECORDED", result["errors"][0]["error"])
        self.assertEqual(list(self.terminals.glob("*.json")), [])

    def test_packet_cannot_claim_outcome_blindness_with_outcome_paths(self):
        candidate = self.candidate(cid="leak-1")
        self.write_candidate(candidate)
        self.commit("candidate", "2026-09-02T10:11:00Z")
        packet = self.packet(candidate, decision="REJECT")
        packet["outcome_paths_read"] = ["research/api_agent/forecast_candidates/MATURED/ff.json"]
        self.write_packet(packet)
        self.commit("invalid leaking packet", "2026-09-02T10:21:00Z")
        with self.assertRaisesRegex(ValueError, "RATIFICATION_OUTCOME_PATHS_MUST_BE_EMPTY"):
            process(
                self.pending, self.packets, self.terminals, self.frozen, self.captures, self.repo,
                datetime(2026, 9, 2, 10, 30, tzinfo=UTC),
            )

    def test_multiple_packets_for_same_candidate_fail_closed(self):
        candidate = self.candidate(cid="multi-packet")
        self.write_candidate(candidate)
        self.commit("candidate", "2026-09-02T10:11:00Z")
        packet = self.packet(candidate, decision="REJECT")
        self.write_packet(packet, "a/multi-packet.json")
        self.write_packet(packet, "b/multi-packet.json")
        self.commit("duplicate packets", "2026-09-02T10:21:00Z")
        with self.assertRaisesRegex(ValueError, "MULTIPLE_RATIFICATION_PACKETS"):
            process(
                self.pending, self.packets, self.terminals, self.frozen, self.captures, self.repo,
                datetime(2026, 9, 2, 10, 30, tzinfo=UTC),
            )

    def test_queue_is_outcome_free_and_only_shows_live_post_cutover_candidates(self):
        legacy = self.candidate(cid="legacy-q", created="2026-09-01T23:34:00Z")
        live = self.candidate(cid="live-q", created="2026-09-02T10:10:00Z")
        self.write_candidate(legacy)
        self.write_candidate(live)
        queue = build_queue(self.pending, self.terminals, datetime(2026, 9, 2, 10, 20, tzinfo=UTC))
        self.assertFalse(queue["outcome_data_included"])
        self.assertEqual(queue["outcome_paths_read"], [])
        self.assertEqual(queue["counts"]["legacy_pre_cutover"], 1)
        self.assertEqual(queue["counts"]["decision_required"], 1)
        self.assertEqual(queue["candidates"][0]["candidate_id"], "live-q")
        self.assertFalse(queue["candidates"][0]["outcome_data_included"])

    def test_terminalization_is_idempotent(self):
        candidate = self.candidate(cid="idem-1", created="2026-09-01T23:34:00Z")
        self.write_candidate(candidate)
        self.commit("legacy candidate", "2026-09-01T23:35:00Z")
        now = datetime(2026, 9, 2, 11, 0, tzinfo=UTC)
        first = process(self.pending, self.packets, self.terminals, self.frozen, self.captures, self.repo, now)
        before = (self.terminals / "idem-1.json").read_bytes()
        second = process(self.pending, self.packets, self.terminals, self.frozen, self.captures, self.repo, now)
        self.assertEqual(first["status"], "PASS")
        self.assertEqual(second["counts"]["ALREADY_TERMINAL"], 1)
        self.assertEqual((self.terminals / "idem-1.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
