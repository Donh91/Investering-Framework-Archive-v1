"""D1 research candidate: pure content-neutral branch update proof, never authority.

No network, writes, scheduler, credentials or release decisions. Input completeness
and commit/tree bindings must be established by an independent native reader.
"""
from dataclasses import dataclass
import re

SHA = re.compile(r"[0-9a-f]{40}\Z")
MODES = {"100644", "100755"}


class Hold(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise Hold(reason)


def sha_ok(value):
    return isinstance(value, str) and SHA.fullmatch(value) is not None


def path_ok(path):
    return (isinstance(path, str) and bool(path) and "\x00" not in path
            and all(part not in ("", ".", "..", ".git") for part in path.split("/")))


@dataclass(frozen=True)
class Entry:
    mode: str
    sha: str


@dataclass(frozen=True)
class Snapshot:
    commit: str
    tree: str
    complete: bool
    entries: dict  # flattened leaf path -> Entry; directories omitted


@dataclass(frozen=True)
class Plan:
    base: str
    head: str
    main: str
    main_tree: str
    changes: tuple  # (path, Entry or None), sorted
    expected: tuple  # all final leaf paths and modes/blobs, sorted


def checked(snapshot):
    require(isinstance(snapshot, Snapshot) and snapshot.complete is True, "TREE_INCOMPLETE")
    require(sha_ok(snapshot.commit) and sha_ok(snapshot.tree), "TREE_BINDING_INVALID")
    require(isinstance(snapshot.entries, dict), "TREE_INVALID")
    paths = set(snapshot.entries)
    for path, entry in snapshot.entries.items():
        require(path_ok(path) and isinstance(entry, Entry) and sha_ok(entry.sha), "ENTRY_INVALID")
        require(entry.mode in MODES | {"120000", "160000"}, "MODE_INVALID")
        parts = path.split("/")
        require(not any("/".join(parts[:i]) in paths for i in range(1, len(parts))), "PATH_COLLISION")
    return snapshot.entries.copy()


def delta(a, b):
    return {p for p in a.keys() | b.keys() if a.get(p) != b.get(p)}


def related(a, b):
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def directories(entries):
    return {"/".join(p.split("/")[:i]) for p in entries for i in range(1, len(p.split("/")))}


def vanished_directory(base, added_side, other_side):
    vanished = directories(base) - directories(other_side)
    return any("/".join(p.split("/")[:i]) in vanished
               for p in added_side.keys() - base.keys()
               for i in range(1, len(p.split("/"))))


def propose(base, head, main, *, pr_paths, pr_complete, native_merge_base,
            current_head, owner_gated, writer_clear, historical_overlap_clear):
    """Only construct an advisory plan; caller must retain every live governance gate.

    historical_overlap_clear must be independently proven by the current policy's
    complete native comparison; a capped comparison may never supply True.
    """
    require(owner_gated is False and writer_clear is True, "AUTHORITY_OR_WRITER_HOLD")
    require(historical_overlap_clear is True, "HISTORY_UNPROVEN")
    b, h, m = map(checked, (base, head, main))
    require(native_merge_base == base.commit and current_head == head.commit, "REF_BINDING_CHANGED")
    require(head.commit != main.commit and base.commit != main.commit, "NO_BRANCH_UPDATE")
    require(pr_complete is True and isinstance(pr_paths, dict), "PR_DIFF_INCOMPLETE")
    require(0 < len(pr_paths) <= 100, "PR_DIFF_LIMIT")
    changed = delta(b, h)
    require(changed == set(pr_paths), "PR_DIFF_MISMATCH")
    for p in changed:
        old, new = b.get(p), h.get(p)
        status = "added" if old is None else "removed" if new is None else "modified"
        require(pr_paths[p] == status, "PR_STATUS_MISMATCH")
        require(all(x is None or x.mode in MODES for x in (old, new)), "UNSUPPORTED_PR_MODE")
    require(not any(related(p, q) for p in changed for q in delta(b, m)), "MAIN_OVERLAP")
    require(not (vanished_directory(b, h, m) or vanished_directory(b, m, h)), "DIRECTORY_VANISHED")
    expected = m.copy()
    for p in changed:
        if p in h:
            expected[p] = h[p]
        else:
            expected.pop(p, None)
    checked(Snapshot(main.commit, main.tree, True, expected))
    return Plan(base.commit, head.commit, main.commit, main.tree,
                tuple((p, h.get(p)) for p in sorted(changed)), tuple(sorted(expected.items())))


def verify_readback(plan, *, actual, parents, live_head, native_main):
    """Validate a completed operation; no proof of review, CI or merge authority."""
    require(isinstance(plan, Plan), "PLAN_INVALID")
    actual_entries = checked(actual)
    require(isinstance(parents, (list, tuple)) and tuple(parents) == (plan.head, plan.main), "PARENTS_MISMATCH")
    require(live_head == actual.commit and actual.commit not in (plan.head, plan.main, plan.base), "HEAD_READBACK_MISMATCH")
    require(native_main == plan.main, "MAIN_MOVED_RECHECK")
    require(tuple(sorted(actual_entries.items())) == plan.expected, "TREE_READBACK_MISMATCH")
    return True
