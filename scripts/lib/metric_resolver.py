"""Canonical metric-path resolver shared by forecast freeze and outcome maturation.

Implements the invariant specified in TASK3 R3-04:

    A path stored while freezing metric X from capture C must later resolve
    metric X from capture C using the same canonical resolver employed during
    outcome maturation.

Design constraints (R3-04, Task 4 Implementation 1):

* deterministic
* no I/O
* only the two explicitly authorised root contracts
* unknown root conventions are rejected, never guessed
* a missing path is distinguished from a non-numeric value
* a vanished namespace is distinguished from a wrong lookup
* no fuzzy fallback, no namespace guessing, no semantic substitution

The canonical convention for NEW forecasts is CAPTURE_DOCUMENT_ROOT: the stored
path is resolved from the root of the evidence capture document as a whole.

Forecasts frozen before the cutover carry no explicit root and are interpreted
under MARKET_METRICS_ROOT. That is a fact about the producer at those commits
(scripts/experiments/experiment_lifecycle.py resolved and therefore stored paths
relative to context.latest_capture.market_metrics), not an inference drawn from
observed outcomes.
"""

from __future__ import annotations

from typing import Any

RESOLVER_VERSION = "METRIC_PATH_RESOLVER_v1"

CAPTURE_DOCUMENT_ROOT = "CAPTURE_DOCUMENT_ROOT"
MARKET_METRICS_ROOT = "MARKET_METRICS_ROOT"
ROOT_CONTRACTS = (CAPTURE_DOCUMENT_ROOT, MARKET_METRICS_ROOT)

MARKET_METRICS_KEY = "market_metrics"

# Resolution statuses. RESOLVED carries a numeric value; every other status
# carries value None and maps to an existing or R3-04-authorised censor reason.
RESOLVED = "RESOLVED"
METRIC_UNAVAILABLE = "METRIC_UNAVAILABLE"
EVIDENCE_NAMESPACE_UNAVAILABLE = "EVIDENCE_NAMESPACE_UNAVAILABLE"
METRIC_PATH_ROOT_AMBIGUOUS = "METRIC_PATH_ROOT_AMBIGUOUS"
METRIC_PATH_ROOT_UNDECLARED = "METRIC_PATH_ROOT_UNDECLARED"

CENSOR_REASONS = (
    METRIC_UNAVAILABLE,
    EVIDENCE_NAMESPACE_UNAVAILABLE,
    METRIC_PATH_ROOT_AMBIGUOUS,
    METRIC_PATH_ROOT_UNDECLARED,
)


class UnknownRootContract(ValueError):
    """Raised when a root contract outside ROOT_CONTRACTS is requested.

    This fails closed on purpose. A forecast declaring an unsupported root is a
    contract violation, not a data gap, and must never be silently coerced into
    one of the supported roots.
    """


class Resolution:
    """Immutable result of one resolution attempt."""

    __slots__ = ("status", "value", "root_contract", "path")

    def __init__(self, status: str, value: Any, root_contract: str | None, path: str) -> None:
        self.status = status
        self.value = value
        self.root_contract = root_contract
        self.path = path

    @property
    def ok(self) -> bool:
        return self.status == RESOLVED

    def __repr__(self) -> str:  # pragma: no cover - diagnostic only
        return f"Resolution(status={self.status!r}, value={self.value!r}, root={self.root_contract!r}, path={self.path!r})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Resolution):
            return NotImplemented
        return (self.status, self.value, self.root_contract, self.path) == (
            other.status,
            other.value,
            other.root_contract,
            other.path,
        )


def is_wellformed(path: Any) -> bool:
    """True only for a dot-separated path of non-empty segments.

    Rejects empty strings, leading/trailing dots, empty interior segments and
    compound ';'-separated paths. Malformed paths are never repaired.
    """
    if not isinstance(path, str) or not path:
        return False
    if ";" in path:
        return False
    segments = path.split(".")
    return all(segment != "" for segment in segments)


def root_object(document: Any, root_contract: str) -> Any:
    """Return the object a path is resolved against, or None if unavailable."""
    if root_contract not in ROOT_CONTRACTS:
        raise UnknownRootContract(f"unsupported_root_contract:{root_contract}")
    if not isinstance(document, dict):
        return None
    if root_contract == CAPTURE_DOCUMENT_ROOT:
        return document
    candidate = document.get(MARKET_METRICS_KEY)
    return candidate if isinstance(candidate, dict) else None


def _walk(node: Any, segments: list[str]) -> Any:
    current = node
    for segment in segments:
        if not isinstance(current, dict):
            return None
        current = current.get(segment)
    return current


def resolve(document: Any, path: str, root_contract: str) -> Resolution:
    """Resolve `path` against `document` under exactly `root_contract`.

    Never searches, never falls back to another root, never substitutes a
    neighbouring metric. Returns a Resolution whose status explains the outcome.
    """
    if root_contract not in ROOT_CONTRACTS:
        raise UnknownRootContract(f"unsupported_root_contract:{root_contract}")

    if not is_wellformed(path):
        return Resolution(METRIC_UNAVAILABLE, None, root_contract, path if isinstance(path, str) else "")

    base = root_object(document, root_contract)
    if not isinstance(base, dict):
        # The declared root itself is absent from this document.
        return Resolution(METRIC_UNAVAILABLE, None, root_contract, path)

    segments = path.split(".")
    head = segments[0]

    if base:
        # A populated root that lacks the leading namespace, or carries it as an
        # emptied placeholder, means the data moved rather than that the lookup
        # is wrong. R3-05 D3: market_metrics.spot -> spot_legacy on 2026-08-08.
        if head not in base:
            return Resolution(EVIDENCE_NAMESPACE_UNAVAILABLE, None, root_contract, path)
        if isinstance(base[head], dict) and not base[head]:
            return Resolution(EVIDENCE_NAMESPACE_UNAVAILABLE, None, root_contract, path)

    value = _walk(base, segments)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        # bool is a subclass of int and is never an admissible metric value.
        return Resolution(METRIC_UNAVAILABLE, None, root_contract, path)
    return Resolution(RESOLVED, value, root_contract, path)


def declared_root_contract(forecast: Any) -> str | None:
    """Return the root contract a forecast explicitly declares, if any."""
    if not isinstance(forecast, dict):
        return None
    declared = forecast.get("metric_path_root")
    if declared is None:
        return None
    if declared not in ROOT_CONTRACTS:
        raise UnknownRootContract(f"unsupported_root_contract:{declared}")
    return declared


def legacy_root_contract(forecast: Any) -> str | None:
    """Attribute an undeclared forecast to the producer that froze it.

    This is attribution from immutable provenance fields, not inference from the
    evidence. Each branch is a fact about a specific producer's code:

    * `source_candidate_id` is written only by
      scripts/experiments/experiment_lifecycle.py, which resolved and therefore
      stored paths relative to context.latest_capture.market_metrics.
    * `candidate_id` (without `source_candidate_id`) is written only by
      scripts/learning/ratify_forecast_candidate.py, which resolves against the
      root of the supplied baseline evidence document.

    A forecast attributable to neither producer is not interpreted. Returning
    None makes the caller fail closed rather than pick a root.
    """
    if not isinstance(forecast, dict):
        return None
    if forecast.get("source_candidate_id"):
        return MARKET_METRICS_ROOT
    if forecast.get("candidate_id"):
        return CAPTURE_DOCUMENT_ROOT
    return None


def resolve_for_forecast(document: Any, forecast: Any, path: str | None = None) -> Resolution:
    """Resolve a forecast's metric path using its declared or attributed root.

    * An explicitly declared `metric_path_root` is authoritative and is used as
      given; no ambiguity can arise.
    * Absent a declaration the producer-attribution rule applies, and only after
      proving the path does not also resolve numerically under the other root.
      If both resolve the resolver refuses with METRIC_PATH_ROOT_AMBIGUOUS
      rather than choosing.
    * A forecast that declares no root and cannot be attributed to a known
      producer is refused with METRIC_PATH_ROOT_UNDECLARED. The resolver never
      falls back to the other root and never searches for the value.
    """
    metric_path = path if path is not None else (forecast or {}).get("metric_path")
    if not isinstance(metric_path, str):
        return Resolution(METRIC_UNAVAILABLE, None, None, "")

    declared = declared_root_contract(forecast)
    if declared is not None:
        return resolve(document, metric_path, declared)

    attributed = legacy_root_contract(forecast)
    if attributed is None:
        return Resolution(METRIC_PATH_ROOT_UNDECLARED, None, None, metric_path)

    other = CAPTURE_DOCUMENT_ROOT if attributed == MARKET_METRICS_ROOT else MARKET_METRICS_ROOT
    primary = resolve(document, metric_path, attributed)
    alternate = resolve(document, metric_path, other)
    if primary.ok and alternate.ok:
        return Resolution(METRIC_PATH_ROOT_AMBIGUOUS, None, None, metric_path)
    return primary


def canonical_path(market_metrics_relative_path: str) -> str:
    """Convert a market-metrics-relative path into the canonical document-rooted form.

    Used by the producer at freeze time so that the path it stores is the path
    the maturation resolver will later dereference.
    """
    if not is_wellformed(market_metrics_relative_path):
        return market_metrics_relative_path
    if market_metrics_relative_path.split(".")[0] == MARKET_METRICS_KEY:
        return market_metrics_relative_path
    return f"{MARKET_METRICS_KEY}.{market_metrics_relative_path}"
