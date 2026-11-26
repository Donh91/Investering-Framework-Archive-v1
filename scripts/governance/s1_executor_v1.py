"""S1 executor: the job `execute` of .github/workflows/s1-executor.yml performs the ONE action of S1_DECISION_V1.

AGENTS.md section 0.2i ("S1 is GitHub"). The build job of a run of .github/workflows/s1-tick-brief.yml read GitHub
natively and decided (s1_decision_v1.decide), and its publish job wrote the brief issue. Fix round 6 (F2): this job is
its OWN workflow, started only by a completed, SUCCESSFUL scheduled or manual run of that brief workflow on main, so the
brief's run conclusion (TICK.md T2 run_not_success, and the next build's C1b anchor) never depends on the executor: an
executor that fails, is cancelled or times out ends its own run, never the brief's. It reads the published brief issue
(the brief of exactly that run) and re-reads every fact of that one action natively, immediately before it writes, and
writes only when the switch 00_FMOS/S1/REVIEWED_MERGE_LANE.json on main reads "executor": "LIVE" (missing or unknown:
OFF) and the owner's repository variable S1_EXECUTOR_HOLD is empty. In SHADOW it makes the same reads and prints what
it WOULD do; it never writes. It runs main's own code only and never checks out, imports or executes a PR head.

The only writes this file can make (write() is the one call site of each):
  POST   /repos/<repo>/issues/1156/comments  an S1_LANE_MERGE_INTENT_v1, S1_LANE_MERGE_v1, S1_LANE_HALTED, S1_OP_DONE_v1,
                                             S1_HEARTBEAT_v1, S1_FALLBACK_CANDIDATE_v1, S1_CODEX_RECALL_PENDING_v1 or
                                             S1_CODEX_RECALL_CLEARED_v1 on the owner ledger
  PUT    /repos/<repo>/pulls/<n>/merge       {"merge_method": "squash", "sha": <the decision's exact head>}
  POST   /repos/<repo>/issues/<n>/labels     the ONE label codex-recall-pending, on the PR this run merged by the fallback
  DELETE /repos/<repo>/issues/<n>/labels/codex-recall-pending   after this run itself read Codex's completed review

Review route (owner decision 2026-11-25): a merge needs the completed Codex review, a Claude exact-head APPROVE receipt
on the PR, or the Codex-offline fallback. The fallback is TWO executor runs: the first posts S1_FALLBACK_CANDIDATE_v1
with a hash of what it derived; a later run (another run id, at least 50 minutes on, the candidate proven to be an
executor run's) derives everything again from its own reads and merges only when its hash is equal. Such a merge is
flagged for Codex to revisit (ledger receipt and label) until Codex's completed review of that head.
A merge is ONE per run, always intent first, readback after, receipt or halt last (EVIDENCE_BINDINGS B3, C9, C10).
ONE attempt per PR head, ever: a refused or failed merge is never retried at that head (a new commit is a new head).

No silent failure: the result lines go to the job summary, and the process exits non-zero when an operation was left
without its outcome, a readback did not match, a read stopped after a write, or anything unexpected was raised. That
exit fails this workflow's own run only (fix round 6, F2); the run that carries the brief has already concluded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import s1_decision_v1 as D  # noqa: E402
import s1_tick_brief_v1 as B  # noqa: E402

EXECUTE_API_CALLS = 220                # this job's own cap (the build is capped at 300). One PR is verified twice (fix round 4, #2:
                                       # the final look re-derives every gate after the intent), about 40 reads each
MAX_WRITES = 8                         # heartbeat, one recall clear (receipt, label), intent, merge, receipt or halt, recall flag (receipt, label)
# Fix round 5 (#173/7190895883 D04): what a merge needs AFTER its intent is reserved BEFORE the intent. Measured on the
# fake (Harness): the final look, the merge call, the readback and the receipts take 38 calls after the intent on route
# (a) and 47 on route (c); 80 leaves room for the paged reads of a busier PR. Writes: intent, merge, receipt or halt,
# recall receipt, label.
MERGE_CALL_RESERVE = 80
MERGE_WRITE_RESERVE = 5
RECONCILES_PER_RUN = 3                 # EVIDENCE_BINDINGS op_reconciles_per_run
MAX_ATTEMPTS_PER_HEAD = 1              # merge intents per PR head, ever: a refused merge is NOT retried, that head is the owner's
EVENTS = ("schedule", "workflow_dispatch")      # the events of the BRIEF run this executor run may act for
EXECUTOR_TRIGGER = "workflow_run"              # fix round 6 (F2): the event of this executor run itself
# Trigger round (2026-11-26): GitHub creates no workflow_run event for a brief run that the metronome dispatched with the
# workflow token, so such a brief never started the executor. The metronome now also dispatches s1-executor.yml; such a
# run has no triggering run, resolves the brief to evaluate from the PUBLISHED brief issue (its run_id and run_attempt),
# re-reads that run natively (completed, success, schedule or workflow_dispatch, main, this repository, head = the
# brief's main, the issue not edited after the run) and then takes the same path as a workflow_run.
SELF_TRIGGER = "workflow_dispatch"
BRIEF_ENV = ("S1_BRIEF_RUN_ID", "S1_BRIEF_RUN_ATTEMPT", "S1_BRIEF_MAIN", "S1_BRIEF_EVENT")
# One evaluation per brief run and attempt, whatever started the executor: the earlier executor runs of s1-executor.yml
# on main that ended after the brief was generated are read (one list, then jobs and log of at most EVALUATION_READS of
# them); one whose own health line names this brief run (and attempt) with a result other than NO_DECISION has
# evaluated it. Anything unread is "not proven": no second evaluation.
EXECUTOR_RUNS_PAGE = 30
EVALUATION_READS = 4
EXECUTOR_RUN_MAX_MINUTES = 15          # the job's timeout (10) plus queueing: how far before the window a run may have started
POSTS = ("S1_LANE_MERGE_INTENT_v1", "S1_LANE_MERGE_v1", "S1_LANE_HALTED", "S1_OP_DONE_v1", "S1_HEARTBEAT_v1",
         "S1_FALLBACK_CANDIDATE_v1", "S1_CODEX_RECALL_PENDING_v1", "S1_CODEX_RECALL_CLEARED_v1")
MAX_POST_CHARS = 4000
HOLD_VARIABLE = "S1_EXECUTOR_HOLD"     # read from the job's env at start AND live before the intent and before the merge (live_stop)


BLOCKED, UNVERIFIED, HELD = "BLOCKED", "UNVERIFIED", "HELD"


class Stop(Exception):
    """A check failed: nothing (more) is written in this run. `reason` is the skipped=<...> text. Fix round 5
    (#173/7188234670 P1-08): `kind` says what the stop proves. BLOCKED: a fact was read completely and it blocks (a
    verified "not now"). HELD: the owner's or the lane's stop. UNVERIFIED: something could not be read or proven. The
    default is UNVERIFIED, so a stop nobody classified is never reported as a verified NOOP."""

    def __init__(self, reason, kind=UNVERIFIED):
        super().__init__(reason)
        self.reason, self.kind = reason, kind


def need(ok, reason, kind=UNVERIFIED):
    if not ok:
        raise Stop(reason, kind)


# ----------------------------------------------------------------------------------------------- native git reads
class Native:
    """Git reads of the executor, from main's own checkout (never a PR checkout). Tests replace this object."""

    def __init__(self, root):
        self.root = Path(root)
        self.graph = Path(str(root) + ".due-graph")

    def drift(self, base, head):
        """(relation, paths) of base -> head exactly as the brief's due check reads it (ahead, behind, unknown, too_large)."""
        return B.git_drift(self.root, base, head)

    def head_commit(self):
        """The commit this checkout is at (trigger round: a dispatched run must have checked out the brief's main)."""
        return B.git(self.root, "rev-parse", "--verify", "HEAD")

    def tree_shas(self, commit, paths):
        """{path: blob or tree SHA at `commit`} (None: absent or unreadable)."""
        out = dict.fromkeys(paths)
        if commit not in B.fetch_commits(self.root, [commit], "--depth=1", "--filter=blob:none"):
            return out
        for path in paths:
            try:
                out[path] = B.git(self.root, "rev-parse", "--verify", "--quiet", f"{commit}:{path}") or None
            except Exception:                                    # noqa: BLE001  (absent at that commit)
                out[path] = None
        return out

    def tree_entries(self, commit, paths):
        """{path: entry} at `commit` in the tri-state of D.tree_entry: ("PRESENT", mode, type, sha) from `git ls-tree`,
        ("ABSENT",) only when the commit was fetched and ls-tree read it and listed nothing for that exact path, and
        ("UNREADABLE",) for everything else (fetch failed, git failed, output that does not parse)."""
        out = {p: ("UNREADABLE",) for p in paths}
        if commit not in B.fetch_commits(self.root, [commit], "--depth=1", "--filter=blob:none"):
            return out
        for path in paths:
            try:
                raw = B.git(self.root, "ls-tree", "--full-tree", commit, "--", path)
            except Exception:                                    # noqa: BLE001  (git failed: unknown, never "absent")
                continue
            rows = [line for line in raw.splitlines() if line.strip()]
            if not rows:
                out[path] = ("ABSENT",)
                continue
            m = re.fullmatch(r"([0-7]{6}) (blob|tree|commit) ([0-9a-f]{40})\t(.+)", rows[0])
            if len(rows) == 1 and m and m.group(4) == path:
                out[path] = ("PRESENT", m.group(1), m.group(2), m.group(3))
        return out

    def is_ancestor(self, sha, main):
        """Fix round 5 (D06): True, False (git proved it is not an ancestor) or None (fetch or graph unreadable)."""
        if sha == main:
            return True
        try:
            B.git(self.root, "remote", "get-url", "origin")
            self.graph.mkdir(parents=True, exist_ok=True)
            B.git(self.graph, "init", "--quiet", "--bare")
            if "origin" not in B.git(self.graph, "remote").split():
                B.git(self.graph, "remote", "add", "origin", B.git(self.root, "remote", "get-url", "origin"))
            if not {sha, main} <= B.fetch_commits(self.graph, [sha, main], "--filter=tree:0"):
                return None
        except Exception:                                        # noqa: BLE001
            return None
        return B.ancestry(self.graph, sha, main)

    def changed(self, parent, commit):
        """Fix round 5 (N05): every path `commit` changed against `parent` (both trees, no rename detection), or None."""
        if parent not in B.fetch_commits(self.root, [parent], "--depth=1", "--filter=blob:none") \
                or commit not in B.fetch_commits(self.root, [commit], "--depth=1", "--filter=blob:none"):
            return None
        return B.changed_between(self.root, parent, commit)


# ----------------------------------------------------------------------------------------------- the run
class Run:
    def __init__(self, gh, native, env, files, now_fn=None, out=print):
        self.gh, self.native, self.env, self.files, self.out = gh, native, env, files, out
        self.now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self.writes, self.mode, self.lines, self.ledger_read_at = [], "OFF", [], None
        self.brief = self.decision = None
        self.run_of = B.RunReader(gh)                             # proves which Actions-bot ledger posts are this job's
        self.alarms, self.pending = [], None                      # what makes the process exit non-zero (finish)
        self.recall_cleared = set()                               # PRs whose recall THIS run proved cleared (the label may then go)
        self.cleared_for = None                                   # (pr, head) whose final look after the intent passed (A32)
        self.merge_of = B.MergeReader(gh)                         # the native merge proof behind a merge receipt (A10, fix round 4 #5)
        self.comments = []                                        # the ledger as this run read it (the final look adds what came later)
        self.label_repair = set()                                 # recalled PRs whose missing label THIS run proved natively (fix round 4)
        self.log_of = B.LogReader(gh)                             # fix round 5 (P1-05): the execute log that proves an intent closes older ones
        self.uncertain = []                                       # fix round 5 (P1-08): what this run could not settle or prove (health)
        self.stop_kind = None                                     # the kind of the Stop that ended the run, if one did
        self.verified_main = None                                 # the main the final look verified (D03: the receipt names it)
        self.body = None                                          # the issue body this run executes (D02: re-checked at the boundary)
        self.guard_paths = ()                                     # the PR's path set once verified (live_stop's drift check)
        self.published_issue = None                               # the brief issue number the first publication check read
        self.published_doc = None                                 # trigger round: the brief issue execute_published() read
        self.env = dict(env)                                      # trigger round: a dispatched run adds the S1_BRIEF_* it resolved

    # ---- the ONE place that writes
    def write(self, kind, **kw):
        """kind 'comment' (body=...) or 'merge' (pr=..., sha=...). Refused unless the mode is LIVE, the clock allows a
        write now (H1 is checked before EVERY write), the cap holds and the payload is one of the two allowed shapes."""
        need(self.mode == "LIVE", "executor_not_live")
        need(len(self.writes) < MAX_WRITES, "write_cap")
        self.live_stop(f"write:{kind}")                           # fix round 4 (#11, 7186140947-07): hold, switch and contract, live, before EVERY write
        clock = D.clock_gate(self.now_fn(), self.decision["generated_at"], self.decision["expires_at"], D.EXECUTE_MAX_AGE_MINUTES)
        need(clock is None, f"clock:{clock}", HELD if clock == "MONDAY_READ_ONLY" else UNVERIFIED)
        if kind == "comment":
            body = kw["body"]
            need(isinstance(body, str) and 0 < len(body) <= MAX_POST_CHARS and B.first_line_token(body) in POSTS, "post_shape")
            raw, _h = self.gh._request("POST", self.gh.url(f"issues/{B.OWNER_ISSUE}/comments"), {"body": body})
            doc = json.loads(raw)
            self.writes.append(("comment", B.first_line_token(body), doc.get("id")))
            return doc
        if kind == "label":                                       # the ONE label, added to the PR this run merged or removed after this run's proof
            pr, add = kw["pr"], kw["add"]
            need(type(pr) is int and type(add) is bool, "label_shape")
            if add:
                need(any(w[0] == "merge" and w[1] == pr for w in self.writes) or pr in self.label_repair, "label_without_merge")
                self.gh._request("POST", self.gh.url(f"issues/{pr}/labels"), {"labels": [D.RECALL_LABEL]})
            else:
                need(pr in self.recall_cleared, "label_without_clear")
                self.gh._request("DELETE", self.gh.url(f"issues/{pr}/labels/{D.RECALL_LABEL}"))
            self.writes.append(("label", "add" if add else "remove", pr))
            return None
        need(kind == "merge" and not any(w[0] == "merge" for w in self.writes), "one_merge_per_run")
        pr, sha = kw["pr"], kw["sha"]
        need(type(pr) is int and isinstance(sha, str) and D.SHA40.fullmatch(sha) is not None, "merge_shape")
        need(self.decision.get("action") == "MERGE" and self.decision["merge"]["pr"] == pr and self.decision["merge"]["sha"] == sha, "merge_not_the_decision")
        # ChatGPT audit A32: the gateway itself requires this run's intent for this PR and head on #1156 and a final look
        # passed after it, not only the caller's order of calls
        need(any(w[0] == "comment" and w[1] == "S1_LANE_MERGE_INTENT_v1" for w in self.writes) and self.cleared_for == (pr, sha), "merge_without_intent")
        self.writes.append(("merge", pr, sha))                   # recorded BEFORE the call: an ambiguous answer is never retried
        raw, _h = self.gh._request("PUT", self.gh.url(f"pulls/{pr}/merge"), {"merge_method": "squash", "sha": sha})
        return json.loads(raw)

    def say(self, line):
        line = re.sub(r"[\x00-\x1f\x7f]", " ", str(line))        # one line stays one line, whatever a path or a reason holds
        self.lines.append(line)
        self.out(line)

    # ---- reads shared by several steps
    def ledger(self):
        self.ledger_read_at = B.iso(self.now_fn() - timedelta(seconds=5))   # BEFORE the read: last_look() covers everything after it
        rows, complete = self.gh.pages(f"issues/{B.OWNER_ISSUE}/comments", max_pages=120)
        need(complete, "lane:C7:ledger_unreadable")
        return rows

    def last_look(self):
        """Immediately before the intent: no halt and no other intent reached #1156 since the ledger read (one page)."""
        late = self.gh.get(f"issues/{B.OWNER_ISSUE}/comments", {"since": self.ledger_read_at, "per_page": 100})
        need(isinstance(late, list) and len(late) < 100, "lane:C7:ledger_unreadable")
        need(not B.lane_halts(late), "lane:C7:halt_after_read", HELD)
        need(not any(B.is_s1_author(c) and B.first_line_token(c.get("body")) in ("S1_LANE_MERGE_INTENT_v1", "S1_OP_INTENT_v1") for c in late),
             "lane:C9:intent_after_read", BLOCKED)

    def main_now(self):
        branch = self.gh.get("branches/main")
        sha = (branch.get("commit") or {}).get("sha")
        need(isinstance(sha, str) and D.SHA40.fullmatch(sha) is not None, "main_unreadable")
        return sha, branch.get("protected")

    def no_code_drift(self, main, pr_paths=()):
        """TICK T3 as code: current main is the decision's main or ahead of it by data-only commits that touch no path
        of the PR. Returns the drift paths."""
        base = self.decision["main"]
        if main == base:
            return []
        relation, paths = self.native.drift(base, main)
        need(relation == "ahead" and isinstance(paths, list), f"BRIEF_STALE(drift:{relation})", BLOCKED if relation == "too_large" else UNVERIFIED)
        need(len(paths) < B.DRIFT_MAX_FILES, "BRIEF_STALE(drift_unreadable)")
        code = [p for p in paths if B.code_drift_path(p)]
        need(not code, "BRIEF_STALE(source_changed)", BLOCKED)
        overlap = sorted(set(paths) & set(pr_paths))
        need(not overlap, "C2:needs_branch_update", BLOCKED)
        return paths

    # ---- lane, at current main, from fresh reads
    def pins_at(self, main, where="lane"):
        """Every pin of the switch and every blob of the S1 chain at `main`, by a native git read (fix round 5, P1-09:
        shared by the lane check and the last read before every write)."""
        switch, contract = self.files["switch"], self.files["contract"]
        pins = switch.get("pins") if isinstance(switch, dict) else None
        need(isinstance(pins, dict) and pins, "lane:C7:pins_missing")
        chain = {contract.get("lane_switch_path"): contract.get("lane_switch_blob"), contract.get("action_loop_path"): contract.get("action_loop_blob"),
                 contract.get("tick_path"): contract.get("tick_blob"), **(contract.get("rubric_blobs") or {})}
        want = dict(pins, **chain)
        need(all(isinstance(k, str) and isinstance(v, str) for k, v in want.items()), "lane:C7:contract_unreadable")
        actual = self.native.tree_shas(main, sorted(want) + [B.CONTRACT_FILE])
        for path in sorted(want):
            need(actual.get(path) == want[path], f"lane:C7:pins:{path}" + ("" if where == "lane" else f":{where}"))
        need(actual.get(B.CONTRACT_FILE) == self.decision["contract_blob"], "lane:C7:pins:contract_blob" + ("" if where == "lane" else f":{where}"))

    def lane_now(self, main, protected, comments):
        switch, bindings = self.files["switch"], self.files["bindings"]
        need(isinstance(switch, dict) and switch.get("contract") == "S1_REVIEWED_MERGE_LANE_v1", "lane:C7:switch")
        need(switch.get("state") == "ON", "lane:C7:switch_off", HELD)
        self.pins_at(main)
        halts = B.lane_halts(comments)
        halt = B.standing_halt(halts, switch.get("clears_halt"))
        need(halt is None, f"lane:C7:halt c={halt}", HELD)
        runs, complete = self.gh.pages(f"actions/workflows/{Path(bindings['main_health']['workflow_path']).name}/runs",
                                       {"event": "schedule", "branch": "main"}, key="workflow_runs", max_pages=1)
        # fix round 6 (#173/7194141485 S3): the producer's exact read scope (ROUTE 1: the newest page of 100 runs), proven
        # as that scope, not merely non-empty; and only a proven failure is a verified block (FAIL), every NOT_PROVEN
        # reason (unread, malformed, stale) is UNVERIFIED
        health = B.main_health(runs, B.health_window_ok(runs, complete), self.now_fn(), B.lane_merges(comments), halts, bindings["main_health"])
        need(health.get("status") == "PASS", f"lane:C7:main_health:{health.get('reason')}", BLOCKED if health.get("status") == "FAIL" else UNVERIFIED)
        r1, c1 = self.gh.pages("rulesets", {"includes_parents": "true"}, max_pages=2)
        r2, c2 = self.gh.pages("rulesets", {"includes_parents": "true"}, max_pages=2)
        rules = B.ruleset_census(r1, r2, c1 and c2)
        need(rules.get("stable") is True and rules.get("census") == (self.brief.get("rulesets") or {}).get("census"), "lane:C8:ruleset_census")
        need(type(rules.get("active")) is int, "lane:C8:ruleset_census")
        need(rules["active"] == 0, "lane:C8:ruleset_active", BLOCKED)
        protection_known(protected, "")
        return health

    # ---- MERGE: every fact, natively, right before the write
    def verify_merge(self, comments, own_intent=None):
        d, brief, m = self.decision, self.brief, self.decision["merge"]
        n, head, repo_id = m["pr"], m["sha"], (brief.get("repo") or {}).get("id")
        entry = next((e for e in brief.get("prs") or [] if e.get("n") == n), None)
        need(entry is not None and entry.get("head") == head and not entry.get("open") and not entry.get("skip"), f"{n}:C8:not_the_briefs_candidate")
        need(D.pr_gates(entry, brief["thin"]) == [], f"{n}:C8:decision_gates")
        repo = self.gh.get("")
        need(repo.get("full_name") == B.REPO and repo.get("fork") is False and repo.get("id") == repo_id and type(repo_id) is int, "B1:repository_identity")

        def head_read():
            pr = self.gh.get(f"pulls/{n}")
            need(pr.get("state") == "open" and pr.get("merged") is not True and pr.get("draft") is False, f"{n}:C8:state", BLOCKED)
            need((pr.get("head") or {}).get("sha") == head, f"{n}:C8:head_changed", BLOCKED)
            need((pr.get("base") or {}).get("ref") == "main" and ((pr.get("base") or {}).get("repo") or {}).get("id") == repo_id
                 and ((pr.get("head") or {}).get("repo") or {}).get("id") == repo_id, f"{n}:B1:fork_head", BLOCKED)
            need(pr.get("mergeable") is not False and pr.get("mergeable_state") not in ("dirty", "blocked"), f"{n}:C2:mergeable", BLOCKED)
            return pr

        pr = head_read()
        files, fc = self.gh.pages(f"pulls/{n}/files", max_pages=31)
        need(fc, f"{n}:C8:files_unreadable")
        need(len(files) == pr.get("changed_files") == m.get("files"), f"{n}:C8:files_changed", BLOCKED)
        paths = sorted({f.get("filename") or "" for f in files} | {f["previous_filename"] for f in files if f.get("previous_filename")})
        need(hashlib.sha256("\n".join(paths).encode()).hexdigest()[:16] == m.get("paths_sha256"), f"{n}:C8:files_changed", BLOCKED)
        # risk and exclusions, recomputed from the LIVE diff, title and labels (exclusion 3 is a function of the head and of
        # main's code: the head is unchanged and no_code_drift proves main's code is; the isolation facts themselves are
        # the producer's, from this same run's build job: fix round 5, D05, section 0.2i)
        reasons, floor = B.path_exclusions(files, True, self.files["policy"], self.files["gate_isolation"] == "LIVE", {"owner_gated": [], "high_floor": []})
        need(not reasons and floor in D.MERGE_RISKS, f"{n}:C2:owner_gated", BLOCKED)
        # fix round 5 (#173/7190895883 D05): the push-trigger rule is recomputed HERE from main's own workflow files
        # (a merge made with the workflow token starts no push workflow), not trusted from the brief
        facts = D.entry_facts(pr, files, True, self.files.get("push_filters"))
        need(not facts["x"] and not facts["direction"] and not facts["hold_labels"], f"{n}:C2:judgment", BLOCKED)
        need(not facts["push"], f"{n}:C2:push_trigger:{(facts['push'] or ['-'])[0]}", UNVERIFIED if facts["push"] == ["unknown"] else BLOCKED)
        need(facts["title_sha256"] == m.get("title_sha256"), f"{n}:C8:title_changed", BLOCKED)
        need(not any(f.get("status") not in ("added", "removed", "renamed") and not str(f.get("filename") or "").startswith(("scripts/", "tests/"))
                     and (f.get("deletions") or 0) > (f.get("additions") or 0) for f in files), f"{n}:C2:shrinks", BLOCKED)
        # CI identity (B4), every check, and the one privacy line
        tuples = self.files["bindings"]["required_job_tuples"]
        runs, rc = self.gh.pages("actions/runs", {"head_sha": head, "event": "pull_request"}, key="workflow_runs", max_pages=5)
        jobs = {}
        for path in sorted({t["workflow_path"] for t in tuples}):
            kept = [r for r in runs if r.get("path") == path and r.get("head_sha") == head]
            if kept:
                run = max(kept, key=lambda r: r.get("run_number") or 0)
                rows, jc = self.gh.pages(f"actions/runs/{run['id']}/jobs", {"filter": "latest"}, key="jobs", max_pages=3)
                jobs[run["id"]] = rows if jc else None
        ci = B.ci_tuples(head, repo_id, runs, rc, jobs, tuples)
        ci_ids = {}
        for t in tuples:
            got = ci.get(t["job"]) or {}
            need(got.get("s") == "PASS" and [got.get("run"), got.get("att"), got.get("job")] == (m.get("ci") or {}).get(t["job"]), f"{n}:C4:ci_identity:{t['job']}",
                 UNVERIFIED if got.get("s") == "NOT_PROVEN" else BLOCKED)
            ci_ids[t["job"]] = [got.get("run"), got.get("att"), got.get("job")]
        checks, k1 = self.gh.pages(f"commits/{head}/check-runs", key="check_runs", max_pages=5)
        statuses, k2 = self.gh.pages(f"commits/{head}/statuses", max_pages=3)
        need(B.checks_summary(checks, statuses, k1 and k2).get("green") is True, f"{n}:C4:checks", BLOCKED if k1 and k2 else UNVERIFIED)
        privacy_job = ci["privacy-scan"]["job"]
        line = B.privacy_line(self.gh.text(f"actions/jobs/{privacy_job}/logs"), head)
        need(line.get("result") == "NO_RESTRICTED_CONTENT", f"{n}:C3:privacy_line", BLOCKED if line.get("result") else UNVERIFIED)
        # reviews, threads, writer
        commits, cc = self.gh.pages(f"pulls/{n}/commits", max_pages=3)
        prc, c1 = self.gh.pages(f"issues/{n}/comments", max_pages=10)
        reviews, c2 = self.gh.pages(f"pulls/{n}/reviews", max_pages=10)
        inline, c3 = self.gh.pages(f"pulls/{n}/comments", max_pages=10)
        need(cc and c1 and c2 and c3, f"{n}:C5:reviews_unreadable")
        now = self.now_fn()
        need(B.concurrent_writer(commits, cc, prc, head, now, self.files["bindings"]["foreign_commit_quiet_minutes"]) is None, f"{n}:C1:concurrent_writer", BLOCKED)
        need(B.changes_requested(reviews) is False, f"{n}:C5:changes_requested", BLOCKED)   # on ANY commit: a push never lifts the veto
        item = B.newest_item(prc) or {}                          # the PR's S1_ITEM_v1 history as it is NOW: a risk or kind is only ever raised
        need(item.get("kind") != "DIRECTION", f"{n}:C5:strategist", BLOCKED)
        risk = D.risk_max(floor, facts["risk"], item.get("risk"))
        data_ok = D.data_route(pr, files, True, commits, cc, D.fallback_allowlist(self.files["switch"]))[0]   # addendum c, from THIS run's reads
        author = B.authorship(pr, commits, cc, prc)
        cx = B.codex_review(head, pr, commits, cc, prc, reviews, inline, True, now, self.files["budgets"]["codex_silent_hours"])
        if author.get("codex") and cx.get("status") == "FINAL":
            cx = {"status": "INADMISSIBLE"}
        candidates = B.fallback_candidates(comments).get((n, head), [])
        live = {"review": {"codex": cx}, "author": author, "lane": {"risk_floor": floor}, "item": item,
                "thin": {"bot": (pr.get("user") or {}).get("type") != "User", "docs_only": facts["docs_only"],
                         "ai": B.ai_authored(pr, commits, cc, author), "claude": B.claude_receipt(head, prc),
                         "claude_written": B.claude_written(pr, commits, cc), "data_route": data_ok, "fallback_candidates": len(candidates),
                         "fallback_mismatch": B.fallback_mismatch(candidates), "p01_named": B.p01_named(prc, reviews, inline),
                         "risk": facts["risk"], "codex_offline": self.codex_offline(n, cx, prc, reviews, inline, now) if str(m.get("review")).startswith("FALLBACK(") else None}}
        cfg = D.thin_config(self.files["switch"])
        route, gate = D.review_route(live, cfg["review_policy"], cfg["fallback_route"])   # the route itself is derived again, from this run's reads
        need(gate is None, f"{n}:{gate}", UNVERIFIED if gate == "C5:review_unreadable" else BLOCKED)
        need(route == m.get("review"), f"{n}:C8:review_changed", BLOCKED)
        # fix round 5 (#173/7188234670 P1-03): the HIGH stored-data admission and the word-list exemption hold on route (c) only
        admitted = D.data_fallback(live, route)
        need(risk == m.get("risk") and D.merge_risk_ok(risk, admitted) and admitted is (m.get("data") is True), f"{n}:C2:risk", BLOCKED)
        need(facts["diff_x"] == [] or admitted, f"{n}:C2:judgment:diff", UNVERIFIED if "patch_unread" in facts["diff_x"] else BLOCKED)
        if admitted:                                              # a stored-data merge: every path a plain file at the head (no link, no mode change)
            entries = self.native.tree_entries(head, [f.get("filename") for f in files])
            need(all(v[0] == "PRESENT" and v[1] == "100644" and v[2] == "blob" for v in entries.values()), f"{n}:C2:data_mode",
                 UNVERIFIED if any(v[0] == "UNREADABLE" for v in entries.values()) else BLOCKED)
        evidence = D.fallback_evidence(n, head, risk, len(files), hashlib.sha256("\n".join(paths).encode()).hexdigest()[:16], facts["title_sha256"],
                                       pr.get("body"), ci_ids,
                                       policy=f"{self.decision.get('contract_blob')}:{brief['thin']['review_policy']}")
        try:
            threads = B.read_threads(self.gh, n)
        except (RuntimeError, urllib.error.HTTPError, KeyError, TypeError):   # a GraphQL error or an odd answer: unread (P1-08)
            threads = None
        need(threads is not None, f"{n}:C6:threads")
        need(not any(not t.get("resolved") and re.search(r"(?i)\bP[01]\b", t.get("first_body") or "") for t in threads), f"{n}:C6:unresolved_p0p1", BLOCKED)
        # lane, drift, intents; then the head once more, immediately before the intent
        main, protected = self.main_now()
        self.no_code_drift(main, paths)
        health = self.lane_now(main, protected, comments)
        open_now = B.open_intents(comments, now, 0, self.run_of, self.merge_of, self.log_of)
        need(not any(i.get("kind") == "S1_LANE_MERGE_INTENT_v1" and i.get("id") != own_intent for i in open_now), "lane:C9:open_merge_intent", BLOCKED)
        # idempotency key = PR + head: a receipt for it means done, and an earlier intent for it means it was tried.
        # ONE attempt per head, ever: no retry of a refused merge (the owner merges that head, or a new commit arrives)
        key = re.compile(rf"(?m)^pr: {n}\s*$")
        others = [c for c in comments if own_intent is None or c.get("id") != own_intent]   # the final look excludes this run's own intent
        mine = [B.first_line_token(c.get("body")) for c in others if B.is_s1_author(c) and key.search(str(c.get("body") or ""))
                and head in str(c.get("body") or "")]
        need("S1_LANE_MERGE_v1" not in mine, f"{n}:C9:already_done", BLOCKED)
        need(mine.count("S1_LANE_MERGE_INTENT_v1") < MAX_ATTEMPTS_PER_HEAD and (n, head) not in B.attempted_heads(others), f"{n}:C9:attempted_head", BLOCKED)
        head_read()                                              # the head a SECOND time, the last read before the intent
        return {"paths": paths, "files": files, "head_read": head_read, "main": main, "privacy_run": ci["privacy-scan"]["run"], "repo_id": repo_id, "health": health,
                "evidence": evidence, "candidates": candidates, "offline": route[9:-1] if route.startswith("FALLBACK(") else None,
                "claude": B.claude_receipt_fields(head, prc) if route == "CLAUDE" else None, "route": route, "risk": risk, "ci_ids": ci_ids,
                "health_run": health.get("run_id")}

    # ---- fix round 3 (ChatGPT audit: HOLD semantics, TOCTOU): fresh reads at the two write boundaries
    def live_stop(self, where):
        """The owner's stop, read LIVE (never the value the job started with): the repository variable S1_EXECUTOR_HOLD
        and the lane switch at current main. A non-empty hold turns this run OFF; a switch blob that is no longer the one
        this run verified stops it. A hold that cannot be read stops too (fail closed): 404 is the only "not set". Called
        immediately before the intent post and immediately before the merge call; SHADOW makes the same reads, so the
        SHADOW ticks prove the token can read the variable. What it cannot do: stop a merge call already sent."""
        self.hold_now(where)
        main, protected = self.main_now()                        # the switch and the contract as current main holds them, by a native git read
        blobs = self.native.tree_shas(main, [B.SWITCH, B.CONTRACT_FILE])
        need(isinstance(blobs.get(B.SWITCH), str) and blobs[B.SWITCH] == self.files["contract"].get("lane_switch_blob"), f"lane:C7:switch_changed:{where}",
             HELD if isinstance(blobs.get(B.SWITCH), str) else UNVERIFIED)
        need(isinstance(blobs.get(B.CONTRACT_FILE), str) and blobs[B.CONTRACT_FILE] == self.decision.get("contract_blob"), f"lane:C7:contract_changed:{where}",
             HELD if isinstance(blobs.get(B.CONTRACT_FILE), str) else UNVERIFIED)
        if not any(w[0] == "merge" for w in self.writes):
            # fix round 5 (#173/7188234670 P1-09): until this run's merge call, the LAST read also covers what the final
            # look verified: main unprotected, main moved since the decision by data only (no code, no path of the PR),
            # and every pin and chain blob of the switch at the main read here. After the merge call the outcome posts
            # (receipt, halt, recall) need only the hold, the switch and the contract: they record what happened.
            protection_known(protected, f":{where}")
            if main != self.decision.get("main"):
                self.no_code_drift(main, self.guard_paths)
            self.pins_at(main, where)

    def hold_now(self, where):
        """S1_EXECUTOR_HOLD read live: any non-empty value turns this run OFF; 404 is the only "not set"; anything else
        that is not a readable string stops (fail closed). Whether 404 can also mean "this token may not read
        variables" is a pre-LIVE gate (section 0.2i enable steps): the owner sets the hold once in SHADOW and the
        health line must read HELD with hold:intent."""
        try:
            doc = self.gh.get(f"actions/variables/{HOLD_VARIABLE}")
            value = doc.get("value") if isinstance(doc, dict) else None
            need(isinstance(value, str), f"hold_unreadable:{where}")
        except urllib.error.HTTPError as exc:
            need(exc.code == 404, f"hold_unreadable:{where}({exc.code})")
            value = ""
        if value != "":                                          # fix round 5 (P1-09): ANY non-empty value, whitespace included
            self.mode = "OFF"
            raise Stop(f"hold:{where}", HELD)

    def final_look(self, proof, intent_id, first=None):
        """After the intent and immediately before the merge call, every fact that can change without a new head is read
        again: the hold and the switch (live_stop), the PR (state, exact head, draft, base, mergeable), its labels and its
        title, every review (a CHANGES_REQUESTED on any commit), every check run and status of the head, main (a data-only
        move is allowed, anything else stops), and the ledger since this run's read (a halt, or an intent that is not this
        run's own). These reads shrink the window; they do not close it: main is not protected and no ruleset is active,
        so GitHub enforces nothing but the exact head (`sha` in the merge call). A stop here leaves the intent open: it is
        an alarm, and the next run settles it from native state (ABSENT)."""
        m = self.decision["merge"]
        n, head = m["pr"], m["sha"]
        pr = proof["head_read"]()
        facts = D.entry_facts(pr, proof["files"], True, self.files.get("push_filters"))
        need(not facts["hold_labels"] and not facts["x"] and not facts["direction"] and facts["title_sha256"] == m.get("title_sha256"),
             f"{n}:C8:pr_changed_after_intent", BLOCKED)
        reviews, rc = self.gh.pages(f"pulls/{n}/reviews", max_pages=10)
        need(rc and B.changes_requested(reviews) is False, f"{n}:C5:changes_requested_after_intent", BLOCKED if rc else UNVERIFIED)
        checks, k1 = self.gh.pages(f"commits/{head}/check-runs", key="check_runs", max_pages=5)
        statuses, k2 = self.gh.pages(f"commits/{head}/statuses", max_pages=3)
        need(B.checks_summary(checks, statuses, k1 and k2).get("green") is True, f"{n}:C4:checks_after_intent", BLOCKED if k1 and k2 else UNVERIFIED)
        main, protected = self.main_now()
        protection_known(protected, "")
        if main != proof["main"]:
            self.no_code_drift(main, proof["paths"])
        late = self.gh.get(f"issues/{B.OWNER_ISSUE}/comments", {"since": self.ledger_read_at, "per_page": 100})
        need(isinstance(late, list) and len(late) < 100, "lane:C7:ledger_unreadable")
        need(not B.lane_halts(late), "lane:C7:halt_after_intent", HELD)
        need(not any(B.is_s1_author(c) and c.get("id") != intent_id and B.first_line_token(c.get("body")) in ("S1_LANE_MERGE_INTENT_v1", "S1_OP_INTENT_v1")
                     for c in late), "lane:C9:intent_after_read", BLOCKED)
        # fix round 5 (#173/7190895883 D02): the publication is re-read at the boundary, by the same exact check
        published = self.published(self.body) if self.body is not None else "body_unknown"
        need(published is None, f"BRIEF_UNVERIFIED(publication_after_intent:{published})")
        if first is not None:
            # fix round 5 (#173/7188234670 P1-06): the first fallback run's candidate, re-read by its id after the intent:
            # the same body, never edited, still the executor's own post. Its log proof is immutable and was read before.
            row = self.gh.get(f"issues/comments/{int(first['id'])}")
            need(isinstance(row, dict) and row.get("id") == first.get("id") and row.get("body") == first.get("body")
                 and row.get("updated_at") == first.get("updated_at") and B.executor_post(row, self.run_of, self.now_fn()),
                 f"{n}:C5:fallback_first_changed", BLOCKED)
        # fix round 4 (ChatGPT #2): EVERY mutable gate again, by the same code that verified it before the intent: the
        # PR's conversation and inline comments, review threads, the newest S1_ITEM, the Claude receipt or veto, the
        # Codex state and (route (c)) the repository-wide offline feed, the writer, every CI tuple with its run,
        # attempt and job and the privacy line, the lane (switch, pins, halts, main health, the full ruleset census)
        # and the ledger as it is now. The route and the evidence must be exactly what they were.
        known = {c.get("id") for c in self.comments}
        again = self.verify_merge(self.comments + [c for c in late if isinstance(c, dict) and c.get("id") not in known], own_intent=intent_id)
        for key in ("route", "risk", "evidence", "paths", "privacy_run", "ci_ids", "claude", "offline"):
            need(again.get(key) == proof.get(key), f"{n}:C8:{key}_changed_after_intent", BLOCKED)
        if first is not None:
            need(any(c.get("id") == first.get("id") for c in again.get("candidates") or []), f"{n}:C5:fallback_first_changed", BLOCKED)
        self.verified_main, proof["final_health_run"] = again.get("main"), again.get("health_run")
        self.live_stop("put" if intent_id is not None else "shadow_put")   # the owner's hold and the switch: the LAST reads before the call
        if intent_id is not None:
            self.cleared_for = (n, head)

    def codex_offline(self, n, cx, prc, reviews, inline, now):
        """The offline signal of route (c), derived again by THIS run: Codex's activity in the whole repository is read
        again (two list reads), together with this PR's own comments, reviews and inline comments (P1-A, P3-F)."""
        feed = B.read_codex_feed(self.gh, now)
        return B.offline_signal(cx, B.codex_activity(feed, {n: {"comments": prc, "reviews": reviews, "inline": inline}}), now)

    # ---- route (c): the Codex-offline fallback needs TWO independent runs that agree
    def fallback(self, proof):
        """(candidate, None) when an EARLIER executor run recorded the same evidence: its S1_FALLBACK_CANDIDATE_v1 is
        proven to be an executor run's (B.executor_post), of another run id, at least FALLBACK_MIN_GAP_MINUTES and at
        most FALLBACK_MAX_AGE_HOURS old, and its evidence hash equals the one THIS run derived from its own reads.
        Otherwise (None, result), and this run merges nothing. It posts its own candidate (LIVE): as a first run, as a
        restart (the same evidence, but the earlier candidate is expired, unproven or this run's own), or as the record
        of a MISMATCH (the runs disagree: two different hashes on the ledger park the head from then on, in the brief
        and in verify_merge). An agreeing candidate that is simply too young is waited for; a head that used up its
        candidates is PARK."""
        d, m, now, run_id = self.decision, self.decision["merge"], self.now_fn(), self.env.get("GITHUB_RUN_ID")
        newest = proof["candidates"][-1] if proof["candidates"] else None
        why = "first_run"
        if newest is not None:
            age = (now - B.stamp(newest["created_at"])).total_seconds() / 60
            agrees = (B.fields(newest.get("body")).get("evidence") or "").strip() == proof["evidence"]
            other_run = str(B.executor_run(newest.get("body"))) != str(run_id)
            if not agrees:
                why = "mismatch"
            elif other_run and 0 <= age <= D.FALLBACK_MAX_AGE_HOURS * 60 and B.executor_post(newest, self.run_of, now) and self.candidate_logged(newest):
                if age >= D.FALLBACK_MIN_GAP_MINUTES:
                    return newest, None
                return None, f"FALLBACK_WAITING(pr={m['pr']},age_min={int(age)})"
            else:
                why = "restart"
        need(len(proof["candidates"]) < D.FALLBACK_MAX_CANDIDATES, f"{m['pr']}:C5:fallback_parked:candidates")
        if self.mode != "LIVE":
            return None, f"WOULD_POST_FALLBACK_CANDIDATE(pr={m['pr']},head={m['sha'][:8]},{why})"
        self.write("comment", body=D.candidate_body(d, proof["evidence"], proof["offline"], len(proof["candidates"]) + 1, run_id))
        kind = "FALLBACK_MISMATCH" if why == "mismatch" else "FALLBACK_CANDIDATE"
        return None, f"{kind}(pr={m['pr']},head={m['sha'][:8]},n={len(proof['candidates']) + 1},{why})"

    def candidate_logged(self, post):
        """Fix round 4 (ChatGPT #4, P2-E): the first run's candidate counts only when the `execute` job of the run it
        names wrote it: that job's own log (GET actions/runs/<id>/jobs, then the job's log) holds its S1_EXECUTOR_V1
        line with mode=LIVE and S1_FALLBACK_CANDIDATE_v1#<this comment id> among its writes. Another workflow that holds
        issues: write can post a candidate naming a run of this workflow; it cannot write into that run's execute log.
        Two reads, only on a second fallback run. Unread, unfinished or not found: not proven (the run restarts)."""
        rid = B.executor_run(post.get("body"))
        try:
            jobs, ok = self.gh.pages(f"actions/runs/{rid}/jobs", {"filter": "latest"}, key="jobs", max_pages=1)
            job = [j for j in jobs or [] if isinstance(j, dict) and j.get("name") == "execute" and j.get("status") == "completed"
                   and (j.get("run_id") in (None, rid))]
            if not ok or len(job) != 1 or not isinstance(job[0].get("id"), int):
                return False
            text = self.gh.text(f"actions/jobs/{job[0]['id']}/logs")
        except urllib.error.HTTPError:
            return False
        want = re.compile(rf"S1_EXECUTOR_V1 mode=LIVE decision=\S+ action=MERGE result=FALLBACK_CANDIDATE\(pr={self.decision['merge']['pr']},"
                          rf"head={self.decision['merge']['sha'][:8]},n=\d+,[a-z_]+\) writes=\d+:\S*S1_FALLBACK_CANDIDATE_v1#{int(post.get('id'))}(?![0-9])")
        return isinstance(text, str) and want.search(text) is not None

    def readback(self, n, head, intent_at, paths, actor=B.ACTIONS_BOT["login"]):
        pr = self.gh.get(f"pulls/{n}")
        sha = pr.get("merge_commit_sha") if pr.get("merged") is True else None
        commit = None
        if isinstance(sha, str) and D.SHA40.fullmatch(sha):
            try:
                commit = self.gh.get(f"commits/{sha}")
            except urllib.error.HTTPError:                       # fix round 5 (D06): unread is UNREADABLE, never a mismatch
                commit = None
            commit = commit if isinstance(commit, dict) and commit else None
        main, _p = self.main_now()
        blobs, parents = None, B.c1b_parents(commit) if commit else []
        parent = parents[0] if len(parents) == 1 else None
        changed = None
        if commit is not None and paths:
            a, b = self.native.tree_entries(sha, paths), self.native.tree_entries(head, paths)
            blobs = [(p, a.get(p, ("UNREADABLE",)), b.get(p, ("UNREADABLE",))) for p in paths]
            changed = self.native.changed(parent, sha) if parent else None   # fix round 5 (N05): the squash's whole delta
        state, why = D.readback_verdict(pr, head, intent_at, commit, blobs, self.native.is_ancestor(sha, main) if commit is not None else None,
                                        self.now_fn(), executor_login=actor, paths=paths, changed=changed)
        return state, why, {"pr": n, "head": head, "merge_commit": sha, "main_after": main, "paths": len(paths or []), "merge_parent": parent,
                            "verified_main": self.verified_main, "delta": f"{len(changed)} paths" if isinstance(changed, list) and state == "MATCH" else None}

    def do_merge(self, comments):
        d, m = self.decision, self.decision["merge"]
        self.comments = list(comments)
        proof = self.verify_merge(comments)
        self.guard_paths = tuple(proof["paths"])
        self.last_look()
        first = None
        if m["review"].startswith("FALLBACK("):                   # never a merge in the run that first saw the PR qualify
            first, waiting = self.fallback(proof)
            if first is None:
                return waiting
        # fix round 5 (#173/7190895883 D04): everything the merge needs after its intent is reserved BEFORE the intent:
        # calls for the final look, the merge call, the readback and the receipts, and the writes intent, merge,
        # receipt or halt, recall receipt and label. Not enough left: no intent (the next run starts fresh).
        remaining = self.gh.remaining() if callable(getattr(self.gh, "remaining", None)) else None
        need(isinstance(remaining, int) and remaining >= MERGE_CALL_RESERVE and MAX_WRITES - len(self.writes) >= MERGE_WRITE_RESERVE,
             f"budget:merge_reserve(calls={remaining},writes={MAX_WRITES - len(self.writes)})")
        self.live_stop("intent")                                 # the hold and the switch, read fresh, right before the intent
        if self.mode != "LIVE":
            self.final_look(proof, None, first)                  # SHADOW makes the reads of the merge boundary too (evidence)
            return f"WOULD_MERGE(pr={m['pr']},head={m['sha'][:8]},risk={m['risk']},review={m['review']})"
        run_id = self.env.get("GITHUB_RUN_ID")
        intent = self.write("comment", body=D.intent_body(d, proof["repo_id"], self.files["contract"]["action_loop_blob"], run_id))
        self.pending = f"intent_without_outcome(c={intent.get('id')})"   # until a receipt or a halt is posted: an alarm
        try:
            self.final_look(proof, intent.get("id"), first)      # after the intent, right before the merge call
        except Stop as stop:
            return f"MERGE_ABORTED_AFTER_INTENT({stop.reason})"  # no merge call; the open intent is the alarm and the next run settles it
        except Exception as exc:                                 # noqa: BLE001  (a read that failed in the final look: no merge call either)
            return f"MERGE_ABORTED_AFTER_INTENT(unreadable:{type(exc).__name__})"
        try:
            answer = self.write("merge", pr=m["pr"], sha=m["sha"])
        except Stop:
            raise
        except urllib.error.HTTPError as exc:                    # 405, 409, 422: STOP, no retry, no other write (C9)
            return f"MERGE_REFUSED({exc.code})"
        except Exception as exc:                                 # noqa: BLE001  (timeout or transport: RECONCILE settles it)
            return f"MERGE_REFUSED({type(exc).__name__})"
        if not isinstance(answer, dict) or answer.get("merged") is not True:
            return "MERGE_REFUSED(not_merged)"
        state, why, rb = self.readback(m["pr"], m["sha"], intent.get("created_at") or B.iso(self.now_fn()), proof["paths"])
        if state == "MATCH":
            self.write("comment", body=D.merge_receipt_body(d, proof["repo_id"], intent.get("id"), rb, run_id, proof["privacy_run"], claude=proof["claude"],
                                                            health_run=proof.get("final_health_run")))
            self.pending = None
            if first is not None:                                 # a fallback merge: flagged for Codex's revisit (the receipt above already says FALLBACK)
                try:
                    self.write("comment", body=D.recall_pending_body(d, rb["merge_commit"], first.get("id"), B.executor_run(first.get("body")), run_id))
                    self.write("label", pr=m["pr"], add=True)
                except Exception as exc:                          # noqa: BLE001  (the recall stays on the ledger through the merge receipt)
                    self.alarms.append(f"recall_flag_incomplete({type(exc).__name__})")
            return f"MERGED(n=1,main={str(rb['main_after'])[:8]})"
        if state == "MISMATCH":
            self.write("comment", body=D.halt_body("readback", pr=m["pr"], head=m["sha"], detail=why, contract=d["contract"], run_id=run_id, intent=intent.get("id")))
            self.pending = None
            self.alarms.append(f"readback_mismatch({why})")
            return f"LANE_HALTED(readback:{why})"
        self.uncertain.append(f"readback:{state}:{why}")
        return f"MERGE_UNSETTLED({state}:{why})"                 # the intent stays OPEN; the next run's RECONCILE settles it

    # ---- RECONCILE: an executor intent with no outcome (EVIDENCE_BINDINGS B3)
    def reconcile(self, comments):
        """Returns the result text when a receipt or a halt was posted (that is this run's action), else None."""
        now, done, records, settled = self.now_fn(), None, [], []
        mine = [i for i in B.open_intents(comments, now, 0, self.run_of, self.merge_of, self.log_of) if i.get("kind") == "S1_LANE_MERGE_INTENT_v1"]
        by_id = {c.get("id"): c for c in comments}
        for it in sorted(mine, key=lambda i: i["id"])[:RECONCILES_PER_RUN]:
            row = by_id.get(it["id"]) or {}
            f = B.fields(row.get("body"))
            head = (f.get("head") or "").strip()
            if it.get("pr") is None or not D.SHA40.fullmatch(head):
                continue
            files, fc = self.gh.pages(f"pulls/{it['pr']}/files", max_pages=31)
            paths = sorted({x.get("filename") or "" for x in files} | {x["previous_filename"] for x in files if x.get("previous_filename")}) if fc else []
            bound = (f.get("paths_sha256") or "").strip()            # the path set the intent was made for (fix round 3)
            # fix round 4 (#10): an intent that does not bind its path set (a legacy row) is never read back as a verified
            # merge: its file list would be today's, not the intent's. It stays open for the owner (lane C9 holds).
            if not fc or (bound and hashlib.sha256("\n".join(paths).encode()).hexdigest()[:16] != bound):
                records.append(f"UNREADABLE({it['id']}:path_set)")    # never a receipt from a file list that is not the intent's (uncertain, P1-08)
                continue
            state, why, rb = self.readback(it["pr"], head, row.get("created_at"), paths, actor=B.login(row))
            if not bound and state in ("MATCH", "MISMATCH"):
                # fix round 4 (#10): an intent that does not bind its path set (a legacy row) is never read back as a verified
                # merge, nor halted on today's file list. ABSENT and FOREIGN need no path set and still settle it.
                records.append(f"UNREADABLE({it['id']}:unbound_path_set)")
                continue
            contract = (f.get("contract") or self.decision["contract"]).strip()
            run_id = self.env.get("GITHUB_RUN_ID")
            if self.mode != "LIVE":
                records.append(f"WOULD_RECONCILE({it['id']}:{state})")
                continue
            if state == "MATCH":
                old = {"id": f.get("decision"), "run_id": f.get("brief"), "main": (f.get("main") or "").strip() or None, "contract": contract,
                       "merge": {"review": (f.get("review") or "unavailable").strip()}}      # a fallback merge keeps its recall (B.recalls)
                gap = "review, privacy, ci, main_health"
                self.write("comment", body=D.merge_receipt_body(old, self.brief["repo"]["id"], it["id"], rb, run_id, None, reconciled=True) + f"\nevidence_gap: {gap}")
                return f"RECONCILED(c={it['id']})"
            if state == "MISMATCH":
                self.write("comment", body=D.halt_body("reconcile_readback", pr=it["pr"], head=head, detail=why, contract=contract, run_id=run_id, intent=it["id"]))
                self.alarms.append(f"reconcile_readback_mismatch({why})")
                return f"LANE_HALTED(reconcile:{why})"
            if state in ("ABSENT", "FOREIGN"):
                self.write("comment", body=D.op_done_body(it["id"], state, f"pr={it['pr']} {why}", contract=contract, run_id=run_id))
                records.append(f"{state}({it['id']})")
                settled.append(f"{state}({it['id']})")
        if records:
            self.say("S1_EXECUTOR_RECONCILE " + " ".join(records))
        # fix round 5 (P1-08): what reconcile could not settle is uncertainty of this run, never a verified NOOP
        self.uncertain += [r for r in records if "UNREADABLE" in r]
        if settled:
            # fix round 5 (#173/7190895883 D04): a run that wrote recovery outcomes does nothing else (a reconciliation-only
            # tick): its writes and calls are not shared with a merge, and the next run decides from the settled ledger
            return "SETTLED(" + ",".join(settled) + ")"
        return done

    # ---- HALT: re-proven natively, then posted
    def do_halt(self, comments):
        d, h = self.decision, self.decision["halt"]
        run_id = self.env.get("GITHUB_RUN_ID")
        named = " ".join(x["body"] for x in B.lane_halts(comments))
        main, _p = self.main_now()
        if h["source"] == "C1B":
            commit = self.gh.get(f"commits/{h['commit']}")
            subject = B.c1b_subject(commit)
            need(commit.get("sha") == h["commit"], "-:C1b:commit")
            need(len(B.c1b_parents(commit)) != 1 or not B.SQUASH_SUBJECT.search(subject), "-:C1b:is_a_squash_merge", BLOCKED)
            a, b = B.c1b_entries(self.gh.get(f"git/trees/{h['parent']}")), B.c1b_entries(self.gh.get(f"git/trees/{h['commit']}"))
            need(a != b, "-:C1b:trees_equal", BLOCKED)
            anc = self.native.is_ancestor(h["commit"], main)       # fix round 5 (D06): proven not on main, or unknown
            need(anc is not None, "-:C1b:ancestry_unknown")
            need(anc is True, "-:C1b:not_on_main", BLOCKED)
            if h["commit"] in named:
                return "LANE_HALTED(c1b:already_posted)"
            if self.mode != "LIVE":
                return f"WOULD_HALT(c1b:{h['commit'][:8]})"
            self.write("comment", body=D.halt_body("unreviewed_code_on_main", commit=h["commit"], contract=d["contract"], run_id=run_id))
            return "LANE_HALTED(c1b)"
        run = self.gh.get(f"actions/runs/{h['run']}")
        health = self.files["bindings"]["main_health"]
        need(run.get("id") == h["run"] and run.get("path") == health["workflow_path"] and run.get("event") == "schedule" and run.get("head_branch") == "main"
             and (run.get("repository") or {}).get("full_name") == B.REPO and (run.get("head_repository") or {}).get("full_name") == B.REPO
             and run.get("status") == "completed" and run.get("conclusion") in B.FAILED_CONCLUSIONS, "-:C7:run", BLOCKED)
        if re.search(rf"(?<!\d){h['run']}(?!\d)", named):
            return "LANE_HALTED(main_health:already_posted)"
        if self.mode != "LIVE":
            return f"WOULD_HALT(main_health:{h['run']})"
        self.write("comment", body=D.halt_body("main_health", run=h["run"], contract=d["contract"], run_id=run_id))
        return "LANE_HALTED(main_health)"

    # ---- CODEX RECALL: bookkeeping, never the action; at most one clear per run
    def recall(self, comments):
        """Recall bookkeeping, at most ONE PR per run, always after this run's own native read. Debt truth is Codex's
        native state (B.recalls, recall_status); the receipt and the label are bookkeeping that this run brings in line
        with it (fix round 4, #11 and 7186140947-06/11):
          FINAL   Codex's completed review of the head, read again here: post the clear receipt if none exists yet (a
                  clear receipt that someone else posted, forged or not, never stops this), and remove the label if it
                  is on the PR (read first).
          else    the PR is natively merged at that head and the label is missing (a run that died after the merge, or a
                  reconciled fallback merge): add it.
        Nothing else is written, and a read that does not prove the state writes nothing."""
        recorded = {(r["pr"], r["head"]): r for r in B.recalls(comments)}
        for item in (self.brief.get("recall") or {}).get("items") or []:
            if not isinstance(item, dict) or (item.get("pr"), item.get("head")) not in recorded or item.get("codex") == "NOT_READ":
                continue
            now, n, head = self.now_fn(), item["pr"], item["head"]
            labels, lc = self.gh.pages(f"issues/{n}/labels", max_pages=1)
            if not lc:
                continue
            has_label = any(isinstance(x, dict) and x.get("name") == D.RECALL_LABEL for x in labels)
            if item.get("codex") == "FINAL":
                if recorded[(n, head)].get("cleared") and not has_label:
                    continue                                     # already in line: nothing to do
                cx = B.codex_review(head, {}, *(lambda r: (r["commits"], r["commits_complete"], r["comments"], r["reviews"], r["inline"], r["complete"]))(B.read_recall(self.gh, n)),
                                    now, self.files["budgets"]["codex_silent_hours"])
                if cx.get("status") != "FINAL":
                    return f"RECALL_NOT_PROVEN(pr={n},{cx.get('status')})"
                if self.mode != "LIVE":
                    return f"WOULD_CLEAR_RECALL(pr={n})"
                if not recorded[(n, head)].get("cleared"):
                    self.write("comment", body=D.recall_cleared_body(n, head, cx.get("requested_at"), self.decision["contract"], self.env.get("GITHUB_RUN_ID")))
                self.recall_cleared.add(n)
                if has_label:
                    try:
                        self.write("label", pr=n, add=False)
                    except urllib.error.HTTPError as exc:
                        if exc.code != 404:                      # 404: the label was not on the PR
                            self.alarms.append(f"recall_label_remove_failed({exc.code})")
                return f"RECALL_CLEARED(pr={n})"
            if has_label:
                continue
            native = self.merge_of(n)                            # the label is missing: is this really a merged fallback head?
            if not (isinstance(native, dict) and native.get("merged") is True and native.get("head_sha") == head):
                continue
            if self.mode != "LIVE":
                return f"WOULD_REPAIR_RECALL_LABEL(pr={n})"
            self.label_repair.add(n)
            self.write("label", pr=n, add=True)
            return f"RECALL_LABEL_REPAIRED(pr={n})"
        return None

    # ---- A26 (fix round 4, ChatGPT #8): the decision this job executes is the one the publish job made durable
    def published(self, body):
        """None when the ONE open brief issue (label s1-tick-brief, by the Actions bot) holds exactly this run's decision
        block and is this run's brief; else the reason. `needs: publish` only proves that the publish job succeeded,
        not what it published: a skipped publish (a newer brief kept, a carried halt kept) or an edited issue would
        otherwise leave the executor acting on a decision nobody can read. One read."""
        issues = self.gh.get("issues", {"labels": B.BRIEF_LABEL, "state": "open", "per_page": 20})
        rows = [i for i in issues if isinstance(i, dict) and "pull_request" not in i] if isinstance(issues, list) else None
        if rows is None:
            return "unreadable"
        mine = [i for i in rows if B.is_actions_bot(i.get("user"))]
        if len(mine) != 1 or len(rows) != 1:
            return f"issues={len(mine)}/{len(rows)}"
        text = str(mine[0].get("body") or "")
        block, ours = D.decision_block(text), D.decision_block(body)
        if ours is None or block != ours:
            return "decision_differs"
        brief = B.parse_body(text)
        if not isinstance(brief, dict) or brief.get("run_id") != self.brief.get("run_id") or brief.get("run_attempt") != self.brief.get("run_attempt"):
            return "brief_differs"
        # fix round 5 (#173/7190895883 D02): the WHOLE published brief, by its canonical digest, and the same issue as at
        # this run's first check (a second issue, or a brief whose evidence was edited under the same decision, differs)
        if B.brief_digest(text) is None or B.brief_digest(text) != B.brief_digest(body):
            return "brief_digest_differs"
        if self.published_issue is not None and mine[0].get("number") != self.published_issue:
            return "issue_differs"
        self.published_issue = mine[0].get("number")
        return None

    # ---- HEARTBEAT: observability, never the action
    def heartbeat(self, comments):
        now = self.now_fn()
        if not self.decision["heartbeat"]["due"] or not B.heartbeat_due(comments, now):
            return None
        if self.mode != "LIVE":
            return "WOULD_HEARTBEAT"
        runs = self.gh.get(f"actions/workflows/{Path(B.WORKFLOW_PATH).name}/runs", {"per_page": 100}).get("workflow_runs") or []
        ticks = sum(1 for r in runs if r.get("event") in EVENTS and timedelta(0) <= now - B.stamp(r["created_at"]) <= timedelta(hours=24))
        self.write("comment", body=D.heartbeat_body(self.decision, self.brief, ticks if len(runs) < 100 else None, self.mode, self.env.get("GITHUB_RUN_ID")))
        return "HEARTBEAT"

    # ---- the whole run
    def execute(self, body):
        end = lambda action, pr, head, result: self.finish(action, pr, head, result)
        brief, d = B.parse_body(body), B.decision_of(body)
        if brief is None or d is None:
            return end("NOOP", None, None, "BRIEF_UNVERIFIED(body)")
        self.brief, self.decision, self.body = brief, d, body
        env = self.env
        # trigger round: a dispatched run (the metronome) has no triggering run; it resolves the brief run from the
        # published brief and proves it natively, then takes the same path. The S1_BRIEF_* of such a run must be empty
        # (the workflow passes github.event.workflow_run.*, which a dispatch does not have): set, they are not proven.
        if env.get("GITHUB_EVENT_NAME") == SELF_TRIGGER:
            if any(env.get(k) for k in BRIEF_ENV) or env.get("GITHUB_REPOSITORY") != B.REPO or env.get("GITHUB_REF") != "refs/heads/main":
                return end("NOOP", None, None, "BRIEF_UNVERIFIED(run_binding)")
            why = self.resolve_brief_run(brief)
            if why is not None:
                return end("NOOP", None, None, f"NO_DECISION(brief_run={d.get('run_id')}:{why})")
            env = self.env
        # fix round 6 (F2): this run is a workflow_run of s1-executor.yml; the brief it acts for is the triggering run's
        # (S1_BRIEF_RUN_ID / _RUN_ATTEMPT / _MAIN / _EVENT, from github.event.workflow_run), and the published brief must
        # be exactly that run's brief. A published brief of another run (that run published nothing: not due, or its
        # publish kept the older brief) is no decision for this run: nothing to execute, nothing is read further.
        if str(d.get("run_id")) != env.get("S1_BRIEF_RUN_ID") and str(env.get("S1_BRIEF_RUN_ID") or "").isdigit():
            return end("NOOP", None, None, f"NO_DECISION(published_run={d.get('run_id')})")
        if not (env.get("GITHUB_REPOSITORY") == B.REPO and env.get("GITHUB_REF") == "refs/heads/main"
                and env.get("GITHUB_EVENT_NAME") in (EXECUTOR_TRIGGER, SELF_TRIGGER) and env.get("S1_BRIEF_EVENT") in EVENTS
                and str(d.get("run_id")) == env.get("S1_BRIEF_RUN_ID") and str(d.get("run_attempt")) == env.get("S1_BRIEF_RUN_ATTEMPT")
                and d.get("main") == env.get("S1_BRIEF_MAIN")):
            return end("NOOP", None, None, "BRIEF_UNVERIFIED(run_binding)")
        cfg = D.thin_config(self.files.get("switch"))
        if cfg != brief.get("thin") or cfg["executor"] != d["executor"] or cfg["review_policy"] != d["review_policy"]:
            return end("NOOP", None, None, "BRIEF_UNVERIFIED(switch)")
        self.mode = D.effective_mode(cfg["executor"], env.get("S1_EXECUTOR_HOLD"))
        if cfg["executor"] == "OFF":
            return end("NOOP", None, None, "EXECUTOR_OFF(switch)")
        if self.mode == "OFF":
            # fix round 6 (#173/7194141485 item 5, pre-LIVE evidence): a hold already in the job's env stops every write at
            # once (mode OFF), and the hold is STILL read natively, so a held tick proves (or disproves) that the token can
            # read the variable: hold:start when the native read shows it, EXECUTOR_OFF(hold:env_only) when only the env did
            try:
                self.hold_now("start")
            except Stop as stop:
                self.stop_kind = stop.kind
                return end("NOOP", None, None, f"NOTHING_ACTIONABLE(skipped={stop.reason})")
            except Exception as exc:                             # noqa: BLE001  (unread: the env hold still holds)
                self.stop_kind = UNVERIFIED
                return end("NOOP", None, None, f"NOTHING_ACTIONABLE(skipped=hold_unreadable:start:{type(exc).__name__})")
            self.mode = "OFF"
            return end("NOOP", None, None, "EXECUTOR_OFF(hold:env_only)")
        clock = D.clock_gate(self.now_fn(), d["generated_at"], d["expires_at"], D.EXECUTE_MAX_AGE_MINUTES)
        if clock is not None:
            return end("NOOP", None, None, clock)
        # ChatGPT audit A11: no write of ANY class (reconcile, heartbeat, recall bookkeeping) on a decision whose source
        # chain did not verify; a pins failure is not "nothing to do", it is "nothing may be done"
        if d.get("pins_ok") is not True:
            return end("NOOP", None, None, d.get("result") or "SOURCE_UNVERIFIED")
        # trigger round: one evaluation per brief run and attempt (a workflow_run and a dispatched run of the same brief,
        # or two dispatches): an earlier executor run that evaluated it, or one that cannot be read, ends this run here
        try:
            done = self.evaluated_before(d["run_id"], d["run_attempt"], d["generated_at"])
        except Exception as exc:                                 # noqa: BLE001  (unread: not proven, no second evaluation)
            done = f"evaluated_unproven:{type(exc).__name__}"
        if done is not None:
            return end("NOOP", None, None, f"NO_DECISION({done})")
        try:
            published = self.published(body)
        except Exception as exc:                                 # noqa: BLE001  (unreadable: not proven, nothing is written)
            published = f"unreadable:{type(exc).__name__}"
        if published is not None:
            return end("NOOP", None, None, f"BRIEF_UNVERIFIED(publication:{published})")
        try:
            # fix round 5 (#173/7190895883 D08): the owner's hold is read LIVE once at the start of every SHADOW and LIVE run,
            # so every tick is evidence that the token can read it (and a hold set after the job's env snapshot stops it)
            self.hold_now("start")
            comments = self.ledger()
            settled = self.reconcile(comments)
            if settled is not None:                              # a reconciled receipt, a reconcile halt or settled outcomes: this run's action
                return end("MERGE" if settled.startswith("RECONCILED") else "NOOP", None, None, settled)
            beat = self.heartbeat(comments)
            if beat:
                self.say(f"S1_EXECUTOR_HEARTBEAT {beat}")
            cleared = self.recall(comments)
            if cleared:
                self.say(f"S1_EXECUTOR_RECALL {cleared}")
            if d["action"] == "HALT":
                return end("NOOP", None, None, self.do_halt(comments))
            if d["action"] == "MERGE":
                result = self.do_merge(comments)
                return end("MERGE" if result.startswith("MERGED") else "NOOP", d["pr"], d["head"], result)   # only a read-back merge is a MERGE line
            return end("NOOP", None, None, d["result"])
        except Stop as stop:
            self.stop_kind = stop.kind
            pr, head = (d.get("pr"), d.get("head")) if d["action"] == "MERGE" else (None, None)
            return end("NOOP", pr, head, f"NOTHING_ACTIONABLE(skipped={stop.reason})")
        except B.StopReading as stop:
            if self.writes:
                self.alarms.append(f"read_stopped_after_write({stop.reason})")
            return end("NOOP", None, None, f"BRIEF_INCOMPLETE(executor:{stop.reason})")
        except Exception as exc:                                 # noqa: BLE001  (an unreadable read: nothing more is written)
            self.alarms.append(f"unexpected({type(exc).__name__})")
            return end("NOOP", None, None, f"BRIEF_INCOMPLETE(executor:{type(exc).__name__})")

    def execute_published(self):
        """Fix round 6 (F2): the brief issue as published, read once, then execute() on exactly that body (published()
        re-reads it and must find the same block, digest and issue)."""
        try:
            issues = self.gh.get("issues", {"labels": B.BRIEF_LABEL, "state": "open", "per_page": 20})
            rows = [i for i in issues if isinstance(i, dict) and "pull_request" not in i and B.is_actions_bot(i.get("user"))] \
                if isinstance(issues, list) else []
            body = str(rows[0].get("body") or "") if len(rows) == 1 else ""
            self.published_doc = rows[0] if len(rows) == 1 else None
        except Exception as exc:                                 # noqa: BLE001  (unreadable: nothing is decided, nothing is written)
            self.alarms.append(f"brief_unreadable({type(exc).__name__})")
            return self.finish("NOOP", None, None, "BRIEF_UNVERIFIED(unreadable)")
        return self.execute(body)

    def resolve_brief_run(self, brief, checkout=True):
        """Trigger round: for a dispatched run, the brief run the published brief names, proven natively (one read).
        None when it qualifies (and the S1_BRIEF_* of this run are set from the native run), else the reason. The run
        must be exactly what the previous build's C1b anchor accepts (B.previous_anchor: a run of the brief workflow on
        main of this repository at the brief's main and attempt, COMPLETED with success, the brief generated inside the
        run and the issue not edited after it), started by schedule or workflow_dispatch; and this checkout must be the
        brief's main (the workflow checks it out), so the code that evaluates it is the code that built it."""
        issue, rid = self.published_doc, brief.get("run_id")
        if not isinstance(issue, dict):
            return "issue_unread"
        if type(rid) is not int or rid <= 0:
            return "run_id"
        try:
            run = self.gh.get(f"actions/runs/{rid}")
        except Exception as exc:                                 # noqa: BLE001  (unreadable: not proven)
            return f"unreadable:{type(exc).__name__}"
        _known, _halt, why = B.previous_anchor(issue, brief, run, self.now_fn())
        if why is not None and why != "no_checked_through":     # no_checked_through is about the C1b point, not the run
            return why
        if run.get("event") not in EVENTS:
            return f"event:{run.get('event')}"
        if not checkout:                                         # the resolve step: before the checkout of that SHA
            return None
        try:
            head = self.native.head_commit()
        except Exception:                                        # noqa: BLE001  (unread: not proven)
            head = None
        if head != brief.get("main") or head != run.get("head_sha"):
            return "checkout"
        self.env = dict(self.env, S1_BRIEF_RUN_ID=str(run["id"]), S1_BRIEF_RUN_ATTEMPT=str(run["run_attempt"]),
                        S1_BRIEF_MAIN=run["head_sha"], S1_BRIEF_EVENT=run["event"])
        return None

    def evaluated_before(self, run_id, attempt, generated_at):
        """Trigger round: None when no earlier executor run evaluated brief run `run_id` attempt `attempt`, proven from
        native reads; else "already_evaluated=<executor run>" or "evaluated_unproven:<why>". Read: the newest page of
        runs of s1-executor.yml on main; every run older than this one (by id) that ended after the brief was generated
        and was not skipped; for each, its execute job and that job's ONE S1_EXECUTOR_HEALTH line. The concurrency group
        runs one execute job at a time, so when this job runs every older run has ended and no newer one has started."""
        own = str(self.env.get("GITHUB_RUN_ID") or "")
        need(own.isdigit(), "own_run_id")
        since = B.stamp(generated_at) - timedelta(seconds=B.RUN_POST_SLACK_SECONDS)
        doc = self.gh.get(f"actions/workflows/{Path(B.EXECUTOR_WORKFLOW_PATH).name}/runs", {"branch": "main", "per_page": EXECUTOR_RUNS_PAGE})
        rows = doc.get("workflow_runs") if isinstance(doc, dict) else None
        if not isinstance(rows, list) or not all(isinstance(r, dict) and type(r.get("id")) is int for r in rows):
            return "evaluated_unproven:runs_unreadable"
        older = [r for r in rows if r["id"] < int(own)]
        try:
            if len(rows) >= EXECUTOR_RUNS_PAGE and min(B.stamp(r["created_at"]) for r in rows) >= since - timedelta(minutes=EXECUTOR_RUN_MAX_MINUTES):
                return "evaluated_unproven:runs_page"           # the window may reach past this page
            window = [r for r in older if B.stamp(r["updated_at"]) >= since]
        except (KeyError, TypeError, ValueError):
            return "evaluated_unproven:run_row"
        window = [r for r in window if not (r.get("status") == "completed" and r.get("conclusion") == "skipped")]
        if any(r.get("status") != "completed" for r in window):
            return "evaluated_unproven:run_active"
        if len(window) > EVALUATION_READS:
            return "evaluated_unproven:too_many_runs"
        for r in sorted(window, key=lambda r: r["id"], reverse=True):
            jobs, ok = self.gh.pages(f"actions/runs/{r['id']}/jobs", {"filter": "latest"}, key="jobs", max_pages=1)
            job = [j for j in jobs or [] if isinstance(j, dict) and j.get("name") == "execute"]
            if not ok or len(job) > 1:
                return f"evaluated_unproven:jobs={r['id']}"
            if not job or job[0].get("conclusion") == "skipped" or (job[0].get("conclusion") == "cancelled" and not job[0].get("steps")):
                continue                                         # the job never ran: nothing was evaluated
            if job[0].get("status") != "completed" or type(job[0].get("id")) is not int:
                return f"evaluated_unproven:job={r['id']}"
            text = self.gh.text(f"actions/jobs/{job[0]['id']}/logs")
            found = B.HEALTH_LINE.findall(text) if isinstance(text, str) else []
            try:
                line = json.loads(found[0]) if len(found) == 1 else None
            except ValueError:
                line = None
            if not isinstance(line, dict):
                return f"evaluated_unproven:health={r['id']}"
            result, brief_run = str(line.get("result") or ""), line.get("brief_run")
            if brief_run in (None, "") and not result.startswith("NO_DECISION("):
                return f"evaluated_unproven:brief_run={r['id']}"   # a crash line names no brief: it may have been this one
            if str(brief_run) == str(run_id) and line.get("brief_attempt") in (None, "", str(attempt)) and not result.startswith("NO_DECISION("):
                return f"already_evaluated={r['id']}"
        return None

    def resolve_main(self):
        """Trigger round, the workflow's resolve step: the brief main a dispatched run must check out, or None. Only the
        published brief and its run are read (resolve_brief_run without the checkout check); execute() proves all of
        it again after the checkout."""
        try:
            issues = self.gh.get("issues", {"labels": B.BRIEF_LABEL, "state": "open", "per_page": 20})
            rows = [i for i in issues if isinstance(i, dict) and "pull_request" not in i and B.is_actions_bot(i.get("user"))] \
                if isinstance(issues, list) else []
            self.published_doc = rows[0] if len(rows) == 1 else None
            brief = B.parse_body(str(rows[0].get("body") or "")) if len(rows) == 1 else None
            if not isinstance(brief, dict) or not isinstance(brief.get("main"), str) or D.SHA40.fullmatch(brief["main"]) is None:
                return None
            return brief["main"] if self.resolve_brief_run(brief, checkout=False) is None else None
        except Exception:                                        # noqa: BLE001  (nothing resolved: execute() reports NO_DECISION)
            return None

    def finish(self, action, pr, head, result):
        d = self.decision or {}
        main, contract = str(d.get("main") or "-")[:8], d.get("contract") or "-"
        if self.pending:                                         # an intent was posted and this run posted no outcome for it
            self.alarms.append(self.pending)
        if self.alarms:
            self.say("S1_EXECUTOR_ALARM " + " ".join(self.alarms))
        state = health_state(result, self.alarms, self.pending, self.stop_kind, self.uncertain, (self.decision or {}).get("unverified"))
        self.say("S1_EXECUTOR_HEALTH " + json.dumps({"v": 1, "state": state, "run": self.env.get("GITHUB_RUN_ID"), "attempt": self.env.get("GITHUB_RUN_ATTEMPT"),
                                                     "brief_run": self.env.get("S1_BRIEF_RUN_ID"), "brief_attempt": self.env.get("S1_BRIEF_RUN_ATTEMPT"),
                                                     "at": B.iso(self.now_fn()), "mode": self.mode, "action": action, "result": str(result)[:160],
                                                     "writes": len(self.writes), "stop": self.stop_kind, "uncertain": self.uncertain[:3],
                                                     "unverified": list((self.decision or {}).get("unverified") or [])[:3]},
                                                    sort_keys=True, separators=(",", ":")))
        self.say(f"S1_EXECUTOR_V1 mode={self.mode} decision={d.get('id')} action={d.get('action')} result={result} "
                 f"writes={len(self.writes)}:{','.join(str(w[1]) + (f'#{w[2]}' if w[0] == 'comment' else '') for w in self.writes) or '-'}")
        self.say(f"S1_TICK {action} {pr if pr is not None else '-'} {head[:8] if head else '-'} {result} main={main} contract={contract}")
        return {"mode": self.mode, "action": action, "pr": pr, "head": head, "result": result, "writes": list(self.writes), "lines": list(self.lines),
                "alarms": list(self.alarms), "health": state}


def protection_known(protected, where):
    """Fix round 6 (#173/7194141485 S3): main's `protected` flag as GitHub returned it. True: a proven protected main, a
    verified block (the job token cannot prove compliance or bypass evidence). Anything that is not the real bool False
    or True (missing, null, a string, a number): unread, UNVERIFIED, never a proven block and never a pass."""
    need(isinstance(protected, bool), f"lane:C8:protection_unreadable{where}")
    need(protected is False, f"lane:C8:main_protected{where}", BLOCKED)


def health_state(result, alarms, pending, stop_kind=None, uncertain=(), unverified=()):
    """Executor health, machine-readable and separate from the producer (ChatGPT audit, P2 executor health): a green
    build says nothing about the executor. Fix round 5 (#173/7188234670 P1-08): classified by structure, not by
    fragments of the result text, and OK is an explicit, positive state:
      AMBIGUOUS   an intent was posted and this run posted no outcome for it (a merge call may or may not have landed;
                  the next run settles it from native state)
      DEGRADED    an alarm, a crash, or a run that could not verify its own inputs (brief, publication, source chain)
      UNVERIFIED  the run stopped on a fact it could not read or prove (Stop kind UNVERIFIED, the default), reconcile
                  left an intent it could not read, or the decision's NOOP rests on unread facts (decision.unverified)
      HELD        the owner's hold, the switch, a standing halt, the Monday window
      OK          a verified outcome: a merge, a halt, a reconciliation, a WOULD_* in SHADOW, or a NOOP whose every
                  reason was read and proven (a BLOCKED stop, or a decision with no unverified gate)
    Anything else is UNVERIFIED. The newest run whose line reads OK or HELD is the last successful executor tick."""
    text = str(result)
    if pending or text.startswith(("MERGE_UNSETTLED", "MERGE_REFUSED", "MERGE_ABORTED_AFTER_INTENT")):
        return "AMBIGUOUS"
    if alarms or text.startswith(("BRIEF_INCOMPLETE", "BRIEF_UNVERIFIED", "SOURCE_UNVERIFIED", "EXECUTOR_CRASHED")):
        return "DEGRADED"
    if text.startswith(("EXECUTOR_OFF", "MONDAY_READ_ONLY")) or stop_kind == HELD:
        return "HELD"
    if stop_kind == UNVERIFIED or uncertain or text.startswith("BRIEF_STALE"):
        return "UNVERIFIED"
    if stop_kind == BLOCKED:
        return "OK"
    if text.startswith("NOTHING_ACTIONABLE"):
        return "UNVERIFIED" if unverified else "OK"
    if text.startswith(OK_RESULTS):
        return "OK"
    return "UNVERIFIED"


OK_RESULTS = ("MERGED", "LANE_HALTED", "RECONCILED", "SETTLED", "WOULD_", "FALLBACK_CANDIDATE", "FALLBACK_MISMATCH", "FALLBACK_WAITING")


def write_summary(env, lines):
    """The run's own lines in the job summary (the file the runner names in its *_STEP_SUMMARY variable), so that the
    executor's result is visible on the run page without opening a log. Text only, inside one fenced block."""
    path = env.get("GITHUB" + "_STEP_SUMMARY")
    if not path:
        return False
    text = "\n".join(re.sub(r"[^\x20-\x7e]", "?", str(line)).replace("`", "'") for line in lines)
    try:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write("### S1 executor\n\n```text\n" + text + "\n```\n")
    except OSError:
        return False
    return True


def read_files(root):
    """main's own policy files, from the checkout this script runs in (the workflow checks out github.sha)."""
    read = lambda rel: (Path(root) / rel).read_text(encoding="utf-8")
    return {"switch": json.loads(read(B.SWITCH)), "contract": json.loads(read(B.CONTRACT_FILE)), "policy": json.loads(read(B.POLICY_FILE)),
            "gate_isolation": json.loads(read(B.ISOLATION_FILE)).get("gate_isolation"),
            "push_filters": B.read_push_filters(root),            # fix round 5 (D05): main's own push-triggered workflows; None: every PR matches
            "bindings": B.parse_json_block(read(B.BINDINGS_FILE), "S1_EVIDENCE_BINDINGS_v1"),
            "budgets": B.parse_json_block(read("00_FMOS/S1/STEWARD_STATES.md"), "S1_STEWARD_BUDGETS_v1")}


def resolve_brief_main(env):
    """Trigger round: the step before the second checkout of a dispatched run. Prints and writes to the step output
    file ONE line brief_main=<40 hex>, or nothing; exits 0 either way (execute-published decides and reports)."""
    if env.get("GITHUB_REPOSITORY", B.REPO) != B.REPO or env.get("GITHUB_EVENT_NAME") != SELF_TRIGGER:
        print("S1_EXECUTOR_RESOLVE none (not a dispatched run of this repository)")
        return 0
    token = env.get("GITHUB" + "_TOKEN", "")
    run = Run(B.GitHub(token, budget=4), Native(B.CHECKOUT_ROOT), dict(env), {}, out=lambda line: None)
    sha = run.resolve_main()
    sha = sha if isinstance(sha, str) and D.SHA40.fullmatch(sha) else None
    print(f"S1_EXECUTOR_RESOLVE {sha or 'none'}")
    path = env.get("GITHUB" + "_OUTPUT")
    if sha and path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(f"brief_main={sha}\n")
    return 0


def main(argv):
    if len(argv) == 2 and argv[1] == "resolve-brief-main":
        # trigger round: never a health line from this step (the execute job's log must hold exactly the ONE health line
        # of execute-published, which the watchdog and the next run's one-evaluation check read)
        try:
            return resolve_brief_main(os.environ)
        except Exception as exc:                                 # noqa: BLE001  (nothing resolved: execute-published reports NO_DECISION)
            print(f"S1_EXECUTOR_RESOLVE none ({type(exc).__name__})")
            return 0
    try:
        # fix round 5 (P1-08): the usage and repository checks are inside the handler too, so they also print a health
        # line. What no handler can cover (an import that fails, a cancelled or killed job) prints none: the next
        # build's watchdog reads the job's own log and reports EXECUTOR_NOHEALTH.
        if not ((len(argv) == 3 and argv[1] == "execute") or (len(argv) == 2 and argv[1] == "execute-published")):
            raise SystemExit("usage: s1_executor_v1.py execute-published | resolve-brief-main | execute <issue body file>")
        token = os.environ.get("GITHUB" + "_TOKEN", "")
        if os.environ.get("GITHUB_REPOSITORY", B.REPO) != B.REPO:
            raise SystemExit(f"REFUSED: repository is not {B.REPO}")
        root = B.CHECKOUT_ROOT
        B.GIT_ENV = B.token_git_env(token)
        run = Run(B.GitHub(token, budget=EXECUTE_API_CALLS), Native(root), dict(os.environ), read_files(root))
        out = run.execute_published() if argv[1] == "execute-published" else run.execute(Path(argv[2]).read_text(encoding="utf-8"))
    except BaseException as exc:                                 # noqa: BLE001  (fix round 4, #8: one health line per run, whatever fails)
        line = "S1_EXECUTOR_HEALTH " + json.dumps({"v": 1, "state": "DEGRADED", "run": os.environ.get("GITHUB_RUN_ID"),
                                                   "attempt": os.environ.get("GITHUB_RUN_ATTEMPT"), "mode": "UNKNOWN", "action": "NOOP",
                                                   "result": f"EXECUTOR_CRASHED({type(exc).__name__})", "writes": "UNKNOWN"},
                                                  sort_keys=True, separators=(",", ":"))
        print(line)
        write_summary(os.environ, [line])
        return 1
    write_summary(os.environ, out["lines"])
    # a failed JOB (continue-on-error), never a failed run; UNVERIFIED exits 0, and the next build reads the health line itself
    return 1 if out["alarms"] or out.get("health") in ("AMBIGUOUS", "DEGRADED") else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
