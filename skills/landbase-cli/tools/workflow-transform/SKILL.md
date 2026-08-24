---
name: workflow-transform
description:
  Run custom SQL against a Landbase dataset (uploaded CSV, search result, or
  pipeline output) to filter, reshape, or derive new columns. The SQL operates
  on the columns in the input dataset.
when_to_use:
  when the user wants to filter a dataset with custom criteria, run SQL
  transformations, select specific columns, join across dataset fields, or
  reshape results that a search query can't express precisely enough
version: 1.1.0
user-invocable: true
allowed-tools:
  - Read
  - Bash
  - AskUserQuestion
model: sonnet
---

# Workflow Transform

Runs custom SQL against a Landbase dataset — an uploaded CSV, search result, or
pipeline output. The SQL operates on the columns in the input dataset (use
`datasets fields` to see what's available). The result is a new child dataset.

## Run

Inline SQL:

```bash
landbase-cli workflow transform ds-XXXX \
  --sql="SELECT company_name, industry, employees_count FROM input_dataset WHERE hq_country = 'US'" \
  --wait
```

SQL from a file:

```bash
landbase-cli workflow transform ds-XXXX --sql-file=./query.sql --wait
```

## Flags

| Flag                | Notes                                        |
| ------------------- | -------------------------------------------- |
| `--sql="<query>"`   | Inline SQL string                            |
| `--sql-file=<path>` | Path to a `.sql` file for complex queries    |
| `--wait`            | Always — blocks until the workflow completes |

Use `--sql-file` for anything beyond a simple SELECT — multiline SQL with CTEs,
JOINs, or subqueries is easier to maintain in a file.

## Discovering available columns

Before writing SQL, check what columns are available in the dataset:

```bash
landbase-cli datasets fields ds-XXXX
```

The table name in SQL is always `input_dataset`.

## Getting the result

Transform writes a new dataset; the finished run names it in
`output_dataset_id`:

```bash
DS=$(landbase-cli workflow transform ds-XXXX --sql-file=./q.sql --wait \
  | jq -r '.poll.run.output_dataset_id')
landbase-cli datasets download "$DS" results.zstd.parquet
```

Without `--wait`: `workflow status ds-XXXX --run=<run-id>` →
`.[0].output_dataset_id` once `SUCCEEDED`. Falling back to `datasets lineage`
needs `--workflow=dataset_transform` — there is no `transform` alias.

## Common use cases

- **Filter to a subset** — `WHERE hq_country = 'US' AND employees_count > 100`
- **Select specific columns** — reduce a wide dataset to the fields you need
- **Derive new columns** —
  `CASE WHEN employees_count > 500 THEN 'enterprise' ELSE 'mid-market' END AS segment`
- **Deduplicate** — `SELECT DISTINCT website, company_name FROM input_dataset`
- **Rank / take top N** — `ORDER BY employees_count DESC LIMIT 50`
- **Aggregate** —
  `SELECT industry, COUNT(*) FROM input_dataset GROUP BY industry`
- **Join / union another dataset you own** —
  `--additional-datasets="crm=ds-CRM"` then
  `SELECT i.* FROM input_dataset i JOIN crm c ON i.website = c.website`

## When to use this instead of --mode=research

`workflow transform` runs SQL over datasets you already own — the primary way to
refine a `search --mode=default` pool (or an uploaded dataset) without paying
the credit cost of a `--mode=research` run. Filter, rank, derive, dedup,
aggregate, or join across your own lists here (if a needed column is absent,
`workflow enrich` it first); reach for `--mode=research` only when the query
must run over the full Landbase database.

**Scope limit:** transform sees only `input_dataset` plus datasets passed via
`--additional-datasets`. It never reaches the full Landbase database. To find
the globally top-N companies (not just rank within your pool), use
`--mode=research`.

**Pool-completeness prerequisite:** transform can only return rows already in
`input_dataset`. If the original `--mode=default` search excluded rows you now
need, no SQL recovers them — widen the original search or use `--mode=research`.

## Red Flags — STOP

- About to reference a column name without checking `datasets fields` first →
  column names vary by dataset; always verify
- Writing SQL with table name other than `input_dataset` → that's the only valid
  table name
- Using `--sql` with a multiline query → use `--sql-file` instead for
  readability
