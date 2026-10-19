"""Offline adversarial tests of canonical first Git publication anchoring."""
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.experiments.source_git_anchor import first_accepted_main_raw


def git(root, *args):
    return subprocess.run(("git", "-C", str(root), *args), check=True,
                          capture_output=True, timeout=10).stdout


class CanonicalSourceAnchorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        parent = Path(self.tmp.name)
        self.root = parent / "checkout"
        self.root.mkdir()
        self.origin = parent / "origin.git"
        git(parent, "init", "-q", "--bare", str(self.origin))
        git(self.root, "init", "-q", "-b", "main")
        git(self.root, "config", "user.name", "SyntheticFixture")
        git(self.root, "config", "user.email", "fixture@example.invalid")
        git(self.root, "remote", "add", "origin", self.origin.as_uri())
        self.rel = Path("raw/EXP-FC-test/source.json")
        self.source = self.root / self.rel
        self.source.parent.mkdir(parents=True)
        self.original = b'[[1,"100","104","99","100.2","1",59999]]'
        self.source.write_bytes(self.original)
        git(self.root, "add", self.rel.as_posix())
        git(self.root, "commit", "-qm", "first accepted synthetic receipt")
        git(self.root, "push", "-q", "-u", "origin", "main")
        self.digest = hashlib.sha256(self.original).hexdigest()

    def check(self, digest=None, path=None, *, fixture=True):
        kw = {"fixture_origin": self.origin.as_uri()} if fixture else {}
        return first_accepted_main_raw(
            self.root, self.rel if path is None else path,
            self.digest if digest is None else digest, **kw,
        )

    def test_first_original_git_blob_accepted(self):
        self.assertTrue(self.check())

    def test_untrusted_pr_worktree_still_reads_remote_main(self):
        git(self.root, "checkout", "-qb", "untrusted-pr")
        self.assertTrue(self.check())

    def test_coordinated_raw_digest_and_market_forgery_rejected(self):
        forged = self.original.replace(b"100.2", b"102.0")
        self.source.write_bytes(forged)
        self.assertFalse(self.check(hashlib.sha256(forged).hexdigest()))

    def test_later_canonical_commit_cannot_replace_first_acceptance(self):
        forged = self.original.replace(b"100.2", b"102.0")
        self.source.write_bytes(forged)
        git(self.root, "add", self.rel.as_posix())
        git(self.root, "commit", "-qm", "later mutation")
        git(self.root, "push", "-q", "origin", "main")
        self.assertFalse(self.check(hashlib.sha256(forged).hexdigest()))

    def test_branch_only_source_not_accepted(self):
        git(self.root, "checkout", "-qb", "untrusted-pr")
        relative = Path("raw/EXP-FC-new/source.json")
        extra = self.root / relative
        extra.parent.mkdir(parents=True)
        extra.write_bytes(b"forged")
        git(self.root, "add", relative.as_posix())
        git(self.root, "commit", "-qm", "PR-only fake source")
        self.assertFalse(self.check(hashlib.sha256(b"forged").hexdigest(), relative))

    def test_local_ref_override_does_not_override_remote(self):
        git(self.root, "checkout", "-qb", "untrusted-pr")
        self.source.write_bytes(b"counterfeit")
        git(self.root, "add", self.rel.as_posix())
        git(self.root, "commit", "-qm", "PR mutation")
        git(self.root, "branch", "-f", "main", "HEAD")
        self.assertFalse(self.check(hashlib.sha256(b"counterfeit").hexdigest()))

    def test_remote_main_advances_without_trusting_stale_local_ref(self):
        writer = Path(self.tmp.name) / "independent-writer"
        subprocess.run(("git", "clone", "-q", "-b", "main", self.origin.as_uri(),
                        str(writer)), check=True, capture_output=True, timeout=10)
        git(writer, "config", "user.name", "IndependentSyntheticPublisher")
        git(writer, "config", "user.email", "independent@example.invalid")
        (writer / "unrelated.txt").write_text("unrelated new official main publication")
        git(writer, "add", "unrelated.txt")
        git(writer, "commit", "-qm", "legitimate later unrelated update")
        git(writer, "push", "-q", "origin", "main")
        first_local_main = git(self.root, "rev-parse", "main").decode().strip()
        self.assertTrue(self.check())
        self.assertEqual(git(self.root, "rev-parse", "main").decode().strip(),
                         first_local_main)

    def test_untrusted_remote_and_missing_remote_fail_closed(self):
        self.assertFalse(self.check(fixture=False))
        git(self.root, "remote", "remove", "origin")
        self.assertFalse(self.check())

    def test_wrong_digest_missing_raw_and_escape_fail_closed(self):
        self.assertFalse(self.check("0" * 64))
        self.assertFalse(self.check(path=Path("../raw/EXP-FC-test/source.json")))
        self.source.unlink()
        self.assertFalse(self.check())

    def test_symlink_fails_closed(self):
        self.source.unlink()
        self.source.symlink_to(self.origin)
        self.assertFalse(self.check())

    def test_shallow_history_fails_closed(self):
        parent = Path(self.tmp.name)
        git(self.root, "commit", "--allow-empty", "-qm", "latest")
        git(self.root, "push", "-q", "origin", "main")
        clone = parent / "shallow"
        subprocess.run(("git", "clone", "-q", "--depth=1", "-b", "main",
                        self.origin.as_uri(), str(clone)), check=True,
                        capture_output=True, timeout=10)
        self.assertFalse(first_accepted_main_raw(
            clone, self.rel, self.digest, fixture_origin=self.origin.as_uri()))
