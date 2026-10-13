# Public research brief: REA browser sandbox, Claude Free review
**Date:** 2026-10-12  
**Visibility:** PUBLIC RESEARCH ONLY. No Alpha Lab source code, passwords, secrets, personal wallet details or private data.
**Status:** QUESTION PACKET, not security certification or approved production implementation.

## Problem, precisely scoped
A privately maintained, internally developed REA Playwright agent navigates public crypto-project websites, clicks safe navigation tabs, captures screenshots, and records proof of whether advertised product functions work. It must never sign a transaction, connect a wallet, trade, call a metered LLM/browser API, or leak GitHub repository credentials.

The original synthetic GitHub Actions fixture passed. An attempted hardening to `chromiumSandbox: true` failed on a standard GitHub-hosted Ubuntu runner with **"Chromium sandboxing failed!"**. The safe interim gate blocks *all unknown public website browsing* until a dedicated, verified sandbox is available; local loopback fixture tests may continue. This brief makes no claim about unrelated browser engines, CI capabilities or product readiness.

**Source material for independent source review is delivered privately by the user as a standalone TXT/ZIP attachment.** Reviewers with no private GitHub access must not assume they can read the original PR. Do not make that repository public for convenience.

## Questions for Claude or independent reviewer
1. Can a GitHub-hosted Ubuntu runner run a Playwright Chromium browser sandbox safely in a non-root container? Identify exact Linux user namespace and seccomp requirements, container options, and specific preflight evidence.
2. How to keep an untrusted webpage isolated from `GITHUB_TOKEN`, runner filesystem, env variables, Git credentials, service sockets and private network/metadata addresses?
3. What is the correct defense against DNS rebinding, redirects, unsafe GET side effects, Chromium/Playwright route interception bypasses, subframes, WebSockets, downloads, popup windows, authentication, service workers and forbidden routes?
4. How to detect disabled/simulated/dummy UI without erroneously marking a site as fraud when CDN resources, unsupported wallet flows or external origins are blocked?
5. Which version-pinned open-source components and license-preserving methods are genuinely useful without any paid API/model token use?
6. How to test with frozen positive and negative websites, independently verify onchain events from deployment to block head, and keep product-authenticity separate from token BUY value?
7. Can the existing Monday Supervisor AI Dev Stack research and existing OSS tool-watch feed REA's Tuesday shadow learning, without any new schedule, duplicative crawler, automatic self-merge or invisible billing?

## Primary public references
- [Official Playwright: Docker, non-root Chromium and seccomp for untrusted websites](https://playwright.dev/docs/docker).
- [Upstream Playwright Docker source](https://github.com/microsoft/playwright/blob/main/docs/src/docker.md).
- [Microsoft Playwright, Apache-2.0 open source](https://github.com/microsoft/playwright).
- [Playwright Linux Chromium sandbox mismatch discussion, August 2026](https://github.com/microsoft/playwright/issues/42452).
- [GitHub Actions: GitHub-hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners).
- [GitHub Actions: Security hardening](https://docs.github.com/en/actions/reference/security/secure-use).
- [Docker seccomp official overview](https://docs.docker.com/engine/security/seccomp/).
- [Browser Use, MIT licensed](https://github.com/browser-use/browser-use). Its open-source Python library is distinct from optional paid hosted inference.
- [Stagehand, MIT licensed](https://github.com/browserbase/stagehand). The agent-inference part typically needs a model; no hidden paid adoption.
- [Claude supported file uploads](https://support.claude.com/en/articles/8241126-upload-files-to-claude). TXT is documented; ZIP isn't among guaranteed supported types.

## Practical security hypothesis
A **non-root** Chromium process in a dedicated short-lived container with explicit seccomp/user namespace support may solve the launch issue while retaining an actual browser sandbox. The solution is **not established by the upstream Docker example alone**. Test the exact GitHub runner environment and avoid privileged containers, host socket mounts, root browser execution, unverified `--no-sandbox`, and unrestricted network egress. In case of failure, leave live browsing disabled.

Additional concerns: a "GET only" client can still trigger server-side state mutations; JavaScript in the visited webpage can make outbound network calls. Denying requests by HTTP method or validating DNS before the browser opens the URL is not a complete isolation boundary. Network-level egress deny rules and constrained capabilities are separate defenses.

## Review output requested
A Danish report with: (1) SHIP/HOLD for trusted synthetic fixture and untrusted website as **different verdicts**, (2) exact P0/P1/P2 issues with reproducible exploit paths and fixes, (3) a pinned $0-external-API container/runner design, (4) at least 8 adversarial tests and 3 normal UI controls, (5) licensing and open-source attribution, and (6) a small budget and GitHub Actions-minute estimate.

No auto-merge, new schedulers, wallet connection, paid subscriptions or deployment authorization follows from this research brief.


## Update — 2026-10-13: offline sandbox proven, HTTPS egress still NOT proven
The historical note above reflects the earlier failed hosted-Chromium sandbox attempts. A **later, private CI proof** succeeded on a pinned Playwright/Chromium non-root Docker sandbox with no network, seccomp/user namespaces and an intentionally unsandboxed negative control (GitHub run 38358406829; accessible only to authorized repository users). This establishes **offline sandbox execution only**. There has been no public-site REA visit and no independent approval for live browsing.

The current P0 work is a **separate stacked private Draft PR #150**, building a bounded in-house HTTPS CONNECT destination broker and synthetic DNS/metadata attack fixtures. It does **not** turn on live browsing, create a new schedule, grant wallet/trading authority or publish private source. Connecting only to an approved DNS-resolved public IP addresses one risk (lookup-to-connect rebinding) but not browser and Node bypass, host firewall, container namespace configuration, or encrypted HTTPS method enforcement.

### High-value external research conclusions
- A Chromium sandbox and HTTPS egress policy solve **different** security problems. Neither substitutes for the other.
- A CONNECT tunnel passes encrypted bytes. Without TLS interception the proxy cannot inspect GET versus POST inside it; therefore a destination-only proxy must **not** be described as a complete read-only guarantee. Even HTTP GET endpoints can have side effects.
- The minimum practical live-release gate is: separate network namespace with **zero direct browser and Node egress**, broker-only network path, host-level private/metadata deny, all special IPv4/IPv6 and Azure platform VIP tests, packet-level bypass tests, bounded evidence and independent security review.
- A functioning UI transition is **not** proof of a working backend, an on-chain value transfer or viable token economics. Keep independent verification and an explicit UNKNOWN result.
- GitHub Actions private repository minutes are finite; no TinyFish Agent/Browser, Firecrawl, hosted inference, or unreviewed autonomous improvement should be added.

Primary sources: [Playwright Docker](https://playwright.dev/docs/docker), [Docker seccomp](https://docs.docker.com/engine/security/seccomp/), [IANA IPv4 special registry](https://www.iana.org/assignments/iana-ipv4-special-registry), [IANA IPv6 special registry](https://www.iana.org/assignments/iana-ipv6-special-registry), [Azure 168.63.129.16](https://learn.microsoft.com/azure/virtual-network/what-is-ip-address-168-63-129-16), [GitHub Actions secure use](https://docs.github.com/en/actions/reference/security/secure-use).
