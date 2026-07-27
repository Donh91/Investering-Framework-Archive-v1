from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from pathlib import Path
from typing import Any, Iterable


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def read_csv_bytes(payload: bytes) -> list[dict[str, str]]:
    text = payload.decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def read_csv_path(path: Path) -> list[dict[str, str]]:
    return read_csv_bytes(path.read_bytes())


def canonical_number(value: float | int | None) -> str | None:
    if value is None:
        return None
    number = float(value)
    if math.isnan(number):
        return None
    if number == 0:
        number = 0.0
    return format(number, ".15g")


def canonical_rows_hash(rows: Iterable[dict[str, Any]], columns: list[str]) -> str:
    canonical: list[dict[str, Any]] = []
    for row in rows:
        item: dict[str, Any] = {}
        for column in columns:
            value = row.get(column)
            if isinstance(value, float):
                item[column] = canonical_number(value)
            elif isinstance(value, bool):
                item[column] = value
            elif value in ("", None):
                item[column] = None
            else:
                item[column] = value
        canonical.append(item)
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256_bytes(payload)
