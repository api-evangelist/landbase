---
name: landbase-feedback
description:
  Send feedback or a bug report to the Landbase team via landbase-cli. Use when
  the user wants to report a problem, share feedback about Landbase, or flag
  that a landbase-cli command failed.
---

# Landbase Feedback

Send feedback or a bug report to the Landbase team using
`landbase-cli feedback`.

## Steps

1. **Get the feedback text.** Use the argument if the user provided one.
   Otherwise ask what they'd like to report.

2. **If it's a bug report, gather context.** For failed commands:
   - `--endpoint=<path>` — the Landbase API endpoint involved
   - `--error-details="<text>"` or `--error-from-file=<path>`

3. **Offer to attach the conversation.** Ask the user if they want to include
   the current conversation so the Landbase team has full context for debugging:

   Use `AskUserQuestion`:

   > This sends to the Landbase team:
   >
   > - Your message: {feedback text}
   > - {if gathered} Endpoint and error details
   >
   > Would you also like to attach this conversation? It helps the team
   > reproduce the issue but includes everything said in this session.

   Options: "Send with conversation" / "Send without conversation" / "Cancel"

4. **Send it.**

   Without transcript:

   ```bash
   landbase-cli feedback "<feedback text>"
   ```

   With transcript:

   ```bash
   landbase-cli feedback "<feedback text>" --transcript
   ```

   Bug report with context:

   ```bash
   landbase-cli feedback "<feedback text>" --endpoint=/v1/workflows/enrich-only/run --error-from-file=/tmp/err.txt --transcript
   ```

5. **Report the result.** On success, tell the user it was sent. If cancelled,
   do nothing. If rate-limited (HTTP 429), offer to retry in a minute.
