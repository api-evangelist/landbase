# Matching Rules

How `dedupe-leads` decides two rows are the same lead and which one to keep.

## Match key

Rows are grouped by a single key, chosen in this order:

1. **Email** — if the row has a non-empty `email`, the key is the normalized
   email.
2. **Company + name** — if `email` is blank, the key is normalized `company` +
   normalized `name`.
3. **No key** — if a row has none of these, it is never merged with another row.

## Normalization

- **Email:** trim surrounding whitespace, lowercase. (`"  JANE@Acme.com "` ->
  `jane@acme.com`)
- **Name:** trim, collapse internal whitespace, lowercase. (`"Maria   Garcia"`
  -> `maria garcia`)
- **Company:** lowercase, remove punctuation, drop common legal suffixes (`inc`,
  `incorporated`, `llc`, `ltd`, `limited`, `corp`, `corporation`, `co`,
  `company`, `gmbh`, `plc`). (`"Initech, LLC"` -> `initech`)

## Which record is kept

Within a group, keep the **most complete** record — the row with the most
non-empty fields. Ties are broken by first appearance. The output preserves the
order in which each key first appeared.
