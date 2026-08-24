---
name: transcript-synthesis
description:
  Extract a structured ICP definition from a call transcript, meeting notes, or
  any freeform text. Classifies each attribute as must/should/nice, identifies
  seed companies for lookalike expansion, and writes a reusable
  icp-definition.md.
when_to_use:
  when the user has a call transcript, meeting notes, recorded call summary, or
  any freeform description of their ideal customer — phrases like "extract ICP
  from this call", "here's my call notes", "synthesize this transcript", "pull
  the ICP from this", "I just got off a call with a prospect"
version: 1.0.0
user-invocable: true
allowed-tools:
  - Read
  - Write
  - AskUserQuestion
model: sonnet
---

# Transcript Synthesis

## Step 1 — Get the transcript

Accept whichever form the user provides:

- **Pasted text** — already in context, proceed
- **File path** — `Read` the file (supports .txt, .md, .json, .vtt, any text
  format)
- **Freeform notes** — ask the user to share what they remember from the call

If nothing has been provided yet, ask:

> "Share the transcript or notes — paste them here or give me a file path."

## Step 2 — Extract ICP attributes

Read the full transcript and extract every ICP signal mentioned. Organize into
these dimensions:

**Firmographics**

- Industry / vertical (specific is better than broad: "mortgage servicers" not
  "finance")
- Company size (employee count, revenue, or both if mentioned)
- Geography (country, region, state — be specific)
- Funding stage (bootstrapped, Series A, enterprise, etc.)
- Other company attributes (public/private, age, growth rate, etc.)

**Technographics**

- Specific tools, platforms, or tech stack mentioned
- Integrations or compatibility requirements

**Buying signals & triggers**

- Events that indicate readiness (hiring, funding, expansion, regulatory change,
  etc.)
- Timing triggers ("companies that recently...")

**Disqualifiers**

- Explicit exclusions mentioned ("not X", "we don't want Y")
- Deal-breaker criteria

**Target contacts**

- Job titles, seniority levels, departments
- Decision-maker vs. champion distinctions if mentioned

**Reference companies**

- Any example companies or domains mentioned as "companies like these"
- Existing customers named as exemplars
- Competitors' customers mentioned

**Quality vs. volume preference**

- Did the prospect indicate they want a tight high-precision list or broad
  coverage?
- Any stated list size targets?

## Step 3 — Present the extraction table

Show all extracted attributes in a single table:

| Dimension      | Value                          | Captured priority |
| -------------- | ------------------------------ | :---------------: |
| Industry       | mortgage servicers             |         —         |
| Geography      | US only                        |         —         |
| Size           | 200–2,000 employees            |         —         |
| Title          | VP of Operations, COO          |         —         |
| Trigger        | recent CFPB compliance action  |         —         |
| Disqualifier   | credit unions                  |         —         |
| Seed companies | loancare.com, bsmservicing.com |         —         |

Then ask:

> "Does this capture everything? Add anything missing, correct anything wrong,
> then I'll ask you to prioritize each attribute."

Wait for confirmation before proceeding.

## Step 4 — Classify must/should/nice

For each attribute, determine priority:

- **must** — non-negotiable; a lead without this doesn't qualify
- **should** — improves fit; worth filtering for but not a hard gate
- **nice** — enrichment only; good to have, not required

**When the transcript is explicit** ("we absolutely need X", "X is critical", "X
would be nice to have") — capture that classification verbatim.

**When ambiguous** — mark as `unclassified` and surface those to the user.

Present the unclassified attributes and ask the user to classify each:

> "These attributes weren't explicitly prioritized in the transcript. Classify
> each as must / should / nice:"

Do not silently default. Never assume must for everything (over-conservative) or
should for everything (under-conservative).

Once all attributes are classified, show the final table for confirmation:

| Dimension      | Value                          | Priority |
| -------------- | ------------------------------ | :------: |
| Industry       | mortgage servicers             |   must   |
| Geography      | US only                        |   must   |
| Size           | 200–2,000 employees            |  should  |
| Title          | VP of Operations, COO          |   must   |
| Trigger        | recent CFPB compliance action  |  should  |
| Disqualifier   | credit unions                  |   must   |
| Seed companies | loancare.com, bsmservicing.com |    —     |

Ask: "Anything to promote, demote, or change? Reply with edits or 'looks good'
to save."

## Step 5 — Surface next steps

Return the classified attribute table to the calling context. If invoked
standalone (not from `icp-capture`):

- **Capture the full ICP** → run `icp-capture` to validate scope, check for
  similar builds, and write `icp-definition.md`
- **Build a prospect list** → use `prospect-builder` with the classified
  attributes
- **Find lookalike companies** → if seed domains were captured, use
  `lookalike-expansion`

## Red Flags — STOP

- About to classify all attributes as must → that's over-conservative; ask the
  user to prioritize
- About to skip Step 4 because the transcript seemed clear → always confirm the
  table with the user
- Transcript mentions a company by name but no domain → try to infer the domain
  or note it as unresolved
- Quality vs. volume preference not mentioned → ask explicitly; it affects how
  the search query is constructed
