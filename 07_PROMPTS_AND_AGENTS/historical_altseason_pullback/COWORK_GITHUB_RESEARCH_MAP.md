# Cowork GitHub Research Map

Repository: `Donh91/Investering-Framework-Archive-v1`
Authoritative ref: `main`

## Operating model
GitHub is the authoritative research universe. Do not treat the handoff ZIP as a frozen copy of the repository. Use the ZIP for instructions, launch contracts, manifests and immutable artifact pointers, then read the current authoritative research material directly from `main`.

## Mandatory read order
1. `07_PROMPTS_AND_AGENTS/historical_altseason_pullback/COWORK_OPUS5_LAUNCH_INSTRUCTION.md`
2. `07_PROMPTS_AND_AGENTS/historical_altseason_pullback/COWORK_OPUS5_MASTER_RESEARCH_PROMPT.md`
3. `06_RESEARCH_LAB/historical_altseason_pullback_v1/COWORK_READINESS_PROTOCOL.md`
4. `06_RESEARCH_LAB/historical_altseason_pullback_v1/COWORK_OPUS5_RESEARCH_PROTOCOL_ADDENDUM.md`
5. `06_RESEARCH_LAB/historical_altseason_pullback_v1/INTRADAY_EXECUTION_COWORK_ADDENDUM.md`
6. `07_PROMPTS_AND_AGENTS/historical_altseason_pullback/COWORK_OPUS5_MAX_VALUE_SIDECARS.md`
7. `06_RESEARCH_LAB/historical_altseason_pullback_v1/config.json`
8. `06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts/RESEARCH_READINESS_MANIFEST.json`
9. all remaining files under `06_RESEARCH_LAB/historical_altseason_pullback_v1/`
10. all code under `scripts/historical_lab/`

## Prospective 2026 evidence lanes
Read these directly from `main`, while keeping them analytically separate from historical discovery:
- `04_MARKET_LEARNING/entry_signals/`
- `04_MARKET_LEARNING/breadth/`
- `04_MARKET_LEARNING/pullback_learning/`
- `04_MARKET_LEARNING/rotation_survival/`
- `04_MARKET_LEARNING/stress_flush/`
- `04_MARKET_LEARNING/sensor_tournament/`
- `04_MARKET_LEARNING/truth_layer/`
- `04_MARKET_LEARNING/forward_tests/`
- `04_MARKET_LEARNING/intraday_execution/`
- `scripts/intraday_execution/`
- `04_MARKET_LEARNING/data_ping/`
- `04_MARKET_LEARNING/master_monday/`
- `04_MARKET_LEARNING/cycle_navigator/`
- `04_MARKET_LEARNING/etf/`
- `04_MARKET_LEARNING/stablecoin_deployment/`
- `04_MARKET_LEARNING/stablecoin_validation/`
- `03_DAILY_CAPTURE_LOGS/hourly/`
- `03_DAILY_CAPTURE_LOGS/breadth_rich/`
- `03_DAILY_CAPTURE_LOGS/pullback_forensics/`
- `03_DAILY_CAPTURE_LOGS/cfgi_weekly/`
- `03_DAILY_CAPTURE_LOGS/stablecoin_liquidity/`
- `03_DAILY_CAPTURE_LOGS/etf/`

## Heavy historical bulk
`alt_hourly_panel.csv.gz` is intentionally not stored in Git. Resolve it only through:
`06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts/FREE_BULK_ARTIFACT_POINTER.json`.

The pointer binds the source Actions run, artifact name, byte size and SHA-256. Download that exact Actions artifact, locate `alt_hourly_panel.csv.gz`, verify byte size and SHA-256 against the pointer before use. Never substitute a reconstructed or later file silently.

## Authority
Research only. Historical findings may not be promoted above `FORWARD_TEST`. No portfolio execution, market-state mutation, automatic rule changes, threshold changes or weight changes are authorized.

## Output
Return exactly one final package: `HISTORICAL_ALTSEASON_COWORK_OPUS5_RESEARCH_PACKAGE.zip`.
