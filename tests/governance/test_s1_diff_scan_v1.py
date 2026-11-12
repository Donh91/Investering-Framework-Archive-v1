"""Adversarial tests for the SHADOW advisory S1 diff privacy scanner."""
import copy
import unittest
from scripts.governance.s1_diff_scan_v1 import scan_pr, CONTRACT

H = "a" * 40
REPO = "Donh91/Investering-Framework-Archive-v1"

def f(path="README.md", content="Public release notes.", patch="@@ -1,1 +1,1 @@\n-old\n+Public release notes.\n", **kw):
    row = dict(path=path, status="modified", head_sha=H,
               patch=patch, patch_complete=True, binary=False, is_symlink=False,
               content=content, content_head_sha=H)
    row.update(kw)
    return row

def sample(files=None, title="Update public documentation", body="Public docs typo fix."):
    files = [f()] if files is None else files
    return dict(repo=REPO, head=H, pr_head_sha=H, changed_files_count_head_sha=H,
                changed_files_count=len(files), pages_complete=True,
                title=title, body=body, files=files)

class PrivacyScan(unittest.TestCase):
    def check(self, d, result):
        out = scan_pr(d)
        self.assertEqual(out["result"], result, out)
        self.assertEqual(out["head"], d.get("head"))
        self.assertEqual(out["method"], CONTRACT)
        self.assertFalse(out["externally_authenticated"])
        self.assertEqual(out["authority"], "ADVISORY_ONLY")
        return out

    def test_public_docs_typo_is_admissible_advisory_only(self):
        self.assertEqual(self.check(sample(), "NO_RESTRICTED_CONTENT")["findings_count"], 0)

    def test_public_methodology_reference_to_private_repo_name_not_raw_value(self):
        self.check(sample([f(content="Public metadata pointer: Donh91/secrets, only SHA and counts.")]),
                   "NO_RESTRICTED_CONTENT")

    def test_internal_alpha_design_is_detected_without_token_regex(self):
        self.check(sample([f("scripts/util.py", content="# OWNER_ONLY Alpha model design\nx=1")]), "RESTRICTED_CONTENT")
        self.check(sample([f(content="PRIVATE_ALPHA_ARCHITECTURE decision tree")]), "RESTRICTED_CONTENT")

    def test_private_design_in_pr_body_is_detected(self):
        self.check(sample(body="Confidential_Research design detail under owner review"), "RESTRICTED_CONTENT")

    def test_private_design_in_removed_diff_still_publicly_exposed(self):
        self.check(sample([f("README.md", content="Public", patch="@@\n-PRIVATE_ALPHA_DESIGN\n+Public")]),
                   "RESTRICTED_CONTENT")

    def test_api_and_private_key_markers_redacted(self):
        out = self.check(sample([f(content="-----BEGIN PRIVATE KEY-----\n(redacted)\n")]), "RESTRICTED_CONTENT")
        self.assertNotIn("BEGIN PRIVATE KEY", str(out))
        self.check(sample(body="token sk-proj-ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"),
                   "RESTRICTED_CONTENT")

    def test_private_path_blocks_even_with_no_secret_literal(self):
        self.check(sample([f("research/api_agent/code.py", content="x = 1")]), "RESTRICTED_CONTENT")
        self.check(sample([f(".github/workflows/test.yml", content="name: safe")]), "RESTRICTED_CONTENT")
        self.check(sample([f("AGENTS.md", content="Policy")]), "RESTRICTED_CONTENT")

    def test_missing_count_or_wrong_head_fails(self):
        for key, value in (("changed_files_count", 2), ("changed_files_count", True),
                           ("pr_head_sha", "f"*40), ("changed_files_count_head_sha", "f"*40),
                           ("pages_complete", False)):
            with self.subTest(key=key, val=value):
                r = sample(); r[key] = value
                self.check(r, "UNKNOWN")

    def test_omitted_test_file_on_other_page_fails(self):
        r = sample(); r["changed_files_count"] = 2
        self.check(r, "UNKNOWN")

    def test_duplicate_path_unknown(self):
        r = sample([f(), f()])
        self.check(r, "UNKNOWN")

    def test_missing_pr_body_and_non_text_file_unknown(self):
        r = sample(); del r["body"]; self.check(r, "UNKNOWN")
        self.check(sample([f("picture.png")]), "UNKNOWN")

    def test_binary_symlink_and_truncated_diff_unknown(self):
        for changed in ({"binary": True}, {"is_symlink": True},
                        {"patch_complete": False}, {"patch": None},
                        {"content_head_sha": "f"*40}):
            with self.subTest(change=changed):
                self.check(sample([f(**changed)]), "UNKNOWN")

    def test_rename_requires_previous_path(self):
        self.check(sample([f(status="renamed")]), "UNKNOWN")
        self.check(sample([f(status="renamed", previous_filename="docs/old.md")]),
                   "NO_RESTRICTED_CONTENT")

    def test_site_generated_output_cannot_be_self_attested(self):
        r = sample([f("05_CYCLE_NAVIGATOR/site/safe.mjs")])
        self.check(r, "UNKNOWN")
        r["generated_site_outputs_complete"] = True
        self.check(r, "UNKNOWN")  # boolean is not live served-output evidence

    def test_uppercase_private_prefix_is_also_blocked(self):
        self.check(sample([f("PRIVATE/strategy.py", content="x=1")]), "RESTRICTED_CONTENT")
        self.check(sample([f(".GITHUB/workflows/ci.yml", content="x=1")]), "RESTRICTED_CONTENT")

    def test_restricted_evidence_overrides_incomplete_unknown(self):
        r = sample([f(content="PRIVATE_ALPHA_STRATEGY internal note", binary=True)])
        self.check(r, "RESTRICTED_CONTENT")

    def test_noncanonical_input_never_crashes_or_approves(self):
        for r in (None, [], {"head": H}, {"head": H, "oops": {1,2}}):
            out = scan_pr(r)
            self.assertNotEqual(out["result"], "NO_RESTRICTED_CONTENT")
            self.assertFalse(out["externally_authenticated"])

    def test_codex_p2_quoted_json_api_key_marker(self):
        synthetic = '{"api_key":"SYNTHETIC_EXAMPLE_01234567890123456789"}'
        self.check(sample([f("config.json", content=synthetic, patch="+ " + synthetic)]),
                   "RESTRICTED_CONTENT")

    def test_codex_p2_nested_blocked_basename(self):
        self.check(sample([f("docs/AGENTS.md", content="policy note")]), "RESTRICTED_CONTENT")
        self.check(sample([f("docs/subfolder/Id_RSA.txt", content="reference")]), "UNKNOWN")

    def test_codex_p2_rename_from_private_directory(self):
        self.check(sample([f("docs/moved.md", status="renamed",
                             previous_filename="private/design.md")]), "RESTRICTED_CONTENT")

    def test_codex_p2_surrogates_are_unknown_not_crashes(self):
        value = "\ud800"
        for field in ("patch", "content"):
            row = f()
            row[field] = value
            self.check(sample([row]), "UNKNOWN")
        for field in ("title", "body"):
            data = sample()
            data[field] = value
            self.check(data, "UNKNOWN")
        self.check(sample([f("docs/" + value + ".md")]), "UNKNOWN")

    def test_codex_p2_untrusted_head_never_leaks_original_value(self):
        bad = {"head": {"body": "PRIVATE_ALPHA_DESIGN synthetic-sensitive-prose"}}
        out = scan_pr(bad)
        self.assertEqual(out["result"], "UNKNOWN")
        self.assertIsNone(out["head"])
        self.assertNotIn("PRIVATE_ALPHA_DESIGN", str(out))
        bad = sample()
        bad["head"] = "PRIVATE_ALPHA_DESIGN synthetic-sensitive-prose"
        out = scan_pr(bad)
        self.assertEqual(out["result"], "UNKNOWN")
        self.assertIsNone(out["head"])
        self.assertNotIn("PRIVATE_ALPHA_DESIGN", str(out))

    def test_findings_never_emit_private_path_literal(self):
        bad = sample([f("private/PRIVATE_ALPHA_DESIGN_0123.md")])
        out = self.check(bad, "RESTRICTED_CONTENT")
        self.assertNotIn("PRIVATE_ALPHA_DESIGN", str(out))
        self.assertIn("path_sha256_16", str(out))

    def test_run_is_deterministic_and_never_emits_excerpt(self):
        r = sample([f(content="PRIVATE_RESEARCH_DESIGN do not publish")])
        a, b = scan_pr(copy.deepcopy(r)), scan_pr(copy.deepcopy(r))
        self.assertEqual(a, b)
        self.assertNotIn("do not publish", str(a))
        self.assertEqual(a["findings_count"], 1)

if __name__ == "__main__":
    unittest.main()
