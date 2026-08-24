---
name: landbase-email-campaigns
description:
  Create and launch outbound email campaigns from an imported audience via
  landbase-cli. Use when the user wants to build, personalize, send, or check an
  email campaign — covers the create -> audience -> messages -> coverage ->
  launch flow, the per-contact personalized-CSV path, and the "launch != sends"
  gotcha.
---

# Landbase email campaigns

`landbase-cli email-campaigns` runs the full outbound flow on top of the
platform gateway. The normal order is:

```
create -> audience -> messages -> coverage (optional check) -> launch
```

Run `landbase-cli email-campaigns --help` for the exact subcommand/flag
reference; this skill is the procedural guide.

## Prereqs (in order)

1. `landbase-cli auth login` — platform session.
2. `landbase-cli account set` — pick + persist the account id.
3. Import contacts via the **contacts-import skill** — a hard handoff: follow
   that skill end to end and do not run `contacts-import start` until its
   mapping flow has produced a resolved `mapping` for the body. The import
   produces the **tag** the campaign targets;
   `contacts-import status <importId>` surfaces both `tagName` and `tagId`.

Sending inboxes are configured separately on the account (in the web app), not
via this CLI.

## Identifying the audience tag

The audience names its tag by **exactly one** of:

- `tagName` (preferred — human-readable, what `contacts-import` shows the user),
  or
- `tagId` (the opaque numeric id).

The back-end resolves `tagName` to an id within the account. Tag names are not
guaranteed unique per account; if a name matches more than one tag the create
call fails with `tag_name_ambiguous` and lists the candidate `{id, name, type}`
— re-issue with the explicit `tagId` from that list.

## `create` body shape

### Template mode (one shared message per step)

Channel must be `"email"`; step orders contiguous from 1; each step carries an
inline message. Bodies may use ONLY these bracketed variables (anything else
400s): `[Recipient's Name]` `[Recipient's Company Name]` `[Your Company]`
`[Opener]`.

```json
{
  "schemaVersion": 1,
  "name": "Q2 outreach",
  "audience": {
    "type": "tag",
    "tagName": "Q2 Leads",
    "excludeContactedDays": 30,
    "excludeType": "contacted",
    "limitPerCompany": 2
  },
  "sequence": {
    "steps": [
      {
        "order": 1,
        "channel": "email",
        "daysDelay": 0,
        "message": { "subject": "...", "body": "..." }
      },
      {
        "order": 2,
        "channel": "email",
        "daysDelay": 3,
        "message": { "subject": "...", "body": "..." }
      }
    ]
  }
}
```

(`"tagId": 15` may be used instead of `"tagName"` — exactly one.)

### Personalized mode (per-contact messages generated locally by an AI agent)

Set `"messaging": { "mode": "personalized" }` on create. Steps are a skeleton —
`order`/`channel`/`daysDelay` only, NO inline `message`. The agent fills ONE
wide CSV (one row per contact) and uploads it; the back-end matches by email and
sends the copy **verbatim** (no server-side generation).

Create-first flow:

1. `landbase-cli email-campaigns create --json campaign.json` (mode
   personalized, N steps)
2. `landbase-cli email-campaigns audience --campaign <id> --out audience.csv`
3. (agent) `landbase-cli onboarding get` — pull seller-side context for the
   copy.
4. (agent) fill `subject_1/body_1 ... subject_N/body_N` in `audience.csv`, in
   place.
5. `landbase-cli email-campaigns messages --campaign <id> --csv audience.csv --watch`
6. `landbase-cli email-campaigns coverage --campaign <id> --show <email>`
   (spot-check)
7. `landbase-cli email-campaigns launch <id> --watch`

**Seller context (step 3) matters.** `onboarding get` returns `aboutCompany` /
`aboutAudience` / `aboutCompetition` — the value prop, ICP, and differentiation
the copy needs to land. The more complete the account onboarding, the better the
generated messages; fill it in (`onboarding update`) before generating.

**The wide CSV** = the exported context columns + `subject_i`/`body_i` for each
step. `email` is the join key (must match the export exactly). `subject_i` ≤
1000 chars, `body_i` ≤ 10000 chars. The back-end validates the upload and
reports per-row errors in the ingest status. Upload is async + idempotent
(re-upload a fixed file = full replace).

**Coverage gate.** `launch` is BLOCKED on incomplete coverage — fix the CSV and
re-upload. Partial / covered-only launch is not supported; every matched contact
must have a message.

## Assignment (optional — send from a teammate's inboxes)

By default the caller owns the campaign and their inboxes send. To send from
another account user:

- `landbase-cli account users` lists the users the caller can assign campaigns
  to — the server returns only your assignable set (no client-side filtering
  needed): account Owners see every current member, everyone else sees only
  themselves (non-Owners may only self-assign; assigning to another user as a
  non-Owner fails with `assignment_not_allowed`, exit 2). Shape:
  `{data:[{identityId, firstName, lastName, email, roleId, roleName, hasActiveInboxes, hasConnectedLinkedin}]}`.
  `identityId` is the value assignment takes; for email pick a user with
  `hasActiveInboxes: true`.
- `create --json` accepts an optional top-level `assignedUserId` (an
  `identityId`). The assigned user becomes the campaign **owner** — THEIR
  inboxes send — while the caller stays recorded as creator and can still drive
  `audience` / `messages` / `launch`.
- `assign --campaign <id> --user <identityId>` re-assigns a DRAFT (Owner only —
  non-Owners may pass only their own `identityId`). DRAFT only — once launched,
  assignment is final (409 `campaign_not_reassignable`).
- `launch` on a campaign assigned to someone OTHER than its creator requires
  `--yes`; without it the CLI exits 1 `CONFIRMATION_REQUIRED` with a stderr
  message naming the assignee. Unassigned campaigns launch exactly as before (no
  `--yes` needed). **Never pass `--yes` preemptively**: on
  `CONFIRMATION_REQUIRED`, show the user WHO the campaign is assigned to and
  re-run with `--yes` only after they explicitly confirm — the flag consents to
  sending from that teammate's inboxes on the user's behalf.
- Assignability is validated at create/assign AND re-checked server-side at
  launch (the assignee may have lost inboxes or membership since create):
  `assigned_user_not_found`, `assigned_user_not_in_account`,
  `assigned_user_no_active_inboxes`, `email_channel_permission_required` — all
  exit 2. Remedy: re-run `landbase-cli account users` and pick a user whose
  `hasActiveInboxes` is true.

## `--watch` runs long — prefer a sub-agent

Both `messages --watch` (ingest) and `launch --watch` poll and can block for a
minute or more (launch polls up to 10×10s; ingest longer). When driving from a
coding agent, dispatch the `--watch` call as a **sub-agent** so it doesn't tie
up the main session. Without `--watch` the command returns immediately and you
poll later with `messages` / `status`.

## LAUNCH != SENDS (the trap)

`launch` returns immediately with `"processing_messages"` and hands the audience
to the async scheduler; the campaign reaches `"scheduled"` a little later.
`launch --watch` polls the status (max 10, 10s apart) so you can see it land on
`"scheduled"` — on timeout the launch already succeeded, just keep polling with
`status`.

`"scheduled"` means enrolled + handed to the send scheduler; actual sends are
further gated by inbox status + daily caps, the account send window (default
06:00–15:00 PT), and contact verification. `status` returns:

```
{ status, stats{delivered,replies,bounced,contacted},
  outreach{inQueue,inProgress,completed}, excluded{...},
  timing{estimatedDaysToFirstTouchComplete,estimatedDaysToCompletion,dailyCapacity} }
```

Audience accounting: `create` and `launch` return only `{ campaignId, status }`.
Enrollment

- exclusion counts are produced by the async scheduler AFTER launch — read them
  from `status` / `coverage`, not the launch response.

## Errors (upstream bodies surface verbatim)

- `INVALID_INPUT` — malformed body; read the message (unsupported channel /
  `audience.type` / `messaging.mode`, or "exactly one of tagId/tagName").
- `NOT_FOUND` — `tag_not_found` | `campaign_not_found` | `user_not_found` |
  `assigned_user_not_found`.
- `API_ERROR` — `campaign_not_launchable` (409 + current status),
  `tag_name_ambiguous` (pass the explicit tagId), `no_contacts_matched` /
  `campaign_has_no_tag_audience` (422), `campaign_coverage_incomplete` (fix the
  CSV), `campaign_creator_mismatch` (403 — the caller is neither the campaign's
  owner nor its creator), `campaign_not_reassignable` (409 — assignment is final
  once launched), `assignment_not_allowed` (403 — only the account Owner can
  assign to another user; self-assign or omit `assignedUserId`),
  `assigned_user_not_in_account` / `assigned_user_no_active_inboxes` /
  `email_channel_permission_required` (pick another user via
  `landbase-cli account users` — needs `hasActiveInboxes: true`).
- `AUTH_REQUIRED` / `AUTH_FAILED` — run `landbase-cli auth login`.

## Example (import -> create -> launch -> track)

```bash
# import.json must already carry the resolved "mapping" built by the
# contacts-import skill — never start without one.
landbase-cli contacts-import start --json import.json
landbase-cli email-campaigns create --json campaign.json
# If the campaign is assigned to a teammate this exits 1 CONFIRMATION_REQUIRED:
# show the user the assignee and re-run with `--yes` only after they confirm.
landbase-cli email-campaigns launch 123 --watch
landbase-cli email-campaigns status 123
```
