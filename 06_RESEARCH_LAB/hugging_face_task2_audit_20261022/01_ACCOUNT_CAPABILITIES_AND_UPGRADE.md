# Phase 1 | Hugging Face free account, connector and upgrade economics

**Audit date:** 2026-10-22. **HF whoami:** FrameworkCN, user account, `is_pro=false`, OAuth connected, scopes `openid/profile/read-mcp/read-repos/jobs/contribute-repos/inference-api`. This confirms identity and granted scopes, NOT unlimited or prepaid compute or permission to charge. No HF Jobs are currently listed under this connector (read-only `ps` returned 0).

## What can be done immediately on FREE
- Hub discovery: search public datasets/models/Spaces, inspect metadata, structure, splits, schemas, small preview rows, model cards and licensing.
- Browse/download openly available public repository files under HF access/usage restrictions; build lightweight source manifests and small sampled *public* QA notebooks through existing approved research infrastructure.
- Search and reuse open model weights offline when host compute and license allow; downloading a model is not paying for inference, nor does it create a live hosted service.
- Static public Spaces. Some free ZeroGPU/Gradio hosting exceptions are described separately in HF docs; do not assume unlimited Gradio/Docker hosting on free.
- Run read-only plugin source-screening now without changing the production architecture.

## Current plan details verified from official HF documentation
- Hugging Face PRO: **$9/month**; 10x private storage, 2x public storage, $2/month included general compute/inference credit, larger ZeroGPU quota and queue priority, hosting/development benefits.
- Inference Providers included credit: free **$0.10/month**, PRO **$2.00/month**, subject to changes; additional usage requires billing/purchased credits.
- Published Hub fixed 5-minute limits: free 1,000 API / 5,000 resolver / 200 page requests; PRO 2,500 / 12,000 / 400. Free limits may be dynamically adjusted; limits are not a per-month dataset cap.
- HF Jobs require positive compute credit balance; PRO's general $2 monthly credit can apply, but running Jobs remains metered. Jobs CPU Basic **$0.01/hour** on current published rates; GPU T4-small **$0.40/hour**, L4 **$0.80/hour**; pricing can change. Set explicit timeout and approval cap before any execution. The Jobs API is callable/readable by this account, but **paid execution has not been tested or authorized**.
- HF Spaces CPU Basic **2 vCPU, 16 GB RAM, 50 GB ephemeral disk, $0 hardware hourly rate**; new Gradio/Docker compute Space creation generally needs a paid plan under current Spaces Overview. Free account ZeroGPU/Gradio exceptions and priority differ; verify exact entitlement at deployment time.
- HF Team **$20/month** primarily adds organization governance, SSO, access controls, audit logging; not a magic replacement for per-hour compute charges.
- Paid subscription, paid hardware and our connected ChatGPT plugin are three different entitlements. ChatGPT connector scope does **not** grant HF PRO or circumvent limits.

## Recommendation / purchase gate
**FREE remains recommended** for phases 1–2. No HF subscription and no pay-as-you-go compute approval is requested at present. Do not add an unapproved scheduled HF collector to work around exhausted GitHub Actions minutes. HF is not a free always-on replacement for Actions.

Consider one month of PRO **only if** a bounded, documented experiment requires persistent HF compute Space, larger ZeroGPU quota, higher Hub limits or private-dataset viewer and the blocker cannot be solved cheaply with source sampling. Before upgrading: record exact task, plan limits, expected hours, data transfer, model license, API costs, forecast relevance and cancellation criteria. PRO's $2 credit alone does not justify a $9 subscription for a few dozen read-only dataset queries.

Example arithmetic (published rates, excluding extra services and transfer): 100 CPU-Basic Job hours = approximately $1 compute; 5 L4 GPU hours = approximately $4 compute. These *illustrate separate usage charges*, not entitlements nor committed spend.

## Official source references, checked 2026-10-22
- https://huggingface.co/pricing
- https://huggingface.co/docs/inference-providers/pricing
- https://huggingface.co/docs/hub/rate-limits
- https://huggingface.co/docs/hub/jobs-pricing
- https://huggingface.co/docs/hub/spaces-overview
- https://huggingface.co/docs/hub/billing

## Safety / unknowns
- No authenticated billing-page balance or account-specific limit header was retrieved; do not claim credits remaining.
- API token expires/refreshes independently; do not store token, OAuth details or secrets in public GitHub.
- Availability, storage and gating can differ by account and date.
- Limit request rates; cache immutable revisions, use backoff for 429, prefer Parquet metadata and column/partition projection rather than full dataset downloads.
