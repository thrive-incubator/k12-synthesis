#!/usr/bin/env python3
"""Expand {{ref}} citation tokens in a drafted synthesis into real source links,
and refuse to emit a file that contains any fabricated or hand-typed URL.

WHY THIS EXISTS
A URL is an opaque string (e.g. an article id like /824164/, or a Google News
redirect blob) that a language model cannot reliably reproduce from memory. If the
model types URLs inline while writing the digest, it will occasionally emit a
plausible-but-wrong URL — silently, because a wrong URL looks exactly like a right
one. The only robust fix is to keep URLs entirely in code: ingest.py stamps every
candidate with a short `ref`, the model cites [link]({{ref}}) instead of a URL, and
this script swaps in the exact link from candidates.json.

GUARANTEE
- Every {{ref}} must exist in candidates.json, or this fails (unknown token).
- The draft must contain NO raw http(s) URL — every link must be a token, or this
  fails (hand-typed URL). This is what catches a hallucinated link.
On any failure the final file is NOT written and the exit code is non-zero.

USAGE
    python3 assemble.py --candidates /tmp/candidates.json --draft draft.md --out final.md
"""
import argparse
import json
import re
import sys

TOKEN = re.compile(r"\{\{\s*([A-Za-z0-9_-]+)\s*\}\}")
RAW_URL = re.compile(r"https?://[^\s)\]<>]+")


def load_refs(path):
    d = json.load(open(path))
    refs = {}
    for key in ("news", "opportunities", "federal_register"):
        for item in d.get(key, []) or []:
            ref = item.get("ref")
            url = item.get("link") or item.get("url")
            if ref and url:
                refs[ref] = {
                    "url": url,
                    "source": item.get("source") or item.get("agency") or "",
                    "title": item.get("title", ""),
                }
    return refs


def main():
    ap = argparse.ArgumentParser(description="Expand citation tokens; reject fabricated URLs.")
    ap.add_argument("--candidates", required=True, help="candidates.json produced by ingest.py")
    ap.add_argument("--draft", required=True, help="the drafted digest markdown (tokens, no URLs)")
    ap.add_argument("--out", required=True, help="path to write the assembled digest")
    args = ap.parse_args()

    refs = load_refs(args.candidates)
    text = open(args.draft).read()

    errors = []

    # 1. Unknown tokens — a ref the model invented or mistyped.
    used = [m.group(1) for m in TOKEN.finditer(text)]
    for ref in sorted(set(used)):
        if ref not in refs:
            errors.append(f"unknown citation token {{{{{ref}}}}} — not a ref in candidates.json")

    # 2. Hand-typed URLs — the model typed a link instead of citing a token. This is the
    #    hallucination vector; forbid it outright. All provenance must flow through tokens.
    for url in sorted(set(RAW_URL.findall(text))):
        errors.append(f"hand-typed URL is not allowed (cite a {{{{ref}}}} token instead): {url}")

    if errors:
        print("ASSEMBLE FAILED — final file NOT written:", file=sys.stderr)
        for e in errors:
            print("  -", e, file=sys.stderr)
        valid = sum(1 for r in used if r in refs)
        print(f"\n({valid} valid tokens found. Fix the above and re-run — do not hand-edit URLs in.)",
              file=sys.stderr)
        sys.exit(1)

    expanded = TOKEN.sub(lambda m: refs[m.group(1)]["url"], text)
    with open(args.out, "w") as f:
        f.write(expanded)

    # Report the ref -> source -> url map so the author can eyeball that tokens hit the intended
    # items. Cheap insurance against a valid-but-wrong ref (right format, wrong article).
    print(f"assembled {args.out}: expanded {len(used)} citation tokens, 0 fabricated URLs.",
          file=sys.stderr)
    for ref in dict.fromkeys(used):
        info = refs[ref]
        print(f"   {{{{{ref}}}}} -> {info['source']}: {info['url']}", file=sys.stderr)


if __name__ == "__main__":
    main()
