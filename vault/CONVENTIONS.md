---
type: manual
last_updated: null
---

# CONVENTIONS — Operating Manual

The operating manual for the Thrive Center K12 Knowledge Vault. Read this before adding to or
restructuring the vault.

## Purpose & lens

This vault is a self-growing knowledge base for Thrive Center Incubator staff covering the K12
edtech funding ecosystem — how federal money and policy flow down through state systems, district
purchasing, and the charter sector into the technology/vendor layer and the ideas/influence
layer — with a deliberate weighting toward **student wellbeing and mental health**. Its job is to
turn the weekly `k12-synthesis` digest into durable, pre-synthesized knowledge so that
longitudinal questions can be answered from an accreting page instead of re-derived each time.

## The two-axis model

1. **Chronological digests** (`digests/`) — the weekly synthesis output, append-only raw material,
   one file per ISO week.
2. **Accreting entity & theme pages** (`entities/`, `themes/`) — the knowledge, built up over time.
   Each page carries a mutable **Current snapshot** and an append-only **Timeline**.

Digests are *what happened this week*; entity/theme pages are *what we know so far*. The weekly
procedure (below) feeds the first axis into the second.

## File naming conventions

- **ISO 8601 weeks** for digests: `digests/<YYYY>/<YYYY>-W<ww>.md`, e.g. `digests/2026/2026-W26.md`.
  The week is the ISO week (Mon–Sun) the digest covers. Years get their own subdirectory.
- **Lowercase-hyphenated slugs** for entity and theme filenames: `entities/companies/hazel-health.md`,
  `themes/school-medicaid-mental-health.md`. Display names and aliases live in front-matter.
- See [TAGS.md](TAGS.md) for the full naming rules and the controlled vocabulary.

## Front-matter schemas

Every file carries YAML front-matter. The three content schemas:

### Digest — `digests/2026/2026-Wxx.md`

```yaml
---
type: digest
week: 2026-W26
date_start: 2026-06-22
date_end: 2026-06-28
generated: 2026-06-30
layers: [federal, state, vendor]      # only layers that had items this week
entities: [hazel-health, samhsa]      # canonical slugs mentioned
states: [CA, TX]                      # US state postal codes touched
tags: [school-medicaid, telehealth]   # from TAGS.md only
items: 14
---
```

### Entity — `entities/<type>/<slug>.md`

```yaml
---
type: entity
entity_type: company         # company | agency | program | fund
name: Hazel Health
slug: hazel-health
aliases: ["Hazel"]
layer: vendor
status: active               # active | acquired | shutdown | dormant
first_seen: 2026-W26
last_updated: 2026-W26
tags: [telehealth, student-mental-health]
---
```

### Theme — `themes/<slug>.md`

```yaml
---
type: theme
name: School Medicaid for Mental Health
slug: school-medicaid-mental-health
status: active
last_updated: 2026-W26
related_entities: [samhsa, medicaid]
related_states: [CA, TX]
tags: [school-medicaid, financing]
---
```

## Snapshot + Timeline body structure

Every entity and theme page has exactly two sections under the front-matter:

### `## Current snapshot`

One short paragraph stating what is true **now**, ending with `*(as of 2026-W26)*` (the current
ISO week). This section is **overwritten** each time the page is updated — it is the mutable
current truth. Keep it to a few sentences; the history lives in the Timeline.

### `## Timeline`

Append-only log, **newest first**. Each entry:

```markdown
### 2026-W26 — short headline of what happened
*Source · Month DD, YYYY* · [link](url)
1–2 sentences, key facts raw (dollar amounts, names, dates).
```

Prepend new entries above older ones; never edit or delete existing entries. The Timeline is the
provenance-backed audit trail; the snapshot is the synthesis on top of it.

## Provenance rule

**Every fact on an entity or theme page links its source.** Every Timeline entry MUST carry a
source link. No fact enters a page without provenance — if you can't cite it, it doesn't go in.
The Current snapshot synthesizes facts that already exist (with their links) in the Timeline.

## Controlled-vocabulary rule

**Check [TAGS.md](TAGS.md) before inventing a tag or entity.** Reuse an existing canonical tag,
layer slug, or entity slug rather than coining a near-duplicate. If a new canonical term is
genuinely needed, add it to TAGS.md as part of the same update.

## Markdown conventions (for clean .docx conversion)

These mirror the `k12-synthesis` skill so digests and vault pages convert cleanly to Word:

- Use **ATX headings** (`#`, `##`, `###`) — they map directly to Word heading styles.
- Standard bullet lists and `**bold**` / `*italic*` only. Plain `[text](url)` links.
- **Never nest a link inside an emphasis span.** Close the italic *before* the link —
  `*Source · June 28, 2026* · [link](url)`, not `*Source · June 28, 2026 · [link](url)*`. A link
  wrapped in `*…*` is mis-parsed by Obsidian-style renderers.
- No raw HTML, no nested tables, no multi-level bullet gymnastics — those break in
  markdown-to-docx conversion.

## Weekly update procedure (manual — not automated)

After a digest is generated, do this by hand (do **not** automate it yet):

1. **Save the digest** to `digests/<YYYY>/<YYYY>-W<ww>.md` with the digest front-matter filled in
   (layers, entities, states, tags, item count).
2. **For each entity the digest touches:** open its page in `entities/<type>/` (create it from
   `entities/<type>/_template.md` if new), **overwrite** the Current snapshot to reflect what is
   now true, and **prepend** a Timeline entry with a source link. Update `last_updated` (and
   `status`/`aliases`/`tags` if they changed).
3. **For each theme the digest touches:** do the same in `themes/` (create from `themes/_template.md`
   if new) — overwrite the snapshot, prepend a sourced Timeline entry, update `last_updated`.
4. **Update [index.md](index.md):** add/refresh the three sections — Active themes, Tracked
   entities (by type), and Digests by week (newest first).
5. **Add any new canonical tags** to [TAGS.md](TAGS.md) so the vocabulary stays consolidated.

## How an agent should navigate this vault

1. **Read [index.md](index.md) first** — it is the router/map of the vault.
2. **Filter on front-matter** (`layers`, `entities`, `states`, `tags`) to narrow to relevant pages.
3. **Read entity/theme pages** for the synthesized arc (snapshot for the current state, Timeline
   for the history).
4. **Read specific digests only** when you need week-level detail not captured on a page.

Answer longitudinal questions from the pre-synthesized pages; drop to digests for raw week detail.
