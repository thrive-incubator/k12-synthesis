#!/usr/bin/env python3
"""Provenance gate for k12-vault-ingest.

INVARIANT
The digest is the sole provenance source for the vault. So every source link that
this run writes onto an entity/theme page — i.e. every link inside a Timeline entry
stamped with the week being ingested — must appear VERBATIM in that week's digest.

WHY THIS EXISTS
Copying a link from the digest onto a page is a transcription step, and a model
transcribing an opaque URL from working memory will occasionally mistype or
"tidy up" it into a plausible-but-wrong link — silently. This check makes that
impossible to miss: if a page link for this week is not present in the digest, it
was not copied faithfully. Pages accrete across weeks, so only THIS week's Timeline
entries are checked; earlier weeks were validated in their own runs.

USAGE
    python3 check_links.py <vault_root> <digest_path>
      e.g. python3 check_links.py . digests/2026/2026-W27.md

Exit code 0 = all this-week page links trace to the digest; 1 = violations found.
"""
import glob
import os
import re
import sys

LINK = re.compile(r"\]\((https?://[^)]+)\)")
WEEK = re.compile(r"(\d{4}-W\d{2})")


def links_in(text):
    return set(LINK.findall(text))


def week_timeline_links(path, week):
    """Links inside this page's `### {week} ...` Timeline blocks only."""
    text = open(path, encoding="utf-8").read()
    links = set()
    # Split on headings; a block runs from a `### ` heading to the next one.
    for block in re.split(r"\n(?=### )", text):
        head = block.lstrip()
        if head.startswith(f"### {week}"):
            links |= links_in(block)
    return links


def main():
    if len(sys.argv) != 3:
        print("usage: check_links.py <vault_root> <digest_path>", file=sys.stderr)
        sys.exit(2)
    vault, digest = sys.argv[1], sys.argv[2]

    m = WEEK.search(os.path.basename(digest))
    if not m:
        print(f"cannot derive ISO week from digest filename: {digest}", file=sys.stderr)
        sys.exit(2)
    week = m.group(1)

    allowed = links_in(open(digest, encoding="utf-8").read())

    pages = [
        p for p in glob.glob(os.path.join(vault, "entities", "**", "*.md"), recursive=True)
        + glob.glob(os.path.join(vault, "themes", "*.md"))
        if not os.path.basename(p).startswith("_")
    ]

    violations = []
    checked = 0
    for p in pages:
        for url in week_timeline_links(p, week):
            checked += 1
            if url not in allowed:
                violations.append((os.path.relpath(p, vault), url))

    if violations:
        print(f"LINK PROVENANCE FAILED — {len(violations)} link(s) in {week} Timeline entries "
              f"are not present verbatim in {os.path.basename(digest)}:", file=sys.stderr)
        for rel, url in violations:
            print(f"  - {rel}\n      {url}", file=sys.stderr)
        print("\nEvery link on a vault page must be COPIED from the digest, not retyped. Fix each by\n"
              "pasting the exact URL from the matching digest item.", file=sys.stderr)
        sys.exit(1)

    print(f"OK: {checked} link(s) in {week} Timeline entries all trace verbatim to "
          f"{os.path.basename(digest)} ({len(allowed)} links in digest).", file=sys.stderr)


if __name__ == "__main__":
    main()
