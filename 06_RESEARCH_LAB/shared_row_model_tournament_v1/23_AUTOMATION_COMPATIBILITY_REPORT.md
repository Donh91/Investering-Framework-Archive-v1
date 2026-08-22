# Automation Compatibility

The tournament is designed as a passive research consumer of already-owned timestamped market data. It must not modify Master Monday, Cycle Navigator, DATA PING thresholds or portfolio execution.

Safe automation sequence:
1. read contemporaneous owner outputs;
2. materialize one shared row;
3. compute only preregistered transforms with frozen versions;
4. serialize candidate decisions;
5. append divergences;
6. mature 24h/72h/7d outcomes when due;
7. rerun comparator after evidence gates are met.

If a required owner is unresolved, that family stays missing and no proxy is silently inserted.
