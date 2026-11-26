"""Capture exact public Kompas Live bytes for research custody, never scoring.

Offline input only. Caller observation clock is NOT authenticated publication/PIT.
No production integration, network, scheduler, model, outcome or trade authority.
"""
import argparse
import base64
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import tempfile

CONTRACT = "KOMPAS_LIVE_MEMORY_CAPTURE_v1"
SOURCE = "https://donh91.github.io/Investering-Framework-Archive-v1/data/kompas-live.json"
MAX_BYTES = 4 * 1024 * 1024
FLAGS = {"research_only": True, "official_forecast": False,
         "compass_probability_claim": False, "trading": False,
         "promotion": False, "site_synthesis": False}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError("nonfinite JSON constant")


def parse(raw, max_bytes=MAX_BYTES):
    if not isinstance(raw, bytes) or not 0 < len(raw) <= max_bytes:
        raise ValueError("invalid packet size")
    doc = json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                     parse_constant=invalid_constant)
    if not isinstance(doc, dict):
        raise ValueError("object required")
    return doc


def utc(value):
    if not isinstance(value, str):
        raise ValueError("timestamp required")
    clock = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if clock.tzinfo is None:
        raise ValueError("timezone required")
    return clock.astimezone(dt.timezone.utc)


def iso(clock):
    return clock.isoformat().replace("+00:00", "Z")


def capture(raw, observed_at):
    doc = parse(raw)
    if doc.get("contract") != "KOMPAS_LIVE_PATH_v1":
        raise ValueError("wrong source contract")
    authority = doc.get("authority", {})
    if not isinstance(authority, dict) or any(authority.get(k) is not v for k, v in FLAGS.items()):
        raise ValueError("unexpected source authority")
    claimed = doc.pop("path_sha256", None)
    canonical = json.dumps(doc, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, allow_nan=False).encode("utf-8")
    if claimed != sha(canonical):
        raise ValueError("source seal mismatch")
    issued = utc(doc["generated_at_utc"])
    observed = utc(observed_at)
    if issued > observed:
        raise ValueError("issue after observation")
    status = doc.get("status")
    assets = doc.get("assets")
    if status not in ("OK", "PARTIAL", "UNAVAILABLE") or not isinstance(assets, dict) or set(assets) != {"BTC", "ETH"}:
        raise ValueError("invalid source status or assets")
    if any(not isinstance(a, dict) or a.get("status") not in ("OK", "UNAVAILABLE")
           for a in assets.values()):
        raise ValueError("invalid asset status")
    count = sum(a["status"] == "OK" for a in assets.values())
    if status != ("OK" if count == 2 else "PARTIAL" if count == 1 else "UNAVAILABLE"):
        raise ValueError("status mismatch")
    # Preserve even unavailable and late captures, never silently select successes.
    return {"contract": CONTRACT, "source_url_label": SOURCE,
            "source_contract": doc["contract"], "generated_at_utc": iso(issued),
            "observer_reported_at_utc": iso(observed),
            "source_status": status, "source_seal_sha256": claimed,
            "source_bytes": len(raw), "source_bytes_sha256": sha(raw),
            "source_bytes_base64": base64.b64encode(raw).decode("ascii"),
            "publication_authenticated": False, "pit_admitted": False,
            "scoring_authorized": False, "research_only": True}


def read_existing(path, expected_clock):
    if path.stat().st_size > 2 * MAX_BYTES:
        raise ValueError("existing capture too large")
    prior = parse(path.read_bytes(), 2 * MAX_BYTES)
    previous_raw = base64.b64decode(prior["source_bytes_base64"], validate=True)
    expected = capture(previous_raw, prior["observer_reported_at_utc"])
    if (json.dumps(prior, sort_keys=True, allow_nan=False) !=
            json.dumps(expected, sort_keys=True, allow_nan=False)
            or expected["generated_at_utc"] != expected_clock):
        raise ValueError("existing capture corruption")
    return previous_raw


def store(root, raw, observed_at):
    receipt = capture(raw, observed_at)
    issued = utc(receipt["generated_at_utc"])
    # Primary file is first write; divergent same-clock bytes get no-replace siblings.
    directory = Path(root) / issued.strftime("%Y/%m/%d")
    directory.mkdir(parents=True, exist_ok=True)
    dest = directory / (issued.strftime("%H%M%S") + ("%06d" % issued.microsecond) + "Z.json")
    payload = (json.dumps(receipt, sort_keys=True, indent=1) + "\n").encode("utf-8")
    fd, temporary = tempfile.mkstemp(dir=directory, prefix=".capture-")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, dest)  # atomic no-replace, same filesystem
            return dest, "CREATED"
        except FileExistsError:
            previous_raw = read_existing(dest, receipt["generated_at_utc"])
            if previous_raw == raw:
                return dest, "ALREADY_CAPTURED"
            conflict = dest.with_name(dest.stem + ".conflict-" + sha(raw)[:16] + ".json")
            try:
                os.link(temporary, conflict)
                return conflict, "CONFLICT"
            except FileExistsError:
                if read_existing(conflict, receipt["generated_at_utc"]) != raw:
                    raise ValueError("conflict digest-prefix collision or corruption")
                return conflict, "CONFLICT_ALREADY_CAPTURED"
    finally:
        os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--observed-at", required=True,
                        help="caller-reported timestamp, not trusted first-known proof")
    args = parser.parse_args()
    if args.packet.stat().st_size > MAX_BYTES:
        parser.error("packet too large")
    dest, status = store(args.archive, args.packet.read_bytes(), args.observed_at)
    print(json.dumps({"status": status, "path": str(dest), "scoring_authorized": False}))


if __name__ == "__main__":
    main()
