"""Synthetic receipt/census tests. No network, market data or outcome linkage."""
import base64
import hashlib
import json
import unittest
from kompas_live_publication_preflight import bind_publication, census, PATH, ORIGIN

DOC = {"contract": "KOMPAS_LIVE_PATH_v1", "generated_at_utc": "2026-11-25T20:25:26Z",
       "status": "OK",
       "authority": {"research_only": True, "official_forecast": False,
                     "compass_probability_claim": False, "trading": False,
                     "promotion": False, "site_synthesis": False},
       "assets": {"BTC": {"status": "OK"}, "ETH": {"status": "OK"}}}
SEAL = hashlib.sha256(json.dumps(DOC, sort_keys=True, separators=(",", ":"),
                                ensure_ascii=False).encode()).hexdigest()
RAW = json.dumps(dict(DOC, path_sha256=SEAL)).encode()
DIGEST = hashlib.sha256(RAW).hexdigest()
START = "2026-11-25T20:00:00Z"
END = "2026-11-26T00:00:00Z"


def capture(**kw):
    return dict({"contract": "KOMPAS_LIVE_MEMORY_CAPTURE_v1",
                 "source_url_label": ORIGIN+PATH, "source_bytes": len(RAW),
                 "source_contract": DOC["contract"], "source_seal_sha256": SEAL,
                 "source_bytes_base64": base64.b64encode(RAW).decode("ascii"),
                 "source_bytes_sha256": DIGEST, "source_status": "OK",
                 "generated_at_utc": "2026-11-25T20:25:26Z",
                 "observer_reported_at_utc": "2026-11-25T20:49:00Z",
                 "publication_authenticated": False, "pit_admitted": False,
                 "scoring_authorized": False, "research_only": True}, **kw)


def parity(**kw):
    return dict({"contract": "CN_PAGES_ARTIFACT_TO_CDN_PARITY_v1",
                 "status": "PASS", "canonical_public_url": ORIGIN,
                 "discovery_status": "PASS", "discovery_error": None,
                 "checked_at_utc": "2026-11-25T20:30:00Z",
                 "run_head_sha": "a"*40, "built_checkout_sha": "b"*40,
                 "files": [{"path": PATH, "status": "PASS", "http_status": 200,
                            "expected_sha256": DIGEST, "served_sha256": DIGEST}]}, **kw)


class PreflightTests(unittest.TestCase):
    def test_exact_match_never_authorizes(self):
        result = bind_publication(RAW, capture(), parity())
        self.assertEqual(result["status"], "BYTE_MATCH_UNAUTHENTICATED")
        self.assertIs(result["pit_admitted"], False)
        self.assertIs(result["scoring_authorized"], False)

    def test_bad_capture_or_parity(self):
        for c, p in [(capture(pit_admitted=True), parity()),
                     (capture(source_bytes=True), parity()),
                     (capture(source_bytes_sha256="0"*64), parity()),
                     (capture(), parity(status="DEGRADED")),
                     (capture(), parity(discovery_error="bad")),
                     (capture(), parity(checked_at_utc=START)),
                     (capture(), parity(files=[])),
                     (capture(), parity(files=parity()["files"]*2)),
                     (capture(), parity(files=[dict(parity()["files"][0], served_sha256="f"*64)]))]:
            with self.subTest(c=c, p=p), self.assertRaises(ValueError):
                bind_publication(RAW, c, p)

    def test_capture_metadata_tampering_rejected(self):
        for c in (capture(generated_at_utc="2026-11-25T20:10:00Z"),
                  capture(source_status="UNAVAILABLE"),
                  capture(source_seal_sha256="f"*64),
                  capture(source_contract="OTHER"),
                  capture(source_bytes_base64="eA==")):
            with self.subTest(c=c), self.assertRaises(ValueError):
                bind_publication(RAW, c, parity())

    def test_wrong_raw_payload_even_with_matching_hash_rejected(self):
        raw = b"not JSON"
        digest = hashlib.sha256(raw).hexdigest()
        c = capture(source_bytes=len(raw), source_bytes_sha256=digest,
                    source_bytes_base64=base64.b64encode(raw).decode("ascii"))
        p = parity(files=[dict(parity()["files"][0], expected_sha256=digest, served_sha256=digest)])
        with self.assertRaises(ValueError):
            bind_publication(raw, c, p)

    def test_self_sealed_invalid_source_rejected(self):
        for changes in (
                {"authority": {}},
                {"authority": dict(DOC["authority"], trading=True)},
                {"authority": dict(DOC["authority"], research_only=1)},
                {"assets": {"BTC": {"status": "OK"}}},
                {"assets": {"BTC": {"status": "OK"}, "ETH": {"status": "UNAVAILABLE"}}}):
            doc = dict(DOC, **changes)
            seal = hashlib.sha256(json.dumps(doc, sort_keys=True, separators=(",", ":"),
                                             ensure_ascii=False).encode()).hexdigest()
            raw = json.dumps(dict(doc, path_sha256=seal)).encode()
            digest = hashlib.sha256(raw).hexdigest()
            c = capture(source_bytes=len(raw), source_bytes_sha256=digest,
                        source_seal_sha256=seal,
                        source_bytes_base64=base64.b64encode(raw).decode("ascii"))
            p = parity(files=[dict(parity()["files"][0], expected_sha256=digest, served_sha256=digest)])
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                bind_publication(raw, c, p)

    def test_same_digest_different_issue_rejected(self):
        other = capture(generated_at_utc="2026-11-25T20:30:00Z")
        with self.assertRaises(ValueError):
            census(START, END, [capture(), other])

    def test_hour_census_keeps_missing_unavailable_and_retries(self):
        unavailable = capture(generated_at_utc="2026-11-25T22:30:00Z",
                              observer_reported_at_utc="2026-11-25T22:45:00Z",
                              source_status="UNAVAILABLE", source_bytes_sha256="e"*64)
        r = census(START, END, [capture(), capture(), unavailable])
        self.assertEqual(r["expected_hours"], 4)
        self.assertEqual(r["missing_hours"], 2)
        self.assertEqual([x["state"] for x in r["hours"]], ["OK", "MISSING", "UNAVAILABLE", "MISSING"])
        self.assertEqual(r["hours"][0]["duplicate_observations"], 1)

    def test_multiple_and_conflict_are_not_selected_away(self):
        another = capture(generated_at_utc="2026-11-25T20:40:00Z", source_bytes_sha256="f"*64)
        self.assertEqual(census(START, END, [capture(), another])["hours"][0]["state"], "MULTIPLE_ISSUES")
        different = capture(source_bytes_sha256="d"*64)
        self.assertEqual(census(START, END, [capture(), different])["hours"][0]["state"], "CONFLICT")

    def test_bad_bounds_and_status(self):
        for start in ("2026-11-25T20:01:00Z", "2026-11-25T20:00:00", END):
            with self.assertRaises(ValueError):
                census(start, END, [])
        with self.assertRaises(ValueError):
            census(START, END, [capture(source_status="MAYBE")])
        with self.assertRaises(ValueError):
            census(START, END, [capture(), capture(source_status="PARTIAL")])

    def test_parity_row_for_other_bytes_rejected(self):
        other = "f" * 64
        p = parity(files=[dict(parity()["files"][0], expected_sha256=other,
                               served_sha256=other)])
        with self.assertRaisesRegex(ValueError, "Kompas bytes not bound"):
            bind_publication(RAW, capture(), p)

    def test_integer_false_flags_rejected(self):
        for key in ("publication_authenticated", "pit_admitted", "scoring_authorized",
                    "research_only"):
            with self.subTest(key=key):
                c = capture(**{key: int(capture()[key])})
                with self.assertRaisesRegex(ValueError, "capture binding mismatch"):
                    bind_publication(RAW, c, parity())
                with self.assertRaisesRegex(ValueError, "invalid census row"):
                    census(START, END, [c])

    def test_census_observation_before_issue_rejected(self):
        with self.assertRaisesRegex(ValueError, "future issue"):
            census(START, END, [capture(observer_reported_at_utc=START)])

    def test_late_census_is_not_ok_and_preserves_source_status(self):
        late = capture(observer_reported_at_utc="2026-11-28T20:49:00Z")
        boundary = capture(observer_reported_at_utc="2026-11-25T21:00:00Z")
        for row in (late, boundary):
            with self.subTest(row=row):
                hour = census(START, END, [row])["hours"][0]
                self.assertEqual(hour["state"], "LATE")
                self.assertEqual(hour["source_statuses"], ["OK"])
                self.assertEqual(hour["late_packets"], 1)
        before = capture(observer_reported_at_utc="2026-11-25T20:59:59Z")
        for rows in ([before, late], [late, before]):
            hour = census(START, END, rows)["hours"][0]
            self.assertEqual(hour["state"], "OK")
            self.assertEqual(hour["late_packets"], 0)
            self.assertEqual(hour["duplicate_observations"], 1)
        unavailable = capture(source_status="UNAVAILABLE",
                              observer_reported_at_utc="2026-11-25T21:00:00Z")
        hour = census(START, END, [unavailable])["hours"][0]
        self.assertEqual(hour["state"], "LATE")
        self.assertEqual(hour["source_statuses"], ["UNAVAILABLE"])

    def test_http_status_requires_integer(self):
        p = parity(files=[dict(parity()["files"][0], http_status=200.0)])
        with self.assertRaisesRegex(ValueError, "invalid, duplicate or nonpassing parity row"):
            bind_publication(RAW, capture(), p)
