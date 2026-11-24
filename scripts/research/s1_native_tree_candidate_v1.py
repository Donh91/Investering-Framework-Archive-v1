"""D5 read-only local Git evidence, not authorization or a live S1 connector.

Only a trusted, independently provisioned local object store is supported. No
fetch, checkout, ref update, credential, scheduler or merge authority. A commit
hash proves object identity, not that a remote ref currently points to it.
"""
from hashlib import sha1
import os
from pathlib import Path
import subprocess

from scripts.research.s1_branch_update_candidate_v1 import Entry, Hold, Snapshot, sha_ok

MAX_BYTES = 96 * 1024 * 1024
MAX_ENTRIES = 500_000
MODES = {"100644", "100755", "120000", "160000"}


def oid(kind, raw):
    return sha1(kind.encode() + b" " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()


def root_oid(entries):
    """Rebuild Git SHA-1 tree objects, including executable and gitlink modes."""
    if not isinstance(entries, dict) or len(entries) > MAX_ENTRIES:
        raise Hold("TREE_LIMIT")
    root = {}
    for path, entry in entries.items():
        if not isinstance(path, str) or not isinstance(entry, Entry) or not sha_ok(entry.sha) or entry.mode not in MODES:
            raise Hold("TREE_ENTRY_INVALID")
        parts = path.split("/")
        if len(parts) > 64 or any(not p or p in (".", "..") or "\x00" in p for p in parts):
            raise Hold("TREE_PATH_INVALID")
        node = root
        for part in parts[:-1]:
            node = node.setdefault(part, {})
            if not isinstance(node, dict):
                raise Hold("TREE_PATH_COLLISION")
        if parts[-1] in node:
            raise Hold("TREE_PATH_COLLISION")
        node[parts[-1]] = entry

    def encode(node):
        items = []
        for name, value in node.items():
            try:
                raw_name = name.encode("utf-8", "strict")
            except UnicodeError as exc:
                raise Hold("TREE_PATH_ENCODING") from exc
            directory = isinstance(value, dict)
            mode = "40000" if directory else value.mode
            digest = encode(value) if directory else value.sha
            items.append((raw_name + (b"/" if directory else b""),
                          mode.encode() + b" " + raw_name + b"\x00" + bytes.fromhex(digest)))
        return oid("tree", b"".join(raw for _, raw in sorted(items)))

    return encode(root)


def parse_leaves(raw):
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        raise Hold("TREE_BYTES_LIMIT")
    if raw and not raw.endswith(b"\x00"):
        raise Hold("TREE_TRUNCATED")
    records = raw.split(b"\x00")[:-1]
    if len(records) > MAX_ENTRIES:
        raise Hold("TREE_LIMIT")
    entries = {}
    try:
        for record in records:
            metadata, name = record.split(b"\t", 1)
            mode, kind, digest = metadata.decode("ascii").split(" ")
            path = name.decode("utf-8", "strict")
            if mode not in MODES or kind != ("commit" if mode == "160000" else "blob") or not sha_ok(digest) or path in entries:
                raise Hold("TREE_ENTRY_INVALID")
            entries[path] = Entry(mode, digest)
    except (ValueError, UnicodeError) as exc:
        if isinstance(exc, Hold):
            raise
        raise Hold("TREE_RECORD_INVALID") from exc
    return entries


def read_snapshot(git_dir, commit):
    """Exact SHA only. Read the commit and complete leaf listing, recompute tree.

    Missing objects, unsupported encodings, empty nested trees, limits, shallow
    ancestry and unsupported hash formats are not silently treated as complete.
    This proves a snapshot only, not ancestry, remote head or overlap history.
    """
    if not sha_ok(commit):
        raise Hold("COMMIT_SHA_INVALID")
    path = Path(git_dir).resolve(strict=True)
    if not path.is_dir():
        raise Hold("OBJECT_STORE_INVALID")
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_TERMINAL_PROMPT="0", GIT_NO_LAZY_FETCH="1")

    def read(*args):
        try:
            p = subprocess.run(["git", "--no-replace-objects", "--git-dir=" + str(path),
                                "-c", "protocol.allow=never", *args], env=env,
                               stdin=subprocess.DEVNULL, capture_output=True, timeout=45, check=True)
        except (OSError, subprocess.SubprocessError) as exc:
            raise Hold("NATIVE_OBJECT_UNREADABLE") from exc
        if len(p.stdout) > MAX_BYTES:
            raise Hold("TREE_BYTES_LIMIT")
        return p.stdout

    raw = read("cat-file", "commit", commit)
    if oid("commit", raw) != commit:
        raise Hold("COMMIT_HASH_MISMATCH")
    first = raw.split(b"\n", 1)[0]
    try:
        tree = first.removeprefix(b"tree ").decode("ascii")
    except UnicodeError as exc:
        raise Hold("COMMIT_TREE_INVALID") from exc
    if not first.startswith(b"tree ") or not sha_ok(tree):
        raise Hold("COMMIT_TREE_INVALID")
    entries = parse_leaves(read("ls-tree", "-r", "-z", "--full-tree", tree))
    if root_oid(entries) != tree:
        raise Hold("TREE_HASH_MISMATCH")
    return Snapshot(commit, tree, True, entries)
