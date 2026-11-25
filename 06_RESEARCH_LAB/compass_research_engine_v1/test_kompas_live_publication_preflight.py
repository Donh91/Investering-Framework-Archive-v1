"""Synthetic receipt/census tests. No network, market data or outcome linkage."""
import hashlib
import unittest
from kompas_live_publication_preflight import bind_publication, census, PATH, ORIGIN

RAW = b"synthetic fixture, not a real forecast"
DIGEST = hashlib.sha256(RAW).hexdigest()
START = "2026-11-25T20:00:00Z"
END = "2026-11-26T00:00:00Z"


def capture(**kw):
    return dict({"contract": "KOMPAS_LIVE_MEMORY_CAPTURE_v1",
                 "source_url_label": ORIGIN+PATH, "source_bytes": len(RAW),
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
