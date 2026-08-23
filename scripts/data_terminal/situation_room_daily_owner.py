from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

CONTRACT = "SITUATION_ROOM_DAILY_OWNER_v1"
AUTHORITY = "RESEARCH_ONLY_NON_CANONICAL"
USER_AGENT = "InvesteringFramework-SituationRoomOwner/1.0 research-only"

KEYWORDS = (
    "crypto", "bitcoin", "ethereum", "digital asset", "stablecoin", "tokenized",
    "treasury buyback", "buyback", "liquidity", "fomc", "interest rate", "rates",
    "sanction", "cyber", "hack", "security breach", "geopolit", "tariff",
    "market structure", "clarity act", "securities law", "regulation crypto",
)

SOURCES = (
    ("SITUATION_ROOM", "DISCOVERY_ONLY", "https://situationroom.space/briefings"),
    ("SEC", "PRIMARY", "https://www.sec.gov/newsroom/press-releases"),
    ("TREASURY", "PRIMARY", "https://home.treasury.gov/news/press-releases"),
    ("WHITE_HOUSE", "PRIMARY", "https://www.whitehouse.gov/news/"),
    ("CFTC", "PRIMARY", "https://www.cftc.gov/PressRoom/PressReleases"),
    ("FEDERAL_RESERVE", "PRIMARY", "https://www.federalreserve.gov/newsevents/pressreleases.htm"),
)

STOPWORDS = {
    "the", "a", "an", "and", "of", "to", "for", "on", "in", "with", "from",
    "press", "release", "statement", "announces", "announcement", "new", "proposed",
    "proposes", "meeting", "update", "federal", "u", "s", "us",
}

MONTH_DATE_RE = re.compile(
    r"\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    r"\.?\s+(\d{1,2}),\s+(20\d{2})\b",
    re.I,
)
MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._anchor: list[str] = []
        self.title_parts: list[str] = []
        self._in_title = False
        self.meta: dict[str, str] = {}
        self.times: list[str] = []

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
        elif tag.lower() == "time" and values.get("datetime"):
            self.times.append(values["datetime"].strip())

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href:
            text = " ".join("".join(self._anchor).split())
            self.links.append((self._href, text))
            self._href = None
            self._anchor = []
        elif tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._anchor.append(data)
        if self._in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return self.meta.get("og:title") or " ".join("".join(self.title_parts).split())


@dataclass
class FetchResult:
    url: str
    status: str
    http_status: int | None
    fetched_at_utc: str
    body: bytes
    error: str | None

    def receipt(self, source_id: str, role: str) -> dict:
        return {
            "source_id": source_id,
            "role": role,
            "url": self.url,
            "status": self.status,
            "http_status": self.http_status,
            "fetched_at_utc": self.fetched_at_utc,
            "bytes": len(self.body),
            "sha256": hashlib.sha256(self.body).hexdigest() if self.body else None,
            "error_class": self.error,
        }


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fetch(url: str, timeout: int = 15) -> FetchResult:
    stamp = utc_now()
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
        with urlopen(req, timeout=timeout) as response:
            body = response.read(2_000_000)
            return FetchResult(url, "PASS", getattr(response, "status", 200), stamp, body, None)
    except Exception as exc:  # network/source failures are evidence states, never no-event
        return FetchResult(url, "FAIL", None, stamp, b"", type(exc).__name__)


def parse_page(body: bytes) -> PageParser:
    parser = PageParser()
    parser.feed(body.decode("utf-8", errors="replace"))
    return parser


def relevant(text: str) -> bool:
    value = " ".join(text.lower().split())
    return any(keyword in value for keyword in KEYWORDS)


def normalize_published(raw: str | None) -> tuple[str | None, str]:
    if not raw:
        return None, "UNRESOLVED"
    value = raw.strip()
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"), "ASSUMED_UTC_FROM_SOURCE"
        return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"), "TIMESTAMP"
    except ValueError:
        pass
    match = re.search(r"(20\d{2})[-/](\d{1,2})[-/](\d{1,2})", value)
    if match:
        y, m, d = map(int, match.groups())
        return datetime(y, m, d, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"), "DATE_ONLY"
    match = MONTH_DATE_RE.search(value)
    if match:
        month_name, day, year = match.groups()
        month = MONTHS[month_name[:3].lower()]
        return datetime(int(year), month, int(day), tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"), "DATE_ONLY"
    return None, "UNRESOLVED"


def published_from_page(parser: PageParser, body: bytes) -> tuple[str | None, str]:
    for key in ("article:published_time", "date", "datepublished", "parsely-pub-date", "dc.date"):
        if key in parser.meta:
            value = normalize_published(parser.meta[key])
            if value[0]:
                return value
    for value in parser.times:
        normalized = normalize_published(value)
        if normalized[0]:
            return normalized
    text = body.decode("utf-8", errors="replace")
    for pattern in (
        r'"datePublished"\s*:\s*"([^"]+)"',
        r'"dateCreated"\s*:\s*"([^"]+)"',
    ):
        match = re.search(pattern, text, flags=re.I)
        if match:
            normalized = normalize_published(match.group(1))
            if normalized[0]:
                return normalized
    # Several primary public-sector pages expose a visible English publication date
    # without structured metadata. Parse only a full month/day/year token, never a year alone.
    normalized = normalize_published(text[:250_000])
    if normalized[0]:
        return normalized
    return None, "UNRESOLVED"


def family_key(title: str) -> str:
    tokens = re.findall(r"[a-z0-9]+", title.lower())
    keep = sorted({t for t in tokens if len(t) > 2 and t not in STOPWORDS})[:18]
    basis = "|".join(keep) or title.lower().strip()
    return "EVF_" + hashlib.sha256(basis.encode()).hexdigest()[:16]


def classify(title: str, source_id: str) -> tuple[str, str, str, list[str]]:
    t = title.lower()
    if any(k in t for k in ("regulation crypto", "crypto asset", "digital asset", "clarity act", "stablecoin", "tokenized")):
        return "STRUCTURAL", "REGULATORY_CATALYST", "WEEKS_TO_MONTHS", ["CATALYST_NEWS", "MACRO_RISK", "CRYPTO_POLICY"]
    if "buyback" in t or (source_id == "TREASURY" and "liquidity" in t):
        return "SYSTEMIC", "MACRO_LIQUIDITY_POLICY", "DAYS_TO_MONTHS", ["MACRO_RISK", "LIQUIDITY", "BTC", "ETH"]
    if any(k in t for k in ("fomc", "interest rate", "rates", "monetary policy")):
        return "MARKET_RELEVANT", "MACRO_POLICY_CONTEXT", "DAYS_TO_WEEKS", ["MACRO_RISK", "LIQUIDITY", "BTC", "ETH"]
    if any(k in t for k in ("sanction", "geopolit", "tariff")):
        return "SYSTEMIC", "MACRO_OR_GEOPOLITICAL_SHOCK", "DAYS_TO_WEEKS", ["MACRO_RISK", "BTC", "ETH", "LEVERAGE"]
    if any(k in t for k in ("hack", "cyber", "security breach")):
        return "MARKET_RELEVANT", "SECURITY_EVENT", "HOURS_TO_DAYS", ["CATALYST_NEWS", "LEVERAGE", "RISK"]
    return "MARKET_RELEVANT", "GENERAL_MARKET_CATALYST", "HOURS_TO_DAYS", ["CATALYST_NEWS", "MACRO_RISK"]


def source_candidate_allowed(source_id: str, base_url: str, absolute: str) -> bool:
    parsed = urlparse(absolute)
    base = urlparse(base_url)
    path = parsed.path.rstrip("/")
    base_path = base.path.rstrip("/")
    if path == base_path:
        return False
    low = path.lower()
    if source_id == "SITUATION_ROOM":
        return low.startswith("/briefing/")
    if source_id == "SEC":
        return low.startswith("/newsroom/press-releases/")
    if source_id == "TREASURY":
        return low.startswith("/news/press-releases/")
    if source_id == "CFTC":
        return low.startswith("/pressroom/pressreleases/")
    if source_id == "FEDERAL_RESERVE":
        if not low.startswith("/newsevents/pressreleases/"):
            return False
        name = Path(parsed.path).name.lower()
        return re.fullmatch(r"20\d{2}-press-[a-z0-9-]+\.htm", name) is None
    if source_id == "WHITE_HOUSE":
        return low.startswith((
            "/articles/", "/fact-sheets/", "/remarks/", "/presidential-actions/",
            "/briefings-statements/", "/news/",
        ))
    # Synthetic/unknown sources used by deterministic tests retain same-host behavior.
    return True


def candidate_links(source_id: str, base_url: str, parser: PageParser) -> Iterable[tuple[str, str]]:
    seen: set[str] = set()
    host = urlparse(base_url).netloc
    for href, text in parser.links:
        absolute = urljoin(base_url, href)
        parsed = urlparse(absolute)
        if parsed.scheme not in {"http", "https"} or parsed.netloc != host:
            continue
        if not source_candidate_allowed(source_id, base_url, absolute):
            continue
        label = f"{text} {absolute}"
        if not relevant(label) or absolute in seen:
            continue
        seen.add(absolute)
        yield absolute, text


def observation_date(event_time: str | None) -> str | None:
    return event_time[:10] if event_time and len(event_time) >= 10 else None


def run(output_root: Path, date_utc: str, timeout: int = 15) -> dict:
    detection = utc_now()
    receipts: list[dict] = []
    events: list[dict] = []
    discoveries: list[dict] = []
    unresolved: list[dict] = []
    primary_pass = 0
    primary_total = sum(1 for _, role, _ in SOURCES if role == "PRIMARY")

    for source_id, role, landing_url in SOURCES:
        landing = fetch(landing_url, timeout=timeout)
        receipts.append(landing.receipt(source_id, role))
        if role == "PRIMARY" and landing.status == "PASS":
            primary_pass += 1
        if landing.status != "PASS":
            continue
        parser = parse_page(landing.body)
        for url, anchor in candidate_links(source_id, landing_url, parser):
            page = fetch(url, timeout=timeout)
            page_receipt = page.receipt(source_id, role)
            if page.status != "PASS":
                candidate = {
                    "source_id": source_id,
                    "source_role": role,
                    "url": url,
                    "title": anchor or url,
                    "event_time_utc": None,
                    "event_time_precision": "UNRESOLVED",
                    "detection_time_utc": detection,
                    "reason": "CANDIDATE_FETCH_FAILED",
                    "source_receipt": page_receipt,
                }
                if role == "DISCOVERY_ONLY":
                    candidate["verification_status"] = "DISCOVERY_FETCH_FAILED"
                    discoveries.append(candidate)
                else:
                    candidate["verification_status"] = "PRIMARY_CANDIDATE_FETCH_FAILED"
                    unresolved.append(candidate)
                continue
            detail = parse_page(page.body)
            title = detail.title or anchor or url
            if not relevant(title + " " + page.body[:100_000].decode("utf-8", errors="replace")):
                continue
            event_time, precision = published_from_page(detail, page.body)
            candidate = {
                "source_id": source_id,
                "source_role": role,
                "title": title,
                "url": url,
                "event_time_utc": event_time,
                "event_time_precision": precision,
                "detection_time_utc": detection,
                "source_receipt": page_receipt,
            }
            if role == "DISCOVERY_ONLY":
                candidate["verification_status"] = "DISCOVERY_UNVERIFIED"
                discoveries.append(candidate)
                continue
            if not event_time:
                candidate["verification_status"] = "EVENT_TIME_UNRESOLVED"
                unresolved.append(candidate)
                continue
            if observation_date(event_time) != date_utc:
                continue
            classification, subtype, duration, lanes = classify(title, source_id)
            event_id = "EVT_" + hashlib.sha256(url.encode()).hexdigest()[:20]
            events.append({
                "event_id": event_id,
                "event_family_id": family_key(title),
                "title": title,
                "event_time_utc": event_time,
                "event_time_precision": precision,
                "detection_time_utc": detection,
                "classification": classification,
                "catalyst_subtype": subtype,
                "confidence": "HIGH_PRIMARY_SOURCE",
                "expected_duration": duration,
                "affected_framework_lanes": lanes,
                "verification_status": "PRIMARY_SOURCE_VERIFIED",
                "source_receipts": [page_receipt],
                "causal_authority": "NONE",
            })

    current_discoveries = [
        item for item in discoveries
        if item.get("verification_status") == "DISCOVERY_UNVERIFIED"
        and observation_date(item.get("event_time_utc")) == date_utc
    ]

    if primary_pass == 0:
        daily_result = "COLLECTOR_FAILURE"
    elif primary_pass < 3:
        daily_result = "UNKNOWN_DUE_TO_SOURCE_FAILURE"
    elif events:
        daily_result = "MATERIAL_CATALYSTS_FOUND"
    elif unresolved:
        daily_result = "REVIEW_REQUIRED_UNRESOLVED_CANDIDATES"
    elif current_discoveries:
        daily_result = "REVIEW_REQUIRED_UNVERIFIED_DISCOVERY"
    else:
        daily_result = "NO_NEW_MATERIAL_CATALYST"

    result = {
        "contract": CONTRACT,
        "authority": AUTHORITY,
        "run_id": "SRDO_" + hashlib.sha256((date_utc + detection).encode()).hexdigest()[:16],
        "observation_date_utc": date_utc,
        "detection_time_utc": detection,
        "run_status": "PASS" if daily_result in {"MATERIAL_CATALYSTS_FOUND", "NO_NEW_MATERIAL_CATALYST"} else "DEGRADED",
        "daily_result": daily_result,
        "source_coverage": {"primary_pass": primary_pass, "primary_total": primary_total, "receipts": receipts},
        "events": events,
        "unverified_discoveries": discoveries,
        "current_unverified_discoveries": current_discoveries,
        "unresolved_candidates": unresolved,
        "market_reaction_observations": [],
        "market_reaction_separate_from_event": True,
        "shared_row_tournament_eligible": False,
        "retroactive_candidate_eligibility": False,
        "canonical_effect": False,
        "market_state_effect": False,
        "portfolio_effect": False,
        "situation_room_role": "DISCOVERY_ONLY",
    }
    write_outputs(output_root, result)
    return result


def write_outputs(root: Path, result: dict) -> None:
    date_utc = result["observation_date_utc"]
    year, month, _ = date_utc.split("-")
    dated = root / year / month / f"{date_utc}.json"
    dated.parent.mkdir(parents=True, exist_ok=True)
    dated.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    root.mkdir(parents=True, exist_ok=True)
    latest = {
        "contract": "SITUATION_ROOM_DAILY_OWNER_LATEST_POINTER_v1",
        "authority": AUTHORITY,
        "observation_date_utc": date_utc,
        "daily_result": result["daily_result"],
        "run_status": result["run_status"],
        "run_id": result["run_id"],
        "path": dated.as_posix(),
        "shared_row_tournament_eligible": False,
    }
    (root / "LATEST.json").write_text(json.dumps(latest, sort_keys=True, indent=2) + "\n")

    ledger = root / "EVENT_LEDGER.jsonl"
    existing: set[str] = set()
    if ledger.exists():
        for line in ledger.read_text().splitlines():
            try:
                row = json.loads(line)
                if row.get("event_id"):
                    existing.add(str(row["event_id"]))
            except json.JSONDecodeError:
                continue
    with ledger.open("a", encoding="utf-8") as fh:
        for event in result["events"]:
            if event["event_id"] in existing:
                continue
            row = dict(event)
            row["ledger_recorded_at_utc"] = result["detection_time_utc"]
            row["shared_row_tournament_eligible"] = False
            fh.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
            existing.add(event["event_id"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=Path("03_DAILY_CAPTURE_LOGS/catalyst_overlay/situation_room"))
    parser.add_argument("--date-utc", default=datetime.now(timezone.utc).date().isoformat())
    parser.add_argument("--timeout", type=int, default=15)
    args = parser.parse_args()
    result = run(args.output_root, args.date_utc, timeout=args.timeout)
    print(json.dumps({"run_id": result["run_id"], "daily_result": result["daily_result"], "run_status": result["run_status"]}, sort_keys=True))
    if result["daily_result"] == "COLLECTOR_FAILURE":
        raise SystemExit(2)
    if result["daily_result"] in {
        "UNKNOWN_DUE_TO_SOURCE_FAILURE",
        "REVIEW_REQUIRED_UNRESOLVED_CANDIDATES",
        "REVIEW_REQUIRED_UNVERIFIED_DISCOVERY",
    }:
        raise SystemExit(78)


if __name__ == "__main__":
    main()
