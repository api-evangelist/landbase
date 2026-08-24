---
name: landbase-search
description:
  Reference for landbase-cli search — query patterns that invoke each
  user-facing tool, scoping a contact search to the companies in a dataset you
  own, scope-based routing (build with --mode=default vs self-serve refine with
  workflow enrich + workflow transform vs --mode=research), --download routing,
  session management, 524 recovery, and concurrency limits.
when_to_use:
  when writing a landbase-cli search query and unsure which phrasing invokes the
  right tool, deciding whether to build with --mode=default, refine a pool you
  already have with workflow enrich + workflow transform, or escalate to
  --mode=research, using --download, managing multi-turn sessions, or debugging
  524 timeouts and concurrency limits
version: 1.3.0
---

# Landbase Search

## Query Patterns

All user-facing tools that use `search "<query>"` are dispatched automatically
by the NL agent based on query intent — there is no flag to select them
directly. Use these patterns to invoke the right tool:

| Tool                            | Query pattern                                  | Example                                                          |
| ------------------------------- | ---------------------------------------------- | ---------------------------------------------------------------- |
| **Build Audience**              | "find [title] at [company type] in [location]" | "find VPs of Sales at B2B SaaS companies in the US"              |
| **Search Companies**            | "find [company type] in [location]"            | "find fintech startups in NYC with 50-200 employees"             |
| **Search Contacts**             | "find [title] at [company type]"               | "find heads of marketing at mid-market software companies"       |
| **Contacts in a Dataset**       | "find [title] at companies in ds-XXXX"         | "find heads of sales at the companies in ds-abc123"              |
| **Search by Meaning**           | "find companies that [do/sell/help with X]"    | "find companies that help restaurants manage their supply chain" |
| **Scout Lookalikes**            | "find companies like [domain]"                 | "find companies like stripe.com and braintree.com"               |
| **Expand Titles**               | include a job title to broaden                 | "find roles similar to VP of Revenue Operations"                 |
| **Expand Industries**           | include industries to broaden                  | "find industries adjacent to cybersecurity"                      |
| **Discover Related Industries** | ask for nearby verticals                       | "find verticals related to healthcare IT"                        |
| **Research Products**           | ask what a company sells or offers             | "what products does salesforce.com offer?"                       |
| **Search the Web**              | query needs live or recent information         | "find recent news about Anthropic's funding"                     |
| **Read Webpage**                | query references a specific URL                | "extract content from https://example.com/pricing"               |
| **Find Local Businesses**       | ask for physical locations                     | "find coffee shops in downtown Austin"                           |

Refinement beyond these filters → **Mode Selection** below (usually self-serve
`workflow enrich` + `workflow transform`, not `--mode=research`).

## Contacts at companies in a dataset you own

Any contact/audience query can be scoped to the companies in a dataset you
already own — name its `ds-…` id in the query. The dataset supplies the
**companies**; your title/seniority/other person filters still apply on top
(AND). Omit person filters to pull everyone the search can find at those
companies.

```bash
landbase-cli search "find heads of marketing at the companies in ds-abc123"
```

- **Where the dataset comes from:** an earlier company search's result, or a CSV
  you uploaded. Rows can be companies _or_ people — the only requirement is a
  company identifier column: a **website**, a **LinkedIn company URL**, or a
  **Landbase company id**.
- **Uploaded CSVs: name the onboarded id, not the upload id.** A raw `upload` id
  fails with `its underlying uploaded file is unavailable (404 Not Found)`. Run
  `workflow onboard <upload-id> --wait` and take `.poll.run.output_dataset_id` —
  the trigger response's `dataset_id` is the upload you passed in, not the
  onboarded output. Onboarding prefixes columns with `CLI_` (`company_domain` →
  `CLI_company_domain`): query text can name either, but SQL you write yourself
  (`workflow transform`, `datasets peek`) must use the prefixed names.
- **Must be yours.** You can only target a dataset your own account owns.
- **Fail-closed.** If none of the dataset's rows resolve to known Landbase
  companies, the search errors out — it does **not** silently drop the dataset
  and run an unconstrained search.

This is the path for finding **new contacts** at a set of companies you already
have. Path B (`workflow enrich`/`transform`, below) only reshapes rows already
in a dataset — it can't discover new people.

## Mode Selection

Omitting `--mode` is equivalent to `--mode=default`. But mode is only half the
picture: once a search returns a `dataset_id`, refining it is usually
**self-serve** and needs no new search run. Route by **which data the task must
touch**, not by how complex it is.

### Three paths, by data scope

**Path A — `--mode=default`** (default) — NL audience build over the full
Landbase company/contact database. Returns a `dataset_id` (your "pool"). Usually
under a minute; larger audiences take longer (see _524 Timeout Recovery_ below).
Handles most prospecting queries, including multi-condition filters over
standard fields. **Use this to build or widen a pool.**

**Path B — self-serve refine** (`workflow enrich` → `workflow transform`) —
Works entirely on datasets you already own (a search `dataset_id`, or a dataset
you uploaded). No new search run, no long wait. **Use this to refine a pool you
already have:**

1. `workflow enrich <ds> --company-fields=<field>,…` (and/or `--person-fields=`)
   appends a company/person attribute that wasn't a search filter — e.g.
   `technologies_used`, `description`, `employees_count`, `revenue_range` —
   writing the result to a new dataset. `funding_stage` and `growth_signals` are
   NOT enrich fields: they come back as empty columns (see `workflow-enrich`).
2. `workflow transform <ds-enriched> --sql="…"` runs SQL over `input_dataset`
   (optionally joined via `--additional-datasets` against other datasets you
   own) to filter, rank, derive columns, dedup, or aggregate. Point it at the
   **enrich output** — `.poll.run.output_dataset_id` from the enrich run — not
   the original `<ds>`, which still lacks the just-appended columns.

Scope limit: `workflow transform` sees only datasets you own — never the full
database. `workflow enrich` can append a field only if it's in the
company/person catalog (see Path C for what isn't).

**Path C — `--mode=research`** — Custom SQL over the full Landbase database via
a two-turn flow: turn 1 drafts the SQL and quotes an **estimated credit cost**,
turn 2 confirms and spends it. Reserve for what Path B structurally can't reach
(Path C table below).

```bash
# turn 1 — drafts SQL, returns an estimated credit cost. Free.
landbase-cli search --mode=research --session=p1 \
  "List top 50 SaaS companies in California by employee count"
# turn 2 — authorizes the spend. Only after the user approves the estimate.
landbase-cli search --mode=research --session=p1 "yes, run it"
```

**Turn 2 spends the user's credits — never auto-confirm.** Relay turn 1's quote
verbatim and get explicit approval. The reply quotes cost but not balance — use
`credits balance` for that. Some accounts are exempt from charges; the reply
says so, and nothing is billed. Re-drafting is free; the charge follows actual
usage and can differ from the estimate.

Both turns return in well under the default 300s timeout, but turn 2 only
_starts_ the SQL — it returns `status: "COMPLETED"` and a `dataset_id` while the
workflow is still running. **That envelope is not success.** Poll
`workflow status <ds-id>` to `SUCCEEDED` before reporting rows; it can land on
`FAILED` seconds later with a generic `error_message`, or on `CANCELLED` if
someone stopped it. All three are terminal — stop polling on any of them.

**Turn 2 is the last exit.** `workflow cancel` is accepted on a research run,
but it's a best-effort stop, not an undo: SQL already executing runs to
completion, and the user is billed for the work actually performed. Never offer
cancel as a way to back out of a spend they just approved.

Cost refusals come back as prose in `content` with **exit 0 and no
`dataset_id`** — not an error exit:

- **Quote exceeds balance** — narrow the query, or top up (`credits plans`,
  `credits subscribe`). Re-sending the same query fails identically.
- **Query too large to price** — narrow it: fewer columns, tighter filters.
- **Credential carries no billing account** — Path C is unavailable to it;
  rewording or retrying won't help.

### Path-first rule

**Default to Path A. For post-build refinement, prefer Path B before escalating
to Path C.** `--mode=research` is a last resort — it charges credits and needs a
human go-ahead — not a hedge.

**Path A handles (stay on `--mode=default`):**

| Signal type                          | Examples                                                |
| ------------------------------------ | ------------------------------------------------------- |
| Industry, vertical, sub-industry     | "fintech startups", "logistics companies"               |
| Geography                            | "in the US", "headquartered in NYC"                     |
| Company size / headcount             | "50–200 employees", "mid-market"                        |
| Funding stage                        | "Series A", "recently funded"                           |
| Persona / job title                  | "VP of Sales", "heads of engineering"                   |
| Tech stack                           | "companies using Salesforce"                            |
| Lookalike / similar companies        | "companies like stripe.com"                             |
| Semantic / meaning-based             | "companies that help restaurants manage supply chain"   |
| Local businesses                     | "coffee shops in Austin"                                |
| Multi-condition standard-field logic | "Series B AND fintech AND not in NY AND <500 employees" |

**Path B handles — self-serve, once you have a `dataset_id`:**

| Task on your existing pool                         | How                                                              |
| -------------------------------------------------- | ---------------------------------------------------------------- |
| Filter on an attribute that wasn't a search filter | `workflow enrich` the field, then `workflow transform … WHERE …` |
| Ranked subset within the pool                      | `workflow transform … ORDER BY employees_count DESC LIMIT 50`    |
| Derived / bucketed column                          | `workflow transform` with `CASE WHEN … THEN … END AS segment`    |
| Aggregate within the pool ("count by industry")    | `workflow transform … GROUP BY industry`                         |
| Dedup, or join/union with another dataset you own  | `workflow transform --additional-datasets="b=ds-OTHER" …`        |

**Path C — `--mode=research` — required only when the task must reach the full
database:**

| Signal type                                    | Examples                                            |
| ---------------------------------------------- | --------------------------------------------------- |
| Phrase-match that DEFINES a universe (no pool) | "description mentions 'CFPB compliance'"            |
| Job-posting signals                            | "posted a VP of Sales role in the last 90 days"     |
| Headcount trend / growth rate                  | "grew headcount >20% in last 6 months"              |
| Global top-N over the whole database           | "the 50 largest SaaS companies worldwide"           |
| Join a dataset you own to the whole database   | "for each company in ds-abc123, pull its job posts" |

Path C reaches company, person, and job-posting data, plus any dataset you own
(name its `ds-…` id in the query — it can be joined against the rest; for an
uploaded CSV see
[Contacts at companies in a dataset you own](#contacts-at-companies-in-a-dataset-you-own)).
Other specialty datasets are not queryable through the CLI.

**Spot-check a join before trusting it.** A domain can map to many records
(sub-brands, partner pages, user groups) and the SQL picks one per domain, so a
join can return a row for every input and still be wrong — `match_found: true`
only means a row joined. Verify a few against
`match company --website=<domain>`, which returns the canonical record; if they
disagree, re-run asking for the **most prominent** company per domain.

### "Top N by X" — Path B or Path C?

Ranking is ambiguous: **within your pool** → Path B
(`workflow transform … ORDER BY … LIMIT`); **across the whole database** → Path
C (a `--mode=default` pool may not contain the globally largest rows). When
unclear, ask "Rank within your existing dataset, or across all of Landbase?"
before choosing.

### Path B failure modes — STOP and check

Path B silently returns wrong results in these cases — no error is raised:

- **Pool-completeness trap.** `enrich`/`transform` see only rows already in the
  dataset. If the original `--mode=default` search filtered out rows the
  refinement needs (e.g. pool is US-only, now you want non-US), Path B can't
  recover them. Widen the original search or use Path C.
- **Enrich coverage gap.** `workflow enrich` appends catalog fields only — ask
  for a non-catalog attribute (job-posting signals, headcount trend) and the
  column comes back empty, so a `WHERE` on it silently drops every row. Confirm
  a field is enrichable by asking the NL agent what company/person fields it can
  enrich — **not** with `datasets fields <id>`, which lists the columns already
  on the pool, not the enrichment catalog (a valid-but-unenriched field reads as
  "missing" there, same as a non-catalog one). If it isn't in the catalog, use
  Path C.

### Lookalike synonym normalization

These phrasings all mean **Scout Lookalikes** (`--mode=default`), not
`--mode=research`:

- "companies similar to X"
- "companies like X"
- "find companies comparable to X"
- "alternatives to X"
- "companies in the same space as X"
- "X competitors"
- "what companies look like X"

When X resolves to a **specific company or domain**, route to
`landbase-cli search "find companies like <domain>"` — never to
`--mode=research`. When X is a **category** (e.g. "fintech competitors",
"alternatives to CRM tools"), treat it as a standard industry search on
`--mode=default` instead.

### Ambiguity: ask before routing to `--mode=research`

When a query is ambiguous — it could be Path A (or a Path B refinement) or might
genuinely need Path C — ask one clarifying question rather than defaulting to
Path C. Paths A and B are free; Path C charges credits.

**Ask:** "I can run this as a fast search, refine a list you already have, or
run a custom SQL query over the full database — the last one costs credits and
I'll quote you the estimate before it runs. For '[signal]', do you need exact
phrase matching / job-posting data / a full-database ranking, or will a standard
filter work?"

Only route to `--mode=research` after the user confirms the signal genuinely
requires the full database.

### Phrasing gotchas

Some words mean different things across industries. When a query contains any of
these, confirm intent before searching:

| Term       | Ambiguity                                                      | Clarify with                                                                      |
| ---------- | -------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| "movers"   | Logistics/moving companies OR people who recently changed jobs | "Do you mean moving/logistics companies, or people who recently changed jobs?"    |
| "moving"   | Industry vertical OR hiring/growth signal                      | Same as above                                                                     |
| "agents"   | Real estate agents OR insurance agents OR software agents      | "Which industry — real estate, insurance, or software?"                           |
| "staffing" | Staffing agencies OR companies actively hiring                 | "Are you looking for staffing firms, or companies that are actively hiring?"      |
| "local"    | Geographic (nearby) OR small/independent businesses            | "Do you mean nearby to a specific city, or independently-owned local businesses?" |

## --download Routing

`--download[=<path>]` triggers a download after search. Bare `--download`
defaults to `./results.jsonl`.

| Extension    | Behavior                                                                             |
| ------------ | ------------------------------------------------------------------------------------ |
| `*.parquet`  | Streams raw bytes immediately. No publish step. Column names are not `LB_`-prefixed. |
| `*.csv`      | Triggers `workflow publish --format=csv`, downloads CSV child. Takes a few minutes.  |
| `*.jsonl.gz` | Triggers `workflow publish --format=jsonl.gz`, keeps gzipped.                        |
| `*.jsonl`    | Triggers `workflow publish --format=jsonl.gz`, gunzips on disk.                      |

Use parquet to skip the publish step and get raw results immediately.

## Session Management

`--session=<label>` saves and reuses sessions for multi-turn refinement:

```bash
landbase-cli search "find fintech startups in NYC" --session=nyc-fintech
landbase-cli search "narrow to 50-200 employees" --session=nyc-fintech
```

Sessions are stored in `~/.landbase/sessions.json`. The server echoes
`session_id` in the response — use it for manual recovery.

## 524 Timeout Recovery

Long searches may return HTTP 524 (Cloudflare edge timeout) before the agent
completes. The CLI auto-polls `/runs/latest` until completion or `--timeout` is
reached (default 300s).

If `--timeout` is hit:

```bash
landbase-cli runs latest --session=<id-from-stderr>
```

`runs latest` returns NOT_FOUND while the run is still in flight — wait and
retry.

## Concurrency Limits

- Max 10 concurrent runs per account. HTTP 429 = rate limited.
- CLI auto-retries 3× with 5s/10s/20s backoff honouring `Retry-After`.
- Fan-out beyond 10 workers produces no speedup and burns retries.

## AI Qualification

After getting a dataset from search, qualify it with AI to score each row
against custom yes/no criteria. This is the step that makes Landbase results
meaningfully better than keyword-only filtering — widening first, then
qualifying typically yields 50%+ more results than narrow keywords alone.

```bash
landbase-cli workflow qualify ds-XXXX \
  --qualification-prompts="Is this company a B2B SaaS company?|Does this company have 100 or more employees?" \
  --context-cols=company_name,website,industry,description,employees_count \
  --wait
```

Use the `qualify-leads` skill for the full guided workflow, including column
discovery, criteria translation, and web-search options.
