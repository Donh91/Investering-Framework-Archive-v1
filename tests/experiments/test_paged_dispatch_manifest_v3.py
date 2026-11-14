"""Source producer v3: complete 63k paged manifest with deterministic hashes."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/experiments"))
from scripts.experiments.experiment_lifecycle_scientific_admission import (  # noqa: E402
    MANIFEST_V3, PAGE_CONTRACT, write_paged_dispatch_manifest,
)


def refs(start: int, n: int) -> list[dict]:
    return [{
        "request_id": f"ER-{i:09d}", "candidate_id": f"EC-{i%762:04d}",
        "path": f"research/experiment_lifecycle/dispatch/2026/11/14/ER-{i:09d}.json",
        "sha256": "a" * 64, "raw_url": "https://raw.githubusercontent.com/Donh91/Investering-Framework-Archive-v1/main/unknown",
    } for i in range(start, start + n)]


def produce(root: Path, rows: list[dict]):
    return write_paged_dispatch_manifest(
        rows, repo_root=root,
        manifest_output=root / "research/experiment_lifecycle/LATEST_EXPERIMENT_DISPATCH_MANIFEST.json",
        source_repository="Donh91/Investering-Framework-Archive-v1",
        source_branch="main", generated_at_utc="2026-11-14T21:00:00Z",
    )


class PagedProducerTests(unittest.TestCase):
    def test_full_63219_request_coverage_no_truncation_and_replay_identical(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            requested = refs(0, 63219)
            index = produce(root, requested)
            self.assertEqual(index["contract"], MANIFEST_V3)
            self.assertEqual(index["request_count"], 63219)
            self.assertEqual(len(index["pages"]), 247)
            all_ids = []
            for seq, meta in enumerate(index["pages"]):
                page_path = root / meta["path"]
                raw = page_path.read_bytes()
                self.assertLess(len(raw), 2_000_000)
                self.assertEqual(meta["sha256"], hashlib.sha256(raw).hexdigest())
                page = json.loads(raw)
                self.assertEqual(page["contract"], PAGE_CONTRACT)
                self.assertEqual(page["sequence"], seq)
                self.assertEqual(page["request_count"], meta["request_count"])
                all_ids.extend(r["request_id"] for r in page["requests"])
            self.assertEqual(all_ids, [r["request_id"] for r in requested])
            before = (root / "research/experiment_lifecycle/LATEST_EXPERIMENT_DISPATCH_MANIFEST.json").read_bytes()
            produce(root, requested)
            self.assertEqual(before, (root / "research/experiment_lifecycle/LATEST_EXPERIMENT_DISPATCH_MANIFEST.json").read_bytes())

    def test_duplicate_request_id_fails_before_writing_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(ValueError, "DUPLICATE_DISPATCH_REQUEST_ID"):
                produce(root, refs(0, 2) + refs(1, 2))
            self.assertFalse((root / "research/experiment_lifecycle/LATEST_EXPERIMENT_DISPATCH_MANIFEST.json").exists())

    def test_zero_request_manifest_is_explicit_and_not_fake(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            idx = produce(root, [])
            self.assertEqual(idx["request_count"], 0)
            self.assertEqual(idx["pages"], [])

    def test_page_index_url_and_count_bind_to_main(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            idx = produce(root, refs(0, 257))
            self.assertEqual([p["request_count"] for p in idx["pages"]], [256, 1])
            self.assertEqual(idx["pages"][1]["first_request_id"], "ER-000000256")
            self.assertEqual(idx["pages"][1]["last_request_id"], "ER-000000256")
            self.assertTrue(idx["pages"][1]["raw_url"].endswith("/dispatch_manifest_pages/part-000001.json"))


if __name__ == "__main__":
    unittest.main()
