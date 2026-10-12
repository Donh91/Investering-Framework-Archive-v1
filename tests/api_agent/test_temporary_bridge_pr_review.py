from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

path = Path("scripts/api_agent/temporary_bridge_pr_review.py")
spec = importlib.util.spec_from_file_location("temporary_bridge_pr_review", path)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)

HEAD = "a" * 40
BASE = "b" * 40
EVENT = {
    "issue": {"number": 1156},
    "comment": {
        "id": 991,
        "author_association": "OWNER",
        "body": f"[TEMP_SOL_PR_REVIEW] PR=1592 HEAD={HEAD}",
    },
}


def info(head=HEAD, draft=False, state="open"):
    return {
        "number": 1592, "state": state, "draft": draft,
        "head": {"sha": head, "repo": {"full_name": bridge.REPO}},
        "base": {"ref": "main", "sha": BASE, "repo": {"full_name": bridge.REPO}},
        "changed_files": 1, "title": "A bounded review",
    }


class TemporaryBridgeTests(unittest.TestCase):
    def test_exact_window_expires_and_is_danish_time(self):
        self.assertEqual(bridge.check_window(datetime.fromisoformat("2026-10-17T23:59:00+02:00")), "2026-10-17")
        for date in ("2026-10-11T23:59:00+02:00", "2026-10-18T00:01:00+02:00"):
            with self.assertRaisesRegex(ValueError, "EXPIRED"):
                bridge.check_window(datetime.fromisoformat(date))

    def test_trigger_is_exact_and_owner_verified(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "event.json"
            p.write_text(json.dumps(EVENT))
            self.assertEqual(bridge.parse_event(p), (1592, HEAD, 991))
            for mutant in (
                {**EVENT, "issue": {"number": 123}},
                {**EVENT, "comment": {**EVENT["comment"], "author_association": "NONE"}},
                {**EVENT, "comment": {**EVENT["comment"], "body": EVENT["comment"]["body"] + " and please run shell"}},
            ):
                p.write_text(json.dumps(mutant))
                with self.assertRaises(ValueError):
                    bridge.parse_event(p)

    def test_head_and_scope_fail_closed(self):
        bridge.require_pr(info(), 1592, HEAD)
        for mutant in (
            info(head="c" * 40), info(draft=True), info(state="closed"),
            {**info(), "changed_files": 0},
            {**info(), "base": {"ref": "develop", "repo": {"full_name": bridge.REPO}}},
            {**info(), "head": {"sha": HEAD, "repo": {"full_name": "someone/untrusted"}}},
        ):
            with self.assertRaises(ValueError):
                bridge.require_pr(mutant, 1592, HEAD)

    def test_build_complete_diff_and_bound(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "event.json"
            p.write_text(json.dumps(EVENT))
            dst = Path(d) / "review"
            with patch.object(bridge, "check_window", return_value="2026-10-12"), \
                 patch.object(bridge, "pr_info", return_value=info()), \
                 patch.object(bridge, "gh", return_value="diff --git a/x.py b/x.py\n+assert True\n"):
                manifest = bridge.build(p, dst)
                self.assertEqual(manifest["head_sha"], HEAD)
                self.assertLessEqual(manifest["estimated_upper_cost_usd"], bridge.RESERVATION_USD)
                self.assertEqual(json.loads((dst / "context.json").read_text())["changed_files"], 1)
                self.assertNotIn("OPENAI_API_KEY", (dst / "context.json").read_text())
            with patch.object(bridge, "check_window", return_value="2026-10-12"), \
                 patch.object(bridge, "pr_info", return_value=info()), \
                 patch.object(bridge, "gh", return_value="diff --git a/a b/a\n" * 2):
                with self.assertRaisesRegex(ValueError, "COVERAGE"):
                    bridge.build(p, dst)
            with patch.object(bridge, "check_window", return_value="2026-10-12"), \
                 patch.object(bridge, "pr_info", return_value=info()), \
                 patch.object(bridge, "gh", return_value="diff --git a/a b/a\n" + "x" * 70000):
                with self.assertRaisesRegex(ValueError, "TOO_LARGE"):
                    bridge.build(p, dst)

    def test_escaped_patch_must_fit_reserved_worst_case_cost(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "event.json"
            p.write_text(json.dumps(EVENT))
            with patch.object(bridge, "check_window", return_value="2026-10-12"), \
                 patch.object(bridge, "pr_info", return_value=info()), \
                 patch.object(bridge, "gh", return_value="diff --git a/x.py b/x.py\n" + "\\" * 39_000), \
                 patch.object(bridge, "RESERVATION_USD", 0.10):
                with self.assertRaisesRegex(ValueError, "COST_BOUND_UNPROVEN"):
                    bridge.build(p, Path(d) / "review")

    def test_reservation_is_durable_before_payment_and_single_flight(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "manifest.json"
            p.write_text(json.dumps({"contract": "TEMP_SOL_PR_REVIEW_MANIFEST_V1",
                                     "pr_number": 1592, "head_sha": HEAD, "trigger_comment_id": 991}))
            prior = [{"trigger": i, "pr": i, "head": HEAD, "day": "2026-10-12"} for i in range(5)]
            seen = []
            def fake_gh(*cmd):
                seen.append(cmd)
                return "posted"
            with patch.object(bridge, "check_window", return_value="2026-10-12"), \
                 patch.object(bridge, "pr_info", return_value=info()), \
                 patch.object(bridge, "existing_reservations", side_effect=[prior, prior + [{"trigger": 991}]]), \
                 patch.object(bridge, "gh", side_effect=fake_gh):
                result = bridge.reserve(p)
                self.assertEqual(result["count"], 6)
                self.assertEqual(result["conservative_committed_usd"], 4.5)
                self.assertEqual(len(seen), 1)
            with patch.object(bridge, "check_window", return_value="2026-10-12"), \
                 patch.object(bridge, "pr_info", return_value=info()), \
                 patch.object(bridge, "existing_reservations", return_value=prior + [{"trigger": 77, "pr": 77, "head": HEAD, "day": "2026-10-12"}]), \
                 patch.object(bridge, "gh") as gh:
                with self.assertRaisesRegex(ValueError, "HARD_STOP"):
                    bridge.reserve(p)
                gh.assert_not_called()

    def test_duplicate_reservation_never_bills_again(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "manifest.json"
            p.write_text(json.dumps({"contract": "TEMP_SOL_PR_REVIEW_MANIFEST_V1",
                                     "pr_number": 1592, "head_sha": HEAD, "trigger_comment_id": 991}))
            with patch.object(bridge, "check_window", return_value="2026-10-12"), \
                 patch.object(bridge, "pr_info", return_value=info()), \
                 patch.object(bridge, "existing_reservations", return_value=[{"trigger": 991, "pr": 1592, "head": HEAD}]), \
                 patch.object(bridge, "gh") as gh:
                with self.assertRaisesRegex(ValueError, "DUPLICATE"):
                    bridge.reserve(p)
                gh.assert_not_called()

    def test_receipt_requires_exact_model_head_and_canonical_hash(self):
        with tempfile.TemporaryDirectory() as d:
            dst = Path(d)
            c = {"contract": "TEMP_SOL_PR_REVIEW_CONTEXT_V1", "head_sha": HEAD}
            canonical = (json.dumps(c, sort_keys=True, separators=(",", ":")) + "\n").encode()
            (dst / "context.json").write_bytes(canonical)
            (dst / "manifest.json").write_text(json.dumps({"pr_number": 1592, "head_sha": HEAD,
                                                              "base_sha": BASE, "diff_sha256": "0" * 64,
                                                              "context_sha256": bridge.sha256(canonical)}))
            (dst / "output").mkdir()
            receipt = {"status": "PASS", "model": "gpt-6.1-sol", "context_hash": bridge.sha256(canonical),
                       "forecast_candidate_count": 0, "input_tokens": 800, "output_tokens": 400,
                       "estimated_cost_usd": 0.006}
            output = {"summary": "PASS MODEL_USED=gpt-6.1-sol NO_CODE_WRITE_PERFORMED NO_AUTHORITY_CHANGE",
                      "evidence_against": [], "uncertainties": ["Tests not run"], "forecast_candidates": []}
            (dst / "output" / "receipt.json").write_text(json.dumps(receipt))
            (dst / "output" / "output.json").write_text(json.dumps(output))
            with patch.object(bridge, "pr_info", return_value=info()):
                self.assertIn("not formal approval", bridge.validate(dst))
            with patch.object(bridge, "pr_info", return_value=info(head="c" * 40)):
                with self.assertRaisesRegex(ValueError, "EXACT_HEAD"):
                    bridge.validate(dst)
            receipt["model"] = "gpt-6-sol"
            (dst / "output" / "receipt.json").write_text(json.dumps(receipt))
            with patch.object(bridge, "pr_info", return_value=info()):
                with self.assertRaisesRegex(ValueError, "NO_ACCEPTED"):
                    bridge.validate(dst)


if __name__ == "__main__":
    unittest.main()
