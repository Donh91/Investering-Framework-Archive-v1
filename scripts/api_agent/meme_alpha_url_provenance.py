from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING_KEYS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "ref", "ref_src", "source", "sourceid", "mc_cid", "mc_eid", "fbclid", "gclid",
}


def canonicalize_url(url: str) -> str:
    """Normalize benign URL differences without weakening host/path provenance."""
    raw = str(url or "").strip()
    if not raw.startswith(("http://", "https://")):
        return raw
    parts = urlsplit(raw)
    scheme = parts.scheme.lower()
    host = (parts.hostname or "").lower()
    if not host:
        return raw
    port = parts.port
    netloc = host
    if port and not ((scheme == "https" and port == 443) or (scheme == "http" and port == 80)):
        netloc = f"{host}:{port}"
    path = parts.path or "/"
    if path != "/":
        path = path.rstrip("/") or "/"
    query_pairs = []
    for key, value in parse_qsl(parts.query, keep_blank_values=True):
        if key.lower() in TRACKING_KEYS or key.lower().startswith("utm_"):
            continue
        query_pairs.append((key, value))
    query = urlencode(sorted(query_pairs))
    return urlunsplit((scheme, netloc, path, query, ""))


def reconcile_source_urls(claimed_urls: set[str], observed_urls: set[str]) -> tuple[list[str], list[str]]:
    """Return provenance-supported claimed URLs plus unsupported claims.

    Matching uses canonical URL identity, but retained values are the observed tool URLs
    so downstream evidence points to an actually retrieved source rather than a model-normalized variant.
    """
    observed_by_canonical: dict[str, str] = {}
    for url in sorted(observed_urls):
        canonical = canonicalize_url(url)
        if canonical:
            observed_by_canonical.setdefault(canonical, url)

    supported: list[str] = []
    unsupported: list[str] = []
    for claimed in sorted(claimed_urls):
        canonical = canonicalize_url(claimed)
        observed = observed_by_canonical.get(canonical)
        if observed:
            supported.append(observed)
        else:
            unsupported.append(claimed)
    return sorted(set(supported)), unsupported
