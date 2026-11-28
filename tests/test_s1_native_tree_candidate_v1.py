import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.research.s1_branch_update_candidate_v1 import Entry, Hold
from scripts.research.s1_native_tree_candidate_v1 import oid, parse_leaves, root_oid, read_snapshot


class NativeTreeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                        GIT_AUTHOR_NAME="D5", GIT_AUTHOR_EMAIL="d5@example.invalid",
                        GIT_COMMITTER_NAME="D5", GIT_COMMITTER_EMAIL="d5@example.invalid")
        self.git("init", "-q", "--object-format=sha1")
        self.blob = self.git("hash-object", "-w", "--stdin", data=b"hello\n")

    def git(self, *args, data=None):
        return subprocess.run(["git", *args], cwd=self.repo, env=self.env, input=data,
                              capture_output=True, check=True, timeout=10).stdout.decode().strip()

    def tree(self, lines):
        return self.git("mktree", data=lines.encode())

    def commit(self, tree):
        return self.git("commit-tree", tree, "-m", "D5 fixture")

    def test_native_modes_and_git_sort_order(self):
        sub = self.tree(f"100755 blob {self.blob}\tfile\n")
        tree = self.tree(f"040000 tree {sub}\td\n100644 blob {self.blob}\td.txt\n120000 blob {self.blob}\tlink\n")
        head = self.commit(tree)
        snap = read_snapshot(self.repo / ".git", head)
        self.assertEqual(snap.tree, tree)
        self.assertEqual(snap.entries["d/file"].mode, "100755")
        self.assertEqual(snap.entries["link"].mode, "120000")
        self.assertEqual(root_oid(snap.entries), tree)
        for changed in ({k: v for k, v in snap.entries.items() if k != "d/file"},
                        snap.entries | {"d/file": Entry("100644", self.blob)}):
            self.assertNotEqual(root_oid(changed), tree)

    def test_gitlink_and_empty_root(self):
        empty = self.tree("")
        self.assertEqual(root_oid({}), empty)
        self.assertEqual(read_snapshot(self.repo / ".git", self.commit(empty)).entries, {})
        target = self.commit(empty)
        tree = self.tree(f"160000 commit {target}\tmodule\n")
        self.assertEqual(read_snapshot(self.repo / ".git", self.commit(tree)).entries,
                         {"module": Entry("160000", target)})

    def test_empty_nested_tree_fails_closed(self):
        empty = self.tree("")
        tree = self.tree(f"040000 tree {empty}\tempty\n")
        with self.assertRaisesRegex(Hold, "TREE_HASH_MISMATCH"):
            read_snapshot(self.repo / ".git", self.commit(tree))

    def test_ref_and_missing_object_refused(self):
        with self.assertRaisesRegex(Hold, "COMMIT_SHA_INVALID"):
            read_snapshot(self.repo / ".git", "HEAD")
        with self.assertRaisesRegex(Hold, "NATIVE_OBJECT_UNREADABLE"):
            read_snapshot(self.repo / ".git", "f"*40)

    def test_leaf_parser_refuses_partial_duplicate_and_bad_type(self):
        row = f"100644 blob {self.blob}\ta".encode()
        with self.assertRaisesRegex(Hold, "TREE_TRUNCATED"):
            parse_leaves(row)
        with self.assertRaisesRegex(Hold, "TREE_ENTRY_INVALID"):
            parse_leaves((row + b"\x00")*2)
        with self.assertRaisesRegex(Hold, "TREE_ENTRY_INVALID"):
            parse_leaves(row.replace(b"blob", b"tree") + b"\x00")
        with self.assertRaisesRegex(Hold, "TREE_PATH_COLLISION"):
            root_oid({"a": Entry("100644", self.blob), "a/b": Entry("100644", self.blob)})

    def test_replace_ref_cannot_substitute_commit(self):
        empty = self.commit(self.tree(""))
        other = self.commit(self.tree(f"100644 blob {self.blob}\ta\n"))
        self.git("replace", empty, other)
        self.assertEqual(read_snapshot(self.repo / ".git", empty).entries, {})


if __name__ == "__main__":
    unittest.main()
