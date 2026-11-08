# S1 Release Control · natural consumer adoption and Pages release checklist v1

**Owner:** existing Archive issue #1156. **Status:** integration acceptance contract, NOT proof of agent adoption, a deployment or an independent permission. This file adds no scheduler, workflow, agent identity, model invocation, write authority or new queue.

## Host decision

- Canonical operational truth: original source-controlled GitHub owners, exact SHA and timestamp.
- Permanent human interface: dedicated PUBLIC GitHub Pages repository, separate from Cycle Navigator. AppDeploy is staging only.
- Machine interface: on-demand `node tools/s1-release-control/agent-brief-v1.mjs --stdout` and `agent-context-v1.mjs --stdout`, using the existing agent runtime, or independently verified exact-source public GitHub GET if Node execution is unavailable. Agents MUST NOT scrape HTML or treat either host as a release authority.
- Original restricted Bridge, Vault and Alpha Lab data must never flow through the public site or public machine output.

## Existing consumer lanes, actual acceptance

| Existing consumer | Expected read | Required evidence | Must NOT claim |
| --- | --- | --- | --- |
| Hourly S1 task `6ae5fd466b48819187abc224ec0f1c5f` | On a natural scheduled eligible tick, verify current original owner + public agent brief or equivalent SHA-bound sources | Scheduled task run ID, read time, current main SHA, brief/source digest, source age, decision impact, native issue/PR receipt and post-action main readback where applicable | That an interactive run, local test or merged PR alone proves natural adoption |
| Strategist | Public context plus original issue/source | Native actual run or artifact, exact source identity, original-owner next action | New authority, new owner or invented agent invocation |
| Codex | Original `LATEST_CODEX_READY_TASKS.json` and exact original candidate; brief only a hint | Exact task reference, candidate HEAD, CI/review and native execution receipt | That a hint is a paid API authorization or READY |
| Grok Bridge | Public source-bound contract and existing restricted Bridge owner | Actual Grok-authored Bridge-native report with referenced SHA and finding, separate from GitHub comment | That a GitHub request proves Grok ran or constitutes GitHub formal approval |
| Research Lab | Original research source and falsifier | Real experiment/run record with clocks and source provenance | Predictive edge or model validation from a dashboard snapshot |

## Per-run minimum adoption receipt

Record only on the original owner, using its existing reporting channel:

```json
{
  "contract": "S1_RELEASE_CONTROL_CONSUMPTION_RECEIPT_v1",
  "consumer": "EXISTING_LANE_NAME",
  "execution_mode": "NATURAL_SCHEDULED|INTERACTIVE|ON_DEMAND",
  "native_run_id": null,
  "observed_at_utc": null,
  "archive_main_sha": null,
  "source_path_or_original_url": null,
  "source_sha_or_digest": null,
  "freshness": "VERIFIED|STALE|UNOBSERVED",
  "source_read_proven": false,
  "original_issue_or_pr": null,
  "decision_impact": "NONE|DISCOVERY|REPAIR|QUALIFIED_ACTION",
  "native_action_url": null,
  "natural_consumer_proven": false,
  "notes": "Unknown is not success; never copy private source content into public logs."
}
```

A receipt is not immutable by virtue of being a comment. Source identity and actual native run must be independently cross-checked. Missing task-run provenance => natural_consumer_proven=false. Preserve S1 max 3 legitimate original PRs per eligible tick and Monday 09:30–10:30 Copenhagen READ-ONLY.

## Seven-day adoption evaluation

Count distinct **actual** consumers, natural S1 scheduled source reads, eligible ticks with no read, stale/partial failures, decision-impact cases, S1-own native merges and separately complete source-to-production outcomes. Denominator must be observed scheduled ticks, not a presumed schedule. Never infer success from the presence of this file or from a request to Grok.

## Pages deployment gates

Follow `DEPLOYMENT_CONTRACT_v1.md`. Required: real dedicated repo-create and Pages administration capability, qualified source HEAD, source-specific recovery/custody and policy gates, immutable static bundle digests, actual target main/Pages run, live CDN byte readback, correct stale/live API behavior and unchanged CN Pages. If unavailable, report the precise external capability blocker. Do not replace Pages with an invented URL or quietly repurpose CN.

## Immediate action order

1. On next existing S1 eligible scheduled tick, use this contract and source-bound brief as a *read-only discovery accelerator*; verify original sources before action.
2. Existing Grok Bridge owner independently reviews the public contract; obtain real Bridge-native evidence before crediting adoption.
3. Track actual 7-day outcomes under original #1156 without a new automation or duplicated queue.
4. Publish dedicated GitHub Pages only when release and administrative gates are satisfied.
