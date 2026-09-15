from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import io
import json
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

PUMP_PROGRAM_ID = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _zip_member_by_basename(zf: zipfile.ZipFile, basename: str) -> str:
    for name in zf.namelist():
        if Path(name).name == basename:
            return name
    raise FileNotFoundError(basename)


def _rows(zf: zipfile.ZipFile, member: str) -> Iterable[dict[str, Any]]:
    raw = zf.read(member)
    stream = gzip.GzipFile(fileobj=io.BytesIO(raw), mode="rb") if member.endswith(".gz") else io.BytesIO(raw)
    for line in stream:
        if line.strip():
            yield json.loads(line)


def _rpc_get_transaction(rpc_url: str, signature: str, *, timeout: int = 20) -> tuple[str, dict[str, Any] | None]:
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            signature,
            {
                "encoding": "jsonParsed",
                "commitment": "finalized",
                "maxSupportedTransactionVersion": 0,
            },
        ],
    }).encode("utf-8")
    req = urllib.request.Request(
        rpc_url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "MemeAlphaResearch/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return f"HTTP_{exc.code}", None
    except Exception as exc:  # research probe, preserve failure class not secrets
        return f"ERROR_{type(exc).__name__}", None
    if body.get("error"):
        code = body["error"].get("code", "UNKNOWN") if isinstance(body["error"], dict) else "UNKNOWN"
        return f"RPC_ERROR_{code}", None
    if body.get("result") is None:
        return "NOT_FOUND", None
    return "OK", body["result"]


def _account_sets(tx: dict[str, Any]) -> tuple[set[str], set[str]]:
    message = (((tx.get("transaction") or {}).get("message")) or {})
    keys = message.get("accountKeys") or []
    accounts: set[str] = set()
    signers: set[str] = set()
    for item in keys:
        if isinstance(item, dict):
            pubkey = item.get("pubkey")
            if pubkey:
                accounts.add(str(pubkey))
                if item.get("signer") is True:
                    signers.add(str(pubkey))
        elif isinstance(item, str):
            accounts.add(item)
    return accounts, signers


def _has_pump_evidence(tx: dict[str, Any]) -> bool:
    accounts, _ = _account_sets(tx)
    if PUMP_PROGRAM_ID in accounts:
        return True
    logs = ((tx.get("meta") or {}).get("logMessages")) or []
    return any(PUMP_PROGRAM_ID in str(line) for line in logs)


def _epoch_guess(value: Any) -> tuple[str, int | None]:
    try:
        x = int(value)
    except (TypeError, ValueError):
        return "UNPARSEABLE", None
    if x > 10**14:
        return "MICROSECONDS", x // 1_000_000
    if x > 10**11:
        return "MILLISECONDS", x // 1_000
    if x > 10**9:
        return "SECONDS", x
    return "NON_EPOCH_OR_RELATIVE", None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rpc-url", default="https://api.mainnet-beta.solana.com")
    ap.add_argument("--sample-rows", type=int, default=24)
    ap.add_argument("--max-signatures", type=int, default=40)
    ap.add_argument("--sleep-seconds", type=float, default=0.30)
    args = ap.parse_args()

    zip_path = Path(args.zip)
    with zipfile.ZipFile(zip_path) as zf:
        member = _zip_member_by_basename(zf, "sniper_cohorts_intra.jsonl.gz")
        all_rows = list(_rows(zf, member))

    # Deterministic, content-derived sample rather than first-N/cherry-picked rows.
    ranked = sorted(all_rows, key=lambda r: _hash(str(r.get("mint", ""))))
    sample = ranked[: max(1, args.sample_rows)]

    row_shape = collections.Counter()
    detected_units = collections.Counter()
    detected_epochs: list[int] = []
    for row in all_rows:
        wallets = row.get("wallets") or []
        sigs = row.get("tx_sigs") or []
        row_shape[(len(wallets), len(sigs))] += 1
        unit, epoch = _epoch_guess(row.get("detected_at"))
        detected_units[unit] += 1
        if epoch is not None:
            detected_epochs.append(epoch)

    selected: list[tuple[dict[str, Any], str]] = []
    for row in sample:
        for sig in row.get("tx_sigs") or []:
            selected.append((row, str(sig)))
    # Deduplicate signatures while retaining the first deterministic row association.
    seen: set[str] = set()
    deduped: list[tuple[dict[str, Any], str]] = []
    for row, sig in selected:
        if sig in seen:
            continue
        seen.add(sig)
        deduped.append((row, sig))
        if len(deduped) >= args.max_signatures:
            break

    status_counts: collections.Counter[str] = collections.Counter()
    pump_tx_count = 0
    tx_success = 0
    row_wallets_in_any_account = 0
    row_wallets_as_signer = 0
    total_row_wallet_checks = 0
    tx_blocktimes: list[int] = []
    detection_minus_block: list[int] = []
    tx_error_free = 0

    for idx, (row, sig) in enumerate(deduped):
        status, tx = _rpc_get_transaction(args.rpc_url, sig)
        status_counts[status] += 1
        if tx is None:
            if idx + 1 < len(deduped):
                time.sleep(args.sleep_seconds)
            continue
        tx_success += 1
        accounts, signers = _account_sets(tx)
        wallets = {str(w) for w in (row.get("wallets") or [])}
        total_row_wallet_checks += len(wallets)
        row_wallets_in_any_account += sum(1 for wallet in wallets if wallet in accounts)
        row_wallets_as_signer += sum(1 for wallet in wallets if wallet in signers)
        if _has_pump_evidence(tx):
            pump_tx_count += 1
        if (tx.get("meta") or {}).get("err") is None:
            tx_error_free += 1
        block_time = tx.get("blockTime")
        if isinstance(block_time, int):
            tx_blocktimes.append(block_time)
            _, detected_epoch = _epoch_guess(row.get("detected_at"))
            if detected_epoch is not None:
                detection_minus_block.append(detected_epoch - block_time)
        if idx + 1 < len(deduped):
            time.sleep(args.sleep_seconds)

    def stats(values: list[int]) -> dict[str, Any]:
        if not values:
            return {"n": 0}
        s = sorted(values)
        return {
            "n": len(s),
            "min": s[0],
            "median": s[len(s)//2],
            "max": s[-1],
        }

    result = {
        "experiment": "RED_COHORT_TX_RECONSTRUCTION_FEASIBILITY_v1",
        "source": "RED-COHORT-2026-v1.1.1",
        "sample_design": {
            "all_intra_rows": len(all_rows),
            "deterministic_sample_rows": len(sample),
            "unique_tx_signatures_requested": len(deduped),
            "selection_rule": "sort all rows by SHA256(mint), take first N; then dedupe tx_sigs and cap signatures",
            "sample_identity_sha256": _hash("|".join(sorted(_hash(str(r.get('mint',''))) for r in sample))),
            "raw_mints_or_signatures_logged": False,
        },
        "row_shape": {
            "wallet_count_equals_tx_sig_count_rows": sum(n for (w, s), n in row_shape.items() if w == s),
            "wallet_count_differs_tx_sig_count_rows": sum(n for (w, s), n in row_shape.items() if w != s),
            "most_common_wallet_sig_count_pairs": [
                {"wallets": pair[0], "tx_sigs": pair[1], "rows": n}
                for pair, n in row_shape.most_common(12)
            ],
        },
        "detected_at_semantics": {
            "unit_guess_counts": dict(sorted(detected_units.items())),
            "epoch_range_utc": {
                "min": datetime.fromtimestamp(min(detected_epochs), tz=timezone.utc).isoformat().replace("+00:00", "Z") if detected_epochs else None,
                "max": datetime.fromtimestamp(max(detected_epochs), tz=timezone.utc).isoformat().replace("+00:00", "Z") if detected_epochs else None,
            },
        },
        "rpc_reconstruction": {
            "rpc_host_class": "PUBLIC_SOLANA_MAINNET_RPC_NO_AUTH",
            "status_counts": dict(sorted(status_counts.items())),
            "transactions_resolved": tx_success,
            "transactions_with_pump_program_evidence": pump_tx_count,
            "transactions_error_free": tx_error_free,
            "row_wallet_checks": total_row_wallet_checks,
            "row_wallets_present_in_any_tx_account": row_wallets_in_any_account,
            "row_wallets_present_as_tx_signer": row_wallets_as_signer,
            "wallet_account_match_rate": round(row_wallets_in_any_account / total_row_wallet_checks, 6) if total_row_wallet_checks else None,
            "wallet_signer_match_rate": round(row_wallets_as_signer / total_row_wallet_checks, 6) if total_row_wallet_checks else None,
            "blocktime_stats": stats(tx_blocktimes),
            "detected_at_minus_tx_blocktime_seconds": stats(detection_minus_block),
        },
        "decision_logic": {
            "reconstruction_path_supported_if": [
                "A material fraction of sampled tx_sigs resolve on chain",
                "Listed cohort wallets are present in the corresponding transaction accounts/signers",
                "Pump program evidence is present",
                "detected_at timing is compatible with transaction block times",
            ],
            "does_not_prove": [
                "wallet independence",
                "profitability",
                "sellable return",
                "cohort intent",
            ],
        },
        "authority": {
            "research_only": True,
            "automatic_trading": False,
            "buy_now_promotion": False,
            "live_threshold_change": False,
        },
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
