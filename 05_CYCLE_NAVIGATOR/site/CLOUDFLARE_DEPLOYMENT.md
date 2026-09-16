# Cycle Navigator - Cloudflare Pages deployment

## Goal

Publish Cycle Navigator from the private framework repository without exposing the repository, owner identity, internal paths or framework source to website visitors.

## Cloudflare Pages settings

Use Cloudflare Pages with Git integration.

Recommended project name:

`cycle-navigator`

If that hostname is unavailable, use a neutral variant such as:

`cycle-navigator-live`

Production branch:

`main`

Framework preset:

`None`

Root directory:

repository root / leave blank

Build command:

`node 05_CYCLE_NAVIGATOR/site/build-public.mjs`

Build output directory:

`05_CYCLE_NAVIGATOR/site/dist`

Environment variables:

none required

Secrets:

none required

## GitHub App access

When Cloudflare requests GitHub access, grant the Cloudflare Workers & Pages GitHub App access only to:

`Donh91/Investering-Framework-Archive-v1`

The repository may be private. Cloudflare Pages supports private GitHub repositories through its Git integration.

## What becomes public

Only the generated `dist` bundle:

- `index.html`
- `styles.css`
- `motion.css`
- `app.js`
- `motion.js`
- `data/latest.json`

`data/latest.json` contains a deliberately selected subset of Cycle Navigator output required for the public dashboard.

## What stays private

Everything else, including:

- the canonical pointer's internal `week_dir`;
- machine package hashes and internal paths;
- repository structure outside the public bundle;
- research files;
- framework logic;
- queues and workflows;
- private archives and unrelated investment data.

## URL

Cloudflare assigns a free `pages.dev` hostname from the project name, for example:

`https://cycle-navigator.pages.dev`

The exact hostname depends on availability at project creation time.

A custom domain can be added later, but it is not required for a clean GitHub-free public URL.

## Verification checklist

After deployment:

1. Open the public URL in a private browser window.
2. Confirm Cycle Navigator loads OFFICIAL state and LIVE market data.
3. Inspect page source / network requests and confirm there is no request to `github.com`, `raw.githubusercontent.com`, or a repository URL.
4. Confirm `/data/latest.json` contains only the approved public fields.
5. Confirm `DEGRADED` remains visible when canonical status is degraded.
6. Confirm null BTC/ETH forecast ranges remain unpublished.
7. Confirm repository access is private from a logged-out GitHub session.

## Authority reminder

The public snapshot is delivery infrastructure only. The private pointer and referenced machine package remain the sole OFFICIAL authority.
