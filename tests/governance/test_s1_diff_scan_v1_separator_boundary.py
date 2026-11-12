"""Codex P2 (#2091, s1_diff_scan_v1.py:37): credential tokens after "_"/"-" separators.

`\\b` does not fire between "_" and a letter, so `backup_sk-proj-...` slipped through
as a filename, a rename source, or inline identifier text. These cases must be
RESTRICTED_CONTENT; alphanumeric-glued look-alikes keep their previous behaviour.
"""
import unittest
from scripts.governance.s1_diff_scan_v1 import scan_pr
from tests.governance.test_s1_diff_scan_v1 import f, sample

TOKEN = "sk-proj-" + "A" * 32
AWS = "AKIA" + "B" * 16


class SeparatorBoundaryTests(unittest.TestCase):
    def verdict(self, d):
        return scan_pr(d)["result"]

    def test_underscore_prefixed_token_in_filename(self):
        self.assertEqual(self.verdict(sample([f(f"docs/backup_{TOKEN}.md")])), "RESTRICTED_CONTENT")

    def test_underscore_prefixed_token_in_rename_source(self):
        row = f("docs/notes.md", status="renamed", previous_filename=f"docs/old_{TOKEN}.md")
        self.assertEqual(self.verdict(sample([row])), "RESTRICTED_CONTENT")

    def test_hyphen_and_underscore_prefixed_tokens_in_content(self):
        for text in (f"x = backup_{TOKEN}", f"ref-{TOKEN}", f"aws_{AWS}_key", f"my_api_key = '{'Z' * 24}'"):
            with self.subTest(text=text[:20]):
                self.assertEqual(self.verdict(sample([f(content=text)])), "RESTRICTED_CONTENT")

    def test_plain_public_text_stays_clean(self):
        self.assertEqual(self.verdict(sample([f(content="Public docs: rotate keys via the vault UI.")])),
                         "NO_RESTRICTED_CONTENT")

    def test_alnum_glued_lookalike_unchanged(self):
        # Not a token boundary: the scanner keeps its previous (non-matching) behaviour.
        self.assertEqual(self.verdict(sample([f(content="tasksk-projectplan is a word")])),
                         "NO_RESTRICTED_CONTENT")


if __name__ == "__main__":
    unittest.main()
