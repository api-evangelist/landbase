---
name: query-assist
description:
  Translate an ICP definition into a well-formed Landbase search query with the
  standard attribute pack, route signals by data scope to the right execution
  path (standard NL search, self-serve enrich+transform refine, or advanced
  SQL), and execute to produce a downloadable prospect dataset.
when_to_use:
  when the user has an icp-definition.md and wants to build a prospect dataset
  from it, or says "build the query", "run the search", "translate my ICP to a
  query", "generate the audience", or after icp-capture completes and the user
  is ready to build
version: 1.1.0
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
model: sonnet
---

# Query Assist

Translates an ICP definition into a Landbase search query, routes to the right
execution path, and downloads the resulting dataset. Mirrors Phase 2 (Query
Assist) from the internal `tam-mapping` pipeline.

## Hard rules

1. **Always discover canonical taxonomy before drafting the query.** Never infer
   industry values from the ICP definition alone — seed enrichment shows only
   what the examples hit, not the full taxonomy. Query the NL agent first.
2. **Show the full query verbatim before executing.** The user must approve the
   exact query and attribute pack before any dataset is created. You can't
   un-run — or un-charge — a `--mode=research` query.
3. **Always include the standard attribute pack.** Don't trim it — downstream
   skills (tam-mapping, qualify-leads) depend on these columns being present.
4. **Default-first — exhaust Path A and Path B before routing to Path C
   (`--mode=research`).** Path C charges credits; Paths A and B don't. Before
   using it, confirm the signal can't be handled by `--mode=default` (Path A) or
   by `workflow enrich` + `workflow transform` on the built list (Path B). Say
   so and ask: "This signal needs the full Landbase database, which costs
   credits — I'll quote you the estimate before anything runs. Proceed, or try
   the fast path first?" Only route to Path C after the user confirms.

---

## Step 1 — Read the ICP definition

Read `icp-definition.md` from the current directory or a path the user provides.

Extract:

- Must-have signals and their values
- Should-have signals (noted separately — don't include in base query)
- Build path routing (Path A / Path B / Path C per signal, if already in the
  file)
- Proposed query (if already drafted in the file — show it and ask if they want
  to regenerate)

If no `icp-definition.md` exists, ask the user to describe their ICP briefly or
run `icp-capture` first.

---

## Step 2 — Canonical taxonomy discovery

Before drafting the query, ask the NL agent for the canonical Landbase industry
taxonomy for the ICP's vertical:

```bash
landbase-cli search "What Landbase company-industry taxonomy values cover [vertical X]? \
  Return the canonical industry tags to use as filters, any adjacent tags to consider, \
  and any broad-bucket tags that will pull noise. List only — don't build an audience."
```

Mirror the agent's primary tag set verbatim in the query. If the ICP's industry
values already match the canonical tags (e.g. carried from `icp-capture` Step
5), confirm they're still current before proceeding.

---

## Step 3 — Build path routing

Assign each must-have signal a path by **data scope** — which data the signal
must touch — not by query complexity:

| Path                      | When                                                                                                                                                          | Command                                                                                               |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **A — Standard search**   | Industry, size, geography, persona, tech stack, keywords, lookalikes; multi-condition logic over standard fields                                              | `landbase-cli search "..."`                                                                           |
| **B — Self-serve refine** | Post-build: filter/rank/derive/dedup on a catalog attribute not in the built list, or a join/union across lists you own                                       | `workflow enrich` the `dataset_id` Path A produced, then `workflow transform` its `output_dataset_id` |
| **C — Advanced search**   | Phrase-match that defines the universe, job-posting signals, headcount-growth, global top-N, joining a list you own to the whole database — **costs credits** | `landbase-cli search --mode=research "..."`                                                           |

**Default to Path A**, then prefer Path B before Path C. For each signal, ask in
order:

1. Can Path A express it as a standard NL filter (industry, geo, size, persona,
   tech stack, multi-condition standard-field logic)? → **Path A** (~30s).
2. Is it a refinement over a catalog field on the list Path A produces (e.g.
   filter to a `technologies_used` value, rank by `employees_count`)? → **Path
   B**: `workflow enrich` the field, then `workflow transform` that run's
   `output_dataset_id` — no new search.
3. Does it need the full Landbase database? → **Path C** (`--mode=research`,
   charges credits).

Joining a list you own on Path C: name the onboard run's `output_dataset_id`,
not the `upload` id, and spot-check matched names against
`match company --website=` before using the result — see
[landbase-search](../landbase-search/SKILL.md).

**Path B scope caveat:** it touches only rows already in your list — if Path A
was filtered so needed rows were excluded (e.g. built US-only, now want non-US),
widen Path A or use Path C. And `workflow enrich` appends catalog fields only;
non-catalog attributes (job-posting signals, headcount trend) come back empty →
Path C.

Produce a per-signal routing table and show it to the user before drafting the
query. For any Path C signals, get explicit user confirmation (Hard rule 4)
before proceeding.

---

## Step 4 — Draft the query

### Standard attribute pack

Always include these columns in the query output — don't trim:

```
company_name, website, linkedin_url,
industry, sub_industry, size_range, revenue_range, employees_count,
hq_country, hq_state, hq_city,
founded_year, description, keywords, technologies_used,
funding_stage, last_funding_amount_usd, total_funding_usd,
growth_signals
```

### Path A — Standard NL query

Build the query from must-have attributes using canonical taxonomy tags from
Step 2. Must-haves only — don't add should-haves to the base query:

```bash
landbase-cli search "find [persona] at [canonical industry tags] in [geography] \
  with [size] employees. Include: company_name, website, linkedin_url, industry, \
  sub_industry, size_range, employees_count, hq_country, hq_state, hq_city, \
  description, keywords, technologies_used, funding_stage, growth_signals." \
  --download=prospects.jsonl
```

### Path B — Self-serve refine

Not drafted here — Path B runs _after_ the Path A build. Build the base list
with Path A, then `workflow enrich` the resulting `dataset_id` (appends the
catalog attribute to a **new dataset**, named in the finished run's
`output_dataset_id`), then `workflow transform` that id (filter/rank/derive/
dedup/join over your list). See the `workflow-enrich` and `workflow-transform`
skills for field selection and SQL. Don't carry the attribute pack above into
`--company-fields` — that list is search vocabulary, and several of its names
enrich to empty columns. No new search run, so nothing to confirm here beyond
the Path A query.

### Path C — Advanced search

Translate the query to NL for `--mode=research`. The NL prompt must:

- Preserve all phrase lists verbatim (don't summarize)
- Include the full standard attribute pack in the SELECT
- Specify geography and size filters
- Specify dedup (one row per company)

```bash
landbase-cli search --mode=research \
  "[NL prompt describing the full query including all signals and attribute pack]" \
  --session=<slug>-query
```

The agent drafts SQL and quotes an estimated credit cost — a two-turn
conversation (Step 5).

Show the full NL prompt or query to the user before executing. Ask: "Does this
look right?"

---

## Step 5 — Execute

### Path A execution

```bash
landbase-cli search "[approved query]" --download=prospects.jsonl
```

Download completes synchronously. Report row count and a sample of 5 rows.

### Path B execution (self-serve refine)

Run after the Path A download, on the `dataset_id` it produced.
`workflow enrich` writes the appended fields to a **new child dataset** —
resolve that child and transform it; transforming the original id runs against
the un-enriched pool and the SQL fails on the missing columns:

```bash
landbase-cli workflow enrich <dataset-id> --company-fields=<field>,… --wait
# enrich wrote a child — get its id, then transform THAT:
landbase-cli datasets lineage <dataset-id> --direction=children --workflow=enrich
# → [{ "id": "ds-ENRICHED", ... }]
landbase-cli workflow transform ds-ENRICHED --sql="…" --wait
```

Follow the `workflow-enrich` and `workflow-transform` skills. Fast (seconds to
minutes), no confirmation turn.

### Path C execution (two-turn)

**Turn 1:** Send the NL prompt. The agent drafts SQL, prices it, and returns
both for review:

```bash
landbase-cli search --mode=research "[NL prompt]" \
  --session=<slug>-query
```

Show the drafted SQL **and the quoted credit estimate** to the user. Verify the
SQL:

- Preserves all phrase lists
- Includes the standard attribute pack
- Has correct geography and size filters
- Deduplicates to one row per company

If the SQL dropped something or simplified incorrectly, send a follow-up turn to
correct it before confirming. Re-drafting is free.

**Turn 2:** Confirm execution — **this spends the quoted credits.** Send it only
after the user has seen the estimate and explicitly approved it:

```bash
landbase-cli search --mode=research "yes, run it" \
  --session=<slug>-query
```

Both turns return in seconds. The charge follows actual usage and can differ
from the estimate; exempt accounts are told so in the reply and billed nothing.
If the quote exceeds the balance (or the query is too large to price), turn 2
declines with the reason in `content` — **exit 0, no `dataset_id`**. Narrow the
query, or top up with `credits plans` / `credits subscribe`; re-sending the same
query fails identically.

Turn 2 returns `status: "COMPLETED"` and a `dataset_id` while the SQL is still
running — **not success.** Poll to `SUCCEEDED` before reporting rows; a run can
land on `FAILED` seconds later with a generic `error_message`, or on `CANCELLED`
if someone stopped it. All three are terminal — stop polling on any of them:

```bash
landbase-cli workflow status <dataset-id>
```

When complete, publish and download:

```bash
landbase-cli workflow publish <dataset-id> --format=csv --wait
landbase-cli datasets download <published-dataset-id> prospects.csv
```

---

## Step 6 — Deliver

Report to the user:

- Row count
- Sample of 5 rows (company name, website, industry, size, location)
- File path of the downloaded dataset
- Dataset ID (for use with qualify-leads, tam-mapping, or lookalike-expansion)

If a Google Drive MCP is available, offer to push to Google Sheets.

**Next steps to suggest:**

- Run `qualify-leads` on the dataset to filter to must-have criteria
- Run `tam-mapping` to score and tier the full list
- Run `lookalike-expansion` using the dataset as seeds

---

## Red Flags — STOP

- About to draft the query before running Step 2 (taxonomy discovery) → always
  discover canonical tags first
- About to execute without showing the query verbatim to the user → always show
  and confirm
- About to trim the standard attribute pack → don't; downstream skills depend on
  these columns
- About to route to Path C without checking if Path A or Path B could handle it
  → `--mode=default` first, then self-serve `enrich` + `transform`; only
  escalate to `--mode=research` after confirming the signal needs the full
  database
- About to send Turn 2 → it is a spend authorization; always relay the quoted
  estimate and get explicit user approval first
- Should-haves included in the base query → must-haves only in the base;
  should-haves are qualify-leads refinements
