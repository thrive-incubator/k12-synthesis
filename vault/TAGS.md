---
type: vocabulary
last_updated: 2026-W27
---

# TAGS — Controlled Vocabulary

This is the vault's controlled vocabulary. **Before creating a new tag or entity, check this
file.** If a new canonical term is genuinely needed, add it here first so the vocabulary doesn't
fragment into near-duplicates (`telehealth` vs `tele-health` vs `virtual-care`).

## The six layers

These are the canonical layer slugs. Use the **slug** everywhere in front-matter (`layers:`,
`layer:`). The full names and descriptions come from the `k12-synthesis` skill and follow the
money from source to outcome.

| Slug | Full name | One-line description |
| --- | --- | --- |
| `federal` | Federal Funding & Policy | Formula/competitive grants, regulations, guidance, and appropriations out of ED, HHS/SAMHSA, and related agencies — the top of the funnel. |
| `state` | State Systems | How federal dollars become state allocations, state plans, Medicaid and state-funded school mental health — the translation layer. |
| `district` | District Purchasing Layer | District budgets, contracts, procurement, RFPs, and staffing decisions — where money becomes a buying decision. |
| `charter` | Charter School Sector | Public funding flows, CMO contracts, vendor purchasing, and innovation pilots in the charter sector — a distinct buying and experimentation channel. |
| `vendor` | Technology & Vendor Layer | Software, screening/assessment tools, telehealth, SEL platforms, compliance tools, and the companies behind them — where ideas become products. |
| `ideas` | Ideas & Influence Layer | Research, evidence, evaluations, advocacy, and narratives — where wellbeing ideas gain or lose legitimacy before the money follows. |

## Canonical theme tags

A short starter list. These grow over time — add new canonical tags here as themes emerge, and
prefer an existing tag over coining a near-synonym.

- `school-medicaid` — Medicaid reimbursement for school-based health/mental-health services.
- `sel` — social-emotional learning.
- `telehealth` — virtual/remote care delivery (incl. teletherapy in schools).
- `screening` — mental-health / behavioral screening and assessment in schools.
- `school-based-mental-health` — mental-health services delivered in the school setting.
- `counseling-staffing` — counselors, therapists, psychologists, and staffing ratios.
- `esser` — ESSER / pandemic-relief education funding.
- `esser-cliff` — the expiration of ESSER funds and its downstream budget consequences.
- `financing` — funding mechanisms, allocation formulas, appropriations, and budget structure.
- `enrollment-decline` — falling K-12 enrollment and its per-pupil revenue and consolidation effects.
- `assessment` — academic testing and assessment products and the companies behind them.
- `special-education` — funding and administration of special education / IDEA services.

## Naming rules

- **Filenames are lowercase-hyphenated slugs.** `hazel-health.md`, `school-medicaid-mental-health.md`.
  No spaces, no capitals, no underscores (except the `_template.md` prefix, which is reserved to
  keep templates sorted first and visibly non-real).
- **Canonical display name and any aliases go in front-matter**, not the filename
  (`name:`, `aliases:`). The slug is the stable identifier; the display name can read naturally.
- **One slug per real-world entity/theme.** Before creating a page, search existing pages and this
  file for an existing slug or alias. If it exists, update it; don't fork a near-duplicate.
- **Add new canonical terms here before first use** — a tag or entity that isn't in TAGS.md should
  be added to TAGS.md as part of the same update.
- **State codes** are two-letter US postal codes (`CA`, `TX`) in `states:` / `related_states:`.
