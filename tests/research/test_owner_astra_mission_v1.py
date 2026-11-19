"""No-network, no-bill tests of the generic owner Astra mission launcher (trigger, claim, guard, no retry)."""
import contextlib
import copy
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

from scripts.research import owner_astra_mission_v1 as m
from scripts.api_agent import astra_mission_reservations_v1 as res

ROOT = Path(__file__).resolve().parents[2]
MID = "ASTRA-S1-V32-REDTEAM-20261118-R2"
SOL_MID = "ASTRA-S1-V32-REDTEAM-20261118-R2-SOL"
ALPHA_MID = "ASTRA-ALPHA-GLOBAL-SPECIALIST-20261118"
# Wire bytes of the existing Astra missions, pinned before multi-model support: they must never change.
ASTRA_REQUEST_SHA = {MID: "73ac962b93e6119652ed0b8c39894c0404811c0c1beafb7991f8333d342fee68"}
# Alpha was rerouted to Sol 6.2 MAX by the owner on 2026-11-19 (never launched as Astra); its Sol wire bytes are pinned.
SOL_REQUEST_SHA = {ALPHA_MID: "a2d47d8df628aa2fd76297fab5467a40c5b6e473f8e1874267f0f5e992ad3184"}
BUNDLE_SHA = "b1b9e7698207dbdbfcad80b9c20a14602e93d4755f22c5879c372e7b2edc802c"
GUARD = ROOT / "scripts/api_agent/check_monthly_cost_guard.py"
CANONICAL_LEDGER = ROOT / "research/api_agent/coordination/API_PENDING_BILLING_RISK_V1.json"
def checkout_head():
    # Derive at event construction, not collection: full-suite tests can move HEAD.
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def reservation(mid=MID, upper=20):
    return {"work_id": mid, "created_month_utc": "2026-11", "status": "OWNER_RESERVED_PREHTTP", "lower_usd": 0,
            "upper_usd": upper, "source": res.SOURCE, "one_paid_post_max": 1, "reconciliation_required": True,
            "authorization": "test", "basis": "Owner-approved single Astra mission POST reserved before HTTP (test)."}


def consumed_row(mid=MID, upper=20, **over):
    row = dict(reservation(mid, upper), status="CONSUMED_PENDING_INVOICE", consumed_run_id=44386340009,
               consumed_response_id="resp_0477227a70790153006afe044ec9c487d08ebd44a0466687db",
               consumed_estimated_upper_usd=3.13212)
    row.update(over)
    return row


def trigger(mid=MID, sha=BUNDLE_SHA):
    return "OWNER_LAUNCH_ASTRA_MISSION " + mid + " " + sha


def event(body=None, **over):
    ev = {"action": "created", "issue": {"number": 1156},
          "comment": {"id": 777, "body": trigger() if body is None else body,
                      "user": {"login": "Donh91", "type": "User"}, "author_association": "OWNER"}}
    for k, v in over.items():
        if k in ("login", "type"):
            ev["comment"]["user"][k] = v
        elif k == "author_association":
            ev["comment"][k] = v
        elif k == "issue_number":
            ev["issue"]["number"] = v
        elif k == "pull_request":
            ev["issue"]["pull_request"] = v
        else:
            ev[k] = v
    return ev


class FakeAPI:
    """Routes core.http_json; records every call. No real network."""
    def __init__(self, comments=None, response=None, post_error=None, artifacts=0, responses=None, model=m.MODEL,
                 mid=MID):
        self.calls, self.comments, self.artifacts = [], list(comments or []), artifacts
        self.model, self.mid = model, mid
        self.keys, self.responses = [], list(responses or [])
        self.next_id = 9000
        self.response = response or {"id": "resp_test1234", "model": model, "status": "completed",
                                     "output": [{"type": "message", "content": [{"type": "output_text",
                                                                                 "text": "# report\nbody\n"}]}],
                                     "usage": {"input_tokens": 90000, "output_tokens": 30000}}
        self.post_error = post_error

    def __call__(self, method, url, *, api_key=None, github_token=None, body=None, timeout=60):
        self.calls.append((method, url, body))
        self.keys.append((method, url, api_key))
        if method == "GET" and "/issues/1156/comments" in url:
            page = int(url.rsplit("page=", 1)[1])
            return self.comments[(page - 1) * 100: page * 100]
        if method == "POST" and url.endswith("/issues/1156/comments"):
            self.next_id += 1
            row = {"id": self.next_id, "body": body["body"], "user": {"login": "github-actions[bot]"}}
            self.comments.append(row)
            return row
        if method == "GET" and "/actions/artifacts?" in url:
            assert url.endswith("&name=astra-mission-claim-" + self.mid), url
            return {"total_count": self.artifacts, "artifacts": []}
        if method == "GET" and url.endswith("/models/" + self.model):
            return {"id": self.model}
        if method == "POST" and url.endswith("/responses"):
            if self.post_error:
                raise self.post_error
            return {"id": "resp_test1234", "status": "queued"}
        if method == "GET" and "/responses/" in url:
            if self.responses:
                nxt = self.responses.pop(0)
                return nxt if nxt is not None else self.response
            return self.response
        raise AssertionError("UNEXPECTED_HTTP " + method + " " + url)

    def count(self, method, suffix):
        return sum(1 for c in self.calls if c[0] == method and c[1].endswith(suffix))


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.out = self.tmp / "out"
        ledger = json.loads(CANONICAL_LEDGER.read_text())
        ledger["astra_mission_reservations"] = [reservation()]
        self.ledger = self.tmp / "ledger.json"
        self.ledger.write_text(json.dumps(ledger))
        self.patches = [mock.patch.object(m, "LEDGER", self.ledger)]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)

    def env(self, ev=None, **over):
        path = self.tmp / "event.json"
        path.write_text(json.dumps(ev if ev is not None else event()))
        values = {"GITHUB_EVENT_NAME": "issue_comment", "GITHUB_ACTOR": "Donh91", "GITHUB_REPOSITORY": m.REPO,
                  "GITHUB_REF": "refs/heads/main", "GITHUB_RUN_ATTEMPT": "1", "GITHUB_EVENT_PATH": str(path),
                  "GITHUB_SHA": checkout_head(), "GITHUB_RUN_ID": "123456", "GITHUB_TOKEN": "dummy", "OPENAI_API_KEY": "dummy"}
        values.update(over)
        return mock.patch.dict(os.environ, values, clear=False)

    def guard_pass(self, mid=MID, **over):
        g = {"status": "PASS", "owner_astra_mission_id": mid, "new_request_reserved_upper_usd": 0,
             "owner_global_remaining_usd_after_risk": 30.0, "owner_global_reserve_usd": 4.0,
             "pending_liability_upper_usd": 43.0, "fail_closed": True}
        g.update(over)
        path = self.tmp / "guard.json"
        path.write_text(json.dumps(g))
        return path

    def run_to_claim(self, api):
        with self.env(), mock.patch.object(m.core, "http_json", api):
            m.prepare(self.out, preview=False)
            m.reserve(self.out, self.guard_pass())


class TestRequest(Base):
    def test_preview_exact_repeatable_and_offline(self):
        with mock.patch.object(m.core, "http_json", side_effect=AssertionError("NETWORK_FORBIDDEN")):
            a = m.build_request(MID)
            self.assertEqual(a, m.build_request(MID))
        req, data, meta = a
        self.assertEqual(req["model"], "gpt-6.2-astra")
        self.assertEqual(req["reasoning"], {"effort": "max"})
        self.assertEqual(req["max_output_tokens"], 128000)
        self.assertNotIn("tools", req)
        self.assertEqual(meta["bundle_sha256"], BUNDLE_SHA)
        self.assertEqual(meta["request_sha256"], m.digest(data))
        self.assertLessEqual(meta["worst_case_usd"], meta["max_usd"])
        self.assertEqual(meta["max_usd"], 20)

    def test_preview_stdout_is_wire_bytes(self):
        class Capture:
            buffer = io.BytesIO()
        with mock.patch.object(m.sys, "stdout", Capture()) as out, contextlib.redirect_stderr(io.StringIO()), \
                mock.patch.object(m.core, "http_json", side_effect=AssertionError("NETWORK_FORBIDDEN")):
            m.prepare(self.out, preview=True, mission_id=MID)
        self.assertEqual((self.out / "request.json").read_bytes(), out.buffer.getvalue())

    def test_preview_all_lists_trigger(self):
        with contextlib.redirect_stdout(io.StringIO()):
            m.preview_all(self.out)
        rows = json.loads((self.out / "preview_all.json").read_text())
        expected_ids = sorted(p.name for p in m.MISSIONS.iterdir() if p.is_dir())
        self.assertEqual([row["mission_id"] for row in rows], expected_ids)
        self.assertEqual(len(expected_ids), len(set(expected_ids)))
        selected = {row["mission_id"]: row for row in rows}
        self.assertIn(MID, selected)
        self.assertEqual(selected[MID]["trigger"], trigger())
        for mission_id, row in selected.items():
            mission = json.loads((m.MISSIONS / mission_id / "mission.json").read_text())
            self.assertEqual(row["trigger"], f"OWNER_LAUNCH_ASTRA_MISSION {mission_id} {mission['bundle_sha256']}")

    def test_model_only_from_verified_policy(self):
        policy = json.loads(m.POLICY.read_text())
        for mutate in (lambda p: p["manual_research_preference"].update(id="gpt-6-astra"),
                       lambda p: p["manual_research_preference"].update(standard_output_usd_per_million=1),
                       lambda p: p["manual_research_preference"].update(requires_new_owner_bound_mission=False),
                       lambda p: p["forbidden_auto_models"].remove("gpt-6.2-astra")):
            bad = copy.deepcopy(policy)
            mutate(bad)
            path = self.tmp / "policy.json"
            path.write_text(json.dumps(bad))
            with mock.patch.object(m, "POLICY", path), self.assertRaisesRegex(ValueError, "MODEL_POLICY"):
                m.model_policy()

    def test_mission_contract_and_cost_cap(self):
        mission = json.loads((ROOT / m.MISSIONS_REL / MID / "mission.json").read_text())
        self.assertEqual(mission["bundle_sha256"], BUNDLE_SHA)
        for key, value, reason in (("model", "gpt-6-astra", "MISSION_CONTRACT"),
                                   ("max_usd", 26, "MISSION_BOUNDS"), ("max_usd", 1, "COST_CAP"),
                                   ("bundle_file", "../x.md", "FILE_NAME"), ("bundle_file", "a/b.md", "FILE_NAME"),
                                   ("tools", [], "MISSION_CONTRACT")):
            bad = dict(mission, **{key: value})
            raw = json.dumps(bad).encode()
            real = m.tracked_bytes
            with mock.patch.object(m, "tracked_bytes",
                                   side_effect=lambda rel: raw if rel.endswith("mission.json") else real(rel)), \
                    self.assertRaisesRegex(ValueError, reason):
                m.build_request(MID)

    def test_untracked_or_modified_file_rejected(self):
        with self.assertRaisesRegex(ValueError, "UNSAFE_OR_MISSING|NOT_TRACKED"):
            m.tracked_bytes(m.MISSIONS_REL + "/" + MID + "/nope.md")
        with self.assertRaisesRegex(ValueError, "UNSAFE_OR_MISSING"):
            m.tracked_bytes("AGENTS.md")

    def test_existing_astra_missions_byte_identical(self):
        for mid, want in ASTRA_REQUEST_SHA.items():
            req, data, meta = m.build_request(mid)
            self.assertEqual((m.digest(data), req["model"], meta["model"]), (want, m.MODEL, m.MODEL), mid)
            self.assertEqual(meta["model_policy"]["id"], m.MODEL)

    def test_rerouted_sol_missions_pinned(self):
        for mid, want in SOL_REQUEST_SHA.items():
            req, data, meta = m.build_request(mid)
            self.assertEqual((m.digest(data), req["model"], meta["model"]), (want, m.SOL_MODEL, m.SOL_MODEL), mid)
            self.assertLessEqual(meta["worst_case_usd"], 3)

    def test_sol_mission_request(self):
        with mock.patch.object(m.core, "http_json", side_effect=AssertionError("NETWORK_FORBIDDEN")):
            req, data, meta = m.build_request(SOL_MID)
        self.assertEqual((req["model"], req["reasoning"], req["max_output_tokens"]), ("gpt-6.2-sol", {"effort": "max"}, 128000))
        self.assertNotIn("tools", req)
        self.assertEqual((meta["model"], meta["model_policy"]["id"], meta["max_usd"]), ("gpt-6.2-sol", "gpt-6.2-sol", 3))
        self.assertEqual(meta["bundle_sha256"], BUNDLE_SHA)
        self.assertEqual(meta["worst_case_usd"], round(m.estimate_cost("gpt-6.2-sol", len(data) + 20_000, 128000), 6))
        self.assertLessEqual(meta["worst_case_usd"], 3)
        sol_dir, r2_dir = ROOT / m.MISSIONS_REL / SOL_MID, ROOT / m.MISSIONS_REL / MID
        for name in ("BUNDLE_R2.md", "MISSION_R2.md"):
            self.assertEqual((sol_dir / name).read_bytes(), (r2_dir / name).read_bytes())
        # the same mission text as R2 except the mission id and the model
        r2_req = m.build_request(MID)[0]
        self.assertEqual(req["input"][0]["content"][0]["text"],
                         r2_req["input"][0]["content"][0]["text"].replace("Mission " + MID + ".", "Mission " + SOL_MID + ".", 1))

    def test_unknown_or_unverified_model_refused(self):
        mission = json.loads((ROOT / m.MISSIONS_REL / SOL_MID / "mission.json").read_text())
        real = m.tracked_bytes
        for model in ("gpt-6.1-sol", "gpt-6-astra", "gpt-6.2-sol-2026-11-01", "GPT-6.2-SOL", "", None, ["gpt-6.2-sol"], 1):
            raw = json.dumps(dict(mission, model=model)).encode()
            with mock.patch.object(m, "tracked_bytes",
                                   side_effect=lambda rel: raw if rel.endswith("mission.json") else real(rel)), \
                    self.assertRaisesRegex(ValueError, "MISSION_CONTRACT"):
                m.build_request(SOL_MID)
        with self.assertRaisesRegex(ValueError, "MODEL_NOT_ALLOWED"):
            m.model_policy("gpt-6.1-sol")
        # no "model": the Astra default applies (its cost then exceeds the USD3 cap and fails closed)
        raw = json.dumps({k: v for k, v in mission.items() if k != "model"}).encode()
        with mock.patch.object(m, "tracked_bytes", side_effect=lambda rel: raw if rel.endswith("mission.json") else real(rel)):
            self.assertEqual(m.mission_model(json.loads(raw)), m.MODEL)
            with self.assertRaisesRegex(ValueError, "COST_CAP"):
                m.build_request(SOL_MID)

    def test_sol_policy_must_verify(self):
        policy = json.loads(m.POLICY.read_text())
        def sol(p):
            return next(r for r in p["available_verified_sol_models"] if r["id"] == "gpt-6.2-sol")
        newer = {**copy.deepcopy(sol(policy)), "id": "gpt-6.3-sol", "version": [6, 3]}
        for mutate in (lambda p: sol(p).update(verified_available=False),
                       lambda p: sol(p).update(standard_output_usd_per_million=9),
                       lambda p: sol(p).update(standard_input_usd_per_million=1),
                       lambda p: sol(p).update(standard_cache_write_12h_usd_per_million=2.5),
                       lambda p: sol(p).update(long_context_input_multiplier=1),
                       lambda p: sol(p).update(official_model_spec="https://example.com/gpt-6.2-sol"),
                       lambda p: sol(p).update(max_output_tokens=64000),
                       lambda p: p["available_verified_sol_models"].append(copy.deepcopy(newer)),
                       lambda p: p["forbidden_auto_models"].append("gpt-6.2-sol"),
                       lambda p: p.update(owner_issue=1)):
            bad = copy.deepcopy(policy)
            mutate(bad)
            path = self.tmp / "policy.json"
            path.write_text(json.dumps(bad))
            with mock.patch.object(m, "POLICY", path), self.assertRaisesRegex(ValueError, "SOL_MODEL_POLICY"):
                m.model_policy("gpt-6.2-sol")
        with mock.patch.dict(m.PRICES_PER_MILLION, {"gpt-6.2-sol": {"input": 2.0, "output": 12.0}}), \
                self.assertRaisesRegex(ValueError, "SOL_MODEL_POLICY"):
            m.model_policy("gpt-6.2-sol")
        self.assertEqual(m.model_policy("gpt-6.2-sol")["id"], "gpt-6.2-sol")


class TestTrigger(Base):
    def assert_rejected(self, ev=None, reason="EXACT_OWNER_TRIGGER_REQUIRED", **env):
        with self.env(ev, **env), mock.patch.object(m.core, "http_json", side_effect=AssertionError("NET")), \
                self.assertRaisesRegex(ValueError, reason):
            m.prepare(self.out, preview=False)
        self.assertFalse((self.out / "request.json").exists())

    def test_exact_trigger_accepted_and_offline(self):
        with self.env(), mock.patch.object(m.core, "http_json", side_effect=AssertionError("NET")):
            m.prepare(self.out, preview=False)
        self.assertEqual((self.out / "guard_mission_id.txt").read_text(), MID)
        self.assertEqual(json.loads((self.out / "source_manifest.json").read_text())["trigger_comment_id"], 777)

    def test_wrong_author(self):
        self.assert_rejected(event(login="Donh92"))
        self.assert_rejected(event(author_association="COLLABORATOR"))
        self.assert_rejected(event(type="Bot"))
        self.assert_rejected(reason="NATIVE_OWNER_EVENT", GITHUB_ACTOR="someone")

    def test_wrong_issue_event_or_attempt(self):
        self.assert_rejected(event(issue_number=937))
        self.assert_rejected(event(pull_request={"url": "x"}))
        self.assert_rejected(event(action="edited"))
        self.assert_rejected(reason="NATIVE_OWNER_EVENT", GITHUB_EVENT_NAME="pull_request")
        self.assert_rejected(reason="NATIVE_OWNER_EVENT", GITHUB_RUN_ATTEMPT="2")
        self.assert_rejected(reason="NATIVE_OWNER_EVENT", GITHUB_REF="refs/heads/feature")
        self.assert_rejected(reason="LIVE_CHECKOUT_SHA_MISMATCH", GITHUB_SHA="0" * 40)

    def test_wrong_body(self):
        for body in (trigger() + "\n", trigger() + " ", " " + trigger(), trigger().lower(),
                     trigger().replace("MISSION ", "MISSION  ", 1), "OWNER_LAUNCH_ASTRA_MISSION " + MID,
                     trigger() + " extra", "OWNER_LAUNCH_ASTRA_MISSIONS " + MID + " " + BUNDLE_SHA,
                     trigger(sha=BUNDLE_SHA.upper()), trigger(sha=BUNDLE_SHA[:63])):
            self.assert_rejected(event(body=body))

    def test_wrong_sha(self):
        self.assert_rejected(event(body=trigger(sha="a" * 64)), reason="COMMENT_BUNDLE_SHA_MISMATCH")

    def test_unknown_mission(self):
        self.assert_rejected(event(body=trigger(mid="ASTRA-NOT-THERE-1")), reason="MISSION_UNKNOWN")

    def test_path_traversal(self):
        for mid in ("ASTRA-../../etc", "ASTRA-X/../../scripts", "ASTRA-..", "ASTRA-a-b", "ASTRA-X--Y", "ASTRA-",
                    "ASTRA-X-" + "Y" * 25, "astra-s1-x"):
            self.assert_rejected(event(body=trigger(mid=mid)), reason="EXACT_OWNER_TRIGGER|MISSION_ID_INVALID")
        for mid in ("ASTRA-../../etc", "../x", "ASTRA-X/Y-Z", "ASTRA-X\x00-Y"):
            with self.assertRaisesRegex(ValueError, "MISSION_ID_INVALID"):
                m.mission_rel(mid)

    def test_symlinked_mission_rejected(self):
        link = ROOT / m.MISSIONS_REL / "ASTRA-LINK-TEST-1"
        link.symlink_to(ROOT / "scripts")
        self.addCleanup(link.unlink)
        with self.assertRaisesRegex(ValueError, "MISSION_PATH_ESCAPE"):
            m.mission_rel("ASTRA-LINK-TEST-1")

    def test_missing_or_mismatched_reservation(self):
        ledger = json.loads(self.ledger.read_text())
        ledger["astra_mission_reservations"] = [reservation(upper=19)]
        self.ledger.write_text(json.dumps(ledger))
        self.assert_rejected(reason="MISSION_RESERVATION_MISMATCH")
        del ledger["astra_mission_reservations"]
        self.ledger.write_text(json.dumps(ledger))
        self.assert_rejected(reason="MISSION_RESERVATION_REQUIRED")

    def test_consumed_reservation_refused(self):
        # R2-1: a CONSUMED_PENDING_INVOICE row is counted by the guard but never launches again.
        ledger = json.loads(self.ledger.read_text())
        ledger["astra_mission_reservations"] = [consumed_row()]
        self.ledger.write_text(json.dumps(ledger))
        with self.assertRaisesRegex(ValueError, "MISSION_RESERVATION_MISMATCH"):
            m.check_reservation(MID, 20)
        self.assert_rejected(reason="MISSION_RESERVATION_MISMATCH")
        self.assertFalse((self.out / "guard_mission_id.txt").exists())


class TestClaimAndNoRetry(Base):
    def test_full_offline_flow_one_post(self):
        api = FakeAPI()
        self.run_to_claim(api)
        with self.env(), mock.patch.object(m.core, "http_json", api), contextlib.redirect_stdout(io.StringIO()):
            m.mark_attempt(self.out)
            m.submit(self.out)
            self.assertEqual(m.collect(self.out, sleep=lambda s: None), 0)
            m.report(self.out)
        self.assertEqual(api.count("POST", "/responses"), 1)
        results = self.out / "archive" / m.MISSIONS_REL / MID / "results"
        self.assertEqual((results / "ASTRA_RAW_REPORT.md").read_bytes(), b"# report\nbody\n")
        self.assertEqual((results / "receipt.json").read_bytes(), (self.out / "receipt.json").read_bytes())
        self.assertIn(m.digest(b"# report\nbody\n") + "  ASTRA_RAW_REPORT.md", (results / "SHA256SUMS").read_text())
        posted = [c[2]["body"] for c in api.calls if c[0] == "POST" and c[1].endswith("/comments")]
        self.assertTrue(posted[0].startswith(m.CLAIM_PREFIX + MID + " run=123456"))
        self.assertEqual(posted[1], m.handle_body(MID, "123456", "resp_test1234", json.loads(
            (self.out / "claim.json").read_text())["request_sha256"]))
        self.assertTrue(posted[2].startswith(m.RESULT_PREFIX + MID + " run=123456 stage=COLLECTED status=completed"))
        self.assertNotIn("report\nbody", posted[2])

    def test_claim_reuse_blocks_before_any_model_call(self):
        prior = {"id": 1, "body": m.claim_body(MID, "999", "f" * 64), "user": {"login": "github-actions[bot]"}}
        api = FakeAPI(comments=[prior])
        with self.assertRaisesRegex(ValueError, "ALREADY_CLAIMED"):
            self.run_to_claim(api)
        self.assertEqual(api.count("GET", "/models/" + m.MODEL), 0)
        self.assertEqual(api.count("POST", "/responses"), 0)
        self.assertFalse((self.out / "claim.json").exists())

    def test_claim_on_later_page_found(self):
        filler = [{"id": i, "body": "x", "user": {"login": "Donh91"}} for i in range(150)]
        prior = {"id": 500, "body": m.claim_body(MID, "1", "0" * 64), "user": {"login": "github-actions[bot]"}}
        with self.assertRaisesRegex(ValueError, "ALREADY_CLAIMED"):
            self.run_to_claim(FakeAPI(comments=filler + [prior]))

    def test_forged_non_bot_claim_ignored_and_other_mission_ignored(self):
        forged = {"id": 1, "body": m.claim_body(MID, "1", "0" * 64), "user": {"login": "Donh91"}}
        other = {"id": 2, "body": m.claim_body(MID + "X", "1", "0" * 64), "user": {"login": "github-actions[bot]"}}
        api = FakeAPI(comments=[forged, other])
        self.run_to_claim(api)
        self.assertTrue((self.out / "claim.json").exists())

    def test_concurrent_claim_loses(self):
        api = FakeAPI()
        real_post = api.__call__

        def racing(method, url, **kw):
            row = real_post(method, url, **kw)
            if method == "POST" and url.endswith("/comments") and len(api.comments) == 1:
                api.comments.insert(0, {"id": 5, "body": m.claim_body(MID, "222", "e" * 64),
                                        "user": {"login": "github-actions[bot]"}})
            return row
        with self.env(), mock.patch.object(m.core, "http_json", side_effect=racing):
            m.prepare(self.out, preview=False)
            with self.assertRaisesRegex(ValueError, "NOT_UNIQUE"):
                m.reserve(self.out, self.guard_pass())
        self.assertFalse((self.out / "claim.json").exists())

    def test_no_retry_second_submit_and_second_attempt_fail(self):
        api = FakeAPI()
        self.run_to_claim(api)
        with self.env(), mock.patch.object(m.core, "http_json", api), contextlib.redirect_stdout(io.StringIO()):
            m.mark_attempt(self.out)
            with self.assertRaises(FileExistsError):
                m.mark_attempt(self.out)
            m.submit(self.out)
            with self.assertRaises(FileExistsError):
                m.submit(self.out)
        self.assertEqual(api.count("POST", "/responses"), 1)

    def test_no_retry_after_post_error(self):
        api = FakeAPI(post_error=RuntimeError("HTTP_500_POST"))
        self.run_to_claim(api)
        with self.env(), mock.patch.object(m.core, "http_json", api):
            m.mark_attempt(self.out)
            with self.assertRaises(RuntimeError):
                m.submit(self.out)
            with self.assertRaises(FileExistsError):
                m.submit(self.out)
        self.assertEqual(api.count("POST", "/responses"), 1)
        self.assertFalse((self.out / "handle.json").exists())
        with self.env(), mock.patch.object(m.core, "http_json", api), contextlib.redirect_stdout(io.StringIO()):
            m.report(self.out)
        self.assertIn("stage=POST_OUTCOME_UNKNOWN", api.calls[-1][2]["body"])

    def test_submit_requires_attempt_marker_and_claim(self):
        api = FakeAPI()
        with self.env(), mock.patch.object(m.core, "http_json", api):
            m.prepare(self.out, preview=False)
            with self.assertRaises(FileNotFoundError):
                m.submit(self.out)
        self.assertEqual(api.count("POST", "/responses"), 0)

    def test_drift_after_prepare_blocks(self):
        api = FakeAPI()
        with self.env(), mock.patch.object(m.core, "http_json", api):
            m.prepare(self.out, preview=False)
        (self.out / "request.json").write_bytes(b"{}\n")
        with self.env(), mock.patch.object(m.core, "http_json", api), self.assertRaisesRegex(ValueError, "DRIFT"):
            m.reserve(self.out, self.guard_pass())
        self.assertEqual(api.count("POST", "/comments"), 0)

    def test_guard_result_must_pass_for_this_mission(self):
        for over in ({"status": "BLOCKED"}, {"owner_astra_mission_id": None}, {"pending_liability_upper_usd": 5},
                     {"owner_global_remaining_usd_after_risk": 3.9}, {"new_request_reserved_upper_usd": 1}):
            api = FakeAPI()
            out = self.tmp / ("o" + str(len(os.listdir(self.tmp))))
            with self.env(), mock.patch.object(m.core, "http_json", api):
                m.prepare(out, preview=False)
                with self.assertRaisesRegex(ValueError, "SHARED_COST_GUARD_BLOCKED"):
                    m.reserve(out, self.guard_pass(**over))
            self.assertEqual(api.calls, [])

    def test_every_poll_uses_the_real_api_key(self):
        # Regression (Claude review #2225 P1): a loop variable once shadowed the API key after the first GET.
        api = FakeAPI(responses=[{"id": "resp_test1234", "model": m.MODEL, "status": "in_progress"},
                                 {"id": "resp_test1234", "model": m.MODEL, "status": "in_progress"}, None])
        self.run_to_claim(api)
        with self.env(), mock.patch.object(m.core, "http_json", api), contextlib.redirect_stdout(io.StringIO()):
            want = os.environ["OPENAI_API_KEY"]
            m.mark_attempt(self.out)
            m.submit(self.out)
            m.collect(self.out, sleep=lambda s: None, clock=lambda: 0)
        polls = [k for meth, url, k in api.keys if meth == "GET" and "/responses/" in url]
        self.assertGreaterEqual(len(polls), 3)
        self.assertEqual(set(polls), {want})

    def test_collect_pending_and_identity(self):
        api = FakeAPI(response={"id": "resp_test1234", "model": m.MODEL, "status": "in_progress"})
        self.run_to_claim(api)
        ticks = iter(range(0, 10 ** 6, 600))
        with self.env(), mock.patch.object(m.core, "http_json", api), contextlib.redirect_stdout(io.StringIO()):
            m.mark_attempt(self.out)
            m.submit(self.out)
            self.assertEqual(m.collect(self.out, sleep=lambda s: None, clock=lambda: next(ticks)), 2)
        self.assertTrue((self.out / "pending.json").exists())
        self.assertEqual(api.count("POST", "/responses"), 1)
        for model, ok in (("gpt-6.2-astra-2026-11-01", True), ("gpt-6.2-sol", False), ("gpt-6-astra", False)):
            self.assertEqual(bool(m.PROVIDER_MODEL.fullmatch(model)), ok)

    def test_result_comment_or_claim_artifact_also_consumes(self):
        result = {"id": 3, "body": m.RESULT_PREFIX + MID + " run=1 stage=NO_POST", "user": {"login": "github-actions[bot]"}}
        for api in (FakeAPI(comments=[result]), FakeAPI(artifacts=1)):
            out = self.tmp / ("c" + str(len(os.listdir(self.tmp))))
            with self.env(), mock.patch.object(m.core, "http_json", api):
                m.prepare(out, preview=False)
                with self.assertRaisesRegex(ValueError, "ALREADY_CLAIMED"):
                    m.reserve(out, self.guard_pass())
            self.assertEqual(api.count("POST", "/comments"), 0)
            self.assertEqual(api.count("POST", "/responses"), 0)

    def test_claim_artifact_name_output(self):
        gh_out = self.tmp / "gh_output"
        with self.env(GITHUB_OUTPUT=str(gh_out)), mock.patch.object(m.core, "http_json", side_effect=AssertionError):
            m.prepare(self.out, preview=False)
            m.claim_artifact_output(self.out)
        self.assertEqual(gh_out.read_text(), "claim_artifact=astra-mission-claim-" + MID + "\n")

    def test_receipt_written_without_usage_counts_full_reservation(self):
        api = FakeAPI(response={"id": "resp_test1234", "model": m.MODEL, "status": "failed", "output": []})
        self.run_to_claim(api)
        with self.env(), mock.patch.object(m.core, "http_json", api), contextlib.redirect_stdout(io.StringIO()):
            m.mark_attempt(self.out)
            m.submit(self.out)
            self.assertEqual(m.collect(self.out, sleep=lambda s: None), 3)
        receipt = json.loads((self.out / "receipt.json").read_text())
        self.assertEqual((receipt["usage"], receipt["usage_valid"], receipt["estimated_upper_usd"]), (None, False, 20.0))

    def test_recover_is_get_only_and_needs_one_claim(self):
        api = FakeAPI(response={"id": "resp_test1234", "model": m.MODEL, "status": "in_progress"})
        self.run_to_claim(api)
        with self.env(), mock.patch.object(m.core, "http_json", api), contextlib.redirect_stdout(io.StringIO()):
            m.mark_attempt(self.out)
            m.submit(self.out)
        claim_rows = list(api.comments)
        rec_ok = FakeAPI(comments=claim_rows)
        rec_ok.response["id"] = "resp_test1234"
        body = "OWNER_COLLECT_ASTRA_MISSION " + MID + " resp_test1234"
        rec = rec_ok
        out = self.tmp / "rec"
        with self.env(event(body=body), GITHUB_RUN_ID="777777"), mock.patch.object(m.core, "http_json", rec), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(m.recover(out), 0)
            m.report(out)
        self.assertEqual(rec.count("POST", "/responses"), 0)
        self.assertIn("stage=COLLECTED", rec.calls[-1][2]["body"])
        self.assertTrue((out / "archive" / m.MISSIONS_REL / MID / "results" / "ASTRA_RAW_REPORT.md").exists())
        # an unbound response id is refused (the handle comment names resp_test1234)
        unbound = "OWNER_COLLECT_ASTRA_MISSION " + MID + " resp_other9999"
        with self.env(event(body=unbound)), mock.patch.object(m.core, "http_json", FakeAPI(comments=claim_rows)), \
                self.assertRaisesRegex(ValueError, "NOT_BOUND_TO_CLAIM"):
            m.recover(self.tmp / "unbound")
        no_handle = [r for r in claim_rows if not r["body"].startswith(m.HANDLE_PREFIX)]
        with self.env(event(body=body)), mock.patch.object(m.core, "http_json", FakeAPI(comments=no_handle)), \
                self.assertRaisesRegex(ValueError, "NOT_BOUND_TO_CLAIM"):
            m.recover(self.tmp / "nohandle")
        # a second recovery after a COLLECTED result, or without any claim, is refused
        for rows in (rec.comments, []):
            with self.env(event(body=body)), mock.patch.object(m.core, "http_json", FakeAPI(comments=rows)), \
                    self.assertRaisesRegex(ValueError, "RECOVERY_NEEDS_ONE_CLAIM"):
                m.recover(self.tmp / ("r" + str(len(os.listdir(self.tmp)))))
        for bad in (body + "\n", "OWNER_COLLECT_ASTRA_MISSION " + MID + " resp_x/../y"):
            with self.env(event(body=bad)), mock.patch.object(m.core, "http_json", side_effect=AssertionError), \
                    self.assertRaisesRegex(ValueError, "RECOVERY_TRIGGER"):
                m.recover(self.tmp / "bad")
        with self.env(event(body=body, login="Donh92")), mock.patch.object(m.core, "http_json", side_effect=AssertionError), \
                self.assertRaisesRegex(ValueError, "RECOVERY_TRIGGER"):
            m.recover(self.tmp / "bad2")

    def test_collect_rejects_other_parameters(self):
        for extra in ({"max_output_tokens": 1000}, {"reasoning": {"effort": "high"}}):
            api = FakeAPI()
            api.response = dict(api.response, **extra)
            out_dir = self.tmp / ("p" + str(len(os.listdir(self.tmp))))
            self.out = out_dir
            self.run_to_claim(api)
            with self.env(), mock.patch.object(m.core, "http_json", api), contextlib.redirect_stdout(io.StringIO()):
                m.mark_attempt(out_dir)
                m.submit(out_dir)
                with self.assertRaisesRegex(ValueError, "PARAMETERS_MISMATCH"):
                    m.collect(out_dir, sleep=lambda s: None)

    def test_report_without_claim_posts_nothing(self):
        with self.env(), mock.patch.object(m.core, "http_json", side_effect=AssertionError("NET")), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(m.report(self.out), 0)


class TestSolMission(Base):
    """A Sol mission uses its own model in the provider GET, the POST body, the identity check and the receipt."""
    def setUp(self):
        super().setUp()
        ledger = json.loads(self.ledger.read_text())
        ledger["astra_mission_reservations"] = [reservation(SOL_MID, 3)]
        self.ledger.write_text(json.dumps(ledger))

    def sol_env(self):
        return self.env(event(body=trigger(mid=SOL_MID)))

    def run_sol(self, api):
        with self.sol_env(), mock.patch.object(m.core, "http_json", api), contextlib.redirect_stdout(io.StringIO()):
            m.prepare(self.out, preview=False)
            m.reserve(self.out, self.guard_pass(mid=SOL_MID))
            m.mark_attempt(self.out)
            m.submit(self.out)
            return m.collect(self.out, sleep=lambda s: None)

    def test_full_sol_flow(self):
        api = FakeAPI(model="gpt-6.2-sol", mid=SOL_MID)
        self.assertEqual(self.run_sol(api), 0)
        self.assertEqual(api.count("GET", "/models/gpt-6.2-sol"), 1)
        self.assertEqual(api.count("GET", "/models/" + m.MODEL), 0)
        posted = [c[2] for c in api.calls if c[0] == "POST" and c[1].endswith("/responses")]
        self.assertEqual(len(posted), 1)
        self.assertEqual((posted[0]["model"], posted[0]["reasoning"]), ("gpt-6.2-sol", {"effort": "max"}))
        receipt = json.loads((self.out / "receipt.json").read_text())
        self.assertEqual((receipt["model"], receipt["provider_model"], receipt["owner_reserved_usd"]),
                         ("gpt-6.2-sol", "gpt-6.2-sol", 3))
        self.assertEqual(receipt["estimated_upper_usd"], m.estimate_cost("gpt-6.2-sol", 90000, 30000))

    def test_sol_provider_model_mismatch_refused(self):
        for reported in (m.MODEL, "gpt-6.1-sol", "gpt-6.2-sol-mini", None):
            api = FakeAPI(model="gpt-6.2-sol", mid=SOL_MID)
            api.response = dict(api.response, model=reported)
            self.out = self.tmp / ("s" + str(len(os.listdir(self.tmp))))
            with self.assertRaisesRegex(ValueError, "PROVIDER_RESPONSE_IDENTITY_MISMATCH"):
                self.run_sol(api)
            self.assertEqual(api.count("POST", "/responses"), 1)
            self.assertFalse((self.out / "receipt.json").exists())
        dated = FakeAPI(model="gpt-6.2-sol", mid=SOL_MID)
        dated.response = dict(dated.response, model="gpt-6.2-sol-2026-11-18")
        self.out = self.tmp / "dated"
        self.assertEqual(self.run_sol(dated), 0)

    def test_sol_provider_get_must_name_sol(self):
        api = FakeAPI(model="gpt-6.2-sol", mid=SOL_MID)
        real = api.__call__

        def wrong(method, url, **kw):
            if method == "GET" and url.endswith("/models/gpt-6.2-sol"):
                return {"id": m.MODEL}
            return real(method, url, **kw)
        with self.sol_env(), mock.patch.object(m.core, "http_json", side_effect=wrong):
            m.prepare(self.out, preview=False)
            with self.assertRaisesRegex(ValueError, "PROVIDER_MODEL_NOT_VERIFIED"):
                m.reserve(self.out, self.guard_pass(mid=SOL_MID))
        self.assertEqual(api.count("POST", "/comments"), 0)


class TestCostGuard(unittest.TestCase):
    """The shared guard counts each mission reservation and admits only its own mission."""
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        (self.tmp / "receipts").mkdir()
        self.base = json.loads(CANONICAL_LEDGER.read_text())
        # Fixture rows are explicit per test; the canonical mission row is pinned in test_canonical_mission_row.
        self.base.pop("astra_mission_reservations", None)
        # The canonical rows as they are: settled/consumed rows hold nothing, active rows count in full.
        self.stop = self.base["absolute_budget_usd"]

    def guard(self, rows, *extra, hard_stop=None):
        ledger = dict(self.base)
        if rows is not None:
            ledger["astra_mission_reservations"] = rows
        path = self.tmp / "ledger.json"
        path.write_text(json.dumps(ledger))
        proc = subprocess.run([sys.executable, str(GUARD), "--receipt-root", str(self.tmp / "receipts"),
                               "--hard-stop-usd", str(hard_stop or self.stop), "--reserve-usd", "4",
                               "--new-request-upper-usd", "0", "--liability-ledger", str(path), *extra],
                              capture_output=True, text=True, cwd=ROOT, timeout=120)
        return proc.returncode, json.loads(proc.stdout)

    def test_canonical_mission_row(self):
        rows = json.loads(CANONICAL_LEDGER.read_text()).get("astra_mission_reservations", [])
        self.assertEqual([(r["work_id"], r["status"], r["lower_usd"], r["upper_usd"], r["one_paid_post_max"]) for r in rows],
                         [("ASTRA-S1-V32-REDTEAM-20261118-R2", "CONSUMED_PENDING_INVOICE", 0, 20, 1),
                          ("ASTRA-ALPHA-GLOBAL-SPECIALIST-20261118", "OWNER_RESERVED_PREHTTP", 0, 3, 1),
                          ("ASTRA-S1-V32-REDTEAM-20261118-R2-SOL", "CONSUMED_PENDING_INVOICE", 0, 3, 1),
                          ("ASTRA-NAVIGATOR-ONE-KOMPAS2-20261118", "OWNER_RESERVED_PREHTTP", 0, 20, 1),
                          ("ASTRA-NAVIGATOR-ONE-KOMPAS2-20261118-SOL", "OWNER_RESERVED_PREHTTP", 0, 3, 1),
                          ("ASTRA-NAVIGATOR-APP-ARCH-20261119-SOL", "OWNER_RESERVED_PREHTTP", 0, 3, 1),
                          ("ASTRA-NAVIGATOR-APP-WALLET-20261119-SOL", "OWNER_RESERVED_PREHTTP", 0, 3, 1),
                          ("ASTRA-NAVIGATOR-APP-REG-20261119-SOL", "OWNER_RESERVED_PREHTTP", 0, 3, 1),
                          ("ASTRA-S1-SUPERVISOR-EVOLUTION-20261119-SOL", "OWNER_RESERVED_PREHTTP", 0, 3, 1)])
        self.assertEqual((rows[0]["consumed_run_id"], rows[0]["consumed_response_id"],
                          rows[0]["consumed_estimated_upper_usd"]),
                         (44386340009, "resp_0477227a70790153006afe044ec9c487d08ebd44a0466687db", 3.13212))
        self.assertEqual(res.mission_reservations(json.loads(CANONICAL_LEDGER.read_text()), set())[:2], (61.0, 9))
        for mid in (ALPHA_MID, SOL_MID):
            proc = subprocess.run([sys.executable, str(GUARD), "--receipt-root", str(self.tmp / "receipts"),
                                   "--hard-stop-usd", str(self.stop), "--reserve-usd", "4", "--new-request-upper-usd", "0",
                                   "--liability-ledger", str(CANONICAL_LEDGER), "--owner-astra-mission-id", mid],
                                  capture_output=True, text=True, cwd=ROOT, timeout=120)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertEqual(json.loads(proc.stdout)["pending_liability_upper_usd"], 61.0)
        # The consumed R2 row stays counted but can never launch again.
        with mock.patch.object(m, "LEDGER", CANONICAL_LEDGER), self.assertRaisesRegex(ValueError, "RESERVATION_MISMATCH"):
            m.check_reservation(MID, 20)
        # The consumed R2 and the consumed Sol A/B rows stay counted but can never launch again.
        with mock.patch.object(m, "LEDGER", CANONICAL_LEDGER), self.assertRaisesRegex(ValueError, "RESERVATION_MISMATCH"):
            m.check_reservation(SOL_MID, 3)
        with mock.patch.object(m, "LEDGER", CANONICAL_LEDGER):
            m.check_reservation(ALPHA_MID, 3)   # Alpha (rerouted to Sol, USD3) remains launchable once
            m.check_reservation("ASTRA-S1-SUPERVISOR-EVOLUTION-20261119-SOL", 3)  # newly admitted one-shot Sol research

    def test_consumed_row_still_counted_in_full(self):
        code, result = self.guard([consumed_row()], hard_stop=50)
        _, without = self.guard([], hard_stop=50)
        self.assertEqual(code, 0, result)
        self.assertEqual(result["pending_liability_upper_usd"], without["pending_liability_upper_usd"] + 20)
        self.assertEqual(res.mission_reservations({"astra_mission_reservations": [consumed_row()]}, set())[:2],
                         (20.0, 1))

    def test_consumed_rows_validated(self):
        for bad in (consumed_row(consumed_run_id="44386340009"), consumed_row(consumed_run_id=True),
                    consumed_row(consumed_run_id=0), consumed_row(consumed_response_id="chatcmpl_x"),
                    consumed_row(consumed_response_id=None), consumed_row(consumed_estimated_upper_usd=20.01),
                    consumed_row(consumed_estimated_upper_usd=0), consumed_row(consumed_estimated_upper_usd=float("inf")),
                    consumed_row(consumed_estimated_upper_usd="3"), consumed_row(status="CONSUMED"),
                    dict(reservation(), consumed_run_id=1)):
            with self.assertRaises(ValueError):
                res.mission_reservations({"astra_mission_reservations": [bad]}, set())
        for missing in ("consumed_run_id", "consumed_response_id", "consumed_estimated_upper_usd"):
            row = consumed_row()
            del row[missing]
            with self.assertRaises(ValueError):
                res.mission_reservations({"astra_mission_reservations": [row]}, set())

    def test_mission_passes_and_is_counted(self):
        code0, before = self.guard(None, "--owner-astra-mission-id", MID)
        self.assertNotEqual(code0, 0)          # no reservation row: blocked
        code, result = self.guard([reservation()], "--owner-astra-mission-id", MID)
        self.assertEqual(code, 0, result)
        self.assertEqual(result["owner_astra_mission_id"], MID)
        self.assertEqual(result["pending_liability_upper_usd"], before["pending_liability_upper_usd"] + 20)

    def test_mismatch_unknown_and_shape(self):
        self.assertNotEqual(self.guard([reservation(upper=19)], "--owner-astra-mission-id", MID)[0], 0)
        self.assertNotEqual(self.guard([reservation(mid="ASTRA-NOT-THERE-1")], "--owner-astra-mission-id", MID)[0], 0)
        self.assertNotEqual(self.guard([reservation(), reservation()], "--owner-astra-mission-id", MID)[0], 0)
        self.assertNotEqual(self.guard([reservation()], "--owner-astra-mission-id", "ASTRA-OTHER-1")[0], 0)
        self.assertNotEqual(self.guard([reservation()], "--owner-astra-mission-id", MID, hard_stop=50)[0], 0)
        self.assertNotEqual(self.guard([reservation()], "--owner-astra-mission-id", MID,
                                       "--owner-astra-program-work-id", "ASTRA-HIGH-S1-VNEXT-ARCHITECTURE-20261116-ONE")[0], 0)

    def test_routine_callers_still_count_mission_liability(self):
        code, result = self.guard([reservation()], hard_stop=50)
        _, without = self.guard([], hard_stop=50)
        self.assertEqual(result["pending_liability_upper_usd"], without["pending_liability_upper_usd"] + 20)
        self.assertEqual(result["owner_global_remaining_usd_after_risk"],
                         without["owner_global_remaining_usd_after_risk"] - 20)

    def test_hard_stop_cannot_be_exceeded(self):
        # A current-month receipt that leaves less than USD20 + USD4 reserve under the hard stop blocks the mission.
        import time
        spent = self.stop - 4 - 20 + 1
        (self.tmp / "receipts" / "r.json").write_text(json.dumps({
            "contract": "TEST_COST_RECEIPT", "task": "test", "run_id": "1", "estimated_cost_usd": spent,
            "created_unix": time.time()}))
        code, result = self.guard([reservation()], "--owner-astra-mission-id", MID)
        self.assertEqual(result["spent_usd"], spent, result)
        self.assertNotEqual(code, 0)
        self.assertEqual(result["status"], "BLOCKED")

    def test_reservation_rows_validated(self):
        for bad in (dict(reservation(), upper_usd=26), dict(reservation(), lower_usd=1),
                    dict(reservation(), source="https://example.com"), dict(reservation(), one_paid_post_max=2),
                    dict(reservation(), status="SETTLED"), dict(reservation(), extra=1),
                    dict(reservation(), work_id="../x"), dict(reservation(), upper_usd=float("nan"))):
            with self.assertRaises(ValueError):
                res.mission_reservations({"astra_mission_reservations": [bad]}, set())
        with self.assertRaises(ValueError):
            res.mission_reservations({"astra_mission_reservations": [reservation()]}, {MID})
        self.assertEqual(res.mission_reservations({"astra_mission_reservations": [reservation()]}, set())[:2], (20.0, 1))


class TestWorkflow(unittest.TestCase):
    def setUp(self):
        self.text = (ROOT / ".github/workflows/owner-astra-mission.yml").read_text()
        self.wf = yaml.safe_load(self.text)

    def test_secrets_only_in_paid_job_and_no_paid_path_on_pr(self):
        jobs = self.wf["jobs"]
        for name, job in jobs.items():
            dumped = json.dumps(job)
            self.assertEqual("secrets." in dumped, name in ("paid", "recover"), name)
        paid = jobs["paid"]
        self.assertNotIn("pull_request'", paid["if"].replace("pull_request == null", ""))
        self.assertIn("github.event_name == 'issue_comment'", paid["if"])
        self.assertIn("github.event.comment.user.login == 'Donh91'", paid["if"])
        self.assertIn("github.run_attempt == 1", paid["if"])
        self.assertEqual(paid["permissions"], {"contents": "read", "issues": "write", "actions": "read"})
        self.assertEqual(jobs["recover"]["permissions"], {"contents": "read", "issues": "write"})
        self.assertEqual(self.wf["permissions"], {"contents": "read"})
        self.assertEqual(jobs["offline"]["if"], "github.event_name == 'pull_request'")
        on = self.wf[True] if True in self.wf else self.wf["on"]
        self.assertEqual(on["issue_comment"], {"types": ["created"]})
        self.assertNotIn("pull_request_target", on)
        self.assertNotIn("workflow_dispatch", on)

    def test_paid_path_gate_conditions_are_exact(self):
        # Regression (Claude review #2225 P1): every guard on a job that can reach the paid key is pinned here,
        # so dropping or weakening one (e.g. replacing it with `true`) fails CI.
        common = ["github.event_name == 'issue_comment'", "github.event.action == 'created'",
                  "github.event.issue.number == 1156", "github.event.issue.pull_request == null",
                  "github.event.comment.user.login == 'Donh91'", "github.actor == 'Donh91'",
                  "github.event.comment.author_association == 'OWNER'", "github.ref == 'refs/heads/main'",
                  "github.run_attempt == 1"]
        want = {"verify": "OWNER_LAUNCH_ASTRA_MISSION ", "paid": "OWNER_LAUNCH_ASTRA_MISSION ",
                "recover": "OWNER_COLLECT_ASTRA_MISSION "}
        for name, prefix in want.items():
            parts = [p.strip() for p in self.wf["jobs"][name]["if"].split("&&")]
            self.assertEqual(parts, common + [f"startsWith(github.event.comment.body, '{prefix}')"], name)

    def test_comment_body_never_interpolated(self):
        for job in self.wf["jobs"].values():
            for step in job["steps"]:
                for value in (step.get("run", ""), json.dumps(step.get("env", {})), json.dumps(step.get("with", {}))):
                    self.assertNotIn("github.event.comment", value)
                    self.assertNotIn("github.event.issue.title", value)
                    self.assertNotIn("github.event.issue.body", value)
                if "uses" in step and step["uses"].startswith("actions/checkout"):
                    self.assertIs(step["with"]["persist-credentials"], False)


if __name__ == "__main__":
    unittest.main()
