"""Owner-bound Terra Max review must be a non-executing, one-shot audit."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.api_agent import s1_v43_terra_max_review as terra

HEAD = "a" * 40
BASE = "b" * 40


def event(owner=True, head=HEAD):
    return {"issue": {"number": 1156}, "comment": {
        "id": 887766, "author_association": "OWNER" if owner else "NONE",
        "body": "[S1_TERRA_MAX_REVIEW] PR=1877 HEAD=" + head,
    }}


def pr(head=HEAD, state="open"):
    return {"number": 1877, "state": state, "draft": False,
        "head": {"sha": head, "repo": {"full_name": terra.REPO}},
        "base": {"ref": "main", "sha": BASE, "repo": {"full_name": terra.REPO}},
        "changed_files": 1}


class TerraReviewTests(unittest.TestCase):
    def test_exact_owner_trigger(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "event.json"
            p.write_text(json.dumps(event()))
            self.assertEqual(terra.parse_event(p), (HEAD, 887766))
            p.write_text(json.dumps(event(owner=False)))
            with self.assertRaises(ValueError):
                terra.parse_event(p)
            p.write_text(json.dumps({"issue": {"number": 123}, "comment": event()["comment"]}))
            with self.assertRaises(ValueError):
                terra.parse_event(p)
            modified = event()
            modified["comment"]["body"] += " malicious instructions"
            p.write_text(json.dumps(modified))
            with self.assertRaises(ValueError):
                terra.parse_event(p)

    def test_exact_head_required(self):
        with patch.object(terra, "gh", return_value=json.dumps(pr())):
            terra.check_pr(HEAD)
            with self.assertRaises(ValueError):
                terra.check_pr("c" * 40)
        with patch.object(terra, "gh", return_value=json.dumps(pr(state="closed"))):
            with self.assertRaises(ValueError):
                terra.check_pr(HEAD)

    def test_postmerge_original_head_can_be_audited(self):
        merged = {**pr(state="closed"), "merged_at": "2026-11-02T11:00:00Z"}
        with patch.object(terra, "gh", return_value=json.dumps(merged)):
            terra.check_pr(HEAD)
        merged["head"]["sha"] = "c" * 40
        with patch.object(terra, "gh", return_value=json.dumps(merged)):
            with self.assertRaises(ValueError):
                terra.check_pr(HEAD)

    def test_full_patch_coverage_and_context_bound(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "event.json"
            p.write_text(json.dumps(event()))
            out = Path(d) / "out"
            diff = "diff --git a/test.py b/test.py\n+assert True\n"
            with patch.object(terra, "gh", side_effect=[json.dumps(pr()), diff]):
                manifest = terra.build(p, out)
            self.assertEqual(manifest["head"], HEAD)
            self.assertEqual(manifest["max_reserved_usd"], 1.5)
            self.assertIn("public_pr_diff_untrusted", json.loads((out / "context.json").read_text()))
            with patch.object(terra, "gh", side_effect=[json.dumps(pr()), diff*2]):
                with self.assertRaisesRegex(ValueError, "INCOMPLETE"):
                    terra.build(p, out)

    def test_reservation_duplicate_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            dest = Path(d)
            (dest / "manifest.json").write_text(json.dumps({"pr": 1877, "head": HEAD, "comment": 991}))
            prior = {"user": {"login": "github-actions[bot]"},
                     "body": "S1_TERRA_MAX_RESERVATION_V1 PR=1877 HEAD=" + HEAD + " COMMENT=991"}
            with patch.object(terra, "gh", return_value=json.dumps([[prior]])):
                with self.assertRaisesRegex(ValueError, "ALREADY_USED"):
                    terra.reserve(dest)

    def test_valid_paid_receipt_model_and_cost_required(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            (out / "output").mkdir()
            context = {"hello": "world"}
            canonical = (json.dumps(context, sort_keys=True, separators=(",", ":")) + "\n").encode()
            (out / "context.json").write_bytes(canonical)
            (out / "prompt.txt").write_text("review prompt")
            (out / "manifest.json").write_text(json.dumps({
                "head": HEAD, "context_sha256": terra.sha256(canonical)
            }))
            receipt = {"status": "PASS", "model": "gpt-6.1-terra", "reasoning_effort": "max",
                       "attempt_count": 1, "estimated_cost_usd": 0.34,
                       "forecast_candidate_count": 0, "context_hash": terra.sha256(canonical), "response_id": "resp_valid"}
            result = {"status": "READY", "evidence_against": [], "summary": "PASS MODEL_USED=gpt-6.1-terra REASONING_MAX NO_CODE_WRITE_PERFORMED NO_AUTHORITY_CHANGE",
                      "forecast_candidates": []}
            (out / "output" / "receipt.json").write_text(json.dumps(receipt))
            (out / "output" / "output.json").write_text(json.dumps(result))
            receipt.update({
                "task": terra.TASK, "prompt_hash": terra.sha256(b"review prompt"),
                "output_hash": terra.sha256((out / "output" / "output.json").read_bytes()),
                "input_tokens": 900, "output_tokens": 220, "request_hash": "f"*64,
            })
            (out / "output" / "receipt.json").write_text(json.dumps(receipt))
            with patch.object(terra, "check_pr", return_value=pr()):
                self.assertEqual(terra.validate(out)["head"], HEAD)
                receipt["model"] = "gpt-6.1-sol"
                (out / "output" / "receipt.json").write_text(json.dumps(receipt))
                with self.assertRaises(ValueError):
                    terra.validate(out)
                receipt["model"] = "gpt-6.1-terra"
                receipt["estimated_cost_usd"] = 2.4
                (out / "output" / "receipt.json").write_text(json.dumps(receipt))
                with self.assertRaises(ValueError):
                    terra.validate(out)
                receipt["estimated_cost_usd"] = 0.25
                (out / "output" / "receipt.json").write_text(json.dumps(receipt))
                result["evidence_against"] = ["P1|scripts/api_agent/example.py|counterexample"]
                (out / "output" / "output.json").write_text(json.dumps(result))
                with self.assertRaisesRegex(ValueError, "FALSE_PASS"):
                    terra.validate(out)
                result["evidence_against"] = []
                (out / "output" / "output.json").write_text(json.dumps(result))
                receipt["estimated_cost_usd"] = float("nan")
                (out / "output" / "receipt.json").write_text(json.dumps(receipt))
                with self.assertRaisesRegex(ValueError, "FINITE"):
                    terra.validate(out)


    def test_spoofed_public_reservations_do_not_block_owner(self):
        body = "S1_TERRA_MAX_RESERVATION_V1 PR=1877 HEAD=" + HEAD + " COMMENT=991"
        spoof = [{"user": {"login": "anonymous"}, "body": body},
                 {"user": {"login": "anonymous"}, "body": "S1_TERRA_MAX_RESERVATION_V1 bad"}]
        mine = {"user": {"login": "github-actions[bot]"}, "body": body}
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            (out / "manifest.json").write_text(json.dumps({"pr": 1877, "head": HEAD, "comment": 991}))
            with patch.object(terra, "gh", side_effect=[json.dumps([spoof]), "", json.dumps([[*spoof, mine]])]), patch.object(terra, "check_pr", return_value=pr()):
                terra.reserve(out)

    def test_spoofed_readback_cannot_validate_reservation(self):
        body = "S1_TERRA_MAX_RESERVATION_V1 PR=1877 HEAD=" + HEAD + " COMMENT=991"
        spoof = {"user": {"login": "anonymous"}, "body": body}
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            (out / "manifest.json").write_text(json.dumps({"pr": 1877, "head": HEAD, "comment": 991}))
            with patch.object(terra, "gh", side_effect=[json.dumps([[]]), "", json.dumps([[spoof]])]), patch.object(terra, "check_pr", return_value=pr()):
                with self.assertRaisesRegex(ValueError, "READBACK_FAILED"):
                    terra.reserve(out)

    def test_fail_with_p1_required_even_when_receipt_is_valid(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            (out / "output").mkdir()
            canonical = b'{"a":1}\n'
            (out / "context.json").write_bytes(canonical)
            (out / "prompt.txt").write_text("p")
            (out / "manifest.json").write_text(json.dumps({"head": HEAD, "context_sha256": terra.sha256(canonical)}))
            def check(findings, verdict, status):
                result = {"status": status, "evidence_against": findings, "forecast_candidates": [],
                          "summary": verdict + " MODEL_USED=gpt-6.1-terra REASONING_MAX NO_CODE_WRITE_PERFORMED NO_AUTHORITY_CHANGE"}
                (out / "output" / "output.json").write_text(json.dumps(result))
                receipt = {"status": "PASS", "model": "gpt-6.1-terra", "reasoning_effort": "max",
                           "attempt_count": 1, "estimated_cost_usd": 0.3, "forecast_candidate_count": 0,
                           "context_hash": terra.sha256(canonical), "response_id": "resp_x",
                           "task": terra.TASK, "prompt_hash": terra.sha256(b"p"),
                           "output_hash": terra.sha256((out / "output" / "output.json").read_bytes()),
                           "input_tokens": 9, "output_tokens": 9, "request_hash": "f" * 64}
                (out / "output" / "receipt.json").write_text(json.dumps(receipt))
                return terra.validate(out)
            with patch.object(terra, "check_pr", return_value=pr()):
                for finding in (
                    "P1|x.py|blocking", " P1|x.py|blocking",
                    "P1 |x.py|blocking", "  p1 |x.py|blocking",
                    "P0 |x.py|critical", "blocking P1 in x.py",
                ):
                    with self.subTest(finding=finding):
                        with self.assertRaisesRegex(ValueError, "UNDERSTATED"):
                            check([finding], "PASS_WITH_FINDINGS", "DEGRADED")
                for finding in (" P2 |x.py|minor", "p2|x.py|minor"):
                    with self.subTest(finding=finding):
                        with self.assertRaisesRegex(ValueError, "FALSE_PASS"):
                            check([finding], "PASS", "READY")
                self.assertEqual(check(["P2|x.py|minor"], "PASS_WITH_FINDINGS", "DEGRADED")["head"], HEAD)
                self.assertEqual(check([" P1 |x.py|blocking"], "FAIL", "BLOCKED")["head"], HEAD)


if __name__ == "__main__":
    unittest.main()
