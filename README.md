# Landbase

<!-- API-EVANGELIST-PROVENANCE:BEGIN -->
> ### About this repository
>
> **This is not our API.** This repository is an independent, third-party profile of a company's
> **publicly available** API surface, maintained by [API Evangelist](https://apievangelist.com).
> API Evangelist does not operate, host, resell, or support this company's APIs, and is not
> affiliated with or endorsed by the company unless stated on the profile.
>
> **Where the information came from.** Everything here is assembled from material a member of the
> public can reach with a browser and no credentials — the company's own website, developer portal
> and documentation, the specifications it publishes for public use (OpenAPI, AsyncAPI, JSON Schema,
> `apis.json`, `llms.txt` and similar), its public repositories, and its public status, pricing and
> changelog pages. **Nothing here is obtained by breaching a system, defeating an access control, or
> using credentials of any kind.**
>
> **The rating is an independent assessment.** The Kin Score and Agent Readiness rating are
> independently calculated scores of a company's *public* API artifacts, produced by API Evangelist
> against a published rubric. They are not certifications, endorsements, security assessments, or
> audits, and they score published artifacts — not the quality, safety, or security of the software.
>
> **Corrections, re-scores, and removal are free.** No partnership, contract, or purchase is
> required, and you do not need to justify the request.
>
> - **Something wrong?** Open an issue on this repository, or email
>   [info@apievangelist.com](mailto:info@apievangelist.com).
> - **Published something new?** Ask for a re-score and we will re-run the rating.
> - **Want the listing taken down?** Say so and we will honor it. The profile is reduced to your
>   company name, a factual description, and a link to your own site, and the company is recorded as
>   **unrated** — never scored zero for having asked.
>
> **Response times.** Acknowledgement within **one business day**; removal or restriction within
> **two business days**; corrections and re-scores within **five business days**.
>
> **Not from the company, and here with a question?** You are welcome here — we would rather be the
> front line and point you the right way than have a good report go nowhere. What this repository
> can answer is narrow, though, so it is worth knowing who you are actually looking for:
>
> - **A question about how the API works, an account, billing, or a bug in the service** — that is
>   the company's own support, not us. We profile this API; we do not operate it and cannot see
>   your account.
> - **A bug in an open-source project we only catalog** — file it on that project's own repository.
>   This has happened with a real and correct bug report that reached us instead of the people who
>   could fix it, which helped nobody.
> - **Anything about this listing itself** — the description, the tags, the rating, a missing or
>   wrong artifact — is ours. Open an issue here.
> - **Not sure, or something general about API Evangelist or APIs.io** — open an issue on the
>   [APIs.io Inbox](https://github.com/api-search/inbox) and we will route it.
>
> **This repository contains no software, and we will never ask you to download anything.** There is
> no build, release, installer, or binary here — only text and machine-readable API descriptions, so
> there is nothing here that can be "corrupt" or need "repairing". Any issue, comment, or email
> claiming otherwise and offering a download link is not from us and is hostile. Do not follow the
> link; it is a lure. Report it to GitHub and, if you like, tell us at
> [info@apievangelist.com](mailto:info@apievangelist.com) so we can take it down.
>
> **On a security or compliance team?** Email
> [info@apievangelist.com](mailto:info@apievangelist.com) with *security* in the subject line and
> you will get a person, not a form. We will tell you exactly which public URLs this profile was
> built from so your team can see the same surface we did, and we will take the listing down on
> request while you work through it.
>
> Full detail: **[Where this data comes from](https://apievangelist.com/about/where-our-data-comes-from)**
<!-- API-EVANGELIST-PROVENANCE:END -->

Landbase is a Palo Alto, California go-to-market (GTM) data and agentic-AI company whose platform builds, qualifies, enriches and activates B2B audiences from natural-language requests. Its GTM-1/GTM-2 Omni models sit behind a B2B database of 300M+ contacts with 1,500+ enrichment fields, an agentic search surface, lookalike expansion, AI lead qualification, and email/LinkedIn outbound campaign execution. Landbase's programmable surface is deliberately agent-first rather than REST-first: the documented client is `landbase-cli`, a self-updating binary distributed from cli.landbase.com that talks to the cloud gateway at api.landbase.com, returns JSON on stdout and stable error codes on stderr, and ships a library of provider-authored Agent Skills for Claude Code and Codex. No OpenAPI description of the gateway is published; the gateway itself sits behind a Cloudflare bot challenge on every path except /.well-known/.

**Areas:** Company · Go-To-Market · Sales · Marketing · B2B Data · Data Enrichment · Artificial Intelligence · Agents · Command Line Interface · Lead Generation

## Landbase on APIs.io

Everything profiled for Landbase is published on APIs.io rather than in this repository. Start at the provider page — **[apis.io/providers/landbase/](https://apis.io/providers/landbase/)** — or go straight to one of the APIs or properties below.

### APIs (1)

- [Landbase Platform API](https://apis.io/apis/landbase/landbase-platform-api/) — The Landbase cloud gateway that landbase-cli calls in platform mode. It backs natural-language audience search and agent runs, dataset…

### Published properties

Each property below is a page on APIs.io carrying the machine-readable artifact and what it says.

#### Agent skills (23)

Agent skills built on the API.

- [contact-enrich](https://apis.io/agent-skills/landbase/contact-enrich/)
- [contacts-import](https://apis.io/agent-skills/landbase/contacts-import/)
- [dataset-management](https://apis.io/agent-skills/landbase/dataset-management/)
- [dataset-pipeline](https://apis.io/agent-skills/landbase/dataset-pipeline/)
- [dedupe-leads](https://apis.io/agent-skills/landbase/dedupe-leads/)
- [icp-capture](https://apis.io/agent-skills/landbase/icp-capture/)
- [landbase-email-campaigns](https://apis.io/agent-skills/landbase/landbase-email-campaigns/)
- [landbase-feedback](https://apis.io/agent-skills/landbase/landbase-feedback/)
- [landbase-linkedin-campaigns](https://apis.io/agent-skills/landbase/landbase-linkedin-campaigns/)
- [landbase-quickstart](https://apis.io/agent-skills/landbase/landbase-quickstart/)
- [landbase-search](https://apis.io/agent-skills/landbase/landbase-search/)
- [list-similarity-check](https://apis.io/agent-skills/landbase/list-similarity-check/)
- [lookalike-expansion](https://apis.io/agent-skills/landbase/lookalike-expansion/)
- [match-lookup](https://apis.io/agent-skills/landbase/match-lookup/)
- [presentation](https://apis.io/agent-skills/landbase/presentation/)
- [prospect-builder](https://apis.io/agent-skills/landbase/prospect-builder/)
- [qualify-leads](https://apis.io/agent-skills/landbase/qualify-leads/)
- [query-assist](https://apis.io/agent-skills/landbase/query-assist/)
- [tam-mapping](https://apis.io/agent-skills/landbase/tam-mapping/)
- [transcript-synthesis](https://apis.io/agent-skills/landbase/transcript-synthesis/)
- [workflow-enrich](https://apis.io/agent-skills/landbase/workflow-enrich/)
- [workflow-monitor](https://apis.io/agent-skills/landbase/workflow-monitor/)
- [workflow-transform](https://apis.io/agent-skills/landbase/workflow-transform/)

#### Security (3)

Authentication, trust centre, and vulnerability disclosure.

- [Landbase Authentication](https://apis.io/security/landbase/landbase-authentication/)
- [Landbase Domain Security](https://apis.io/security/landbase/landbase-domain-security/)
- [Landbase Trust Center](https://apis.io/security/landbase/landbase-trust-center/)

#### Plans and pricing (1)

Published plans, tiers and prices.

- [Landbase Plans Pricing](https://apis.io/plans/landbase/landbase-plans-pricing/)

#### Rate limits (1)

Published request limits.

- [Landbase Rate Limits](https://apis.io/rate-limits/landbase/landbase-rate-limits/)

## Where to find this API

Links to the company's own pages. This repository publishes no copy of their specifications — the canonical document is theirs and lives at the URLs below.

- [Website](https://www.landbase.com/)
- [Documentation](https://www.landbase.com/docs)
- [Getting started](https://www.landbase.com/docs/quickstart)
- [API reference](https://www.landbase.com/docs/reference/search)
- [Pricing](https://www.landbase.com/pricing)
- [Sign up](https://accounts.landbase.com/sign-up)
- [Support](https://support.landbase.com/landbase/directories)
- [Blog](https://www.landbase.com/blog)
- [Terms of service](https://www.landbase.com/legal/terms-of-service)
- [Privacy policy](https://www.landbase.com/legal/privacy-policy)
- [GitHub](https://github.com/landbaseapp)

## API Evangelist rating

**Kin Score 45.8** — developing · rubric 0.25.0 · scored 2026-10-23

| Facet | Score |
|---|---|
| Discoverability | 73.2 |
| Contract quality | 0.0 |
| Contract governance | 0.0 |
| Operational transparency | 50.0 |
| Developer ergonomics | 66.7 |
| Access clarity | 84.2 |

**Agent readiness 18.7** — agent-aware

| Agent-readiness dimension | Result |
|---|---|
| Spec Presence | — |
| Agentic Access | — |
| Reversibility Documented | — |
| MCP Server | — |
| Auth Clarity | served (partial credit) |
| Idempotency | documented (partial credit) |
| Error Semantics | documented (partial credit) |
| OpenAPI Examples | — |
| Rate Limit Signal | documented (partial credit) |
| Event Surface Described | — |
| Agent Skills | yes |
| Well Known Catalog | — |
| Consent Identity | — |
| Agent Card | — |
| Dry Run Mode | — |
| Delegated Identity | — |
| Protected Resource Metadata | — |
| Dynamic Client Registration | — |
| Agentic Commerce | — |
| Pagination Ratio | na |
| Operation Distinctiveness | na |

**Regulatory alignment 27.3** — Horizontal (data, software, accessibility, platform)

The rubric is published at [github.com/api-evangelist/kin-score](https://github.com/api-evangelist/kin-score). The per-check breakdown behind these numbers — which checks were earned, partial or missed — along with score history and how this provider compares to its peers, is available at [apis.io/providers/landbase/](https://apis.io/providers/landbase/).

## How this profile is made

API Evangelist profiles a company's public API surface the way a developer would find it: the website, developer portal and documentation, the specifications it publishes, its public repositories, and its pricing, status and changelog pages. From that it derives the properties above — contracts split per API, workflows, schemas, collections, governance rules, plans and rate limits — and scores them against the published [Kin Score rubric](https://github.com/api-evangelist/kin-score).

The artifacts are published on [APIs.io](https://apis.io), not in this repository. This repository is the public record for Landbase: the place to say something is wrong, missing or out of date, and to ask for a re-score or a removal.

## Open an issue

- **Something about this listing** — a wrong description, a missing API, a stale artifact or a question about the rating: [open an issue on this repository](https://github.com/api-evangelist/landbase/issues/new).
- **A new API, or one that is not in the catalog yet** — [submit it on APIs.io](https://apis.io/add/).
- **Anything else** — [the APIs.io inbox](https://github.com/api-search/inbox/issues/new) or [info@apievangelist.com](mailto:info@apievangelist.com).
