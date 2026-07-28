# Claude Challenge Wave 1 handoff checklist

Before sending the prompt to Claude Opus 5 Max, attach or provide:

- exact frozen owner datasets;
- source and package hashes;
- frozen independent event IDs;
- frozen policy definitions;
- point-in-time publication and settlement contracts;
- metric definitions and transaction-cost assumptions;
- holdout boundary;
- artifact naming contract.

Do not provide:

- ChatGPT result rows;
- ChatGPT implementation outputs;
- ChatGPT narrative conclusions;
- any preliminary package-supplied backtest result as evidence.

Claude must return a manifest with row counts, hashes, exclusions and failed tasks before model comparison begins.
