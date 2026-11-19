# SOL 6.2 MAX MISSION: Navigator One regulation, tax and operating boundary (Denmark / EU)

Read the whole BUNDLE first. One run, no tools. This is research, not legal advice; mark everything that needs a lawyer or accountant as `PROFESSIONAL_CHECK`.

**Deliverable: `NAVIGATOR_REGULATORY_REPORT_v1`.**

1. **Personal use vs offering the app to others.** Under EU MiCA and Danish implementation, where does a self-used, non-custodial, research-and-prepare app cross into a regulated crypto-asset service? Cover custody, exchange, transfer, advice, portfolio management, and order reception and transmission. Where are the lines, and what keeps the app clearly on the personal-tool side?
2. **Investment advice and the AI assistant.** When do personalised "suggested actions" become regulated advice if the app is shared? What disclaimers and design choices matter? Is "research only, user decides and signs" enough?
3. **Tax and record keeping (Denmark).**
   - The records the app should keep automatically: per-trade cost basis, fees, gas, timestamps, chain, and tx hash.
   - Export formats that Danish crypto tax tools and Skattestyrelsen reporting can use (TO_VERIFY).
   - FIFO vs average-cost rules (TO_VERIFY), and DeFi/LP/airdrop edge cases.
4. **Data protection.** If the app ever has a second user: GDPR for wallet addresses and portfolios, hosting location, and logs.
5. **Third-party terms.** MetaMask/Consensys, WalletConnect/Reown, data providers (CoinGecko, CMC, BlockchainCenter, DEX APIs), and RPC providers. Cover rate limits, commercial-use clauses and attribution (TO_VERIFY).
6. **A decision checklist** for each release R0–R4: what must be true legally and operationally before shipping.
7. **What would change** if bounded automation were ever considered. Description only; it is not in this phase.
