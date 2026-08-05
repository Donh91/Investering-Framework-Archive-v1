#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

UPSTREAM_REPOSITORY = "https://github.com/firecrawl/anydoc"
ANYDOC_PACKAGE = "@firecrawl/anydoc"
PINNED_VERSION = "0.1.3"
MAX_INPUT_BYTES = 25 * 1024 * 1024
SUPPORTED_EXTENSIONS = {
    ".doc", ".docx", ".docm",
    ".ppt", ".pps", ".pot", ".pptx", ".pptm", ".ppsx", ".ppsm",
    ".xls", ".xlsx", ".xlsm", ".xlsb",
    ".odt", ".ods", ".odp",
    ".rtf", ".epub", ".csv", ".pdf",
}
SUPPORTED_FORMAT_HINTS = {
    "doc", "docx", "ppt", "pptx", "xls", "xlsx",
    "odt", "ods", "odp", "rtf", "epub", "csv", "pdf",
}
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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_input(path: Path, format_hint: str | None, max_bytes: int = MAX_INPUT_BYTES) -> str:
    if not path.is_file():
        raise IngestionError("INPUT_NOT_FOUND")
    size = path.stat().st_size
    if size <= 0:
        raise IngestionError("EMPTY_INPUT")
    if size > max_bytes:
        raise IngestionError(f"INPUT_OVER_LIMIT:{size}>{max_bytes}")

    extension = path.suffix.lower()
    normalized_hint = format_hint.lower() if format_hint else None
    if normalized_hint and normalized_hint not in SUPPORTED_FORMAT_HINTS:
        raise IngestionError(f"UNSUPPORTED_FORMAT_HINT:{normalized_hint}")
    if extension not in SUPPORTED_EXTENSIONS and normalized_hint is None:
        raise IngestionError(f"UNSUPPORTED_EXTENSION:{extension or 'NONE'}")
    return normalized_hint or extension.lstrip(".")


def build_command(
    input_path: Path,
    markdown_path: Path,
    anydoc_bin: Path | None,
    format_hint: str | None,
) -> list[str]:
    if anydoc_bin is not None:
        command = [str(anydoc_bin), str(input_path), "-o", str(markdown_path)]
    else:
        command = [
            "npx",
            "-y",
            f"{ANYDOC_PACKAGE}@{PINNED_VERSION}",
            str(input_path),
            "-o",
            str(markdown_path),
        ]
    if format_hint:
        command.extend(["--format", format_hint])
    return command


def run_command(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(command), text=True, capture_output=True, check=False)


def output_record(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def write_manifest(output_dir: Path, manifest: dict[str, Any]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def blocked_manifest(
    input_path: Path,
    output_dir: Path,
    error: str,
    format_hint: str | None,
) -> dict[str, Any]:
    source: dict[str, Any] = {"filename": input_path.name}
    if input_path.is_file():
        source.update({
            "bytes": input_path.stat().st_size,
            "sha256": sha256_file(input_path),
        })
    manifest = {
        "contract": "ANYDOC_AGENT_INGESTION_RECEIPT_v1",
        "status": "BLOCKED",
        "created_at_utc": utc_now(),
        "error": error,
        "source": source,
        "format_hint": format_hint,
        "parser": {
            "repository": UPSTREAM_REPOSITORY,
            "package": ANYDOC_PACKAGE,
            "version": PINNED_VERSION,
        },
        "authority": AUTHORITY,
    }
    write_manifest(output_dir, manifest)
    return manifest


def ingest(
    input_path: Path,
    output_dir: Path,
    anydoc_bin: Path | None = None,
    format_hint: str | None = None,
    allow_pdf_fallback: bool = False,
) -> dict[str, Any]:
    normalized_format = validate_input(input_path, format_hint)
    is_pdf = normalized_format == "pdf" or input_path.suffix.lower() == ".pdf"
    if is_pdf and not allow_pdf_fallback:
        raise IngestionError("USE_EXISTING_PDF_INSPECTOR")

    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = output_dir / "document.md"
    if markdown_path.exists():
        markdown_path.unlink()

    command = build_command(input_path, markdown_path, anydoc_bin, format_hint)
    result = run_command(command)
    if result.returncode != 0:
        stderr = result.stderr.strip().replace("\n", " ")[-1000:]
        raise IngestionError(f"ANYDOC_FAILED:{result.returncode}:{stderr}")
    if not markdown_path.is_file():
        raise IngestionError("MARKDOWN_NOT_CREATED")
    if markdown_path.stat().st_size <= 0 or not markdown_path.read_text(encoding="utf-8", errors="replace").strip():
        raise IngestionError("EMPTY_MARKDOWN_OUTPUT")

    warnings: list[str] = []
    status = "READY"
    if is_pdf:
        status = "DEGRADED"
        warnings.append("PDF_FALLBACK_USED_WITHOUT_SPECIALIZED_LAYOUT_OR_OCR_RECEIPT")

    manifest = {
        "contract": "ANYDOC_AGENT_INGESTION_RECEIPT_v1",
        "status": status,
        "created_at_utc": utc_now(),
        "source": {
            "filename": input_path.name,
            "bytes": input_path.stat().st_size,
            "sha256": sha256_file(input_path),
            "format": normalized_format,
            "original_remains_primary": True,
        },
        "parser": {
            "repository": UPSTREAM_REPOSITORY,
            "package": ANYDOC_PACKAGE,
            "version": PINNED_VERSION,
            "invocation": "EXPLICIT_BINARY" if anydoc_bin else "NPX_PINNED_PACKAGE",
            "exit_code": result.returncode,
        },
        "routing": {
            "pdf_specialist_default": "scripts/pdf_ingestion/pdf_ingest.py",
            "pdf_fallback_used": is_pdf,
            "ocr_performed": False,
            "visual_interpretation_performed": False,
        },
        "warnings": warnings,
        "outputs": [output_record(markdown_path, output_dir)],
        "stderr": result.stderr[-1000:] if result.stderr else "",
        "authority": AUTHORITY,
    }
    write_manifest(output_dir, manifest)
    print(json.dumps(manifest, sort_keys=True))
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--anydoc-bin", type=Path)
    parser.add_argument("--format-hint")
    parser.add_argument("--allow-pdf-fallback", action="store_true")
    args = parser.parse_args()

    try:
        manifest = ingest(
            input_path=args.input,
            output_dir=args.output_dir,
            anydoc_bin=args.anydoc_bin,
            format_hint=args.format_hint,
            allow_pdf_fallback=args.allow_pdf_fallback,
        )
        return 0 if manifest["status"] in {"READY", "DEGRADED"} else 2
    except IngestionError as exc:
        manifest = blocked_manifest(args.input, args.output_dir, str(exc), args.format_hint)
        print(json.dumps(manifest, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
