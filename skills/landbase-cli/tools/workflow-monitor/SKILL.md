---
name: workflow-monitor
description:
  Report live progress and a rolling ETA while a Landbase workflow run executes,
  by polling the REST endpoint directly (no CLI binary) — works the same in
  local and cloud Claude Code sessions. Also covers stopping a run.
when_to_use:
  when a Landbase workflow run is in flight (onboard, match, enrich, qualify,
  research, transform, publish) and the user wants live progress updates or an
  ETA, when monitoring a long --wait-style run from inside a Claude Code
  session, when polling a workflow_run_id for completion without blocking on the
  CLI, or when the user wants to stop / cancel / abort a run already underway
version: 1.2.0
user-invocable: true
allowed-tools:
  - Bash
model: sonnet
---

# Workflow Monitor

Report live progress and a rolling ETA for an in-flight Landbase workflow run.
Query the REST endpoint **directly** — do NOT invoke the CLI binary for
monitoring. Direct polling works identically in local and cloud sessions and
avoids ANSI escape codes, so report **plain text only** (no animated progress
bar).

## When to use this vs. `--wait`

`landbase-cli workflow <verb> --wait` already blocks and prints a live progress
line. Use **this skill instead** when you want to keep the session responsive:
trigger the workflow **without** `--wait`, capture the `workflow_run_id`, and
poll the REST endpoint yourself so you can narrate progress to the user between
other steps.

## The progress endpoint

The workflow-runs endpoint returns the run plus these nullable fields:

| Field               | Meaning                                                              |
| ------------------- | -------------------------------------------------------------------- |
| `status`            | `PENDING` / `RUNNING` / `SUCCEEDED` / `FAILED` / `CANCELLED`         |
| `rows_total`        | Total rows the run will process (nullable)                           |
| `rows_processed`    | Rows processed so far (nullable)                                     |
| `percentage`        | Server-computed percent complete (nullable)                          |
| `current_stage`     | Current stage label, e.g. `person_matching` (null on qualify/enrich) |
| `dataset_id`        | The run's INPUT — unchanged by the run                               |
| `output_dataset_id` | The dataset the run produced; null until terminal                    |

Report `output_dataset_id`, never `dataset_id`. Null on a terminal run is
**not** proof nothing was produced — fall back to `datasets lineage <ds-id>`.

Since this skill bypasses the CLI, poll the endpoint directly:

| Base URL + path                               | Auth                                                                              |
| --------------------------------------------- | --------------------------------------------------------------------------------- |
| `https://api.landbase.com/workflow-runs/{id}` | `Authorization: Bearer <lbs_ session token>` **and** `X-Account-Id: <account id>` |

Credentials live in `~/.landbase/platform.json` (`accessToken` is the `lbs_*`
session token; `accountId` is the `X-Account-Id` value). Both headers are
required — the call is **unscoped without `X-Account-Id`**.

If `LANDBASE_LEGACY_MODE` is set there is no session token to poll with; use
`landbase-cli workflow status <ds-id>` instead of a direct GET.

## Procedure

1. **Trigger without `--wait`** and capture the run id:

   ```bash
   landbase-cli workflow match ds-XXXX
   # stdout: { "workflow_run_id": "...", "workflow_name": "match", "dataset_id": "ds-XXXX" }
   ```

   Save `workflow_run_id` from the response.

2. **Poll every ~30s** with the REST endpoint (read-only GET — never pipe a
   response into a shell):

   ```bash
   # Un-versioned path, session token + X-Account-Id.
   TOKEN=$(jq -r .accessToken ~/.landbase/platform.json)
   ACCOUNT=$(jq -r .accountId ~/.landbase/platform.json)
   curl -s -H "Authorization: Bearer $TOKEN" -H "X-Account-Id: $ACCOUNT" \
     "https://api.landbase.com/workflow-runs/$RUN_ID" | jq .
   ```

3. **Track `(timestamp, rows_processed)` across the two most recent polls** to
   compute a rolling rate, then an ETA:

   ```
   rate        = (rows_processed_now - rows_processed_prev) / (seconds_between_polls)
   eta_seconds = (rows_total - rows_processed_now) / rate
   ```

   Guard: if `rate <= 0` (no rows advanced, or it went backwards) or it can't be
   computed, **omit the ETA** — just report rows/percent.

4. **Report each tick in plain text** to the user, mirroring what the CLI's
   `formatProgressLine` prints. Prefer the server `percentage`; if it's null but
   rows are present, compute `round(rows_processed / rows_total * 100)`. Show
   the stage in **brackets** only when `current_stage` is non-null. Format the
   ETA as `~Xm Ys` for durations ≥ 60s (always with seconds — e.g. `~4m 0s`,
   never a bare `~4m`) and `~Xs` for shorter:

   ```
   Processing... 450/1000 rows (45%) [person_matching] — ETA ~4m 20s
   ```

5. **Stop polling** when `status` is `SUCCEEDED`, `FAILED`, or `CANCELLED` — all
   three are terminal. On `SUCCEEDED`, report `output_dataset_id` as the result.
   On `FAILED`, report `error_message`. On `CANCELLED`, report that the run was
   stopped (its `error_message` reads `Cancelled by user`) — it can still have
   registered a complete dataset, and `output_dataset_id` names it, but validate
   before presenting it as a result.

## Per-workflow narration

- **match** — `current_stage` is non-null and moves through
  `field_mapping → person_matching → company_matching`. Show the stage in
  **brackets**. The server `percentage`/ETA is **per-stage** and **resets to 0
  at each stage boundary** — narrate it as progress _within the current stage_
  (e.g. `[person_matching] 60%`), not as a single overall bar, or the bar will
  appear to jump backwards when the stage advances.
- **qualify / enrich** — no stage (`current_stage` is null). Report plain
  rows/`%`/ETA with no brackets. The server total (`rows_total`) is populated;
  if it's ever null, fall back to the count-only line below — never fabricate a
  `%`/ETA.

## Fallback (no `rows_total`)

If `rows_total` is null but `rows_processed` is present and advancing (streaming
workflows that never report a denominator), report the **count only** — same
degraded line as the CLI's `formatProgressLine`:

```
Processing... 45 rows so far…
```

Show the stage in **brackets** when `current_stage` is non-null
(`Processing... 45 rows so far… [person_matching]`). Still omit the percentage
and ETA — both are meaningless without a total. **Don't fabricate a percentage
or ETA from a null `rows_total`.**

Only when there is **no `rows_processed` at all** (null/absent, or zero) does
the workflow report no row-level progress — then fall back to the **status
string only**, same as the CLI:

```
match: RUNNING (no row-level progress reported)
```

## Stopping a run

If the user asks to stop, kill, or abort an in-flight run, cancel it by its
`workflow_run_id`. The no-CLI rule above doesn't apply — cancel is one-shot and
returns immediately:

```bash
landbase-cli workflow cancel "$RUN_ID"
# stdout: {"workflow_run_id":"...","status":"CANCELLED","cancelled":true}
```

Say what cancel does **not** do before running it: a step that reports row
progress stops at its next record or batch, but one that doesn't report progress
runs to completion; rows already written stay; and the user is billed for the
work performed, including work that finishes after the cancel lands.

`cancelled: false` means this request didn't newly stop the run — already
stopped, or its status was only reconciled. Exit 0, safe to retry.

Exit 2 with code `CONFLICT` means the run already succeeded, finished on its own
first, or has no cancellable execution: poll once more and report the real
status instead of retrying. On any other exit 2 the cancel **may still have
landed** — retry once (safe), then re-read the status. Don't report the run as
still going on the strength of a failed cancel.

## Red Flags — STOP

- About to run `landbase-cli workflow ... --wait` to monitor → that blocks the
  session; for live narration trigger without `--wait` and poll the REST
  endpoint instead.
- About to print an animated progress bar or ANSI control codes → report plain
  text only; the monitoring path is environment-agnostic (local and cloud).
- About to show an ETA when `rows_total` is null or the rate is ≤ 0 → omit it;
  report rows/percent (or status only) instead.
- Polling faster than ~30s → adds load without better signal; the run reports
  progress on a coarse cadence.
- About to cancel a run the user didn't ask you to stop → irreversible and
  billed. Confirm first.
