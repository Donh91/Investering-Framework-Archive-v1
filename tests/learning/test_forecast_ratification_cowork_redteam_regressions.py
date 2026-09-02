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
from process_forecast_ratifications import process  # noqa: E402

UTC = timezone.utc


def canon(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value):
    return hashlib.sha256(canon(value)).hexdigest()


class CoworkRedTeamRegressionTests(unittest.TestCase):
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
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        env = dict(os.environ)
        env["GIT_AUTHOR_DATE"] = when
        env["GIT_COMMITTER_DATE"] = when
        subprocess.run(["git", "commit", "-qm", message], cwd=self.repo, check=True, env=env)

    def candidate(self, cid: str, metric: str = "derivatives.BTC-USDT-SWAP.mark_price.mark_price"):
        return {
            "contract": "FORECAST_CANDIDATE_v1",
            "authority": "UNRATIFIED_RESEARCH_ONLY",
            "candidate_id": cid,
            "created_at_utc": "2026-09-02T10:10:00Z",
            "model": "fixture",
            "task": "DAILY_DIRECTOR_SHADOW",
            "prompt_sha256": "a" * 64,
            "context_sha256": "b" * 64,
            "source_output_sha256": "c" * 64,
            "candidate": {
                "metric_path": metric,
                "direction": "DOWN",
                "target_mode": "PCT_MOVE",
                "threshold_pct": 1.0,
                "target_value": None,
                "range_low": None,
                "range_high": None,
                "horizon_days": 1,
                "rationale": "red-team fixture",
            },
            "ratification_status": "PENDING",
            "self_promotion_allowed": False,
        }

    def packet(self, candidate, decision="RATIFY"):
        return {
            "contract": "FORECAST_RATIFICATION_PACKET_v2",
            "candidate_id": candidate["candidate_id"],
            "candidate_sha256": digest(candidate),
            "decision": decision,
            "decision_at_utc": "2026-09-02T10:20:00Z",
            "authority": "CHATGPT_FRAMEWORK_OWNER",
            "owner_actor": "GPT-5.6 Sol",
            "outcome_blind": True,
            "self_promotion_allowed": False,
            "prospective_cutover_commit_sha": CUTOVER_COMMIT_SHA,
            "decision_basis_scope": ["RATIFICATION_QUEUE", "CANDIDATE_RECORD"],
            "outcome_paths_read": [],
            "decision_rationale": "fixture",
        }

    def write_candidate(self, candidate, suffix=""):
        path = self.pending / "2026/09/02" / f"{candidate['candidate_id']}{suffix}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(canon(candidate))
        return path

    def write_packet(self, packet):
        path = self.packets / f"{packet['candidate_id']}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(canon(packet))
        return path

    def write_capture(self, name: str, observed: str, market_metrics: dict):
        path = self.captures / "2026/09/02" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(canon({"captured_at_utc": observed, "market_metrics": market_metrics}))
        return path

    def run_process(self):
        return process(
            self.pending, self.packets, self.terminals, self.frozen, self.captures, self.repo,
            datetime(2026, 9, 2, 10, 30, tzinfo=UTC),
        )

    def test_f01_fresh_capture_without_metric_never_falls_back_to_old_metric(self):
        candidate = self.candidate("stale-spot", "spot.BTCUSDT.close")
        self.write_candidate(candidate)
        self.write_capture("old.json", "2026-09-02T09:30:00Z", {"spot": {"BTCUSDT": {"close": 65015.28}}})
        self.write_capture("fresh.json", "2026-09-02T10:19:00Z", {"derivatives": {"BTC-USDT-SWAP": {"mark_price": {"mark_price": 76957.0}}}})
        self.commit("candidate and captures", "2026-09-02T10:19:30Z")
        self.write_packet(self.packet(candidate))
        self.commit("packet", "2026-09-02T10:21:00Z")
        result = self.run_process()
        self.assertEqual(result["status"], "FAIL")
        self.assertFalse(result["pipeline_blocking"])
        self.assertTrue(any("BASELINE_METRIC_UNAVAILABLE_IN_FRESHEST_ARCHIVED_CAPTURE" in row["error"] for row in result["errors"]))
        self.assertEqual(list(self.frozen.glob("*.json")), [])

    def test_f02_packet_body_is_bound_to_first_git_add_content(self):
        candidate = self.candidate("packet-lock")
        self.write_candidate(candidate)
        self.write_capture("fresh.json", "2026-09-02T10:19:00Z", {"derivatives": {"BTC-USDT-SWAP": {"mark_price": {"mark_price": 100.0}}}})
        self.commit("candidate", "2026-09-02T10:19:30Z")
        packet_path = self.write_packet(self.packet(candidate, decision="REJECT"))
        self.commit("reject packet", "2026-09-02T10:21:00Z")
        packet_path.write_bytes(canon(self.packet(candidate, decision="RATIFY")))
        self.commit("mutate packet body", "2026-09-02T10:25:00Z")
        result = self.run_process()
        self.assertTrue(any("RATIFICATION_PACKET_CONTENT_CHANGED_AFTER_FIRST_ADD" in row["error"] for row in result["errors"]))
        self.assertEqual(list(self.frozen.glob("*.json")), [])

    def test_f02_deleted_terminal_cannot_resurrect_rejected_candidate(self):
        candidate = self.candidate("terminal-lock")
        self.write_candidate(candidate)
        self.commit("candidate", "2026-09-02T10:11:00Z")
        packet_path = self.write_packet(self.packet(candidate, decision="REJECT"))
        self.commit("reject packet", "2026-09-02T10:21:00Z")
        first = self.run_process()
        self.assertEqual(first["counts"]["REJECTED_BY_OWNER"], 1)
        self.commit("record terminal", "2026-09-02T10:31:00Z")
        (self.terminals / "terminal-lock.json").unlink()
        packet_path.write_bytes(canon(self.packet(candidate, decision="RATIFY")))
        self.commit("delete terminal and mutate packet", "2026-09-02T10:35:00Z")
        second = self.run_process()
        self.assertTrue(any("RATIFICATION_TERMINAL_MISSING_BUT_GIT_RECORDED" in row["error"] for row in second["errors"]))
        self.assertEqual(list(self.frozen.glob("*.json")), [])

    def test_f03_post_cutover_duplicate_is_quarantined_without_blocking_valid_candidate(self):
        valid = self.candidate("valid-1")
        duplicate = self.candidate("dup-1")
        self.write_candidate(valid)
        self.write_candidate(duplicate, "-a")
        self.write_candidate(duplicate, "-b")
        self.write_capture("fresh.json", "2026-09-02T10:19:00Z", {"derivatives": {"BTC-USDT-SWAP": {"mark_price": {"mark_price": 100.0}}}})
        self.commit("candidates and capture", "2026-09-02T10:19:30Z")
        self.write_packet(self.packet(valid))
        self.commit("valid packet", "2026-09-02T10:21:00Z")
        result = self.run_process()
        self.assertFalse(result["pipeline_blocking"])
        self.assertEqual(result["counts"]["RATIFIED_AND_FROZEN"], 1)
        self.assertEqual(result["counts"]["POST_CUTOVER_CANDIDATE_STRUCTURE_QUARANTINED"], 1)
        quarantine = json.loads((self.terminals / "dup-1.json").read_text())
        self.assertEqual(quarantine["disposition"], "POST_CUTOVER_CANDIDATE_STRUCTURE_QUARANTINED")
        self.assertFalse(quarantine["ratification_allowed"])

    def test_f04_supported_alias_freezes_to_canonical_exact_metric(self):
        alias = "latest_capture.market_metrics.derivatives.BTC-USDT-SWAP.mark_price.mark_price"
        candidate = self.candidate("alias-1", alias)
        self.write_candidate(candidate)
        self.write_capture("fresh.json", "2026-09-02T10:19:00Z", {"derivatives": {"BTC-USDT-SWAP": {"mark_price": {"mark_price": 100.0}}}})
        self.commit("candidate and capture", "2026-09-02T10:19:30Z")
        self.write_packet(self.packet(candidate))
        self.commit("packet", "2026-09-02T10:21:00Z")
        result = self.run_process()
        self.assertEqual(result["counts"]["RATIFIED_AND_FROZEN"], 1)
        frozen = json.loads(next(self.frozen.glob("*.json")).read_text())
        self.assertEqual(frozen["metric_path"], "derivatives.BTC-USDT-SWAP.mark_price.mark_price")
        self.assertEqual(frozen["candidate_authored_metric_path"], alias)
        self.assertEqual(frozen["settlement_contract_version"], "FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1")


if __name__ == "__main__":
    unittest.main()
