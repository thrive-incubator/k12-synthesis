# thrive-k12-synthesis

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

No scripts, no dependencies. Claude fetches a fixed set of **no-auth** sources directly —
RSS feeds, Google News topic queries, and public JSON APIs (Federal Register, Grants.gov) —
filters for relevance, keeps facts mostly raw with a thin layer of synthesis on top, sorts items
into the six layers, and writes a clean, docx-ready markdown file.

See [`SKILL.md`](SKILL.md) for the full source list and workflow.

## Usage

Once installed as a Claude Code skill, trigger it with any of: "run the Thrive synthesis",
"what moved in K12 funding & wellbeing this week", "the Thrive Center briefing", or
"regenerate the synthesis".

## Install

Symlink (or copy) this repo into your Claude skills directory:

```
ln -s "$PWD" ~/.claude/skills/thrive-k12-synthesis
```
