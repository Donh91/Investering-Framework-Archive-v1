from __future__ import annotations

import threading
import time

import red_sellability_aware_outcomes_v1 as outcome

# Public archival Solana RPC is a research dependency, not a throughput target.
# Serialize getTransaction calls and pace them so transient HTTP 429 responses
# cannot silently turn a complete historical target set into a smaller sample.
_lock = threading.Lock()
_original_fetch_tx = outcome.fetch_tx


def throttled_fetch_tx(url: str, sig: str):
    with _lock:
        time.sleep(0.35)
        return _original_fetch_tx(url, sig)


outcome.fetch_tx = throttled_fetch_tx

if __name__ == "__main__":
    outcome.main()
