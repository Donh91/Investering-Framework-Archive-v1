# TauricResearch TradingAgents v0.5.0 - frozen external-method source note

Capture date: 2026-09-21
Source type: PUBLIC GITHUB REPOSITORY / PAPER-ADJACENT IMPLEMENTATION / FAILURE CORPUS
Project: TauricResearch/TradingAgents
Repository: https://github.com/TauricResearch/TradingAgents
Frozen release: v0.5.0
Release date: 2026-09-18
Release commit: 7fe225224431aeb3adfe1a6a23885c03fc43620a
Annotated tag object: 6aafdce38e0d1c1f211127f9ff8f969695020478
License observed at capture: Apache-2.0
Framework authority: RESEARCH_ONLY / NO_TRADING_AUTHORITY / NO_COPY_WHOLE_SYSTEM

## Why this source is retained

TradingAgents is retained primarily as a correctness-engineering and failure-corpus source, not as proof that a multi-agent LLM trading architecture has robust alpha.

The high-value evidence is the repository's documented sequence of real failure modes and repairs across releases, especially:
- historical data look-ahead;
- revised macro/fundamental data leaking into prior dates;
- present-day social data entering historical runs;
- future outcome lessons entering historical memory;
- premature outcome settlement;
- missing/unobserved source coverage being interpreted as absence;
- vendor failures being confused with no-data states;
- unreadable model decisions being converted into tradeable HOLD;
- debate agents rebutting an opponent who had not spoken;
- checkpoint identity not binding sufficiently to graph configuration.

These defects are directly useful as adversarial test cases for our own Auto Trading, Alpha Lab, evidence, backtest and agent-governance machinery.

## Frozen upstream anchors

Primary release:
- https://github.com/TauricResearch/TradingAgents/releases/tag/v0.5.0

Primary changelog:
- https://github.com/TauricResearch/TradingAgents/blob/v0.5.0/CHANGELOG.md

High-value implementation/test surfaces:
- tradingagents/dataflows/date_window.py
- tradingagents/dataflows/errors.py
- tradingagents/dataflows/interface.py
- tradingagents/agents/utils/memory.py
- tradingagents/agents/utils/rating.py
- tradingagents/graph/signal_processing.py
- tradingagents/graph/trading_graph.py
- tradingagents/backtest.py
- tests/test_memory_pointintime.py
- tests/test_vendor_errors.py
- tests/test_signal_processing.py
- tests/test_backtest.py

High-value historical defects explicitly documented in the changelog:
- #1115 Alpha Vantage future-report leakage
- #1275 FRED revision/vintage leakage
- #1220 current social chatter leaking into historical runs
- #1251 future resolved-memory leakage
- #1169 premature outcome settlement
- #1201 latest OHLCV bar / missing-close handling
- #1176 debate opening fabrication
- #1170 silent HOLD on unreadable decision
- #1089 checkpoint identity mismatch across graph shape
- #1300 present-day company profile in historical runs
- #1331 / #1319 / #1118 dated-tool run-date binding

## Release-level facts retained

TradingAgents v0.5.0 states and implements the following design direction:

1. Dated tools are bounded by the run's analysis date.
2. Historical fundamentals should reflect information actually filed/observable by the historical date where the vendor permits this.
3. Data-source failure, unavailable historical coverage and observed zero/absence are different states.
4. Unreadable decision output should fail closed to REVIEW rather than silently becoming HOLD.
5. Outcome scoring should wait for a complete configured holding window.
6. Historical memory must not contain lessons whose outcomes became known after the historical decision date.
7. Backtests should use the same decision pipeline while isolating the backtest decision log from live memory.
8. Missing portfolio context must not be silently interpreted as an empty/flat portfolio.
9. A backtest harness should preserve failed cells and continue the sweep rather than erasing failures.
10. Debate/adversarial agents must not invent an absent opponent position.

## Critical limitations

Do not treat the original TradingAgents paper performance as validated post-correction evidence.

The repository subsequently fixed multiple point-in-time, memory and outcome-evaluation defects. This does not prove that every original paper result was affected, but it is enough that old headline returns/Sharpe values cannot be used as framework evidence without a fresh reproduction on the corrected pipeline with realistic costs, proper holdouts and broader universes.

The v0.5.0 backtest module itself explicitly evaluates decision quality and is not a full portfolio/execution simulator. Its own test documentation states that it does not provide fees, an equity curve or execution simulation. Therefore it is useful as a decision-evaluation architecture reference, not as a complete execution backtester.

## Archiving decision

Retain:
- release identity and commit;
- changelog defect history;
- mechanism descriptions;
- selected file/test paths;
- extracted invariants and transfer candidates;
- negative lessons and anti-patterns.

Do not retain:
- full repository clone;
- vendor credentials/config;
- whole multi-agent architecture;
- marketing/performance claims as fact;
- copied code unless a future implementation review shows a small licensed mechanism is materially superior to our existing owner.

## Framework routing

Primary extraction:
- 04_RESEARCH_LAB/auto_trading/source_notes/AT-SRC-0016_TAURIC_TRADINGAGENTS_CORRECTNESS_ENGINEERING.md
- 04_RESEARCH_LAB/auto_trading/TRADINGAGENTS_EXTRACTION_2026-09-21.md
- 04_RESEARCH_LAB/auto_trading/TRADINGAGENTS_TRANSFER_CANDIDATES_v1.json

Existing owners remain authoritative. This source note creates no new trading, portfolio, execution, market-state, scanner, agent-swarm or governance authority.
