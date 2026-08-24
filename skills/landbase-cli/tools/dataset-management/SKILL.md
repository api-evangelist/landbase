---
name: dataset-management
description:
  Inspect, preview, download, and manage Landbase datasets — fields discovery,
  row previews, lineage, and download.
when_to_use:
  when inspecting a dataset before running a workflow, discovering available
  column names before qualify or transform, checking the status of a dataset,
  viewing parent/child relationships with lineage, downloading results, or
  listing existing datasets
version: 1.1.0
user-invocable: true
allowed-tools:
  - Bash
  - AskUserQuestion
model: sonnet
---

# Dataset Management

## Quick reference

| Task                           | Command                                                              |
| ------------------------------ | -------------------------------------------------------------------- |
| List all datasets              | `landbase-cli datasets list`                                         |
| Show dataset details           | `landbase-cli datasets show ds-XXXX`                                 |
| Discover available columns     | `landbase-cli datasets fields ds-XXXX`                               |
| Preview rows                   | `landbase-cli datasets peek ds-XXXX`                                 |
| Get parent/child relationships | `landbase-cli datasets lineage ds-XXXX`                              |
| Download a dataset             | `landbase-cli datasets download ds-XXXX file.csv`                    |
| Delete a dataset               | `landbase-cli datasets delete ds-XXXX` (requires `--yes` to confirm) |

## fields — discover columns before running workflows

Always run `datasets fields` before `workflow qualify`, `workflow transform`, or
`workflow research` to confirm column names. Column names vary by dataset
source:

```bash
landbase-cli datasets fields ds-XXXX
```

Datasets produced by `workflow onboard` have columns prefixed with `CLI_` (e.g.
`CLI_website`, `CLI_company_name`). Raw search results and enriched datasets use
standard names (e.g. `website`, `company_name`).

## peek — preview rows before committing to a long workflow

```bash
landbase-cli datasets peek ds-XXXX
```

Use `peek` before running `qualify` or `transform` on a large dataset to verify
the data shape and spot issues early.

## lineage — walk the dataset tree

For the **main result** of a step you just ran, read `output_dataset_id` off the
finished run — `.poll.run.output_dataset_id` under `--wait`, or
`workflow status <input-ds> --run=<run-id>` → `.[0].output_dataset_id`.

Use `lineage` for everything else: auditing where a dataset came from, listing
every child of a parent, recovering the output of a run old enough that
`output_dataset_id` is null, and finding a run's **other** outputs.

```bash
landbase-cli datasets lineage ds-XXXX --direction=children --workflow=<name>
# newest-first, so [0].id is the newest child of that type — a guess, not
# necessarily a given run's output, once a step has run twice on one parent

landbase-cli datasets lineage ds-XXXX   # full tree, both directions
```

`--workflow` takes the _server-side_ name: `onboard`, `match`, `enrich_only`
(alias `enrich`), `qualify`, `research`, `dataset_transform` (no `transform`
alias), `sketch`, `publish`, `similar_company_expansion`, `crm_suppress`.

**One run can register more than one dataset.** `output_dataset_id` names only
the primary; siblings appear in lineage under their own `workflow_name` —
`onboard` leaves a `column_mapping` sidecar beside the onboarded table,
contact-enrich a summary report at a different grain. Chain the primary forward;
the siblings are for auditing.

## download — get results locally

```bash
landbase-cli datasets download ds-XXXX results.jsonl.gz
```

`download` streams **native bytes** and converts nothing — the path is just a
filename, so a `.csv` name gets you whatever the producing workflow wrote under
a `.csv` name. Name the file after what the producer writes:

| Producer                                    | Native format   |
| ------------------------------------------- | --------------- |
| `search`, `onboard`                         | `.parquet`      |
| `match`, `transform`/`union`/`relaxed-join` | `.zstd.parquet` |
| `enrich`                                    | `.jsonl.gz`     |

To get a format you chose rather than the native one, `publish` first and
download the id that run reports:

```bash
DS=$(landbase-cli workflow publish ds-XXXX --format=csv --wait \
  | jq -r '.poll.run.output_dataset_id')
landbase-cli datasets download "$DS" ./results.csv
```

Not every output downloads directly:

| Output of                                                                                             | `datasets download` |
| ----------------------------------------------------------------------------------------------------- | ------------------- |
| `upload`, `onboard`, `match`, `search`, `enrich`, `transform`, `union`, `relaxed-join`, `publish`     | works               |
| `qualify`, `research`, advanced-search, `contact-enrich`, `crm-suppress`, `similar-company-expansion` | `PUBLISH_REQUIRED`  |

Publish those, then download that run's `output_dataset_id`.

## list and show

```bash
# List recent datasets
landbase-cli datasets list

# Show details for a specific dataset
landbase-cli datasets show ds-XXXX
```

## Red Flags — STOP

- About to run `workflow qualify` or `workflow transform` without checking
  `datasets fields` → column names vary; missing or wrong names cause silent
  failures
- Dataset shows `CLI_`-prefixed columns and you're passing
  `--website-column=website` to `similar-company-expansion` → use
  `--website-column=CLI_website` instead
- `PUBLISH_REQUIRED` on `download` → `publish` it, then download that run's
  `output_dataset_id`
- Reading the dataset you passed IN to a workflow and seeing no new columns →
  you want the run's `output_dataset_id`; steps never modify their input in
  place
