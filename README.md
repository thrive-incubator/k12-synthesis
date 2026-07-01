# Thrive K12

Prototype for Thrive Center's internal K12 funding & wellbeing knowledge system. One repo,
two cleanly separated halves:

```
thrive-k12/
├── vault/     ← the knowledge base (open THIS on its own for an agent to navigate)
└── skills/    ← the tooling that produces and files the weekly digests
```

## vault/ — the knowledge base

A self-contained markdown vault. It is designed to be opened **on its own** (point a Claude
Project or agent at `vault/`) — it carries its own map and rules and references nothing outside
itself. Start at [`vault/index.md`](vault/index.md); the operating manual is
[`vault/CONVENTIONS.md`](vault/CONVENTIONS.md) and the controlled vocabulary is
[`vault/TAGS.md`](vault/TAGS.md). It has two axes: chronological weekly digests under
`vault/digests/`, and accreting entity & theme pages under `vault/entities/` and `vault/themes/`.

## skills/ — the tooling

Two Claude skills that form one pipeline:

- **`skills/k12-synthesis/`** — *produces* the weekly digest from no-auth sources. `ingest.py`
  fetches and stamps each item with a citation ref; the model cites `{{ref}}` tokens (never raw
  URLs); `assemble.py` expands them to real links and rejects any fabricated URL.
- **`skills/k12-vault-ingest/`** — *files* a digest into `vault/` and grows the entity/theme
  pages. `check_links.py` enforces that every link written onto a page traces verbatim to the
  digest.

The loop: **`k12-synthesis` writes a digest → `k12-vault-ingest` accretes it into `vault/` →
repeat weekly.**

### Making the skills runnable

Claude Code discovers skills under `~/.claude/skills/`. This repo is the source of truth; symlink
the two skill folders into place:

```
ln -sfn "$PWD/skills/k12-synthesis"    ~/.claude/skills/k12-synthesis
ln -sfn "$PWD/skills/k12-vault-ingest" ~/.claude/skills/k12-vault-ingest
```

(Run from the repo root.) Edit the skills here in the repo; the symlinks pick up changes.
