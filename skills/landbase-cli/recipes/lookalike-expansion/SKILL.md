---
name: lookalike-expansion
description:
  Build a lookalike audience from a set of seed companies using the Landbase
  lookalike engine. Use when the user wants to find companies similar to their
  customers, a competitor's customer base, or any set of example companies — at
  any scale from a quick 25-company preview up to a full 20K expansion.
when_to_use:
  when the user says "find companies like X", "build a lookalike list", "expand
  from these seed accounts", "find similar companies to our customers", "clone
  this audience", or provides a list of example companies and wants more like
  them
version: 1.0.0
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Glob
  - Bash
  - AskUserQuestion
model: sonnet
---

# Lookalike Expansion

Two-phase workflow: Scout (quick 25-company preview) → Expand (full scale, up to
20K).

Always scout first. Expanding without validation wastes time on a bad seed
profile.

## Hard rules

1. **Scout before you expand.** Run a quick preview first unless the user
   explicitly says to skip it.
2. **Confirm scale before running.** Full expansion can return up to 20K
   companies — confirm how many the user wants.
3. **Landbase only.** Do not fall back to external sources if results look thin.
   Flag coverage gaps instead.
4. **Never truncate the output dataset.** If the user wants a subset, filter
   after downloading.

## Phase 1 — Scout (quick preview)

Use when: the user has example company domains and wants to validate the
direction before committing to a full run.

```bash
landbase-cli search "find companies similar to [domain1.com] and [domain2.com]"
```

Returns top 25 pre-computed lookalikes. Fast, no dataset needed.

**After scouting:** show the user a few representative results (name, industry,
size, location) and ask:

- Do these look right?
- Any firmographic constraints to add (industry, geography, size)?
- Ready to expand at scale?

**If the scout looks wrong:** ask the user to revise the seed companies or add
firmographic guidance before proceeding. Do not expand from a bad scout.

## Phase 2 — Expand at scale

### Step 1: Get a dataset ID

Expansion requires a `ds-XXXX` dataset ID. Three paths:

**A. User has a CSV of seed companies** — upload it:

```bash
landbase-cli upload seed-companies.csv
# Returns a dataset ID, e.g. ds-abc123
```

**B. User ran a prior search** — they already have a dataset ID from that run.
Ask them for it or find it:

```bash
landbase-cli runs latest
```

**C. User wants to search first, then expand** — run a search, capture the
dataset ID from the output, then proceed.

### Step 2: Run the expansion

This is an interactive flow, so trigger **without** `--wait`, capture the
`workflow_run_id`, and follow the `workflow-monitor` skill to narrate live
progress — a `--wait` subprocess can't stream its progress line into the chat.
The examples keep `--wait` for compactness; drop it when monitoring live, and
keep it only for scripted/CI runs or when the user just wants the final result.

```bash
landbase-cli workflow similar-company-expansion ds-XXXX --wait
```

**With firmographic steering** (use when the seed companies span multiple
industries and you want to narrow):

```bash
landbase-cli workflow similar-company-expansion ds-XXXX \
  --firmographics-guidance="keep only B2B SaaS companies, US only" \
  --wait
```

**With a non-default website column** (only needed when the dataset came from
`workflow onboard`, where columns are prefixed with `CLI_`):

```bash
landbase-cli workflow similar-company-expansion ds-XXXX \
  --website-column=CLI_website \
  --wait
```

### Step 3: Deliver results

If you used `--wait`, the JSON result carries the new dataset ID. If you
monitored without `--wait`, you only have the run id and the input dataset id —
once the run reaches `SUCCEEDED`, get the output child dataset id with
`datasets lineage`:

```bash
landbase-cli datasets lineage ds-XXXX --direction=children --workflow=similar_company_expansion
# Returns [{ "id": "ds-YYYY", ... }] — child ID is at [0].id
```

Then download it:

```bash
landbase-cli datasets download ds-YYYY lookalikes.jsonl
```

If a Drive MCP is available, push to Google Sheets and return the live URL.
Otherwise deliver the file and note the path.

### Step 4: Suggest AI qualification

After delivering the expansion results, suggest running AI qualification to
filter the lookalikes against ICP criteria the lookalike engine can't apply on
its own — funding stage, tech stack, recent signals, etc.:

```bash
landbase-cli workflow qualify ds-YYYY \
  --qualification-prompts="<yes/no ICP question>" \
  --context-cols=company_name,website,industry,description \
  --wait
```

Use the `qualify-leads` skill for the full guided workflow. Widening with
lookalike expansion then qualifying typically yields 50%+ more relevant results
than filtering by keywords alone.

## When to use firmographic guidance

Provide `--firmographics-guidance` when:

- The seed companies are from multiple verticals and you want only one
- The user wants geographic constraints (e.g. US only, EU only)
- The seed companies include very large and very small companies and you want to
  narrow size range

Keep the guidance concise and specific: `"B2B SaaS, 50-500 employees, US only"`.

## Flags reference

| Flag                             | When to use                                                                                                                 |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `--wait`                         | For scripted/unattended runs (blocks, returns JSON). For live monitoring, trigger without it and follow `workflow-monitor`. |
| `--firmographics-guidance="..."` | Steering when seed profile is broad or mixed                                                                                |
| `--website-column=CLI_website`   | Only when dataset came from `workflow onboard`                                                                              |

## Red Flags — STOP

- About to run `workflow similar-company-expansion` without scouting first → go
  back to Phase 1
- Scout results look unrelated to what the user asked for → fix the seed before
  expanding
- User hasn't said how many results they want → ask before running (20K is the
  max)
- About to use a non-Landbase source because results look thin → flag the gap
  instead
