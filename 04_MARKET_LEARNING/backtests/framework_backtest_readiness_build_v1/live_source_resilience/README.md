# Live ETH/BTC dual-source resilience

Append one settled-session row after both Binance ETHBTC and Coinbase ETH-BTC are available. Coinbase may confirm a direct threshold during Binance outage, but cannot replace the owner before the 30-live-session substitution gate passes.

Kraken ETH/XBT remains third-source shadow.