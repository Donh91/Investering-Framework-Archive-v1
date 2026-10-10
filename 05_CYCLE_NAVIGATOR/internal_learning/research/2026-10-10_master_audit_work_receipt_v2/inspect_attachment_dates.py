#!/usr/bin/env python3
"""Count date anchors in two hash-bound attachments; never admit OHLC values.

Requires pdftotext. Originals stay local. Output contains provenance/counts only.
This is a bounded source-quality check, not a forecast or performance evaluator.
"""
import argparse
import hashlib
import json
import re
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path

ANCHOR = re.compile(r"^\s*([A-Z][a-z]{2} \d{2}, \d{4})(.*)$", re.MULTILINE)


def inspect(path, source_id, expected_sha):
    actual_sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual_sha != expected_sha:
        raise ValueError(f"Source {source_id}: hash mismatch; stop before parsing")
    text = subprocess.check_output(["pdftotext", "-layout", str(path), "-"], text=True)
    matches = list(ANCHOR.finditer(text))
    dates = [datetime.strptime(m.group(1), "%b %d, %Y").date() for m in matches]
    if not dates:
        raise ValueError(f"Source {source_id}: no date anchors; not valid empty coverage")
    unique = set(dates)
    low, high = min(dates), max(dates)
    # A date at a PDF page end can have its values on the next page.
    split = sum(not m.group(2).strip() for m in matches)
    return {
        "source_id": source_id, "sha256": actual_sha,
        "date_labels": len(dates), "unique_dates": len(unique),
        "duplicate_dates": len(dates) - len(unique),
        "actual_min_date": low.isoformat(), "actual_max_date": high.isoformat(),
        "missing_calendar_dates_inside_observed_span": (high-low).days+1-len(unique),
        "date_only_page_split_rows": split,
        "2026_date_labels": sum(d.year == 2026 for d in dates),
        "covers_week25_2026": all(date(2026, 6, 15)+timedelta(days=i) in unique for i in range(7)),
        "price_columns_admitted": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("--index", type=Path, default=Path(__file__).with_name("P3_SOURCE_ADMISSION_INDEX.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sources = json.loads(args.index.read_text())["sources"]
    rows = [inspect(args.source_dir / s["filename"], s["source_id"], s["sha256"])
            for s in sources if s["source_id"] in {"21", "22"}]
    receipt = {
        "records": rows,
        "negative_control": "Requiring date and values on the same line drops 55 ETH date anchors. Date-only anchors invalidate that artificial-gap claim; OHLC joining remains unadmitted.",
        "source_time": "PDF footer dates are declared export times, not eligible knowledge-time proof.",
        "qualified_forecasts_admitted": 0,
        "public_payload_values": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"sources_checked": len(rows), "date_labels": sum(r["date_labels"] for r in rows), "price_columns_admitted": False}))


if __name__ == "__main__":
    main()
