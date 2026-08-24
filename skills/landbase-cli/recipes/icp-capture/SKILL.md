---
name: icp-capture
description:
  Full ICP capture workflow — synthesize from a transcript or structured
  questions, classify each attribute as must/should/nice, check for similar
  prior builds, validate scope, propose a search query, and write
  icp-definition.md for use by prospect-builder and tam-mapping.
when_to_use:
  when starting a new GTM initiative, before running prospect-builder or
  tam-mapping, when the ICP is unclear or needs to be documented — phrases like
  "define my ICP", "help me figure out who to target", "build my ICP", "what's
  my ideal customer", "I have a call transcript and want to build a list", or
  when a user is about to prospect without a clear ICP
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

# ICP Capture

## Hard rules

1. **Never default must/should/nice.** Every attribute must be explicitly
   classified. Mark ambiguous attributes `unclassified` and prompt — never
   assume must for everything or should for everything.
2. **Always show the full ICP table in chat before saving.** After every
   capture, correction, or update, post the full attribute × value × priority
   table and ask "Anything to change?"
3. **Always check similarity before finalizing.** Run `list-similarity-check`
   before writing output — a prior build may save significant work.
4. **Industries over NAICS.** Use the LinkedIn-derived `industry` taxonomy.
   Never use NAICS as a primary filter. Discover canonical taxonomy via the NL
   agent (Step 5) rather than inferring from seed examples.

---

## Step 1 — Transcript synthesis

**If the user provides a transcript, call notes, or file:**

- Invoke `transcript-synthesis`
- It returns a classified attribute table and reference companies
- Proceed to Step 2 with that output

**If starting from scratch:** Ask one dimension at a time:

1. **Vertical / industry** — specific is better than broad ("mortgage servicers"
   not "financial services")
2. **Company size** — employee count or revenue range
3. **Geography** — countries, regions, or states
4. **Funding / stage** — if relevant
5. **Tech stack** — specific tools or platforms, if they matter
6. **Target persona** — job titles, departments, seniority
7. **Buying signals & triggers** — events that indicate readiness (hiring,
   funding, regulatory change, etc.)
8. **Disqualifiers** — what immediately rules a company out
9. **Reference companies** — 2–5 example domains that fit perfectly (e.g.
   stripe.com)
10. **Quality vs. volume preference:**

Use AskUserQuestion:

> "For this list — smaller high-confidence set, or broader coverage?"

Options: "Smaller, high-precision" / "Broader coverage" / "Balanced"

---

## Step 2 — Classification backstop

**Hard gate.** Every attribute must have a priority before continuing.
`transcript-synthesis` handles classification — this step resolves anything it
left `unclassified`.

Show the full attribute table and ask:

> "Anything to promote, demote, or change? Reply with edits or 'looks good' to
> continue."

If any attributes are `unclassified`, prompt explicitly before proceeding:

> "These weren't prioritized in the source. Classify each as must / should /
> nice:"

**Do not silently default.** Wait for explicit answers.

---

## Step 3 — Router

Determine which path applies:

| Situation                              | Action                                                            |
| -------------------------------------- | ----------------------------------------------------------------- |
| No existing list — build from scratch  | Continue to Step 4                                                |
| User has a list and wants more like it | Hand off to `lookalike-expansion` with reference domains as seeds |
| User has a list and wants to score it  | Hand off to `tam-mapping`, passing `icp-definition.md` as input   |

If unclear:

> "Do you want to build a new list, expand an existing one, or score a list you
> already have?"

If scoring-existing: write `icp-definition.md` (Step 10) and hand off to
`tam-mapping`. Stop this pipeline.

---

## Step 4 — List similarity check

Invoke `list-similarity-check` with the ICP's key dimensions (vertical,
geography, size, persona).

**If a HIGH match is found:**

> "A similar list was built on {date}: {description}. Start from that run, or
> build fresh?"

- Start from prior → point to the output path, skip to Step 10
- Build fresh → note what's different, continue

**If MEDIUM match:** surface it as a reference, offer to use it as a template.

**If no match:** "This looks like a new build."

---

## Step 5 — Canonical taxonomy discovery

Before routing signals or drafting a query, ask the NL agent for the canonical
Landbase industry taxonomy for the customer's vertical:

```bash
landbase-cli search "What Landbase company-industry taxonomy values cover [vertical X]? \
  Return the canonical industry tags I would use to filter for this universe, \
  any semantically-adjacent tags to consider, and any broad-bucket tags that \
  will pull noise so I know to add exclusions. List only — don't build an audience."
```

Save the agent's response and use the primary tag set verbatim when drafting the
query. If the agent flags a broad-bucket tag (e.g. `Hospitals and Health Care`
covers multiple sub-verticals), note it for the gap analysis in Step 8.

---

## Step 6 — Build path routing

For each must-have signal, decide which execution path applies. Route by **data
scope** — which data the signal must touch:

| Path                      | When to use                                                                                                      | Command                                                            |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| **A — Standard search**   | Industry, size, geography, persona, tech stack, simple keywords; multi-condition logic over standard fields      | `landbase-cli search "..."`                                        |
| **B — Self-serve refine** | Post-build: filter/rank/derive/dedup on a catalog attribute not in the built list, over rows already in the pool | `workflow enrich` + `workflow transform` on the built `dataset_id` |
| **C — Advanced search**   | Phrase-match that defines the universe, job-posting signals, headcount-growth, global top-N — **costs credits**  | `landbase-cli search --mode=research "..."`                        |

Default to **A**; a catalog attribute that just isn't a search filter is **B**
(`workflow enrich` then `workflow transform`, no new search); reserve **C** for
signals needing the full Landbase database — it quotes an estimated credit cost
on turn 1 and charges on confirm in turn 2.

Produce a per-signal routing table:

| Signal                          | Priority | Path | Notes                                                                                                                      |
| ------------------------------- | :------: | :--: | -------------------------------------------------------------------------------------------------------------------------- |
| Industry: mortgage servicers    |   must   |  A   | standard filter                                                                                                            |
| Geography: US                   |   must   |  A   | standard filter                                                                                                            |
| Size: 200–2,000 employees       |  should  |  A   | standard filter                                                                                                            |
| Trigger: CFPB compliance action |  should  |  B   | enrich `description`, transform `WHERE description ILIKE '%CFPB%'` (or `qualify`) — it filters the mortgage-servicers pool |

If a signal like "CFPB compliance action" were instead the **primary** criterion
defining the universe (find every company that mentions it, no prior pool), it
would be **Path C** — Path B only filters rows already in a pool you built.

---

## Step 7 — Scope-size validation

Run a count probe from must-have attributes to size the universe before
committing to a full build.

```bash
landbase-cli search "How many [industry] companies with [size] employees in [geography] are there? \
  Return the total count only — do not build a dataset or return rows."
```

Show the count to the user. Round up to the next round number (e.g. 12,500 →
~13K; 47,200 → ~50K).

**If very low (< 100):** flag — the ICP may be too narrow. Consider softening
some must-haves to should-haves.

**If very high (> 100K):** flag — the must-haves may be too broad. Consider
tightening.

Ask: "Does this scope look right, or do you want to adjust criteria?"

---

## Step 8 — Gap analysis

One row per must-have signal. Two buckets:

| Signal                          | Priority |      Status      | Notes                                    |
| ------------------------------- | :------: | :--------------: | ---------------------------------------- |
| Industry: mortgage servicers    |   must   |    ✅ Covered    | Standard landbase-cli search filter      |
| Geography: US                   |   must   |    ✅ Covered    | Standard landbase-cli search filter      |
| Size: 200–2,000 employees       |  should  |    ✅ Covered    | Standard landbase-cli search filter      |
| Trigger: CFPB compliance action |  should  | ❌ Outside scope | Regulatory signal not available natively |

**Must-have coverage check:** every must-have must be ✅ Covered. If any
must-have is ❌ Outside scope, flag it as a blocker:

> "The following must-have signals can't be filtered natively in Landbase.
> Options: (1) reclassify as should-have and add as a qualify-leads step
> post-build, (2) remove from ICP, or (3) accept a broader initial universe and
> qualify down."

Ask the user to resolve blockers before continuing.

---

## Step 9 — Write icp-definition.md

Save to `icp-definition.md` in the current directory (or project folder):

```yaml
# ICP Definition
# Generated: {YYYY-MM-DD}
# Source: {transcript-synthesis / structured questions}

firmographics:
  industries:
    values: [mortgage servicers]
    priority: must
  geography:
    values: [US]
    priority: must
  employee_range:
    value: "200-2000"
    priority: should
  custom_criteria:
    value: ""

technographics:
  tech_stack:
    values: []
    priority: ""

signals:
  triggers:
    value: "recent CFPB compliance action"
    priority: should

disqualifiers:
  industry_exclusion:
    value: "credit unions"
    priority: must

contacts:
  decision_makers:
    values: [VP of Operations, COO]
    priority: must
  champions:
    values: []

reference_companies:
  companies:
    - domain: loancare.com
    - domain: bsmservicing.com

delivery_preference:
  quality_vs_volume: high-precision

proposed_query:
  path_a: ""
  path_b: ""

scope_validation:
  estimated_count: "~13K"
  filters_used: [industry, geography, employee_range]

gap_analysis:
  - signal: "CFPB compliance action"
    priority: should
    status: outside_scope
    note: "Regulatory signal not available natively; qualify post-build"
```

After saving, confirm the path. Ask if the user wants to push to a project
folder (e.g. `prospects/YYYY-MM-DD_<slug>/icp-definition.md`).

---

## Step 10 — Query proposal

Hand off to `query-assist` with the ICP definition and build path routing from
Step 6. It reads `icp-definition.md` directly.

`query-assist` will:

- Confirm canonical taxonomy tags
- Draft the NL query from must-have signals with the standard attribute pack
- Run Path B self-serve refinement (`workflow enrich` + `workflow transform`),
  or handle the two-turn advanced-search confirmation for Path C signals
- Execute and download the resulting dataset
- Save the proposed query back to `icp-definition.md`

---

## Step 11 — Handoff

**Find lookalike companies** (if reference domains were captured): Run
`lookalike-expansion` using the domains in `reference_companies`.

**Score an existing list:** Run `tam-mapping` — pass `icp-definition.md` as the
ICP input.

---

## Red Flags — STOP

- About to classify all attributes as must → over-conservative; prompt the user
  to prioritize
- About to skip Step 5 (taxonomy discovery) and infer industry values from seed
  examples → always query the agent for canonical tags
- A must-have is ❌ Outside scope in the gap analysis → resolve before saving
- Scope count is very low or very high → flag before proceeding
- About to skip `list-similarity-check` → always run Step 4 first
- `icp-definition.md` already exists → ask whether to overwrite or version it
