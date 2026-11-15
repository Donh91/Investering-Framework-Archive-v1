"""Tests for the Claude-independent S1 and Vault watchdog (v2: structured receipt parsing)."""
import datetime as dt
import json
import unittest

from scripts.governance import s1_vault_watchdog_v1 as W

NOW = dt.datetime(2026, 11, 20, 6, 0, tzinfo=dt.timezone.utc)

# Verbatim body of a real VAULT_FINAL_REF_RECEIPT_v1 (Archive #1593 comment 6876185627, already public).
REAL_RECEIPT = "<!-- VAULT_FINAL_REF_RECEIPT_v1:43578373086-2 -->\nTechnical final-ref proof only. Not custody or release authorization.\n\n~~~json\n{\n  \"custody\": \"UNATTESTED_TECHNICAL_ONLY\",\n  \"final_ref\": \"refs/heads/backup/vault-final-20261114-43578373086-2\",\n  \"final_state\": \"CREATED_BY_THIS_FINALIZER\",\n  \"manifest_sha256\": \"a48a04674611338faeb87c65cbf1e10178f7461a104545a0d8b90587f86b3831\",\n  \"original_native_comment_id\": 6876181271,\n  \"release_permission\": false,\n  \"rules\": [\n    \"update\",\n    \"deletion\",\n    \"non_fast_forward\"\n  ],\n  \"ruleset_id\": 26489349,\n  \"run_attempt\": \"2\",\n  \"run_id\": \"43578373086\",\n  \"schema\": \"VAULT_FINAL_REF_RECEIPT_v1\",\n  \"snapshot_commit\": \"0bf108d1f07acf60041e85f4d6b81f1ee4d90d7d\",\n  \"source_sha\": \"da60923267f30f0bef36a586d4a19f86d8094cb6\",\n  \"source_tree_sha\": \"20fb2fd1327960273624d475b23827c2177001e0\",\n  \"staging_ref_advisory\": \"refs/heads/agent/task-20261114-recovery-43578373086-2\",\n  \"verified_at_utc\": \"2026-11-14T10:52:23.154454+00:00\",\n  \"verified_files\": 331011\n}\n~~~\n"
APP = {"slug": W.VAULT_APP_SLUG}
BOT = f"{W.VAULT_APP_SLUG}[bot]"


def c(body, hours_ago, login="Donh91", typ="User", app=None):
    return {"body": body, "created_at": (NOW - dt.timedelta(hours=hours_ago)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "user": {"login": login, "type": typ}, "performed_via_github_app": app}


def bot(body, hours_ago):
    return c(body, hours_ago, login=BOT, typ="Bot", app=APP)


def edit(**changes):
    head, rest = REAL_RECEIPT.split("~~~json\n", 1)
    block, tail = rest.split("\n~~~", 1)
    data = json.loads(block)
    for k, v in changes.items():
        if v is None:
            data.pop(k, None)
        else:
            data[k] = v
    return head + "~~~json\n" + json.dumps(data, indent=2) + "\n~~~" + tail


HB = c("S1_HEARTBEAT_v1 main=1 contract=2", 5)


class FakeGithub:
    def __init__(self, s1, vault):
        self.data = {W.S1_ISSUE: s1, W.VAULT_ISSUE: vault}
        self.posts = []

    def comments(self, issue):
        return self.data[issue]

    def post(self, issue, body):
        self.posts.append((issue, body))


class ReceiptParsing(unittest.TestCase):
    def test_real_receipt_is_a_valid_seal(self):
        self.assertTrue(W.valid_seal(REAL_RECEIPT))
        self.assertNotIn("PASS", REAL_RECEIPT)  # v1 text matching would have rejected every real receipt

    def test_failure_text_with_prior_pass_is_not_a_seal(self):
        self.assertFalse(W.valid_seal("<!-- VAULT_FINAL_REF_RECEIPT_v1:1-1 -->\nVAULT_FINAL_REF_RECEIPT_v1 FAIL restore=FAIL prior=PASS"))

    def test_every_field_is_checked(self):
        bad = [
            edit(schema="OTHER"), edit(final_state="FAILED"), edit(final_state=None), edit(release_permission=True),
            edit(final_ref="refs/heads/agent/task-x"), edit(run_id="999"), edit(run_attempt="9"),
            edit(snapshot_commit="xyz"), edit(source_sha=None), edit(source_tree_sha="0" * 39),
            edit(verified_files=0), edit(verified_files=True), edit(verified_files="331011"),
        ]
        for body in bad:
            with self.subTest(body=body[:80]):
                self.assertFalse(W.valid_seal(body))


    def test_syntactically_valid_nonobject_json_fails_closed(self):
        # Non-object App-authored JSON must alert rather than crash in continue-on-error CI.
        prefix = REAL_RECEIPT.partition("~~~json")[0]
        for payload in ("[]", "null", "42", "true", "false"):
            body = prefix + "~~~json" + chr(10) + payload + chr(10) + "~~~" + chr(10)
            with self.subTest(payload=payload):
                self.assertFalse(W.valid_seal(body))
                causes = W.evaluate([HB], [bot(body, 1)], NOW)
                self.assertEqual([x["cause"] for x in causes], ["VAULT_RECEIPT_INVALID"])

    def test_malformed_json_is_not_a_seal(self):
        self.assertFalse(W.valid_seal(REAL_RECEIPT.replace('"schema"', '"schema" "')))
        self.assertFalse(W.valid_seal(REAL_RECEIPT.replace("~~~json", "~~~text")))


class WatchdogTest(unittest.TestCase):
    def test_healthy_posts_nothing(self):
        gh = FakeGithub([HB], [bot(REAL_RECEIPT, 10)])
        r = W.run(gh, NOW, dry_run=False)
        self.assertEqual(r["causes"], [])
        self.assertEqual(gh.posts, [])

    def test_newer_invalid_receipt_overrides_older_valid_one(self):
        causes = W.evaluate([HB], [bot(REAL_RECEIPT, 20), bot(edit(final_state="FAILED"), 1)], NOW)
        self.assertEqual([x["cause"] for x in causes], ["VAULT_RECEIPT_INVALID"])

    def test_stale_heartbeat_and_stale_vault_alert_once_each(self):
        gh = FakeGithub([c("S1_HEARTBEAT_v1 x", 27)], [bot(REAL_RECEIPT, 31)])
        r = W.run(gh, NOW, dry_run=False)
        self.assertEqual(r["posted"], ["S1_HEARTBEAT_STALE", "VAULT_RECEIPT_STALE"])
        self.assertTrue(all(i == W.S1_ISSUE and "@Donh91" in b for i, b in gh.posts))
        gh2 = FakeGithub(gh.data[W.S1_ISSUE] + [c(b, 0) for _, b in gh.posts], gh.data[W.VAULT_ISSUE])
        self.assertEqual(W.run(gh2, NOW, dry_run=False)["posted"], [])

    def test_owner_account_and_lookalike_receipts_are_not_trusted(self):
        forged = c(REAL_RECEIPT, 1)
        no_app = c(REAL_RECEIPT, 1, login=BOT, typ="Bot", app=None)
        other_app = c(REAL_RECEIPT, 1, login="other[bot]", typ="Bot", app={"slug": "other"})
        user_typed = c(REAL_RECEIPT, 1, login=BOT, typ="User", app=APP)
        causes = W.evaluate([HB], [forged, no_app, other_app, user_typed], NOW)
        self.assertEqual([x["cause"] for x in causes], ["VAULT_APP_RECEIPT_MISSING"])

    def test_native_app_receipt_without_final_ref_identifies_finalizer_gap(self):
        native = bot("<!-- VAULT_NATIVE_RECEIPT_V1:43657764359-1 -->\\nTechnical restore PASS, not final-ref authority.", 1)
        old_owner_final = c(REAL_RECEIPT, 2)  # owner account is not independent App
        causes = W.evaluate([HB], [native, old_owner_final], NOW)
        self.assertEqual([x["cause"] for x in causes], ["VAULT_APP_FINAL_REF_MISSING"])
        diagnostic = W.alert_body(causes[0], NOW)
        self.assertIn("finalizer job", diagnostic)
        self.assertIn("Do not re-run the snapshot", diagnostic)
        self.assertNotIn("Start \'Vault canonical snapshot", diagnostic)

    def test_lookalike_native_receipt_cannot_satisfy_app_identity(self):
        forged_native = c("<!-- VAULT_NATIVE_RECEIPT_V1:43657764359-1 -->", 1)
        causes = W.evaluate([HB], [forged_native], NOW)
        self.assertEqual([x["cause"] for x in causes], ["VAULT_APP_RECEIPT_MISSING"])

    def test_missing_heartbeat(self):
        causes = W.evaluate([c("S1_TICK NOOP", 1)], [bot(REAL_RECEIPT, 1)], NOW)
        self.assertEqual([x["cause"] for x in causes], ["S1_HEARTBEAT_MISSING"])

    def test_dry_run_never_posts(self):
        gh = FakeGithub([], [])
        r = W.run(gh, NOW, dry_run=True)
        self.assertEqual(len(r["posted"]), 2)
        self.assertEqual(gh.posts, [])

    def test_route_allowlist(self):
        with self.assertRaises(ValueError):
            W.Github("t")._req("GET", "/repos/Donh91/Investering-Framework-Vault/issues/1")


if __name__ == "__main__":
    unittest.main()
