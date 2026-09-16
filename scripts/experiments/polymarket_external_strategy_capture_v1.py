from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GAMMA = "https://gamma-api.polymarket.com"
DATA = "https://data-api.polymarket.com"
WALLET_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def get_json(base: str, path: str, params: dict[str, Any], timeout: int = 30) -> tuple[Any, str]:
    query = urllib.parse.urlencode(
        [(k, str(v).lower() if isinstance(v, bool) else str(v)) for k, v in params.items() if v is not None]
    )
    url = f"{base}{path}" + (f"?{query}" if query else "")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Investering-Framework-Research/1.0", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {exc.code} for {url}: {body[:500]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"network error for {url}: {exc}") from exc
    return json.loads(raw), url


def norm(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def resolve_profile(query: str) -> tuple[dict[str, Any], dict[str, Any]]:
    result, search_url = get_json(
        GAMMA,
        "/public-search",
        {"q": query, "search_profiles": True, "limit_per_type": 20},
    )
    profiles = result.get("profiles") or [] if isinstance(result, dict) else []
    target = norm(query)
    exact = [p for p in profiles if target in {norm(p.get("name")), norm(p.get("pseudonym"))}]
    if len(exact) != 1:
        raise RuntimeError(
            f"identity unresolved: expected exactly one exact profile match for {query!r}, got {len(exact)}"
        )
    candidate = exact[0]
    wallet = candidate.get("proxyWallet")
    if not isinstance(wallet, str) or not WALLET_RE.fullmatch(wallet):
        raise RuntimeError("identity unresolved: exact profile match has no valid proxyWallet")
    verified, profile_url = get_json(GAMMA, "/public-profile", {"address": wallet})
    if norm(verified.get("proxyWallet")) != norm(wallet):
        raise RuntimeError("identity mismatch: public-profile proxyWallet differs from search result")
    audit = {
        "contract": "POLYMARKET_EXTERNAL_PROFILE_IDENTITY_v1",
        "query": query,
        "retrieved_at_utc": now_utc(),
        "search_url": search_url,
        "profile_url": profile_url,
        "proxy_wallet": wallet,
        "search_profile": candidate,
        "verified_profile": verified,
        "status": "IDENTITY_RESOLVED_SINGLE_EXACT_MATCH",
    }
    return audit, result


def save(path: Path, value: Any) -> dict[str, Any]:
    data = canonical(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {"path": str(path), "sha256": sha256_bytes(data), "bytes": len(data)}


def page_endpoint(
    *,
    out: Path,
    name: str,
    path: str,
    wallet: str,
    limit: int,
    max_offset: int,
    extra: dict[str, Any] | None = None,
) -> tuple[list[Any], list[dict[str, Any]]]:
    rows: list[Any] = []
    pages: list[dict[str, Any]] = []
    offset = 0
    page_no = 0
    while True:
        params: dict[str, Any] = {"user": wallet, "limit": limit, "offset": offset}
        if extra:
            params.update(extra)
        payload, url = get_json(DATA, path, params)
        if not isinstance(payload, list):
            raise RuntimeError(f"{name}: expected list response, got {type(payload).__name__}")
        page_file = out / "raw" / name / f"page_{page_no:04d}.json"
        meta = save(page_file, payload)
        pages.append({**meta, "url": url, "offset": offset, "rows": len(payload)})
        rows.extend(payload)
        if len(payload) < limit:
            break
        next_offset = offset + limit
        if next_offset > max_offset:
            raise RuntimeError(
                f"{name}: pagination cap reached at offset {offset}; use time-window paging before accepting completeness"
            )
        offset = next_offset
        page_no += 1
        time.sleep(0.05)
    return rows, pages


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Read-only forensic Polymarket capture for an external strategy profile."
    )
    ap.add_argument("--query", default="EdgeOnchain")
    ap.add_argument("--output-root", type=Path, required=True)
    args = ap.parse_args()

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = args.output_root / run_id
    out.mkdir(parents=True, exist_ok=False)

    identity, search_raw = resolve_profile(args.query)
    wallet = identity["proxy_wallet"]
    artifacts: dict[str, Any] = {}
    artifacts["identity"] = save(out / "identity.json", identity)
    artifacts["profile_search_raw"] = save(out / "raw" / "profile_search.json", search_raw)

    activity, activity_pages = page_endpoint(
        out=out,
        name="activity",
        path="/activity",
        wallet=wallet,
        limit=500,
        max_offset=5000,
        extra={"start": 1, "sortDirection": "ASC", "excludeDepositsWithdrawals": False},
    )
    trades, trade_pages = page_endpoint(
        out=out,
        name="trades",
        path="/trades",
        wallet=wallet,
        limit=10000,
        max_offset=10000,
        extra={"start": 1, "takerOnly": False},
    )
    closed, closed_pages = page_endpoint(
        out=out,
        name="closed_positions",
        path="/closed-positions",
        wallet=wallet,
        limit=50,
        max_offset=100000,
        extra={"sortBy": "TIMESTAMP", "sortDirection": "ASC"},
    )

    artifacts["activity"] = save(out / "activity.json", activity)
    artifacts["trades"] = save(out / "trades.json", trades)
    artifacts["closed_positions"] = save(out / "closed_positions.json", closed)

    manifest = {
        "contract": "POLYMARKET_EXTERNAL_STRATEGY_CAPTURE_v1",
        "authority": "RESEARCH_READ_ONLY",
        "created_at_utc": now_utc(),
        "run_id": run_id,
        "query": args.query,
        "proxy_wallet": wallet,
        "completeness": "FAIL_CLOSED_ON_PAGINATION_CAP",
        "artifacts": artifacts,
        "pages": {
            "activity": activity_pages,
            "trades": trade_pages,
            "closed_positions": closed_pages,
        },
        "counts": {
            "activity": len(activity),
            "trades": len(trades),
            "closed_positions": len(closed),
        },
        "notes": [
            "No execution or signing authority.",
            "takerOnly=false is intentional so capture is not restricted to taker-side trades.",
            "Maker/taker attribution still requires microstructure/on-chain reconstruction; do not infer role solely from this capture.",
            "If pagination caps are hit, the run fails instead of silently claiming complete history.",
        ],
    }
    artifacts["manifest"] = save(out / "MANIFEST.json", manifest)
    print(
        json.dumps(
            {
                "status": "CAPTURED",
                "run_id": run_id,
                "proxy_wallet": wallet,
                "counts": manifest["counts"],
                "manifest": str(out / "MANIFEST.json"),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
