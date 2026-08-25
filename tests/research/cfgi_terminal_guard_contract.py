from __future__ import annotations


REQUIRED_TERMINAL_MARKERS = (
    "Historical Altseason CFGI Recovery Terminal Guard",
    "permissions:\n  contents: read",
    "verify-terminal-state:",
    "CFGI_MARKET_PROVIDER_TERMINAL_RECEIPT_v1",
    "TERMINAL_PROVIDER_NO_HISTORICAL_ROWS",
    "no_additional_paid_retry_authorized",
    "automatic_retry_after_failure",
    "max_attempts",
    "allowed_symbols",
    "PAID_RETRY_DISPATCH_DISABLED",
)

FORBIDDEN_PAID_RETRY_MARKERS = (
    "schedule:",
    "cron:",
    "CFGI_API_KEY",
    "cfgi_targeted_backfill.py",
    "gh workflow run historical-altseason-cfgi-enrichment.yml",
)


def validate_terminal_guard_contract(source: str) -> None:
    """Accept only the terminal, read-only, zero-paid-retry launcher contract."""
    for marker in REQUIRED_TERMINAL_MARKERS:
        assert marker in source, f"missing terminal guard marker: {marker}"
    for marker in FORBIDDEN_PAID_RETRY_MARKERS:
        assert marker not in source, f"paid retry capability present: {marker}"
