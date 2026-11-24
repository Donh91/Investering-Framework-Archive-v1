import unittest
from dataclasses import replace
from scripts.research.s1_branch_update_candidate_v1 import Entry, Hold, Snapshot, propose, verify_readback


def s(n):
    return f"{n:040x}"


def e(n, mode="100644"):
    return Entry(mode, s(n))


def snap(n, entries, complete=True):
    return Snapshot(s(n), s(n + 100), complete, entries)


class D1Test(unittest.TestCase):
    def setUp(self):
        self.b = snap(1, {"a": e(10), "old": e(11), "ledger": e(12)})
        self.h = snap(2, {"a": e(13, "100755"), "new": e(14), "ledger": e(12)})
        self.m = snap(3, {"a": e(10), "old": e(11), "ledger": e(15)})
        self.kw = dict(pr_paths={"a": "modified", "old": "removed", "new": "added"},
                       pr_complete=True, native_merge_base=s(1), current_head=s(2),
                       owner_gated=False, writer_clear=True, historical_overlap_clear=True)

    def plan(self, **kw):
        return propose(self.b, kw.pop("head", self.h), kw.pop("main", self.m), **(self.kw | kw))

    def test_positive_and_exact_readback(self):
        p = self.plan()
        expected = {"a": e(13, "100755"), "new": e(14), "ledger": e(15)}
        self.assertEqual(dict(p.expected), expected)
        self.assertEqual(dict(p.changes), {"a": e(13, "100755"), "new": e(14), "old": None})
        self.assertTrue(verify_readback(p, actual=snap(4, expected), parents=[s(2), s(3)], live_head=s(4), native_main=s(3)))

    def test_authority_and_incomplete_evidence(self):
        for kw in (dict(owner_gated=True), dict(owner_gated=None), dict(writer_clear=False),
                   dict(writer_clear=None), dict(historical_overlap_clear=False), dict(historical_overlap_clear=None),
                   dict(pr_complete=False), dict(current_head=s(9)), dict(native_merge_base=s(9)),
                   dict(main=replace(self.m, complete=False)), dict(pr_paths={"a": "modified"}),
                   dict(pr_paths=self.kw["pr_paths"] | {"a": "renamed"})):
            with self.subTest(kw=kw), self.assertRaises(Hold):
                self.plan(**kw)

    def test_shared_path_and_mode_only_conflict(self):
        for new in (e(30), e(10, "100755"), e(13, "100755")):
            with self.subTest(new=new), self.assertRaisesRegex(Hold, "MAIN_OVERLAP"):
                self.plan(main=replace(self.m, entries=self.m.entries | {"a": new}))

    def test_ancestor_conflict(self):
        m = replace(self.m, entries=self.m.entries | {"new/child": e(20)})
        with self.assertRaisesRegex(Hold, "MAIN_OVERLAP"):
            self.plan(main=m)
        h = replace(self.h, entries={"a": e(13, "100755"), "new/child": e(14), "ledger": e(12)})
        m = replace(self.m, entries=self.m.entries | {"new": e(20)})
        with self.assertRaisesRegex(Hold, "MAIN_OVERLAP"):
            self.plan(head=h, main=m, pr_paths={"a": "modified", "old": "removed", "new/child": "added"})

    def test_invalid_path_and_unsupported_changed_mode(self):
        for path in ("../bad", "/bad", "a//b", "a/b", ".git/config"):
            with self.subTest(path=path), self.assertRaises(Hold):
                self.plan(main=replace(self.m, entries=self.m.entries | {path: e(30)}))
        with self.assertRaisesRegex(Hold, "UNSUPPORTED_PR_MODE"):
            self.plan(head=replace(self.h, entries=self.h.entries | {"new": e(14, "120000")}))

    def test_directory_rename_conflict_both_directions(self):
        self.b = snap(1, {"d/a": e(10), "d/b": e(11)})
        moved = {"e/a": e(10), "e/b": e(11)}
        added = self.b.entries | {"d/new": e(12)}
        with self.assertRaisesRegex(Hold, "^DIRECTORY_VANISHED$"):
            self.plan(head=snap(2, added), main=snap(3, moved), pr_paths={"d/new": "added"})
        with self.assertRaisesRegex(Hold, "^DIRECTORY_VANISHED$"):
            self.plan(head=snap(2, moved), main=snap(3, added),
                      pr_paths={"d/a": "removed", "d/b": "removed", "e/a": "added", "e/b": "added"})

    def test_cap_and_empty_pr_delta(self):
        paths = {f"n{i}": e(1000+i) for i in range(101)}
        with self.assertRaisesRegex(Hold, "^PR_DIFF_LIMIT$"):
            self.plan(head=snap(2, self.b.entries | paths), pr_paths={p: "added" for p in paths})
        with self.assertRaisesRegex(Hold, "^PR_DIFF_LIMIT$"):
            self.plan(head=snap(2, self.b.entries), pr_paths={})

    def test_exact_snapshot_guards(self):
        for change, reason in [
            (dict(commit="bad"), "TREE_BINDING_INVALID"),
            (dict(tree="bad"), "TREE_BINDING_INVALID"),
            (dict(entries=self.m.entries | {"other": Entry("100644", "bad")}), "ENTRY_INVALID"),
            (dict(entries=self.m.entries | {"other": e(20, "100600")}), "MODE_INVALID"),
            (dict(entries=self.m.entries | {"a/child": e(20)}), "PATH_COLLISION"),
            (dict(entries=self.m.entries | {"bad\x00path": e(20)}), "ENTRY_INVALID"),
        ]:
            with self.subTest(change=change), self.assertRaisesRegex(Hold, "^"+reason+"$"):
                self.plan(main=replace(self.m, **change))

    def test_old_special_mode_and_no_update(self):
        self.b = replace(self.b, entries=self.b.entries | {"a": e(10, "120000")})
        m = replace(self.m, entries=self.m.entries | {"a": e(10, "120000")})
        with self.assertRaisesRegex(Hold, "^UNSUPPORTED_PR_MODE$"):
            self.plan(main=m)
        with self.assertRaisesRegex(Hold, "^NO_BRANCH_UPDATE$"):
            self.plan(main=replace(m, commit=s(2)))

    def test_readback_rejects_old_commit_and_invalid_plan(self):
        p = self.plan()
        for n in (1, 2, 3):
            with self.subTest(n=n), self.assertRaisesRegex(Hold, "^HEAD_READBACK_MISMATCH$"):
                verify_readback(p, actual=snap(n, dict(p.expected)), parents=[s(2), s(3)], live_head=s(n), native_main=s(3))
        with self.assertRaisesRegex(Hold, "^PLAN_INVALID$"):
            verify_readback(None, actual=snap(4, dict(p.expected)), parents=[s(2), s(3)], live_head=s(4), native_main=s(3))

    def test_readback_rejects_losses_and_races(self):
        p = self.plan()
        expected = dict(p.expected)
        args = dict(actual=snap(4, expected), parents=[s(2), s(3)], live_head=s(4), native_main=s(3))
        for changes in (dict(parents=[s(3), s(2)]), dict(live_head=s(5)), dict(native_main=s(5)),
                        dict(actual=snap(4, expected | {"ledger": e(12)})),
                        dict(actual=snap(4, expected | {"a": e(13)})),
                        dict(actual=snap(4, expected | {"extra": e(40)})),
                        dict(actual=snap(4, {k: v for k, v in expected.items() if k != "new"})),
                        dict(actual=snap(4, expected, False))):
            with self.subTest(changes=changes), self.assertRaises(Hold):
                verify_readback(p, **(args | changes))


if __name__ == "__main__":
    unittest.main()
