#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UPSTREAM_REPOSITORY = "https://github.com/firecrawl/pdf-inspector"
DEFAULT_UPSTREAM_COMMIT = "a15ec2d68d51dbe6a39d1da688ec7a3f642d846c"
MAX_INPUT_BYTES = 25 * 1024 * 1024
AUTHORITY = {
    "creates_truth": False,
    "framework_state_change": False,
    "model_weight_change": False,
    "portfolio_action": False,
    "canonical_promotion": False,
}


class IngestionError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_pdf(path: Path, max_bytes: int = MAX_INPUT_BYTES) -> None:
    if not path.is_file():
        raise IngestionError("INPUT_NOT_FOUND")
    size = path.stat().st_size
    if size <= 0:
        raise IngestionError("EMPTY_INPUT")
    if size > max_bytes:
        raise IngestionError(f"INPUT_OVER_LIMIT:{size}>{max_bytes}")
    with path.open("rb") as handle:
        if handle.read(5) != b"%PDF-":
            raise IngestionError("INVALID_PDF_MAGIC")


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=False)


def parse_json_output(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if not stripped:
        raise IngestionError("EMPTY_DETECTOR_OUTPUT")
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start < 0 or end <= start:
            raise IngestionError("INVALID_DETECTOR_JSON")
        value = json.loads(stripped[start : end + 1])
    if not isinstance(value, dict):
        raise IngestionError("DETECTOR_OUTPUT_NOT_OBJECT")
    return value


def first_present(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in data:
            return data[key]
    return default


def normalize_detection(data: dict[str, Any]) -> dict[str, Any]:
    pdf_type = first_present(data, "pdf_type", "pdfType", "type", default="UNKNOWN")
    page_count = first_present(data, "page_count", "pageCount", "pages", default=None)
    pages_needing_ocr = first_present(data, "pages_needing_ocr", "pagesNeedingOcr", default=[])
    pages_with_tables = first_present(data, "pages_with_tables", "pagesWithTables", default=[])
    pages_with_columns = first_present(data, "pages_with_columns", "pagesWithColumns", default=[])
    confidence = first_present(data, "confidence", default=None)
    complex_layout = first_present(data, "is_complex_layout", "isComplexLayout", "is_complex", default=None)
    encoding_issues = first_present(data, "has_encoding_issues", "hasEncodingIssues", default=None)
    return {
        "pdf_type": str(pdf_type),
        "page_count": page_count,
        "confidence": confidence,
        "pages_needing_ocr": pages_needing_ocr if isinstance(pages_needing_ocr, list) else [],
        "pages_with_tables": pages_with_tables if isinstance(pages_with_tables, list) else [],
        "pages_with_columns": pages_with_columns if isinstance(pages_with_columns, list) else [],
        "is_complex_layout": complex_layout,
        "has_encoding_issues": encoding_issues,
    }


def output_record(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def ingest(
    input_path: Path,
    output_dir: Path,
    detect_bin: Path,
    pdf2md_bin: Path,
    upstream_commit: str = DEFAULT_UPSTREAM_COMMIT,
) -> dict[str, Any]:
    validate_pdf(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    detector = run_command([str(detect_bin), str(input_path), "--analyze", "--json"])
    if detector.returncode != 0:
        raise IngestionError(f"DETECTOR_FAILED:{detector.returncode}:{detector.stderr[-500:]}")
    raw_detection = parse_json_output(detector.stdout)
    normalized = normalize_detection(raw_detection)

    detection_path = output_dir / "detection.json"
    detection_path.write_text(json.dumps(raw_detection, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    extractor = run_command([str(pdf2md_bin), str(input_path), "--raw", "--compact", "--pages"])
    markdown = extractor.stdout.strip()
    markdown_path = output_dir / "document.md"
    if extractor.returncode == 0 and markdown:
        markdown_path.write_text(markdown + "\n", encoding="utf-8")

    requires_ocr = bool(normalized["pages_needing_ocr"])
    pdf_type = normalized["pdf_type"].lower()
    if pdf_type in {"scanned", "imagebased", "image_based", "mixed"}:
        requires_ocr = True

    if extractor.returncode == 0 and markdown:
        status = "DEGRADED" if requires_ocr or normalized["has_encoding_issues"] is True else "READY"
    else:
        status = "DEGRADED" if requires_ocr else "BLOCKED"

    outputs = [output_record(detection_path, output_dir)]
    if markdown_path.is_file():
        outputs.append(output_record(markdown_path, output_dir))

    manifest = {
        "contract": "PDF_INSPECTOR_INGESTION_RECEIPT_v1",
        "status": status,
        "created_at_utc": utc_now(),
        "source": {
            "filename": input_path.name,
            "bytes": input_path.stat().st_size,
            "sha256": sha256_file(input_path),
        },
        "parser": {
            "repository": UPSTREAM_REPOSITORY,
            "commit": upstream_commit,
            "detector_exit_code": detector.returncode,
            "extractor_exit_code": extractor.returncode,
        },
        "detection": normalized,
        "requires_ocr_or_vision": requires_ocr,
        "markdown_materialized": markdown_path.is_file(),
        "extractor_stderr": extractor.stderr[-1000:] if extractor.stderr else "",
        "outputs": outputs,
        "authority": AUTHORITY,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, sort_keys=True))
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--detect-bin", type=Path, required=True)
    parser.add_argument("--pdf2md-bin", type=Path, required=True)
    parser.add_argument("--upstream-commit", default=DEFAULT_UPSTREAM_COMMIT)
    args = parser.parse_args()
    try:
        manifest = ingest(args.input, args.output_dir, args.detect_bin, args.pdf2md_bin, args.upstream_commit)
        return 0 if manifest["status"] in {"READY", "DEGRADED"} else 2
    except IngestionError as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc), "authority": AUTHORITY}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
