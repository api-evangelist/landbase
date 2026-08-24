---
name: dataset-pipeline
description:
  The full landbase-cli dataset pipeline — upload → onboard → match → enrich →
  qualify/research — and how to read each step's output dataset ID to feed the
  next step.
when_to_use:
  when running a multi-step dataset pipeline, chaining upload → onboard → match
  → enrich → qualify, or extracting the output dataset ID between workflow steps
version: 1.2.0
---

# Dataset Pipeline

The full pipeline for processing a CSV through Landbase. Each step writes a NEW
dataset and leaves its input untouched — so always feed the next step the
finished run's `output_dataset_id`, never the id you passed in. Reading the
input after a `SUCCEEDED` run shows it without the new columns, which looks like
the step did nothing.

The examples below use `--wait` to keep the chained commands compact. **In an
interactive session, the long steps (`match`, `enrich`, `qualify`, `research`)
should instead be triggered _without_ `--wait`** — capture the `workflow_run_id`
and follow the `workflow-monitor` skill to narrate live progress, since a
`--wait` subprocess can't stream its progress line into the chat. When chaining
this way, poll to `SUCCEEDED` (per `workflow-monitor`) and read
`output_dataset_id` off the finished run before starting the next step. `FAILED`
and `CANCELLED` are terminal too — stop the chain on either. Keep `--wait` for
scripted/CI runs or when only the final result matters.

To abort a step already underway (wrong dataset, wrong criteria burning
credits), cancel it by run id:

```bash
landbase-cli workflow cancel <workflow-run-id>
```

Cancel is best-effort: a step reporting row progress stops at its next record or
batch, one that reports none runs to completion, rows already written stay, and
the account is billed for the work performed. A `--wait` that times out does
**not** cancel — the run keeps going.

Don't assume a cancelled step produced nothing usable — cancellation is
graceful, so a complete output dataset may still exist, and a cancelled run
still reports its `output_dataset_id`. Inspect that dataset before deciding
whether to re-run the step or resume the chain from it.

## Full Pipeline: Upload → Onboard → Match → Enrich → Qualify

```bash
# 1. Upload CSV
landbase-cli upload ./leads.csv --name="Q1 leads"
# Response: { "id": "ds-UPLOADED", ... }

# 2. Onboard (normalize into Landbase schema). --wait prints
# {trigger, poll}; the next step's input is poll.run.output_dataset_id.
landbase-cli workflow onboard ds-UPLOADED --wait | jq -r '.poll.run.output_dataset_id'
# → ds-ONBOARDED

# 3. Match
landbase-cli workflow match ds-ONBOARDED --wait | jq -r '.poll.run.output_dataset_id'
# → ds-MATCHED

# 4. Enrich (see workflow-enrich for field selection)
landbase-cli workflow enrich ds-MATCHED \
  --company-fields=industry,size_range,description,keywords,technologies_used \
  --wait | jq -r '.poll.run.output_dataset_id'
# → ds-ENRICHED

# 5a. Qualify (yes/no AI classification)
landbase-cli workflow qualify ds-ENRICHED \
  --qualification-prompts="Is this an enterprise SaaS company?" \
  --context-cols=company_name,website,industry,description \
  --wait

# 5b. Research (structured LLM extraction with citations)
landbase-cli workflow research ds-ENRICHED --tasks-file=./tasks.json --wait
```

## Extracting Dataset IDs Between Steps

Every verb reports its **primary** output in the same field:

| Path                       | Read the id from                                                       |
| -------------------------- | ---------------------------------------------------------------------- |
| `upload`                   | `.id` on the upload response                                           |
| `workflow <verb> --wait`   | `.poll.run.output_dataset_id`                                          |
| triggered without `--wait` | `workflow status <input-ds> --run=<run-id>` → `.[0].output_dataset_id` |

It fills in on `SUCCEEDED` and on `CANCELLED` (a graceful cancel still registers
what it wrote). Null in flight, on `FAILED`, on steps that register no output,
and on runs predating output attribution — **null is not proof the step produced
nothing**, so fall back to lineage before concluding that:

```bash
landbase-cli datasets lineage <input-id> --direction=children --workflow=<server-name>
```

Two traps keep that a fallback: `--workflow` wants the _server-side_ name
(`enrich_only` for `workflow enrich`, `dataset_transform` for
`workflow transform`, `crm_suppress` for `workflow crm-suppress`), and children
come back newest-first, so `[0]` is whichever is newest — not necessarily your
run — once a step has run twice on the same parent.

Lineage is also the only way to see a run's **other** outputs: a step can
register siblings beside its primary (`onboard` writes a `column_mapping` child,
contact-enrich a summary report). Chain the primary forward; the siblings are
for auditing. Omit `--workflow` to list them all.

**Downloading:** `upload`, `onboard`, `match`, `search`, `enrich`, and the
transform family download directly. Everything else — `qualify`, `research`,
advanced-search, `contact-enrich`, `crm-suppress`, `similar-company-expansion` —
is rejected with `PUBLISH_REQUIRED`. Run `workflow publish <ds-id> --wait` and
download that run's `output_dataset_id`; `publish` defaults to `jsonl.gz`, pass
`--format=csv` for CSV.

## Importing a dataset into the Execution platform (contacts-import)

Optional last step — only when the user wants the contacts inside the Execution
platform to run campaigns on them; downloading the published dataset is a
complete outcome on its own. When importing, hand off to the **contacts-import**
skill and follow it end to end — its guardrails (mapping discipline, stop
conditions, what to report) live there, and do not run `contacts-import start`
until that skill's flow has produced a resolved `mapping`.
