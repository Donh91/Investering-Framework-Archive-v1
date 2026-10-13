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


## Independent Sol High API security design cross-examination — public, code-free

**Scope:** This document contains no private Alpha Lab source or credentials. The actual private REA implementation remains on private Draft PR #149; the isolated egress research is private Draft PR #150. Reviewing this PUBLIC document cannot be called a code audit, executed security test, or permission to merge. It is a request for an adversarial design-level critique only.

### Frozen system assertions and unresolved gaps

1. **Project-reported offline milestone, not independently verifiable from this public diff:** Nonroot disposable Chromium on Ubuntu 22.04 under a digest-pinned official Playwright Docker image, seccomp, no new privileges, separate renderer user/PID namespaces and `--network none`. The deliberately unsandboxed negative control was rejected. This only proves isolated synthetic browser operation for that image/runner.
2. **Unverified transport P0:** In the original runner, DNS name validation happens before the Playwright-controlled HTTP request is sent. There is no guaranteed connect-time DNS/IP binding. A browser/Node worker with ordinary host networking may still send direct traffic to cloud metadata, private IP, local services, IPv6 special routes or bypass request interception via alternate browser protocols.
3. **Experimental component only:** A proposed HTTPS CONNECT broker accepts an explicitly approved exact hostname and port 443, resolves A and AAAA, rejects any non-public result and then dials an approved literal public IP. The code is not integrated into production or connected to a network-isolated REA deployment. Its in-memory limit controls cannot replace a host-enforced packet filter.
4. **Critical semantic concern:** CONNECT is an opaque bidirectional TLS tunnel. Without inspecting the encrypted requests it cannot independently guarantee GET/HEAD-only. Even GET requests can have side effects. No wallet/credentials reduces consequences but does not prove harmlessness.
5. **Security boundary must be both ways:** The browser and Node orchestrator should have no Internet route except through a separately isolated, least-privileged egress component. The egress component itself should be unable to contact metadata/internal networks even when its application code is compromised, and it must not receive GitHub API tokens, private repo source or Docker socket access.
6. **Integrity boundary:** The site's DOM, screenshots, title, redirects, web metadata and future AI summaries are hostile input. They must not become tool calls, workflow edits, portfolio actions, prompt instructions, unreviewed research truth or an automated merge.
7. **Research boundary:** UI clicking is not backend integrity, economic utilization, protocol execution, verifiable revenue or token quality. A result whose scripts/CDN are policy-blocked must be UNKNOWN/SOURCE_BLOCKED, not LARP or REAL. Prospective blinded controls are needed before any financial utility claim.
8. **Supply-chain concern:** A digest-pin to a browser image does not pin npm transitive dependencies or GitHub Actions ref hashes. The executor runs on a GitHub-hosted VM where the security of kernel namespaces, seccomp/AppArmor and host control must be treated as an assumption, not a demonstrated complete security boundary.

### Adversarial questions and falsification criteria for a separate API advisor

| Code | Hypothesis to attack | Failure condition |
|---|---|---|
| S1 | Deny special/private IPv4 and IPv6 before socket connect | Any metadata/loopback/RFC1918/cloud platform packet succeeds |
| S2 | DNS name and IP pinned at connection | An A/AAAA rebinding, CNAME chain or split-horizon result can route to disallowed IP |
| S3 | HTTP CONNECT-only gateway | It accepts arbitrary ports, request-target smuggling, unknown DNS errors, proxy bypass, CONNECT to IP literals or unsafe upstream |
| S4 | Browser + Node cannot bypass gateway | WebSocket, WebRTC, QUIC/UDP, DNS, DoH, preconnect, service worker, subframe or direct socket egress succeeds |
| S5 | SSL integrity survives literal-IP dial | Wrong hostname/SNI certificate accepted, trust store relaxed or shared-IP vhost confinement incorrectly assumed |
| S6 | TLS tunnel alone is read-only | A POST, state-changing GET or arbitrary HTTPS protocol can pass undetected |
| S7 | Host namespace isolates gateway | Compromised proxy itself can access GitHub runner socket/token, host net, metadata or privileged runtime |
| S8 | Evidence reports are trustworthy | DNS/HTTP block is marked fraud, a demo tab is counted as real backend, or future AI obeys untrusted webpage instructions |
| S9 | CI can authorize a live trial | An unreviewed branch or repository variable can change live gate from false to true or access secrets on a PR |
| S10 | Frozen controls measure value | A retrospective or selection-biased cohort claims forecasting edge without matched baselines and holdout |

### Required differentiation in any conclusions

- **Evidence reported, not independently checked by the public API reviewer:** A previous private synthetic offline Chromium run and its negative control (accessible to authorized repository members), not real-site security.
- **Proposed/partly implemented:** Destination-address filtering and CONNECT dial design are not independently validated in deployment.
- **Not evidenced:** TLS method enforcement, runtime capture of emitted packets, robust DNS rebinding defenses under hostile inputs, full npm/actions supply-chain pinning and an independent code auditor sign-off.
- **No-go rule:** Any S1–S7 **or S9** uncertain, unverified, or positive bypass case means public-site opening stays disabled. Architectural plausibility, test fixture PASS or model approval is insufficient.

### Reviewer priority

Please compare (A) explicit CONNECT broker with system firewall, (B) a pinned-IP HTTP(S) fetch-and-serve model without a live interactive browser, and (C) a supervised browser-only inert-site pilot where no external gateway exists. Identify which option offers the strongest provable **least authority** at the lowest GitHub Actions and implementation cost. Explicitly challenge any use of the phrase “read-only” for an arbitrary public dApp, and specify the smallest **testable, cost-bounded** next change that meaningfully reduces a P0 risk. Unsupported assumptions must remain UNKNOWN.

**Authority:** RESEARCH_ONLY / ADVISORY. Never authorize public browsing, write to private repositories, modify autonomous task schedules, promote investment signals, touch wallets, trade, or increase budgets based on this document. Private source must stay private. Sol output is a reviewer perspective, not a replacement for CI or an independent security sign-off.

### 2026-10-13 independent GPT-6.1 Sol High API advisory — actual receipt and amendments

A bounded **public-document-only** GPT-6.1 Sol High review ran on PR #1595 at exact frozen head `a14440bb2b73f937f687ab780a22cd9dfceb6b4f` (trigger comment `6142502175`). The API receipt reports `PASS`, model `gpt-6.1-sol`, `high`, 4,460 input tokens, 3,667 output tokens, **estimated USD 0.04559**. The model's response was `PASS_WITH_FINDINGS;` with no established implementation-level P0/P1; the stricter downstream report validator declined the semicolon-formatted prefix. **The model invocation happened**, but the automated advisory publication did not validate, and the result is NOT a formal security approval.

Original report: `research/api_agent/outputs/temporary_bridge/pr-1595/comment-6142502175/output.json`; receipt alongside it. Two concrete findings:

- **P2 corrected:** No-go criteria explicitly include the S9 authorization/secret boundary, independently of network safety (a passing S1–S7 does not allow an unreviewed branch, variable or CI job to enable live browsing or read credentials). A dedicated negative case must test S9.
- **P3 corrected:** The private offline CI milestone is labeled as **project-reported and inaccessible to this public reviewer**, even though an authorized private maintainer can check the run. No independent public verification or code audit is implied.

S8 remains an integrity gate for published evidence and automated follow-up, not proof of a particular exploit. S10 prospective performance cannot be inferred from an offline browser canary. No repeated paid Sol call is requested for these documentation-only amendments.

Private REA PRs and all unknown public browsing remain unmerged/disabled pending **independent implementation review and isolated network egress tests**.
