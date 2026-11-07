# Research Parallel Lanes, GitHub Actions execution pattern

**Reference only.** This file is NOT placed under `.github/workflows/` and cannot launch anything. Adapt inside the ORIGINAL authorized domain workflow/PR after owner/source preflight. This is a tiny pattern, not a separate scheduler or an extra agent.

## What was actually proven

- [Ironflow PR #1988](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1988) had `public-source-replay` and `tick-hip4-source-qa` as independent GitHub Actions jobs on the **same run**. [Run 42311443044](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42311443044) completed both; separate artifacts had distinct IDs and digests.
- [Ironflow PR #1989](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1989) added a third separate job `full18m-history-walkforward` and ultimately merged on main, with the 72-source-SHA and 25-hour train-label embargo checks. These are computational/data jobs; **no independent AI-agent execution is implied**.
- Multiple jobs may run simultaneously, but shared GitHub runner quotas, network rate limits and true `needs` dependencies can serialize or queue them. Observe actual `started_at`/`completed_at` before asserting concurrency.

## Adaptation template (illustrative, nonexecutable here)

```yaml
# INSERT INSIDE AN EXISTING OWNER-APPROVED PR-ONLY/ON-DEMAND WORKFLOW:
# permissions: contents: read
# on: pull_request + workflow_dispatch, NEVER add a cron by default
jobs:
  lane-market-path:
    # Job A has no needs on B, so they can execute independently.
    runs-on: ubuntu-latest
    timeout-minutes: 25
    steps:
      - uses: actions/checkout@v4
      - name: Verify pinned source and negative fixtures
        run: python scripts/<owner>/verify_known_source.py
      - name: Evaluate frozen hypothesis A
        run: python scripts/<owner>/study_a.py
      - name: Retain research receipt only
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: research-a-receipt
          path: /tmp/study-a-receipts/
          retention-days: 14
          if-no-files-found: warn

  lane-microstructure:
    runs-on: ubuntu-latest
    timeout-minutes: 25
    steps:
      - uses: actions/checkout@v4
      - name: Verify independent pinned source
        run: python scripts/<owner>/verify_tick_source.py
      - name: Evaluate frozen hypothesis B
        run: python scripts/<owner>/study_b.py
      - name: Retain research receipt only
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: research-b-receipt
          path: /tmp/study-b-receipts/
          retention-days: 14
          if-no-files-found: warn
```

The `<owner>` paths above are **placeholders, not existing code**. Never copy and run without first replacing them with verified scripts, adding negative tests and verifying source access and repository rights. Prefer no new workflow file if the original workflow already supports parallel jobs. Do not upload restricted raw provider data to public artifacts.

## Matrix when lanes differ only by approved parameters

```yaml
strategy:
  fail-fast: false
  max-parallel: 3
  matrix:
    lane: [BTC, ETH, HYPE]
```

Matrix workers must use **the same frozen input contract**, separate output and artifact names per matrix lane, and must avoid contaminating each other's results. `fail-fast:false` means another lane may complete after one fails. It does **not** mean overall PR or study should pass if any required lane fails.

Use `needs: [lane-market-path, lane-microstructure]` only for a downstream synthesis job that requires both results. Otherwise the lead in the conversation can synthesize after verifying all job/artifact receipts. If a true input-preflight prerequisite exists, complete it before spawning dependent jobs; it is scientifically wrong to treat dependency as independent concurrency.

## Evidence-based completion

For each lane record original owner, job ID, run URL, exact HEAD, actual status/conclusion, pinned source SHAs, test output, artifact ID, byte digest, retention, observed result and uncertainty. Separately record S1's own execution if it performs unattended work; an ordinary manual ChatGPT merge cannot prove S1 autonomy.

Capacity: start with **2-4 concurrent jobs**, even for 10 research hypotheses. Calculate expected GitHub Actions minutes per job and cap downloads. Parallel total wall-clock time may decrease while aggregate billed runner minutes increase.
