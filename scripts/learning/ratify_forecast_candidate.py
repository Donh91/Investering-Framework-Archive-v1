from __future__ import annotations

# Compatibility import surface only. Production writes must go through
# process_forecast_ratifications.py, which enforces candidate Git recording,
# packet Git recording, prospective timing, outcome-blind scope and terminal state.
from forecast_ratification_freezer import *  # noqa: F401,F403


def main() -> None:
    raise SystemExit("DIRECT_RATIFIER_CLI_DISABLED_USE_PROCESS_FORECAST_RATIFICATIONS")


if __name__ == "__main__":
    main()
