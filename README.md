# k12-synthesis

A weekly K12 news synthesis skill for Claude, built for the Thrive Center.

It produces a research briefing that maps the **K12 funding ecosystem** — federal dollars and
policy flowing down through state systems, district purchasing, and the charter sector, into the
technology/vendor layer and the ideas/influence layer — with a deliberate weighting toward
**student wellbeing and mental health**. The goal is to help a time-poor Thrive Center researcher
see where ideas that produce positive wellbeing outcomes can take root inside the real funding
framework.

## The six layers

1. **Federal Funding & Policy** — formula/competitive grants, regulations, guidance.
2. **State Systems** — federal dollars → state allocations; policy implementation.
3. **District Purchasing Layer** — budgets, contracts, staffing decisions.
4. **Charter School Sector** — public funding, management contracts, vendor purchasing, pilots.
5. **Technology & Vendor Layer** — software, screening tools, telehealth, SEL, compliance tools.
6. **Ideas & Influence Layer** — research, evidence, advocacy, narratives.

## How it works

**Deterministic plumbing in code, judgment in the model.**

- [`ingest.py`](ingest.py) (stdlib only, no dependencies) fetches a fixed set of **no-auth**
  sources — RSS/Atom feeds, Google News topic queries, and public JSON APIs (Federal Register,
  Grants.gov) — parses them, filters news to the window and grants to those open/closing soon,
  dedupes, and writes a compact `candidates.json` (~9k tokens, vs. ~800k tokens of raw XML). A
  dead source is reported loudly, never dropped silently.
- **Claude** reads `candidates.json` and does the rest by judgment: applies the relevance bar,
  assigns the six layers, keeps facts raw with a thin layer of synthesis on top, and writes a
  clean, docx-ready markdown file.

See [`SKILL.md`](SKILL.md) for the full source list, workflow, and known blind spots.

## Run the ingest step directly

```
python3 ingest.py                   # trailing 7 days ending today
python3 ingest.py --days 14         # custom window
python3 ingest.py --end 2026-06-24 --out /tmp/candidates.json
```

## Usage

Once installed as a Claude Code skill, trigger it with any of: "run the Thrive synthesis",
"what moved in K12 funding & wellbeing this week", "the Thrive Center briefing", or
"regenerate the synthesis".

## Install

Symlink this repo into your Claude skills directory (so edits here go live immediately). Run from
inside the cloned repo:

```
mkdir -p ~/.claude/skills
ln -s "$(pwd)" ~/.claude/skills/k12-synthesis
```

`mkdir -p` is needed because `~/.claude/skills/` may not exist on a fresh setup, and `ln` won't
create it. Prefer a copy over a symlink? Use `cp -R "$(pwd)" ~/.claude/skills/k12-synthesis`
instead — but then re-copy after each change.

Verify it took:

```
ls -l ~/.claude/skills/k12-synthesis/SKILL.md   # should resolve
python3 ~/.claude/skills/k12-synthesis/ingest.py --out /tmp/candidates.json
```

Requires Python 3 (stdlib only — no `pip install`). Restart Claude Code after installing so the
skill loads.
