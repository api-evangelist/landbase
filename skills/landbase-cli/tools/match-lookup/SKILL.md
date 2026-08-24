---
name: match-lookup
description:
  Resolve any external record — a domain, LinkedIn URL, name, or email — to its
  entity in the Landbase graph using match company or match person.
when_to_use:
  when the user wants to look up a single specific company or person in Landbase
  — phrases like "look up [company]", "find [person] at [company]", "what do we
  know about [domain]", "resolve this record", "enrich this contact", or when
  given a domain, LinkedIn URL, name, or email and asked to find the matching
  Landbase record. For matching a full dataset of records in bulk, use
  dataset-pipeline (workflow match) instead.
version: 1.0.0
user-invocable: true
allowed-tools:
  - Bash
  - AskUserQuestion
model: sonnet
---

# Match Lookup

Resolve a **single** company or person to their record in the Landbase graph.

**This skill is for single-record lookups only.** For matching a full dataset of
records in bulk, use `workflow match` via `dataset-pipeline` (upload → onboard →
match → enrich).

Two subcommands — `match company` and `match person` — each with exact and fuzzy
modes depending on what information is available.

## Quick dispatch

| You have                       | Use                                                                                |
| ------------------------------ | ---------------------------------------------------------------------------------- |
| Company domain or LinkedIn URL | `match company --website` or `--linkedin-url` (exact)                              |
| Company name only              | `match company --name` (fuzzy)                                                     |
| Person LinkedIn URL or email   | `match person --linkedin-url` or `--email` (exact)                                 |
| Person name + company          | `match person --first-name --last-name --company-website`                          |
| Person name only               | `match person --first-name --last-name` + optionally `--expand-first-name-aliases` |

---

## Match company

### Exact lookup (preferred when you have a domain or LinkedIn URL)

```bash
# By domain — most reliable
landbase-cli match company --website=anthropic.com

# By LinkedIn URL
landbase-cli match company --linkedin-url=https://www.linkedin.com/company/anthropic

# By Landbase company ID
landbase-cli match company --company-id=12345

# Narrow by country when ID is ambiguous
landbase-cli match company --company-id=12345 --hq-country=US
```

### Fuzzy lookup (when you only have a name)

```bash
# By name alone
landbase-cli match company --name=Anthropic

# Name + location (improves precision for common names)
landbase-cli match company --name="Landbase" --hq-location-phrase="Los Angeles"

# Name only, skip website resolution
landbase-cli match company --name=Acme --no-name-to-website
```

**When to use `--no-name-to-website`:** when the company name is generic or
shared across many entities and you don't want Landbase to attempt website
inference — it prevents false positives at the cost of lower match rate.

---

## Match person

### Exact lookup

```bash
# By LinkedIn URL — most reliable for people
landbase-cli match person --linkedin-url=https://www.linkedin.com/in/danielsaks

# By email
landbase-cli match person --email=daniel@landbase.com

# By Landbase person ID
landbase-cli match person --person-id=67890
```

### Name-based lookup

```bash
# Name + company (recommended — reduces ambiguity)
landbase-cli match person --first-name=Daniel --last-name=Saks --company-website=landbase.com

# Name only
landbase-cli match person --first-name=Daniel --last-name=Saks

# Expand aliases for common nicknames (Bill → William, Bob → Robert, etc.)
landbase-cli match person --first-name=Bill --last-name=Gates --expand-first-name-aliases
```

**When to use `--expand-first-name-aliases`:** when the name provided might be a
nickname or shortened form. Without it, "Bill Gates" won't match a record stored
as "William Gates."

---

## Chaining: company → person

Common pattern — look up the company first to get a reliable domain, then find a
person there:

```bash
# Step 1: resolve the company
landbase-cli match company --name="Acme Corp" --hq-location-phrase="New York"

# Step 2: use the resolved domain to find a person
landbase-cli match person --first-name=Jane --last-name=Smith --company-website=acme.com
```

This is more reliable than passing a fuzzy company name to `match person`
directly.

---

## When match fails

If `match company` or `match person` returns no result:

1. **Try an alternate identifier** — if name matching failed, try domain or
   LinkedIn URL
2. **Loosen the query** — remove `--hq-location-phrase` or `--hq-country`
   constraints
3. **Try `--expand-first-name-aliases`** for person lookups with short first
   names
4. **Fall back to search** —
   `landbase-cli search "find [company/person description]"` may surface the
   record via the NL agent

Don't report a match failure without trying at least one alternate approach.

---

## Red Flags — STOP

- About to loop this command over many records → use `dataset-pipeline`
  (workflow match) for bulk matching instead
- Using `match company --name` for a very generic name (e.g. "Services LLC")
  without a location → add `--hq-location-phrase` first
- Using `match person` with only a first name → always provide last name at
  minimum
- Reporting "not found" after one attempt → try an alternate identifier before
  giving up
