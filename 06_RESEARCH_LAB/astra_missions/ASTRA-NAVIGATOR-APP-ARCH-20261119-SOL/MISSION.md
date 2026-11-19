# SOL 6.2 MAX MISSION: Navigator One app architecture, hosting and delivery plan

Read the whole BUNDLE first. One run, no tools.

**Deliverable: `NAVIGATOR_APP_ARCHITECTURE_REPORT_v1`.**

1. **Product slicing.** Define the smallest valuable releases in order:
   - R0: read-only TODAY + PORTFOLIO with fixture data;
   - R1: live read adapters to Kompas and Alpha;
   - R2: paper intents;
   - R3: wallet connect and a read-only on-chain portfolio;
   - R4: user-signed manual trades.

   For each release, give scope, acceptance tests and the "done" evidence.
2. **Client.**
   - PWA vs React Native/Expo vs native. Cover offline behaviour, push notifications on iOS, and wallet deep-links (MetaMask mobile, WalletConnect).
   - Recommend one option and justify it.
3. **Backend and hosting.**
   - Compare, for one developer: a static PWA plus serverless functions; one small VPS with Postgres; a managed platform; and GitHub-Pages-like static hosting plus a read API.
   - Cover cost per month (TO_VERIFY), the security surface, secrets, backups, observability, EU data residency and vendor lock-in.
4. **Data contracts.**
   - Read adapters for the existing owners (Kompas/CN frozen forecast, current Kompas, Alpha candidates, paper ledgers).
   - Freshness and staleness labels, caching, and an append-only event journal.
   - Use the typed handoff in INTEGRATION_AND_RISK as the starting point.
5. **The DESK assistant.** Decide whether the chat roles are LLM calls or deterministic projections. Cover cost control, prompt-injection risk from token metadata, and logging without private data.
6. **Build plan for an AI-agent developer.**
   - Repo layout, test strategy (contract tests, fixture replay, e2e on mobile widths), CI, release gates, and rollback.
   - What a long autonomous build run (Claude Fable) needs as inputs so that it does not start from zero.
7. **Top 10 risks**, each with a mitigation and a kill criterion.
