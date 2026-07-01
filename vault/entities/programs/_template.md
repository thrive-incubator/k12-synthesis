---
type: entity
entity_type: program         # company | agency | program | fund
name: <Display Name>
slug: <lowercase-hyphenated-slug>
aliases: []                  # other names this entity/program goes by
layer: federal               # one of: federal | state | district | charter | vendor | ideas
status: active               # active | acquired | shutdown | dormant
first_seen: <YYYY-Www>       # ISO week first added, e.g. 2026-W26
last_updated: <YYYY-Www>     # ISO week of the most recent update
tags: []                     # from TAGS.md only
---

<!--
  Generic entity template. The same template covers companies, agencies, and programs —
  set `entity_type` accordingly (company | agency | program | fund) and place the file in the
  matching entities/<type>/ folder. Save as <slug>.md. Delete these comments when you create
  a real page. Check TAGS.md before adding a new tag or coining a new slug.
-->

## Current snapshot

<!--
  One short paragraph: what is true about this entity/program NOW. OVERWRITE this section on
  every update. End with "*(as of <YYYY-Www>)*".
-->

*(as of <YYYY-Www>)*

## Timeline

<!--
  Append-only, NEWEST FIRST. Prepend new entries above older ones; never edit or delete past
  entries. Every entry MUST carry a source link.

### <YYYY-Www> — short headline of what happened
*Source · Month DD, YYYY* · [link](url)
1–2 sentences, key facts raw (dollar amounts, names, dates).
-->
