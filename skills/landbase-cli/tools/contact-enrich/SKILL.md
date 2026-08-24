---
name: contact-enrich
description:
  Async batch email and phone enrichment for individual leads via workflow
  contact-enrich — not the same as workflow enrich which adds company/person
  attributes.
when_to_use:
  when the user needs email addresses or phone numbers for a list of people,
  enriching a dataset of contacts, checking the status of a contact enrichment
  run, or resuming a timed-out enrichment request
version: 1.1.0
user-invocable: true
allowed-tools:
  - Bash
  - AskUserQuestion
model: sonnet
---

# Contact Enrich

Async batch email and phone enrichment: takes people, finds their contact
details.

This is different from `workflow enrich` — that command adds company/person
attributes (industry, size, description) from the Landbase graph.

## Enrich a dataset (`workflow contact-enrich`)

The current path is dataset-in / dataset-out; `contact-enrich submit|get` is
**deprecated** (below).

```bash
# From a file: upload → onboard → contact-enrich. Each step emits a NEW
# dataset id — enrich the onboarded child, not the uploaded id.
landbase-cli upload ./leads.csv                    # → { "id": "ds-UPLOADED" }
landbase-cli workflow onboard ds-UPLOADED --wait
landbase-cli datasets lineage ds-UPLOADED --direction=children --workflow=onboard
landbase-cli workflow contact-enrich ds-ONBOARDED --wait   # email + phone (default)
landbase-cli workflow contact-enrich ds-ONBOARDED --enrich-phone --wait   # phone ONLY
```

A positive `--enrich-email`/`--enrich-phone` switches to opt-in: the named one
runs and the other does not. Both run when neither is passed.
`--overwrite-existing` replaces existing
`contact_email_address`/`contact_phone_number` values with only this run's
results; the default preserves an existing value when this run finds nothing, so
re-running never wipes data.

Two children are registered: the enriched dataset (with a per-row
`contact_enrichment_status` of `enriched` / `not_enriched` / `failed` /
`skipped`) and a 1-row `contact_enrich_report`.

**This output does not download directly (`PUBLISH_REQUIRED`).** Run
`workflow publish <ds-id> --wait`, then download that run's `output_dataset_id`.

### Slice a large input (`--row-slice`)

A run that does not finish enriching in time **FAILS** with no partial output.
Above 500 rows, tile the input into **500-row windows**. If a slice still FAILS
on the time limit, narrow the window and re-run just that slice.

`landbase-cli datasets show ds-XXXX` reports `row_count`. At 500 rows or fewer,
run one pass and skip this step.

```bash
# 1500 rows → three tiles, run one at a time.
for s in 0:500 500:1000 1000:1500; do
  landbase-cli workflow contact-enrich ds-XXXX --row-slice=$s --wait
done

# Collect the child dataset ids (one per slice, named "... rows 0-499" etc.)
landbase-cli datasets lineage ds-XXXX --direction=children --workflow=contact_enrich

# Recombine. No --dedupe-keys: the tiles are disjoint, so a union keeps every row.
landbase-cli workflow union ds-SLICE0 ds-SLICE1 ds-SLICE2 --wait
```

Rules:

- **Run slices serially, not in parallel.** Slicing buys runs that finish, not
  throughput.
- **Credits are charged per slice, so tiling costs the same as one big run.**
- A last slice running past the final row is fine — it returns the remaining
  rows and the child records the window it actually holds.
- **Recombine without `--dedupe-keys`.** Never key on `contact_email_address`:
  rows that did not enrich carry a NULL email and every NULL collapses into one,
  silently dropping them. Verify the union's `row_count` equals the sum of the
  tiles'.

## Required signals per person

Each person needs `linkedin_url` **OR** (`first_name` + `last_name` +
`company`/`company_domain`) — as columns in the dataset, or as fields in a
submitted lead. Providing both name signals AND LinkedIn URL improves match rate
materially.

## Deprecated: `contact-enrich submit|get`

Predates the dataset flow. Prefer `workflow contact-enrich` above; use this only
to poll a `request_id` from an older submission.

```bash
landbase-cli contact-enrich submit ./leads.jsonl --wait

# Also enrich phone numbers (costs more per lead)
landbase-cli contact-enrich submit ./leads.jsonl --wait --enrich-phone
```

Or pipe from stdin:

```bash
echo '{"first_name":"Jane","last_name":"Smith","linkedin_url":"https://www.linkedin.com/in/janesmith","company_domain":"example.com"}' \
  | landbase-cli contact-enrich submit - --wait --enrich-phone
```

### Field mapping from match output

If feeding output from `match person` into `contact-enrich`, rename fields:

| match output                               | contact-enrich input |
| ------------------------------------------ | -------------------- |
| `member_websites_linkedin`                 | `linkedin_url`       |
| `member_name_first`                        | `first_name`         |
| `member_name_last`                         | `last_name`          |
| (not in candidate — carry from your input) | `company_domain`     |

The candidate exposes `company_id` but not `company_domain` — always carry
`company_domain` from your original match input.

### Input formats

Auto-detected by file extension:

| Source                      | Format                                |
| --------------------------- | ------------------------------------- |
| `.json`                     | Strict JSON — array or single object  |
| `.jsonl` / `.ndjson`        | Line-by-line JSONL                    |
| `-` (stdin) or no extension | Tries JSON first, falls back to JSONL |

### Check status

```bash
landbase-cli contact-enrich get <request-id>
```

Poll until status is: `COMPLETED` | `FAILED` | `CANCELLED` | `PARTIAL_SUCCESS`

### Resuming after timeout

If `--wait` times out, the `error.meta.request_id` field lets you resume:

```bash
landbase-cli contact-enrich get <request-id-from-error-meta>
```

### Rate limits

- Keep `submit` calls under ~10/minute per account
- Pack batches close to the 100-lead max — one full batch is faster and cheaper
  than many small ones
- Fanning out beyond 10/min risks provider-side limits (402 /
  out-of-credits, 429)
