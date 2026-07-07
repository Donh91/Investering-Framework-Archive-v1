# P1b Data Files Note — 2026-07-06

This note records the machine-readable files produced by Fable P1b.

The full uploaded files in the working thread were:

- `FRAMEWORK FABLE RAPPORT P1b EXECUTED.pdf`
- `framework recommendation rows.md`
- `experiment results 2.json`
- `btc ohlc master.csv`
- `etf flow daily.csv`
- `source manifest 2.csv`

Due to the current GitHub text-write workflow, the archive stores the governance ratification and recommendation rows as canonical text.

The key archived files in this folder are:

- `P1b_Executed_Ratification_2026-07-06.md`
- `framework_recommendation_rows_2026-07-06.md`
- prior status file: `P1b_Status_Interrupted_Run_2026-07-03.md`

If exact machine data is needed later, retrieve it from the Fable P1b uploaded artifacts and re-add as CSV/JSON through a direct file upload workflow.

Canonical result summary:

- E5-OHLC supports v0.2 hybrid design under true OHLC.
- 59.0K hard-death remains ratified but should be annotated as tight, not a wide buffer.
- E3-FULL does not support 2/3-close as a price edge, even after flow-conditioning.
- E8-FULL supports keeping the FNP expected-cost prior around 9 percent, with p90 around 12 percent.

Standing governance constraints remain unchanged:

- Rebuy locked.
- No portfolio action.
- No recovery or rotation confirmation from this research alone.
- FNP is measurement only.
