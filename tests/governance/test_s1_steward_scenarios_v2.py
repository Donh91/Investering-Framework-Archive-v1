"""S1 v2 steward: behaviour tests on a pure-Python model of 00_FMOS/S1/STEWARD_STATES.md and REVIEW_ADMISSION.md.

The model reads its budgets from the machine-readable S1_STEWARD_BUDGETS_v1 block of STEWARD_STATES.md, so a budget
edit there changes these results. Token tests (test_s1_reviewed_merge_lane_v1.py) pin the wording; these tests pin the
behaviour: budgets force dispositions, parking terminates, closes need two signals, review needs a non-author, OWNER_ONLY
never merges, the loop guard fires, Monday is read-only, and S1 keeps working when Claude is silent for 7 days.
No network, no GitHub, no clock: every scenario uses fixture data and a simulated day counter.
"""
import json
import random
import re
import unittest
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S1 = ROOT / "00_FMOS" / "S1"
STATES_MD = (S1 / "STEWARD_STATES.md").read_text(encoding="utf-8")
ADMISSION_MD = (S1 / "REVIEW_ADMISSION.md").read_text(encoding="utf-8")
B = json.loads(re.search(r"```json\n(\{.*?\})\n```", STATES_MD, re.S).group(1))
TERMINAL = {"MERGED", "CLOSED_NOISE", "PARKED_OWNER_DECISION"}
S1_TRAILER = "S1-Authored-By: 6ae5fd466b48819187abc224ec0f1c5f"


@dataclass
class Head:
    sha: str
    branch: str = "feature/x"
    commit_messages: tuple = ("fix: x",)
    commit_logins: tuple = ("Donh91",)
    commits_readable: bool = True


@dataclass
class Item:
    key: str
    state: str = "DISCOVERED"
    kind: str = "FIX"
    risk: str = "LOW"
    owner_only: bool = False
    attempt: int = 0
    park_count: int = 0
    due: int = 0
    signals: set = field(default_factory=set)
    new_info: bool = False
    noop_streak: int = 0
    triage_cycles: int = 0
    repair_cycles: int = 0
    log: list = field(default_factory=list)


# ---------------------------------------------------------------- review admission (REVIEW_ADMISSION.md)
def s1_authored(h: Head) -> bool:
    return (not h.commits_readable or h.branch.startswith("s1/") or any(S1_TRAILER in m for m in h.commit_messages))


def codex_authored(h: Head) -> bool:
    return (not h.commits_readable or h.branch.startswith("codex/") or "chatgpt-codex-connector[bot]" in h.commit_logins)


def admissible_review(h: Head, risk: str, reviews: dict, codex_silent: bool, docs_only: bool = True, ci_green: bool = True):
    """Return the first admissible review kind for h, or None. reviews maps kind -> verdict for this exact head."""
    if reviews.get("native") == "CHANGES_REQUESTED" or "REQUEST_CHANGES" in reviews.values() or "BLOCK" in reviews.values():
        return None
    if reviews.get("codex") == "APPROVE" and not codex_authored(h):
        return "codex"
    if reviews.get("claude") == "APPROVE":
        return "claude"
    if (reviews.get("specialist") == "APPROVE" and not s1_authored(h) and risk == "LOW" and docs_only and ci_green   # D3: LOW LANE only
            and (codex_silent or codex_authored(h))):
        return "specialist"
    return None


# ---------------------------------------------------------------- state machine (STEWARD_STATES.md)
def enter(item: Item, state: str, today: int, reason: str, attempt_up: bool = False):
    if state == "TRIAGED" and item.state != "TRIAGED":
        if item.triage_cycles >= B["max_triage_cycles"]:        # LIFETIME CAP
            state, reason = "PARKED_OWNER_DECISION", "cycle_cap"            # D2: a cap never closes
        else:
            item.triage_cycles += 1
    if state in ("BUILD", "TEST") and item.state == "REVIEW":
        if item.repair_cycles >= B["max_repair_cycles"]:        # REPAIR CAP
            state, reason = "PARKED_OWNER_DECISION", "repair_cap"
        else:
            item.repair_cycles += 1
    item.attempt = item.attempt + 1 if (attempt_up and state == item.state) else (1 if attempt_up else 0)
    item.state = state
    item.due = today + (B["park_revisit_max_days"] if state == "PARKED" else B["dwell_days"].get(state, 10 ** 6))
    item.log.append((today, state, reason))


def overdue(item: Item, today: int) -> bool:
    limit = B["max_attempts"].get(item.state)
    return (today > item.due or (limit is not None and item.attempt > limit) or item.noop_streak >= B["same_noop_runs"])


def park(item: Item, today: int, reason: str):
    item.noop_streak = 0
    if item.park_count >= B["max_parks"]:     # a fourth park is never made
        enter(item, "PARKED_OWNER_DECISION", today, "park_limit")
        return
    item.park_count += 1
    enter(item, "PARKED", today, reason)


def revisit(item: Item, today: int, strategist: dict):
    """F7 / PARKED: what happens at the revisit date."""
    if item.new_info:
        item.new_info = False
        enter(item, "TRIAGED", today, "new_info")
        return
    if strategist.get(item.key) == "KEEP":
        enter(item, "TRIAGED", today, "strategist_keep")
        return
    if strategist.get(item.key) == "CLOSE":
        item.signals.add("strategist_concur")
    if item.park_count == 1:
        park(item, today, "revisit_no_info")          # and one S1_STRATEGIST_CONSULT_v1
    elif item.park_count == 2:
        if close_allowed(item):
            enter(item, "CLOSED_NOISE", today, "signals")
        else:
            park(item, today, "final_park")
    elif close_allowed(item):
        enter(item, "CLOSED_NOISE", today, "signals")
    else:
        enter(item, "PARKED_OWNER_DECISION", today, "stale_final_park")


OBJECTIVE = {"duplicate", "superseded", "superseded_native", "premise_falsified"}
INDEPENDENT = {"strategist_concur", "reviewer_concur", "superseded_native"}
CONTENT = OBJECTIVE | INDEPENDENT   # time and budget facts (stale_*, park_limit, cycle_cap, no_owner_link) never count


def close_allowed(item) -> bool:
    """D2: CLOSED_NOISE needs >= 2 content signals, one objective, one independent of S1, risk LOW/MEDIUM, not OWNER_ONLY."""
    if isinstance(item, set):
        item = Item("probe", signals=item)
    sig = item.signals & CONTENT
    if "superseded_native" in sig:
        sig = sig - {"superseded"}   # one fact counts once
    return (len(sig) >= B["close_noise_min_signals"] and bool(sig & OBJECTIVE) and bool(sig & INDEPENDENT)
            and item.risk in ("LOW", "MEDIUM") and not item.owner_only)


def counters(comments: list, receipts: set) -> int:
    """D2: park_count only from receipt-backed S1_ITEM_v1 comments (id listed in a later heartbeat receipts=)."""
    return max([c["park_count"] for c in comments if c["id"] in receipts] or [0])


def main_health(runs, now_h: int, readable: bool = True) -> str:
    """D1: newest kept scheduled main run of the health workflow, SUCCESS within 26 h; else NOT PROVEN."""
    if not readable:
        return "NOT_PROVEN(TOOL_CANNOT_READ)"
    kept = [r for r in runs if r["path"] == ".github/workflows/automation-production-health.yml" and r["event"] == "schedule"
            and r["head_branch"] == "main" and (r.get("head_repository") or {}).get("full_name") == "Donh91/Investering-Framework-Archive-v1"
            and r["status"] == "completed"]
    if not kept:
        return "NOT_PROVEN(main_health_stale)"
    newest = max(kept, key=lambda r: r["completed_h"])
    if now_h - newest["completed_h"] > 26:
        return "NOT_PROVEN(main_health_stale)"
    return "PASS" if newest["conclusion"] == "success" else "FAIL"


def forced_disposition(item: Item, today: int, ctx: dict):
    """FORCED DISPOSITION TABLE F1-F7, first match wins. Returns the row id."""
    if item.owner_only and ctx.get("waiting_only_for_owner", {}).get(item.key):
        enter(item, "OWNER_APPROVAL", today, "F1")
        return "F1"
    if item.state == "PARKED":
        revisit(item, today, ctx.get("strategist", {}))
        return "F7"
    if item.state == "REVIEW" and item.attempt < B["max_attempts"]["REVIEW"]:
        enter(item, "REVIEW", today, "F2", attempt_up=True)
        return "F2"
    if item.state in ("REVIEW", "BUILD", "TEST"):
        park(item, today, "F3")
        return "F3"
    if item.state == "STRATEGIST":
        if item.kind == "RESEARCH" and ctx.get("active_handoffs", 0) < B["max_active_research_handoffs"]:
            enter(item, "RESEARCH_HANDOFF", today, "F4")
        else:
            park(item, today, "F4")
        return "F4"
    if item.state == "RESEARCH_HANDOFF":
        park(item, today, "F5")
        return "F5"
    if item.state in ("DISCOVERED", "TRIAGED", "PLAN"):
        if item.new_info and item.attempt < B["max_attempts"][item.state]:
            item.new_info = False
            enter(item, "TRIAGED", today, "F6", attempt_up=True)
        else:
            park(item, today, "F6")
        return "F6"
    raise AssertionError(f"no row for {item.state}")


# ---------------------------------------------------------------- branch update (STEWARD_STATES.md BRANCH UPDATE)
def three_way(base: dict, ours: dict, theirs: dict):
    """Reference merge of path->content maps; None on a conflict."""
    out = {}
    for p in set(base) | set(ours) | set(theirs):
        b, o, t = base.get(p), ours.get(p), theirs.get(p)
        if o == t:
            v = o
        elif o == b:
            v = t
        elif t == b:
            v = o
        else:
            return None
        if v is not None:
            out[p] = v
    return out


def route2_branch_update(base: dict, head: dict, main: dict):
    """Route 2: tree of M with each PR path set to its blob at H, only if main changed none of the PR's paths."""
    pr_paths = {p for p in set(base) | set(head) if base.get(p) != head.get(p)}
    main_paths = {p for p in set(base) | set(main) if base.get(p) != main.get(p)}
    if pr_paths & main_paths:
        return None                                   # conflict: rule 2(d) "@codex address", never overwrite
    tree = dict(main)
    for p in pr_paths:
        if head.get(p) is None:
            tree.pop(p, None)
        else:
            tree[p] = head[p]
    return tree


def branch_update_readback(base: dict, head: dict, main: dict, new: dict) -> bool:
    pr_paths = {p for p in set(base) | set(head) if base.get(p) != head.get(p)}
    main_paths = {p for p in set(base) | set(main) if base.get(p) != main.get(p)}
    diff_vs_main = {p for p in set(main) | set(new) if main.get(p) != new.get(p)}
    return (not (pr_paths & main_paths) and diff_vs_main == pr_paths and all(new.get(p) == head.get(p) for p in pr_paths)
            and all(new.get(p) == main.get(p) for p in main_paths - pr_paths))


def may_merge(item: Item, head: Head, reviews: dict, codex_silent: bool, ctx: dict) -> bool:
    if item.owner_only or ctx.get("monday_read_only") or ctx.get("lane") != "ON":
        return False
    if item.kind == "DIRECTION" and ctx.get("strategist", {}).get(item.key) != "CONCUR":
        return False
    kind = admissible_review(head, item.risk, reviews, codex_silent)
    if kind is None:
        return False
    if item.risk in ("HIGH", "HIGH_IMPACT") and kind == "specialist":
        return False
    return ctx.get("ci_green", True)


def waiting_only_for_owner(ci_green, review_kind, p0p1, changes_requested, high_evidence, package, detached):
    return bool(ci_green and review_kind and not p0p1 and not changes_requested and high_evidence == "PASS"
                and (not package or review_kind != "claude" or detached))


def first_line(waiting, lane_off_reason, manual_only_pkgs):
    entries = [f"#{n} {h[:8]}" for n, h in waiting]
    if lane_off_reason:
        entries.append(f"LANE_OFF({lane_off_reason})")
    entries += [f"pkg{p}:manual_only" for p in manual_only_pkgs]
    return "OWNER APPROVAL REQUIRED: " + (" ; ".join(entries) if entries else "NONE")


class Run:
    """One hourly S1 run on a set of items: ONE action (a batch of up to max_transitions_per_run is one action)."""

    def __init__(self, today, hour_cph, weekday):
        self.today, self.hour, self.weekday = today, hour_cph, weekday
        self.writes = []

    def monday_read_only(self):
        return self.weekday == 0 and (9 * 60 + 30) <= self.hour < (10 * 60 + 30)

    def execute(self, items, ctx):
        lines = [first_line(ctx.get("waiting", []), ctx.get("lane_off"), ctx.get("manual_only", [])),
                 "HIGH_IMPACT BLOCKED: NONE", "DISPOSITIONS TODAY: merged=0 parked=0 closed=0 handed_off=0 owner=0"]
        if self.monday_read_only():
            return lines, "NOOP MONDAY_READ_ONLY"
        due = [i for i in items if i.state not in TERMINAL | {"OWNER_APPROVAL"} and overdue(i, self.today)]
        if due:
            for item in sorted(due, key=lambda i: i.due)[:B["max_transitions_per_run"]]:
                self.writes.append((item.key, forced_disposition(item, self.today, ctx)))
            return lines, "STEWARD DISPOSED"
        return lines, "NOOP NOTHING_ACTIONABLE"


class ScenarioTest(unittest.TestCase):
    def test_branch_update_never_loses_main_changes(self):
        """R1 P1-1: route 2 equals a real 3-way merge when disjoint, refuses a shared file, and the readback catches overwrites."""
        base = {"ledger.csv": "row1", "a.py": "a0", "b.py": "b0", "old.txt": "x"}
        head = {"ledger.csv": "row1", "a.py": "a1", "b.py": "b0"}            # PR changes a.py, removes old.txt
        main = {"ledger.csv": "row1\nrow2_main_writer", "a.py": "a0", "b.py": "b1", "old.txt": "x"}
        new = route2_branch_update(base, head, main)
        self.assertEqual(new, three_way(base, head, main))
        self.assertTrue(branch_update_readback(base, head, main, new))
        shared_head = {"ledger.csv": "row1\nrow2_pr", "a.py": "a0", "b.py": "b0", "old.txt": "x"}
        self.assertIsNone(route2_branch_update(base, shared_head, main), "a shared file is a conflict, never an overlay")
        overlay = dict(main, **{"ledger.csv": "row1\nrow2_pr"})          # the v2.0-draft construction R1 reproduced
        self.assertFalse(branch_update_readback(base, shared_head, main, overlay), "readback must catch lost main rows")
        rng = random.Random(7)
        for _ in range(500):
            paths = [f"f{i}" for i in range(6)]
            b = {p: "0" for p in paths if rng.random() < 0.8}
            h = {p: rng.choice([b.get(p), "h"]) for p in paths}
            m = {p: rng.choice([b.get(p), "m"]) for p in paths}
            h = {k: v for k, v in h.items() if v is not None}
            m = {k: v for k, v in m.items() if v is not None}
            got = route2_branch_update(b, h, m)
            if got is not None:
                self.assertEqual(got, three_way(b, h, m))
                self.assertTrue(branch_update_readback(b, h, m, got))
        for token in ("main changed NONE of the PR's files", "never by overwriting", "parents are exactly [H, M]",
                      "every path that main changed since the merge base still has its blob at M", "expected_head_sha = H",
                      "still lists none of the PR paths"):
            self.assertIn(token, STATES_MD)

    def test_new_information_cannot_loop_forever(self):
        """R1 P2-4: TRIAGED with new information every day, and a handoff that is always answered, both end."""
        it = Item("pr:20")
        enter(it, "TRIAGED", 0, "start")
        for day in range(1, 400):
            it.new_info = True
            if it.state in TERMINAL:
                break
            if overdue(it, day):
                forced_disposition(it, day, {})
        self.assertIn(it.state, TERMINAL, it.log[-5:])
        loop = Item("pr:21", kind="RESEARCH")
        enter(loop, "TRIAGED", 0, "start")
        for day in range(1, 400):
            if loop.state in TERMINAL:
                break
            if loop.state == "TRIAGED":
                enter(loop, "STRATEGIST", day, "consult")
            elif loop.state == "STRATEGIST":
                enter(loop, "RESEARCH_HANDOFF", day, "handoff")
            elif loop.state == "RESEARCH_HANDOFF":
                enter(loop, "TRIAGED", day, "answered")           # always answered
            elif overdue(loop, day):
                forced_disposition(loop, day, {})
        self.assertIn(loop.state, TERMINAL, loop.log[-5:])
        self.assertLessEqual(loop.triage_cycles, B["max_triage_cycles"])
        self.assertIn("LIFETIME CAP", STATES_MD)

    def test_review_test_cannot_alternate_forever(self):
        """R2 P2-1: a PR that bounces REVIEW -> TEST (repair) -> REVIEW every day still ends."""
        it = Item("pr:22")
        enter(it, "REVIEW", 0, "green")
        for day in range(1, 400):
            if it.state in TERMINAL:
                break
            if it.state == "REVIEW":
                enter(it, "TEST", day, "repair")
            elif it.state == "TEST":
                enter(it, "REVIEW", day, "green again")
            elif overdue(it, day):
                forced_disposition(it, day, {})
        self.assertIn(it.state, TERMINAL, it.log[-4:])
        self.assertLessEqual(it.repair_cycles, B["max_repair_cycles"])
        self.assertIn("REPAIR CAP", STATES_MD)

    def test_weak_signals_never_close(self):
        self.assertFalse(close_allowed({"duplicate", "no_owner_link"}))
        self.assertFalse(close_allowed({"duplicate", "superseded"}), "D2: two objective signals but none independent of S1")
        self.assertTrue(close_allowed({"duplicate", "strategist_concur"}))
        self.assertIn("duplicate and no_owner_link alone never close", STATES_MD)

    def test_forged_comments_only_raise(self):
        """R1 P2-2: S1 takes the maximum over history and a fresh classification, so a forged S1_ITEM_v1 cannot lower risk."""
        order = ["LOW", "MEDIUM", "HIGH", "HIGH_IMPACT"]
        history, fresh, forged = ["HIGH"], "MEDIUM", "LOW"
        self.assertEqual(max(history + [fresh, forged], key=order.index), "HIGH")
        self.assertIn("S1 never lowers anything a comment says", STATES_MD)
        self.assertIn("re-derives every RUBRIC item from native reads of H itself", ADMISSION_MD)

    def test_budget_block_is_complete(self):
        for state in ("DISCOVERED", "TRIAGED", "PLAN", "STRATEGIST", "BUILD", "TEST", "REVIEW", "RESEARCH_HANDOFF"):
            self.assertIn(state, B["dwell_days"])
            self.assertGreater(B["dwell_days"][state], 0)
        self.assertLessEqual(B["park_revisit_max_days"], 30)
        self.assertIn("becomes PARKED_OWNER_DECISION instead (reason park_limit)", STATES_MD)
        self.assertEqual(B["same_noop_runs"], 3)
        self.assertEqual(B["max_active_research_handoffs"], 3)
        self.assertGreaterEqual(B["close_noise_min_signals"], 2)
        for row in ("F1", "F2", "F3", "F4", "F5", "F6", "F7"):
            self.assertIn(f"\n- {row} ", STATES_MD)

    def test_s1_pr_hits_review_budget(self):
        """Scenario 1: a PR in REVIEW gets re-requested once, then parked; it never waits forever."""
        it = Item("pr:1", kind="FIX")
        enter(it, "REVIEW", 0, "green", attempt_up=True)
        day, rows = 0, []
        while it.state == "REVIEW":
            day += 1
            if overdue(it, day):
                rows.append(forced_disposition(it, day, {}))
        self.assertEqual(rows, ["F2", "F3"])
        self.assertEqual(it.state, "PARKED")
        self.assertLessEqual(day, 1 + 2 * (B["dwell_days"]["REVIEW"] + 1))

    def test_park_revisit_cycle_terminates(self):
        """Scenario 2: park -> revisit -> park + consult -> final park -> CLOSED_NOISE; new info returns to TRIAGED."""
        it = Item("pr:2")
        park(it, 0, "repair_budget")
        day = 0
        while it.state == "PARKED":
            day = it.due + 1
            forced_disposition(it, day, {})
        self.assertEqual(it.state, "PARKED_OWNER_DECISION", "D2: time alone never closes")
        self.assertEqual(it.park_count, B["max_parks"])
        self.assertLessEqual(day, B["max_parks"] * (B["park_revisit_max_days"] + 1))
        back = Item("pr:3")
        park(back, 0, "x")
        back.new_info = True
        forced_disposition(back, back.due + 1, {})
        self.assertEqual(back.state, "TRIAGED")
        keep = Item("pr:4")
        park(keep, 0, "x")
        forced_disposition(keep, keep.due + 1, {"strategist": {"pr:4": "KEEP"}})
        self.assertEqual(keep.state, "TRIAGED")

    def test_duplicate_close_needs_two_signals(self):
        """Scenario 3: a duplicate closes on the second revisit only with a second independent signal."""
        one = Item("pr:5", signals={"duplicate"})
        park(one, 0, "x"); park(one, 1, "revisit_no_info")
        forced_disposition(one, one.due + 1, {})
        self.assertEqual(one.state, "PARKED", "one signal alone never closes")
        two = Item("pr:6", signals={"duplicate"})
        park(two, 0, "x"); park(two, 1, "revisit_no_info")
        forced_disposition(two, two.due + 1, {"strategist": {"pr:6": "CLOSE"}})
        self.assertEqual(two.state, "CLOSED_NOISE")
        self.assertEqual(two.signals, {"duplicate", "strategist_concur"})

    def test_missing_reviewer(self):
        """Scenario 4: without Claude, Codex reviews; a specialist only for LOW/MEDIUM non-S1 heads when Codex is silent."""
        plain, s1h, codexh = Head("a" * 40), Head("b" * 40, branch="s1/pkg-1"), Head("c" * 40, branch="codex/fix")
        trailer = Head("d" * 40, commit_messages=("fix", "fix: y\n\n" + S1_TRAILER))
        unreadable = Head("e" * 40, commits_readable=False)
        self.assertEqual(admissible_review(plain, "LOW", {"codex": "APPROVE"}, False), "codex")
        self.assertIsNone(admissible_review(codexh, "LOW", {"codex": "APPROVE"}, False), "Codex never reviews its own head")
        self.assertEqual(admissible_review(plain, "LOW", {"specialist": "APPROVE"}, True), "specialist")
        self.assertIsNone(admissible_review(plain, "LOW", {"specialist": "APPROVE"}, False), "specialist only when Codex is silent")
        self.assertIsNone(admissible_review(plain, "MEDIUM", {"specialist": "APPROVE"}, True), "D3: MEDIUM needs Codex or detached Claude")
        self.assertIsNone(admissible_review(plain, "HIGH", {"specialist": "APPROVE"}, True), "HIGH needs Codex or Claude")
        for head in (s1h, trailer, unreadable):
            self.assertIsNone(admissible_review(head, "LOW", {"specialist": "APPROVE"}, True), "no self-review by S1")
        self.assertEqual(admissible_review(s1h, "LOW", {"codex": "APPROVE"}, False), "codex")
        self.assertIsNone(admissible_review(plain, "LOW", {"codex": "APPROVE", "native": "CHANGES_REQUESTED"}, False))
        self.assertIsNone(admissible_review(plain, "LOW", {"codex": "APPROVE", "claude": "REQUEST_CHANGES"}, False))
        it = Item("pr:7", state="REVIEW")
        self.assertFalse(may_merge(it, s1h, {}, True, {"lane": "ON"}), "no reviewer means no merge")
        for kind in ("(i) CODEX", "(ii) CLAUDE", "(iii) SPECIALIST", "never writes an S1_SPECIALIST_REVIEW_v1 for a head it authored"):
            self.assertIn(kind, ADMISSION_MD)

    def test_high_impact_item_is_owner_only(self):
        """Scenario 5: an OWNER_ONLY PR never merges; it waits for the owner only when every gate passed."""
        it = Item("pr:8", owner_only=True, risk="HIGH")
        self.assertFalse(may_merge(it, Head("f" * 40), {"codex": "APPROVE"}, False, {"lane": "ON"}))
        self.assertTrue(waiting_only_for_owner(True, "codex", False, False, "PASS", False, False))
        for broken in ((False, "codex", False, False, "PASS", False, False), (True, None, False, False, "PASS", False, False),
                       (True, "codex", True, False, "PASS", False, False), (True, "codex", False, True, "PASS", False, False),
                       (True, "codex", False, False, "HOLD", False, False), (True, "claude", False, False, "PASS", True, False)):
            self.assertFalse(waiting_only_for_owner(*broken), broken)
        line = first_line([(8, "f" * 40)], "pins:AGENTS.md", [123])
        self.assertEqual(line, "OWNER APPROVAL REQUIRED: #8 ffffffff ; LANE_OFF(pins:AGENTS.md) ; pkg123:manual_only")
        self.assertEqual(first_line([], None, []), "OWNER APPROVAL REQUIRED: NONE")
        self.assertNotEqual(first_line([], "main_health", []), "OWNER APPROVAL REQUIRED: NONE", "P2-4: LANE_OFF is never NONE")
        forced_disposition(it, 1, {"waiting_only_for_owner": {"pr:8": True}})
        self.assertEqual(it.state, "OWNER_APPROVAL")

    def test_named_high_impact_is_never_lane_merged(self):
        """R4 P2-1: a PR that a receipt or its body names HIGH_IMPACT is OWNER_ONLY; the lane never replaces the owner for it."""
        loop = (S1 / "ACTION_LOOP.md").read_text(encoding="utf-8").splitlines()
        h2 = next(l for l in loop if l.startswith("H2 "))
        self.assertNotIn("HIGH or HIGH_IMPACT;", h2)
        self.assertIn("lane-eligible PRs of risk class HIGH; HIGH_IMPACT (owner-only", h2)
        owner_only = next(l for l in loop if l.startswith("- A PR is OWNER_ONLY"))
        self.assertIn("its risk class is HIGH_IMPACT, EXTREME or unclear", owner_only)
        self.assertIn("A PR named HIGH_IMPACT is OWNER_ONLY", (S1 / "REVIEW_ADMISSION.md").read_text(encoding="utf-8"))
        it = Item("pr:9", owner_only=True, risk="HIGH_IMPACT")
        self.assertFalse(may_merge(it, Head("e" * 40), {"codex": "APPROVE"}, False, {"lane": "ON"}))

    def test_every_forced_park_reason_is_in_the_rules(self):
        """Mutant gap (v2.1): the F3 park reasons used by the simulator must exist in the rule text."""
        self.assertIn("PARKED (reason review_budget, repair_budget or test_budget)", (S1 / "STEWARD_STATES.md").read_text(encoding="utf-8"))

    def test_d1_main_health_freshness(self):
        """D1: 26 h freshness from the schedule endpoint; PR, dispatch, workflow_run, fork and other-workflow runs never count."""
        own = {"full_name": "Donh91/Investering-Framework-Archive-v1"}
        def r(h, ev="schedule", ok="success", br="main", repo=own, path=".github/workflows/automation-production-health.yml"):
            return {"path": path, "event": ev, "head_branch": br, "head_repository": repo, "status": "completed", "conclusion": ok, "completed_h": h}
        self.assertEqual(main_health([r(90)], 100), "PASS")
        self.assertEqual(main_health([r(70)], 100), "NOT_PROVEN(main_health_stale)")
        self.assertEqual(main_health([], 100), "NOT_PROVEN(main_health_stale)")
        self.assertEqual(main_health([r(90)], 100, readable=False), "NOT_PROVEN(TOOL_CANNOT_READ)")
        self.assertEqual(main_health([r(90, ok="failure")], 100), "FAIL")
        for noise in (r(99, ev="pull_request"), r(99, ev="workflow_dispatch"), r(99, ev="workflow_run"),
                      r(99, repo={"full_name": "fork/Investering-Framework-Archive-v1"}), r(99, repo=None), r(99, path=".github/workflows/other.yml"),
                      r(99, br="feature")):
            self.assertEqual(main_health([r(70), noise], 100), "NOT_PROVEN(main_health_stale)", noise)
            self.assertEqual(main_health([r(90, ok="failure"), dict(noise, conclusion="success")], 100), "FAIL", noise)
        loop = (S1 / "ACTION_LOOP.md").read_text(encoding="utf-8")
        for token in ("API/actions/workflows/automation-production-health.yml/runs?event=schedule&branch=main&per_page=100", "head_repository.full_name is Donh91/Investering-Framework-Archive-v1",
                      "NOT PROVEN(TOOL_CANNOT_READ), never a pass and never a waiver", "its updated_at must be within 26 h",
                      "keep only runs whose path is .github/workflows/automation-production-health.yml",
                      "(pull_request, workflow_dispatch, workflow_run and fork runs never count)"):
            self.assertIn(token, loop)

    def test_d2_time_and_budget_never_close(self):
        """D2: forged counters, time/budget signals, HIGH risk or a missing Strategist answer never close an item."""
        forged = [{"id": 1, "park_count": 1}, {"id": 2, "park_count": 3}]
        self.assertEqual(counters(forged, receipts={1}), 1, "a forged park_count without a receipt is ignored")
        laundered = Item("pr:34", park_count=counters(forged, receipts={1, 2}), signals={"duplicate"})   # forged heartbeat too
        enter(laundered, "PARKED", 0, "x")
        while laundered.state == "PARKED":
            forced_disposition(laundered, laundered.due + 1, {})
        self.assertEqual(laundered.state, "PARKED_OWNER_DECISION", "RESIDUAL: a forged heartbeat at most escalates to the owner")
        it = Item("pr:30", park_count=counters(forged, {1}))
        enter(it, "PARKED", 0, "x")
        while it.state == "PARKED":
            forced_disposition(it, it.due + 1, {})
        self.assertNotEqual(it.state, "CLOSED_NOISE")
        self.assertFalse(close_allowed({"stale_final_park", "park_limit", "cycle_cap", "stale_parked", "no_owner_link"}))
        high = Item("pr:31", risk="HIGH", signals={"duplicate", "strategist_concur", "superseded_native"})
        self.assertFalse(close_allowed(high), "HIGH is never auto-closed")
        self.assertFalse(close_allowed(Item("pr:32", owner_only=True, signals={"duplicate", "strategist_concur"})))
        silent = Item("pr:33", signals={"duplicate"})
        park(silent, 0, "x"); park(silent, 1, "x")
        while silent.state == "PARKED":
            forced_disposition(silent, silent.due + 1, {})
        self.assertEqual(silent.state, "PARKED_OWNER_DECISION", "no Strategist answer: escalate, never close")
        for token in ("TIME AND BUDGET NEVER CLOSE", "receipts=<key>:<comment id>", "HIGH, HIGH_IMPACT, EXTREME, unclear and OWNER_ONLY items are never closed by S1",
                      "at least one is INDEPENDENT of S1", "at least one is OBJECTIVE", "Rows F2 to F7 never close an item",
                      "RESIDUAL: a forged counter or heartbeat can at most move an item to PARKED_OWNER_DECISION", "subject similarity alone is never duplicate"):
            self.assertIn(token, STATES_MD)

    def test_d3_specialist_is_preflight_only(self):
        """D3: author spoofing, mixed authorship, old head, native CHANGES_REQUESTED; MEDIUM+ needs Codex or detached Claude."""
        plain, codexh = Head("a" * 40), Head("c" * 40, branch="codex/fix")
        mixed = Head("f" * 40, branch="feature/y", commit_logins=("Donh91", "chatgpt-codex-connector[bot]"))
        spoof = Head("9" * 40, branch="feature/z", commit_messages=("fix", "x\n\n" + S1_TRAILER))
        for risk in ("MEDIUM", "HIGH", "HIGH_IMPACT"):
            self.assertIsNone(admissible_review(plain, risk, {"specialist": "APPROVE"}, True), risk)
            self.assertIsNone(admissible_review(codexh, risk, {"specialist": "APPROVE"}, True), risk)
            self.assertEqual(admissible_review(codexh, risk, {"claude": "APPROVE"}, True), "claude")
        self.assertIsNone(admissible_review(mixed, "MEDIUM", {"codex": "APPROVE"}, False), "mixed authorship: Codex co-authored the head")
        self.assertIsNone(admissible_review(spoof, "LOW", {"specialist": "APPROVE"}, True), "an S1 trailer makes the head S1-authored")
        self.assertIsNone(admissible_review(plain, "LOW", {"specialist": "APPROVE"}, True, docs_only=False), "tests-only LOW is not the LOW LANE")
        self.assertIsNone(admissible_review(plain, "LOW", {"specialist": "APPROVE"}, True, ci_green=False))
        self.assertIsNone(admissible_review(plain, "LOW", {"specialist": "APPROVE", "native": "CHANGES_REQUESTED"}, True))
        self.assertIsNone(admissible_review(Head("b" * 40), "LOW", {}, True), "a receipt for an old head is not a review of this head")
        for token in ("It is a PREFLIGHT by the merging agent, never an independent review", "For MEDIUM, HIGH and HIGH_IMPACT it is preflight only",
                      "AUDIT SAMPLE (part of rule 4, inside the same action)", "carries audit=<comment id>", "a specialist receipt is never the review for them."):
            self.assertIn(token, ADMISSION_MD)
        self.assertIn("also carries out the AUDIT SAMPLE of REVIEW_ADMISSION.md in this same action", (S1 / "ACTION_LOOP.md").read_text(encoding="utf-8"))
        self.assertFalse(close_allowed({"superseded", "superseded_native"}), "one supersession fact counts once")
        self.assertFalse(close_allowed({"duplicate", "owner_close"}), "a close comment is never an independent signal")

    def test_loop_guard_forces_disposition(self):
        """Scenario 6: the same NOOP reason three runs in a row forces a disposition, never a fourth NOOP."""
        it = Item("pr:9")
        enter(it, "TEST", 0, "red")
        results = []
        for _ in range(B["same_noop_runs"] + 1):
            outcome = Run(1, 12 * 60, 2).execute([it], {})[1]
            results.append(outcome)
            if outcome.startswith("NOOP"):
                it.noop_streak += 1
        self.assertEqual(results[:3], ["NOOP NOTHING_ACTIONABLE"] * 3)
        self.assertEqual(results[3], "STEWARD DISPOSED")
        self.assertEqual(it.state, "PARKED")

    def test_monday_read_only(self):
        """Scenario 7: Monday 09:30-10:30 Copenhagen writes nothing, but the status lines are still printed."""
        it = Item("pr:10")
        enter(it, "REVIEW", 0, "x")
        run = Run(30, 9 * 60 + 45, 0)
        lines, outcome = run.execute([it], {"lane_off": "main_health"})
        self.assertEqual(outcome, "NOOP MONDAY_READ_ONLY")
        self.assertEqual(run.writes, [])
        self.assertTrue(lines[0].startswith("OWNER APPROVAL REQUIRED: LANE_OFF(main_health)"))
        self.assertTrue(lines[1].startswith("HIGH_IMPACT BLOCKED:"))
        self.assertTrue(lines[2].startswith("DISPOSITIONS TODAY:"))
        self.assertEqual(Run(30, 10 * 60 + 30, 0).execute([it], {})[1], "STEWARD DISPOSED")
        self.assertFalse(may_merge(Item("pr:11"), Head("1" * 40), {"codex": "APPROVE"}, False, {"lane": "ON", "monday_read_only": True}))

    def test_direction_needs_strategist(self):
        """A direction change merges only with a Strategist CONCUR; a silent Strategist parks it (F4)."""
        it = Item("pr:12", kind="DIRECTION", risk="MEDIUM")
        head = Head("2" * 40)
        self.assertFalse(may_merge(it, head, {"codex": "APPROVE"}, False, {"lane": "ON"}))
        self.assertTrue(may_merge(it, head, {"codex": "APPROVE"}, False, {"lane": "ON", "strategist": {"pr:12": "CONCUR"}}))
        enter(it, "STRATEGIST", 0, "consult")
        self.assertEqual(forced_disposition(it, B["dwell_days"]["STRATEGIST"] + 1, {}), "F4")
        self.assertEqual(it.state, "PARKED")
        research = Item("pr:13", kind="RESEARCH")
        enter(research, "STRATEGIST", 0, "consult")
        forced_disposition(research, 99, {"active_handoffs": 2})
        self.assertEqual(research.state, "RESEARCH_HANDOFF")
        full = Item("pr:14", kind="RESEARCH")
        enter(full, "STRATEGIST", 0, "consult")
        forced_disposition(full, 99, {"active_handoffs": 3})
        self.assertEqual(full.state, "PARKED", "max 3 ACTIVE handoffs")

    def test_claude_off_for_seven_days(self):
        """Acceptance 5: Claude silent for 7 days. S1 still merges with Codex and no item outlives its budget."""
        items = [Item(f"pr:{n}", state="REVIEW", due=B["dwell_days"]["REVIEW"]) for n in range(20)]
        heads = {it.key: Head(f"{n:040x}") for n, it in enumerate(items)}
        merged = 0
        for hour in range(7 * 24):
            day = hour // 24
            run = Run(day, (hour % 24) * 60, day % 7)
            if run.monday_read_only():
                continue
            for it in items:   # Codex answers half the PRs; Claude never answers
                n = int(it.key.split(":")[1])
                if it.state == "REVIEW" and n % 2 == 0 and may_merge(it, heads[it.key], {"codex": "APPROVE"}, False, {"lane": "ON"}):
                    enter(it, "MERGED", day, "codex")
                    merged += 1
                    break
            run.execute(items, {})
        self.assertGreaterEqual(merged, 1)
        for it in items:
            self.assertTrue(it.state in TERMINAL or not overdue(it, 6), (it.key, it.state, it.due))

    def test_every_item_terminates_under_silence(self):
        """Property: whatever routes stay silent, every item reaches MERGED, CLOSED_NOISE or OWNER_APPROVAL in bounded time."""
        rng = random.Random(20261116)
        states = ["DISCOVERED", "TRIAGED", "PLAN", "STRATEGIST", "BUILD", "TEST", "REVIEW", "RESEARCH_HANDOFF"]
        bound = (sum(B["dwell_days"].values()) + B["park_revisit_max_days"] + 1) * (B["max_parks"] + 1) * 2
        for trial in range(300):
            it = Item(f"x:{trial}", kind=rng.choice(["FIX", "TEST", "DOCS", "RESEARCH", "DIRECTION"]))
            enter(it, rng.choice(states), 0, "start")
            day = 0
            while it.state not in TERMINAL | {"OWNER_APPROVAL"}:
                day += 1
                self.assertLess(day, bound, f"item never resolves: {it.log}")
                if rng.random() < 0.05 and it.state != "PARKED":
                    it.new_info = True
                if overdue(it, day):
                    forced_disposition(it, day, {"active_handoffs": rng.randint(0, 3)})
                if it.state == "TRIAGED":
                    enter(it, "BUILD", day, "start_build")
            self.assertLessEqual(it.park_count, B["max_parks"])


if __name__ == "__main__":
    unittest.main()
