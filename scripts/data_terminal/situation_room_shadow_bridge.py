from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

CONTRACT = "SITUATION_ROOM_VERIFICATION_SHADOW_BRIDGE_v1"
AUTHORITY = "SHADOW_RESEARCH_ONLY_NON_CANONICAL"
USER_AGENT = "InvesteringFramework-SituationRoomShadowBridge/1.0 research-only"

TRUSTED_PRIMARY_HOST_SUFFIXES = (
    "federalreserve.gov",
    "ecb.europa.eu",
    "bls.gov",
    "bea.gov",
    "sec.gov",
    "treasury.gov",
    "cftc.gov",
    "eia.gov",
    "whitehouse.gov",
    "fincen.gov",
    "congress.gov",
    "bankofengland.co.uk",
    "bis.org",
    "imf.org",
)

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "for", "on", "in", "with", "from",
    "as", "at", "by", "is", "are", "was", "were", "be", "been", "today", "new",
    "situation", "room", "briefing", "market", "markets", "press", "release",
}


class LinkTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._anchor: list[str] = []
        self.text_parts: list[str] = []
        self.title_parts: list[str] = []
        self._in_title = False
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {k.lower(): (v or "") for k, v in attrs}
        if tag.lower() == "a":
            self._href = values.get("href")
            self._anchor = []
        elif tag.lower() == "title":
            self._in_title = True
        elif tag.lower() == "meta":
            key = values.get("property") or values.get("name")
            content = values.get("content")
            if key and content:
                self.meta[key.lower()] = content.strip()

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href:
            text = " ".join("".join(self._anchor).split())
            self.links.append((self._href, text))
            self._href = None
            self._anchor = []
        elif tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        self.text_parts.append(data)
        if self._href is not None:
            self._anchor.append(data)
        if self._in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return self.meta.get("og:title") or " ".join("".join(self.title_parts).split())

    @property
    def text(self) -> str:
        return " ".join(" ".join(self.text_parts).split())


@dataclass
class FetchResult:
    url: str
    status: str
    body: bytes
    error: str | None


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fetch(url: str, timeout: int) -> FetchResult:
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
        with urlopen(req, timeout=timeout) as response:
            return FetchResult(url, "PASS", response.read(1_500_000), None)
    except Exception as exc:
        return FetchResult(url, "FAIL", b"", type(exc).__name__)


def parse_html(body: bytes) -> LinkTextParser:
    parser = LinkTextParser()
    parser.feed(body.decode("utf-8", errors="replace"))
    return parser


def tokens(value: str) -> set[str]:
    out: set[str] = set()
    for token in re.findall(r"[a-z0-9]+", value.lower()):
        if token in STOPWORDS:
            continue
        if len(token) >= 3 or token.isdigit():
            out.add(token)
    return out


def overlap(a: str, b: str) -> tuple[float, list[str]]:
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return 0.0, []
    common = sorted(ta & tb)
    score = len(common) / max(1, min(len(ta), len(tb)))
    return score, common


def trusted_primary(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    return any(host == suffix or host.endswith("." + suffix) for suffix in TRUSTED_PRIMARY_HOST_SUFFIXES)


def owner_primary_match(discovery: dict, events: list[dict]) -> dict | None:
    title = str(discovery.get("title") or "")
    best: tuple[float, list[str], dict] | None = None
    for event in events:
        if event.get("verification_status") != "PRIMARY_SOURCE_VERIFIED":
            continue
        score, common = overlap(title, str(event.get("title") or ""))
        if len(common) < 2 or score < 0.45:
            continue
        if best is None or score > best[0]:
            best = (score, common, event)
    if best is None:
        return None
    score, common, event = best
    return {
        "verification_method": "OWNER_PRIMARY_EVENT_TITLE_OVERLAP",
        "verification_status": "PRIMARY_EVENT_CORROBORATED",
        "match_score": round(score, 4),
        "shared_tokens": common[:20],
        "primary_event_id": event.get("event_id"),
        "primary_title": event.get("title"),
        "primary_event_time_utc": event.get("event_time_utc"),
        "primary_source_receipts": event.get("source_receipts", []),
    }


def linked_primary_match(discovery: dict, timeout: int) -> dict | None:
    source_url = str(discovery.get("url") or "")
    title = str(discovery.get("title") or "")
    if not source_url:
        return None
    page = fetch(source_url, timeout)
    if page.status != "PASS":
        return None
    parsed = parse_html(page.body)
    candidates: list[tuple[str, str]] = []
    seen: set[str] = set()
    for href, anchor in parsed.links:
        absolute = urljoin(source_url, href)
        if absolute in seen or not trusted_primary(absolute):
            continue
        seen.add(absolute)
        candidates.append((absolute, anchor))
        if len(candidates) >= 8:
            break

    best: tuple[float, list[str], str, str] | None = None
    for url, anchor in candidates:
        target = fetch(url, timeout)
        if target.status != "PASS":
            continue
        target_parser = parse_html(target.body)
        comparison = f"{anchor} {target_parser.title}"
        score, common = overlap(title, comparison)
        if len(common) < 2 or score < 0.45:
            continue
        if best is None or score > best[0]:
            best = (score, common, url, anchor)
    if best is None:
        return None
    score, common, url, anchor = best
    return {
        "verification_method": "SITUATION_ROOM_LINKED_PRIMARY_SOURCE",
        "verification_status": "PRIMARY_LINK_CORROBORATED",
        "match_score": round(score, 4),
        "shared_tokens": common[:20],
        "primary_url": url,
        "primary_anchor": anchor,
    }


def stable_id(discovery: dict) -> str:
    basis = "|".join([
        str(discovery.get("url") or ""),
        str(discovery.get("event_time_utc") or ""),
        str(discovery.get("title") or ""),
    ])
    return "SRSH_" + hashlib.sha256(basis.encode()).hexdigest()[:20]


def load_owner(source_root: Path) -> tuple[dict, Path]:
    pointer = json.loads((source_root / "LATEST.json").read_text())
    source_path = Path(pointer["path"])
    return json.loads(source_path.read_text()), source_path


def already_processed(output_root: Path, source_run_id: str) -> bool:
    pointer = output_root / "LATEST.json"
    if not pointer.exists():
        return False
    try:
        prior = json.loads(pointer.read_text())
    except json.JSONDecodeError:
        return False
    return prior.get("source_run_id") == source_run_id


def run(source_root: Path, output_root: Path, timeout: int) -> dict:
    owner, source_path = load_owner(source_root)
    source_run_id = str(owner.get("run_id") or "")
    if not source_run_id:
        raise ValueError("owner result missing run_id")
    if already_processed(output_root, source_run_id):
        return {"status": "NO_CHANGE", "source_run_id": source_run_id}

    discoveries = list(owner.get("current_unverified_discoveries") or [])
    events = list(owner.get("events") or [])
    accepted: list[dict] = []
    pending: list[dict] = []

    for discovery in discoveries:
        verification = owner_primary_match(discovery, events)
        if verification is None:
            verification = linked_primary_match(discovery, timeout)
        record = {
            "shadow_id": stable_id(discovery),
            "source": "SITUATION_ROOM",
            "title": discovery.get("title"),
            "url": discovery.get("url"),
            "event_time_utc": discovery.get("event_time_utc"),
            "detection_time_utc": discovery.get("detection_time_utc"),
            "source_receipt": discovery.get("source_receipt"),
            "canonical_effect": False,
            "market_state_effect": False,
            "portfolio_effect": False,
        }
        if verification is not None:
            record.update(verification)
            record["shadow_admission"] = "ACCEPTED_VERIFIED_CONTEXT"
            accepted.append(record)
        else:
            record["verification_status"] = "PENDING_PRIMARY_VERIFICATION"
            record["shadow_admission"] = "NOT_ADMITTED_PENDING_VERIFICATION"
            pending.append(record)

    if accepted:
        status = "SHADOW_HANDOFF_READY"
    elif discoveries:
        status = "PENDING_VERIFICATION"
    else:
        status = "NO_CURRENT_SITUATION_ROOM_DISCOVERY"

    result = {
        "contract": CONTRACT,
        "authority": AUTHORITY,
        "generated_at_utc": utc_now(),
        "source_run_id": source_run_id,
        "source_owner_contract": owner.get("contract"),
        "source_owner_path": source_path.as_posix(),
        "observation_date_utc": owner.get("observation_date_utc"),
        "status": status,
        "verified_shadow_context": accepted,
        "pending_verification": pending,
        "verification_policy": {
            "situation_room_is_discovery_only": True,
            "automatic_admission_requires_primary_corroboration": True,
            "accepted_methods": [
                "OWNER_PRIMARY_EVENT_TITLE_OVERLAP",
                "SITUATION_ROOM_LINKED_PRIMARY_SOURCE",
            ],
            "minimum_title_overlap": 0.45,
            "minimum_shared_tokens": 2,
        },
        "authority_firewall": {
            "canonical_effect": False,
            "market_state_effect": False,
            "portfolio_effect": False,
            "topup_authority": False,
            "execution_authority": False,
        },
    }
    write_outputs(output_root, result)
    return result


def write_outputs(root: Path, result: dict) -> None:
    date_utc = str(result.get("observation_date_utc") or datetime.now(timezone.utc).date().isoformat())
    year, month, _ = date_utc.split("-")
    dated = root / year / month / f"{date_utc}.json"
    dated.parent.mkdir(parents=True, exist_ok=True)
    dated.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    root.mkdir(parents=True, exist_ok=True)
    pointer = {
        "contract": "SITUATION_ROOM_VERIFICATION_SHADOW_BRIDGE_LATEST_v1",
        "authority": AUTHORITY,
        "source_run_id": result["source_run_id"],
        "observation_date_utc": date_utc,
        "status": result["status"],
        "verified_count": len(result["verified_shadow_context"]),
        "pending_count": len(result["pending_verification"]),
        "path": dated.as_posix(),
        "canonical_effect": False,
        "portfolio_effect": False,
    }
    (root / "LATEST.json").write_text(json.dumps(pointer, sort_keys=True, indent=2) + "\n")

    ledger = root / "VERIFIED_SHADOW_LEDGER.jsonl"
    existing: set[str] = set()
    if ledger.exists():
        for line in ledger.read_text().splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("shadow_id"):
                existing.add(str(row["shadow_id"]))
    with ledger.open("a", encoding="utf-8") as fh:
        for row in result["verified_shadow_context"]:
            if row["shadow_id"] in existing:
                continue
            ledger_row = dict(row)
            ledger_row["shadow_recorded_at_utc"] = result["generated_at_utc"]
            fh.write(json.dumps(ledger_row, sort_keys=True, separators=(",", ":")) + "\n")
            existing.add(row["shadow_id"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=Path("03_DAILY_CAPTURE_LOGS/catalyst_overlay/situation_room"))
    parser.add_argument("--output-root", type=Path, default=Path("04_MARKET_LEARNING/external_research/situation_room_shadow"))
    parser.add_argument("--timeout", type=int, default=8)
    args = parser.parse_args()
    result = run(args.source_root, args.output_root, args.timeout)
    print(json.dumps({
        "status": result.get("status"),
        "source_run_id": result.get("source_run_id"),
        "verified_count": len(result.get("verified_shadow_context", [])),
        "pending_count": len(result.get("pending_verification", [])),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
