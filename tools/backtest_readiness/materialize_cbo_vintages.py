#!/usr/bin/env python3
"""Materialize and structurally audit pinned CBO ten-year-budget vintages.

This utility is deliberately limited to source engineering. It computes byte and
structural receipts only. It does not run economic tests, inspect final holdout
state, select parameters, or change framework authority.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Iterable
from urllib.request import Request, urlopen

SOURCE_REPOSITORY = "US-CBO/cbo-data"
SOURCE_COMMIT = "284a95665f9f2f74ed1f482feb629b43fce323da"
CANONICAL_COLUMNS = ["date", "variable", "value"]
TARGET_VARIABLES = {
    "proj_outlays_net_interest",
    "proj_outlays_net_interest_gdp_share",
    "proj_debt_held_by_public",
    "proj_primary_deficit",
}
VINTAGES = {
    "2024-06": {
        "path": "data/budget/ten_year_budget/annual_fy_2024-06.csv",
        "github_blob_sha": "c71ef5986e1ccf6bdb4d993b6fcc141bfc3db9bc",
    },
    "2025-01": {
        "path": "data/budget/ten_year_budget/annual_fy_2025-01.csv",
        "github_blob_sha": "999655e773307bd04b7ea07bd03b81f5d516fa7b",
    },
    "2026-02": {
        "path": "data/budget/ten_year_budget/annual_fy_2026-02.csv",
        "github_blob_sha": "99f55b63bb8db8c214e2ee08de5ce0c216358fac",
    },
}


class MaterializationError(RuntimeError):
    """Raised when source bytes fail the frozen structural contract."""


def raw_url(path: str) -> str:
    return f"https://raw.githubusercontent.com/{SOURCE_REPOSITORY}/{SOURCE_COMMIT}/{path}"


def fetch_bytes(path: str, timeout: float = 60.0) -> bytes:
    request = Request(
        raw_url(path),
        headers={"User-Agent": "Investering-Framework-GLC-WP01B/1.0"},
    )
    with urlopen(request, timeout=timeout) as response:  # nosec B310 - pinned HTTPS owner URL
        return response.read()


def _fiscal_year(value: str) -> int:
    if not value.startswith("FY") or len(value) != 6 or not value[2:].isdigit():
        raise MaterializationError(f"invalid fiscal-year label: {value!r}")
    return int(value[2:])


def _missing_in_contiguous_span(years: Iterable[int]) -> list[int]:
    ordered = sorted(set(years))
    if not ordered:
        return []
    expected = set(range(ordered[0], ordered[-1] + 1))
    return sorted(expected.difference(ordered))


def analyze_csv_bytes(vintage: str, payload: bytes) -> dict:
    if vintage not in VINTAGES:
        raise MaterializationError(f"unregistered CBO vintage: {vintage}")

    sha256 = hashlib.sha256(payload).hexdigest()
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise MaterializationError("CBO CSV is not valid UTF-8") from exc

    reader = csv.DictReader(io.StringIO(text, newline=""))
    if reader.fieldnames != CANONICAL_COLUMNS:
        raise MaterializationError(
            f"unexpected columns for {vintage}: {reader.fieldnames!r}"
        )

    rows = list(reader)
    if not rows:
        raise MaterializationError(f"empty CBO vintage: {vintage}")

    duplicate_keys: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    missing_value_rows = 0
    variable_years: dict[str, list[int]] = {name: [] for name in TARGET_VARIABLES}

    for row in rows:
        key = (row["date"], row["variable"])
        if key in seen:
            duplicate_keys.append(key)
        else:
            seen.add(key)
        if row["value"] == "":
            missing_value_rows += 1
        if row["variable"] in TARGET_VARIABLES:
            variable_years[row["variable"]].append(_fiscal_year(row["date"]))

    if duplicate_keys:
        raise MaterializationError(
            f"duplicate (date, variable) keys in {vintage}: {len(duplicate_keys)}"
        )

    missing_targets = sorted(name for name, years in variable_years.items() if not years)
    if missing_targets:
        raise MaterializationError(
            f"required target variables missing in {vintage}: {missing_targets}"
        )

    target_audit = {}
    for name in sorted(TARGET_VARIABLES):
        years = sorted(set(variable_years[name]))
        gaps = _missing_in_contiguous_span(years)
        if gaps:
            raise MaterializationError(
                f"fiscal-year gaps for {name} in {vintage}: {gaps}"
            )
        target_audit[name] = {
            "row_count": len(variable_years[name]),
            "unique_fiscal_year_count": len(years),
            "first_fiscal_year": years[0],
            "last_fiscal_year": years[-1],
            "missing_fiscal_years_within_span": [],
        }

    return {
        "vintage": vintage,
        "path": VINTAGES[vintage]["path"],
        "github_blob_sha": VINTAGES[vintage]["github_blob_sha"],
        "sha256": sha256,
        "bytes": len(payload),
        "row_count": len(rows),
        "columns": CANONICAL_COLUMNS,
        "duplicate_date_variable_keys": 0,
        "missing_value_rows": missing_value_rows,
        "target_variables": target_audit,
        "publication_timestamp": None,
        "publication_timestamp_status": "PENDING_OFFICIAL_RELEASE_BINDING",
        "structural_validation": "PASS",
    }


def materialize(*, input_dir: Path | None, fetch: bool) -> dict:
    if (input_dir is None) == (not fetch):
        raise MaterializationError("choose exactly one acquisition mode: --input-dir or --fetch")

    results = []
    for vintage, metadata in VINTAGES.items():
        if fetch:
            payload = fetch_bytes(metadata["path"])
        else:
            assert input_dir is not None
            source_path = input_dir / Path(metadata["path"]).name
            if not source_path.is_file():
                raise MaterializationError(f"missing input file: {source_path}")
            payload = source_path.read_bytes()
        results.append(analyze_csv_bytes(vintage, payload))

    return {
        "schema_version": "1.0",
        "receipt_id": "GLC_WP01B_CBO_BYTE_MATERIALIZATION",
        "source_owner": "CONGRESSIONAL_BUDGET_OFFICE",
        "source_repository": SOURCE_REPOSITORY,
        "source_repository_commit": SOURCE_COMMIT,
        "acquisition_mode": "PINNED_RAW_GITHUB" if fetch else "LOCAL_EXACT_BYTES",
        "vintage_count": len(results),
        "vintages": results,
        "economic_execution": False,
        "parameter_search": False,
        "final_holdout_access": False,
        "framework_or_portfolio_authority": "NONE",
        "status": "PASS_BYTES_AND_STRUCTURE_ONLY",
        "remaining_blocker": "OFFICIAL_PUBLICATION_TIMESTAMPS_AND_POINT_IN_TIME_SELECTOR",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fetch", action="store_true", help="fetch exact pinned owner bytes")
    group.add_argument("--input-dir", type=Path, help="directory containing exact vintage CSV files")
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    receipt = materialize(input_dir=args.input_dir, fetch=args.fetch)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "output": str(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
