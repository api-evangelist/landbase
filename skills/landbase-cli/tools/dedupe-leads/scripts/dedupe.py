#!/usr/bin/env python3
"""Deduplicate a CSV of leads.

Removes duplicate rows by normalized email (primary key) or normalized
company+name (fallback when email is blank), keeping the most complete record.
Standard library only; no network.

Usage:
    python3 dedupe.py INPUT.csv [-o OUTPUT.csv]

If -o is omitted, output is written to INPUT.deduped.csv. A one-line summary is
printed to stdout.
"""
import argparse
import csv
import os
import re
import sys

_COMPANY_SUFFIXES = {
    "inc", "incorporated", "llc", "ltd", "limited", "corp",
    "corporation", "co", "company", "gmbh", "plc",
}


def normalize_email(value):
    """Lowercase and strip an email; empty string if falsy."""
    return (value or "").strip().lower()


def normalize_name(value):
    """Collapse whitespace and lowercase a person name."""
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def normalize_company(value):
    """Lowercase, strip punctuation, and drop common legal suffixes."""
    text = (value or "").strip().lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = [t for t in text.split() if t and t not in _COMPANY_SUFFIXES]
    return " ".join(tokens)


def record_key(row, index):
    """Return a dedupe key for a row.

    Uses the normalized email when present, otherwise normalized
    company+name. Rows with neither get a unique key so they are never merged.
    """
    email = normalize_email(row.get("email"))
    if email:
        return ("email", email)
    company = normalize_company(row.get("company"))
    name = normalize_name(row.get("name"))
    if company or name:
        return ("company-name", company, name)
    return ("unique", index)


def completeness(row):
    """Count non-empty fields in a row."""
    return sum(1 for v in row.values() if v and str(v).strip())


def dedupe(rows):
    """Deduplicate rows, keeping the most complete record per key.

    Returns (deduped_rows, stats). deduped_rows preserves the order of each
    key's first appearance; stats has input/output/removed counts.
    """
    best = {}
    order = []
    for index, row in enumerate(rows):
        key = record_key(row, index)
        if key not in best:
            best[key] = row
            order.append(key)
        elif completeness(row) > completeness(best[key]):
            best[key] = row
    deduped = [best[key] for key in order]
    stats = {
        "input": len(rows),
        "output": len(deduped),
        "removed": len(rows) - len(deduped),
    }
    return deduped, stats


def _default_output_path(input_path):
    base, ext = os.path.splitext(input_path)
    return "{base}.deduped{ext}".format(base=base, ext=ext or ".csv")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Deduplicate a CSV of leads.")
    parser.add_argument("input", help="Path to the input CSV")
    parser.add_argument("-o", "--output", help="Path to write the deduped CSV")
    args = parser.parse_args(argv)

    with open(args.input, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    deduped, stats = dedupe(rows)

    output_path = args.output or _default_output_path(args.input)
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(deduped)

    print(
        "Deduped {input} rows -> {output} ({removed} removed). Wrote {path}".format(
            path=output_path, **stats
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
