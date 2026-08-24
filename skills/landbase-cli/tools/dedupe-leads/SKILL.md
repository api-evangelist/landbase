---
name: dedupe-leads
description:
  Deduplicate a CSV of leads or contacts by email or company+name, keeping the
  most complete record.
when_to_use:
  when the user wants to clean, dedupe, or merge duplicate rows in a leads or
  contacts CSV
version: 1.0.0
---

# Dedupe Leads

Remove duplicate rows from a CSV of leads or contacts.

## Steps

1. Read
   `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/landbase-dedupe-leads/references/matching-rules.md`
   to understand how rows are matched and which record is kept.
2. Confirm the input CSV path with the user. The file should have a header row;
   the `email`, `company`, and `name` columns are used for matching when
   present.
3. Run the dedupe script that ships with this skill:

   ```bash
   python3 "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/landbase-dedupe-leads/scripts/dedupe.py" <INPUT.csv> -o <OUTPUT.csv>
   ```

   If you omit `-o`, the script writes `<INPUT>.deduped.csv`.

4. Report the summary the script prints (input rows, output rows, removed) and
   the path to the output file.

The script uses only the Python standard library — nothing to install.
