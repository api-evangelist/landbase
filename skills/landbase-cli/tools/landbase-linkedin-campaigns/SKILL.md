---
name: landbase-linkedin-campaigns
description:
  Create and launch outbound LinkedIn campaigns from an imported audience via
  landbase-cli. Use when the user wants to build, personalize, send, or check a
  LinkedIn campaign — covers the create -> audience -> messages -> coverage ->
  launch flow, the per-contact personalized-CSV path, and the "launch != sends"
  gotcha.
---

# Landbase LinkedIn campaigns

`landbase-cli linkedin-campaigns` runs the full outbound LinkedIn flow on top of
the platform gateway. The normal order is:

```
create -> audience -> messages -> coverage (optional check) -> launch
```

Run `landbase-cli linkedin-campaigns --help` for the exact subcommand/flag
reference; this skill is the procedural guide. It mirrors `email-campaigns` —
the differences are: messages carry **no subject** (message body only), keyed by
**`linkedin_url`**, and steps run from **order 0** (the connection request).

## Prereqs (in order)

1. `landbase-cli auth login` — platform session.
2. `landbase-cli account set` — pick + persist the account id.
3. Import contacts via the **contacts-import skill** — a hard handoff: follow
   that skill end to end and do not run `contacts-import start` until its
   mapping flow has produced a resolved `mapping` for the body. The import
   produces the **tag** the campaign targets;
   `contacts-import status <importId>` surfaces both `tagName` and `tagId`.

A **connected LinkedIn account** (configured separately in the web app, not via
this CLI) is required to launch — launch sends from the campaign **owner's**
connected LinkedIn account(s): the assigned user's when assigned (see Assignment
below), otherwise the creator's.

## Identifying the audience tag

The audience names its tag by **exactly one** of `tagName` (preferred —
human-readable, what `contacts-import` shows) or `tagId` (the opaque numeric
id). The back-end resolves `tagName` within the account; if a name matches more
than one tag the create call fails with `tag_name_ambiguous` and lists the
candidate `{id, name, type}` — re-issue with the explicit `tagId`.

## `create` body shape

Steps run from `order: 0` (the connection request) and are contiguous. Each step
declares `isMessageInclude` — `true` if it sends a message. The wait before a
step runs is **exactly one** of `delayDays` or `minutesDelay`. `minutesDelay` is
only allowed **after the first message** (order ≥ 2); the connection request
(order 0) and the first message (order 1) use `delayDays`, and **order 1 must be
`delayDays` ≥ 1** (LinkedIn requires at least 1 day between the request and the
first message).

### Template mode (one shared message per step)

Each message-bearing step carries an inline body:

```json
{
  "schemaVersion": 1,
  "name": "Q2 LinkedIn outreach",
  "goal": "book intro calls",
  "audience": { "type": "tag", "tagName": "Q2 Leads" },
  "sequence": {
    "steps": [
      { "order": 0, "delayDays": 0, "isMessageInclude": false },
      {
        "order": 1,
        "delayDays": 2,
        "isMessageInclude": true,
        "message": { "body": "..." }
      },
      {
        "order": 2,
        "minutesDelay": 30,
        "isMessageInclude": true,
        "message": { "body": "..." }
      }
    ]
  }
}
```

(`"tagId": 15` may be used instead of `"tagName"` — exactly one. Set
`"isMessageInclude": true` with a `message.body` on `order: 0` to send a note
with the connection request.)

### Personalized mode (per-contact messages generated locally by an AI agent)

Set `"messaging": { "mode": "personalized" }` on create. Steps are a skeleton —
`order`/`delayDays`/`isMessageInclude` only, NO inline `message`. The agent
fills ONE wide CSV (one row per contact) and uploads it; the back-end matches by
`linkedin_url` and sends the copy **verbatim** (no server-side generation).

Create-first flow:

1. `landbase-cli linkedin-campaigns create --json campaign.json` (mode
   personalized)
2. `landbase-cli linkedin-campaigns audience --campaign <id> --out audience.csv`
3. (agent) `landbase-cli onboarding get` — pull seller-side context for the
   copy.
4. (agent) fill the `message_<order>` columns in `audience.csv`, in place.
5. `landbase-cli linkedin-campaigns messages --campaign <id> --csv audience.csv --watch`
6. `landbase-cli linkedin-campaigns coverage --campaign <id> --show <linkedinUrl>`
   (spot-check)
7. `landbase-cli linkedin-campaigns launch <id> --watch`

**Seller context (step 3) matters.** `onboarding get` returns `aboutCompany` /
`aboutAudience` / `aboutCompetition` — the value prop, ICP, and differentiation
the copy needs. The more complete the onboarding, the better the generated
messages; fill it in (`onboarding update`) before generating.

**The wide CSV** = the exported context columns + `message_<order>` for each
message-bearing step. `linkedin_url` is the join key (must match the export
exactly). `message_<order>` ≤ 5000 chars; `message_0` (when present) is the
connection-request note, `message_1..` are follow-ups. The back-end validates
the upload and reports per-row errors in the ingest status. Upload is async +
idempotent (re-upload a fixed file = full replace).

**Coverage gate.** `launch` is BLOCKED on incomplete coverage — fix the CSV and
re-upload. Partial / covered-only launch is not supported; every matched contact
must have a message. Upload is allowed only on **personalized** campaigns
(`campaign_not_personalized` otherwise).

**Sendability.** The dedicated `sendability --campaign <id>` command returns a
`sendability` object explaining why the messaged audience is smaller than the
tag: `tagged` (all tagged contacts), `sendable` (== `total`/`matched`),
`excluded` (= `tagged − sendable`), plus a per-reason diagnostic breakdown —
`contactsWithoutLinkedinUrl`, `contactsWithInvalidProfile`, `contactsInDnc`,
`contactsUnsubscribed`, `contactsAlreadyInCampaign`. The reasons are independent
counts (a contact can hit several) so they may overlap and need not sum to
`excluded`; the CLI prints the non-zero reasons as a stderr warning when any
contacts are excluded. `coverage` (message-completeness) and `audience` (CSV
export) do not carry sendability — run `sendability` for it.

**Pre-launch (DRAFT) only.** Both `sendability` and `coverage` are pre-launch
planning tools — they re-resolve the audience / read the temp staging, which
become meaningless once a campaign is launched (its own contacts now count as
enrolled and the staging is consumed). After launch they return
`409 sendability_unavailable` / `coverage_unavailable`. Inspect them while the
campaign is still a DRAFT.

## Assignment (optional — send from a teammate's LinkedIn account)

By default the caller owns the campaign and their connected LinkedIn account(s)
send. To send from another account user:

- `landbase-cli account users` lists the users the caller can assign campaigns
  to — the server returns only your assignable set (no client-side filtering
  needed): account Owners see every current member, everyone else sees only
  themselves (non-Owners may only self-assign; assigning to another user as a
  non-Owner fails with `assignment_not_allowed`, exit 2). Shape:
  `{data:[{identityId, firstName, lastName, email, roleId, roleName, hasActiveInboxes, hasConnectedLinkedin}]}`.
  `identityId` is the value assignment takes; for LinkedIn pick a user with
  `hasConnectedLinkedin: true`.
- `create --json` accepts an optional top-level `assignedUserId` (an
  `identityId`). The assigned user becomes the campaign **owner** — THEIR
  connected LinkedIn account(s) send — while the caller stays recorded as
  creator and can still drive `audience` / `messages` / `launch`.
- `assign --campaign <id> --user <identityId>` re-assigns a DRAFT (Owner only —
  non-Owners may pass only their own `identityId`). DRAFT only — once launched,
  assignment is final (409 `campaign_not_reassignable`).
- `launch` on a campaign assigned to someone OTHER than its creator requires
  `--yes`; without it the CLI exits 1 `CONFIRMATION_REQUIRED` with a stderr
  message naming the assignee. Unassigned campaigns launch exactly as before (no
  `--yes` needed). **Never pass `--yes` preemptively**: on
  `CONFIRMATION_REQUIRED`, show the user WHO the campaign is assigned to and
  re-run with `--yes` only after they explicitly confirm — the flag consents to
  sending from that teammate's LinkedIn account on the user's behalf.
- Assignability is validated at create/assign AND re-checked server-side at
  launch (the assignee may have disconnected LinkedIn or lost membership since
  create): `assigned_user_not_found`, `assigned_user_not_in_account`,
  `linkedin_not_connected`, `linkedin_channel_permission_required` — all exit 2.
  Remedy: re-run `landbase-cli account users` and pick a user whose
  `hasConnectedLinkedin` is true.

## `--watch` runs long — prefer a sub-agent

Both `messages --watch` (ingest) and `launch --watch` poll and can block for a
minute or more (launch polls up to 10×10s; ingest longer). When driving from a
coding agent, dispatch the `--watch` call as a **sub-agent** so it doesn't tie
up the main session. Without `--watch` the command returns immediately and you
poll later with `messages` / `status`.

## LAUNCH != SENDS (the trap)

`launch` hands the audience to the LinkedIn send pipeline; the campaign reaches
`"scheduled"` and then sends connection requests / messages on a throttled
cadence (LinkedIn rate limits, per-account caps). `launch --watch` polls the
status (max 10, 10s apart) so you can see it land on `"scheduled"` — on timeout
the launch already succeeded, just keep polling with `status`. `status` returns
the campaign type, lifecycle status, and allocated/sent counts.

## Errors (upstream bodies surface verbatim)

- `INVALID_INPUT` — malformed body; read the message (e.g. "exactly one of
  tagId/tagName", non-contiguous step orders).
- `NOT_FOUND` — `tag_not_found` | `campaign_not_found` |
  `assigned_user_not_found`.
- `API_ERROR` — `campaign_not_launchable` (409 + current status),
  `tag_name_ambiguous` (pass the explicit tagId), `no_contacts_matched` /
  `campaign_has_no_tag_audience` (422), `campaign_coverage_incomplete` (fix the
  CSV), `campaign_not_personalized` (upload only on personalized campaigns),
  `campaign_creator_mismatch` (403 — the caller is neither the campaign's owner
  nor its creator), `campaign_not_reassignable` (409 — assignment is final once
  launched), `assignment_not_allowed` (403 — only the account Owner can assign
  to another user; self-assign or omit `assignedUserId`),
  `assigned_user_not_in_account` / `linkedin_not_connected` /
  `linkedin_channel_permission_required` (the owner can't send on LinkedIn —
  connect an account in the web app, or pick another user via
  `landbase-cli account users` with `hasConnectedLinkedin: true`).
- `AUTH_REQUIRED` / `AUTH_FAILED` — run `landbase-cli auth login`.

## Example (import -> create -> launch -> track)

```bash
# import.json must already carry the resolved "mapping" built by the
# contacts-import skill — never start without one.
landbase-cli contacts-import start --json import.json
landbase-cli linkedin-campaigns create --json campaign.json
# If the campaign is assigned to a teammate this exits 1 CONFIRMATION_REQUIRED:
# show the user the assignee and re-run with `--yes` only after they confirm.
landbase-cli linkedin-campaigns launch 123 --watch
landbase-cli linkedin-campaigns status 123
```
