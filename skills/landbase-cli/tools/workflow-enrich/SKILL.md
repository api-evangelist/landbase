---
name: workflow-enrich
description:
  Batch attribute enrichment on a Landbase dataset — adds company and person
  fields (industry, size, description, technologies, etc.) from the Landbase
  graph at scale.
when_to_use:
  when enriching a dataset with company or person attributes, adding fields like
  industry, size_range, description, or technologies_used to matched records, or
  running the enrich step of the upload → onboard → match → enrich pipeline
version: 1.1.0
user-invocable: true
allowed-tools:
  - Bash
  - AskUserQuestion
model: sonnet
---

# Workflow Enrich

Adds company and person attribute fields to a matched dataset from the Landbase
graph. This is the attribute enrichment step — it adds fields like industry,
size, description, and tech stack. For email and phone enrichment, use
`contact-enrich` instead.

## Run

```bash
landbase-cli workflow enrich ds-MATCHED \
  --company-fields=industry,size_range,description,keywords,technologies_used \
  --wait
```

An unrecognized field name is **not** an error: the run SUCCEEDs and that column
comes back empty on every row. Use the names below verbatim, and `datasets peek`
the output before feeding it to `qualify` or `research` — those read a blank
column as "no information" and answer anyway.

**Interactive runs:** enrich on a large dataset is long. In an interactive
session, trigger **without** `--wait`, capture the `workflow_run_id`, and follow
the `workflow-monitor` skill to narrate live progress — a `--wait` subprocess
can't stream its progress line into the chat. Keep `--wait` for scripted/CI runs
or when the user just wants the final result.

## Flags

| Flag                      | Notes                                                                                                                                                                                                       |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--company-fields=<list>` | Comma-separated company attribute fields to enrich                                                                                                                                                          |
| `--person-fields=<list>`  | Comma-separated person attribute fields to enrich                                                                                                                                                           |
| `--wait`                  | Blocks until the workflow completes. Use for scripted/CI runs or when only the final result is wanted; **drop it in interactive sessions** and monitor live via `workflow-monitor` (see the Run note above) |

## Standard field pack

Common company fields for most enrichment tasks:

```
industry,
size_range, revenue_range, employees_count,
hq_country, hq_state, hq_city,
founded_year, description, keywords, technologies_used,
last_funding_round_name, last_amount_raised_usd, total_amount_raised_usd
```

Identity columns (`company_name`, `website`, `linkedin_url`) are already on the
matched row — no need to request them again.

Names that look plausible but return an empty column: `business_description`
(use `description`), `sub_industry`, `growth_signals`, `funding_stage` (use
`last_funding_round_name`), `employee_count` (use `employees_count`),
`last_funding_amount_usd` / `total_funding_usd` (use the `_amount_raised_usd`
spellings above). These are enrich-path names only — the same word may be valid
in a `search` query, which resolves against a different vocabulary.

## Getting the enriched dataset

Enrich writes a new dataset and leaves `ds-MATCHED` untouched — the finished run
names the output in `output_dataset_id`:

```bash
landbase-cli workflow enrich ds-MATCHED --company-fields=industry,size_range --wait \
  | jq -r '.poll.run.output_dataset_id'
# → ds-ENRICHED
```

Without `--wait`: `workflow status ds-MATCHED --run=<run-id>` →
`.[0].output_dataset_id` once `SUCCEEDED`.

Enrich output downloads directly —
`datasets download <ds-ENRICHED> out.jsonl.gz`, no `publish` step, unlike
`qualify` and `research`. Those are the native bytes; name the file `.jsonl.gz`
because that is what enrich writes, not because the extension converts anything.
`publish` only if you need CSV.

## In the pipeline

`workflow enrich` fits both the upload pipeline and the search-refinement path:

```
# Upload pipeline
upload → onboard → match → enrich → qualify / research → publish

# Search-created pool refinement (Path B in the landbase-search skill)
search --mode=default → enrich → transform → publish
```

Datasets from `search --mode=default` are already matched, so they go straight
to `enrich` (no `onboard`/`match`). Uploaded CSVs must be onboarded and matched
first.

See `dataset-pipeline` for the full upload pipeline with ID extraction, and
`workflow-transform` for the refinement step.

## When to use this instead of --mode=research

To filter or rank a `search --mode=default` list on a catalog attribute it
doesn't carry yet, `workflow enrich` is the self-serve alternative to a fresh
`--mode=research` run — and it doesn't charge credits, which `--mode=research`
does. Append the field here, then filter/rank with `workflow transform`.

**Works** when the attribute is in the Landbase company/person catalog — e.g.
`technologies_used`, `description`, `employees_count`, `revenue_range`,
`founded_year`, `keywords`.

**Does NOT work — use `--mode=research` instead:**

- The attribute is non-catalog — job-posting signals, headcount trend (enrich
  returns an empty column, and a `WHERE` on it drops every row). Confirm with
  `datasets peek` on the enrich output.
- The rows you need were already filtered out of the pool by the original search
  — enrich only appends to rows already present, it can't recover excluded rows.
  Widen the original `--mode=default` search instead.
- The signal needs a phrase-match over the full Landbase database to define the
  universe — enrich only appends to your existing pool.

## Red Flags — STOP

- About to request identity fields (`company_name`, `website`) in
  `--company-fields` → they're already on matched rows, skip them
- Running enrich before `match` → dataset must be matched first; raw
  uploaded/onboarded datasets don't have Landbase IDs to look up against
- Confusing this with `contact-enrich submit` → `workflow enrich` adds graph
  attributes; `contact-enrich` finds email/phone via external providers
