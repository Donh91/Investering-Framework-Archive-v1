"""S1 executor: the job `execute` of .github/workflows/s1-tick-brief.yml performs the ONE action of S1_DECISION_V1.

AGENTS.md section 0.2i ("S1 is GitHub"). The build job of the same workflow run read GitHub natively and decided
(s1_decision_v1.decide); this job re-reads every fact of that one action natively, immediately before it writes, and
writes only when the switch 00_FMOS/S1/REVIEWED_MERGE_LANE.json on main reads "executor": "LIVE" (missing or unknown:
OFF) and the owner's repository variable S1_EXECUTOR_HOLD is empty. In SHADOW it makes the same reads and prints what
it WOULD do; it never writes. It runs main's own code only and never checks out, imports or executes a PR head.

The only writes this file can make (write() is the one call site of each):
  POST /repos/<repo>/issues/1156/comments   an S1_LANE_MERGE_INTENT_v1, S1_LANE_MERGE_v1, S1_LANE_HALTED, S1_OP_DONE_v1
                                            or S1_HEARTBEAT_v1 on the owner ledger
  PUT  /repos/<repo>/pulls/<n>/merge        {"merge_method": "squash", "sha": <the decision's exact head>}
A merge is ONE per run, always intent first, readback after, receipt or halt last (EVIDENCE_BINDINGS B3, C9, C10).
ONE attempt per PR head, ever: a refused or failed merge is never retried at that head (a new commit is a new head).

No silent failure: the result lines go to the job summary, and the process exits non-zero when an operation was left
without its outcome, a readback did not match, a read stopped after a write, or anything unexpected was raised. The
job is `continue-on-error`, so that exit shows as a failed JOB and never fails the run that carries the brief.
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

EXECUTE_API_CALLS = 150                # this job's own cap (the build is capped at 300; one PR in depth costs about 40)
MAX_WRITES = 6                         # heartbeat, intent, merge, receipt or halt, and at most two reconcile records
RECONCILES_PER_RUN = 3                 # EVIDENCE_BINDINGS op_reconciles_per_run
MAX_ATTEMPTS_PER_HEAD = 1              # merge intents per PR head, ever: a refused merge is NOT retried, that head is the owner's
EVENTS = ("schedule", "workflow_dispatch")
POSTS = ("S1_LANE_MERGE_INTENT_v1", "S1_LANE_MERGE_v1", "S1_LANE_HALTED", "S1_OP_DONE_v1", "S1_HEARTBEAT_v1")
MAX_POST_CHARS = 4000


class Stop(Exception):
    """A check failed: nothing (more) is written in this run. `reason` is the skipped=<...> text."""

    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def need(ok, reason):
    if not ok:
        raise Stop(reason)


# ----------------------------------------------------------------------------------------------- native git reads
class Native:
    """Git reads of the executor, from main's own checkout (never a PR checkout). Tests replace this object."""

    def __init__(self, root):
        self.root = Path(root)
        self.graph = Path(str(root) + ".due-graph")

    def drift(self, base, head):
        """(relation, paths) of base -> head exactly as the brief's due check reads it (ahead, behind, unknown, too_large)."""
        return B.git_drift(self.root, base, head)

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

    def is_ancestor(self, sha, main):
        try:
            B.git(self.root, "remote", "get-url", "origin")
            self.graph.mkdir(parents=True, exist_ok=True)
            B.git(self.graph, "init", "--quiet", "--bare")
            if "origin" not in B.git(self.graph, "remote").split():
                B.git(self.graph, "remote", "add", "origin", B.git(self.root, "remote", "get-url", "origin"))
            if not {sha, main} <= B.fetch_commits(self.graph, [sha, main], "--filter=tree:0"):
                return False
        except Exception:                                        # noqa: BLE001
            return False
        return sha == main or B.on_main(self.graph, sha, main)


# ----------------------------------------------------------------------------------------------- the run
class Run:
    def __init__(self, gh, native, env, files, now_fn=None, out=print):
        self.gh, self.native, self.env, self.files, self.out = gh, native, env, files, out
        self.now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self.writes, self.mode, self.lines, self.ledger_read_at = [], "OFF", [], None
        self.brief = self.decision = None
        self.run_of = B.RunReader(gh)                             # proves which Actions-bot ledger posts are this job's
        self.alarms, self.pending = [], None                      # what makes the process exit non-zero (finish)

    # ---- the ONE place that writes
    def write(self, kind, **kw):
        """kind 'comment' (body=...) or 'merge' (pr=..., sha=...). Refused unless the mode is LIVE, the clock allows a
        write now (H1 is checked before EVERY write), the cap holds and the payload is one of the two allowed shapes."""
        need(self.mode == "LIVE", "executor_not_live")
        need(len(self.writes) < MAX_WRITES, "write_cap")
        clock = D.clock_gate(self.now_fn(), self.decision["generated_at"], self.decision["expires_at"], D.EXECUTE_MAX_AGE_MINUTES)
        need(clock is None, f"clock:{clock}")
        if kind == "comment":
            body = kw["body"]
            need(isinstance(body, str) and 0 < len(body) <= MAX_POST_CHARS and B.first_line_token(body) in POSTS, "post_shape")
            raw, _h = self.gh._request("POST", self.gh.url(f"issues/{B.OWNER_ISSUE}/comments"), {"body": body})
            doc = json.loads(raw)
            self.writes.append(("comment", B.first_line_token(body), doc.get("id")))
            return doc
        need(kind == "merge" and not any(w[0] == "merge" for w in self.writes), "one_merge_per_run")
        pr, sha = kw["pr"], kw["sha"]
        need(type(pr) is int and isinstance(sha, str) and D.SHA40.fullmatch(sha) is not None, "merge_shape")
        need(self.decision.get("action") == "MERGE" and self.decision["merge"]["pr"] == pr and self.decision["merge"]["sha"] == sha, "merge_not_the_decision")
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
        need(not B.lane_halts(late), "lane:C7:halt_after_read")
        need(not any(B.is_s1_author(c) and B.first_line_token(c.get("body")) in ("S1_LANE_MERGE_INTENT_v1", "S1_OP_INTENT_v1") for c in late),
             "lane:C9:intent_after_read")

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
        need(relation == "ahead" and isinstance(paths, list), f"BRIEF_STALE(drift:{relation})")
        need(len(paths) < B.DRIFT_MAX_FILES, "BRIEF_STALE(drift_unreadable)")
        code = [p for p in paths if B.code_drift_path(p)]
        need(not code, "BRIEF_STALE(source_changed)")
        overlap = sorted(set(paths) & set(pr_paths))
        need(not overlap, "C2:needs_branch_update")
        return paths

    # ---- lane, at current main, from fresh reads
    def lane_now(self, main, protected, comments):
        switch, contract, bindings = self.files["switch"], self.files["contract"], self.files["bindings"]
        need(isinstance(switch, dict) and switch.get("contract") == "S1_REVIEWED_MERGE_LANE_v1" and switch.get("state") == "ON", "lane:C7:switch")
        pins = switch.get("pins")
        need(isinstance(pins, dict) and pins, "lane:C7:pins_missing")
        chain = {contract.get("lane_switch_path"): contract.get("lane_switch_blob"), contract.get("action_loop_path"): contract.get("action_loop_blob"),
                 contract.get("tick_path"): contract.get("tick_blob"), **(contract.get("rubric_blobs") or {})}
        want = dict(pins, **chain)
        need(all(isinstance(k, str) and isinstance(v, str) for k, v in want.items()), "lane:C7:contract_unreadable")
        actual = self.native.tree_shas(main, sorted(want) + [B.CONTRACT_FILE])
        for path in sorted(want):
            need(actual.get(path) == want[path], f"lane:C7:pins:{path}")
        need(actual.get(B.CONTRACT_FILE) == self.decision["contract_blob"], "lane:C7:pins:contract_blob")
        halts = B.lane_halts(comments)
        halt = B.standing_halt(halts, switch.get("clears_halt"))
        need(halt is None, f"lane:C7:halt c={halt}")
        runs, _c = self.gh.pages(f"actions/workflows/{Path(bindings['main_health']['workflow_path']).name}/runs",
                                 {"event": "schedule", "branch": "main"}, key="workflow_runs", max_pages=1)
        health = B.main_health(runs, bool(runs), self.now_fn(), B.lane_merges(comments), halts, bindings["main_health"])
        need(health.get("status") == "PASS", f"lane:C7:main_health:{health.get('reason')}")
        r1, c1 = self.gh.pages("rulesets", {"includes_parents": "true"}, max_pages=2)
        r2, c2 = self.gh.pages("rulesets", {"includes_parents": "true"}, max_pages=2)
        rules = B.ruleset_census(r1, r2, c1 and c2)
        need(rules.get("stable") is True and rules.get("census") == (self.brief.get("rulesets") or {}).get("census"), "lane:C8:ruleset_census")
        need(rules.get("active") == 0 and protected is False, "lane:C8:ruleset_unproven")
        return health

    # ---- MERGE: every fact, natively, right before the write
    def verify_merge(self, comments):
        d, brief, m = self.decision, self.brief, self.decision["merge"]
        n, head, repo_id = m["pr"], m["sha"], (brief.get("repo") or {}).get("id")
        entry = next((e for e in brief.get("prs") or [] if e.get("n") == n), None)
        need(entry is not None and entry.get("head") == head and not entry.get("open") and not entry.get("skip"), f"{n}:C8:not_the_briefs_candidate")
        need(D.pr_gates(entry, brief["thin"]) == [], f"{n}:C8:decision_gates")
        repo = self.gh.get("")
        need(repo.get("full_name") == B.REPO and repo.get("fork") is False and repo.get("id") == repo_id and type(repo_id) is int, "B1:repository_identity")

        def head_read():
            pr = self.gh.get(f"pulls/{n}")
            need(pr.get("state") == "open" and pr.get("merged") is not True and pr.get("draft") is False, f"{n}:C8:state")
            need((pr.get("head") or {}).get("sha") == head, f"{n}:C8:head_changed")
            need((pr.get("base") or {}).get("ref") == "main" and ((pr.get("base") or {}).get("repo") or {}).get("id") == repo_id
                 and ((pr.get("head") or {}).get("repo") or {}).get("id") == repo_id, f"{n}:B1:fork_head")
            need(pr.get("mergeable") is not False and pr.get("mergeable_state") not in ("dirty", "blocked"), f"{n}:C2:mergeable")
            return pr

        pr = head_read()
        files, fc = self.gh.pages(f"pulls/{n}/files", max_pages=31)
        need(fc and len(files) == pr.get("changed_files") == m.get("files"), f"{n}:C8:files_changed")
        paths = sorted({f.get("filename") or "" for f in files} | {f["previous_filename"] for f in files if f.get("previous_filename")})
        need(hashlib.sha256("\n".join(paths).encode()).hexdigest()[:16] == m.get("paths_sha256"), f"{n}:C8:files_changed")
        # risk and exclusions, recomputed from the LIVE diff, title and labels (exclusion 3 is a function of the head and of
        # main's code: the head is unchanged and no_code_drift proves main's code is)
        reasons, floor = B.path_exclusions(files, True, self.files["policy"], self.files["gate_isolation"] == "LIVE", {"owner_gated": [], "high_floor": []})
        need(not reasons and floor in D.MERGE_RISKS, f"{n}:C2:owner_gated")
        facts = D.entry_facts(pr, files, True, [])
        need(not facts["x"] and not facts["direction"] and not facts["hold_labels"], f"{n}:C2:judgment")
        need(facts["title_sha256"] == m.get("title_sha256"), f"{n}:C8:title_changed")
        need(not any(f.get("status") not in ("added", "removed", "renamed") and not str(f.get("filename") or "").startswith(("scripts/", "tests/"))
                     and (f.get("deletions") or 0) > (f.get("additions") or 0) for f in files), f"{n}:C2:shrinks")
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
        for t in tuples:
            got = ci.get(t["job"]) or {}
            need(got.get("s") == "PASS" and [got.get("run"), got.get("att"), got.get("job")] == (m.get("ci") or {}).get(t["job"]), f"{n}:C4:ci_identity:{t['job']}")
        checks, k1 = self.gh.pages(f"commits/{head}/check-runs", key="check_runs", max_pages=5)
        statuses, k2 = self.gh.pages(f"commits/{head}/statuses", max_pages=3)
        need(B.checks_summary(checks, statuses, k1 and k2).get("green") is True, f"{n}:C4:checks")
        privacy_job = ci["privacy-scan"]["job"]
        line = B.privacy_line(self.gh.text(f"actions/jobs/{privacy_job}/logs"), head)
        need(line.get("result") == "NO_RESTRICTED_CONTENT", f"{n}:C3:privacy_line")
        # reviews, threads, writer
        commits, cc = self.gh.pages(f"pulls/{n}/commits", max_pages=3)
        prc, c1 = self.gh.pages(f"issues/{n}/comments", max_pages=10)
        reviews, c2 = self.gh.pages(f"pulls/{n}/reviews", max_pages=10)
        inline, c3 = self.gh.pages(f"pulls/{n}/comments", max_pages=10)
        need(cc and c1 and c2 and c3, f"{n}:C5:reviews_unreadable")
        now = self.now_fn()
        need(B.concurrent_writer(commits, cc, prc, head, now, self.files["bindings"]["foreign_commit_quiet_minutes"]) is None, f"{n}:C1:concurrent_writer")
        need(B.changes_requested(reviews) is False, f"{n}:C5:changes_requested")   # on ANY commit: a push never lifts the veto
        item = B.newest_item(prc) or {}                          # the PR's S1_ITEM_v1 history as it is NOW: a risk or kind is only ever raised
        need(item.get("kind") != "DIRECTION", f"{n}:C5:strategist")
        need(D.risk_max(floor, facts["risk"], item.get("risk")) == m.get("risk") and m.get("risk") in D.MERGE_RISKS, f"{n}:C2:risk")
        author = B.authorship(pr, commits, cc, prc)
        cx = B.codex_review(head, pr, commits, cc, prc, reviews, inline, True, now, self.files["budgets"]["codex_silent_hours"])
        if author.get("codex") and cx.get("status") == "FINAL":
            cx = {"status": "INADMISSIBLE"}
        live = {"review": {"codex": cx}, "author": author,
                "thin": {"bot": (pr.get("user") or {}).get("type") != "User", "docs_only": facts["docs_only"],
                         "ai": B.ai_authored(pr, commits, cc, author)}}
        gate = D.review_gate(live, brief["thin"]["review_policy"])
        need(gate is None, f"{n}:{gate}")
        need(("CODEX" if cx.get("status") == "FINAL" else f"NONE(policy={brief['thin']['review_policy']})") == m.get("review"), f"{n}:C8:review_changed")
        threads = B.read_threads(self.gh, n)
        need(threads is not None, f"{n}:C6:threads")
        need(not any(not t.get("resolved") and re.search(r"(?i)\bP[01]\b", t.get("first_body") or "") for t in threads), f"{n}:C6:unresolved_p0p1")
        # lane, drift, intents; then the head once more, immediately before the intent
        main, protected = self.main_now()
        self.no_code_drift(main, paths)
        health = self.lane_now(main, protected, comments)
        open_now = B.open_intents(comments, now, 0, self.run_of)
        need(not any(i.get("kind") == "S1_LANE_MERGE_INTENT_v1" for i in open_now), "lane:C9:open_merge_intent")
        # idempotency key = PR + head: a receipt for it means done, and an earlier intent for it means it was tried.
        # ONE attempt per head, ever: no retry of a refused merge (the owner merges that head, or a new commit arrives)
        key = re.compile(rf"(?m)^pr: {n}\s*$")
        mine = [B.first_line_token(c.get("body")) for c in comments if B.is_s1_author(c) and key.search(str(c.get("body") or ""))
                and head in str(c.get("body") or "")]
        need("S1_LANE_MERGE_v1" not in mine, f"{n}:C9:already_done")
        need(mine.count("S1_LANE_MERGE_INTENT_v1") < MAX_ATTEMPTS_PER_HEAD and (n, head) not in B.attempted_heads(comments), f"{n}:C9:attempted_head")
        head_read()                                              # the head a SECOND time, the last read before the intent
        return {"paths": paths, "main": main, "privacy_run": ci["privacy-scan"]["run"], "repo_id": repo_id, "health": health}

    def readback(self, n, head, intent_at, paths, actor=B.ACTIONS_BOT["login"]):
        pr = self.gh.get(f"pulls/{n}")
        sha = pr.get("merge_commit_sha") if pr.get("merged") is True else None
        commit = self.gh.get(f"commits/{sha}") if isinstance(sha, str) and D.SHA40.fullmatch(sha) else None
        main, _p = self.main_now()
        blobs = None
        if commit is not None and paths:
            a, b = self.native.tree_shas(sha, paths), self.native.tree_shas(head, paths)
            blobs = [(p, a.get(p), b.get(p)) for p in paths]
        state, why = D.readback_verdict(pr, head, intent_at, commit, blobs, commit is not None and self.native.is_ancestor(sha, main),
                                        self.now_fn(), executor_login=actor)
        return state, why, {"pr": n, "head": head, "merge_commit": sha, "main_after": main, "paths": len(paths or [])}

    def do_merge(self, comments):
        d, m = self.decision, self.decision["merge"]
        proof = self.verify_merge(comments)
        self.last_look()
        if self.mode != "LIVE":
            return f"WOULD_MERGE(pr={m['pr']},head={m['sha'][:8]},risk={m['risk']},review={m['review']})"
        run_id = self.env.get("GITHUB_RUN_ID")
        intent = self.write("comment", body=D.intent_body(d, proof["repo_id"], self.files["contract"]["action_loop_blob"], run_id))
        self.pending = f"intent_without_outcome(c={intent.get('id')})"   # until a receipt or a halt is posted: an alarm
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
            self.write("comment", body=D.merge_receipt_body(d, proof["repo_id"], intent.get("id"), rb, run_id, proof["privacy_run"]))
            self.pending = None
            return f"MERGED(n=1,main={str(rb['main_after'])[:8]})"
        if state == "MISMATCH":
            self.write("comment", body=D.halt_body("readback", pr=m["pr"], head=m["sha"], detail=why, contract=d["contract"], run_id=run_id))
            self.pending = None
            self.alarms.append(f"readback_mismatch({why})")
            return f"LANE_HALTED(readback:{why})"
        return f"MERGE_UNSETTLED({state}:{why})"                 # the intent stays OPEN; the next run's RECONCILE settles it

    # ---- RECONCILE: an executor intent with no outcome (EVIDENCE_BINDINGS B3)
    def reconcile(self, comments):
        """Returns the result text when a receipt or a halt was posted (that is this run's action), else None."""
        now, done, records = self.now_fn(), None, []
        mine = [i for i in B.open_intents(comments, now, 0, self.run_of) if i.get("kind") == "S1_LANE_MERGE_INTENT_v1"]
        by_id = {c.get("id"): c for c in comments}
        for it in sorted(mine, key=lambda i: i["id"])[:RECONCILES_PER_RUN]:
            row = by_id.get(it["id"]) or {}
            f = B.fields(row.get("body"))
            head = (f.get("head") or "").strip()
            if it.get("pr") is None or not D.SHA40.fullmatch(head):
                continue
            files, fc = self.gh.pages(f"pulls/{it['pr']}/files", max_pages=31)
            paths = sorted({x.get("filename") or "" for x in files} | {x["previous_filename"] for x in files if x.get("previous_filename")}) if fc else []
            state, why, rb = self.readback(it["pr"], head, row.get("created_at"), paths, actor=B.login(row))
            contract = (f.get("contract") or self.decision["contract"]).strip()
            run_id = self.env.get("GITHUB_RUN_ID")
            if self.mode != "LIVE":
                records.append(f"WOULD_RECONCILE({it['id']}:{state})")
                continue
            if state == "MATCH":
                old = {"id": f.get("decision"), "run_id": f.get("brief"), "main": (f.get("main") or "").strip() or None, "contract": contract, "merge": None}
                self.write("comment", body=D.merge_receipt_body(old, self.brief["repo"]["id"], it["id"], rb, run_id, None, reconciled=True) + "\nevidence_gap: review, privacy, ci, main_health")
                return f"RECONCILED(c={it['id']})"
            if state == "MISMATCH":
                self.write("comment", body=D.halt_body("reconcile_readback", pr=it["pr"], head=head, detail=why, contract=contract, run_id=run_id))
                self.alarms.append(f"reconcile_readback_mismatch({why})")
                return f"LANE_HALTED(reconcile:{why})"
            if state in ("ABSENT", "FOREIGN"):
                self.write("comment", body=D.op_done_body(it["id"], state, f"pr={it['pr']} {why}", contract=contract, run_id=run_id))
                records.append(f"{state}({it['id']})")
        if records:
            self.say("S1_EXECUTOR_RECONCILE " + " ".join(records))
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
            need(len(B.c1b_parents(commit)) != 1 or not B.SQUASH_SUBJECT.search(subject), "-:C1b:is_a_squash_merge")
            a, b = B.c1b_entries(self.gh.get(f"git/trees/{h['parent']}")), B.c1b_entries(self.gh.get(f"git/trees/{h['commit']}"))
            need(a != b, "-:C1b:trees_equal")
            need(self.native.is_ancestor(h["commit"], main), "-:C1b:not_on_main")
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
             and run.get("status") == "completed" and run.get("conclusion") in B.FAILED_CONCLUSIONS, "-:C7:run")
        if re.search(rf"(?<!\d){h['run']}(?!\d)", named):
            return "LANE_HALTED(main_health:already_posted)"
        if self.mode != "LIVE":
            return f"WOULD_HALT(main_health:{h['run']})"
        self.write("comment", body=D.halt_body("main_health", run=h["run"], contract=d["contract"], run_id=run_id))
        return "LANE_HALTED(main_health)"

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
        self.brief, self.decision = brief, d
        env = self.env
        if not (env.get("GITHUB_REPOSITORY") == B.REPO and env.get("GITHUB_REF") == "refs/heads/main" and env.get("GITHUB_EVENT_NAME") in EVENTS
                and str(d.get("run_id")) == env.get("GITHUB_RUN_ID") and str(d.get("run_attempt")) == env.get("GITHUB_RUN_ATTEMPT")
                and d.get("main") == env.get("GITHUB_SHA")):
            return end("NOOP", None, None, "BRIEF_UNVERIFIED(run_binding)")
        cfg = D.thin_config(self.files.get("switch"))
        if cfg != brief.get("thin") or cfg["executor"] != d["executor"] or cfg["review_policy"] != d["review_policy"]:
            return end("NOOP", None, None, "BRIEF_UNVERIFIED(switch)")
        self.mode = D.effective_mode(cfg["executor"], env.get("S1_EXECUTOR_HOLD"))
        if self.mode == "OFF":
            return end("NOOP", None, None, "EXECUTOR_OFF(" + ("hold" if cfg["executor"] != "OFF" else "switch") + ")")
        clock = D.clock_gate(self.now_fn(), d["generated_at"], d["expires_at"], D.EXECUTE_MAX_AGE_MINUTES)
        if clock is not None:
            return end("NOOP", None, None, clock)
        try:
            comments = self.ledger()
            settled = self.reconcile(comments)
            if settled is not None:                              # a reconciled receipt or a reconcile halt is this run's action
                return end("MERGE" if settled.startswith("RECONCILED") else "NOOP", None, None, settled)
            beat = self.heartbeat(comments)
            if beat:
                self.say(f"S1_EXECUTOR_HEARTBEAT {beat}")
            if d["action"] == "HALT":
                return end("NOOP", None, None, self.do_halt(comments))
            if d["action"] == "MERGE":
                result = self.do_merge(comments)
                return end("MERGE" if result.startswith("MERGED") else "NOOP", d["pr"], d["head"], result)   # only a read-back merge is a MERGE line
            return end("NOOP", None, None, d["result"])
        except Stop as stop:
            pr, head = (d.get("pr"), d.get("head")) if d["action"] == "MERGE" else (None, None)
            return end("NOOP", pr, head, f"NOTHING_ACTIONABLE(skipped={stop.reason})")
        except B.StopReading as stop:
            if self.writes:
                self.alarms.append(f"read_stopped_after_write({stop.reason})")
            return end("NOOP", None, None, f"BRIEF_INCOMPLETE(executor:{stop.reason})")
        except Exception as exc:                                 # noqa: BLE001  (an unreadable read: nothing more is written)
            self.alarms.append(f"unexpected({type(exc).__name__})")
            return end("NOOP", None, None, f"BRIEF_INCOMPLETE(executor:{type(exc).__name__})")

    def finish(self, action, pr, head, result):
        d = self.decision or {}
        main, contract = str(d.get("main") or "-")[:8], d.get("contract") or "-"
        if self.pending:                                         # an intent was posted and this run posted no outcome for it
            self.alarms.append(self.pending)
        if self.alarms:
            self.say("S1_EXECUTOR_ALARM " + " ".join(self.alarms))
        self.say(f"S1_EXECUTOR_V1 mode={self.mode} decision={d.get('id')} action={d.get('action')} result={result} "
                 f"writes={len(self.writes)}:{','.join(str(w[1]) for w in self.writes) or '-'}")
        self.say(f"S1_TICK {action} {pr if pr is not None else '-'} {head[:8] if head else '-'} {result} main={main} contract={contract}")
        return {"mode": self.mode, "action": action, "pr": pr, "head": head, "result": result, "writes": list(self.writes), "lines": list(self.lines),
                "alarms": list(self.alarms)}


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
            "bindings": B.parse_json_block(read(B.BINDINGS_FILE), "S1_EVIDENCE_BINDINGS_v1"),
            "budgets": B.parse_json_block(read("00_FMOS/S1/STEWARD_STATES.md"), "S1_STEWARD_BUDGETS_v1")}


def main(argv):
    if len(argv) != 3 or argv[1] != "execute":
        raise SystemExit("usage: s1_executor_v1.py execute <issue body file>")
    token = os.environ.get("GITHUB" + "_TOKEN", "")
    if os.environ.get("GITHUB_REPOSITORY", B.REPO) != B.REPO:
        raise SystemExit(f"REFUSED: repository is not {B.REPO}")
    root = B.CHECKOUT_ROOT
    B.GIT_ENV = B.token_git_env(token)
    run = Run(B.GitHub(token, budget=EXECUTE_API_CALLS), Native(root), dict(os.environ), read_files(root))
    out = run.execute(Path(argv[2]).read_text(encoding="utf-8"))
    write_summary(os.environ, out["lines"])
    return 1 if out["alarms"] else 0                             # a failed JOB (continue-on-error), never a failed run


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
