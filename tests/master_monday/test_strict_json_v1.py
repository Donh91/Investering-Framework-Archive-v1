import unittest
from scripts.master_monday.strict_json_v1 import load_evidence_object


class StrictEvidenceJSON(unittest.TestCase):
    def test_valid_nested_object(self):
        self.assertEqual(load_evidence_object(b'{"signal":{"value":0.031},"hour":168}'),
                         {'signal': {'value': .031}, 'hour': 168})

    def test_duplicate_top_level_and_nested_keys(self):
        for raw in (b'{"iso_week":47,"iso_week":48}',
                    b'{"signal":{"value":1,"value":-1}}'):
            with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, 'DUPLICATE_JSON_KEY'):
                load_evidence_object(raw)

    def test_nonfinite_and_overflow(self):
        for raw in (b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}', b'{"x":1e999}'):
            with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, 'NONFINITE_JSON_NUMBER'):
                load_evidence_object(raw)

    def test_invalid_shape_and_encoding(self):
        for raw in (b'[]', b'null', b'{"x":"\xff"}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                load_evidence_object(raw)
