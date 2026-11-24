"""Fake GitHub + fault injection for txn.py. In memory only; nothing here is authority.

The fake keeps GROUND TRUTH (who really merged, with what) that the kernel can
never read; violations() judges the kernel's receipts against that truth with its
own parser, so a broken kernel cannot vouch for itself.
"""
import hashlib
import importlib.util
import pathlib
import sys

_P = pathlib.Path(__file__).resolve().parent / "txn.py"
_S = importlib.util.spec_from_file_location("s1_root_v2_txn", _P)
txn = importlib.util.module_from_spec(_S)
sys.modules[_S.name] = txn
_S.loader.exec_module(txn)

LEDGER, LOGIN = 1156, "Donh91"
INTENT, RCPT, HALT, DONE = "S1_LANE_MERGE_INTENT_v1", "S1_LANE_MERGE_v1", "S1_LANE_HALTED", "S1_OP_DONE_v1"
TAMPERS = ("subject", "blobs", "two_parent", "bypass", "off_main")
EVENTS = ("main_moves", "owner_push", "owner_merge", "owner_merge_late", "owner_merge_2p",
          "owner_push_merge", "other_login_merge", "owner_note", "foreign_halt")
MODES = ("lost", "error")      # lost: applied, response lost; error: not applied, call failed


def sha(*parts):
    return hashlib.sha1(repr(parts).encode()).hexdigest()


def fields(c):
    lines = c["body"].split("\n")
    return lines[0], dict(ln.split(": ", 1) for ln in lines[1:] if ": " in ln)


class FakeGitHub:
    PR, REPO = 7, 424242

    def __init__(self, tamper=None):
        self.now, self.seq, self.tamper = 1_700_000_000, 0, tamper
        self.commits, self.files, self.bypass, self.log, self.poster = {}, {}, set(), [], {}
        self.main = self._commit([], "root", {})
        self.pr = dict(number=self.PR, state="open", merged=False, head=None, merged_at=None,
                       merge_commit_sha=None, merged_by=None)
        self.comments = {LEDGER: [], self.PR: []}
        self.push()

    def _commit(self, parents, subject, files):
        self.seq += 1
        s = sha("commit", self.seq)
        self.commits[s] = dict(sha=s, parents=list(parents), subject=subject, files=dict(files))
        return s

    def push(self):
        self.seq += 1
        self.pr["head"] = h = sha("head", self.seq)
        self.files[h] = {"research/note.md": sha("blob", self.seq)}

    def candidate(self):
        """What a passed F1-F6 qualification hands to the transaction."""
        h = self.pr["head"]
        return dict(repo_id=self.REPO, pr=self.PR, head=h, base_main=self.main,
                    loop_blob=sha("loop"), head_blobs=dict(self.files[h]))

    def post(self, issue, body, tid=None, author=LOGIN):
        self.seq += 1
        c = dict(id=self.seq, author=author, created_at=self.now, updated_at=self.now, body=body)
        self.comments[issue].append(c)
        self.poster[c["id"]] = tid
        return dict(c)

    def merge(self, actor, sha_arg, method="squash", login=LOGIN, tid=None):
        prior = any(fields(c)[0] == INTENT and fields(c)[1].get("head") == sha_arg
                    and self.poster[c["id"]] == tid for c in self.comments[LEDGER])
        e = dict(actor=actor, sha=sha_arg, applied=False, prior_intent=prior)
        self.log.append(e)
        p, t = self.pr, self.tamper
        if p["merged"] or p["state"] != "open":
            raise txn.NativeError(405)
        if sha_arg is not None and sha_arg != p["head"]:
            raise txn.NativeError(409)
        files = dict(self.files[p["head"]])
        if t == "blobs":
            files["scripts/evil.py"] = sha("evil")
        two = method == "merge" or t == "two_parent"
        m = self._commit([self.main] + ([p["head"]] if two else []),
                         "Change" if t == "subject" else "Change (#%d)" % self.PR, files)
        if t == "bypass":
            self.bypass.add(m)
        self.main = self._commit([self.main], "rewritten", {}) if t == "off_main" else m
        p.update(state="closed", merged=True, merged_at=self.now, merge_commit_sha=m, merged_by=login)
        e.update(applied=True, head=p["head"])
        return {"merged": True, "sha": m}

    def compare(self, a):
        seen, todo = set(), [self.main]
        while todo:
            s = todo.pop()
            if s not in seen:
                seen.add(s)
                todo += self.commits[s]["parents"]
        return "identical" if a == self.main else "ahead" if a in seen else "diverged"

    def call(self, tid, req):
        """One native call by an S1 tick."""
        self.now += 1
        op, a = req[0], req[1:]
        if op == "list_comments":
            return [dict(c) for c in self.comments[a[0]]]
        if op == "post_comment":
            return self.post(a[0], a[1], tid)
        if op == "get_pr":
            return dict(self.pr)
        if op == "merge":
            return self.merge("s1", a[1], a[2], tid=tid)
        if op == "get_commit":
            c = self.commits[a[0]]
            return dict(c, parents=list(c["parents"]), files=dict(c["files"]))
        if op == "compare":
            return self.compare(a[0])
        if op == "rule_suite":
            return "bypass" if a[0] in self.bypass else "pass"
        if op == "pr_files":
            return dict(self.files[self.pr["head"]])
        raise AssertionError(op)

    def event(self, name):
        """Something that is not the tick acts. The owner uses the SAME login as S1."""
        try:
            if name == "main_moves":
                self.main = self._commit([self.main], "data", {})
            elif name == "owner_push":
                if not self.pr["merged"]:
                    self.push()
            elif name == "owner_merge":
                self.merge("owner", None)
            elif name == "owner_merge_late":
                self.now += txn.WINDOW_S + 1
                self.merge("owner", None)
            elif name == "owner_merge_2p":
                self.merge("owner", None, method="merge")
            elif name == "owner_push_merge":
                if not self.pr["merged"]:
                    self.push()
                self.merge("owner", None)
            elif name == "other_login_merge":
                self.merge("other", None, login="someone-else")
            elif name == "owner_note":
                self.post(LEDGER, "OWNER_MERGE_NOTE_v1\npr: %d" % self.PR)
            elif name == "foreign_halt":
                self.post(LEDGER, HALT + "\npr: -\nhead: -\nreason: main_health")
            else:
                raise AssertionError(name)
        except txn.NativeError:
            pass


class Proc:
    """One S1 run, advanced one native call at a time (so runs can be interleaved,
    crashed between calls, or handed a lost response)."""

    def __init__(self, gh, cand, tid):
        self.gh, self.tid, self.gen = gh, tid, txn.tick(cand)
        self.calls, self.out, self.done = [], None, False
        self._advance(lambda: next(self.gen))

    def _advance(self, f):
        try:
            req = f()
            while req[0] == "date":
                req = self.gen.send(self.gh.now)
            self.req = req
        except StopIteration as s:
            self.done, self.out = True, s.value

    def step(self, fault=None):
        req = self.req
        self.calls.append(req[0])
        try:
            if fault == "error":
                self.gh.now += 1
                raise txn.NativeError("timeout")
            res = self.gh.call(self.tid, req)
            if fault == "lost":
                raise txn.NativeError("timeout")
        except txn.NativeError as e:
            return self._advance(lambda: self.gen.throw(e))
        self._advance(lambda: self.gen.send(res))

    def run(self):
        while not self.done:
            self.step()
        return self


def recover(gh, cand, n, outs):
    for r in range(n):
        gh.now += txn.SETTLE_S + 1
        outs.append(Proc(gh, cand, "r%d" % r).run().out)


def scenario(crash=None, fault=None, event=None, tamper=None, crash2=None, ticks=3):
    """Tick t1 under faults, then hourly recovery ticks with the same (now stale) candidate.
    crash=k: t1 dies before its call k (= after call k-1).   fault=(k, mode).
    event=(k, name): fires before t1's call k, or after t1 if it ends earlier.
    crash2=k: the first recovery tick dies before its call k."""
    gh = FakeGitHub(tamper)
    cand, p, k, fired, outs = gh.candidate(), None, 0, False, []
    p = Proc(gh, cand, "t1")
    while not p.done:
        if event and event[0] == k:
            gh.event(event[1])
            fired = True
        if crash == k:
            break
        p.step(fault[1] if fault and fault[0] == k else None)
        k += 1
    if event and not fired:
        gh.event(event[1])
    outs.append(p.out if p.done else None)
    if crash2 is not None:
        gh.now += txn.SETTLE_S + 1
        q = Proc(gh, cand, "c2")
        while not q.done and len(q.calls) < crash2:
            q.step()
        outs.append(q.out if q.done else None)
    recover(gh, cand, ticks, outs)
    return gh, cand, outs


def interleavings(make, switches=None):
    """Every schedule of two concurrent runs (stateless DFS by re-execution); with
    `switches`, every schedule of at most that many context switches.
    make() -> (gh, cand, [proc_a, proc_b]). Yields (gh, cand, procs, schedule)."""
    stack = [()]
    while stack:
        prefix = stack.pop()
        gh, cand, procs = make()
        trace = []
        while not (procs[0].done and procs[1].done):
            live = [x for x in (0, 1) if not procs[x].done]
            c = live[0]
            if len(live) == 2:
                if len(trace) < len(prefix):
                    c = prefix[len(trace)]
                else:
                    c = trace[-1] if trace else 0
                    alt = tuple(trace) + (1 - c,)
                    if switches is None or sum(x != y for x, y in zip(alt, alt[1:])) <= switches:
                        stack.append(alt)
                trace.append(c)
            procs[c].step()
        yield gh, cand, procs, tuple(trace)


def duplicate_ticks():
    """Two runs of the same plan, started together on a fresh PR."""
    def make():
        gh = FakeGitHub()
        cand = gh.candidate()
        return gh, cand, [Proc(gh, cand, "a"), Proc(gh, cand, "b")]
    return interleavings(make)


def duplicate_reconcilers(crash, switches=3):
    """t1 crashes before call `crash`; an hour later two runs reconcile concurrently."""
    def make():
        gh = FakeGitHub()
        cand = gh.candidate()
        p = Proc(gh, cand, "t1")
        while not p.done and len(p.calls) < crash:
            p.step()
        gh.now += txn.SETTLE_S + 1
        return gh, cand, [Proc(gh, cand, "a"), Proc(gh, cand, "b")]
    return interleavings(make, switches)


def summary(gh):
    """The settled outcome of the scenario, from the ledger."""
    ks = [fields(c) for c in gh.comments[LEDGER]]
    if any(k == RCPT for k, f in ks):
        return "MERGED:" + next(f["merge_execution_origin"] for k, f in ks if k == RCPT)
    if any(k == HALT and f.get("pr") == str(gh.PR) for k, f in ks):
        return "HALTED"
    done = [f["result"] for k, f in ks if k == DONE]
    return done[-1] if done else "NO_TRANSACTION"


def violations(gh, cand, concurrent=False):
    """Safety and settlement properties, judged against ground truth. [] is clean."""
    v, led, p = [], gh.comments[LEDGER], gh.pr
    ks = [(c, *fields(c)) for c in led]
    s1 = [e for e in gh.log if e["actor"] == "s1"]
    applied = [e for e in gh.log if e["applied"]]
    if len(s1) > 1:
        v.append("duplicate_merge_attempt")
    if len(applied) > 1:
        v.append("duplicate_merge")
    for e in s1:
        if not e["prior_intent"]:
            v.append("merge_without_prior_intent")
        if e["sha"] != cand["head"]:
            v.append("merge_of_non_intent_head")
    rcpts = [(c, f) for c, k, f in ks if k == RCPT]
    for c, k, f in ks:
        if k != INTENT:
            continue
        if f["head"] != cand["head"]:
            v.append("intent_rebound_to_other_head")
        later = [(k2, f2) for c2, k2, f2 in ks if c2["id"] > c["id"]]
        if not any((k2 in (RCPT, HALT) and f2.get("pr") == str(gh.PR))
                   or (k2 == DONE and f2.get("intent") == str(c["id"])) for k2, f2 in later):
            v.append("intent_left_open")
        cited = [k2 + ":" + f2.get("result", "") for k2, f2 in later if f2.get("intent") == str(c["id"])]
        if len(set(cited)) > 1:
            v.append("conflicting_outcomes")
        if len(cited) > 1 and not concurrent:
            v.append("duplicate_outcome")
    for c, f in rcpts:
        i = next((c2 for c2, k2, f2 in ks if k2 == INTENT and str(c2["id"]) == f.get("intent")), None)
        m = gh.commits.get(p["merge_commit_sha"])
        good = (i is not None and p["merged"] and p["head"] == f["head"] == cand["head"]
                and f["merge"] == p["merge_commit_sha"] and len(m["parents"]) == 1
                and m["subject"].endswith("(#%d)" % gh.PR) and m["files"] == gh.files[p["head"]]
                and gh.compare(m["sha"]) != "diverged" and m["sha"] not in gh.bypass
                and p["merged_by"] == LOGIN
                and i["created_at"] < p["merged_at"] <= i["created_at"] + txn.WINDOW_S)
        if not good:
            v.append("unverified_reported_as_success")
        if f["merge_execution_origin"] == "S1_RUN" and not (applied and applied[0]["actor"] == "s1"):
            v.append("false_s1_origin")
        if f["reconciled"] == "True" and any(k2 == "OWNER_MERGE_NOTE_v1" and c2["id"] < c["id"]
                                             for c2, k2, f2 in ks):
            v.append("success_despite_owner_marker")
        kinds = {fields(x)[0] for x in gh.comments[gh.PR] if fields(x)[1].get("key") == f["key"]}
        if not {"S1_ITEM_v1", "S1_CLOSURE_v1"} <= kinds:
            v.append("merge_receipt_without_closure")
    if len(rcpts) > 1 and not concurrent:
        v.append("duplicate_merge_receipt")
    if applied and applied[0]["actor"] == "s1" and not rcpts and not any(
            k == HALT and f.get("pr") == str(gh.PR) for c, k, f in ks):
        v.append("s1_merge_unaccounted")
    return v


def measure_call_counts():
    """Actual native calls per path: {path: (total, [ops])}."""
    out = {}

    def calls(name, gh, cand, tid="m"):
        p = Proc(gh, cand, tid).run()
        out[name] = (len(p.calls), p.calls)
        return p

    gh = FakeGitHub()
    calls("ordinary_merge", gh, gh.candidate())
    gh = FakeGitHub()
    cand = gh.candidate()
    gh.push()
    calls("noop_head_changed", gh, cand)
    gh = FakeGitHub()
    gh.event("foreign_halt")
    calls("noop_lane_halted", gh, gh.candidate())
    for name, crash, ev in (("reconcile_own", 5, None), ("reconcile_absent", 4, None),
                            ("reconcile_foreign", 4, "owner_push_merge")):
        gh = FakeGitHub()
        cand = gh.candidate()
        p = Proc(gh, cand, "t1")
        while len(p.calls) < crash:
            p.step()
        if name == "reconcile_absent":
            calls("noop_intent_young", gh, cand)
        if ev:
            gh.event(ev)
        gh.now += txn.SETTLE_S + 1
        calls(name, gh, cand)
    return out


if __name__ == "__main__":
    for name, (n, ops) in measure_call_counts().items():
        print("%-20s %2d  %s" % (name, n, " ".join(ops)))
