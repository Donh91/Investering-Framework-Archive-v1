# DATA PING QA boundaries

```yaml
run_id: run_586b93af2ad54a49b13f7453e7ea40e2
source_status: PARTIAL
main_use_status: USABLE_WITH_LIMITS
```

Accepted:

- live direct BTC, ETH and ETH/BTC market feeds;
- direct ETH/BTC identity;
- settled ETF sessions through 24 July;
- current breadth snapshot with run-specific membership hash;
- current derivatives snapshots and deterministic features;
- latest available FRED observations.

Excluded from confirmation:

- stale CFGI values;
- unavailable global stablecoin total;
- unavailable realized-volatility windows;
- optional DeFi total TVL skipped under runtime limit;
- any predecessor delta, because no accepted same-thread predecessor was supplied;
- settled 0.0300 gate confirmation, because the supplied value is live;
- full packet transport hash, because chat transport integrity is unverified.

The packet is adequate for a bounded current-state framework read, but not for a complete sensor-confidence or regime-confidence claim.
