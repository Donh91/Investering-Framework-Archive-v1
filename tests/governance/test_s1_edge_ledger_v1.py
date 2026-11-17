"""S1 edge ledger: a reference model of 00_FMOS/S1/EDGE_LEDGER.md and its behaviour tests.

The model reads its gates from the machine-readable S1_EDGE_LEDGER_GATES_v1 block, so an edit there changes these
results. It pins what "improvement compounds until an edge appears or is falsified" means mechanically:
a preregistration on main before its window, an identical-clock baseline, a weekly anytime-valid e-process, and a
total, ordered decision table (promote, park, kill, close, accumulate) in which every stream ends.
No market data, no outcome data, no Round 3 data: every number here is a synthetic fixture.
"""
import itertools
import json
import random
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S1 = ROOT / "00_FMOS" / "S1"
EDGE_MD = (S1 / "EDGE_LEDGER.md").read_text(encoding="utf-8")
LOOP_MD = (S1 / "ACTION_LOOP.md").read_text(encoding="utf-8")
STATES_MD = (S1 / "STEWARD_STATES.md").read_text(encoding="utf-8")
ADMISSION_MD = (S1 / "REVIEW_ADMISSION.md").read_text(encoding="utf-8")
G = json.loads(re.search(r"```json\n(\{.*?\})\n```", EDGE_MD, re.S).group(1))
WEEK = 7 * 24                       # hours; week k starts at hour k * WEEK (a Monday 00:00 UTC)


# ---------------------------------------------------------------- E1 preregistration
def prereg(**kw):
    doc = {"stream_id": "s1", "hypothesis": "model beats best baseline on interval score", "forecaster_ref": "scripts/x.py@b1",
           "scorer_ref": "scripts/score.py@b2", "baselines": ["B0@b0", "B4@b4"], "data_paths": ["05_CYCLE_NAVIGATOR/public_series/"],
           "outcome": "btc_7d", "loss": "interval_score", "unit": "iso_week", "clip_c": 1.0,
           "MDE": 0.05, "n_min": 8, "n_max": 26, "family_id": "cn", "family_k_max": 1,
           "bootstrap": {"block_weeks": 1, "replicates": 2000, "seed": 7}, "kill_rules": ["futility", "harm"],
           "readiness_checks": ["freeze", "pit"], "first_week": 10}
    doc.update(kw)
    return doc


def prereg_status(doc, merged_at_h, blob_changed_later=False, killed=(), promoted_on_outcome=(), family_members=None):
    """E1: 'VALID' or the INVALID_PREREG reason. family_members: family_k_max of every stream on main with this family_id,
    the newcomer included, oldest first."""
    if any(k not in doc for k in G["prereg_required_fields"]):
        return "missing_field"
    if not doc["data_paths"] or any("round3" in p.lower().replace("_", "").replace("-", "")
                                    or p.startswith(("private/", "vault/", "secrets/")) for p in doc["data_paths"]):
        return "firewall"
    if not doc["clip_c"] > 0 or doc["MDE"] < G["mde_min_share_of_clip"] * doc["clip_c"]:
        return "floor"
    members = [doc["family_k_max"]] if family_members is None else list(family_members)
    if doc["family_k_max"] < 1 or len(members) > members[0] or any(k != members[0] for k in members):
        return "family_cap"
    if merged_at_h is None or merged_at_h >= doc["first_week"] * WEEK:
        return "not_before_window"
    if blob_changed_later:
        return "prereg_edited"
    if (doc["hypothesis"], doc["forecaster_ref"]) in killed:
        return "rerun_of_killed"
    if any(p not in doc["baselines"] for p in promoted_on_outcome):
        return "baseline_ratchet"
    return "VALID"


def gate(doc, name):
    """A preregistration may tighten a gate and never loosen one."""
    if name == "n_min":
        return max(G["n_min"], doc.get("n_min", 0))
    if name == "n_max":
        return min(G["n_max"], doc.get("n_max", G["n_max"]))
    if name == "harm_e":
        return min(G["harm_e"], doc.get("harm_e", G["harm_e"]))
    raise KeyError(name)


TIGHTEN_UP, TIGHTEN_DOWN = ("MDE", "n_min"), ("n_max", "harm_e")
FROZEN_IN_AMENDMENT = ("hypothesis", "outcome", "loss", "unit", "clip_c", "forecaster_ref", "scorer_ref", "family_id",
                       "family_k_max", "bootstrap", "data_paths")


def amendment_ok(old, new):
    """E1 AN AMENDMENT ONLY TIGHTENS."""
    if any(old.get(k) != new.get(k) for k in FROZEN_IN_AMENDMENT):
        return False
    if any(new[k] < old[k] for k in TIGHTEN_UP) or any(new.get(k, G.get(k)) > old.get(k, G.get(k)) for k in TIGHTEN_DOWN):
        return False
    return set(old["baselines"]) <= set(new["baselines"]) and set(old["readiness_checks"]) <= set(new["readiness_checks"])


def candidacy_from_posts(posts, mde):
    """E3: weeks_since_candidate and candidate_held from S1's OWN decision posts, oldest first. Each post holds
    decision, n, mean_d and readiness_fail_share. Only a post for a NEW VALID WEEK (n exactly one higher than in the
    previous post) counts as a confirmation week; a calendar week with no new valid row adds nothing."""
    since, held, in_candidacy, prev = 0, True, False, None
    for post in posts:
        new_valid_week = prev is not None and post["n"] == prev["n"] + 1
        if in_candidacy and new_valid_week:
            since += 1
            held = held and post["mean_d"] >= mde and post["readiness_fail_share"] <= prev["readiness_fail_share"]
        if post["decision"] == "PROMOTE_CANDIDATE" and not in_candidacy:
            in_candidacy, since, held = True, 0, True
        elif post["decision"] not in ("PROMOTE_CANDIDATE", "PROMOTED"):
            in_candidacy, since, held = False, 0, True
        prev = post
    return since, held


def week_counts(week, doc, amendment_merged_at_h=None, selection_exposed=()):
    """A week counts only from first_week on, never when selection-exposed, and an amendment applies only to weeks
    that start after its own merge."""
    if week < doc["first_week"] or week in selection_exposed:
        return False
    if amendment_merged_at_h is not None and week * WEEK <= amendment_merged_at_h:
        return False
    return True


# ---------------------------------------------------------------- E2 identical clock
def row_admissible(row):
    clocks = {row["model"]["issue_clock"]} | {b["issue_clock"] for b in row["baselines"]}
    snaps = {row["model"]["snapshot"]} | {b["snapshot"] for b in row["baselines"]}
    runs = {row["model"]["run_id"]} | {b["run_id"] for b in row["baselines"]}
    return len(clocks) == 1 and len(snaps) == 1 and len(runs) == 1 and bool(row["baselines"])


def best_baseline_loss(row):
    return min(b["loss"] for b in row["baselines"])            # the bar is the BEST baseline, not a chosen one


# ---------------------------------------------------------------- E3 e-process
def clip(d, c):
    return max(-c, min(c, d))


def predictable_lambda(past, c):
    """lambda_w from EARLIER weeks only: a clipped running mean (an aGRAPA-style plug-in), in [0, lambda_max]."""
    if not past:
        return 0.0
    mean = sum(past) / len(past)
    var = sum((x - mean) ** 2 for x in past) / len(past) + (c * c) / 4
    return max(0.0, min(G["lambda_max"], mean * c / var))


def e_process(ds, c, reverse=False):
    """E_t = prod (1 + lambda_w * d_w / c); returns the path. With lambda in [0, 0.5] and |d| <= c every factor is
    at least 0.5, so the product never reaches zero."""
    e, path, past = 1.0, [], []
    for d in ds:
        d = clip(-d if reverse else d, c)
        lam = predictable_lambda(past, c)
        e *= 1 + lam * d / c
        path.append(e)
        past.append(d)
    return path


def summary(ds, c, readiness_fail_weeks=0, ci_upper=None):
    n = len(ds)
    mean = sum(clip(d, c) for d in ds) / n if n else 0.0
    total = n + readiness_fail_weeks
    return {"n": n, "e_value": (e_process(ds, c) or [1.0])[-1], "e_reverse": (e_process(ds, c, reverse=True) or [1.0])[-1],
            "mean_d": mean, "ci_upper": mean + 0.02 if ci_upper is None else ci_upper,
            "readiness_fail_share": readiness_fail_weeks / total if total else 0.0}


# ---------------------------------------------------------------- E4 decision table
def decide(doc, row, *, prereg_ok=True, pit_ok=True, ledger_rewritten=False, previous="ACCUMULATE", reviewed=True,
           weeks_since_candidate=0, candidate_held=True, idle_weeks=0):
    """First matching row wins. idle_weeks: consecutive weeks parked or without a new ledger row.
    weeks_since_candidate and candidate_held come from S1's own decision posts, never from the scorer."""
    mde, k = doc["MDE"], max(1, doc["family_k_max"])
    if not prereg_ok:
        return "INVALID_PREREG"
    if idle_weeks > G["max_parked_weeks"]:
        return "CLOSED_INCONCLUSIVE"                  # no stream waits forever
    if row["readiness_fail_share"] > G["park_readiness_fail_share"] or not pit_ok or ledger_rewritten:
        return "PARKED"
    if row["e_reverse"] >= gate(doc, "harm_e"):
        return "KILLED_HARM"
    if row["n"] >= gate(doc, "n_min") and row["ci_upper"] < mde:
        return "KILLED_FUTILITY"
    if previous == "PROMOTE_CANDIDATE" and weeks_since_candidate >= G["confirm_weeks"] and candidate_held and reviewed:
        return "PROMOTED"
    if (row["e_value"] >= k / G["alpha_family"] and row["mean_d"] >= mde and reviewed
            and gate(doc, "n_min") <= row["n"] < gate(doc, "n_max") + G["confirm_weeks"]):
        return "PROMOTE_CANDIDATE"
    if row["n"] >= gate(doc, "n_max"):
        return "CLOSED_INCONCLUSIVE"
    return "ACCUMULATE"


def run_stream(doc, ds, reviewed=True):
    """Feed weekly differences until a final decision; return the decision history."""
    history, previous, since, held = [], "ACCUMULATE", 0, True
    for n in range(1, len(ds) + 1):
        row = summary(ds[:n], doc["clip_c"])
        if previous == "PROMOTE_CANDIDATE":
            since += 1
            held = held and row["mean_d"] >= doc["MDE"]
        decision = decide(doc, row, previous=previous, reviewed=reviewed, weeks_since_candidate=since, candidate_held=held)
        if decision == "PROMOTE_CANDIDATE" and (previous != "PROMOTE_CANDIDATE" or not held):
            since, held = 0, True                 # a new candidacy starts its confirmation weeks again
        history.append(decision)
        if decision in G["final_decisions"]:
            break
        previous = decision
    return history


# ================================================================ tests
class GatesTest(unittest.TestCase):
    def test_block_is_complete(self):
        self.assertEqual(G["contract"], "S1_EDGE_LEDGER_GATES_v1")
        self.assertEqual(G["ledger_dir"], "06_RESEARCH_LAB/edge_ledger_v1")
        self.assertEqual((G["n_min"], G["n_max"], G["alpha_family"], G["harm_e"], G["confirm_weeks"]), (8, 26, 0.05, 20, 4))
        self.assertLessEqual(G["lambda_max"], 0.5)
        self.assertEqual(G["decisions"], ["INVALID_PREREG", "PARKED", "KILLED_HARM", "KILLED_FUTILITY", "PROMOTED",
                                          "PROMOTE_CANDIDATE", "CLOSED_INCONCLUSIVE", "ACCUMULATE"])
        self.assertLessEqual(set(G["final_decisions"]), set(G["decisions"]))
        self.assertEqual((G["max_parked_weeks"], G["park_readiness_fail_share"], G["futility_ci"], G["streams_per_run"]), (8, 0.25, 0.9, 3))
        self.assertEqual(G["summary_file"], "LEDGER_SUMMARY.json")
        self.assertEqual(G["final_decisions"], ["INVALID_PREREG", "KILLED_HARM", "KILLED_FUTILITY", "PROMOTED", "CLOSED_INCONCLUSIVE"])
        for field in ("hypothesis", "forecaster_ref", "scorer_ref", "baselines", "data_paths", "MDE", "clip_c", "n_min", "n_max",
                      "family_id", "family_k_max", "bootstrap", "kill_rules", "first_week"):
            self.assertIn(field, G["prereg_required_fields"])

    def test_a_prereg_only_tightens(self):
        self.assertEqual(gate(prereg(n_min=4), "n_min"), 8)
        self.assertEqual(gate(prereg(n_min=12), "n_min"), 12)
        self.assertEqual(gate(prereg(n_max=40), "n_max"), 26)
        self.assertEqual(gate(prereg(n_max=16), "n_max"), 16)
        self.assertEqual(gate(prereg(harm_e=50), "harm_e"), 20)
        self.assertEqual(gate(prereg(harm_e=10), "harm_e"), 10)
        self.assertIn("may tighten a gate", EDGE_MD)
        self.assertIn("and never loosen one: S1 uses the stricter of the two values", EDGE_MD)


class PreregistrationTest(unittest.TestCase):
    def test_on_main_before_the_window(self):
        doc = prereg(first_week=10)
        self.assertEqual(prereg_status(doc, merged_at_h=10 * WEEK - 1), "VALID")
        self.assertEqual(prereg_status(doc, merged_at_h=10 * WEEK), "not_before_window")       # Monday 00:00 itself is late
        self.assertEqual(prereg_status(doc, merged_at_h=10 * WEEK + 5), "not_before_window")
        self.assertEqual(prereg_status(doc, merged_at_h=None), "not_before_window")            # never merged, or unreadable

    def test_frozen_complete_and_firewalled(self):
        self.assertEqual(prereg_status(prereg(), 1, blob_changed_later=True), "prereg_edited")
        incomplete = prereg()
        del incomplete["MDE"]
        self.assertEqual(prereg_status(incomplete, 1), "missing_field")
        self.assertEqual(prereg_status(prereg(data_paths=["06_RESEARCH_LAB/round3_new_information_v1/x.json"]), 1), "firewall")
        self.assertEqual(prereg_status(prereg(data_paths=["private/x.json"]), 1), "firewall")
        self.assertEqual(prereg_status(prereg(data_paths=[]), 1), "firewall")              # no declared data: nothing to check
        no_paths = prereg()
        del no_paths["data_paths"]
        self.assertEqual(prereg_status(no_paths, 1), "missing_field")

    def test_floors_a_stream_cannot_define_success_away(self):
        for bad in ({"MDE": 0}, {"MDE": -1.0}, {"clip_c": 0}, {"clip_c": -2}, {"MDE": 1e-12}, {"MDE": 0.0099}):
            self.assertEqual(prereg_status(prereg(**bad), 1), "floor", bad)
        self.assertEqual(prereg_status(prereg(MDE=0.01), 1), "VALID")       # the floor binds: 1 % of clip_c
        self.assertEqual(G["mde_min_share_of_clip"], 0.01)

    def test_family_cap_is_fixed_by_the_first_member(self):
        self.assertEqual(prereg_status(prereg(family_k_max=3), 1, family_members=[3, 3, 3]), "VALID")
        self.assertEqual(prereg_status(prereg(family_k_max=3), 1, family_members=[3, 3, 3, 3]), "family_cap")   # a fourth member
        self.assertEqual(prereg_status(prereg(family_k_max=1), 1, family_members=[3, 1]), "family_cap")         # another value
        self.assertEqual(prereg_status(prereg(family_k_max=0), 1), "family_cap")

    def test_an_amendment_only_tightens(self):
        v1 = prereg()
        self.assertTrue(amendment_ok(v1, prereg(MDE=0.08, n_min=10, n_max=20, baselines=["B0@b0", "B4@b4", "A@b9"])))
        for change in ({"MDE": 0.01}, {"n_min": 4}, {"n_max": 40}, {"baselines": ["B0@b0"]}, {"hypothesis": "another"},
                       {"loss": "brier"}, {"clip_c": 5.0}, {"forecaster_ref": "scripts/y.py@b3"}, {"family_k_max": 9},
                       {"bootstrap": {"block_weeks": 1, "replicates": 10, "seed": 1}}, {"data_paths": ["x/"]},
                       {"readiness_checks": ["freeze"]}, {"harm_e": 50}):
            with self.subTest(change=change):
                self.assertFalse(amendment_ok(v1, prereg(**change)))

    def test_no_rerun_and_ratchet(self):
        doc = prereg()
        self.assertEqual(prereg_status(doc, 1, killed={(doc["hypothesis"], doc["forecaster_ref"])}), "rerun_of_killed")
        self.assertEqual(prereg_status(doc, 1, promoted_on_outcome=["A@b9"]), "baseline_ratchet")
        self.assertEqual(prereg_status(prereg(baselines=["B0@b0", "A@b9"]), 1, promoted_on_outcome=["A@b9"]), "VALID")

    def test_which_weeks_count(self):
        doc = prereg(first_week=10)
        self.assertFalse(week_counts(9, doc))
        self.assertTrue(week_counts(10, doc))
        self.assertFalse(week_counts(11, doc, selection_exposed={11}))
        # an amendment merged during week 12 applies from week 13
        self.assertFalse(week_counts(12, doc, amendment_merged_at_h=12 * WEEK + 3))
        self.assertTrue(week_counts(13, doc, amendment_merged_at_h=12 * WEEK + 3))

    def test_rule_text(self):
        for token in ("was merged to main before first_week's Monday 00:00 UTC",
                      "a commit's own author or committer date is never the clock",
                      "a later commit on main that changes an existing PREREG_v<k>.json blob makes the stream INVALID_PREREG",
                      "it applies only to weeks that start after its own merged_at",
                      "selection-exposed weeks", "reason rerun_of_killed", "reason baseline_ratchet",
                      "No stream reads Round 3 data", "or that lists none, is INVALID_PREREG",
                      "FLOORS: clip_c is above 0 and MDE is at least mde_min_share_of_clip times clip_c; otherwise INVALID_PREREG",
                      "a final decision of KILLED_HARM, KILLED_FUTILITY or CLOSED_INCONCLUSIVE is INVALID_PREREG (reason rerun_of_killed)",
                      "An INVALID_PREREG stream that has no scored week in LEDGER.jsonl never held evidence",
                      "one that was scored before it became invalid (a preregistration edited later, a firewall breach) is banned like a killed one",
                      "and nothing else. A changed hypothesis",
                      "For the evidence process E_t the bar is the BEST baseline of the week",
                      "FAMILY CAP: the first preregistration of a family fixes family_k_max",
                      "is INVALID_PREREG (reason family_cap) for the newcomer",
                      "AN AMENDMENT ONLY TIGHTENS", "is a new stream with a new stream_id and an e-process that starts at 1",
                      "bootstrap fixes the block length, the number of replicates and the seed behind ci_upper",
                      "the baseline with the best cumulative loss up to the PREVIOUS week"):
            self.assertIn(token, EDGE_MD)


class IdenticalClockTest(unittest.TestCase):
    @staticmethod
    def row(**kw):
        cell = {"issue_clock": 100, "snapshot": "s", "run_id": 7, "loss": 1.0}
        row = {"model": dict(cell, loss=0.8), "baselines": [dict(cell, loss=1.0), dict(cell, loss=0.9)]}
        row.update(kw)
        return row

    def test_same_run_same_snapshot_same_clock(self):
        self.assertTrue(row_admissible(self.row()))
        cell = {"issue_clock": 100, "snapshot": "s", "run_id": 7, "loss": 1.0}
        for change in ({"issue_clock": 101}, {"snapshot": "later"}, {"run_id": 8}):
            late = self.row(baselines=[dict(cell), dict(cell, **change)])
            with self.subTest(change=change):
                self.assertFalse(row_admissible(late))
        self.assertFalse(row_admissible(self.row(baselines=[])))

    def test_the_bar_is_the_best_baseline(self):
        self.assertEqual(best_baseline_loss(self.row()), 0.9)
        self.assertIn("the bar is the BEST baseline of the week on the stream's loss, not a chosen one", EDGE_MD)
        self.assertIn("A baseline computed later, in another run or from another snapshot is not admissible", EDGE_MD)
        self.assertIn("S1 never repairs a row", EDGE_MD)


class EProcessTest(unittest.TestCase):
    def test_lambda_is_predictable_and_bounded(self):
        rng = random.Random(7)
        ds = [rng.uniform(-1, 1) for _ in range(40)]
        for k in range(len(ds)):
            lam = predictable_lambda(ds[:k], 1.0)
            self.assertGreaterEqual(lam, 0.0)
            self.assertLessEqual(lam, G["lambda_max"])
        # predictable: changing week k's outcome never changes the bet placed in week k
        a = e_process([0.2, 0.3, 0.1, 0.9], 1.0)
        b = e_process([0.2, 0.3, 0.1, -0.9], 1.0)
        self.assertEqual(a[:3], b[:3])
        # the bet of week 4 is the same whatever week 4 brings: recover lambda_4 from the two paths
        lam_up = (a[3] / a[2] - 1) / 0.9
        lam_down = (b[3] / b[2] - 1) / -0.9
        self.assertAlmostEqual(lam_up, lam_down, places=12)
        self.assertAlmostEqual(lam_up, predictable_lambda([0.2, 0.3, 0.1], 1.0), places=12)

    def test_evidence_compounds_under_a_real_effect(self):
        path = e_process([0.4] * 20, 1.0)
        self.assertTrue(all(b >= a for a, b in zip(path, path[1:])))
        self.assertGreater(path[-1], 20)
        self.assertLess(e_process([0.4] * 20, 1.0, reverse=True)[-1], 1.0 + 1e-9)

    def test_no_effect_rarely_crosses_the_threshold(self):
        # Ville: under H0 (mean d <= 0) the chance that E_t ever reaches 1/alpha is at most alpha.
        rng = random.Random(20261117)
        crossings = 0
        trials = 2000
        for _ in range(trials):
            ds = [rng.choice((-1.0, 1.0)) * rng.random() for _ in range(G["n_max"])]
            if max(e_process(ds, 1.0)) >= 1 / G["alpha_family"]:
                crossings += 1
        self.assertLessEqual(crossings / trials, G["alpha_family"])

    def test_clipping_bounds_one_week(self):
        self.assertEqual(clip(9.0, 1.0), 1.0)
        self.assertEqual(clip(-9.0, 1.0), -1.0)
        self.assertGreater(min(e_process([-5.0] * 30, 1.0)), 0.0)
        self.assertLessEqual(e_process([0.5] * 5 + [50.0], 1.0)[-1], e_process([0.5] * 5, 1.0)[-1] * (1 + G["lambda_max"]))

    def test_rule_text(self):
        for token in ("clipped to [-clip_c, clip_c]", "chosen from EARLIER weeks only",
                      "A lambda that depends on its own week's outcome makes the row inadmissible",
                      "LEDGER.jsonl is append-only", "reason ledger_rewritten",
                      "Never report a p-value from overlapping windows", "never restate E_t as a probability"):
            self.assertIn(token, EDGE_MD)


class DecisionTableTest(unittest.TestCase):
    ROW = {"n": 10, "e_value": 30.0, "e_reverse": 0.2, "mean_d": 0.08, "ci_upper": 0.12, "readiness_fail_share": 0.0}

    def test_promote_candidate_needs_every_gate(self):
        doc = prereg()
        self.assertEqual(decide(doc, self.ROW), "PROMOTE_CANDIDATE")
        self.assertEqual(decide(doc, dict(self.ROW, e_value=19.9)), "ACCUMULATE")
        self.assertEqual(decide(doc, dict(self.ROW, mean_d=0.04)), "ACCUMULATE")
        self.assertEqual(decide(doc, dict(self.ROW, n=7)), "ACCUMULATE")
        self.assertEqual(decide(doc, self.ROW, reviewed=False), "ACCUMULATE")

    def test_family_control(self):
        self.assertEqual(decide(prereg(family_k_max=5), dict(self.ROW, e_value=99.0)), "ACCUMULATE")     # K=5 needs E >= 100
        self.assertEqual(decide(prereg(family_k_max=5), dict(self.ROW, e_value=100.0)), "PROMOTE_CANDIDATE")
        self.assertEqual(decide(prereg(family_k_max=0), dict(self.ROW, e_value=20.0)), "PROMOTE_CANDIDATE")   # never below 1
        # the union bound over a whole family that uses one fixed cap: K * (alpha / K) = alpha, however members come and go
        k = 4
        self.assertAlmostEqual(sum(G["alpha_family"] / k for _ in range(k)), G["alpha_family"])

    def test_confirmation_weeks_are_valid_weeks_counted_from_s1_own_posts(self):
        def post(n, decision="PROMOTE_CANDIDATE", mean_d=0.08, share=0.0):
            return {"decision": decision, "n": n, "mean_d": mean_d, "readiness_fail_share": share}

        doc = prereg()
        steady = [post(9, "ACCUMULATE"), post(10), post(11), post(12), post(13), post(14)]
        self.assertEqual(candidacy_from_posts(steady, doc["MDE"]), (4, True))
        self.assertEqual(candidacy_from_posts(steady[:5], doc["MDE"]), (3, True))
        # R2 N-5: three calendar weeks with no ledger PR, then one new row: ONE confirmation week, not four
        gap = [post(10), post(10), post(10), post(10), post(11)]
        since, held = candidacy_from_posts(gap, doc["MDE"])
        self.assertEqual((since, held), (1, True))
        self.assertEqual(decide(doc, self.ROW, previous="PROMOTE_CANDIDATE", weeks_since_candidate=since, candidate_held=held),
                         "PROMOTE_CANDIDATE")
        # a dip or a readiness failure breaks the hold; falling back restarts the count
        self.assertEqual(candidacy_from_posts([post(10), post(11, mean_d=0.01), post(12), post(13), post(14)], doc["MDE"]), (4, False))
        self.assertEqual(candidacy_from_posts([post(10), post(11, share=0.1), post(12, share=0.1)], doc["MDE"]), (2, False))
        self.assertEqual(candidacy_from_posts([post(10), post(11), post(12, "ACCUMULATE"), post(13), post(14)], doc["MDE"]), (1, True))
        for token in ("weeks_since_candidate is the number of posts for a NEW VALID WEEK (n exactly one higher than in the previous post)",
                      "a calendar week with no new valid row adds nothing"):
            self.assertIn(token, EDGE_MD)

    def test_promotion_needs_confirmation_weeks(self):
        doc = prereg()
        kw = {"previous": "PROMOTE_CANDIDATE", "candidate_held": True}
        self.assertEqual(decide(doc, self.ROW, weeks_since_candidate=3, **kw), "PROMOTE_CANDIDATE")
        self.assertEqual(decide(doc, self.ROW, weeks_since_candidate=4, **kw), "PROMOTED")
        self.assertEqual(decide(doc, self.ROW, weeks_since_candidate=4, previous="PROMOTE_CANDIDATE", candidate_held=False),
                         "PROMOTE_CANDIDATE")
        self.assertEqual(decide(doc, self.ROW, weeks_since_candidate=4, reviewed=False, **kw), "ACCUMULATE")
        self.assertEqual(decide(doc, self.ROW, weeks_since_candidate=9), "PROMOTE_CANDIDATE")     # never straight from ACCUMULATE

    def test_kill_park_and_close_rows(self):
        doc = prereg()
        self.assertEqual(decide(doc, dict(self.ROW, e_reverse=20.0)), "KILLED_HARM")
        self.assertEqual(decide(doc, dict(self.ROW, ci_upper=0.049)), "KILLED_FUTILITY")
        self.assertEqual(decide(doc, dict(self.ROW, n=7, ci_upper=0.01, e_value=1.0)), "ACCUMULATE")    # futility needs n_min
        self.assertEqual(decide(doc, dict(self.ROW, readiness_fail_share=0.26)), "PARKED")
        self.assertEqual(decide(doc, dict(self.ROW, readiness_fail_share=0.25)), "PROMOTE_CANDIDATE")
        self.assertEqual(decide(doc, self.ROW, pit_ok=False), "PARKED")
        self.assertEqual(decide(doc, self.ROW, ledger_rewritten=True), "PARKED")
        self.assertEqual(decide(doc, self.ROW, prereg_ok=False), "INVALID_PREREG")
        # no stream waits forever: parked or silent for more than max_parked_weeks closes it
        parked = dict(self.ROW, readiness_fail_share=0.9)
        self.assertEqual(decide(doc, parked, idle_weeks=G["max_parked_weeks"]), "PARKED")
        self.assertEqual(decide(doc, parked, idle_weeks=G["max_parked_weeks"] + 1), "CLOSED_INCONCLUSIVE")
        self.assertEqual(decide(doc, self.ROW, idle_weeks=G["max_parked_weeks"] + 1), "CLOSED_INCONCLUSIVE")   # no new ledger row
        self.assertEqual(decide(doc, dict(self.ROW, n=26, e_value=3.0)), "CLOSED_INCONCLUSIVE")
        # a candidate may finish its confirmation weeks past n_max, and no later
        self.assertEqual(decide(doc, dict(self.ROW, n=29)), "PROMOTE_CANDIDATE")
        self.assertEqual(decide(doc, dict(self.ROW, n=30)), "CLOSED_INCONCLUSIVE")
        self.assertEqual(decide(doc, dict(self.ROW, n=30), previous="PROMOTE_CANDIDATE", weeks_since_candidate=4), "PROMOTED")
        self.assertEqual(decide(doc, dict(self.ROW, n=25, e_value=3.0)), "ACCUMULATE")

    def test_row_order(self):
        doc = prereg()
        everything = dict(self.ROW, e_reverse=25.0, ci_upper=0.0, readiness_fail_share=0.9, n=30)
        self.assertEqual(decide(doc, everything, prereg_ok=False), "INVALID_PREREG")
        self.assertEqual(decide(doc, everything), "PARKED")                                  # a broken ledger is not evidence
        self.assertEqual(decide(doc, dict(everything, readiness_fail_share=0.0)), "KILLED_HARM")
        self.assertEqual(decide(doc, dict(everything, readiness_fail_share=0.0, e_reverse=1.0)), "KILLED_FUTILITY")
        # harm and futility outrank a promotion: a stream is never promoted on a row that kills it
        kw = {"previous": "PROMOTE_CANDIDATE", "weeks_since_candidate": 9}
        self.assertEqual(decide(doc, dict(self.ROW, e_reverse=20.0), **kw), "KILLED_HARM")
        self.assertEqual(decide(doc, dict(self.ROW, ci_upper=0.01), **kw), "KILLED_FUTILITY")

    def test_table_is_total_and_deterministic(self):
        doc = prereg()
        grid = itertools.product((0, 7, 8, 26, 30), (0.5, 19.9, 20.0, 500.0), (0.1, 20.0), (-0.1, 0.05, 0.2),
                                 (0.0, 0.049, 0.3), (0.0, 0.26), ("ACCUMULATE", "PROMOTE_CANDIDATE"), (0, 4), (True, False))
        seen = set()
        for n, e, er, mean, ci, share, prev, since, rev in grid:
            row = {"n": n, "e_value": e, "e_reverse": er, "mean_d": mean, "ci_upper": ci, "readiness_fail_share": share}
            first = decide(doc, row, previous=prev, weeks_since_candidate=since, reviewed=rev)
            self.assertEqual(first, decide(doc, row, previous=prev, weeks_since_candidate=since, reviewed=rev))
            self.assertIn(first, G["decisions"])
            seen.add(first)
        self.assertEqual(seen, set(G["decisions"]) - {"INVALID_PREREG"})

    def test_rule_text_matches_the_model_order(self):
        rows = re.findall(r"^(\d)\. ([A-Z_]+):", EDGE_MD, re.M)
        self.assertEqual([name for _, name in rows], G["decisions"])
        for token in ("first matching row wins", "e_reverse is at or above harm_e", "n is at or above n_min and ci_upper is below MDE",
                      "weeks_since_candidate is at or above confirm_weeks",
                      "n is at or above n_min and below n_max + confirm_weeks",
                      "every stream has a final decision by n_max + confirm_weeks valid weeks at the latest",
                      "A final decision (final_decisions) is final: S1 never reopens it",
                      "the Bonferroni bound for e-values over the whole family",
                      "e_value is at or above family_k_max / alpha_family, mean_d is at or above MDE",
                      "candidate_held is true, and an independent exact-head review of the scorer run exists",
                      "for more than max_parked_weeks consecutive weeks is CLOSED_INCONCLUSIVE instead: no stream waits forever",
                      "S1 changes nothing that is shown anywhere",
                      "weeks_since_candidate and candidate_held are NOT scorer fields: S1 derives them from its own S1_EDGE_DECISION_v1 posts"):
            self.assertIn(token, EDGE_MD)


class CompoundingLoopTest(unittest.TestCase):
    def test_a_real_edge_is_promoted_and_only_after_confirmation(self):
        history = run_stream(prereg(), [0.45] * 26)
        self.assertEqual(history[-1], "PROMOTED")
        first = history.index("PROMOTE_CANDIDATE")
        self.assertGreaterEqual(first + 1, G["n_min"])                        # never before n_min weeks
        self.assertEqual(history.index("PROMOTED") - first, G["confirm_weeks"])
        self.assertNotIn("PROMOTED", history[:G["n_min"]])

    def test_no_edge_is_falsified_or_closed_never_left_open(self):
        rng = random.Random(3)
        for trial in range(200):
            ds = [rng.uniform(-0.3, 0.3) for _ in range(G["n_max"] + G["confirm_weeks"])]
            history = run_stream(prereg(), ds)
            self.assertIn(history[-1], G["final_decisions"], trial)
            self.assertLessEqual(len(history), G["n_max"] + G["confirm_weeks"])
            self.assertNotEqual(history[-1], "PROMOTED", trial)

    def test_a_harmful_model_is_killed(self):
        history = run_stream(prereg(), [-0.6] * 26)
        self.assertIn(history[-1], ("KILLED_HARM", "KILLED_FUTILITY"))
        self.assertNotIn("PROMOTE_CANDIDATE", history)

    def test_without_review_nothing_is_promoted(self):
        history = run_stream(prereg(), [0.45] * 26, reviewed=False)
        self.assertNotIn("PROMOTE_CANDIDATE", history)
        self.assertNotIn("PROMOTED", history)
        self.assertEqual(history[-1], "CLOSED_INCONCLUSIVE")

    def test_every_stream_ends_by_n_max(self):
        rng = random.Random(11)
        for trial in range(300):
            drift = rng.uniform(-0.5, 0.5)
            ds = [max(-1.0, min(1.0, drift + rng.uniform(-0.4, 0.4))) for _ in range(G["n_max"] + 20)]
            history = run_stream(prereg(), ds)
            self.assertIn(history[-1], G["final_decisions"], (trial, drift))
            self.assertLessEqual(len(history), G["n_max"] + G["confirm_weeks"], (trial, drift))


class StewardIntegrationTest(unittest.TestCase):
    def test_s1_role_is_bounded(self):
        for token in ("S1 does not score outcomes itself", "It never changes a live product, a site page or a trading setting",
                      "post one S1_EDGE_DECISION_v1 on #1512", "Never post a second decision for the same stream and week",
                      "skipped=<PR>:E1:window_started", "reason needs_prereg", "S1 guesses nothing",
                      "at most streams_per_run streams per run; no new schedule", "edge=ABSENT",
                      "06_RESEARCH_LAB/edge_ledger_v1/LEDGER_SUMMARY.json at M",
                      "This release ships the rules only: the ledger directory and its scorer arrive by their own reviewed PRs"):
            self.assertIn(token, EDGE_MD)
        self.assertIn("B7 EDGE LEDGER (rule 6(b), first in its order)", LOOP_MD)
        self.assertIn("S1 never claims an edge the ledger has not decided.", LOOP_MD)
        self.assertIn("edge:<stream_id>", STATES_MD)
        self.assertIn("names an EDGE_LEDGER.md stream whose preregistration passes E1", ADMISSION_MD)
        self.assertIn("only while 06_RESEARCH_LAB/edge_ledger_v1/ exists on main", ADMISSION_MD)

    def test_no_new_schedule_identity_or_paid_call(self):
        for word in ("workflow_dispatch", "cron", "paid"):
            self.assertNotIn(word, EDGE_MD)
        self.assertGreaterEqual(G["streams_per_run"], 1)


if __name__ == "__main__":
    unittest.main()
