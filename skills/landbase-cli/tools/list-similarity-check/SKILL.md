---
name: list-similarity-check
description:
  Check whether a similar prospect list has been built before by comparing an
  ICP against a history of past builds. Use before starting a new prospect build
  to surface reusable prior work.
when_to_use:
  when the user is about to build a prospect list and wants to check for prior
  similar builds, or says "have I built something like this before", "check for
  similar lists", "did we already do this", "reuse a prior query", or when
  icp-capture or prospect-builder is about to start a new build
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

# List Similarity Check

## Step 1 — Get the ICP to compare

Accept whichever form is available:

- **`icp-definition.md`** — if one exists in the current directory, read it
- **Freeform description** — e.g. "HR leaders at mid-market SaaS companies in
  the US"
- **Current conversation context** — if `icp-capture` or `prospect-builder` just
  ran, the ICP is already in context

Extract these dimensions for matching:

- Vertical / industry
- Geography
- Company size
- Persona / target title
- Targeting method (open market, account list, lookalike, keyword, tech stack)
- Special signals (hiring, funding, headcount change, etc.)

## Step 2 — Find the history source

Try each source in order, use the first that's available:

### Option A: Google Sheet URL

If the user provides a Google Sheet URL, or one is saved in `.landbase/config`:

- If a Google Sheets MCP tool is available, read the sheet directly
- If not, ask the user to export it as CSV and provide the file path

Expected columns (flexible — the skill adapts to whatever's present):

| Column         | Description                                 |
| -------------- | ------------------------------------------- |
| `name`         | Run name or identifier                      |
| `date`         | Date the list was built                     |
| `description`  | Natural language ICP description            |
| `vertical`     | Industry or vertical                        |
| `geography`    | Geographic scope                            |
| `company_size` | Employee range or size tier                 |
| `persona`      | Target title or persona                     |
| `signals`      | Special signals used                        |
| `output_path`  | File path or Google Sheet URL of the output |

### Option B: Local CSV or Excel file

If the user provides a file path, or a `prospect-history.csv` /
`prospect-history.xlsx` exists in:

- Current directory
- `~/.landbase/prospect-history.csv`

Read it and match against whatever columns are present. Adapt to the schema —
don't require exact column names.

### Option C: `prospects/` directory

Scan for past `prospect-builder` runs by finding `brief.md` files:

```bash
find ./prospects -name "brief.md" | sort -r
```

Read each `brief.md` for the original ask and ICP criteria. This is the
zero-configuration path — works automatically if the user has used
`prospect-builder` before.

### Option D: No history found

If none of the above yields results:

> "No prospect history found. Once you've run a few builds with
> `prospect-builder`, this skill will automatically find similar past work in
> your `prospects/` directory. You can also maintain a `prospect-history.csv`
> for builds done outside this tool."

Offer to create a `prospect-history.csv` template they can start filling in.

## Step 3 — Score similarity

For each history entry, score against the current ICP:

**HIGH** — same or closely overlapping vertical + persona + geography

> Likely reusable with minor edits. Surface immediately.

**MEDIUM** — shares 2–3 key dimensions

> Useful as a starting template. Worth reviewing.

**LOW** — shares 1–2 dimensions

> Reference only. Probably not worth reusing.

Rank by similarity. Surface top 5–10 matches.

## Step 4 — Present results

Show as a table:

| #   | Similarity | Name               | Date       | Description                         | Vertical | Geography | Persona | Output                        |
| --- | ---------- | ------------------ | ---------- | ----------------------------------- | -------- | --------- | ------- | ----------------------------- |
| 1   | HIGH       | hr-leaders-saas-us | 2026-04-12 | HR VPs at US SaaS, 200–2K employees | SaaS     | US        | VP HR   | prospects/2026-04-12_hr-saas/ |

If no matches score MEDIUM or higher:

> "No strong matches found. This looks like a new build."

## Step 5 — Act on results

**If HIGH match found:** Ask the user:

> "A similar list was built on {date}. Want to start from that run, or build
> fresh?"

- **Start from prior run** — point them to the output path; suggest running
  `prospect-builder` with the prior query as a starting point
- **Build fresh** — proceed, but note what's different about this run vs. the
  prior one

**If MEDIUM match found:** Show the prior query or brief and ask:

> "This is similar but not identical. Want to use it as a reference?"

**If no match:** Proceed to the new build. Optionally log this run to the
history file (Step 6).

## Step 6 — Log the new run (optional)

After a new prospect build completes, offer to add it to the history:

```
Append to prospect-history.csv:
name, date, description, vertical, geography, company_size, persona, signals, output_path
```

If using the `prospects/` directory, this happens automatically via
`prospect-builder`'s `brief.md`.

## History file template

If no history exists and the user wants to start one, write
`prospect-history.csv`:

```csv
name,date,description,vertical,geography,company_size,persona,signals,output_path
```

Save to `./prospect-history.csv` or `~/.landbase/prospect-history.csv` per user
preference.

## History sources

| Source                 | When available                      | How to use                          |
| ---------------------- | ----------------------------------- | ----------------------------------- |
| Google Sheet URL       | User provides URL                   | Google Sheets MCP or export to CSV  |
| Local CSV/Excel        | File exists at known path           | Read directly                       |
| `prospects/` directory | Prior `prospect-builder` runs exist | Scan `brief.md` files automatically |
| None                   | First-time user                     | Offer to create template            |

## Red Flags — STOP

- About to start a new build without checking history → run this skill first
- History file has no `description` or `vertical` column → adapt to whatever
  columns exist, don't fail
- HIGH match found but user wants to build fresh anyway → note the duplication,
  proceed without blocking
