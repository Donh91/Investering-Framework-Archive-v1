"""Exact PR-head object access for tests; never turn a full clone shallow."""
import re
import subprocess


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, timeout=60).stdout


def ensure_exact_pr_head(root, head):
    if not isinstance(head, str) or not re.fullmatch(r"[0-9a-f]{40}", head):
        raise ValueError("EXACT_PR_HEAD_INVALID")
    current = git(root, "rev-parse", "HEAD").decode().strip()
    shallow = git(root, "rev-parse", "--is-shallow-repository").decode().strip()
    if shallow not in {"true", "false"}:
        raise ValueError("EXACT_PR_HEAD_GRAPH_UNKNOWN")
    if shallow == "false":
        # Complete history is authoritative. No fetching or history mutation.
        if git(root, "rev-parse", head + "^{commit}").decode().strip() != head:
            raise ValueError("EXACT_PR_HEAD_OBJECT_MISMATCH")
        git(root, "merge-base", "--is-ancestor", head, "HEAD")
    else:
        # A depth-one PR merge checkout lacks its parent objects, but the
        # commit object's raw parent headers still bind the exact PR head.
        # Never accept an unrelated requested SHA or the base parent.
        raw = git(root, "cat-file", "-p", current).split(b"\n\n", 1)[0]
        parents = [line[7:].decode("ascii") for line in raw.splitlines()
                   if line.startswith(b"parent ")]
        if current != head and not (len(parents) == 2 and parents[1] == head):
            raise ValueError("EXACT_PR_HEAD_NOT_RAW_MERGE_PARENT")
        present = subprocess.run(["git", "-C", str(root), "cat-file", "-e",
                                  head + "^{commit}"], capture_output=True, timeout=10)
        if present.returncode:
            # Only in an ALREADY shallow standalone checkout. The full
            # repository suite must never execute this branch.
            git(root, "fetch", "--no-tags", "--depth=1", "origin", head)
        if git(root, "rev-parse", head + "^{commit}").decode().strip() != head:
            raise ValueError("EXACT_PR_HEAD_OBJECT_MISMATCH")
    if git(root, "rev-parse", "HEAD").decode().strip() != current:
        raise ValueError("EXACT_PR_HEAD_CHECKOUT_CHANGED")
    if git(root, "rev-parse", "--is-shallow-repository").decode().strip() != shallow:
        raise ValueError("EXACT_PR_HEAD_GRAPH_MODE_CHANGED")
    return head
