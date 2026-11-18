"""S1_DIFF_SCAN_V1 marker precision (v3; Claude review of Archive #2204, owner handoff Bridge #173 c=6947286743).

The restricted-design predicate must match marker TOKENS and explicit LABELS, never narrative prose. Two public Astra
reports tripped the old case-insensitive pattern on ordinary English. Only that one predicate changed: this file also
proves that every credential, key and path rule is byte-for-byte the rule of the previous scanner, and that missing
or ambiguous evidence still fails closed.

Every marker below is built by concatenation, so this file itself holds no marker and stays scanner-clean.
"""
import hashlib
import re
import unittest

from scripts.governance import s1_diff_scan_v1 as scan
from tests.governance.test_s1_diff_scan_v1 import f, sample

RULES = dict(scan.KNOWN_SECRET_OR_RESTRICTED_DESIGN)
RULE = RULES["EXPLICIT" + "_PRIVATE_DESIGN"]
PHRASES = (("OWNER", "ONLY"), ("INTERNAL", "ONLY"), ("NOT", "FOR", "PUBLICATION"), ("PRIVATE", "ALPHA", "DESIGN"),
           ("PRIVATE", "ALPHA", "STRATEGY"), ("PRIVATE", "ALPHA", "ARCHITECTURE"), ("PRIVATE", "ALPHA", "MODEL"),
           ("PRIVATE", "RESEARCH", "DESIGN"), ("CONFIDENTIAL", "RESEARCH"))
# The exact public lines that tripped the old pattern (06_RESEARCH_LAB/astra_program_20261116/results/, #2204).
ASTRA_COMPASS_EDGE_L409 = ("| Governed weekly strategic owner" + " only. No stretching of 2\u20133-week output. |")
ASTRA_S1_VNEXT_L859 = ("computation and explicit unknowns. Some changes may remain owner" + "-only indefinitely. "
                       "[Basis: D, \u00a76; V, D4]")
# sha256 of (name, pattern, flags) for every rule except the one this release narrows: they must not move.
UNCHANGED_RULES_SHA256 = "c5e2131bba3bb24d1ebf430649b83df7d09e90dd1d32a44b2e212966b775a163"


def verdict(content=None, path="docs/note.md", **kw):
    row = f(path, **kw) if content is None else f(path, content=content, **kw)
    return scan.scan_pr(sample([row]))["result"]


class MarkerPrecisionTest(unittest.TestCase):
    def test_upper_case_tokens_match_with_every_separator(self):
        for words in PHRASES:
            for sep in ("_", "-", " "):
                token = sep.join(words)
                with self.subTest(token=token):
                    self.assertTrue(RULE.search(f"see {token} here"))
                    self.assertEqual(verdict(f"Draft. {token} material.\n"), "RESTRICTED_CONTENT")

    def test_underscore_tokens_match_in_any_case(self):
        for words in PHRASES:
            for token in ("_".join(words).lower(), "_".join(w.capitalize() for w in words)):
                with self.subTest(token=token):
                    self.assertTrue(RULE.search(f"flag {token}=1"))

    def test_header_and_label_variants_match(self):
        for words in PHRASES:
            phrase = " ".join(words).capitalize()
            hyphen = "-".join(words).lower()
            for line in (f"## {phrase}", f"# {phrase.upper()}", f"**{phrase}**", f"> {phrase}", f"[{phrase}]",
                         f"*{hyphen}*", f"Classification: {phrase.lower()}", f"visibility = {hyphen}",
                         f"**Confidentiality:** {phrase}", f"| Distribution: {phrase} |", f"Handling: `{hyphen}`",
                         f'"classification": "{phrase.lower()}"', f'  "visibility": "{hyphen}",', f"'handling': '{hyphen}'",
                         '{"sensitivity": "' + phrase.lower() + '"}', f"| Classification | {phrase.title()} |",
                         f"<!-- {phrase.lower()} -->", f"<!-- {phrase.upper()} -->",
                         f"data_classification: {phrase.lower()}", f"x-classification: {hyphen}",
                         f"doc.classification = '{phrase.lower()}'", f'"data_visibility": "{hyphen}"'):
                with self.subTest(line=line):
                    self.assertTrue(RULE.search("intro\n" + line + "\noutro"), line)
                    self.assertEqual(verdict("intro\n" + line + "\n"), "RESTRICTED_CONTENT")

    def test_narrative_prose_does_not_match(self):
        prose = [ASTRA_COMPASS_EDGE_L409, ASTRA_S1_VNEXT_L859,
                 "the owner" + " only approves gated changes", "this is for internal" + " only use by the team",
                 "Owner" + "-only merges stay with the owner.", "it is not" + " for publication yet, said the author",
                 "confidential" + " research was never used here", "a private" + " research design is out of scope",
                 "owner" + " only", "Internal" + " only", "- owner" + " only", "| owner" + " only |",
                 "status: the owner" + " only reads it",
                 # recorded decisions (detached review R1): prose shapes that are neither a token nor a label
                 "# internal" + " only draft", "DRAFT - Not" + " For Publication", "Not" + " For Publication.",
                 "the owner" + "-only rule", "(see the internal" + " only note)",
                 # recorded decisions (detached review R2): not a label key, not a decorated label line
                 "the reclassification: internal" + " only", "// internal" + " only", "<h1>internal" + " only</h1>",
                 "- internal" + " only"]
        for line in prose:
            with self.subTest(line=line[:40]):
                self.assertIsNone(RULE.search(line))
                self.assertEqual(verdict("Report.\n" + line + "\nEnd.\n"), "NO_RESTRICTED_CONTENT")

    def test_token_boundaries_are_kept(self):
        glued = "pre" + "OWNER" + "_ONLY" + "post"
        self.assertIsNone(RULE.search(glued))
        self.assertIsNone(RULE.search("pre" + "OWNER" + "_ONLY" + " end"))          # glued on the left only
        self.assertIsNone(RULE.search("start " + "OWNER" + "_ONLY" + "post"))       # glued on the right only
        self.assertIsNone(RULE.search("x9" + "INTERNAL" + " ONLY" + " end"))
        self.assertTrue(RULE.search("backup_" + "OWNER" + "_ONLY" + ".md"))
        self.assertTrue(RULE.search("backup-" + "INTERNAL" + "_ONLY" + ".md"))

    def test_marker_in_title_body_filename_and_rename_source_still_blocks(self):
        token = "NOT" + "_FOR_" + "PUBLICATION"
        record = sample([f("docs/note.md", content="Public text.\n")])
        record["title"] = f"Add {token} notes"
        self.assertEqual(scan.scan_pr(record)["result"], "RESTRICTED_CONTENT")
        record = sample([f("docs/note.md", content="Public text.\n")])
        record["body"] = f"## {'Internal' + ' only'}\nSee thread."
        self.assertEqual(scan.scan_pr(record)["result"], "RESTRICTED_CONTENT")
        self.assertEqual(verdict(None, path=f"docs/{token}.md"), "RESTRICTED_CONTENT")
        row = f("docs/new.md", status="renamed", previous_filename=f"docs/{token}.md")
        self.assertEqual(scan.scan_pr(sample([row]))["result"], "RESTRICTED_CONTENT")


class LinearTimeTest(unittest.TestCase):
    def test_pathological_lines_scan_in_linear_time(self):
        # A first draft of this predicate nested two quantifiers and backtracked exponentially on decoration runs.
        import time
        lines = ["#" * 4000 + " x", "* " * 3000 + "x", "|---" * 2000 + "|", "- " * 3000 + "classification",
                 ">" * 3000 + " owner" + " onlyx", "_*_*" * 2000 + "y", "[" * 3000 + "confidential" + " researcher",
                 "classification" + " :*`" * 2000 + " none", "a " * 50000]
        start = time.perf_counter()
        for line in lines:
            self.assertIsNone(RULE.search("intro\n" + line + "\noutro\n" * 3))
        self.assertLess(time.perf_counter() - start, 5.0)

    def test_no_nested_quantifier_in_the_pattern(self):
        self.assertIsNone(re.search(r"[+*]\)[+*]", RULE.pattern), "a repeated group that itself ends in a repetition")


class NothingElseWeakenedTest(unittest.TestCase):
    def test_every_other_rule_is_unchanged(self):
        names = [name for name, _ in scan.KNOWN_SECRET_OR_RESTRICTED_DESIGN]
        self.assertEqual(names, ["PRIVATE_KEY_BLOCK", "API_KEY_LITERAL", "AWS_ACCESS_KEY", "SIGNED_URL",
                                 "EXPLICIT" + "_PRIVATE_DESIGN", "CREDENTIAL_ASSIGNMENT", "MNEMONIC_EXPOSURE"])
        blob = "\n".join(f"{name}\t{rx.pattern}\t{rx.flags}" for name, rx in scan.KNOWN_SECRET_OR_RESTRICTED_DESIGN
                         if name != "EXPLICIT" + "_PRIVATE_DESIGN")
        self.assertEqual(hashlib.sha256(blob.encode("utf-8")).hexdigest(), UNCHANGED_RULES_SHA256)

    def test_credential_and_key_detections_unchanged(self):
        samples = ["-----BEGIN " + "PRIVATE KEY-----", "gh" + "p_" + "A" * 36, "sk-" + "proj-" + "b" * 24,
                   "AK" + "IA" + "Z" * 16, "X-Amz-" + "Signature=" + "abcdef0123456789",
                   "api_" + "key = '" + "Z" * 24 + "'", "seed " + "phrase: one two three four five six seven"]
        for text in samples:
            with self.subTest(text=text[:12]):
                self.assertEqual(verdict("x\n" + text + "\n"), "RESTRICTED_CONTENT")

    def test_blocked_paths_and_prefixes_unchanged(self):
        self.assertEqual(scan.BLOCKED_PREFIXES, (".github/", ".agents/", "00_FMOS/", "00_ARCHIVE_CONTROL/",
                                                 "research/api_agent/", "private/", "secrets/", "vault/",
                                                 "config/private/", "data/private/", "08_SOURCE_MATERIAL/private/"))
        self.assertEqual(scan.BLOCKED_BASENAMES, {"AGENTS.md", ".env", ".npmrc", ".pypirc", "id_rsa", "id_ed25519"})
        for path in ("private/x.md", "00_FMOS/x.md", ".github/workflows/x.yml", "docs/.env", "keys/a.pem"):
            self.assertEqual(verdict(None, path=path), "RESTRICTED_CONTENT", path)

    def test_missing_or_ambiguous_evidence_still_fails_closed(self):
        self.assertEqual(verdict("clean\n", patch_complete=False), "UNKNOWN")
        self.assertEqual(verdict("clean\n", binary=True), "UNKNOWN")
        self.assertEqual(verdict("clean\n", content_head_sha="0" * 40), "UNKNOWN")
        record = sample([f("docs/note.md", content="clean\n")])
        record["pages_complete"] = False
        self.assertEqual(scan.scan_pr(record)["result"], "UNKNOWN")
        record = sample([f("docs/note.md", content="clean\n")])
        del record["title"]
        self.assertEqual(scan.scan_pr(record)["result"], "UNKNOWN")
        self.assertEqual(scan.scan_pr({})["result"], "UNKNOWN")

    def test_no_allowlist_or_bypass_exists(self):
        source = (scan.__file__ and open(scan.__file__, encoding="utf-8").read())
        for word in ("allowlist_paths", "ALLOW_MARKER", "SKIP_SCAN", "noqa-privacy", "os.environ"):
            self.assertNotIn(word, source)
        self.assertEqual(len(re.findall(r"^def scan_pr\(", source, re.M)), 1)


if __name__ == "__main__":
    unittest.main()
