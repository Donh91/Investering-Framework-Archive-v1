# Skill-run receipt — ChatGPT Backtest Wave 1 research 1–5

```yaml
run_date: 2026-07-28
run_type: CONTROLLED_RESEARCH_EXECUTION
branch: agent/backtest-wave1-chatgpt-research-1-5-20260728
reproducible_script: run_wave1_research.py
script_sha256: d1ebf2ae660df5209e9b4c4737f794c1db967c8b536cdf2d1d826a13d39d6376
clean_process_return_code: 0
result_zip: BACKTEST_WAVE1_CHATGPT_RESEARCH_1_5_20260728.zip
result_zip_bytes: 346692
result_zip_sha256: 006d19f85ba59c61c5dff704161e135432827a68d8f9f20a4153aeb93ce75654
source_packages_verified: 4
final_holdout_opened: NO
claude_results_seen: NO
framework_state_change: NONE
portfolio_action: NONE
```

## Evidence discipline

- package-supplied preliminary backtest outputs were not used as evidence;
- direct and derived ETH/BTC were kept separate;
- spot, swap and index authority remained separated;
- missing `knowledge_at` rows were quarantined rather than inferred;
- overlapping events were clustered;
- bootstrap uncertainty was retained;
- no threshold was changed from a result;
- the final chronological holdout was not opened.

## Package contents

The result ZIP contains 35 artifacts including:

- full executive and methods report;
- byte and checksum manifest;
- reproducible Python implementation;
- row-level event and policy ledgers;
- bootstrap intervals;
- Cycle Navigator tournament rows;
- PCA, clustering and walk-forward ablation outputs;
- provenance GraphML;
- four audit charts;
- clean-process stdout and stderr.

Result: `CHATGPT_WAVE1_RESEARCH_1_5_COMPLETE_WITH_EXPLICIT_BLOCKERS`.
