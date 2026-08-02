from __future__ import annotations

import importlib.util
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts/pdf_ingestion/pdf_ingest.py"
SPEC = importlib.util.spec_from_file_location("pdf_ingest", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

FIXTURE_PATH = ROOT / "tests/pdf_ingestion/build_minimal_pdf.py"
FIXTURE_SPEC = importlib.util.spec_from_file_location("pdf_fixture", FIXTURE_PATH)
FIXTURE = importlib.util.module_from_spec(FIXTURE_SPEC)
assert FIXTURE_SPEC.loader is not None
FIXTURE_SPEC.loader.exec_module(FIXTURE)


def executable(path: Path, body: str) -> Path:
    path.write_text("#!/usr/bin/env python3\n" + body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


class PdfIngestionTests(unittest.TestCase):
    def test_invalid_magic_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.pdf"
            path.write_text("not a pdf")
            with self.assertRaises(MODULE.IngestionError):
                MODULE.validate_pdf(path)

    def test_ready_native_text_materializes_markdown_and_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.pdf"
            source.write_bytes(FIXTURE.build_pdf("Framework PDF integration test"))
            detect = executable(
                root / "detect",
                "import json\nprint(json.dumps({'pdf_type':'text_based','page_count':1,'confidence':0.99,'pages_needing_ocr':[]}))\n",
            )
            pdf2md = executable(root / "pdf2md", "print('# Framework PDF integration test')\n")
            output = root / "output"
            manifest = MODULE.ingest(source, output, detect, pdf2md)
            self.assertEqual(manifest["status"], "READY")
            self.assertTrue(manifest["markdown_materialized"])
            self.assertFalse(manifest["requires_ocr_or_vision"])
            self.assertIn("Framework PDF integration test", (output / "document.md").read_text())
            stored = json.loads((output / "manifest.json").read_text())
            self.assertFalse(stored["authority"]["portfolio_action"])
            self.assertFalse(stored["authority"]["framework_state_change"])

    def test_scanned_document_routes_to_ocr_without_inventing_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.pdf"
            source.write_bytes(FIXTURE.build_pdf("image placeholder"))
            detect = executable(
                root / "detect",
                "import json\nprint(json.dumps({'pdfType':'Scanned','pageCount':2,'confidence':0.95,'pagesNeedingOcr':[1,2]}))\n",
            )
            pdf2md = executable(root / "pdf2md", "import sys\nprint('no extractable text', file=sys.stderr)\nraise SystemExit(2)\n")
            output = root / "output"
            manifest = MODULE.ingest(source, output, detect, pdf2md)
            self.assertEqual(manifest["status"], "DEGRADED")
            self.assertTrue(manifest["requires_ocr_or_vision"])
            self.assertFalse(manifest["markdown_materialized"])
            self.assertFalse((output / "document.md").exists())

    def test_output_hashes_match_materialized_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.pdf"
            source.write_bytes(FIXTURE.build_pdf("hash test"))
            detect = executable(root / "detect", "print('{\"pdf_type\":\"text_based\",\"pages_needing_ocr\":[]}')\n")
            pdf2md = executable(root / "pdf2md", "print('hash test')\n")
            output = root / "output"
            manifest = MODULE.ingest(source, output, detect, pdf2md)
            for item in manifest["outputs"]:
                path = output / item["path"]
                self.assertEqual(item["sha256"], MODULE.sha256_file(path))


if __name__ == "__main__":
    unittest.main()
