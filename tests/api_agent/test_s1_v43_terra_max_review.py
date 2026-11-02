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
            prior = {"body": "S1_TERRA_MAX_RESERVATION_V1 PR=1877 HEAD=" + HEAD + " COMMENT=991"}
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


if __name__ == "__main__":
    unittest.main()
