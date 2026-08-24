---
name: qualify-leads
description:
  Run AI qualification on a Landbase dataset to score each row as qualified or
  not against custom yes/no criteria. Use when the user wants to filter a
  prospect list, score leads against ICP criteria, or find the best-fit accounts
  in a dataset.
when_to_use:
  when the user wants to qualify, score, or filter leads against specific
  criteria — phrases like "which of these fit our ICP", "filter to enterprise
  only", "score these leads", "qualify this list", "find the ones that match X",
  or when working with a dataset that needs to be narrowed down
version: 1.1.0
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
model: sonnet
---

# Qualify Leads

Run AI qualification on a dataset. Each row is evaluated against your criteria
and marked qualified or not.

## Hard rules

1. **Qualification prompts must be yes/no questions.** The AI answers yes or no
   per row — not scores, not open-ended analysis. If the user gives you criteria
   that aren't yes/no, rewrite them into yes/no questions and confirm.
2. **Multiple prompts use AND logic.** A row is only qualified if it passes all
   prompts. Be explicit with the user about this before running.
3. **Always check available columns first.** Run `datasets fields` before
   picking context columns — don't guess column names.
4. **Landbase only.** If the dataset is thin and qualification is uncertain,
   recommend enriching through Landbase first rather than enabling web search as
   a substitute for missing data.

## Workflow

### Step 1: Confirm the dataset

Ask the user for the dataset ID (`ds-XXXX`). If they don't have one, they need
to run a search or upload a CSV first.

Check what columns are available:

```bash
landbase-cli datasets fields ds-XXXX
```

### Step 2: Define qualification criteria

Ask the user: what makes a lead qualified? Translate their answer into explicit
yes/no questions:

| User says          | Qualification prompt                                  |
| ------------------ | ----------------------------------------------------- |
| "enterprise SaaS"  | "Is this an enterprise SaaS company?"                 |
| "100+ employees"   | "Does this company have 100 or more employees?"       |
| "US only"          | "Is this company headquartered in the United States?" |
| "raises Series B+" | "Has this company raised a Series B round or later?"  |

If multiple criteria, confirm they should all be required (AND logic).

### Step 3: Choose context columns

Select the columns that give the AI enough signal to answer the prompts. More
columns = better accuracy, but slower.

Good defaults for most qualification tasks:

```
company_name,website,industry,description,employees_count,hq_country
```

Only include columns that exist in the dataset (verified in Step 1).

### Step 4: Decide on web search

Ask the user whether to enable web search (`--enable-web-search`).

**Enable when:**

- Criteria require information not likely in the dataset (funding stage, recent
  news, product details)
- Dataset descriptions are sparse

**Skip when:**

- Criteria can be answered from structured fields (employee count, industry,
  location)
- Speed matters more than precision

Web search is slower and costs more API calls per row. Be explicit about this
tradeoff.

### Step 5: Decide on early stopping (optional)

If the user wants the top N qualified leads rather than a full scan:

```bash
--stop-early-at-num-qualified=N
```

Useful for large datasets when you only need a fixed number of results. Ask if
they have a target count.

### Step 5b: Slice a large input (`--row-slice`)

**Above 100 rows, tile in 100-row windows** — with or without `--wait`.
`landbase-cli datasets show ds-XXXX` reports `row_count`; at 100 rows or fewer,
run one pass and skip this step.

`--row-slice=START:END` qualifies input rows `START..END-1` (half-open) and puts
only those rows in the output, so each slice registers its own child dataset.
Qualification is slow per row (slower still with `--enable-web-search`): tiling
lands completed children as you go rather than one all-or-nothing result. Under
`--wait` it also keeps each run inside the 30-minute poll ceiling, past which
`--wait` exits `TIMEOUT` while the run keeps going.

```bash
# 250 rows → three tiles, run one at a time (see Rules).
for s in 0:100 100:200 200:300; do
  landbase-cli workflow qualify ds-XXXX --row-slice=$s \
    --qualification-prompts="Is this an enterprise SaaS company?" \
    --context-cols=company_name,website,industry --wait \
    | jq -r '.poll.run.output_dataset_id'
done

# One output per slice ("... rows 0-99" etc.), or list them all at once:
landbase-cli datasets lineage ds-XXXX --direction=children --workflow=qualify

# Recombine. No --dedupe-keys: the tiles are disjoint, so a union keeps every row.
landbase-cli workflow union ds-SLICE0 ds-SLICE1 ds-SLICE2 --wait
```

Rules:

- **Run slices serially, not in parallel.** A single run already qualifies its
  rows concurrently, so parallel slices add no throughput. Slicing buys a run
  you can poll to completion, not a faster one.
- A last slice running past the final row is fine — it returns the remaining
  rows.
- `--row-slice` with `--stop-early-at-num-qualified` → `INVALID_INPUT`: an early
  stop leaves a tile partly qualified but recorded as fully covered. Narrow the
  window instead of working around this.
- **Recombine without `--dedupe-keys`.** Tiles are disjoint, so a key drops rows
  instead of merging duplicates. Verify the union's `row_count` equals the sum
  of the tiles'.
- **Row order is not preserved.** Qualification runs concurrently, so output
  order varies between runs. The recombined dataset holds every row but not in
  the original sequence — don't tell the user their list came back in the order
  they supplied it.

### Step 6: Run qualification

**Interactive vs. scripted.** In an interactive session, trigger **without**
`--wait`, capture the `workflow_run_id`, and follow the `workflow-monitor` skill
to narrate live progress (rows/`%`/ETA) — a `--wait` subprocess can't stream its
progress line into the chat. Use `--wait` only for a scripted/CI run or when the
user just wants the final result. Drop the `--wait` from the examples below when
monitoring live.

Full run:

```bash
landbase-cli workflow qualify ds-XXXX \
  --qualification-prompts="Is this an enterprise SaaS company?|Does this company have 100+ employees?" \
  --context-cols=company_name,website,industry,description,employees_count \
  --wait
```

With web search:

```bash
landbase-cli workflow qualify ds-XXXX \
  --qualification-prompts="Has this company raised Series B or later?" \
  --context-cols=company_name,website,description \
  --enable-web-search \
  --wait
```

With early stopping:

```bash
landbase-cli workflow qualify ds-XXXX \
  --qualification-prompts="Is this a B2B company?" \
  --context-cols=company_name,website \
  --stop-early-at-num-qualified=25 \
  --wait
```

### Step 7: Deliver results

Qualify writes a NEW dataset — read its id off the finished run, not the id you
passed in:

```bash
# With --wait
landbase-cli workflow qualify ds-XXXX ... --wait | jq -r '.poll.run.output_dataset_id'

# Monitored without --wait — once the run is SUCCEEDED
landbase-cli workflow status ds-XXXX --run=<run-id> | jq -r '.[0].output_dataset_id'
```

Only if that is null, fall back to
`datasets lineage ds-XXXX --direction=children --workflow=qualify`. A sliced run
(Step 5b) produces one output per slice — recombine them first.

There is no `qualified` column: a single-prompt run may carry
`ai_qualification_result`, a multi-prompt one per-criterion columns, and
`publish` prefixes Landbase columns with `LB_`. Read the real names off
`datasets fields <output-id>` (or the published header) before filtering.

Qualify output is partitioned, so `datasets download` on it fails with
`PUBLISH_REQUIRED`. Publish, then download that run's output:

```bash
DS=$(landbase-cli workflow publish <output-id> --format=csv --wait \
  | jq -r '.poll.run.output_dataset_id')
landbase-cli datasets download "$DS" qualified-leads.csv
```

Report: how many rows evaluated, how many qualified, what percentage passed.

If a Drive MCP is available, push to Google Sheets and return the live URL.

## Flags reference

| Flag                              | Required | Notes                                                                                                                                                                                           |
| --------------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--qualification-prompts="..."`   | Yes      | Pipe-delimited (`\|`) list of yes/no questions                                                                                                                                                  |
| `--context-cols=col1,col2`        | Yes      | Comma-separated; must exist in the dataset                                                                                                                                                      |
| `--enable-web-search`             | No       | Slower, more accurate for criteria not in structured fields                                                                                                                                     |
| `--stop-early-at-num-qualified=N` | No       | Stop scanning once N rows have qualified. Cannot be combined with `--row-slice`                                                                                                                 |
| `--row-slice=START:END`           | No       | Qualify input rows `START..END-1` only; output holds just those rows. Above 100 rows, tile in 100-row windows, then `workflow union` the children (see Step 5b)                                 |
| `--wait`                          | Scripted | Blocks until the workflow completes. Use for scripted/CI runs or when only the final result is wanted; **drop it in interactive sessions** and monitor live via `workflow-monitor` (see Step 6) |

## Red Flags — STOP

- Qualification prompts are not yes/no questions → rewrite them before running
- `--context-cols` includes columns not verified to exist in the dataset → check
  with `datasets fields` first
- User wants to qualify 10,000 rows with `--enable-web-search` → flag the time
  and cost implication, confirm
- Large dataset queued as one run → likely to time out; slice it (Step 5b)
- Recombined a sliced run without checking the output `row_count` against the
  sum of the tiles' → the dedupe key may have silently dropped rows
- About to skip Steps 1–3 and run directly → go back and confirm criteria and
  columns first
