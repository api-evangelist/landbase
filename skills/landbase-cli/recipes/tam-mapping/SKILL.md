---
name: tam-mapping
description:
  Run a full TAM map using the tam_map_creator agent — validates reference
  companies, expands the ICP, searches and scores the universe, qualifies a
  sample, and publishes a TAM result with HTML report.
when_to_use:
  when the user wants to build a total addressable market map, score a universe
  of companies against an ICP, run a full TAM analysis, or says "run a TAM map",
  "build my TAM", "score my universe", "map my market"
version: 1.0.0
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
model: sonnet
---

# TAM Mapping

## Step 1 — Verify the agent is available

`tam_map_creator` is GA — always selectable, no env flag needed. Confirm the
installed CLI is recent enough to ship it:

```bash
landbase-cli search --help | grep tam_map_creator
```

If nothing prints, the CLI is out of date — run `landbase-cli update`.

## Step 2 — Collect inputs

Check for `icp-definition.md` in the current directory. If it exists, read it —
use the ICP and reference companies from it directly.

If it doesn't exist, ask the user for:

1. Their seller domain (e.g. `medibrief.com`)
2. 2–5 reference company domains — known true-fit customers
3. ICP: industries, company size, geography, target titles, signals,
   disqualifiers

Do not proceed with fewer than 2 reference companies. Ask for more.

## Step 3 — Run the agent

```bash
landbase-cli search \
  --agent=tam_map_creator \
  --session=<slug>-tam \
  "Run a full TAM map end-to-end for [seller-domain]. We sell [description]. \
   Reference companies (true-fit customers): [domain1], [domain2], [domain3]. \
   ICP: [industries]; [size]; [geography]; [signals]; target titles [titles]; disqualify [disqualifiers]. \
   Validate and expand industries and titles, show the ICP summary, then proceed \
   through every pipeline stage without pausing for confirmation, and publish the result."
```

The agent runs 8 stages and narrates each one. Full runs take 15–20+ minutes;
the agent already defaults to a 30-minute timeout, so don't pass a shorter
`--timeout`. A completed run publishes a `TAM_MAP_RESULT` artifact and a project
URL.

Do not use `--download` — TAM results are not dataset downloads.

## Step 4 — Surface results

When the run completes, show the user:

- The project URL (`https://gtm.landbase.com/project/<session_id>`)
- The tier breakdown (A/B/C/D)
- Any flags or gaps the agent reported

To re-fetch at any time:

```bash
landbase-cli runs latest --session=<slug>-tam
```

## Step 5 — Refine (if needed)

Use the same `--session` label to continue the conversation:

```bash
landbase-cli search \
  --agent=tam_map_creator \
  --session=<slug>-tam \
  "Narrow the ICP to exclude companies under 50 employees and re-score"
```

## Red Flags — STOP

- `tam_map_creator` not in `--help` → CLI is out of date; run
  `landbase-cli update`
- Fewer than 2 reference companies → ask for more before running
- About to use `--download` → not supported; use `runs latest` instead
