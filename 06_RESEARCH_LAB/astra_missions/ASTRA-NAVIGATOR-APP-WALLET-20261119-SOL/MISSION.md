# SOL 6.2 MAX MISSION: Navigator One non-custodial wallet, signing and security design

Read the whole BUNDLE first. One run, no tools. Binding constraint 1 (non-custodial, user signs everything) is absolute.

**Deliverable: `NAVIGATOR_WALLET_SECURITY_REPORT_v1`.**

1. **Connection options.**
   - MetaMask SDK, WalletConnect/Reown, injected EIP-1193 providers, hardware wallets via MetaMask, and embedded/MPC wallets (explain why they conflict or fit with "keys stay with the user").
   - Cover mobile and desktop flows. Recommend one primary option and one fallback.
2. **Chains and assets.**
   - ETH mainnet plus the L2s and alt-L1s relevant to Alpha Lab candidates.
   - USDT/USDC handling: allowances, decimals, and USDT's non-standard approve.
   - The native gas token on each chain, and how gas is sourced.
3. **"MetaMask supplies gas" in practice.**
   - The user pays gas from their own wallet, versus ERC-4337 account abstraction with a paymaster (gas sponsorship or gas paid in USDT).
   - EIP-7702. Swap routing: aggregators vs direct DEX; MetaMask Swaps vs in-app quotes.
   - For each, cover the trust assumptions, cost and complexity.
4. **Transaction preparation UX.**
   - The intent card shows token identity checks, quote, slippage, min-received, route, gas estimate, expiry, simulation (eth_call or tenderly-like, TO_VERIFY), and the risk veto from the framework.
   - The user signs in the wallet. Afterwards the app reconciles the receipt against the intent.
   - Every case where the app must refuse to prepare a transaction (stale quote, unsellable token, honeypot or tax token, mismatched chain).
5. **Threat model.**
   - Phishing and spoofed dApps, malicious token metadata, approval drains (Permit/Permit2), RPC trust, front-running/MEV (private RPCs), supply chain of front-end dependencies, XSS in the PWA, and session hijack.
   - For each, give a mitigation and a test.
6. **Data boundary.** What on-chain data the app may read; where portfolio state lives; and how it is kept out of public repos, logs and analytics.
7. **What a later "bounded automation" decision would require** (description only, NOT a design): legal review, separate keys and limits, kill switch, audit. Make clear that this phase does not build it.
8. **Top 10 security tests** to pass before R4 (user-signed manual trades).
