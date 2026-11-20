"""S1 v3.3 W2 (SHADOW): the hardened parse_body, B.verdict and the S1_BRIEF_DIGEST_V1 readback of the brief.

Fixtures only, no network. W2 step 0 is the hardened parser (CHARTER_ADDENDUM_1 items 1 and 2): ordered and unique
markers, one fence, unique keys at every level, no NaN or Infinity, and typed fields. W2 core adds B.verdict (the
producer's own BOOTSTRAP 3/3b and T2 pins checks at B.main, plus the T3 tree basis) and the readback digest (R2-7).
Both are SHADOW: TICK.md does not read them, and the rest of the rendered brief is byte-identical to before W2."""
import copy
import hashlib
import json
import re
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT / "scripts" / "governance", ROOT / "tests" / "governance"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import s1_tick_brief_v1 as B  # noqa: E402
import test_s1_tick_brief_v1 as TB  # noqa: E402  (module import: its TestCases are not collected twice)
import test_s1_trajectory_replay_v1 as TR  # noqa: E402

TICK = (ROOT / "00_FMOS" / "S1" / "TICK.md").read_text(encoding="utf-8")
ACTION_LOOP = (ROOT / "00_FMOS" / "S1" / "ACTION_LOOP.md").read_text(encoding="utf-8")
BOOTSTRAP = (ROOT / "00_FMOS" / "S1" / "BOOTSTRAP.txt").read_text(encoding="utf-8")
SOURCE = (ROOT / "scripts" / "governance" / "s1_tick_brief_v1.py").read_text(encoding="utf-8")

# sha256 of render() on main BEFORE W2 (base c0bda2e3), for three briefs of the fixture world: plain, shrink level 1/2
# and shrink level 3. W2 must keep these bytes when B.verdict is taken out (shadow: nothing else moved).
RENDER_SHA256_BEFORE_W2 = {
    "plain": (3252, "199cfbc66486367add452b15bb1538456b63ece9f5f30b254e246645a9345d6e"),
    "medium": (46363, "cf497ce5a506e7dc163443f206d87b1f0d14d00d9acf285ee543372835b29295"),
    "huge": (1337, "0386f61406d545806d26da4a102b8fff8c24429391586deac9d827b2d9c0915e"),
}


def many(w, n, pad):
    for i in range(100, 100 + n):
        w["pulls"].append(TB.pull(i, TB.HEAD))
        d = TB.pr_data()
        d["detail"]["number"] = d["detail2"]["number"] = i
        d["files"][0]["filename"] = "docs/" + "x" * pad + f"/{i}.md"
        w["pr"][i] = d


SIZES = {"plain": None, "medium": lambda w: many(w, 70, 200), "huge": lambda w: many(w, 400, 10)}


def block_of(body):
    return body.split("```json\n", 1)[1].rsplit("\n```", 1)[0]


def wrap(text, before=B.BEGIN, after=B.END):
    return f"{before}\n```json\n{text}\n```\n{after}\n"


GOOD = B.render(TB.brief_of())
GOOD_TEXT = block_of(GOOD)


def swap(old, new):
    assert GOOD_TEXT.count(old) >= 1, old
    return wrap(GOOD_TEXT.replace(old, new, 1))


# ================================================================================================ W2 step 0: parser
class HardenedParser(unittest.TestCase):
    """Each rule with a positive and a negative case."""

    def test_the_rendered_brief_still_parses(self):
        self.assertEqual(B.parse_body(GOOD), json.loads(json.dumps(TB.brief_of())))
        self.assertIsNotNone(B.parse_body(wrap(GOOD_TEXT)))

    def test_markers_exactly_one_each_and_begin_first(self):
        self.assertIsNone(B.parse_body(wrap(GOOD_TEXT, before=B.END, after=B.BEGIN)))          # END before BEGIN
        self.assertIsNone(B.parse_body(B.BEGIN + "\n" + wrap(GOOD_TEXT)))                     # two BEGIN
        self.assertIsNone(B.parse_body(wrap(GOOD_TEXT) + B.END))                              # two END
        self.assertIsNone(B.parse_body(wrap(GOOD_TEXT, before="")))                           # no BEGIN
        self.assertIsNone(B.parse_body(wrap(GOOD_TEXT, after="")))                            # no END
        self.assertIsNotNone(B.parse_body("prose above\n\n" + wrap(GOOD_TEXT) + "\nprose below"))

    def test_exactly_one_json_fence(self):
        two = f"{B.BEGIN}\n```json\n{GOOD_TEXT}\n```\n```json\n{GOOD_TEXT}\n```\n{B.END}"
        self.assertIsNone(B.parse_body(two))
        self.assertIsNone(B.parse_body(f"{B.BEGIN}\n{GOOD_TEXT}\n{B.END}"))                   # no fence
        self.assertIsNone(B.parse_body(f"{B.BEGIN}\n```\n{GOOD_TEXT}\n```\n{B.END}"))         # not a json fence

    def test_duplicate_keys_are_rejected_at_every_level(self):
        self.assertIsNone(B.parse_body(swap('"complete":true', '"complete":false,"complete":true')))   # top level
        self.assertIsNone(B.parse_body(swap('"ok":true', '"ok":false,"ok":true')))                     # pins.ok
        self.assertIsNone(B.parse_body(swap('"head":"' + TB.HEAD, '"head":"x","head":"' + TB.HEAD)))  # inside prs[] / next[]
        self.assertIsNone(B.parse_body(swap('"id":4242', '"id":4242,"id":4242')))                      # same value twice
        # the SAME key in DIFFERENT objects is fine (pins.ok and verdict.shadow sit beside many other "ok"/"main" keys)
        self.assertGreater(GOOD_TEXT.count('"main":'), 1)
        self.assertIsNotNone(B.parse_body(GOOD))

    def test_nan_and_infinity_are_rejected(self):
        for bad in ("NaN", "Infinity", "-Infinity"):
            self.assertIsNone(B.parse_body(swap('"max_age_minutes":45', f'"max_age_minutes":{bad}')), bad)
        self.assertIsNotNone(B.parse_body(swap('"max_age_minutes":45', '"max_age_minutes":45.5')))     # a real number is fine
        self.assertIsNotNone(B.parse_body(swap('"event":"schedule"', '"event":"NaN"')))               # so is the string

    def test_ids_are_positive_ints_and_never_bools(self):
        for bad in ("true", "false", "0", "-5", "1.0", '"44690000101"', "null"):
            with self.subTest(run_id=bad):
                self.assertIsNone(B.parse_body(swap('"run_id":555', f'"run_id":{bad}')))
            with self.subTest(run_attempt=bad):
                self.assertIsNone(B.parse_body(swap('"run_attempt":1', f'"run_attempt":{bad}')))
        self.assertIsNone(B.parse_body(swap('"id":4242', '"id":true')))                               # repo.id
        self.assertEqual(B.parse_body(swap('"run_id":555', '"run_id":44690000101'))["run_id"], 44690000101)

    def test_sha_fields_are_40_hex(self):
        for bad in ('"' + "a" * 39 + '"', '"' + "A" * 40 + '"', '"' + "g" * 40 + '"', '"' + "a" * 41 + '"', "null", "7"):
            with self.subTest(main=bad):
                self.assertIsNone(B.parse_body(swap('"main":"' + TB.MAIN + '"', f'"main":{bad}')))
        for key, value in (("contract_blob", "8" * 40), ("tick_blob", "6" * 40), ("action_loop_blob", "4" * 40)):
            with self.subTest(key):
                self.assertIsNone(B.parse_body(swap(f'"{key}":"{value}"', f'"{key}":"{value[:12]}"')))
                self.assertIsNotNone(B.parse_body(swap(f'"{key}":"{value}"', f'"{key}":null')))       # unreadable at main: null, typed

    def test_the_other_typed_fields(self):
        for old, new in (('"ok":true', '"ok":"true"'), ('"complete":true', '"complete":1'), ('"incomplete":null', '"incomplete":5'),
                         ('"schema":"S1_TICK_BRIEF_V1"', '"schema":"S1_TICK_BRIEF_V2"'), ('"event":"schedule"', '"event":7'),
                         ('"next":[', '"next":7,"x":['), ('"claude_slots":[]', '"claude_slots":{}'), ('"prs":[', '"prs":7,"y":[')):
            with self.subTest(new):
                body = swap(old, new)
                json.loads(block_of(body))                                                         # still valid JSON: the TYPE fails
                self.assertIsNone(B.parse_body(body))
        doc = json.loads(GOOD_TEXT)
        for lines in (doc["status_lines"][:2], doc["status_lines"] + ["x"], [1, 2, 3]):
            self.assertIsNone(B.parse_body(wrap(json.dumps(dict(doc, status_lines=lines)))))
        self.assertIsNone(B.parse_body(wrap(json.dumps(dict(doc, next=[1])))))
        self.assertIsNone(B.parse_body(wrap(json.dumps([doc]))))                                   # not an object

    def test_deep_nesting_is_rejected_without_a_crash(self):
        self.assertIsNone(B.parse_body(wrap("[" * 100000 + "]" * 100000)))
        self.assertIsNone(B.parse_body(wrap('{"a":' * 30000 + "1" + "}" * 30000)))

    def test_verify_brief_and_publish_use_the_hardened_reading(self):
        auth = TB.Authenticity("test_authentic_fresh_brief")
        auth.setUp()
        self.assertEqual(auth.check()[1], "OK")
        text = block_of(auth.issue["body"])
        for name, body in {"order": wrap(text, before=B.END, after=B.BEGIN),
                           "duplicate": wrap(text.replace('"ok":true', '"ok":false,"ok":true', 1)),
                           "nan": wrap(text.replace('"max_age_minutes":45', '"max_age_minutes":NaN', 1)),
                           "bool_run_id": wrap(text.replace('"run_id":555', '"run_id":true', 1))}.items():
            with self.subTest(name):
                self.assertEqual(auth.check(issues=[dict(auth.issue, body=body)])[1], "BRIEF_UNVERIFIED(body)")
                with self.assertRaises(SystemExit):
                    B.publish(TB.Publish.Fake([]), body)                                          # never published either


class ParserParityWithTheReferenceExecutor(unittest.TestCase):
    """AD-2 differential: parse_body against read_block(mode="strict") of the W1 harness, the reading of TICK T1 plus
    BOOTSTRAP step 4, over every W1 fixture body and the mutations above. One intended difference: parse_body also
    requires the pins SHA fields to be 40-hex (the harness only types them as strings)."""

    def corpus(self):
        bodies = {f"{fx['id']}": fx["world"]["routes"].get(TR.ISSUES_URL) for fx in TR.FIXTURES}
        out = {k: v[0].get("body") for k, v in bodies.items() if isinstance(v, list) and v and isinstance(v[0], dict)}
        out.update({"good": GOOD, "order": wrap(GOOD_TEXT, before=B.END, after=B.BEGIN), "nested_dupe": swap('"ok":true', '"ok":false,"ok":true'),
                    "inf": swap('"max_age_minutes":45', '"max_age_minutes":Infinity'), "bool": swap('"run_id":555', '"run_id":false'),
                    "two_fences": f"{B.BEGIN}\n```json\n{GOOD_TEXT}\n```\n```json\n{GOOD_TEXT}\n```\n{B.END}",
                    "short_pin": swap('"tick_blob":"' + "6" * 40, '"tick_blob":"' + "6" * 12)})
        return out

    def test_same_reading_on_every_body(self):
        differ = {}
        for name, body in self.corpus().items():
            mine, ref = B.parse_body(body), TR.read_block(body)
            if mine != ref:
                differ[name] = (mine is None, ref is None)
        self.assertEqual(differ, {"short_pin": (True, False)})
        self.assertGreaterEqual(len(self.corpus()), 40)


# ================================================================================================ W2 core: B.verdict
def verdict_world(**change):
    """The fixture world of test_s1_tick_brief_v1 with a complete source chain at B.main, so the verdict is OK."""
    w = TB.world()
    w["contract"]["bootstrap_version"] = "S1_BOOTSTRAP_v8"
    w["bootstrap_text"] = "3. ... and bootstrap_version must be S1_BOOTSTRAP_v8. If any\n3b. ... must equal " + "8" * 40 + ". This value"
    w["trees_actual"] = {"": "c" * 40, **{d: f"{i + 1:x}" * 40 for i, d in enumerate(B.T3_TREE_DIRS)}}
    for key, value in change.items():
        w[key] = value
    return w


def verdict_of(mutate=None):
    w = verdict_world()
    if mutate:
        mutate(w)
    return B.build_brief(w)["verdict"]


class Verdict(unittest.TestCase):
    def test_a_complete_chain_is_ok_and_names_what_only_s1_decides(self):
        v = verdict_of()
        self.assertEqual({k: v[k] for k in ("schema", "shadow", "main", "source", "t1", "t2", "t2_scope", "t3", "reasons")},
                         {"schema": "S1_BRIEF_VERDICT_V1", "shadow": True, "main": TB.MAIN, "source": "OK", "t1": "S1_DECIDES",
                          "t2": "OK", "t2_scope": "pins", "t3": "S1_DECIDES", "reasons": []})
        self.assertEqual((v["contract_blob"], v["bootstrap_3b"]), ("8" * 40, "8" * 40))

    def test_each_bootstrap_step_3_check(self):
        cases = {
            "3:action_loop_blob": lambda w: w["pins_actual"].update({"00_FMOS/S1/ACTION_LOOP.md": "0" * 40}),
            "3:tick_blob": lambda w: w["pins_actual"].update({"00_FMOS/S1/TICK.md": None}),
            "3:lane_switch_blob": lambda w: w["contract"].update(lane_switch_blob="5" * 39),
            "3:rubric:00_FMOS/S1/STEWARD_STATES.md": lambda w: w["pins_actual"].pop("00_FMOS/S1/STEWARD_STATES.md"),
            "3:bootstrap_version": lambda w: w["contract"].update(bootstrap_version="S1_BOOTSTRAP_v7"),
        }
        for reason, mutate in cases.items():
            with self.subTest(reason):
                v = verdict_of(mutate)
                self.assertEqual(v["source"], "SOURCE_UNVERIFIED(3)")
                self.assertIn(reason, v["reasons"])
        v = verdict_of(lambda w: w.update(bootstrap_text=w["bootstrap_text"].replace("bootstrap_version must be", "version")))
        self.assertIn("3:bootstrap_version", v["reasons"])
        self.assertEqual(verdict_of(lambda w: w["contract"].pop("rubric_blobs"))["source"], "OK")        # none listed: none to check
        w = verdict_world()
        bad = B.brief_verdict(TB.MAIN, dict(w["contract"], rubric_blobs=["x"]), w["pins_actual"], w["bootstrap_text"], {}, w["trees_actual"])
        self.assertIn("3:rubric_blobs", bad["reasons"])                                           # not a map: unverifiable
        self.assertIn("3:rubric:00_FMOS/S1/STEWARD_STATES.md",
                      B.brief_verdict(TB.MAIN, dict(w["contract"], rubric_blobs={"00_FMOS/S1/STEWARD_STATES.md": None}), w["pins_actual"],
                                      w["bootstrap_text"], {}, w["trees_actual"])["reasons"])    # a listed value that is no SHA

    def test_step_3b_against_the_bootstrap_text_at_b_main(self):
        v = verdict_of(lambda w: w.update(bootstrap_text=w["bootstrap_text"].replace("8" * 40, "9" * 40)))
        self.assertEqual((v["source"], v["bootstrap_3b"]), ("SOURCE_UNVERIFIED(3b)", "9" * 40))
        self.assertIn("3b:bootstrap_text", v["reasons"])
        v = verdict_of(lambda w: w["pins_actual"].update({B.CONTRACT_FILE: None}))
        self.assertEqual((v["source"], v["contract_blob"]), ("SOURCE_UNVERIFIED(3b)", None))
        both = verdict_of(lambda w: (w["contract"].update(tick_blob="0" * 40), w.update(bootstrap_text=w["bootstrap_text"].replace("8" * 40, "9" * 40))))
        self.assertEqual(both["source"], "SOURCE_UNVERIFIED(3)")                                  # step 3 is checked first
        self.assertEqual(both["reasons"][:2], ["3:tick_blob", "3b:bootstrap_text"])

    def test_the_t2_pins_clause(self):
        self.assertIn("pins:ok", verdict_of(lambda w: w["pins_actual"].update({"AGENTS.md": "0" * 40}))["reasons"])
        # computed on its own, not copied from pin_check: a pins block that says ok with other blobs still fails here
        v = B.brief_verdict(TB.MAIN, verdict_world()["contract"], verdict_world()["pins_actual"], verdict_world()["bootstrap_text"],
                            {"ok": True, "contract_blob": "9" * 40, "action_loop_blob": "0" * 40, "tick_blob": None}, verdict_world()["trees_actual"])
        self.assertEqual((v["t2"], v["reasons"]), ("BRIEF_UNVERIFIED(pins)", ["pins:contract_blob", "pins:action_loop_blob", "pins:tick_blob"]))
        self.assertEqual(v["source"], "OK")
        ok = B.build_brief(verdict_world())["pins"]
        self.assertEqual(B.brief_verdict(TB.MAIN, verdict_world()["contract"], verdict_world()["pins_actual"], verdict_world()["bootstrap_text"],
                                         ok, verdict_world()["trees_actual"])["t2"], "OK")
        stale_3b = dict(ok, contract_blob="8" * 40)
        text = verdict_world()["bootstrap_text"].replace("8" * 40, "9" * 40)
        self.assertIn("pins:contract_blob", B.brief_verdict(TB.MAIN, verdict_world()["contract"], verdict_world()["pins_actual"], text,
                                                            stale_3b, verdict_world()["trees_actual"])["reasons"])

    def test_t3_basis_root_and_every_c1b_tree(self):
        v = verdict_of()
        self.assertEqual(B.T3_TREE_DIRS, ("scripts", "tests", ".github", ".agents", "00_FMOS"))
        self.assertEqual(v["t3_basis"], {"root_tree": "c" * 40, "trees": {d: f"{i + 1:x}" * 40 for i, d in enumerate(B.T3_TREE_DIRS)}})
        for name in ("", *B.T3_TREE_DIRS):
            with self.subTest(name or "root"):
                for bad in (None, "c" * 12):
                    v = verdict_of(lambda w: w["trees_actual"].update({name: bad}))
                    self.assertIn(f"t3_basis:{name or 'root'}", v["reasons"])
                    self.assertEqual((v["source"], v["t2"]), ("OK", "OK"))                       # basis is evidence, not a source check
        v = B.build_brief(TB.world())["verdict"]                                                  # no tree reads recorded at all
        self.assertEqual(v["t3_basis"]["root_tree"], None)
        self.assertEqual(len(v["reasons"]), len(set(v["reasons"])))

    def test_collect_records_the_real_trees_of_this_checkout(self):
        snap, _fake, _seen = TB.CollectReplay().run_collect()
        brief = B.build_brief(snap)
        v, git = brief["verdict"], lambda *a: B.git(ROOT, *a)
        self.assertEqual(v["main"], brief["main"])
        self.assertEqual(v["t3_basis"]["root_tree"], git("rev-parse", "HEAD^{tree}"))
        for d in B.T3_TREE_DIRS:
            self.assertEqual(v["t3_basis"]["trees"][d], git("rev-parse", f"HEAD:{d}"), d)
        self.assertEqual((v["source"], v["t2"], v["contract_blob"]), ("OK", "OK", git("rev-parse", f"HEAD:{B.CONTRACT_FILE}")))
        self.assertEqual(v["reasons"], [])
        self.assertIn('snap["trees_actual"] = root_trees(root)', SOURCE)
        self.assertEqual(B.root_trees(Path("/nonexistent")), dict.fromkeys(("", *B.T3_TREE_DIRS)))   # unreadable: every value None

    def test_root_trees_takes_only_tree_entries_of_the_root(self):
        rows = {("rev-parse", "HEAD^{tree}"): "c" * 40,
                ("ls-tree", "-z", "HEAD"): "\0".join(["040000 tree " + "1" * 40 + "\tscripts", "100644 blob " + "2" * 40 + "\ttests",
                                                       "040000 tree " + "3" * 40 + "\t.github", "040000 tree " + "4" * 40 + "\tdocs",
                                                       "160000 commit " + "5" * 40 + "\t.agents", "040000 tree " + "6" * 40 + "\t00_FMOS"])}
        saved = B.git
        B.git = lambda root, *args: rows[args]
        try:
            got = B.root_trees(ROOT)
        finally:
            B.git = saved
        self.assertEqual(got, {"": "c" * 40, "scripts": "1" * 40, "tests": None, ".github": "3" * 40, ".agents": None, "00_FMOS": "6" * 40})

    def test_shadow_s1_does_not_read_it(self):
        for text in (TICK, ACTION_LOOP, BOOTSTRAP):
            self.assertNotIn("B.verdict", text, "TICK, ACTION_LOOP and BOOTSTRAP do not read B.verdict (shadow)")
            self.assertNotIn(B.DIGEST_TOKEN, text)
        auth = TB.Authenticity("test_authentic_fresh_brief")
        auth.setUp()
        lying = dict(auth.brief, verdict=dict(auth.brief["verdict"], source="SOURCE_UNVERIFIED(3)", t2="BRIEF_UNVERIFIED(pins)"))
        self.assertEqual(auth.check(issues=[dict(auth.issue, body=B.render(lying))])[1], "OK")      # verify_brief ignores it
        honest = dict(auth.brief, verdict=dict(auth.brief["verdict"], source="OK", t2="OK"))
        auth.brief["pins"]["ok"] = False
        self.assertEqual(auth.check(issues=[dict(auth.issue, body=B.render(dict(honest, pins=auth.brief["pins"])))])[1],
                         "BRIEF_UNVERIFIED(pins)")                                                  # and can never be talked into OK by it
        broken = dict(auth.brief)
        broken.pop("verdict")
        auth.brief["pins"]["ok"] = True
        self.assertEqual(auth.check(issues=[dict(auth.issue, body=B.render(dict(broken, pins=auth.brief["pins"])))])[1], "OK")
        self.assertEqual(auth.check(issues=[dict(auth.issue, body=B.render(dict(broken, verdict="garbage")))])[1], "OK")


class RenderStability(unittest.TestCase):
    def test_everything_but_the_verdict_is_byte_identical_to_before_w2(self):
        for name, mutate in SIZES.items():
            with self.subTest(name):
                brief = TB.brief_of(mutate)
                self.assertIn("verdict", brief)
                brief.pop("verdict")
                body = B.render(brief)
                self.assertEqual((len(body), hashlib.sha256(body.encode("utf-8")).hexdigest()), RENDER_SHA256_BEFORE_W2[name])

    def test_the_verdict_survives_every_shrink_level_and_the_body_fits(self):
        seen = {}
        for name, mutate in SIZES.items():
            brief = TB.brief_of(mutate)
            body = B.render(brief)
            doc = B.parse_body(body)
            self.assertLessEqual(len(body), B.MAX_BODY, name)
            self.assertEqual(doc["verdict"], json.loads(json.dumps(brief["verdict"])), name)
            seen[name] = doc.get("shrunk")
        self.assertEqual((seen["plain"], seen["huge"]), (None, 3))
        self.assertIn(seen["medium"], (1, 2))
        self.assertLess(len(json.dumps(TB.brief_of()["verdict"], separators=(",", ":"))), 1200)   # small and fixed in size

    def test_a_brief_just_under_the_limit_still_fits_with_its_verdict(self):
        for n in range(60, 130, 7):                                                               # sweep across the level-1/2/3 edges
            with self.subTest(n=n):
                body = B.render(TB.brief_of(lambda w: many(w, n, 200)))
                self.assertLessEqual(len(body), B.MAX_BODY)
                self.assertIn("verdict", B.parse_body(body))


# ================================================================================================ R2-7: digest + readback
class Digest(unittest.TestCase):
    class Gh:
        def __init__(self, answer):
            self.answer, self.paths = answer, []

        def get(self, path, params=None):
            self.paths.append(path)
            if isinstance(self.answer, BaseException):
                raise self.answer
            return self.answer

    def test_the_digest_is_over_the_exact_block_bytes(self):
        want = hashlib.sha256(GOOD_TEXT.encode("utf-8")).hexdigest()
        self.assertEqual(B.brief_digest(GOOD), want)
        self.assertEqual(B.brief_digest("prose\n" + GOOD + "\nmore prose"), want)               # the block, not the whole body
        self.assertNotEqual(B.brief_digest(GOOD.replace('"complete":true', '"complete":true ', 1)), want)   # one byte
        self.assertIsNone(B.brief_digest("no block"))
        self.assertIsNone(B.brief_digest(wrap(GOOD_TEXT, before=B.END, after=B.BEGIN)))
        nonascii = GOOD.replace('"event":"schedule"', '"event":"schédule"', 1)
        self.assertEqual(B.brief_digest(nonascii), hashlib.sha256(block_of(nonascii).encode("utf-8")).hexdigest())

    def line(self, answer, body=GOOD):
        gh = self.Gh(answer)
        out = B.readback_line(gh, 3000, body)
        self.assertEqual(gh.paths, ["issues/3000"])                                               # exactly ONE read
        return out

    def test_readback_states(self):
        mine = B.parse_body(GOOD)
        other_run = B.render(dict(TB.brief_of(), run_id=mine["run_id"] + 1))
        other_attempt = B.render(dict(TB.brief_of(), run_attempt=2))
        same_run_other_bytes = GOOD.replace('"complete":true', '"complete":true ', 1)
        cases = {"MATCH": {"body": GOOD}, "SUPERSEDED": {"body": other_run}, "MISMATCH": {"body": same_run_other_bytes},
                 "UNREADABLE": {"body": "no block"}}
        for state, answer in cases.items():
            with self.subTest(state):
                self.assertTrue(self.line(answer).endswith(f" readback={state}"))
        self.assertTrue(self.line({"body": other_attempt}).endswith("readback=SUPERSEDED"))
        self.assertTrue(self.line({"body": wrap('{"run_id":555,"x":NaN}')}).endswith("readback=MISMATCH"))
        for answer in (OSError("down"), B.ApiBudget("API_BUDGET_EXHAUSTED"), B.RateLimited("HTTP_429"), [], {"body": None}, None):
            with self.subTest(answer=repr(answer)):
                self.assertTrue(self.line(answer).endswith(" readback=UNREADABLE"))              # never raised: shadow

    def test_the_line_names_the_bytes_and_both_digests(self):
        out = self.line({"body": GOOD})
        want = B.brief_digest(GOOD)
        self.assertEqual(out, f"S1_BRIEF_DIGEST_V1 issue=3000 run=555 main={TB.MAIN} sha256={want} "
                              f"bytes={len(GOOD_TEXT.encode('utf-8'))} expected_sha256={want} readback=MATCH")
        out = self.line({"body": "x"})
        self.assertIn(" sha256=- bytes=- expected_sha256=" + want, out)

    def test_it_is_printed_after_the_publish_on_its_own_budget_and_reads_only(self):
        publish_mode = SOURCE[SOURCE.index('    if mode == "publish":'):]
        self.assertLess(publish_mode.index('print(f"S1_TICK_BRIEF_PUBLISHED'), publish_mode.index("print(readback_line(GitHub(token, budget=READBACK_API_CALLS), number, body))"))
        self.assertIn("publish(GitHub(token, budget=PUBLISH_API_CALLS), body)", publish_mode)
        self.assertEqual((B.READBACK_API_CALLS, B.PUBLISH_API_CALLS), (2, 25))
        fn = SOURCE[SOURCE.index("def readback_line("):SOURCE.index("def main(argv):")]
        self.assertNotIn("_request(", fn)                                                         # a GET through gh.get only
        self.assertEqual(re.findall(r"gh\.(\w+)\(", fn), ["get"])
        wf = (ROOT / B.WORKFLOW_PATH).read_text(encoding="utf-8")
        self.assertIn("python scripts/governance/s1_tick_brief_v1.py publish", wf)                # same step, no new permission
        self.assertEqual(TB.yaml.safe_load(wf)["jobs"]["publish"]["permissions"], {"contents": "read", "issues": "write", "actions": "read"})

    def test_a_real_github_client_counts_the_readback_against_its_own_cap(self):
        gh = B.GitHub("t", budget=B.READBACK_API_CALLS)
        gh.calls = B.READBACK_API_CALLS                                                           # spent: the read is refused by the cap
        self.assertTrue(B.readback_line(gh, 3000, GOOD).endswith("readback=UNREADABLE"))


# The one intended difference. F02: main carries a NEW contract and the owner's paste still holds the old 3b. W1 (S1)
# compares B.pins.contract_blob with the saved paste and, with 3b switched off, accepts the old value; the producer
# compares it with the contract blob AT B.main and refuses it. That is why S1 keeps its own 3b cross-check (charter W2).
KNOWN_PINS_DIVERGENCE = {"F02": ("BRIEF_UNVERIFIED(pins)", "OK")}


class VerdictAgreesWithW1(unittest.TestCase):
    """Charter W2 acceptance, fixture half: on every W1 fixture whose brief was built at the M of the tick, the
    producer's verdict over the same recorded contract, listing and pins agrees with the reference executor. The
    producer reads BOOTSTRAP.txt at B.main; in a fixture that is the owner's saved paste (S1's own 3b cross-check),
    so the 3b part is compared through verdict.contract_blob against the saved value."""

    @staticmethod
    def inputs(fx):
        routes, saved = fx["world"]["routes"], fx["world"]["saved_3b"]
        main = routes.get(TR.API + "/branches/main")
        m = (main.get("commit") or {}).get("sha") if isinstance(main, dict) else None
        listing = routes.get(f"{TR.API}/contents/{TR.S1_DIR}?ref={m}")
        try:
            contract = json.loads(routes.get(f"file:{TR.CONTRACT_PATH}@{m}"))
        except (TypeError, ValueError):
            return None
        if not isinstance(listing, list) or not isinstance(contract, dict):
            return None
        blobs = {e.get("path"): e.get("sha") for e in listing if isinstance(e, dict) and e.get("type") == "file"}
        issues = routes.get(TR.ISSUES_URL)
        brief = TR.read_block(issues[0].get("body")) if isinstance(issues, list) and len(issues) == 1 and isinstance(issues[0], dict) else None
        text = f"and bootstrap_version must be {TR.BOOTSTRAP_VERSION}. If any\n3b. ... must equal {saved}. This value"
        return m, contract, blobs, text, brief

    # T1 and the T2 clauses before pins switched off (W1 mutant switches), so W1 reaches its own pins clause
    BEFORE_PINS = ("t0_monday", "issues", "author", "run_binding", "run_not_success", "edited_outside_run", "bootstrap_3b")

    @classmethod
    def w1_pins(cls, fx):
        r = TR.replay(fx, off=cls.BEFORE_PINS)
        if r.result == "BRIEF_UNVERIFIED(pins)":
            return "BRIEF_UNVERIFIED(pins)"
        if r.stages.get("T2") == "OK" or r.result.startswith(("BRIEF_STALE(age_min=", "BRIEF_INCOMPLETE(")) and "T3:" not in r.result:
            return "OK"
        return None                                                # W1 never reached its pins clause

    def test_every_fixture(self):
        compared = {"source": [], "t2": []}
        for fx in TR.FIXTURES:
            got = self.inputs(fx)
            if got is None:
                continue
            m, contract, blobs, text, brief = got
            v = B.brief_verdict(m, contract, blobs, text, (brief or {}).get("pins"), {})
            r = TR.replay(fx, off=("t0_monday",))
            with self.subTest(fx["id"]):
                if r.result.startswith("SOURCE_UNVERIFIED"):
                    self.assertEqual(v["source"], r.result)
                else:
                    self.assertEqual((v["source"], v["contract_blob"]), ("OK", fx["world"]["saved_3b"]))
                compared["source"].append(fx["id"])
                if brief is None or brief.get("main") != m:
                    continue                                       # T2 pins at B.main != M: C is not the contract at B.main
                want = self.w1_pins(fx)
                if want is not None:
                    self.assertEqual((v["t2"], want), KNOWN_PINS_DIVERGENCE.get(fx["id"], (want, want)))
                    compared["t2"].append((fx["id"], v["t2"]))
        self.assertEqual(len(compared["source"]), len(TR.FIXTURES) - 1)                  # every fixture with a readable source
        self.assertEqual(sorted(i for i, w in compared["t2"] if w != "OK"), ["F02", "F13", "F13b"])
        self.assertGreaterEqual(len(compared["t2"]), 15)


class W1StaysGreen(unittest.TestCase):
    """CHARTER_ADDENDUM_2 item 5: every W2 change keeps W1 at 0 unsafe writes and both metrics at 1.0."""

    def test_metrics(self):
        s = TR.score()
        self.assertEqual((s["task_completion"], s["policy_compliance"], s["unsafe_effects"]), (1.0, 1.0, 0))


if __name__ == "__main__":
    unittest.main()
