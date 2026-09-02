from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

from forecast_ratification_baseline import select_archived_baseline  # noqa: E402

UTC = timezone.utc


def metric_value(value, metric):
    cur = value
    for part in metric.split('.'):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def evidence_timestamp(value):
    return datetime.fromisoformat(value['captured_at_utc'].replace('Z', '+00:00')).astimezone(UTC)


class ForecastRatificationBaselineTests(unittest.TestCase):
    def write(self, root: Path, relative: str, observed: str, price: float):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({'captured_at_utc': observed, 'market': {'price': price}}))
        return path

    def test_mutable_latest_pointer_is_never_selected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            archived = self.write(root, '2026/09/02/archive.json', '2026-09-02T10:19:00Z', 100.0)
            self.write(root, 'LATEST.json', '2026-09-02T10:19:59Z', 999.0)
            path, value, observed = select_archived_baseline(
                root, 'market.price', datetime(2026, 9, 2, 10, 20, tzinfo=UTC),
                metric_value=metric_value, evidence_timestamp=evidence_timestamp,
            )
            self.assertEqual(path, archived)
            self.assertEqual(value['market']['price'], 100.0)
            self.assertEqual(observed, datetime(2026, 9, 2, 10, 19, tzinfo=UTC))

    def test_non_archive_top_level_json_is_not_admissible(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write(root, 'runtime/pointer.json', '2026-09-02T10:19:59Z', 999.0)
            archived = self.write(root, '2026/09/02/archive.json', '2026-09-02T10:19:00Z', 100.0)
            path, value, _ = select_archived_baseline(
                root, 'market.price', datetime(2026, 9, 2, 10, 20, tzinfo=UTC),
                metric_value=metric_value, evidence_timestamp=evidence_timestamp,
            )
            self.assertEqual(path, archived)
            self.assertEqual(value['market']['price'], 100.0)

    def test_conflicting_values_at_latest_timestamp_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write(root, '2026/09/02/a.json', '2026-09-02T10:19:00Z', 100.0)
            self.write(root, '2026/09/02/b.json', '2026-09-02T10:19:00Z', 101.0)
            with self.assertRaisesRegex(ValueError, 'AMBIGUOUS_BASELINE_CAPTURE_AT_DECISION'):
                select_archived_baseline(
                    root, 'market.price', datetime(2026, 9, 2, 10, 20, tzinfo=UTC),
                    metric_value=metric_value, evidence_timestamp=evidence_timestamp,
                )

    def test_identical_values_at_latest_timestamp_are_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            a = self.write(root, '2026/09/02/a.json', '2026-09-02T10:19:00Z', 100.0)
            self.write(root, '2026/09/02/b.json', '2026-09-02T10:19:00Z', 100.0)
            path, value, _ = select_archived_baseline(
                root, 'market.price', datetime(2026, 9, 2, 10, 20, tzinfo=UTC),
                metric_value=metric_value, evidence_timestamp=evidence_timestamp,
            )
            self.assertEqual(path, a)
            self.assertEqual(value['market']['price'], 100.0)

    def test_only_post_decision_observations_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write(root, '2026/09/02/later.json', '2026-09-02T10:21:00Z', 100.0)
            with self.assertRaisesRegex(ValueError, 'NO_ARCHIVED_BASELINE_EVIDENCE'):
                select_archived_baseline(
                    root, 'market.price', datetime(2026, 9, 2, 10, 20, tzinfo=UTC),
                    metric_value=metric_value, evidence_timestamp=evidence_timestamp,
                )


if __name__ == '__main__':
    unittest.main()
