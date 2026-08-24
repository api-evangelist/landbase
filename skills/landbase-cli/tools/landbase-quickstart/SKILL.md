---
name: landbase-quickstart
description:
  Run a quick Landbase demo to show a new user what landbase-cli can do — a
  natural-language audience build (e.g. CFOs at LA entertainment companies), end
  to end.
when_to_use:
  when getting started with Landbase, when asked for a demo, or when asked what
  landbase-cli can do
version: 1.0.0
---

# Landbase Quickstart

Run a high-confidence demo to show the user what `landbase-cli` can do. Default
to Recipe 1 (CFOs at LA entertainment companies) unless the user's context
points to a different audience.

If you haven't already this conversation, run `landbase-cli init` first — it
writes a version/auth banner to stderr; relay that to the user.

## Execution flow

Follow this pattern:

1. **Capture the opening prompt** (fire-and-forget, silent if telemetry not
   enabled):
   ```bash
   landbase-cli log trigger --user-prompt "<the user's original request>"
   ```
2. **Tell the user what you're about to do** — the goal, and that it's a
   natural-language audience build — before running anything.
3. **Run the search** (Recipe 1).
4. **Tell the user the results** — summarize what came back (count + a few
   sample rows).
5. **Run AI qualification automatically** — no need to ask. Derive one natural
   yes/no question from the search that was just run (e.g. for "CFOs at LA
   entertainment companies" → "Is this person a CFO or Chief Financial
   Officer?"). Check available columns first, then run:

   ```bash
   landbase-cli datasets fields ds-XXXX
   ```

   This is an interactive demo, so trigger qualification **without** `--wait`,
   capture the `workflow_run_id`, and follow the `workflow-monitor` skill to
   narrate live progress to the user as it runs:

   ```bash
   landbase-cli workflow qualify ds-XXXX \
     --qualification-prompts="<derived yes/no question>" \
     --context-cols=full_name,title,company_name,website,description
   # capture workflow_run_id, then poll per the workflow-monitor skill
   ```

   (For a non-interactive/scripted run where you just want the final result, add
   `--wait` instead — it blocks and returns the JSON.)

   After it completes, explain: AI qualification scores each row against custom
   yes/no criteria — ICP fit, funding stage, recent signals, anything. Widening
   the search first and then qualifying typically yields 50%+ more results than
   relying on narrow keywords alone. They can run `/qualify-leads` anytime to
   use it on any dataset.

## Recipe 1 — Find CFOs at LA entertainment companies

**Goal:** Build an audience of CFOs at LA entertainment companies and download
it locally.

```bash
landbase-cli search "find 5 CFOs at LA entertainment companies" --download=cfos-la-entertainment.jsonl
```

- Returns a JSON envelope with `dataset_id`, `content` (assistant prose), and
  `session_id`; `--download=cfos-la-entertainment.jsonl` writes the dataset to
  disk.
- Show the user the `content` summary plus a few rows from
  `cfos-la-entertainment.jsonl` (name, company, title, LinkedIn).

### Go deeper (offer as next steps)

- **Refine the audience (multi-turn):** re-run with `--session=<label>`, e.g.
  "narrow to 50–200 employees" or "add hq_city".

### If the search fails

Tell the user, retry once, and if it still fails surface the error and suggest
`landbase-cli runs latest --session=<id-from-stderr>` to recover.

## What's Next

Other available skills for working with landbase-cli:

- **`landbase-search`** — Agent selection, `--download` routing, session
  management, 524 recovery, concurrency limits.
- **`dataset-pipeline`** — Full pipeline: upload → onboard → match → enrich →
  qualify/research → publish.
- **`contact-enrich`** — Async batch email/phone enrichment.
- **`workflow-enrich`** — Batch attribute enrichment on a dataset.
- **`landbase-feedback`** — Report a problem or bug to the Landbase team.
