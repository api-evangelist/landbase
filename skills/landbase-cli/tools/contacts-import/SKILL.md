---
name: contacts-import
description:
  Import contacts into the Execution platform via landbase-cli contacts-import —
  covers building and validating an AI-driven header mapping, tracking an import
  to completion, and repairing failures using the server's authoritative header
  list.
when_to_use:
  when importing contacts into the Execution platform via contacts-import,
  building or repairing a header mapping, or reporting dropped columns / mapping
  failures after an import
version: 1.0.0
---

# Contacts Import (Execution platform) with AI header mapping

Import a dataset's contacts into the current account on the Execution platform
(where campaigns run). NEVER run a bare `contacts-import start` — default header
resolution drops every column it can't match. The drop is reported in the final
status, not silent, but the user's data is still not imported. Build a mapping
first. Violating the letter of these rules is violating their spirit.

Prereqs: `landbase-cli auth login`, then `landbase-cli account set` (or
`--account=<id>`). You need a dataset id from a prior search/agent run or
`upload` — those commands print `dataset_id`; pass that same value as
`datasetId` (camelCase) in the start body.

Mechanics (command list, body/response shapes, phases, polling) live in
`landbase-cli contacts-import --help`. This skill is the authority on when to
stop, what to repair, and what to report to the user.

## Red Flags — STOP

- About to run `contacts-import start` without a `mapping` in the body
- About to guess a field from its header name alone ("Contact", "Info", "ID")
  instead of checking sample values via `datasets peek`
- About to read the local CSV for headers when a `datasetId` exists —
  `datasets fields` is the authoritative source; upload/publish can change the
  columns
- About to `start` while `resolve` still reports `invalidMappingEntries`,
  `missingRequired`, or `violatedRowRules`
- About to proceed with non-empty `unmappedHeaders` without the user's explicit
  OK to drop those columns

## The mapping flow

1. Headers come from the DATASET, not your local file:
   `landbase-cli datasets fields <datasetId>` is the authoritative column list.
   For ambiguous header names, check sample values:
   `landbase-cli datasets peek <datasetId> --sql "SELECT * FROM input_dataset LIMIT 3"`.
2. `landbase-cli contacts-import schema` — match each column to a catalog field
   by its `description` and by comparing sample values to `examples`/`format`.
   `rowRules` in the response is the authoritative list of `required` fields and
   `atLeastOneOf` groups (server-owned; never hardcode the rules).
3. Preflight: `landbase-cli contacts-import resolve --json -` on
   `{ "headers": [...], "mapping": { "company": {...}, "contact": {...} } }`.
   Stop conditions — fix, re-`resolve`, only then start:
   - `invalidMappingEntries`: `unknown_field` → use its `didYouMean`;
     `header_not_in_file` → use its `suggestion`. `resolve` tolerates unknown
     field names; `start` rejects them outright.
   - `missingRequired` / `violatedRowRules` non-empty → the import WILL fail.
   - `unmappedHeaders` non-empty → those columns will NOT be imported — remap
     them or confirm the loss with the user.
4. Start with the same mapping and watch to terminal:
   `echo '{"datasetId":"<id>","tagName":"<tag>","mapping":{...}}' | landbase-cli contacts-import start --json - --watch`
   (or poll `status <importId>` / block with `wait <importId>`).

## Reading the terminal status — what to report

- `unmapped.total > 0` → name the non-imported columns to the user
  (`unmapped.headers` caps at the first 50; `total` is the real count — say so
  when the list is truncated).
- `failed` with non-null `mappingErrors` → resolution failed BEFORE any rows
  ran. The repair source is `fileHeaders` in the SAME status — the server-side
  header list, authoritative over your local parse (first 50; `totalFileHeaders`
  is the real count). Rebuild the mapping against it, re-`resolve`, re-`start`.
- `partial` → some rows landed (`counts` shows what), `error` says why the rest
  didn't.
- On `completed`, report `counts` (imported/merged/skipped/invalid).

Dataset imports: the server sees the dataset's columns plus `LB_*` system
columns — those are excluded from mapping checks automatically; never map to
them.

## Failure modes

- `CONFLICT` on `start` — that importId is already enqueued; don't retry, poll
  `status <importId>`.
- `http_404` on `schema`/`resolve` — the server predates these endpoints (an
  older deployment's route-level 404 carries no error envelope, so it surfaces
  as the fallback `http_404` code, not `NOT_FOUND`).
- `TIMEOUT` on `wait`/`--watch` after 30min — the import keeps running; resume
  with `status <importId>` (the id rides in the error's `meta.importId`).
- `VALIDATION_ERROR` on `start` — usually a datasetId unknown or not accessible
  to this account.

## Integration

**Called by:** `landbase-email-campaigns`, `landbase-linkedin-campaigns`,
`dataset-pipeline` — each hands off here before importing contacts. Return to
the calling skill only after the import reaches a terminal phase and the outcome
(counts + any dropped columns) has been reported to the user.
