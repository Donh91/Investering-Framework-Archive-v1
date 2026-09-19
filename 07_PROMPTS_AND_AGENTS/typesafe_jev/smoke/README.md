# Jev sanitized smoke harness

This directory contains the first live TypeSafe connectivity test.

It deliberately uses synthetic support-ticket data rather than market, Alpha Lab, portfolio, private-provider or repository data.

## What a PASS proves

- the GitHub Actions secret is available to the job;
- the pinned Python SDK can authenticate;
- the API accepts one batched request containing Choice, Score and Noul;
- the SDK returns typed results.

It does **not** prove Jev intelligence, calibration, Alpha Lab value, cost advantage or production readiness.

## Running

The workflow is manual-only:

`.github/workflows/typesafe_jev_sanitized_smoke.yml`

It has read-only repository permission and no write step.

After a successful connectivity test, the next owner is the frozen Alpha Lab blind-replay design. Do not reuse this synthetic smoke result as model-quality evidence.
