"""Capture the live Farside BTC/ETH tables with the owner's own client path (urllib + owner User-Agent).

Writes WORK/live/{btc,eth}.html and fetch_receipt.json. Read-only against the source; if the source serves a
challenge page or errors, the capture fails and nothing is retried or worked around.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import urllib.request

from etf_lab_common import LIVE, owner_module


def main() -> None:
    LIVE.mkdir(parents=True, exist_ok=True)
    mod = owner_module()
    out = {}
    for asset, url in mod.URLS.items():
        t0 = datetime.datetime.now(datetime.timezone.utc)
        req = urllib.request.Request(url, headers={"User-Agent": "InvesteringFramework/2.2 (+verified ETF owner capture)"})
        raw = urllib.request.urlopen(req, timeout=30).read()
        t1 = datetime.datetime.now(datetime.timezone.utc)
        (LIVE / f"{asset.lower()}.html").write_bytes(raw)
        out[asset.lower()] = {"url": url, "request_started_utc": t0.isoformat().replace("+00:00", "Z"),
                              "retrieved_at_utc": t1.isoformat().replace("+00:00", "Z"), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    (LIVE / "fetch_receipt.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
