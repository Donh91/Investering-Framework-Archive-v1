from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.document_ingestion.anydoc_ingest import IngestionError, ingest


FAKE_ANYDOC = r'''#!/usr/bin/env python3
import sys
from pathlib import Path

source = Path(sys.argv[1])
out = Path(sys.argv[sys.argv.index("-o") + 1])
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(f"# Converted\n\nSource: {source.name}\n", encoding="utf-8")
'''

FAILING_ANYDOC = r'''#!/usr/bin/env python3
import sys
print("anydoc: synthetic failure", file=sys.stderr)
raise SystemExit(1)
'''


class AnyDocIngestTests(unittest.TestCase):
    def make_executable(self, root: Path, content: str, name: str = "fake-anydoc") -> Path:
        path = root / name
        path.write_text(content, encoding="utf-8")
        path.chmod(path.stat().st_mode | 0o111)
        return path

    def test_docx_success_writes_markdown_and_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "report.docx"
            source.write_bytes(b"synthetic-docx")
            binary = self.make_executable(root, FAKE_ANYDOC)
            output = root / "out"

            manifest = ingest(source, output, anydoc_bin=binary)

            self.assertEqual(manifest["status"], "READY")
            self.assertTrue((output / "document.md").is_file())
            stored = json.loads((output / "manifest.json").read_text())
            self.assertEqual(stored["parser"]["version"], "0.1.3")
            self.assertFalse(stored["authority"]["creates_truth"])
            self.assertFalse(stored["routing"]["pdf_fallback_used"])

    def test_pdf_defaults_to_existing_specialist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "report.pdf"
            source.write_bytes(b"%PDF-synthetic")
            binary = self.make_executable(root, FAKE_ANYDOC)

            with self.assertRaisesRegex(IngestionError, "USE_EXISTING_PDF_INSPECTOR"):
                ingest(source, root / "out", anydoc_bin=binary)

    def test_explicit_pdf_fallback_is_degraded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "report.pdf"
            source.write_bytes(b"%PDF-synthetic")
            binary = self.make_executable(root, FAKE_ANYDOC)

            manifest = ingest(source, root / "out", anydoc_bin=binary, allow_pdf_fallback=True)

            self.assertEqual(manifest["status"], "DEGRADED")
            self.assertTrue(manifest["routing"]["pdf_fallback_used"])
            self.assertIn("PDF_FALLBACK_USED_WITHOUT_SPECIALIZED_LAYOUT_OR_OCR_RECEIPT", manifest["warnings"])

    def test_format_hint_allows_extensionless_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "table"
            source.write_text("a,b\n1,2\n", encoding="utf-8")
            binary = self.make_executable(root, FAKE_ANYDOC)

            manifest = ingest(source, root / "out", anydoc_bin=binary, format_hint="csv")

            self.assertEqual(manifest["status"], "READY")
            self.assertEqual(manifest["source"]["format"], "csv")

    def test_converter_failure_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "slides.pptx"
            source.write_bytes(b"synthetic-pptx")
            binary = self.make_executable(root, FAILING_ANYDOC, "failing-anydoc")

            with self.assertRaisesRegex(IngestionError, "ANYDOC_FAILED:1"):
                ingest(source, root / "out", anydoc_bin=binary)

    def test_unsupported_extension_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "payload.bin"
            source.write_bytes(b"data")
            binary = self.make_executable(root, FAKE_ANYDOC)

            with self.assertRaisesRegex(IngestionError, "UNSUPPORTED_EXTENSION"):
                ingest(source, root / "out", anydoc_bin=binary)


if __name__ == "__main__":
    unittest.main()
